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

test_allow_pipeline_reject if {
	write.allow with input as {
		"source_kind": "pipeline_generated",
		"feature_flag_r2_v2_enabled": true,
		"flag_state": "enabled",
		"governance_decision": "reject",
		"eligibility_score": 30,
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
