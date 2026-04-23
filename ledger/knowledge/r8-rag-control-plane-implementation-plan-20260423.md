---
category: implementation-plan
doc_family: knowledge
source_type: plan
title: R8 RAG Control Plane — Implementation Plan
slug: r8-rag-control-plane-implementation-plan
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-23"
updated_by: "@fafa"
related_adr: ["ADR-022"]
related_knowledge: ["r8-rag-control-plane-design-20260423"]
status: draft
---

# R8 RAG Control Plane — Implementation Plan

> Plan tactique d'execution pour [[ADR-022-r8-rag-control-plane]].
> Design source : [[r8-rag-control-plane-design-20260423]].
> Plan ordonnancé par **dépendances strictes** (DAG). Chaque artefact a ses critères
> d'acceptation vérifiables, sa branche Git, son effort estimé.

## 1. DAG des 16 artefacts

```
┌─ A01 migration __rag_proposals ──────────────────────┐
│   │                                                  │
│   ├─→ A04 vehicle-model.schema.json ──┐              │
│   ├─→ A05 vehicle-variations.schema   │              │
│   ├─→ A06 vehicle-role-map.schema     │              │
│   │                                   │              │
│   │   A02 ops: migration tests        │              │
│   │   A03 ops: RLS audit              │              │
│   │                                   ▼              │
│   │                           A07 CI rag-vehicle-lint│
│   │                                   │              │
│   ▼                                   ▼              │
│  A08 CI rag-proposals-validate ──── A09 CI merge-    │
│   │                                    approved      │
│   ▼                                                  │
│  A10 VehicleRagGenerator refactor (propose mode)     │
│   │                                                  │
│   ▼                                                  │
│  A11 TemplateRotator class                           │
│   │                                                  │
│   ▼                                                  │
│  A12 r8-vehicle-enricher v2 (lit HEAD + gates)       │
│   │                                                  │
│   ▼                                                  │
│  A13 POST /api/admin/r8/:typeId/publish              │
│   │                                                  │
│   ▼                                                  │
│  A14 Grafana dashboard R8 Control Plane              │
│   ├─→ A15 Alertes drift                              │
│   │                                                  │
│   ▼                                                  │
│  A16 Extension ADR-020 weekly-vault-lint scope       │
└──────────────────────────────────────────────────────┘
```

Dépendances critiques :
- A01 bloque tout (table fondatrice)
- A04-A06 bloquent A07 (schemas avant CI lint)
- A07 bloque A08-A09 (lint avant workflows validate/merge)
- A10 dépend de A01+A04 (propose mode écrit __rag_proposals selon schema)
- A12 dépend de A10+A11 (enricher lit fichiers produits par generator refactoré + utilise rotator)
- A13 dépend de A12 (publish gate lit seo_decision produit par enricher v2)
- A14-A15 dépendent de A12 (metrics sur données enricher)
- A16 indépendant (peut être shipé en parallèle après A04-A06)

## 2. Catalogue des 16 artefacts

### A01 — Migration SQL `__rag_proposals`

- **Stage** : 0
- **Repo** : monorepo (`nestjs-remix-monorepo`)
- **Fichier** : `backend/supabase/migrations/20260424_create_rag_proposals.sql`
- **Branche** : `feat/r8-rag-proposals-table`
- **Effort** : 0.5 jour
- **Dépendances** : aucune
- **Contenu** :
  - `CREATE TABLE __rag_proposals` avec toutes colonnes du design spec § 5.1
  - Indexes : `idx_rag_proposals_status_expires`, `idx_rag_proposals_target_slug`, `idx_rag_proposals_fingerprint_pending` (unique partial)
  - RLS ENABLE + policy service_role (pattern ADR-021 zero-trust)
  - CHECK constraint : `status='approved'` impossible si `schema_valid IS NOT TRUE`
- **Acceptance** :
  - [ ] Migration appliquée en DEV sans erreur
  - [ ] `SELECT * FROM __rag_proposals LIMIT 1` retourne 0 rows (table vide)
  - [ ] Insert test row + update status fonctionne
  - [ ] RLS : anon query retourne 0 rows, service_role retourne rows
  - [ ] `INSERT ... status='approved'` avec `schema_valid=false` lève CHECK violation
- **Rollback** : `DROP TABLE __rag_proposals`

### A02 — Script tests migration

- **Stage** : 0
- **Repo** : monorepo
- **Fichier** : `scripts/db/test-rag-proposals-migration.ts`
- **Branche** : même que A01
- **Effort** : 0.5 jour
- **Dépendances** : A01
- **Contenu** : suite tests insert/update/expire/supersede + RLS
- **Acceptance** : CI job passe, 10+ tests verts

### A03 — RLS audit `__rag_proposals`

- **Stage** : 0
- **Repo** : monorepo
- **Fichier** : `scripts/db/audit-rls-rag-proposals.sh`
- **Branche** : même que A01
- **Effort** : 0.2 jour
- **Dépendances** : A01
- **Contenu** : script qui queries `pg_policies` + advisor check, aligné pattern PR #42
- **Acceptance** : 0 flag advisor `rls_disabled_in_public`

### A04 — `vehicle-model.schema.json`

- **Stage** : 0
- **Repo** : governance-vault
- **Fichier** : `_scripts/schemas/vehicle-model.schema.json`
- **Branche** : `schemas/vehicle-rag-v1`
- **Effort** : 0.5 jour
- **Dépendances** : aucune
- **Contenu** : JSON Schema draft 2020-12 complet du design spec § 4.1
- **Acceptance** :
  - [ ] Fichier `renault-clio-iii.md` actuel VALIDATE OU produire rapport d'écart précis
  - [ ] Schema validé par `ajv-cli` (syntactique)
  - [ ] `additionalProperties: false` à tous niveaux

### A05 — `vehicle-variations.schema.json`

- **Stage** : 0
- **Repo** : governance-vault
- **Fichier** : `_scripts/schemas/vehicle-variations.schema.json`
- **Branche** : même que A04
- **Effort** : 0.3 jour
- **Dépendances** : aucune
- **Acceptance** :
  - [ ] Exemple `renault-clio-3.variations.yaml` (produit par A10 plus tard) VALIDATE
  - [ ] `min_variants: 3` enforced

### A06 — `vehicle-role-map.schema.json`

- **Stage** : 0
- **Repo** : governance-vault
- **Fichier** : `_scripts/schemas/vehicle-role-map.schema.json`
- **Branche** : même que A04
- **Effort** : 0.2 jour
- **Dépendances** : aucune
- **Acceptance** : `renault-clio-iii.role_map.json` produit VALIDATE

### A07 — Workflow CI `rag-vehicle-lint.yml`

- **Stage** : 0
- **Repo** : governance-vault (où vivent les schemas) + monorepo (où les RAG files sont)
- **Fichiers** :
  - `.github/workflows/rag-vehicle-lint.yml` (monorepo, trigger sur PR modifiant `rag/knowledge/vehicles/**`)
- **Branche** : `ci/rag-vehicle-lint`
- **Effort** : 0.5 jour
- **Dépendances** : A04, A05, A06
- **Contenu** : pour chaque `.md`, `.variations.yaml`, `.role_map.json` modifié dans la PR :
  - Validate vs JSON Schema (ajv-cli)
  - Check forbidden terms (29 R7)
  - Check placeholders résolvables
  - Check FK `type_ids` → `auto_type` via Supabase query
- **Acceptance** : PR test avec fichier invalide = workflow fail, PR avec fichier valide = pass

### A08 — Workflow CI `rag-proposals-validate.yml`

- **Stage** : 0 (skeleton) puis actif en Stage 1
- **Repo** : monorepo
- **Fichier** : `.github/workflows/rag-proposals-validate.yml`
- **Branche** : `ci/rag-proposals-validate`
- **Effort** : 1 jour
- **Dépendances** : A01, A04-A06
- **Contenu** :
  - Cron toutes les 10 min (ou webhook Supabase)
  - Fetch `status='pending'` → run validate() → update `schema_valid`, `forbidden_terms_found[]`, etc.
  - Auto-approve si `risk_level='low' AND schema_valid=true AND forbidden empty AND RAG_PROPOSAL_AUTO_APPROVE_LOW=true`
  - Skeleton Stage 0 : schedule disabled, `workflow_dispatch` only
- **Acceptance** :
  - [ ] Skeleton parses sans erreur
  - [ ] Dry-run `workflow_dispatch` sur 3 proposals test en DEV retourne reports

### A09 — Workflow CI `rag-proposals-merge-approved.yml`

- **Stage** : 2
- **Repo** : monorepo
- **Fichier** : `.github/workflows/rag-proposals-merge-approved.yml`
- **Branche** : `ci/rag-proposals-merge`
- **Effort** : 1 jour
- **Dépendances** : A08
- **Contenu** :
  - Cron 15 min
  - Fetch `status='approved' AND merged_at IS NULL`
  - Pour chaque proposal : `git checkout -b rag-propose-{uuid}`, write `proposed_content` à `target_path`, commit signé G3, open PR
  - Label PR selon `risk_level`
  - Auto-merge si `risk_level='low'` et checks passent
- **Acceptance** :
  - [ ] Proposal test approved → PR ouverte dans 20 min
  - [ ] Low-risk merge automatique
  - [ ] Medium/high attend human review

### A10 — Refactor `VehicleRagGeneratorService` propose mode

- **Stage** : 1
- **Repo** : monorepo
- **Fichier** : `backend/src/modules/admin/services/vehicle-rag-generator.service.ts`
- **Branche** : `refactor/rag-generator-propose-mode`
- **Effort** : 2-3 jours
- **Dépendances** : A01, A04
- **Contenu** :
  - Nouvelle méthode `proposeChanges(modeleId: number): Promise<RagProposal>`
  - Feature flag `RAG_PROPOSAL_MODE=off|shadow|propose-only`
  - En `shadow` : écrit fichier ET insère proposal (parallel, pour validation flow)
  - En `propose-only` : insère proposal uniquement
  - En `off` : comportement legacy (direct write)
  - Génère les 3 artefacts (.md, .variations.yaml, .role_map.json) en 3 proposals liées via `depends_on`
  - `input_fingerprint` = `sha256(modele_id + latest TecDoc sync SHA + motorisations count)`
- **Acceptance** :
  - [ ] Shadow mode : fichiers identiques à legacy + proposals correctes en DB
  - [ ] Propose-only : aucun write disque, proposals correctes
  - [ ] Dedup : regen 2x même input = 1 seule proposal
  - [ ] Tests unitaires `VehicleRagGeneratorService.spec.ts` passent

### A11 — Classe `TemplateRotator`

- **Stage** : 4
- **Repo** : monorepo
- **Fichier** : `backend/src/modules/admin/services/template-rotator.service.ts`
- **Branche** : `feat/template-rotator`
- **Effort** : 1 jour
- **Dépendances** : A05
- **Contenu** :
  - `pickVariant(slug, typeId, slotName, salt, variants[]): Variant`
  - Hash SHA-256(`${salt}:${slug}:${typeId}`) % variants.length
  - Résolution placeholders (injection brand, model, type_name, power_ps, fuel, year_from, year_to, engine_code, families_count, body, power_tier)
  - Fallback : si placeholder non-résoluble, tenter variant suivant (rotation modulo)
  - Si aucun variant résout → throw `TemplateUnresolvableError` (enricher capture → `seo_decision=REGENERATE`)
- **Acceptance** :
  - [ ] Test déterministe : `pickVariant('clio-3', 34746, 'h1', 'h1', 3)` retourne toujours même index
  - [ ] 3 type_ids Clio 3 (34746, 34747, 34748) tombent sur des index distincts pour slot h1 (probabilité > 80%)
  - [ ] Fallback testé : variant avec placeholder non-résoluble → variant suivant

### A12 — Refactor `r8-vehicle-enricher` v2

- **Stage** : 4
- **Repo** : monorepo
- **Fichier** : `backend/src/modules/admin/services/r8-vehicle-enricher.service.ts`
- **Branche** : `refactor/r8-enricher-v2`
- **Effort** : 3 jours
- **Dépendances** : A10, A11
- **Contenu** :
  - Lit RAG via `git show HEAD:rag/knowledge/vehicles/{slug}.md` (pas fs direct)
  - Intègre `TemplateRotator` pour h1, intro, meta, catalog_h2, faq_h2
  - Compose blocs avec variations (S_IDENTITY, S_SEO_INTRO, S_CATALOG_ACCESS, S_FAQ_DEDICATED, S_ENTRETIEN_CONTEXT, etc.)
  - Hard gate AVANT UPSERT :
    - `diversityScore >= 70` sinon INSERT `__seo_r8_regeneration_queue`
    - `semantic_hash` ≠ neighbor → sinon queue
  - `seo_decision` : INDEX si tous gates ok, REVIEW si diversity 50-70, REGENERATE si < 50 ou dup, REJECT si data insuffisante
  - Feature flag `R8_ENRICHER_V2_ENABLED=true|false`
  - Legacy v1 conservé jusqu'à Stage 7
- **Acceptance** :
  - [ ] 10 modèles canary : re-enrich via v2, `diversity_score` médian ≥ 70
  - [ ] Clio 3 1.5 dCi 90 ch vs 106 ch : `h1_hash`, `intro_hash`, `meta_hash` distincts
  - [ ] Regen queue reçoit entries si gate fail (pas silent skip)
  - [ ] v1 conservé opérationnel (flag OFF)

### A13 — Endpoint `POST /api/admin/r8/:typeId/publish`

- **Stage** : 6
- **Repo** : monorepo
- **Fichier** : `backend/src/modules/admin/controllers/admin-r8-vehicle.controller.ts`
- **Branche** : `feat/r8-publish-gate`
- **Effort** : 1-2 jours
- **Dépendances** : A12
- **Contenu** :
  - Endpoint POST avec IsAdminGuard
  - Check `seo_decision='INDEX'` AND `diversity_score >= 70` AND `quality_score >= 60`
  - Update `publication_status='PUBLISHED'`, `published_at=NOW()`
  - Retourne 400 si gates fail
  - Sitemap R8 filter `WHERE publication_status='PUBLISHED'`
- **Acceptance** :
  - [ ] Publish sur page REGENERATE → 400 rejected
  - [ ] Publish sur page INDEX → 200 + sitemap updated
  - [ ] Sitemap R8 compte = count pages PUBLISHED

### A14 — Dashboard Grafana `R8 RAG Control Plane`

- **Stage** : 8
- **Repo** : grafana-dashboards (ou monorepo `docker/grafana/`)
- **Fichier** : `docker/grafana/r8-rag-control-plane.json`
- **Branche** : `feat/grafana-r8-dashboard`
- **Effort** : 1-2 jours
- **Dépendances** : A12, A13
- **Contenu** :
  - Panel 1 : Proposals by status (pending/validating/approved/rejected/merged/expired) × 24h
  - Panel 2 : Proposals by risk_level × 24h
  - Panel 3 : Time-in-state distribution (median, p95, p99)
  - Panel 4 : Pages R8 quality_score distribution (histogram)
  - Panel 5 : Pages R8 diversity_score distribution
  - Panel 6 : Pages R8 seo_decision breakdown
  - Panel 7 : Drift : quality_score δ week-over-week
  - Panel 8 : Proposals dedup rate (% rejected as supersede)
- **Acceptance** : dashboard loads, tous panels remplis avec data DEV

### A15 — Alertes drift detection

- **Stage** : 8
- **Repo** : grafana-dashboards
- **Fichier** : `docker/grafana/r8-alerts.yml`
- **Branche** : même que A14
- **Effort** : 0.5 jour
- **Dépendances** : A14
- **Contenu** :
  - Alert : `diversity_score` médian baisse > 5% sur 7j
  - Alert : `rejected` proposals > 20% sur 24h
  - Alert : pages indexées avec `quality_score < 50` > 5
  - Alert : queue pending > 100 (pipeline bloqué)
- **Acceptance** : test synthétique de chaque alert → Slack/email reçu

### A16 — Extension ADR-020 weekly-vault-lint scope

- **Stage** : Peut être shipé en parallèle dès Stage 0
- **Repo** : governance-vault
- **Fichier** : `.github/workflows/weekly-vault-lint.yml` + script lint
- **Branche** : `ci/weekly-vault-lint-extend-vehicles`
- **Effort** : 0.5 jour
- **Dépendances** : A04-A06 (schemas déployés)
- **Contenu** :
  - Ajoute pattern `rag/knowledge/vehicles/**/*.md` et `**/*.variations.yaml` et `**/*.role_map.json` dans scope lint
  - Validate vs 3 schemas nouveaux
  - Issue auto si new findings (pattern Suivi #3 ADR-020)
- **Acceptance** : weekly run en DEV détecte fichiers `renault-clio-iii.md` invalides vs nouveau schema (qui sera normal en attendant A10)

## 3. Timeline consolidée

| Semaine | Stage | Artefacts livrés | Flag actif |
|---------|-------|------------------|------------|
| S1 J1-J2 | 0 | A01, A02, A03, A04, A05, A06 | — |
| S1 J3 | 0 | A07 (CI lint) | — |
| S1 J4-J5 | 0 | A08 (skeleton), A16 | — |
| S2 J1-J3 | 1 | A10 (propose mode) | `RAG_PROPOSAL_MODE=shadow` en DEV |
| S2 J4 | 1 | A08 activé schedule + A09 | `MODE=shadow` PROD, `AUTO_APPROVE=false` |
| S2 J5 — S3 J1 | 2 | Canary 10 modèles | `SLUGS=[10 low-profile]` en propose-only |
| S3 J2 | 3 | Activation auto-approve low-risk | `AUTO_APPROVE_LOW=true` |
| S3 J3-J5 | 4 | A11 (rotator), A12 (enricher v2) | `R8_ENRICHER_V2_ENABLED=true` canary |
| S4 | 5 | Extension top 100 (incl. Clio 3) | SLUGS top 100 |
| S5 J1-J2 | 6 | A13 (publish gate) | `R8_PUBLISH_GATE_ENABLED=true` |
| S5 J3-J5 | 7 | Full rollout + cleanup legacy | — |
| S5 (parallèle) | 8 | A14, A15 | — |

**Chemin critique** : A01 → A04-A06 → A07 → A10 → A11 → A12 → A13 ≈ **12 jours ouvrés** min.

## 4. Stage 0 Pre-Launch Checklist

Avant de lancer A01 :

- [ ] ADR-022 vault PR #51 **accepté + mergé**
- [ ] Statut ADR-022 passe de `proposed` → `accepted`
- [ ] Confirmation @fafa que créneau 5 semaines OK vs roadmap
- [ ] Snapshot Supabase DB DEV (backup avant migration table)
- [ ] Vérif 0 incident en cours touchant `backend/src/modules/admin/services/`
- [ ] RPC Gate vérifié : `__rag_proposals` n'entre pas en conflit avec allowlist existante
- [ ] Feature flags env vars provisionnés (DEV + PROD placeholders OFF)
- [ ] Branche `feat/r8-rag-proposals-table` créée depuis main à jour
- [ ] TODO list session réinitialisée pour Stage 0

## 5. Critères GO/NO-GO entre stages

### Stage 0 → 1 GO si :
- Migration A01 appliquée sans downtime
- JSON Schemas valident le fichier `renault-clio-iii.md` actuel (ou produisent rapport d'écart précis)
- CI workflow A07 bloquait PR test invalide et laissait passer PR valide
- 0 advisor Supabase flag nouveau

### Stage 1 → 2 GO si :
- Shadow mode 3 modèles DEV : fichiers disque identiques à legacy (diff nul) + proposals insérées correctement
- Dedup vérifié : 2 runs même input = 1 proposal
- Tests unitaires VehicleRagGenerator > 90% couverture sur propose path

### Stage 2 → 3 GO si :
- 10 modèles canary : 100% proposals passées `validating` → `approved|rejected` en < 20 min
- 0 incident éditorial (pas de rejet a posteriori sur approved)
- Diff PR auto lisible (YAML canonical, pas de bruit formatage)

### Stage 3 → 4 GO si :
- CI auto-approve low-risk : taux faux-positif < 1%
- Dashboard CI proposal flow accessible

### Stage 4 → 5 GO si :
- Enricher v2 sur 10 canary : `diversity_score` médian ≥ 70
- Clio 3 1.5dCi 90 vs 106 : `h1_hash` distinct, `intro_hash` distinct, `meta_hash` distinct
- v1 legacy toujours opérationnel (flag OFF)

### Stage 5 → 6 GO si :
- Top 100 : > 80% INDEX, < 10% REGENERATE, < 5% REJECT
- Quality_score médian stable ±5% vs baseline
- 7j sans incident P1/P2

### Stage 6 → 7 GO si :
- Publish gate : 0 faux positif (pages REGENERATE non-indexées)
- Sitemap R8 cohérent avec publication_status PUBLISHED

### Stage 7 → 8 GO si :
- 100% modèles migrés vers propose pattern
- grep `writeFileSync` dans VehicleRagGenerator = 0
- Legacy flag supprimé, code dead propre

### Stage 8 (closure) si :
- Dashboard Grafana accessible
- Alertes armées et testées
- Weekly canary job shipé
- ADR-022 passe `accepted` → `canon`

## 6. Plan d'urgence pendant execution

### Scénario 1 : Migration A01 casse DB

Impact : aucun (table nouvelle, pas d'ALTER)
Action : `DROP TABLE __rag_proposals` + analyser erreur + re-run

### Scénario 2 : Shadow mode produit différence vs legacy

Impact : bug silent potentiel
Action : `RAG_PROPOSAL_MODE=off`, analyser diff file par file, fixer refactor A10

### Scénario 3 : CI auto-approve approuve à tort

Impact : proposal bogus mergée → fichier RAG invalide
Action : `git revert` PR + `RAG_PROPOSAL_AUTO_APPROVE_LOW=false`, ajuster risk classification

### Scénario 4 : Enricher v2 fait tomber pages production

Impact : pages R8 INDEX en prod disparaissent
Action : `R8_ENRICHER_V2_ENABLED=false` (retour v1 instant)

### Scénario 5 : Clio 3 canary Stage 5 produit duplicates

Impact : duplicate content Google potentiel
Action : retirer Clio 3 des SLUGS + rollback pages Clio 3 via v1 + analyser TemplateRotator

## 7. Coverage Manifest

- scope_requested : plan d'exécution détaillé 16 artefacts
- scope_actually_scanned : design spec + ADR-022 + vault structure + memory Claude Code
- files_read_count : design spec + ADR-022 + renault-clio-iii.md + renault.md (R7) + r8-keyword-plan.constants.ts + r7-brand-rag-generator.md
- remaining_unknowns :
  - Qui porte CODEOWNER `vehicle-schema` pour high-risk proposals (à définir avec @fafa en Stage 0 kick-off)
  - Source ranking top 100 Stage 5 (GSC clicks vs GA4 sessions vs heuristique SQL `cross_gamme_car_new` count) — décidé au lancement Stage 5
  - Forbidden terms R8 : identique 29 R7 OU élargi ? (validé en Stage 1 après 3 proposals réelles)
- corrections_proposed : 16 artefacts A01-A16 listés avec acceptance
- corrections_applied : 0 (plan seul, execution en attente GO @fafa)
- final_status : VALIDATED_FOR_SCOPE_ONLY — plan complet, attend accept ADR-022 + Stage 0 pre-launch checklist

## 8. Exit Conditions (lancement Stage 0)

- [x] Design spec rédigé
- [x] ADR-022 rédigé + commité + PR ouverte
- [x] Implementation plan rédigé (ce document)
- [ ] ADR-022 accepté + mergé
- [ ] Pre-launch checklist § 4 complète
- [ ] Lancement A01 (branche créée, TODO list réinitialisée)
