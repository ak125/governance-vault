# =============================================================================
# SEO Content — R2 Runtime Read Policy (ADR-072)
# =============================================================================
#
# Rôle : enforcer les invariants CQRS read-side + DDD bounded contexts + 5
# prerequisites full-scale launch pour le pipeline R2 v2.
#
# Consommé par (futur, PR 2D monorepo) :
#   - backend/src/modules/seo/r2/gates/r2-runtime-read-evaluator.service.ts
#     (WASM bundle embedded, sync eval < 1ms)
#   - frontend/app/routes/pieces.$gamme.$marque.$modele.$type[.]html.tsx
#     (validation runtime read query au server-load time, dev mode debug)
#   - backend/src/modules/seo/admin/r2-full-scale-launch-gate.controller.ts
#     (validation 5 prerequisites avant flip feature flag V2 full-scale)
#
# Discipline canon (MEMORY feedback_opa_rego_invariants_only) :
#   Cette policy enforce des INVARIANTS architecturaux uniquement.
#   Aucun scoring, aucun weight, aucune logique métier.
#
# Source de vérité paradigme : ADR-072-r2-cqrs-ddd-snapshot-artifact.md
# Source plan : /home/deploy/.claude/plans/le-contenu-de-r2-scalable-tower.md
# =============================================================================

package seo.runtime.r2.read

import rego.v1

# ── Décision par défaut : ALLOW (fail-open pour runtime read non-destructif) ─
# Le runtime read est read-only par construction. Les deny ciblent des
# violations CQRS/DDD spécifiques. fail-open évite de bloquer toute requête
# Remix runtime si l'input policy a un champ inattendu.
default allow := true

# ── Tables/paths autorisés runtime read (CQRS read-side scope strict) ────────
#
# Le runtime Remix ne peut lire QUE :
#   - __seo_r2_pages (index parent + current_snapshot_id pointer)
#   - __seo_r2_page_snapshot (published artifact immutable)
#
# Toute lecture d'une autre table SEO R2 au request time = violation CQRS.
# Note : caches Redis (ex: r2:snapshot:{pgId}:{typeId}) sont OK car ce sont
# des dérivés du snapshot, pas une SoT alternative.

allowed_runtime_tables := {
	"__seo_r2_pages",
	"__seo_r2_page_snapshot",
}

# ── Bounded contexts owners (ADR-072 §2 DDD) ─────────────────────────────────
#
# Mapping aggregate_type → owner_module. Toute écriture cross-context doit
# passer par integration events (outbox), pas par accès direct SoT.

bounded_context_owners := {
	"R8VehicleSnapshot": "modules/seo/r8",
	"R1GammeContext": "modules/seo/r1",
	"VehiclePartKnowledgeFact": "modules/seo/r2/services/kg",
	"ValidatedWikiEvidence": "modules/seo/r2/services/research",
	"R2PageSnapshot": "modules/seo/r2/services/render",
}

# ── 5 Prerequisites full-scale launch (ADR-070 Round 6 canon) ────────────────
#
# Tous les 5 doivent être true avant flip feature flag R2_V2_FULL_SCALE.

full_scale_prerequisites := {
	"golden_examples_validated",
	"business_signature_validated",
	"internal_difference_score_calibrated",
	"r1_completeness_audited",
	"r8_snapshot_stability_verified",
}

# ── DENY 1 : CQRS runtime read scope strict ──────────────────────────────────
#
# Runtime ne peut lire QUE __seo_r2_pages + __seo_r2_page_snapshot.
# Toute lecture d'une autre table SEO R2 au request time = bug CQRS.

deny contains reason if {
	input.runtime_query == true
	is_string(input.reads_table)
	not allowed_runtime_tables[input.reads_table]
	reason := sprintf("denied: ADR-072 §1 — CQRS runtime read scope strict. Runtime peut lire __seo_r2_pages OR __seo_r2_page_snapshot uniquement (got reads_table=%v). Si tu as besoin d'autres données (KG facts, WIKI evidence, R8 snapshot raw), elles doivent déjà être projetées dans rendered_sections JSONB du snapshot publié — JAMAIS de query live multi-source au request time.", [input.reads_table])
}

# ── DENY 2 : No live compose au request time ─────────────────────────────────
#
# Aucun appel R2CompositionService / R2DataLoaderService / R2KnowledgeGraphService
# au request time. Compose = batch async background uniquement.

deny contains reason if {
	input.runtime_query == true
	input.performs_live_compose == true
	reason := "denied: ADR-072 §1 — CQRS no live compose. Compose pipeline = BullMQ async workers uniquement. Runtime Remix DOIT lire le published snapshot __seo_r2_page_snapshot (via __seo_r2_pages.current_snapshot_id pointer + Redis L1 cache). Si snapshot absent → 404 propre + enqueue async compose, JAMAIS de compose live au request time."
}

# ── DENY 3 : DDD bounded context isolation ───────────────────────────────────
#
# Un module ne peut JAMAIS écrire dans la SoT d'un autre bounded context.
# Communication cross-context = integration events via __seo_outbox_event.

deny contains reason if {
	input.cross_context_write == true
	is_string(input.aggregate_type)
	is_string(input.actor_module)
	owner := bounded_context_owners[input.aggregate_type]
	input.actor_module != owner
	reason := sprintf("denied: ADR-072 §2 — DDD bounded context isolation. Aggregate '%v' est owned par '%v', mais actor_module='%v' tente une écriture directe. Communication cross-context DOIT passer par integration events (__seo_outbox_event + OutboxRelayService BullMQ). Eventual consistency assumée — pas de transactions distribuées.", [input.aggregate_type, owner, input.actor_module])
}

# ── DENY 4 : 5 prerequisites full-scale launch mandatory ─────────────────────
#
# Avant flip R2_V2_FULL_SCALE feature flag, tous les 5 prerequisites doivent
# être validés (canon ADR-070 Round 6).

deny contains reason if {
	input.full_scale_launch_enabled == true
	some prerequisite in full_scale_prerequisites
	not prerequisite_satisfied(prerequisite, input)
	reason := sprintf("denied: ADR-072 §10 — 5 prerequisites full-scale launch mandatory (canon ADR-070 Round 6). Prerequisite '%v' not satisfied. Tous les 5 (golden_examples_validated, business_signature_validated, internal_difference_score_calibrated, r1_completeness_audited, r8_snapshot_stability_verified) DOIVENT être true avant V2 full-scale launch. Pilote V1 measurement gate doit confirmer empiriquement avant cette bascule.", [prerequisite])
}

# Helper : true if input.prerequisites_status[name] == true
prerequisite_satisfied(name, obj) if {
	obj.prerequisites_status[name] == true
}

# ── Audit reasons (toujours émises pour observabilité) ───────────────────────

# Surface info reason même si allow=true, pour logging traces OTel.
audit contains info if {
	input.runtime_query == true
	allowed_runtime_tables[input.reads_table]
	info := sprintf("audit: runtime read OK on table=%v", [input.reads_table])
}
