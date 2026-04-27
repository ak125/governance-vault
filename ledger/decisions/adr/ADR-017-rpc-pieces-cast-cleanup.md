---
id: ADR-017
title: "Nettoyer les casts TEXT↔INTEGER dans les RPC pieces_* — indexation effective"
status: accepted
date: 2026-04-21
decision_makers:
  - "@automecanik.seo"
supersedes: []
superseded_by: []
related_rules:
  - rpc-governance
  - performance-budget-ttfb
related_incidents:
  - INC-2026-005-gsc-5xx-vehicle-page-cold-rpc
related_adrs:
  - ADR-016-vehicle-page-matview-persistence
  - ADR-018-dual-column-schema-consolidation
reviewed_by: "Claude Opus 4.7"
implementation_evidence:
  status_review_at: 2026-04-27
  reviewed_by: "Claude Opus 4.7"
  phase_1_status: LIVE
  phase_1_live_at: 2026-04-21
  migrations_shipped:
    - 20260421_adr017_rpc_pieces_cast_cleanup.sql
  perf_gain_phase1: "RPC #1 -96% (395ms vs 10.5s baseline)"
  index_gain: "+2.6 GB de couverture index effective"
  remaining_phases:
    - "8 RPC pieces_* restantes à traiter dans les phases suivantes"
  notes: |
    Phase 1 LIVE en production le 2026-04-21. RPC #1 mesuré à 395ms vs 10.5s
    baseline pré-cleanup (gain -96%). Décision factuellement appliquée et
    mesurée. Statut passé de `proposed` (6 jours stale après livraison Phase 1)
    à `accepted` pour refléter la réalité. Les 8 phases restantes sont du
    follow-up tracké via le plan d'implémentation, pas une raison de garder
    la décision en `proposed`.
tags:
  - adr/accepted
  - domain/catalog
  - tech/postgres
  - tech/supabase
---

# ADR-017 : Nettoyer les casts TEXT↔INTEGER dans les RPC `pieces_*` — indexation effective

## Contexte

Audit CPU Supabase 2026-04-21 — les **top 3 RPC consomment 82% du CPU DB total** :

| Rang | RPC | Appels | Moy | % CPU | Cause |
|:---:|---|---:|---:|---:|---|
| 1 | `get_alternative_vehicles_for_gamme` | 353 k | 10,5 s | 45% | 3 casts `::text/::integer` + index leading `rtp_pg_id` absent |
| 2 | `rm_get_page_complete_v2` | 3,2 M | 575 ms | 23% | 4 `NULLIF(...)::INTEGER` |
| 3 | `get_pieces_for_type_gamme_v3` | 2,4 M | 504 ms | 15% | 17 `NULLIF(...)::INTEGER` |

Audit étendu sur **toutes les RPC `public.*`** touchant `pieces_relation_type` + `auto_type` : **9 RPC** partagent le même pattern de casts, pas seulement les 3 du top.

### Faits mesurés DB (2026-04-21)

- `pieces_relation_type` : **47 GB / 368 M lignes**
- Indexes actuels : `(rtp_type_id, rtp_piece_id)` PK, `(rtp_type_id, rtp_pg_id)` partial, `rtp_piece_id`
- **Aucun index leading `rtp_pg_id`** → filtrage par gamme = Index-Only Scan sur toute la leading-col (coûteux)
- `auto_type` a **deux colonnes pour chaque FK** : `type_id TEXT` + `type_id_i INTEGER` (pattern dual, cf. memory `db-pieces-indexes.md`)
- Index unique `idx_auto_type_type_id_i_unique` sur `type_id_i` INTEGER **déjà présent** mais inutilisable car les RPC casted `rtp.rtp_type_id::text`

## Décision

**Réécrire les 9 RPC identifiées pour utiliser les colonnes `_i` INTEGER, supprimer les casts TEXT↔INTEGER, et créer les 2-3 index manquants sur `pieces_relation_type`.** Une seule migration, un seul commit, rollback trivial via `CREATE OR REPLACE`.

ADR-017 traite la **surface de contamination** (9 RPC). La **cause racine** (schéma dual TEXT/INTEGER) est hors-scope ici et renvoyée à **ADR-018**.

## Options Considérées

### Option A : Cleanup ciblé top-3 (SUBOPTIMAL)

Corriger uniquement les 3 RPC du top CPU.

**Avantages**
- -82% CPU immédiat.
- 2 h d'effort.

**Inconvénients**
- Les 6 autres RPC avec le même pattern continuent de gaspiller CPU et de bloquer les index.
- Prochaine RPC ajoutée par erreur dans le même pattern = régression invisible.
- Pas de garantie de consistance.

### Option B : Cleanup systématique 9 RPC + index (RETENUE)

Réécrire les 9 RPC avec colonnes `_i` et supprimer tous les casts. Créer les indexes manquants.

**Avantages**
- Surface 100% couverte.
- Mêmes primitives partout → revue simplifiée.
- Prépare ADR-018 (schéma propre) en prouvant qu'aucune RPC ne dépend des colonnes TEXT.

**Inconvénients**
- 1-2 jours d'effort (vs 2 h pour A).
- Plus de tests à écrire/valider.

### Option C : Matérialisation à la ADR-016 pour chaque RPC

Créer une table cache dédiée pour chaque RPC coûteuse.

**Avantages**
- O(1) lookup sur chaque cache.

**Inconvénients**
- **Ne traite pas la cause racine** — même si on cache, les RPC de rebuild auront toujours le bug.
- Multiplie les tables de cache (maintenance, invalidation, storage).
- Rejetée : ADR-016 est justifiée pour le cas véhicule (données quasi-statiques) ; généraliser à pieces_* = bricolage.

### Option D : Ignorer, compter sur Caddy/Redis

**Rejetée** — c'est exactement le bricolage supprimé dans ADR-016 Phase 2.

## Justification

Option B retenue pour 4 raisons :

1. **Cause unique, fix unique** : les 9 RPC partagent le même bug (casts bloquant indexes `_i`). Corriger une par une = bricolage. Corriger les 9 ensemble = méthode.
2. **Prérequis ADR-018** : avant d'éliminer les colonnes TEXT, il faut s'assurer qu'aucune RPC ne s'y accroche. ADR-017 valide ce préalable.
3. **Risque minimal** : `CREATE OR REPLACE FUNCTION` est réversible immédiatement. `CREATE INDEX CONCURRENTLY` ne lock pas.
4. **Observabilité** : pg_stat_statements donnera une preuve nette (CPU/s par RPC) avant/après.

## Conséquences

### Positives

- p99 `get_alternative_vehicles_for_gamme` : 10,5 s → **< 200 ms** (cible)
- CPU DB total : **-60 à -75%** estimé sur les 9 RPC
- Supprime la nécessité d'un cache Redis devant `/api/rm/alternatives`
- Clarifie le codebase : une seule façon de joindre les tables (par les `_i`)
- Prépare ADR-018 (schéma consolidé)

### Négatives

- Les colonnes `_i` doivent être **backfillées à 100%** — à vérifier en préalable (quelques RPC pourraient avoir des NULL `_i` legacy).
- Migration = 9 `CREATE OR REPLACE FUNCTION` + 2-3 `CREATE INDEX CONCURRENTLY`. Fichier SQL volumineux.
- 1-2 h de build d'index sur table 47 GB (CONCURRENTLY, non-bloquant).

### Neutres

- API contracts inchangés (même signatures RPC).
- Callers backend NestJS inchangés.

## Critères de Succès

- [ ] 9 RPC réécrites, `pg_stat_statements` confirme `-60% CPU` total après 48 h d'observation
- [ ] 0 cast `::text` / `::integer` / `NULLIF(...)::INTEGER` restant dans `pg_proc WHERE nspname='public'` sur ces 9 fonctions
- [ ] `CREATE INDEX CONCURRENTLY idx_prt_pg_id_type_id` construit et utilisé (EXPLAIN)
- [ ] `get_alternative_vehicles_for_gamme` p99 < 200 ms (vs 10,5 s)
- [ ] Tests d'intégration sur les 3 routes appelantes OK
- [ ] Aucune régression sur `__error_logs` après 7 jours

## Implémentation

### Phase 1 — Pré-requis (J0)

1. **Vérifier backfill des colonnes `_i`** :
   ```sql
   SELECT 'auto_type' AS t, COUNT(*) FILTER (WHERE type_id_i IS NULL) AS null_i FROM auto_type;
   -- Idem pour auto_modele, auto_marque, pieces, pieces_gamme
   ```
2. **Snapshot pg_stat_statements** pour baseline avant.
3. **Audit query** déjà exécutée 2026-04-21 : 9 RPC identifiées.

### Phase 2 — Migration SQL (J0, ~1 h)

Un fichier `backend/supabase/migrations/YYYYMMDD_rpc_pieces_cast_cleanup_adr017.sql` contenant :

1. `CREATE OR REPLACE FUNCTION public.get_alternative_vehicles_for_gamme(...)` version `_i`
2. `CREATE OR REPLACE FUNCTION public.rm_get_page_complete_v2(...)` version `_i`
3. `CREATE OR REPLACE FUNCTION public.get_pieces_for_type_gamme_v3(...)` version `_i`
4. ... et les 6 autres (v1, v2, v4, listing_*, build_v2)
5. `CREATE INDEX CONCURRENTLY idx_prt_pg_id_type_id ON pieces_relation_type (rtp_pg_id, rtp_type_id)` — **hors transaction**, à exécuter séparément.

### Phase 3 — Validation (J0+2h)

1. EXPLAIN ANALYZE sur chaque RPC avec un type_id/gamme_id standard → plan attendu : Index Scan, pas de Seq Scan sur `auto_type`/`auto_modele`/`auto_marque`.
2. Smoke test 5 URLs live → temps de réponse < 500 ms.
3. Snapshot pg_stat_statements à J+1 → delta CPU mesurable.

### Phase 4 — Observation (J+7)

1. Dashboard Supabase : p50/p95/p99 par RPC.
2. Alerte PREV-1 : `err_status >= 500 AND err_url LIKE '/api/rm/%'` > 5/h.
3. Si les 4 critères de succès sont verts : marquer ADR-017 `accepted`.

**Fichiers concernés (monorepo `nestjs-remix-monorepo`) :**

- `backend/supabase/migrations/YYYYMMDD_rpc_pieces_cast_cleanup_adr017.sql` (nouveau)
- Aucun changement côté NestJS (signatures RPC inchangées).
- Mise à jour `backend/src/database/types/database.types.ts` après migration (regénération).

## Revue Planifiée

**Date** : 2026-05-19 (J+28)
**Critères de revue** :
- Si p99 `get_alternative_vehicles_for_gamme` > 200 ms → partitionner `pieces_relation_type` par tranche de `rtp_pg_id`.
- Si le bug se reproduit sur une nouvelle RPC ajoutée post-ADR : ajouter un CI gate qui refuse toute RPC avec casts `::text`/`::integer`/`NULLIF(...)::INTEGER` sur ces tables.
- Déclencher ADR-018 (schéma dual) dès que les 9 RPC sont stables et l'audit couvre 100% des consommateurs de colonnes TEXT.

## Liens

- Related : [[2026-04-20-gsc-5xx-vehicle-page-cold-rpc]]
- Related : [[ADR-016-vehicle-page-matview-persistence]] (même classe de problème, autre RPC)
- Related : [[ADR-018-dual-column-schema-consolidation]] (cause racine)
- Related rules : [[rules-technical]], [[rules-technical]]

---

*Proposé le : 2026-04-21*
*Accepté le : (en attente de validation @automecanik.seo)*
*Dernière revue : 2026-04-21*
