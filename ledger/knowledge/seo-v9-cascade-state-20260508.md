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

## 3 PRs livrées (drafts, en HOLD jusqu'à validation utilisateur de la cascade)

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

## Cumul tests cascade : 70/70 verts

- PR-1 : 16 (Vitest scripts/seo/audit)
- PR-2a + PR-2b backend : 40 (Jest registries + policies)
- PR-2a package : 14 nouveaux + 6 conformance existants

## Architecture livrée (foundation prête)

```
@repo/seo-role-contracts (Zod SoT)
   ├─ surface-keys.ts (16 surfaces R0..R8 + blog + static + 410/412)
   ├─ noindex-thresholds.ts (seuils legacy chiffrés par surface)
   └─ r2-indexability-conditions.ts (7 conditions cumulatives)
              ↓
backend/src/modules/seo/registries/ (PR-2a)
   ├─ SeoSurfaceRegistry      → consommé PR-2b par SeoIndexabilityPolicyService
   ├─ SeoVariantFamilyRegistry → consommé PR-2c par SeoSwitchSelector
   └─ SeoFeatureFlagRegistry  → consommé PR-3+ par controllers (branchement)
              ↓
backend/src/modules/seo/services/policies/ (PR-2b)
   ├─ SeoCanonicalService          → calcul URL canonique
   ├─ R2IndexabilityGate           → wrapper 7 conditions R2
   ├─ SeoIndexabilityPolicyService → cascade robots (DI sur les 2 ci-dessus)
   └─ SeoUnavailablePolicy         → stub 410/412 (branche en PR-8)
```

## Ce qui reste (HOLD jusqu'à reprise session)

- **PR-2c** : refactor `DynamicSeoV4UltimateService` en chaîne 7 services + extraction `SeoSwitchesService` existant (effort ~1 sprint plan v9). Le PR le plus complexe de la cascade.
- **PR-2d** : tests integration chaîne complète + variables marketing manquantes (`#PrixPasCher#`/`#VousPropose#`/`#MinPrice#`).
- **PR-3+** : branchement applicatif sur les 4 services réels (`rm-builder`, `gamme-rest`, `brand-rpc`, `vehicle-rpc`) avec feature flag `SEO_CHAIN_<flag>_MODE=shadow|on`.

## Pour reprise nouvelle session

1. **Charger contexte** : ce fichier + mémoires `seo-chain-architecture-seo-v9.md` + `seo-r2-indexability-rule.md` + `seo-legacy-philosophy.md`.
2. **Lire le plan tactique PR-1** (`docs/superpowers/plans/2026-05-08-seo-v9-pr1-gap-matrix.md`) pour le pattern de cascade.
3. **Vérifier état des PRs** : `gh pr list --search "seo-v9" --state all` (3 drafts en attente de merge ou de poursuite cascade).
4. **Démarrer PR-2c** : créer branche `feat/seo-v9-pr2c-renderer-switch` stacked sur `feat/seo-v9-pr2b-policies`.

## Conformité gouvernance

- ✅ Aucun service métier touché (V4 inchangé, controllers inchangés).
- ✅ Pas de Prisma — Supabase SDK direct (CLAUDE.md backend.md respecté).
- ✅ Pattern stacked PR (mémoire `feedback_stacked_pr_pattern_for_atomic_phase`).
- ✅ Convention DB MySQL → PostgreSQL respectée (mémoire `db-mysql-pg-naming-convention.md`).
- ✅ Wiki ADR-031 référencé pour contenu canonique R3 (cascade PR-13 différée).
- ✅ ADR-037 RoleId enum + ADR-039 Zod canon respectés dans tout PR-2a.
