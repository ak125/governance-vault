# =============================================================================
# SEO Content — R2 Cluster Health Policy (ADR-066)
# =============================================================================
#
# Rôle : enforce les invariants de diversité au niveau d'un cluster
# (motorisations sœurs partageant brand+model+fuel+body × pg_id, ou
# vehicle_family_id v2). Évalué nightly après le similarity-scan batch.
#
# Consommé par (futur, PR 2 monorepo) :
#   - backend/src/modules/seo/r2/queues/r2-similarity-scan.processor.ts
#   - backend/src/modules/seo/r2/gates/r2-opa-evaluator.service.ts
#
# Discipline canon (MEMORY feedback_opa_rego_invariants_only) :
#   Cette policy enforce des INVARIANTS uniquement. Aucun scoring composite,
#   aucun weight cluster-level. Les seuils (≥85% pages healthy) sont des
#   invariants binaires (passes/fails), pas un calcul.
#
# Verdict empirique qui motive le verrou : feedback expert 2026-05-15
# improvement A (canonical-chain prevention) + cluster-level diversity gate
# pour détecter les régressions massives sur un cluster (ex: 80% des
# motorisations d'un modèle qui dégradent semanticSim > 0.80 simultanément).
#
# Plan source : /home/deploy/.claude/plans/le-contenu-de-r2-scalable-tower.md
# ADR : ADR-066-r2-content-composition-v2.md
# =============================================================================

package seo.content.r2.cluster_health

import rego.v1

# ── Invariant 1 : cluster_healthy ────────────────────────────────────────────
#
# Un cluster est healthy ssi ≥ 85% de ses pages INDEX ont
# semanticSimilarityScore ≤ 0.80. Le ratch 85% absorbe les cas borderline
# sans casser le pipeline pour 1 page mauvaise.
#
# Pages comptées : status='published' AND decision='index'.
# Les SUPPRESSED, REVIEW, REGENERATE, REJECT ne sont pas comptées
# (par définition pas indexées, donc pas porteuses de duplicate risk).

default cluster_healthy := false

cluster_healthy if {
	count(indexed_pages) > 0
	healthy_count := count([p | p := indexed_pages[_]; p.semanticSimilarityScore <= 0.80])
	healthy_ratio := healthy_count / count(indexed_pages)
	healthy_ratio >= 0.85
}

# Helper : extrait les pages INDEX du cluster
indexed_pages := [p |
	some p in input.pages
	p.status == "published"
	p.decision == "index"
]

# ── Invariant 2 : zero collision exacte ──────────────────────────────────────
#
# Si une page du cluster a sameContentFingerprintCount > 0, c'est une
# collision exacte de content_fingerprint avec une autre page — duplicate
# garanti, jamais acceptable.

deny_collision contains page_key if {
	some p in input.pages
	p.sameContentFingerprintCount > 0
	page_key := p.pageKey
}

# ── Invariant 3 : anti-chain canonical (couche cluster) ──────────────────────
#
# Renforce l'invariant local de r2-content-write.rego à l'échelle cluster :
# aucune page SUPPRESSED ne doit pointer vers une page SUPPRESSED ou REJECT
# du même cluster.
#
# Détection à scan nightly — utile si une page INDEX a transitionné
# REVIEW/REJECT entre le write et le scan, et la cascade revalidation
# (BullMQ r2-canonical-revalidate) n'a pas encore convergé.

deny_canonical_chain contains page_key if {
	some p in input.pages
	p.decision == "suppressed"
	is_number(p.canonical_target_type_id)
	some target in input.pages
	target.typeId == p.canonical_target_type_id
	target.decision != "index"
	page_key := p.pageKey
}

# ── Invariant 4 : taux SUPPRESSED max (signal cluster pollué) ────────────────
#
# Si > 70% des pages d'un cluster sont SUPPRESSED, le cluster est pollué :
# trop de pseudo-doublons, indique que l'eligibility gate amont aurait dû
# filtrer plus agressivement, ou que le cluster_key est mal défini
# (mélange phases/plateformes/générations).

default cluster_pollution_detected := false

cluster_pollution_detected if {
	count(input.pages) >= 4 # cluster significatif
	suppressed_count := count([p | p := input.pages[_]; p.decision == "suppressed"])
	pollution_ratio := suppressed_count / count(input.pages)
	pollution_ratio > 0.70
}

# ── Reasons (introspectable côté NestJS) ─────────────────────────────────────

deny_reasons contains reason if {
	not cluster_healthy
	count(indexed_pages) > 0
	healthy_count := count([p | p := indexed_pages[_]; p.semanticSimilarityScore <= 0.80])
	healthy_ratio := healthy_count / count(indexed_pages)
	reason := sprintf("cluster_unhealthy: only %v of %v INDEX pages healthy (%.2f), require ≥0.85", [healthy_count, count(indexed_pages), healthy_ratio])
}

deny_reasons contains reason if {
	not cluster_healthy
	count(indexed_pages) == 0
	reason := "cluster_unhealthy: no INDEX pages in cluster (likely all suppressed or rejected)"
}

deny_reasons contains reason if {
	some page_key in deny_collision
	reason := sprintf("collision_exact: page %v has sameContentFingerprintCount > 0 (duplicate guaranteed)", [page_key])
}

deny_reasons contains reason if {
	some page_key in deny_canonical_chain
	reason := sprintf("canonical_chain: SUPPRESSED page %v targets non-INDEX page (chain detected, cascade revalidation needed)", [page_key])
}

deny_reasons contains reason if {
	cluster_pollution_detected
	suppressed_count := count([p | p := input.pages[_]; p.decision == "suppressed"])
	reason := sprintf("cluster_polluted: %v of %v pages SUPPRESSED (>0.70 ratio) — review cluster_key boundaries or eligibility threshold", [suppressed_count, count(input.pages)])
}
