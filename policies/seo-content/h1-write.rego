# =============================================================================
# SEO Content — H1 Write Policy (PR-V)
# =============================================================================
#
# Rôle : autorise / refuse les écritures sur la valeur d'un H1 SEO.
#
# Consommé par (futur, PR-C dans monorepo) :
#   - backend/src/modules/seo/governance/opa-policy-engine.service.ts (WASM
#     bundle embedded, sync eval < 1ms)
#   - backend/src/modules/seo/governance/seo-content-write.service.ts (single
#     write path, decorator @SeoFieldGuard)
#
# Source de l'autorité (qui peut écrire quoi) :
#   ak125/nestjs-remix-monorepo : .spec/00-canon/repository-registry/seo-field-authority.yaml
#   PR-B #535 — `authoritative_writers` et `denied_writers` du field 'h1'.
#
# Cette policy applique ces décisions au runtime. La policy elle-même ne définit
# PAS l'authorité — elle la fait respecter.
#
# Verdict empirique qui motive le verrou : PR-A1 #532 (2026-05-15) — 13/23
# pages R1 audités avec H1 shifting / cross-gamme misassignment, cause probable
# bulk update SQL avec mauvaise jointure. Field Authority + OPA = défense en
# profondeur pour prévenir toute récurrence.
#
# Plan source : /home/deploy/.claude/plans/lors-du-audite-seo-concurrent-swan.md §6 Phase C
# =============================================================================

package seo.content.h1.write

import rego.v1

# ── Décision par défaut : DENY (fail-closed) ─────────────────────────────────
#
# Memory : feedback_no_touch_meta_h1_if_optimized (STRICT) — toute écriture
# non-explicitement autorisée par les règles ci-dessous est refusée.

default allow := false

# ── Règles d'autorisation (ordre d'écriture, sans priorité — toutes évaluées) ─

# Règle 1 : human_curated
# Une écriture humaine explicite depuis l'admin-ui (IsAdminGuard authentifié)
# est toujours autorisée. Surpasse les locks éventuels (humain = autorité finale).
allow if {
	input.source_kind == "human_curated"
	is_non_empty_string(input.actor)
}

# Règle 2 : human_validated_llm
# Une écriture LLM qui a été validée explicitement par un humain (flip de source
# au moment de la validation admin). L'actor est obligatoire (audit-trail).
allow if {
	input.source_kind == "human_validated_llm"
	is_non_empty_string(input.actor)
}

# Règle 3 : legacy_recovery
# Réservé Phase E. Doit :
#   - Provenir d'un event 'proposed' référencé (input.proposed_event.event_id)
#   - Porter une evidence_tier ∈ exact_match_* (jamais 'unknown' ni 'heuristic_*')
#   - Le flag GrowthBook 'seo.h1.recovery.enabled' doit être ON
#   - L'asset ne doit pas avoir de lock actif (un lock actif signifie qu'une
#     écriture authoritative récente est en place — ne pas la remplacer)
allow if {
	input.source_kind == "legacy_recovery"
	input.flag_state == "enabled"
	is_non_empty_string(input.proposed_event.event_id)
	input.proposed_event.parent_event_kind == "proposed"
	is_exact_match_tier(input.evidence_tier)
	not input.lock_active
}

# Règle 4 : deterministic_builder
# Builder déterministe (template hardcoded, sans LLM). Autorisé si :
#   - L'actor identifie le builder (audit-trail)
#   - Aucun lock actif sur l'asset (un humain a posé un H1 → ne pas écraser)
allow if {
	input.source_kind == "deterministic_builder"
	is_non_empty_string(input.actor)
	not input.lock_active
}

# ── Helpers (predicats utilitaires) ──────────────────────────────────────────

is_non_empty_string(s) if {
	is_string(s)
	count(s) > 0
}

is_exact_match_tier(tier) if {
	exact_match_tiers := {
		"exact_match_snapshot",
		"exact_match_event_log",
		"exact_match_blog_advice",
		"exact_match_builder_template",
	}
	exact_match_tiers[tier]
}

# ── Raisons de refus (introspectable côté NestJS) ────────────────────────────
#
# Les règles deny[reason] permettent au gateway de logger précisément pourquoi
# une écriture a été refusée (insert dans __seo_policy_evaluations en Phase C).

deny contains reason if {
	not allow
	input.source_kind == "llm_generated_direct"
	reason := "denied: llm_generated_direct is in denied_writers (canon enforcement)"
}

deny contains reason if {
	not allow
	input.source_kind == "legacy_recovery"
	input.flag_state != "enabled"
	reason := "denied: legacy_recovery requires flag_state='enabled' (Phase E rollout)"
}

deny contains reason if {
	not allow
	input.source_kind == "legacy_recovery"
	input.flag_state == "enabled"
	not is_exact_match_tier(input.evidence_tier)
	reason := sprintf("denied: legacy_recovery requires evidence_tier in exact_match_* (got %v)", [input.evidence_tier])
}

deny contains reason if {
	not allow
	input.source_kind == "deterministic_builder"
	input.lock_active == true
	reason := "denied: deterministic_builder cannot overwrite an active lock"
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

# Catch-all : source_kind non reconnue → deny par défaut.
deny contains reason if {
	not allow
	known_kinds := {
		"human_curated",
		"human_validated_llm",
		"legacy_recovery",
		"deterministic_builder",
		"llm_generated_direct",
	}
	not known_kinds[input.source_kind]
	reason := sprintf("denied: unknown source_kind %v (not in authoritative_writers nor denied_writers)", [input.source_kind])
}
