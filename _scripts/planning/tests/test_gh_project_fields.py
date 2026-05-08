"""Tests for gh_project_fields.py — best-effort field population.

Mocks subprocess.run to avoid real gh CLI calls.
"""
import json
from unittest.mock import patch

from _scripts.planning import gh_project_fields


def _mock_subprocess_view_then_fieldlist():
    """Returns side-effect list for subprocess.run mock : view, then field-list."""
    view_out = json.dumps({"id": "PVT_test", "number": 99})
    field_list_out = json.dumps({
        "fields": [
            {"id": "PVTF_title", "name": "Title", "type": "ProjectV2Field"},
            {"id": "PVTSSF_priority", "name": "Priority", "type": "ProjectV2SingleSelectField",
             "options": [{"id": "opt_p0", "name": "P0"}, {"id": "opt_p1", "name": "P1"}]},
            {"id": "PVTSSF_itemtype", "name": "ItemType", "type": "ProjectV2SingleSelectField",
             "options": [{"id": "opt_pr", "name": "PR"}, {"id": "opt_adr", "name": "ADR"}]},
            {"id": "PVTSSF_planstatus", "name": "PlanStatus", "type": "ProjectV2SingleSelectField",
             "options": [{"id": "opt_review", "name": "review"}, {"id": "opt_done", "name": "done"}]},
            {"id": "PVTF_canonicalid", "name": "CanonicalId", "type": "ProjectV2Field"},
            {"id": "PVTF_owner", "name": "Owner", "type": "ProjectV2Field"},
            {"id": "PVTF_stagnationdays", "name": "StagnationDays", "type": "ProjectV2Field"},
        ]
    })

    class FakeResult:
        def __init__(self, stdout):
            self.stdout = stdout

    return [FakeResult(view_out), FakeResult(field_list_out)]


def _reset_cache():
    gh_project_fields._FIELD_MAP_CACHE = None


def test_get_field_map_builds_dict_keyed_by_snake_case():
    _reset_cache()
    with patch.object(gh_project_fields.subprocess, "run") as mock_run:
        mock_run.side_effect = _mock_subprocess_view_then_fieldlist()
        fmap = gh_project_fields.get_field_map(99)

    assert fmap["project_id"] == "PVT_test"
    fields = fmap["fields"]
    assert "priority" in fields
    assert "itemtype" in fields  # nosep variant from "ItemType"
    assert "plan_status" in fields  # snake_case from "PlanStatus"
    assert fields["priority"]["id"] == "PVTSSF_priority"
    assert fields["priority"]["options"]["P0"] == "opt_p0"


def test_get_field_map_returns_empty_on_subprocess_failure():
    _reset_cache()
    with patch.object(gh_project_fields.subprocess, "run", side_effect=RuntimeError("API down")):
        fmap = gh_project_fields.get_field_map(99)

    assert fmap == {"project_id": None, "fields": {}}


def test_set_select_field_skips_when_option_unknown():
    field = {"id": "PVTSSF_x", "options": {"P0": "opt_p0", "P1": "opt_p1"}}
    with patch.object(gh_project_fields.subprocess, "run") as mock_run:
        result = gh_project_fields.set_select_field("ITEM_1", "PVT_x", field, "P9_BAD")
    assert result is False
    mock_run.assert_not_called()


def test_set_select_field_calls_gh_with_option_id():
    field = {"id": "PVTSSF_x", "options": {"P0": "opt_p0", "P1": "opt_p1"}}
    with patch.object(gh_project_fields.subprocess, "run") as mock_run:
        result = gh_project_fields.set_select_field("ITEM_1", "PVT_x", field, "P0")
    assert result is True
    args = mock_run.call_args[0][0]
    assert "item-edit" in args
    assert "--single-select-option-id" in args
    assert "opt_p0" in args


def test_set_text_field_skips_when_value_empty():
    field = {"id": "PVTF_x"}
    with patch.object(gh_project_fields.subprocess, "run") as mock_run:
        assert gh_project_fields.set_text_field("ITEM_1", "PVT_x", field, "") is False
        assert gh_project_fields.set_text_field("ITEM_1", "PVT_x", field, None) is False
    mock_run.assert_not_called()


def test_set_number_field_handles_zero():
    field = {"id": "PVTF_x"}
    with patch.object(gh_project_fields.subprocess, "run") as mock_run:
        assert gh_project_fields.set_number_field("ITEM_1", "PVT_x", field, 0) is True
        assert gh_project_fields.set_number_field("ITEM_1", "PVT_x", field, None) is False
    # 0 IS a valid stagnation_days value, must be set
    args = mock_run.call_args[0][0]
    assert "--number" in args


def test_populate_item_fields_skips_unknown_fields_and_returns_results():
    _reset_cache()
    with patch.object(gh_project_fields.subprocess, "run") as mock_run:
        # First 2 calls are for get_field_map, then per-field calls
        mock_run.side_effect = _mock_subprocess_view_then_fieldlist() + [
            type("FR", (), {"stdout": ""})() for _ in range(20)
        ]
        item = {
            "canonical_id": "vault:adr:ADR-053",
            "priority": "P0",
            "item_type": "ADR",
            "status": "review",
            "blocked_reason": None,
            "owner": "fafa",
            "depends_on": [],
            "adr_link": "ADR-053",
            "title": "Planning Live System",
            "stagnation_days": 0,
        }
        results = gh_project_fields.populate_item_fields("ITEM_1", item, 99)

    # Priority/ItemType/PlanStatus called (single-select success)
    assert results.get("priority") is True
    assert results.get("itemtype") is True
    assert results.get("plan_status") is True
    # Owner/CanonicalId text set
    assert results.get("owner") is True
    assert results.get("canonical_id") is True
    # StagnationDays=0 IS a valid value
    assert results.get("stagnation_days") is True
    # blocked_reason None → skipped (not in results)
    assert "blocked_reason" not in results
    # depends_on empty list → skipped
    assert "depends_on" not in results
