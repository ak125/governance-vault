#!/usr/bin/env bash
# Synchronise les miroirs dans un worktree Git dedie (ADR-061 §3).
# Le checkout partage garde sa branche, son index et ses fichiers, meme sales.
# Les commits restent signes ; la PR reste soumise a fusion humaine.
# Usage : sans argument = projection + commit + push + PR ; dry = lecture seule.
# MONOREPO_ROOT : depot DEV de reference (defaut /opt/automecanik/app).
# Signature Git et authentification gh existantes requises ; aucune configuration ici.

set -euo pipefail

VAULT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MONOREPO_ROOT="${MONOREPO_ROOT:-/opt/automecanik/app}"

if (( $# > 1 )) || [[ "${1:-}" != "" && "${1:-}" != "dry" ]]; then
  echo "Usage: $0 [dry]" >&2
  exit 2
fi
if [[ ! -d "$MONOREPO_ROOT" ]]; then
  echo "Error: monorepo not found at $MONOREPO_ROOT" >&2
  exit 2
fi
MONOREPO_ROOT="$(cd "$MONOREPO_ROOT" && pwd -P)"

# Preview : aucun fetch, branche, commit ou appel GitHub.
if [[ "${1:-}" == "dry" ]]; then
  python3 "$VAULT_ROOT/_scripts/sync_canon_mirrors.py" --dry-run --monorepo "$MONOREPO_ROOT"
  exit 0
fi
if [[ "$(git -C "$MONOREPO_ROOT" rev-parse --show-toplevel)" != "$MONOREPO_ROOT" ]]; then
  echo "Error: MONOREPO_ROOT must be a Git checkout root" >&2
  exit 2
fi

TODAY="$(date -u +%Y-%m-%d)"
TIMESTAMP="$(date -u +%Y-%m-%dT%H%M%SZ)"
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/canon-sync.XXXXXXXX")"
WORKTREE="$RUN_DIR/worktree"
BRANCH="govvault/cron-sync-canon-mirrors-${TIMESTAMP}-${RUN_DIR##*.}"
NO_CHANGES=false

# Git n'ecrit ni ne retire .git/worktrees/<id>/ de facon atomique. Pendant un
# `worktree add` ou un `worktree remove`, une commande qui enumere les worktrees
# (fetch vers une branche locale, worktree add, worktree remove) peut lire une entree
# incomplete ou un dossier disparu et echouer :
#   « failed to read .git/worktrees/<id>/commondir: Success »                      (code 128)
#   « failed to read .git/worktrees/<id>/commondir: No such file or … »            (code 128)
#   « could not create directory of '.git/worktrees/<id>': No such file or … »     (code 128)
#   « bad object worktrees/<id>/HEAD »                                             (code 1)
# Ces trois commandes passent donc par un verrou partage entre les runs de ce script,
# pose sur le depot Git commun (aucun fichier cree). Le verrou est tenu par le
# descripteur 9 de ce script, que Git n'herite pas (9<&-) : un code de sortie de Git ne
# se confond pas avec un verrou non obtenu, et un processus que Git laisse derriere lui
# (maintenance) ne garde pas le verrou. Verrou non obtenu en LOCK_TIMEOUT secondes : la
# commande Git n'est pas lancee et worktree_admin rend 75. Le run sort alors en 75 au
# fetch et au `worktree add` (aucun commit ni PR ; au `worktree add`, la branche locale
# du run reste), en 1 au `worktree remove` (le resultat du run est deja produit, le
# worktree reste : voir finish). Le verrou ne couvre pas les commandes Git lancees hors
# de ce script : voir le runbook, « Verrou des worktrees ».
LOCK_TIMEOUT=120
GIT_COMMON_DIR="$(git -C "$MONOREPO_ROOT" rev-parse --path-format=absolute --git-common-dir)"
worktree_admin() {
  local label="$1" result=0
  if [[ "$1" == worktree ]]; then
    label="worktree $2"
  fi
  if ! exec 9<"$GIT_COMMON_DIR"; then
    echo "Error: cannot open $GIT_COMMON_DIR for locking (git $label not run)." >&2
    return 1
  fi
  flock --timeout "$LOCK_TIMEOUT" --conflict-exit-code 75 9 || result=$?
  if (( result != 0 )); then
    exec 9<&-
    if (( result == 75 )); then
      echo "Error: worktree lock not obtained within $LOCK_TIMEOUT s on $GIT_COMMON_DIR (git $label not run)." >&2
    else
      echo "Error: flock failed (code $result) on $GIT_COMMON_DIR (git $label not run)." >&2
    fi
    return "$result"
  fi
  git -C "$MONOREPO_ROOT" "$@" 9<&- || result=$?
  exec 9<&-
  return "$result"
}

finish() {
  local result=$?
  if (( result != 0 )); then
    echo "Error: sync failed; retain branch $BRANCH and worktree $WORKTREE for recovery (if created)." >&2
    # Une erreur de l'API peut arriver apres creation de la PR : ne pas supprimer
    # la branche distante, ni les preuves locales d'un commit/push incomplet.
    return "$result"
  fi
  cd "$MONOREPO_ROOT"
  # Signal recu pendant le nettoyage, attente du verrou comprise : dire ou sont les restes.
  trap 'echo "Error: interrupted during cleanup; inspect $RUN_DIR" >&2; exit 1' INT TERM
  # Sans --force : si un hook ou une intervention a laisse du travail, le garder.
  # Code 1 quelle que soit la cause (Git ou verrou) : a ce stade le run a deja produit
  # son resultat, et c'est le worktree conserve qui demande une intervention.
  if ! worktree_admin worktree remove "$WORKTREE"; then
    echo "Error: worktree retained for inspection: $WORKTREE" >&2
    exit 1
  fi
  if [[ "$NO_CHANGES" == true ]]; then
    # Supprime uniquement notre ref sans commit nouveau, si elle n'a pas bouge.
    git update-ref -d "refs/heads/$BRANCH" "$BASE"
  fi
  # Derniere commande : un signal recu maintenant n'a plus rien a signaler ; l'ignorer
  # plutot que sortir en 1 sur un run nettoye. Apres les commandes Git, pas avant : lance
  # avec ces signaux ignores, Git retire ses verrous au signal puis continue sans eux.
  trap '' INT TERM
  rmdir "$RUN_DIR"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Ref unique par run : pas de checkout/reset de main, ni de course sur FETCH_HEAD.
# Une branche preexistante n'est jamais reutilisee.
if git -C "$MONOREPO_ROOT" show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo "Error: sync branch already exists: $BRANCH" >&2
  exit 1
fi
worktree_admin fetch --quiet --no-write-fetch-head origin "refs/heads/main:refs/heads/$BRANCH"
BASE="$(git -C "$MONOREPO_ROOT" rev-parse "refs/heads/$BRANCH^{commit}")"
worktree_admin worktree add --quiet "$WORKTREE" "$BRANCH"
cd "$WORKTREE"

python3 "$VAULT_ROOT/_scripts/sync_canon_mirrors.py" --write --monorepo "$WORKTREE"

# Indexer avant le test de diff inclut aussi les miroirs nouvellement crees.
# Un echec d'indexation est une erreur ; ne jamais le masquer par `|| true`.
git add --all -- .claude/canon-mirrors/ ':(glob)workspaces/*/.claude/canon-mirrors/**'
if git diff --cached --quiet; then
  NO_CHANGES=true
  echo "OK: no canon mirror drift, no PR opened"
  exit 0
fi

git commit -S -m "chore(canon-mirrors): auto-sync from vault — ${TODAY}" \
  -m "Generated by governance-vault/_scripts/sync_canon_mirrors.py (ADR-061 §3)."
git push -u origin "$BRANCH" --quiet

gh pr create --repo ak125/nestjs-remix-monorepo \
  --base main \
  --head "$BRANCH" \
  --title "chore(canon-mirrors): auto-sync from vault — ${TODAY}" \
  --body-file - \
  --label "auto" <<EOF
Auto-PR par cron VPS DEV (ADR-061 §3), preparee dans un worktree Git isole.

Projection des miroirs depuis le manifeste et les sources du governance-vault.
Le checkout partage et ses modifications en cours sont preserves.

Reviewer humain valide ou ferme.
EOF

echo "OK: auto-PR opened on branch $BRANCH"
