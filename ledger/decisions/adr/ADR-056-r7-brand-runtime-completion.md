---
id: ADR-056
title: R7 Brand Runtime Completion (ExecutionRouter dispatch canonique)
status: accepted
date: 2026-05-09
deciders: [Fafa]
decision_makers: [Fafa]
related: [ADR-031, ADR-037, ADR-046, ADR-047, ADR-055, R-SEO-09]
---

# ADR-056: R7 Brand Runtime Completion

## Context

R7_BRAND (hub marque/constructeur/équipementier) était canonisé partout sauf **runtime** :

- Type `RoleId.R7_BRAND` dans `@repo/seo-roles` (canonical.ts)
- Surface key `R7_BRAND_HUB` dans `@repo/seo-role-contracts`
- Entrée complète dans `EXECUTION_REGISTRY` (`enricherServiceKey: 'R7BrandEnricherService'`,
  `defaultWriteMode: 'draft_write'`, `stopPolicy: { maxRetries: 2, timeoutMs: 180_000 }`)
- Service `R7BrandEnricherService` (NestJS) avec `enrichSingle(marqueId)` UPSERTant 5 tables
  R7 + lecture seule `__seo_brand_editorial`
- 3 agents Claude (`r7-brand-validator`, `r7-brand-execution`, `r7-brand-rag-generator`)
- 7 tables DB (`__seo_r7_pages`, `__seo_r7_page_versions`, `__seo_r7_fingerprints`,
  `__seo_r7_regeneration_queue`, `__seo_r7_qa_reviews`, `__seo_r7_keyword_plan`,
  `__seo_brand_editorial`)
- Sitemap `sitemap-brands.xml`
- Route publique `/constructeurs/{brand}.html`
- Validator backend `validateR7Brand()` + agent Claude validator
- Enrichment admin via `AdminR7BrandController` (`POST /api/admin/r7-brand/enrich/:marque_id`)
- SeoShadowObservatory R7 câblé (cf. ADR-055 surface `R7_BRAND_HUB`, mode `off` à J0)

**Mais** `ExecutionRouterService.execute({roleId: 'R7_BRAND'})` retournait explicit
`not_implemented` — court-circuit hardcodé avant même la résolution registry. R7 n'était
pas joignable via le seul endpoint canonique pipeline (`/api/admin/pipeline/execute`),
donc :

- Aucune trace `__pipeline_chain_queue` pour les enrichissements R7
- Aucun `executeWithRetryBackoff` / `executeWithTimeout` uniforme
- Aucune cohérence observabilité avec R1-R8 (logs structurés, listRoles cohérent)
- L'agent `r7-brand-execution` documenté pour batch, mais pas branché côté pipeline

PR monorepo [#418](https://github.com/ak125/nestjs-remix-monorepo/pull/418) (3 commits)
finalise le runtime. Sans ADR vault, le code shippé n'est **pas LIVE** au sens canon
(cf. mémoire `feedback_canon_rule_live_iff_adr_accepted.md`).

## Decision

### D1. ExecutionRouter = entrée canon pour batch R7

`ExecutionRouterService.execute({roleId: 'R7_BRAND', targetIds, dryRun})` est l'**entrée
canon pour tout enrichissement batch R7** (CLI `/content-gen --r7`, jobs cron, agents
Claude `r7-brand-execution`). `AdminR7BrandController` reste valide pour les appels admin
directs (UI single-marque, debug), mais **partage** le même `R7BrandEnricherService` —
aucun chemin d'écriture parallèle.

### D2. targetId R7 = `marque_id` numérique strict

R7 utilise un `targetId` numérique (analogue à R8 / `typeId`), pas un `pgId` (gamme).
Le router applique une **validation stricte** :

```ts
if (!/^\d+$/.test(targetId)) return failed;        // rejette "abc", "30abc", " 30", "+30", "0x1E", ""
const marqueId = Number.parseInt(targetId, 10);
if (Number.isNaN(marqueId) || marqueId <= 0) return failed;  // rejette "-1", "0"
const exists = await client.from('auto_marque').eq('marque_id', marqueId).single();
if (!exists) return failed;                        // rejette marque_id inconnue
```

Aucun alias R7 (pas de `marque_alias` accepté en `targetId`). La regex stricte amont
prévient l'injection silencieuse `parseInt("30abc", 10) === 30`.

### D3. dryRun = preview lecture-seule par le router

Le mode `dryRun: true` est implémenté **côté router** : SELECT lecture seule sur
`__seo_r7_pages` + `auto_marque`, retour `{status: 'ready', exists, currentDecision,
currentScore, lastUpdate, action: 'would create' | 'would regenerate'}`. **L'enricher
n'est pas appelé.**

La signature publique `R7BrandEnricherService.enrichSingle(marqueId: number)` reste
**inchangée** (pas de `{dryRun}` ajouté) — backward-compat avec
`AdminR7BrandController.enrichBatch` et toute orchestration future.

### D4. Validation R7 = interne enricher, jamais dupliquée routeur

Le `R7BrandEnricherService` appelle `roleValidator.validateR7Brand(contentMain)` en
interne (defense in depth surface purity). Le router n'invoque **pas** le validator —
cohésion service intacte. L'agent Claude `r7-brand-validator` reste l'audit profond
indépendant (réflexion, anti-dérive), à invoquer manuellement post-batch.

### D5. `__seo_brand_editorial` = lecture seule depuis l'enricher

`__seo_brand_editorial` (FAQ, common_issues, maintenance_tips) est curé manuellement
via UI admin (chemin `BrandEditorialService`). L'enricher R7 le **lit** dans
`composeBlocks()` mais ne le réécrit jamais. Aucun chemin d'écriture R7 batch ne touche
cette table — séparation humain/auto stricte (cf. mémoire
`feedback_no_bricolage_human_vs_auto_content`).

### D6. `pcq_pg_id` réutilisé pour `marque_id` (dette nommage tracée)

`__pipeline_chain_queue.pcq_pg_id` est une colonne integer générique (R8 stocke déjà
un `typeId` dedans). R7 stocke un `marque_id`. **Refacto nommage hors scope** —
impacterait toutes les surfaces non-gamme (R7, R8, futur R0). Tracé comme dette pour
follow-up monorepo.

### D7. SeoShadowObservatory R7 reste actif (cohabitation ADR-055)

ADR-055 D6 cite `R7_BRAND_HUB` câblé en mode `off` à J0 dans `SeoShadowObservatory`. Cette
ADR-056 ne touche pas l'observatoire — R7 enrichment via ExecutionRouter et observation
shadow legacy↔chain via `BrandRpcService` sont **deux chemins indépendants**, l'un
batch (write 5 tables R7), l'autre runtime (read RPC, écrit `__seo_event_log`).

## Invariants

- **I1** — `ExecutionRouterService.execute` reste l'**unique** entrée pipeline pour R7 batch.
  Toute orchestration (`/content-gen --r7`, agents Claude, jobs futurs) DOIT passer par
  cet endpoint, jamais en appelant `R7BrandEnricherService` directement.
- **I2** — `targetId` R7 = `string`-numeric strict (regex `/^\d+$/` + `> 0` + existence
  `auto_marque`). Aucun alias accepté.
- **I3** — `R7BrandEnricherService.enrichSingle(marqueId)` signature publique **immuable**
  sans ADR amendement (consommée par `AdminR7BrandController` + ExecutionRouter).
- **I4** — `__seo_brand_editorial` = lecture seule dans le pipeline R7. Curation humaine
  exclusivement via UI admin (`BrandEditorialService`).
- **I5** — `EXECUTION_REGISTRY[RoleId.R7_BRAND]` = SoT pour modes / timeouts / retry R7.
  Tests doivent asserter `result.mode === EXECUTION_REGISTRY[RoleId.R7_BRAND].defaultWriteMode`,
  jamais `'draft_write'` hardcodé.
- **I6** — Validation `validateR7Brand` reste **interne** au `R7BrandEnricherService`.
  Le router ne duplique pas la validation surface purity.
- **I7** — Le mode `dryRun: true` ne doit JAMAIS muter `__seo_r7_*` ni `__seo_brand_editorial`.
  Test `R7 dryRun → no UPSERT` couvre cette propriété (PR #418 spec, cas 2 et 3).

## Surfaces actuellement câblées

| Surface | Service caller | Mode default | Status (post PR #418) |
|---|---|---|---|
| R7_BRAND batch | `ExecutionRouterService.execute` | n/a (sync write) | LIVE |
| R7_BRAND admin single | `AdminR7BrandController.enrich` | n/a (sync write) | LIVE (pré-existant, BC préservée) |
| R7_BRAND_HUB observatoire | `BrandRpcService.getBrandPageDataOptimized` | `off` | LIVE shadow (cf. ADR-055) |

## Dette résiduelle hors scope

| Item | Raison hors scope |
|---|---|
| `parseNumericTargetId` partagé R7+R8 + skip `resolvePgAlias` pour rôles à `targetId` numérique | Refacto cross-rôles, asymétrie si fait pour R7 seul. Issue follow-up monorepo |
| `__pipeline_chain_queue.pcq_pg_id` nommage générique (stocke `pgId` ou `typeId` ou `marque_id`) | Impacte toutes les surfaces non-gamme. Refacto nommage cross-table, scope creep |
| `executeWithConcurrency` ordre `results[]` non préservé (bug pré-existant) | Non spécifique R7. Pour batch R7 multi-marques, garder le path controller dédié |
| Mapping `R7EnrichResult.reasons[]` → `data.reason` pour `extractDetailedError` | Fallback générique accepté, aligné R1/R2/R8 |
| Vrai dryRun dans l'enricher (compose+score sans UPSERT) | Preview routeur suffit ; à reconsidérer si signal empirique le demande |

## Conséquences

- **Code R7 atterri sur main 2026-05-09** (PR #418) = officiellement LIVE
  (ADR.status=accepted).
- **`/api/admin/pipeline/execute` accepte désormais `{roleId: 'R7_BRAND'}`** avec parité
  observabilité R1-R8 (`__pipeline_chain_queue` log, retry, timeout, listRoles cohérent
  `available:true`).
- **3 dettes hors scope** documentées ci-dessus → issues monorepo follow-up.
- **R7 dans `seo-gamme-audit` skill** désormais utilisable (doc obsolète "R7 non implémenté"
  remplacée par requête SQL réelle, commit C de la PR).

## Critères de succès empiriques

- [ ] `gh pr list --state merged --search "#418"` retourne PR mergée.
- [ ] `curl -X POST .../api/admin/pipeline/execute -d '{"roleId":"R7_BRAND","targetIds":["30"],"dryRun":true}'`
      → `results[0].status === 'success'` + `data.status === 'ready'` + 0 row écrite.
- [ ] `curl .../api/admin/pipeline/roles | jq '.[] | select(.roleId=="R7_BRAND")'` →
      `available: true`, `enricherServiceKey: "R7BrandEnricherService"`, `timeoutMs: 180000`.
- [ ] Smoke réel `dryRun: false` pour `marque_id=30` (Audi) → row insérée
      `__seo_r7_pages` + `__seo_r7_page_versions` + `__seo_r7_fingerprints`.
- [ ] Régression R8 `targetIds:['12345'], dryRun:true` → identique pré-PR.

## Références

- PR monorepo : [ak125/nestjs-remix-monorepo#418](https://github.com/ak125/nestjs-remix-monorepo/pull/418)
- Plan d'implémentation : `~/.claude/plans/utiliser-meileure-approche-meilleure-quiet-quasar.md`
- Mémoire projet : `r7-router-wired-pr418-20260509.md`
- ADR-031 : Canonical 4-layer framework
- ADR-037 : RoleId enum canon
- ADR-046 : R-stack single generator and layers
- ADR-047 : SeoChainOrchestratorService canon
- ADR-055 : SEO Shadow Mode Architecture (cohabitation R7_BRAND_HUB shadow ↔ R7 batch)
- R-SEO-09 : URL Immutability rule (`/constructeurs/{brand}.html` immuable sans signoff)
