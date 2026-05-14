---
id: ADR-063
title: "CWV Monitoring PROD via CrUX API (field data 28j)"
status: accepted
date: 2026-05-14
decision_date: 2026-05-14
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-045"]
related_rules: ["G1", "G3", "Q1", "Q2"]
related_incidents: ["INC-2026-005"]
related_adr: ["ADR-028", "ADR-044", "ADR-045", "ADR-050", "ADR-058"]
implementation_status: not-started
---

# ADR-063 — CWV Monitoring PROD via CrUX API (field data 28j)

## Contexte

PROD ne dispose d'**aucune surveillance field user-facing** des Core Web Vitals
(LCP, INP, CLS). Les signaux existants sont structurellement insuffisants pour
détecter une régression d'expérience page côté utilisateurs réels :

| Signal | Nature | Limite |
|---|---|---|
| `bundle-stats` CI (`.github/workflows/perf-gates.yml`) | Proxy structurel code | Aucune corrélation avec l'expérience utilisateur réelle |
| `CwvFetcherService` (PageSpeed Insights API) | Synthetic lab Lighthouse | Variance ~13% flake observée, lab data ≠ field. **Exclu volontairement** du cron daily par [[ADR-045-seo-monitoring-cron-v0]] (sample top-1k stable manquant — V0.D future) |
| `web-vitals.client.ts` (Sentry / GA4) | RUM côté client | Émis mais **pas agrégé / pas alerté** côté backend ; difficile à interroger ou à corréler avec déploiements |
| GSC clicks / impressions (`__seo_gsc_daily`) | Signal business | Latence J-2 à J-7, secondaire pour la perf (canon `feedback_gsc_is_secondary_signal_only`) |

**Ce qui manque** : la mesure **field** alignée avec les rapports Core Web
Vitals dans Google Search Console (section *Expérience*). C'est cette mesure
que **Google Search utilise pour informer le facteur page experience** ;
elle vient du **Chrome User Experience Report (CrUX)** — dataset public
agrégé sur fenêtre glissante 28 jours, par origin et par URL.

### Incident déclencheur

`2026-05-14-INC-2026-005-closure` (audit-trail vault, en cours de merge sur main) (recovery GSC 5xx, 30k pages) a montré que
la régression a été détectée à **J-7** via GSC clicks plongeant, alors que
les utilisateurs Chrome la voyaient depuis plusieurs jours. Aucun signal
disponible côté backend pour alerter en amont. CrUX field aurait fourni
le signal manquant.

### Canon mémoires consultées

- `feedback_slo_must_be_multi_source` — SLO mono-source = faux sentiment de
  sécurité. CrUX field complète runtime + synthetic + edge + GSC pondérés.
- `feedback_ci_smoke_neq_runtime_monitoring` — CI smoke protège le code,
  CrUX field protège l'expérience runtime.
- `feedback_gsc_is_secondary_signal_only` — GSC = confirmation business
  (J-2 à J-7), jamais primaire. CrUX field = signal primaire user-facing.
- `feedback_no_blind_trust_gsc_first_detection_date` — Première détection
  CrUX ≠ date de régression code (fenêtre rolling 28j ; appliqué aussi à
  CrUX, voir Conséquences).

## Décision

Mettre en place un pipeline **CrUX History API → Supabase → alerting**
quotidien, intégré au cron `seo-monitor` BullMQ existant ([[ADR-045-seo-monitoring-cron-v0]]),
avec :

1. **Ingestion** quotidienne via CrUX History API
   (`POST /v1/records:queryHistoryRecord` avec `collectionPeriodCount: 40`,
   ~9 mois d'historique hebdomadaire). `queryRecord` (snapshot 28j daily) est
   **explicitement exclu en V1** pour éviter toute ambiguïté lecture/source.
   - **Origin** `https://automecanik.com` × form_factors `PHONE` + `DESKTOP`
     (2 calls/jour).
   - **Top-100 URLs PHONE dynamique** seedées depuis `__seo_gsc_daily`
     (rolling 28j clicks), recalculées chaque dimanche.
   - **Backoff sticky 404** : origin/URL absent CrUX → 1/jour puis 1/7j (J+3)
     puis 1/30j (J+21). Reset si signal observé.
   - Coût quota : ~102 calls/jour, < 1 RPM moyen sous quota 150 RPM.

2. **Stockage** dans deux nouvelles tables Supabase partitionnées mensuel :
   - `__seo_crux_field_history` : timeseries hebdo p75 LCP/INP/CLS/TTFB/FCP.
     PK `(origin, url_key, form_factor, collection_period_end_date)` où
     `url_key TEXT GENERATED ALWAYS AS (COALESCE(url, '')) STORED` — exigence
     PostgreSQL : les expressions sont interdites dans la PK d'une table
     partitionnée.
   - `__seo_crux_alert_state` : state machine alertes, même contrainte
     `url_key` pour éviter duplication sur origin-level (`url = NULL`).
   - Audit trail dans `__seo_event_log` existant (event_type
     `crux_fetch_run`), pas de nouvelle colonne structurée.
   - RLS : `SELECT authenticated`, `INSERT service_role` only.

3. **Détection + alerting** à double signal, fire-once :
   - **Détecteur A (absolu)** — seuils Google standards : LCP p75 > 2500
     WARN / > 4000 CRIT ; INP > 200 / > 500 ; CLS > 0.1 / > 0.25.
   - **Détecteur B (relatif)** — Δ% current period vs `median(trailing 4
     periods)`, **V1 origin-level uniquement** (URL-level Δ% trop noisy sur
     top-100 volatil ; URL-level limité au détecteur A absolu CRIT en V1).
     WARN si Δp75 LCP ≥ +15% ou +200ms absolu ; CRIT ≥ +30% ou +400ms.
   - **State machine** persistée : `OPEN` → `STILL_OPEN` (résumé hebdo si
     état > 7j) → `RESOLVED`. Évite spam quotidien sans perdre le signal
     long-running.
   - **Sinks multi-canal** : Slack webhook `#seo-alerts` + Sentry event +
     Prometheus counter `crux_alert_total{severity,metric,state}`.

4. **Exposition** :
   - `GET /api/admin/seo-monitoring/timeseries/crux` (params : `days`,
     `origin`, `url`, `formFactor`) — **2 couches** de sécurité :
     `@UseGuards(IsAdminGuard)` NestJS + RLS Supabase authenticated.
   - `GET /api/admin/seo-monitoring/cron/health` (étendu avec
     `last_crux_run_at`, `crux_404_sticky_origins`).

### Garde-fous canon

| Garde-fou | Implémentation |
|---|---|
| **READ_ONLY gate au processor** ([[ADR-028-preprod-supabase-isolation]] Option D) | Wrap CrUX fetch idem ADR-045 — court-circuit sans appel API/DB en preprod miroir prod |
| **Non-blocking `onModuleInit`** | Réutilise pattern existant `void warmer()` (canon `.claude/rules/backend.md` du monorepo) |
| **Failure isolée par cible** | `try/catch` par fetch URL → échec d'une URL ne court-circuite pas les 99 autres |
| **Pas de schema change `__seo_event_log`** | Type event `crux_fetch_run` injecté dans le ENUM existant, payload JSONB pour détails |
| **Secret propagation complète** | `CRUX_API_KEY` propagé `.env.example`, `docker-compose.yml`, `docker-compose.preprod.yml`, GH secret, `ci.yml` (canon `feedback_check_secret_propagation_when_adding_fail_fast`) |
| **Pas d'endpoint debug temporaire** | Tout via routes admin existantes étendues (canon `feedback_no_temporary_debug_endpoints`) |

## Options Considérées

### Option A — CrUX History API (retenue)

**Description** : ingestion quotidienne via `queryHistoryRecord`, granularité
hebdomadaire native, fenêtre rolling 28j. Origin + Top-100 URLs dynamique.

**Avantages** :
- Source officielle Google : alignement direct avec les rapports CWV /
  Search Console *Expérience* (ce que voit l'opérateur dans GSC est
  produit à partir du même dataset CrUX).
- Field data réelle (utilisateurs Chrome) → reflète l'expérience pondérée
  par la distribution de trafic, supérieur au synthetic per-URL.
- 1 call retourne 40 périodes hebdo (~9 mois) — drift detection gratuite,
  catch-up automatique si fetch raté N jours.
- Quota gratuit 150 RPM largement suffisant (~102 calls/jour).
- Pas de Service Account requis (API key simple, dataset public agrégé).

**Inconvénients** :
- Latence inhérente : 7 à 10 jours pour qu'une régression devienne visible
  (CrUX publie hebdo + données déjà lissées 28j en interne). Inacceptable
  comme **seul** signal ; acceptable comme **signal field aligné GSC**
  parmi un SLO multi-source.
- Dépendance Google API key (rotation, quota).
- Origin/URL doit avoir trafic Chrome suffisant pour figurer dans le
  dataset (URLs longue traîne → 404 CrUX, géré par backoff sticky).

### Option B — Étendre ADR-045 V0.D (PageSpeed cron complet)

**Description** : implémenter le plan ADR-045 V0.D — sample top-1k pages
stable + PageSpeed Insights synthetic per-URL daily.

**Avantages** :
- Réutilise `CwvFetcherService` existant.
- Granularité par-URL directe sans backoff sticky.

**Inconvénients** :
- **Synthetic lab data** ≠ field user — PageSpeed mesure Lighthouse depuis
  serveurs Google, pas l'expérience utilisateur réelle. Variance ~13%.
- Pré-requis sample top-1k stable = construction `gsc-coverage-fetcher`
  + définition critères stabilité = chantier amont coûteux non terminé.
- **Off-signal** : ne correspond pas à ce que Google Search lit pour le
  facteur page experience.
- Quota PageSpeed plus serré (25k requêtes/jour, 240/min) — 1k URLs
  daily = pression non négligeable.

### Option C — RUM client agrégat Sentry-only

**Description** : agréger côté backend les mesures déjà émises par
`web-vitals.client.ts` via Sentry distribution API.

**Avantages** :
- Pas de dépendance API externe Google.
- Couvre réellement les utilisateurs du site (pas seulement Chrome).

**Inconvénients** :
- Sentry distribution non conçu pour requêtes timeseries libres ; agréger
  par URL + jour côté backend = build d'un pipeline analytique.
- Distribution de devices/browsers ≠ pondération CrUX → divergence avec
  GSC garantie (le diagnostic croisé avec rapports GSC devient pénible).
- Désalignement avec le signal réel utilisé par Google Search.
- Aucune **rétrocompatibilité 9 mois** (Sentry retention typique 30-90j).

## Justification

**Option A > Option B** : la mesure qui informe le facteur page experience
côté Google Search est dérivée de CrUX, pas de PageSpeed synthetic. Aligner
notre monitoring sur la **même source** que GSC élimine les écarts
diagnostiques de moitié et supprime la dépendance à un sample top-1k
stable inexistant. L'inconvénient latence (7-10j) est inhérent au signal
field — il s'applique aussi à Option B.

**Option A > Option C** : Sentry est conçu pour collecter, pas pour servir
de moteur analytique perf. La divergence systématique avec les rapports
GSC rendrait le diagnostic croisé pénible à chaque incident.

**Canon `feedback_slo_must_be_multi_source`** : ce plan ne remplace pas
les autres signaux, il les complète. Le SLO global reste pondéré :
bundle-stats CI (code) + synthetic manuel (debug per-URL) + RUM Sentry
(visibilité instantanée user) + GSC (confirmation business) + **CrUX
field (signal page experience aligné Search Console)**.

## Conséquences

### Positives

- **Signal page experience direct**, aligné avec les rapports CWV / Search
  Console *Expérience*. Le diagnostic croisé GSC ↔ backend devient trivial.
- **Détection régression user-facing en ≤ 7 à 10 jours** sur origin + 100
  URLs top-trafic, vs J-7 (GSC seul, confirmation business uniquement) ou
  jamais (PageSpeed cron exclu d'ADR-045).
- **Catch-up automatique** : chaque fetch ramène 40 périodes hebdo ; un
  fetch raté N jours est rattrapé au suivant sans logique replay custom.
- **Pas de pré-requis bloquant** : origin-level couvre 100% du trafic, le
  top-100 dynamique GSC se construit en SQL window function sans nouveau
  service `gsc-coverage-fetcher`.
- **Réutilisation infra** : module `seo-monitoring`, BullMQ queue
  `seo-monitor`, table partition pattern `__seo_*` ADR-045, gate READ_ONLY
  ADR-028 Option D, audit `__seo_event_log`. Zéro nouveau module.

### Négatives

- **Dépendance Google CrUX API** : changement de schéma ou retrait du
  service casse l'ingestion. Mitigé par : Zod validation à la réception,
  métrique `crux_parse_error_total`, fallback dégradé (autres signaux du
  SLO multi-source continuent).
- **Latence intrinsèque 7-10j** : la fenêtre 28j lissée + publication
  hebdo rendent **impossible** une détection rapide via CrUX seul. C'est
  une caractéristique structurelle de la source, pas un défaut du pipeline.
  L'alerting CrUX doit être **complémentaire** des signaux à latence
  courte (RUM Sentry user-facing, synthetic on-demand), pas substitutif.
- **Première détection CrUX ≠ date de régression code** : la fenêtre
  rolling 28j signifie qu'une dégradation observée la semaine S a pu
  commencer plusieurs semaines en arrière. L'alerte ne doit jamais être
  utilisée comme estampille de date de régression — canon
  `feedback_no_blind_trust_gsc_first_detection_date` (appliqué à CrUX).
- **Origin/URL absent CrUX** = pas de signal (trafic Chrome insuffisant).
  Acceptable pour origin (30k+ URLs indexées garantissent présence),
  attendu pour longue traîne (géré par backoff sticky).

### Neutres

- 2 nouvelles tables Supabase, ~37k lignes/an cumulées (origin × 2 form
  factors × 52 + 100 URLs × 52). Négligeable comparé aux 30M lignes/mois
  GSC déjà en place.
- 1 nouveau secret `CRUX_API_KEY` (gratuit côté Google).
- Nouveau type event `crux_fetch_run` dans le ENUM `seo_event_type`.

## Critères de Succès

- [ ] CrUX field ingéré 14 jours consécutifs preprod sans miss > 48h
      (catch-up automatique vérifié).
- [ ] p75 LCP/INP/CLS lisibles pour origin PHONE + DESKTOP, 40 périodes
      hebdo (~9 mois) retournées par History API (`collectionPeriodCount: 40`).
- [ ] Top-100 URLs PHONE seedées dynamiquement depuis `__seo_gsc_daily`,
      recalculées chaque dimanche, logguées dans `__seo_event_log` pour
      audit de volatilité.
- [ ] Backoff 404 sticky vérifié sur ≥ 1 URL absente CrUX (logs Loki
      montrent escalade 1d → 7d → 30d).
- [ ] Alerte Slack `OPEN` reçue < 5 min après détection seuil absolu
      violé (test forcé).
- [ ] Alerte Slack `OPEN` reçue < 5 min après détection Δ% > 30%
      origin-level (test forcé via seed) ; URL-level Δ% **non alerté V1**.
- [ ] State machine `OPEN → STILL_OPEN (J+7) → RESOLVED` vérifiée sans
      spam quotidien.
- [ ] Endpoint admin `/timeseries/crux` documenté OpenAPI + 2 couches
      sécurité (`IsAdminGuard` + RLS authenticated).
- [ ] Patch ADR-045 (paragraphe daté section "Décision" /
      "Contrat CWV exclu") mergé même PR vault — frontmatter ADR-045
      inchangé (pas de `superseded_by_partial`, ce champ n'existe pas).
- [ ] Zéro régression `seo-daily-fetch` existant (durée run < 12 min
      vs 10 min avant).
- [ ] Coverage tests unit ≥ 85% sur les 3 services applicatifs.
- [ ] Migration UP + DOWN idempotentes (apply → rollback → reapply vert
      sur Supabase branch preview).
- [ ] Secret `CRUX_API_KEY` propagé partout (canon
      `feedback_check_secret_propagation_when_adding_fail_fast`).
- [ ] Runbook [[cwv-alert-response]] mergé même PR vault.
- [ ] Métriques Prometheus collectées : `crux_fetch_duration_seconds`,
      `crux_fetch_total{status}`, `crux_alert_total{severity,metric,state}`,
      `crux_404_sticky_total`.
- [ ] Post-PROD : 30 jours sans incident → status `accepted` + cron
      `vault-weekly-lint.yml` valide.

## Implémentation

Plan détaillé exhaustif : monorepo
`.claude/plans/adr-cwv-monitoring-prod-wobbly-swan.md` (5 PRs atomiques
séquentielles).

### Découpage PRs

| PR | Repo | Scope |
|---|---|---|
| PR-1 | `ak125/governance-vault` | ADR-063 (cet ADR) + patch ADR-045 corps + audit-trail + runbook |
| PR-2 | `ak125/nestjs-remix-monorepo` | Migration UP/DOWN `__seo_crux_field_history` + `__seo_crux_alert_state` + types Zod + env vars |
| PR-3 | monorepo | `CruxApiClient` + `CruxFieldFetcherService` (avec sampling + backoff sticky) — services dormants |
| PR-4 | monorepo | `CruxAlerterService` (détecteurs A + B + state machine + sinks Slack/Sentry/Prom) |
| PR-5 | monorepo | Wiring : processor step + endpoint admin + health étendu — preprod 7j → tag PROD `v2.X.0` → 14j PROD silencieux avant `accepted` |

### Pré-step

```bash
# Monorepo : branche dédiée depuis main propre, APRES merge gsc-5xx-recovery
git checkout main && git pull
git checkout -b feat/adr-063-cwv-monitoring-crux-api
```

### Schéma SQL pivot (extrait migration UP)

```sql
CREATE TABLE __seo_crux_field_history (
  origin TEXT NOT NULL,
  url TEXT NULL,
  url_key TEXT GENERATED ALWAYS AS (COALESCE(url, '')) STORED,
  form_factor TEXT NOT NULL CHECK (form_factor IN ('PHONE','DESKTOP','TABLET','ALL_FORM_FACTORS')),
  collection_period_start_date DATE NOT NULL,
  collection_period_end_date DATE NOT NULL,
  p75_lcp_ms INT,
  p75_inp_ms INT,
  p75_cls NUMERIC,
  p75_ttfb_ms INT,
  p75_fcp_ms INT,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source_api TEXT NOT NULL DEFAULT 'history' CHECK (source_api IN ('history','record')),
  PRIMARY KEY (origin, url_key, form_factor, collection_period_end_date)
) PARTITION BY RANGE (collection_period_end_date);
-- Partitions mensuelles + indexes + RLS séparés
```

## Anti-patterns à rejeter (futurs)

- ❌ Stocker en granularité **daily** alors que CrUX renvoie **weekly** —
  duplication x7 et incohérence sémantique. Le pipeline stocke ce que
  CrUX renvoie réellement (`collection_period_*_date` hebdo).
- ❌ Utiliser `queryRecord` (snapshot 28j daily) en V1 — produit un signal
  ambigu vs `queryHistoryRecord`. Réservé V2 si besoin de granularité
  intra-semaine ; alors `source_api='record'` permettra de distinguer.
- ❌ Inventer un champ `superseded_by_partial` dans le frontmatter
  ADR-045 — n'existe pas dans `_scripts/schemas/adr.schema.json`. Le
  signal "modification partielle" se fait via `amends: ["ADR-045"]` côté
  ADR-063 (cet ADR) et paragraphe daté dans le corps d'ADR-045.
- ❌ PK directe `(origin, COALESCE(url, ''), form_factor, ...)` sur table
  partitionnée — PostgreSQL refuse les expressions dans la PK d'une table
  partitionnée. Solution canonique : colonne générée `url_key` STORED.
- ❌ Z-score sur série déjà lissée 28j pour détection drift — variance
  écrasée par double lissage, faux négatifs. Méthode retenue : Δ% vs
  `median(trailing 4 periods)`.
- ❌ Alerter quotidiennement tant qu'un seuil reste violé — spam. State
  machine `OPEN → STILL_OPEN (J+7) → RESOLVED` requise.
- ❌ Étendre Détecteur B (Δ% relatif) au niveau URL en V1 — top-100 volatil
  saisonnalité = bruit alerting. URL-level limité à Détecteur A absolu
  CRIT en V1, élargissement V2 après stabilisation baseline.
- ❌ Mention "CrUX = ce que Google ranking utilise" — phrasing
  over-claim. Formulation canon : "field data CrUX utilisé par Google
  Search pour informer le facteur page experience, et aligné avec les
  rapports CWV / Search Console".
- ❌ Endpoint admin sécurisé par RLS seul — défense profondeur exige
  `@UseGuards(IsAdminGuard)` NestJS + RLS Supabase (2 couches).

## Revue Planifiée

**Date** : 2026-08-14 (3 mois après acceptance attendue)

**Critères de revue** :
- Volume d'alertes false-positive Δ% origin-level — si > 1/semaine en
  régime stable, ré-évaluer seuils.
- Couverture top-100 URLs effective (taux 200 vs 404 CrUX) — si < 60%,
  reconsidérer scope V1 (passer à top-50 stable).
- Latence détection effective vs incidents réels — si CrUX a manqué un
  incident détecté par RUM Sentry < 24h, valider que RUM reste le primaire
  user-facing pour ces cas.
- Faisabilité **V2** : étendre Détecteur B au niveau URL, ajouter
  annotations CrUX ↔ git commits, ajouter dashboard Grafana CWV.

## Références

- Plan détaillé monorepo : `.claude/plans/adr-cwv-monitoring-prod-wobbly-swan.md`
- Incident déclencheur : `2026-05-14-INC-2026-005-closure` (audit-trail vault, en cours de merge sur main)
- ADRs liés :
  - [[ADR-028-preprod-supabase-isolation]] — Option D READ_ONLY gate
  - [[ADR-044-seo-strategy-2026-roles-priority]] — Vague 0 pilotage
  - [[ADR-045-seo-monitoring-cron-v0]] — daily-fetch GSC/GA4/Links (amends)
  - [[ADR-050-quality-history-and-drift-detection]] — cadre drift detection
  - [[ADR-058-repository-control-plane]] — overlay ownership Layer 2
- Runbook ops : [[cwv-alert-response]]
- Mémoires canon : `feedback_slo_must_be_multi_source`,
  `feedback_gsc_is_secondary_signal_only`,
  `feedback_ci_smoke_neq_runtime_monitoring`,
  `feedback_no_blind_trust_gsc_first_detection_date`,
  `feedback_check_secret_propagation_when_adding_fail_fast`,
  `feedback_no_overclaim_security_words`,
  `feedback_verify_existing_first`.
- Documentation Google CrUX API : `https://developer.chrome.com/docs/crux/api`
  (à valider au moment de l'implémentation — pas hardcodé hors documentation).
