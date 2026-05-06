---
title: "Session 2026-05-06 — R1 drift canon livré (3 PRs séquencées)"
date: 2026-05-06
type: session-trail
related_chantier: D
related_adr: ["ADR-040"]
related_prs:
  - "ak125/nestjs-remix-monorepo#317"
  - "ak125/nestjs-remix-monorepo#318"
  - "ak125/nestjs-remix-monorepo#319"
status: closed
session_closed_at: 2026-05-06
---

# 2026-05-06 — R1 drift canon livré (3 PRs séquencées)

> **Chantier de rattachement** : `D` (SEO indexation / crawl budget). Étend
> l'application opérationnelle d'ADR-040 (canon SEO R0..R8 socle TS-side
> consacré 2026-05-05, voir audit-trail `2026-05-05-seo-canon-r0-r8-stack-shipped.md`)
> au pipeline de classification keyword. Aucune nouvelle décision architecturale —
> implémentation conforme au canon déjà acté.

## Synthèse

Stack de **3 PRs séquencées** éliminant le drift R1 transactionnel dans la
classification keyword. Le drift consistait en : `scripts/seo/build-keyword-clusters.ts`
dupliquait inline (`ROLE_KEYWORD_PATTERNS`, `ROLE_INTENT_AFFINITY`, `inferIntent`)
la logique de classification, avec triggers `acheter` / `prix` / `livraison`
mal-routés vers R1_ROUTER au lieu de R2_PRODUCT. Le canon `@repo/seo-roles@0.2.0`
existait mais le script ne l'utilisait pas — bricolage par duplication.

Approche **no-bricolage** : extension du package canon (`@repo/seo-roles@0.3.0`)
avec point d'entrée unique `classifyKeywordToRole`, refactor du script consommateur,
puis enforcement statique pour empêcher le retour de la duplication.

## 3 PRs séquencées

| PR | Commit | Branche | Scope |
|----|--------|---------|-------|
| #317 PR-1 | `59f7423f` | `feat/seo-roles-keyword-intent-canon` | `@repo/seo-roles@0.3.0` — module `keyword-intent.ts` + 46 golden tests `node:test` + `SearchIntentSchema` Zod. Surface publique : `classifyKeywordToRole`, `KeywordRoleClassification`, `SearchIntentSchema`, `SearchIntent`. `ROLE_KEYWORD_TRIGGERS` PRIVATE non exporté (validation indirecte via classifier). |
| #318 PR-2 | `3757d204` | `refactor/kw-clusters-consume-seo-roles` | `scripts/seo/build-keyword-clusters.ts` consomme le canon. -90 lignes duplication. Ajouts : `CANONICAL_TO_CLUSTER_BUCKET` (canon RoleId → script PageRole), `splitR6Bucket()` (transitionnel R3_guide vs R6), `intentFromRole()` (mapping 4-value SearchIntent legacy DB), `traceClassification()` (stderr opt-in `KW_CLASSIFY_TRACE=1`), champ `excludedTransactionalKeywords[]`. |
| #319 PR-3 | `91aaa7cd` | `chore/r1-canon-enforcement-and-docs` | ast-grep rule `seo-no-inline-role-keyword-pattern.yml` (cible exacte `ROLE_KEYWORD_PATTERNS` / `ROLE_INTENT_AFFINITY`, zéro faux positif générique) + 4 docs corrigés (`R4-reference.md`, `domain-map.md`, `r1-content-batch.md`, `rpcs-critical.md`). |

## Drift élimination par construction

`classifyKeywordToRole` évalue **R2_PRODUCT en priorité 1** dans `orderedRoles`.
Conséquence : `acheter filtre huile voiture` retourne `R2_PRODUCT` même si la
regex R1 capture `voiture`. Pas de regex défensive — l'**ordre de match EST**
la garantie. Approche structurelle, non patch-and-pray.

## Smoke tests dry-run validés (PR-2)

| Gamme | R1.primary | R1.secondary | R1 drift transactionnel | excludedTransactionalKeywords |
|-------|------------|--------------|------------------------|------------------------------|
| `filtre-a-huile` | `filtre a huile` (vol=5000) | 5 | **0** | 32 |
| `plaquette-de-frein` | `disque et plaquette de frein clio 4` | 5 | **0** | 38 |
| `filtre-a-air` | `filtre à air` | 5 | **0** | 5 |

R1 ne tombe à zéro sur aucune des 3 gammes (pas de régression SEO). Tous les
triggers transactionnels (acheter / prix / commander / livraison) redirigés
vers `excludedTransactionalKeywords[]` pour observabilité aval R2_PRODUCT.

## 4 couches enforcement actives

L'élimination du drift est désormais protégée par **4 couches indépendantes**,
toutes triggered automatiquement (pre-commit + CI) :

| # | Couche | Mécanisme | PR origine |
|---|--------|-----------|-----------|
| 1 | **TS branded type** | `CanonicalRoleId` (compile-time guarantee) | PR-0B v0.2.0 (#307) |
| 2 | **Zod runtime** | `SearchIntentSchema`, `assertCanonicalRoleStrict` | PR-1 (#317) |
| 3 | **Golden tests** | 46 cas `node:test` anti-régression dans `keyword-intent.test.ts` | PR-1 (#317) |
| 4 | **ast-grep static** | `seo-no-inline-role-keyword-pattern.yml` (pre-commit + CI lint) | PR-3 (#319) |

## Décisions canon explicites tracées

- **R3_guide vs R6** : split local `splitR6Bucket()` dans le script pour
  préserver la shape JSON 2-buckets historiques. Fusion R3_guide → R6 différée
  à un ticket dédié (pattern deprecate → migrate → drop).
- **R2_PRODUCT** : pas de bucket script historique — collecté dans
  `excludedTransactionalKeywords[]` (additif au niveau racine du JSON output,
  pas de breaking change `SeoCluster` shape).
- **Liste de marques R6** : 50+ marques OEM/aftermarket
  (`purflux|mann-filter|bosch|mahle|...`) vivent dans le regex canon
  `keyword-intent.ts` (réplication conservatrice de l'inline historique
  ligne 171 du script, snapshot 2026-05-05). À externaliser vers DB
  (`__seo_r6_brand_dictionary`) en PR future.
- **`type PageRole`** legacy : conservé dans `build-keyword-clusters.ts` pour
  compat shape JSON output. ast-grep ne le bloque PAS encore — restriction à
  ajouter quand la shape migrera vers `Record<CanonicalRoleId, _>`.

## Différé (chantiers dédiés futurs)

1. **PR-4 deprecate→migrate→drop** :
   `PurchaseGuideDataService.getR1Slots()` →
   `R1RouterDataService.getR1Slots()`. Anti-pattern : classe achat (R6)
   exposant méthode router (R1). Suivre `feedback_deprecate_before_rename_before_drop.md`.
2. **Externalisation DB R6 brand list** : sortir les 50+ marques du regex
   canon vers une table `__seo_r6_brand_dictionary`.
3. **Migration shape JSON `type PageRole` → `Record<CanonicalRoleId, _>`** :
   déclenchera l'ajout du pattern bloquant ast-grep correspondant.

## Cohérence avec le canon vault

Cette livraison **étend opérationnellement** ADR-040 (canon SEO R0..R8
TS-side consacré 2026-05-05) sans introduire de nouvelle décision
architecturale. Le keyword classifier est conforme au mapping canon
`@repo/seo-roles` : aucune divergence à arbitrer.

Mémoire monorepo `r1-drift-canon-shipped-20260506.md` (référence locale au
DEV) capture les détails techniques. Cette entrée vault est la trace
canonique audit-trail (SoT).

## Références

- Plan d'exécution : `plans/verifier-r1-est-officiellement-eager-fog.md` (DEV local, hors vault)
- ADR ratifiée : `decisions/adr/ADR-040-*.md` (canon SEO R0..R8)
- Audit-trail précédent : `audit-trail/2026-05-05-seo-canon-r0-r8-stack-shipped.md` (foundation `@repo/seo-roles`)
- Mémoire technique DEV : `r1-drift-canon-shipped-20260506.md` (mémoire Claude DEV)
- Session log monorepo : `log.md` entrée `2026-05-06`

## Statut session

**CLOSED** — 3 PRs mergées sur main, worktrees nettoyés, branches locales
supprimées, mémoire + session-log + audit-trail vault tracés. Aucune action
en cours. Différé documenté pour chantiers futurs.
