"""Load + validate canonical YAML schemas under .spec/00-canon/planning/."""
from pathlib import Path
from typing import Any

import yaml


SCHEMA_DIR = Path(".spec/00-canon/planning")


class SchemaError(ValueError):
    """Raised when a value violates a canonical schema."""


def _load(vault_path: Path, name: str) -> dict[str, Any]:
    p = vault_path / SCHEMA_DIR / f"{name}.yml"
    if not p.exists():
        raise SchemaError(f"Schema not found: {p}")
    with p.open() as f:
        return yaml.safe_load(f)


def load_priority(vault_path: Path) -> dict[str, dict[str, Any]]:
    return _load(vault_path, "planning-priority")["priorities"]


def load_itemtype(vault_path: Path) -> dict[str, dict[str, Any]]:
    return _load(vault_path, "planning-itemtype")["types"]


def load_blocked_reason(vault_path: Path) -> dict[str, str]:
    return _load(vault_path, "planning-blocked-reason")["reasons"]


def load_status(vault_path: Path) -> dict[str, str]:
    return _load(vault_path, "planning-status")["statuses"]


def validate_priority(p: str, vault_path: Path) -> None:
    valid = load_priority(vault_path)
    if p not in valid:
        raise SchemaError(f"{p} not in canonical priorities {sorted(valid)}")


def validate_itemtype(t: str, vault_path: Path) -> None:
    valid = load_itemtype(vault_path)
    if t not in valid:
        raise SchemaError(f"{t} not in canonical itemtypes {sorted(valid)}")


def build_canonical_id(item_type: str, **kwargs: Any) -> str:
    if item_type == "PR":
        return f"github:ak125/{kwargs['repo']}:pr:{kwargs['num']}"
    if item_type == "ADR":
        return f"vault:adr:ADR-{kwargs['number']}"
    if item_type == "ROADMAP":
        return f"vault:moc-roadmap-2026:item:{kwargs['slug']}"
    if item_type == "INCIDENT":
        return f"vault:incident:{kwargs['slug']}"
    if item_type == "EPIC":
        return f"vault:planning-live:epic:{kwargs['slug']}"
    raise SchemaError(f"Unknown item_type: {item_type}")
