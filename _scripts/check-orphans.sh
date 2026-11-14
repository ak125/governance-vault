#!/usr/bin/env bash
# check-orphans.sh - Enforce G2 (Zero Orphelin)
#
# Un document est "non-orphelin" s'il est:
#   - un MOC dans ops/moc/ (point d'entree), OU
#   - la cible resolue d'un [[wikilink]] ou [[path/to/file|alias]] depuis un AUTRE .md du vault
#
# Identite par chemin (ADR-127, resolveur partage _scripts/wikilinks.py) :
#   - [[dossier/nom]] : chemin depuis la racine du vault ('/' initial accepte), resolution exacte ;
#   - [[nom]]         : resolu par nom seulement si un seul document porte ce nom ;
#   - un lien ambigu (nom porte par plusieurs documents) ne compte pour aucun d'eux ;
#   - un lien d'un document vers lui-meme ne compte pas comme lien entrant.
# Chaque document est controle, homonymes compris.
#
# Exclusions (whitelist sains, non-orphelins par nature):
#   - ops/moc/           (MOCs = roots)
#   - 99-meta/           (gouvernance du vault lui-meme)
#   - _assets/           (images, diagrammes)
#   - _templates/        (templates reutilisables)
#   - _scripts/          (scripts d'enforcement)
#   - .obsidian/, .git/  (infra)
#   - README.md, CLAUDE.md, AGENTS.md (racine)
#
# Ignore les [[...]] dans les blocs de code (``` ... ``` et `inline`) pour eviter
# les faux positifs (bash `[[ -n $var ]]`, exemples `[[wikilink]]` en doc).
#
# Exit 1 si des orphelins sont detectes; ecrit le rapport dans 99-meta/orphans-report.md.

set -euo pipefail

VAULT_PATH="${1:-$(cd "$(dirname "$0")/.." && pwd)}"

if [[ ! -d "$VAULT_PATH" ]]; then
  echo "Error: vault path not found: $VAULT_PATH" >&2
  exit 2
fi

# Find a real Python 3 interpreter across Linux / macOS / Windows (Git Bash).
# Windows ships a "python" shim that opens the Microsoft Store — we must avoid it.
find_python() {
  for candidate in python3 py python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      # Verify it actually runs Python (filters out the Windows Store alias,
      # which prints a message and exits nonzero when run non-interactively).
      if "$candidate" -c "import sys; sys.exit(0 if sys.version_info[0]>=3 else 1)" >/dev/null 2>&1; then
        echo "$candidate"
        return 0
      fi
      # Try "py -3" as a second form of the Python Launcher on Windows
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
exec $PY_BIN "$SCRIPT_DIR/wikilinks.py" orphans "$VAULT_PATH"
