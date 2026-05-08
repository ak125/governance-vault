"""Write outputs: immutable snapshots, MOC mirror (skip-on-hash), GH Project (best-effort)."""
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class WriteResult:
    ok: bool
    error: Optional[str] = None
    items_written: int = 0


def _parse_iso(s: str) -> datetime:
    # ISO 8601 with trailing Z
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def write_snapshot(
    items: list[dict[str, Any]],
    *,
    vault_path: Path,
    generated_at: str,
    semantic_hash_value: str,
) -> Path:
    """Write canonical immutable snapshot run-{HHMMSS}Z.json + update latest.json pointer."""
    ts = _parse_iso(generated_at)
    date_dir = vault_path / "ledger/snapshots/planning" / ts.strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    run_path = date_dir / f"run-{ts.strftime('%H%M%S')}Z.json"
    payload = {
        "schema_version": "planning.v1",
        "generated_at": generated_at,
        "semantic_hash": semantic_hash_value,
        "items": items,
    }
    run_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    # Pointer (non-canonical, rewritable)
    (date_dir / "latest.json").write_text(json.dumps(payload, indent=2, sort_keys=True))
    return run_path


_HASH_RE = re.compile(r"^semantic_hash:\s*(\S+)\s*$", re.M)


def _read_moc_hash(moc_path: Path) -> Optional[str]:
    if not moc_path.exists():
        return None
    m = _HASH_RE.search(moc_path.read_text())
    return m.group(1) if m else None


def write_moc(
    moc_path: Path,
    *,
    items: list[dict[str, Any]],
    semantic_hash_value: str,
    ack_block: dict[str, Any],
) -> bool:
    """Rewrite MOC ssi semantic_hash differs. Returns True if file rewritten."""
    existing_hash = _read_moc_hash(moc_path)
    if existing_hash == semantic_hash_value:
        return False
    body = _render_moc(items=items, semantic_hash_value=semantic_hash_value, ack_block=ack_block)
    moc_path.write_text(body)
    return True


def _render_moc(*, items, semantic_hash_value, ack_block) -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    rows = "\n".join(
        f"| {i['canonical_id']} | {i.get('priority','-')} | {i.get('item_type','-')} | {i.get('status','-')} | {i.get('title','-')} |"
        for i in sorted(items, key=lambda x: (x.get('priority',''), x.get('canonical_id','')))
    ) or "| (none) | | | | |"
    ack_yaml = "ack: {}" if not ack_block else _yaml_dump_ack(ack_block)
    return f"""---
type: moc
status: proposed
updated: {today}
schema_version: planning.v1
semantic_hash: {semantic_hash_value}
adr_link: ADR-053
---

# MOC-Planning-Live

## Items actifs (auto-generated)

| canonical_id | priority | item_type | status | title |
|--------------|----------|-----------|--------|-------|
{rows}

## Ack block (édition humaine — exception I2)

```yaml
{ack_yaml}
```

## See also

- [[ADR-053-planning-live-system]]
- [[MOC-Roadmap-2026]]
"""


def _yaml_dump_ack(ack: dict[str, Any]) -> str:
    return yaml.safe_dump({"ack": ack}, default_flow_style=False).strip()


def _gh_project_upsert_one(item: dict[str, Any], project_number: int) -> None:
    """Add or update a single item in the GitHub Project v2.

    Strategy :
    - PR items (have `url`) → `gh project item-add` (idempotent : if already linked, gh
      returns success without duplication).
    - ADR/ROADMAP/INCIDENT/EPIC (no GH URL) → `gh project item-create` (draft item).
      The item title carries the canonical_id for later identification.

    Custom fields (Priority/ItemType/Status/CanonicalId/...) are NOT set here — that's
    a follow-up task post-PR-2 once we have the field-id cache loaded from project
    metadata. For PR-2 MVP, items just appear on the board with default fields ; field
    population deferred to PR-2.x or PR-3 follow-up.

    Raises subprocess.CalledProcessError on `gh` failure ; caller (write_gh_project)
    catches and converts to WriteResult(ok=False) when strict=False.
    """
    if item.get("url"):
        result = subprocess.run(
            ["gh", "project", "item-add", str(project_number),
             "--owner", "ak125", "--url", item["url"], "--format", "json"],
            check=True, capture_output=True, text=True, timeout=15,
        )
    else:
        title = f"{item['canonical_id']}: {item.get('title','(no title)')}"
        body = f"canonical_id: {item['canonical_id']}\nitem_type: {item.get('item_type','?')}"
        result = subprocess.run(
            ["gh", "project", "item-create", str(project_number),
             "--owner", "ak125", "--title", title, "--body", body, "--format", "json"],
            check=True, capture_output=True, text=True, timeout=15,
        )

    # Populate custom fields (Priority/ItemType/PlanStatus/...) — best-effort.
    # Failures here don't fail the upsert (the item is already added).
    try:
        from _scripts.planning import gh_project_fields
        item_id = json.loads(result.stdout).get("id")
        if item_id:
            gh_project_fields.populate_item_fields(item_id, item, project_number)
    except Exception:
        # Best-effort — item-add already succeeded, field population is bonus.
        pass


def write_gh_project(
    items: list[dict[str, Any]],
    *,
    project_number: int,
    strict: bool = False,
) -> WriteResult:
    """Best-effort projection to GitHub Project v2 (I1 invariant).

    Per-item failures are accumulated but don't stop the loop unless strict=True.
    Returns aggregate WriteResult with items_written count + last error message.
    """
    written = 0
    last_error: Optional[str] = None
    for it in items:
        try:
            _gh_project_upsert_one(it, project_number)
            written += 1
        except Exception as e:
            last_error = f"{it.get('canonical_id','?')}: {e}"
            if strict:
                raise
            log_msg = f"GH Project upsert failed (best-effort): {last_error}"
            # Use stderr-friendly print since logger may not be configured here
            import sys
            print(log_msg, file=sys.stderr)
    return WriteResult(ok=last_error is None, error=last_error, items_written=written)
