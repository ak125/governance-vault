"""MOC governance enums — mirror of _scripts/schemas/moc.schema.json.

STRICT SCOPE: data only (frozenset literals). No imports other than __future__,
no def, no class. See package __init__ for rationale.
"""
from __future__ import annotations

MOC_STATUSES: frozenset[str] = frozenset({
    "canon", "draft",
})
