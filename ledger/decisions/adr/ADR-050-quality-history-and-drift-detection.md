---
id: ADR-050
title: "Quality history & drift detection — `__seo_quality_history` + RPC outliers + Sentry/OTel enrichers"
status: proposed
date: 2026-05-07
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "Q1", "AP-04", "AP-08"]
related_incidents: []
related_adr: ["ADR-046", "ADR-047"]
implementation_status: phase-0-baseline-2026-05-07
---

# ADR-050 — Quality history & drift detection : `__seo_quality_history` + RPC outliers + Sentry/OTel enrichers

## Contexte

L'audit R-stack v2 [[2026-05-07-r-stack-audit]] a identifié 8 trous
structurels. Les trous #1-#7 sont adressés par [[ADR-046-r-stack-single-generator-and-layers]]
(layers L0-L5, promotion gates, L3 read-only) et [[ADR-047-seo-role-contracts-as-code]]
(`@repo/seo-role-contracts` SoT comportemental).

Le **trou #8 — Drift invisible** reste découvert :

1. **Zéro Prometheus / OTel** sur les enrichers `*-enricher.service.ts` —
   aucune métrique d'outcome (success / fail / partial), aucun compteur
   de violations gates, aucun histogramme de durée.
2. **Sentry câblé partiellement** — la règle ast-grep
   `no-direct-rag-knowledge-write.yml` envoie un évent en cas de
   violation canon, mais **les enrichers eux-mêmes ne capturent pas
   leurs exceptions au catch level**. Une 502 Anthropic, un timeout
   Supabase, ou un parse error tombent silencieusement dans les logs.
3. **Aucun test E2E `RAG → enrich → DB → frontend read`** — chaque
   couche est testée isolément (unit), aucune validation de bout en
   bout. Une régression de schéma dans `__seo_*_slots` n'est détectée
   qu'en production.
4. **Zéro table d'historique qualité** — impossible de constater une
   régression de 30% du `gatekeeper_score` médian sur une cohorte de
   slots R1 entre deux exécutions du batch enrichissement. Les valeurs
   actuelles écrasent les précédentes.
5. **Backfill scripts sans safety net** — `npm run rag:backfill`,
   `r4-backfill.ts`, etc., ne capturent pas de snapshot pré-batch, ne
   produisent pas de diff post-batch, n'abortent pas si le delta
   excède un seuil. Une corruption massive (ex. 80K images
   supprimées 2026-04-11, cf. mémoire `incident-images-2026-04-11.md`)
   passe inaperçue jusqu'à plainte utilisateur.
6. **`/health` non content-aware** — le endpoint répond 200 même si
   les enrichers n'ont rien produit depuis 24h, ou si 50% des slots
   sont en `pending`.

Ce trou bloque mécaniquement la **Phase 4 PR-T** (re-enrich 163 slots)
prévue par le plan refondation R-stack : sans baseline et sans
détection automatique de dérive, on ne peut pas distinguer une
amélioration d'une régression au moment de réviser les contrats.

## Décision

Cadrer l'observabilité enrichers + drift detection en **3 livrables canon
fail-closed** + **2 compteurs OTel minimum**, en Phase 0 baseline du plan
refondation. Tout enricher futur DOIT respecter ce contrat.

### Livrable 1 — Table `__seo_quality_history` (snapshot per role + metric)

Schéma cible (PR-X1 monorepo, Phase 0 baseline) :

```sql
CREATE TABLE __seo_quality_history (
  id BIGSERIAL,
  pg_id INT NOT NULL,
  role_id TEXT NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value NUMERIC NOT NULL,
  sampled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  snapshot_kind TEXT NOT NULL CHECK (snapshot_kind IN (
    'pre_batch', 'post_batch', 'monthly_cron', 'on_demand'
  )),
  metadata JSONB,
  PRIMARY KEY (id, sampled_at)
) PARTITION BY RANGE (sampled_at);
```

- **Partitionnée mensuellement** — 1 partition par mois (ex.
  `__seo_quality_history_2026_05`), créée par fonction
  `ensure_next_month_partition()` exécutée par cron mensuel.
- **RLS activée** — `service_role` ALL, `authenticated` SELECT only.
- **Indexes** — `(pg_id, role_id, sampled_at DESC)`, `(metric_name,
  sampled_at DESC)`, GIN sur `metadata`.
- **Snapshot kinds** :
  - `pre_batch` / `post_batch` : capturé avant et après chaque batch
    enrichissement (par les scripts `r{N}-backfill.ts`).
  - `monthly_cron` : capture périodique de tous les slots (cron
    mensuel, baseline pour drift à long terme).
  - `on_demand` : déclenchement manuel admin (debug, audit).

### Livrable 2 — RPC `detect_quality_outliers(window, drop_pct, role, metric)`

```sql
CREATE OR REPLACE FUNCTION detect_quality_outliers(
  window_interval INTERVAL DEFAULT '30 days',
  drop_pct NUMERIC DEFAULT 0.30,
  filter_role TEXT DEFAULT NULL,
  filter_metric TEXT DEFAULT NULL
) RETURNS TABLE (
  pg_id INT,
  role_id TEXT,
  metric_name TEXT,
  baseline_median NUMERIC,
  current_value NUMERIC,
  drop_ratio NUMERIC,
  sampled_at TIMESTAMPTZ
);
```

Comportement : compare la valeur actuelle d'une métrique à la médiane
sur la fenêtre temporelle, retourne les slots dont la valeur a chuté
≥ `drop_pct`. Utilisable par `/health` content-aware, alerting, et
backfill abort gates.

### Livrable 3 — Sentry `captureException` obligatoire dans tous les enrichers

Tout `*-enricher.service.ts` DOIT capturer ses exceptions au catch level :

```ts
import * as Sentry from '@sentry/nestjs';

try {
  return await this.runEnrich(slot);
} catch (err) {
  Sentry.captureException(err, {
    tags: { role: 'r1', enricher: this.constructor.name },
    extra: { slot_id: slot.id, pg_id: slot.pg_id },
  });
  throw err; // re-throw pour que le caller (batch runner) puisse abort/retry
}
```

**Garde mécanique** (PR-X2-min monorepo) : règle ast-grep
`no-enricher-without-sentry-capture.yml` qui flag tout `catch` block
dans `*-enricher.service.ts` ne contenant pas `Sentry.captureException`.

### Compteurs OTel minimum (Livrable 3 bis)

```ts
// Avec @opentelemetry/api Counter
seo_enrich_total{role, outcome}      // outcome: success|fail|skip
seo_gate_violation_total{role, gate} // gate: gatekeeper|router|content|...
```

Cardinalité bornée : `role` ∈ R0..R8 (9 valeurs), `outcome` ∈ 3, `gate`
∈ ~6. Total maximum 9*3 + 9*6 = 81 séries — supportable Prometheus
remote-write.

## Statut

- **Statut** : `proposed` (cet ADR — ratification dans la même PR vault
  Phase 0 que [[ADR-046-r-stack-single-generator-and-layers]] ratify et
  [[ADR-047-seo-role-contracts-as-code]] ratify)
- **Implémentation** : Phase 0 baseline du plan refondation R-stack
  - **PR-X1 monorepo** (Action 6 master plan, ~1.5j) : table SQL +
    RPC + partition cron + RLS
  - **PR-X2-min monorepo** (Action 7 master plan, ~1j) : Sentry
    `captureException` + 2 compteurs OTel + ast-grep guard
- **Prérequis bloquant** : pour PR-T (re-enrich 163 slots Phase 4) —
  tant que `__seo_quality_history` + RPC outliers + instrumentation
  Sentry/OTel ne sont pas LIVE, **PR-T ne peut pas merger** (sans
  baseline ni détection drift, impossible de distinguer une
  amélioration d'une régression).

## Conséquences

### Positives

- **Drift mensuel détectable** : régression de 30% sur
  `gatekeeper_score` médian R1 sur 30 jours est captée par
  `detect_quality_outliers()`, alertable Slack/Sentry.
- **Backfill safety net** : tout script `r{N}-backfill.ts` peut
  comparer pre/post snapshot et abort si delta > seuil. Plus
  d'incident type "80K images supprimées silencieusement"
  (cf. `incident-images-2026-04-11.md`).
- **`/health` content-aware** : le endpoint NestJS peut interroger
  `detect_quality_outliers(window=24h, drop_pct=0.50)` et répondre
  503 si dérive critique récente. Stop la propagation de pannes
  silencieuses.
- **Visibilité Sentry exhaustive** : toute 502 Anthropic, timeout
  Supabase, parse error d'un enricher remonte avec contexte
  `role`, `pg_id`, `slot_id`. Triage en O(1).
- **Métriques OTel agrégeables** : Prometheus / Grafana peut
  dashboarder `rate(seo_enrich_total{outcome="fail"}[5m])` par
  rôle, et alerter si > 10%.

### Négatives / risques

- **Cardinalité OTel à surveiller** : 81 séries max actuellement, mais
  l'ajout futur d'un nouveau rôle (R9) ou d'un label libre (ex.
  `error_class`) ferait exploser. Mitigation : ast-grep guard sur
  toute tentative d'ajout de label hors enum bounded.
- **Cron mensuel à monitorer** : la fonction
  `ensure_next_month_partition()` doit s'exécuter avant le 28 de
  chaque mois — sinon `INSERT` du 1er suivant échoue. Mitigation :
  cron 25 du mois + alerting sur job failure.
- **Volume snapshot** : ~163 slots × 8 rôles × 5 métriques × 12 mois
  = ~78K rows/an. Acceptable Supabase (sub-1GB sur 5 ans). Au-delà,
  drop des partitions > 24 mois.
- **Dépendance Phase 0** : aucun enricher ne peut merger après
  cette ADR sans `Sentry.captureException` (ast-grep guard fail
  CI). Coût : refactor 8 enrichers existants — **wave-by-wave en
  PR-X2-min**, pas big-bang.

## Anti-patterns à rejeter (futurs)

- ❌ **Enricher sans `Sentry.captureException` au catch level** —
  bloqué par `no-enricher-without-sentry-capture.yml` (PR-X2-min).
- ❌ **Batch backfill sans pre/post snapshot dans `__seo_quality_history`**
  — bloqué par convention `r{N}-backfill.ts` doit appeler
  `recordQualitySnapshot('pre_batch'|'post_batch')` (test snapshot dans
  PR-X1, ast-grep guard à étendre Phase 1).
- ❌ **Ajouter un label OTel libre (`error_class`, `user_id`, etc.)** —
  cardinalité non-bornée, cassage Prometheus. Reviewer rejette.
- ❌ **`/health` qui répond 200 sans interroger
  `detect_quality_outliers()` sur fenêtre courte** — toute mise à jour
  du `/health` endpoint NestJS doit rester content-aware (test E2E
  PR-X1).
- ❌ **Drop d'une partition `__seo_quality_history_YYYY_MM` < 24 mois**
  — risque de perdre la baseline drift. RLS `service_role` only sur
  DELETE/DROP des partitions.

## Références

- Plan détaillé : `/home/deploy/.claude/plans/je-remarque-une-faiblesse-eventual-flamingo.md`
  (§ Action 6 PR-X1, § Action 7 PR-X2-min)
- Reconciliation numérotation :
  `/home/deploy/.claude/plans/adr-status-r-el-sujet-lively-flurry.md`
  (ADR-049 claimée par autre session pour DB Governance — cet ADR
  prend ADR-050)
- Audit baseline : [[2026-05-07-r-stack-audit]] (trou #8)
- ADRs liés Phase 0 :
  - [[ADR-046-r-stack-single-generator-and-layers]] (cadre L0-L5)
  - [[ADR-047-seo-role-contracts-as-code]] (SoT comportemental)
- Mémoires session : `incident-images-2026-04-11.md`,
  `feedback_no_overclaim_security_words.md`,
  `feedback_empirical_proof_external_systems.md`
- Précédent ADR observabilité : [[ADR-021-database-rls-hardening-zero-trust]]
  (RLS per-table) — pattern fail-closed similaire
