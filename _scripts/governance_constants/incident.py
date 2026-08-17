"""Incident governance enums — mirror of _scripts/schemas/incident.schema.json.

STRICT SCOPE: data only (frozenset literals). No imports other than __future__,
no def, no class. See package __init__ for rationale.
"""
from __future__ import annotations

INCIDENT_STATUSES: frozenset[str] = frozenset({
    "open", "investigating", "mitigated", "resolved",
    "closed", "closed-with-followup", "closed-with-structural-fix",
})
