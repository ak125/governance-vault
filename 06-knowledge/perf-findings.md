# perf-findings.md

> **Version** : 1.0.3
> **Date** : 2026-03-14
> **Phase** : BASELINE_AUDIT
> **Complement de** : execution-map.md V1.2.0, schema-governance-matrix.md V1.2.0
> **Methode** : EXPLAIN ANALYZE read-only + pg_stat_* introspection
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`

---

## 1. Scope

**Perimetre** : priorites P1-P6 definies dans execution-map.md V1.2.0 (section "Priorites de profiling").

**Contrainte** : toutes les mesures sont **read-only**. Les profiling en ecriture (P3 write `__seo_gamme_purchase_guide`, P4 trigger cascade `__seo_keywords`) n'ont pas pu etre executes. Ils sont documentes en section 5 "Decisions non prises".

**Environnement** : Supabase PostgreSQL (managed), single-run EXPLAIN ANALYZE sans warm-up prealable. Les temps incluent potentiellement du cold-cache I/O.

**Flux de reference** (execution-map.md V1.2.0) :
- U1 : Listing produit (RPC `rm_get_page_complete_v2`)
- U2 : Recherche (table `pieces_ref_search`)
- U3 : Content-refresh pipeline (BullMQ)
- U4 : RAG ingestion
- U5 : Import (theorique, non materialise)

---

## 2. Methode de mesure

| Outil | Usage |
|-------|-------|
| `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` | Mesure du plan d'execution reel, buffer hits/reads |
| `pg_stat_user_tables` | seq_scan, idx_scan, dead tuples, last autovacuum |
| `pg_stat_user_indexes` | idx_scan count, taille index, detection 0-scan |
| `pg_trigger` + `pg_get_triggerdef()` | Inventaire triggers reels |

**Limites** :
- Single-run : pas de moyenne sur N executions
- Cold cache possible : les `read` dans BUFFERS peuvent etre gonfles par rapport a un run warm
- Pas de `pg_stat_statements` disponible (extension non activee sur Supabase managed)

---

## 3. Findings par requete

### F1 — rm_get_page_complete_v2 (U1 listing) — CRITIQUE

**Ou** : RPC `rm_get_page_complete_v2(82, 24259, 200)` — gamme "disque-de-frein", vehicule 24259
**Flux** : U1 (listing produit, hot path)
**Estimation execution-map** : ~400ms
**Mesure reelle** : **1080ms** (2.7x l'estimation)

**Preuve EXPLAIN ANALYZE** :
```
Execution Time: 1080.xxx ms
Buffers: shared hit=117239 read=150
```

**Constat** :
- 117K buffer hits indiquent une RPC qui touche un volume massif de donnees
- 150 reads supplementaires (I/O disque, potentiellement cold cache)
- Le ratio hits/reads est bon (cache efficace) mais le volume total est le probleme
- La RPC est un monolithe qui agrege plusieurs sous-requetes internes (pieces, criteres, relations, SEO)

**Gate** : action autorisee → profiling interne de la RPC (decomposer les sous-requetes) dans change-control-plan.md

---

### F2 — pieces_ref_search (U2 search, proxy query) — OK

**Ou** : `SELECT * FROM pieces_ref_search WHERE prs_search ILIKE '%disque frein%' LIMIT 20`
**Flux** : U2 (recherche utilisateur)
**Mesure** : **28ms**

> **Note** : cette requete est une **proxy query indicative** pour U2. Le flux reel U2 utilise des variants normalises (`prs_search IN (...)`) avec fallback sur `pieces_price`. Le finding valide le comportement de l'index sur un pattern ILIKE, mais ne constitue pas une mesure exacte du flux canonique U2.

**Preuve EXPLAIN ANALYZE** :
```
Index Scan using idx_pieces_ref_search_search on pieces_ref_search
Execution Time: 28.xxx ms
Buffers: shared hit=3 read=44
```

**Constat** :
- Index Scan confirme (pas de Seq Scan)
- 28ms acceptable pour une recherche ILIKE avec index
- 44 reads possiblement cold cache, probablement < 10ms en warm

**Gate** : pas d'action requise. Performance acceptable sur cette proxy query.

---

### F3 — pieces_relation_type (U1 listing) — OK

**Ou** : `SELECT * FROM pieces_relation_type WHERE rtp_type_id = X`
**Flux** : U1 (sous-requete de listing)
**Mesure** : **0.164ms**

**Preuve EXPLAIN ANALYZE** :
```
Index Scan using idx_pieces_relation_type_type_id_composite on pieces_relation_type
Execution Time: 0.164 ms
Buffers: shared hit=4
```

**Constat** :
- Index Scan confirme, pas de Seq Scan sur le hot path
- Les 463B seq_tup_read vus dans pg_stat_user_tables sont **cumulatifs** et proviennent de batch operations (import, maintenance), pas du flux U1
- Performance individuelle negligeable

> **Contre-preuve locale** : F3 ne contredit pas F4. Il valide uniquement qu'un acces cible indexe sur `rtp_type_id` est performant. Le probleme observe en F4 porte sur un plan de jointure specifique (Seq Scan force par stats obsoletes), pas sur toute lecture de `pieces_relation_type`.

**Gate** : pas d'action requise. Le signal pg_stat (463B seq_tup_read) ne justifie PAS d'alarme sur U1.

---

### F4 — pieces_relation_criteria JOIN (U1 listing) — CRITIQUE

**Ou** : `SELECT prc.* FROM pieces_relation_criteria prc JOIN pieces_relation_type prt ON prt.rtp_type_id = prc.rcp_type_id WHERE prc.rcp_cri_id = 1 LIMIT 50`
**Flux** : U1 (listing, sous-requete criteres)
**Mesure** : **5884ms**

**Preuve EXPLAIN ANALYZE** :
```
Limit  (cost=0.58..3.18 rows=50 width=45) (actual time=5880.587..5883.637 rows=50 loops=1)
  Buffers: shared hit=4290 read=22852
  ->  Nested Loop  (cost=0.58..9112162.22 rows=175399282 width=45) (actual time=5880.586..5883.629 rows=50 loops=1)
        Buffers: shared hit=4290 read=22852
        ->  Seq Scan on pieces_relation_type prt  (cost=0.00..2556467.00 rows=146371200 width=4) (actual time=0.039..235.278 rows=1120837 loops=1)
              Buffers: shared hit=1865 read=6447
        ->  Memoize  (cost=0.58..174.47 rows=1 width=45) (actual time=0.005..0.005 rows=0 loops=1120837)
              Cache Key: prt.rtp_type_id
              Cache Mode: logical
              Hits: 1120168  Misses: 669  Evictions: 0  Overflows: 0  Memory Usage: 45kB
              Buffers: shared hit=2425 read=16405
              ->  Index Scan using pk_pieces_relation_criteria on pieces_relation_criteria prc  (cost=0.57..174.46 rows=1 width=45) (actual time=7.905..7.910 rows=0 loops=669)
                    Index Cond: ((rcp_type_id = prt.rtp_type_id) AND (rcp_cri_id = 1))
                    Buffers: shared hit=2425 read=16405
Planning Time: 6.199 ms
Execution Time: 5883.997 ms
```

**Constat** :
- Le planner choisit un **Seq Scan sur pieces_relation_type** (estime 146M rows, reel 1.1M) → estimation x130, statistiques de table obsoletes
- Nested Loop avec Memoize : 1.1M iterations, 669 misses sur le cache
- 22K reads (I/O disque massif)
- `pieces_relation_criteria` = **36GB**, 158M live tuples
- `pieces_relation_type` = table plus petite mais scanee integralement
- Le LIMIT 50 n'aide pas car le Nested Loop doit scanner prt en entier avant de limiter
- **Cause probable** : statistiques obsoletes (last autoanalyze = 2025-09-18, 6 mois) + absence possible d'index plus adapte a ce pattern de jointure

**Gate** : action autorisee → `ANALYZE` immediat sur les deux tables pour corriger les stats du planner, puis re-run F4 pour mesurer l'amelioration. Investigation index composite en P2 dans change-control-plan.md. La decision `VACUUM (ANALYZE)` complet est une etape separee, justifiable par T1/T2 mais pas par F4 seul.

---

## 4. Findings transverses

### T1 — Vacuum staleness : pieces_relation_type

**Preuve pg_stat_user_tables** :
```
last_autovacuum:  2025-09-18 21:41:15
last_autoanalyze: 2025-09-18
n_dead_tup:       2,200,000
n_live_tup:       146,371,200
```

**Constat** : 6 mois sans autovacuum. 2.2M dead tuples non reclames. Les statistiques du planner sont obsoletes de 6 mois, ce qui explique directement l'estimation x130 en F4.

---

### T2 — Vacuum staleness : pieces_relation_criteria

**Preuve pg_stat_user_tables** :
```
last_autovacuum:  2025-09-18 21:41:15
last_autoanalyze: 2025-09-18 21:48:04
n_dead_tup:       0
n_live_tup:       157,858,492
total_size:       36 GB
```

**Constat** : 6 mois sans autovacuum. Meme si dead_tup = 0 actuellement, les statistiques du planner (158M tuples) n'ont pas ete rafraichies depuis 6 mois. Table de 36GB sans maintenance reguliere.

---

### T3 — Vacuum staleness : pieces_ref_search

**Preuve pg_stat_user_tables** :
```
last_autovacuum:  2025-09-06
n_dead_tup:       802,000
```

**Constat** : 6 mois sans autovacuum. 802K dead tuples non reclames. Impact moindre que T1/T2 car F2 montre une performance acceptable (28ms), mais le bloat s'accumule.

---

### T4 — Index 0-scan : ~25.6 GB de stockage gaspille

**Preuve pg_stat_user_indexes** (indexes avec idx_scan = 0) :

| Domaine | Nombre indexes 0-scan | Taille totale |
|---------|-----------------------|---------------|
| D2 (Legacy/XTR) | 168 | 16 GB |
| D1 (Catalog Core) | 118 | 9.4 GB |
| Autres | 771 | 231 MB |
| **Total** | **1057** | **~25.6 GB** |

**Top indexes 0-scan par taille** :
- `idx____xtr_msg_msg_content` : 14 GB (D2, table `__xtr_msg`)
- `idx_pieces_relation_criteria_rcp_cri_id` : 1.5 GB (D1, table `pieces_relation_criteria`)
- `idx_pieces_relation_type_composite` : 1.4 GB (D1, table `pieces_relation_type`)

**Constat** : 25.6 GB d'espace disque occupe par des indexes jamais utilises depuis le dernier reset des stats. Certains peuvent etre des indexes de maintenance/import (utilises rarement), d'autres sont des orphelins reels. Le statut `idx_scan = 0` est observe sur la **fenetre stats courante uniquement** (depuis le dernier `pg_stat_reset()` ou redemarrage) ; il ne suffit pas a lui seul a autoriser un DROP.

**Gate** : action autorisee → audit individuel des top 20 indexes 0-scan pour classification keep/drop dans change-control-plan.md. Aucun DROP sans verification des RPC/queries qui pourraient les utiliser.

---

### T5 — UNEXPLAINED_DB_ACTIVITY : __seo_quality_log

**Preuve** :
```
Table:     __seo_quality_log
Rows:      0 (table vide)
idx_scan:  104,000,000 (sur idx_sql_record_id, index 8KB)
tuples returned: 0
```

**Source identifiee** : 3 views referencent cette table :
- `v_seo_blocking_issues`
- `v_seo_quality_stats`
- `v_seo_url_health`

1 RPC ecrit : `log_seo_quality_check()`. Aucun trigger n'appelle cette RPC.

**Constat** : les 104M scans proviennent des views qui sont probablement interrogees par un dashboard ou un cron. Chaque scan retourne 0 tuples (table vide). C'est du travail inutile mais a cout negligeable (index 8KB).

**Gate** : action autorisee → review des 3 views pour determiner si elles sont encore utilisees. Si oui, peupler la table ou supprimer la reference. Si non, DROP candidates.

---

### T6 — Trigger count discrepancy : __seo_keywords

**Preuve pg_trigger** : 5 triggers reels sur `__seo_keywords` :

| # | Trigger | Event | Fonction |
|---|---------|-------|----------|
| 1 | `trg_seo_keywords_updated_at` | BEFORE UPDATE | `update_seo_keywords_updated_at()` |
| 2 | `trg_sync_keywords_aggregates` | AFTER INSERT/DELETE/UPDATE | `sync_keywords_to_gamme_aggregates()` |
| 3 | `trg_update_v2_repetitions_delete` | AFTER DELETE (WHERE type='vehicle') | `update_v2_repetitions_on_delete()` |
| 4 | `trg_update_v2_repetitions_insert` | AFTER INSERT/UPDATE OF v_level (WHERE type='vehicle') | `update_v2_repetitions_on_change()` |
| 5 | `trg_vlevel_integrity` | BEFORE INSERT/UPDATE | `validate_vlevel_integrity()` |

**Constat** : domain-map.md V1.4.2 mentionne "7 triggers en cascade". La realite mesuree au niveau DDL est **5 triggers definis**. Ecart de 2. La cascade effective depend du type d'operation :
- Un INSERT de type `text` declenche : #1 (non, BEFORE UPDATE only), #2 (oui), #5 (oui) = **2 triggers**
- Un INSERT de type `vehicle` declenche : #2 (oui), #4 (oui), #5 (oui) = **3 triggers**
- Un UPDATE de type `vehicle` sur `v_level` declenche : #1 (oui), #2 (oui), #4 (oui), #5 (oui) = **4 triggers**
- Un DELETE de type `vehicle` declenche : #2 (oui), #3 (oui) = **2 triggers**

Le nombre de triggers **definis** (5) et le nombre de triggers **effectivement declenches** par operation (2-4) sont deux mesures distinctes. P4 doit mesurer le temps reel de la cascade pour le pattern d'ecriture le plus frequent.

**Gate** : correction documentaire dans domain-map.md (prochaine version V1.4.3). Pas d'impact sur les decisions de profiling — P4 doit mesurer les 5 triggers definis sur le pattern d'ecriture reel.

---

## 5. Decisions non prises

| ID | Decision | Raison | Pre-requis |
|----|----------|--------|------------|
| D1 | Write profiling P3 (`__seo_gamme_purchase_guide`) | Necessite INSERT/UPDATE reel | Environnement de test ou write access |
| D2 | Trigger cascade timing P4 (`__seo_keywords`) | Necessite INSERT reel pour mesurer les 5 triggers en serie | Environnement de test ou write access |
| D3 | Confirmation F1 (1080ms) | Single-run, potentiellement cold cache | Second run apres warm-up |
| D4 | Profiling P7/P8 | Priorites basses, pas encore traitees | Apres resolution F1/F4 |
| D5 | Mesure impact vacuum sur F4 | F4 = 5884ms, probablement ameliorable par ANALYZE seul | Executer ANALYZE puis re-run F4 |

---

## 6. Export decisionnel → change-control-plan.md

Ce tableau liste les actions **autorisees** par les findings ci-dessus. Chaque action doit etre detaillee avec procedure, risque et rollback dans change-control-plan.md.

| Finding | Action autorisee | Priorite | Risk level |
|---------|-----------------|----------|------------|
| F1 (1080ms) | Profiling interne de la RPC : decomposer `rm_get_page_complete_v2` en sous-requetes mesurees individuellement | P1 | R1 (read-only, reversible) |
| F4 (5884ms) | `ANALYZE pieces_relation_type, pieces_relation_criteria` pour corriger les stats du planner, puis re-run F4 | P0 | R0 (maintenance standard) |
| F4 (5884ms) | Investigation index composite sur `pieces_relation_criteria(rcp_cri_id, rcp_type_id)` | P2 | R2 (index creation, reversible) |
| T1-T3 (vacuum) | Evaluer `VACUUM (ANALYZE)` sur les 3 tables apres l'ANALYZE initial, selon bloat / dead tuples / fenetre d'exploitation | P1 | R0 (maintenance standard) |
| T4 (25.6GB 0-scan) | Audit individuel des top 20 indexes 0-scan → classification keep/drop | P3 | R1 (read-only audit) |
| T5 (UNEXPLAINED_DB_ACTIVITY, 104M idx_scan) | Review des 3 views `v_seo_*` : usage reel, decision keep/drop | P3 | R1 (read-only investigation) |
| T6 (5 vs 7 triggers) | Correction documentaire domain-map.md V1.4.2 → V1.4.3 | P4 | R0 (documentation) |
| D5 (ANALYZE → F4) | Re-run F4 apres ANALYZE pour mesurer l'amelioration des stats du planner | P1 | R0 (read-only) |

**Actions NON autorisees par ce document** :
- DROP d'index sans audit individuel prealable (T4)
- DROP de views sans confirmation d'absence de consumers (T5)
- Modification de la RPC `rm_get_page_complete_v2` sans profiling prealable (F1)
- Modification de triggers sans mesure de cascade (T6/D2)

---

## Refs croisees

| Document | Version | Role |
|----------|---------|------|
| domain-map.md | V1.4.2 | Classification des 283 tables en 15 domaines |
| schema-governance-matrix.md | V1.2.0 | Matrice objet-par-objet avec tiering et gates |
| execution-map.md | V1.2.0 | 5 flux critiques + priorites de profiling P1-P8 |
| **perf-findings.md** | **V1.0.3** | **Ce document — preuves de performance mesurees** |
| change-control-plan.md | A creer | Procedures d'execution des actions autorisees |
| remediation-plan.md | A creer | Sequence de migrations + timeline |
