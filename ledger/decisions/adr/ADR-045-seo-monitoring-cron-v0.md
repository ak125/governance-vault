---
id: ADR-045
title: "SEO Monitoring Cron V0 — daily-fetch GSC/GA4/Links + cron/health endpoint"
status: proposed
date: 2026-05-07
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G3", "Q1", "AP-04", "AP-08"]
related_incidents: []
related_adr: ["ADR-025", "ADR-028", "ADR-044"]
implementation_status: v0a-pr-340-open
---

# ADR-045 — SEO Monitoring Cron V0

## Contexte

[[ADR-044-seo-strategy-2026-roles-priority]] (proposed simultanément) classe la
Vague 0 du plan SEO 2026 comme **socle obligatoire** de pilotage : sans cron
quotidien sur les fetchers existants `GscDailyFetcherService`,
`Ga4DailyFetcherService`, `GscLinksFetcherService`, les tables
`__seo_gsc_daily` / `__seo_ga4_daily` / `__seo_gsc_links_weekly` redeviennent
stales sous 48h, et aucune mesure d'impact n'est possible pour les vagues
contenu (V1 R6, V2 S2_DIAG, V3 R8, V4 R7).

### État pré-V0 (cartographie session 2026-05-06)

- ✅ Queue BullMQ `seo-monitor` enregistrée
- ✅ `SeoMonitorSchedulerService` non-blocking (pattern `void warmer()`)
- ✅ `SeoMonitorProcessor` actif (jobs `check-pages` toutes les 30min/6h pour URLs
  critiques — orthogonal au daily-fetch)
- ✅ Fetchers `GSC`/`GA4`/`CWV`/`GSC Links` opérationnels (testés via backfill 33j
  sur `cxpojprgwgubzjyqzmoq`)
- ✅ `SeoMonitoringRunsService.logStarted/logCompleted/logFailed` câblés dans les
  4 fetchers
- ✅ Table `__seo_event_log` (event_type ENUM `seo_event_type` + payload JSONB
  + index GIN), valeurs ENUM incluent déjà `ingestion_run_started/completed/failed`
  et `anomaly_detected`
- ✅ Sentry backend init (commits #324/#327/#334 — `instrument.ts`)
- ❌ **Aucun cron** ne déclenche les fetchers daily — c'est le manque exact
- ❌ **Aucune route health** par fetcher (pas de détection silently-broken)
- ❌ **Aucune segmentation par rôle** dans `__seo_gsc_daily` (V0.5 — séparé)

### Contrat CWV exclu volontairement

`CwvFetcherService.fetchAndPersist({ pages: string[], strategy?, date?, dryRun? })`
exige une liste explicite de pages à auditer. L'établissement de cette liste
(top 1000 prioritaires) requiert un nouveau service `gsc-coverage-fetcher`
prévu en **V0.D** (separate ADR ultérieur). Brancher CWV dans le daily-fetch
sans ce sample serait du bricolage (liste arbitraire ou liste vide).

## Décision

### Architecture

Nouveau processor **`SeoDailyFetchProcessor`** dans
`backend/src/modules/seo-monitoring/processors/seo-daily-fetch.processor.ts` :

- Décorateur `@Processor('seo-monitor')` (même queue que `SeoMonitorProcessor`)
- Handler `@Process('daily-fetch')` distinct (cohabitation propre — pas de
  modification de l'existant)
- Inject DI : `GscDailyFetcherService`, `Ga4DailyFetcherService`,
  `GscLinksFetcherService`, `AdminJobHealthService`
- Date par défaut **J-3** (latence GSC ~3j, GA4 ~24-48h)
- Task `all` exécute **GSC + GA4 + Links** (pas CWV)
- Failure isolée par source (un échec GSC n'annule pas GA4/Links)

Extension de **`SeoMonitorSchedulerService.configureRepeatableJobs()`** :

- `setupDailyFetchJob()` cron `0 4 * * *` UTC (04:00)
  - `attempts: 3`, `backoff: { type: 'exponential', delay: 30_000 }` (30s / 1min / 2min)
  - `removeOnComplete: 30` (~1 mois historique), `removeOnFail: 100` (debug)
  - `jobId: 'seo-daily-fetch'` (idempotent)
- `triggerManualDailyFetch({ date?, task? })` pour debug/backfill (priority:1, attempts:1)

Nouvelle méthode service **`SeoMonitoringRunsService.getRunsHealth()`** :

- Lit `__seo_event_log` filtré par `event_type IN ('ingestion_run_completed', 'ingestion_run_failed')`
  ET `payload->>source IN ('gsc', 'ga4', 'cwv', 'gsc_links')`
- Retourne par source : `lastSuccessAt`, `lastFailureAt`, `lastFailureClass`,
  `lastFailureMessage`
- Aucune colonne structurée nouvelle ajoutée — utilise `payload JSONB` existant

Nouvelle route **`GET /api/admin/seo-monitoring/cron/health`** dans le controller :

- Retourne `{ overall, monitoring_enabled, checked_at, stale_threshold_hours: 36, sources[] }`
- `overall = 'healthy'` ssi tous les fetchers ont un `lastSuccessAt` dans les 36h
- Staleness threshold 36h = J-3 par défaut + tolérance 12h
- Utilisable par monitoring externe (Slack alerting, dashboard, readiness probe)

### Garde-fous canon

| Garde-fou | Implémentation |
|---|---|
| **READ_ONLY gate au processor** ([[ADR-028-preprod-supabase-isolation]] Option D) | `if (this.readOnly) { logger.warn('[READ_ONLY] Skip seo-daily-fetch'); return emptyResult(...) }` — cron registered en preprod miroir prod, court-circuit sans appel API/DB |
| **Failure isolée par source** | `try/catch` dans la boucle `for (const t of tasks)` → un échec GSC ne court-circuite pas GA4/Links |
| **Non-blocking `onModuleInit`** | Pattern existant `void this.configureRepeatableJobs()` respecté (cf. `.claude/rules/backend.md` du monorepo) |
| **Pas de schema change** | `__seo_event_log` reste générique (`event_type ENUM + payload JSONB` + index GIN existant) |
| **Sentry capture** | Déjà initialisé via `instrument.ts` — capture automatique des exceptions backend |

## Statut

- **Statut** : proposed (PR vault en cours, cet ADR)
- **Implémentation** : monorepo PR #340 ([feat/seo-v0a-cron-foundation](https://github.com/ak125/nestjs-remix-monorepo/pull/340))
  - 5 fichiers, 441 insertions, 0 suppression
  - Commit `1f317f74` `feat(seo-monitoring): add daily-fetch cron and cron/health endpoint`
  - Typecheck ✅, ESLint+Prettier ✅, CI en cours
- **Hors-scope V0.A (PRs séparées)** :
  - V0-bis : OpenTelemetry + Prometheus + DLQ replay UI + Redlock distribué
  - V0.B : GA4 multi-events client + sanitize PII helper
  - V0.C : GA4 Measurement Protocol server-side (purchase backend)
  - V0.D : `gsc-coverage-fetcher` + sample top 1k + CWV intégré daily

## Conséquences

### Positives

- **Réutilisation 100% existant** : 0 nouveau service core, juste un processor
  qui orchestre + un cron qui déclenche + un health endpoint qui lit. Toute la
  logique de fetch/log/persist était déjà câblée dans les fetchers PROD.
- **Failure isolation** : un échec GSC (quota, auth) ne casse pas GA4/Links —
  observabilité par source via `__seo_event_log`
- **READ_ONLY safe** : le cron peut shipper en preprod (validation BullMQ wiring)
  sans risque d'appel API/DB
- **Health endpoint permet alerting externe** sans dépendre du stack OTel
  (V0-bis), donc V0 ship rapidement et observable

### Négatives / risques

- **Pas de Redlock distribué en V0.A** : si 2 instances backend tournent en
  preprod simultanément (deploy en cours), le job daily peut s'exécuter en
  double. Mitigé par : (a) `jobId` unique BullMQ qui évite les duplicates dans
  le repeat schedule ; (b) idempotence des fetchers via upsert
  `onConflict: 'date,page,query,device'`. Redlock proposé en V0-bis.
- **Pas de DLQ replay UI** : si un job échoue 3 fois, il reste dans `failed`
  state — debug manuel requis. UI proposée en V0-bis.
- **CWV exclu** : le daily-fetch ne couvre pas Core Web Vitals tant que V0.D
  (gsc-coverage-fetcher + sample top 1k) n'est pas livré. Mitigé : CWV reste
  triggable manuellement via la route admin existante avec liste de pages
  explicite.
- **Pas d'OTel/Prometheus en V0.A** : observabilité limitée aux logs Sentry +
  `__seo_event_log` query. Acceptable pour V0, OTel ajouté en V0-bis.

## Anti-patterns à rejeter (futurs)

- ❌ Modifier `SeoMonitorProcessor` existant pour y ajouter le daily-fetch =
  pollution single-responsibility. Use-case orthogonal (URLs critiques 30min/6h
  vs daily fetch 04:00 UTC).
- ❌ Bypasser `SeoMonitoringRunsService` pour écrire directement dans
  `__seo_event_log` = duplication logique, anti-pattern AP-11
- ❌ Ajouter une colonne structurée à `__seo_event_log` (`anomaly_type`,
  `delta_pct`) = la table est volontairement générique avec payload JSONB
  + index GIN. Conserver pour évolutions futures (V0.5 anomaly detection).
- ❌ `Cron` decorator NestJS au lieu de BullMQ repeatable job = incompatible
  avec le pattern existant `seo-monitor` queue, perte de retry/persistance.
- ❌ Coder CWV avec `pages: []` ou liste arbitraire = bricolage. Attendre V0.D.

## Références

- Plan détaillé monorepo : `.claude/plans/utiliser-la-meilleure-approche-zippy-waterfall.md` § V0.A
- PR monorepo : https://github.com/ak125/nestjs-remix-monorepo/pull/340
- Mémoires session : `seo-strategy-2026-approved-20260506`,
  `feedback_seo_methodology_canon_20260506`,
  `feedback_event_log_uses_payload_jsonb` (8e règle methodologie)
- ADRs liés : ADR-025 (SEO Department), ADR-028 (Option D READ_ONLY),
  ADR-044 (SEO Strategy 2026 master)
