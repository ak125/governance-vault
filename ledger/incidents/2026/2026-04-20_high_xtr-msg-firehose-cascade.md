---
id: INC-2026-004
date: 2026-04-20
severity: high
status: resolved
impact_duration: "~3 semaines (latence diffuse) + ~1 h de hard-failure 2026-04-18"
affected_systems:
  - ___xtr_msg
  - ErrorLogService
  - GlobalErrorFilter
  - RagChangeWatcherService
  - __pipeline_chain_queue
  - Supabase REST API (PostgREST)
root_cause: "Firehose de logs d'erreur dans ___xtr_msg (insert synchrone à chaque 4xx/5xx) qui saturait PostgREST, provoquant 15 s de timeouts sur les autres appels Supabase — chaque timeout générait à son tour une OperationFailedException insérée dans ___xtr_msg (boucle positive)."
related_rules:
  - G2-zero-orphelin
  - G4-ci-read-only
related_adr:
  - ADR-010-ci-final-authority
related_prs:
  - "ak125/nestjs-remix-monorepo#83"
  - "ak125/nestjs-remix-monorepo#84"
owner: "@fafa"
reviewed_by: ""
---

# Incident: `___xtr_msg` firehose cascade → timeouts Supabase REST

## Résumé

`ErrorLogService.logError()` écrivait **2 inserts synchrones par erreur HTTP** (un log + un `ERROR_STATISTICS` dérivé). `GlobalErrorFilter` le déclenchait sur chaque 4xx/5xx. Googlebot frappant des URLs de storage cassées (concat double `https:/.../https:/...`) injectait ~2 500 ERROR_404 sur 10 min. PostgREST saturait. Les requêtes légitimes (notamment `RagChangeWatcherService`) timeout-aient à 15 s, déclenchant `OperationFailedException` → insert → saturation amplifiée.

## Timeline

| Heure (UTC) | Événement |
|-------------|-----------|
| ~2026-03 | Conditions en place (GlobalErrorFilter + ErrorLogService existants) |
| 2026-04-18 ~15:10 | User reporte timeouts `RagChangeWatcherService` récurrents (logs backend) |
| 15:15 | Investigation : `__rag_change_events`=0 pending, `__pipeline_chain_queue`=50 pending orphelins |
| 15:18 | Mesure directe curl VPS → Supabase : TTFB 37 ms, body 13-20 s (saturation PostgREST confirmée) |
| 15:20 | Premier fix (#83) : RPC `rag_watcher_breaker_metrics()` (3 calls → 1) + purge 50 orphelins |
| 15:35 | Investigation racine : ~12 500 inserts/10 min sur `___xtr_msg`, dominé par `ERROR_OperationFailedException` (feedback loop) |
| 15:55 | Deuxième fix (#83) : ErrorLogService buffer + batch + dedup + bot filter + circuit breaker |
| 16:06 | Rate d'inserts `___xtr_msg` : 60/min → 3/min (-95 %) |
| 16:20 | PR #83 mergée + déployée en prod |
| ~13:15 (+2 j) | Plan de nettoyage architectural accepté |
| 13:16 | Table dédiée `__error_logs` appliquée en DB (typed schema + pg_cron 30 j) |
| 13:20 | Refactor `ErrorLogService` → écrit dans `__error_logs` |
| 11:35 UTC 2026-04-20 | PR #84 mergée + deploy prod |

## Impact

- **Utilisateurs affectés** : latence diffuse backend (p95 dégradé sur les endpoints hitting Supabase), pas d'indisponibilité totale
- **Transactions perdues** : 0 identifiée (les erreurs loguées en doublon n'ont pas bloqué de commande)
- **Durée d'indisponibilité** : aucune coupure franche, ~3 semaines de latence mesurable sur `RagChangeWatcherService` (timeouts 15 s toutes les ~60 s)
- **Impact business** : SEO pipeline R1→R6 bloqué par pressure PostgREST, dashboards admin d'erreurs pollués par 2022+ rows `ERROR_STATISTICS` en 10 min

## Root Cause

3 causes composées :

1. **Firehose synchrone** — `ErrorLogService.logErrorOriginal` et `logErrorAdvanced` faisaient `await supabase.from(TABLES.xtr_msg).insert(row)` pour **chaque** erreur HTTP, sans buffering ni dedup. Plus `updateStatistics()` qui inséra un second row `ERROR_STATISTICS` à chaque fois.
2. **Boucle positive** — chaque timeout (OperationFailedException) était lui-même loggé via le même chemin, générant plus de pression sur PostgREST, donc plus de timeouts.
3. **Pas de filtre bots** — Googlebot-Image frappant des URLs de storage cassées (bug de concat `https:/cxpoj.../https:/cxpoj.../...`) générait ~ 2 500 ERROR_404/10 min, tous persistés en DB.

Aggravants :

- `___xtr_msg` est une table fourre-tout (redirect rules, legal docs, support) — indexes partagés entre concerns sans rapport
- Aucune retention policy côté DB, cleanup applicatif jamais appelé → table à ~6 M lignes
- `msg_date` en TEXT (pas timestamptz) rendait les filtres temporels lexicographiques → pièges d'analyse

## Résolution

### PR #83 — `fix(rag-watcher): collapse breaker checks into single server-side RPC`

```sql
-- Migration 20260418_rag_watcher_breaker_metrics_rpc.sql
CREATE OR REPLACE FUNCTION public.rag_watcher_breaker_metrics() RETURNS jsonb ...
CREATE INDEX idx_pcq_created_at ON __pipeline_chain_queue (pcq_created_at DESC);
```

- `RagChangeWatcherService.evaluateBreakerConditions()` : 3 REST calls → 1 RPC (JSONB)
- 50 rows orphans `pending` dans `__pipeline_chain_queue` marquées `failed` avec reason (fausse alerte breaker retirée)

### PR #83 (même PR) — `fix(error-log): buffer + batch + dedup + bot filter + breaker`

- `ErrorLogService` : buffer 2000 + flush 5 s + batch ≤ 500 rows par insert
- Dedup signature `(subject|url|ip)` TTL 60 s
- Bot-UA filter 4xx (Googlebot, Bingbot, AhrefsBot, imgproxy, …) → `logger.debug`, pas de DB
- Circuit-breaker auto-off après 3 échecs consécutifs de flush, silent 60 s puis retry
- Retrait du second insert `ERROR_STATISTICS`

### PR #84 — `feat(error-log): dedicated __error_logs table + pg_cron retention`

```sql
CREATE TABLE __error_logs (err_id bigserial, err_created_at timestamptz, err_severity text CHECK ..., err_ip inet, err_context jsonb, ...);
SELECT cron.schedule('error-logs-retention', '0 3 * * *',
  $$DELETE FROM __error_logs WHERE err_created_at < now() - interval '30 days'$$);
```

- Table dédiée typée, 4 indexes ciblés (created_at, subject+created, unresolved partial, severity critical/high partial)
- `ErrorLogService` redirige writes + reads vers `__error_logs`
- `___xtr_msg` conserve seulement ses usages légitimes (redirects, legal, support)

### Fix de compliance CI

- `RagChangeWatcherService` passe par `SupabaseBaseService.callRpc()` (gouvernance) au lieu de `this.client.rpc()` direct → RPC Safety Gate ✅

## Mesures (DEV live)

| Métrique | Avant | Après |
|---|---|---|
| Inserts/min `___xtr_msg` | ~60 | ~3 (-95 %) |
| REST INSERT calls/min | ~60 | ~3 |
| `rag_watcher_breaker_metrics` RPC | timeouts 15 s | 53 ms avg / 171 ms max |
| Watcher RPC success rate | ~0 % | 100 % (28/28 sur observation) |
| `ERROR_STATISTICS` writes | 2 022 / 10 min | 0 |
| ERROR_404 bots | dominant | 0 |

## Lessons Learned

1. **Les logs d'erreur ne doivent jamais partager leur backend avec un flux business.** Une table fourre-tout pour erreurs + redirects + legal + support est un anti-pattern (indexes partagés, retention impossible, debugging difficile).
2. **Un logger synchrone est une arme de destruction.** Le choke-point d'erreur doit être async, buffered, dedupé, avec circuit-breaker **sur lui-même**. Sinon toute latence backend devient une boucle positive.
3. **Filtre bots dès le choke-point.** 4xx venant de crawlers n'apporte aucune valeur métier — logger.debug suffit.
4. **`msg_date` en TEXT = piège analytique.** Toujours timestamptz, avec index DESC et partitioning ou TTL via pg_cron si volume élevé.
5. **pg_stat_statements est obligatoire** pour diagnostiquer ce genre de cascade — différencier `calls` vs `rows` révèle le batching effectif.

## Actions Correctives

- [x] PR #83 mergée (watcher RPC + error-log hardening) — 2026-04-18
- [x] PR #84 mergée (table dédiée + pg_cron) — 2026-04-20
- [x] Incident documenté (ce fichier)
- [ ] Audit des autres services écrivant dans `___xtr_msg` pour valider qu'aucun flux business n'y pousse plus d'erreurs — Owner: @fafa — Deadline: 2026-04-30
- [ ] Scanner les autres tables fourre-tout candidates au même pattern (ex: `__blog_advice` ?) — Owner: @fafa — Deadline: 2026-05-15
- [ ] Alerte Prometheus/Grafana sur rate d'inserts `__error_logs` > 30/min pour détecter une prochaine cascade — Owner: @fafa — Deadline: 2026-05-15

## Preuves

- Log backend initial (extraits) : `Supabase Request Timeout (15s) for …/__rag_change_events`, `Supabase Request Timeout (15s) for …/rpc/rag_watcher_breaker_metrics`, `breaker_metrics_rpc_failed: ConfigurationException`
- Mesure directe : curl VPS → Supabase (5 requêtes), total 13-20 s malgré TTFB 37 ms
- `pg_stat_statements` : 6 009 550 INSERT cumulés sur `___xtr_msg` avec `rows = calls` (zéro batching pré-fix)
- Query dedup (post-fix) : 533 rows OperationFailedException sur 10 min avec `err_subject` distinct par alias

## Références

- PR #83 : https://github.com/ak125/nestjs-remix-monorepo/pull/83 (commit `3fee687f`)
- PR #84 : https://github.com/ak125/nestjs-remix-monorepo/pull/84 (commit `b71fef8b`)
- Migration #1 : `backend/supabase/migrations/20260418_rag_watcher_breaker_metrics_rpc.sql`
- Migration #2 : `backend/supabase/migrations/20260420_error_logs_dedicated_table.sql`
- Service : `backend/src/modules/errors/services/error-log.service.ts`
- Service : `backend/src/workers/services/rag-change-watcher.service.ts`
