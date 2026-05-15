# =============================================================================
# SEO Content — R2 Cluster Health Policy Tests (ADR-066)
# =============================================================================
#
# Unit tests Rego pour `policies/seo-content/r2-cluster-health.rego`.
# Exécutés par `opa test policies/` en CI.
#
# Coverage :
#   - cluster_healthy : ≥85% INDEX pages avec semanticSim ≤ 0.80
#   - deny_collision : sameContentFingerprintCount > 0
#   - deny_canonical_chain : SUPPRESSED → non-INDEX target
#   - cluster_pollution_detected : >70% SUPPRESSED dans cluster ≥4
# =============================================================================

package seo.content.r2.cluster_health_test

import rego.v1

import data.seo.content.r2.cluster_health

# ── cluster_healthy : ratio ≥ 85% ────────────────────────────────────────────

test_healthy_100pct_pages_ok if {
	cluster_health.cluster_healthy with input as {"pages": [
		{"status": "published", "decision": "index", "semanticSimilarityScore": 0.5, "pageKey": "a"},
		{"status": "published", "decision": "index", "semanticSimilarityScore": 0.7, "pageKey": "b"},
		{"status": "published", "decision": "index", "semanticSimilarityScore": 0.8, "pageKey": "c"},
	]}
}

test_healthy_at_85pct_boundary if {
	# 17 healthy + 3 unhealthy = 85% exactly
	pages := [{"status": "published", "decision": "index", "semanticSimilarityScore": 0.7, "pageKey": sprintf("p%v", [i])} | i := numbers.range(1, 17)[_]]
	bad_pages := [{"status": "published", "decision": "index", "semanticSimilarityScore": 0.95, "pageKey": sprintf("bad%v", [i])} | i := numbers.range(1, 3)[_]]
	cluster_health.cluster_healthy with input as {"pages": array.concat(pages, bad_pages)}
}

test_unhealthy_50pct_ok if {
	not cluster_health.cluster_healthy with input as {"pages": [
		{"status": "published", "decision": "index", "semanticSimilarityScore": 0.5, "pageKey": "a"},
		{"status": "published", "decision": "index", "semanticSimilarityScore": 0.95, "pageKey": "b"},
	]}
}

test_unhealthy_no_index_pages if {
	# Cluster avec uniquement SUPPRESSED → pas healthy (aucun INDEX)
	not cluster_health.cluster_healthy with input as {"pages": [
		{"status": "published", "decision": "suppressed", "semanticSimilarityScore": 0.5, "pageKey": "a"},
		{"status": "published", "decision": "suppressed", "semanticSimilarityScore": 0.6, "pageKey": "b"},
	]}
}

test_unhealthy_empty_cluster if {
	not cluster_health.cluster_healthy with input as {"pages": []}
}

# ── deny_collision : sameContentFingerprintCount > 0 ─────────────────────────

test_deny_collision_detected if {
	denied := cluster_health.deny_collision with input as {"pages": [
		{"pageKey": "100_12345", "sameContentFingerprintCount": 0},
		{"pageKey": "100_67890", "sameContentFingerprintCount": 2},
	]}
	"100_67890" in denied
}

test_no_collision_clean_cluster if {
	denied := cluster_health.deny_collision with input as {"pages": [
		{"pageKey": "a", "sameContentFingerprintCount": 0},
		{"pageKey": "b", "sameContentFingerprintCount": 0},
	]}
	count(denied) == 0
}

# ── deny_canonical_chain : SUPPRESSED → non-INDEX target ─────────────────────

test_deny_chain_suppressed_to_suppressed if {
	denied := cluster_health.deny_canonical_chain with input as {"pages": [
		{
			"pageKey": "100_A",
			"typeId": 10001,
			"decision": "suppressed",
			"canonical_target_type_id": 10002,
		},
		{
			"pageKey": "100_B",
			"typeId": 10002,
			"decision": "suppressed", # chain ! B aussi SUPPRESSED
		},
	]}
	"100_A" in denied
}

test_deny_chain_suppressed_to_reject if {
	denied := cluster_health.deny_canonical_chain with input as {"pages": [
		{
			"pageKey": "100_A",
			"typeId": 10001,
			"decision": "suppressed",
			"canonical_target_type_id": 10002,
		},
		{
			"pageKey": "100_B",
			"typeId": 10002,
			"decision": "reject",
		},
	]}
	"100_A" in denied
}

test_no_chain_suppressed_to_index if {
	denied := cluster_health.deny_canonical_chain with input as {"pages": [
		{
			"pageKey": "100_A",
			"typeId": 10001,
			"decision": "suppressed",
			"canonical_target_type_id": 10002,
		},
		{
			"pageKey": "100_B",
			"typeId": 10002,
			"decision": "index", # valid target
		},
	]}
	count(denied) == 0
}

# ── cluster_pollution_detected : > 70% SUPPRESSED ────────────────────────────

test_pollution_detected_80pct_suppressed if {
	cluster_health.cluster_pollution_detected with input as {"pages": [
		{"decision": "suppressed"},
		{"decision": "suppressed"},
		{"decision": "suppressed"},
		{"decision": "suppressed"},
		{"decision": "index"},
	]}
}

test_no_pollution_50pct_suppressed if {
	not cluster_health.cluster_pollution_detected with input as {"pages": [
		{"decision": "suppressed"},
		{"decision": "suppressed"},
		{"decision": "index"},
		{"decision": "index"},
	]}
}

test_no_pollution_small_cluster_below_threshold if {
	# Cluster de 3 pages, même si toutes SUPPRESSED, on n'a pas le signal cluster
	# (minimum significatif = 4 pages)
	not cluster_health.cluster_pollution_detected with input as {"pages": [
		{"decision": "suppressed"},
		{"decision": "suppressed"},
		{"decision": "suppressed"},
	]}
}

# ── deny_reasons : présence pour chaque cas ──────────────────────────────────

test_deny_reasons_unhealthy_cluster if {
	reasons := cluster_health.deny_reasons with input as {"pages": [
		{"status": "published", "decision": "index", "semanticSimilarityScore": 0.95, "pageKey": "a"},
		{"status": "published", "decision": "index", "semanticSimilarityScore": 0.93, "pageKey": "b"},
	]}
	count(reasons) > 0
}

test_deny_reasons_pollution if {
	reasons := cluster_health.deny_reasons with input as {"pages": [
		{"decision": "suppressed", "status": "published", "semanticSimilarityScore": 0.5, "pageKey": "a"},
		{"decision": "suppressed", "status": "published", "semanticSimilarityScore": 0.5, "pageKey": "b"},
		{"decision": "suppressed", "status": "published", "semanticSimilarityScore": 0.5, "pageKey": "c"},
		{"decision": "suppressed", "status": "published", "semanticSimilarityScore": 0.5, "pageKey": "d"},
		{"decision": "index", "status": "published", "semanticSimilarityScore": 0.5, "pageKey": "e"},
	]}
	count(reasons) > 0
}
