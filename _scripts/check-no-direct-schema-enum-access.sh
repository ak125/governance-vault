#!/usr/bin/env bash
# check-no-direct-schema-enum-access.sh — wrapper minimaliste qui délègue
# à l'AST walker Python (PR-2b). Conserve la compat weekly-lint.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 _scripts/check_no_direct_schema_enum_access.py
