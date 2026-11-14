#!/usr/bin/env bash
# check-broken-links.sh - Detecte les [[wikilinks]] casses ou ambigus du vault
#
# Resolution par chemin (ADR-127, resolveur partage _scripts/wikilinks.py) :
#   - [[dossier/nom]] : chemin depuis la racine du vault ('/' initial accepte) ; casse s'il n'existe pas ;
#   - [[nom]]         : casse si aucun document ne porte ce nom, ambigu si plusieurs le portent.
#
# Ignore les [[...]] dans les blocs de code (fenced ``` et inline `).
# Exit 1 si des liens casses ou ambigus sont trouves ; rapport : 99-meta/broken-links-report.md.

set -euo pipefail

VAULT_PATH="${1:-$(cd "$(dirname "$0")/.." && pwd)}"

if [[ ! -d "$VAULT_PATH" ]]; then
  echo "Error: vault path not found: $VAULT_PATH" >&2
  exit 2
fi

# Find a real Python 3 interpreter across Linux / macOS / Windows (Git Bash).
find_python() {
  for candidate in python3 py python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" -c "import sys; sys.exit(0 if sys.version_info[0]>=3 else 1)" >/dev/null 2>&1; then
        echo "$candidate"
        return 0
      fi
      if [[ "$candidate" == "py" ]] && py -3 -c "import sys" >/dev/null 2>&1; then
        echo "py -3"
        return 0
      fi
    fi
  done
  return 1
}

PY_BIN="$(find_python || true)"
if [[ -z "$PY_BIN" ]]; then
  echo "Error: Python 3 is required (tried: python3, py, python)." >&2
  echo "Install from https://python.org (cocher 'Add to PATH') ou 'winget install Python.Python.3'." >&2
  echo "Sur Windows, desactive aussi l'alias Store: Parametres > Apps > Alias d'execution > python/python3 OFF." >&2
  exit 2
fi

# Logique et rapport : _scripts/wikilinks.py (resolveur partage, ADR-127).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec $PY_BIN "$SCRIPT_DIR/wikilinks.py" links "$VAULT_PATH"
