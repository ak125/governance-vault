#!/usr/bin/env bash
# check-broken-links.sh - Detecte les [[wikilinks]] qui ne resolvent aucun .md du vault
#
# Ignore les [[...]] dans les blocs de code (fenced ``` et inline `).
# Exit 1 si des liens casses sont trouves.

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

$PY_BIN - "$VAULT_PATH" <<'PY'
import os, re, sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
EXCLUDE_DIRS = {".git", ".obsidian"}

all_stems = set()
all_paths = set()
for p in root.rglob("*.md"):
    if any(part in EXCLUDE_DIRS for part in p.parts):
        continue
    all_stems.add(p.stem)
    all_paths.add(str(p.relative_to(root))[:-3])

def strip_code(txt):
    txt = re.sub(r"```[\s\S]*?```", "", txt)
    txt = re.sub(r"`[^`\n]*`", "", txt)
    return txt

link_re = re.compile(r"\[\[([^\]]+?)\]\]")
broken = []
for p in root.rglob("*.md"):
    if any(part in EXCLUDE_DIRS for part in p.parts):
        continue
    try:
        txt = strip_code(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        continue
    for m in link_re.findall(txt):
        name = m.strip()
        if "|" in name:
            name = name.split("|", 1)[0]
        if "#" in name:
            name = name.split("#", 1)[0]
        name = name.strip().rstrip("\\")
        stem = name.rsplit("/", 1)[-1]
        if stem not in all_stems and name not in all_paths:
            broken.append((str(p.relative_to(root)), name))

out_path = root / "99-meta" / "broken-links-report.md"
out_path.parent.mkdir(parents=True, exist_ok=True)

if broken:
    from datetime import datetime
    with out_path.open("w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("type: report\n")
        f.write("status: generated\n")
        f.write(f"generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"broken_count: {len(broken)}\n")
        f.write("---\n\n")
        f.write("# Broken Wikilinks Report\n\n")
        f.write(f"**Liens casses detectes**: {len(broken)}\n\n")
        f.write("| Fichier source | Cible (cassee) |\n")
        f.write("|----------------|----------------|\n")
        for src, tgt in broken:
            f.write(f"| `{src}` | `[[{tgt}]]` |\n")
    print(f"FAIL: {len(broken)} broken wikilink(s) detected")
    print(f"Report: {out_path.relative_to(root)}")
    sys.exit(1)
else:
    if out_path.exists():
        out_path.unlink()
    print("PASS: 0 broken wikilink")
    sys.exit(0)
PY
