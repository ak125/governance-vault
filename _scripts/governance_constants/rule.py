"""Rule governance enums — mirror of _scripts/schemas/rule.schema.json.

STRICT SCOPE: data only (frozenset literals). No imports other than __future__,
no def, no class. See package __init__ for rationale.
"""
from __future__ import annotations

RULE_STATUSES: frozenset[str] = frozenset({
    "canon", "draft", "deprecated", "superseded",
})

RULE_TYPES: frozenset[str] = frozenset({
    "rule", "rules-document",
    # NB: "canon" historically present in schema, removed in PR-2 atomic with
    # PR-1 normalization (4 files `type: canon` → `rules-document`).
    # `canon` reserved for the `status` field only (anti-ambiguity).
})
