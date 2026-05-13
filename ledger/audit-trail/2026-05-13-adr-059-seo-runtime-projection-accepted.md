---
date: 2026-05-13
type: audit-trail
related: [ADR-059, ADR-031, ADR-033, ADR-039, ADR-046, ADR-055, ADR-027, MOC-Decisions, MOC-AuditTrail, MOC-Roadmap-2026]
---

# 2026-05-13 — ADR-059 SEO Runtime Projection (proposed → accepted)

## What

ADR-059 "SEO Runtime Projection Architecture — wiki/exports/seo → DB versionnée → Pages R0-R8" passe de **status: proposed** à **status: accepted**. Décision @fafa, `decision_date: 2026-05-13`.

## Why

ADR-059 a été ouverte en `proposed` le 2026-05-13 (vault PR #259) après revue itérative (9 rounds reviewer, 26 sections finales). Elle comble formellement le gap laissé par ADR-031 §Couche 3 « wiki n'est pas un moteur SEO » en spécifiant :

- Format JSON contractuel `wiki/exports/seo/<entity_type>/<slug>.json` avec `schema_version` + `projection_contract_version` distincts
- Projection runtime DB via pattern kg_v3 (7 tables + 2 MVs CONCURRENT REFRESH)
- Runner diff-first avec 2 queues BullMQ découplées (write + refresh, debounce 5s)
- Replay deterministic via snapshots immutables content-addressed (tar.zst object-store, jamais `git checkout`)
- Versions complètes stockées (`builder_version`, `pipeline_version`, `extractor_version`, `runner_version`) pour reconstruction du moteur, pas seulement du contenu
- Rollout via GrowthBook self-hosted % rollout (1→10→50→100, advisory-only avec fallback deterministe)
- 3 règles fondamentales : exports = vues éphémères, no direct page SQL, projections never generate canon

Phase A (vault + monorepo + wiki) shippée le même jour avec 6 PRs MERGED + 1 follow-up non-bloquant :

- vault PR #258 (knowledge gap analysis ADR-031)
- vault PR #259 (ADR-059 proposed)
- monorepo PR #467 (canon registries pipelines + projections + schemas JSON + cross-ref validator + CI workflow)
- monorepo PR #471 (fix ajv draft-07 compat post-merge)
- monorepo PR #472 (fix registries ADR ref ADR-058 → ADR-059)
- wiki PR #24 (singular rename `gammes`/`vehicles`/`constructeurs` → singulier + `schema-version-clarification.md`)
- wiki PR #25 (fix clarification ADR ref ADR-058 → ADR-059)

Vérification consolidée Phase A : ADR-059 26 sections (≥22 requis), 6 pipelines + 1 projection PLANNED dans registries, cross-references bidirectionnelles cohérentes, rename singulier effectif côté wiki, frontmatter `status: proposed`, `supplements: [ADR-031]`.

L'acceptation lève le HOLD strict sur Phase B (PR-3..7).

## How

Acceptation via PR vault `vault/adr-059-accept` :

1. `ledger/decisions/adr/ADR-059-seo-runtime-projection.md` :
   - `status: proposed` → `status: accepted`
   - `decision_date: null` → `decision_date: 2026-05-13`
2. `ops/moc/MOC-Decisions.md` ligne ADR-059 : `Proposed` → `Accepted`
3. Ce fichier audit-trail créé (G1/G2 traceability, conforme `feedback_auto_vault_audit_trail_on_adr.md`)

Pas d'écriture code Phase B dans cette PR. Phase B (Pydantic v2, Trafilatura, GrowthBook self-hosted, BullMQ workers, migration DB 7 tables + 2 MVs, scripts capture/extract/build/replay, routes Remix R0-R8, depcruise/ast-grep guards, systemd timer, tar.zst snapshots, DRP runbook, CI workflow replay-regression) démarrera sur instruction explicite @fafa séparée, après vérification empirique :

```python
import re, pathlib, yaml
p = pathlib.Path("/opt/automecanik/governance-vault/ledger/decisions/adr/ADR-059-seo-runtime-projection.md")
m = re.match(r"^---\n(.*?)\n---", p.read_text(), re.S)
assert yaml.safe_load(m.group(1))["status"] == "accepted"
```

## What changes downstream

Avec `ADR-059.status == "accepted"` :

- **Phase B UNLOCKED** : PR-3 (capture web → wiki promotion) peut démarrer en premier
- **Canon LIVE** : 3 règles fondamentales (exports ephemeral, no direct page SQL, projections never generate canon) deviennent canon courant — toute violation future est régression
- **Registres canon** monorepo (`pipelines.registry.json` 6 pipelines, `projections.registry.json` `seo_runtime_v1` PLANNED) référencent un ADR LIVE
- **MOC-Roadmap-2026 §D — SEO indexation** : ADR-059 devient un plan dédié actif
- **9 ADR-059 sections de durcissement** entrent en canon : audit metadata vs replay authority, MV transitional, exports non-publicly-routable, GrowthBook advisory-only, roles_allowed future normalization, projections never generate canon, replay infra = G1/G2 critical governance, known scalability limitation MV, state machine extension future

Phase B reste sous démarrage explicite @fafa (pas auto-déclenché par cette acceptation).

## Refs

- [ADR-059](../decisions/adr/ADR-059-seo-runtime-projection.md) (accepted 2026-05-13)
- [adr-031-gap-analysis-seo-runtime](../knowledge/adr-031-gap-analysis-seo-runtime.md) (prep knowledge note)
- [ADR-031](../decisions/adr/ADR-031-four-layer-content-architecture.md) (supplemented, status: proposed)
- [ADR-058](../decisions/adr/ADR-058-repository-control-plane.md) (registre parallèle, distinct)
- PRs Phase A : vault #258 + #259 ; monorepo #467 + #471 + #472 ; wiki #24 + #25
