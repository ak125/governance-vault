---
type: retrospective
date: 2026-04-21
owner: Fafa
duration: ~8h
session_id: r7-brand-live-sync-complete
related_prs:
  monorepo: [86, 91, 92, 94]
  vault: [14, 15, 16, 18, 19, 21, 23]
tags: [r7, retrospective, session-log, deployment]
---

# Session Retrospective — R7 Brand Live-Sync Architecture Complete

> **Date** : 2026-04-21
> **Scope** : architecture R7 constructeur complète (backend + frontend + admin UI) + gouvernance + déploiement prod

---

## TL;DR

Ship complet de l'architecture R7 constructeur canonical : 36/36 pages PUBLISH avec contenu brand-specific (Wikidata + DB + Wikipedia), admin UI pour curer FAQ/issues/maintenance, auto-trigger enrichSingle sur PUT editorial, **zéro friction curation**. Déployé en PROD via tag `v2026.04.21-r7-popular-parts-fix`.

## Livrables

### Monorepo (ak125/nestjs-remix-monorepo) — 4 PRs MERGED

| PR | Titre | Impact |
|----|-------|--------|
| [#86](https://github.com/ak125/nestjs-remix-monorepo/pull/86) | feat(r7): live-sync editorial + Wikidata canonical RAG | Architecture de base |
| [#91](https://github.com/ak125/nestjs-remix-monorepo/pull/91) | docs(deployment): push main = DEV preprod, tag v* = PROD | Correction doc ambiguë |
| [#92](https://github.com/ak125/nestjs-remix-monorepo/pull/92) | feat(admin-brand): editorial R7 editor (FAQ/issues/maintenance) | Admin UI curation |
| [#94](https://github.com/ak125/nestjs-remix-monorepo/pull/94) | fix(r7): show vehicle name + remove "Universel" on popular parts | Fix rendering visible |

### Governance Vault (ak125/governance-vault) — 7 PRs MERGED

| PR | Titre | Type |
|----|-------|------|
| [#14](https://github.com/ak125/governance-vault/pull/14) | knowledge: r7-brand-route-refactoring | Patterns frontend |
| [#15](https://github.com/ak125/governance-vault/pull/15) | knowledge: r7-brand-editorial-live-sync (merged via #16) | Architecture |
| [#16](https://github.com/ak125/governance-vault/pull/16) | knowledge: r7-surface-purity-no-cross-surface-urls | Règle pureté |
| [#18](https://github.com/ak125/governance-vault/pull/18) | chore(hooks): pre-push G2 + broken-wikilinks | Automation CI |
| [#19](https://github.com/ak125/governance-vault/pull/19) | rules: deployment-workflow D1-D6 (DEV preprod vs PROD tag) | Règle canon |
| [#21](https://github.com/ak125/governance-vault/pull/21) | docs: INC-2026-007 + pre-push hook pattern | Incident + pattern |
| [#23](https://github.com/ak125/governance-vault/pull/23) | runbook: build-brand-rag.py | Runbook ops |

### Déploiement PROD

- Tag : `v2026.04.21-r7-popular-parts-fix` (déployé 2026-04-21 ~13:30 UTC)
- VPS : 49.12.233.2 (via `deploy-prod.yml`)
- Image : `massdoc/nestjs-remix-monorepo:production`
- Status : Success (32m 56s)

## Architecture finale R7

```
┌─────────────────────────────────────────────────────────────────┐
│ SOURCES DE VÉRITÉ (une par champ, zéro scraping HTML)           │
├─────────────────────────────────────────────────────────────────┤
│ country, founded, group, headquarters, logo  → Wikidata SPARQL  │
│ top_models, top_engines                       → DB RPC agg      │
│ history                                       → Wikipedia REST  │
│ faq, common_issues, maintenance_tips          → __seo_brand_editorial │
└─────────────────────────────────────────────────────────────────┘
              ↓                                    ↓
      ┌───────────────┐                    ┌──────────────┐
      │ .md frontmatter │                    │ DB editorial │
      │ (stable, 18 champs canoniques) │    │ (live, curé) │
      │ Schéma Zod validé au load       │    └──────────────┘
      └────────────┬──────────────────────────────┘
                   ↓
         R7BrandEnricherService
         (merge rag + editorial, compose 11 blocs)
                   ↓
            __seo_r7_pages (36/36 PUBLISH)
                   ↓
         /constructeurs/{alias}-{id}.html
```

## Métriques

| Avant session | Après session |
|---------------|----------------|
| 3 sections body / 11 déclarées | 11 blocs renderedJson complets |
| `country` mal mappé (pays→country bug) | 34/36 country Wikidata |
| diversity_score moyen 79.40 | diversity_score moyen 80.86 (85.41 avec curation) |
| Boilerplate 100% identique | Prose Wikipedia par marque, modèles DB, adjectif pays |
| 3 étapes manuelles pour curer | 1 PUT auto-trigger enrichSingle |
| URLs S3 dérive R8 | S3 R7-pur (gammes pièces) |
| Cards "Universel" sans modèle | Modèle + motorisation visible + badge year/ch |

## Ce qui a bien marché

1. **Approche "pas de bricolage"** — rollback des scripts Phase G scraping HTML + regex pour redémarrer sur architecture propre (Wikidata SPARQL + DB + Wikipedia REST)
2. **Schéma Zod canonique** — contrat explicite entre script Python et enricher NestJS, fail-safe au chargement
3. **Live merge editorial** — `BrandEditorialService.findOne()` dans l'enricher élimine le resync .md↔DB
4. **Auto-trigger enrichSingle** — PUT editorial = 1 appel HTTP = page R7 à jour
5. **Pre-push hook vault** — élimine les aller-retours CI G2/wikilinks (invariant: scripts identiques CI/local)
6. **Force-push discipline** — branches feature uniquement, force-with-lease, jamais sur main

## Ce qui a dérapé (et été corrigé en session)

1. **Dérive R7 → R8** dans S3_SHORTCUTS (commits `7a09ca51` annulé par `60386066`) → règle canon D1 + leçon [[r7-surface-purity-no-cross-surface-urls]]
2. **False prod claim** après merge PR #86 sur main (INC-2026-007) → règle canon deployment D1-D6 + doc monorepo corrigée
3. **Scope pollution** multi-sessions Deploy Bot (commits ADR-019 atterris sur branche r7) → cherry-pick + force-push discipline
4. **QID Wikidata hardcodés faux** (Q42305=Richard Cœur de Lion, pas Alfa Romeo) → résolution dynamique via `wbsearchentities` + 2 overrides

## Règles canon dérivées

| Règle | Origine | Fichier vault |
|-------|---------|---------------|
| D1-D6 Deployment | INC-2026-007 | [[rules-deployment-workflow]] |
| Surface purity (enricher ne construit pas d'URL cross-surface) | Dérive R7→R8 | [[r7-surface-purity-no-cross-surface-urls]] |
| Pre-push local check | Friction CI PRs #14/15/16 | [[pre-push-local-check-pattern]] |

## Dette identifiée, non-traitée

| Item | Priorité | Effort estimé |
|------|----------|---------------|
| Admin UI v1 : formulaire dynamique add/remove row pour FAQ/issues/maintenance (actuellement JSON textareas MVP) | Moyenne | 2-3h |
| Preview live page R7 après save éditorial | Basse | 1-2h |
| Curation réelle des FAQ/issues/maintenance pour 35 marques | Haute (travail éditorial humain) | 1-2 semaines |
| `chore(ci): bump GitHub actions to Node 24` (31 warnings deprecation) | Basse (sept 2026 deadline) | 1h |
| Investiguer régression R2 fiche produit (3116ms vs budget 3000ms) | Moyenne | 1-2h (monitoring) |
| Tests E2E flaky `/pieces/plaquettes-de-frein-1.html` | Moyenne | 2-3h |
| Gate CI surface purity (`r7-brand-validator` regex URL R8) | Basse | 1-2h |
| Runbook admin UI éditorial (mode d'emploi pour human editor) | Basse | 1h |

## Références ancre

- Enricher core : [`r7-brand-enricher.service.ts`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/backend/src/modules/admin/services/r7-brand-enricher.service.ts)
- Schéma Zod : [`brand-rag-frontmatter.schema.ts`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/backend/src/config/brand-rag-frontmatter.schema.ts)
- Script build : [`scripts/rag/build-brand-rag.py`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/scripts/rag/build-brand-rag.py)
- Admin UI : [`admin.brands-seo.tsx`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/frontend/app/routes/admin.brands-seo.tsx)
- Route R7 : [`constructeurs.$brand[.]html.tsx`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/frontend/app/routes/constructeurs.%24brand%5B.%5Dhtml.tsx)

## Liens vault connexes

- Architecture : [[r7-brand-editorial-live-sync]]
- Patterns frontend : [[r7-brand-route-refactoring]]
- Pureté surface : [[r7-surface-purity-no-cross-surface-urls]]
- Runbook script : [[runbook-build-brand-rag]]
- Pattern pre-push : [[pre-push-local-check-pattern]]
- Rules deployment : [[rules-deployment-workflow]]
- Incident : [[2026-04-21-false-prod-claim-on-main-merge]]
