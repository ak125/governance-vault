#!/usr/bin/env bash
# check-self-review-marker.sh - Vérifie le marker self-review obligatoire dans la PR body.
#
# Source canon : ledger/knowledge/vault-self-review-workflow-20260504.md §9
#
# Usage:
#   check-self-review-marker.sh <PR_NUMBER>
#   PR_NUMBER=148 check-self-review-marker.sh
#
# Env:
#   GH_TOKEN ou GITHUB_TOKEN : token avec scope `pull-requests:read`
#
# Markers acceptes (case-insensitive, **bold** tolere) :
#   - Self-review verdict: APPROVE        -> Claude a applique la 8-item checklist
#   - Self-review verdict: AUTO_SYNC      -> PR mecanique (canon-publish, Dependabot, etc.)
#   - Self-review verdict: HUMAN_AUTHORED -> PR humaine (auto-review explicit skip)
#
# Exit:
#   0 - marker valide trouve
#   1 - marker absent ou valeur invalide
#   2 - erreur runtime (gh CLI manquant, PR introuvable)
set -euo pipefail

PR_NUMBER="${1:-${PR_NUMBER:-}}"
if [[ -z "$PR_NUMBER" ]]; then
  echo "Error: PR_NUMBER non fourni (positional arg ou env)" >&2
  exit 2
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh CLI introuvable dans PATH" >&2
  exit 2
fi

if ! PR_BODY="$(gh pr view "$PR_NUMBER" --json body --jq .body 2>&1)"; then
  echo "Error: impossible de lire la PR #$PR_NUMBER" >&2
  echo "$PR_BODY" >&2
  exit 2
fi

# Pattern : tolere whitespaces, casse, **bold** Markdown, et ` `/`-` separator.
PATTERN='self[- ]review[ -]?verdict[[:space:]]*:[[:space:]]*\*{0,2}(APPROVE|AUTO_SYNC|HUMAN_AUTHORED)\*{0,2}'

if echo "$PR_BODY" | grep -qiE "$PATTERN"; then
  MATCHED=$(echo "$PR_BODY" | grep -oiE "$PATTERN" | head -1)
  echo "✅ Self-review marker trouvé : $MATCHED"
  exit 0
fi

cat >&2 <<EOF
❌ Marker self-review absent dans la PR body.

Format attendu (un de ces 3, ligne dans la description GitHub) :
  - Self-review verdict: APPROVE        -> Claude a appliqué la 8-item checklist
                                           (canon vault-self-review-workflow-20260504)
  - Self-review verdict: AUTO_SYNC      -> PR mécanique (canon-publish, Dependabot, ...)
  - Self-review verdict: HUMAN_AUTHORED -> PR humaine (auto-review explicit skip)

Voir : ledger/knowledge/vault-self-review-workflow-20260504.md §9 Marker
EOF

exit 1
