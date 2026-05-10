#!/usr/bin/env python3
"""AST-based detection : interdit l'accès direct aux ENUMS des schemas
(`["properties"][...]["enum"]`) en dehors des allowlist.

CIBLE PRÉCISE : enum extraction métier, PAS lecture générale des schemas.
Les validateurs légitimes (`check-frontmatter-schema.py`) lisent les schemas
pour valider la conformité de frontmatter, ce qui est OK et nécessaire.
Ce qui est interdit : utiliser les enums comme source pour de la logique
métier (filtering, switch, etc.) — cela doit passer par
`governance_constants.py`.

Détecte 1 pattern (volontairement étroit pour ne pas casser les validateurs) :
  Subscript chain qui contient "properties" → <field> → "enum" en chaîne contiguë
    → x["properties"]["status"]["enum"]
    → schema["properties"]["type"]["enum"]
    → data["adr"]["properties"]["status"]["enum"]

LIMITE CONNUE — contournement involontaire possible :
  props = data["properties"]      # chaîne brisée par assignation
  enum = props["status"]["enum"]  # detector ne voit pas le lien

  Mitigation Phase 2 (follow-up — taint tracking léger / data-flow simplifié) :
  - Tracker les assignations `x = y["properties"]`
  - Suivre x à travers une fonction (intra-procedural data flow)
  - Détecter `x["status"]["enum"]` reliée à un schema source

  Pas urgent maintenant (cas rare, signal-driven), mais à surveiller dès
  qu'un script complexe arrive dans `_scripts/`.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

# Allowlist : scripts autorisés à accéder aux enums depuis schemas.
# - test_governance_constants : test de parité (DOIT lire les enums pour comparer)
# - governance_constants       : ne fait pas d'accès dict, mais listé par sécurité
# - check_no_direct_schema_enum_access : self-exclusion (le scanner contient le pattern)
ALLOWED = {
    "test_governance_constants.py",
    "governance_constants.py",
    "check_no_direct_schema_enum_access.py",
}

# Validateurs légitimes : lisent les schemas pour validation de conformité,
# pas pour extraction d'enum métier. Vérifiés manuellement, à maintenir
# si nouveau validateur ajouté.
LEGITIMATE_SCHEMA_READERS = {
    "check-frontmatter-schema.py",
}

SCRIPTS_DIR = Path(__file__).resolve().parent

# Patterns ciblés : chaîne contiguë de string subscripts contenant
# "properties" puis un champ puis "enum". Lecture human-readable.
TARGET_PATTERNS: tuple[tuple[str, ...], ...] = (
    ("properties", "status", "enum"),
    ("properties", "type", "enum"),
    ("properties", "id", "enum"),
)


class EnumAccessDetector(ast.NodeVisitor):
    """Détecte UNIQUEMENT les chaînes CONTIGUËS d'accès enum, jamais
    deux constantes séparées dans des sous-expressions distinctes.

    Faux positif évité :
        meta["properties"]["foo"]; x["enum"]   # 2 chaînes distinctes → OK
    Vrai positif :
        schema["properties"]["status"]["enum"] # chaîne contiguë → BLOCK
    """

    def __init__(self) -> None:
        self.violations: list[str] = []
        self._seen_lines: set[int] = set()

    def visit_Subscript(self, node: ast.Subscript) -> None:
        chain = self._extract_subscript_chain(node)
        # chain est dans l'ordre [innermost subscript, ..., outermost subscript].
        # Lecture python `a["x"]["y"]["z"]` → chain extraite = ["z","y","x"].
        # On compare donc reversed(chain) au pattern.
        readable = list(reversed(chain))
        for pat in TARGET_PATTERNS:
            n = len(pat)
            if any(readable[i : i + n] == list(pat) for i in range(len(readable) - n + 1)):
                if node.lineno not in self._seen_lines:
                    self._seen_lines.add(node.lineno)
                    pat_str = '"]["'.join(pat)
                    self.violations.append(
                        f'line {node.lineno}: contiguous chain ["{pat_str}"] '
                        "(business enum extraction — use governance_constants instead)"
                    )
                break
        self.generic_visit(node)

    @staticmethod
    def _extract_subscript_chain(node: ast.Subscript) -> list[str]:
        """Returns chain in [innermost subscript, ..., outermost subscript] order."""
        keys: list[str] = []
        cur: ast.AST = node
        while isinstance(cur, ast.Subscript):
            slc = cur.slice
            if isinstance(slc, ast.Constant) and isinstance(slc.value, str):
                keys.append(slc.value)
            else:
                # subscript non-string (variable, slice) → break la chaîne contiguë
                return keys
            cur = cur.value
        return keys


def scan(file: Path) -> list[str]:
    try:
        tree = ast.parse(file.read_text(encoding="utf-8"))
    except SyntaxError:
        return [f"{file.name}: SyntaxError, skipped"]
    det = EnumAccessDetector()
    det.visit(tree)
    return [f"{file.name}: {v}" for v in det.violations]


def main() -> int:
    violations: list[str] = []
    skipped_legitimate: list[str] = []
    scanned = 0
    for f in sorted(SCRIPTS_DIR.glob("*.py")):
        scanned += 1
        if f.name in ALLOWED:
            continue
        if f.name in LEGITIMATE_SCHEMA_READERS:
            skipped_legitimate.append(f.name)
            continue
        violations.extend(scan(f))
    if violations:
        print("::error::Direct schema ENUM ACCESS forbidden (PR-2/PR-2b invariant)", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print(f"\nAllowed (test/SoT): {sorted(ALLOWED)}", file=sys.stderr)
        print(
            f"Skipped (legitimate validators reading schemas, not enums): "
            f"{sorted(LEGITIMATE_SCHEMA_READERS)}",
            file=sys.stderr,
        )
        print("Other scripts MUST: from governance_constants import <ENUM_NAME>", file=sys.stderr)
        return 1
    msg = (
        f"OK: scanned {scanned} scripts, no direct enum access outside allowed list"
    )
    if skipped_legitimate:
        msg += (
            f" (skipped {len(skipped_legitimate)} legitimate schema readers: "
            f"{skipped_legitimate})"
        )
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
