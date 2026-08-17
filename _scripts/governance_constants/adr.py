"""ADR governance enums — mirror of _scripts/schemas/adr.schema.json.

STRICT SCOPE: data only (frozenset literals + named subsets). No imports
other than __future__, no def, no class. See package __init__ for rationale.
"""
from __future__ import annotations

ADR_STATUSES: frozenset[str] = frozenset({
    "proposed",
    "accepted",
    "accepted-revised",
    "rejected",
    "deprecated",
    "superseded",
    "deferred",
})

# Statuses considered "active" for runtime consistency checks.
ADR_STATUSES_ACTIVE: frozenset[str] = frozenset({
    "accepted",
    "accepted-revised",
})

# Historical terminal statuses. Pre-declared (mental model frozen) even if not
# yet consumed — avoids re-wiring 15 scripts later when MOC main becomes noisy.
#
# STRICT RULES on derived subsets (ARCHIVED, ACTIVE, VISIBLE_IN_MOC):
# 1. MUST remain STATIC declarations (frozenset literal)
# 2. MUST be strict subset/superset of a canonical enum (no free composition)
# 3. MUST be purely declarative (no business logic encoded in the name)
# 4. FORBIDDEN: names that encode business policy
#    ❌ ADR_STATUSES_DEPLOYABLE   (deployable = policy)
#    ❌ ADR_STATUSES_RUNTIME_VISIBLE (visibility runtime = policy)
#    ❌ ADR_STATUSES_PUBLIC       (public/private = policy)
#    ✅ ADR_STATUSES_ACTIVE       (lifecycle terminology, descriptive)
#    ✅ ADR_STATUSES_ARCHIVED     (lifecycle terminology, descriptive)
#    ✅ ADR_STATUSES_VISIBLE_IN_MOC (rendering scope, declarative)
ADR_STATUSES_ARCHIVED: frozenset[str] = frozenset({
    "deprecated",
    "rejected",
    "deferred",
    "superseded",
})

# ADRs visible in MOC-Decisions: today = all (preserve historical traceability,
# equivalent to ADR_STATUSES). check-moc-integrity previously used a subset
# that silently masked deprecated/rejected.
# Future Phase B migration: VISIBLE_IN_MAIN_MOC = ACTIVE | {proposed},
# archived mapped to MOC-Decisions-Archive separately. Do NOT do this before
# empirical signal.
ADR_STATUSES_VISIBLE_IN_MOC: frozenset[str] = ADR_STATUSES
