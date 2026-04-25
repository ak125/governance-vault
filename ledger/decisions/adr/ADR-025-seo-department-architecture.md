---
id: ADR-025
title: "SEO Department Architecture (Observability, On-page, Content ops, Intelligence, GEO/AEO)"
status: accepted
date: 2026-04-25
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G1, G2, G4, AP-10, AP-11]
related_incidents: []
reviewed_by: "Claude Code Opus 4.7"
---

# ADR-025: SEO Department Architecture

## Contexte

Le 2026-04-25, l'utilisateur a demandé un **département SEO complet, robuste et moderne, pas du bricolage** suite à la critique des livraisons précédentes (PR #159 + #164 — un simple vérificateur de vault Obsidian, pas une vraie team SEO).

Avant de rédiger un plan, 4 Explore agents ont été dispatchés en parallèle (skill `superpowers:dispatching-parallel-agents`) pour cartographier l'existant :

**État réel du codebase au 2026-04-25** :

| Domaine | Statut réel |
|---------|-------------|
| GSC Search Analytics + Inspection API | ✅ Branchés (`crawl-budget-audit.service.ts:208-218`), credentials lus depuis `GSC_CLIENT_EMAIL`/`GSC_PRIVATE_KEY`/`GSC_SITE_URL`. Manque : cron daily et persistance |
| GA4 Data API | ✅ Branché (`url-audit.service.ts:50-60`), `BetaAnalyticsDataClient` actif. Manque : cron daily et persistance |
| Internal linking | ✅ Service `internal-linking.service.ts` gère déjà ~105k liens, A/B testing config |
| E-E-A-T scoring | ✅ Embryon dans `conseil-pack.constants.ts` + `conseil-quality-scorer.service.ts` |
| BullMQ schedulers | ✅ Actifs (sitemap, audit weekly), 4 queues |
| Email transactionnel | ✅ Infrastructure complète (`nodemailer 8.0.0` + queue dédiée `email`) |
| Tables `__seo_entity_health`, `__seo_entity_score_v10`, `__seo_index_status` | ✅ Créées et partiellement peuplées |
| PageSpeed/CWV, GSC Links, anomaly detection, alerting externe | ❌ Absents |
| Schema validation runtime, meta A/B, image audit, canonical audit | ❌ Absents |
| AI Overviews / LLM citations / Helpful Content | ❌ Absents |

Cette ADR documente la décision architecturale pour combler les manques **sans réécrire l'existant**, **sans nouvelle dette technique**, et **avec un design DB lean** validé par l'utilisateur (*"on peut fusionner ou ajouter des colonnes au lieu de créer de nouvelles tables, ma DB est énorme pour rien — par contre pas de bricolage solution robuste"*).

## Décision

Implémenter le département SEO en **5 modules cloisonnés** (non 8 comme initialement proposé — Off-page externe et Outreach actif reportés en V2 budget débloqué) sur **8 semaines de chemin critique**, en réutilisant l'infrastructure existante au maximum.

### 1. Modules

| Module | Localisation | Stratégie |
|--------|--------------|-----------|
| 1 — Observability | `backend/src/modules/seo-monitoring/` | Wrapper sur services GSC/GA4 existants + nouveaux fetchers CWV / GSC Links |
| 2 — On-page intelligence | extension `backend/src/modules/seo/` + nouveaux services | Étend `internal-linking.service.ts`, ajoute `schema-validator`, `meta-ab-engine`, `image-seo-auditor`, `canonical-auditor` |
| 4 — Content ops | `backend/src/modules/seo-content-ops/` | Pure façade NestJS sur les 15 skills existants + editorial calendar |
| 5 — Intelligence | `backend/src/modules/seo-monitoring/` (sub-services) | Délègue ML à `ai-agents-python/` existant, alerting via queue `email` existante |
| 7 — GEO/AEO light | `backend/src/modules/seo-geo-aeo/` + extension `conseil-quality-scorer.service.ts` | E-E-A-T scoring local + Helpful Content audit + answer-engine format suggestions |

**Hors scope V1** : Modules 3 (Off-page externe payant), 6 (Outreach automation), 8 (International FR-FR uniquement), AI Overviews / LLM citation tracking (APIs payantes).

### 2. DB design — lean, 7 nouvelles tables au lieu de 15

Décision prise sur instruction utilisateur explicite *"fusionner ou ajouter des colonnes au lieu de créer de new tables"* + contrainte *"par contre pas de bricolage solution robuste"*.

**Time-series (4 tables séparées)** — non fusionnables, partitionnement mensuel obligatoire, indexes spécialisés par dimension :

- `__seo_gsc_daily(date, page, query, device, clicks, impressions, ctr, position)` PARTITION BY RANGE(date) MONTHLY
- `__seo_ga4_daily(date, page, channel, sessions, conversions, bounce_rate, avg_session_duration)` PARTITION BY RANGE(date) MONTHLY
- `__seo_cwv_daily(date, page, lcp, fid, cls, inp, ttfb)` PARTITION BY RANGE(date) MONTHLY
- `__seo_gsc_links_weekly(snapshot_date, source_domain, source_url, target_url, anchor_text)`

**Findings unifiés (1 table)** — au lieu de 5 tables `__seo_schema_violations`/`__seo_image_audit`/`__seo_canonical_audit`/`__seo_meta_experiments`/`__seo_internal_link_suggestions` :

```sql
CREATE TABLE __seo_audit_findings (
  id UUID PRIMARY KEY,
  audit_type ENUM ('schema_violation','image_seo','canonical_conflict','meta_experiment','internal_link_suggestion'),
  entity_url TEXT,
  severity ENUM,
  payload JSONB,
  detected_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ,
  fixed_at TIMESTAMPTZ
);
CREATE INDEX ON __seo_audit_findings (audit_type, entity_url);
CREATE INDEX ON __seo_audit_findings USING GIN (payload);
```

Robustesse : `audit_type` ENUM contraint les valeurs, schemas Zod par variant typent les `payload` côté API (cf. `packages/seo-types/src/onpage.ts` discriminated unions), GIN index permet requêtes performantes.

**Event log unifié (1 table)** — au lieu de 3 tables `__seo_anomalies`/`__seo_alerts_log`/`__seo_monitoring_runs` :

```sql
CREATE TABLE __seo_event_log (
  id UUID PRIMARY KEY,
  event_type ENUM ('anomaly_detected','alert_sent','ingestion_run_started','ingestion_run_completed','ingestion_run_failed','forecast_generated','digest_sent'),
  entity_url TEXT,
  severity ENUM,
  payload JSONB,
  created_at TIMESTAMPTZ,
  ack_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ
);
CREATE INDEX ON __seo_event_log (event_type, created_at);
CREATE INDEX ON __seo_event_log USING GIN (payload);
```

**Editorial calendar (1 table workflow)** — minimaliste, séparée car state machine ne fit pas en JSONB :

```sql
CREATE TABLE __seo_editorial_calendar (
  id UUID PRIMARY KEY,
  entity_id TEXT REFERENCES __seo_entity(entity_id),
  role ENUM ('R0','R1','R2','R3','R4','R5','R6','R7','R8'),
  scheduled_at TIMESTAMPTZ,
  state ENUM ('planned','brief_draft','brief_approved','in_progress','review','published','blocked','cancelled'),
  assignee TEXT,
  brief_id UUID,
  completed_at TIMESTAMPTZ
);
```

**Entity-level scores (0 nouvelle table — colonnes JSONB sur `__seo_entity_health` existant)** :

```sql
ALTER TABLE __seo_entity_health
  ADD COLUMN eeat_scores JSONB,            -- Phase 5 GEO/AEO
  ADD COLUMN helpful_content_audit JSONB,  -- Phase 5 GEO/AEO
  ADD COLUMN freshness_state JSONB,        -- Phase 3 Content ops
  ADD COLUMN onpage_audit_summary JSONB;   -- Phase 2 (aggrégat findings open par entité)
```

`__seo_entity_health` est déjà la table d'état actuel par entité (`entity_score`, `risk_flag`) — y ajouter les scores E-E-A-T / Helpful Content / freshness est sémantiquement cohérent (single source of truth).

**Bilan tables** : 7 nouvelles (4 time-series + audit_findings + event_log + editorial_calendar) au lieu de 15. Réutilisation + 4 colonnes JSONB sur table existante.

### 3. Stack technique

| Couche | Décision | Pourquoi |
|--------|----------|----------|
| Backend | NestJS modules (existant), 1 nouveau module + extensions services existants | Pas de refonte stack |
| Cron | BullMQ (existant, 4 queues actives) | Réutilisation `seo-monitor-scheduler.service.ts` |
| DB | Supabase Postgres + tsvector | pgvector reporté V2 (tsvector suffit pour Phase 1-5 internal linking) |
| Frontend | Remix SSR + shadcn/ui (47 composants existants) + **Recharts ^2.15** ajouté | Recharts compatible shadcn, ~150KB gzip, lib la plus stable charting React |
| ML/IA | `ai-agents-python/` (existant, 16 scripts) | Anomaly detection délégué à Python, gRPC ou subprocess |
| Email | `nodemailer 8.0.0` + queue BullMQ `email` (existant, 8 jobs) | Pas de webhook Slack ; alertes via email infra existante |
| Logging | pino + Loki (existants) | Audit trail dans `__seo_event_log` complète |
| Types | Nouveau `packages/seo-types/` | Zod schemas partagés backend + frontend, discriminated unions pour les payloads JSONB |

### 4. APIs externes — gratuit uniquement

Décision utilisateur : **0$/mo budget APIs**. Sources gratuites uniquement :

- Google Search Console API (Search Analytics + URL Inspection + Site Links)
- Google Analytics 4 Data API
- PageSpeed Insights API
- Chrome UX Report API (fallback PageSpeed)

**Reporté V2** (budget débloqué) : DataForSEO ($50-150/mo), Ahrefs ($500/mo), Hunter.io ($49/mo), Postmark ($15/mo), SerpAPI ($75/mo), Perplexity / ChatGPT APIs.

### 5. Périmètre data — 50k pages

Décision utilisateur : couverture totale (gammes ~230 + véhicules ~50k pages) dès Phase 1, pas démarrage gammes-only.

Implications :
- Partitionnement DB obligatoire (~30M rows/mois sur `__seo_gsc_daily`)
- Pagination GSC par préfixe URL (~90 min/run quotidien)
- GA4 sampling : segmentation par groupe URL pour éviter
- Vues matérialisées hebdo pour agrégations top-N

### 6. Dashboard

**Décision** : **dashboard unifié unique** (utilisateur = single dev, pas de stakeholders multiples), extension de la route Remix existante `frontend/app/routes/admin.seo-hub.monitoring.tsx` (534 lignes, déjà fonctionnelle avec 3 endpoints API consommés), avec 5 nouvelles sections via `Tabs` shadcn/ui (déjà installé) :

1. Overview (existant, gardé) : Crawl, Index changes, URLs at risk
2. Traffic (NOUVEAU) : Recharts timeseries 90j GSC + GA4
3. Pages (NOUVEAU) : tableau filtrable 50k pages, top winners/losers
4. Content ops (NOUVEAU) : editorial calendar + freshness queue
5. Intelligence (NOUVEAU) : anomalies récentes, log alertes, weekly digest preview
6. GEO/AEO (NOUVEAU) : E-E-A-T scores top pages, Helpful Content audit

### 7. Roadmap 8 semaines

| Phase | Module | Durée | Output |
|-------|--------|-------|--------|
| 0 | Foundations | 3 jours | Cette ADR + types package + runbook + recharts + env vars (PR monorepo #166) |
| 1 | Observability | 2 sem | GSC/GA4/CWV/Links daily ingestion + dashboard timeseries |
| 2 | On-page intelligence | 2 sem | Schema validation runtime + meta A/B + linking suggestions + image/canonical audit |
| 3 | Content ops | 1 sem | Façade skills + editorial calendar + freshness rotation |
| 4 | Intelligence (alerting) | 2 sem | Anomaly detection (Python) + email alerts + weekly digest |
| 5 | GEO/AEO light | 1 sem | E-E-A-T scoring + Helpful Content audit + answer-engine format |

Chaque phase = 1 PR monorepo dédiée + 1 runbook dans `.spec/runbooks/seo/` + tests + extensions dashboard.

### 8. Conventions ENV (réutilisation, cf. AP-11)

Pas d'invention de nouvelles conventions — les services existants lisent déjà :

| Var | Service consumer existant |
|-----|---------------------------|
| `GSC_CLIENT_EMAIL`, `GSC_PRIVATE_KEY` | `crawl-budget-audit.service.ts:208-216` |
| `GSC_SITE_URL` (fallback `SITE_ORIGIN` = `https://www.automecanik.com`) | `url-audit.service.ts:50` |
| `GA4_CLIENT_EMAIL`, `GA4_PRIVATE_KEY`, `GA4_PROPERTY_ID` | `url-audit.service.ts:50-60` |

Nouvelles variables uniquement quand zéro existante :

| Var | Rôle |
|-----|------|
| `SEO_MONITORING_ENABLED` | kill-switch global fetchers |
| `SEO_ALERTS_EMAIL_TO` | recipient alertes |
| `SEO_ALERTS_THRESHOLD_POSITION_PCT` | seuil régression positions (défaut 20) |
| `SEO_ALERTS_THRESHOLD_TRAFFIC_PCT` | seuil régression trafic (défaut 30) |

## Conséquences

**Positives** :

- Réutilisation infra existante à ~50-60% (pas de réécriture, pas de risque de régression)
- DB lean : 7 nouvelles tables au lieu de 15 grâce aux discriminated unions JSONB + ALTER TABLE
- Coût mensuel récurrent additionnel : 0$/mo
- Type safety end-to-end via `packages/seo-types/` (Zod) cohérente backend NestJS + frontend Remix
- Kill-switches partout (`SEO_MONITORING_ENABLED`)
- 4 ADRs supplémentaires prévues (1 par module majeur) : observability stack, internal-linking tsvector vs pgvector, intelligence alerting thresholds, GEO/AEO E-E-A-T local scoring

**Négatives / risques** :

- 8 semaines de chemin critique = 3-4 mois calendaires à temps partiel
- GEO/AEO local sans tracking externe LLMs : limites assumées (E-E-A-T scores locaux ≠ perception réelle Perplexity/ChatGPT). Documenté dans runbook.
- Volume 50k pages × 30 jours = ~30M rows/mois `__seo_gsc_daily` → partitionnement strict obligatoire, sinon performance dégrade
- Dépendance Google : si SA révoqué, fallback en `auth_failure` event sans crash, mais ingestion stoppe
- Recharts ajout : ~150KB gzip impact bundle frontend → mitigation lazy-load via Remix `Suspense`

**Neutres** :

- Aucun impact sur les pipelines content R0-R8 existants (les skills restent où ils sont, Module 4 fait juste façade NestJS)
- Skill `seo-vault-verify` (PR #159 + #164) conservé orthogonal — c'est de l'hygiène doc consultant, scope distinct du département SEO opérationnel

## Conformité règles vault

- **AP-10 (services <500 lignes)** : chaque service Phase 1-5 conçu pour rester <500 lignes ; sinon split par responsabilité (ex: `gsc-fetcher` ≠ `gsc-links-fetcher`)
- **AP-11 (verify existing first)** : conventions ENV, services à étendre, tables à réutiliser tous validés via `grep` du codebase avant proposition (cf. PR vault #66)
- **G2 (Zero Orphelin)** : aucune écriture dans `app/.local/governance-vault/` ; runbook dans `.spec/runbooks/seo/` (monorepo) + ADR ici (vault canon) + memory `feedback_verify_existing_first.md`
- **G4 (CI Read-Only)** : aucune action CI auto sur le vault ; manual setup Service Account documenté dans runbook §1-3

## Références

- Plan complet (validé utilisateur 2026-04-25) : `/home/deploy/.claude/plans/c-est-ca-votre-equipe-zippy-puzzle.md`
- PR Phase 0 : [ak125/nestjs-remix-monorepo#166](https://github.com/ak125/nestjs-remix-monorepo/pull/166)
- PR vault rule AP-11 : [ak125/governance-vault#66](https://github.com/ak125/governance-vault/pull/66)
- Runbook setup : `.spec/runbooks/seo/observability-setup.md` (monorepo)
- Memory feedback : `~/.claude/projects/-opt-automecanik-app/memory/feedback_verify_existing_first.md`
- ADRs précédents liés :
  - [[ADR-015-vault-single-source-of-truth]] — vault SoT
  - [[ADR-022-r8-rag-control-plane]] — précédent module modulaire
  - [[ADR-023-hook-layer-defense]] — defense in depth pattern
  - [[ADR-024-claude-session-log-pattern]] — observabilité session

## ADRs filles à venir (prévus)

- ADR-026 : seo-observability stack (détails fetchers GSC/GA4/CWV)
- ADR-027 : seo-internal-linking tsvector vs pgvector (justification non-pgvector V1)
- ADR-028 : seo-intelligence alerting thresholds + anomaly detection model
- ADR-029 : seo-geo-aeo E-E-A-T local scoring algorithm + signals

Chaque ADR fille = 1 PR vault dédiée, signed commit, en début de chaque phase.

---

_Créé : 2026-04-25 — Décision autonome utilisateur après audit codebase 4 Explore agents parallèles._
