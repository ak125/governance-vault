"""Tests for schemas.py — YAML loader + validator."""
from pathlib import Path

import pytest

from _scripts.planning import schemas


VAULT_PATH = Path("/opt/automecanik/governance-vault")


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
