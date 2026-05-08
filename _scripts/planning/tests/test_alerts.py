"""Tests for alerts.py — cooldown 24h + ack preservation + best-effort fallback."""
from datetime import datetime, timedelta, timezone

from _scripts.planning import alerts


NOW = datetime(2026, 5, 8, 12, 0, 0, tzinfo=timezone.utc)


def test_p0_stagnant_24h_triggers_alert():
    items = [{"canonical_id": "x", "priority": "P0", "stagnation_days": 1,
              "title": "T", "url": "u"}]
    ack = {}
    targets = alerts.compute_alert_targets(items, ack_block=ack, now=NOW)
    assert len(targets) == 1


def test_p1_does_not_trigger_alert():
    items = [{"canonical_id": "x", "priority": "P1", "stagnation_days": 10}]
    targets = alerts.compute_alert_targets(items, ack_block={}, now=NOW)
    assert targets == []


def test_recent_alert_suppressed_by_cooldown():
    items = [{"canonical_id": "x", "priority": "P0", "stagnation_days": 5}]
    ack = {"x": {"last_alert_at": (NOW - timedelta(hours=1)).isoformat()}}
    targets = alerts.compute_alert_targets(items, ack_block=ack, now=NOW)
    assert targets == []


def test_alert_24h_old_not_suppressed():
    items = [{"canonical_id": "x", "priority": "P0", "stagnation_days": 5}]
    ack = {"x": {"last_alert_at": (NOW - timedelta(hours=25)).isoformat()}}
    targets = alerts.compute_alert_targets(items, ack_block=ack, now=NOW)
    assert len(targets) == 1


def test_acked_with_mute_until_suppresses():
    items = [{"canonical_id": "x", "priority": "P0", "stagnation_days": 5}]
    ack = {"x": {"acked_at": NOW.isoformat(),
                   "mute_until": (NOW + timedelta(days=7)).isoformat()}}
    targets = alerts.compute_alert_targets(items, ack_block=ack, now=NOW)
    assert targets == []


# ---------------------------------------------------------------------------
# Ack-block helpers tests (Task 3.3) — read/update/write
# ---------------------------------------------------------------------------


def test_read_ack_block_returns_dict_when_present(tmp_path):
    moc = tmp_path / "MOC.md"
    moc.write_text("""---
type: moc
---
body
```yaml
ack:
  "vault:adr:ADR-053":
    last_alert_at: 2026-05-08T08:00:00Z
```
""")
    ack = alerts.read_ack_block(moc)
    assert "vault:adr:ADR-053" in ack
    assert ack["vault:adr:ADR-053"]["last_alert_at"] == "2026-05-08T08:00:00Z"


def test_read_ack_block_returns_empty_when_absent(tmp_path):
    moc = tmp_path / "MOC.md"
    moc.write_text("# no ack block\n")
    assert alerts.read_ack_block(moc) == {}


def test_update_last_alert_at_sets_iso_for_fired_ids():
    ack = {"x": {"acked_by": "fafa"}}
    new = alerts.update_last_alert_at(ack, fired_ids=["x", "y"], now=NOW)
    assert new["x"]["last_alert_at"] == "2026-05-08T12:00:00+00:00"
    assert new["y"]["last_alert_at"] == "2026-05-08T12:00:00+00:00"
    assert new["x"]["acked_by"] == "fafa"  # preserves existing keys


def test_write_ack_update_returns_true_on_change(tmp_path):
    moc = tmp_path / "MOC.md"
    moc.write_text("""---
type: moc
---
body
```yaml
ack: {}
```
""")
    changed = alerts.write_ack_update(moc, ack_block={"x": {"last_alert_at": "2026-05-08T12:00:00Z"}})
    assert changed is True
    assert "last_alert_at" in moc.read_text()


def test_write_ack_update_returns_false_when_unchanged(tmp_path):
    moc = tmp_path / "MOC.md"
    moc.write_text("""---
type: moc
---
body
```yaml
ack:
  x:
    last_alert_at: 2026-05-08T12:00:00Z
```
""")
    changed = alerts.write_ack_update(moc, ack_block={"x": {"last_alert_at": "2026-05-08T12:00:00Z"}})
    assert changed is False
