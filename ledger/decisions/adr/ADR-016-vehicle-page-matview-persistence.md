---
id: ADR-016
title: "Vehicle Page Data — Persistance par matérialisation, pas par tolérance de timeout"
status: proposed
date: 2026-04-20
decision_makers:
  - "@automecanik.seo"
supersedes: []
superseded_by: []
related_rules:
  - performance-budget-ttfb
  - seo-http-status-contract
  - rpc-governance
related_incidents:
  - INC-2026-005-gsc-5xx-vehicle-page-cold-rpc
reviewed_by: "Claude Opus 4.7"
tags:
  - adr/proposed
  - domain/catalog
  - domain/seo
  - tech/postgres
  - tech/supabase
---

# ADR-016 : Vehicle Page Data — Persistance par matérialisation, pas par tolérance de timeout

## Contexte

La page véhicule R8 (`/constructeurs/{brand}/{model}/{type}.html`) et la page produit R2 (`/pieces/{gamme}/{brand}/{model}/{type}.html`) s'appuient sur la RPC `get_vehicle_page_data_optimized(p_type_id)` qui agrège **7 sections** incluant des jointures sur `pieces_relation_type`.

**Faits mesurés (2026-04-20) :**
- `pieces_relation_type` : **47 GB** (27 GB heap, 20 GB indexes), **368 304 448 rows**
- RPC cold p99 ≈ **4 s** (documenté dans commit `eff30b7f`)
- RPC warm p99 = **42-48 ms** via Redis
- 8 index dont **`idx_pieces_relation_type_popular`** — index partiel WHERE `rtp_type_id IN (top-10 hardcodé)` : bricolage existant qui ne protège que 10 types sur ~54 000
- 53 959 `type_id` en catalogue (30 502 legacy + 23 457 TecDoc remap)

**Problème constaté (INC-2026-005) :**
Entre 2026-03 et 2026-04-13, **30 500 URLs** (GSC) ont renvoyé 5xx parce que :
1. Le timeout backend (1500 ms) était plus strict que le p99 cold (4000 ms).
2. Le long tail de 53 949 types (tout sauf le top-10) passait systématiquement par le plan lent.
3. Chaque éviction Redis ou type rare = rafale de 503 au crawler.

Le palliatif déployé le 13/04 (timeout adaptatif 3/9 s + Caddy retry) **tolère** la lenteur au lieu de la corriger. La table continue de grossir (+TecDoc sync quotidien). Sans correction structurelle, la régression est probable.

## Décision

**Matérialiser les données de page véhicule dans une table dénormalisée `__vehicle_page_cache`, peuplée et rafraîchie de façon pilotée, et réécrire la RPC en simple `SELECT WHERE type_id = $1` sur cette table.**

Supprimer les palliatifs qui deviennent inutiles :
1. `idx_pieces_relation_type_popular` (index partiel hardcodé top-10)
2. Le timeout adaptatif `RPC_TIMEOUT_MS` / `RPC_COLD_TIMEOUT_MS` (retour à un timeout unique court)
3. Le fallback stale Redis (la source de vérité rapide est la table cache)

## Options Considérées

### Option A : Matérialisation persistante `__vehicle_page_cache` (RETENUE)

**Description** : Table régulière (pas matview) avec une ligne par `type_id`, contenant la sortie JSON complète de l'ancienne RPC. Peuplée par un job batch nightly (après la sync TecDoc), lignes individuelles invalidées/reconstruites à la demande via trigger sur `pieces_relation_type` ou appel explicite d'un endpoint admin.

```sql
CREATE TABLE __vehicle_page_cache (
  type_id        INTEGER PRIMARY KEY,
  payload        JSONB NOT NULL,
  built_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  source_hash    TEXT NOT NULL,  -- hash des inputs pour invalidation ciblée
  stale          BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_vpc_stale ON __vehicle_page_cache(stale) WHERE stale = TRUE;
```

**Avantages** :
- Lookup O(1) sur PK → p99 < 10 ms garanti, indépendant de la taille de `pieces_relation_type`.
- Rebuild ciblé (un seul type_id) possible, pas de REFRESH MATVIEW global bloquant.
- Supprime 3 bricolages : timeout adaptatif, Caddy retry, index partiel top-10, fallback stale Redis.
- Permet un contrat SLA strict : `RPC p99 < 50 ms`.
- Taille estimée : 54 000 types × ~30 KB JSON ≈ **1,6 GB** (soutenable).
- Invalidation fine : on peut marquer `stale=TRUE` pour un seul type sans toucher aux 54 k autres.

**Inconvénients** :
- Fraîcheur = latence du batch (objectif : J+1 après sync TecDoc). Acceptable : TecDoc sync quotidien, pas de données temps réel sur une page véhicule.
- Coût d'écriture initial : ~54 k appels de la fonction de build (à paralléliser).
- Une nouvelle source de vérité à maintenir (cohérence de `source_hash`).

### Option B : Materialized View `mv_vehicle_page_data` + REFRESH CONCURRENTLY

**Description** : Matview Postgres standard rafraîchie nightly.

**Avantages** :
- Syntaxe Postgres native, pas de table custom.
- Rebuild atomique.

**Inconvénients** :
- `REFRESH MATERIALIZED VIEW CONCURRENTLY` nécessite un UNIQUE INDEX et **lock partiel** pendant le refresh; sur 54 k lignes + jointures 368 M, le refresh lui-même prend plusieurs minutes et consomme fortement l'IO.
- Pas d'invalidation ciblée : toute modification force un REFRESH global.
- Moins flexible pour backfill incrémental.

### Option C : Index covering + query rewrite + STATISTICS

**Description** : Ajouter `CREATE INDEX CONCURRENTLY idx_prt_type_covering ON pieces_relation_type(rtp_type_id) INCLUDE (rtp_piece_id, rtp_pg_id)` + forcer hash join via `SET enable_nestloop=off` dans la RPC + `CREATE STATISTICS` multi-colonnes.

**Avantages** :
- Moins invasif, pas de nouvelle table.
- Laisse Postgres décider du plan.

**Inconvénients** :
- Ne descend probablement pas sous 500 ms-1 s sur cold path (368 M rows reste 368 M rows).
- Ajoute encore un index sur une table déjà à 20 GB d'index.
- Ne supprime pas le bricolage existant (timeout adaptatif, index top-10).
- Le `SET enable_nestloop=off` dans RPC = anti-pattern Postgres.

### Option D : Statut quo (ne rien faire)

**Description** : Conserver le palliatif du 13/04.

**Avantages** :
- Zéro travail immédiat.

**Inconvénients** :
- La table grossit, le p99 grossit avec elle → régression inéluctable.
- Les bricolages empilés (index hardcodé, timeout adaptatif) sont une dette de gouvernance G2 (Zero Orphelin).
- Risque SEO permanent : GSC continuera d'alerter à chaque rafale d'évictions Redis.

## Justification

**Option A retenue** pour 4 raisons :

1. **Contrat SLA restauré** : on passe d'un "timeout plus grand que p99 cold" (tolérance) à un "lookup O(1) garanti" (contrat). C'est la définition de "pas de bricolage".
2. **Dette supprimée, pas ajoutée** : 3 workarounds disparaissent (`idx_…_popular`, `RPC_COLD_TIMEOUT_MS`, `fallback stale Redis`).
3. **Alignement domaine** : les données de page véhicule ne sont pas temps réel (TecDoc = batch quotidien), matérialiser est cohérent avec le cycle métier.
4. **Supporte la croissance** : si `pieces_relation_type` passe de 368 M à 500 M rows, la table `__vehicle_page_cache` reste stable (toujours ~54 k lignes).

Option B rejetée : le refresh global bloque l'IO pendant plusieurs minutes sur une table déjà à 47 GB. Option C rejetée : n'élimine pas le problème, ajoute de la dette. Option D rejetée : la régression est certaine à moyen terme.

## Conséquences

### Positives

- **p99 SSR page véhicule < 100 ms** (cible), **LCP Googlebot < 1 s**.
- Suppression de 3 bricolages → codebase plus lisible.
- `__error_logs` ne remonte plus de 503 sur `/constructeurs/*` et `/pieces/*/…`.
- GSC "erreur 5xx" → 0 sur cette catégorie après 7 jours.
- La logique métier de construction du payload centralisée dans **une seule fonction** (`build_vehicle_page_payload(type_id)`), réutilisable pour debug/QA/regen.

### Négatives

- Fraîcheur J+1 (acceptable métier, à communiquer aux équipes content/SEO).
- 1,6 GB de stockage supplémentaire (négligeable vs 47 GB actuels).
- Migration initiale ~6 h compute (parallélisable) pour backfill les 54 k types.
- Nouvelle table à sauvegarder et surveiller.

### Neutres

- Le code frontend ne change pas (même RPC, même payload JSON).
- Le contrat d'API `/api/vehicles/types/{type_id}/page-data-rpc` est préservé.

## Critères de Succès

- [ ] `get_vehicle_page_data_optimized` p99 mesuré < 50 ms sur 7 jours consécutifs
- [ ] 0 entrée dans `__error_logs` WHERE `err_status >= 500 AND err_url LIKE '/constructeurs/%'` sur 14 jours
- [ ] GSC "Erreur serveur (5xx)" sur sitemap véhicule : 0 URLs après 14 jours
- [ ] `idx_pieces_relation_type_popular` supprimé
- [ ] Constantes `RPC_COLD_TIMEOUT_MS` et `RPC_TIMEOUT_MS` fusionnées en une seule `RPC_TIMEOUT_MS = 500`
- [ ] Doc runbook `ops/runbooks/vehicle-page-cache-rebuild.md` publiée

## Implémentation

### Phase 1 — Schéma et backfill (J+1 à J+3)

1. Migration Supabase : créer `__vehicle_page_cache` (DDL ci-dessus).
2. Créer la fonction `build_vehicle_page_payload(p_type_id INTEGER) RETURNS JSONB` — extraction propre de la logique actuelle de `get_vehicle_page_data_optimized`.
3. Créer la fonction `rebuild_vehicle_page_cache(p_type_id INTEGER)` qui appelle `build_vehicle_page_payload` et UPSERT dans `__vehicle_page_cache` avec `source_hash = md5(…inputs)`.
4. Script batch `scripts/seo/backfill-vehicle-page-cache.ts` — itère les 54 k types par paquets de 200, en parallèle × 4. Durée estimée 4-6 h.
5. Vérification : `SELECT COUNT(*) FROM __vehicle_page_cache` == `SELECT COUNT(DISTINCT type_id) FROM auto_type WHERE type_display = 1`.

### Phase 2 — Réécriture RPC (J+4)

```sql
CREATE OR REPLACE FUNCTION get_vehicle_page_data_optimized(p_type_id INTEGER)
RETURNS JSONB LANGUAGE sql STABLE AS $$
  SELECT payload
  FROM __vehicle_page_cache
  WHERE type_id = p_type_id AND NOT stale
$$;
```

Fallback : si `stale = TRUE` ou ligne absente, appeler synchroniquement `build_vehicle_page_payload` (cold path one-shot, puis persiste). Timeout unique 500 ms côté backend suffira.

### Phase 3 — Invalidation et refresh (J+5 à J+7)

1. Trigger sur `pieces_relation_type` : `AFTER INSERT/UPDATE/DELETE → UPDATE __vehicle_page_cache SET stale=TRUE WHERE type_id IN (NEW.rtp_type_id, OLD.rtp_type_id)`.
2. Cron Supabase `refresh_stale_vehicle_cache` toutes les 10 min : `SELECT rebuild_vehicle_page_cache(type_id) FROM __vehicle_page_cache WHERE stale = TRUE LIMIT 500`.
3. Endpoint admin `POST /api/admin/vehicle-cache/rebuild/:type_id` pour rebuild manuel.

### Phase 4 — Nettoyage bricolages (J+8)

1. `DROP INDEX idx_pieces_relation_type_popular`.
2. Supprimer `RPC_COLD_TIMEOUT_MS` dans `vehicle-rpc.service.ts`, fusionner avec `RPC_TIMEOUT_MS = 500`.
3. Retirer le fallback stale Redis (plus nécessaire, Redis devient cache de second niveau optionnel).
4. Simplifier Caddy : retirer `lb_try_duration` (le backend ne met plus > 500 ms).

### Phase 5 — Observation & validation (J+8 à J+22)

1. Dashboard Supabase : p50/p95/p99 sur `get_vehicle_page_data_optimized` par heure.
2. Alerte PREV-1 : `err_status >= 500 AND err_url LIKE '/constructeurs/%'` > 5/h → Gmail.
3. J+14 : relancer la validation GSC.
4. J+22 : clore l'ADR (status `accepted` → évaluer pour `implemented`).

**Fichiers concernés :**
- `backend/supabase/migrations/20260501_vehicle_page_cache.sql` (nouveau)
- `backend/supabase/migrations/20260502_rebuild_vehicle_page_payload.sql` (nouveau)
- `backend/supabase/migrations/20260503_drop_popular_index.sql` (nouveau)
- `backend/src/modules/vehicles/services/vehicle-rpc.service.ts` (simplification)
- `backend/src/modules/admin/controllers/admin-vehicle-cache.controller.ts` (nouveau)
- `scripts/seo/backfill-vehicle-page-cache.ts` (nouveau)
- `docker/caddy/Caddyfile` (retrait `lb_try_duration`)
- `.spec/runbooks/vehicle-page-cache-rebuild.md` → à publier dans vault `ops/runbooks/`

## Revue Planifiée

**Date** : 2026-05-18 (J+28 après déploiement prévu ~2026-04-25 à 2026-05-02)
**Critères de revue** :
- Si p99 > 50 ms, rouvrir l'ADR et évaluer partitionnement de `__vehicle_page_cache` par range de type_id.
- Si le trigger sur `pieces_relation_type` dégrade l'INSERT TecDoc de > 10%, le remplacer par un diff-based refresh batch.
- Si un jour on passe à TecDoc temps réel (pas batch nightly), reconsidérer vers un pattern streaming (Kafka + Debezium).

## Liens

- Related : [[2026-04-20-gsc-5xx-vehicle-page-cold-rpc]]
- Related : [[ADR-003-rpc-governance]] (principes RPC)
- Related rules : [[rules-technical]], [[rules-seo-pagerole]]

---

*Proposé le : 2026-04-20*
*Accepté le : (en attente de validation @automecanik.seo)*
*Dernière revue : 2026-04-20*
