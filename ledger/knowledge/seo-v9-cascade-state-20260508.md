---
title: SEO seo-v9 cascade — état après session 2026-05-08
date: 2026-05-08
status: in-progress
domain: SEO
related_adrs: [ADR-031 wiki canonical, ADR-037 RoleId enum, ADR-039 Zod canon]
related_memories: [seo-chain-architecture-seo-v9.md, seo-r2-indexability-rule.md, seo-legacy-philosophy.md, db-mysql-pg-naming-convention.md]
---

# SEO seo-v9 cascade — état session 2026-05-08

## Contexte

Refonte SEO seo-v9 approuvée 2026-05-08 après 15 itérations utilisateur (plan stratégique : `/home/deploy/.claude/plans/apres-investigation-seo-on-iterative-spark.md`). Verdict empirique : **70-80% du legacy SEO PHP est déjà porté côté monorepo**, 20-30% gaps de finition. Pas une refonte from scratch — un raccordement + complétion ciblée.

## 4 PRs livrées (drafts, en HOLD jusqu'à validation utilisateur de la cascade)

### PR-1 : `feat(seo-v9): PR-1 audit inventaire + matrice gap legacy → monorepo (READ-ONLY)`

- **PR GitHub** : https://github.com/ak125/nestjs-remix-monorepo/pull/398
- **Branche** : `feat/seo-v9-pr1-gap-matrix`
- **Tests** : 16/16 verts (Vitest)
- **Livrable canon** : `docs/seo/legacy_to_monorepo_gap_matrix.md` (10 lignes baseline + findings empiriques)
- **Script** : `backend/scripts/seo/audit-v9-inventaire.ts` (READ-ONLY, 5 volets)
- **Findings clés inscrits dans la matrice** :
  1. **V4 = code mort de production confirmé** : `DynamicSeoV4UltimateService.generateCompleteSeo()` n'est appelé QUE par `dynamic-seo.controller.ts` (4 endpoints admin/debug `/api/seo-dynamic-v4/*`). 0 appel par `rm-builder`, `gamme-rest`, `brand-rpc`, `vehicle-rpc` — les services applicatifs réels.
  2. **Contrat V4 strict (14 variables Zod) handicap debug** : throw 500 générique sans détail Zod si un champ requis manque. Pas une régression prod (V4 jamais appelé), mais bloque tests manuels.
  3. **Sortie V4 ≠ sortie actuelle (divergent)** : sample 2/2 URLs avec inputs complets → `diff_verdict = divergent`. Confirme empiriquement que les 4 systèmes SEO parallèles produisent des sorties différentes.
- **Volume R2 (3 sources Supabase croisées)** : 4 135 954 raw / 502 734 SEO-safe (vue `v_pieces_seo_safe`) / 1 960 sitemap actuel. Justifie empiriquement le `R2IndexabilityGate` : sans gate, R2 pourrait passer de 1 960 → 502 734 URLs (×256), spam Google catastrophique.
- **Décision PR-2 retenue** : scénario A (refactor majeur — V4 jamais branché applicativement, pas de raccord léger possible).

### PR-2a : `feat(seo-v9): PR-2a registries + Zod contracts (foundation, no business logic)`

- **PR GitHub** : https://github.com/ak125/nestjs-remix-monorepo/pull/399
- **Branche** : `feat/seo-v9-pr2a-registries` (depuis main)
- **Commit** : `8d66d310`
- **Tests** : 33/33 verts (14 node:test package + 13 Jest backend + 6 conformance package existants)
- **Livraisons** :
  - `packages/seo-role-contracts/src/surface-keys.ts` — Zod enum 16 surfaces SEO + `SURFACE_TO_ROLE` mapping vers RoleId (ADR-037).
  - `packages/seo-role-contracts/src/noindex-thresholds.ts` — seuils legacy chiffrés par surface (`families<3`, `gammes<5`, canonical strict).
  - `packages/seo-role-contracts/src/r2-indexability-conditions.ts` — 7 conditions cumulatives R2 + `evaluateR2Indexability()`.
  - `backend/src/modules/seo/registries/seo-surface.registry.ts` — Injectable NestJS.
  - `backend/src/modules/seo/registries/seo-variant-family.registry.ts` — 4 familles switch (`__seo_item_switch`, `__seo_type_switch`, `__seo_gamme_car_switch`, `__seo_family_gamme_car_switch`).
  - `backend/src/modules/seo/registries/seo-feature-flag.registry.ts` — centralise `SEO_CHAIN_<flag>_MODE=off|shadow|on` (8 flags).
- **Wiring** : `SeoModule.providers + exports` étendus.
- **Workspace** : `@repo/seo-role-contracts` ajouté à `backend/package.json` + lockfile régénéré.

### PR-2b : `feat(seo-v9): PR-2b policies (canonical/indexability/R2gate/unavailable, stacked sur 2a)`

- **PR GitHub** : https://github.com/ak125/nestjs-remix-monorepo/pull/400
- **Branche** : `feat/seo-v9-pr2b-policies` (stacked depuis `feat/seo-v9-pr2a-registries`)
- **Commit** : `85731ace`
- **Tests** : 27/27 verts (Jest)
- **Livraisons** (4 services dans `backend/src/modules/seo/services/policies/`) :
  - `SeoCanonicalService` — URL canonique stricte par surface (8 surfaces gérées, 6 throw `not-supported` jusqu'à PR-2c+).
  - `R2IndexabilityGate` — wrapper Injectable de `evaluateR2Indexability` (PR-2a contract).
  - `SeoIndexabilityPolicyService` — cascade décisionnelle robots (5 règles, R2 délégué). Injecte `SeoSurfaceRegistry` + `R2IndexabilityGate`.
  - `SeoUnavailablePolicy` — STUB 410/412. Branchement réel = PR-8 (raccord système 3 couches erreurs 4xx existant côté backend).
- **Wiring** : `SeoModule` étendu avec les 4 services.

### PR-2c : `feat(seo-v9): PR-2c chain services + orchestrator (stacked sur 2b)`

- **PR GitHub** : https://github.com/ak125/nestjs-remix-monorepo/pull/401
- **Branche** : `feat/seo-v9-pr2c-renderer-switch` (stacked depuis `feat/seo-v9-pr2b-policies`)
- **Commit** : `d4278b8e`
- **Tests** : 51/51 chain (Jest), 120/120 SEO module total (0 régression)
- **Livraisons** (8 services dans `backend/src/modules/seo/services/chain/`) :
  - `SeoSlugService` — `url_title_optimizer` FR (stop-words FR `de/du/des/la/le/les/et`, élision `l'`/`d'`, accents incl. œ/æ/ñ/ß, smart quotes `’/‘/‚/‛` → ASCII, troncature word-boundary). 14 tests.
  - `SeoArianeBreadcrumbService` — JSON-LD `BreadcrumbList` Schema.org + `buildTextTrail` compat `mta_ariane`. Validation HTTPS absolue. 7 tests.
  - `SeoMetaRegistryService` — lecture cachée `___meta_tags_ariane` (5 rows pages standard) + `__blog_meta_tags_ariane` (5 rows blog). Cache mémoire 1h. 7 tests.
  - `SeoSwitchSelector` — seed canonique sha256 `parseInt(sha256("$surfaceKey:$pgId:$vehicleId:$alias").slice(0,8),16) % length`. Remplace seed legacy `(typeId+pgId)%len` fragile aux renumérotations TecDoc V2. Distribution testée 10k tirages 10 buckets. 6 tests.
  - `SeoTemplateRenderer` — variables métier (#Gamme, #VMarque, #VModele, #VType, #VAnnee, #VNbCh, …) + marketing (#PrixPasCher 16, #VousPropose 12, #MinPrice format title|descrip) + contextuelles (#ArticlesCount, #QualityBadge, #FamilyContext). 9 tests.
  - `SeoInternalLinkingService` (chain) — résolution `#LinkGamme*#`/`#LinkGammeCar*#` via lookup direct `pieces_gamme`. STUB PR-2c, **PR-7 remplacera par MV `seo_internal_link_candidates`** (gain ~5-10× TTFB R1/R7/R8). 9 tests.
  - `SeoContentBlockBuilder` — assemblage `contentBlocks` structurés (lead / paragraph / switch-variant alias 1-3 / link). Pure. 5 tests.
  - `SeoChainOrchestratorService` — composition stateless 7 services + policies PR-2b. Output `SeoChainOutput` exhaustif (template + contentBlocks + policies + ariane + metadata). 5 tests intégration. **chain_version = `seo-v9-pr2c`**.
- **Wiring** : `SeoModule` étendu avec les 8 nouveaux providers + exports (alias `SeoChainInternalLinkingService` pour éviter collision avec `InternalLinkingService` legacy au top level).
- **Décision V4** : `DynamicSeoV4UltimateService.generateCompleteSeo()` reste **intact** (audit PR-1 a confirmé 0 controller applicatif réel le consomme, juste 4 endpoints debug). La chaîne PR-2c est un nouveau code path consommable en PR-3+ via feature flag `SEO_CHAIN_<surface>_MODE`. API publique V4 inchangée → 0 régression.

## Cumul tests cascade : 121/121 verts

- PR-1 : 16 (Vitest scripts/seo/audit)
- PR-2a + PR-2b backend : 40 (Jest registries + policies)
- PR-2a package : 14 nouveaux + 6 conformance existants
- PR-2c : 51 (Jest chain) — 18 nouveaux Jest backend non-chain inclus dans le 120 SEO module total

## Architecture livrée (foundation + chaîne complète)

```
@repo/seo-role-contracts (Zod SoT)
   ├─ surface-keys.ts (16 surfaces R0..R8 + blog + static + 410/412)
   ├─ noindex-thresholds.ts (seuils legacy chiffrés par surface)
   └─ r2-indexability-conditions.ts (7 conditions cumulatives)
              ↓
backend/src/modules/seo/registries/ (PR-2a)
   ├─ SeoSurfaceRegistry      → consommé PR-2b/2c par policies + chain
   ├─ SeoVariantFamilyRegistry → consommé PR-2c par SeoSwitchSelector
   └─ SeoFeatureFlagRegistry  → consommé PR-3+ par controllers (branchement)
              ↓
backend/src/modules/seo/services/policies/ (PR-2b)
   ├─ SeoCanonicalService          → calcul URL canonique
   ├─ R2IndexabilityGate           → wrapper 7 conditions R2
   ├─ SeoIndexabilityPolicyService → cascade robots (DI sur les 2 ci-dessus)
   └─ SeoUnavailablePolicy         → stub 410/412 (branche en PR-8)
              ↓
backend/src/modules/seo/services/chain/ (PR-2c)
   ├─ SeoSlugService                → slugify FR (stop-words, accents, élisions)
   ├─ SeoArianeBreadcrumbService    → JSON-LD BreadcrumbList + text trail
   ├─ SeoMetaRegistryService        → lecture ___meta_tags_ariane (cache 1h)
   ├─ SeoSwitchSelector             → seed canonique sha256
   ├─ SeoTemplateRenderer           → variables métier + marketing + contextuelles
   ├─ SeoInternalLinkingService     → stub #LinkGamme*# (MV en PR-7)
   ├─ SeoContentBlockBuilder        → assemblage contentBlocks
   └─ SeoChainOrchestratorService   → composition stateless des 7 + policies
```

## Ce qui reste (HOLD jusqu'à reprise session)

- **PR-2d** : variables marketing exhaustives (#PrixPasCher / #VousPropose / #MinPrice) si gaps détectés via diff vs legacy + tests intégration shadow vs sortie controllers actuels.
- **PR-3+** : branchement applicatif sur les 4 services réels (`rm-builder`, `gamme-rest`, `brand-rpc`, `vehicle-rpc`) via `SeoChainOrchestratorService.run()` derrière feature flag `SEO_CHAIN_<flag>_MODE=shadow|on`.
- **PR-7** : remplace stub `SeoInternalLinkingService` par MV `seo_internal_link_candidates` (gain perf ~5-10× sur TTFB R1/R7/R8).

## Pour reprise nouvelle session

1. **Charger contexte** : ce fichier + mémoires `seo-chain-architecture-seo-v9.md` + `seo-r2-indexability-rule.md` + `seo-legacy-philosophy.md`.
2. **Lire le plan tactique PR-1** (`docs/superpowers/plans/2026-05-08-seo-v9-pr1-gap-matrix.md`) pour le pattern de cascade.
3. **Vérifier état des PRs** : `gh pr list --search "seo-v9" --state all` (4 drafts dont PR-2c #401 en attente de merge ou de poursuite cascade).
4. **Démarrer PR-2d** : créer branche `feat/seo-v9-pr2d-marketing-vars` stacked sur `feat/seo-v9-pr2c-renderer-switch`.

## Conformité gouvernance

- ✅ Aucun service métier touché (V4 inchangé, controllers inchangés).
- ✅ Pas de Prisma — Supabase SDK direct (CLAUDE.md backend.md respecté).
- ✅ Pattern stacked PR (mémoire `feedback_stacked_pr_pattern_for_atomic_phase`).
- ✅ Convention DB MySQL → PostgreSQL respectée (mémoire `db-mysql-pg-naming-convention.md`).
- ✅ Wiki ADR-031 référencé pour contenu canonique R3 (cascade PR-13 différée).
- ✅ ADR-037 RoleId enum + ADR-039 Zod canon respectés dans tout PR-2a.
