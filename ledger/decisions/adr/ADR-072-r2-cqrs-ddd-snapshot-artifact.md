---
id: ADR-072
title: "R2 — Paradigme architectural industry-standard : CQRS + DDD bounded contexts + Published Snapshot Artifact + Outbox pattern + Schema Registry + OpenTelemetry canon + GitOps publication"
status: accepted
date: 2026-05-16
decision_date: 2026-05-16
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: [ADR-066, ADR-070]
related_rules: [G1, T1, AI1]
related_incidents: []
reviewed_by: "@fafa"
---

# ADR-072 : R2 — Paradigme architectural industry-standard (CQRS + DDD + Snapshot Artifact + Outbox + Schema Registry + OTel + GitOps)

## Contexte

[[ADR-070-r8-r1-first-r2-second-active-disambiguation]] (commit `410b17a`, accepted 2026-05-16) a verrouillé la **doctrine** R2 v2 (formule canon Rounds 5+6+7 : `R2Content = render(R8 + R1 + KG + WIKI)`). Ce qui reste à codifier est le **paradigme architectural** qui supporte cette doctrine à l'échelle (10K-100K pages R2).

### Pourquoi ADR-072 séparée d'ADR-070

ADR-070 = "QUOI" (canon doctrinal : cadre/matière, ordre exécution L0-L5, usage critères techniques).
ADR-072 = "COMMENT" (paradigme architectural : où vivent les écritures, comment le runtime lit, comment les contextes communiquent, comment on observe, comment on rollback).

Mélanger les deux dans une seule ADR = anti-pattern industrie (un ADR ≠ 7 piliers architecturaux). Sépare aussi les responsabilités de review : ADR-070 review doctrinale @fafa, ADR-072 review architecturale @fafa pré-implémentation PR 2D.

### Trigger

Décisions @fafa 2026-05-16 (Round 8 brainstorming + 8 review-fix corrections). Identifié 7 piliers architecturaux industry-standard requis pour soutenir la doctrine ADR-070 à scale :

1. CQRS strict (Compose write ≠ Runtime read)
2. 5 DDD bounded contexts (Vehicle / PartFamily / Compatibility / Evidence / Render)
3. Published Snapshot Artifact (`__seo_r2_page_snapshot` immutable versioned content-addressed)
4. Outbox pattern (`__seo_outbox_event` transactional)
5. Schema Registry versioned R2 v2 contracts (mirror Repository Contract Series)
6. OpenTelemetry canon (trace `r2.compose` + 8 metrics thresholded)
7. GitOps-like content publication (rollback atomique via pointer)

Référence industrie : Shopify Storefront CDN, Sanity.io headless CMS, Vercel ISR, Netflix Hollow, Confluent transactional outbox, Microservices.io.

## Décision

### 1. CQRS strict (Command Query Responsibility Segregation)

```
COMMAND side (WRITE) — Compose Pipeline
  BullMQ async workers ONLY
  Idempotent (compose_input_hash dedup)
  Durable (Outbox pattern Postgres)
  Observed (OTel spans full lifecycle)
       ↓ writes
__seo_r2_page_snapshot (immutable, versioned, content-addressed)
       ↑ reads only
QUERY side (READ) — Remix runtime
  frontend/app/routes/pieces.$gamme.$marque.$modele.$type[.]html.tsx
  Read latest snapshot via __seo_r2_pages.current_snapshot_id pointer
  p95 < 50ms (single PK lookup + Redis L1 cache)
  JAMAIS de compose live, JAMAIS d'orchestration multi-source
  JAMAIS de KG/WIKI/L4 query au request time
```

**Invariants** (enforced via `r2-runtime-read.rego` nouveau) :
- Runtime ne peut lire QUE `__seo_r2_page_snapshot` + `__seo_r2_pages` (index)
- Aucun appel à `R2CompositionService`, `R2DataLoaderService`, `R2KnowledgeGraphService` au request time

### 2. DDD bounded contexts (Domain-Driven Design strategic patterns)

5 contextes délimités, owners distincts, schémas isolés, communication par **integration events** (Outbox + BullMQ transport) :

| Bounded Context | Owner (NestJS module) | Aggregate root | SoT table | Integration events émis |
|-----------------|----------------------|----------------|-----------|--------------------------|
| **Vehicle Domain** | `modules/seo/r8/` | `R8VehicleSnapshot` | `__seo_r8_snapshot_store` | `R8SnapshotUpdated`, `R8DisambiguationChanged` |
| **PartFamily Domain** | `modules/seo/r1/` (existing) | `R1GammeContext` | `__seo_gamme_conseil` + `__seo_r1_keyword_plan` | `R1ContextUpdated`, `R1SectionBackfilled` |
| **Compatibility Domain** (NEW) | `modules/seo/r2/services/kg/` (sous-module r2, pas module séparé) | `VehiclePartKnowledgeFact` | `__seo_vehicle_part_knowledge` | `KGFactUpserted`, `KGFactExpired`, `KGFactConflicted` |
| **Evidence Domain** | `modules/seo/r2/services/research/` | `ValidatedWikiEvidence` | `__seo_r2_wiki_evidence` | `WikiEvidenceValidated`, `WikiEvidenceRejected` |
| **SEO Render Domain** (R2) | `modules/seo/r2/services/render/` | `R2PageSnapshot` | `__seo_r2_page_snapshot` | `R2PagePublished`, `R2PageReviewRequired`, `R2PageRejected` |

**Note implementation** : Compatibility Domain reste sous-module `r2/services/kg/` initialement (pas module NestJS séparé). Promotion vers module dédié si justifié empiriquement post-PR 2H. Évite wiring DI lourd pré-maturité.

**Anti-pattern interdit** : un module n'écrit JAMAIS dans la SoT d'un autre contexte. Communication via integration events + outbox uniquement. Reconciliation explicite (eventual consistency assumée).

### 3. Published Snapshot Artifact (read model immutable)

Table canon Round 8 — `__seo_r2_page_snapshot` :

```sql
CREATE TABLE __seo_r2_page_snapshot (
  id                       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  pg_id                    BIGINT NOT NULL,
  type_id                  BIGINT NOT NULL,
  version_sha              TEXT NOT NULL UNIQUE,
  compose_input_hash       TEXT NOT NULL,
  rendered_sections        JSONB NOT NULL,
  rendered_html_compact    TEXT,
  governance_decision      TEXT NOT NULL CHECK (governance_decision IN ('index', 'review_required', 'reject')),
  internal_difference_score NUMERIC(5,2),
  l4_external_used         BOOLEAN NOT NULL DEFAULT false,
  r8_snapshot_version_sha  TEXT NOT NULL,
  r1_context_hash          TEXT NOT NULL,
  kg_fact_signatures       TEXT[] NOT NULL DEFAULT '{}',
  wiki_evidence_signatures TEXT[] NOT NULL DEFAULT '{}',
  trace_id                 TEXT,
  compose_run_id           UUID NOT NULL,
  composed_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  composed_by_worker_id    TEXT NOT NULL,
  render_engine_version    TEXT NOT NULL
);
-- No UPDATE/DELETE grant : versions immuables (CQRS canon)

ALTER TABLE __seo_r2_pages ADD COLUMN current_snapshot_id BIGINT REFERENCES __seo_r2_page_snapshot(id);
```

**Propriétés canon** :
- **Content-addressed** : `version_sha = sha256(canonical(input + engine_version))` via fast-json-stable-stringify (canon `feedback_deterministic_input_hash_canonical_json` monorepo)
- **Immutable** : aucun UPDATE/DELETE GRANT. Rollback = repointer `__seo_r2_pages.current_snapshot_id`
- **Traçable** : lineage des 4 inputs (R8/R1/KG/WIKI signatures) stocké
- **Observabilité** : `trace_id` + `compose_run_id` corrèlent les spans OTel

### 4. Outbox pattern + Integration events (Postgres transactional)

Pour garantir cohérence write-side ↔ event publication sans transactions distribuées (référence industrie : Confluent, Microservices.io, AWS DynamoDB Streams).

```sql
CREATE TABLE __seo_outbox_event (
  id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  aggregate_type  TEXT NOT NULL,
  aggregate_id    TEXT NOT NULL,
  event_type      TEXT NOT NULL,
  payload         JSONB NOT NULL,
  trace_id        TEXT,
  occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  published_at    TIMESTAMPTZ,
  attempts        INTEGER NOT NULL DEFAULT 0,
  last_error      TEXT
);
```

`OutboxRelayService` BullMQ repeatable :
- Concurrency 1, poll 5s, batch 100
- `SELECT ... WHERE published_at IS NULL ORDER BY occurred_at LIMIT 100 FOR UPDATE SKIP LOCKED`
- Per event : publish vers BullMQ queue ciblée → `UPDATE published_at = NOW()`
- Retry exponential backoff, dead-letter post 5 attempts

### 5. Schema Registry + Versioned Contracts (mirror Repository Contract Series)

Pattern existant canon (mémoire monorepo `repository-contract-series-canon-20260514`) :

- Tous Zod schemas R2 v2 dans `packages/registry/src/{shared,entries,canonical}/seo-r2-v2/`
- `R2CompositionInputSchema`, `R2PageSnapshotSchema`, `KGFactSchema`, `OutboxEventSchema` dans `shared/`
- Breaking changes → Architecture Contract gate observed → ratchet → enforce (3-phase canon)
- CI gate : tout merge qui change un schema R2 v2 doit fournir migration plan

### 6. OpenTelemetry canon (observability industrie)

Traces span obligatoires :

```
trace: r2.compose
  ├─ span: r2.load_r8_snapshot
  ├─ span: r2.load_r1_gamme_context
  ├─ span: r2.load_kg_facts
  ├─ span: r2.compute_internal_diff
  ├─ span: r2.gate_decision           (skip L4 ou not, attribute l4_skipped=bool)
  ├─ (optional) span: r2.load_wiki
  ├─ span: r2.project_facts_to_sections
  ├─ span: r2.render
  ├─ span: r2.governance_evaluate
  └─ span: r2.publish_snapshot
```

Metrics OTel canon Round 8 :

| Metric | Type | Threshold alerte |
|--------|------|-------------------|
| `r2.compose.duration_ms` | histogram | p95 > 3s |
| `r2.compose.idempotent_skip_rate` | gauge | < 30% = recompose excessif |
| `r2.compose.l4_external_called_rate` | gauge | > 30% = audit interne |
| `r2.compose.embedding_called_rate` | gauge | > 10% = structural-first failed |
| `r2.snapshot.publish_success_rate` | gauge | < 99% = alert |
| `r2.runtime.read_latency_ms` | histogram | p95 > 50ms = alert |
| `r2.runtime.snapshot_miss_rate` | gauge | > 0% = critical bug (CQRS broken) |
| `r2.outbox.lag_seconds` | gauge | > 60s = relay degraded |

**Verify-existing-first (canon `feedback_verify_existing_first`)** : grep `@opentelemetry` dans monorepo AVANT PR 2D :
- Si présent : étendre tracer provider existant
- Si absent : ADR-072 décide build NestJS OpenTelemetry SDK + OTLP exporter OU defer Phase 2 (logs structurés JSON intermédiaires) selon coût implémentation

### 7. GitOps-like content publication

Snapshot `version_sha` = commit-like identifier :
- **Rollback** = `UPDATE __seo_r2_pages SET current_snapshot_id = <previous>` (atomique, instantané)
- **Audit-trail** = full lineage via `__seo_r2_page_snapshot` history (jamais TRUNCATE, jamais DELETE)
- **Cherry-pick** = re-publier une version antérieure validée (admin tool dans `r2-admin-review.controller.ts`)

### 8. render_engine_version bump rule (canon)

`render_engine_version` ∈ `__seo_r2_page_snapshot` (SemVer) :

| Bump | Trigger | Impact |
|------|---------|--------|
| **Major** (X.0.0) | Breaking change projection (suppression section, schéma sections changé) | Invalide TOUS snapshots, force recompose batch |
| **Minor** (X.Y.0) | Nouvelle section optionnelle, enrichissement non-breaking | Recompose lazy (on-demand, snapshot stale acceptable transitoire) |
| **Patch** (X.Y.Z) | Bug fix render, performance, no output diff | No-op (snapshots existants restent valides) |

CI gate : tout PR qui change `R2ContentRenderer` doit déclarer le bump explicitement (label PR ou commit message).

### 9. r2-runtime-read.rego (NEW)

Nouvelle policy Rego pour enforcer CQRS read invariants :

1. `runtime_query AND reads_table NOT IN ('__seo_r2_page_snapshot', '__seo_r2_pages')` → deny `ADR-072 CQRS runtime lit snapshot uniquement`
2. `runtime_query AND performs_live_compose == true` → deny `ADR-072 CQRS no live compose`
3. `cross_context_write AND actor_module != owner_module` → deny `ADR-072 DDD bounded context isolation (events outbox uniquement)`
4. `full_scale_launch_enabled == true AND any({golden_validated, signature_validated, score_calibrated, r1_audited, r8_stability_verified}) != true` → deny `ADR-072 5 prerequisites Round 6 mandatory`

### 10. 5 prerequisites full-scale launch (canon Round 6, enforced Rego)

```
full_scale_launch_enabled = true
  REQUIRES (ALL):
    golden_examples_validated         = true
    business_signature_validated      = true
    internal_difference_score_calibrated = true
    r1_completeness_audited           = true
    r8_snapshot_stability_verified    = true
```

Sans ces 5 préconditions → interdiction de basculer pilote V1 vers V2 full-scale (Rego deny `r2-runtime-read.rego` invariant 4).

## Conséquences

### Positives

- **Read side trivialement performant** : single PK lookup + cache Redis → p95 < 50ms garanti
- **Write side découplé** : compose batch async ne pénalise jamais le runtime
- **Rollback atomique** : repointage `current_snapshot_id`, pas de cascade complexe
- **Bounded contexts isolés** : changement R8 ne casse pas R1 ni KG (eventual consistency via events)
- **Observability industrie** : OTel canon = compatible avec tout stack monitoring (Grafana / Jaeger / Datadog / Honeycomb)
- **Schema versioning enforced** : drift R2 v2 contracts blocked au PR time via Architecture Contract gate
- **GitOps publication** : auditable, reproductible, rollback-able

### Négatives

- **Eventual consistency** : un changement R8 ne se propage pas instantanément à R2 (peut prendre quelques minutes via outbox + recompose). Acceptable car SEO content batch async par nature.
- **Storage overhead** : `__seo_r2_page_snapshot` immutable history grandit. Mitigation : partition Postgres mensuel + archivage cold storage > 6 mois (déféré V2).
- **Complexity Budget** : 5 bounded contexts + outbox + OTel + schema registry = non-trivial. Mitigation : Compatibility Domain reste sous-module r2 initialement (pas module NestJS séparé), promotion empirique post-PR 2H.

### Risques résiduels

| Risque | Mitigation |
|--------|------------|
| Outbox relay degrade (lag > 60s) | Métrique OTel `r2.outbox.lag_seconds` + alerte Slack `#seo-ops` |
| CQRS broken (runtime fait compose live) | Rego `r2-runtime-read.rego` invariant 2 deny + métrique `r2.runtime.snapshot_miss_rate` > 0 = bug critique |
| Drift schema R2 v2 vs runtime | Architecture Contract gate observed (ratchet PR-3b pattern) |
| Compose stuck (compose_run_id sans publish) | Métrique `r2.snapshot.publish_success_rate` < 99% + dead-letter queue post 5 attempts |
| Major bump invalide snapshots prod | Migration batch recompose obligatoire AVANT déploiement render code change |

### Compatibilité

- **ADR-066 (foundation)** : amended (paradigme architectural codifié au-delà de la doctrine eligibility)
- **ADR-070 (R8+R1 first + matter + criteria=evidence)** : amended (codifie le COMMENT supporte le QUOI)
- **ADR-067 + ADR-068** : préservés (aucune réintroduction d'auto-désindexation/suppression)
- **ADR-058 (Repository Control Plane)** : impacts ownership.yaml — nouvelle entrée `seo-r2-v2-snapshot-artifact` (à ajouter PR 2D)

## Évidence + métriques (post-merge)

- 8 metrics OTel canon Round 8 documentés section 6
- Tests OPA `r2-runtime-read_test.rego` : 4 deny invariants + 4 allow happy path = 8 tests minimum
- Snapshot E2E test golden : 10 type_ids stratified samples, render byte-identical entre pages R2 même gamme (R1 hérités), distinct entre type_ids (KG facts différents)

## Cross-refs

- [[ADR-066-r2-content-composition-v2]] (foundation, accepted 2026-05-15)
- [[ADR-067-r2-no-auto-suppression]] (amends ADR-066, accepted 2026-05-15)
- [[ADR-068-r2-doctrine-strict-no-auto-deindex]] (amends ADR-066+067, accepted 2026-05-16)
- [[ADR-070-r8-r1-first-r2-second-active-disambiguation]] (amends ADR-066/067/068, accepted 2026-05-16)
- [[ADR-058-repository-control-plane]] (Layer 2 ownership.yaml entry à ajouter PR 2D)
- [[ADR-062-repository-contract-system-meta-model]] (Schema Registry pattern parent)
- `feedback_deterministic_input_hash_canonical_json` (monorepo memory)
- `feedback_verify_existing_first` (monorepo memory, OTel verify-existing avant infra new)
- `feedback_no_bricolage_escalate_to_industry_standard` (monorepo memory, escalade paradigme)
- `repository-contract-series-canon-20260514` (monorepo memory, contract gate pattern)

## Self-review

Self-review verdict: APPROVE

Checklist 8 items :

1. ✅ **ADR numbering** : ADR-072 disponible (ADR-071 réservé Knowledge Graph fact-first decay, à drafter dans PR 2H)
2. ✅ **amends/supersedes** : amends ADR-066 + ADR-070 (cascade canon préservée)
3. ✅ **Rego deny invariants** : 4 nouveaux deny `r2-runtime-read.rego` énumérés (CQRS read scope + no live compose + bounded context isolation + 5 prerequisites full-scale)
4. ✅ **Tests Rego à mettre à jour** : `r2-runtime-read_test.rego` NEW à créer (8 tests minimum : 4 deny + 4 allow)
5. ✅ **WASM regen** : `build-opa-bundles.sh` à étendre pour `r2-runtime-read` policy (ajouter au POLICIES registry)
6. ✅ **Audit-trail** : entry à créer dans `ledger/audit-trail/2026-05-16-adr-072-r2-cqrs-ddd-snapshot-artifact-accepted.md` post-commit
7. ✅ **MOC link** : entry à créer dans `ops/moc/MOC-Decisions.md` + `ops/moc/MOC-AuditTrail.md`
8. ✅ **Cross-refs** : wikilinks validés vers ADR-066/067/068/070/058/062 + memories monorepo (backtick refs cross-repo)

PR body marker obligatoire : `Self-review verdict: APPROVE`
