"""Source unique des enums gouvernance (statuts ADR/rule/MOC/incident).

# IMPORTANT — DERIVED MIRROR, NOT CANONICAL SOURCE
# ================================================
# This package is NOT the canonical source.
# JSON Schemas (_scripts/schemas/*.schema.json) remain the canonical authority.
# This package is a runtime PROJECTION optimized for Python scripts that
# need to filter / group / compare statuses without parsing JSON every call.
#
# How to evolve:
#   1. Modify the relevant *.schema.json (canonical change).
#   2. Update the matching submodule in the SAME commit to reflect the change.
#   3. test_governance_constants.py will fail loudly if you forget step 2.
#
# Drift policy:
#   - The ONLY script allowed to parse `*.schema.json` for enums at runtime
#     is `test_governance_constants.py` (parity test).
#   - Any other script that wants enum values MUST import from this package.
#   - Scanned by `check-no-direct-schema-enum-access.sh` in weekly-lint.
#
# Scope of the parity mirror:
#   - Only schemas with a `properties.status.enum` are mirrored here.
#     Currently: adr, rule, moc, incident. Vehicle/tombstones schemas are
#     not gouvernance artefacts and are explicitly out of scope.
#
# Package layout (split atomic per submodule — anti god-registry):
#   _scripts/governance_constants/
#     __init__.py     ← this file: facade re-exports for backward compat
#     adr.py          ← ADR_STATUSES + 3 named subsets
#     rule.py         ← RULE_STATUSES + RULE_TYPES
#     moc.py          ← MOC_STATUSES
#     incident.py     ← INCIDENT_STATUSES
#     lifecycle.py    ← LEGACY_FRONTMATTER_KEYS
#
#   Add a new enum family → new submodule, never grow an existing one.
#
# STRICT SCOPE RULES — ENFORCED BY TestPurity:
#   Each submodule contains ONLY:
#      - canonical enum sets (frozenset[str]) mirrors of schemas
#      - compatibility aliases (e.g. LEGACY_FRONTMATTER_KEYS) with migration plan
#      - named subsets (ARCHIVED, ACTIVE, VISIBLE_IN_MOC) that remain
#        _enum projections_, not runtime decisions
#   Forbidden in submodules:
#      - imports other than `from __future__ import ...`
#      - routing / handoff / dispatch logic (= business policy)
#      - lifecycle orchestration decisions (= state machine)
#      - cross-repo / cross-domain rules (= governance engine)
#      - semantic transformations (= renderer)
#      - computed `def foo(...)` functions (TestPurity detects these)
#   If any of these needs arises → create a separate module
#   (`governance_policies.py`, `lifecycle_engine.py`, `governance_renderers.py`).
#
# This __init__.py is exempt from "no imports" rule — its sole purpose is
# re-exporting submodule symbols for backward compat (`from governance_constants
# import ADR_STATUSES` unchanged after split). TestPurity allows internal
# package imports (`from .X import ...`) here but nothing else.
"""
from __future__ import annotations

from .adr import (
    ADR_STATUSES,
    ADR_STATUSES_ACTIVE,
    ADR_STATUSES_ARCHIVED,
    ADR_STATUSES_VISIBLE_IN_MOC,
)
from .incident import INCIDENT_STATUSES
from .lifecycle import LEGACY_FRONTMATTER_KEYS
from .moc import MOC_STATUSES
from .rule import RULE_STATUSES, RULE_TYPES

__all__ = [
    "ADR_STATUSES",
    "ADR_STATUSES_ACTIVE",
    "ADR_STATUSES_ARCHIVED",
    "ADR_STATUSES_VISIBLE_IN_MOC",
    "INCIDENT_STATUSES",
    "LEGACY_FRONTMATTER_KEYS",
    "MOC_STATUSES",
    "RULE_STATUSES",
    "RULE_TYPES",
]
