---
type: runbook
status: canon
updated: 2026-06-26
related: [ADR-045, ADR-063, ADR-028]
---

# Runbook — CWV RUM Pipeline Recovery (raw → hourly → daily_rum)

> Récupération opérationnelle de la chaîne d'agrégation **RUM** (Real User Monitoring)
> Core Web Vitals, **orchestrée par pg_cron** depuis la migration
> `20260626_seo_cwv_aggregation_cron`. **Distinct de [[cwv-alert-response]]** (alertes CrUX
> field, latence 7–10 j). Ici : la donnée RUM est interne, quasi-instantanée, et **se perd
> définitivement passé le TTL raw (~48 h)** si l'agrégation décroche.
>
> Cause de création : agrégation **figée 2026-06-03 → 2026-06-23** (scheduler Bull v4 mort
> sur le poste DEV — `onModuleInit` retournait sur flag-off avant le nettoyage). Incident
> `web-vitals-attribution-unstable`. Fix monorepo #1165 (pg_cron) + #1166 (retrait Bull).

## Topologie — RUM vs CrUX vs lab (ne pas confondre)

| Source | Table(s) | Nature | Fraîcheur | Orchestration |
|--------|----------|--------|-----------|---------------|
| **RUM** (ce runbook) | `__seo_cwv_raw` → `__seo_cwv_hourly` → `__seo_cwv_daily_rum` | Field, beacons humains | Quasi-instantané (raw), horaire/journalier (agrégats) | **pg_cron** |
| **CrUX** ([[cwv-alert-response]]) | `__seo_crux_field_history` | Field, Chrome agrégé | Inertiel 7–10 j (fenêtre 28 j) | BullMQ `seo-monitor` |
| **Lab** | `__seo_cwv_daily` | Synthetic PageSpeed (top-1k) | Reproductible | (hors scope) |

`__seo_cwv_raw` : bloc 3, beacons landing, **humains uniquement** (les bots vont dans
`__seo_event_log`), partitions daily, **TTL ~48 h**. `__seo_cwv_hourly` : bloc 4, agrégat par
`(surface × route_group × device × metric × ua_class)`, TTL 14 j. `__seo_cwv_daily_rum` :
bloc 4, rollup journalier (moyenne pondérée `sample_count`), TTL 12 mois.

## Composants

| Composant | Path / objet | Rôle |
|-----------|--------------|------|
| **RPC horaire** | `aggregate_cwv_hourly(p_target_hour timestamptz)` | raw → hourly, UPSERT idempotent |
| **RPC journalier** | `aggregate_cwv_daily_rum(p_target_date date)` | hourly → daily_rum (pondéré) |
| **Cron horaire** | `cwv-hourly-aggregation` @ `5 * * * *` | réagrège les 48 dernières heures (auto-heal) |
| **Cron journalier** | `cwv-daily-rum-aggregation` @ `15 0 * * *` UTC | réagrège hier + avant-hier |
| **Détecteur couverture** | `detect_cwv_aggregation_coverage_gap()` + job `cwv-aggregation-coverage-check` @ `35 * * * *` | alerte heures raw non agrégées ; auto-résout OPEN→RESOLVED |
| **Consommateur** | `CwvDashboardService` → `get_cwv_dashboard` RPC → `GET /api/seo/cwv/dashboard` | lit `__seo_cwv_daily_rum` |

## Diagnostic (dans l'ordre)

### 1. Les deux jobs existent, sont actifs, et ont tourné (exécution, pas existence)

```sql
SELECT j.jobname, j.schedule, j.active, r.status, r.return_message, r.start_time
FROM cron.job j
LEFT JOIN LATERAL (SELECT * FROM cron.job_run_details d
                   WHERE d.jobid = j.jobid ORDER BY d.start_time DESC LIMIT 1) r ON true
WHERE j.jobname IN ('cwv-hourly-aggregation','cwv-daily-rum-aggregation');
-- Pré-requis : SELECT current_setting('cron.log_run', true);  -- doit être 'on'
```
Attendu : 2 lignes, `active=true`, dernier `status='succeeded'`, `start_time` récent
(hourly < 1 h, daily < 24 h). Absence / `null` / `failed` → section Réparation.

### 2. Couverture (anti-join raw → hourly)

```sql
WITH raw_hours AS (
  SELECT DISTINCT date_trunc('hour', received_at) AS hour
  FROM __seo_cwv_raw
  WHERE ua_class = 'human' AND received_at < date_trunc('hour', now())
)
SELECT count(*) AS missing_complete_hours
FROM raw_hours r
WHERE NOT EXISTS (SELECT 1 FROM __seo_cwv_hourly h WHERE h.hour = r.hour AND h.ua_class = 'human');
-- Attendu : 0. > 0 → trou de couverture (backfill ci-dessous AVANT purge raw).
```
Fraîcheur daily : `SELECT max(date) FROM __seo_cwv_daily_rum;` → doit être ≥ J-1 (UTC).

### 3. Pas de double orchestrateur Bull (état résiduel après bascule)

```bash
# Sur le runtime worker concerné (REDIS_URL), lecture seule, URL Redis rédigée :
tsx scripts/audit/runtime-truth/bull-repeatable-drift.ts
# Attendu : 0 repeatable / waiting / delayed / active préfixés 'cwv-aggregation'.
```

### 4. Partitions (le raw doit avoir une partition courante)

```sql
SELECT c.relname FROM pg_inherits i
JOIN pg_class c ON c.oid = i.inhrelid
JOIN pg_class p ON p.oid = i.inhparent
WHERE p.relname = '__seo_cwv_raw' ORDER BY c.relname DESC LIMIT 3;
-- Vérifier qu'une partition couvre aujourd'hui (sinon les beacons échouent à l'insert).
```

## Réparation

### A. Mesurer + journaliser la perte AVANT tout write (baseline)

```sql
WITH d AS (SELECT max(date) AS last_daily FROM __seo_cwv_daily_rum),
     r AS (SELECT (min(received_at) AT TIME ZONE 'UTC')::date AS first_raw
           FROM __seo_cwv_raw WHERE ua_class = 'human')
SELECT last_daily, first_raw, last_daily + 1 AS lost_from, first_raw - 1 AS lost_to FROM d CROSS JOIN r;
```
`lost_from .. lost_to` = **fenêtre perdue définitivement** (raw déjà purgé). La consigner
(audit-trail vault / `log.md`). **Aucune reconstruction artificielle** : on n'invente pas de
lignes pour une fenêtre dont le raw a expiré — la perte est documentée, pas comblée.

### B. Backfill ordonné (hourly AVANT daily — daily lit hourly)

```sql
-- 1) heures complètes présentes dans raw (UTC-explicite) :
WITH b AS (SELECT date_trunc('hour', min(received_at) AT TIME ZONE 'UTC') AT TIME ZONE 'UTC' AS first_hour,
                  date_trunc('hour', now() AT TIME ZONE 'UTC') AT TIME ZONE 'UTC' - interval '1 hour' AS last_hour
           FROM __seo_cwv_raw WHERE ua_class = 'human')
SELECT public.aggregate_cwv_hourly(gs.h) FROM b
CROSS JOIN LATERAL generate_series(b.first_hour, b.last_hour, interval '1 hour') AS gs(h)
WHERE b.first_hour <= b.last_hour;
-- 2) vérifier hourly non vide, PUIS jours complets :
WITH b AS (SELECT (min(received_at) AT TIME ZONE 'UTC')::date AS first_date,
                  (now() AT TIME ZONE 'UTC')::date - 1 AS last_date
           FROM __seo_cwv_raw WHERE ua_class = 'human')
SELECT public.aggregate_cwv_daily_rum(b.first_date + off.d) FROM b
CROSS JOIN LATERAL generate_series(0, b.last_date - b.first_date) AS off(d)
WHERE b.first_date <= b.last_date;
```
Les RPC sont idempotentes (UPSERT) : réagréger une heure déjà faite est un no-op sûr.

### C. Purger une repeatable Bull résiduelle (si section 3 ≠ 0)

Sur le runtime worker (poste DEV principalement) : désactiver le scheduler, puis
`removeRepeatableByKey` les configs `cwv-aggregation-hourly|daily` + retirer les jobs
`waiting`/`delayed` du même nom (laisser drainer un `active`). Re-vérifier via le probe = 0.
NB : depuis #1166 le code Bull CWV est supprimé — un résiduel ne peut venir que d'un runtime
non redéployé.

### D. Résolution manuelle d'une alerte coincée

Le détecteur auto-résout normalement quand la couverture revient. Si une alerte
`cwv_aggregation_coverage_gap` reste `OPEN` après backfill :
```sql
SELECT public.detect_cwv_aggregation_coverage_gap();  -- ré-évalue ; auto-résout si missing < seuil
-- En dernier recours (justifier dans l'audit-trail) :
UPDATE __seo_event_log SET resolved_at = now(),
  payload = payload || jsonb_build_object('resolution_kind','manual_after_backfill','resolved_at',now())
WHERE event_type = 'anomaly_detected' AND resolved_at IS NULL
  AND payload->>'alert_kind' = 'cwv_aggregation_coverage_gap';
```

### E. Rollback de la migration cron (si la planification elle-même est en cause)

`20260626_seo_cwv_aggregation_cron.down.sql` retire **uniquement** les jobs possédés par
cette migration (marqueur de provenance). Ne touche ni les RPC ni les rotations. Réversible.

## Preuve de rétablissement (consommateur)

```bash
curl -s "https://dev.automecanik.com/api/seo/cwv/dashboard" -H "Authorization: Bearer $ADMIN_JWT" | jq '.[0:2]'
```
Le dashboard renvoie des lignes fraîches (`__seo_cwv_daily_rum` à J-1) ⇒ trigger + sortie +
consommateur prouvés. Synchroniser l'overlay `automation-reality.yaml`
(`cwv-rum-aggregation`, `actual_mode: ACTIVE`).

## Notes latentes (à connaître)

- **Clé `ON CONFLICT` sans `priority_tier`.** `aggregate_cwv_*` groupe par `priority_tier`
  mais la clé d'upsert l'**omet** et *remplace* `sample_count` → **last-wins silencieux** si
  `priority_tier` dérivait à l'intérieur d'une même clé de conflit. Sûr aujourd'hui (dérivé
  serveur déterministe) ; à revoir si la dérivation devient non déterministe.
- **`fetched_at` = « dernière recomputation », pas « première vue ».** L'auto-heal réagrège
  les 48 dernières heures → `fetched_at` est réécrit à chaque tick. Ne pas l'interpréter
  comme date de première ingestion.

## Anti-patterns à rejeter

- ❌ **Reconstruire artificiellement** des lignes pour une fenêtre dont le raw a dépassé le
  TTL ~48 h. La perte se **documente**, ne s'invente pas.
- ❌ **Remettre l'agrégation sous un scheduler applicatif** (Bull/NestJS `@Cron`) « parce que
  c'est là que vit le code » — le SQL/RPC idempotent local à la donnée vit sous **pg_cron**
  (ADR-045 amendement 2026-06-26). Bull reste pour l'I/O externe.
- ❌ **Annoncer « pipeline rétabli »** sur la seule existence des jobs. Exiger un run
  `succeeded` POSTÉRIEUR au fix + `missing_complete_hours = 0` + daily J-1 + dashboard frais.
- ❌ **Purger le raw** avant d'avoir backfillé hourly/daily — perte définitive.

## Références

- [[ADR-045-seo-monitoring-cron-v0]] — amendement 2026-06-26 (placement pg_cron vs Bull)
- [[ADR-063-cwv-monitoring-prod-crux-api]] — CrUX field (distinct du RUM)
- [[ADR-028-preprod-supabase-isolation]] — Option D READ_ONLY
- [[cwv-alert-response]] — runbook CrUX (sibling)
- Monorepo : migration `20260626_seo_cwv_aggregation_cron`, PR #1165 / #1166 ;
  skills `web-vitals-audit` (checks `cwv-beacon-ingestion-gap` / `cwv-aggregation-coverage-gap`)
  + `runtime-truth-audit` (`scheduled-orchestrator-drift` + probe `bull-repeatable-drift.ts`).
