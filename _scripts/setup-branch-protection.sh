#!/usr/bin/env bash
# Configuration versionnee de la protection de main (99-meta/branch-protection.md).
#
#   setup-branch-protection.sh           PUT complet puis relecture : (re)cree la protection
#   setup-branch-protection.sh --check   relecture seule : compare la protection en vigueur
#                                        a ce fichier, ne modifie rien
#
# Pour ajouter ou retirer un check sur une protection existante : PATCH de la
# sous-ressource required_status_checks, puis --check
# (ledger/knowledge/vault-branch-protection-contexts-vs-checks-gotcha-20260504.md).
# Sorties : 0 conforme, 1 protection differente de ce fichier, 2 usage ou prerequis.
set -euo pipefail

REPO="${REPO:-ak125/governance-vault}"
BRANCH="${BRANCH:-main}"
EP="repos/${REPO}/branches/${BRANCH}/protection"

case "${1:-}" in
  "") MODE=apply ;;
  --check) MODE=check ;;
  *) echo "usage: $0 [--check]" >&2; exit 2 ;;
esac
command -v gh >/dev/null || { echo "gh requis" >&2; exit 2; }
command -v jq >/dev/null || { echo "jq requis" >&2; exit 2; }

# checks = noms affiches des jobs (champ `name:` des workflows), pas les cles de
# job, lies a GitHub Actions (app_id 15368) : sans app_id, n'importe quelle app
# pourrait rapporter le check, et `contexts` (deprecie) ignore sans erreur un nom
# jamais observe. Un check qu'aucun job ne rapporte bloque toutes les PR : renommer
# un job impose de mettre a jour cette liste dans la meme PR
# (_scripts/test_setup_branch_protection.py le verifie).
BODY="$(cat <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "G2: Zero Orphelin", "app_id": 15368},
      {"context": "Broken Wikilinks", "app_id": 15368},
      {"context": "G3: Commits signes", "app_id": 15368},
      {"context": "G4: CI read-only sur canon", "app_id": 15368},
      {"context": "No V1 Paths (ADR-015)", "app_id": 15368},
      {"context": "Vault Scripts Tests", "app_id": 15368},
      {"context": "Vault Lint Gate (ADR-020)", "app_id": 15368}
    ]
  },
  "enforce_admins": true,
  "required_linear_history": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true
}
JSON
)"

# Memes champs, forme de la demande (PUT) et forme de la reponse (GET).
WANT='{
  strict: .required_status_checks.strict,
  checks: (.required_status_checks.checks | sort_by(.context)),
  enforce_admins, required_linear_history,
  reviews: .required_pull_request_reviews,
  restrictions, allow_force_pushes, allow_deletions, block_creations,
  required_conversation_resolution
}'
GOT='{
  strict: .required_status_checks.strict,
  checks: (.required_status_checks.checks | map({context, app_id}) | sort_by(.context)),
  enforce_admins: .enforce_admins.enabled,
  required_linear_history: .required_linear_history.enabled,
  reviews: (.required_pull_request_reviews
    | {required_approving_review_count, dismiss_stale_reviews, require_code_owner_reviews}),
  restrictions,
  allow_force_pushes: .allow_force_pushes.enabled,
  allow_deletions: .allow_deletions.enabled,
  block_creations: .block_creations.enabled,
  required_conversation_resolution: .required_conversation_resolution.enabled
}'

verify() {
  local current
  current="$(gh api "$EP")" || { echo "ERREUR : lecture de la protection impossible" >&2; return 2; }
  if ! diff <(jq -S "$WANT" <<<"$BODY") <(jq -S "$GOT" <<<"$current"); then
    echo "ERREUR : la protection de ${REPO}:${BRANCH} differe de ce fichier (< attendu, > en vigueur)" >&2
    return 1
  fi
}

if [[ "$MODE" == check ]]; then
  verify
  echo "OK : la protection de ${REPO}:${BRANCH} est conforme a ce fichier."
  exit 0
fi

echo "Configuring branch protection for ${REPO}:${BRANCH}..."
gh api -X PUT "$EP" -H "Accept: application/vnd.github+json" --input - <<<"$BODY" >/dev/null
# Le 200 ne prouve rien (drop silencieux possible) : relire et comparer a la demande.
verify
echo "OK : protection appliquee et relue conforme a ce fichier."
