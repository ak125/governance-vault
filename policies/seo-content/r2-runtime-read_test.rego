# =============================================================================
# SEO Content — R2 Runtime Read Policy Tests (ADR-072)
# =============================================================================
#
# Unit tests Rego pour `policies/seo-content/r2-runtime-read.rego`.
# Exécutés par `opa test policies/` en CI.
#
# Coverage :
#   - DENY 1 : CQRS runtime read scope strict (whitelist 2 tables)
#   - DENY 2 : No live compose au request time
#   - DENY 3 : DDD bounded context isolation (cross-context writes blocked)
#   - DENY 4 : 5 prerequisites full-scale launch mandatory
#   - ALLOW happy paths : runtime read snapshot, no live compose, same-context write
# =============================================================================

package seo.runtime.r2.read_test

import rego.v1

import data.seo.runtime.r2.read

# ── DENY 1 : CQRS runtime read scope strict ──────────────────────────────────

test_deny_runtime_read_kg_table if {
	reasons := read.deny with input as {
		"runtime_query": true,
		"reads_table": "__seo_vehicle_part_knowledge",
	}
	count([r | r := reasons[_]; contains(r, "ADR-072 §1")]) > 0
	count([r | r := reasons[_]; contains(r, "CQRS runtime read scope")]) > 0
}

test_deny_runtime_read_wiki_table if {
	reasons := read.deny with input as {
		"runtime_query": true,
		"reads_table": "__seo_r2_wiki_evidence",
	}
	count(reasons) > 0
}

test_deny_runtime_read_r8_snapshot_store if {
	reasons := read.deny with input as {
		"runtime_query": true,
		"reads_table": "__seo_r8_snapshot_store",
	}
	count(reasons) > 0
}

test_allow_runtime_read_r2_page_snapshot if {
	reasons := read.deny with input as {
		"runtime_query": true,
		"reads_table": "__seo_r2_page_snapshot",
	}
	count([r | r := reasons[_]; contains(r, "CQRS runtime read scope")]) == 0
}

test_allow_runtime_read_r2_pages_index if {
	reasons := read.deny with input as {
		"runtime_query": true,
		"reads_table": "__seo_r2_pages",
	}
	count([r | r := reasons[_]; contains(r, "CQRS runtime read scope")]) == 0
}

# ── DENY 2 : No live compose au request time ─────────────────────────────────

test_deny_runtime_performs_live_compose if {
	reasons := read.deny with input as {
		"runtime_query": true,
		"performs_live_compose": true,
	}
	count([r | r := reasons[_]; contains(r, "no live compose")]) > 0
}

test_allow_runtime_no_live_compose if {
	reasons := read.deny with input as {
		"runtime_query": true,
		"performs_live_compose": false,
		"reads_table": "__seo_r2_page_snapshot",
	}
	count([r | r := reasons[_]; contains(r, "no live compose")]) == 0
}

# ── DENY 3 : DDD bounded context isolation ───────────────────────────────────

test_deny_cross_context_write_r8_from_r2_module if {
	reasons := read.deny with input as {
		"cross_context_write": true,
		"aggregate_type": "R8VehicleSnapshot",
		"actor_module": "modules/seo/r2/services/render",
	}
	count([r | r := reasons[_]; contains(r, "DDD bounded context isolation")]) > 0
}

test_deny_cross_context_write_kg_from_r8_module if {
	reasons := read.deny with input as {
		"cross_context_write": true,
		"aggregate_type": "VehiclePartKnowledgeFact",
		"actor_module": "modules/seo/r8",
	}
	count([r | r := reasons[_]; contains(r, "DDD bounded context isolation")]) > 0
}

test_allow_same_context_write_r8_aggregate if {
	reasons := read.deny with input as {
		"cross_context_write": true,
		"aggregate_type": "R8VehicleSnapshot",
		"actor_module": "modules/seo/r8",
	}
	count([r | r := reasons[_]; contains(r, "DDD bounded context isolation")]) == 0
}

test_allow_same_context_write_r2_snapshot if {
	reasons := read.deny with input as {
		"cross_context_write": true,
		"aggregate_type": "R2PageSnapshot",
		"actor_module": "modules/seo/r2/services/render",
	}
	count([r | r := reasons[_]; contains(r, "DDD bounded context isolation")]) == 0
}

# ── DENY 4 : 5 prerequisites full-scale launch mandatory ─────────────────────

test_deny_full_scale_launch_missing_golden_validation if {
	reasons := read.deny with input as {
		"full_scale_launch_enabled": true,
		"prerequisites_status": {
			"golden_examples_validated": false,
			"business_signature_validated": true,
			"internal_difference_score_calibrated": true,
			"r1_completeness_audited": true,
			"r8_snapshot_stability_verified": true,
		},
	}
	count([r | r := reasons[_]; contains(r, "5 prerequisites full-scale")]) > 0
	count([r | r := reasons[_]; contains(r, "golden_examples_validated")]) > 0
}

test_deny_full_scale_launch_missing_internal_score_calibration if {
	reasons := read.deny with input as {
		"full_scale_launch_enabled": true,
		"prerequisites_status": {
			"golden_examples_validated": true,
			"business_signature_validated": true,
			"internal_difference_score_calibrated": false,
			"r1_completeness_audited": true,
			"r8_snapshot_stability_verified": true,
		},
	}
	count([r | r := reasons[_]; contains(r, "internal_difference_score_calibrated")]) > 0
}

test_deny_full_scale_launch_all_prerequisites_missing if {
	reasons := read.deny with input as {
		"full_scale_launch_enabled": true,
		"prerequisites_status": {},
	}
	# 5 deny entries (un par prerequisite manquant)
	count([r | r := reasons[_]; contains(r, "5 prerequisites full-scale")]) == 5
}

test_allow_full_scale_launch_all_prerequisites_satisfied if {
	reasons := read.deny with input as {
		"full_scale_launch_enabled": true,
		"prerequisites_status": {
			"golden_examples_validated": true,
			"business_signature_validated": true,
			"internal_difference_score_calibrated": true,
			"r1_completeness_audited": true,
			"r8_snapshot_stability_verified": true,
		},
	}
	count([r | r := reasons[_]; contains(r, "5 prerequisites full-scale")]) == 0
}

# ── ALLOW : runtime read happy path complet ──────────────────────────────────

test_allow_runtime_read_happy_path if {
	read.allow with input as {
		"runtime_query": true,
		"reads_table": "__seo_r2_page_snapshot",
		"performs_live_compose": false,
	}
}

# ── Audit : runtime read OK émet info audit ──────────────────────────────────

test_audit_runtime_read_snapshot_emits_info if {
	infos := read.audit with input as {
		"runtime_query": true,
		"reads_table": "__seo_r2_page_snapshot",
	}
	count([i | i := infos[_]; contains(i, "runtime read OK")]) > 0
}
