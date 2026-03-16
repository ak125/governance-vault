# Schema Governance Matrix — massdoc DB

> **Matrice de gouvernance objet par objet — evidence code search**
> **Version**: 1.2.0 | **Status**: BASELINE_AUDIT | **Date**: 2026-03-14
> **Complement de**: domain-map.md V1.4.2

---

## Legende

### Decision status (set ferme)

| Status | Signification |
|--------|---------------|
| `protected` | Aucune modification sans evidence complete |
| `stabilize` | Corrections mineures possibles sous gate |
| `profile` | Profiling requis avant decision |
| `review` | Evaluation structuree en cours |
| `observe_activation` | Design present, activation a confirmer |
| `archive_review` | Candidat archivage, validation legale requise |

### Object status (tables non-hot-path)

| Status | Signification |
|--------|---------------|
| `APP_ORPHAN_CONFIRMED` | 0 refs code backend. Retention policy et usages hors-app non verifies |
| `UNEXPLAINED_DB_ACTIVITY` | 0 refs code mais activite DB anormale. Investigation requise |
| `ORPHAN` | Donnees presentes, 0 consumer applicatif |
| `EMPTY_ACTIVE_DESIGN` | Schema en place, activation non confirmee. Ne pas supprimer |
| `EMPTY_STAGING` | Usage test/validation uniquement |

### Evidence status

| Status | Signification |
|--------|---------------|
| `confirmed` | Code search execute, consumers identifies |
| `partial` | Certains consumers identifies, investigation incomplete |
| `pending` | Aucun code search execute |

### Change risk

| Niveau | Signification |
|--------|---------------|
| R0 | Reversible, 0 impact — DROP INDEX CONCURRENTLY |
| R1 | Reversible, impact mesurable — test en preprod requis |
| R2 | Semi-reversible — shadow path recommande |
| R3 | Difficile a reverser — dual-run obligatoire |
| R4 | Irreversible — validation comite + backup complet |

---

## Tier 1 — Hot path confirme / objets critiques

> Tables a forte densite de consumers ou criticite P0. Modification = regression garantie sans tests.

| Object | Type | Domain | Owner | P | Classification | Consumers (refs) | Read path | Write path | Risk | Status | Gate | Evidence | Next step |
|--------|------|--------|-------|---|----------------|-------------------|-----------|------------|------|--------|------|----------|-----------|
| `pieces_gamme` | table | D1 | CatalogModule | P0 | source_of_truth | 49 refs / 28+ services | admin/, blog/, gamme-rest/, marketing/, seo/ | admin-gammes-seo, content-refresh | R4 | protected | Full regression | confirmed | freeze + profile read queries |
| `__seo_gamme_purchase_guide` | table | D3 | SeoModule | P1 | source_of_truth | 33 refs | gamme-rest/, seo/, marketing/ | buying-guide-enricher, r1-content-pipeline | R3 | protected | Pipeline test + SEO check | confirmed | audit write pipeline |
| `__seo_reference` | table | D3 | SeoModule | P1 | source_of_truth | 26 refs | reference.service, seo-generator, marketing-data | content-refresh | R3 | protected | SEO regression | confirmed | profile read paths |
| `__rag_knowledge` | table | D6 | RagProxyModule | P2 | source_of_truth | 25 refs | rag-knowledge, rag-admissibility-gate, rag-foundation-gate | rag-ingestion, rag-normalization | R3 | protected | RAG pipeline test | confirmed | profile ingestion perf |
| `__seo_observable` | table | D3 | SeoModule | P1 | derived | 18 refs | seo/, admin/, marketing/ | — (read-only) | R2 | profile | EXPLAIN + consumer audit | confirmed | EXPLAIN ANALYZE on hot queries |
| `__seo_page_brief` | table | D3 | SeoModule | P1 | derived | 17 refs | brief-template, page-brief, seo/ | r1-content-pipeline | R3 | protected | Pipeline test | confirmed | audit write pipeline |
| `__seo_gamme` | table | D3 | SeoModule | P1 | source_of_truth | 17 refs | admin/, seo/, dashboard, marketing/ | enrichment pipeline | R3 | protected | SEO regression | confirmed | profile enrichment writes |
| `__seo_keywords` | table | D3 | SeoModule | P1 | source_of_truth | 13 refs + 7 triggers | admin/, seo/ | keyword pipeline | R3 | profile | Profiler INSERT (7 triggers cascade) | confirmed | profile writes + trigger audit |
| `__seo_page` | table | D3 | SeoModule | P1 | source_of_truth | 12 refs | seo/ sitemap services | seo-generator | R3 | protected | Sitemap regression | confirmed | sitemap perf test |
| `ic_postback` | table | D11 | PaymentsModule | P0 | operational | 11 refs | payments/, orders/ | payment-data.service (WRITE critical) | R4 | protected | Payment flow test | confirmed | payment flow regression |
| `kg_edges` | table | D7 | KnowledgeGraphModule | P3 | source_of_truth | 11 refs | knowledge-graph/ | kg services | R2 | observe_activation | Feature flag check | confirmed | feature flag audit |
| `pieces` | table | D1 | CatalogModule | P0 | source_of_truth | ~8 refs + 2 triggers | catalog/, search/ | catalog import | R4 | protected | Full regression | confirmed | profile catalog import |
| `auto_type` | table | D4 | VehicleModule | P0 | source_of_truth | ~6 refs | vehicle/, seo/, gamme-rest/ | — (read-only) | R4 | protected | Vehicle matching test | confirmed | vehicle matching regression |

> Note : certains objets D7 (KG) apparaissent ici par densite de references code, sans impliquer une criticite business equivalente aux flux P0/P1 de production.

---

## Tier 2 — Medium risk / consumers confirmes hors hot path

> Tables avec consumers identifies mais impact plus limite. Gate standard.

| Object | Type | Domain | Owner | P | Classification | Consumers (refs) | Read path | Write path | Risk | Status | Gate | Evidence | Next step | Retention |
|--------|------|--------|-------|---|----------------|-------------------|-----------|------------|------|--------|------|----------|-----------|-----------|
| `catalog_gamme` | table | D1 | CatalogModule | P0 | source_of_truth | ~6 refs | catalog/, seo/ | — | R3 | protected | Catalog regression | confirmed | profile read paths | keep_active |
| `catalog_family` | table | D1 | CatalogModule | P0 | source_of_truth | ~5 refs | catalog/, seo/ | — | R3 | protected | Catalog regression | confirmed | profile read paths | keep_active |
| `__seo_gamme_conseil` | table | D3 | SeoModule | P1 | source_of_truth | ~8 refs | seo/, gamme-rest/ | conseil-enricher | R3 | protected | Content pipeline | confirmed | pipeline regression test | keep_active |
| `__blog_advice` | table | D5 | BlogModule | P1 | source_of_truth | ~5 refs | blog/, seo/ | — | R2 | stabilize | Blog regression | confirmed | blog regression test | keep_active |
| `__blog_guide` | table | D5 | BlogModule | P1 | source_of_truth | ~5 refs | blog/, seo/ | — | R2 | stabilize | Blog regression | confirmed | blog regression test | keep_active |
| `___xtr_order` | table | D2 | — (legacy) | P2 | legacy | ~5 refs | payments/, orders/ | payment-data.service | R3 | archive_review | Legal retention + payment flow active — not eligible for archive until decoupled | confirmed | decouple payment flow | legal_hold_unknown |
| `___xtr_customer` | table | D2 | — (legacy) | P2 | legacy | ~3 refs | admin/ | — | R2 | archive_review | Legal retention | partial | complete code search | legal_hold_unknown |
| `kg_nodes` | table | D7 | KnowledgeGraphModule | P3 | source_of_truth | ~6 refs | knowledge-graph/ | kg services | R2 | observe_activation | Feature flag | confirmed | feature flag audit | design_intent_keep |
| `__rag_content_refresh_log` | table | D6 | RagProxyModule | P2 | operational | ~5 refs | admin/, rag-proxy/ | content-refresh | R1 | stabilize | — | confirmed | monitor growth | keep_active |
| `gamme_aggregates` | table | D14 | SeoModule | P1 | source_of_truth | ~5 refs + RPC | admin/, seo/ | refresh_gamme_aggregates RPC | R3 | stabilize | RPC test | confirmed | RPC perf test | keep_active |
| `__cross_gamme_car_new` | table | D4 | VehicleModule | P0 | derived | 1 ref (PRIMARY) | blog-article-relation.service | — | R2 | review | Consolidation candidate | confirmed | consolidate with _car | keep_active |
| `__cross_gamme_car` | table | D4 | VehicleModule | P0 | derived | 1 ref (FALLBACK) | gamme-detail-enricher.service | — | R2 | review | Migrate before DROP | confirmed | migrate to _new then DROP | drop_candidate_after_backup |
| `gamme_seo_audit` | table | D14 | AdminModule | P1 | empty_active_design | 4 refs | gamme-seo-audit, seo-cockpit | gamme-seo-audit.service | R1 | stabilize | — | confirmed | monitor activation | design_intent_keep |
| `gamme_seo_metrics` | table | D14 | SeoModule | P1 | derived | ~3 refs + 2 triggers | seo/, admin/ | trigger | R2 | stabilize | Trigger impact | confirmed | trigger perf audit | keep_active |
| `__agentic_runs` | table | D6 | AgenticModule | P2 | operational | 178 refs | agentic-engine/ | agentic-data.service | R2 | stabilize | — | confirmed | monitor growth + purge policy | keep_active |

---

## Tier 3 — Low risk + obsolete confirmed

### 3a — APP_ORPHAN_CONFIRMED (0 refs code backend — candidats DROP)

| Object | Type | Domain | Lignes | Taille | code_refs | runtime_signal | Evidence | Gate minimale | Retention | Mode DROP |
|--------|------|--------|--------|--------|-----------|----------------|----------|---------------|-----------|-----------|
| `__agent_runs` | table | D6 | 5 | 64 KB | 0 | none | doublon de `__agentic_runs` | Backup rows → `__agentic_runs` si necessaire | drop_candidate_after_backup | `DROP TABLE` |
| `messages` | table | D13 | 0 | — | 0 | none | aucune dependance applicative identifiee | Aucune (0 rows) | drop_candidate_after_backup | `DROP TABLE` |
| `sessions` | table | D11 | 0 | — | 0 | none | Redis en prod | Aucune (0 rows) | drop_candidate_after_backup | `DROP TABLE` |
| `___config_old` | table | D13 | 1 | — | 0 | none | suffixe `_old` | Backup 1 row | drop_candidate_after_backup | `DROP TABLE` |
| `products` | table | D1 | 0 | 24 KB | 0 | none | donnees dans `pieces` | Aucune (0 rows) | drop_candidate_after_backup | `DROP TABLE` |
| `categories` | table | D1 | 0 | 24 KB | 0 | none | donnees dans `pieces_gamme` | Aucune (0 rows) | drop_candidate_after_backup | `DROP TABLE` |
| `__blog_advice_old` | table | D5 | 0 | 280 KB | 0 | none | suffixe `_old` | Aucune (0 rows) | drop_candidate_after_backup | `DROP TABLE` |
| `__rag_knowledge_backup_20260222` | table | D6 | 314 | 1.3 MB | 0 | none | corpus actif (367) > backup (314) | Confirmer 367 >= 314 | drop_candidate_after_backup | `DROP TABLE` |

### 3b — ORPHAN (donnees presentes, 0 consumer)

| Object | Type | Domain | Lignes | Taille | Evidence | Gate | Retention | Mode |
|--------|------|--------|--------|--------|----------|------|-----------|------|
| `__cross_gamme_car_new2` | table | D4 | 165K | 30 MB | 0 refs code backend confirmees, aucune lecture applicative identifiee | Backup si donnees uniques vs `_new` | drop_candidate_after_backup | `DROP TABLE` apres verification |

### 3c — UNEXPLAINED_DB_ACTIVITY

| Object | Type | Domain | Lignes | code_refs | runtime_signal | object_status | next_gate |
|--------|------|--------|--------|-----------|----------------|---------------|-----------|
| `__seo_quality_log` | table | D3 | 0 | 0 | 104M idx_scan | UNEXPLAINED_DB_ACTIVITY | `pg_stat_user_indexes` + inspect views / functions / cron |

### 3d — Tables D2 Legacy (usage non confirme en hot path)

| Object | Type | Domain | Taille | Classification | Status | Gate |
|--------|------|--------|--------|----------------|--------|------|
| `___xtr_msg` | table | D2 | 25 GB | historical_support | archive_review | Legal retention + 15.4 GB index review |
| `___xtr_customer_billing_address` | table | D2 | 29 MB | legacy | archive_review | Legal retention |
| `___xtr_customer_delivery_address` | table | D2 | 29 MB | legacy | archive_review | Legal retention |
| `___xtr_order_line` | table | D2 | 2.6 MB | legacy | archive_review | Legal retention |
| `___xtr_invoice*` (2 tables) | table | D2 | 608 KB | legacy | archive_review | Legal retention |
| `___xtr_delivery_*` (4 tables) | table | D2 | ~480 KB | legacy | archive_review | Legal retention |
| `___xtr_supplier*` (2 tables) | table | D2 | 208 KB | legacy | archive_review | Legal retention |
| `___xtr_order_*status` (2 tables) | table | D2 | 224 KB | legacy | archive_review | Legal retention |
| `___xtr_order_line_equiv_ticket` | table | D2 | 112 KB | legacy | archive_review | Legal retention |

### 3e — EMPTY_ACTIVE_DESIGN (design intent, non materialise)

> ~55 tables. Schema et RPC en place, tables vides. Ne pas supprimer.
> Liste non exhaustive — voir domain-map.md V1.4.2 pour details par domaine.

| Domaine | Tables (count) | Exemples | Status |
|---------|---------------|----------|--------|
| D7 KG | 13 | `kg_truth_labels`, `kg_cases`, `kg_diagnostic_cases` | observe_activation |
| D9 Import | 19 | `stg_*`, `norm_*`, `natural_key_*`, `xref_*`, `decision_*` | observe_activation |
| D8 RM | 13 | `rm_listing_products_*`, `rm_product`, `rm_rebuild_queue` | observe_activation |
| D12 Marketing | 11 | `__marketing_social_posts`, `__video_assets` | observe_activation |
| D15 Security | 5 | `__quarantine_items`, `_killswitch_*`, `__airlock_bundles` | observe_activation |
| D3 SEO | 4 | `__seo_r2_keyword_plan`, `__seo_r8_*` | observe_activation |
| D10 Quality | 7 | `__lighthouse_*`, `error_*`, `crawl_budget_metrics` | review |
| D11 Commerce | 5 | `password_resets`, `promo_usage`, `support_tickets`, `ticket_responses`, `reviews` | stabilize |

---

## Services critiques — reference croisee

| Service | Fichier | Tables impactees | Impact |
|---------|---------|-----------------|--------|
| content-refresh | `admin/services/content-refresh.service.ts` | Pipeline SEO orchestrateur multi-tables | Tier 1 |
| payment-data | `payments/repositories/payment-data.service.ts` | `ic_postback`, `___xtr_order` | Tier 1 (P0) |
| reference | `seo/services/reference.service.ts` | `__seo_reference`, diagnostics SEO | Tier 1 |
| rag-knowledge | `rag-proxy/services/rag-knowledge.service.ts` | `__rag_knowledge`, ingestion | Tier 1 |
| buying-guide-data | `gamme-rest/services/buying-guide-data.service.ts` | Frontend content serving | Tier 1 |
| gamme-seo-audit | `admin/services/gamme-seo-audit.service.ts` | `gamme_seo_audit` | Tier 2 |
| blog-article-relation | `blog/services/blog-article-relation.service.ts` | `__cross_gamme_car_new` | Tier 2 |
| gamme-detail-enricher | `admin/services/gamme-detail-enricher.service.ts` | `__cross_gamme_car` | Tier 2 |
| agentic-data | `agentic-engine/services/agentic-data.service.ts` | `__agentic_runs` + 5 tables agentiques | Tier 2 |

---

## Limites de cette matrice

- Le code search backend (`.from()`, `.rpc()`) ne couvre pas : vues SQL, fonctions PostgreSQL, triggers indirects, cron/jobs hors backend, acces SQL brut
- Les `code_refs` comptent les references `.from('table')` et `.rpc()` dans le backend TypeScript uniquement
- `runtime_signal` provient de `pg_stat_user_tables` / `pg_stat_user_indexes` — cumulatif depuis dernier reset
- `owner_metier` n'est pas encore attribue — sera ajoute dans V1.2 apres arbitrage fonctionnel
- Un index a `0 scan` n'est pas automatiquement supprimable. Les primary keys, index de secours, usages batch rares et chemins de reprise doivent etre verifies avant toute decision

---

## Non-goals

Cette matrice ne decide pas a elle seule la suppression ou modification d'un objet.
Les decisions doivent etre validees par :
- perf-findings.md (EXPLAIN ANALYZE)
- change-control-plan.md (procedure shadow/canary)
- validation preprod si risk >= R2

---

_Derniere mise a jour: 2026-03-14_
_Genere depuis code search backend + domain-map.md V1.4.2_
