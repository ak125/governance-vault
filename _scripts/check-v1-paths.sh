#!/usr/bin/env bash
# check-v1-paths.sh — Refuse les paths v1 (pré-refactor v2 2026-04-17)
#
# Contexte : ADR-015 + PR #7 (2026-04-18) ont montré qu'un agent peut créer du contenu
# dans l'ancienne structure v1 (01-incidents/, 02-decisions/, 03-rules/, etc.) si son
# clone est périmé ou si les conventions v2 ne sont pas connues. Ce gate CI bloque
# structurellement toute régression vers v1 paths.
#
# Structure v2 (ADR-015) :
#   ledger/ (historique immuable)  — incidents, decisions, audits, rules, policies, agents, knowledge, compliance
#   ops/    (opérationnel)         — moc/, rules/
#   _templates/                    — templates réutilisables
#   _scripts/                      — scripts d'enforcement
#   99-meta/                       — gouvernance du vault (signing, branch-protection, reports)
#   _assets/                       — images, diagrammes
#
# Paths v1 interdits (regex) :
#   ^0[0-9]-          — 00-index, 01-incidents, 02-decisions, 03-rules, 03-policies,
#                       04-audit-trail, 05-agents, 05-compliance, 06-compliance, 06-knowledge
#   ^scripts/         — renommé en _scripts/ sur v2 (le _ marque le statut "infra")
#
# Note : 99-meta/ NE matche PAS ^0[0-9]- (commence par 9), donc reste valide.
#
# Usage :
#   ./_scripts/check-v1-paths.sh [vault_path]
#
# Exit 0 : aucun path v1 détecté
# Exit 1 : paths v1 détectés (rapport dans 99-meta/v1-paths-report.md)
# Exit 2 : erreur (vault path missing, git indisponible)

set -euo pipefail

VAULT_PATH="${1:-$(cd "$(dirname "$0")/.." && pwd)}"

if [[ ! -d "$VAULT_PATH" ]]; then
  echo "Error: vault path not found: $VAULT_PATH" >&2
  exit 2
fi

cd "$VAULT_PATH"

if [[ ! -d .git ]]; then
  echo "Error: $VAULT_PATH n'est pas un repo git" >&2
  exit 2
fi

# Regex des patterns v1 interdits
V1_PATTERN='^(0[0-9]-[a-z-]+/|scripts/)'

# Tous les fichiers trackés
V1_FILES="$(git ls-files | grep -E "$V1_PATTERN" || true)"

REPORT="99-meta/v1-paths-report.md"

if [[ -z "$V1_FILES" ]]; then
  # Cleanup rapport obsolète si existait
  [[ -f "$REPORT" ]] && rm "$REPORT"
  echo "PASS: 0 v1 path detected (ADR-015 respected)"
  exit 0
fi

# Génération rapport
mkdir -p "$(dirname "$REPORT")"
COUNT="$(echo "$V1_FILES" | wc -l)"
{
  echo "---"
  echo "type: report"
  echo "status: generated"
  echo "generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "v1_path_count: $COUNT"
  echo "---"
  echo ""
  echo "# V1 Paths Report (ADR-015 violation)"
  echo ""
  echo "**Paths v1 détectés** : $COUNT fichier(s)"
  echo ""
  echo "La structure v1 (\`01-incidents/\`, \`02-decisions/\`, \`03-rules/\`, etc.) a été refactorée en v2 le 2026-04-17 (\`ledger/\` + \`ops/\`)."
  echo "Tout fichier sous un path v1 est une régression — voir [[ADR-015-vault-single-source-of-truth]]."
  echo ""
  echo "## Fichiers en path v1"
  echo ""
  while IFS= read -r f; do
    echo "- \`$f\`"
  done <<< "$V1_FILES"
  echo ""
  echo "## Action requise"
  echo ""
  echo "1. Pour chaque fichier, déterminer la destination v2 correcte (voir [[AGENTS]] §Placement par type)"
  echo "2. \`git mv\` vers le nouveau path (ex : \`01-incidents/YYYY/x.md\` → \`ledger/incidents/YYYY/x.md\`)"
  echo "3. Mettre à jour les wikilinks qui pointaient vers l'ancien path"
  echo "4. Vérifier avec \`_scripts/check-orphans.sh\` et \`_scripts/check-broken-links.sh\`"
  echo "5. Commit signé : \`docs(refactor): migrate v1 paths to v2 (ADR-015)\`"
} > "$REPORT"

echo "FAIL: $COUNT v1 path(s) detected"
echo "Report: $REPORT"
echo ""
echo "Sample (first 10):"
echo "$V1_FILES" | head -10 | sed 's/^/  - /'
exit 1
