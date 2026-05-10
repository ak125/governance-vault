"""test_governance_constants.py — verify parity with JSON Schemas + module purity.

If a schema adds/removes a status, this test fails → forces updating
governance_constants.py in the same commit.

If governance_constants.py grows beyond constants (imports, functions),
TestPurity fails → forces creating a separate module for the logic.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from governance_constants import (
    ADR_STATUSES,
    INCIDENT_STATUSES,
    MOC_STATUSES,
    RULE_STATUSES,
    RULE_TYPES,
)

SCHEMA_DIR = Path(__file__).parent / "schemas"


def load_enum(schema_name: str, prop: str) -> set[str]:
    return set(json.loads((SCHEMA_DIR / schema_name).read_text())["properties"][prop]["enum"])


class TestParity(unittest.TestCase):
    def test_adr_statuses(self):
        self.assertEqual(set(ADR_STATUSES), load_enum("adr.schema.json", "status"))

    def test_rule_statuses(self):
        self.assertEqual(set(RULE_STATUSES), load_enum("rule.schema.json", "status"))

    def test_moc_statuses(self):
        self.assertEqual(set(MOC_STATUSES), load_enum("moc.schema.json", "status"))

    def test_incident_statuses(self):
        self.assertEqual(set(INCIDENT_STATUSES), load_enum("incident.schema.json", "status"))

    def test_rule_types(self):
        self.assertEqual(set(RULE_TYPES), load_enum("rule.schema.json", "type"))


class TestPurity(unittest.TestCase):
    """STRICT SCOPE RULE enforcement (anti policy creep)."""

    SOURCE = Path(__file__).parent / "governance_constants.py"

    def test_no_imports_except_future(self):
        import ast
        tree = ast.parse(self.SOURCE.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                self.assertEqual(
                    node.module,
                    "__future__",
                    f"governance_constants.py: forbidden import 'from {node.module}'. "
                    "Move logic to a separate module.",
                )
            elif isinstance(node, ast.Import):
                self.fail(
                    f"governance_constants.py: forbidden 'import {node.names[0].name}'. "
                    "Constants module accepts only `from __future__ import ...`."
                )

    def test_no_functions_or_classes(self):
        import ast
        tree = ast.parse(self.SOURCE.read_text())
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                self.fail(
                    f"governance_constants.py: forbidden function `def {node.name}(...)`. "
                    "Move to governance_policies.py / *_engine.py."
                )
            if isinstance(node, ast.ClassDef):
                self.fail(
                    f"governance_constants.py: forbidden class `class {node.name}`. "
                    "Constants module = data only."
                )


if __name__ == "__main__":
    unittest.main()
