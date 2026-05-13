---
id: ADR-059
title: "SEO Runtime Projection Architecture — wiki/exports/seo → DB versionnée → Pages R0-R8"
status: proposed
date: 2026-05-13
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
# NOTE: ADR-031 status=proposed. ADR-059 "supplements" plutôt que "amends" :
# - amends impliquerait que ADR-031 est canon LIVE (status=accepted)
# - supplements = complète sans dépendre du statut canon de la cible
# Les 2 ADRs peuvent évoluer sur des tracks parallèles indépendamment.
supplements: ["ADR-031"]
related_rules: ["G1", "G2", "G3", "AP-10"]
related_incidents: []
related_adr: ["ADR-031", "ADR-033", "ADR-039", "ADR-046", "ADR-047", "ADR-055", "ADR-027"]
---

# ADR-059: SEO Runtime Projection Architecture

## § Contexte

ADR-031 (Four-Layer Content Architecture, status `proposed`) définit la séparation `automecanik-raw` → `automecanik-wiki` → `wiki/exports/{rag,seo,support}` → consumers. Sa §Couche 3 ligne 163 stipule :

> « `wiki/exports/seo/` fournit la matière validée — intentions, angles, données structurées, sourcing — ; **la logique SEO R0-R8 (génération, classification, V-Level, rotation, publish gates) reste dans `nestjs-remix-monorepo`. Le wiki n'est pas un moteur SEO.** »

Le knowledge note [adr-031-gap-analysis-seo-runtime](../../knowledge/adr-031-gap-analysis-seo-runtime.md) (2026-05-13) documente formellement le **gap** : ADR-031 n'a pas spécifié

1. Le **format JSON contractuel** de `wiki/exports/seo/<entity>.json`
2. La **mécanique de projection runtime** entre exports/seo et DB SEO
3. La **stratégie publish gate / rollout** au runtime (shadow mode, percent rollout, rollback granulaire)

ADR-059 comble ce gap.

## § Principe directeur

Hiérarchie SoT **strictement unidirectionnelle** :

```
Raw = preuve
Wiki = canon (humain-validé, sourced)
Exports = VUE filtrée éphémère (jamais SoT)
DB = projection runtime versionnée
Pages = consommateurs lecture seule
```

5 entity_types : `gamme` / `vehicle` / `constructeur` / `support` / `diagnostic` (singulier per ADR-031 §148).

## § Règle fondamentale "Exports are ephemeral derived views"

Les fichiers sous `wiki/exports/{seo,support,rag}/` sont des **vues dérivées éphémères**. **Jamais** authoritative, **jamais** éditées à la main, **jamais** enrichies indépendamment, **jamais** source-of-truth relationnelle. Si une équipe veut enrichir un export, elle doit éditer le wiki canon et regénérer. Pre-commit hook wiki repo refuse les commits touchant `exports/` sans label `regenerated`.

## § Règle fondamentale "No Direct Page SQL"

Les pages R0-R8 ne font **JAMAIS** `SELECT ... FROM __seo_entity_*` directement. Tout passe par RPC (`get_active_seo_projection`) ou adapter service. Sinon : couplage, bypass `active_version_id`, shadow impossible, rollout impossible, replay impossible. Guards depcruise + ast-grep en PR-7 (interdit imports directs des tables `__seo_entity_*` depuis `frontend/`).

## § Décision

### Format JSON contractuel `wiki/exports/seo/<entity_type>/<slug>.json`

```json
{
  "entity_id": "gamme:filtre-a-huile",
  "entity_type": "gamme",
  "schema_version": "1.0.0",
  "projection_contract_version": "1.0.0",
  "source_wiki_commit": "<sha>",
  "wiki_path": "wiki/gamme/filtre-a-huile.md",
  "content_hash": "sha256:...",
  "generated_at": "2026-05-XX",
  "facts": [{"key": "...", "value": "...", "source_id": "..."}],
  "sources": [{"id": "bosch_fad_2020", "type": "specialist"}],
  "blocks": [{"role": "R3_CONSEILS", "section": "S2_DIAG", "content_md": "..."}],
  "roles_allowed": ["R3_CONSEILS", "R4_REFERENCE", "R6_GUIDE_ACHAT"],
  "consumers_allowed": ["seo", "rag", "support"]
}
```

- `schema_version` = version du contrat JSON export
- `projection_contract_version` = version du contrat runner / RPC / pages (distinct)
- `roles_allowed` `minItems: 1` (RoleId enum R0..R8 sans R5 per ADR-027) — si vide, l'entité est routée vers `exports/support/`

### DB projection versionnée

Pattern **kg_v3 éprouvé** (réutilisé tel quel) sur 7 tables :

| Table | Rôle |
|---|---|
| `__seo_projection_runs` | Audit trail (1 row par run) avec versions complètes |
| `__seo_entity_facts` | Facts par entity (avec `active_version_id`) |
| `__seo_entity_fact_versions` | Versions historiques (status draft/active/deprecated, valid_from, valid_to, source_type, confidence_base, content_hash) |
| `__seo_entity_sources` | Sources par entity |
| `__seo_content_blocks` | Blocks rôle-aware (avec `active_version_id`) |
| `__seo_content_block_versions` | Versions historiques de blocks |
| `__seo_projection_conflicts` | Conflits non auto-appliqués (resolution: pending/resolved/ignored) |

Plus **2 materialized views CONCURRENT REFRESH** pour lecture pages :

- `mv_seo_entity_facts_current` = JOIN facts × fact_versions WHERE active_version_id AND status='active'
- `mv_seo_content_blocks_current` = idem pour content_blocks

### Versioning complet (replay determinism)

`__seo_projection_runs` stocke :

- `projection_contract_version` (du runner)
- `exports_snapshot_hash` (sha256 du tarball)
- `exports_snapshot_uri` (URI vers tar.zst immutable object-store, replay SoT)
- `wiki_commit_sha` (audit-only, **pas** replay-authoritative)
- `builder_version`, `pipeline_version`, `extractor_version`, `runner_version` (semver)
- `trigger_kind` (cron/manual/replay)
- `replayed_from_run_id` (pour traçabilité replay)

### Découplage write ↔ refresh (2 queues BullMQ)

`REFRESH MATERIALIZED VIEW CONCURRENTLY` ne s'exécute **JAMAIS** dans la transaction runner (lock contention, queue bloquée, latence projection inacceptable).

| Queue | Worker | Tâche | Transaction |
|---|---|---|---|
| `projection-write-queue` | `SeoProjectionWriteWorker` | INSERT versions + UPDATE active_version_id | Courte (< 100ms) |
| `projection-refresh-queue` | `SeoProjectionRefreshWorker` | `REFRESH ... CONCURRENTLY` | Hors-transaction, lock-free |

Coalescing : si N writes pendant 5s → 1 seul refresh job (debounce 5s côté worker, concurrency=1, single-flight).

### Snapshots immutables content-addressed (replay SoT)

Object-store local : `/opt/automecanik/object-store/exports-snapshots/<sha256>.tar.zst` + `<sha256>.manifest.json` (avec builder/pipeline/extractor/runner versions). `chattr +i` (immutable filesystem flag) post-write. Backup VPS DEV → cron `0 5 * * *` rsync vers Hetzner Storage Box offsite.

### Rollout via GrowthBook self-hosted

Feature flag `seo_projection_read_v1` (% rollout 1→10→50→100 sur drift threshold). GrowthBook **advisory-only** : circuit breaker (3 fails → open 60s) + cache Redis 5min + deterministic default `SEO_PROJECTION_READ_ENABLED=false`. Pages R0-R8 ne **bloquent jamais** sur lookup feature flag.

### Rollback

`UPDATE __seo_entity_facts SET active_version_id = <prev_version_id>` (jamais DELETE, audit trail préservé).

## § Known scalability limitation (MV global REFRESH)

MV `REFRESH MATERIALIZED VIEW CONCURRENTLY` global acceptable **< ~100k entities**. Cardinalité réelle SEO automotive (variants × compatibilités × blocks R3/R6/R8 × FAQs × enrichissements) peut exploser. **Architecture cible long-terme possible** :

1. Tables current-state maintenues transactionnellement
2. Incremental refresh
3. Projection partitions par entity_type
4. Event-driven denormalized read models

Migration déclenchée si `pg_stat_user_tables.seq_tup_read` sur MV dépasse seuil (à définir). **Ne jamais** considérer les MV comme architecture définitive.

## § State machine extension future

kg_v3 status fournit `draft / active / deprecated`. SEO runtime peut nécessiter à terme : `draft / validated / shadow / active / deprecated / quarantined / replayed / failed`. Extension par migration additive (ADR followup), pas dans Phase B initiale.

## § Contract versioning extensible

Phase B initiale : `schema_version` (JSON export) + `projection_contract_version` (runner+RPC+pages) distincts. **Extensions futures possibles** :

- `rpc_contract_version` (si RPC évolue indépendamment des pages)
- `consumer_contract_version` (si pages Remix évoluent indépendamment du runner)

Chaque couche doit pouvoir évoluer à son rythme.

## § Interdictions formelles

- Web → DB direct (capture passe par raw)
- Web → SEO direct
- Raw → DB direct (passe par wiki canon validé)
- Raw → pages direct
- Wiki canonique → prod direct (toujours via exports + projection)
- DB overwrite destructive (INSERT nouvelle version, jamais UPDATE row existante)
- LLM summary → wiki direct (proposals avec source_map obligatoires)
- Manual edit dans `exports/`
- Direct `SELECT __seo_entity_*` depuis frontend (RPC ou adapter uniquement)
- `REFRESH MATERIALIZED VIEW` dans transaction runner
- Replay via `git checkout` (snapshot tar.zst seul SoT)

## § Plan d'implémentation (Phase B, HOLD jusqu'à status=accepted)

Phase B HOLD strict tant que `ADR-059.status != "accepted"` (décision signée @fafa). Composants :

- **PR-3a/3b** : pipeline raw → wiki robuste (capture Playwright + claims + source_map + proposals)
- **PR-4** : 5 wrappers Pydantic GateResult (source/claim/contradiction/risk/confidence)
- **PR-5a/5b** : builder + cron systemd timer + sd_notify
- **PR-6** : 7 tables + 2 MVs + 2 queues BullMQ + replay_projection.py
- **PR-7** : RPC `get_active_seo_projection` + adapter pages + depcruise/ast-grep guards

## § Quality gates

5 wrappers Pydantic-typed (source/claim/contradiction/risk/confidence) **réutilisant** les gates existants de `automecanik-wiki/_scripts/quality-gates.py` (documentés `_meta/quality-gates.md` §2 + §5.bis ADR-033). Inventaire précis dressé en PR-4 Step 0 par `ast.parse`.

Option future (followup) : migrer vers OPA/Conftest avec Rego policies pour policy-as-code uniforme.

## § Registres canon

- `.spec/00-canon/repository-registry/pipelines.registry.json` (6 pipelines tracked) — créé par PR-2 monorepo (mergée 2026-05-13)
- `.spec/00-canon/repository-registry/projections.registry.json` (1 projection `seo_runtime_v1` PLANNED) — créé par PR-2 monorepo
- Cross-references bidirectionnelles `feeds_projection` ↔ `fed_by_pipeline` validées par CI

## § Audit metadata vs replay authority

`wiki_commit_sha` (et tout `source_wiki_commit`) est **informational-only audit metadata**. Temporal reconstruction authority belongs **exclusively to immutable exports snapshots** (object-store). Squash merge / force push / history rewrite / subtree split / mirror sync / migration repo peuvent casser l'alignement historique git. **Aucun rebuild via `git checkout` n'est autorisé** ; toute tentative "historical replay from commit" doit être bloquée par `replay_projection.py` (read tar.zst, pas git).

## § Materialized views = transitional acceleration structures

(Voir §Known scalability limitation). Garde-fou : **ne jamais** considérer les MV comme architecture définitive.

## § Exports non-publicly-routable

Tous les `exports/{seo,support,rag}/` sont des **artefacts internes non-publics**. Ils **MUST** :

- never be publicly routable (no nginx/caddy/Remix route serving `exports/*.json`)
- never be indexable by crawlers
- never be attached to CDN public origins (Cloudflare, Bunny, etc.)
- emit `X-Robots-Tag: noindex, nofollow, noarchive` si exposés accidentellement (defense-in-depth)

Enforcement : CI check anti-leak scan reverse proxy configs (`/etc/caddy/*`, `frontend/app/routes/api.exports*`). Catastrophe SEO si exports/seo/*.json indexés (duplicate content, canonical drift).

## § GrowthBook advisory-only, never runtime-critical

GrowthBook est **advisory-only** pour rollout orchestration. **Projection runtime must remain operational if GrowthBook is unavailable.** Safe fallback mode :

- If GrowthBook unavailable → fallback to **last locally cached flag state** (Redis snapshot < 5min old)
- If cache also expired → fallback to **deterministic default configuration** (`SEO_PROJECTION_READ_ENABLED=false`, défaut sûr = legacy lecture)

Circuit breaker GrowthBook (3 failures → open 60s) + Sentry alert. Pages R0-R8 ne **bloquent jamais** sur GrowthBook lookup.

## § roles_allowed future normalization

Phase B initiale : `roles_allowed: ["R3_CONSEILS", ...]` enum direct (simple, validable par schema). **Future evolution possible** (followup ADR) : normaliser via `role_profiles` ou `role_set_id` résolus via canon registry. Justification : duplication / drift / typos / incohérences inter-export probables à grande échelle. Garde-fou immédiat : test contractuel — tous les exports d'un même `entity_type` doivent avoir `roles_allowed` identique (sauf exception documentée).

## § Projections never generate canon (one-way SoT enforcement)

Runtime projections sont **write-only consumers** des canonical sources. **No runtime projection may** :

- mutate canonical wiki content
- regenerate canonical wiki content
- enrich canonical wiki content
- rewrite canonical wiki content
- sync back to wiki ("auto-fix projection", "LLM repair from DB", "projection-to-wiki feedback loop")

Hiérarchie SoT (raw → wiki → exports → projection → pages) est **strictement unidirectionnelle**. RPC `projection_write_back_to_wiki` n'existe pas et ne doit jamais exister. Pre-commit hook wiki repo refuse commits avec `Author: SeoProjectionWriter <...>` (uniquement humains signed G3).

## § Replay infrastructure = critical governance infrastructure (G1/G2)

`replay_projection.py` + object-store immutable snapshots sont classifiés **critical governance infrastructure (niveau G1/G2)**. Implications :

- **Tests obligatoires** : property-based Hypothesis sur replay determinism (round-trip snapshot → projection → query identique)
- **CI obligatoire** : workflow `.github/workflows/replay-projection-regression.yml` exécute `replay_projection.py --dry-run` sur 10 runs historiques aléatoires à chaque PR touchant `backend/src/modules/seo/projection/` ou `app/scripts/seo-projection/`
- **No-refactor-libre** : modification de `replay_projection.py` requiert review @fafa explicite + ADR amendment si signature ou comportement change
- **Version pinning stricte** : Docker image taggée immuable pour chaque release (`replay-projection:1.0.0`), rebuild historique disponible 5 ans
- **Backup offsite quotidien** vers Hetzner Storage Box + checksums vérifiés
- **DRP runbook** : `ops/runbooks/disaster-recovery-seo-projection.md` (créer en Phase B avant PR-6 merge)

## § Compatibilité ADR-031

**supplements** (pas amends, pas supersedes). ADR-031 est status `proposed` ; ADR-059 ne dépend pas de son acceptation. ADR-059 spécifie le PROJECTOR runtime omis par ADR-031 §Couche 3, sans modifier ADR-031.

## § Compatibilité ADR-046

(R-stack single-generator) : projection alimente le generator unifié — la projection est l'INPUT du generator, pas un duplicat.

## § Compatibilité ADR-055

(SEO shadow mode) : runner peut tourner en shadow avant promotion publique. % rollout via GrowthBook renforce la stratégie shadow mode existante.

## § Compatibilité ADR-027

(R5 sunset) : `diagnostic` projeté uniquement si block R3 S2_DIAG présent (pas URL R5 dédiée). Sinon → `exports/support/diagnostic/`.

## § Stack moderne (best-in-class, 100% OSS / self-hosted)

| Couche | Choix |
|---|---|
| Capture | Playwright + Trafilatura + Readability + Schema.org JSON-LD direct lift |
| Storage raw | content-addressed (filename = sha256(body)) |
| Validation | Pydantic v2 (Python) + Zod TS (ADR-039) + JSON Schema bidirectionnel |
| Pipeline | Python typés Pydantic + Click CLI + BullMQ côté NestJS |
| Gates | Pydantic GateResult typed (option future OPA/Conftest Rego) |
| Tests | Pytest + Hypothesis property-based |
| Cron | systemd timer + sd_notify + journald |
| Observability | OpenTelemetry + Sentry (LIVE PR #324) + Grafana |
| DB versioning | kg_v3 + MVs CONCURRENT REFRESH |
| Idempotency | BullMQ retries + sha256 jobId + INSERT ON CONFLICT |
| Rollout | GrowthBook self-hosted % rollout |
| Frontmatter | ADR-039 Zod TS mirror v1.0.0 LIVE |

**Coût total** : 0 € en boucle production.

## § Numérotation ADR

ADR-058 initialement réservé pour ce chantier a été pris par PR vault #257 (Repository Control Plane) le même jour. Re-numérotation à ADR-059 (prochain libre).

## § Références

- [ADR-031 Four-Layer Content Architecture](ADR-031-four-layer-content-architecture.md) (proposed)
- [ADR-039 Wiki Frontmatter Zod Canon](ADR-039-wiki-frontmatter-zod-canon.md) (LIVE)
- [ADR-033 Wiki Gamme Diagnostic Relations](ADR-033-wiki-gamme-diagnostic-relations.md) (accepted)
- [ADR-058 Repository Control Plane](ADR-058-repository-control-plane.md) (registry parallèle)
- [adr-031-gap-analysis-seo-runtime](../../knowledge/adr-031-gap-analysis-seo-runtime.md) (knowledge note prep)
- PRs SEO v9 MERGED : #398, #399, #400 (fondation registries + R2IndexabilityGate)
- PR vault #258 (knowledge note PR-0)
- PR monorepo #467 (canon registries PR-2)
- PR wiki #24 (singular rename PR-2b)
