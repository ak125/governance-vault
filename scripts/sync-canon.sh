#!/usr/bin/env bash
# sync-canon.sh - Sync canon → vault (mode safe)
# Usage: ./sync-canon.sh [--dry-run] [--commit]
#
# Par défaut: dry-run (montre les changements sans modifier)
# --commit: applique les changements ET crée un commit signé
set -euo pipefail

MONOREPO_PATH="${MONOREPO_PATH:-/opt/automecanik/app}"
VAULT_PATH="${VAULT_PATH:-/opt/automecanik/governance-vault}"
CANON_PATH="$MONOREPO_PATH/.spec/00-canon"

DRY_RUN=true
AUTO_COMMIT=false

for arg in "$@"; do
  case $arg in
    --commit) DRY_RUN=false; AUTO_COMMIT=true ;;
    --dry-run) DRY_RUN=true ;;
  esac
done

SYNC_DIR="$VAULT_PATH/99-meta"
SYNC_LOG="$SYNC_DIR/sync-log.md"
LAST_SYNC="$SYNC_DIR/last-sync-timestamp"

mkdir -p "$SYNC_DIR"

if [ ! -f "$LAST_SYNC" ]; then
  echo "1970-01-01T00:00:00Z" > "$LAST_SYNC"
fi

LAST="$(cat "$LAST_SYNC")"

# Trouver les fichiers modifiés
mapfile -t CHANGED < <(find "$CANON_PATH" -type f -name "*.md" -newermt "$LAST" 2>/dev/null | sort)

if [ "${#CHANGED[@]}" -eq 0 ]; then
  echo "✅ No canon changes since $LAST"
  exit 0
fi

echo "🔄 Canon changes detected: ${#CHANGED[@]}"

# Fonction de routage
route_dest() {
  local src="$1"
  local name
  name="$(basename "$src")"
  case "$name" in
    *adr*|ADR-*) echo "$VAULT_PATH/02-decisions/adr" ;;
    *rule*|R*|*canon*) echo "$VAULT_PATH/03-rules/technical" ;;
    *architecture*|*overview*|*map*) echo "$VAULT_PATH/06-knowledge" ;;
    *) echo "$VAULT_PATH/06-knowledge" ;;
  esac
}

CONFLICTS=0
SYNCED=0
CHANGES_SUMMARY=""

for f in "${CHANGED[@]}"; do
  dest_dir="$(route_dest "$f")"
  dest="$dest_dir/$(basename "$f")"

  rel_src=$(realpath --relative-to="$MONOREPO_PATH" "$f" 2>/dev/null || echo "$f")
  rel_dest=$(realpath --relative-to="$VAULT_PATH" "$dest" 2>/dev/null || echo "$dest")

  if [ "$DRY_RUN" = true ]; then
    if [ -f "$dest" ] && ! cmp -s "$f" "$dest"; then
      echo "⚠️  [CONFLICT] $rel_src → $rel_dest"
      CHANGES_SUMMARY+="- ⚠️ CONFLICT: $rel_src\n"
      ((CONFLICTS++)) || true
    elif [ ! -f "$dest" ]; then
      echo "➕ [NEW] $rel_src → $rel_dest"
      CHANGES_SUMMARY+="- ➕ NEW: $rel_src\n"
      ((SYNCED++)) || true
    else
      echo "📄 [UPDATE] $rel_src → $rel_dest"
      CHANGES_SUMMARY+="- 📄 UPDATE: $rel_src\n"
      ((SYNCED++)) || true
    fi
  else
    mkdir -p "$dest_dir"

    if [ -f "$dest" ] && ! cmp -s "$f" "$dest"; then
      ((CONFLICTS++)) || true
      conflict="$dest.conflict.$(date +%s)"
      cp "$f" "$conflict"
      echo "$(date -Iseconds) | CONFLICT | $(basename "$f") → $(basename "$conflict")" >> "$SYNC_LOG"
      continue
    fi

    cp "$f" "$dest"
    echo "$(date -Iseconds) | SYNC | $(basename "$f")" >> "$SYNC_LOG"
    ((SYNCED++)) || true
  fi
done

echo ""
echo "=== Summary ==="
echo "Files to sync: $SYNCED"
echo "Conflicts: $CONFLICTS"

if [ "$DRY_RUN" = true ]; then
  echo ""
  echo "📋 DRY-RUN MODE - Aucune modification effectuée"
  echo "Pour appliquer: ./sync-canon.sh --commit"
  exit 0
fi

# Mettre à jour timestamp
date -Iseconds > "$LAST_SYNC"

if [ "$AUTO_COMMIT" = true ] && [ "$SYNCED" -gt 0 ]; then
  cd "$VAULT_PATH"
  git add -A
  git commit -S -m "sync(canon): update $SYNCED files from monorepo

Source: $CANON_PATH
Conflicts: $CONFLICTS
Files synced:
$(echo -e "$CHANGES_SUMMARY")"
  echo ""
  echo "✅ Commit signé créé"
  echo "Pour pousser: cd $VAULT_PATH && git push origin main"
fi

if [ "$CONFLICTS" -gt 0 ]; then
  echo ""
  echo "⚠️  $CONFLICTS conflict(s) détecté(s)"
  echo "Fichiers .conflict.* créés - résolution manuelle requise"
  exit 2
fi

echo "✅ Sync completed"
