---
type: audit-trail
date: 2026-05-07
chantier: CI infra hygiene (post-MVP-0 R-stack)
status: shipped
related_adr: []
related_prs:
  monorepo: [373]
related_memories:
  - feedback_no_overclaim_security_words
  - feedback_audit_workflow_before_proposing_infra
related_audit_trails:
  - 2026-05-07-mvp0-r-stack-shipped
---

# Audit-trail — GATE-3 false-positive fix (yaml-comment-aware grep)

## Synthèse

PR monorepo #373 (`fix/gate-3-false-positive-comment-match`) corrige un faux positif systématique du gate `tools/validator-gates/gate-3-runner-blast-radius.sh` invoqué par le job `🔍 DEV Safety (Observe)` du CI. Le check était rouge sur **toutes** les PRs du monorepo depuis l'introduction du workflow `dependabot-claude-review.yml`, polluant les rollups de status et déclenchant de faux signaux de risque supply-chain.

## Cause racine

Le gate fait un `grep -q "actions/checkout"` plat sur le contenu des workflows `.github/workflows/*.yml`. Quand un workflow utilise `pull_request_target` ET le grep matche `actions/checkout`, il déclenche `❌ CRITICAL: ... uses pull_request_target with actions/checkout`.

Or `dependabot-claude-review.yml` lignes 37-38 contient un commentaire **explicatif** qui mentionne `actions/checkout` pour documenter pourquoi il l'évite délibérément :

```yaml
# Pas de `actions/checkout` ici : DEV Safety GATE-3 interdit la combinaison
# `pull_request_target` + `actions/checkout` (risque d'exécution de code …)
```

Le grep ne distinguait pas la prose YAML du code YAML → false positive permanent.

## Fix

Patch dans `gate-3-runner-blast-radius.sh:19-26` :

1. **Strip yaml comments** via `sed 's/[[:space:]]*#.*//'` avant tout grep dans le check 1.
2. **Regex précise** `uses:[[:space:]]*actions/checkout` pour matcher seulement la syntaxe yaml `uses:` (la forme réelle d'invocation d'une action), pas la simple sous-chaîne.

Les autres checks du gate (self-hosted runner sans push-only guard, références production paths) sont inchangés. Les warnings existants sur `ci.yml`/`deploy-prod.yml` (commentaires mentionnant `~/production/.env`) restent émis — un fix similaire pourrait s'y appliquer en follow-up si le bruit devient gênant.

## Validation

- Local : `MODE=observe bash tools/validator-gates/gate-3-runner-blast-radius.sh` → `✅ GATE-3 PASSED` (au lieu de `🚫 GATE-3 FAILED (1 critical)`)
- CI : `🔍 DEV Safety (Observe)` PASS sur PR #373 elle-même (auto-test du fix)
- PR #373 mergée à 2026-05-07 20:02 UTC après cycle update-branch + auto-merge (race condition récurrente avec le rythme de merges sur main)

## Impact

- **Bruit CI éliminé** : le rollup de status de chaque PR future ne contient plus une ligne rouge permanente non-actionable
- **Crédibilité du gate restaurée** : un futur vrai positif ne sera plus noyé dans le bruit
- **Pattern réutilisable** : tout autre gate qui grep des fichiers yaml peut adopter le `sed 's/[[:space:]]*#.*//'` comme garde-fou

## Limites & honnêteté

- Réduction de bruit, pas une réduction de risque réelle (le supply-chain risk était déjà absent de `dependabot-claude-review.yml`, le fix ne fait que rendre le gate honnête à ce sujet)
- Pas une preuve que tous les workflows sont sûrs : le gate reste un check syntaxique, pas une analyse de flux

## Lessons learned

- **Gates qui grep des fichiers structurés (yaml/json/toml) doivent parser au moins minimalement la structure**, sinon ils échouent sur la documentation inline. Pour bash, `sed`/`awk` sur les commentaires est la première ligne. Pour des règles plus rigoureuses, préférer `yq`/`jq`/ast-grep.
- **Un check qui est rouge sur 100% des PRs perd toute valeur de signal** — il devient un coût (d'attention, de scroll dans le rollup) sans bénéfice. Soit on le fixe, soit on l'enlève.
- **Le commentaire `# Pas de actions/checkout ici` était lui-même un signal de gouvernance** (auteur du workflow conscient de la règle, choix délibéré documenté) — la règle aurait dû préserver ce métadonnée plutôt que la pénaliser.

## Refs

- PR : https://github.com/ak125/nestjs-remix-monorepo/pull/373
- Fichier modifié : `tools/validator-gates/gate-3-runner-blast-radius.sh`
- Workflow concerné : `.github/workflows/dependabot-claude-review.yml`
- Audit-trail amont (même session) : [[2026-05-07-mvp0-r-stack-shipped]]
