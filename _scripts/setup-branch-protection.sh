#!/usr/bin/env bash
# setup-branch-protection.sh - Configure la protection de branche main.
#
# Cette config enforce les regles G1-G4 cote serveur (GitHub):
#   - Aucun push direct sur main (PR obligatoire)
#   - Les 4 CI checks doivent passer (g2-orphans, broken-links, g3-signed-commits, g4-canon-write-block)
#   - Historique lineaire (pas de merge commits)
#   - Admins eux-memes soumis aux regles
#
# Prerequis: gh auth login effectue, token avec scope admin:repo
#
# Usage (une seule fois, ou apres recreation du repo):
#   _scripts/setup-branch-protection.sh
#
# Note: `required_signatures` n'est PAS inclus car il necessite un plan GitHub
# Pro/Team pour les repos prives. Notre CI job `g3-signed-commits` fait le meme
# travail en verifiant %G? sur chaque commit du push/PR.

set -euo pipefail

REPO="${REPO:-ak125/governance-vault}"
BRANCH="${BRANCH:-main}"

echo "Configuring branch protection for ${REPO}:${BRANCH}..."

gh api -X PUT "repos/${REPO}/branches/${BRANCH}/protection" \
  -H "Accept: application/vnd.github+json" \
  -F required_status_checks.strict=true \
  -f 'required_status_checks.contexts[]=g2-orphans' \
  -f 'required_status_checks.contexts[]=broken-links' \
  -f 'required_status_checks.contexts[]=g3-signed-commits' \
  -f 'required_status_checks.contexts[]=g4-canon-write-block' \
  -F enforce_admins=true \
  -F required_linear_history=true \
  -F required_pull_request_reviews.required_approving_review_count=0 \
  -F required_pull_request_reviews.dismiss_stale_reviews=true \
  -F restrictions= \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  -F block_creations=false \
  -F required_conversation_resolution=true

echo ""
echo "Branch protection applied. Verify with:"
echo "  gh api repos/${REPO}/branches/${BRANCH}/protection | jq ."
