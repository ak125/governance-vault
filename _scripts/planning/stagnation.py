"""Dual-metric stagnation: max(last_human_activity_at, last_state_change_at)."""
from datetime import datetime
from typing import Optional


def compute_stagnation_days(
    *,
    last_human_activity_at: Optional[datetime],
    last_state_change_at: Optional[datetime],
    now: datetime,
) -> Optional[int]:
    candidates = [t for t in (last_human_activity_at, last_state_change_at) if t is not None]
    if not candidates:
        return None
    most_recent = max(candidates)
    return (now - most_recent).days
