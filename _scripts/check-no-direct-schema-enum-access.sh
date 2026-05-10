#!/usr/bin/env bash
# check-no-direct-schema-enum-access.sh — MVP grep contre l'extraction directe
# d'enums depuis _scripts/schemas/*.schema.json (PR-2 invariant).
#
# Refuse toute lecture directe d'enum schema en dehors de l'allowlist.
# PR-2b remplace ce grep MVP par un walker AST plus précis.
#
# Allowlist :
#   - test_governance_constants.py (parity test, DOIT lire les enums)
#   - governance_constants.py (SoT, n'a pas d'accès dict mais listé par sécurité)
#
# Validateurs légitimes (ignorés intentionnellement) :
#   - check-frontmatter-schema.py (lit les schemas pour validation conformité,
#     pas pour extraction enum métier)
set -euo pipefail
cd "$(dirname "$0")/.."

VIOLATIONS=$(grep -lEn 'schemas/.+\.schema\.json|properties.*enum' \
  _scripts/*.py 2>/dev/null \
  | grep -v 'test_governance_constants\.py' \
  | grep -v 'governance_constants\.py' \
  | grep -v 'check-frontmatter-schema\.py' \
  || true)

if [[ -n "$VIOLATIONS" ]]; then
  echo "::error::Direct schema enum parse forbidden (PR-2 invariant)" >&2
  echo "Files in violation:" >&2
  echo "$VIOLATIONS" >&2
  echo "Allowed: test_governance_constants.py only." >&2
  echo "Other scripts MUST: from governance_constants import <ENUM_NAME>" >&2
  exit 1
fi
echo "OK: no direct schema enum parsing outside test_governance_constants.py"
