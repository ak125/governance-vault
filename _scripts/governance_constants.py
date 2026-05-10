"""Source unique des enums gouvernance (statuts ADR/rule/MOC/incident).

# IMPORTANT — DERIVED MIRROR, NOT CANONICAL SOURCE
# ================================================
# governance_constants.py is NOT the canonical source.
# JSON Schemas (_scripts/schemas/*.schema.json) remain the canonical authority.
# This module is a runtime PROJECTION optimized for Python scripts that
# need to filter / group / compare statuses without parsing JSON every call.
#
# How to evolve:
#   1. Modify the relevant *.schema.json (canonical change).
#   2. Update this file in the SAME commit to reflect the change.
#   3. test_governance_constants.py will fail loudly if you forget step 2.
#
# Drift policy:
#   - The ONLY script allowed to parse `*.schema.json` for enums at runtime
#     is `test_governance_constants.py` (parity test).
#   - Any other script that wants enum values MUST import from this module.
#   - Scanned by `check-no-direct-schema-enum-access.sh` in weekly-lint.
#
# Scope of the parity mirror:
#   - Only schemas with a `properties.status.enum` are mirrored here.
#     Currently: adr, rule, moc, incident. Vehicle/tombstones schemas are
#     not gouvernance artefacts and are explicitly out of scope.
#
# Split threshold (anti god-registry — strict thresholds):
#   - >120 LOC (force early split)
#   - OR 4 enum families max
#   - OR first lifecycle alias added
#   - OR first non-trivial composition (subset OR superset)
#   Trigger any one = split into submodules:
#     _scripts/governance_constants/{adr,rule,moc,incident,lifecycle}.py
#     with __init__.py re-exporting everything for backward compat.
#
# STRICT SCOPE RULE — ENFORCED BY TestPurity:
#   This file contains ONLY:
#      - canonical enum sets (frozenset[str]) mirrors of schemas
#      - compatibility aliases (e.g. LEGACY_FRONTMATTER_KEYS) with migration plan
#      - named subsets (ARCHIVED, ACTIVE, VISIBLE_IN_MOC) that remain
#        _enum projections_, not runtime decisions
#   Forbidden:
#      - imports other than `from __future__ import ...`
#      - routing / handoff / dispatch logic (= business policy)
#      - lifecycle orchestration decisions (= state machine)
#      - cross-repo / cross-domain rules (= governance engine)
#      - semantic transformations (= renderer)
#      - computed `def foo(...)` functions (TestPurity detects these)
#   If any of these needs arises → create a separate module
#   (`governance_policies.py`, `lifecycle_engine.py`, `governance_renderers.py`).
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

RULE_STATUSES: frozenset[str] = frozenset({
    "canon", "draft", "deprecated", "superseded",
})

MOC_STATUSES: frozenset[str] = frozenset({
    "canon", "draft",
})

INCIDENT_STATUSES: frozenset[str] = frozenset({
    "open", "investigating", "mitigated", "resolved",
    "closed", "closed-with-followup", "closed-with-structural-fix",
})

RULE_TYPES: frozenset[str] = frozenset({
    "rule", "rules-document",
    # NB: "canon" historically present in schema, removed in PR-2 atomic with
    # PR-1 normalization (4 files `type: canon` → `rules-document`).
    # `canon` reserved for the `status` field only (anti-ambiguity).
})

# Legacy frontmatter aliases — keys to migrate in a dedicated PR.
# Referenced by sync-moc-decisions.py for the fallback (deciders OR
# decision_makers). Logged as warning at each sync to make the debt visible
# and resorbable.
LEGACY_FRONTMATTER_KEYS: dict[str, str] = {
    "deciders": "decision_makers",
}
