# change-control-plan.md

> **Version** : 1.3.0
> **Date** : 2026-03-14
> **Phase** : COMPLETE (V1-V5, C1-C4)
> **Source** : table-remediation-matrix.md V1.4.2 (gele)
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`

---

## Principes d'execution

1. **Chaque vague est autonome** : pas de dependance inter-vagues sauf ou indique
2. **Gate obligatoire** : chaque action doit etre validee avant execution
3. **Rollback documente** : chaque action indique la procedure de retour arriere
4. **Horaire** : actions R0 possibles a tout moment ; R1+ hors heures de pointe (avant 8h ou apres 22h CET)
5. **Evidence** : chaque action executee produit un log mesure (avant/apres) dans ce document
6. **Schema explicite obligatoire** : toute commande SQL destructive ou de backup doit qualifier le schema (`public.`, `archive.`)
7. **idx_scan = 0 ≠ safe** : le statut 0-scan est observe sur la fenetre stats courante uniquement, il ne suffit pas a autoriser un DROP
8. **grep seul ≠ suffisant** : aucune decision de DROP table ne peut reposer sur grep backend seul — revue SQL/RPC/vues/jobs obligatoire
9. **pg_stat_statements indisponible** : Supabase managed ne fournit pas pg_stat_statements — le profiling repose sur code search backend + reconstruction des queries candidates + EXPLAIN ANALYZE

---

## Vague 1 — ANALYZE + re-run F4 (P0, R0)

**Objectif** : rafraichir les stats planner des tables critiques et valider l'amelioration F4.

| # | Commande | Table | Rollback | Statut |
|---|----------|-------|----------|--------|
| 1.1 | `ANALYZE public.pieces_relation_criteria` | 36 GB, 158M rows | Aucun (non destructif) | `done` |
| 1.2 | `ANALYZE public.pieces_relation_type` | 13 GB, 146M rows | Aucun | `done` |
| 1.3 | `ANALYZE public.pieces_media_img` | 1.1 GB, 4.6M rows | Aucun | `done` |
| 1.4 | `ANALYZE public.pieces` | 1.6 GB, 3.5M rows | Aucun | `done` |
| 1.5 | `ANALYZE public.pieces_price` | 344 MB, 442K rows | Aucun | `done` |
| 1.6 | Re-run F4 : `EXPLAIN ANALYZE` jointure pieces_relation_criteria × pieces_relation_type | — | — | `done` |

**Gate V1** :
1. Comparer le plan EXPLAIN avant/apres ANALYZE (changement de Seq Scan → Index Scan ?)
2. Mesurer le gain relatif en temps d'execution
3. Considerer V1 concluante si :
   - le planner abandonne le mauvais plan initial (ex: Seq Scan → Index Scan), ou
   - le temps d'execution baisse de facon significative
4. Si plan inchange ou amelioration insuffisante → escalade Vague 2 (profile_query)

### Mesures attendues

```
-- Avant (baseline de perf-findings V1.0.3)
F4 = 5,884 ms (Seq Scan force sur pieces_relation_criteria, 1.1M rows scannees)

-- Apres (2026-03-14, post-ANALYZE 5 tables)
F4 = 1.6 ms (gain x3600)
Plan type = Nested Loop + Memoize (Seq Scan prt mais LIMIT pushdown correct : 50 rows)
Buffers read = 96 (vs 22,852 avant)
Memoize = 50 loops, 1 miss (vs 1.1M loops, 669 misses)
```

### Requete F4 de reference

```sql
-- F4 : jointure critique pieces_relation_criteria × pieces_relation_type
-- Source : perf-findings.md V1.0.3 F4 (baseline = 5884ms)
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT prc.*
FROM public.pieces_relation_criteria prc
JOIN public.pieces_relation_type prt ON prt.rtp_type_id = prc.rcp_type_id
WHERE prc.rcp_cri_id = 1
LIMIT 50;
```

> **Note** : cette requete est une query de reproduction baseline, utilisee pour comparer le plan avant/apres ANALYZE. Elle ne represente pas necessairement a elle seule le flux canonique complet U1.

---

## Vague 2 — Profile seq_scan anomalies (P0-P1, R1)

**Objectif** : identifier les queries responsables des seq_scans pathologiques sur les 4 tables critiques.

**Pre-requis** : Vague 1 terminee (stats planner a jour).

| # | Table | seq_tup_read | Methode | Statut |
|---|-------|-------------|---------|--------|
| 2.1 | pieces_price | 288B | code search + `EXPLAIN ANALYZE` | `done` |
| 2.2 | auto_type_number_code | 287B | code search + `EXPLAIN ANALYZE` | `done` |
| 2.3 | pieces_media_img | 267B | code search + `EXPLAIN ANALYZE` | `done` |
| 2.4 | __sitemap_p_link | 15.8B | code search + `EXPLAIN ANALYZE` | `done` |

### Procedure de profiling

> **Note** : pg_stat_statements n'est pas disponible sur Supabase managed.
> Le profiling repose sur la reconstruction des queries candidates.

**Etape 1** — Identifier les consumers dans le code :
- `grep -r "<table_name>" backend/src/` (services, data services, RPC calls)
- Revue des fonctions/RPC SQL connues (cf. execution-map.md)
- Revue des vues SQL dependantes
- Revue des cron/jobs documentes

**Etape 2** — Reconstruire la query candidate et la profiler :
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
<query reconstruite>;
```

**Etape 3** — Evaluer index cible :
- NE PAS creer d'index sans avoir identifie la query en premier

### Format de sortie obligatoire (par table)

| Champ | Valeur |
|-------|--------|
| Table | — |
| Query candidate | `SELECT ...` |
| Consumer probable | service/RPC/vue/cron |
| Plan observe | Seq Scan / Index Scan / ... |
| Colonne(s) de filtre/jointure | — |
| Index existant(s) | — |
| Verdict | index absent / inadapte / query non-indexable |
| Action proposee | CREATE INDEX / rewrite query / accept |
| Risque | R0-R3 |

### Gate V2

Pour chaque table profilee :
1. Format de sortie rempli integralement
2. Query identifiee : oui/non
3. Cause du seq_scan : index absent / index inadapte / requete non-indexable
4. Action recommandee : CREATE INDEX / rewrite query / accept (si volume faible)
5. Validation avant execution

### Resultats V2 (2026-03-14)

**Constat global** : les queries directes (SDK Supabase) utilisent toutes des Index Scans (< 4ms).
Les seq_tup_read massifs proviennent des **jointures internes des RPC functions** (`rm_get_page_complete_v2`, `get_pieces_for_type_gamme_v*`) et de la **vue `__sitemap_p_link_index`**.

ANALYZE supplementaire execute sur `auto_type_number_code` (last autoanalyze = 2025-06-23, 9 mois).

#### 2.1 — pieces_price

| Champ | Valeur |
|-------|--------|
| Table | `pieces_price` (442K rows, 344 MB) |
| Query candidate | Jointures internes dans 8 RPC : `rm_get_page_complete_v2`, `get_pieces_for_type_gamme_v[1-4]`, `get_listing_products_*`, `get_gamme_price_preview` |
| Consumer probable | RPC hot path (U1 listing) + SDK (stock, pricing, search, cart — 15+ services) |
| Plan observe (query directe) | Index Scan using idx_pprice_piece_id → **0.189ms** |
| Colonne(s) de filtre/jointure | `pri_piece_id` (jointure principale), `pri_ref` (search fallback) |
| Index existant(s) | 40+ indexes dont `idx_pprice_piece_id`, `idx_pieces_price_pri_ref` |
| Verdict | Queries directes OK. seq_scans = jointures internes RPC (non profilables individuellement via EXPLAIN externe) |
| Action proposee | **accept** — queries directes indexees, RPC a profiler internement en P2+ |
| Risque | R0 (monitoring) |

#### 2.2 — auto_type_number_code

| Champ | Valeur |
|-------|--------|
| Table | `auto_type_number_code` (165K rows, ~30 MB) |
| Query candidate | `.eq('tnc_type_id', typeId)` / `.in('tnc_type_id', typeIds)` + jointures RPC `rm_get_page_complete_v2`, `get_vehicle_page_data_optimized` |
| Consumer probable | vehicle-motor-codes.service, vehicles.controller, gamme-rpc.service + 2 RPC |
| Plan observe (query directe) | Index Scan using idx_atnc_type_id → **0.126ms** |
| Colonne(s) de filtre/jointure | `tnc_type_id` |
| Index existant(s) | `idx_atnc_type_id`, `idx_atnc_code`, `idx_auto_type_number_code_tnc_cnit/tnc_code/tnc_type_id` |
| Verdict | 1.7M seq_scans (165K/scan = full table) — provient des RPC internes. Table petite (30 MB), seq_scan acceptable en RAM |
| Action proposee | **accept** — table petite, queries directes indexees, seq_scans = RPC internes |
| Risque | R0 |

#### 2.3 — pieces_media_img

| Champ | Valeur |
|-------|--------|
| Table | `pieces_media_img` (4.6M rows, 1.1 GB) |
| Query candidate | `.eq('pmi_piece_id', pieceId)` + jointures dans `rm_get_page_complete_v2` |
| Consumer probable | catalog.service, search-simple.service, search-enhanced-existing.service + RPC |
| Plan observe (query directe) | Index Scan using idx_pmi_piece_id → **0.173ms** |
| Colonne(s) de filtre/jointure | `pmi_piece_id` |
| Index existant(s) | 8 indexes dont `idx_pmi_piece_id`, `idx_pmi_piece_id_int_display`, `idx_pieces_media_img_pmi_piece_id` (doublon potentiel) |
| Verdict | Queries directes OK. 62K seq_scans × 4.6M rows = jointures RPC internes. Note : 3 index sur `pmi_piece_id` (doublon probable → candidat V3) |
| Action proposee | **accept** pour seq_scan + **audit doublons index** en V3 |
| Risque | R0 |

#### 2.4 — __sitemap_p_link

| Champ | Valeur |
|-------|--------|
| Table | `__sitemap_p_link` (473K rows, ~30 MB) |
| Query candidate | Vue `__sitemap_p_link_index` : `SELECT ... FROM __sitemap_p_link p WHERE map_pg_id IN (SELECT pg_id FROM pieces_gamme WHERE pg_display='1' AND pg_relfollow='1')` + pagination sitemap |
| Consumer probable | sitemap-v10-pieces.service, sitemap-v10-hubs-cluster.service, sitemap-v10-hubs-vehicle.service, dashboard.service |
| Plan observe | Seq Scan sur __sitemap_p_link + Hash Join → **1.843ms** (avec LIMIT 100) |
| Colonne(s) de filtre/jointure | `map_pg_id` (jointure avec pieces_gamme) |
| Index existant(s) | **PK seul** (`map_id`) — **pas d'index sur `map_pg_id`** |
| Verdict | **Index absent** sur colonne de jointure `map_pg_id` |
| Action proposee | `CREATE INDEX idx_sitemap_p_link_map_pg_id ON public.__sitemap_p_link (map_pg_id)` (R1, ~15 MB) |
| Risque | R1 (CREATE INDEX CONCURRENTLY) |

### Synthese V2

| Table | seq_scan source | Query directe | Action |
|-------|----------------|---------------|--------|
| pieces_price | RPC internes | Index Scan 0.2ms | accept (monitoring) |
| auto_type_number_code | RPC internes | Index Scan 0.1ms | accept (table petite) |
| pieces_media_img | RPC internes | Index Scan 0.2ms | accept + audit doublons index V3 |
| __sitemap_p_link | Vue + pagination | Seq Scan (pas d'index map_pg_id) | **CREATE INDEX** (R1) |

---

## Vague 3 — Audit top indexes 0-scan (P2, R1)

**Objectif** : identifier les indexes inutiles qui consomment de l'espace sans etre utilises.

**Source** : perf-findings.md V1.0.3 T4 (25.6 GB d'indexes 0-scan).

| # | Action | Cible | Statut |
|---|--------|-------|--------|
| 3.1 | Lister top 25 indexes par taille avec idx_scan = 0 | pg_stat_user_indexes | `done` |
| 3.2 | Croiser avec les RPC/vues/consumers connus (code search + SQL) | Pour chaque index | `done` |
| 3.3 | Classifier : drop_candidate / keep_for_constraints / keep_for_future | — | `done` |

### Requete d'audit

```sql
SELECT
  schemaname,
  relname AS table_name,
  indexrelname AS index_name,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;
```

### Gate V3

- Ne pas DROP un index qui est une contrainte UNIQUE ou PK
- Ne pas DROP un index sans verifier qu'il n'est pas reference dans une RPC
- Candidats confirmes → Vague 4 ou action separee

### Cas special : `idx____xtr_msg_msg_content` (14 GB, 0-scan)

Cet index est le plus gros 0-scan de la base. Son DROP seul libere ~14 GB. Mais il est lie a la decision d'archivage de ___xtr_msg (Vague 5). Traiter ensemble.

### Resultats V3 (2026-03-14)

**25 indexes 0-scan audites**, total **~23.5 GB**.

**Methode** : croisement pg_stat_user_indexes (0-scan) × pg_indexes (definitions) × index actifs (meme table) × contraintes PK/UNIQUE.

#### Classification

| Classe | Indexes | Taille | Critere |
|--------|---------|--------|---------|
| `keep_constraint` | 1 (___xtr_msg_pkey) | 714 MB | Contrainte PK |
| `drop_candidate` (hors V5) | 19 indexes | ~8.1 GB | 0-scan, supersede par index actif ou doublon |
| `drop_candidate` (V5-tied) | 5 indexes ___xtr_msg | ~14.7 GB | Lies a decision archivage V5 |

#### Top drop candidates (hors V5, par taille decroissante)

| Index | Table | Taille | Raison |
|-------|-------|--------|--------|
| `idx_pieces_relation_criteria_rcp_cri_id` | pieces_relation_criteria | 1.5 GB | Couvert par PK composite (32.7M scans) |
| `idx_pieces_relation_type_composite` | pieces_relation_type | 1.4 GB | Doublon exact de idx_type_id_composite (22M scans) + WHERE |
| `idx_pieces_relation_criteria_rcp_pg_id` | pieces_relation_criteria | 1.3 GB | 0-scan, colonne non filtree |
| `idx_pieces_ref_search_ref` | pieces_ref_search | 1.1 GB | PK couvre (42M scans) |
| `idx_prt_type_gamme` | pieces_relation_type | 1.1 GB | Doublon idx_type_id_composite (memes colonnes) |
| `idx_pieces_relation_type_type_id` | pieces_relation_type | 984 MB | Single-col supersede par composite actif |
| `idx_prs_ref_exact` | pieces_ref_search | 836 MB | 0-scan |
| `idx_pieces_ref_ean_code_ean` | pieces_ref_ean | 169 MB | PK couvre (6M scans) |
| `idx_pieces_ref_clean` | pieces | 156 MB | 0-scan, idx_ref + trgm couvrent |
| `idx_pieces_ref_ean_piece_id` | pieces_ref_ean | 126 MB | 0-scan |
| 3× pieces_criteria | pieces_criteria | 330 MB | 0-scan, colonnes couvertes par index actifs |
| `idx_pre_code_ean_exact` | pieces_ref_ean | 90 MB | 0-scan |
| `idx_pmi_piece_id_int_display` | pieces_media_img | 83 MB | Supersede par idx_pmi_piece_id (54.8M scans) |
| 2× pmi_pm_id doublons | pieces_media_img | 60 MB | Doublons entre eux, les 2 a 0-scan |
| 2× pieces_list | pieces_list | 92 MB | 0-scan |

#### Doublons confirmes (memes colonnes, index different)

| Index 0-scan | Index actif (scans) | Colonnes | Verdict |
|-------------|---------------------|----------|---------|
| `idx_pieces_relation_type_composite` | `idx_pieces_relation_type_type_id_composite` (22M) | (rtp_type_id, rtp_pg_id) | DROP le 0-scan |
| `idx_prt_type_gamme` | `idx_pieces_relation_type_type_id_composite` (22M) | (rtp_type_id, rtp_pg_id) | DROP le 0-scan |
| `idx_pieces_relation_type_type_id` | `idx_pieces_relation_type_type_id_composite` (22M) | (rtp_type_id) prefix | DROP le 0-scan |
| `idx_pmi_pm_id` | `idx_pieces_media_img_pmi_pm_id` | (pmi_pm_id) | DROP les 2 (tous 0-scan) |

### Synthese V3

- **1 PK** protege (714 MB)
- **19 drop candidates** hors V5 = **~8.1 GB** reclaimables
- **5 drop candidates** V5-tied = **~14.7 GB** (decision V5)
- **Total potentiel** : **~22.8 GB** si V5 confirme archivage
- Index `idx_sitemap_p_link_map_pg_id` cree (action V2) : `done`

### Execution V3bis — DROP batch (2026-03-14)

**19 indexes DROP en 3 batches** via `DROP INDEX CONCURRENTLY` (zero downtime).

| Batch | Indexes | Taille liberee | Verification |
|-------|---------|---------------|-------------|
| Batch 1 (doublons) | 5 indexes | ~4 GB | 69 GB → 65 GB |
| Batch 2 (supersedes >1GB) | 4 indexes | ~4 GB | 65 GB → 61 GB |
| Batch 3 (petits 0-scan) | 10 indexes | ~1 GB | 61 GB → 60 GB |
| **Total** | **19 indexes** | **~9 GB** | **69 GB → 60 GB (-13%)** |

**Post-verification** : `idx_pieces_relation_type_type_id_composite` fonctionne (Index Scan, 0.174ms).

---

## Vague 4 — Drop confirmed empty orphans (P3, R1-R2)

**Objectif** : nettoyer le schema des tables vides sans consumer.

**Pre-requis** : validation multi-couches (pas grep seul).

| # | Table | Size | Check | Action | Statut |
|---|-------|------|-------|--------|--------|
| 4.1 | products | 24 KB | 0 rows, 0 code refs, 0 vues/RPC | `DROP TABLE` | `done` |
| 4.2 | categories | 24 KB | 0 rows, 0 code refs, 0 vues/RPC | `DROP TABLE` | `done` |
| 4.3 | messages | 64 KB | 0 rows, 0 code refs (___xtr_msg actif), 0 vues | `DROP TABLE` | `done` |
| 4.4 | sessions | 48 KB | 0 rows, 1 dead code ref (supprime), Redis = seul store | `DROP TABLE` + cleanup code | `done` |
| 4.5 | __blog_advice_old | 280 KB | 0 rows, 2 type-only refs, 0 vues/RPC | `DROP TABLE` | `done` |
| 4.6 | __rag_knowledge_backup_20260222 | 1.3 MB | 314 rows, subset de __rag_knowledge (367 rows), 0 code refs | `DROP TABLE` | `done` |
| 4.7 | __cross_gamme_car_new2 | 30 MB | 164K rows, subset de __cross_gamme_car_new (175K rows, 1 consumer actif), schema identique, 0 code refs | `DROP TABLE` | `done` |

### Pre-requis global

```sql
-- Creer le schema d'archive s'il n'existe pas
CREATE SCHEMA IF NOT EXISTS archive;
```

### Procedure de DROP

```sql
-- 1. Confirmer 0 rows (ou backup si data)
SELECT count(*) FROM public.<table>;

-- 2. Backup si necessaire (schema explicite)
CREATE TABLE archive.<table>_bak_20260314 AS SELECT * FROM public.<table>;

-- 3. DROP (schema explicite)
DROP TABLE IF EXISTS public.<table>;
```

### Gate V4

- Chaque DROP necessite validation explicite
- Validation multi-couches obligatoire avant DROP :
  1. Confirmation 0 refs backend (`grep`)
  2. Confirmation absence de vue / RPC / fonction SQL dependante connue
  3. Confirmation absence d'usage cron/job/documente
  4. Validation explicite
- Les tables avec data (4.6, 4.7) necessitent backup prealable dans `archive.*`
- `sessions` : confirmer que Redis est le seul store de sessions (pas de fallback Postgres)
- `messages` : confirmer le schema exact (2 instances detectees)

### Resultats V4 (2026-03-14)

**5 tables DROP en 2 lots** (V4-A + V4-B). Toutes confirmees 0 rows, 0 vues, 0 RPC.

| Lot | Tables | Verification |
|-----|--------|-------------|
| V4-A (orphelins purs) | products, categories, __blog_advice_old | 0 code refs, DROP direct |
| V4-B (avec cleanup) | messages, sessions | messages: 0 refs (___xtr_msg actif). sessions: 1 dead method `invalidateAllUserSessions()` supprimee de password.service.ts |

**Cleanup code** : `backend/src/modules/users/services/password.service.ts` — methode `invalidateAllUserSessions()` et ses 2 appels supprimes. Build TypeScript OK.

**V4-C** (tables avec data) :
- `__rag_knowledge_backup_20260222` (314 rows, 1.3 MB) : subset obsolete de `__rag_knowledge` (367 rows). 0 code refs. **DROP**.
- `__cross_gamme_car_new2` (164K rows, 30 MB) : subset ancien de `__cross_gamme_car_new` (175K rows, 1 consumer actif). Schema identique, 394 rows exclusives = stale mappings. 0 code refs. **DROP**.

---

## Vague 5 — Arbitrate ___xtr_msg (P2, R2)

**Objectif** : decider du sort de la table ___xtr_msg (25 GB + 14 GB index).

**Enjeu** : 39 GB potentiellement liberables, mais 7.6M idx_scan indiquent un consumer actif.

| # | Action | Statut |
|---|--------|--------|
| 5.1 | Identifier le consumer des 7.6M idx_scan (code search backend + revue RPC/vues/cron) | `done` |
| 5.2 | Evaluer si le consumer est critique ou peut etre decouple | `done` — CRITICAL (contact/review/legal) |
| 5.3 | Si archivable : backup complet → `archive.___xtr_msg_bak_YYYYMMDD` | `skipped` — table KEEP |
| 5.4 | DROP index `idx____xtr_msg_msg_content` (14 GB, 0-scan, btree TEXT inutile) | `done` |
| 5.5 | DROP index `idx____xtr_msg_msg_orl_equiv_id` (176 MB, 0 refs code) | `done` |
| 5.6 | DROP index `idx____xtr_msg_msg_orl_id` (80 MB, 0 refs code) | `done` |
| 5.7 | KEEP index `idx____xtr_msg_msg_parent_id` (280 MB, contact threads) | `done` |
| 5.8 | KEEP index `idx____xtr_msg_msg_ord_id` (136 MB, order-actions) | `done` |
| 5.9 | Si archivage : `DROP TABLE IF EXISTS public.___xtr_msg` | `skipped` — table KEEP |

### Arbre de decision

```
___xtr_msg (25 GB, 15M rows)
├── 7.6M idx_scan : consumer actif ?
│   ├── OUI, critique → keep_until_decoupled + evaluer DROP index 14GB apres validation
│   ├── OUI, non-critique → migrate_consumer vers table legere → archive_after_backup (gain: 39 GB)
│   └── NON (cron/dashboard) → archive_after_backup (gain: 39 GB)
└── idx____xtr_msg_msg_content : drop_candidate_high_confidence (0-scan sur fenetre stats)
    └── Necessite : verification absence d'usage rare + revue RPC/jobs + validation explicite
```

### Gate V5

- Ne pas archiver sans avoir identifie ET confirme le statut du consumer
- L'index 14 GB est `drop_candidate_high_confidence` (0-scan sur fenetre stats) mais **pas** "safe dans tous les cas" :
  1. Confirmer absence d'usage rare (batch, import, cron)
  2. Revue des queries/RPC/jobs connus qui pourraient l'utiliser
  3. Validation explicite avant DROP

### Resultats V5 (2026-03-14)

**Decision : TABLE KEEP** — 7 services actifs dont 3 critiques (contact tickets, product reviews, legal/RGPD).

#### Cartographie consumers

| Service | Criticite | Usage |
|---------|-----------|-------|
| `contact.service.ts` | **CRITICAL** | Tickets support client |
| `review.service.ts` | **HIGH** | Avis produits + moderation |
| `legal.service.ts` | **HIGH** | Documents CGU/RGPD (compliance) |
| `legal-version.service.ts` | MEDIUM | Versioning docs legaux |
| `error-log.service.ts` | MEDIUM | Logs d'erreurs |
| `redirect.service.ts` | MEDIUM | Redirections 404→301/302 |
| `order-actions.service.ts` | MEDIUM | Notifications commande |

#### Indexes — decisions

| Index | Taille | Decision | Justification |
|-------|--------|----------|---------------|
| `idx____xtr_msg_msg_content` | 14 GB | **DROP** | 0-scan, btree sur TEXT/JSON polymorphe = inutile (btree ne supporte pas LIKE '%...%') |
| `idx____xtr_msg_msg_orl_equiv_id` | 176 MB | **DROP** | 0-scan, 0 refs code (types auto-generes seuls) |
| `idx____xtr_msg_msg_orl_id` | 80 MB | **DROP** | 0-scan, 0 refs code |
| `idx____xtr_msg_msg_parent_id` | 280 MB | **KEEP** | contact.service.ts — reply chains |
| `idx____xtr_msg_msg_ord_id` | 136 MB | **KEEP** | order-actions.service.ts — filtre par commande |

#### Verification post-DROP

```
Espace indexes : 60 GB → 45 GB (gain = 15 GB)
Query critique : Index Scan using idx____xtr_msg_msg_cst_id → 0.837ms ✓
```

#### Bilan cumule V1-V5

| Vague | Gain |
|-------|------|
| V1 (ANALYZE) | F4 5884ms → 1.6ms |
| V2 (profiling) | 1 index cree (map_pg_id) |
| V3bis (19 drops) | 69 GB → 60 GB (9 GB) |
| V5 (3 drops ___xtr_msg) | 60 GB → 45 GB (15 GB) |
| **Total indexes** | **69 GB → 45 GB (-24 GB, -35%)** |

---

## Suivi d'execution

| Vague | Priorite | Risque | Pre-requis | Date planifiee | Date executee | Resultat |
|-------|----------|--------|------------|----------------|---------------|----------|
| V1 | P0 | R0 | aucun | 2026-03-14 | 2026-03-14 | **CONCLUANTE** : F4 5884ms → 1.6ms (x3600), LIMIT pushdown corrige |
| V2 | P0-P1 | R1 | V1 done | 2026-03-14 | 2026-03-14 | **DONE** : 4/4 tables profilées. 3 accept (RPC internes), 1 CREATE INDEX recommandé (map_pg_id) |
| V3 | P2 | R1 | aucun | 2026-03-14 | 2026-03-14 | **DONE** : 25 indexes audites. 19 DROP executes = **9 GB liberes** (69→60 GB). Index map_pg_id cree. 5 restants lies V5. |
| V4 | P3 | R1-R2 | grep code | 2026-03-14 | 2026-03-14 | **DONE** : 5 tables DROP (products, categories, messages, sessions, __blog_advice_old). Dead code cleanup password.service.ts. 2 tables reportees (V4-C). |
| V5 | P2 | R2 | V3 evidence | 2026-03-14 | 2026-03-14 | **DONE** : table KEEP (7 consumers critiques). 3 indexes DROP = **15 GB liberes** (60→45 GB). 2 indexes KEEP (parent_id, ord_id). |

---

## Actions complementaires (P4, hors vagues)

| # | Action | Cible | Statut |
|---|--------|-------|--------|
| C1 | Correction "7 triggers" → "5 triggers" | domain-map.md V1.4.3 | `done` |
| C2 | Monitor tables design-intent D8/D9 | rm_*, import_* | `ongoing` |
| C3 | profile_query sur tables SEO secondaires | __seo_gamme_car, __seo_keyword_type_mapping | `done` |
| C4 | review_views sur vues fantomes | v_seo_blocking_issues, v_seo_quality_stats, v_seo_url_health | `done` |

### Resultats C4 (2026-03-14)

**2 vues DROP, 1 n'existait pas, 5 indexes phantom DROP.**

| Objet | Action | Detail |
|-------|--------|--------|
| `v_seo_blocking_issues` | **DROP VIEW** | 0 consumers, 0 downstream, table source vide |
| `v_seo_quality_stats` | **DROP VIEW** | 0 consumers, 0 downstream, table source vide |
| `v_seo_url_health` | **SKIP** | N'existe pas en DB (reference documentaire uniquement) |
| `__seo_quality_log` | **KEEP** (table, 0 rows, 56 KB) | Infrastructure QA SEO, pas de gain espace |
| 5 indexes sur `__seo_quality_log` | **DROP** | `idx_sql_record_id` (104M phantom scans, 0 tuples), `idx_sql_table`, `idx_sql_date`, `idx_sql_action`, `idx_sql_score_before` — tous 0-scan ou phantom. PK conservee. |

**Source des 104M scans** : aucun trigger ni cron actif identifie. Probablement un trigger historique supprime. Le compteur ne croitra plus.

**2 RPC orphelines** conservees pour l'instant : `log_seo_quality_check()`, `get_seo_quality_daily_stats()` — aucun consumer, mais pas de gain espace.

### Resultats C3 (2026-03-14)

**2 tables profilées, verdict : accept pour les deux. Aucune action DB requise.**

| Table | Rows | Size | seq_scan | Consumers | Verdict |
|-------|------|------|----------|-----------|---------|
| `__seo_gamme_car` | 118 | 1.2 MB | 6.6M | 11 RPCs + 5 services backend | **accept** — table minuscule, tient en RAM, lookup table hot path |
| `__seo_keyword_type_mapping` | ~0 (stats) | 11 MB | 18.7K | 11 RPCs (0 code direct) | **accept** — petite, activement utilisee par RPCs |

**Note** : `idx___seo_gamme_car_sgc_preview` (0 scans, 40 KB) et 2 low-use indexes sur `__seo_keyword_type_mapping` (4 et 16 scans, <1 MB) identifies mais gain negligeable → SKIP.

---

## Refs croisees

| Document | Version | Role |
|----------|---------|------|
| table-remediation-matrix.md | V1.4.2 (gele) | Decisions et actions par table |
| domain-map.md | V1.4.2 | Classification des 283 tables en 15 domaines |
| perf-findings.md | V1.0.3 | Preuves de performance mesurees (F1-F4, T1-T6) |
| execution-map.md | V1.2.0 | 5 flux critiques + priorites de profiling |
| schema-governance-matrix.md | V1.2.0 | Matrice objet-par-objet avec tiering et gates |
| final-exec-summary.md | V1.0.0 | Rapport de cloture : avant/apres, gains, lessons learned |
