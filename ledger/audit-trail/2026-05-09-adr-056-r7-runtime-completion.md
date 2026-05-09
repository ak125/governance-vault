---
date: 2026-05-09
type: audit-trail
related: [ADR-056, ADR-055, ADR-047, ADR-046, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-09 — ADR-056 R7 Brand Runtime Completion

## What

Ouverture ADR-056 dans [[MOC-Decisions]] pour formaliser la finalisation runtime
de R7_BRAND : l'`ExecutionRouterService` du monorepo dispatche désormais
`{roleId: 'R7_BRAND', targetIds, dryRun}` vers `R7BrandEnricherService`, exactement
comme R8.

Auto-application de la convention ADR-054 : tout ADR vault destiné au merge
génère par défaut une entrée audit-trail (méta-application, cf. ADR-054 D2).

## Why

R7_BRAND était canonisé partout (RoleId, registry, service, agents Claude, sitemap,
route publique, validators, 7 tables DB) **sauf** runtime : le router émettait un
`not_implemented` skip pour R7. Conséquence empirique :

- `/api/admin/pipeline/execute` ne dispatchait pas vers R7
- L'enricher n'était joignable que via `/api/admin/r7-brand/enrich/:marque_id`
  (controller dédié, sans log `__pipeline_chain_queue`, sans uniformité retry/timeout)
- L'agent Claude `r7-brand-execution` documenté pour batch mais pas branché côté pipeline
- Sans ADR vault, le code de finalisation shippé n'aurait pas été LIVE au sens canon
  (cf. mémoire DEV `feedback_canon_rule_live_iff_adr_accepted.md`)

## How

### Code (PR monorepo #418)

3 commits rebasés sur main, auto-merge SQUASH armé :

- `feat(seo-v9): wire R7_BRAND in ExecutionRouter` — retire le hardblock lignes 135-155,
  ajoute `R7BrandEnricherService` au `serviceClassMap`, ajoute case inline dans
  `dispatchSingle`, helpers `resolveMarqueId(targetId)` (regex `/^\d+$/` + `Number.parseInt`
  + check `auto_marque`) et `dryRunR7Preview` (SELECT lecture seule).
- `test(seo-v9): cover R7 dispatch + R8 smoke regression in router spec` — premier spec
  `ExecutionRouterService` (jamais existé), 14/14 PASS via `service.execute()` couvrant
  tout le flow (`normalizeRoleId` + `EXECUTION_REGISTRY` + `resolveEnricher` +
  `executeWithRetryBackoff` + `executeWithTimeout` + `inferStatus` + `logExecution`).
- `docs(seo-batch): unblock R7 step in seo-gamme-audit skill` — corrige doc obsolète
  "R7 non implémenté" → requête SQL réelle sur `__seo_r7_pages`.

### ADR (cette PR vault)

- [[ADR-056-r7-brand-runtime-completion]] — 7 invariants (I1-I7), 7 décisions (D1-D7),
  cohabitation explicite avec [[ADR-055-seo-shadow-mode-architecture]] (R7_BRAND_HUB
  shadow mode `off` ↔ R7 batch via ExecutionRouter sont deux chemins indépendants).
- Entrée [[MOC-Decisions]] ajoutée juste après ADR-055.

## Dettes hors scope (5 items, follow-up monorepo)

1. Refacto `parseNumericTargetId` partagé R7+R8 + skip `resolvePgAlias` pour rôles
   à `targetId` numérique (-2 SELECTs `pieces_gamme` inutiles par exécution).
2. `__pipeline_chain_queue.pcq_pg_id` nommage générique (stocke `pgId` ou `typeId` ou
   `marque_id`).
3. `executeWithConcurrency` ordre `results[]` non préservé (bug pré-existant).
4. Mapping `R7EnrichResult.reasons[]` → `data.reason` pour `extractDetailedError`
   (fallback générique accepté).
5. Vrai dryRun dans l'enricher (compose+score sans UPSERT) — preview routeur suffit
   à J0.

Tracées dans la description PR #418 + corps ADR-056 § "Dette résiduelle hors scope".

## Patterns réutilisables (mémoires DEV ajoutées)

- `feedback_strict_numeric_targetid_parsing.md` : regex `/^\d+$/` AVANT `Number.parseInt`
  (prévient injection `parseInt("30abc",10)===30`).
- `feedback_dispatcher_tests_drive_public_method.md` : tests router via méthode publique
  `execute()`, jamais helpers privés (couvre flow complet).
- `feedback_test_assert_from_registry_not_magic_value.md` : asserter
  `EXECUTION_REGISTRY[X].defaultWriteMode`, pas `'draft_write'` hardcodé.
- `spec-pattern-per-table-supabase-mock.md` : pattern per-table chain mock pour
  `SupabaseBaseService` (permet asserter qu'une table N'EST PAS interrogée).
- `r7-router-wired-pr418-20260509.md` : état projet R7 + dette résiduelle.

## Self-review verdict: APPROVE

8 items checklist (cf. mémoire `feedback_vault_self_review_before_admin_merge.md`) :

1. Numéro ADR libre (ADR-056) — vérifié, ADR-051/052/054 pris par PRs vault ouvertes.
2. Frontmatter conforme template — `id`, `title`, `status: accepted`, `date`, `deciders`,
   `related`.
3. Lien depuis MOC (G2 anti-orphelin) — entrée ajoutée dans [[MOC-Decisions]] juste après
   ADR-055.
4. Audit-trail co-créé (ADR-054 default) — ce fichier.
5. Pas de modification de canon `status: canon` sans ADR — uniquement ajouts (ADR + MOC + audit-trail).
6. Pas d'écriture depuis CI (G4) — toutes les écritures vault depuis VPS DEV
   (`46.224.118.55`).
7. Cohabitation ADR-055 R7_BRAND_HUB shadow ↔ ADR-056 R7 batch documentée explicitement
   (D7).
8. Code monorepo référencé empiriquement (PR #418, lignes citées, tests 14/14 PASS).
