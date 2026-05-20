"""Tests for schemas.py — YAML loader + validator."""
from pathlib import Path

import pytest

from _scripts.planning import schemas


# Resolve to repo root from this file (_scripts/planning/tests/) so tests run in
# any worktree and in CI, not just the canonical /opt deployment path.
VAULT_PATH = Path(__file__).resolve().parents[3]


def test_load_priority_returns_p0_through_p8():
    p = schemas.load_priority(VAULT_PATH)
    assert set(p.keys()) == {f"P{i}" for i in range(9)}
    assert p["P0"]["sla_hours"] == 24


def test_load_itemtype_includes_pr_adr_roadmap():
    t = schemas.load_itemtype(VAULT_PATH)
    assert {"PR", "ADR", "ROADMAP", "INCIDENT", "EPIC"} <= set(t.keys())


def test_load_blocked_reason_includes_waiting_review():
    r = schemas.load_blocked_reason(VAULT_PATH)
    assert "waiting-review" in r


def test_load_status_includes_lifecycle():
    s = schemas.load_status(VAULT_PATH)
    assert {"todo", "in-progress", "review", "blocked", "done", "cancelled"} == set(s.keys())


def test_invalid_priority_rejected():
    with pytest.raises(schemas.SchemaError, match="P9 not in canonical priorities"):
        schemas.validate_priority("P9", VAULT_PATH)


def test_invalid_itemtype_rejected():
    with pytest.raises(schemas.SchemaError, match="RANDOM not in canonical itemtypes"):
        schemas.validate_itemtype("RANDOM", VAULT_PATH)


def test_canonical_id_pr_pattern():
    cid = schemas.build_canonical_id("PR", repo="governance-vault", num=149)
    assert cid == "github:ak125/governance-vault:pr:149"


def test_canonical_id_adr_pattern():
    cid = schemas.build_canonical_id("ADR", number="053")
    assert cid == "vault:adr:ADR-053"


def test_load_worktype_includes_runtime_critical_and_experiment():
    w = schemas.load_worktype(VAULT_PATH)
    assert {"runtime-critical", "emergency", "governance", "seo-runtime",
            "observability", "cleanup", "migration", "debt", "experiment"} == set(w.keys())
    assert w["runtime-critical"]["auto_priority"] == "P0"
    assert "DoD3" in w["runtime-critical"]["requires"]


def test_worktype_auto_priority_is_valid_priority():
    w = schemas.load_worktype(VAULT_PATH)
    valid_priorities = schemas.load_priority(VAULT_PATH)
    for name, spec in w.items():
        assert spec["auto_priority"] in valid_priorities, f"{name} has invalid auto_priority"


def test_invalid_worktype_rejected():
    with pytest.raises(schemas.SchemaError, match="bogus not in canonical worktypes"):
        schemas.validate_worktype("bogus", VAULT_PATH)


def test_state_transitions_keys_are_canonical_statuses():
    transitions = schemas.load_state_transitions(VAULT_PATH)
    statuses = schemas.load_status(VAULT_PATH)
    assert set(transitions.keys()) == set(statuses.keys())


def test_state_transitions_targets_are_canonical_statuses():
    transitions = schemas.load_state_transitions(VAULT_PATH)
    statuses = set(schemas.load_status(VAULT_PATH).keys())
    for src, targets in transitions.items():
        for dst in targets:
            assert dst in statuses, f"{src}->{dst} targets unknown status"


def test_cancelled_is_terminal():
    transitions = schemas.load_state_transitions(VAULT_PATH)
    assert transitions["cancelled"] == []


def test_valid_transition_passes():
    schemas.validate_transition("todo", "in-progress", VAULT_PATH)
    schemas.validate_transition("review", "done", VAULT_PATH)


def test_invalid_transition_rejected():
    with pytest.raises(schemas.SchemaError, match="transition todo->done not allowed"):
        schemas.validate_transition("todo", "done", VAULT_PATH)


def test_transition_unknown_status_rejected():
    with pytest.raises(schemas.SchemaError, match="WIP not in canonical statuses"):
        schemas.validate_transition("WIP", "done", VAULT_PATH)


def test_required_dod_for_review_to_done():
    dod = schemas.required_dod_for_transition("review", "done", VAULT_PATH)
    assert "DoD1" in dod and "DoD7" in dod


def test_required_dod_empty_when_no_gate():
    assert schemas.required_dod_for_transition("blocked", "in-progress", VAULT_PATH) == []
