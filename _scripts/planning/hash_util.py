"""Compute semantic_hash over canonical projection (I3 blacklist)."""
import hashlib
import json
from typing import Any


CANONICAL_FIELDS = (
    "canonical_id",
    "priority",
    "item_type",
    "status",
    "blocked_reason",
    "owner",
    "depends_on",
    "adr_link",
    "title",
)


def _canonical_projection(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    projected = [
        {k: item.get(k) for k in CANONICAL_FIELDS}
        for item in items
    ]
    projected.sort(key=lambda i: i.get("canonical_id") or "")
    return projected


def semantic_hash(items: list[dict[str, Any]]) -> str:
    payload = json.dumps(_canonical_projection(items), sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
