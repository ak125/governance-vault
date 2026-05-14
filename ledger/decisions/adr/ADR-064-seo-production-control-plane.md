---
id: ADR-064
title: "SEO Production Control Plane (4-layer Collectors/Evaluators/Actions/Governance)"
status: proposed
date: 2026-05-14
decision_date: TBD
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G3", "Q1", "Q2"]
related_incidents: ["INC-2026-005"]
related_adr: ["ADR-028", "ADR-045", "ADR-050", "ADR-058", "ADR-061", "ADR-062", "ADR-063"]
implementation_status: foundation-only
---

# ADR-064 — SEO Production Control Plane (4-layer architecture)

## TL;DR grepable

> **Collectors observent, Evaluators jugent, Actions remédient, Governance contracte. Aucun composant ne mélange ces responsabilités. Monolithe `seo-monitor.service.ts` interdit par construction.**

## Contexte

L'incident INC-2026-005 (30 400 pages GSC en 5xx, validation 2026-05-06 →
2026-05-12 FAILED) a été détecté par un **email Google Search Console** envoyé
le 2026-05-13 à 13h11 UTC — soit ~7 jours après que le bug ait commencé à
contaminer le cache Cloudflare.

PR-1 #510 (closure) a livré :
- `notify503ToErrorLog` étendu à `pieces/*` (instrumentation runtime)
- AST rules + bash lint anti-régression (build-time)
- Playwright e2e cache-control invariant
- `prod-smoke-tests.yml` v2 sample 150 URLs seedés

**Mais aucune surveillance runtime réelle** ne nous a alerté avant l'email
Google. Critique technique user 2026-05-14 post-PR-1 :

> "Le CI protège le code. Le crawler protège la production. Ce sont deux
> couches différentes."
> "Vous avez besoin d'un SEO Production Control Plane. PR-2 devient un
> chantier architecture/platform engineering majeur."
> "Ne mélangez PAS observabilité + décision + remédiation automatique dans
> les mêmes services. Sinon PR-2 deviendra rapidement un monolithe
> 'seo-monitor.service.ts'."

## Décision

Construction d'un **SEO Production Control Plane** structuré en **4 layers
strictement séparés**, livré en sous-PRs atomiques.

### Architecture 4-layer

```
Layer 1 — Collectors (read-only, pure data ingestion)
  ├─ synthetic-crawler.service.ts        (BullMQ q15min, UA AutoMecanikSyntheticBot)
  ├─ cf-analytics-collector.service.ts   (Cloudflare GraphQL httpRequestsAdaptiveGroups)
  ├─ runtime-logs-collector.service.ts   (__error_logs query par tier)
  └─ gsc-coverage-collector.service.ts   (Search Console API, signal secondaire)
  → écrivent dans __seo_snapshot_* (raw observations, jamais d'évaluation)

Layer 2 — Evaluators (lecture L1, pas d'I/O externe, pure compute)
  ├─ slo-engine.service.ts               (4-source pondéré 99.7/99/98% par tier)
  ├─ drift-engine.service.ts             (title/h1/canonical/word_count diff N vs N-1)
  └─ anomaly-scoring.service.ts          (statistical outlier per stratum/tier)
  → écrivent dans __seo_evaluation_* (verdicts, breaches, drift scores)

Layer 3 — Actions (déclenchées par L2, fire-and-forget, idempotent)
  ├─ cache-warmup.action.ts              (post-purge, rate-limit, criticality priority)
  ├─ cf-purge.action.ts                  (chirurgical, max-urls, audit-trail)
  ├─ github-issue.action.ts              (auto-issue si breach persiste 30min)
  ├─ webhook.action.ts                   (Slack/Discord/PagerDuty configurable)
  └─ sentry-transaction.action.ts        (tag tier/route/source)
  → idempotents, retry-safe, jamais de read direct sur L1

Layer 4 — Governance (config/policy/contracts, jamais runtime)
  ├─ @repo/registry seo_criticality overlay      (tier0/1/2/excluded YAML)  ← PR-2D #515
  ├─ ADR-064 (this doc)                          (vault, status proposed)
  ├─ policies/seo-slo-thresholds.yaml            (par tier, versionné, futur)
  └─ .ast-grep rules + bash lint                  (invariants build-time, déjà partiellement livrés PR-1)
  → lecture par L2/L3 au boot, jamais de mutation runtime
```

### Invariants architecturaux non-négociables

1. **Aucun import cross-layer en remontée** : L3 ne lit JAMAIS L1 direct, passe
   par L2 (via `__seo_evaluation_*`).
2. **L4 Governance jamais mutée runtime** : YAML overlay éditée manuellement,
   PR séparée, validée par Zod schema + CI gate.
3. **Synthetic crawler UA identifiable obligatoire** :
   `AutoMecanikSyntheticBot/1.0 (+https://www.automecanik.com/bots/synthetic)`
   — JAMAIS spoof Googlebot/Bingbot. Cf. canon
   `feedback_synthetic_bot_ua_never_spoof_googlebot`.
4. **GSC = signal secondaire/business** dans SLO multi-source, JAMAIS
   monitoring primaire (latence J-2 à J-7). Cf. canon
   `feedback_gsc_is_secondary_signal_only`.
5. **`admin/*` toujours en `excluded`**, jamais en `tier2`. Cf. canon
   `feedback_seo_routes_need_criticality_tiers`.
6. **Tests unitaires par layer + tests d'intégration par boundary** — pas de
   test cross-layer monolithique.

### Découpage en sous-PRs atomiques

| Sous-PR | Branche | Scope | Status |
|---|---|---|---|
| **PR-2D** | `feat/seo-cp-criticality-tiers` | L4 foundation : YAML overlay + Zod schema + `classifyRoute()` + 22 tests | **OPEN** [monorepo #515](https://github.com/ak125/nestjs-remix-monorepo/pull/515) |
| **PR-2D-bis** | `feat/adr-064-seo-production-control-plane` | L4 governance : cet ADR (proposed) | **OPEN** vault — cette PR |
| PR-2A | `feat/seo-cp-collectors` | L1 : 4 collectors + tables `__seo_snapshot_*` | Pending PR-2D merge + 48h |
| PR-2B | `feat/seo-cp-evaluators` | L2 : SLO engine + drift + anomaly + tables `__seo_evaluation_*` | Pending PR-2A |
| PR-2C | `feat/seo-cp-actions` | L3 : 5 actions + alerting | Pending PR-2B |

## Conséquences

### Positives

- **Détection 15 min** vs J-7 actuel : synthetic crawler q15min sur 500 URLs
  stratifiées par tier rattrape l'incident **avant** l'utilisateur final.
- **Multi-source SLO** : un faux positif d'une source (ex. GSC retard) est
  pondéré et n'alerte pas seul. Cf. canon `feedback_slo_must_be_multi_source`.
- **Discipline review** : 4 sous-PRs atomiques, chacune reviewable ≤ 1 jour,
  vs méga-PR `seo-monitor.service.ts` qui serait impossible à reviewer.
- **Idempotent à la non-implémentation** : PR-2D (cette foundation) est
  utile **sans** L1/L2/L3 — elle documente la cible et fournit les types.

### Négatives / coûts

- **Surface code** : ~5-8 services backend NestJS + 4-6 tables Supabase +
  workflows CI supplémentaires. Sprint complet plateforme engineering.
- **Coût Supabase** : tables `__seo_snapshot_*` partitioned by day, TTL 90j.
  Storage ~5-10 GB estimé (à valider sur warmup PR-2A).
- **Coût Cloudflare GraphQL API** : usage rate-limited mais inclus dans plan
  Cloudflare Business actuel (à confirmer).

### Risques

- **Stampede synthetic crawler mal calibré** : 500 URLs × 4 fois/heure =
  2k req/h. Mitigation : `sampling_weight` tier-pondéré + `cf-cache-status:
  HIT` skip pré-flight + UA identifiable filtrable par WAF.
- **Drift entre L4 schema et L1/L2 consumption** : mitigation = tests
  d'intégration par boundary (Zod parse au boot, refus si schema mismatch).
- **Auto-issue spam GitHub** : breach_threshold_minutes par tier + dedup
  par fingerprint (route + source + 1h window).

## Alternatives considérées

### Alt 1 — Étendre `seo-monitoring/` existant

Rejeté. Le module `backend/src/modules/seo-monitoring/` mélange déjà 3
responsabilités (collect + evaluate + alert). Y ajouter L1/L2/L3 sans
séparation aggravera la dette. PR-2 doit séparer, pas accumuler.

### Alt 2 — Outil externe (Datadog Synthetics, Pingdom, Cloudflare Workers)

Rejeté pour V1 :
- Datadog : coût $$$$, lock-in vendor, données SEO custom (criticality tier,
  drift HTML) pas natif.
- Cloudflare Workers Synthetic : encore alpha, observability faible.
- Solution interne avec BullMQ existant + Sentry existant = coût marginal
  zéro, contrôle total.

À reconsidérer V2 si volume > 100k URLs ou besoin de multi-region probing.

### Alt 3 — Monolithe `seo-control-plane.service.ts`

Rejeté explicitement par critique user 2026-05-14. Ne respecte aucun des
invariants architecturaux. Devient `seo-monitor.service.ts` v2 en 6 mois.

## Implementation plan

### Phase 1 — Foundation (livré PR-2D)

- [x] `.spec/00-canon/repository-registry/seo-criticality.yaml`
- [x] Zod schema `packages/registry/src/canonical/seo-criticality.ts`
- [x] `classifyRoute()` helper + glob matcher
- [x] 22 tests vitest
- [x] ADR-064 status `proposed` (this doc)

### Phase 2 — Collectors (PR-2A, à venir)

- [ ] `backend/src/modules/seo-control-plane/collectors/` module NestJS
- [ ] Tables Supabase `__seo_snapshot_synthetic`, `__seo_snapshot_cf`,
      `__seo_snapshot_runtime`, `__seo_snapshot_gsc`
- [ ] BullMQ queue dédiée `seo-crawler-monitor` (ne pas mutualiser
      `seo-monitor` pour éviter contention — cf. canon
      `feedback_schedulemodule_disabled_use_bullmq`)
- [ ] Cloudflare GraphQL Analytics auth + query builder
- [ ] Tests : 1 test par collector + 1 test d'intégration boundary

### Phase 3 — Evaluators (PR-2B)

- [ ] `seo-control-plane/evaluators/`
- [ ] Tables `__seo_evaluation_slo`, `__seo_evaluation_drift`,
      `__seo_evaluation_anomaly`
- [ ] Formule SLO multi-source : `breach = (sum_A + sum_B*2 + sum_C) / total
      > threshold[tier]` (poids 2 sur source B = synthetic = ground-truth)
- [ ] Drift detection : diff snapshot N vs N-1 sur title/h1/canonical
- [ ] Tests : edge cases multi-source (panne d'un signal, recovery)

### Phase 4 — Actions (PR-2C)

- [ ] `seo-control-plane/actions/`
- [ ] Cache warmup post-purge (full version vs PR-1 minimal embarqué)
- [ ] CF purge action wrapped sur `scripts/ops/cloudflare-purge-by-pattern.sh`
      (déjà livré PR-1)
- [ ] GitHub issue auto-créée si breach > 30 min (label `incident:5xx-detected`)
- [ ] Webhook configurable `SEO_SCP_WEBHOOK_URL` (Slack/Discord/PagerDuty)
- [ ] Sentry transaction `seo.scp.breach` avec tags

### Phase 5 — Promotion to `accepted`

Critères :
- PR-2D + PR-2A + PR-2B + PR-2C mergées
- DEV preprod stable 7 jours avec synthetic crawler tournant
- ≥ 1 breach détecté en DEV par le système (preuve de fonctionnement)
- Dashboard Grafana en place

ETA : 2026-06-30 (sprint 1 + sprint 2 + retours).

## Refs

- Incident déclencheur : `ledger/audit-trail/2026-05-14-INC-2026-005-closure.md` (vault PR [#270](https://github.com/ak125/governance-vault/pull/270) en attente admin-merge)
- Critique user 2026-05-14 (architectural guidance) : voir corps de la PR-2D
- Canon mémoire :
  - `feedback_seo_control_plane_layered_architecture` (4-layer)
  - `feedback_synthetic_bot_ua_never_spoof_googlebot` (UA identifiable)
  - `feedback_slo_must_be_multi_source` (4-source pondéré)
  - `feedback_ci_smoke_neq_runtime_monitoring` (smoke ≠ crawler)
  - `feedback_gsc_is_secondary_signal_only` (GSC J-2)
  - `feedback_cf_purge_requires_warmup` (purge stampede)
  - `feedback_seo_routes_need_criticality_tiers` (tier0/1/2/excluded)
  - `feedback_pr_scope_recovery_vs_platform` (split atomic PRs)
- PR-1 monorepo (recovery + tactical hardening) : [#510](https://github.com/ak125/nestjs-remix-monorepo/pull/510) (merged)
- PR-2D monorepo (cette foundation) : [#515](https://github.com/ak125/nestjs-remix-monorepo/pull/515) (open)
- ADR-058 Repository Control Plane (registry overlay où vit la criticality YAML)
- ADR-063 CWV Monitoring PROD (sister chantier perf, complémentaire)
