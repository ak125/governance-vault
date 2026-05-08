"""GitHub Project v2 custom field population (ADR-053 follow-up).

Wraps `gh project item-add` + `gh project item-edit` to set Priority/ItemType/
PlanStatus/BlockedReason/Owner/StagnationDays/DependsOn/AdrLink/CanonicalId
custom fields per item. Enables Kanban views colored by Priority etc.

Best-effort: any subprocess error is logged + swallowed (caller decides strict).
Field map cached per process — fetched once on first call via gh CLI.
"""
import json
import logging
import re
import subprocess
from typing import Any, Optional


log = logging.getLogger("planning.gh_fields")


_FIELD_MAP_CACHE: Optional[dict[str, Any]] = None
_OWNER = "ak125"


def _camel_to_snake(name: str) -> str:
    """Convert 'PlanStatus' → 'plan_status', 'ItemType' → 'itemtype' (no underscore inside compound)."""
    # Insert underscore before uppercase letters (except first), then lowercase.
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    # Special: 'item_type' from 'ItemType' is correct, but our ADR uses 'itemtype' (no _)
    # Keep both formats by storing both keys in dict.
    return s


def get_field_map(project_number: int) -> dict[str, Any]:
    """Fetch + cache project_id + all custom fields with their options.

    Returns: {
        "project_id": "PVT_xxx",
        "fields": {
            "priority": {"id": "PVTSSF_xxx", "options": {"P0": "abc", "P1": "def", ...}},
            "itemtype": {"id": "PVTSSF_xxx", "options": {"PR": "...", ...}},
            ...
        }
    }
    """
    global _FIELD_MAP_CACHE
    if _FIELD_MAP_CACHE is not None:
        return _FIELD_MAP_CACHE

    try:
        view = subprocess.run(
            ["gh", "project", "view", str(project_number),
             "--owner", _OWNER, "--format", "json"],
            check=True, capture_output=True, text=True, timeout=15,
        )
        project_id = json.loads(view.stdout)["id"]

        flist = subprocess.run(
            ["gh", "project", "field-list", str(project_number),
             "--owner", _OWNER, "--format", "json", "--limit", "30"],
            check=True, capture_output=True, text=True, timeout=15,
        )
        fields_raw = json.loads(flist.stdout)["fields"]
    except Exception as e:
        log.warning("get_field_map failed: %s", e)
        return {"project_id": None, "fields": {}}

    fields = {}
    for f in fields_raw:
        name = f["name"]
        snake = _camel_to_snake(name)
        # Also add a no-underscore variant for compound names like "ItemType" → "itemtype"
        nosep = name.lower()
        entry: dict[str, Any] = {"id": f["id"], "type": f.get("type", "")}
        if "options" in f:
            entry["options"] = {opt["name"]: opt["id"] for opt in f["options"]}
        fields[snake] = entry
        if nosep != snake:
            fields[nosep] = entry

    _FIELD_MAP_CACHE = {"project_id": project_id, "fields": fields}
    return _FIELD_MAP_CACHE


def _gh_edit(args: list[str]) -> bool:
    """Run `gh project item-edit` best-effort. Returns True on success."""
    try:
        subprocess.run(
            ["gh", "project", "item-edit"] + args,
            check=True, capture_output=True, text=True, timeout=15,
        )
        return True
    except Exception as e:
        log.warning("item-edit failed (%s): %s", " ".join(args[:6]), e)
        return False


def set_select_field(
    item_id: str,
    project_id: str,
    field: dict[str, Any],
    value: Optional[str],
) -> bool:
    """Set a single-select field value by option name. Skip if value None or option unknown."""
    if not value or "options" not in field:
        return False
    option_id = field["options"].get(value)
    if not option_id:
        log.debug("option %r not in field %s", value, field.get("id"))
        return False
    return _gh_edit([
        "--id", item_id, "--project-id", project_id,
        "--field-id", field["id"], "--single-select-option-id", option_id,
    ])


def set_text_field(
    item_id: str,
    project_id: str,
    field: dict[str, Any],
    value: Optional[str],
) -> bool:
    if not value:
        return False
    return _gh_edit([
        "--id", item_id, "--project-id", project_id,
        "--field-id", field["id"], "--text", str(value),
    ])


def set_number_field(
    item_id: str,
    project_id: str,
    field: dict[str, Any],
    value: Optional[float],
) -> bool:
    if value is None:
        return False
    return _gh_edit([
        "--id", item_id, "--project-id", project_id,
        "--field-id", field["id"], "--number", str(value),
    ])


_PLAN_TO_GH_STATUS = {
    "todo": "Todo",
    "in-progress": "In Progress",
    "review": "In Progress",   # PR in review IS being worked on (board UX)
    "blocked": "In Progress",  # blocked items still alive — keep visible
    "done": "Done",
    "cancelled": "Done",       # closed without delivery — out of board
}


def _map_plan_status_to_gh_status(plan_status: Optional[str]) -> Optional[str]:
    """Map our 6-value planning-status.yml to GH default Status's 3 options.

    Lossy but pragmatic : the default Kanban view is grouped by GH Status,
    so populating it makes the board immediately useful without UI configuration.
    """
    if not plan_status:
        return None
    return _PLAN_TO_GH_STATUS.get(plan_status)


def populate_item_fields(item_id: str, item: dict[str, Any], project_number: int) -> dict[str, bool]:
    """Set all 9 custom fields for an item. Returns per-field success map (best-effort).

    item dict is expected to have keys (per planning canon):
      canonical_id, priority, item_type, status, blocked_reason, owner,
      depends_on (list), adr_link, stagnation_days
    """
    fmap = get_field_map(project_number)
    project_id = fmap.get("project_id")
    fields = fmap.get("fields", {})
    if not project_id or not fields:
        return {}

    results: dict[str, bool] = {}

    # Single-select fields
    if "priority" in fields:
        results["priority"] = set_select_field(item_id, project_id, fields["priority"], item.get("priority"))
    if "itemtype" in fields:
        results["itemtype"] = set_select_field(item_id, project_id, fields["itemtype"], item.get("item_type"))
    if "plan_status" in fields:
        results["plan_status"] = set_select_field(item_id, project_id, fields["plan_status"], item.get("status"))
    if "blocked_reason" in fields and item.get("blocked_reason"):
        results["blocked_reason"] = set_select_field(item_id, project_id, fields["blocked_reason"], item["blocked_reason"])

    # Default GH Status field (3-option : Todo/In Progress/Done) — drives the
    # default Kanban view shown when user opens the project for the first time.
    # Maps our 6 canon plan-status values onto GH's 3 — lossy but useful for UX.
    if "status" in fields:
        gh_status_value = _map_plan_status_to_gh_status(item.get("status"))
        if gh_status_value:
            results["gh_status"] = set_select_field(item_id, project_id, fields["status"], gh_status_value)

    # Text fields
    if "owner" in fields and item.get("owner"):
        results["owner"] = set_text_field(item_id, project_id, fields["owner"], item["owner"])
    if "canonical_id" in fields:
        results["canonical_id"] = set_text_field(item_id, project_id, fields["canonical_id"], item.get("canonical_id"))
    if "adr_link" in fields and item.get("adr_link"):
        results["adr_link"] = set_text_field(item_id, project_id, fields["adr_link"], item["adr_link"])
    if "depends_on" in fields and item.get("depends_on"):
        deps = ",".join(item["depends_on"]) if isinstance(item["depends_on"], list) else str(item["depends_on"])
        if deps:
            results["depends_on"] = set_text_field(item_id, project_id, fields["depends_on"], deps)

    # Number fields
    if "stagnation_days" in fields and item.get("stagnation_days") is not None:
        results["stagnation_days"] = set_number_field(item_id, project_id, fields["stagnation_days"], item["stagnation_days"])

    return results
