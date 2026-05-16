---
date: 2026-05-16
type: audit-trail
related: [ADR-072, ADR-070, ADR-068, ADR-067, ADR-066, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-16 — ADR-072 R2 — Paradigme architectural industry-standard (CQRS + DDD + Snapshot Artifact + Outbox + Schema Registry + OTel + GitOps)

## What

Création et acceptance de [[ADR-072-r2-cqrs-ddd-snapshot-artifact]] qui **amende** [[ADR-066-r2-content-composition-v2]] et [[ADR-070-r8-r1-first-r2-second-active-disambiguation]] avec le **paradigme architectural** qui supporte la doctrine R2 v2 :

- ADR-072 `status: accepted` (date 2026-05-16, decision_maker `@fafa`, reviewed_by `@fafa`)
- **7 piliers architecturaux industry-standard** :
  1. CQRS strict (Compose write ≠ Runtime read)
  2. 5 DDD bounded contexts (Vehicle / PartFamily / Compatibility / Evidence / Render)
  3. Published Snapshot Artifact (`__seo_r2_page_snapshot` immutable versioned content-addressed)
  4. Outbox pattern (`__seo_outbox_event` transactional)
  5. Schema Registry versioned R2 v2 contracts (mirror Repository Contract Series ADR-062)
  6. OpenTelemetry canon (trace `r2.compose` + 8 metrics thresholded)
  7. GitOps-like content publication (rollback atomique via `current_snapshot_id` pointer)
- **Nouvelle policy Rego** `r2-runtime-read.rego` : 4 deny invariants (CQRS read scope + no live compose + DDD bounded context isolation + 5 prerequisites full-scale)
- **render_engine_version SemVer bump rule** : Major invalide tous snapshots, Minor recompose lazy, Patch no-op
- **5 prerequisites full-scale launch** enforced Rego (canon ADR-070 Round 6)
- 113/113 OPA tests pass (96 existant ADR-066+067+068+070 + 17 nouveaux r2-runtime-read)
- WASM bundle `r2-runtime-read.wasm` créé (SHA `ecc626fd2aac5d4f5ec2e8d6967c8104daf5fe0cd35fa93dc3770474946dbd6a`)
- `_scripts/build-opa-bundles.sh` registry étendu (4 policies maintenant)

## Why

ADR-070 (`410b17a`) a verrouillé la **doctrine** R2 v2 (formule canon Rounds 5+6+7). ADR-072 codifie le **paradigme architectural** qui soutient cette doctrine à l'échelle (10K-100K pages R2).

**Pourquoi 2 ADRs séparées** :
- ADR-070 = QUOI (canon doctrinal : cadre/matière, ordre L0-L5, technical criteria = evidence)
- ADR-072 = COMMENT (paradigme architectural : où vivent les écritures, comment le runtime lit, comment les contextes communiquent, comment on observe, comment on rollback)

Mélanger les deux = anti-pattern industrie (un ADR ≠ 7 piliers architecturaux). Sépare aussi les responsabilités de review : ADR-070 review doctrinale, ADR-072 review architecturale pré-implémentation PR 2D.

**Pourquoi industry-standard escalade Round 8** : la cascade R5/R6/R7 a verrouillé la doctrine, mais l'implémentation sans paradigme strict risque 3 catastrophes identifiées (canon mémoire monorepo) :
1. SEO devient ERP (KG devient source de vérité métier catalogue au lieu de projection SEO)
2. R2 runtime explosion (orchestration live multi-source au request time)
3. Evidence addiction (Playwright/WIKI massif sans bornes)

Le paradigme CQRS + DDD + Snapshot Artifact + Outbox prévient ces 3 catastrophes par construction.

## Changements concrets

### Vault (cette PR)

- `ledger/decisions/adr/ADR-072-r2-cqrs-ddd-snapshot-artifact.md` (nouvelle, accepted)
- `policies/seo-content/r2-runtime-read.rego` (NEW, package `seo.runtime.r2.read`) :
  - `default allow := true` (fail-open runtime read non-destructif)
  - Sets canon : `allowed_runtime_tables`, `bounded_context_owners` (5 contexts), `full_scale_prerequisites` (5)
  - 4 deny invariants : CQRS read scope strict / no live compose / DDD bounded context isolation / 5 prerequisites full-scale
  - 1 audit rule : runtime read OK info pour OTel traces
  - Helper : `prerequisite_satisfied(name, obj)` pour check 5 prerequisites
- `policies/seo-content/r2-runtime-read_test.rego` (NEW) : 17 tests (5 deny cases + 5 allow cases + 7 edge cases)
- `_scripts/build-opa-bundles.sh` : ajout entrée `r2-runtime-read` au POLICIES registry (4 policies maintenant : h1-write, r2-content-write, r2-cluster-health, r2-runtime-read)
- `dist/policies/r2-runtime-read.wasm` (NEW, SHA `ecc626fd2aac5d4f5ec2e8d6967c8104daf5fe0cd35fa93dc3770474946dbd6a`)
- `dist/policies/r2-runtime-read.bundle.tar.gz` (NEW)
- `ledger/audit-trail/2026-05-16-adr-072-r2-cqrs-ddd-snapshot-artifact-accepted.md` (cette entrée)
- `ops/moc/MOC-AuditTrail.md` : ligne 2026-05-16 ADR-072
- `ops/moc/MOC-Decisions.md` : entry ADR-072 sous "R2 paradigme architectural cascade"

### Monorepo (PRs séquencées à suivre, séparées de cette PR vault)

À implémenter post-merge ADR-072 dans l'ordre canon (plan local `/home/deploy/.claude/plans/le-contenu-de-r2-scalable-tower.md`) :

| PR | Scope | Tables migration |
|----|-------|------------------|
| PR 2C' Mono R1 backfill prerequisite | Audit `__seo_gamme_conseil` sections vides + relance R1 keyword planner agent existant | (aucune) |
| PR 2D Mono R8 snapshot + foundation Round 8 | `R8ParentEnrichmentService` + `R8SnapshotReaderService` + **job seed initial idempotent INSERT minimal pour TOUS type_ids existants** | `__seo_r8_snapshot_store`, `__seo_r2_page_snapshot`, `__seo_outbox_event` |
| PR 2H Mono Knowledge Graph L3 + Evidence Decay | `R2KnowledgeGraphService` + `R2EvidenceDecayJobService` | `__seo_vehicle_part_knowledge` |
| PR 2E Mono R2DataLoader + pilot sync 10 URLs | `R2InternalDifferenceScoreService` (Round 6 gate) + `R2FactsToSectionsProjector` (Round 7) + `R2DuplicateBusinessSignatureService` (Round 4) + Frontend Remix CQRS + Sitemap V10 CQRS + `OutboxRelayService` BullMQ | (aucune) |

**Verify-existing-first OTel canon (ADR-072 §6)** : grep `@opentelemetry` dans monorepo AVANT PR 2D pour décider build/buy/defer (canon mémoire monorepo `feedback_verify_existing_first`).

## Verification locale

```
$ /tmp/opa test policies/seo-content/
PASS: 113/113
```

- 22 h1-write tests (régression PR-V intacte)
- 49 r2-content-write tests (ADR-066+067+068+070 cumulés)
- 15 r2-cluster-health tests (intacts)
- 17 r2-runtime-read tests (NEW, ADR-072 §1 + §2 + §10)
- 10 misc helpers tests

WASM reproducible (paths relatifs depuis vault root) :
- `h1-write.wasm` SHA inchangé
- `r2-content-write.wasm` SHA inchangé (`ecb7c5183e20d65a1a24c4feb35d3329cfa3041ba24ebb7150293e973f128063`)
- `r2-cluster-health.wasm` SHA inchangé
- `r2-runtime-read.wasm` NEW SHA `ecc626fd2aac5d4f5ec2e8d6967c8104daf5fe0cd35fa93dc3770474946dbd6a`

## Impacts cross-canon

- **ADR-066** : amended (paradigme architectural codifié au-delà de la doctrine eligibility)
- **ADR-070** : amended (codifie le COMMENT supporte le QUOI Rounds 5+6+7)
- **ADR-067 + ADR-068** : préservés (aucune réintroduction d'auto-désindexation/suppression)
- **ADR-058 (Repository Control Plane)** : impacts ownership.yaml — nouvelle entrée `seo-r2-v2-snapshot-artifact` (à ajouter PR 2D mono séparée, hors scope vault)
- **ADR-062 (Repository Contract System meta-model)** : ADR-072 Schema Registry §5 = instance directe du pattern parent (R2 v2 contracts mirror conformity criteria 9/9)
- **MOC-Decisions** : ADR-072 indexé sous "R2 paradigme architectural cascade"
- **MOC-AuditTrail** : ligne 2026-05-16 ADR-072

## Hors scope post-acceptance

- **ADR-069 evidence-based** : restera CONDITIONAL post-measurement gate Round 6 (PR 2A vault). Activé uniquement si pilote V1 confirme insuffisance L0-L3.
- **ADR-071 Knowledge Graph + fact-first + evidence decay** : à drafter dans PR 2H mono (sera ADR vault séparé stack sur ADR-072).
- **Migration historique** : aucun (zéro page R2 v2 publiée encore)
- **OTel SDK setup** : décision build/buy/defer en début de PR 2D (verify-existing-first canon)

## Self-review verdict: APPROVE

5 ADR successifs (066 → 067 → 068 → 070 → 072) en 2 jours = doctrine + paradigme architectural cumulés pré-production. Coût correction = zéro (aucune page R2 v2 publiée). Bénéfice = canon doctrinal (ADR-070 Rounds 5+6+7) + canon paradigme (ADR-072 industry-standard) étanche complet AVANT toute écriture de code R2 v2. 113/113 OPA pass (17 nouveaux r2-runtime-read). WASM reproducible. Cross-refs ADR-066+070 préservés via `amends`. Pattern Schema Registry mirror ADR-062 conformity criteria. Prêt pour merge.
