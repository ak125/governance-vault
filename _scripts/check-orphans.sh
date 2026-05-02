#!/usr/bin/env bash
# check-orphans.sh - Enforce G2 (Zero Orphelin)
#
# Un document est "non-orphelin" s'il est:
#   - un MOC dans ops/moc/ (point d'entree), OU
#   - reference via [[wikilink]] ou [[path/to/file|alias]] depuis un autre .md du vault
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

$PY_BIN - "$VAULT_PATH" <<'PY'
import os, re, sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()

EXCLUDE_DIRS = {".git", ".obsidian"}
ROOT_DIRS = {"ops/moc", "99-meta", "_assets", "_templates", "_scripts"}
ROOT_FILES = {"README.md", "CLAUDE.md", "AGENTS.md"}

def is_root_path(rel_path: str) -> bool:
    if rel_path in ROOT_FILES:
        return True
    for prefix in ROOT_DIRS:
        if rel_path.startswith(prefix + "/") or rel_path == prefix:
            return True
    return False

# Collect all .md files
# Use .as_posix() so paths use forward slashes on Windows too
# (otherwise the ROOT_DIRS whitelist below would miss files under 99-meta\ etc.)
all_stems = {}   # stem -> relative path
for p in root.rglob("*.md"):
    if any(part in EXCLUDE_DIRS for part in p.parts):
        continue
    rel = p.relative_to(root).as_posix()
    all_stems[p.stem] = rel

def strip_code(txt: str) -> str:
    # Strip fenced code blocks and inline code
    txt = re.sub(r"```[\s\S]*?```", "", txt)
    txt = re.sub(r"`[^`\n]*`", "", txt)
    return txt

link_re = re.compile(r"\[\[([^\]]+?)\]\]")
linked = set()
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
        linked.add(stem)

# Any stem not linked AND not a root is an orphan
orphans = []
for stem, rel in sorted(all_stems.items()):
    if is_root_path(rel):
        continue
    if stem in linked:
        continue
    orphans.append(rel)

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
    print(f"FAIL: {len(orphans)} orphan(s) detected")
    print(f"Report: {out_path.relative_to(root)}")
    sys.exit(1)
else:
    if out_path.exists():
        out_path.unlink()
    print("PASS: 0 orphan (G2 respected)")
    sys.exit(0)
PY
