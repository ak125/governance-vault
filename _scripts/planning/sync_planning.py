"""Orchestrator: fetch + classify + hash + write outputs.

Usage:
    python3 -m _scripts.planning.sync_planning --vault-path PATH [--dry-run] [--strict-projections]
"""
import argparse
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from _scripts.planning import alerts, fetch, hash_util, schemas, stagnation, writers


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("planning.sync")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--vault-path", required=True, type=Path)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--strict-projections", action="store_true")
    p.add_argument("--strict-alerts", action="store_true",
                    help="(reserved for PR-3 alerts)")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    vault = args.vault_path

    # Validate schemas exist
    schemas.load_priority(vault)
    schemas.load_itemtype(vault)
    schemas.load_status(vault)
    schemas.load_blocked_reason(vault)

    # Fetch
    prs_vault = fetch.fetch_prs("ak125/governance-vault")
    prs_mono = fetch.fetch_prs("ak125/nestjs-remix-monorepo")
    adrs = fetch.parse_proposed_adrs(vault / "ops/moc/MOC-Decisions.md")
    items = prs_vault + prs_mono + adrs
    log.info("Fetched items=%d (vault_prs=%d mono_prs=%d adrs=%d)",
              len(items), len(prs_vault), len(prs_mono), len(adrs))

    # TODO PR-2.x: enrich each item with stagnation_days using fetch_pr_activity()

    now = datetime.now(timezone.utc)

    # Enrich each item with stagnation_days (MVP — PR-2)
    for it in items:
        upd = it.get("updated_at")
        if upd:
            it["last_human_activity_at"] = upd
            it["last_state_change_at"] = upd  # proxy for MVP — no granular tracking yet
            try:
                ts = datetime.fromisoformat(upd.replace("Z", "+00:00"))
                it["stagnation_days"] = stagnation.compute_stagnation_days(
                    last_human_activity_at=ts,
                    last_state_change_at=ts,
                    now=now,
                )
            except (ValueError, TypeError):
                it["stagnation_days"] = None
        else:
            # ADRs and items without timestamp metadata get None — explicit unknown.
            # Follow-up PR-2.x will add file mtime tracking for ADRs from
            # `git log -1 --format=%ct -- ledger/decisions/adr/ADR-NNN-*.md`.
            it["stagnation_days"] = None

    # Hash (computed AFTER enrichment, but stagnation_days is excluded by I3 blacklist)
    h = hash_util.semantic_hash(items)
    generated_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    log.info("semantic_hash=%s generated_at=%s", h, generated_at)

    if args.dry_run:
        print(f"[DRY-RUN] items={len(items)} hash={h}")
        return 0

    # Write snapshot (always)
    snap = writers.write_snapshot(items, vault_path=vault,
                                    generated_at=generated_at,
                                    semantic_hash_value=h)
    log.info("Snapshot written: %s", snap)

    # Write MOC (skip if hash unchanged)
    moc_path = vault / "ops/moc/MOC-Planning-Live.md"
    moc_changed = writers.write_moc(moc_path, items=items,
                                      semantic_hash_value=h, ack_block={})
    log.info("MOC %s", "rewritten" if moc_changed else "unchanged (hash stable)")

    # Best-effort GH Project projection (uses project_number for `gh project` CLI)
    project_number = _read_project_number_from_adr(vault)
    if project_number:
        result = writers.write_gh_project(items, project_number=project_number,
                                            strict=args.strict_projections)
        log.info("GH Project: ok=%s items_written=%d error=%s",
                  result.ok, result.items_written, result.error)
    else:
        log.warning("No project_number found in ADR-053 §Annexe A — skipping GH Project")

    # Alerts (PR-3) — best-effort, ack-aware
    ack_block = alerts.read_ack_block(moc_path)

    # 1. Fire new alerts for stagnant P0
    targets = alerts.compute_alert_targets(items, ack_block=ack_block, now=now)
    fired_ids = alerts.fire_alerts(targets, strict=args.strict_alerts)

    # 2. Detect closed-issue acks (operator closed `planning-p0-stagnant` issue → ack)
    closed_acks = alerts.fetch_closed_alert_issues()

    # 3. Merge ack updates : new alerts (last_alert_at) + closed acks (acked_at + acked_by)
    new_ack = dict(ack_block)
    if fired_ids:
        new_ack = alerts.update_last_alert_at(new_ack, fired_ids=fired_ids, now=now)
    for ack_event in closed_acks:
        cid = ack_event["canonical_id"]
        entry = new_ack.setdefault(cid, {})
        # Only update if not already acked (don't overwrite manual acks)
        if not entry.get("acked_at"):
            entry["acked_at"] = ack_event["closed_at"]
            entry["acked_by"] = ack_event["closed_by"]

    if new_ack != ack_block:
        alerts.write_ack_update(moc_path, ack_block=new_ack)
        log.info("Ack block updated (fired=%d, closed_acks=%d)",
                  len(fired_ids), len(closed_acks))
    else:
        log.info("Alerts: 0 fired, 0 closed-issue acks")

    return 0


def _read_project_number_from_adr(vault: Path) -> int | None:
    """Reads `project_number: NN` from ADR-053 §Annexe A YAML block.

    Format attendu (cf. ADR-053 §Annexe A) :
        ```yaml
        github_project:
          project_number: 42
          ...
        ```

    Distinction :
    - `project_number` (int) → `gh project` CLI
    - `project_id` (PV2_xxx string) → GraphQL API (non lu ici, lu par
      `_read_project_id_from_adr` si jamais nécessaire pour GraphQL fallback)
    """
    adr_path = vault / "ledger/decisions/adr/ADR-053-planning-live-system.md"
    if not adr_path.exists():
        return None
    text = adr_path.read_text()
    # Match line `  project_number: 42` (any leading whitespace, integer value).
    # Robust to YAML indentation, ignores backticks/parens in surrounding prose.
    m = re.search(r"^\s*project_number:\s*(\d+)\s*$", text, re.MULTILINE)
    if not m or int(m.group(1)) == 0:  # 0 = placeholder unfilled
        return None
    return int(m.group(1))


if __name__ == "__main__":
    sys.exit(main())
