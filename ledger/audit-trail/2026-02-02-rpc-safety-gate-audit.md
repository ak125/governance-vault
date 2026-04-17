# RPC SAFETY GATE — MASSDOC

**Date** : 2026-02-02
**Projet** : massdoc (`cxpojprgwgubzjyqzmoq`)
**Total RPC** : 233 fonctions
**Mode** : READ-ONLY Audit

---

## RÉSUMÉ EXÉCUTIF

| Catégorie | Count | Action |
|-----------|-------|--------|
| **ALLOWLIST (READ_SAFE)** | 137 | Accès autorisé |
| **DENYLIST (WRITE_DANGEROUS)** | 23 | Bloquer en DEV/PROD |
| **DENYLIST (SECURITY_DEFINER)** | 73 | Audit requis |
| **SYSTEM (pg_trgm, etc.)** | 23 | Ignorer |

**Verdict** : 73 fonctions SECURITY DEFINER + 23 WRITE_DANGEROUS = **96 RPC à bloquer** minimum.

---

## SECTION 1 — CLASSIFICATION DÉTAILLÉE

### 1.1 DENYLIST — WRITE_DANGEROUS (P0)

| # | Fonction | Risque | Pattern Détecté |
|---|----------|--------|-----------------|
| 1 | `delete_duplicates_batch` | **CRITIQUE** | DELETE massif, batch loop |
| 2 | `delete_first_records_batch` | **CRITIQUE** | DELETE massif, batch loop |
| 3 | `rollback_switch` | **CRITIQUE** | Rollback état prod |
| 4 | `switch_to_next` | **CRITIQUE** | Switch état prod |
| 5 | `apply_decisions_shadow` | **ÉLEVÉ** | Apply decisions |
| 6 | `apply_quarantine_rules` | **ÉLEVÉ** | Modifie quarantine |
| 7 | `run_import_pipeline` | **ÉLEVÉ** | Pipeline complet |
| 8 | `finalize_import_batch` | **ÉLEVÉ** | Finalise batch |
| 9 | `execute_diff_apply_workflow` | **ÉLEVÉ** | Workflow apply |
| 10 | `prepare_shadow_tables` | **ÉLEVÉ** | Shadow tables |
| 11 | `move_decisions_to_quarantine` | **ÉLEVÉ** | Move to quarantine |
| 12 | `create_index_async` | **MOYEN** | DDL asynchrone |
| 13 | `create_composite_index_async` | **MOYEN** | DDL asynchrone |
| 14 | `create_rm_listing_products_partition` | **MOYEN** | DDL partition |
| 15 | `ensure_rm_partition` | **MOYEN** | DDL partition |
| 16 | `cleanup_old_pipeline_logs` | **MOYEN** | DELETE logs |
| 17 | `cleanup_expired_carts` | **MOYEN** | DELETE carts |
| 18 | `cleanup_expired_password_resets` | **MOYEN** | DELETE resets |
| 19 | `cleanup_old_error_logs` | **MOYEN** | DELETE logs |
| 20 | `purge_seo_interpolation_alerts` | **MOYEN** | DELETE alerts |
| 21 | `aggregate_seo_link_metrics` | **MOYEN** | INSERT/UPDATE |
| 22 | `refresh_gamme_aggregates` | **MOYEN** | INSERT/UPDATE |
| 23 | `refresh_temperature_scores` | **MOYEN** | UPDATE |

### 1.2 DENYLIST — SECURITY_DEFINER (73 fonctions)

**Toutes ces fonctions s'exécutent avec les privilèges du propriétaire (service_role).**

```
acquire_import_lock, add_to_quarantine, all_gates_passed, apply_decisions_shadow,
apply_quarantine_rules, build_article_decisions, build_brand_decisions, can_merge_batch,
check_all_gates, check_anti_purge, check_gate, check_gate_g0, check_gate_g1, check_gate_g2,
check_gate_g3, check_gate_g4, check_manifest_complete, cleanup_old_pipeline_logs,
complete_pipeline_step, create_batch_contract, create_batch_contract_v2, create_composite_index_async,
create_import_batch, create_index_async, create_rm_listing_products_partition, diagnose_symptoms,
ensure_rm_partition, execute_diff_apply_workflow, fail_pipeline_step, finalize_import_batch,
get_batch_report, get_brand_bestsellers_optimized, get_brand_page_data_optimized,
get_context_questions, get_decision_report, get_gamme_page_data_optimized, get_homepage_data_optimized,
get_import_gate_report, get_listing_products_for_build, get_nk_stats, get_oem_refs_for_vehicle,
get_or_create_brand_nk, get_pieces_for_type_gamme, get_pieces_for_type_gamme_v2,
get_pieces_for_type_gamme_v3, get_pieces_for_type_gamme_v4, get_purchase_excluded_ids,
get_quarantine_dashboard, get_quarantine_stats, get_seo_excluded_ids, get_substitution_data,
get_symptoms_by_subsystem, get_vehicle_page_data_optimized, init_import_gates, is_quarantined,
log_pipeline_event, move_decisions_to_quarantine, normalize_batch_brands, populate_golden_set,
prepare_shadow_tables, release_import_lock, resolve_batch_brands, resolve_brand_multilevel,
resolve_quarantine_item, rm_get_listing_page, rm_get_page_complete, rm_get_page_complete_v2,
rm_health, rollback_switch, run_import_pipeline, switch_to_next, update_batch_contract, validate_shadow
```

### 1.3 ALLOWLIST — READ_SAFE (137 fonctions)

**Fonctions de lecture pure, sans effets de bord.**

#### Calcul & Validation (IMMUTABLE/STABLE)
```
calc_article_bf, calc_brand_bf, calc_business_fingerprint, calc_vehicle_bf,
calculate_product_score, calculate_quality_score, calculate_seo_score_gate,
calculate_text_similarity, check_*, compute_seo_indexable, count_words,
decode_html_entities, determine_*, evaluate_*, fix_utf8_encoding,
get_action_definition, get_penalty, get_threshold, get_zone_severity,
jsonb_object_keys_count, map_facets_to_filter_keys, match_keyword_to_type,
normalize_brand_name, process_prix_pas_cher, process_seo_switch, process_seo_template,
validate_*
```

#### Getters (SELECT only)
```
get_all_seo_observables_for_sitemap, get_auto_types_batch, get_automecanik_id,
get_brands_with_pieces, get_cart_stats, get_catalog_*, get_external_id,
get_extras_v4_type_ids, get_facet_config, get_family_completeness_stats,
get_gamme_data_v3, get_gamme_page_data, get_gammes_*, get_listing_products_extended,
get_listing_products_for_build_v2, get_mandatory_fields, get_missing_v4_type_ids,
get_seo_*, get_sitemap_*, get_stabilize_pages, get_staging_stats,
get_subsystem_components, get_top_money_gammes, get_vehicle_compatible_gammes_php,
get_vlevel_*, is_import_running, search_*, show_limit, table_exists,
test_pieces_relation_access
```

#### KG Diagnostic (READ)
```
kg_calculate_*, kg_check_safety_gate, kg_diagnose_*, kg_explain_*,
kg_find_*, kg_generate_*, kg_get_*, kg_quality_report, kg_rag_file_needs_sync,
kg_rag_get_node_id
```

#### Triggers (contexte limité)
```
__seo_observable_updated_at, auto_promote_to_v1, check_v2_uniqueness,
kg_cases_updated_at, kg_safety_triggers_updated_at, kg_truth_labels_updated_at,
kg_update_updated_at, sync_keywords_to_gamme_aggregates, update_*_updated_at,
update_cart_totals*, update_pieces_search_vector, validate_vlevel_integrity
```

### 1.4 SYSTEM FUNCTIONS (Ignorer - pg_trgm, unaccent)

```
gin_extract_query_trgm, gin_extract_value_trgm, gin_trgm_consistent, gin_trgm_triconsistent,
gtrgm_compress, gtrgm_consistent, gtrgm_decompress, gtrgm_distance, gtrgm_in,
gtrgm_options, gtrgm_out, gtrgm_penalty, gtrgm_picksplit, gtrgm_same, gtrgm_union,
set_limit, show_trgm, similarity, similarity_dist, similarity_op, strict_word_similarity*,
unaccent, unaccent_init, unaccent_lexize, word_similarity*
```

---

## SECTION 2 — TOP 20 FONCTIONS LES PLUS RISQUÉES

| Rang | Fonction | Risque | Security | Raison |
|------|----------|--------|----------|--------|
| 1 | `delete_duplicates_batch` | P0 | INVOKER | DELETE en boucle, jusqu'à 31M lignes |
| 2 | `delete_first_records_batch` | P0 | INVOKER | DELETE en boucle, jusqu'à 31M lignes |
| 3 | `rollback_switch` | P0 | DEFINER | Rollback état production |
| 4 | `switch_to_next` | P0 | DEFINER | Switch état production |
| 5 | `run_import_pipeline` | P0 | DEFINER | Pipeline import complet |
| 6 | `apply_decisions_shadow` | P0 | DEFINER | Apply batch decisions |
| 7 | `execute_diff_apply_workflow` | P0 | DEFINER | Workflow diff + apply |
| 8 | `apply_quarantine_rules` | P1 | DEFINER | Modifie quarantine items |
| 9 | `finalize_import_batch` | P1 | DEFINER | Finalise import |
| 10 | `prepare_shadow_tables` | P1 | DEFINER | Prepare shadow |
| 11 | `move_decisions_to_quarantine` | P1 | DEFINER | Move to quarantine |
| 12 | `create_index_async` | P1 | DEFINER | DDL CREATE INDEX |
| 13 | `create_composite_index_async` | P1 | DEFINER | DDL CREATE INDEX |
| 14 | `create_rm_listing_products_partition` | P1 | DEFINER | DDL partition |
| 15 | `ensure_rm_partition` | P1 | DEFINER | DDL partition |
| 16 | `get_or_create_brand_nk` | P1 | DEFINER | INSERT sur collision |
| 17 | `build_article_decisions` | P1 | DEFINER | Build decisions |
| 18 | `build_brand_decisions` | P1 | DEFINER | Build decisions |
| 19 | `resolve_quarantine_item` | P1 | DEFINER | UPDATE quarantine |
| 20 | `populate_golden_set` | P2 | DEFINER | INSERT golden set |

---

## SECTION 3 — FICHIERS JSON

### 3.1 rpc_inventory.json

```json
{
  "generated_at": "2026-02-02T12:00:00Z",
  "project_id": "cxpojprgwgubzjyqzmoq",
  "total_functions": 233,
  "summary": {
    "security_definer": 73,
    "security_invoker": 160,
    "volatile": 189,
    "stable": 36,
    "immutable": 31
  }
}
```

### 3.2 rpc_allowlist.json

```json
{
  "version": "1.0.0",
  "generated_at": "2026-02-02T12:00:00Z",
  "description": "RPC READ_SAFE - Autorisées pour tous les rôles",
  "total": 137,
  "functions": [
    {"name": "calc_article_bf", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "calc_brand_bf", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "calc_business_fingerprint", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "calc_vehicle_bf", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "calculate_product_score", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "calculate_quality_score", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "calculate_seo_score_gate", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "calculate_text_similarity", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "check_all_content_lengths", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_all_object_associations", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_ambiguous_terms", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_claims_tiered", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_compatibility_proof", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_completeness", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_confusion_pairs", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_content_length", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_cooccurrence", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_database_health", "volatility": "VOLATILE", "reason": "Monitoring only"},
    {"name": "check_duplicate_content", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_freinage_rules", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_heading_structure", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_internal_contradictions", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_lexique_confusion", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_lexique_cross_component", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_object_associations", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_product_completeness", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_product_completeness_v2", "volatility": "STABLE", "reason": "Validation only"},
    {"name": "check_rm_products_integrity", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_subsystem_integrity", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_threshold", "volatility": "STABLE", "reason": "Validation only"},
    {"name": "check_unresolved_variables", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_variable_hallucination", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_vehicle_compatibility_claim", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "check_vehicle_compatibility_full", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "compute_seo_indexable", "volatility": "STABLE", "reason": "Pure calculation"},
    {"name": "count_sitemap_urls_by_temperature", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "count_words", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "decode_html_entities", "volatility": "IMMUTABLE", "reason": "Pure transformation"},
    {"name": "detect_components_in_text", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "determine_indexation_status", "volatility": "VOLATILE", "reason": "Pure calculation"},
    {"name": "determine_product_quality", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "determine_stock_status", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "evaluate_business_rules", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "evaluate_rule_condition", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "fix_utf8_encoding", "volatility": "VOLATILE", "reason": "Pure transformation"},
    {"name": "get_action_definition", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_all_seo_observables_for_sitemap", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_auto_types_batch", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_automecanik_id", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_brands_with_pieces", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_cart_stats", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_catalog_families_for_vehicle", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_catalog_families_for_vehicle_optimized", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_catalog_hierarchy_optimized", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_catalog_legacy", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_catalog_mapping_stats", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_catalog_type_ids_for_gamme", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_external_id", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_extras_v4_type_ids", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_facet_config", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_family_completeness_stats", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_gamme_data_v3", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_gamme_page_data", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_gammes_for_family_and_vehicle", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_gammes_with_pieces", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_listing_products_extended", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_listing_products_for_build_v2", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_mandatory_fields", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_missing_v4_type_ids", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_penalty", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_seo_critical_alerts", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_seo_observable_by_slug", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_seo_observables_by_cluster", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_seo_quality_daily_stats", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_seo_reference_by_slug", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_sitemap_urls_by_temperature", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_stabilize_pages", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_staging_stats", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_subsystem_components", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_threshold", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_top_money_gammes", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_vehicle_compatible_gammes_php", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_vlevel_champions", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_vlevel_dashboard", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "get_vlevel_data", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_vlevel_section_k_extras", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_vlevel_section_k_metrics", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_vlevel_section_k_missing", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "get_zone_severity", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "is_import_running", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "jsonb_object_keys_count", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "kg_calculate_adapted_interval", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_calculate_bayesian_weight", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "kg_calculate_confidence_score", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_calculate_risk_level", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_calculate_truth_label_reliability", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_calculate_weight_with_truth_labels", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "kg_check_safety_gate", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_diagnose_by_labels", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_diagnose_contextual", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_diagnose_vehicle_aware", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_diagnose_with_explainable_score", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_diagnose_with_safety", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_explain_diagnosis_result", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_find_actions_for_fault", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_find_faults_from_observables", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_find_parts_for_fault", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_generate_batch_explanations", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_generate_explainable_diagnostic", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_get_edge_type_weight_multiplier", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "kg_get_input_type_confidence", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "kg_get_learning_stats", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_get_vehicle_maintenance_schedule", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_get_vehicle_recalls", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_quality_report", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_rag_file_needs_sync", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "kg_rag_get_node_id", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "map_facets_to_filter_keys", "volatility": "IMMUTABLE", "reason": "Pure calculation"},
    {"name": "match_keyword_to_type", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "match_keywords_batch", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "match_keywords_batch_clean", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "normalize_brand_name", "volatility": "IMMUTABLE", "reason": "Pure transformation"},
    {"name": "process_prix_pas_cher", "volatility": "IMMUTABLE", "reason": "Pure transformation"},
    {"name": "process_seo_switch", "volatility": "IMMUTABLE", "reason": "Pure transformation"},
    {"name": "process_seo_template", "volatility": "STABLE", "reason": "Pure transformation"},
    {"name": "search_pieces_fts", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "search_pieces_hybrid", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "search_rag_knowledge", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "search_seo_observable_by_dtc", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "show_limit", "volatility": "STABLE", "reason": "SELECT only"},
    {"name": "table_exists", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "test_pieces_relation_access", "volatility": "VOLATILE", "reason": "SELECT only"},
    {"name": "validate_content_full", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "validate_lexique_allumage", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "validate_lexique_amortisseur", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "validate_lexique_direction", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "validate_lexique_embrayage", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "validate_lexique_entrainement", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "validate_lexique_freinage", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "validate_lexique_support_moteur", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "validate_seo_content", "volatility": "VOLATILE", "reason": "Validation only"},
    {"name": "validate_staging_brands", "volatility": "VOLATILE", "reason": "Validation only"}
  ]
}
```

### 3.3 rpc_denylist.json

```json
{
  "version": "1.0.0",
  "generated_at": "2026-02-02T12:00:00Z",
  "description": "RPC WRITE_DANGEROUS + SECURITY_DEFINER - Bloquer en DEV, restreindre service_role en PROD",
  "total": 96,
  "categories": {
    "P0_CRITICAL": {
      "count": 6,
      "access": "BLOCK_ALL",
      "functions": [
        {"name": "delete_duplicates_batch", "risk": "DELETE massif jusqu'à 31M lignes"},
        {"name": "delete_first_records_batch", "risk": "DELETE massif jusqu'à 31M lignes"},
        {"name": "rollback_switch", "risk": "Rollback état production"},
        {"name": "switch_to_next", "risk": "Switch état production"},
        {"name": "run_import_pipeline", "risk": "Pipeline import complet"},
        {"name": "apply_decisions_shadow", "risk": "Apply batch decisions"}
      ]
    },
    "P1_HIGH": {
      "count": 17,
      "access": "SERVICE_ROLE_ONLY",
      "functions": [
        {"name": "execute_diff_apply_workflow", "risk": "Workflow diff + apply"},
        {"name": "apply_quarantine_rules", "risk": "Modifie quarantine items"},
        {"name": "finalize_import_batch", "risk": "Finalise import batch"},
        {"name": "prepare_shadow_tables", "risk": "Prepare shadow tables"},
        {"name": "move_decisions_to_quarantine", "risk": "Move to quarantine"},
        {"name": "create_index_async", "risk": "DDL CREATE INDEX"},
        {"name": "create_composite_index_async", "risk": "DDL CREATE INDEX"},
        {"name": "create_rm_listing_products_partition", "risk": "DDL partition"},
        {"name": "ensure_rm_partition", "risk": "DDL partition"},
        {"name": "get_or_create_brand_nk", "risk": "INSERT on conflict"},
        {"name": "build_article_decisions", "risk": "Build decisions"},
        {"name": "build_brand_decisions", "risk": "Build decisions"},
        {"name": "resolve_quarantine_item", "risk": "UPDATE quarantine"},
        {"name": "normalize_batch_brands", "risk": "UPDATE batch"},
        {"name": "resolve_batch_brands", "risk": "UPDATE batch"},
        {"name": "resolve_brand_multilevel", "risk": "UPDATE brand"},
        {"name": "validate_shadow", "risk": "Validate shadow"}
      ]
    },
    "P2_MEDIUM": {
      "count": 73,
      "access": "SERVICE_ROLE_ALLOWLIST",
      "reason": "SECURITY_DEFINER - toutes les fonctions avec élévation de privilèges",
      "functions": [
        "acquire_import_lock", "add_to_quarantine", "all_gates_passed",
        "can_merge_batch", "check_all_gates", "check_anti_purge", "check_gate",
        "check_gate_g0", "check_gate_g1", "check_gate_g2", "check_gate_g3", "check_gate_g4",
        "check_manifest_complete", "cleanup_old_pipeline_logs", "complete_pipeline_step",
        "create_batch_contract", "create_batch_contract_v2", "create_import_batch",
        "diagnose_symptoms", "fail_pipeline_step", "get_batch_report",
        "get_brand_bestsellers_optimized", "get_brand_page_data_optimized",
        "get_context_questions", "get_decision_report", "get_gamme_page_data_optimized",
        "get_homepage_data_optimized", "get_import_gate_report", "get_listing_products_for_build",
        "get_nk_stats", "get_oem_refs_for_vehicle", "get_pieces_for_type_gamme",
        "get_pieces_for_type_gamme_v2", "get_pieces_for_type_gamme_v3", "get_pieces_for_type_gamme_v4",
        "get_purchase_excluded_ids", "get_quarantine_dashboard", "get_quarantine_stats",
        "get_seo_excluded_ids", "get_substitution_data", "get_symptoms_by_subsystem",
        "get_vehicle_page_data_optimized", "init_import_gates", "is_quarantined",
        "log_pipeline_event", "populate_golden_set", "release_import_lock",
        "rm_get_listing_page", "rm_get_page_complete", "rm_get_page_complete_v2",
        "rm_health", "update_batch_contract"
      ]
    }
  }
}
```

---

## SECTION 4 — RECOMMANDATIONS

### 4.1 Accès par Environnement

| Environnement | ALLOWLIST | DENYLIST P0 | DENYLIST P1 | DENYLIST P2 |
|---------------|-----------|-------------|-------------|-------------|
| **DEV** | Libre | **BLOQUER** | service_role | service_role |
| **STAGING** | Libre | **BLOQUER** | service_role | service_role |
| **PROD** | Libre | **BLOQUER** | service_role + approval | service_role |

### 4.2 Actions Immédiates (P0)

1. **Révoquer l'accès public** aux 6 fonctions P0 CRITICAL
2. **Créer un rôle `rpc_admin`** avec accès restreint aux P1/P2
3. **Logger tous les appels** aux fonctions SECURITY_DEFINER
4. **Migrer vers INVOKER** les getters SECURITY_DEFINER qui n'en ont pas besoin

### 4.3 Fonctions SECURITY_DEFINER à Migrer vers INVOKER

Ces fonctions sont READ-ONLY mais utilisent SECURITY_DEFINER sans raison :

```
get_batch_report, get_brand_bestsellers_optimized, get_brand_page_data_optimized,
get_context_questions, get_decision_report, get_gamme_page_data_optimized,
get_homepage_data_optimized, get_import_gate_report, get_listing_products_for_build,
get_nk_stats, get_oem_refs_for_vehicle, get_pieces_for_type_gamme*,
get_purchase_excluded_ids, get_quarantine_dashboard, get_quarantine_stats,
get_seo_excluded_ids, get_substitution_data, get_symptoms_by_subsystem,
get_vehicle_page_data_optimized, rm_get_listing_page, rm_get_page_complete*,
rm_health
```

**Recommandation** : Migrer ces 25 getters vers INVOKER pour réduire la surface d'attaque.

---

## SECTION 5 — BACKLOG JSON

```json
{
  "generated_at": "2026-02-02T12:00:00Z",
  "scope": ["rpc", "security"],
  "project_id": "cxpojprgwgubzjyqzmoq",
  "items": [
    {
      "id": "RPC-SAFETY-001",
      "type": "rpc",
      "severity": "P0",
      "description": "Bloquer delete_duplicates_batch et delete_first_records_batch",
      "evidence": "Fonctions DELETE pouvant supprimer jusqu'à 31M lignes",
      "impact": "Perte de données irréversible",
      "recommendation": "REVOKE EXECUTE FROM public, authenticated, anon",
      "safe_to_apply_now": true
    },
    {
      "id": "RPC-SAFETY-002",
      "type": "rpc",
      "severity": "P0",
      "description": "Bloquer rollback_switch et switch_to_next",
      "evidence": "Fonctions SECURITY DEFINER modifiant l'état production",
      "impact": "Corruption données production",
      "recommendation": "REVOKE EXECUTE, créer rôle admin dédié",
      "safe_to_apply_now": true
    },
    {
      "id": "RPC-SAFETY-003",
      "type": "rpc",
      "severity": "P0",
      "description": "Bloquer run_import_pipeline",
      "evidence": "Pipeline complet avec multiples effets de bord",
      "impact": "Import non contrôlé",
      "recommendation": "REVOKE EXECUTE, usage via cron/service uniquement",
      "safe_to_apply_now": true
    },
    {
      "id": "RPC-SAFETY-004",
      "type": "rpc",
      "severity": "P1",
      "description": "Restreindre 17 fonctions P1_HIGH à service_role",
      "evidence": "Fonctions DDL et workflow avec SECURITY DEFINER",
      "impact": "Élévation de privilèges possible",
      "recommendation": "REVOKE FROM public; GRANT TO service_role",
      "safe_to_apply_now": true
    },
    {
      "id": "RPC-SAFETY-005",
      "type": "rpc",
      "severity": "P1",
      "description": "Migrer 25 getters SECURITY_DEFINER vers INVOKER",
      "evidence": "Getters read-only avec élévation inutile",
      "impact": "Surface d'attaque réduite",
      "recommendation": "ALTER FUNCTION ... SECURITY INVOKER",
      "safe_to_apply_now": false
    },
    {
      "id": "RPC-SAFETY-006",
      "type": "rpc",
      "severity": "P2",
      "description": "Implémenter logging pour fonctions SECURITY_DEFINER",
      "evidence": "73 fonctions sans audit trail",
      "impact": "Traçabilité manquante",
      "recommendation": "Créer trigger/wrapper pour audit log",
      "safe_to_apply_now": false
    },
    {
      "id": "RPC-SAFETY-007",
      "type": "rpc",
      "severity": "P2",
      "description": "Créer rôle rpc_admin pour fonctions pipeline",
      "evidence": "Pas de séparation des privilèges",
      "impact": "Meilleure isolation",
      "recommendation": "CREATE ROLE rpc_admin; GRANT EXECUTE ...",
      "safe_to_apply_now": false
    }
  ]
}
```

---

**FIN DU RAPPORT RPC SAFETY GATE**

*Généré par Claude Code — Audit READ-ONLY — 2026-02-02*
