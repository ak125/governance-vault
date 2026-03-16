# Domain Map — massdoc DB

> **Baseline d'architecture et de gouvernance fonctionnelle de la DB massdoc**
> **Version**: 1.4.2 | **Status**: BASELINE_ACCEPTED | **Date**: 2026-03-14
> **Projet Supabase**: `cxpojprgwgubzjyqzmoq` (eu-west-3)

---

## Contexte d'observation

| Parametre | Valeur |
|-----------|--------|
| Source | `pg_stat_*`, `information_schema`, `pg_tables`, `pg_indexes` |
| Fenetre | Depuis le dernier reset stats PostgreSQL (date inconnue) |
| Environnement | Production (`cxpojprgwgubzjyqzmoq`) |
| Date de collecte DB | 2026-03-13 |
| Date de consolidation doc | 2026-03-14 |

**Limites connues :**
- Les compteurs `pg_stat_*` sont cumulatifs depuis le dernier reset — ils peuvent etre biaises par un reset recent, une maintenance, ou un restart du serveur
- Un index a 0 scan sur la periode observee n'est pas automatiquement un index supprimable (batch rare, import mensuel, failover de requete)
- Les `seq_tup_read` et `idx_tup_fetch` refletent l'activite DB, pas l'activite business
- Les tables a 0 rows peuvent etre : en attente d'activation, shadow/staging, feature flag off, ou reellement obsoletes

---

## Modele de confiance

| Niveau | Signification | Exemples |
|--------|---------------|----------|
| **C1** | Mesure directement depuis la DB | Taille, lignes, index, triggers, taille index |
| **C2** | Infere depuis DB + conventions de nommage | Domaine, owner technique, role fonctionnel |
| **C3** | Hypothese a confirmer dans le code/RPC/jobs | Consumers, hot path business, obsolescence |

Chaque affirmation du document est marquee implicitement :
- Les **tableaux de taille/lignes** = C1
- Les **classifications par domaine** = C2
- Les **recommandations et anomalies** = C3 sauf mention contraire

---

## Hot path : DB vs Business

| Type | Definition | Exemple |
|------|-----------|---------|
| **db_hot_path** | Fort volume d'operations DB (scans, fetches) | `pieces_relation_type` : 463B seq_tup_read |
| **business_hot_path** | Impact direct sur l'experience utilisateur / conversion / SEO | Page listing produits, checkout, indexation Google |

Un db_hot_path n'est pas forcement un business_hot_path (batch nocturne a fort volume). Un business_hot_path peut avoir un faible volume DB (page checkout avec peu de requetes mais impact critique).

Dans ce document, les colonnes "Hot path" des tableaux indiquent le **business_hot_path presume** (C3). Le db_hot_path est documente dans les sections "Hot path critique" avec metriques (C1).

---

## Inventaire global

| Metrique | Valeur |
|----------|--------|
| Tables | 283 |
| Fonctions/RPC | 306 (dont ~70 systeme: trigram, unaccent) |
| Vues | 40 |
| Triggers | 41 |
| Taille totale | ~102 GB |

---

## D1 — Catalog Core

> Coeur metier : pieces auto, references, prix, medias, criteres, relations vehicule-piece.

| Criticite | **P0** — Site down si indisponible |
|-----------|------|
| Taille | **75 GB** (73% de la DB) |
| Tables | 22 |
| Owner technique | Backend / CatalogModule |
| Decision status | **protected** — coeur metier, aucune modification sans evidence |

### Tables

| Table | Taille | Lignes | Hot path | Notes |
|-------|--------|--------|----------|-------|
| `pieces_relation_criteria` | 36 GB | 157M | U1,U2 | Plus grosse table. Criteres de relation piece-vehicule |
| `pieces_ref_search` | 18 GB | 73M | U2 | Index de recherche references |
| `pieces_relation_type` | 13 GB | 146M | U1 | Relations type vehicule ↔ piece |
| `pieces_criteria` | 5.7 GB | 17.6M | U1 | Criteres techniques des pieces |
| `pieces` | 1.6 GB | 3.5M | U1,U2,U3 | Table mere : toutes les pieces |
| `pieces_media_img` | 1.1 GB | 4.6M | U1 | Images des pieces |
| `pieces_ref_ean` | 897 MB | 3M | U2 | Codes EAN |
| `pieces_list` | 394 MB | 1.8M | U1 | Listes de pieces (kits, composants) |
| `pieces_price` | 344 MB | 442K | U1,U3 | Prix des pieces |
| `pieces_gamme` | 10 MB | 9.7K | U1,U4 | Gammes de pieces (lien famille-gamme) |
| `pieces_criteria_link` | 18 MB | 77K | U1 | Liens criteres-pieces |
| `pieces_criteria_group` | 1.5 MB | 4.3K | U1 | Groupes de criteres |
| `pieces_ref_brand` | 1.4 MB | 5.9K | U2 | References par marque |
| `pieces_gamme_cross` | 416 KB | 1.4K | U4 | Cross-reference gammes |
| `pieces_marque` | 656 KB | 992 | U1 | Marques de pieces |
| `pieces_status` | 128 KB | 13 | — | Statuts des pieces |
| `pieces_details` | 256 KB | 1 | — | Details supplementaires (low materialization state) |
| `pieces_ref_oem` | 112 KB | 1 | — | Refs OEM (low materialization state) |
| `pieces_side_filtre` | 32 KB | 5 | U1 | Filtres lateraux |
| `pieces_marque_next` | 8 KB | 0 | — | Migration marques (vide) |
| `catalog_family` | 224 KB | 19 | U1 | Familles de catalogue |
| `catalog_gamme` | 160 KB | 244 | U1 | Gammes de catalogue |

### Data classification (C2)
- **Source of truth** : `pieces`, `pieces_price`, `pieces_media_img`, `pieces_gamme`, `pieces_marque`, `catalog_family`, `catalog_gamme`
- **Derived / relational expansion** : `pieces_relation_type`, `pieces_relation_criteria`, `pieces_ref_search`, `pieces_ref_ean`, `pieces_ref_brand`, `pieces_criteria`, `pieces_criteria_link`, `pieces_criteria_group`, `pieces_list`, `pieces_gamme_cross`
- **Config** : `pieces_status`, `pieces_side_filtre`
- **LOW_MATERIALIZATION_STATE** : `pieces_details` (1 row), `pieces_ref_oem` (1 row) — schema en place, donnees residuelles
- **EMPTY_UNKNOWN** : `products` (24 KB, 0 rows), `categories` (24 KB, 0 rows), `pieces_marque_next` (0 rows) — consumer non confirme (C3)

### Dependances inter-domaines
- **D4 (Vehicle)** : `pieces_relation_type`, `pieces_relation_criteria` referencent les types vehicule
- **D3 (SEO)** : `pieces_gamme` alimente les pages gamme SEO
- **D8 (Read Model)** : consomme les donnees catalog pour construire les listings

### db_hot_path (C1 — mesure)
- `pieces` : **13 milliards** d'idx_scan — table la plus sollicitee de la DB
- `pieces_relation_type` : 463 milliards seq_tup_read (scans sequentiels massifs)
- `pieces_criteria` : 3.9 trillions idx_tup_fetch

### business_hot_path (C3 — presume)
- U1 (listing catalogue) : `pieces` → `pieces_relation_type` → `pieces_price` → `pieces_media_img`
- U2 (recherche reference) : `pieces_ref_search` → `pieces` → `pieces_ref_ean`

### Index a 0 scan sur la periode observee (C1 — review_for_drop)
- `idx_pieces_relation_criteria_rcp_cri_id` : 1.5 GB, 0 scan
- `idx_pieces_relation_type_composite` : 1.4 GB, 0 scan
- `idx_pieces_relation_criteria_rcp_pg_id` : 1.3 GB, 0 scan
- `idx_pieces_ref_search_ref` : 1.1 GB, 0 scan
- `idx_prt_type_gamme` : 1.1 GB, 0 scan
- `idx_pieces_relation_type_type_id` : 984 MB, 0 scan
- `idx_prs_ref_exact` : 836 MB, 0 scan
- `idx_pieces_ref_clean` : 156 MB, 0 scan
- + index pieces_price, pieces_list (~200 MB total)
- **Total estime : ~8 GB d'index a 0 scan sur D1**
- **Gate requise avant action** : confirmer absence d'usage via code search + EXPLAIN des requetes critiques + verifier fenetre stats representative

---

## D2 — Legacy/XTR (Migration PrestaShop)

> Donnees migrees de l'ancien systeme PrestaShop. Messagerie, clients, commandes historiques.

| Criticite | **P2** — Historique, pas de nouveau flux |
|-----------|------|
| Taille | **25 GB** (24% de la DB) |
| Tables | 18 |
| Owner technique | — (legacy, pas de module actif) |
| Decision status | **archive_review** — 24% de la DB, usage non confirme |

### Tables

| Table | Taille | Lignes | Notes |
|-------|--------|--------|-------|
| `___xtr_msg` | 25 GB | 15M | Messages clients historiques. **14 GB d'index inutilise** |
| `___xtr_customer` | 34 MB | 59K | Clients migres |
| `___xtr_customer_billing_address` | 29 MB | 59K | Adresses facturation |
| `___xtr_customer_delivery_address` | 29 MB | 59K | Adresses livraison |
| `___xtr_order_line` | 2.6 MB | 2.5K | Lignes de commande |
| `___xtr_order` | 1.8 MB | 1.6K | Commandes |
| `___xtr_invoice_line` | 304 KB | 1 | Factures (low materialization state) |
| `___xtr_invoice` | 304 KB | 1 | Factures (low materialization state) |
| `___xtr_delivery_agent` | 176 KB | 1 | Agent livraison |
| `___xtr_delivery_ape_france` | 144 KB | 9 | Tarifs livraison France |
| `___xtr_delivery_ape_corse` | 112 KB | 9 | Tarifs livraison Corse |
| `___xtr_delivery_ape_domtom1` | 112 KB | 7 | Tarifs livraison DOM-TOM |
| `___xtr_delivery_ape_domtom2` | 112 KB | 7 | Tarifs livraison DOM-TOM |
| `___xtr_supplier_link_pm` | 96 KB | 108 | Liens fournisseurs-pieces |
| `___xtr_supplier` | 112 KB | 70 | Fournisseurs |
| `___xtr_order_line_status` | 112 KB | 10 | Statuts ligne commande |
| `___xtr_order_status` | 112 KB | 4 | Statuts commande |
| `___xtr_order_line_equiv_ticket` | 112 KB | 13 | Tickets equivalence |

### Data classification (C2)
- **Legacy / archive candidate** : toutes les tables `___xtr_*` — donnees migrees de PrestaShop, usage non confirme en hot path (C3)
- **Source of truth historique** : `___xtr_customer`, `___xtr_order`, `___xtr_order_line` — donnees transactionnelles d'origine
- **Historical support data** : `___xtr_msg` — messagerie client historique PrestaShop

### Index a 0 scan sur la periode observee (C1 — review_for_drop)
- `idx____xtr_msg_msg_content` : **14 GB**, 0 scan
- `___xtr_msg_pkey` : 714 MB, 0 scan
- `idx____xtr_msg_msg_orl_equiv_id` : 168 MB, 0 scan
- `idx____xtr_msg_msg_orl_id` : 168 MB, 0 scan
- `idx____xtr_msg_msg_parent_id` : 168 MB, 0 scan
- `idx____xtr_msg_msg_ord_id` : 168 MB, 0 scan
- **Total estime : ~15.4 GB d'index a 0 scan sur D2**
- **Gate requise avant action** : confirmer absence de consumers via code search + verifier jobs batch/cron + confirmer que les donnees historiques ne sont pas requises par obligations legales

### Evaluation (C3)
Usage non confirme en hot path. 25 GB (24% de la DB) pour des donnees historiques. **archive_review** — gate requise : confirmer absence de dependances actives + obligations retention legale.

---

## D3 — SEO & Sitemap

> Pages SEO dynamiques, mots-cles, keyword plans (R1-R8), sitemap, quality scoring.

| Criticite | **P1** — Impact SEO/indexation Google direct |
|-----------|------|
| Taille | **~320 MB** |
| Tables | 55 |
| Owner technique | Backend / SeoModule |
| Decision status | **profile** — 5 triggers. `__seo_quality_log` : RESOLVED_C4 (source = extinct trigger, 5 phantom indexes dropped, compteur ne progresse plus) |

### Tables principales

| Table | Taille | Lignes | Hot path | Notes |
|-------|--------|--------|----------|-------|
| `__seo_page` | 114 MB | 322K | U4 | Pages SEO dynamiques |
| `__sitemap_p_link` | 89 MB | 473K | U4 | Liens sitemap pieces |
| `seo_link_impressions` | 25 MB | 104K | — | Tracking impressions |
| `__seo_gamme_conseil` | 18 MB | 2.2K | U4 | Contenu conseil par gamme |
| `__seo_keywords` | 11 MB | 4.6K | U4 | Mots-cles SEO (5 triggers) |
| `__seo_keyword_type_mapping` | 11 MB | 0 | — | Mapping KW-type (EMPTY_UNKNOWN — taille residuelle 11 MB) |
| `__seo_family_gamme_car_switch` | 3 MB | 3.8K | U1 | Switchs famille-gamme-vehicule |
| `__seo_item_switch` | 2.7 MB | 8K | U1 | Switchs item |
| `__sitemap_motorisation` | 3.2 MB | 12.8K | U4 | Sitemap motorisations |
| `__seo_reference` | 2.3 MB | 224 | U4 | References SEO (R4) |
| `__seo_gamme_purchase_guide` | 2 MB | 221 | U4 | Guides d'achat (R6) |
| `__seo_gamme` | 1.7 MB | 151 | U4 | Gammes SEO |
| `__seo_gamme_car_switch` | 1.7 MB | 6.5K | U1 | Switchs gamme-vehicule |

### Keyword Plans (R1-R8)

| Table | Lignes | Role |
|-------|--------|------|
| `__seo_r1_keyword_plan` | 10 | R1 transactionnel |
| `__seo_r2_keyword_plan` | 0 | R2 categorie (vide) |
| `__seo_r3_keyword_plan` | 15 | R3 conseil |
| `__seo_r4_keyword_plan` | 36 | R4 reference |
| `__seo_r6_keyword_plan` | 2 | R6 guide achat |
| `__seo_r8_keyword_plan` | 1 | R8 vehicule |

### Pages R8 (vehicule)

| Table | Lignes | Notes |
|-------|--------|-------|
| `__seo_r8_pages` | 1 | Page vehicule |
| `__seo_r8_page_versions` | 1 | Versions |
| `__seo_r8_fingerprints` | 1 | Fingerprints |
| `__seo_r8_similarity_index` | 0 | Index similarite |
| `__seo_r8_qa_reviews` | 1 | QA reviews |
| `__seo_r8_regeneration_queue` | 0 | Queue regeneration |
| `__seo_r8_engine_family_stats` | 0 | Stats moteur |

### Autres tables SEO/Sitemap

`__seo_type_vlevel` (1.1K), `__seo_observable` (24), `__seo_gamme_info` (986), `__seo_gamme_car` (118), `__seo_equip_gamme` (137), `__seo_marque` (35), `__seo_confusion_pairs` (124), `__seo_type_switch` (134), `__seo_page_brief` (25), `__seo_research_brief` (6), `__seo_observable_policy` (32), `__seo_r3_image_prompts` (10), `__seo_r6_image_prompts` (2), `__seo_generation_log` (25), `__seo_crawl_hub` (2), `__seo_keyword_cluster` (3), `__seo_internal_link` (0), `__seo_interpolation_alerts` (0), `__seo_index_history` (0), `__seo_role_content` (0), `__seo_quality_log` (0), `__seo_diagnostic` (0), `__seo_brief_template` (0), `__seo_sitemap_file` (0), `__seo_crawl_log` (0), `__sitemap_p_xml` (2K), `__sitemap_search_link` (1), `__sitemap_blog` (330), `__sitemap_gamme` (0), `__sitemap_marque` (35), `seo_link_clicks` (283), `seo_link_metrics_daily` (0)

### Data classification (C2)
- **Source of truth** : `__seo_page`, `__seo_gamme`, `__seo_gamme_purchase_guide`, `__seo_gamme_conseil`, `__seo_reference`, `__seo_keywords`
- **Derived / serving** : `__sitemap_p_link`, `__sitemap_motorisation`, `__sitemap_p_xml`, `__sitemap_blog`, `__sitemap_marque`, `seo_link_impressions`, `seo_link_clicks`, `seo_link_metrics_daily`
- **Config / policy** : `__seo_observable_policy`, `__seo_brief_template`, `__seo_keyword_type_mapping`
- **EMPTY_ACTIVE_DESIGN** : `__seo_r2_keyword_plan`, `__seo_r8_similarity_index`, `__seo_r8_engine_family_stats`, `__seo_r8_regeneration_queue` — design intent present, activation non confirmee (C3)
- **EMPTY_UNKNOWN** : `__seo_internal_link`, `__seo_interpolation_alerts`, `__seo_index_history`, `__seo_role_content`, `__seo_quality_log`, `__seo_diagnostic`, `__seo_sitemap_file`, `__seo_crawl_log`, `__sitemap_gamme` — consumer non confirme (C3)

### Anomalie detectee
- `__seo_quality_log` : **104M idx_scan pour 0 rows** — RESOLVED_C4 : source identifiee = trigger historique (maintenant eteint). 5 indexes phantom supprimes. Compteur fige, ne progresse plus.

### Dependances
- **D1 (Catalog)** : `pieces_gamme` → pages gamme
- **D4 (Vehicle)** : `auto_type` → pages vehicule, switchs
- **D5 (Blog)** : `__blog_*` pour le contenu associe

---

## D4 — Vehicle / Compatibility

> Vehicules, modeles, marques automobiles, compatibilite pieces-vehicules.

| Criticite | **P0** — Essentiel pour le matching piece-vehicule |
|-----------|------|
| Taille | **~130 MB** |
| Tables | 12 |
| Owner technique | Backend / VehicleModule |
| Decision status | **protected** — coeur matching vehicule, consolidation cross_gamme_car a evaluer |

### Tables

| Table | Taille | Lignes | Hot path | Notes |
|-------|--------|--------|----------|-------|
| `__cross_gamme_car_new` | 41 MB | 175K | U1 | Cross-reference gamme-vehicule (new) |
| `auto_type_number_code` | 37 MB | 165K | U1 | Codes type vehicule |
| `auto_type` | 37 MB | 49K | U1,U2 | Types vehicule. 104M idx_scan |
| `__cross_gamme_car_new2` | 30 MB | 165K | U1 | Cross-reference v2 |
| `__cross_gamme_car` | 13 MB | 75K | U1 | Cross-reference original |
| `cars_engine` | 10 MB | 35.7K | — | Moteurs |
| `auto_modele` | 1.1 MB | 5.7K | U1 | Modeles |
| `auto_modele_group` | 600 KB | 2K | U1 | Groupes de modeles |
| `auto_type_motor_fuel` | 160 KB | 26 | — | Types carburant |
| `auto_marque` | 64 KB | 117 | U1 | Marques auto |
| `auto_type_motor_code` | 64 KB | 1 | — | Codes moteur (low materialization state) |
| `auto_modele_robot` | 104 KB | 1 | — | Robot modele (low materialization state) |
| `vehicule_v1_dominant` | 32 KB | 0 | — | Vehicule V1 dominant (EMPTY_UNKNOWN) |

### Data classification (C2)
- **Source of truth** : `auto_type`, `auto_modele`, `auto_marque`, `cars_engine`, `auto_modele_group`
- **Derived / cross-reference** : `__cross_gamme_car`, `__cross_gamme_car_new`, `__cross_gamme_car_new2`, `auto_type_number_code`
- **Config** : `auto_type_motor_fuel`
- **EMPTY_UNKNOWN** : `vehicule_v1_dominant` (0 rows), `auto_type_motor_code` (1 row), `auto_modele_robot` (1 row) — consumer non confirme (C3)

### Note — cross_gamme_car* (evidence code 2026-03-14)
3 tables pour la meme fonctionnalite — **statuts confirmes par code search** :
- `__cross_gamme_car_new` : **ACTIVE_PRIMARY** — 1 consumer actif (`blog-article-relation.service.ts:52`), 175K rows
- `__cross_gamme_car` : **ACTIVE_FALLBACK** — 1 consumer actif (`gamme-detail-enricher.service.ts:148`), 75K rows
- `__cross_gamme_car_new2` : **ORPHAN** — 0 refs code, 30 MB, 165K rows

**Recommandation** : consolider sur `__cross_gamme_car_new` (primary). Gate : migrer `gamme-detail-enricher` avant DROP de `__cross_gamme_car`. `__cross_gamme_car_new2` devient drop candidate apres backup et validation d'absence d'ecart avec `_new`.

---

## D5 — Blog / Content

> Articles de blog, guides d'achat, conseils, contenu editorial.

| Criticite | **P1** — Contenu SEO editorial |
|-----------|------|
| Taille | **~16 MB** |
| Tables | 10 |
| Owner technique | Backend / BlogModule |
| Decision status | **stabilize** — 1 obsolete_candidate a confirmer |

### Tables

| Table | Taille | Lignes | Notes |
|-------|--------|--------|-------|
| `__blog_guide_h2` | 8.3 MB | 1.8K | Sections H2 des guides |
| `__blog_advice_h2` | 2.4 MB | 447 | Sections H2 des conseils |
| `__blog_guide` | 2 MB | 224 | Guides principaux |
| `__blog_advice_h3` | 1.1 MB | 200 | Sections H3 des conseils |
| `__blog_advice` | 1 MB | 85 | Conseils principaux |
| `__blog_guide_h3` | 584 KB | 674 | Sections H3 des guides |
| `__blog_advice_cross` | 112 KB | 321 | Cross-references conseils |
| `__blog_meta_tags_ariane` | 176 KB | 5 | Breadcrumbs blog |
| `__blog_seo_marque` | 144 KB | 1 | SEO marque blog |
| `__blog_advice_old` | 280 KB | 0 | EMPTY_OBSOLETE_CANDIDATE (suffixe `_old`) |

### Data classification (C2)
- **Source of truth** : `__blog_guide`, `__blog_advice`
- **Derived / sections** : `__blog_guide_h2`, `__blog_guide_h3`, `__blog_advice_h2`, `__blog_advice_h3`, `__blog_advice_cross`
- **Config** : `__blog_meta_tags_ariane`, `__blog_seo_marque`
- **EMPTY_OBSOLETE_CANDIDATE** : `__blog_advice_old` — suffixe `_old` + 0 rows. Gate requise : confirmer absence de references dans le code (C3)

---

## D6 — RAG & AI Engine

> RAG knowledge base, content refresh, web ingestion, moteur agentique.

| Criticite | **P2** — Pipeline IA, non critique pour le serving |
|-----------|------|
| Taille | **~12 MB** |
| Tables | 12 |
| Owner technique | Backend / RagProxyModule |
| Decision status | **observe_activation** — backup orphelin et doublon possible a investiguer |

### Tables

| Table | Taille | Lignes | Notes |
|-------|--------|--------|-------|
| `__rag_knowledge` | 4.2 MB | 367 | Corpus RAG (source de verite) |
| `__rag_content_refresh_log` | 1.9 MB | 836 | Logs de refresh |
| `__rag_knowledge_backup_20260222` | 1.3 MB | 314 | Backup RAG (EMPTY_OBSOLETE_CANDIDATE — date dans le nom) |
| `__rag_web_ingest_jobs` | 920 KB | 263 | Jobs d'ingestion web |
| `__rag_webhook_audit` | 64 KB | 3 | Audit webhooks |
| `__agentic_steps` | 152 KB | 48 | Steps agentiques |
| `__agentic_evidence` | 120 KB | 44 | Evidence agentique |
| `__agentic_branches` | 120 KB | 29 | Branches agentiques |
| `__agentic_runs` | 120 KB | 9 | Runs agentiques |
| `__agentic_checkpoints` | 96 KB | 8 | Checkpoints |
| `__agentic_gate_results` | 80 KB | 14 | Resultats des gates |
| `__agent_runs` | 64 KB | 5 | Runs agents — possible doublon avec `__agentic_runs` (C3) |

### Data classification (C2)
- **Source of truth** : `__rag_knowledge` (corpus RAG actif)
- **Derived / operational** : `__rag_content_refresh_log`, `__rag_web_ingest_jobs`, `__rag_webhook_audit`
- **Pipeline / agentic** : `__agentic_runs`, `__agentic_branches`, `__agentic_steps`, `__agentic_evidence`, `__agentic_checkpoints`, `__agentic_gate_results`
- **EMPTY_OBSOLETE_CANDIDATE** : `__rag_knowledge_backup_20260222` — backup date dans le nom, gate : confirmer que le corpus actif est complet avant suppression (C3)
- **Consumer non confirme** : `__agent_runs` — possible doublon de `__agentic_runs` (C3), gate : code search pour identifier les consumers

---

## D7 — Knowledge Graph & Diagnostic

> Graphe de connaissances mecaniques, moteur de diagnostic, safety rules.

| Criticite | **P3** — Experimental, pas en production |
|-----------|------|
| Taille | **~2.5 MB** |
| Tables | 33 (KG: 20, Diag: 13) |
| Owner technique | Backend / KnowledgeGraphModule, DiagnosticModule |
| Decision status | **observe_activation** — design present, activation non confirmee |

### Tables KG (20)

| Table | Lignes | Notes |
|-------|--------|-------|
| `kg_nodes` | 83 | Noeuds du graphe |
| `kg_edges` | 72 | Aretes du graphe |
| `kg_engine_families` | 10 | Familles moteur |
| `kg_safety_triggers` | 13 | Declencheurs securite |
| `kg_feedback_config` | 12 | Config feedback |
| `kg_reasoning_cache` | 7 | Cache raisonnement |
| `kg_confidence_config` | 1 | Config confiance |

Tables vides (0 rows) : `kg_truth_labels`, `kg_cases`, `kg_case_outcomes`, `kg_feedback_events`, `kg_review_queue`, `kg_rag_mapping`, `kg_rag_sync_log`, `kg_audit_log`, `kg_edge_history`, `kg_node_history`, `kg_learning_log`, `kg_weight_adjustments`, `kg_diagnostic_cases`

### Tables Diagnostic (13)

| Table | Lignes | Notes |
|-------|--------|-------|
| `__diag_symptom_cause_link` | 55 | Liens symptome-cause |
| `__diag_session` | 47 | Sessions diagnostic |
| `__diag_symptom_family` | 35 | Familles de symptomes |
| `__diag_symptoms` | 31 | Symptomes |
| `__diag_maintenance_symptom_link` | 23 | Liens maintenance-symptome |
| `__diag_symptom` | 18 | Symptomes (v2?) |
| `__diag_cause` | 18 | Causes |
| `__diag_safe_phrases` | 17 | Phrases securisees |
| `__diag_maintenance_operation` | 12 | Operations maintenance |
| `__diag_safety_rule` | 11 | Regles securite |
| `__diag_related_parts` | 7 | Pieces liees |
| `__diag_context_questions` | 5 | Questions contexte |
| `__diag_system` | 3 | Systemes vehicule |

### Data classification (C2)
- **Source of truth** : `kg_nodes`, `kg_edges`, `kg_engine_families`, `kg_safety_triggers`
- **Config** : `kg_feedback_config`, `kg_confidence_config`
- **Derived / cache** : `kg_reasoning_cache`
- **EMPTY_ACTIVE_DESIGN** : `kg_truth_labels`, `kg_cases`, `kg_case_outcomes`, `kg_feedback_events`, `kg_review_queue`, `kg_rag_mapping`, `kg_rag_sync_log`, `kg_audit_log`, `kg_edge_history`, `kg_node_history`, `kg_learning_log`, `kg_weight_adjustments`, `kg_diagnostic_cases` — design intent present (60 RPC existent), activation non confirmee (C3)

### Note
KG a **~60 RPC** (le plus gros domaine en fonctions). Tables majoritairement vides — **EMPTY_ACTIVE_DESIGN** : le design (RPC, schema) est en place, l'activation n'est pas confirmee. Ne pas conclure "inutile" depuis "vide" — ces tables attendent potentiellement un feature flag ou un dataset initial.

---

## D8 — Read Model / Serving (RM)

> CQRS read model pour le serving des pages catalogue. Listings pre-calcules.

| Criticite | **P1** — Performance de serving des pages produit |
|-----------|------|
| Taille | **~1 MB** |
| Tables | 17 |
| Owner technique | Backend / RmModule |
| Decision status | **observe_activation** — schema CQRS en place, materialization incomplete |

### Tables

| Table | Lignes | Notes |
|-------|--------|-------|
| `rm_data_version` | 24 | Versions des donnees |
| `rm_listing` | 3 | Listings pre-calcules |
| `rm_facets` | 2 | Facettes |
| `rm_facet_config` | 1 | Config facettes |
| `rm_listing_products_g1` | 0 | Partition gamme 1 |
| `rm_listing_products_g2` | 0 | Partition gamme 2 |
| `rm_listing_products_g4` | 0 | Partition gamme 4 |
| `rm_listing_products_g5` | 0 | Partition gamme 5 |
| `rm_listing_products_g7` | 0 | Partition gamme 7 |
| `rm_listing_products_g123` | 0 | Partition gamme 123 |
| `rm_listing_products_default` | 0 | Partition par defaut |
| `rm_listing_products` | 0 | Table parent (partitionnee) |
| `rm_product` | 0 | Produits RM |
| `rm_oem_top` | 0 | Top OEM |
| `rm_listing_content` | 0 | Contenu listing |
| `rm_build_log` | 0 | Log de build |
| `rm_rebuild_queue` | 0 | Queue de rebuild |

### Data classification (C2)
- **Control / metadata** : `rm_data_version`, `rm_facet_config`
- **Derived / serving** : `rm_listing`, `rm_facets`, `rm_listing_products` (partitionnee), `rm_product`, `rm_listing_content`, `rm_oem_top`
- **Operational** : `rm_build_log`, `rm_rebuild_queue`
- **EMPTY_ACTIVE_DESIGN** : la majorite des tables — schema et partitionnement en place, `rm_listing` et `rm_data_version` contiennent des donnees. Le serving actuel passe par D1 directement (C3).

### Note
RM a un low materialization state — le schema CQRS est en place (partitions, versions, queues) mais les donnees sont majoritairement dans D1. Ne pas conclure que RM est inutile : le design est intentionnel, l'activation complete n'est pas confirmee (C3). **Gate avant action** : confirmer dans le code si `RmModule` est actif et quels endpoints le consomment.

---

## D9 — Import / ETL / Normalisation

> Pipeline d'import catalogue, staging, normalisation, natural keys, mapping.

| Criticite | **P2** — Pipeline d'import, pas de serving direct |
|-----------|------|
| Taille | **~2 MB** |
| Tables | 26 |
| Owner technique | Backend / ImportModule |
| Decision status | **observe_activation** — pipeline structure, 19 tables vides |

### Tables Import

| Table | Lignes | Notes |
|-------|--------|-------|
| `__staging_brand_mapping` | 1.9K | Mapping marques staging |
| `__catalog_id_mapping` | 950 | Mapping IDs catalogue |
| `__substitution_logs` | 382 | Logs de substitution |
| `__catalog_import_history` | 3 | Historique imports |
| `am_2022_suppliers` | 1.1K | Fournisseurs 2022 |
| `import_batch` | 0 | Batches d'import |
| `__import_batch_contract` | 0 | Contrats de batch |
| `__import_proof` | 0 | Preuves d'import |
| `__import_manifest` | 0 | Manifestes |
| `__import_gate_status` | 0 | Statuts des gates |

### Tables Staging

`__staging_piece_compat` (0), `__staging_vehicle_mapping` (0), `__staging_article_mapping` (0), `stg_vehicle` (0), `stg_article` (0), `stg_compatibility` (0), `stg_brand` (0)

### Tables Normalisation / Natural Keys

`norm_vehicle` (0), `norm_brand` (0), `norm_article` (0), `natural_key_article` (0), `natural_key_brand` (0), `natural_key_vehicle` (0), `xref_article` (0), `xref_brand` (0), `xref_vehicle` (0), `decision_article` (0), `decision_brand` (0), `decision_compat` (0)

### Data classification (C2)
- **Source of truth (import control)** : `__staging_brand_mapping`, `__catalog_id_mapping`
- **Operational / audit** : `__catalog_import_history`, `__substitution_logs`, `am_2022_suppliers`
- **EMPTY_ACTIVE_DESIGN** : `import_batch`, `__import_batch_contract`, `__import_proof`, `__import_manifest`, `__import_gate_status` — schema d'import structure en place, activation non confirmee (C3)
- **EMPTY_ACTIVE_DESIGN (staging)** : `stg_vehicle`, `stg_article`, `stg_compatibility`, `stg_brand`, `__staging_piece_compat`, `__staging_vehicle_mapping`, `__staging_article_mapping` — tables staging suivent le pattern shadow/staging (C2)
- **EMPTY_ACTIVE_DESIGN (normalisation)** : `norm_vehicle`, `norm_brand`, `norm_article`, `natural_key_*`, `xref_*`, `decision_*` — pipeline normalisation/natural keys en place, activation non confirmee (C3)

### Note
Tables majoritairement vides — **EMPTY_ACTIVE_DESIGN** : le pipeline d'import/normalisation est structure (staging → normalisation → natural keys → decisions). Ne pas conclure "inutile" depuis "vide" — ces tables ont un design intent clair et attendent potentiellement un premier import batch.

---

## D10 — Quality, Monitoring & Observabilite

> Scores qualite, audits QA, lighthouse, crawl budget, admin health.

| Criticite | **P2** — Monitoring, pas de serving direct |
|-----------|------|
| Taille | **~3 MB** |
| Tables | 16 |
| Owner technique | Backend / AdminModule, QaModule |
| Decision status | **review** — 7 tables EMPTY_UNKNOWN a investiguer |

### Tables

| Table | Lignes | Notes |
|-------|--------|-------|
| `__qa_audit_issues` | 1.3K | Issues d'audit QA |
| `__quality_page_scores` | 799 | Scores qualite pages |
| `__quality_gamme_scores` | 232 | Scores qualite gammes |
| `__qa_protected_meta_hash` | 140 | Hash meta protege |
| `__qa_audit_runs` | 50 | Runs d'audit |
| `__qa_audit_alerts` | 24 | Alertes audit |
| `__admin_job_health` | 3 | Sante des jobs admin |
| `__agent_metrics` | 0 | Metriques agents |
| `__cron_runs` | 0 | Runs cron |
| `__lighthouse_runs` | 0 | Runs Lighthouse |
| `__lighthouse_alerts` | 0 | Alertes Lighthouse |
| `crawl_budget_experiments` | 1 | Experiences crawl budget |
| `crawl_budget_metrics` | 0 | Metriques crawl budget |
| `error_logs` | 0 | Logs erreurs |
| `error_statistics` | 0 | Stats erreurs |
| `golden_set_products` | 0 | Golden set test |

### Data classification (C2)
- **Source of truth** : `__qa_audit_runs`, `__qa_audit_issues`, `__qa_audit_alerts`, `__qa_protected_meta_hash`
- **Derived / scores** : `__quality_page_scores`, `__quality_gamme_scores`
- **Config** : `crawl_budget_experiments`, `golden_set_products`
- **Operational** : `__admin_job_health`
- **EMPTY_UNKNOWN** : `__agent_metrics`, `__cron_runs`, `__lighthouse_runs`, `__lighthouse_alerts`, `crawl_budget_metrics`, `error_logs`, `error_statistics` — consumer non confirme (C3)

---

## D11 — Commerce & Users

> Utilisateurs, sessions, promotions, avis, shipping, support, paiements historiques.

| Criticite | **P0** — Authentification et transactions |
|-----------|------|
| Taille | **~700 KB** |
| Tables | 11 |
| Owner technique | Backend / AuthModule, PaymentsModule |
| Decision status | **stabilize** — tables vestigiales pre-Redis a confirmer |

### Tables

| Table | Lignes | Notes |
|-------|--------|-------|
| `ic_postback` | 5.9K | Postbacks IC (tracking) |
| `promo_codes` | 8 | Codes promo |
| `quantity_discounts` | 6 | Remises quantite |
| `shipping_rates_cache` | 5 | Cache tarifs livraison |
| `users` | 2 | Utilisateurs (admin only en DB, clients via Supabase Auth) |
| `sessions` | 0 | Sessions (Redis en prod) |
| `password_resets` | 0 | Reset mots de passe |
| `promo_usage` | 0 | Usage promos |
| `support_tickets` | 0 | Tickets support |
| `ticket_responses` | 0 | Reponses tickets |
| `reviews` | 0 | Avis clients |

### Data classification (C2)
- **Source of truth** : `users`, `promo_codes`, `quantity_discounts`, `shipping_rates_cache`
- **Operational / tracking** : `ic_postback`
- **EMPTY_UNKNOWN** : `sessions` (Redis en prod — table potentiellement vestigiale), `password_resets`, `promo_usage`, `support_tickets`, `ticket_responses`, `reviews` — consumer non confirme (C3)

### Note
Le flux commerce actif depend encore partiellement de `___xtr_order*` (D2), notamment via certains chemins paiements / orders. En consequence, D2 ne peut pas etre considere archive-safe tant que ce couplage n'est pas retire. La table `users` ne contient que 2 admins — les clients sont dans Supabase Auth. Les tables vides (`sessions`, `support_tickets`, `reviews`) sont potentiellement des features non activees ou des vestiges pre-Redis (C3).

---

## D12 — Marketing & Video

> Planning marketing, social posts, backlinks, productions video.

| Criticite | **P3** — Non critique, fonctionnalites en construction |
|-----------|------|
| Taille | **~1 MB** |
| Tables | 18 (Marketing: 12, Video: 6) |
| Owner technique | Backend / MarketingModule |
| Decision status | **observe_activation** — EMPTY_ACTIVE_DESIGN massif, basse priorite |

### Tables Marketing (12)

| Table | Lignes | Notes |
|-------|--------|-------|
| `__marketing_content_roadmap` | 58 | Roadmap contenu |
| `__marketing_backlinks` | 122 | Backlinks |
| `__marketing_brand_rules` | 22 | Regles marque |
| `__marketing_kpi_snapshots` | 1 | KPI |

Tables vides : `__marketing_social_posts`, `__marketing_weekly_plans`, `__marketing_utm_registry`, `__marketing_content_library`, `__marketing_analytics_digests`, `__marketing_guest_posts`, `__marketing_outreach`, `__marketing_campaigns`

### Tables Video (6)

| Table | Lignes | Notes |
|-------|--------|-------|
| `__video_execution_log` | 9 | Log execution |
| `__video_productions` | 2 | Productions |
| `__video_audio_cache` | 1 | Cache audio |

Tables vides : `__video_assets`, `__video_variants`, `__video_templates`

### Data classification (C2)
- **Source of truth** : `__marketing_content_roadmap`, `__marketing_backlinks`, `__marketing_brand_rules`
- **Derived / operational** : `__marketing_kpi_snapshots`, `__video_productions`, `__video_execution_log`, `__video_audio_cache`
- **EMPTY_ACTIVE_DESIGN** : `__marketing_social_posts`, `__marketing_weekly_plans`, `__marketing_utm_registry`, `__marketing_content_library`, `__marketing_analytics_digests`, `__marketing_guest_posts`, `__marketing_outreach`, `__marketing_campaigns`, `__video_assets`, `__video_variants`, `__video_templates` — design intent present, activation non confirmee (C3)

---

## D13 — Config & System

> Configuration systeme, menus, pages legales, gates, pipeline.

| Criticite | **P1** — Config necessaire au fonctionnement |
|-----------|------|
| Taille | **~1.5 MB** |
| Tables | 12 |
| Owner technique | Backend / AppModule |
| Decision status | **stabilize** — 2 obsolete_candidates a confirmer |

### Tables

| Table | Lignes | Notes |
|-------|--------|-------|
| `___config` | 1 | Config principale |
| `___config_admin` | 11 | Config admin |
| `___meta_tags_ariane` | 5 | Breadcrumbs |
| `___legal_pages` | 16 | Pages legales |
| `___header_menu` | 6 | Menu header |
| `___footer_menu` | 13 | Menu footer |
| `gate_thresholds` | 17 | Seuils des gates |
| `__pipeline_chain_queue` | 3 | Queue pipeline chain |
| `pipeline_event_log` | 0 | Log evenements pipeline |
| `messages` | 0 | Messages (non utilise) |
| `___config_old` | 1 | Ancienne config |
| `___config_ip` | 3 | Config IP |

### Data classification (C2)
- **Source of truth / config** : `___config`, `___config_admin`, `___config_ip`, `___header_menu`, `___footer_menu`, `___legal_pages`, `___meta_tags_ariane`, `gate_thresholds`
- **Operational** : `__pipeline_chain_queue`, `pipeline_event_log`
- **EMPTY_OBSOLETE_CANDIDATE** : `___config_old` (1 row, suffixe `_old`), `messages` (0 rows) — consumer non confirme (C3)

---

## D14 — Gamme Aggregates & V-Level (Cross-cutting)

> Tables d'agregation gamme, metriques SEO, filtres, V-Level scoring.

| Criticite | **P1** — Alimente SEO et catalog |
|-----------|------|
| Taille | **~5 MB** |
| Tables | 6 |
| Owner technique | Backend / SeoModule, AdminModule |
| Decision status | **stabilize** — gamme_seo_audit reclasse EMPTY_ACTIVE_DESIGN (4 refs) |

### Tables

| Table | Lignes | Notes |
|-------|--------|-------|
| `gamme_aggregates` | 235 | Agregats gamme. 1.4M idx_scan, 1.9M updates |
| `gamme_filter_criteria` | 320 | Criteres de filtre par gamme |
| `gamme_seo_metrics` | 239 | Metriques SEO par gamme |
| `gamme_seo_audit` | 0 | Audit SEO gamme |
| `__v_level_computed` | 16 | V-Level calcule |
| `__v_level_raw` | 16 | V-Level brut |

### Data classification (C2)
- **Source of truth** : `gamme_aggregates` (source pour SEO et catalog)
- **Derived** : `gamme_filter_criteria`, `gamme_seo_metrics`, `__v_level_computed`
- **Source data** : `__v_level_raw`
- **EMPTY_ACTIVE_DESIGN** : `gamme_seo_audit` (0 rows) — 4 refs actives confirmees (`gamme-seo-audit.service.ts`, `seo-cockpit.service.ts`), audit trail fonctionnel

---

## D15 — Security & Governance

> Killswitch, airlock, quarantine — systemes de protection.

| Criticite | **P1** — Securite de la pipeline |
|-----------|------|
| Taille | **~200 KB** |
| Tables | 7 |
| Owner technique | Backend / SecurityModule |
| Decision status | **observe_activation** — activation conditionnelle via feature flags |

### Tables

| Table | Lignes | Notes |
|-------|--------|-------|
| `__quarantine_rules` | 4 | Regles quarantine |
| `__quarantine_items` | 0 | Items en quarantine |
| `__quarantine_history` | 0 | Historique |
| `_killswitch_breakglass` | 0 | Breakglass killswitch |
| `_killswitch_audit` | 0 | Audit killswitch |
| `__airlock_bundles` | 0 | Bundles airlock |
| `__db_governance_snapshots` | 0+ | Snapshots M1-M6 historiques (Phase 2) |

### Data classification (C2)
- **Source of truth** : `__quarantine_rules`
- **Operational** : `__quarantine_items`, `__quarantine_history`, `_killswitch_breakglass`, `_killswitch_audit`, `__airlock_bundles`, `__db_governance_snapshots`
- **EMPTY_ACTIVE_DESIGN** : la majorite des tables sont vides — systeme de securite en place (code actif dans SecurityModule), activation conditionnelle via feature flags (C3)

---

## Vues (40)

### Par domaine

| Domaine | Vues |
|---------|------|
| **KG** (13) | `kg_active_edges`, `kg_active_nodes`, `kg_diagnosis_stats`, `kg_feedback_stats`, `kg_maintenance_summary`, `kg_observables_with_context`, `kg_rag_sync_errors`, `kg_rag_sync_stats`, `kg_truth_labels_dashboard`, `kg_truth_labels_stats` |
| **SEO** (12) | `seo_ab_testing_formula_ctr`, `seo_ab_testing_nouns`, `seo_ab_testing_top_formulas`, `seo_ab_testing_verbs`, `seo_link_ctr`, `v_seo_blocking_issues`, `v_seo_crawl_stats_7d`, `v_seo_internal_link_stats`, `v_seo_interpolation_alerts_24h`, `v_seo_interpolation_alerts_weekly`, `v_seo_keywords_unmatched`, `v_seo_last_googlebot_crawl`, `v_seo_quality_stats` |
| **Pipeline** (4) | `v_conseil_pack_coverage`, `v_pipeline_batch_summary`, `v_pipeline_dashboard`, `v_pipeline_step_stats` |
| **Monitoring** (4) | `v_index_usage`, `v_performance_monitoring`, `v_table_health`, `v_thresholds_by_family`, `v_thresholds_comparison` |
| **Catalog** (2) | `__pg_gammes`, `v_pieces_seo_safe` |
| **Import** (3) | `v_import_lock_status`, `v_substitution_daily`, `v_substitution_funnel` |
| **Sitemap** (2) | `__sitemap_p_link_index`, `__sitemap_vehicules` |
| **Gamme** (1) | `v_gamme_readiness` |

---

## Triggers (41)

### Par table cible

| Table | Triggers | Impact |
|-------|----------|--------|
| `__seo_keywords` | **7** | updated_at, sync_aggregates (INSERT/UPDATE/DELETE), v2_repetitions (INSERT/UPDATE + DELETE), vlevel_integrity (INSERT/UPDATE) |
| `pieces` | 2 | search_vector_update (INSERT/UPDATE) |
| `__rag_knowledge` | 2 | tsvector (INSERT/UPDATE) |
| `__seo_reference` | 2 | ref_search_vector (INSERT/UPDATE) |
| `__seo_r3_keyword_plan` | 2 | kp_validated (INSERT/UPDATE) → pipeline chain |
| `__seo_r6_keyword_plan` | 2 | r6_kp_validated (INSERT/UPDATE) → pipeline chain |
| `gamme_seo_metrics` | 2 | v2_unique (INSERT/UPDATE) |
| Autres (21 tables) | 1 chacun | updated_at ou validation |

### Trigger le plus charge (C1)
`__seo_keywords` avec 5 triggers — chaque INSERT/UPDATE declenche 4 fonctions en cascade. Impact performance a confirmer par profiling (C3).

---

## Fonctions (306)

### Par domaine fonctionnel (C2 — infere depuis nommage)

| Domaine | Count | Exemples |
|---------|-------|----------|
| KG / Diagnostic | ~60 | `kg_diagnose_*`, `kg_calculate_*`, `kg_record_*` |
| Catalog / Listing | ~40 | `get_pieces_for_type_gamme_v4`, `get_gamme_page_data_optimized` |
| Import / ETL | ~35 | `create_import_batch`, `check_gate_*`, `merge_staging_*` |
| SEO | ~30 | `process_seo_template`, `get_seo_observable_*` |
| RM / Serving | ~15 | `rm_get_listing_page`, `rm_get_page_complete_v2` |
| System (trigram, unaccent) | ~70 | Extensions PostgreSQL internes |
| Autres (vehicle, auth, cart) | ~56 | `get_vehicle_page_data_optimized`, `auth_resolve_user` |

---

## Resume des anomalies detectees

| # | Anomalie | Impact | Confiance | Domaine | Decision gate |
|---|---------|--------|-----------|---------|---------------|
| A1 | **~24 GB d'index a 0 scan** (15.4 GB D2, 8 GB D1) | Gaspillage stockage + ralentissement writes | C1 (mesure) | D1, D2 | Code search consumers + EXPLAIN + verifier fenetre stats |
| A2 | `__seo_quality_log` : 104M idx_scan, 0 rows | **RESOLVED_C4** — extinct trigger, 5 indexes dropped | C1 → C4 | D3 | Clos. Source = trigger historique eteint. Indexes phantom supprimes. |
| A3 | `__seo_keywords` : 5 triggers en cascade | Goulot potentiel sur INSERT/UPDATE | C1 (mesure) | D3 | Profiler un INSERT + mesurer latence en preprod |
| A4 | 3 tables `__cross_gamme_car*` | Duplication potentielle (C3) | C2 (nommage) | D4 | Code search : quelle version est active ? |
| A5 | D2 Legacy : 25 GB, usage non confirme en hot path | 24% de la DB, utilite non confirmee | C1 (taille) / C3 (usage) | D2 | Code search + verifier obligations retention legale |
| A6 | RM : low materialization state | Architecture CQRS en place, non exploitee | C1 (taille) / C3 (intention) | D8 | Confirmer si RmModule est actif + endpoints consumers |
| A7 | D9 Import : 26 tables dont 19 vides | Pipeline structure, non materialize | C1 (lignes) / C2 (design) | D9 | Confirmer si premier import est planifie |
| A8 | D7 KG : 33 tables dont 13 vides | Design intent present, activation non confirmee | C1 (lignes) / C2 (60 RPC) | D7 | Confirmer feature flags + dataset initial |
| A9 | `__rag_knowledge_backup_20260222` | Backup date, obsolete_candidate | C2 (nommage) | D6 | Confirmer corpus actif complet avant suppression |
| A10 | `__blog_advice_old` : 0 rows | obsolete_candidate (suffixe `_old`) | C2 (nommage) | D5 | Code search pour confirmer absence de references |

---

## Quick win candidates (sous gate)

> Aucune action directe. Chaque candidat doit passer sa gate avant execution.

| # | Candidat | Gain estime | Risque | Hypothese (C3) | Gate requise | Mode d'execution |
|---|----------|-------------|--------|-----------------|--------------|------------------|
| QW1 | DROP index `idx____xtr_msg_msg_content` | 14 GB | R0 | Aucun consumer actif (0 scan) | Code search `xtr_msg` + EXPLAIN si requetes trouvees | `DROP INDEX CONCURRENTLY` (reversible via `CREATE INDEX CONCURRENTLY`) |
| QW2 | DROP 5 index `___xtr_msg` secondaires | 1.4 GB | R0 | Aucun consumer actif (0 scan) | Meme gate que QW1 | `DROP INDEX CONCURRENTLY` par index |
| QW3 | DROP index D1 a 0 scan | ~8 GB | R1 | Aucun consumer actif (0 scan sur fenetre observee) | Code search + EXPLAIN des 5 requetes critiques U1/U2 + verifier fenetre stats | `DROP INDEX CONCURRENTLY` — un par un, mesurer impact |
| QW4 | DROP table `__rag_knowledge_backup_20260222` | 1.3 MB | R0 | Backup obsolete (date dans le nom) | Confirmer corpus `__rag_knowledge` complet (367 rows >= 314 rows backup) | `DROP TABLE` apres backup de validation |
| QW5 | DROP table `__blog_advice_old` | 280 KB | R0 | Obsolete (suffixe `_old`, 0 rows) | Code search `blog_advice_old` = 0 resultats | `DROP TABLE` |
| QW6 | ~~Investiguer A2~~ **RESOLVED_C4** | Performance | R0 | Source identifiee = extinct trigger | 5 indexes phantom supprimes, 2 vues phantom supprimees | Clos — aucune action restante |

---

## Objets reclasses apres code search initial (2026-03-14)

> Code search backend execute (`.from()`, `.rpc()`). Statuts mis a jour avec evidence. Voir limites ci-dessous.

| Table | Domaine | Lignes | Ancien statut | Statut confirme | Evidence |
|-------|---------|--------|---------------|-----------------|----------|
| `gamme_seo_audit` | D14 | 0 | EMPTY_UNKNOWN | **EMPTY_ACTIVE_DESIGN** | 4 refs : `gamme-seo-audit.service.ts`, `seo-cockpit.service.ts` — audit trail actif |
| `vehicule_v1_dominant` | D4 | 0 | EMPTY_UNKNOWN | **EMPTY_STAGING** | SQL test seulement (`vlevel_health_checks.sql`) — pas de consumer applicatif |
| `__seo_quality_log` | D3 | 0 | EMPTY_UNKNOWN | **RESOLVED_C4** | 0 refs code, 104M idx_scan — source = extinct trigger, 5 indexes + 2 vues supprimes |
| `__agent_runs` | D6 | 5 | Consumer non confirme | **APP_ORPHAN_CONFIRMED** | 0 refs code. `__agentic_runs` = 178 refs — doublon confirme |
| `messages` | D13 | 0 | EMPTY_UNKNOWN | **APP_ORPHAN_CONFIRMED** | 0 refs `.from('messages')`, type definitions seulement |
| `sessions` | D11 | 0 | EMPTY_UNKNOWN | **APP_ORPHAN_CONFIRMED** | 0 refs `.from('sessions')`, Redis en prod |
| `___config_old` | D13 | 1 | EMPTY_OBSOLETE_CANDIDATE | **APP_ORPHAN_CONFIRMED** | 0 refs code, suffixe `_old` |
| `products` | D1 | 0 | EMPTY_UNKNOWN | **APP_ORPHAN_CONFIRMED** | 0 refs `.from('products')`, donnees dans `pieces` |
| `categories` | D1 | 0 | EMPTY_UNKNOWN | **APP_ORPHAN_CONFIRMED** | 0 refs `.from('categories')`, donnees dans `pieces_gamme` |
| `__blog_advice_old` | D5 | 0 | EMPTY_OBSOLETE_CANDIDATE | **APP_ORPHAN_CONFIRMED** | 0 refs code, suffixe `_old` |
| `__rag_knowledge_backup_20260222` | D6 | 314 | EMPTY_OBSOLETE_CANDIDATE | **APP_ORPHAN_CONFIRMED** | 0 refs code, corpus actif (367) > backup (314) |
| `__cross_gamme_car_new2` | D4 | 165K | (non liste) | **ORPHAN** | 0 refs code, 30 MB inutilises |

> **Limites du code search** : Le scan backend (`.from()`, `.rpc()`) ne couvre pas :
> vues SQL dependantes, fonctions PostgreSQL internes, triggers indirects,
> cron/jobs hors backend, acces via SQL brut/psql/outils d'admin.
> Un statut `APP_ORPHAN_CONFIRMED` signifie 0 consumer applicatif confirme, pas 0 usage absolu.

---

## Synthese des tables vides par statut

| Statut | Count | Signification |
|--------|-------|---------------|
| **EMPTY_ACTIVE_DESIGN** | ~56 | Schema en place, activation non confirmee. Ne pas supprimer. |
| **EMPTY_STAGING** | 1 | Usage test/validation uniquement. |
| **RESOLVED_C4** | 1 | Anciennement UNEXPLAINED_DB_ACTIVITY. Source identifiee (extinct trigger), indexes/vues phantom supprimes. |
| **APP_ORPHAN_CONFIRMED** | 8 | 0 refs code backend. Candidats DROP sous gate — retention policy et usages hors-app non verifies. |
| **ORPHAN** | 1 | Table avec donnees mais 0 consumer. Candidat DROP apres backup. |

---

## Priorite de travail proposee

| Rang | Domaine | Justification |
|------|---------|---------------|
| 1 | D1 — Catalog Core | 73% de la DB, P0, 8 GB index review_for_drop |
| 2 | D2 — Legacy/XTR | 24% de la DB, 15.4 GB index, review_for_archive |
| 3 | D3 — SEO & Sitemap | P1, 5 triggers, RESOLVED_C4, 55 tables |
| 4 | D4 — Vehicle | P0, duplication cross_gamme_car |
| 5 | D8 — Read Model | P1, activation state a confirmer |
| 6 | D13 — Config & System | P1, obsolete_candidates |
| 7 | D9 — Import/ETL | P2, 19 tables vides a clarifier |
| 8 | D10 — Quality/Monitoring | P2, 7 tables EMPTY_UNKNOWN a investiguer |
| 9 | D6 — RAG & AI | P2, backup orphelin, doublon confirme (`__agent_runs`) |
| 10 | D5 — Blog/Content | P1, 1 obsolete_candidate |
| 11 | D11 — Commerce/Users | P0 mais petit, tables vestigiales |
| 12 | D14 — Gamme Aggregates | P1, gamme_seo_audit reclasse EMPTY_ACTIVE_DESIGN |
| 13 | D15 — Security/Governance | P1, activation conditionnelle |
| 14 | D7 — KG/Diagnostic | P3, EMPTY_ACTIVE_DESIGN massif |
| 15 | D12 — Marketing/Video | P3, EMPTY_ACTIVE_DESIGN |

---

## Non-goals de ce document

Ce document ne decide pas a lui seul :
- la suppression d'une table
- la suppression d'un index
- la fusion de tables
- l'activation d'un pipeline
- la desactivation d'un module

Ces decisions doivent passer par :
- code search (confirmation des consumers)
- execution-map (validation des flux critiques)
- perf-findings (preuves mesurees)
- change-control-plan (procedure shadow/canary/rollback)
- validation preprod/canary si necessaire

---

## Statut de validation

| Couche | Statut | Prochaine action |
|--------|--------|------------------|
| Domain map | **baseline accepted** | Gele — modifiable uniquement sur evidence nouvelle |
| Validation code/RPC | **partial** | Code search initial realise (2026-03-14), execution-map a completer par usage critique |
| Validation perf critique | pending | perf-findings.md (EXPLAIN ANALYZE) |
| Validation remediation | pending | remediation-plan.md (sequence + risques) |

---

_Derniere mise a jour: 2026-03-14_
_Genere a partir de l'introspection DB reelle — niveau de confiance C1/C2/C3 annote_
