#!/usr/bin/env bash
# audit-signatures.sh - Audit mensuel des signatures de commits
# Usage: ./audit-signatures.sh [--report]
#
# Sans --report: affiche le résultat sur stdout
# Avec --report: génère 99-meta/reports/YYYY-MM-signature-audit.md
set -euo pipefail

VAULT_PATH="${VAULT_PATH:-/opt/automecanik/governance-vault}"
GENERATE_REPORT=false

if [[ "${1:-}" == "--report" ]]; then
  GENERATE_REPORT=true
fi

cd "$VAULT_PATH"

# Collecter tous les commits
TOTAL=0
SIGNED=0
UNSIGNED=()

while read -r commit_hash; do
  ((TOTAL++)) || true
  if git verify-commit "$commit_hash" >/dev/null 2>&1; then
    ((SIGNED++)) || true
  else
    UNSIGNED+=("$commit_hash")
  fi
done < <(git log --pretty=format:'%H')

# Générer le rapport
REPORT_DATE=$(date +%Y-%m)
REPORT_CONTENT="# Audit Signatures - $REPORT_DATE

**Date**: $(date -Iseconds)
**Vault**: $VAULT_PATH
**Total commits**: $TOTAL
**Signés**: $SIGNED
**Non signés**: ${#UNSIGNED[@]}

---

## Résultat

"

if [ "${#UNSIGNED[@]}" -eq 0 ]; then
  REPORT_CONTENT+="✅ **TOUS LES COMMITS SONT SIGNÉS**

Aucune anomalie détectée. La piste d'audit est intègre.
"
  STATUS="✅ OK"
else
  REPORT_CONTENT+="❌ **COMMITS NON SIGNÉS DÉTECTÉS**

| SHA | Date | Auteur | Message |
|-----|------|--------|---------|
"
  for c in "${UNSIGNED[@]}"; do
    info=$(git log -1 --format='| %h | %ai | %an | %s |' "$c")
    REPORT_CONTENT+="$info
"
  done

  REPORT_CONTENT+="
---

## Actions Requises

1. Investiguer chaque commit non signé
2. Vérifier si le commit est légitime
3. Documenter dans [[../01-incidents/]] si compromission
4. Considérer re-signature si possible (rebase interactif)

> **Attention**: Un commit non signé invalide la piste d'audit depuis ce point.
"
  STATUS="❌ ${#UNSIGNED[@]} non signés"
fi

REPORT_CONTENT+="
---

## Prochaine Exécution

Planifier l'audit pour le mois suivant.

*Généré automatiquement par audit-signatures.sh*
"

if [ "$GENERATE_REPORT" = true ]; then
  REPORT_DIR="$VAULT_PATH/99-meta/reports"
  mkdir -p "$REPORT_DIR"
  REPORT_FILE="$REPORT_DIR/${REPORT_DATE}-signature-audit.md"
  echo "$REPORT_CONTENT" > "$REPORT_FILE"
  echo "📄 Rapport généré: $REPORT_FILE"
fi

echo ""
echo "=== Audit Signatures ($REPORT_DATE) ==="
echo "Total: $TOTAL | Signés: $SIGNED | Non signés: ${#UNSIGNED[@]}"
echo "Status: $STATUS"
