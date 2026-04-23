---
category: design-spec
doc_family: knowledge
source_type: design
title: R8 RAG Control Plane — Design Spec
slug: r8-rag-control-plane-design
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-23"
updated_by: "@fafa"
related_adr: ["ADR-022"]
related_prs: ["ak125/nestjs-remix-monorepo#139"]
status: draft
---

# R8 RAG Control Plane — Design Spec

> Consolidation du brainstorming session 2026-04-23 entre @fafa et Claude Code (Opus 4.7 1M).
> Référence canon : [[ADR-022-r8-rag-control-plane]].
> Ce document = design source. Les artefacts (code, schemas JSON, workflows CI) sont produits ensuite.

## 1. Contexte et problème

### 1.1 Constat R8 actuel

Les pages R8 (fiche motorisation, route `constructeurs/{brand}/{model}/{type}.html`) sont quasi-identiques entre motorisations d'un même modèle. Exemple concret :

- Renault Clio III 1.5 dCi 90 ch
- Renault Clio III 1.5 dCi 106 ch

→ même H1 trame, même intro générique, mêmes familles pièces, même FAQ. Duplicate content Google risque.

### 1.2 Cause racine multi-facteurs

| Facteur | État actuel |
|---------|-------------|
| Pipeline R8 | Partiellement déployé : 1 seule page dans `__seo_r8_pages` sur 53 959 types véhicules |
| RAG véhicule | 8 fichiers `.md` uniquement, au niveau MODEL, sans variations templates |
| Enricher `r8-vehicle-enricher.service.ts` | Compose 10 blocs mais sans rotation entre motorisations du même modèle |
| S_TRUST bloc | 100 % hardcoded, identique toutes pages |
| Meta description | Générée sans qualifier fuel/power |
| H2 templates | `S_CATALOG`, `S_FAQ` sans `{power}` / `{fuel}` |
| Contrôle génération | Aucun gate : generator écrit directement dans `/rag/knowledge/` |

### 1.3 Exigence utilisateur

> "ce fichier doit être au top car il est un socle — pas de bricolage — utiliser meilleure solution, plus robuste, plus safe"
> "R7 n'est pas une référence solide : pas contrôlé"

Traduction design : ne pas répliquer un pipeline "qui marche mais pas audité". Produire un plan de contrôle **end-to-end** où chaque étape a un gate explicite.

## 2. Architecture cible

### 2.1 Principe directeur

**1 fichier RAG par model_group (~500 fichiers)** + **TemplateRotator hash-based** pour variations déterministes par `type_id`.

Refus explicite de 3 alternatives :
- 1 fichier par `type_id` (~53 000) : volume ingérable, redondance massive
- 1 fichier par couple moteur (~1 500) : granularité insuffisante pour variation UI
- Hiérarchique brand + model + motorisation overlay : aucun précédent, gold-plating

### 2.2 Flow end-to-end

```
DB véhicule + TecDoc + Wikipedia
          │
          ▼
 VehicleRagGenerator (propose mode)
          │
          ▼
 __rag_proposals (pending|approved|rejected)
          │       ▲
          ▼       │ CI validate (JSON Schema + forbidden + FK)
 PR auto (signed G3) → merge main
          │
          ▼
 /rag/knowledge/vehicles/{slug}.md
 /rag/knowledge/vehicles/{slug}.variations.yaml
 /rag/knowledge/vehicles/{slug}.role_map.json
          │
          ▼
 r8-vehicle-enricher v2 (lit HEAD git uniquement)
          │
          ▼
 TemplateRotator (hash déterministe par type_id)
          │
          ▼
 Gates pre-UPSERT : diversity ≥ 70, no dup fingerprint
          │
          ▼
 __seo_r8_pages (seo_decision: INDEX|REVIEW|REGENERATE|REJECT)
          │
          ▼
 Publish gate explicite (endpoint /api/admin/r8/:typeId/publish)
          │
          ▼
 Sitemap R8 (inclut uniquement PUBLISHED)
          │
          ▼
 Observability : metrics per-page, drift detection, weekly canary
```

## 3. Plan de contrôle — 5 couches

### L0. Source contract (DB + TecDoc)

- FK strictes, types forts, migrations versionnées
- Aucun flow auto vers RAG sans gate
- Gate : CI schema check sur migrations

### L1. Generator = Propose (jamais write direct)

- `VehicleRagGenerator` produit un diff proposé
- Stocké dans `__rag_proposals`
- Gate : JSON Schema + forbidden terms + FK check + placeholder resolution
- Approbation auto low-risk OU humaine (editorial / CODEOWNER selon risk_level)

### L2. Content repository (git, signed commits G3)

- Écriture fichier via PR reviewée uniquement
- `content_hash` SHA-256 + commit signé = audit trail
- Gate : weekly-vault-lint (pattern ADR-020 déjà prod)

### L3. Enricher R8 (lit committed only)

- Lit RAG depuis `git HEAD`, jamais proposal pending
- Compute diversity + fingerprint + QA AVANT write DB
- Si gate fail → `__seo_r8_regeneration_queue` au lieu de `__seo_r8_pages`

### L4. Publish gate explicite

- Page générée ≠ page indexée
- `seo_decision` explicite : INDEX|REVIEW|REGENERATE|REJECT
- Seul INDEX déclenche sitemap + serve en prod
- Endpoint explicite `POST /api/admin/r8/:typeId/publish`

### L5. Observability + drift detection

- Metrics per page (quality_score, diversity_score, similarity)
- Alertes drift (baisse qualité, apparition duplicates)
- Audit log append-only
- Weekly canary : sample N pages re-enrich et compare

## 4. Artefacts RAG — 3 fichiers par modèle

Split assumé (justifié par sources d'évolution différentes) :

| Artefact | Source de vérité | Cadence maj | Owner | Regenerable |
|----------|------------------|-------------|-------|-------------|
| `{slug}.md` | DB + TecDoc + Wikipedia | J+1 TecDoc sync | `VehicleRagGenerator` auto | Oui idempotent |
| `{slug}.variations.yaml` | Éditorial (templates SEO) | Manuel | Équipe contenu | Non |
| `{slug}.role_map.json` | Pipeline schema (stable) | Rarement | Canon | Oui |

### 4.1 `{slug}.md` — structure

Frontmatter YAML strict (schema `vehicle-model.schema.json`) + sections Markdown.

Champs clés :
- `schema_version`, `slug`, `doc_id` (UUIDv5), `modele_id`, `marque_id`
- `motorisations[]` avec `engine_family_key`, `fuel` enum, `cylindree_cc` int, `engine_codes[]`, `trim_level` enum, `variants[]` avec `power_ps` int et `type_ids[]` FK vers `auto_type`
- `motorisations[].specifics` : `problemes_connus`, `pieces_critiques`, `intervalles` (par motorisation, pas modèle)
- `source_of_truth{}` : provenance par champ (tecdoc|db|caradisiac|manual|wikipedia|forum|oem_doc)
- `lifecycle{}` : schema_version, created_at, last_enriched_at, last_enriched_by (service@version), content_hash, enrichment_count, source_commit
- `locked_fields[]` : chemins JSONPath protégés contre regen auto
- `risk_flags[]` : taxonomie fermée (wikipedia_sourced|auto_generated|low_confidence|missing_tecdoc|stale_data)
- `verification_status` : draft|verified|oem_verified|deprecated

Sections Markdown : `S_MODEL_IDENTITY`, `S_MODEL_TECH_SPECS`, `S_MODEL_FAMILIES`, `S_MODEL_MAINTENANCE`, `S_MODEL_FAQ_COMMON`.

### 4.2 `{slug}.variations.yaml` — structure

Frontmatter YAML strict (schema `vehicle-variations.schema.json`).

5 slots de rotation :
- `h1` : 3+ variants, salt "h1"
- `intro_motorisation` : 3+ variants, salt "intro"
- `meta_description` : 3+ variants, salt "meta", max 170 chars
- `catalog_h2` : 3+ variants, salt "cat"
- `faq_h2` : 3+ variants, salt "faq"

Chaque variant : `id`, `template`, `required_placeholders[]`, `optional_placeholders[]`.

Placeholders enum fermé : brand, model, type_name, power_ps, power_kw, fuel, engine_code, year_from, year_to, families_count, body, power_tier, delivery_info.

Quality gates : min_variants_per_slot=3, max_length_meta=170, max_length_h1=70, placeholder_validation=strict, forbidden_terms_ref=29 termes R7.

### 4.3 `{slug}.role_map.json` — structure

Mapping sections Markdown → blocs R8 de l'enricher.

Champs : `doc_type=VEHICLE_MODEL`, `doc_id`, `schema_version`, `sections[]`.

Chaque section : `section_key` (S_MODEL_*), `primary_role=R8_VEHICLE`, `purity_min` (50-100), `chunk_kind[]`, `maps_to_r8_blocks[]`.

## 5. Table `__rag_proposals` — L1 propose-pattern

### 5.1 Schema

Migration SQL complète avec :
- Colonnes cible : `target_path`, `target_slug`, `target_kind`
- Proposal content : `base_commit_sha`, `base_content_hash`, `proposed_content`, `proposed_content_hash`, `diff_unified`
- Idempotence : `input_fingerprint` (unique index partiel sur pending/validating/approved)
- Lifecycle : `status` (pending|validating|approved|rejected|merged|expired|superseded), timestamps, expires_at NOW+14j
- Classification : `risk_level` (low|medium|high), `risk_flags[]`, `diff_lines_added/removed`
- Validation results : `schema_valid`, `forbidden_terms_found[]`, `placeholders_unresolved[]`, `validation_report JSONB`
- Dependencies : `depends_on UUID`, `superseded_by UUID`
- RLS : service_role write-only, admin read+approve, anon deny

### 5.2 Classification risk_level

| Niveau | Conditions | Approbation |
|--------|-----------|-------------|
| low | diff < 30 lignes, pas de `locked_fields` touchés, pas nouveau fichier, pas `schema_version` change | Auto-approve CI si schema_valid + forbidden empty |
| medium | diff 30-200 lignes, OU nouveau fichier, OU changement non-textuel frontmatter | Humain éditorial requis |
| high | diff > 200 lignes, OU `locked_fields` touchés, OU `schema_version` change, OU `engine_codes` change | Humain + CODEOWNER vehicle-schema |

### 5.3 State machine

pending → validating → (approved | rejected)
approved → merged (post PR merge)
pending/validating → expired (après 14j)
pending/validating → superseded (proposal B remplace A pour même input_fingerprint)

### 5.4 API

```typescript
interface RagProposalService {
  propose(input: RagProposalCreateInput): Promise<RagProposal>;
  validate(proposalUuid: string): Promise<ValidationReport>;
  approve(proposalUuid: string, approvedBy: string): Promise<void>;
  merge(proposalUuid: string, commitSha: string): Promise<void>;
  reject(proposalUuid: string, reason: string, rejectedBy: string): Promise<void>;
}
```

## 6. Rotation mécanisme — TemplateRotator

Rotation déterministe par `type_id` :

```typescript
function pickVariant(slug: string, typeId: number, slotName: string, salt: string, variantsCount: number): number {
  const hash = crypto.createHash('sha256')
    .update(`${salt}:${slug}:${typeId}`)
    .digest('hex');
  return parseInt(hash.slice(0, 8), 16) % variantsCount;
}
```

Propriétés :
- Reproductible : même input → même output (testable)
- Per-slot salt : h1 / intro / meta / cat / faq peuvent tomber sur des index différents pour même type_id
- Resilient au refactor : ajout de variants change la distribution mais reste déterministe

Fallback : si template sélectionné a placeholder non-résoluble (ex: `engine_code` absent dans DB pour ce type_id), tenter variant suivant (rotation modulo). Si aucun variant ne résout → `seo_decision=REGENERATE` (pas de page bancale publiée).

## 7. Rollout — 8 stages incrémentaux

Chaque stage réversible via feature flag. Pas de migration destructive.

| Stage | Durée | Cumul | Flag principal | Rollback |
|-------|-------|-------|----------------|----------|
| 0 Parallel build | 1j | 1j | N/A | DROP TABLE |
| 1 Shadow mode | 2-3j | 4j | `RAG_PROPOSAL_MODE=off\|shadow\|propose-only` | flag=off |
| 2 Canary 10 | 3-4j | 8j | `RAG_PROPOSAL_SLUGS` (10 slugs low-profile) | vider liste |
| 3 CI auto-approve | 1j | 9j | `RAG_PROPOSAL_AUTO_APPROVE_LOW` | flag=false |
| 4 Enricher v2 | 3j | 12j | `R8_ENRICHER_V2_ENABLED` | flag=false |
| 5 Top 100 rollout | 7j observation | 19j | Étendre SLUGS à top 100 | retirer slugs |
| 6 Publish gate | 2j | 21j | `R8_PUBLISH_GATE_ENABLED` | flag=false |
| 7 Full rollout + cleanup | 7j | 28j | — (legacy supprimé) | git revert (30j) |
| 8 Observability | 7j | 35j | — | N/A (ajout only) |

**Clio 3 = Stage 5, pas canary** (high-traffic, 18 motorisations, risqué).

### 7.1 Plan d'urgence

Incident P1 pendant rollout :
1. `RAG_PROPOSAL_MODE=off` + `R8_ENRICHER_V2_ENABLED=false` (env vars, pas de deploy)
2. Enricher legacy reprend immédiatement
3. Pages DB R8 existantes intactes
4. Proposals pending expirent à J+14
5. Post-mortem → replay stage quand résolu

## 8. Invariants garantis

### 8.1 Par JSON Schema

1. `slug` unique et canonical (kebab-case ASCII)
2. `type_ids` integer array non vide (FK vers auto_type, CI check SQL)
3. `power_ps` integer, jamais string
4. `motorisations[]` non vide
5. `source_of_truth{}` obligatoire, enum par field
6. `locked_fields[]` paths JSONPath valides
7. Variations min 3 par slot
8. Meta description ≤ 170 chars
9. Placeholders dans templates explicites (enum fermé)
10. role_map sections → blocs R8 enum fermé
11. `content_hash` pattern sha256:[0-9a-f]{16,64}
12. `last_enriched_by` pattern service@version ou user@email
13. `risk_flags[]` taxonomy fermée
14. `verification_status` enum 4 valeurs
15. `additionalProperties: false` partout — aucun champ inconnu

### 8.2 Par process L1-L5

16. Idempotence generator : `input_fingerprint` unique → regen répété = no-op
17. Pas d'écrase curated : `locked_fields` → risk=high → human required
18. Pas de drift silencieux : tout change passe par PR signée G3
19. Rollback atomique : `git revert` + replay proposals
20. Concurrent-safe : `superseded` gère proposals concurrentes
21. Observabilité : `validation_report JSONB` = drift tracking direct
22. Expire cleanup : pending > 14j → auto-expired
23. Pas de régression R8 pendant rollout : page existante servie tout au long
24. Pas de big-bang : stages réversibles, canary avant prod
25. Enricher lit committed only : jamais proposal pending → cohérence git↔DB

## 9. Artefacts à produire (ordre de dépendance)

1. Migration SQL `20260424_create_rag_proposals.sql` (L0→L1 gate)
2. JSON Schema `vehicle-model.schema.json` dans vault (L0 contract)
3. JSON Schema `vehicle-variations.schema.json` dans vault
4. JSON Schema `vehicle-role-map.schema.json` dans vault
5. Workflow CI `.github/workflows/rag-vehicle-lint.yml` (L1 gate)
6. Workflow CI `.github/workflows/rag-proposals-validate.yml` (L1 polling)
7. Workflow CI `.github/workflows/rag-proposals-merge-approved.yml` (L2 PR auto)
8. Refactor `VehicleRagGeneratorService` : `generateForModel()` → `proposeChanges()` (L1)
9. Refactor `r8-vehicle-enricher.service.ts` v2 : lit HEAD git, hard gates pre-UPSERT (L3)
10. Classe `TemplateRotator` : hash déterministe rotation (L3)
11. Endpoint `POST /api/admin/r8/:typeId/publish` explicite (L4)
12. Table `__seo_r8_regeneration_queue` usage validation (L3)
13. Dashboard Grafana R8 RAG Control Plane (L5)
14. Alertes drift detection (L5)
15. ADR-022 canon dans vault
16. ADR-020 weekly-vault-lint extension : ajouter `/rag/knowledge/vehicles/` scope

## 10. Non-buts explicites

- **Pas R7 refactor** : R7 reste tel quel ; ce plan ne touche pas les 36 brand.md
- **Pas multilingue** : `lang: fr` fixé, schema autorise pas d'autres langues en 1.0.0
- **Pas frontend changes** : route R8 existante continue de servir via `r8Content` depuis RPC
- **Pas LLM-powered** : TemplateRotator = déterministe, zero LLM call, aligné skills-first architecture
- **Pas sitemap refactor** : juste filtre `publication_status='PUBLISHED'` ajouté
- **Pas backfill intégral 53 959 types** : stop à top 100 en Stage 5, extension ultérieure
- **Pas R8 schema change `__seo_r8_pages`** : colonnes existantes suffisent

## 11. Risques et mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Proposals pending s'accumulent (bug CI) | Med | Med | Cron cleanup à J+14, alerte si queue > 100 |
| Template rotation produit doublon (hash collision) | Low | Low | Min 3 variants × per-slot salt → collisions improbables |
| FK type_ids obsolète après remap TecDoc | Med | High | CI check avant merge + revalidation mensuelle |
| Generator propose même fichier 2x (race condition) | Low | Med | Dedup via `input_fingerprint` unique index partiel |
| Merge PR auto applique diff obsolète (base_commit_sha drift) | Med | High | Check `base_commit_sha` == HEAD avant merge, sinon re-propose |
| Locked_fields contournés par edit direct | Low | High | Weekly-vault-lint detecte, audit-trail vault |
| Drift non détecté (observability L5 pas shipée) | Med | Med | Stage 8 obligatoire avant full rollout déclaré |

## 12. Coverage Manifest

- scope_requested : enrichir R8 + éliminer duplicate content + contrôle
- scope_actually_scanned : pipeline R8 complet, RAG véhicule (8 files), R7 precedent, R6 pattern, governance-vault schemas, CLAUDE.md rules
- files_read_count : ~20 fichiers
- excluded_paths : backend tests, PROD VPS (49.12.233.2), frontend routes hors R8
- remaining_unknowns : 
  - Top 100 source (GSC vs GA4 vs heuristique SQL) → décidé au Stage 5
  - Qui porte le CODEOWNER vehicle-schema pour high-risk proposals → à définir
  - Forbidden terms R8 = identique R7 (29) OU élargi (e.g., termes moteur inapproprié) → à valider en Stage 1
- corrections_proposed : 16 artefacts listés section 9
- corrections_applied : Phase A uniquement (PR #139 mergée), le reste attend approbation ADR-022
- final_status : VALIDATED_FOR_SCOPE_ONLY (design complet, approbation ADR-022 requise avant execution)

## 13. Exit Conditions (pour passage Phase 4 Implementation)

Conditions pour lancer l'execution :

- [x] 5 sections brainstorming complétées et validées par @fafa
- [x] JSON Schema 3 fichiers conçus
- [x] Rollout 8 stages défini
- [x] Rollback plan explicite par stage
- [x] Design spec rédigé (ce document)
- [ ] ADR-022 draft écrit
- [ ] User review gate sur ce spec + ADR-022
- [ ] Implementation plan détaillé (10-16 artefacts ordonnés par dépendance)
- [ ] Approbation explicite de @fafa pour démarrer Stage 0

## 14. Références

- [[ADR-015-vault-single-source-of-truth]] — vault canon
- [[ADR-020-weekly-vault-lint]] — pattern lint prod
- [[ADR-021-database-rls-hardening-zero-trust]] — pattern RLS zero-trust à répliquer sur `__rag_proposals`
- [[rules-governance-process]] — G1-G4
- Monorepo PR #139 — Phase A blog list variation (livrée)
- Brainstorming session transcript : Claude Code 2026-04-23, modèle Opus 4.7 1M

---

_End of design spec. Next artifact: ADR-022 draft._
