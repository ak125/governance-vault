#!/usr/bin/env bash
# check-vault-pollution.sh — ADR-060 §1A invariant 5 : aucune section opérationnelle dans le vault
#
# Contexte : ADR-060 « Repository Roles Doctrine » (accepted 2026-05-13) codifie 5 invariants
# dont l'invariant 5 : le vault contient uniquement de la **gouvernance**, pas de données métier
# opérationnelles. Ce gate bloque mécaniquement toute régression vers un mini-CMS dans le vault.
#
# Structure autorisée (canon ADR-015 + ADR-060) :
#   ledger/decisions/adr/      — ADRs canoniques
#   ledger/rules/              — Règles T/G/AI/V
#   ledger/knowledge/          — Audit-trail, handoff, governance knowledge UNIQUEMENT
#   ledger/audit-trail/        — Entrées audit-trail SoT (ADR-054)
#   ledger/incidents/          — Incidents formalisés
#   ledger/agents/             — Agents canoniques
#   ledger/compliance/         — Evidence-packs
#   ledger/policies/           — Policies AI/V
#   ops/runbooks/              — Runbooks opérationnels gouvernance
#   ops/moc/                   — Maps of Content
#   _scripts/                  — Scripts d'enforcement vault
#   _templates/                — Templates réutilisables
#   _assets/                   — Images, diagrammes
#   99-meta/                   — Gouvernance du vault (signing, reports)
#   .spec/                     — Specs canon
#
# Sections **interdites** (pollution opérationnelle métier) :
#   growth/        — marketing operating data
#   marketing/     — briefs, campaigns
#   seo/           — keywords, content drafts
#   content/       — articles, drafts
#   infra/         — infra-as-code, configs runtime
#   briefs/        — briefs métier
#   products/      — catalogue produits
#   catalogue/     — catalogue données
#   guides/        — guides produits (≠ runbooks gouvernance)
#   data/          — données brutes (≠ audit-trail SoT)
#
# Même règle applicable récursivement sous ledger/ : `ledger/<section-interdite>/` est rejeté.
#
# Usage :
#   ./_scripts/check-vault-pollution.sh [vault_path]
#
# Exit 0 : aucune pollution détectée
# Exit 1 : sections opérationnelles détectées (rapport dans 99-meta/vault-pollution-report.md)
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

# Patterns interdits — sections opérationnelles métier au root OU sous ledger/
FORBIDDEN_TOP='^(growth|marketing|seo|content|infra|briefs|products|catalogue|guides|data)/'
FORBIDDEN_LEDGER='^ledger/(catalogue|guides|data|products|briefs|growth|marketing|seo|content|infra)/'

POLLUTION_FILES="$(git ls-files | grep -E "$FORBIDDEN_TOP|$FORBIDDEN_LEDGER" || true)"

REPORT="99-meta/vault-pollution-report.md"

if [[ -z "$POLLUTION_FILES" ]]; then
  [[ -f "$REPORT" ]] && rm "$REPORT"
  echo "PASS: 0 vault pollution detected (ADR-060 §1A invariant 5 respected)"
  exit 0
fi

# Génération rapport
mkdir -p "$(dirname "$REPORT")"
COUNT="$(echo "$POLLUTION_FILES" | wc -l)"
{
  echo "---"
  echo "type: report"
  echo "status: generated"
  echo "generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "pollution_path_count: $COUNT"
  echo "rule: ADR-060-section-1A-invariant-5"
  echo "---"
  echo ""
  echo "# Vault Pollution Report (ADR-060 §1A invariant 5)"
  echo ""
  echo "**Sections opérationnelles métier détectées** : $COUNT fichier(s)"
  echo ""
  echo "Le vault \`governance-vault\` contient uniquement de la **gouvernance**, pas de données métier opérationnelles."
  echo "Sections interdites : \`growth/\`, \`marketing/\`, \`seo/\`, \`content/\`, \`infra/\`, \`briefs/\`, \`products/\`, \`catalogue/\`, \`guides/\`, \`data/\` (au root OU sous \`ledger/\`)."
  echo "Voir [[ADR-060-repository-roles-doctrine]] §1A invariant 5."
  echo ""
  echo "## Fichiers en path interdit"
  echo ""
  echo "$POLLUTION_FILES" | sed 's|^|- |'
  echo ""
  echo "## Action corrective"
  echo ""
  echo "1. Déplacer les données métier vers le repo approprié (monorepo \`backend/src/modules/<domain>/\`, wiki, raw, etc.)."
  echo "2. Si la donnée est **gouvernée** (décision, audit-trail, runbook), la reclasser sous \`ledger/\` ou \`ops/\` canonique."
  echo "3. Si la pollution est antérieure à ADR-060 (avant 2026-05-13), archiver via \`_archive/\` avec audit-trail entry expliquant la migration."
} > "$REPORT"

echo "FAIL: $COUNT polluted path(s) detected"
echo "Report: $REPORT"
echo ""
echo "First 5 violations:"
echo "$POLLUTION_FILES" | head -5 | sed 's|^|  - |'

exit 1
