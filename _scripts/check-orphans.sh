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

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

$PY_BIN - "$VAULT_PATH" "$SCRIPT_DIR" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, sys.argv[2])
from wikilinks import orphans as find_orphans  # resolveur partage (ADR-127)

orphans = find_orphans(root)

out_path = root / "99-meta" / "orphans-report.md"
out_path.parent.mkdir(parents=True, exist_ok=True)

if orphans:
    from datetime import datetime
    with out_path.open("w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("type: report\n")
        f.write("status: generated\n")
        f.write(f"generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"orphan_count: {len(orphans)}\n")
        f.write("---\n\n")
        f.write("# Orphans Report (G2 violation)\n\n")
        f.write(f"**Orphelins detectes**: {len(orphans)}\n\n")
        f.write("## Documents orphelins\n\n")
        for rel in orphans:
            f.write(f"- `{rel}`\n")
        f.write("\n## Action requise\n\n")
        f.write("1. Lier ce document depuis un MOC (`ops/moc/MOC-*.md`), OU\n")
        f.write("2. Lier depuis un INDEX-* local, OU\n")
        f.write("3. Archiver dans `ledger/_archive/` (voir G8 Obsolete Handling)\n")
        f.write("\nUn nom porte par plusieurs documents se lie par son chemin : ")
        f.write("`[[dossier/nom|alias]]` (ADR-127).\n")
    print(f"FAIL: {len(orphans)} orphan(s) detected")
    print(f"Report: {out_path.relative_to(root)}")
    sys.exit(1)
else:
    if out_path.exists():
        out_path.unlink()
    print("PASS: 0 orphan (G2 respected)")
    sys.exit(0)
PY
