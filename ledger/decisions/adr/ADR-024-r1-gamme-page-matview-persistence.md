---
id: ADR-024
title: "R1 Gamme Page Data — Persistance par matérialisation, parité ADR-016"
status: proposed
date: 2026-04-27
decision_makers:
  - "@automecanik.seo"
supersedes: []
superseded_by: []
related_rules:
  - rules-engineering-quality
  - performance-budget-ttfb
  - seo-http-status-contract
  - rpc-governance
related_incidents: []
related_adrs:
  - ADR-016-vehicle-page-matview-persistence
  - ADR-017-rpc-pieces-cast-cleanup
reviewed_by: "Claude Opus 4.7"
tags:
  - adr/proposed
  - domain/catalog
  - domain/seo
  - tech/postgres
  - tech/supabase
---

# ADR-024 : R1 Gamme Page Data — Persistance par matérialisation, parité ADR-016

## Contexte

La page R1 gamme (`/pieces/{slug}-{pg_id}.html`) sert ~238 gammes G1/G2 indexées (les plus populaires : plaquettes-de-frein, filtre-à-huile, kit d'embrayage, etc.). Sur cold-load, le SSR critique dépasse régulièrement 15 s, créant des timeouts E2E et des LCP catastrophiques pour les utilisateurs en cache miss.

### Faits mesurés (2026-04-27, run CI 24986826205, post-merge PR #190 sur `main`)

- **E2E Playwright** sur `/pieces/plaquettes-de-frein-1.html` (gamme la plus populaire) :
  - 2 / 8 timeouts à 15 s (échec final après 3 retries)
  - 6 / 8 flaky (récupération aléatoire sur retry)
  - 44 / 8 passed sur d'autres gammes
- **Perf gate** sur `/pieces/plaquette-de-frein-402/...html` (R2) : 3122 ms, **dépasse déjà le budget 3000 ms** (warning, non bloquant). Le run précédent (`695fb86d`) mesurait 3118 ms : pas une régression, c'est un état stable au-dessus du budget.
- Le run précédent main avait **7 / 8 flaky** (tous récupérés → vert). La marge contre le timeout 15 s est aléatoire entre runs.

### Compte des gammes concernées

```sql
SELECT COUNT(*) FROM pieces_gamme WHERE pg_level IN ('1','2');
-- 238 gammes G1/G2 (vs ~232 indiqué historiquement)
SELECT COUNT(*) FROM pieces_gamme WHERE pg_display = '1';
-- 4205 displayed (large surface mais 238 sont la cible canon SEO)
```

### Architecture actuelle

1. **Frontend** `frontend/app/routes/pieces.$slug.tsx:201` :
   ```ts
   const [apiData, substitutionResponse] = await Promise.all([
     fetchGammePageData(gammeId, { signal: controller.signal }),
     fetch(`${API_URL}/api/substitution/check?url=${encodeURIComponent(pathname)}`, { signal: subController.signal })
       .then((res) => (res.ok ? res.json() : null))
       .catch(() => null),
   ]);
   ```
   Loader avec timeout global 15 s — bloque sur `fetchGammePageData` (RPC V2 ou fallback classic).

2. **Backend controller** `gamme-rest-rpc-v2.controller.ts:62` :
   ```ts
   const cached = await this.cacheService.get<Record<string, any>>(cacheKey);
   if (cached) return { ...cached, performance: { responseCacheHit: true } };
   const result = await this.responseBuilder.buildRpcV2Response(pgId);
   ```
   Double couche cache : `gamme:rpc-v2:{pgId}` (data) + `gamme:response:{pgId}` (response). Si miss sur response cache → `buildRpcV2Response` exécute.

3. **Response builder** `gamme-response-builder.service.ts` (948 lignes), après le RPC PostgreSQL :
   - Ligne 174 : query `__seo_gamme.sg_content` (conditionnel)
   - Ligne 195 : query `__seo_r1_image_prompts` (toujours, ordre desc, pas d'index visible sur `rip_pg_id+rip_status`)
   - Ligne 230 : `relatedResources.buildRelatedBlocks` → **filesystem read RAG** + 3 sub-queries Promise.all
   - Ligne 617 : `await buyingGuideService.getBuyingGuideContractV1(pgId)` → 1 RPC + transformation 2662 lignes

### Le bug structurel

Le warming au boot (`cache-warming.service.ts:280`) appelle `rpcService.getPageDataRpcV2()` qui ne warm que le **data cache** (`gamme:rpc-v2:{pgId}`), **pas le response cache** (`gamme:response:{pgId}` géré par le controller). Conséquence : même avec 238 gammes warmed, le **premier hit utilisateur sur chaque gamme** déclenche les 4 requêtes séquentielles → 3-15 s.

Symétrie cassée avec R2 (`fetchRmPageV2`, route R2 produit) qui utilise UNE RPC qui retourne tout, plus aucun enrichissement applicatif au request-time.

### Précédent : ADR-016 (Vehicle Page matview)

ADR-016 (status: `accepted` — promu via PR vault #82 sur evidence implementation) a résolu un problème conceptuellement identique pour la page véhicule R8/R2. Schéma `__vehicle_page_cache` matérialisé, RPC `get_vehicle_page_data_cached` lookup PK O(1). État 2026-04-27 : **28 505 lignes matérialisées**, p99 mesuré conforme aux objectifs.

Le pattern est validé en production. ADR-024 applique la **même architecture** au cas symétrique R1.

## Décision

**Matérialiser les données de page R1 dans une table dénormalisée `__gamme_page_cache`, peuplée et rafraîchie en pipeline pilotée, et réécrire `get_gamme_page_data_optimized` en simple `SELECT WHERE pg_id = $1`.**

**Schéma identique à `__vehicle_page_cache` (parité ADR-016)** :

```sql
CREATE TABLE __gamme_page_cache (
  pg_id          INTEGER PRIMARY KEY,
  payload        JSONB NOT NULL,
  source_hash    TEXT NOT NULL,
  built_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  stale          BOOLEAN NOT NULL DEFAULT FALSE,
  stale_reason   TEXT
);
CREATE INDEX idx_gpc_stale ON __gamme_page_cache(stale) WHERE stale = TRUE;
```

Suppressions associées :
1. Les 4 requêtes séquentielles dans `buildRpcV2Response` (lignes 174, 195, 230, 617 de `gamme-response-builder.service.ts`)
2. Le filesystem RAG read dans `r1-related-resources.service.ts` durant SSR (le service devient seed-only offline)
3. La double couche de cache (`gamme:rpc-v2:` + `gamme:response:`) — une seule clé PK
4. Le controller-level response cache `RESPONSE_CACHE_PREFIX` dans `gamme-rest-rpc-v2.controller.ts:60-69`

## Options Considérées

### Option A : Matérialisation `__gamme_page_cache` (RETENUE)

Décrite ci-dessus. Parité exacte ADR-016.

**Avantages** :
- Lookup O(1) sur PK → **p99 < 50 ms garanti** (ADR-016 mesuré conforme à cet ordre de grandeur)
- Pattern symétrique avec ADR-016 (uniformité architecture, code review reusable)
- Supprime le RAG filesystem read du SSR (pré-calculé offline)
- Supprime les 4 requêtes séquentielles
- Cache warming devient trivial : populate la table au deploy / au backfill
- Taille estimée : 238 gammes × ~50 KB JSON ≈ **12 MB** (négligeable vs `__vehicle_page_cache` à ~1.5 GB)

**Inconvénients** :
- Fraîcheur = J+1 ou trigger-based. Acceptable : données R1 (image_prompts, buying_guide, related_blocks) sont éditoriales, pas temps réel.
- Coût initial : ~238 builds (1-3 s chacun = 4-12 min total, parallélisable)
- Maintenance `source_hash` pour invalidation ciblée

### Option B : Split critical/enrichment endpoint

**Description** : `/page-data-rpc-v2/critical` (RPC + meta only, < 300 ms) + `/page-data-rpc-v2/enrichment` (image_prompts + related + buying_guide). Frontend defer() l'enrichment.

**Avantages** :
- Pas de nouvelle table
- Streaming Suspense natif Remix

**Inconvénients** :
- Enrichment reste lent au cold-load (1-3 s, visible "loading state" below-fold)
- **Asymétrie avec ADR-016** vehicle page (incohérence architecture, dette gouvernance Q1.4 : précédent canon ignoré)
- Le RAG filesystem read reste dans le SSR enrichment path
- Garde la double couche de cache

### Option C : Mega-RPC `get_gamme_page_data_optimized` étendue à TOUT

**Description** : Étendre la fonction PostgreSQL pour qu'elle JOIN `__seo_r1_image_prompts` + `__seo_gamme_purchase_guide` + related blocks data en 1 query.

**Avantages** :
- 1 round-trip backend ↔ DB
- Pas de nouvelle table

**Inconvénients** :
- Le RAG filesystem read ne migre pas en SQL → reste dans le code applicatif
- Une fonction PostgreSQL géante (~300 lignes JOIN) difficile à maintenir
- Toujours 1-3 s au cold path (le travail SQL existe, juste regroupé)
- Cache invalidation : un changement sur n'importe quelle source → invalide tout pour tous les pg_id

### Option D : Statu quo ou warm response cache au deploy (BRICOLAGE — Q1 violation)

**Description** : Étendre `cache-warming.service.ts:warmGammePages` pour appeler le controller (pas le service), pré-payer le coût au boot.

**Avantages** :
- Zéro changement schéma

**Inconvénients** :
- Bricolage explicite : déplace la lenteur, ne la supprime pas (Q1 violation)
- Éviction Redis ou scale event = retour à 15 s
- Pas de garantie SLA, juste de l'espoir
- L'utilisateur a explicitement rejeté cette approche durant la discussion d'origine ("c'est du bricolage pas une solution robuste") — cette ADR existe précisément parce que cette option est insuffisante.

## Justification

**Option A retenue** pour 4 raisons (alignées sur les 4 questions de Q1) :

1. **Q1.1 cause racine** : la page R1 fait 4 requêtes séquentielles + filesystem read au request-time. Matérialiser remet le travail offline, le request-time devient un SELECT.
2. **Q1.2 invariant garanti** : lookup O(1) sur PK → p99 < 50 ms par construction, indépendant de la complexité d'enrichissement, indépendant de la chaleur du cache.
3. **Q1.3 dette nette** : SUPPRIME 4 requêtes séquentielles + 1 filesystem read + 1 couche de cache + ~900 lignes de `gamme-response-builder.service.ts` qui deviennent du code de transformation pure (~50 lignes).
4. **Q1.4 précédent** : ADR-016 (`accepted`, 28505 rows en prod, mesures conformes) **est** le précédent canon. Diverger sans raison forte = dette gouvernance.

Option B rejetée : asymétrie architecture (Q1.4 violation), n'élimine pas le RAG filesystem read, enrichment toujours lent. Option C rejetée : ne supprime pas le RAG filesystem read, fonction monolithique, gain perf marginal. Option D rejetée : bricolage explicite (Q1 violation), rejeté par l'owner.

## Conséquences

### Positives

- **p99 SSR R1 page < 100 ms** (cible, p99 < 50 ms si ADR-016 atteint cet ordre)
- **LCP < 2 s** sur cold-load Googlebot
- **0 timeout E2E Playwright** sur `/pieces/plaquettes-de-frein-1.html` (et autres gammes)
- Suppression de 4 requêtes séquentielles + 1 filesystem read + 1 couche de cache
- Architecture symétrique R1 ↔ R8 (uniformité, ADR-016 réutilisable)
- Budget gate `R1 Gamme Page < 3000 ms` deviendrait stable (actuellement seul R2 a un gate, et il est en warning continu)

### Négatives

- Fraîcheur J+1 (acceptable métier — content éditorial pas temps réel ; même propriété que ADR-016 sur TecDoc daily)
- 12 MB stockage supplémentaire (négligeable)
- Migration initiale ~10 min compute pour 238 gammes
- Nouvelle table à monitorer (cohérent avec `__vehicle_page_cache` déjà monitoré)

### Neutres

- Le contrat d'API frontend `/api/gamme-rest/:pgId/page-data-rpc-v2` est préservé (même JSON shape)
- Aucun changement frontend nécessaire (le loader continue d'appeler le même endpoint)

## Critères de Succès

- [ ] `get_gamme_page_data_optimized` p99 < 50 ms sur 7 jours consécutifs (mesure Supabase, parité avec __vehicle_page_cache)
- [ ] 0 timeout E2E Playwright sur `/pieces/plaquettes-de-frein-1.html` sur 14 jours
- [ ] R1 perf gate ajouté au CI : `<3000ms` sur top 5 gammes (parité avec gate R2 existant)
- [ ] `RESPONSE_CACHE_PREFIX` (controller-level) supprimé du code
- [ ] `r1-related-resources.service.ts` ne lit plus le RAG en SSR (utilise table de cache)
- [ ] `gamme-response-builder.service.ts` réduit de 948 → < 100 lignes (transformation pure post-RPC)
- [ ] Doc runbook `ops/runbooks/gamme-page-cache-rebuild.md` publiée (parité avec `vehicle-page-cache-rebuild.md`)

## Implémentation

### Phase 1 — Schéma et fonction de build (J+1 à J+2)

1. Migration : `CREATE TABLE __gamme_page_cache` (DDL ci-dessus, parité `__vehicle_page_cache`)
2. Fonction `build_gamme_page_payload(p_pg_id INTEGER) RETURNS JSONB` — extraction propre de `buildRpcV2Response` actuel, mais en pure SQL (CTE + JSON aggregation)
3. Fonction `rebuild_gamme_page_cache(p_pg_id)` qui appelle `build_gamme_page_payload` et UPSERT
4. Endpoint admin `POST /api/admin/gamme-cache/rebuild/:pg_id` (parité `admin-vehicle-cache.controller.ts`)

### Phase 2 — RAG → table (J+2 à J+3)

1. Migration : `CREATE TABLE __seo_r1_related_blocks_cache` (pg_id, blocks_json) — réplique des données calculées par `r1-related-resources.service.ts` aujourd'hui à chaque hit
2. Job de seed : `scripts/seo/seed-r1-related-blocks.ts` qui itère 238 gammes, lit le RAG, écrit dans la table
3. Trigger sur changement RAG (file watcher ou cron) → réécrit la ligne concernée

### Phase 3 — Backfill et activation (J+4)

1. Script `scripts/seo/backfill-gamme-page-cache.ts` : itère les 238 G1/G2, appelle `build_gamme_page_payload` en parallèle × 4
2. Réécriture de `get_gamme_page_data_optimized` :

   ```sql
   CREATE OR REPLACE FUNCTION get_gamme_page_data_optimized(p_pg_id INTEGER)
   RETURNS JSONB LANGUAGE sql STABLE AS $$
     SELECT payload
     FROM __gamme_page_cache
     WHERE pg_id = p_pg_id AND NOT stale
   $$;
   ```

3. Fallback : si stale ou absent, `build_gamme_page_payload` synchrone (one-shot, persiste). Pattern parité `get_vehicle_page_data_cached`.

### Phase 4 — Invalidation (J+5)

1. Trigger sur `__seo_gamme`, `__seo_r1_image_prompts`, `__seo_gamme_purchase_guide`, `__seo_gamme_links` :
   `UPDATE __gamme_page_cache SET stale=TRUE, stale_reason='source:<table>' WHERE pg_id = ...`
2. Cron Supabase : `SELECT rebuild_gamme_page_cache(pg_id) FROM __gamme_page_cache WHERE stale=TRUE LIMIT 50` toutes les 10 min
3. Trigger sur fichier RAG (cron file watcher ou hook éditorial) → invalide ligne concernée

### Phase 5 — Nettoyage bricolages (J+6)

1. Supprimer `RESPONSE_CACHE_PREFIX` et logique double-cache de `gamme-rest-rpc-v2.controller.ts`
2. Réduire `gamme-response-builder.service.ts` 948 → ~50 lignes (transformation pure post-RPC, plus de DB queries)
3. `r1-related-resources.service.ts` devient un service de seed (offline only), retiré du chemin SSR
4. Supprimer warming spécifique `warmGammePages` dans `cache-warming.service.ts` (le populate du backfill suffit)

### Phase 6 — Observation (J+6 à J+20)

1. Dashboard Supabase : p50/p95/p99 sur `get_gamme_page_data_optimized` par heure (parité observation ADR-016)
2. CI gate ajouté : `R1 Gamme Page < 3000ms` sur top 5 gammes (équivalent R2 existant)
3. J+14 : validation E2E Playwright stable sur 7 runs consécutifs
4. J+20 : promotion ADR à `accepted` avec evidence (suivant pattern PR vault #82 pour ADR-016)

**Fichiers concernés** :

- `backend/supabase/migrations/<date>_gamme_page_cache_schema.sql` (nouveau)
- `backend/supabase/migrations/<date>_build_gamme_page_payload.sql` (nouveau)
- `backend/supabase/migrations/<date>_seo_r1_related_blocks_cache.sql` (nouveau)
- `backend/supabase/migrations/<date>_get_gamme_page_data_optimized_rewrite.sql` (nouveau)
- `backend/supabase/migrations/<date>_gamme_page_cache_invalidation_triggers.sql` (nouveau)
- `backend/src/modules/gamme-rest/gamme-rest-rpc-v2.controller.ts` (simplification, -50 lignes)
- `backend/src/modules/gamme-rest/services/gamme-response-builder.service.ts` (refactor, 948 → ~50 lignes)
- `backend/src/modules/gamme-rest/services/r1-related-resources.service.ts` (devient seed-only)
- `backend/src/modules/admin/controllers/admin-gamme-cache.controller.ts` (nouveau, parité `admin-vehicle-cache.controller.ts`)
- `scripts/seo/backfill-gamme-page-cache.ts` (nouveau)
- `scripts/seo/seed-r1-related-blocks.ts` (nouveau)
- `.github/workflows/ci.yml` : ajout R1 perf gate
- `.spec/runbooks/gamme-page-cache-rebuild.md` → à publier dans vault `ops/runbooks/`

## Q-Rules trace

- **Q1** : 4-question test documenté en section Justification. Option A gagne sur tous les axes vs B/C/D.
- **Q2** : grep validé `frontend/app/routes/pieces.$slug.tsx`, `backend/src/modules/gamme-rest/`, `__seo_*` tables. Pas de duplication, étend pattern existant.
- **Q3** : `mcp__supabase__execute_sql` exécuté 2026-04-27 sur projet `cxpojprgwgubzjyqzmoq` :
  - `__gamme_page_cache` ABSENT (confirmé pas de duplication)
  - `__vehicle_page_cache` PRÉSENT, schéma capturé pour parité (incluant `stale_reason TEXT`)
  - 238 gammes G1/G2 actifs sur `pieces_gamme.pg_level IN ('1','2')`
  - 4 tables source (`__seo_gamme`, `__seo_r1_image_prompts`, `__seo_gamme_purchase_guide`, `__seo_gamme_links`) confirmées présentes
- **Q4** : déclencheurs identifiés — perf budget R2 dépassé continuellement (3122 ms vs 3000 ms), flake E2E récurrent, pattern dupliqué (`buildRpcV2Response` réimplémente ce que ADR-016 a centralisé), filesystem RAG read en SSR (anti-pattern). ADR-024 traite tous ces déclencheurs simultanément.

## Revue Planifiée

**Date** : 2026-05-25 (J+28 après déploiement prévu ~2026-04-30 à 2026-05-03)
**Critères de revue** :

- Si p99 > 50 ms après backfill, identifier si JSONB > 200 KB pour certaines gammes (élargir l'index ou partitioner par `pg_level`).
- Si triggers sur `__seo_*` dégradent les writes éditoriaux > 10%, passer à diff-based refresh batch.
- Si on étend cette pattern à R3/R4/R5/R6/R7, créer un meta-pattern ADR "page_cache" générique.
- Si 238 gammes G1/G2 grossit significativement (> 500), reconsidérer le coût backfill et la stratégie de partitioning.

## Liens

- Related : [[ADR-016-vehicle-page-matview-persistence]] (parité architecture, précédent canon)
- Related : [[ADR-017-rpc-pieces-cast-cleanup]] (autre optimisation RPC pieces_*, complémentaire)
- Related : [[rules-engineering-quality]] (Q1-Q4 appliquées en justification)
- Related rules : [[rules-technical]], [[rules-seo-pagerole]]

---

*Proposé le : 2026-04-27*
*Accepté le : (en attente de validation @automecanik.seo, suivi pattern PR vault #82)*
*Dernière revue : 2026-04-27*
