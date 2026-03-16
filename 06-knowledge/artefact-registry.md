# Canonical Artefact Registry R0-R8

> Date : 2026-03-14
> Version : 1.0.0

## Par rôle

### R0_HOME

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| Planner | `.claude/prompts/R0_HOME/planner.md` | — (pas de prompt, surface statique) |
| Generator | `.claude/prompts/R0_HOME/generator.md` | — |
| Validator | `.claude/agents/r0-home-validator.md` | ✅ |
| Execution | `.claude/agents/r0-home-execution.md` | ✅ |
| Role reference | — | — (couvert par page-roles.md) |
| Contrat | `backend/src/config/r0-page-contract.constants.ts` | ✅ |
| Consumer réel | routes frontend home | — |

### R1_ROUTER

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| Planner | `.claude/prompts/R1_ROUTER/planner.md` | ✅ |
| Generator | `.claude/prompts/R1_ROUTER/generator.md` | ✅ hardened |
| Validator | `.claude/agents/r1-router-validator.md` | ✅ maximum |
| Role reference | `.claude/skills/.../references/r1-router-role.md` | ✅ canon |
| Contrat | `backend/src/config/page-contract-r1.schema.ts` | ✅ |
| KP constants | `backend/src/config/r1-keyword-plan.constants.ts` | ✅ |
| Pipeline service | `r1-content-pipeline.service.ts` | ✅ |
| Gates service | `r1-keyword-plan-gates.service.ts` | ✅ |
| Route frontend | `pieces.$slug.tsx` | ✅ |
| LLM templates | `r1_intent_lock`, `r1_serp_pack`, `r1_section_copy`, `r1_gatekeeper` | ✅ hardened |

### R2_PRODUCT

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| Planner | — | — (transactionnel, pas de generation editoriale) |
| Generator | — | — |
| Validator | `.claude/agents/r2-product-validator.md` | ✅ |
| Role reference | `.claude/skills/.../references/r2-product-role.md` | ✅ canon |
| Contrat | `backend/src/config/page-contract-r2.schema.ts` | — (a verifier) |
| KP constants | `backend/src/config/r2-keyword-plan.constants.ts` | ✅ |
| Route frontend | `pieces.$gamme.$marque.$modele.$type[.]html.tsx` | ✅ |

### R3_CONSEILS

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| Planner | `.claude/prompts/R3_CONSEILS/planner.md` | ✅ |
| Generator | `.claude/prompts/R3_CONSEILS/generator.md` | ✅ hardened (S4 gate) |
| Validator | `.claude/agents/r3-conseils-validator.md` | ✅ maximum |
| Role reference | `.claude/skills/.../references/conseils-role.md` | ✅ canon |
| Contrat | `backend/src/config/page-contract-r3.schema.ts` | ✅ |
| KP constants | `backend/src/config/keyword-plan.constants.ts` | ✅ |
| Enricher | `conseil-enricher.service.ts` | ✅ |
| Refresh | `content-refresh.service.ts` | ✅ |
| Route frontend | `blog-pieces-auto/{alias}` | ✅ |
| LLM templates | `seo_content_R3` | ✅ hardened |
| Agent batch | `.claude/agents/conseil-batch.md` | ✅ |

### R4_REFERENCE

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| Planner | `.claude/prompts/R4_REFERENCE/planner.md` | ✅ |
| Generator | `.claude/prompts/R4_REFERENCE/generator.md` | ✅ hardened |
| Validator | `.claude/agents/r4-reference-validator.md` | ✅ |
| Execution | `.claude/agents/r4-reference-execution.md` | ✅ |
| Role reference | `.claude/skills/.../references/r4-reference-role.md` | ✅ canon |
| Contrat | `backend/src/config/page-contract-r4.schema.ts` | ✅ |
| Media schema | `backend/src/config/page-contract-r4-media.schema.ts` | ✅ |
| KP constants | `backend/src/config/r4-keyword-plan.constants.ts` | ✅ |
| Route frontend | `reference-auto.$slug.tsx` | ✅ |
| LLM templates | `seo_content_R4` | ✅ hardened |
| Agent batch | `.claude/agents/r4-content-batch.md` | ✅ |

### R5_DIAGNOSTIC

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| Planner | `.claude/prompts/R5_DIAGNOSTIC/planner.md` | ✅ |
| Generator | `.claude/prompts/R5_DIAGNOSTIC/generator.md` | ✅ hardened |
| Validator | `.claude/agents/r5-diagnostic-validator.md` | ✅ maximum |
| Execution | `.claude/agents/r5-diagnostic-execution.md` | ✅ |
| Role reference | `.claude/skills/.../references/r5-diagnostic-role.md` | ✅ canon |
| Contrat | `backend/src/config/page-contract-r5.schema.ts` | ✅ |
| Constants | `backend/src/config/r5-diagnostic.constants.ts` | ✅ |
| Diagnostic engine | `diagnostic-contract.schema.ts`, `evidence-pack.schema.ts` | ✅ |
| Route frontend | `diagnostic-auto.$slug.tsx` | ✅ |

### R6_GUIDE_ACHAT

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| Planner | `.claude/prompts/R6_GUIDE_ACHAT/planner.md` | ✅ |
| Generator | `.claude/prompts/R6_GUIDE_ACHAT/generator.md` | ✅ hardened (price gate) |
| Validator | `.claude/agents/r6-guide-achat-validator.md` | ✅ maximum |
| Role reference | `.claude/skills/.../references/guide-achat-role.md` | ✅ canon |
| Contrat | `backend/src/config/page-contract-r6.schema.ts` | ✅ |
| KP constants | `backend/src/config/r6-keyword-plan.constants.ts` | ✅ |
| Enricher | `buying-guide-enricher.service.ts` | ✅ |
| Refresh | `content-refresh.service.ts` | ✅ |
| Route frontend | guide-achat | ✅ |
| Agent batch | `.claude/agents/r6-content-batch.md` | ✅ |
| Agent KP | `.claude/agents/r6-keyword-planner.md` | ✅ |

### R7_BRAND

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| Planner | `.claude/prompts/R7_BRAND/planner.md` | ✅ |
| Generator | `.claude/prompts/R7_BRAND/generator.md` | ✅ hardened |
| Validator | `.claude/agents/r7-brand-validator.md` | ✅ |
| Execution | `.claude/agents/r7-brand-execution.md` | ✅ |
| Role reference | `.claude/skills/.../references/r7-brand-role.md` | ✅ canon |
| Contrat | `backend/src/config/page-contract-r7.schema.ts` | ✅ |
| KP constants | `backend/src/config/r7-keyword-plan.constants.ts` | ✅ |
| RAG generator | `.claude/agents/r7-brand-rag-generator.md` | ✅ |
| Agent KP | `.claude/agents/r7-keyword-planner.md` | ✅ |
| Route frontend | `constructeurs.$.tsx` | ✅ |

### R8_VEHICLE

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| Planner | `.claude/prompts/R8_VEHICLE/planner.md` | ✅ |
| Generator | `.claude/prompts/R8_VEHICLE/generator.md` | ✅ hardened |
| Validator | `.claude/agents/r8-vehicle-validator.md` | ✅ |
| Execution | `.claude/agents/r8-vehicle-execution.md` | ✅ |
| Role reference | `.claude/skills/.../references/r8-vehicle-role.md` | ✅ canon |
| Contrat | `backend/src/config/page-contract-r8.schema.ts` | ✅ |
| KP constants | `backend/src/config/r8-keyword-plan.constants.ts` | ✅ |
| RAG generator | `vehicle-rag-generator.service.ts` | ✅ |
| Agent KP | `.claude/agents/r8-keyword-planner.md` | ✅ |
| Route frontend | `vehicule/{slug}` | ✅ |

---

## Hors matrice cœur

| Artefact | Emplacement | Statut |
|----------|-------------|--------|
| R6_SUPPORT validator | `.claude/agents/r6-support-validator.md` | ✅ (local, hors matrice) |

---

## Fichiers transversaux

| Artefact | Emplacement |
|----------|-------------|
| Page roles canon | `.claude/skills/.../references/page-roles.md` |
| Keyword planner orchestrateur | `.claude/agents/keyword-planner.md` |
| Stop conditions (shared) | `.claude/prompts/_shared/stop-conditions.md` |
| Quality constraints (shared) | `.claude/prompts/_shared/quality-constraints.md` |
| Upstream required (shared) | `.claude/prompts/_shared/upstream-required.md` |
| Write/publish boundary (shared) | `.claude/prompts/_shared/write-publish-boundary.md` |
| Role IDs enum | `backend/src/config/role-ids.ts` |
| Bridge functions | `backend/src/config/content-section-policy.ts` |
| Scoring bridge | `backend/src/config/scoring-profiles.config.ts` |

---

## Statut maximum par role

| Role | Planner | Generator | Validator | Triplet complet |
|------|---------|-----------|-----------|-----------------|
| R0 | — | — | standard | — (surface statique) |
| R1 | **maximum** | hardened | **maximum** | ✅ triplet maximum |
| R2 | — | — | standard | — (transactionnel) |
| R3 | **maximum** | hardened (S4 gate) | **maximum** | ✅ triplet maximum |
| R4 | standard | hardened | standard | ⚠️ triplet standard |
| R5 | **maximum** | hardened | **maximum** | ✅ triplet maximum |
| R6 | **maximum** | hardened (price gate) | **maximum** | ✅ triplet maximum |
| R7 | standard | hardened | standard | ⚠️ triplet standard |
| R8 | standard | hardened | standard | ⚠️ triplet standard |

**4 roles au niveau maximum** : R1, R3, R5, R6 (les plus critiques en prod)

---

## Pipeline phases

Voir [`phase-matrix.md`](phase-matrix.md) pour la matrice canonique des phases :

| Phase | Fonction |
|-------|----------|
| 1 | Ingestion + Foundation Gate |
| 1.5 | Normalisation canonique |
| 1.6 | Admissibilité métier d'usage vers R* |
| 2 | Synthèse + génération + assemblage |
| G* | Contrôle transverse (G1-G5) |

---

## Comptage

| Type | Nombre |
|------|--------|
| Prompts (planner+generator+validator) | 21 (7 roles × 3) |
| Shared prompt blocks | 4 |
| Agent execution prompts | 5 (R0, R4, R5, R7, R8) |
| Agent validators | 10 (R0-R8 + R6_SUPPORT) |
| Role references | 9 (R1-R8 + page-roles) |
| Orchestrateur | 1 (keyword-planner) |
| **Total artefacts canoniques** | **50** |
