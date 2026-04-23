#!/usr/bin/env python3
"""check-frontmatter-schema.py — Valide le frontmatter YAML des .md du vault contre les JSON schemas.

Usage:
  python3 _scripts/check-frontmatter-schema.py [VAULT_PATH] [--json] [--dry-run]

Types detectes par path:
  - ledger/decisions/adr/ADR-*.md    -> adr.schema.json (required)
  - ops/moc/MOC-*.md                 -> moc.schema.json (required)
  - ledger/incidents/YYYY/*.md       -> incident.schema.json (required)
  - ledger/rules/rules-*.md          -> rule.schema.json (optional frontmatter)

Exit 0 si aucune violation, 1 sinon (errors), 0 + warnings imprimes sinon.
Ne modifie AUCUN fichier.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def _stringify_dates(obj):
    """YAML parse 2026-04-18 en datetime.date; on convertit en str pour matcher les schemas."""
    import datetime as _dt
    if isinstance(obj, (_dt.date, _dt.datetime)):
        return obj.isoformat()[:10] if isinstance(obj, _dt.date) and not isinstance(obj, _dt.datetime) else obj.isoformat()
    if isinstance(obj, dict):
        return {k: _stringify_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_stringify_dates(v) for v in obj]
    return obj


def find_frontmatter(text: str) -> tuple[dict | None, str | None]:
    """Extract YAML frontmatter from a markdown file. Returns (parsed_dict, raw_yaml) or (None, None)."""
    if not text.startswith("---\n"):
        return None, None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, None
    raw = text[4:end]
    try:
        import yaml  # type: ignore
        parsed = yaml.safe_load(raw)
        if not isinstance(parsed, dict):
            return None, raw
        return _stringify_dates(parsed), raw
    except ImportError:
        parsed = {}
        for line in raw.splitlines():
            if ":" not in line or line.lstrip().startswith("#"):
                continue
            key, _, val = line.partition(":")
            parsed[key.strip()] = val.strip().strip('"').strip("'")
        return parsed, raw


def classify(rel_path: str) -> str | None:
    """Map relative path to schema type."""
    if re.match(r"ledger/decisions/adr/ADR-\d+.*\.md$", rel_path):
        return "adr"
    if re.match(r"ops/moc/MOC-.*\.md$", rel_path):
        return "moc"
    if re.match(r"ledger/incidents/\d{4}/.*\.md$", rel_path):
        return "incident"
    if re.match(r"ledger/rules/rules-.*\.md$", rel_path):
        return "rule"
    return None


def validate(data: dict, schema: dict, path_prefix: str = "") -> list[str]:
    """Minimal JSON Schema validator — supports required, type, enum, pattern, items."""
    errors: list[str] = []

    def check_type(val, expected):
        if isinstance(expected, list):
            return any(check_type(val, t) for t in expected)
        if expected == "string":
            return isinstance(val, str)
        if expected == "array":
            return isinstance(val, list)
        if expected == "object":
            return isinstance(val, dict)
        if expected == "null":
            return val is None
        if expected == "number":
            return isinstance(val, (int, float)) and not isinstance(val, bool)
        if expected == "integer":
            return isinstance(val, int) and not isinstance(val, bool)
        if expected == "boolean":
            return isinstance(val, bool)
        return True

    for req in schema.get("required", []):
        if req not in data or data[req] in (None, "", []):
            errors.append(f"{path_prefix}missing required field: '{req}'")

    for key, rules in (schema.get("properties") or {}).items():
        if key not in data:
            continue
        val = data[key]
        if "const" in rules and val != rules["const"]:
            errors.append(f"{path_prefix}field '{key}': expected const '{rules['const']}', got '{val}'")
        if "enum" in rules and val not in rules["enum"]:
            errors.append(f"{path_prefix}field '{key}': value '{val}' not in enum {rules['enum']}")
        if "type" in rules and not check_type(val, rules["type"]):
            errors.append(f"{path_prefix}field '{key}': expected type {rules['type']}, got {type(val).__name__}")
        if "pattern" in rules and isinstance(val, str):
            if not re.match(rules["pattern"], val):
                errors.append(f"{path_prefix}field '{key}': value '{val}' does not match pattern {rules['pattern']}")
        if "minLength" in rules and isinstance(val, str) and len(val) < rules["minLength"]:
            errors.append(f"{path_prefix}field '{key}': length {len(val)} < minLength {rules['minLength']}")
        if "minItems" in rules and isinstance(val, list) and len(val) < rules["minItems"]:
            errors.append(f"{path_prefix}field '{key}': length {len(val)} < minItems {rules['minItems']}")
        if "items" in rules and isinstance(val, list):
            item_schema = rules["items"]
            for i, item in enumerate(val):
                sub_errs = validate({"item": item}, {"properties": {"item": item_schema}}, f"{path_prefix}{key}[{i}]: ")
                errors.extend(sub_errs)

    return errors


def main(argv: list[str]) -> int:
    vault_path = Path(argv[1]).resolve() if len(argv) > 1 and not argv[1].startswith("--") else Path.cwd()
    emit_json = "--json" in argv
    schemas_dir = vault_path / "_scripts" / "schemas"

    if not schemas_dir.is_dir():
        print(f"Error: schemas dir not found: {schemas_dir}", file=sys.stderr)
        return 2

    schemas: dict[str, dict] = {}
    for t in ("adr", "moc", "incident", "rule"):
        path = schemas_dir / f"{t}.schema.json"
        if path.exists():
            with path.open(encoding="utf-8") as f:
                schemas[t] = json.load(f)

    findings: list[dict] = []
    EXCLUDE_DIRS = {".git", ".obsidian", "_archive"}

    for md in vault_path.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in md.parts):
            continue
        rel = md.relative_to(vault_path).as_posix()
        kind = classify(rel)
        if kind is None:
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        data, _ = find_frontmatter(text)

        if data is None:
            severity = "warning" if kind == "rule" else "error"
            findings.append({
                "severity": severity,
                "file": rel,
                "kind": kind,
                "message": "missing YAML frontmatter",
                "rule": f"{kind}.schema/frontmatter-presence",
            })
            continue

        schema = schemas.get(kind)
        if schema is None:
            continue
        errs = validate(data, schema)
        for err in errs:
            findings.append({
                "severity": "error",
                "file": rel,
                "kind": kind,
                "message": err,
                "rule": f"{kind}.schema",
            })

    summary = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        summary[f["severity"]] = summary.get(f["severity"], 0) + 1

    if emit_json:
        print(json.dumps({"check": "frontmatter-schema", "findings": findings, "summary": summary}, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity'].upper()}] {f['file']}: {f['message']}")
        print(f"\nTotal: {summary['error']} error(s), {summary['warning']} warning(s)")

    return 1 if summary["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
