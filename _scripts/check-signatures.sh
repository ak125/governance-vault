#!/usr/bin/env bash
# check-signatures.sh - Verifie que les commits dans un range sont signes (G3)
#
# Usage:
#   check-signatures.sh [VAULT_PATH] [RANGE]
#
# VAULT_PATH : racine du repo (default: parent du script)
# RANGE      : range git rev-list (default: merge-base(origin/main)..HEAD)
#
# Statuses signes acceptes : G (good), U (untrusted), X (expired)
# Statuses rejetes         : N (none), B (bad)
# Mirror logique du job CI vault-governance.yml#G3.
#
# Exit 0 si tout signe, 1 si N/B detecte, 2 si erreur.
set -euo pipefail

VAULT_PATH="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
RANGE="${2:-}"

if [[ ! -e "$VAULT_PATH/.git" ]]; then
  # `-d` would reject git worktrees, where `.git` is a file (gitlink) pointing
  # to the main repo's `.git/worktrees/<name>` instead of a directory.
  echo "Error: not a git repo: $VAULT_PATH" >&2
  exit 2
fi

cd "$VAULT_PATH"

# Default range : commits introduits par la branche depuis main
if [[ -z "$RANGE" ]]; then
  if ! git rev-parse --verify origin/main >/dev/null 2>&1; then
    echo "PASS: origin/main inconnu, skip G3 (premier clone ?)"
    exit 0
  fi
  base="$(git merge-base origin/main HEAD)"
  head="$(git rev-parse HEAD)"
  if [[ "$base" == "$head" ]]; then
    echo "PASS: HEAD == merge-base origin/main, aucun commit a verifier"
    exit 0
  fi
  RANGE="${base}..HEAD"
fi

echo "Checking signatures in range: $RANGE"
unsigned=0
while read -r sha; do
  [[ -z "$sha" ]] && continue
  sig=$(git log -1 --format='%G?' "$sha")
  case "$sig" in
    N|B)
      echo "FAIL: $(git log -1 --format='%h %s' "$sha") (status=$sig)"
      unsigned=$((unsigned + 1))
      ;;
  esac
done < <(git rev-list "$RANGE")

if [[ "$unsigned" -gt 0 ]]; then
  echo "FAIL: $unsigned commit(s) non signe(s) dans $RANGE"
  exit 1
fi

echo "PASS: tous les commits signes dans $RANGE"
exit 0
