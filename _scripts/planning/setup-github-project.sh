#!/usr/bin/env bash
# One-shot setup GitHub Project v2 "AutoMecanik Planning Live" (ADR-053 Task 1.12).
# Prérequis : `gh auth refresh -s read:project,project --hostname github.com` (browser).
# Idempotent : skip si project existe déjà ; field-create idempotent (gracefully handles dup).
set -euo pipefail

OWNER="ak125"
TITLE="AutoMecanik Planning Live"
ADR_FILE="/opt/automecanik/governance-vault/ledger/decisions/adr/ADR-053-planning-live-system.md"

echo "[1/4] Verify gh auth has 'project' scope..."
if ! gh auth status 2>&1 | grep -q "project"; then
  echo "ERROR: gh token manque scope 'project'. Lance d'abord :"
  echo "  gh auth refresh -s read:project,project --hostname github.com"
  exit 1
fi

echo "[2/4] Create project (or reuse existing)..."
EXISTING=$(gh project list --owner "${OWNER}" --format json --jq ".projects[] | select(.title==\"${TITLE}\") | .number" 2>/dev/null || echo "")
if [ -n "${EXISTING}" ]; then
  PROJECT_NUMBER="${EXISTING}"
  echo "  Reusing existing project #${PROJECT_NUMBER}"
else
  CREATE_OUT=$(gh project create --owner "${OWNER}" --title "${TITLE}" --format json)
  PROJECT_NUMBER=$(echo "${CREATE_OUT}" | jq -r '.number')
  echo "  Created project #${PROJECT_NUMBER}"
fi

echo "[3/4] Get project_id (PV2_xxx) via GraphQL..."
PROJECT_ID=$(gh api graphql -f query='
  query($login: String!, $number: Int!) {
    organization(login: $login) {
      projectV2(number: $number) { id }
    }
  }' -f login="${OWNER}" -F number="${PROJECT_NUMBER}" \
  --jq '.data.organization.projectV2.id')
echo "  project_id=${PROJECT_ID}"

echo "[4/4] Create 9 custom fields (idempotent)..."
add_select() {
  local NAME="$1"; shift
  local OPTIONS="$1"
  if gh project field-list "${PROJECT_NUMBER}" --owner "${OWNER}" --format json --jq ".fields[] | select(.name==\"${NAME}\")" 2>/dev/null | grep -q .; then
    echo "  [skip] ${NAME} (exists)"
  else
    gh project field-create "${PROJECT_NUMBER}" --owner "${OWNER}" \
      --name "${NAME}" --data-type SINGLE_SELECT \
      --single-select-options "${OPTIONS}" >/dev/null
    echo "  [created] ${NAME} (single-select)"
  fi
}
add_text() {
  local NAME="$1"
  if gh project field-list "${PROJECT_NUMBER}" --owner "${OWNER}" --format json --jq ".fields[] | select(.name==\"${NAME}\")" 2>/dev/null | grep -q .; then
    echo "  [skip] ${NAME} (exists)"
  else
    gh project field-create "${PROJECT_NUMBER}" --owner "${OWNER}" \
      --name "${NAME}" --data-type TEXT >/dev/null
    echo "  [created] ${NAME} (text)"
  fi
}
add_number() {
  local NAME="$1"
  if gh project field-list "${PROJECT_NUMBER}" --owner "${OWNER}" --format json --jq ".fields[] | select(.name==\"${NAME}\")" 2>/dev/null | grep -q .; then
    echo "  [skip] ${NAME} (exists)"
  else
    gh project field-create "${PROJECT_NUMBER}" --owner "${OWNER}" \
      --name "${NAME}" --data-type NUMBER >/dev/null
    echo "  [created] ${NAME} (number)"
  fi
}

add_select "Priority" "P0,P1,P2,P3,P4,P5,P6,P7,P8"
add_select "ItemType" "PR,ADR,ROADMAP,INCIDENT,EPIC"
add_select "Status" "todo,in-progress,review,blocked,done,cancelled"
add_select "BlockedReason" "waiting-review,waiting-evidence,waiting-deploy,waiting-user,waiting-infra,waiting-dep,waiting-budget"
add_text "Owner"
add_number "StagnationDays"
add_text "DependsOn"
add_text "AdrLink"
add_text "CanonicalId"

echo ""
echo "=== Setup complete ==="
echo "project_number=${PROJECT_NUMBER}"
echo "project_id=${PROJECT_ID}"
echo ""
echo "Next : edit ADR-053 §Annexe A YAML block with these IDs :"
echo "  ${ADR_FILE}"
echo ""
echo "Replace the placeholder block with :"
cat <<YAML
github_project:
  project_number: ${PROJECT_NUMBER}
  project_id: "${PROJECT_ID}"
  field_ids:
$(gh project field-list "${PROJECT_NUMBER}" --owner "${OWNER}" --format json --jq '.fields[] | "    \(.name | ascii_downcase | gsub("[A-Z]"; "_\(.)") ): \"\(.id)\""' | tr '[:upper:]' '[:lower:]')
YAML
