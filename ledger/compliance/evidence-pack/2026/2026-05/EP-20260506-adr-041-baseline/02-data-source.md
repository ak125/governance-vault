# 02 — Source de données

## Pipeline existant (à réutiliser, pas à recréer)

```
Google Search Console API
        │ (SA Owner sc-domain:automecanik.com)
        ▼
googleapis npm + searchconsole_v1   ← gsc-daily-fetcher.service.ts:17
        │
        ▼
Supabase __seo_gsc_daily             ← upsert quotidien (cron)
        │
        ▼
SQL d'agrégation 28j rolling         ← cette evidence-pack (03-)
        │
        ▼
JSON snapshot YYYY-MM-DD.json        ← /snapshots/
```

## Code source

| Fichier | Rôle |
|---------|------|
| [`backend/src/modules/seo-monitoring/services/gsc-daily-fetcher.service.ts`](../../../../../monorepo/backend/src/modules/seo-monitoring/services/gsc-daily-fetcher.service.ts) | Fetch quotidien GSC → upsert `__seo_gsc_daily` |
| [`backend/src/modules/seo-monitoring/services/google-credentials.service.ts`](../../../../../monorepo/backend/src/modules/seo-monitoring/services/google-credentials.service.ts) | SA credentials loader (env vars `GSC_CLIENT_EMAIL`, `GSC_PRIVATE_KEY`, `GSC_SITE_URL`) |
| [`backend/src/modules/seo-monitoring/processors/seo-daily-fetch.processor.ts`](../../../../../monorepo/backend/src/modules/seo-monitoring/processors/seo-daily-fetch.processor.ts) | BullMQ processor déclenchant le fetch |
| [`backend/src/workers/services/seo-monitor-scheduler.service.ts`](../../../../../monorepo/backend/src/workers/services/seo-monitor-scheduler.service.ts) | Cron schedule du fetch quotidien |

## Variables d'env requises (déjà configurées prod)

- `GSC_CLIENT_EMAIL` (pas `GOOGLE_SA_CLIENT_EMAIL` — voir mémoire `feedback_verify_existing_first`)
- `GSC_PRIVATE_KEY`
- `GSC_SITE_URL` (= `sc-domain:automecanik.com`)

## Conformité

- Pas de nouvelle infra GSC (per `feedback_verify_existing_first` — pipeline GSC daily existait).
- Pas de nouveau service backend ni nouvelle ENV var.
- Pas de write au cours de l'extraction (lecture pure `__seo_gsc_daily`).

## Limites connues

- `__seo_gsc_daily` ne stocke que les rows retournés par l'API GSC : URLs avec impressions ≥ 1 sur la fenêtre. Une URL R1 avec 0 impression n'apparaîtra pas → trace explicite "missing" dans le snapshot.
- L'API GSC a un délai T-2 à T-3 jours ; baseline 2026-05-06 reflète données jusqu'à 2026-05-03/04.
- Per `feedback_supabase_cost_traps`, queries lourdes sur gros range = cost. Les requêtes ici sont indexées sur `(date, page)` — coût négligeable.
