#!/usr/bin/env bash
# check-orphans.sh - Garantit R-Vault-02 (aucun document orphelin)
# Un doc est "non orphelin" s'il est dans 00-index/ OU référencé via [[...]]
set -euo pipefail

VAULT_PATH="${1:-/opt/automecanik/governance-vault}"

# Collect all markdown notes (excluding MOCs, meta, assets, and templates)
mapfile -t NOTES < <(find "$VAULT_PATH" -type f -name "*.md" \
  ! -path "$VAULT_PATH/00-index/*" \
  ! -path "$VAULT_PATH/99-meta/*" \
  ! -path "$VAULT_PATH/_assets/*" \
  ! -path "*/_templates/*" \
  ! -path "$VAULT_PATH/scripts/*" \
  ! -name "README.md" \
  2>/dev/null | sort)

# If no notes found, exit successfully
if [ "${#NOTES[@]}" -eq 0 ]; then
  echo "✅ No notes to check (vault is empty or only has MOCs)"
  exit 0
fi

# Build reference file from all notes (using temp file for large content)
CONTENT_FILE=$(mktemp)
trap "rm -f $CONTENT_FILE" EXIT
find "$VAULT_PATH" -type f -name "*.md" -print0 2>/dev/null | xargs -0 cat > "$CONTENT_FILE" 2>/dev/null || true

ORPHANS=()

for note in "${NOTES[@]}"; do
  base="$(basename "$note" .md)"
  # Match [[NoteName]] or [[NoteName|alias]]
  if ! grep -Eq "\[\[$base(\||\]\])" "$CONTENT_FILE"; then
    ORPHANS+=("$note")
  fi
done

OUT="$VAULT_PATH/99-meta/broken-links.md"
mkdir -p "$(dirname "$OUT")"

if [ "${#ORPHANS[@]}" -gt 0 ]; then
  {
    echo "# Orphans Report"
    echo ""
    echo "Date: $(date -Iseconds)"
    echo ""
    echo "## Orphan Notes (${#ORPHANS[@]})"
    echo ""
    for o in "${ORPHANS[@]}"; do
      rel_path=$(realpath --relative-to="$VAULT_PATH" "$o" 2>/dev/null || echo "$o")
      echo "- [[$rel_path]]"
    done
    echo ""
    echo "---"
    echo ""
    echo "> **Action requise**: Lier ces documents depuis un MOC ou les archiver."
  } > "$OUT"

  echo "❌ Orphans found: ${#ORPHANS[@]}"
  echo "Report: $OUT"
  exit 1
else
  echo "✅ No orphans found"
  rm -f "$OUT" 2>/dev/null || true
fi
