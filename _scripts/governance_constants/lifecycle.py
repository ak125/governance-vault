"""Lifecycle aliases — compatibility shims for legacy frontmatter keys.

STRICT SCOPE: data only (dict literal). No imports other than __future__,
no def, no class. See package __init__ for rationale.
"""
from __future__ import annotations

# Legacy frontmatter aliases — keys to migrate in a dedicated PR.
# Referenced by sync-moc-decisions.py for the fallback (deciders OR
# decision_makers). Logged as warning at each sync to make the debt visible
# and resorbable.
LEGACY_FRONTMATTER_KEYS: dict[str, str] = {
    "deciders": "decision_makers",
}
