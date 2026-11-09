"""test_governance_constants.py — verify parity with JSON Schemas + module purity.

If a schema adds/removes a status, this test fails → forces updating the
matching submodule of governance_constants/ in the same commit.

If any submodule grows beyond constants (imports, functions), TestPurity
fails → forces creating a separate module for the logic.

The package __init__.py is exempt from the strict "no imports" rule — it
exists purely to re-export submodule symbols (backward compat). A dedicated
test (`test_init_only_reexports`) enforces that __init__.py contains only
internal `from .X import ...` statements.
"""
from __future__ import annotations

import ast
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
PACKAGE_DIR = Path(__file__).parent / "governance_constants"


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
    """STRICT SCOPE RULE enforcement on each submodule (anti policy creep)."""

    def _submodules(self) -> list[Path]:
        """All package .py files except __init__.py (facade — separate rule)."""
        return sorted(
            p for p in PACKAGE_DIR.glob("*.py") if p.name != "__init__.py"
        )

    def test_submodule_no_imports_except_future(self):
        for source in self._submodules():
            tree = ast.parse(source.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    self.assertEqual(
                        node.module,
                        "__future__",
                        f"{source.name}: forbidden import 'from {node.module}'. "
                        "Move logic to a separate module.",
                    )
                elif isinstance(node, ast.Import):
                    self.fail(
                        f"{source.name}: forbidden 'import {node.names[0].name}'. "
                        "Submodule accepts only `from __future__ import ...`."
                    )

    def test_submodule_no_functions_or_classes(self):
        for source in self._submodules():
            tree = ast.parse(source.read_text())
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef):
                    self.fail(
                        f"{source.name}: forbidden function `def {node.name}(...)`. "
                        "Move to governance_policies.py / *_engine.py."
                    )
                if isinstance(node, ast.ClassDef):
                    self.fail(
                        f"{source.name}: forbidden class `class {node.name}`. "
                        "Submodule = data only."
                    )

    def test_init_only_reexports(self):
        """__init__.py allowed only `from __future__ import ...` and
        `from .<submodule> import <name>` (internal re-exports)."""
        init_path = PACKAGE_DIR / "__init__.py"
        tree = ast.parse(init_path.read_text())
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                # Allowed: from __future__ import ... OR from .X import ... (level=1)
                if node.level == 1:
                    continue  # internal package import
                if module == "__future__":
                    continue
                self.fail(
                    f"__init__.py: forbidden non-internal import 'from {module}'. "
                    "Facade may only re-export submodule symbols (from .X import ...)."
                )
            elif isinstance(node, ast.Import):
                self.fail(
                    f"__init__.py: forbidden 'import {node.names[0].name}'. "
                    "Facade may only re-export submodule symbols (from .X import ...)."
                )
            elif isinstance(node, ast.FunctionDef):
                self.fail(
                    f"__init__.py: forbidden function `def {node.name}(...)`. "
                    "Facade = re-exports only."
                )
            elif isinstance(node, ast.ClassDef):
                self.fail(
                    f"__init__.py: forbidden class `class {node.name}`. "
                    "Facade = re-exports only."
                )


if __name__ == "__main__":
    unittest.main()
