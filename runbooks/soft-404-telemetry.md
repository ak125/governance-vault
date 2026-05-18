# Runbook — Soft-404 R2 Telemetry

**Owner :** `@ak125/seo-team`
**Table :** `__soft_404_events`
**Vue :** `v_soft_404_demand_30d`
**Rétention :** 90 jours (cron purge à câbler post-merge dans `seo-routines`)
**ADR :** [ADR-076](../ledger/decisions/adr/ADR-076-soft-404-r2-strategy.md)

## Quoi

Table append-only des événements soft-404 R2 (page véhicule × gamme sans pièce compatible dans `pieces_relation_type`). Sert à mesurer la demande utilisateur non couverte par le catalogue, et à alimenter une demand-list pour le pôle contenu.

## Schéma

```
__soft_404_events (
  id        bigserial PRIMARY KEY,
  pg_id     integer NOT NULL,
  type_id   integer NOT NULL,
  ts        timestamptz NOT NULL DEFAULT now(),
  referrer  text,
  ua_class  text NOT NULL CHECK (ua_class IN ('bot','browser','unknown'))
);
```

- Pas de PII ; pas d'IP ; pas d'UA brut (seul `ua_class` ∈ {`bot`, `browser`, `unknown`}).
- Pas de session_id stocké ; le throttling Redis se fait en amont (clé `track-soft-404:{sessionId}` TTL 60s).
- `referrer` peut contenir un domaine externe → retention 90j.

## Vue agrégée 30j

```sql
v_soft_404_demand_30d  -- couples (pg_id, type_id) avec ≥ 3 hits browsers / 30j
```

## Requêtes utiles

### Top demand pour le pôle catalogue

```sql
SELECT pg_id, type_id, hits, last_seen
FROM v_soft_404_demand_30d
LIMIT 50;
```

### Enrichi avec gamme + véhicule (lecture humaine)

```sql
SELECT d.pg_id, pg.pg_name, d.type_id,
       ma.marque_name || ' ' || m.modele_name || ' ' || t.type_name AS vehicle,
       d.hits, d.last_seen
FROM v_soft_404_demand_30d d
JOIN pieces_gamme pg ON pg.pg_id = d.pg_id
JOIN auto_type t   ON t.type_id_i = d.type_id
JOIN auto_modele m ON m.modele_id = t.type_modele_id::int
JOIN auto_marque ma ON ma.marque_id = m.modele_marque_id::int
ORDER BY d.hits DESC
LIMIT 50;
```

### Distribution UA sur 7 jours (hygiène anti-bot)

```sql
SELECT ua_class, COUNT(*) AS hits
FROM __soft_404_events
WHERE ts > now() - interval '7 days'
GROUP BY ua_class
ORDER BY hits DESC;
```

### Purge manuelle 90j (au cas où le cron a sauté)

```sql
DELETE FROM __soft_404_events
WHERE ts < now() - interval '90 days';
```

## Alarmes & escalade

| Signal | Seuil | Action |
|---|---|---|
| Volume `browser` > 5 000 hits / jour pendant 3 jours consécutifs | high | Escalader pôle catalogue : la demand-list est mûre pour priorisation. |
| Volume `bot` > 50% des hits totaux 7j | medium | Revoir les patterns UA dans `rm-soft404-tracker.service.ts` (BOT_PATTERNS / BROWSER_PATTERNS). |
| Latence p95 sur `/api/rm/alternatives` > 250ms 5min | medium | Vérifier cache Redis hit-rate ; investiguer `RmAlternativesService.compute()` (OTel span `soft_404.alternatives.compute`). |
| Couverture alternatives < 95% sur smoke CI | high | Fixture déficiente OU bug `EXISTS pieces_relation_type` côté backend. |

## SLO associés

| Métrique | Cible V1 | Source |
|---|---|---|
| p95 `/api/rm/alternatives` | < 200 ms | OTel span `soft_404.alternatives.compute` |
| Cache hit Redis | > 70% | Redis INFO + métric `cache.hit_ratio` |
| Couverture alternatives (≥ 1 véhicule OU ≥ 1 gamme) | > 95% | Smoke CI (`scripts/ci/assert-soft-404.py`) |
| Soft-404 page render | 200 + noindex,follow + ItemList | Synthetic playwright (PR-V1.5) |

## Liens

- ADR-076 : [ADR-076-soft-404-r2-strategy.md](../ledger/decisions/adr/ADR-076-soft-404-r2-strategy.md)
- PR monorepo : [ak125/nestjs-remix-monorepo#595](https://github.com/ak125/nestjs-remix-monorepo/pull/595)
- Spec source : `docs/superpowers/specs/2026-05-18-soft-404-r2-strategy-design.md` (monorepo)

## Self-review verdict

APPROVE
