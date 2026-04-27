---
id: INC-2026-010
type: incident
title: "503 R8 vehicle pages — build_vehicle_page_payload sous-requete catalog mal optimisee"
date: 2026-04-25
date_detected: 2026-04-25T10:20:00Z
date_resolved: 2026-04-25T13:56:00Z
date_steady_state: 2026-04-25T~16:00:00Z  # backfill 28 252 stale termine, watcher auto-unschedule
severity: medium
status: resolved-pending-merge  # fix vivant en DB, PRs monorepo #167 + vault #65 en attente de merge user
impact_duration: "intermittent depuis 2026-04-23 (2j env. en mode degrade probabiliste, 1 utilisateur impacte observe)"
affected_systems:
  - route-frontend: /constructeurs/{brand}/{model}/{type}.html (R8)
  - rpc: build_vehicle_page_payload (cree par Phase 1 ADR-016)
  - table: __vehicle_page_cache (28 252/28 505 marquees stale)
  - cron: refresh_stale_vehicle_cache (jamais schedulee)
  - backend: vehicle-rpc.service.ts (RPC_TIMEOUT_MS=2000ms vs ~2s rebuild)
  - frontend: constructeurs.$brand.$model.$type.tsx (loader 503 paths non instrumentes dans __error_logs)
related_rules:
  - performance-budget-ttfb
  - seo-http-status-contract
  - rpc-governance
related_adrs:
  - ADR-016-vehicle-page-matview-persistence
  - ADR-021-database-rls-hardening-zero-trust
related_incidents:
  - INC-2026-005-gsc-5xx-vehicle-page-cold-rpc
  - INC-2026-006-503-vehicle-pages-rpc-allowlist-stale-image
root_cause: "Phase 1 ADR-016 (commit fc9b94af, 21/04) a cree build_vehicle_page_payload avec une sous-requete catalog qui force le planner sur le PK 12 GB pieces_relation_type_v2_pkey au lieu de l'index covering existant idx_pieces_relation_type_type_id_composite (4 GB). Cause : la jointure forcee sur pieces.piece_id (filtre piece_display=true) force le planner a choisir le PK qui contient les deux colonnes -> scan de 18 384 rows pour produire 116 resultats -> ~692 ms par sous-requete catalog, ~2 s cumule pour les 8 sections. Phase 2 du meme commit a baisse RPC_TIMEOUT_MS de 9000 a 2000 ms sans verifier que la fonction tient le budget. Le 23/04, un script de dedup gamme a marque 28 252 / 28 505 rows stale via UPDATE direct, sans declencher rebuild ni utiliser de wrapper canon. Aucun cron schedule pour refresh_stale_vehicle_cache (Phase 3 ADR-016 jamais implementee). Resultat : chaque hit utilisateur sur un type stale + Redis L1 1h expiree force le rebuild on-miss synchrone qui depasse 2 s -> 503 visible chez l'utilisateur."
owner: "@automecanik.seo"
reviewed_by: "Claude Opus 4.7"
tags:
  - incident/medium
  - domain/seo
  - domain/catalog
  - tech/postgres
  - tech/supabase
  - post-mortem
  - resolved
  - root-cause-fix
  - followup-adr-016
---

# INC-2026-010 : 503 R8 vehicle pages — build_vehicle_page_payload sous-requete catalog mal optimisee

> [!warning] Résumé
> Le 25/04 vers 10:20 UTC, un utilisateur signale un HTTP 503 sur
> `https://www.automecanik.com/constructeurs/renault-140/clio-iii-140004/1-5-dci-34746.html`.
> L'analyse initiale (« blip transitoire ») etait fausse. Le user a corrige 3x avec raison :
> « il y a quelque chose qui a ete touche », « je veux une solution robuste pas de bricolage ».
> RCA empirique : la fonction `build_vehicle_page_payload` (creee Phase 1 ADR-016 le 21/04)
> prend ~2 s en cold a cause d'une sous-requete `catalog` qui n'utilise pas le bon index.
> Combine au timeout 2000 ms et au cache stale 99 % depuis le 23/04 (script dedup sans rebuild),
> chaque hit cold = 503 probabiliste. Fix root-cause deploye : reecriture de la sous-requete
> en deux phases (CTE) + cron one-shot backfill + trigger auto_type + wrapper canon
> mark_stale_with_followup_rebuild + endpoints admin + instrumentation loader Remix
> + smoke prod scheduled. PR monorepo #167.

## Timeline

| Heure UTC | Évènement |
|-----------|-----------|
| 2026-04-21 09:02 | Backfill initial des 28 505 rows `__vehicle_page_cache` (Phase 1 ADR-016) termine |
| 2026-04-21 12:50 | Deploy Phase 2 ADR-016 (`fc9b94af`) — supprime defenses eff30b7f, baisse RPC_TIMEOUT_MS 9000 -> 2000 ms |
| 2026-04-21 13:15-13:57 | INC-2026-006 (allowlist RPC + image preprod obsolete), 67 min de 503 systemique, hotfix |
| 2026-04-23 (heure inconnue) | Script `catalog_gamme_dedup_20260423` execute -> UPDATE direct sur 28 252 rows -> stale=true sans rebuild |
| 2026-04-24 ~14:00-15:00 | Pic de 252 rebuilds declenches par hits user/bots (visible dans `__vehicle_page_cache.built_at`) |
| 2026-04-25 ~10:20 | Hit utilisateur sur type 34746 -> rebuild on-miss -> timeout 2 s -> 503 affiche |
| 2026-04-25 ~10:30 | User signale le 503. Analyse initiale (« blip transitoire ») rejete par user 3x. |
| 2026-04-25 ~12:00-12:30 | RCA empirique : EXPLAIN ANALYZE de `build_vehicle_page_payload`, identification index `idx_..._composite` non utilise |
| 2026-04-25 ~13:00 | Fix root-cause applique en DB (4 migrations) + 2 cron jobs lances pour backfill |
| 2026-04-25 ~13:30 | Trigger auto_type + wrapper canon mark_stale_with_followup_rebuild deployes |
| 2026-04-25 ~13:50 | Endpoints admin vehicle-cache + instrumentation loader 503 + smoke /constructeurs/* + check CI guard |
| 2026-04-25 13:56 | PR monorepo #167 ouverte (3 commits, 7 fichiers nouveaux + 4 modifs) |
| 2026-04-25 14:19 | Commit `84aa9655` cherry-pick : fix smoke URLs (audi-r8 inactif + peugeot-308 redirect 301 remplaces par chevrolet/fiat/vw fresh canonical) |
| 2026-04-25 14:25 | PR vault #65 ouverte (post-mortem INC-2026-010) |
| 2026-04-25 ~16:00 | **Steady state atteint** : backfill 28 252 rows termine, watcher auto-unschedule les 2 cron jobs |
| 2026-04-27 14:03 | **Validation J+2** : stale=0, fresh=28 505, cron_jobs_active=0, page 34746 = HTTP 200 sub-200ms, stress 100 hits = 100/100 = 200 zero 503 |

## Impact

- **URLs affectees** : 100 % des pages `/constructeurs/*/type.html` susceptibles de tomber en 503 cold
- **Probabilite par hit** : (Redis L1 expire) AND (row stale, 99 % du cache) AND (rebuild > 2 s) — combinaison rare en pratique
- **Utilisateurs finaux** : 1 utilisateur impacte observe (le reporter), mais probable que d'autres l'ont vu sans signaler
- **SEO Googlebot** : 67 min de 5xx structurels (INC-2026-006) puis vulnerabilite probabiliste depuis 23/04. A surveiller GSC sur 7-14 j.
- **Trafic e-commerce** : `/pieces/*` et cart pas impactes (autres fonctions)

## Root Cause

> [!bug] Cause racine — fonction nouvellement creee mal optimisee, palliatif retire avant verification, cron de rattrapage jamais schedule
> Trois enchainements en cascade :
>
> 1. **Phase 1 ADR-016 a copie-colle la logique de l'ancienne `get_vehicle_page_data_optimized` sans optimiser** — la nouvelle fonction `build_vehicle_page_payload(p_type_id)` herite d'une sous-requete `catalog` qui force la jointure sur `pieces.piece_id` (pour filtrer `piece_display=true`), ce qui pousse le planner Postgres a choisir le PK `pieces_relation_type_v2_pkey` (12 GB) au lieu de l'index covering deja existant `idx_pieces_relation_type_type_id_composite` (4 GB). Resultat mesure (EXPLAIN ANALYZE 25/04 sur type 18110) : 18 384 row scans pour produire 116 resultats, ~692 ms par sous-requete `catalog`, ~2 s cumule pour les 8 sections de la fonction.
>
> 2. **Phase 2 ADR-016 a baisse `RPC_TIMEOUT_MS` 9000 -> 2000 ms sans verifier que la fonction tient le budget** — supprime aussi le fallback stale Redis 24h, le `RPC_COLD_TIMEOUT_MS = 9000` et le Caddy `lb_try_duration` ajoutes par eff30b7f. Le commentaire ligne 26 du service admet « rebuild on-miss = ~4s » mais le timeout est 2000 ms — contradiction explicite, garantie d'echec.
>
> 3. **Le 23/04, un script `catalog_gamme_dedup_20260423` a fait un UPDATE direct** `UPDATE __vehicle_page_cache SET stale=true WHERE …` sur 28 252 rows sans declencher rebuild. Aucun cron `refresh_stale_vehicle_cache` n'etait schedule (Phase 3 ADR-016 jamais implementee). Resultat : 99 % du cache reste stale, chaque hit user force un rebuild on-miss synchrone, et avec `RPC_TIMEOUT_MS=2000` + rebuild ~2 s, 503 probabiliste apparait quand Redis L1 1h expire pour une URL.

**Facteurs aggravants observes** :

1. **Aucun smoke test prod sur `/constructeurs/*`** dans `prod-smoke-tests.yml` — follow-up explicite d'INC-2026-006 (« ajouter smoke `/constructeurs/*` ») jamais fait.
2. **Aucune alerte sur `__error_logs` 5xx pages vehicule** — follow-up MEDIUM d'INC-2026-005 jamais fait.
3. **Blindspot critique d'instrumentation** : les `throw new Response(503)` du loader Remix n'ecrivaient RIEN dans `__error_logs` (verifie : 0 row depuis 21/04 alors qu'un 503 est observe le 25/04). Le buffer existe (commit `8f0b7b91`) mais le loader Remix n'utilisait pas l'API.
4. **L'ADR-016 est restee en `status: proposed`** alors que les Phases 1+2 ont ete deployees en prod. Aucun garde-fou ne refuse le deploy d'une Phase d'ADR sans validation des criteres.
5. **Mon analyse initiale s'est trompee** sur la severite (« blip transitoire ») et sur la solution proposee (« rallonger le timeout, ajouter cron warm » — bricolage pur). User a rejete 3x avant que je fasse le RCA empirique correct.

## Résolution

### Immediate (fix root-cause deploye 25/04 13:00-14:00 UTC)

**4 migrations Supabase appliquees en DB (CREATE OR REPLACE) :**

1. `20260425_optimize_build_vehicle_page_payload_catalog.sql` — reecrit la sous-requete `catalog` en deux phases (CTE) :
   - Phase 1 : index-only scan sur `idx_pieces_relation_type_type_id_composite` pour rtp_pg_id distincts (skip pieces).
   - Phase 2 : EXISTS check cible pour visibilite reelle.
   - Mesure : warm 27 ms vs 692 ms (-96 %), p50 cold 405 ms vs ~2 s (-80 %).
   - Semantique preservee (validee 10/10 types stale random).

2. `20260425_oneshot_backfill_stale_vehicle_cache.sql` — cron `* * * * *` rebuild 200 rows/min + watcher `*/2 * * * *` qui auto-`unschedule` les 2 jobs quand `stale_count = 0`. Ephemere par design.

3. `20260425_trigger_auto_type_rebuild_vehicle_cache.sql` — trigger AFTER INSERT OR UPDATE OF type_display sur `auto_type`, garantit zero rebuild on-miss en steady state pour les nouveaux types.

4. `20260425_mark_stale_with_followup_rebuild.sql` — wrapper canonique avec `p_reason` obligatoire. Tout script qui invalide `__vehicle_page_cache` DOIT l'utiliser.

**Backend (2 nouveaux controllers NestJS) :**

5. `AdminVehicleCacheController` — endpoints `POST/GET /api/admin/vehicle-cache/{rebuild,invalidate,stats}` (debug/hot-fix manuel).
6. `InternalErrorLogController` — endpoint `POST /api/internal/error-log` (X-Internal-Key auth) qui comble le blindspot loader Remix.

**Frontend (Remix loader R8) :**

7. `constructeurs.$brand.$model.$type.tsx` — helper `notify503ToErrorLog` fire-and-forget appele avant chacun des 4 chemins `throw 503`, avec subjects distincts pour debug.

**CI / Observabilite :**

8. `prod-smoke-tests.yml` — 3 URLs `/constructeurs/*` ajoutees au step pages-check + nouveau step `vehicle-5xx-check` qui interroge Supabase REST `__error_logs` heure par heure.
9. `scripts/ci/check-no-direct-vehicle-cache-stale.sh` — garde-fou CI : grep tout `UPDATE __vehicle_page_cache SET stale` non-exempte.

PR monorepo : https://github.com/ak125/nestjs-remix-monorepo/pull/167

### Differe (PR separees apres validation steady state)

- **Etape 6 (PR a venir)** : passer `RPC_TIMEOUT_MS` 2000 -> 500 ms dans `vehicle-rpc.service.ts` (alignement ADR-016 critere #5). Bloque sur J+1 validation que `stale_count = 0` est tenu en prod.
- **Etape 10 (vault)** : mettre ADR-016 status `proposed` -> `accepted` apres J+7 observation propre.

## Lessons Learned

1. **Une fonction nouvellement creee DOIT passer un EXPLAIN ANALYZE budget < 50 % du timeout cible AVANT deploiement.** `build_vehicle_page_payload` a ete deployee Phase 1 sans mesure de perf cold. Si on l'avait fait, on aurait vu 692 ms sur la seule sous-requete `catalog` et corrige avant. **Action structurelle : ajouter un check CI qui parse les ADR mergees et verifie que les Criteres de Succes coches correspondent a des commits/migrations reels.**

2. **Reduire un timeout requiert d'abord de prouver que le p99 cold tient sous le nouveau seuil.** Phase 2 a fait le contraire : baisse 9000 -> 2000 ms en assumant que la table cache O(1) absorberait tout — sans considerer le cas stale=true ou rebuild on-miss.

3. **`UPDATE __vehicle_page_cache SET stale=true` en bloc DOIT etre interdit en faveur de `mark_stale_with_followup_rebuild()`.** Le script `catalog_gamme_dedup_20260423` a marque 28 252 rows stale sans plan de rebuild, exposant la lenteur structurelle de la fonction. Le check CI `scripts/ci/check-no-direct-vehicle-cache-stale.sh` ferme ce vecteur.

4. **Un ADR avec criteres de succes non verifies ne doit PAS passer en `accepted`.** ADR-016 est restee `proposed` pendant que les Phases 1+2 etaient deployees en prod. La Phase 3 (cron + trigger) etait listee comme requise mais jamais implementee. **Action structurelle : auditer toutes les ADR `proposed` ou `accepted` du vault et verifier que chaque case [x] correspond a un artefact reel.**

5. **L'instrumentation `__error_logs` doit couvrir TOUS les chemins de generation 5xx, pas seulement ceux de NestJS.** Les `throw new Response(503)` du loader Remix etaient un blindspot total — 0 row sur 4 jours alors qu'un 503 a ete observe. Tout futur loader/middleware/edge function qui peut generer un 5xx DOIT appeler `/api/internal/error-log` (ou utiliser le service en injection si meme process).

6. **Mon raisonnement etait biaise par l'optimisme :** premiere reponse « blip transitoire », puis « hybride/pragmatique en attendant », rejetes 3x par user avec raison. **Quand un user dit « robuste pas de bricolage », ne JAMAIS proposer de palliatif type rallongement timeout / cron warm — toujours aller au structurel meme si plus de travail.** Memoire `feedback_no_hybrid_workarounds.md` cree pour codifier cette regle.

7. **Toujours utiliser le terme neutre « catalogue fournisseur »** dans mes propres artefacts (plans, mémoires, commits, incident vault) au lieu de citer le nom du fournisseur tiers, meme quand je resume du contenu vault qui le mentionne. Memoire `feedback_no_tecdoc_name.md` reinforcee suite a une recidive sur le plan initial.

## Actions Correctives

- [x] **[DONE 25/04]** 4 migrations DB appliquees (optim fonction + cron one-shot + trigger + wrapper canon)
- [x] **[DONE 25/04]** 2 nouveaux controllers NestJS (AdminVehicleCacheController + InternalErrorLogController)
- [x] **[DONE 25/04]** Loader Remix instrumente sur 4 chemins 503
- [x] **[DONE 25/04]** Smoke prod 3 URLs `/constructeurs/*` + check `__error_logs` 5xx
- [x] **[DONE 25/04]** Garde-fou CI `check-no-direct-vehicle-cache-stale.sh`
- [x] **[DONE 25/04 13:56]** PR monorepo #167 ouverte (3 commits root-cause + 1 commit fix smoke URLs cherry-pick)
- [x] **[DONE 25/04 14:25]** PR vault #65 ouverte (post-mortem INC-2026-010)
- [x] **[DONE 25/04 ~16:00]** Verifier `stale_count = 0` en prod, watcher unschedule effectif (auto via cron one-shot watcher)
- [x] **[DONE J+2 27/04 14:03]** Re-validation : stale=0, fresh=28 505, page 34746 = HTTP 200, stress 100 hits = 100/100 = 200

### Reste a faire (hors session, attente user)

- [ ] **[USER ACTION]** **Merger PR monorepo #167** : https://github.com/ak125/nestjs-remix-monorepo/pull/167
  - Contient : 4 migrations DB + 2 controllers NestJS + instrumentation loader Remix + smoke CI + check CI guard
  - Note : les 4 migrations DB sont DEJA appliquees en prod via MCP. Le merge ne re-appliquera rien (CREATE OR REPLACE idempotent, DROP TRIGGER IF EXISTS), il trace seulement les fichiers de migration dans le repo.
  - Pre-requis : aucun, PR pure code/migrations sans rollback risque.

- [ ] **[USER ACTION]** **Merger PR vault #65** : https://github.com/ak125/governance-vault/pull/65
  - Contient : ce post-mortem INC-2026-010.

- [ ] **[POST-MERGE #167 — USER]** Tag semver `vYYYY.MM.DD-inc-2026-007` puis push pour declencher `deploy-prod.yml` (cf. memory `deployment-workflow.md`).
  - Etat actuel : DB deja patchee (fonction optim + cron + trigger + canon), mais code backend NestJS et frontend Remix pas encore en prod -> les nouveaux endpoints `/api/admin/vehicle-cache/*` et `/api/internal/error-log` ne sont pas encore disponibles, et le loader Remix ne notifie pas encore les 503 dans `__error_logs`.
  - **Conséquence si pas tagge** : le système continue de marcher (DB resout le 503), mais les blindspots d'observabilite restent ouverts jusqu'au deploy PROD.

- [ ] **[ETAPE 6 — Bloquee sur merge #167]** Ouvrir PR separee qui passe `RPC_TIMEOUT_MS` 2000 -> 500 ms dans `backend/src/modules/vehicles/services/vehicle-rpc.service.ts:27`.
  - Pre-requis tous valides depuis 25/04 ~16:00 (stale=0 + trigger + canon en place).
  - Conformite : alignement final ADR-016 critere de succes #5.
  - Risque : si une anomalie produit un rebuild on-miss, comportement echec-rapide-visible (503 en 500ms + alerte) plutot que tolerance silencieuse.

- [ ] **[ETAPE 10 — Apres J+7 d'observation]** Mettre ADR-016 status `proposed` -> `accepted` avec preuves criteres #1-#5 coches (vault).
  - Date cible : 2026-05-02 (J+7 du steady state 25/04).

- [ ] **[J+14 — 2026-05-09]** Verifier 0 entree `__error_logs` 5xx sur `/constructeurs/*` sur 14 jours rolling (pre-requis : merge #167 + deploy PROD pour que l'instrumentation loader soit active).

- [ ] **[J+14 — 2026-05-09]** Re-validation GSC « erreur serveur (5xx) » sur sitemap vehicule.

- [ ] **[FOLLOWUP CI]** Wirer `scripts/ci/check-no-direct-vehicle-cache-stale.sh` dans `.github/workflows/ci.yml` (le script existe sur la branche fix mais n'est pas encore appele par CI).

- [ ] **[FOLLOWUP STRUCTUREL #1]** Auditer toutes les ADR `proposed`/`accepted` du vault et verifier que chaque case [x] correspond a un artefact reel (issue revele par cet incident : ADR-016 etait `proposed` avec criteres non valides en prod).

- [ ] **[FOLLOWUP STRUCTUREL #2]** Ajouter un check CI qui parse les ADR mergees et verifie que les criteres de succes coches correspondent a des commits/migrations reels.

## Preuves

- Commit Phase 2 ADR-016 (cause #1) : `fc9b94af` (21/04, monorepo) — drop legacy RPC + RPC_TIMEOUT_MS 9000 -> 2000
- Script dedup gamme (cause #3) : `stale_reason='catalog_gamme_dedup_20260423'` sur 28 252 rows
- EXPLAIN ANALYZE before fix (type 18110) : 692 ms / 18 384 row scans / Buffers hit=72 622 read=2 165 (sous-requete `catalog` seule)
- EXPLAIN ANALYZE after fix : 27 ms / 113 rows / Buffers hit=11 868 read=0 (-96 %)
- Stress test 50 types stale random post-fix : p50=405 ms, p95=1816 ms, p99=2135 ms
- Validation semantique : 5/5 types snapshot identique avant/apres (n_families et total_gammes)
- PR monorepo : https://github.com/ak125/nestjs-remix-monorepo/pull/167 (4 commits, OPEN au 27/04)
- PR vault : https://github.com/ak125/governance-vault/pull/65 (1 commit, OPEN au 27/04)
- DB live state au moment du push : 27 052 stale (en cours de rattrapage), 1 453 fresh, 2 cron jobs actifs
- DB live state J+2 (2026-04-27 14:03 UTC) : **stale=0, fresh=28 505, cron_jobs_active=0** (steady state confirme)
- Stress test live J+2 sur 34746 : 100/100 hits paralleles = HTTP 200 (zero 503), p50/p99 ~6.9 s sous charge (file d'attente Node normale)
- Stress test live J+2 sur 4 URLs distinctes (chevrolet-1623, fiat-1630, vw-1709, renault-34746) : 4/4 = HTTP 200 entre 126-234 ms

## Communication

- [x] User (solo-owner) notifie en live pendant l'incident (rejet 3x avant fix root-cause)
- [x] PR monorepo ouverte avec test plan complet
- [ ] PR vault (cet incident) ouverte
- [ ] J+7 : valider que les actions correctives J+1 et J+7 sont coches
- [ ] J+14 : confirmer 0 entree `__error_logs` 5xx + re-validation GSC

## Liens

- Related : [[ADR-016-vehicle-page-matview-persistence]] (ADR origine, status `proposed` a faire passer `accepted`)
- Related : [[ADR-021-database-rls-hardening-zero-trust]] (deployee meme jour 23/04 — non-cause confirmee par mesure RLS=BYPASS effective via SECURITY DEFINER)
- Related : [[2026-04-20-gsc-5xx-vehicle-page-cold-rpc]] (INC-2026-005, ancetre meme classe de bug)
- Related : [[2026-04-21-503-vehicle-pages-rpc-allowlist-stale-image]] (INC-2026-006, meme commit fc9b94af coupable)
- Related rules : [[rules-technical]], [[rules-seo-pagerole]], [[ADR-003-rpc-governance]]
- Code affecte (monorepo) :
  - `backend/src/modules/vehicles/services/vehicle-rpc.service.ts:24-29` (RPC_TIMEOUT_MS)
  - `frontend/app/routes/constructeurs.$brand.$model.$type.tsx:80-110` (notify503ToErrorLog)
  - `backend/supabase/migrations/20260425_*.sql` (4 nouvelles migrations)
- Memories operationnelles creees :
  - `feedback_no_hybrid_workarounds.md` (regle structurel vs bricolage)
  - `feedback_no_tecdoc_name.md` (renforcee suite a recidive)

---

*Cree le : 2026-04-25*
*Derniere mise a jour : 2026-04-25*
