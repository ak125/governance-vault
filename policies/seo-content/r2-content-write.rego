# =============================================================================
# SEO Content — R2 Content Write Policy (ADR-066)
# =============================================================================
#
# Rôle : autorise / refuse les écritures sur le contenu d'une page R2_PRODUCT
# (URL `/pieces/:gamme/:marque/:modele/:type.html`).
#
# Consommé par (futur, PR 1 monorepo) :
#   - backend/src/modules/seo/r2/gates/r2-opa-evaluator.service.ts (WASM
#     bundle embedded, sync eval < 1ms)
#   - backend/src/modules/seo/r2/gates/r2-governance-gate.service.ts
#     (delegate de la décision invariant à cette policy avant write-gate)
#
# Discipline canon (MEMORY feedback_opa_rego_invariants_only) :
#   Cette policy enforce des INVARIANTS uniquement. Aucun scoring, aucun
#   weight, aucune logique métier. Les seuils (THRESHOLD_V1=45, weights
#   0.35/0.35/0.20/0.10) restent en TS testable, fournis en input.
#
# Source de vérité scoring : backend/src/modules/seo/r2/constants/
#   r2-eligibility.constants.ts (TS, property-based fast-check)
#
# Verdict empirique qui motive le verrou : feedback expert 2026-05-15 sur
# plan R2 v2 — 10 points correctifs + 7 améliorations self-review. Le vrai
# risque est l'explosion de cardinalité SEO inutile (1.6 TDI 105 vs 110,
# même OEM set, même catalogue). Eligibility + SUPPRESSED canonical
# préviennent l'index bloat.
#
# Plan source : /home/deploy/.claude/plans/le-contenu-de-r2-scalable-tower.md
# ADR : ADR-066-r2-content-composition-v2.md
# =============================================================================

package seo.content.r2.write

import rego.v1

# ── Décision par défaut : DENY (fail-closed) ─────────────────────────────────
default allow := false

# ── Règles d'autorisation ─────────────────────────────────────────────────────

# Règle 1 : human_curated
# Écriture humaine explicite admin-ui (IsAdminGuard authentifié). Toujours
# autorisée, surpasse les locks et le feature flag (humain = autorité finale).
allow if {
	input.source_kind == "human_curated"
	is_non_empty_string(input.actor)
}

# Règle 2 : human_validated_llm
# Écriture LLM validée explicitement par humain via review queue
# (POST /api/admin/seo/r2/review-queue/:id/approve flip de source au moment
# de l'approbation). L'actor est obligatoire pour audit-trail.
allow if {
	input.source_kind == "human_validated_llm"
	is_non_empty_string(input.actor)
}

# Règle 3 : pipeline_generated_index
# Génération automatisée par le pipeline R2 v2, décision INDEX. Requiert :
#   - feature flag R2_V2_ENABLED ON (improvement D, kill-switch sans redeploy)
#   - flag_state pipeline enabled
#   - aucun lock actif (un humain a verrouillé → pas d'overwrite)
#   - decision="index" ET content_hash présent (no INDEX sans contenu)
#   - eligibility_score dans [0, 100]
#   - retry_count ≤ 2
allow if {
	input.source_kind == "pipeline_generated"
	input.feature_flag_r2_v2_enabled == true
	input.flag_state == "enabled"
	not input.lock_active
	input.governance_decision == "index"
	is_non_empty_string(input.content_hash)
	is_valid_eligibility_score(input.eligibility_score)
	is_valid_retry_count(input.retry_count)
}

# Règle 4 : pipeline_generated_suppressed
# Génération automatisée, décision SUPPRESSED. Requiert tous les invariants
# canonical (improvement A, anti-chain prevention) :
#   - canonical_target_type_id non-null
#   - canonical_target.decision = "index" (no chain : SUPPRESSED → SUPPRESSED interdit)
#   - canonical_target.pg_id = self.pg_id (no cross-gamme canonical)
#   - feature flag + flag_state + scores valides comme règle 3
allow if {
	input.source_kind == "pipeline_generated"
	input.feature_flag_r2_v2_enabled == true
	input.flag_state == "enabled"
	not input.lock_active
	input.governance_decision == "suppressed"
	is_valid_canonical_target(input)
	is_valid_eligibility_score(input.eligibility_score)
	is_valid_retry_count(input.retry_count)
}

# Règle 5 : pipeline_generated_review_or_regenerate
# Décisions intermédiaires (REVIEW_REQUIRED, REGENERATE) qui écrivent un draft
# avec status approprié. Pas de contenu publié, mais persistance pour audit
# trail et queue handling. Pas de canonical_target requis.
allow if {
	input.source_kind == "pipeline_generated"
	input.feature_flag_r2_v2_enabled == true
	input.flag_state == "enabled"
	not input.lock_active
	intermediate_decisions := {"review_required", "regenerate"}
	intermediate_decisions[input.governance_decision]
	is_valid_eligibility_score(input.eligibility_score)
	is_valid_retry_count(input.retry_count)
}

# Règle 6 : pipeline_generated_reject
# Décision REJECT — écrit la raison dans __seo_r2_qa_reviews, no content.
# Pas de canonical target requis (le cas "pas de sibling fiable").
allow if {
	input.source_kind == "pipeline_generated"
	input.feature_flag_r2_v2_enabled == true
	input.flag_state == "enabled"
	input.governance_decision == "reject"
	is_valid_eligibility_score(input.eligibility_score)
}

# ── Helpers (predicats utilitaires) ──────────────────────────────────────────

is_non_empty_string(s) if {
	is_string(s)
	count(s) > 0
}

is_valid_eligibility_score(score) if {
	is_number(score)
	score >= 0
	score <= 100
}

is_valid_retry_count(n) if {
	is_number(n)
	n >= 0
	n <= 2
}

is_valid_canonical_target(obj) if {
	is_number(obj.canonical_target_type_id)
	obj.canonical_target.decision == "index"
	obj.canonical_target.pg_id == obj.pg_id
}

# Détecte la présence de signaux commerciaux dans une section
# qui n'est pas S_REASSURANCE (zone confinée par design).
contains_commercial_signal_outside_reassurance(section_key, content) if {
	section_key != "S_REASSURANCE"
	commercial_signals := {"prix", "promo", "stock", "panier", "livraison", "ajouter au panier"}
	some signal in commercial_signals
	contains(lower(content), signal)
}

# ── Raisons de refus (introspectable côté NestJS) ────────────────────────────
#
# Les règles deny[reason] permettent au gateway de logger précisément
# pourquoi une écriture a été refusée (insert dans __seo_r2_qa_reviews).

deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.feature_flag_r2_v2_enabled != true
	reason := "denied: R2_V2_ENABLED feature flag is OFF (kill-switch active)"
}

deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.feature_flag_r2_v2_enabled == true
	input.flag_state != "enabled"
	reason := sprintf("denied: pipeline flag_state=%v (require 'enabled')", [input.flag_state])
}

deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.feature_flag_r2_v2_enabled == true
	input.flag_state == "enabled"
	input.lock_active == true
	reason := "denied: pipeline cannot overwrite active lock (human authority preserved)"
}

deny contains reason if {
	not allow
	input.governance_decision == "suppressed"
	not is_number(input.canonical_target_type_id)
	reason := "denied: decision=suppressed requires canonical_target_type_id (non-null integer)"
}

deny contains reason if {
	not allow
	input.governance_decision == "suppressed"
	is_number(input.canonical_target_type_id)
	input.canonical_target.decision != "index"
	reason := sprintf("denied: SUPPRESSED canonical chain detected — target decision=%v (must be 'index', no SUPPRESSED→SUPPRESSED chains)", [input.canonical_target.decision])
}

deny contains reason if {
	not allow
	input.governance_decision == "suppressed"
	is_number(input.canonical_target_type_id)
	input.canonical_target.pg_id != input.pg_id
	reason := sprintf("denied: cross-gamme canonical forbidden — target pg_id=%v, self pg_id=%v", [input.canonical_target.pg_id, input.pg_id])
}

deny contains reason if {
	not allow
	input.governance_decision == "index"
	not is_non_empty_string(input.content_hash)
	reason := "denied: decision=index requires non-empty content_hash (no INDEX without content)"
}

deny contains reason if {
	not allow
	input.eligibility_score
	not is_valid_eligibility_score(input.eligibility_score)
	reason := sprintf("denied: eligibility_score=%v outside [0, 100] range", [input.eligibility_score])
}

deny contains reason if {
	not allow
	input.retry_count
	not is_valid_retry_count(input.retry_count)
	reason := sprintf("denied: retry_count=%v exceeds max (2)", [input.retry_count])
}

deny contains reason if {
	not allow
	input.source_kind == "human_curated"
	not is_non_empty_string(input.actor)
	reason := "denied: human_curated requires non-empty actor (audit-trail)"
}

deny contains reason if {
	not allow
	input.source_kind == "human_validated_llm"
	not is_non_empty_string(input.actor)
	reason := "denied: human_validated_llm requires non-empty actor (audit-trail)"
}

# Forbidden commercial signal in non-reassurance section
deny contains reason if {
	contains_commercial_signal_outside_reassurance(input.section_key, input.section_content)
	reason := sprintf("denied: commercial signal in section '%v' — only legal in S_REASSURANCE", [input.section_key])
}

# Catch-all : source_kind non reconnue → deny par défaut
deny contains reason if {
	not allow
	known_kinds := {
		"human_curated",
		"human_validated_llm",
		"pipeline_generated",
	}
	not known_kinds[input.source_kind]
	reason := sprintf("denied: unknown source_kind %v", [input.source_kind])
}
