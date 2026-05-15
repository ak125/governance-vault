# =============================================================================
# SEO Content — H1 Write Policy Tests (PR-V)
# =============================================================================
#
# Unit tests Rego pour `policies/seo-content/h1-write.rego`.
# Exécutés par `opa test policies/` en CI (workflow opa-policy-build.yml).
#
# Coverage :
#   - Denied writers (llm_generated_direct)
#   - Allow rules (deterministic_builder, human_curated, human_validated_llm,
#     legacy_recovery)
#   - Lock interactions
#   - Evidence tier validation pour legacy_recovery
#   - Flag state pour legacy_recovery (Phase E gating)
#   - Edge cases (missing actor, unknown kind, empty input)
# =============================================================================

package seo.content.h1.write_test

import rego.v1

import data.seo.content.h1.write

# ── DENY : llm_generated_direct (canon enforcement) ──────────────────────────

test_deny_llm_generated_direct if {
	not write.allow with input as {
		"source_kind": "llm_generated_direct",
		"actor": "agent:ai-content",
		"field_path": "h1",
	}
}

test_deny_llm_generated_direct_carries_reason if {
	reasons := write.deny with input as {
		"source_kind": "llm_generated_direct",
		"actor": "agent:ai-content",
	}
	count(reasons) > 0
}

# ── ALLOW : human_curated (always wins, even with lock) ──────────────────────

test_allow_human_curated_with_actor if {
	write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"field_path": "h1",
	}
}

test_allow_human_curated_overrides_lock if {
	write.allow with input as {
		"source_kind": "human_curated",
		"actor": "user:fafa",
		"lock_active": true,
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
		"field_path": "h1",
	}
}

test_deny_human_validated_llm_missing_actor if {
	not write.allow with input as {
		"source_kind": "human_validated_llm",
		"actor": "",
	}
}

# ── ALLOW : legacy_recovery (Phase E gated) ──────────────────────────────────

test_allow_legacy_recovery_with_exact_match_snapshot if {
	write.allow with input as {
		"source_kind": "legacy_recovery",
		"actor": "agent:h1-recovery-apply.worker",
		"flag_state": "enabled",
		"proposed_event": {
			"event_id": "11111111-2222-3333-4444-555555555555",
			"parent_event_kind": "proposed",
		},
		"evidence_tier": "exact_match_snapshot",
		"lock_active": false,
	}
}

test_allow_legacy_recovery_with_exact_match_blog_advice if {
	write.allow with input as {
		"source_kind": "legacy_recovery",
		"actor": "agent:h1-recovery-apply.worker",
		"flag_state": "enabled",
		"proposed_event": {
			"event_id": "aaaa-bbbb",
			"parent_event_kind": "proposed",
		},
		"evidence_tier": "exact_match_blog_advice",
		"lock_active": false,
	}
}

test_deny_legacy_recovery_flag_disabled if {
	not write.allow with input as {
		"source_kind": "legacy_recovery",
		"actor": "agent:worker",
		"flag_state": "disabled",
		"proposed_event": {
			"event_id": "x",
			"parent_event_kind": "proposed",
		},
		"evidence_tier": "exact_match_snapshot",
		"lock_active": false,
	}
}

test_deny_legacy_recovery_heuristic_tier if {
	not write.allow with input as {
		"source_kind": "legacy_recovery",
		"actor": "agent:worker",
		"flag_state": "enabled",
		"proposed_event": {
			"event_id": "x",
			"parent_event_kind": "proposed",
		},
		"evidence_tier": "heuristic_recent_change",
		"lock_active": false,
	}
}

test_deny_legacy_recovery_unknown_tier if {
	not write.allow with input as {
		"source_kind": "legacy_recovery",
		"actor": "agent:worker",
		"flag_state": "enabled",
		"proposed_event": {
			"event_id": "x",
			"parent_event_kind": "proposed",
		},
		"evidence_tier": "unknown",
		"lock_active": false,
	}
}

test_deny_legacy_recovery_no_proposed_event if {
	not write.allow with input as {
		"source_kind": "legacy_recovery",
		"actor": "agent:worker",
		"flag_state": "enabled",
		"proposed_event": {"event_id": "", "parent_event_kind": "proposed"},
		"evidence_tier": "exact_match_snapshot",
		"lock_active": false,
	}
}

test_deny_legacy_recovery_wrong_parent_kind if {
	not write.allow with input as {
		"source_kind": "legacy_recovery",
		"actor": "agent:worker",
		"flag_state": "enabled",
		"proposed_event": {"event_id": "x", "parent_event_kind": "applied"},
		"evidence_tier": "exact_match_snapshot",
		"lock_active": false,
	}
}

test_deny_legacy_recovery_with_active_lock if {
	not write.allow with input as {
		"source_kind": "legacy_recovery",
		"actor": "agent:worker",
		"flag_state": "enabled",
		"proposed_event": {
			"event_id": "x",
			"parent_event_kind": "proposed",
		},
		"evidence_tier": "exact_match_snapshot",
		"lock_active": true,
	}
}

# ── ALLOW : deterministic_builder ────────────────────────────────────────────

test_allow_deterministic_builder_no_lock if {
	write.allow with input as {
		"source_kind": "deterministic_builder",
		"actor": "service:backend.modules.seo.builders.h1-deterministic-builder",
		"lock_active": false,
	}
}

test_deny_deterministic_builder_with_active_lock if {
	not write.allow with input as {
		"source_kind": "deterministic_builder",
		"actor": "service:backend.modules.seo.builders.h1-deterministic-builder",
		"lock_active": true,
	}
}

test_deny_deterministic_builder_missing_actor if {
	not write.allow with input as {
		"source_kind": "deterministic_builder",
		"actor": "",
		"lock_active": false,
	}
}

# ── DENY : unknown source_kind ───────────────────────────────────────────────

test_deny_unknown_source_kind if {
	not write.allow with input as {
		"source_kind": "made_up_source",
		"actor": "user:fafa",
	}
}

test_deny_unknown_source_kind_carries_reason if {
	reasons := write.deny with input as {
		"source_kind": "made_up_source",
		"actor": "user:fafa",
	}
	count(reasons) > 0
}

# ── DENY : empty input ───────────────────────────────────────────────────────

test_deny_empty_input if {
	not write.allow with input as {}
}

# ── Edge case : legacy_recovery missing flag_state defaults to deny ──────────

test_deny_legacy_recovery_missing_flag_state if {
	not write.allow with input as {
		"source_kind": "legacy_recovery",
		"actor": "agent:worker",
		"proposed_event": {
			"event_id": "x",
			"parent_event_kind": "proposed",
		},
		"evidence_tier": "exact_match_snapshot",
		"lock_active": false,
	}
}
