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
