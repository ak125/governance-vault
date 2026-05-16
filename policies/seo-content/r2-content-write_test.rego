# =============================================================================
# SEO Content — R2 Content Write Policy Tests (ADR-066)
# =============================================================================
#
# Unit tests Rego pour `policies/seo-content/r2-content-write.rego`.
# Exécutés par `opa test policies/` en CI (workflow opa-policy-build.yml).
#
# Coverage :
#   - Allow rules (human_curated, human_validated_llm, pipeline INDEX/SUPPRESSED/REVIEW/REGENERATE/REJECT)
#   - Feature flag gating (R2_V2_ENABLED kill-switch, improvement D)
#   - Anti-canonical-chain invariants (improvement A) : target.decision=INDEX, same pg_id
#   - Score range invariants : eligibility_score ∈ [0,100], retry_count ≤ 2
#   - INDEX requires content_hash non-null
#   - Commercial signal forbidden hors S_REASSURANCE
#   - Lock interactions (human overrides lock, pipeline does not)
#   - Edge cases (missing actor, unknown source_kind, empty input)
# =============================================================================

package seo.content.r2.write_test

import rego.v1

import data.seo.content.r2.write

# ── ALLOW : human_curated (always wins, even with lock and flag off) ─────────

test_allow_human_curated_with_actor if {
	write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"pg_id": 100,
		"type_id": 12345,
	}
}

test_allow_human_curated_overrides_lock if {
	write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"lock_active": true,
	}
}

test_allow_human_curated_overrides_feature_flag_off if {
	write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"feature_flag_r2_v2_enabled": false,
	}
}

test_deny_human_curated_missing_actor if {
	not write.allow with input as {
		"source_kind": "human_curated",
		"actor": "",
	}
}

# ── ALLOW : human_validated_llm ──────────────────────────────────────────────

test_allow_human_validated_llm if {
	write.allow with input as {
		"source_kind": "human_validated_llm",
		"actor": "user:fafa",
	}
}

test_deny_human_validated_llm_missing_actor if {
	not write.allow with input as {
		"source_kind": "human_validated_llm",
		"actor": "",
	}
}

# ── ALLOW : pipeline_generated INDEX ─────────────────────────────────────────

test_allow_pipeline_index_full if {
	write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"lock_active": false,
		"governance_decision": "index",
		"content_hash": "abc123def456",
		"eligibility_score": 72,
		"retry_count": 0,
		"pg_id": 100,
		"type_id": 12345,
		# ADR-070 (2026-05-16) prerequisites INDEX strict (Round 5+6+7)
		"r8_snapshot_status": "enriched",
		"r1_gamme_context_status": "loaded",
		"knowledge_facts_count": 5,
		"validated_wiki_evidence_count": 0,
		"h1_contains_motor_power_pattern": true,
		"s_variant_disambiguation_present": true,
		"body_long_form_section_contains_raw_specs": false,
	}
}

# ── DENY : feature flag OFF (kill-switch, improvement D) ─────────────────────

test_deny_pipeline_when_feature_flag_off if {
	not write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": false,
		"flag_state": "enabled",
		"governance_decision": "index",
		"content_hash": "abc",
		"eligibility_score": 72,
		"retry_count": 0,
		"pg_id": 100,
		"type_id": 12345,
	}
}

test_deny_pipeline_feature_flag_off_carries_reason if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": false,
	}
	count(reasons) > 0
}

# ── DENY : flag_state != enabled ─────────────────────────────────────────────

test_deny_pipeline_when_flag_state_disabled if {
	not write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "disabled",
		"governance_decision": "index",
		"content_hash": "abc",
		"eligibility_score": 72,
		"retry_count": 0,
	}
}

# ── DENY : pipeline cannot overwrite active lock ─────────────────────────────

test_deny_pipeline_when_lock_active if {
	not write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"lock_active": true,
		"governance_decision": "index",
		"content_hash": "abc",
		"eligibility_score": 72,
		"retry_count": 0,
	}
}

# ── DENY : INDEX without content_hash ────────────────────────────────────────

test_deny_index_without_content_hash if {
	not write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "index",
		"content_hash": "",
		"eligibility_score": 72,
		"retry_count": 0,
	}
}

# ── ADR-067 (2026-05-15) — pipeline_generated → suppressed est INTERDIT ─────
# Cf doctrine pivot : "compatibilité pièce prime sur similarité texte". Seul
# human_curated peut flipper vers SUPPRESSED (admin UI manual override).

test_deny_pipeline_generated_suppressed_even_valid_canonical if {
	not write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"lock_active": false,
		"governance_decision": "suppressed",
		"canonical_target_type_id": 67890,
		"canonical_target": {
			"decision": "index",
			"pg_id": 100,
		},
		"pg_id": 100,
		"type_id": 12345,
		"eligibility_score": 38,
		"retry_count": 0,
	}
}

test_deny_pipeline_suppressed_carries_adr067_reason if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "suppressed",
		"canonical_target_type_id": 67890,
		"canonical_target": {"decision": "index", "pg_id": 100},
		"pg_id": 100,
	}
	some r in reasons
	contains(r, "ADR-067")
}

# ── ALLOW : human_curated → suppressed (manual override, ADR-067) ────────────

test_allow_human_curated_suppressed_valid_canonical if {
	write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"governance_decision": "suppressed",
		"canonical_target_type_id": 67890,
		"canonical_target": {
			"decision": "index",
			"pg_id": 100,
		},
		"pg_id": 100,
		"type_id": 12345,
	}
}

test_deny_human_curated_suppressed_missing_canonical if {
	not write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"governance_decision": "suppressed",
		"canonical_target_type_id": null,
		"pg_id": 100,
		"type_id": 12345,
	}
}

# ── DENY : SUPPRESSED without canonical_target_type_id (human path ADR-067) ─

test_deny_suppressed_null_canonical_target if {
	not write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"governance_decision": "suppressed",
		"canonical_target_type_id": null,
		"pg_id": 100,
		"type_id": 12345,
	}
}

# ── DENY : SUPPRESSED chain (target.decision != "index") — human_curated path
# ADR-067 : pipeline path now deny by source_kind ; anti-chain enforced on
# human_curated SUPPRESSED path (admin override).

test_deny_human_suppressed_chain_target_is_suppressed if {
	not write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"governance_decision": "suppressed",
		"canonical_target_type_id": 67890,
		"canonical_target": {
			"decision": "suppressed",
			"pg_id": 100,
		},
		"pg_id": 100,
		"type_id": 12345,
	}
}

test_deny_human_suppressed_chain_target_is_reject if {
	not write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"governance_decision": "suppressed",
		"canonical_target_type_id": 67890,
		"canonical_target": {
			"decision": "reject",
			"pg_id": 100,
		},
		"pg_id": 100,
		"type_id": 12345,
	}
}

# ── DENY : cross-gamme canonical (target.pg_id != self.pg_id) — human path ──

test_deny_cross_gamme_canonical if {
	not write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"governance_decision": "suppressed",
		"canonical_target_type_id": 67890,
		"canonical_target": {
			"decision": "index",
			"pg_id": 999, # different from self.pg_id=100
		},
		"pg_id": 100,
		"type_id": 12345,
		"eligibility_score": 38,
		"retry_count": 0,
	}
}

test_deny_cross_gamme_carries_reason if {
	reasons := write.deny with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"governance_decision": "suppressed",
		"canonical_target_type_id": 67890,
		"canonical_target": {"decision": "index", "pg_id": 999},
		"pg_id": 100,
	}
	count(reasons) > 0
}

# ── ALLOW : REVIEW_REQUIRED (intermediate, no canonical required) ────────────

test_allow_pipeline_review_required if {
	write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"lock_active": false,
		"governance_decision": "review_required",
		"eligibility_score": 57,
		"retry_count": 1,
	}
}

# ── ALLOW : REGENERATE (retry valid) ─────────────────────────────────────────

test_allow_pipeline_regenerate_retry_2 if {
	write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"lock_active": false,
		"governance_decision": "regenerate",
		"eligibility_score": 48,
		"retry_count": 2,
	}
}

test_deny_regenerate_retry_overflow if {
	not write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "regenerate",
		"eligibility_score": 48,
		"retry_count": 3, # exceeds max
	}
}

# ── ALLOW : REJECT (no content, no canonical required) ───────────────────────

test_allow_pipeline_reject_with_valid_reason if {
	write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "reject",
		"reject_reason": "productCount_under_2",
		"eligibility_score": 0,
	}
}

# ── DENY : eligibility_score out of range ────────────────────────────────────

test_deny_eligibility_score_negative if {
	not write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "index",
		"content_hash": "abc",
		"eligibility_score": -5,
		"retry_count": 0,
	}
}

test_deny_eligibility_score_above_100 if {
	not write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "index",
		"content_hash": "abc",
		"eligibility_score": 105,
		"retry_count": 0,
	}
}

# ── DENY : commercial signal in non-S_REASSURANCE section ────────────────────

test_deny_price_in_selection_guide if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"section_key": "S_SELECTION_GUIDE",
		"section_content": "Choisir une pièce de qualité au meilleur prix sur notre catalogue",
	}
	count(reasons) > 0
}

test_deny_panier_in_faq if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"section_key": "S_FAQ_SPECIFIC",
		"section_content": "Pour ajouter au panier, cliquez sur le bouton vert",
	}
	count(reasons) > 0
}

test_allow_price_in_reassurance if {
	# Pas de deny carrying commercial signal reason quand section = S_REASSURANCE
	# (allow rules indépendantes peuvent quand même refuser, mais pas pour signal)
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "index",
		"content_hash": "abc",
		"eligibility_score": 72,
		"retry_count": 0,
		"section_key": "S_REASSURANCE",
		"section_content": "Livraison rapide, paiement sécurisé, prix au meilleur tarif",
		"pg_id": 100,
		"type_id": 12345,
	}
	# Aucune raison "commercial_signal" — le seul signal est légitime dans S_REASSURANCE
	count([r | r := reasons[_]; contains(r, "commercial signal")]) == 0
}

# ── DENY : unknown source_kind ───────────────────────────────────────────────

test_deny_unknown_source_kind if {
	not write.allow with input as {
		"source_kind": "made_up_source",
		"actor": "user:fafa",
	}
}

# ── DENY : empty input ───────────────────────────────────────────────────────

test_deny_empty_input if {
	not write.allow with input as {}
}

# ── ADR-068 amendment 2026-05-16 — 4 actions auto INTERDITES + REJECT scope ──

# DENY : pipeline → noindex_follow sur page valide (productCount >= 2)
test_deny_pipeline_auto_noindex_on_valid_page if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "noindex_follow",
		"product_count": 50,
	}
	some r in reasons
	contains(r, "ADR-068")
}

# ALLOW : pipeline → noindex_follow sur page invalide (productCount < 2) reste OK
# car c'est la legacy noindex rule preservée
test_pipeline_noindex_on_invalid_page_not_flagged_adr068 if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "noindex_follow",
		"product_count": 1,
	}
	count([r | r := reasons[_]; contains(r, "ADR-068 — pipeline_generated cannot auto-noindex")]) == 0
}

# DENY : REJECT scope strict — reject_reason hors des 4 raisons UNIQUES
test_deny_reject_for_similarity_reason if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "reject",
		"reject_reason": "high_catalog_overlap",
		"eligibility_score": 30,
	}
	some r in reasons
	contains(r, "ADR-068")
	contains(r, "REJECT scope strict")
}

# ALLOW : REJECT pour les 4 raisons légitimes
test_reject_productCount_under_2_passes_adr068 if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "reject",
		"reject_reason": "productCount_under_2",
		"eligibility_score": 0,
	}
	count([r | r := reasons[_]; contains(r, "ADR-068 — REJECT scope strict")]) == 0
}

test_reject_compatibility_absent_passes_adr068 if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "reject",
		"reject_reason": "compatibility_absent",
		"eligibility_score": 0,
	}
	count([r | r := reasons[_]; contains(r, "ADR-068 — REJECT scope strict")]) == 0
}

# DENY : canonical sibling auto sur page INDEX/REVIEW_REQUIRED
test_deny_canonical_sibling_auto_on_index_page if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "index",
		"canonical_url": "https://automecanik.com/pieces/filtre-a-huile/audi/a4/2.0-tdi-140ch.html",
		"self_url": "https://automecanik.com/pieces/filtre-a-huile/audi/a4/1.9-tdi-110ch.html",
	}
	some r in reasons
	contains(r, "ADR-068")
	contains(r, "canonical sibling auto")
}

test_deny_canonical_sibling_auto_on_review_required_page if {
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "review_required",
		"canonical_url": "https://automecanik.com/pieces/filtre-a-huile/audi/a4/2.0-tdi-140ch.html",
		"self_url": "https://automecanik.com/pieces/filtre-a-huile/audi/a4/1.9-tdi-110ch.html",
	}
	some r in reasons
	contains(r, "ADR-068")
}

# ALLOW : canonical self est OK
test_canonical_self_passes_adr068 if {
	url := "https://automecanik.com/pieces/filtre-a-huile/audi/a4/1.9-tdi-110ch.html"
	reasons := write.deny with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "index",
		"canonical_url": url,
		"self_url": url,
	}
	count([r | r := reasons[_]; contains(r, "canonical sibling auto")]) == 0
}

# ── ADR-070 (2026-05-16) — R8+R1 first canon + INTERNAL DIFFERENCE EXHAUSTION + Technical criteria = evidence ──
#
# Formule canon Round 5 : R2Content = render(R8 + R1 + KG + WIKI)
#   CADRE   = R8 + R1 (sans = générique, JAMAIS INDEX)
#   MATIÈRE = KG facts + WIKI evidence (sans = pauvre, JAMAIS INDEX)
# Round 6 : INTERNAL DIFFERENCE EXHAUSTION (L0-L3 avant L4 external)
# Round 7 : Technical criteria = evidence only (PAS éditorial paragraphes spec)

# Base valid INDEX input for ADR-070 tests (full canon Round 5+6+7 inputs)
adr070_valid_index_input := {
	"source_kind": "pipeline_generated",
	"feature_flag_r2_v2_enabled": true,
	"flag_state": "enabled",
	"lock_active": false,
	"governance_decision": "index",
	"content_hash": "abc123def456",
	"eligibility_score": 72,
	"retry_count": 0,
	"pg_id": 100,
	"type_id": 12345,
	# Round 5 canon : 4 inputs CADRE + MATIÈRE
	"r8_snapshot_status": "enriched",
	"r1_gamme_context_status": "loaded",
	"knowledge_facts_count": 12,
	"validated_wiki_evidence_count": 3,
	# Round 5 disambiguation active
	"h1_contains_motor_power_pattern": true,
	"s_variant_disambiguation_present": true,
	# Round 7 technical criteria = evidence only
	"body_long_form_section_contains_raw_specs": false,
}

# DENY ADR-070 #1 : R8 snapshot CADRE requis
test_deny_adr070_r8_snapshot_unavailable if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/r8_snapshot_status", "value": "failed"}])
	not write.allow with input as bad
}

test_deny_adr070_r8_snapshot_missing_carries_reason if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/r8_snapshot_status", "value": "absent"}])
	reasons := write.deny with input as bad
	count([r | r := reasons[_]; contains(r, "ADR-070")]) > 0
	count([r | r := reasons[_]; contains(r, "R8 snapshot CADRE")]) > 0
}

test_allow_adr070_r8_snapshot_minimal_passes if {
	ok := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/r8_snapshot_status", "value": "minimal"}])
	write.allow with input as ok
}

test_allow_adr070_r8_snapshot_stale_passes if {
	ok := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/r8_snapshot_status", "value": "stale"}])
	write.allow with input as ok
}

# DENY ADR-070 #2 : R1 gamme context CADRE requis
test_deny_adr070_r1_gamme_context_missing if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/r1_gamme_context_status", "value": "missing"}])
	not write.allow with input as bad
}

test_deny_adr070_r1_gamme_sections_empty_carries_reason if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/r1_gamme_context_status", "value": "sections_empty"}])
	reasons := write.deny with input as bad
	count([r | r := reasons[_]; contains(r, "ADR-070")]) > 0
	count([r | r := reasons[_]; contains(r, "R1 gamme context CADRE")]) > 0
}

# DENY ADR-070 #3 : MATIÈRE FACTUELLE (KG OR WIKI ≥ 1) requise
test_deny_adr070_no_factual_matter_at_all if {
	bad := json.patch(adr070_valid_index_input, [
		{"op": "replace", "path": "/knowledge_facts_count", "value": 0},
		{"op": "replace", "path": "/validated_wiki_evidence_count", "value": 0},
	])
	not write.allow with input as bad
}

test_deny_adr070_no_matter_carries_reason if {
	bad := json.patch(adr070_valid_index_input, [
		{"op": "replace", "path": "/knowledge_facts_count", "value": 0},
		{"op": "replace", "path": "/validated_wiki_evidence_count", "value": 0},
	])
	reasons := write.deny with input as bad
	count([r | r := reasons[_]; contains(r, "ADR-070")]) > 0
	count([r | r := reasons[_]; contains(r, "MATIÈRE FACTUELLE")]) > 0
}

test_allow_adr070_kg_facts_only_passes if {
	ok := json.patch(adr070_valid_index_input, [
		{"op": "replace", "path": "/knowledge_facts_count", "value": 5},
		{"op": "replace", "path": "/validated_wiki_evidence_count", "value": 0},
	])
	write.allow with input as ok
}

test_allow_adr070_wiki_evidence_only_passes if {
	ok := json.patch(adr070_valid_index_input, [
		{"op": "replace", "path": "/knowledge_facts_count", "value": 0},
		{"op": "replace", "path": "/validated_wiki_evidence_count", "value": 2},
	])
	write.allow with input as ok
}

# DENY ADR-070 #4 : H1 + S_VARIANT_DISAMBIGUATION obligatoires
test_deny_adr070_h1_missing_motor_power_pattern if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/h1_contains_motor_power_pattern", "value": false}])
	not write.allow with input as bad
}

test_deny_adr070_h1_missing_motor_power_carries_reason if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/h1_contains_motor_power_pattern", "value": false}])
	reasons := write.deny with input as bad
	count([r | r := reasons[_]; contains(r, "ADR-070")]) > 0
	count([r | r := reasons[_]; contains(r, "motor_power_pattern")]) > 0
}

test_deny_adr070_s_variant_disambiguation_missing if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/s_variant_disambiguation_present", "value": false}])
	not write.allow with input as bad
}

test_deny_adr070_s_variant_disambiguation_carries_reason if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/s_variant_disambiguation_present", "value": false}])
	reasons := write.deny with input as bad
	count([r | r := reasons[_]; contains(r, "ADR-070")]) > 0
	count([r | r := reasons[_]; contains(r, "S_VARIANT_DISAMBIGUATION")]) > 0
}

# DENY ADR-070 #5 : Technical criteria = evidence only (Round 7)
test_deny_adr070_body_long_form_with_raw_specs if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/body_long_form_section_contains_raw_specs", "value": true}])
	not write.allow with input as bad
}

test_deny_adr070_raw_specs_carries_round7_reason if {
	bad := json.patch(adr070_valid_index_input, [{"op": "replace", "path": "/body_long_form_section_contains_raw_specs", "value": true}])
	reasons := write.deny with input as bad
	count([r | r := reasons[_]; contains(r, "ADR-070 R7")]) > 0
	count([r | r := reasons[_]; contains(r, "evidence only")]) > 0
}

test_allow_adr070_compact_specs_passes if {
	# Compact tableau dans S_TECHNICAL_TABLE_COMPACT = OK, body_long_form_section_contains_raw_specs reste false
	write.allow with input as adr070_valid_index_input
}

# ADR-070 ALLOW : full canon valid input
test_allow_adr070_full_canon_valid_input if {
	write.allow with input as adr070_valid_index_input
}

# ADR-070 cumulé : review_required ne déclenche PAS les gates INDEX strict
# (les gates Round 5+6+7 ne s'appliquent qu'à decision='index' — review_required reste autorisé)
test_allow_adr070_review_required_without_strict_gates if {
	ok := json.patch(adr070_valid_index_input, [
		{"op": "replace", "path": "/governance_decision", "value": "review_required"},
		{"op": "replace", "path": "/knowledge_facts_count", "value": 0},
		{"op": "replace", "path": "/validated_wiki_evidence_count", "value": 0},
		{"op": "replace", "path": "/h1_contains_motor_power_pattern", "value": false},
	])
	write.allow with input as ok
}
