#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-ak125/governance-vault}"
BRANCH="${BRANCH:-main}"

echo "Configuring branch protection for ${REPO}:${BRANCH}..."

gh api -X PUT "repos/${REPO}/branches/${BRANCH}/protection" \
  -H "Accept: application/vnd.github+json" \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "g2-orphans",
      "broken-links",
      "g3-signed-commits",
      "g4-canon-write-block"
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

echo ""
echo "Branch protection applied. Verify with:"
echo "  gh api repos/${REPO}/branches/${BRANCH}/protection | jq ."