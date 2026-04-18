#!/usr/bin/env bash
# _scripts/new-incident.sh — Scaffold un nouveau post-mortem incident (vault v2)
#
# Usage:
#   ./_scripts/new-incident.sh <severity> <slug> [id]
#
# Exemples:
#   ./_scripts/new-incident.sh critical paybox-tunnel
#   ./_scripts/new-incident.sh high redis-sessions-loss INC-2026-003
#
# Effets:
#   1. Crée fichier ledger/incidents/YYYY/YYYY-MM-DD-<slug>.md depuis le template
#   2. Frontmatter YAML pré-rempli (id, date, severity, status: investigating)
#   3. Crée branche git docs/<id>-<slug>
#   4. Ouvre $EDITOR
#   5. Rappelle les prochaines étapes

set -euo pipefail

# --- Validation args ---
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  cat <<USAGE
Usage: $0 <severity> <slug> [id]

  severity  : critical | high | medium | low
  slug      : slug-url-safe du titre incident (ex: paybox-tunnel-sev1)
  id        : optionnel, format INC-YYYY-NNN (auto-calculé sinon)

Exemples:
  $0 critical paybox-tunnel-sev1
  $0 high redis-sessions-loss INC-2026-003
USAGE
  exit 2
fi

SEVERITY="$1"
SLUG="$2"
CUSTOM_ID="${3:-}"

case "$SEVERITY" in
  critical|high|medium|low) ;;
  *)
    echo "ERR: severity doit être critical|high|medium|low (reçu: $SEVERITY)" >&2
    exit 2
    ;;
esac

# --- Vérifications pré-flight ---
VAULT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$VAULT_ROOT"

if [ ! -d .git ]; then
  echo "ERR: $VAULT_ROOT n'est pas un repo git" >&2
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "WARN: branche courante = $CURRENT_BRANCH (attendu: main)"
  read -r -p "Continuer quand même ? [y/N] " REPLY
  [[ "$REPLY" =~ ^[Yy]$ ]] || exit 1
fi

# --- Variables (paths v2) ---
TODAY="$(date +%Y-%m-%d)"
YEAR="$(date +%Y)"
TARGET_DIR="ledger/incidents/$YEAR"
TEMPLATE="_templates/incident-template.md"

if [ ! -f "$TEMPLATE" ]; then
  echo "ERR: template manquant: $TEMPLATE" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

# --- Calcul ID auto si pas fourni ---
if [ -z "$CUSTOM_ID" ]; then
  LAST_NUM="$(grep -rEho 'id: INC-'"$YEAR"'-[0-9]+' ledger/incidents/ 2>/dev/null \
    | sed -E 's/.*-([0-9]+)$/\1/' \
    | sort -n | tail -1 || echo '000')"
  LAST_NUM="${LAST_NUM:-000}"
  NEXT_NUM="$(printf "%03d" $((10#$LAST_NUM + 1)))"
  INC_ID="INC-${YEAR}-${NEXT_NUM}"
else
  INC_ID="$CUSTOM_ID"
fi

TARGET_FILE="${TARGET_DIR}/${TODAY}-${SLUG}.md"
BRANCH_NAME="docs/${INC_ID,,}-${SLUG}"

if [ -f "$TARGET_FILE" ]; then
  echo "ERR: fichier existe déjà: $TARGET_FILE" >&2
  exit 1
fi

# --- Création branche ---
if git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1; then
  echo "WARN: branche $BRANCH_NAME existe, checkout sans create"
  git checkout "$BRANCH_NAME"
else
  git checkout -b "$BRANCH_NAME"
fi

# --- Génération fichier depuis template avec frontmatter pré-rempli ---
cat > "$TARGET_FILE" <<EOF
---
id: $INC_ID
type: incident
title: "[Titre court — à remplir]"
date: $TODAY
date_detected: $TODAY
date_resolved: ""
severity: $SEVERITY
status: investigating
impact_duration: ""
affected_systems: []
root_cause: ""
related_rules: []
related_adrs: []
owner: "@automecanik.seo"
reviewed_by: ""
tags:
  - incident/$SEVERITY
  - post-mortem
---

# $INC_ID: [Titre court — à remplir]

> [!danger] Résumé
> [Description 1-2 phrases de l'impact visible]

## Timeline

| Heure UTC | Événement |
|-----------|-----------|
| HH:MM | Détection |
| HH:MM | Investigation démarrée |
| HH:MM | Root cause identifiée |
| HH:MM | Résolution appliquée |
| HH:MM | Service restauré |

## Impact

- **Utilisateurs affectés** : X
- **Transactions perdues** : Y
- **Durée d'indisponibilité** : Z minutes
- **Impact business** : [description]

## Root Cause

[Description technique détaillée]

## Résolution

\`\`\`bash
# Commandes exécutées
\`\`\`

## Preuves

- Commit: \`[sha]\`
- Log: [lien]
- Migration SQL: [lien]

## Lessons Learned

1. [Leçon 1]
2. [Leçon 2]

## Actions Correctives

- [ ] [Action 1] — Owner: @xxx — Deadline: YYYY-MM-DD
- [ ] [Action 2] — Owner: @xxx — Deadline: YYYY-MM-DD

## Communication

- [ ] Équipe notifiée
- [ ] Stakeholders informés
- [ ] Post-mortem partagé

## Références

- [[2026-MM-DD-related-incident]]
- [[ADR-NNN-related-decision]]
- [[MOC-Incidents]]

---

*Créé le: $TODAY*
*Owner: @automecanik.seo*
*Status: investigating*
EOF

echo ""
echo "=== Incident scaffolded (v2 paths) ==="
echo "  ID      : $INC_ID"
echo "  File    : $TARGET_FILE"
echo "  Branch  : $BRANCH_NAME"
echo ""
echo "Prochaines étapes :"
echo "  1. Remplir le contenu (\$EDITOR = ${EDITOR:-nano})"
echo "  2. Lier depuis ops/moc/MOC-Incidents.md (G2: zéro orphelin)"
echo "  3. Valider: ./_scripts/check-orphans.sh . && ./_scripts/check-broken-links.sh ."
echo "  4. Commit signé: git add -A && git commit -S -m \"docs(incident): $INC_ID — [titre]\""
echo "  5. Push + PR:   git push -u origin $BRANCH_NAME && gh pr create --base main"
echo ""

# --- Ouvre éditeur si dispo ---
if [ -n "${EDITOR:-}" ]; then
  "$EDITOR" "$TARGET_FILE"
fi
