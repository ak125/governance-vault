#!/usr/bin/env bash
# preflight-write.sh — Vérification avant toute écriture gouvernance (ADR-015 §Guardrails)
#
# À exécuter en premier ordre par tout agent (Claude Code, Cowork, Codex, scripts)
# avant de créer une branche / commiter / push un document de gouvernance.
#
# Complémentaire au cron vault-sync (5 min) : couvre la fenêtre temporelle où
# le clone serait périmé entre 2 ticks cron, et où un agent écrirait contre
# un main obsolète (cas PR #7 du 2026-04-18).
#
# Vérifications :
#   1. On est bien dans le canonical vault (pas dans .local/governance-vault/)
#   2. git fetch origin réussit
#   3. HEAD (branche courante) est à jour avec origin/HEAD OU si on part de main :
#      main local = origin/main
#   4. Working tree propre (aucun staged ni unstaged)
#   5. Aucun fichier tracké sous un path v1 (complément au gate CI)
#
# Usage :
#   _scripts/preflight-write.sh [--allow-dirty]
#
# Exit 0  : GO — agent peut écrire
# Exit 10 : BLOCKED — clone périmé, faire git pull --rebase origin main
# Exit 11 : BLOCKED — working tree sale, commit ou stash d'abord
# Exit 12 : BLOCKED — dans .local/governance-vault/ (jamais écrire ici)
# Exit 13 : BLOCKED — v1 paths détectés (régression ADR-015)
# Exit 20 : ERR — repo non-git ou vault-dir manquant
# Exit 21 : ERR — git fetch échoué (réseau)

set -euo pipefail

ALLOW_DIRTY="${1:-}"

VAULT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$VAULT_ROOT" 2>/dev/null || { echo "ERR: cannot cd to $VAULT_ROOT" >&2; exit 20; }

# --- Guard 1 : canonical path ---
if [[ "$VAULT_ROOT" == *"/app/.local/governance-vault"* ]] || [[ "$VAULT_ROOT" == *"/.local/governance-vault"* ]]; then
  echo "❌ BLOCKED (ADR-015) : tu es dans .local/governance-vault/ — path DEPRECATED."
  echo ""
  echo "Canonical vault : /opt/automecanik/governance-vault/"
  echo "Ne jamais écrire ici, ton travail sera perdu (gitignored)."
  exit 12
fi

# --- Guard 2 : repo git ---
if [[ ! -d .git ]]; then
  echo "❌ ERR : $VAULT_ROOT n'est pas un repo git" >&2
  exit 20
fi

# --- Guard 3 : git fetch ---
echo "🔄 Fetch origin..."
if ! timeout 15 git fetch origin --quiet 2>/dev/null; then
  echo "❌ ERR : git fetch origin a échoué (timeout 15s ou réseau indisponible)"
  echo "   Retry avec : git fetch origin"
  exit 21
fi

# --- Guard 4 : working tree clean ---
if [[ "$ALLOW_DIRTY" != "--allow-dirty" ]]; then
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "❌ BLOCKED : working tree ou index sales."
    echo ""
    echo "Actions possibles :"
    echo "  - Commit en cours : git commit -S -m \"...\""
    echo "  - Stash temporaire : git stash"
    echo "  - Autoriser (à tes risques) : _scripts/preflight-write.sh --allow-dirty"
    echo ""
    git status --short | head -10 | sed 's/^/  /'
    exit 11
  fi
fi

# --- Guard 5 : branche courante à jour ---
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
LOCAL="$(git rev-parse HEAD)"

if [[ "$BRANCH" == "main" ]]; then
  REMOTE="$(git rev-parse origin/main)"
  if [[ "$LOCAL" != "$REMOTE" ]]; then
    BASE="$(git merge-base HEAD origin/main)"
    if [[ "$BASE" == "$LOCAL" ]]; then
      COUNT="$(git rev-list --count HEAD..origin/main)"
      echo "❌ BLOCKED : main local est $COUNT commit(s) derrière origin/main."
      echo ""
      echo "Fix : git pull --ff-only origin main"
      echo ""
      echo "Contexte : écrire sur un main périmé produit des PRs qui conflict"
      echo "avec la structure actuelle (cf. PR #7 v1 vs main v2, 2026-04-18)."
      exit 10
    elif [[ "$BASE" == "$REMOTE" ]]; then
      AHEAD="$(git rev-list --count origin/main..HEAD)"
      echo "⚠️  WARN : main local est $AHEAD commit(s) EN AVANCE sur origin/main."
      echo "   (OK si tu viens de commiter et pas encore push)"
    else
      AHEAD="$(git rev-list --count origin/main..HEAD)"
      BEHIND="$(git rev-list --count HEAD..origin/main)"
      echo "❌ BLOCKED : main local DIVERGE d'origin/main (+$AHEAD / -$BEHIND)."
      echo ""
      echo "Fix : rebase interactive + résolution manuelle."
      exit 10
    fi
  fi
else
  # Branche de travail : juste informatif si pas à jour avec origin/main
  MAIN_ORIGIN="$(git rev-parse origin/main)"
  MAIN_BASE="$(git merge-base HEAD origin/main 2>/dev/null || echo "")"
  if [[ -n "$MAIN_BASE" ]] && [[ "$MAIN_BASE" != "$MAIN_ORIGIN" ]]; then
    BEHIND="$(git rev-list --count "$MAIN_BASE..origin/main" 2>/dev/null || echo "?")"
    echo "⚠️  WARN : branche '$BRANCH' basée sur un main périmé ($BEHIND commit(s) derrière)."
    echo "   Considère : git rebase origin/main (si compatible avec travail en cours)"
  fi
fi

# --- Guard 6 : v1 paths (réutilise le script existant) ---
if [[ -x _scripts/check-v1-paths.sh ]]; then
  if ! _scripts/check-v1-paths.sh . >/dev/null 2>&1; then
    echo "❌ BLOCKED : v1 paths détectés dans le clone."
    echo "   Run : _scripts/check-v1-paths.sh . pour voir le rapport"
    exit 13
  fi
fi

# --- GO ---
echo "✅ GO — preflight OK"
echo "   Vault    : $VAULT_ROOT"
echo "   Branch   : $BRANCH"
echo "   HEAD     : $LOCAL"
echo "   Clean    : yes"
echo ""
echo "Rappel ADR-015 / AGENTS.md :"
echo "  - Écris uniquement dans ledger/, ops/, _templates/, _scripts/, 99-meta/"
echo "  - Lie depuis une MOC (ops/moc/MOC-*.md) → G2 Zero Orphelin"
echo "  - Commit signé SSH ed25519 → G3"
echo "  - Valide localement : _scripts/check-orphans.sh . && _scripts/check-broken-links.sh ."
