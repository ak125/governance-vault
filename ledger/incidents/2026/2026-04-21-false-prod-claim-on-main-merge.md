---
id: INC-2026-007
date: 2026-04-21
severity: low
status: resolved
impact_duration: "~2 minutes (durée de la confusion avant correction)"
affected_systems: [governance-communication, agent-workflow]
root_cause: "Documentation .claude/rules/deployment.md ambiguë ('git push main → Deploy') ne distinguait pas DEV préprod de PROD. Agent AI a interprété 'Deploy' comme PROD."
related_rules: [rules-deployment-workflow]
related_adr: []
owner: "@fafa"
reviewed_by: ""
---

# Incident: False PROD Deploy Claim on Main Merge

## Timeline

| Heure (UTC) | Événement |
|-------------|-----------|
| ~11:15 | Agent merge PR #86 monorepo sur `main` via `gh pr merge` |
| ~11:15 | Agent annonce : "Prod dans ~10 min" (factuellement faux) |
| ~11:17 | Owner corrige : "le push main pousse en pré-prod sur dev et le push main tag push sur prod" |
| ~11:18 | Agent inspecte `.github/workflows/ci.yml` et `deploy-prod.yml` → confirme workflow réel |
| ~11:20 | Agent écrit memory Claude + règle vault + corrige `.claude/rules/deployment.md` monorepo |
| ~11:32 | PR #19 vault MERGED (règle canon D1-D6) |
| ~12:24 | PR #91 monorepo MERGED (doc corrigée) |

## Impact

- **Utilisateurs affectés**: 0 (pas d'impact technique)
- **Transactions perdues**: 0
- **Durée d'indisponibilité**: 0 min
- **Impact business**: 0
- **Impact gouvernance**: claim factuellement faux dans un message agent → risque de perte de confiance si généralisé

## Root Cause

`.claude/rules/deployment.md` disait uniquement :
> `git push main` → Lint → TypeCheck → Build Docker → Deploy (~5-10 min).

Cette phrase ambiguë omettait la distinction **DEV préprod** vs **PROD** :

| Trigger | Réalité (vérifiable dans workflow files) |
|---------|-------------------------------------------|
| `push main` | `ci.yml` job `deploy` → image `preprod` → VPS DEV 46.224.118.55 |
| `push tag v*` | `deploy-prod.yml` → promote preprod → production → VPS PROD 49.12.233.2 |

L'agent a lu "Deploy" et supposé "prod" (biais induit par le titre de fichier `# Production Deployment`).

## Résolution

Trois actions menées simultanément :

```bash
# 1. Memory Claude (prévention agent future)
~/.claude/projects/-opt-automecanik-app/memory/deployment-workflow.md

# 2. Règle canon vault (source de vérité gouvernance)
governance-vault/ledger/rules/rules-deployment-workflow.md (D1-D6)
# Enregistrée dans MOC-Rules.md section "Deployment (D)"

# 3. Doc monorepo corrigée (source de vérité opérationnelle)
app/.claude/rules/deployment.md (renamed "Production Deployment" → "Deployment DEV preprod + PROD")
```

Livré via :
- PR #19 vault (MERGED 11:32 UTC)
- PR #91 monorepo (MERGED 12:24 UTC)

## Lessons Learned

1. **La doc ambiguë est un bug**. Une phrase qui peut être lue de 2 façons = 50% de risque d'erreur. Formuler comme un tableau trigger → action évite toute interprétation.
2. **Les titres biaisent**. Titre "Production Deployment" du fichier a amorcé la mauvaise interprétation, indépendamment du contenu. Renommer le titre pour refléter DEV+PROD.
3. **Agent doit vérifier les workflow files avant d'annoncer un déploiement**. Ne jamais croire la doc Markdown sur la foi du nom de fichier.
4. **Règle mnémonique courte bat une doc longue**. "`main` = DEV, `v*` = PROD" est plus durable qu'un paragraphe explicatif.

## Actions correctives suivies

| Action | Status | Livrable |
|--------|--------|----------|
| Règle canon vault D1-D6 | Complete | PR #19 MERGED |
| Doc monorepo corrigée | Complete | PR #91 MERGED |
| Memory Claude agent | Complete | `deployment-workflow.md` |
| Pre-push hook vault anti-orphan | Complete | PR #18 MERGED (contexte adjacent, prévient autre classe de friction CI) |
| Tests automatiques "no false prod claim" | Planifie | Difficile à tester automatiquement (texte libre agent). Prévention = formulation sans ambiguïté dans la doc (fait). |

## Références

- Règle : [[rules-deployment-workflow]]
- PRs : #19 vault, #91 monorepo
- Source code : `.github/workflows/ci.yml:679`, `.github/workflows/deploy-prod.yml:3-5`
