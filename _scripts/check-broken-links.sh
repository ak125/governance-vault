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

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

$PY_BIN - "$VAULT_PATH" "$SCRIPT_DIR" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, sys.argv[2])
from wikilinks import link_problems  # resolveur partage (ADR-127)

broken, ambiguous = link_problems(root)

out_path = root / "99-meta" / "broken-links-report.md"
out_path.parent.mkdir(parents=True, exist_ok=True)

if broken or ambiguous:
    from datetime import datetime
    with out_path.open("w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("type: report\n")
        f.write("status: generated\n")
        f.write(f"generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"broken_count: {len(broken)}\n")
        f.write(f"ambiguous_count: {len(ambiguous)}\n")
        f.write("---\n\n")
        f.write("# Broken Wikilinks Report\n\n")
        f.write(f"**Liens casses detectes**: {len(broken)}\n\n")
        if broken:
            f.write("| Fichier source | Cible (cassee) |\n")
            f.write("|----------------|----------------|\n")
            for link in broken:
                f.write(f"| `{link.source}` | `[[{link.target}]]` |\n")
        f.write(f"\n**Liens ambigus detectes**: {len(ambiguous)}\n\n")
        if ambiguous:
            f.write("Nom porte par plusieurs documents : lier par le chemin, ")
            f.write("`[[dossier/nom|alias]]` (ADR-127).\n\n")
            f.write("| Fichier source | Cible (ambigue) | Candidats |\n")
            f.write("|----------------|-----------------|-----------|\n")
            for link in ambiguous:
                cands = ", ".join(f"`{c[:-3]}`" for c in link.resolved)
                f.write(f"| `{link.source}` | `[[{link.target}]]` | {cands} |\n")
    print(f"FAIL: {len(broken)} broken wikilink(s), {len(ambiguous)} ambiguous wikilink(s) detected")
    print(f"Report: {out_path.relative_to(root)}")
    sys.exit(1)
else:
    if out_path.exists():
        out_path.unlink()
    print("PASS: 0 broken wikilink, 0 ambiguous wikilink")
    sys.exit(0)
PY
