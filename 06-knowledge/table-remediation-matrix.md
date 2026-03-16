# table-remediation-matrix.md

> **Version** : 1.4.2
> **Date** : 2026-03-14
> **Phase** : RESOLUTION
> **Complement de** : domain-map.md V1.4.2, schema-governance-matrix.md V1.2.0, execution-map.md V1.2.0, perf-findings.md V1.0.3
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`

---

## 1. Methode & taxonomie

### Classification par probleme

| Code | Type | Description |
|------|------|-------------|
| A | `hot_path_latency` | Table sur le hot path avec latence mesuree critique |
| B | `seq_scan_anomaly` | Ratio seq_scan/row anormalement eleve |
| C | `stats_stale` | Statistiques du planner obsoletes (> 3 mois) |
| D | `index_bloat` | Indexes 0-scan ou surdimensionnes |
| E | `vacuum_stale` | Autovacuum > 3 mois, dead tuples accumules |
| F | `legacy_archive` | Table legacy avec activite residuelle |
| G | `app_orphan` | Table sans consumer applicatif identifie |
| H | `empty_design_intent` | Table vide par design, pas encore activee |

### Types d'actions

| Action | Description | Risk level |
|--------|-------------|------------|
| `keep` | Garder telle quelle, pas de probleme | R0 |
| `keep_active` | Garder, table active et saine | R0 |
| `keep_pending_confirmation` | Garder sous reserve de confirmation des consumers | R0 |
| `keep_until_decoupled` | Garder tant que le flux n'est pas decouple | R0 |
| `run_analyze` | Executer ANALYZE pour rafraichir stats planner | R0 |
| `evaluate_vacuum` | Evaluer si VACUUM (ANALYZE) necessaire | R0 |
| `profile_query` | Identifier les queries responsables du seq_scan | R1 |
| `review_indexes` | Auditer indexes existants, evaluer ajout/suppression | R1 |
| `monitor_only` | Garder + surveiller, pas d'action immediate | R0 |
| `evaluate_archive` | Evaluer si archivable apres confirmation des consumers actifs | R1 |
| `archive_after_backup` | Archiver apres sauvegarde, puis evaluer DROP | R2 |
| `drop_after_confirmation` | Confirmer 0 refs code puis DROP (table vide) | R1 |
| `drop_after_backup` | Sauvegarder puis DROP (table avec data) | R2 |
| `consolidate` | Fusionner avec une autre table | R3 |
| `migrate_consumer` | Modifier le code applicatif pour changer le pattern d'acces | R3 |
| `defer` | Reporter a une phase ulterieure | R0 |

---

## 2. Bloc 1 — Catalogue chaud (P0)

Tables du hot path U1/U2, responsables de la majorite du temps de reponse.

### Matrice

| Table | Domain | Size | Rows | Problem | Evidence | Action | Risk | Priority | Confidence |
|-------|--------|------|------|---------|----------|--------|------|----------|------------|
| pieces_relation_criteria | D1 | 36 GB | 158M | A,C,E | F4=5884ms, last_analyze=2025-09, Seq Scan force | `run_analyze` + `review_indexes` | R0→R2 | **P0** | high |
| pieces_relation_type | D1 | 13 GB | 146M | B,C,E | 463B seq_tup_read, 2.2M dead, last_vacuum=2025-09 | `run_analyze` + `evaluate_vacuum` | R0 | **P0** | high |
| pieces_price | D1 | 344 MB | 442K | **B** | **654K seq_scan, 288B seq_tup_read** — chaque row scannee ~651K fois | `profile_query` | R1 | **P0** | medium |
| pieces_media_img | D1 | 1.1 GB | 4.6M | B,C | 62K seq_scan, 267B seq_tup_read, last_analyze=2025-06 | `profile_query` + `run_analyze` | R1 | **P0** | high |
| pieces_ref_search | D1 | 18 GB | 73M | E | 802K dead tuples, last_vacuum=2025-09, F2=28ms OK | `evaluate_vacuum` | R0 | P1 | high |
| pieces | D1 | 1.6 GB | 3.5M | C | 13B idx_scan (tres chaud), last_analyze=2025-07 | `run_analyze` | R0 | P1 | high |
| pieces_criteria | D1 | 5.7 GB | 17.6M | B | 2.2B seq_tup_read, 1.9K seq_scan | `profile_query` | R1 | P1 | medium |
| pieces_gamme | D1 | 10 MB | 9.7K | B | 222M idx_scan, 2.3B seq_tup_read, 525K seq_scan | `profile_query` | R1 | P1 | medium |
| pieces_ref_ean | D1 | 897 MB | 3M | B | 9.9B seq_tup_read, 9K seq_scan | `profile_query` | R1 | P2 | medium |
| pieces_list | D1 | 394 MB | 1.8M | — | idx_scan = n_live_tup (1:1), sain | `keep_active` | R0 | — | high |

### Fiches detaillees (tables critiques)

#### pieces_price — ANOMALIE CRITIQUE

```
Taille:         344 MB | 442,173 rows
seq_scan:       654,873
seq_tup_read:   288,102,660,784 (288 milliards)
idx_scan:       50,329,327
last_autovacuum: 2025-07-02
last_autoanalyze: 2025-07-02
```

**Constat** : ratio seq_tup_read/row = **~651,000x**. C'est la table avec le pire ratio de seq scan de la base. Chaque seq_scan lit 442K rows a chaque fois — pattern de lecture pathologique, potentiellement lie a un index absent, inadapte, ou non utilisable par la requete.

**Consumers probables** : U1 listing (prix produit), U2 search fallback (`pieces_price`), possiblement sitemap.
**Blocking dependency** : aucune connue.
**Confidence** : medium (consumer exact non confirme).

**Action** :
1. `profile_query` : identifier les queries qui font du seq_scan sur cette table
2. Evaluer creation d'index cible apres identification de la requete
3. Re-run apres correction pour mesurer gain

**Gate** : ne PAS ajouter d'index sans avoir identifie les queries en premier.

---

#### pieces_media_img — SEQ SCAN MASSIF

```
Taille:         1.1 GB | 4,624,945 rows
seq_scan:       62,351
seq_tup_read:   266,846,612,901 (267 milliards)
idx_scan:       54,879,715
last_autovacuum: 2025-06-19
last_autoanalyze: 2025-06-19
```

**Constat** : 267B seq_tup_read sur 62K seq_scans = ~4.3M rows lues par scan. Stats planner obsoletes depuis 9 mois. La table est utilisee a la fois par idx_scan (55M) et seq_scan (62K) — le seq_scan est probablement un pattern de jointure non indexe.

**Blocking dependency** : aucune.
**Confidence** : high (stats age confirme, seq_scan mesure).

**Action** :
1. `run_analyze` immediat (stats de 9 mois)
2. `profile_query` pour identifier les 62K seq_scans
3. Evaluer index sur la colonne de jointure manquante

---

#### pieces_relation_criteria — RAPPEL F4

```
Taille:         36 GB | 157,858,492 rows
F4 mesuree:     5,884 ms (jointure avec pieces_relation_type)
last_autoanalyze: 2025-09-18
Cause:          Stats obsoletes → planner estime 146M rows au lieu de 1.1M
```

**Blocking dependency** : F4 doit etre re-run apres ANALYZE pour valider.
**Confidence** : high (F4 mesure directe, stats age confirme).

**Action** : `ANALYZE pieces_relation_criteria` immediat → re-run F4 → evaluer index composite `(rcp_cri_id, rcp_type_id)`.

---

## 3. Bloc 2 — Legacy XTR (P2)

Tables du systeme d'echange legacy. Activite residuelle mais pas sur le hot path.

| Table | Size | Rows | seq_scan | idx_scan | Action | Priority | Confidence |
|-------|------|------|----------|----------|--------|----------|------------|
| ___xtr_msg | **25 GB** | 15M | 2,666 | 7.6M | `evaluate_archive` | P2 | medium |
| ___xtr_customer | 34 MB | 59K | 3,774 | 202K | `keep_pending_confirmation` | — | medium |
| ___xtr_customer_billing_address | 29 MB | 59K | 214 | 26K | `keep_active` | — | high |
| ___xtr_customer_delivery_address | 29 MB | 59K | 89 | 22K | `keep_active` | — | high |
| ___xtr_order | 1.8 MB | 1.6K | 4,466 | 6.2K | `keep_until_decoupled` | — | medium |
| ___xtr_order_line | 2.6 MB | 2.5K | 123 | 19K | `keep_active` | — | high |
| ___xtr_invoice / invoice_line | 304 KB | 1 | ~100 seq | ~2 idx | `monitor_only` | P4 | high |
| ___xtr_delivery_agent | 176 KB | 1 | 102 | 1 | `monitor_only` | P4 | high |
| ___xtr_delivery_ape_* | ~120 KB | 7-9 | ~100 | ~550 | `keep_active` | — | high |
| ___xtr_order_status | 112 KB | 5 | 100 | 30K | `keep_active` | — | high |
| ___xtr_order_line_status | 112 KB | 10 | 98 | 12K | `keep_active` | — | high |
| ___xtr_supplier | 112 KB | 70 | 1,589 | 16 | `profile_query` | P3 | medium |

### Fiche ___xtr_msg — 25 GB

**Constat** : table la plus grosse apres pieces_relation_criteria. 15M rows de messages. 2.6K seq_scan avec 4.7B seq_tup_read. Index 0-scan `idx____xtr_msg_msg_content` pese 14 GB a lui seul.

**Action recommandee** :
1. Identifier si les 7.6M idx_scan viennent d'un flux actif ou d'un cron/dashboard
2. Si archivable : backup → table archive → DROP index 14GB → gain immediat ~14 GB
3. Si actif : `review_indexes` (l'index 14GB est 0-scan, donc inutile meme si la table reste)

**Gate** : ne pas archiver sans confirmer que le flux actif (7.6M idx_scan) n'est pas critique.

---

## 4. Bloc 3 — SEO / Sitemap (P1)

| Table | Size | Rows | Problem | Evidence | Action | Priority | Confidence |
|-------|------|------|---------|----------|--------|----------|------------|
| __seo_page | 114 MB | 322K | — | Sain, active | `keep_active` | — | high |
| __seo_gamme_conseil | 18 MB | 2.2K | — | Active, 491 dead | `keep_active` | — | high |
| __seo_keywords | 11 MB | 4.6K | T6 | 5 triggers (pas 7), active | `keep_active` + correction doc | P4 | high |
| __seo_keyword_type_mapping | 11 MB | 0 | `empty_but_runtime_active` | 0 rows mais 1.5M idx_scan | `profile_query` | P2 | medium |
| __seo_family_gamme_car_switch | 3 MB | 3.8K | — | 30M idx_scan, tres chaud | `keep_active` | — | high |
| __seo_item_switch | 2.7 MB | 8K | — | 23M idx_scan, tres chaud | `keep_active` | — | high |
| __seo_reference | 2.3 MB | 224 | — | Active | `keep_active` | — | high |
| __seo_gamme_purchase_guide | 2 MB | 221 | — | Source of truth SEO | `keep_active` | — | high |
| __seo_gamme_car_switch | 1.7 MB | 6.5K | B | 3M seq_scan, 65M idx_scan | `profile_query` | P2 | medium |
| __seo_gamme_car | 1.2 MB | 118 | B | 6.6M seq_scan, 266K idx_scan | `profile_query` | P2 | medium |
| __seo_quality_log | 56 KB | 0 | T5 | 104M idx_scan, 0 rows | `review_views` | P3 | medium |
| __sitemap_p_link | 89 MB | 473K | B | 59K seq_scan, 15.8B seq_tup_read | `profile_query` | P1 | medium |

### Tables SEO a profiler

**__seo_keyword_type_mapping** : 0 rows mais 1.5M idx_scan. Table vide consultee massivement. Similaire a T5 (__seo_quality_log). Identifier le consumer.

**__seo_gamme_car** : 118 rows mais 6.6M seq_scan. Ratio astronomique. Probablement une jointure dans la RPC listing qui scanne cette table integralement a chaque appel.

**__sitemap_p_link** : 473K rows, 15.8B seq_tup_read. Le sitemap generator fait probablement un full scan a chaque generation.

---

## 5. Bloc 4 — Orphelins / drop candidates (P3)

| Table | Size | Rows | Evidence | Action | Gate |
|-------|------|------|----------|--------|------|
| products | 24 KB | 0 | 48 seq, 6 idx, jamais vacuum | `drop_after_confirmation` | Confirmer 0 refs code |
| categories | 24 KB | 0 | 36 seq, 2 idx, jamais vacuum | `drop_after_confirmation` | Confirmer 0 refs code |
| messages | 64 KB | 0 | 14 seq, 0 idx, 2 instances (schemas?) | `drop_after_confirmation` | Confirmer schema |
| sessions | 48 KB | 0 | ~50 seq, 0 idx, 2 instances | `drop_after_confirmation` | Confirmer non utilise par Redis |
| __blog_advice_old | 280 KB | 0 live | 15 dead, rename suffixe _old | `drop_after_confirmation` | Confirmer migration terminee |
| __rag_knowledge_backup_20260222 | 1.3 MB | 314 | 0 scan, backup date | `drop_after_backup` | Verifier si backup existe ailleurs |
| __cross_gamme_car_new2 | 30 MB | 165K | 90 seq, 14 idx, doublon _new? | `compare_then_decide` | Comparer schema + data avec __cross_gamme_car_new avant toute action |

**Note** : aucun DROP ne doit etre execute sans verification prealable des refs dans le code (`grep` sur le nom de table dans le backend).

---

## 6. Bloc 5 — Hors priorite immediate (P4)

Tables qui ne necessitent pas d'action immediate. Separees en 3 sous-categories.

### 6a. Design-intent (vide ou partiellement materialise)

Tables creees pour des fonctionnalites non encore activees ou en cours d'activation. Ne pas toucher.

| Domaine | Tables | Statut | Action |
|---------|--------|--------|--------|
| D8 (RM) | rm_data_version, rm_listing, rm_facets, rm_listing_products_*, rm_product | partial | `monitor_only` |
| D9 (Import) | Non materialise (U5 theorique) | empty | `defer` |

### 6b. Small active non-critical

Tables actives, petit volume, pas de probleme de performance.

| Domaine | Tables | Action |
|---------|--------|--------|
| D1 (Catalog) | pieces_details (1 row), pieces_ref_oem (1 row) | `monitor_only` |
| D6 (RAG/AI) | __rag_knowledge | `keep_active` (actif via pipeline RAG) |
| D10 (Agentique) | __agentic_* (runs, branches, steps, evidence, checkpoints, gate_results) | `keep_active` |
| D12 (Marketing) | Petit volume, actif | `keep_active` |
| D15 (Security) | RPC Gate, governance | `keep_active` |

### 6c. App orphan low-priority

Tables identifiees comme orphelines mais a faible impact. Voir Bloc 4 pour les candidats DROP confirmes.

---

## 7. Bloc 6 — Lookup tables chaudes (P1)

Petites tables avec des ratios seq_scan anormaux — probablement des jointures sans index.

| Table | Domain | Size | Rows | seq_scan | seq_tup_read | idx_scan | Action | Priority | Confidence |
|-------|--------|------|------|----------|-------------|----------|--------|----------|------------|
| auto_type_number_code | D4 | 37 MB | 165K | **1.7M** | **287B** | 264K | `profile_query` | **P0** | medium |
| auto_modele | D4 | 1.1 MB | 5.7K | **1.2M** | **4.4B** | 53M | `profile_query` | P1 | medium |
| pieces_ref_brand | D1 | 1.4 MB | 5.8K | **4.2M** | **4.4B** | 621K | `profile_query` | P1 | medium |
| pieces_gamme | D1 | 10 MB | 9.7K | 525K | 2.3B | 222M | `profile_query` | P1 | medium |

> (*) `objects` (D2, 2.3 GB, 2.8M rows) : table non cartographiee dans domain-map, classee D2 par convention de prefixe. Action : `keep_active`. Statut : `out_of_baseline_scope`. Verifier les consumers avant toute action.

### Fiche auto_type_number_code — ANOMALIE CRITIQUE

```
Taille:         37 MB | 165,082 rows
seq_scan:       1,738,025
seq_tup_read:   286,890,490,731 (287 milliards)
idx_scan:       264,072
```

**Constat** : 287B seq_tup_read sur 1.7M seq_scans = ~165K rows lues a chaque scan (full table scan a chaque appel). Le ratio seq_scan >> idx_scan indique que la majorite des acces passent par un seq_scan. Le pattern suggere qu'un index manque, est mal cible, ou n'est pas exploitable dans les requetes actuelles.

**Blocking dependency** : aucune.
**Confidence** : medium (consumer exact non confirme).

**Action** :
1. Identifier les queries (probablement dans `rm_get_page_complete_v2` ou un flux vehicule)
2. Evaluer creation d'index cible apres identification de la requete
3. Gain attendu : elimination de 287B seq_tup_read

---

## 8. Plan d'action consolide

### P0 — Immediat (maintenance + profiling critique)

| # | Action | Tables | Risque | Gain attendu |
|---|--------|--------|--------|-------------|
| 1 | `ANALYZE` | pieces_relation_criteria, pieces_relation_type, pieces_media_img | R0 | Stats planner a jour, plan F4 corrige |
| 2 | `profile_query` | pieces_price (288B seq_tup_read) | R1 | Identifier la cause du pire seq_scan de la base |
| 3 | `profile_query` | auto_type_number_code (287B seq_tup_read) | R1 | Identifier requete responsable, evaluer index cible |
| 4 | Re-run F4 | pieces_relation_criteria JOIN | R0 | Confirmer amelioration apres ANALYZE |

### P1 — Court terme (profiling + vacuum)

| # | Action | Tables | Risque | Gain attendu |
|---|--------|--------|--------|-------------|
| 5 | `evaluate_vacuum` | pieces_relation_type (2.2M dead), pieces_ref_search (802K dead) | R0 | Reclamer dead tuples, reduire bloat |
| 6 | `profile_query` | pieces_media_img, pieces_gamme, auto_modele, pieces_ref_brand | R1 | Comprendre les patterns seq_scan |
| 7 | `profile_query` | __sitemap_p_link, __seo_gamme_car, __seo_gamme_car_switch | R1 | Optimiser le sitemap generator |
| 8 | `run_analyze` | pieces (last_analyze=2025-07), pieces_price | R0 | Rafraichir stats planner |

### P2 — Moyen terme (archivage + investigation)

| # | Action | Tables | Risque | Gain attendu |
|---|--------|--------|--------|-------------|
| 9 | `evaluate_archive` | ___xtr_msg (25 GB) | R1 | Confirmer consumers, puis evaluer archivage (~25 GB dont 14 GB index 0-scan) |
| 10 | `review_indexes` | Top 20 indexes 0-scan (25.6 GB total) | R1 | Identifier DROP candidates |
| 11 | `profile_query` | __seo_keyword_type_mapping (0 rows, 1.5M idx_scan) | R1 | Comprendre consumer fantome |

### P3 — Nettoyage (DROP candidates)

| # | Action | Tables | Risque | Gain attendu |
|---|--------|--------|--------|-------------|
| 12 | `drop_after_confirmation` | products, categories, messages, sessions, __blog_advice_old | R1 | Nettoyage schema (tables vides) |
| 13 | `drop_after_backup` | __rag_knowledge_backup_20260222 | R2 | Nettoyage legacy (table avec data) |
| 14 | `compare_then_decide` | __cross_gamme_car_new2 (doublon?) | R2 | 30 MB + clarte schema |
| 15 | `review_views` | v_seo_blocking_issues, v_seo_quality_stats, v_seo_url_health | R1 | Eliminer 104M scans inutiles |

### P4 — Maintenance documentaire

| # | Action | Cible | Risque |
|---|--------|-------|--------|
| 16 | Correction "7 triggers" → "5 triggers" | domain-map.md V1.4.3 | R0 |
| 17 | Monitor tables design-intent | D8, D9 | R0 |
| 18 | Monitor small active operational | D10 | R0 |

---

## 9. Actions NON autorisees

- DROP d'index sans audit individuel prealable (T4 de perf-findings)
- DROP de table sans `grep` dans le code backend pour confirmer 0 refs
- Modification de RPC sans profiling prealable
- Ajout d'index sans avoir identifie la query cible
- Archivage de ___xtr_msg sans confirmer que les 7.6M idx_scan ne sont pas critiques
- VACUUM sur des tables de production pendant les heures de pointe

---

## Refs croisees

| Document | Version | Role |
|----------|---------|------|
| domain-map.md | V1.4.2 | Classification des 283 tables en 15 domaines |
| schema-governance-matrix.md | V1.2.0 | Matrice objet-par-objet avec tiering et gates |
| execution-map.md | V1.2.0 | 5 flux critiques + priorites de profiling P1-P8 |
| perf-findings.md | V1.0.3 | Preuves de performance mesurees (F1-F4, T1-T6) |
| **table-remediation-matrix.md** | **V1.4.2** | **Ce document — decisions et actions par table** |
