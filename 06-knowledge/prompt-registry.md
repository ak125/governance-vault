# Canonical Prompt Registry — R0 à R8

> **Date** : 2026-03-14
> **Version** : 1.0.0
> **Statut** : ACTIVE

Ce registre est la table de vérité reliant chaque rôle canonique à son triplet (planner/generator/validator), ses agents, services, tables et routes réels.

---

## Matrice par rôle

### R0_HOME

| Couche | Artefact |
|--------|----------|
| Planner | — (pas de planner dédié) |
| Generator | — (pas de generator dédié) |
| Validator prompt | — |
| Execution agent | `.claude/agents/r0-home-execution.md` |
| Validator agent | `.claude/agents/r0-home-validator.md` |
| Skill reference | — |
| Page contract | `backend/src/config/r0-page-contract.constants.ts` |
| Services | routes frontend home |
| Tables DB | — |
| Routes frontend | `/` (home) |

---

### R1_ROUTER

| Couche | Artefact |
|--------|----------|
| Planner | `.claude/prompts/R1_ROUTER/planner.md` (maximum, 191 lignes) |
| Generator | `.claude/prompts/R1_ROUTER/generator.md` (hardened) |
| Validator prompt | `.claude/prompts/R1_ROUTER/validator.md` |
| Execution agent | — (inline via R1ContentPipelineService) |
| Validator agent | `.claude/agents/r1-router-validator.md` (maximum, 231 lignes) |
| Content batch | `.claude/agents/r1-content-batch.md` |
| Skill reference | `.claude/skills/.../references/r1-router-role.md` |
| Page contract | `backend/src/config/page-contract-r1.schema.ts` |
| Keyword plan | `backend/src/config/r1-keyword-plan.constants.ts` |
| Services | `r1-content-pipeline.service.ts`, `r1-keyword-plan-gates.service.ts`, `content-refresh.processor.ts` |
| LLM templates | `r1_intent_lock`, `r1_serp_pack`, `r1_section_copy`, `r1_gatekeeper` |
| Tables DB | `__seo_gamme_purchase_guide` (colonnes r1_*), `__seo_r1_keyword_plan` |
| Routes frontend | `/pieces/{slug}-{pgId}.html` |

---

### R2_PRODUCT

| Couche | Artefact |
|--------|----------|
| Planner | — (pas de planner dédié) |
| Generator | — (pas de generator prompt dédié) |
| Validator prompt | — |
| Execution agent | — |
| Validator agent | `.claude/agents/r2-product-validator.md` |
| Keyword planner | `.claude/agents/r2-keyword-planner.md` |
| Skill reference | `.claude/skills/.../references/r2-product-role.md` |
| Page contract | `backend/src/config/page-contract-r2.schema.ts` |
| Keyword plan | `backend/src/config/r2-keyword-plan.constants.ts` |
| Services | services produit / catalogue |
| Tables DB | `__seo_r2_keyword_plan` |
| Routes frontend | `/pieces/{gamme}/{marque}/{modele}/{type}.html` |

---

### R3_CONSEILS

| Couche | Artefact |
|--------|----------|
| Planner | `.claude/prompts/R3_CONSEILS/planner.md` (maximum, 195 lignes) |
| Generator | `.claude/prompts/R3_CONSEILS/generator.md` (hardened, S4 gate procédurale) |
| Validator prompt | `.claude/prompts/R3_CONSEILS/validator.md` |
| Execution agent | — (inline via conseil-enricher) |
| Validator agent | `.claude/agents/r3-conseils-validator.md` (maximum, 235 lignes) |
| Image prompt | `.claude/agents/r3-image-prompt.md` |
| Skill reference | `.claude/skills/.../references/conseils-role.md` |
| Page contract | `backend/src/config/page-contract-r3.schema.ts` |
| Keyword plan | `backend/src/config/keyword-plan.constants.ts` |
| Services | `conseil-enricher.service.ts`, `content-refresh.processor.ts` |
| LLM templates | `seo_content_R3` |
| Tables DB | `__seo_gamme_conseil`, `__seo_r3_keyword_plan` |
| Routes frontend | `/blog-pieces-auto/{alias}` |

---

### R4_REFERENCE

| Couche | Artefact |
|--------|----------|
| Planner | `.claude/prompts/R4_REFERENCE/planner.md` |
| Generator | `.claude/prompts/R4_REFERENCE/generator.md` (hardened) |
| Validator prompt | `.claude/prompts/R4_REFERENCE/validator.md` |
| Execution agent | `.claude/agents/r4-reference-execution.md` |
| Validator agent | `.claude/agents/r4-reference-validator.md` |
| Content batch | `.claude/agents/r4-content-batch.md` |
| Keyword planner | `.claude/agents/r4-keyword-planner.md` |
| Skill reference | `.claude/skills/.../references/r4-reference-role.md` |
| Page contract | `backend/src/config/page-contract-r4.schema.ts`, `page-contract-r4-media.schema.ts` |
| Keyword plan | `backend/src/config/r4-keyword-plan.constants.ts` |
| Services | `ReferenceService`, `page-role-validator.service.ts`, `content-refresh.processor.ts` |
| LLM templates | `seo_content_R4` |
| Tables DB | `__seo_reference`, `__seo_r4_keyword_plan` |
| Routes frontend | `/reference-auto/{slug}`, `/reference-auto/intent/{intent}`, `/reference-auto/systeme/{system}` |

---

### R5_DIAGNOSTIC

| Couche | Artefact |
|--------|----------|
| Planner | `.claude/prompts/R5_DIAGNOSTIC/planner.md` (maximum, 191 lignes) |
| Generator | `.claude/prompts/R5_DIAGNOSTIC/generator.md` (hardened) |
| Validator prompt | `.claude/prompts/R5_DIAGNOSTIC/validator.md` |
| Execution agent | `.claude/agents/r5-diagnostic-execution.md` |
| Validator agent | `.claude/agents/r5-diagnostic-validator.md` (maximum, 235 lignes) |
| Skill reference | `.claude/skills/.../references/r5-diagnostic-role.md` |
| Page contract | `backend/src/config/page-contract-r5.schema.ts` |
| Keyword plan | `backend/src/config/r5-diagnostic.constants.ts` |
| Services | `diagnostic.service.ts`, `diagnostic.controller.ts`, `content-refresh.processor.ts` |
| Schemas | `diagnostic-contract.schema.ts`, `diagnostic-input.schema.ts`, `evidence-pack.schema.ts` |
| Tables DB | `__seo_gamme_diagnostic` (si existe) |
| Routes frontend | `/diagnostic-auto/{slug}`, `/diagnostic-auto/`, `/diagnostic` |

---

### R6_GUIDE_ACHAT

| Couche | Artefact |
|--------|----------|
| Planner | `.claude/prompts/R6_GUIDE_ACHAT/planner.md` (maximum, 198 lignes) |
| Generator | `.claude/prompts/R6_GUIDE_ACHAT/generator.md` (hardened, price gate) |
| Validator prompt | `.claude/prompts/R6_GUIDE_ACHAT/validator.md` |
| Execution agent | — (inline via buying-guide-enricher) |
| Validator agent | `.claude/agents/r6-guide-achat-validator.md` (maximum, 254 lignes) |
| Support validator | `.claude/agents/r6-support-validator.md` (hors matrice cœur) |
| Content batch | `.claude/agents/r6-content-batch.md` |
| Keyword planner | `.claude/agents/r6-keyword-planner.md` |
| Image prompt | `.claude/agents/r6-image-prompt.md` |
| Skill reference | `.claude/skills/.../references/guide-achat-role.md` |
| Page contract | `backend/src/config/page-contract-r6.schema.ts` |
| Keyword plan | `backend/src/config/r6-keyword-plan.constants.ts` |
| Services | `buying-guide-enricher.service.ts`, `content-refresh.processor.ts` |
| Tables DB | `__seo_gamme_purchase_guide`, `__seo_r6_keyword_plan` |
| Routes frontend | `/guide-achat/{alias}` |

---

### R7_BRAND

| Couche | Artefact |
|--------|----------|
| Planner | `.claude/prompts/R7_BRAND/planner.md` |
| Generator | `.claude/prompts/R7_BRAND/generator.md` (hardened) |
| Validator prompt | `.claude/prompts/R7_BRAND/validator.md` |
| Execution agent | `.claude/agents/r7-brand-execution.md` |
| Validator agent | `.claude/agents/r7-brand-validator.md` |
| RAG generator | `.claude/agents/r7-brand-rag-generator.md` |
| Keyword planner | `.claude/agents/r7-keyword-planner.md` |
| Skill reference | `.claude/skills/.../references/r7-brand-role.md` |
| Page contract | `backend/src/config/page-contract-r7.schema.ts` |
| Keyword plan | `backend/src/config/r7-keyword-plan.constants.ts` |
| Schema | `backend/src/config/brand-role-map.schema.ts` |
| RAG | `/opt/automecanik/rag/knowledge/constructeurs/{brand}.md` + `role_map.json` |
| Tables DB | `__seo_r7_keyword_plan` |
| Routes frontend | `/constructeurs/{brand}` |

---

### R8_VEHICLE

| Couche | Artefact |
|--------|----------|
| Planner | `.claude/prompts/R8_VEHICLE/planner.md` |
| Generator | `.claude/prompts/R8_VEHICLE/generator.md` (hardened) |
| Validator prompt | `.claude/prompts/R8_VEHICLE/validator.md` |
| Execution agent | `.claude/agents/r8-vehicle-execution.md` |
| Validator agent | `.claude/agents/r8-vehicle-validator.md` |
| Keyword planner | `.claude/agents/r8-keyword-planner.md` |
| Skill reference | `.claude/skills/.../references/r8-vehicle-role.md` |
| Page contract | `backend/src/config/page-contract-r8.schema.ts` |
| Keyword plan | `backend/src/config/r8-keyword-plan.constants.ts` |
| Services | `vehicle-rag-generator.service.ts`, `R8VehicleEnricherService` |
| Tables DB | `__seo_r8_*` (7 tables) |
| Routes frontend | `/vehicule/{slug}` |

---

## Orchestrateur transverse

| Artefact | Path |
|----------|------|
| Keyword planner orchestrateur | `.claude/agents/keyword-planner.md` (canon-aware) |
| Page roles canon | `.claude/skills/.../references/page-roles.md` |
| Gouvernance G1-G5 | `.claude/skills/.../references/page-roles.md` (section Gouvernance) |
| Stop conditions partagées | `.claude/prompts/_shared/stop-conditions.md` |
| Quality constraints partagées | `.claude/prompts/_shared/quality-constraints.md` |
| Upstream required partagé | `.claude/prompts/_shared/upstream-required.md` |
| Write/publish boundary partagé | `.claude/prompts/_shared/write-publish-boundary.md` |

---

## Compteurs

| Type | Nombre |
|------|--------|
| Prompts (planner+generator+validator) | 7 × 3 = 21 |
| Agents exécution | 5 (R0, R4, R5, R7, R8) |
| Agents validator | 10 (R0-R8 + R6_SUPPORT) |
| Agents keyword planner | 6 (R2, R4, R6, R7, R8 + orchestrateur) |
| Agents content batch | 3 (R1, R4, R6) |
| Agents image prompt | 2 (R3, R6) |
| Skill references | 9 (page-roles + 8 rôles) |
| Blocs partagés | 4 (_shared/) |
| **Total artefacts** | **55** |

---

## Règle de maintenance

1. Tout nouvel artefact prompt/agent/skill doit être ajouté à ce registre
2. Tout artefact supprimé doit être retiré du registre
3. Les paths doivent pointer vers des fichiers existants (vérifier avec `ls`)
4. Ce registre est la seule source de vérité pour la cartographie des prompts
