#!/usr/bin/env python3
"""sync_moc_decisions.py — Generate canonical ADR index in MOC-Decisions.md.

## Design (MVP — Phase A)

PR-3 introduces the **first auto-generated section in MOC-Decisions.md**, to
let the dual-section observation pattern (3-7d cron VPS DEV) prove the
generator's stability before PR-4 strict gate locks the system.

**Dual-section approach (intentional, low-risk MVP):**
- The existing `## ADR Actifs` table stays MANUAL — humans keep curating
  rich superseded-by text, joint-coverage notes, version annotations.
- A NEW section `## ADR Canonical Index (auto-generated)` is added between
  markers `<!-- AUTO-GENERATED:moc-decisions-canonical-index {start|end} -->`.
- The generator writes ONLY this section — never touches the manual table.
- Discrepancies between the two sections become observable findings during
  the 3-7d window. Once stable, Phase B (separate PR) deprecates the manual
  table in favor of the auto-generated one + a Notes column for human-only
  metadata.

**Why dual-section, not in-place rewrite of the existing table:**
- Rich text in current rows ("Superseded by [[ADR-010]] + [[ADR-025]]
  (de facto joint coverage, 2026-04-27)") contains info NOT mechanically
  derivable from frontmatter alone.
- Overwriting it on day 1 = data loss + breaking check-moc-integrity which
  parses status text. dual-section preserves zero-risk reversibility.

## Modes

- `--check`     : dry-read both sections, exit 1 if generator output differs
                  from current file content. Used by CI / pre-commit / cron.
- `--write`     : actually rewrite the section between markers. Idempotent.
- `--dry-run`   : print diff to stdout, exit 0.

If markers are absent, `--write` inserts the new section AFTER the existing
`## ADR Actifs` table block (just before the `---` separator that follows).
This is the only structural mutation; subsequent runs are idempotent splices.

## Notes column policy (PR-3 MVP)

NOT introduced in this PR. The Notes column is a Phase B concern (after
3-7d observation). Documented as follow-up to keep this PR <300 lines diff.

## Read paths

- ALL `ledger/decisions/adr/ADR-*.md` frontmatters.
- For each ADR with `superseded_by: ["ADR-XXX"]`, looks up target slug
  to build `[[ADR-XXX-slug]]` wikilink. Falls back to bare `ADR-XXX` text
  if target missing (rare; handled gracefully, not a fatal error since
  PR-4 strict gate will catch it via check-adr-supersedes).

## Write paths

- ONLY rewrites content between the two markers. Frontmatter `updated:` is
  refreshed to today's date if the section content changes.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import re
import sys
from pathlib import Path

from governance_constants import (
    ADR_STATUSES,
    ADR_STATUSES_VISIBLE_IN_MOC,
    LEGACY_FRONTMATTER_KEYS,
)

VAULT_ROOT = Path(__file__).resolve().parent.parent
ADR_DIR = VAULT_ROOT / "ledger" / "decisions" / "adr"
MOC_FILE = VAULT_ROOT / "ops" / "moc" / "MOC-Decisions.md"

MARKER_START = "<!-- AUTO-GENERATED:moc-decisions-canonical-index start -->"
MARKER_END = "<!-- AUTO-GENERATED:moc-decisions-canonical-index end -->"

# Status normalisation for display (canon → human-readable).
STATUS_LABEL = {
    "proposed": "Proposed",
    "accepted": "Accepted",
    "accepted-revised": "Accepted-Revised",
    "rejected": "Rejected",
    "deprecated": "Deprecated",
    "superseded": "Superseded",
    "deferred": "Deferred",
}


def parse_frontmatter(text: str) -> dict:
    """Lightweight frontmatter parser — pyyaml if available, manual fallback."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    raw = text[4:end]
    try:
        import yaml  # type: ignore
        parsed = yaml.safe_load(raw)
        return parsed if isinstance(parsed, dict) else {}
    except ImportError:
        out: dict = {}
        for line in raw.splitlines():
            m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
            if m:
                key, val = m.group(1), m.group(2).strip()
                if val.startswith("[") and val.endswith("]"):
                    inner = val[1:-1].strip()
                    out[key] = [
                        x.strip().strip('"').strip("'")
                        for x in inner.split(",")
                        if x.strip()
                    ]
                elif val in ("", "~", "null"):
                    out[key] = None
                else:
                    out[key] = val.strip('"').strip("'")
        return out


def collect_adrs() -> list[dict]:
    """Read all ADR frontmatters, return sorted list of dicts."""
    adrs: list[dict] = []
    for p in sorted(ADR_DIR.glob("ADR-*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        adr_id = fm.get("id") or _id_from_filename(p)
        if not adr_id:
            continue
        adrs.append({
            "id": adr_id,
            "title": str(fm.get("title", "")).strip().strip('"'),
            "status": str(fm.get("status", "")).strip().lower(),
            "date": str(fm.get("date", "")),
            "slug": p.stem,  # e.g. "ADR-001-environment-separation"
            "superseded_by": _as_list(fm.get("superseded_by")),
        })
    return adrs


def _id_from_filename(p: Path) -> str | None:
    m = re.match(r"^(ADR-\d{3})", p.name)
    return m.group(1) if m else None


def _as_list(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v] if v.strip() else []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return []


def render_status(adr: dict, slug_by_id: dict[str, str]) -> str:
    """Render the Status column.

    Canonical statuses → human label. For `superseded`, append the wikilinked
    targets (resolved from frontmatter superseded_by). Out-of-canon statuses
    are still rendered raw (PR-2 unmask) — these are caught upstream by
    check-frontmatter-schema if invalid.
    """
    status = adr["status"]
    label = STATUS_LABEL.get(status, status.capitalize() or "Unknown")
    if status == "superseded" and adr["superseded_by"]:
        targets = []
        for tgt in adr["superseded_by"]:
            slug = slug_by_id.get(tgt, tgt)
            targets.append(f"[[{slug}]]")
        return f"{label} by {' + '.join(targets)}"
    return label


def render_table(adrs: list[dict]) -> str:
    """Render the auto-generated canonical index table (markdown)."""
    slug_by_id = {a["id"]: a["slug"] for a in adrs}
    lines = [
        "| ID | Titre | Statut canonique | Date | Fichier |",
        "|----|-------|------------------|------|---------|",
    ]
    for a in adrs:
        # Filter to MOC-visible statuses (currently = all, see governance_constants).
        if a["status"] and a["status"] not in ADR_STATUSES_VISIBLE_IN_MOC:
            continue
        title = a["title"].replace("|", "\\|")
        status = render_status(a, slug_by_id).replace("|", "\\|")
        lines.append(
            f"| {a['id']} | {title} | {status} | {a['date']} | [[{a['slug']}]] |"
        )
    return "\n".join(lines) + "\n"


def render_section(adrs: list[dict]) -> str:
    """Full section to splice between markers, including section header."""
    today = _dt.date.today().isoformat()
    return (
        f"{MARKER_START}\n"
        f"\n"
        f"## ADR Canonical Index (auto-generated)\n"
        f"\n"
        f"> Projection mécanique du frontmatter ADR (PR-3 sync_moc_decisions).\n"
        f"> Toute édition manuelle entre les markers est écrasée à chaque sync.\n"
        f"> Pour annoter, éditer le frontmatter ADR ou la table « ADR Actifs » ci-dessus.\n"
        f"> Dernier sync : {today}.\n"
        f"\n"
        f"{render_table(adrs)}"
        f"\n"
        f"{MARKER_END}\n"
    )


def splice_section(current: str, new_section: str) -> str:
    """Replace existing markers content with new_section, or insert if absent.

    Insertion point if absent: just before the first `\\n---\\n` separator
    that follows the `## ADR Actifs` table. Falls back to end of file.
    """
    start = current.find(MARKER_START)
    end = current.find(MARKER_END)
    if start != -1 and end != -1 and end > start:
        end_inclusive = end + len(MARKER_END) + 1  # include trailing newline
        return current[:start] + new_section + current[end_inclusive:]
    # Markers absent → first-time insertion
    actifs_idx = current.find("## ADR Actifs")
    if actifs_idx == -1:
        return current.rstrip() + "\n\n" + new_section
    sep_idx = current.find("\n---\n", actifs_idx)
    if sep_idx == -1:
        return current.rstrip() + "\n\n" + new_section
    insertion_point = sep_idx + len("\n---\n")
    return current[:insertion_point] + "\n" + new_section + current[insertion_point:]


def refresh_frontmatter_updated(text: str) -> str:
    """Bump frontmatter `updated:` to today (only if frontmatter exists)."""
    today = _dt.date.today().isoformat()
    return re.sub(
        r"(?m)^updated:\s*\d{4}-\d{2}-\d{2}\s*$",
        f"updated: {today}",
        text,
        count=1,
    )


def emit_legacy_warnings(adrs: list[dict]) -> list[str]:
    """Warn for ADRs still using LEGACY_FRONTMATTER_KEYS (deciders→decision_makers)."""
    warnings: list[str] = []
    for p in sorted(ADR_DIR.glob("ADR-*.md")):
        fm = parse_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        for legacy, canonical in LEGACY_FRONTMATTER_KEYS.items():
            if legacy in fm and canonical not in fm:
                warnings.append(f"{p.name}: legacy '{legacy}' present without '{canonical}'")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="exit 1 if regen differs from file")
    g.add_argument("--write", action="store_true", help="rewrite section between markers")
    g.add_argument("--dry-run", action="store_true", help="print diff, exit 0")
    args = parser.parse_args()

    if not MOC_FILE.exists():
        print(f"ERROR: {MOC_FILE} not found", file=sys.stderr)
        return 2

    adrs = collect_adrs()
    if not adrs:
        print("ERROR: no ADRs found", file=sys.stderr)
        return 2

    current = MOC_FILE.read_text(encoding="utf-8")
    new_section = render_section(adrs)
    new_text = splice_section(current, new_section)

    # Bump updated only if real diff in section content (not just date in marker comment).
    section_changed = (
        MARKER_START not in current
        or _section_body(current) != _section_body(new_text)
    )
    if section_changed:
        new_text = refresh_frontmatter_updated(new_text)

    legacy_warnings = emit_legacy_warnings(adrs)
    for w in legacy_warnings:
        print(f"::warning:: legacy frontmatter key — {w}", file=sys.stderr)

    if args.check:
        if current != new_text:
            diff = "".join(
                difflib.unified_diff(
                    current.splitlines(keepends=True),
                    new_text.splitlines(keepends=True),
                    fromfile=str(MOC_FILE),
                    tofile=f"{MOC_FILE} (regenerated)",
                )
            )
            print(diff)
            print(
                f"::error:: MOC-Decisions.md drift detected ({len(adrs)} ADRs scanned). "
                f"Run `_scripts/sync_moc_decisions.py --write`.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: MOC-Decisions.md in sync with {len(adrs)} ADRs")
        return 0

    if args.dry_run:
        diff = "".join(
            difflib.unified_diff(
                current.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=str(MOC_FILE),
                tofile=f"{MOC_FILE} (regenerated)",
            )
        )
        print(diff if diff else "(no diff)")
        return 0

    # --write
    if current == new_text:
        print(f"OK: MOC-Decisions.md already up to date ({len(adrs)} ADRs)")
        return 0
    MOC_FILE.write_text(new_text, encoding="utf-8")
    print(f"WROTE: MOC-Decisions.md regenerated ({len(adrs)} ADRs)")
    return 0


def _section_body(text: str) -> str:
    """Extract content between markers (or empty if missing). Excludes the
    "Dernier sync" timestamp line so date-only changes don't mark a diff."""
    s = text.find(MARKER_START)
    e = text.find(MARKER_END)
    if s == -1 or e == -1:
        return ""
    body = text[s + len(MARKER_START):e]
    return re.sub(r"(?m)^>\s*Dernier sync\s*:.*$\n?", "", body)


if __name__ == "__main__":
    sys.exit(main())
