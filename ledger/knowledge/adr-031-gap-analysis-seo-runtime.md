# ADR-031 — Gap Analysis : SEO Runtime Projection

> **Version**: 1.0.0 | **Status**: KNOWLEDGE | **Date**: 2026-05-13
> **Type**: gap-analysis
> **Related ADR**: [ADR-031](../decisions/adr/ADR-031-four-layer-content-architecture.md) (proposed), [ADR-059](../decisions/adr/ADR-059-seo-runtime-projection.md) (proposed)
> **Author**: @fafa
> **Prep for**: ADR-059 SEO Runtime Projection Architecture

## Objectif

Documenter formellement le gap entre ADR-031 (Four-Layer Content Architecture, status `proposed`) et le besoin réel d'une **projection runtime DB versionnée** entre `wiki/exports/seo/` et les pages publiques R0-R8. Cette knowledge note prépare ADR-059 en posant les preuves empiriques.

## Constat textuel

ADR-031 §Couche 3 « Consommateurs (lecture seule) » ligne 163 dit littéralement :

> « `wiki/exports/seo/` fournit la matière validée — intentions, angles, données structurées, sourcing — ; **la logique SEO R0-R8 (génération, classification, V-Level, rotation, publish gates) reste dans `nestjs-remix-monorepo`. Le wiki n'est pas un moteur SEO.** »

ADR-031 §Couche 2 ligne 154-156 :

> « Générés depuis `wiki/<entity_type>/` par scripts dédiés, avec lint + schema validation. Aucun consommateur ne lit `wiki/<entity_type>/` directement — uniquement `wiki/exports/<audience>/`. »

## Verdict architectural

ADR-031 est **valide pour la séparation documentaire** (raw / wiki / exports / consumers) mais **insuffisante pour la mécanique de projection runtime DB SEO**. Trois omissions critiques :

1. **Aucun format JSON contractuel** spécifié pour `wiki/exports/seo/<entity>.json` (juste « scripts dédiés + lint »)
2. **Aucune mécanique de projection runtime** entre exports/seo et les tables `__seo_*` (pas de mention d'`active_version_id`, de versioning, de diff-first)
3. **Aucune stratégie publish gate / rollout** au runtime (shadow mode, percent rollout, rollback granulaire)

## Preuves empiriques (audit 2026-05-13)

### 1. `wiki/exports/seo/` est vide

```
/opt/automecanik/automecanik-wiki/exports/seo/  → uniquement .gitkeep
/opt/automecanik/automecanik-wiki/exports/rag/  → populated (~50 fichiers MD)
```

Le pipeline `wiki → exports/rag/` est implémenté (`app/scripts/rag-sync/sync-wiki-exports-to-rag.py` + cron horaire D20). L'équivalent SEO est **manquant à 100 %**.

### 2. Tables de projection projetées inexistantes (0 / 7)

Recherche dans `backend/supabase/migrations/` :

| Table cible (plan ADR-059) | Existe ? |
|---|---|
| `__seo_projection_runs` | NON |
| `__seo_entity_facts` | NON |
| `__seo_entity_fact_versions` | NON |
| `__seo_entity_sources` | NON |
| `__seo_content_blocks` | NON |
| `__seo_content_block_versions` | NON |
| `__seo_projection_conflicts` | NON |

Les tables `__seo_*` existantes (30+ : `__seo_keywords`, `__seo_entity_health`, `__seo_gamme_purchase_guide`, etc.) sont **alimentées par migrations SQL brutes**, pas par projection versionnée depuis wiki canon. Aucun champ `active_version_id` / `source_wiki_commit` / `content_hash` sur ces tables.

### 3. Pages R0-R8 lisent legacy via RPC sans notion de version active

Loaders `frontend/app/routes/{pieces,gammes,marques}.*` appellent backend NestJS RPC (e.g. `get_pieces_for_type_gamme_v4()`, migration 20260128) qui retourne des templates SEO raw, sans notion « projection version active ». Aucune indirection adapter / version pointer.

### 4. Pattern de versioning éprouvé existe déjà (réutilisable)

`backend/supabase/migrations/20260125_kg_v3_versioning.sql` introduit le pattern kg_v3 sur `kg_nodes` :

- `status` enum (draft / active / deprecated)
- `valid_from` / `valid_to` timestamps
- `source_type` (e.g. specialist / oem)
- `confidence_base` numeric

Ce pattern est **utilisé en production pour le diagnostic** (ADR-033). Le réutiliser tel quel pour la projection SEO évite d'inventer un nouveau modèle de versioning.

### 5. SEO v9 fondation MERGED (PRs #398, #399, #400)

Les fondations sont prêtes pour brancher une projection :

- PR #398 : audit gap matrix `docs/seo/legacy_to_monorepo_gap_matrix.md`
- PR #399 : `@repo/seo-role-contracts`, `SeoSurfaceRegistry`, `SeoVariantFamilyRegistry`, `SeoFeatureFlagRegistry`
- PR #400 : `SeoCanonicalService`, `R2IndexabilityGate`, `SeoIndexabilityPolicyService`

ADR-059 s'appuie sur ces registries existants, pas de duplication.

## Recommandation

Adopter **ADR-059 — SEO Runtime Projection Architecture** (status `proposed`, supplements ADR-031) qui spécifie :

1. Format JSON contractuel `wiki/exports/seo/<entity_type>/<slug>.json` avec `schema_version` + `projection_contract_version`
2. Projection runtime DB via pattern kg_v3 réutilisé (7 tables + 2 materialized views CONCURRENT REFRESH)
3. Runner diff-first avec 2 queues BullMQ découplées (write + refresh) — `REFRESH MV` jamais dans transaction d'écriture
4. Replay deterministic via snapshots immutables content-addressed (tar.zst, pas git checkout)
5. Rollout via GrowthBook self-hosted (% rollout 1→10→50→100, advisory-only)
6. 3 règles fondamentales : exports = vues éphémères, no direct page SQL, projections never generate canon

ADR-059 ne dépend pas de l'acceptation d'ADR-031 (les 2 ADRs évoluent sur des tracks parallèles). Le terme `supplements` est utilisé plutôt que `amends` pour cette raison.

## Références

- ADR-031 : [Four-Layer Content Architecture](../decisions/adr/ADR-031-four-layer-content-architecture.md) (status: proposed)
- ADR-033 : Wiki gamme-diagnostic relations (accepted, pattern kg_v3 utilisé en prod)
- ADR-027 : R5 sunset (diagnostic projeté conditionnel R3 S2_DIAG)
- ADR-046 : R-stack single-generator (projection alimente le generator unifié)
- ADR-055 : SEO shadow mode (renforcé par % rollout GrowthBook)
- Migration `20260125_kg_v3_versioning.sql` (pattern réutilisé)
- PRs SEO v9 MERGED : #398, #399, #400
