"""Tests for dual-metric stagnation (last_human_activity + last_state_change)."""
# File: _scripts/planning/tests/test_stagnation.py
from datetime import datetime, timezone

from _scripts.planning.stagnation import compute_stagnation_days


def _ts(d: str) -> datetime:
    return datetime.fromisoformat(d).replace(tzinfo=timezone.utc)


def test_uses_max_of_two_timestamps():
    now = _ts("2026-05-08T12:00:00")
    days = compute_stagnation_days(
        last_human_activity_at=_ts("2026-05-05T00:00:00"),  # 3 days ago
        last_state_change_at=_ts("2026-05-07T00:00:00"),    # 1 day ago
        now=now,
    )
    assert days == 1  # min stagnation = max(activity)


def test_human_activity_overrides_state_change_when_more_recent():
    now = _ts("2026-05-08T12:00:00")
    days = compute_stagnation_days(
        last_human_activity_at=_ts("2026-05-08T00:00:00"),  # ~0.5 day
        last_state_change_at=_ts("2026-05-01T00:00:00"),    # 7 days
        now=now,
    )
    assert days == 0


def test_returns_none_if_both_missing():
    now = _ts("2026-05-08T12:00:00")
    days = compute_stagnation_days(
        last_human_activity_at=None,
        last_state_change_at=None,
        now=now,
    )
    assert days is None
