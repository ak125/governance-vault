"""Tests for semantic_hash — blacklist of volatile fields (I3)."""
from _scripts.planning.hash_util import semantic_hash


def _item(**overrides):
    base = {
        "canonical_id": "vault:adr:ADR-053",
        "priority": "P1",
        "item_type": "ADR",
        "status": "review",
        "blocked_reason": None,
        "owner": "fafa",
        "depends_on": [],
        "adr_link": "ADR-053",
        "title": "Planning Live System",
        # Volatile fields (must be ignored by hash):
        "last_alert_at": "2026-05-08T08:00:00Z",
        "acked_at": None,
        "mute_until": None,
        "stagnation_days": 5,
        "generated_at": "2026-05-08T12:00:00Z",
        "schema_version": "planning.v1",
        "source_status": "proposed",
    }
    base.update(overrides)
    return base


def test_same_canonical_fields_same_hash():
    a = _item()
    b = _item(stagnation_days=999, generated_at="2099-01-01T00:00:00Z")
    assert semantic_hash([a]) == semantic_hash([b])


def test_changing_priority_changes_hash():
    a = _item()
    b = _item(priority="P0")
    assert semantic_hash([a]) != semantic_hash([b])


def test_changing_status_changes_hash():
    a = _item()
    b = _item(status="done")
    assert semantic_hash([a]) != semantic_hash([b])


def test_changing_alert_volatile_does_not_change_hash():
    a = _item()
    b = _item(last_alert_at="2099-01-01T00:00:00Z", acked_at="2099-01-01T00:00:00Z")
    assert semantic_hash([a]) == semantic_hash([b])


def test_changing_source_status_does_not_change_hash():
    """source_status is upstream raw; canonical status is what matters for I3."""
    a = _item()
    b = _item(source_status="accepted")
    assert semantic_hash([a]) == semantic_hash([b])


def test_order_independent():
    a = _item(canonical_id="vault:adr:ADR-001")
    b = _item(canonical_id="vault:adr:ADR-999")
    assert semantic_hash([a, b]) == semantic_hash([b, a])
