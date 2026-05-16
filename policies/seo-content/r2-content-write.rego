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

# Règle 1 : human_curated (NON-SUPPRESSED)
# Écriture humaine explicite admin-ui (IsAdminGuard authentifié). Toujours
# autorisée pour decisions ≠ suppressed. Pour `suppressed`, la Règle 4
# (human_curated_suppressed) impose les invariants canonical (anti-chain).
# Cf ADR-067 2026-05-15 : SUPPRESSED même humain doit avoir canonical valide.
allow if {
	input.source_kind == "human_curated"
	is_non_empty_string(input.actor)
	not input.governance_decision == "suppressed"
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
#   - ADR-070 (2026-05-16) prerequisites INDEX strict (R5+R6+R7 doctrine) :
#       - R8 snapshot CADRE : r8_snapshot_status ∈ {minimal, enriched, stale}
#       - R1 gamme context CADRE : r1_gamme_context_status == "loaded"
#       - MATIÈRE FACTUELLE : knowledge_facts_count > 0 OR validated_wiki_evidence_count > 0
#       - H1 disambiguation active : h1_contains_motor_power_pattern == true
#       - S_VARIANT_DISAMBIGUATION section présente
#       - Pas de specs brutes en paragraphes longs (R7 technical criteria = evidence only)
allow if {
	input.source_kind == "pipeline_generated"
	input.feature_flag_r2_v2_enabled == true
	input.flag_state == "enabled"
	not input.lock_active
	input.governance_decision == "index"
	is_non_empty_string(input.content_hash)
	is_valid_eligibility_score(input.eligibility_score)
	is_valid_retry_count(input.retry_count)
	# ADR-070 strict gates INDEX
	adr070_r8_cadre_ok(input)
	adr070_r1_cadre_ok(input)
	adr070_factual_matter_ok(input)
	adr070_disambiguation_ok(input)
	adr070_no_raw_specs_in_editorial(input)
}

# ADR-070 helpers (Round 5+6+7 strict INDEX prerequisites)

adr070_r8_cadre_ok(obj) if {
	valid_r8_snapshot_statuses[obj.r8_snapshot_status]
}

adr070_r1_cadre_ok(obj) if {
	obj.r1_gamme_context_status == "loaded"
}

# MATIÈRE FACTUELLE : KG facts > 0 OR WIKI evidence > 0 (au moins un)
adr070_factual_matter_ok(obj) if {
	is_number(obj.knowledge_facts_count)
	obj.knowledge_facts_count > 0
}

adr070_factual_matter_ok(obj) if {
	is_number(obj.validated_wiki_evidence_count)
	obj.validated_wiki_evidence_count > 0
}

adr070_disambiguation_ok(obj) if {
	obj.h1_contains_motor_power_pattern == true
	obj.s_variant_disambiguation_present == true
}

adr070_no_raw_specs_in_editorial(obj) if {
	obj.body_long_form_section_contains_raw_specs == false
}

# valid R8 snapshot statuses (canon ADR-070 §G, status enum strict Round 2)
valid_r8_snapshot_statuses := {"minimal", "enriched", "stale"}

# Règle 4 : human_curated_suppressed (manual override, ADR-067 amendment 2026-05-15)
#
# ADR-067 INTERDIT pipeline_generated → suppressed. Seul un admin humain peut
# manuellement flipper une page vers SUPPRESSED (doublon connu confirmé, page
# legacy abandonnée). Anti-canonical-chain invariants restent valables.
#
# Requiert :
#   - source_kind = "human_curated"
#   - actor non-vide (audit-trail)
#   - canonical_target_type_id non-null
#   - canonical_target.decision = "index" (no chain)
#   - canonical_target.pg_id = self.pg_id (no cross-gamme)
allow if {
	input.source_kind == "human_curated"
	is_non_empty_string(input.actor)
	input.governance_decision == "suppressed"
	is_valid_canonical_target(input)
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
# ADR-068 2026-05-16 : reject_reason DOIT être l'une des 4 raisons UNIQUES
# (productCount_under_2, data_invalid, url_impossible, compatibility_absent).
# Pas REJECT pour similarité (→ REVIEW_REQUIRED).
allow if {
	input.source_kind == "pipeline_generated"
	input.feature_flag_r2_v2_enabled == true
	input.flag_state == "enabled"
	input.governance_decision == "reject"
	is_valid_eligibility_score(input.eligibility_score)
	is_valid_reject_reason(input.reject_reason)
}

is_valid_reject_reason(r) if {
	allowed := {"productCount_under_2", "data_invalid", "url_impossible", "compatibility_absent"}
	allowed[r]
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

# ADR-067 amendment 2026-05-15 : pipeline_generated → suppressed est INTERDIT.
# Seul un admin humain (source_kind=human_curated) peut flipper vers SUPPRESSED.
deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.governance_decision == "suppressed"
	reason := "denied: ADR-067 — pipeline_generated cannot emit SUPPRESSED (manual-only via admin UI human_curated path). Compatibilité pièce prime sur similarité texte."
}

# ── ADR-068 amendment 2026-05-16 : 4 actions auto INTERDITES sur page valide ──

# Une page valide = productCount >= 2 ET compatibilité réelle.
# Si la page est valide, le pipeline NE PEUT PAS auto-noindex / canonicaliser / exclure sitemap.

# DENY 1 : pipeline → noindex_follow sur page valide (désindexation auto interdite)
deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.governance_decision == "noindex_follow"
	is_number(input.product_count)
	input.product_count >= 2
	reason := "denied: ADR-068 — pipeline_generated cannot auto-noindex a valid page (productCount>=2). Une page valide DOIT rester candidate INDEX (similarité forte → REVIEW_REQUIRED + enrichissement, jamais noindex auto)."
}

# DENY 2 : REJECT scope strict — 4 raisons UNIQUEMENT
# (productCount<2, data_invalid, url_impossible, compatibility_absent)
valid_reject_reasons := {
	"productCount_under_2",
	"data_invalid",
	"url_impossible",
	"compatibility_absent",
}

deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.governance_decision == "reject"
	is_string(input.reject_reason)
	not valid_reject_reasons[input.reject_reason]
	reason := sprintf("denied: ADR-068 — REJECT scope strict (4 raisons UNIQUES : productCount_under_2 / data_invalid / url_impossible / compatibility_absent). Got reject_reason=%v. Similarité forte n'est PAS une raison REJECT — utiliser REVIEW_REQUIRED.", [input.reject_reason])
}

# DENY 3 : Page valide INDEX/REVIEW_REQUIRED ne peut pas émettre canonical sibling
# (canonicalisation auto vers sœur interdite par ADR-068)
deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	indexable_decisions := {"index", "review_required"}
	indexable_decisions[input.governance_decision]
	is_string(input.canonical_url)
	input.canonical_url != input.self_url
	reason := sprintf("denied: ADR-068 — pipeline cannot emit canonical sibling auto on valid page (decision=%v). Canonical MUST be self for INDEX/REVIEW_REQUIRED. Canonical sibling reserved for SUPPRESSED human_curated path.", [input.governance_decision])
}

# ── ADR-070 amendment 2026-05-16 : R8+R1 first canon + INTERNAL DIFFERENCE EXHAUSTION + Technical criteria = evidence ──
#
# Formule canon Round 5 : R2Content = render(R8VehicleSnapshot, R1GammeContext, VehiclePartKnowledgeFacts, ValidatedWikiEvidence)
#   CADRE   = R8 + R1 (sans = générique, JAMAIS INDEX)
#   MATIÈRE = KG facts + WIKI evidence (sans = pauvre, JAMAIS INDEX)
#
# Round 6 : INTERNAL DIFFERENCE EXHAUSTION (L0-L3 avant L4 external)
# Round 7 : Technical criteria = evidence only (PAS éditorial — paragraphes spec dumps interdits)
#
# 5 deny invariants stricts INDEX (pipeline only) :

# DENY ADR-070 #1 : R8 snapshot CADRE requis pour INDEX
# (valid_r8_snapshot_statuses set defined near allow rule 3, canon Round 2 status enum strict)

deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.governance_decision == "index"
	not valid_r8_snapshot_statuses[input.r8_snapshot_status]
	reason := sprintf("denied: ADR-070 — R8 snapshot CADRE requis pour INDEX (got r8_snapshot_status=%v). R2 ne compose pas sans R8 parent snapshot persisté. Status valides : minimal | enriched | stale (failed → review_required, absent → review_required + enqueue r8-enrichment).", [input.r8_snapshot_status])
}

# DENY ADR-070 #2 : R1 gamme context CADRE requis pour INDEX
deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.governance_decision == "index"
	input.r1_gamme_context_status != "loaded"
	reason := sprintf("denied: ADR-070 — R1 gamme context CADRE requis pour INDEX (got r1_gamme_context_status=%v). R2 ne compose pas sans R1 parent (sections S_SELECTION_GUIDE / S_MISTAKES_AVOID / S_FAQ_GAMME / S_TECHNICAL_CRITERIA / S_REASSURANCE_METIER hérités tels quels). Status loaded requis.", [input.r1_gamme_context_status])
}

# DENY ADR-070 #3 : MATIÈRE FACTUELLE (KG facts OU WIKI validée) requise pour INDEX
# R8 + R1 seuls = CADRE générique sans valeur SEO. Au moins 1 fact KG ou 1 evidence WIKI validée requis.
deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.governance_decision == "index"
	is_number(input.knowledge_facts_count)
	is_number(input.validated_wiki_evidence_count)
	input.knowledge_facts_count == 0
	input.validated_wiki_evidence_count == 0
	reason := "denied: ADR-070 — MATIÈRE FACTUELLE requise pour INDEX (knowledge_facts_count=0 AND validated_wiki_evidence_count=0). R8+R1 CADRE seul = générique sans valeur SEO. Au moins 1 fact KG canonicalisé OU 1 evidence WIKI validée (auto_validated|human_validated) requis."
}

# DENY ADR-070 #4 : H1 + S_VARIANT_DISAMBIGUATION obligatoires pour INDEX
# Disambiguation active : H1 doit contenir power+body+years pattern, et la section S_VARIANT_DISAMBIGUATION doit exister.
deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.governance_decision == "index"
	input.h1_contains_motor_power_pattern != true
	reason := "denied: ADR-070 — H1 doit contenir motor_power_pattern (puissance + carrosserie + années) pour INDEX. R2 ne peut pas générer contenu générique type 'Pièces Renault Clio III 1.5 dCi' — DOIT être désambiguïsé activement (ex: 'Pièces Renault Clio III 1.5 dCi 88 ch 3/5 portes, 2010-2014')."
}

deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.governance_decision == "index"
	input.s_variant_disambiguation_present != true
	reason := "denied: ADR-070 — section S_VARIANT_DISAMBIGUATION obligatoire pour INDEX (disambiguation active doctrine). Explicite ce qui distingue cette page des sœurs (puissance/carrosserie/années/code moteur)."
}

# DENY ADR-070 #5 : Technical criteria = evidence only (Round 7)
# Paragraphes longs avec specs brutes répétées (>5× pattern \d+[,.]\d+\s?mm) dans une section éditoriale = INTERDIT.
# Les critères techniques DOIVENT rester dans S_COMPAT_DIFFERENCES / S_TECHNICAL_TABLE_COMPACT / S_SELECTION_WARNING uniquement.
deny contains reason if {
	not allow
	input.source_kind == "pipeline_generated"
	input.governance_decision == "index"
	input.body_long_form_section_contains_raw_specs == true
	reason := "denied: ADR-070 R7 — technical criteria = evidence only. Paragraphes longs avec specs brutes (largeur/hauteur/épaisseur mm répétés >5×) dans section éditoriale interdits. Critères techniques DOIVENT rester compacts (tableau S_TECHNICAL_TABLE_COMPACT max 5-7 lignes, warning S_SELECTION_WARNING max 2-3 phrases, mention courte S_COMPAT_DIFFERENCES). Contenu éditorial reste R1 gamme conseil + WIKI prose validée."
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
