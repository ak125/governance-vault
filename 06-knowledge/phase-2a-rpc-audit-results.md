# Phase 2A — RPC Hot Path Audit Results

> **Date** : 2026-03-14
> **Version** : 1.0.0
> **Parametres de test** : gamme_id=82 (disques frein), vehicle_id=30971
> **Methode** : EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) sur chaque sous-requete

---

## Resume des findings

| Sous-requete | Table | Execution | Plan | Verdict |
|-------------|-------|-----------|------|---------|
| SUB-Q1: relations | pieces_relation_type | **2 ms** | Index Scan | OK |
| SUB-Q2: best_prices | pieces_price | **174 ms** | **Seq Scan 442K rows** | PROBLEME |
| SUB-Q3: first_images | pieces_media_img | **277 ms** | Nested Loop (867 loops) | MOYEN |
| SUB-Q4: relation_criteria | pieces_relation_criteria | **43 ms** | Index Scan + filter | OK |
| SUB-Q5: number_codes | auto_type_number_code | **20 ms** | **Parallel Seq Scan** | PROBLEME |
| SUB-Q6: criteria_positions | pieces_criteria | **907 ms** | **Bitmap Scan 1.35M rows** | CRITIQUE |

**Total estime (somme sous-requetes)** : ~1,423 ms
**Bottlenecks** : SUB-Q6 (64%), SUB-Q3 (19%), SUB-Q2 (12%)

---

## Analyse detaillee

### SUB-Q6 — pieces_criteria positions (907 ms) — CRITIQUE

**Probleme** : La requete scanne 1,349,243 rows de `pieces_criteria` (WHERE `pc_cri_id = '100'`) puis fait un Hash Join avec les 867 pieces du vehicule. Seulement 403 rows sont retournees.

**Plan observe** :
```
Hash Join (906 ms)
  -> Bitmap Heap Scan on pieces_criteria (702 ms) — 1,349,243 rows scannees
     -> Bitmap Index Scan idx_pieces_criteria_cri_id — 1,349,243 rows
  -> Hash (relations) — 867 rows
```

**Cause racine** : L'index `idx_pieces_criteria_cri_id` est sur `(pc_cri_id)` seul. Le filtre `pc_cri_id = '100'` retourne 1.35M rows (7.6% de la table). Le planner ne peut pas filtrer par `pc_piece_id` efficacement car les colonnes sont TEXT et le JOIN est sur `::INTEGER`.

**Index manquant** : Un index composite `(pc_cri_id, pc_piece_id)` permettrait un Index Only Scan filtre. Mieux : un index expression `((pc_piece_id)::INTEGER, pc_cri_id)` pour matcher le pattern du JOIN.

**Optimisation proposee** :
```sql
CREATE INDEX CONCURRENTLY idx_pieces_criteria_cri100_piece
  ON pieces_criteria (pc_cri_id, pc_piece_id)
  WHERE pc_cri_id = '100';
```

**Gain attendu** : 907 ms -> ~5-10 ms (Index Scan direct au lieu de Bitmap Scan 1.35M rows)

**Risque** : R1 (faible) — index partiel, pas d'impact ecriture significatif

---

### SUB-Q2 — pieces_price best_prices (174 ms) — PROBLEME

**Probleme** : Seq Scan complet sur 442,173 rows de `pieces_price` malgre l'existence de 4 index sur `pri_piece_id`.

**Plan observe** :
```
Hash Join (174 ms)
  -> Seq Scan on pieces_price (76 ms) — 442,173 rows scannees
  -> Hash (relations) — 867 rows
```

**Cause racine** : L'index expression `idx_pieces_price_piece_id_int_expr` existe sur `((NULLIF(pri_piece_id, '')::INTEGER))` MAIS il a un filtre partiel : `WHERE (pri_dispo = ANY (ARRAY['1','2','3']))`. La RPC ne filtre PAS par `pri_dispo` dans la clause WHERE, donc l'index partiel ne couvre pas toutes les lignes.

Les index `idx_pprice_piece_id` et `idx_pieces_price_pri_piece_id` sont sur `pri_piece_id` (TEXT), mais la jointure fait `NULLIF(pri_piece_id, '')::INTEGER = rtp_piece_id` — le cast `::INTEGER` invalide l'index TEXT.

**Index manquant** : Un index expression sans filtre partiel :
```sql
CREATE INDEX CONCURRENTLY idx_pieces_price_piece_id_int
  ON pieces_price (((NULLIF(pri_piece_id, ''::text))::integer));
```

**Gain attendu** : 174 ms -> ~5-10 ms (Index Scan au lieu de Seq Scan 442K rows)

**Risque** : R1 (faible) — ~15 MB d'espace index supplementaire

---

### SUB-Q3 — pieces_media_img first_images (277 ms) — MOYEN

**Plan observe** :
```
Nested Loop (275 ms)
  -> Unique (relations) — 867 rows
  -> Index Scan idx_pmi_piece_id — 2 rows/loop, 867 loops
     Buffers: shared hit=2804 read=552
```

**Analyse** : Le plan est correct (Index Scan nested loop). Le cout vient du nombre de loops (867) avec des I/O (552 reads). Ceci est attendu pour une table de 1.1 GB avec des donnees dispersees sur disque.

**Optimisation possible** : Pre-fetching via CTE materialize, ou index couvrant `(pmi_piece_id, pmi_display, pmi_sort) INCLUDE (pmi_folder, pmi_name)`. Gain marginal car les buffers sont deja majoritairement en cache (2804 hits vs 552 reads).

**Recommandation** : Pas d'action immediate. Surveiller si le ratio hit/read se degrade.

---

### SUB-Q5 — auto_type_number_code (20 ms) — PROBLEME MINEUR

**Probleme** : Parallel Seq Scan sur 165K rows malgre l'existence de 2 index sur `tnc_type_id`.

**Cause racine** : La colonne `tnc_type_id` est de type TEXT. La RPC fait `WHERE tnc_type_id::INTEGER = 30971`. Le cast `::INTEGER` invalide l'index btree(tnc_type_id TEXT).

**Note** : La PK composite `(tnc_type_id, tnc_cnit)` existe et couvre `tnc_type_id`, mais le cast empeche son utilisation.

**Optimisation** : Modifier la RPC pour comparer en TEXT : `WHERE tnc_type_id = '30971'` (ou `p_vehicle_id::TEXT`).

**Gain attendu** : 20 ms -> ~1 ms

**Risque** : R0 (nul) — changement de comparaison seulement

---

### SUB-Q1 — relations (2 ms) — OK

Index Scan parfait via `idx_pieces_relation_type_type_id_composite`. Pas d'action.

### SUB-Q4 — relation_criteria (43 ms) — OK

Index Scan via `idx_pieces_relation_criteria_rcp_type_id` avec filtre post-scan. 13,945 rows filtrees sur 15,685 scannees. Acceptable pour une table de 36 GB.

---

## Plan d'action — Resultats mesures

| # | Action | Table | Avant | Apres | Gain | Statut |
|---|--------|-------|-------|-------|------|--------|
| A1 | Index expression `((pc_piece_id)::int) WHERE pc_cri_id='100'` + refactorer `IN()` en `LATERAL` dans les RPCs | pieces_criteria | 907 ms | **6 ms** | **x145** | APPLIQUE |
| A2 | Index expression `((NULLIF(pri_piece_id,'')::int))` sans filtre partiel | pieces_price | 174 ms | **4 ms** | **x43** | APPLIQUE |
| A3 | Modifier comparaison `tnc_type_id::INTEGER` -> `tnc_type_id = p_vehicle_id::TEXT` dans les RPCs | auto_type_number_code | 20 ms | ~1 ms | x20 | APPLIQUE |
| A4 | Surveiller pieces_media_img buffer miss ratio | pieces_media_img | 277 ms | - | - | SURVEILLER |

**Indexes crees** :
- `idx_pieces_criteria_cri100_piece_int` — `((pc_piece_id)::integer) WHERE pc_cri_id='100' AND pc_cri_value IS NOT NULL AND pc_cri_value != ''`
- `idx_pieces_price_piece_id_int_full` — `((NULLIF(pri_piece_id, '')::integer))`

**Index supprime (inutile)** : `idx_pieces_criteria_cri100_piece` (TEXT, non utilise par le planner avec le cast INTEGER)

**Note A1** : L'index seul ne suffit pas. Le planner choisit un Merge Join (scan 1.35M rows) avec le pattern `IN (subquery)`. Le pattern `LEFT JOIN LATERAL ... LIMIT 1` force un Nested Loop optimal (867 lookups index, 6 ms). Les RPCs ont ete refactorees pour utiliser LATERAL au lieu de IN.

**RPCs modifiees (2026-03-14)** :
- `rm_get_page_complete_v2` : LATERAL join + TEXT comparison (A1+A3)
- `get_pieces_for_type_gamme_v3` : LATERAL join (A1)

**Impact cumule A1+A2+A3 (mesure)** : ~1,423 ms -> **68 ms** warm cache par appel RPC (**x21**)

---

## Notes

1. Les indexes doivent etre crees avec `CREATE INDEX CONCURRENTLY` pour eviter le blocage en production.
2. Apres creation, executer `ANALYZE` sur les tables concernees.
3. Les deux RPCs (rm_get_page_complete_v2, get_pieces_for_type_gamme_v3) ont ete modifiees pour utiliser LATERAL + TEXT comparison.
4. Les anciennes CTEs `criteria_positions` sont devenues dead code (optimisees away par PG15).
5. Les index doublons `idx_pprice_piece_id` et `idx_pieces_price_pri_piece_id` (meme colonne, meme index) pourraient etre consolides.
