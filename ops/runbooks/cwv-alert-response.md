---
type: runbook
status: canon
updated: 2026-05-14
related: [ADR-063, ADR-045, ADR-028]
---

# Runbook — CWV Alert Response (CrUX field)

> Réponse opérationnelle aux alertes Core Web Vitals émises par
> [[ADR-063-cwv-monitoring-prod-crux-api]]. **Latence intrinsèque CrUX 7 à
> 10 jours** : une alerte CrUX signale une régression déjà installée chez
> les utilisateurs, pas une régression instantanée.

## Vue d'ensemble

| Composant | Path | Rôle |
|-----------|------|------|
| **Service détection** | `backend/src/modules/seo-monitoring/services/crux-alerter.service.ts` | Évalue seuils absolus + Δ% origin-level |
| **State persistée** | Supabase `__seo_crux_alert_state` | OPEN / STILL_OPEN / RESOLVED |
| **Sinks** | Slack `#seo-alerts` + Sentry + Prometheus `crux_alert_total` | Multi-canal |
| **Source données** | Supabase `__seo_crux_field_history` | Timeseries hebdo p75 |
| **API source** | `chromeuxreport.googleapis.com /v1/records:queryHistoryRecord` | Read-only Google |
| **Endpoint inspection** | `GET /api/admin/seo-monitoring/timeseries/crux` | `IsAdminGuard` + RLS |

## Que signale une alerte CWV CrUX

**Une alerte CrUX = régression d'expérience page mesurée chez les utilisateurs
Chrome réels sur une fenêtre rolling 28 jours**. Elle est :

- **Field, pas synthetic** : reflète l'expérience réelle pondérée par le
  trafic, supérieure à PageSpeed lab.
- **Alignée avec Google Search Console > Expérience > Core Web Vitals** :
  ce qu'un opérateur voit dans GSC est produit à partir de cette même source.
- **Inertielle (7-10 jours)** : la fenêtre 28j lissée + publication hebdo
  signifient qu'une régression observée la semaine S a pu commencer plusieurs
  semaines en arrière. **N'utiliser jamais la première date de détection
  comme estampille de date de régression code** (canon
  `feedback_no_blind_trust_gsc_first_detection_date`).

## Niveaux et événements

| Niveau | Trigger | Sévérité | Délai escalade |
|--------|---------|----------|----------------|
| **WARN absolu** | p75 LCP > 2500 / INP > 200 / CLS > 0.1 | Slack OPEN | Acquit < 4h ouvré |
| **CRIT absolu** | p75 LCP > 4000 / INP > 500 / CLS > 0.25 | Slack OPEN + Sentry | Triage < 1h ouvré |
| **WARN Δ% (origin)** | Δp75 LCP ≥ +15% ou +200ms vs median(4 dernières périodes) | Slack OPEN | Acquit < 4h ouvré |
| **CRIT Δ% (origin)** | Δp75 LCP ≥ +30% ou +400ms idem | Slack OPEN + Sentry | Triage < 1h ouvré |
| **STILL_OPEN** | État WARN/CRIT persistant > 7 jours | Slack rappel hebdo | Revue scope incident |
| **RESOLVED** | Métrique repassée sous seuil (absolu ou Δ%) | Slack RESOLVED | Documenter cause racine si trouvée |

**URL-level (V1)** : alertes émises uniquement sur détecteur A absolu CRIT.
Δ% URL-level non émis en V1 (top-100 dynamique = trop volatil pour seuils
relatifs fiables — élargissement V2 après stabilisation baseline).

## Procédure de réponse (3 actions immédiates)

À exécuter dans l'ordre, **au maximum 15 minutes** entre la réception de
l'alerte Slack et la fin de l'action 3.

### Action 1 — Corréler avec le déploiement récent

```bash
# Lister les déploiements PROD des 30 derniers jours (fenêtre CrUX)
gh release list --repo ak125/nestjs-remix-monorepo --limit 30 \
  --json tagName,publishedAt,name | jq -r '.[] | "\(.publishedAt) \(.tagName) \(.name)"'

# Lister les merges sur main des 30 derniers jours (DEV preprod)
gh pr list --repo ak125/nestjs-remix-monorepo --state merged --limit 50 \
  --search "merged:>=$(date -d '30 days ago' +%Y-%m-%d)" \
  --json number,title,mergedAt,mergeCommit | jq -r '.[] | "\(.mergedAt) #\(.number) \(.title)"'
```

**Critère** : un déploiement avec touch sur frontend critique (`frontend/app/**`,
`frontend/app/components/**`, asset/CSS, polices, scripts tiers) dans la
fenêtre 7-30j → fortement suspect, passer Action 2.

Aucun déploiement frontend dans la fenêtre → cause non-code possible (réseau
CDN, dépendance tierce, change comportement Chrome). Passer Action 3.

### Action 2 — Vérifier le cache Edge Cloudflare

```bash
# Headers cache d'une URL touchée par l'alerte (CRIT par-URL)
URL="https://automecanik.com/pieces/exemple-touche"
curl -sI "$URL" -H "Cache-Control: no-cache" | grep -iE "cf-cache-status|age|cache-control|x-served-by"

# Si purge sélective requise (pas de mass purge canon `feedback_cf_purge_requires_warmup`)
bash scripts/ops/cloudflare-purge-by-pattern.sh \
  --pattern "/pieces/regression-prefix/*" \
  --max-urls 200 \
  --warmup
```

**Critère** : `cf-cache-status: MISS` répété ou `age` excessif → cache stale
ou éviction agressive en cause. Purge sélective + warmup, ré-observer 24h.

`cf-cache-status: HIT` normal et même URL renvoie LCP dégradé → la cause
est applicative (assets, JS hydration, CSS critical path). Passer Action 3.

### Action 3 — Décider : rollback, investigation, ou attente

| Signal Action 1 | Signal Action 2 | Décision recommandée |
|---|---|---|
| Déploiement frontend dans 7j + WARN/CRIT origin | Cache normal | **Rollback du tag PROD précédent** (procédure ci-dessous) |
| Déploiement frontend dans 7j + CRIT URL absolu sur 5+ URLs | Cache normal | **Rollback** (impact étendu) |
| Pas de déploiement frontend dans 30j + WARN origin isolé | Cache normal | **Investigation** (RUM Sentry, GA4, GSC) + STILL_OPEN attendu |
| WARN origin + saisonnalité connue | Cache normal | **Attente** (annoter Slack, ré-évaluer hebdo) |
| Indifférent | Cache stale ou éviction | **Purge CF sélective + warmup** + ré-observer 24-48h |

#### Procédure rollback PROD (canon `feedback_rollback_via_revert_pr_branch_protected`)

```bash
# 1. Identifier le tag précédent stable
gh release list --repo ak125/nestjs-remix-monorepo --limit 5

# 2. Ouvrir une revert PR (main protégé : pas de force-push)
gh pr create --repo ak125/nestjs-remix-monorepo \
  --base main \
  --title "revert: rollback to vX.Y.Z (CWV regression — ADR-063 alert)" \
  --body "Rollback automatique suite à alerte CrUX field. Voir #INCIDENT-XXX."

# 3. Merge PR (auto-merge si CI verte + branch protection respectée)
# 4. Tag v* nouveau pour déclencher deploy PROD
git checkout main && git pull
git tag vX.Y.Z+1 && git push origin vX.Y.Z+1
```

**Vérification post-rollback** :

- `GET /api/admin/seo-monitoring/cron/health` → `last_crux_run_at` < 24h
- Lire `__seo_crux_field_history` 7 jours après rollback → CrUX étant
  inertiel (7-10j), la métrique p75 ne reflétera la correction qu'à la
  publication de la période suivante. **Ne pas attendre confirmation CrUX
  immédiate** ; valider via :
  1. Métriques Prometheus runtime (TTFB, durée requête backend) — instantané
  2. RUM Sentry web-vitals — quasi-instantané
  3. Lighthouse synthetic sur 3-5 URLs touchées — < 1h
  4. CrUX → confirmation finale 7-10j plus tard

## Triage en cas d'incident

### Pas de fetch CrUX depuis > 48h

```bash
curl -s "https://dev.automecanik.com/api/admin/seo-monitoring/cron/health" \
  -H "Authorization: Bearer $ADMIN_JWT" | jq '.crux'
```

- `last_crux_run_at` > 48h → vérifier logs Loki `crux_fetch_*`
- Quota Google dépassé → métrique Prometheus `crux_fetch_total{status="429"}`
- API key révoquée → métrique `crux_fetch_total{status="401"}` ; rotation
  via Google Cloud Console, mettre à jour GH secret `CRUX_API_KEY` + redeploy
- BullMQ queue `seo-monitor` en panne → vérifier Redis + `bull-board` admin

### Alerte permanente non-recoverable

- Symptôme : `STILL_OPEN` ré-émis chaque semaine, aucun déploiement frontend
  dans la fenêtre, RUM Sentry stable, Lighthouse stable.
- Cause probable : changement Google (méthode de calcul CrUX, pondération
  device, mise à jour algo p75) — historique GSC/CrUX révèle souvent une
  cassure non-corrélée à notre code.
- Action :
  1. Vérifier annonces officielles `https://developer.chrome.com/blog/`
  2. Comparer avec d'autres sites concurrents (CrUX BigQuery dataset public)
  3. Si confirmé : annoter Slack + audit-trail vault + ajuster baseline
     (`crux_baseline_reset` event dans `__seo_event_log` avec justification)

### Origin `automecanik.com` retourne 404 CrUX

- Symptôme : `crux_404_sticky_origins` contient `https://automecanik.com`
  après 21 jours consécutifs 404.
- Cause possible : trafic Chrome insuffisant agrégé (très rare avec 30k+
  URLs indexées) OU bug normalisation origin (trailing slash, http vs https).
- Action :
  1. Tester manuellement : `curl -X POST "https://chromeuxreport.googleapis.com/v1/records:queryHistoryRecord?key=$CRUX_API_KEY" -H "Content-Type: application/json" -d '{"origin":"https://automecanik.com","formFactor":"PHONE","metrics":["largest_contentful_paint"]}'`
  2. Si la réponse contient `record.metrics` → bug de normalisation côté
     `CruxApiClient`, fix immédiat
  3. Si la réponse contient `urlNormalized` différent → utiliser cette
     valeur comme origin canonique
  4. Si la réponse retourne `NOT_FOUND` → escalade Sentry "origin missing
     from CrUX 21d+"

## Anti-patterns à rejeter

- ❌ **Rollback sur la seule base d'une alerte CrUX WARN** sans corréler
  avec déploiement ou autres signaux. La latence 7-10j rend les rollbacks
  isolés peu informatifs (la régression peut être antérieure de plusieurs
  semaines).
- ❌ **Mass purge Cloudflare** pour "réparer" une régression CWV — purge
  globale = stampede d'origine, dégrade temporairement la perf et n'aide
  pas (canon `feedback_cf_purge_requires_warmup`). Purges sélectives
  `--pattern` + `--max-urls` + `--warmup` uniquement.
- ❌ **Désactiver le cron CrUX** pour "calmer le bruit" — la régression
  est dans les données, pas dans le pipeline. Préférer ajuster les seuils
  via ADR de revue (revue planifiée 2026-08-14 dans ADR-063).
- ❌ **Annoncer "PROD prod fixed"** sur la base d'une seule métrique CrUX
  retombée — l'inertie 7-10j peut masquer une régression persistante.
  Attendre 2 périodes hebdo CrUX consécutives + signal RUM Sentry stable.

## Références

- [[ADR-063-cwv-monitoring-prod-crux-api]] — décision et critères
- [[ADR-045-seo-monitoring-cron-v0]] — cron `seo-monitor` parent
- [[ADR-028-preprod-supabase-isolation]] — Option D READ_ONLY gate
- Documentation CrUX API : `https://developer.chrome.com/docs/crux/api`
- Script purge CF : `scripts/ops/cloudflare-purge-by-pattern.sh`
- Mémoires canon : `feedback_no_blind_trust_gsc_first_detection_date`,
  `feedback_cf_purge_requires_warmup`,
  `feedback_rollback_via_revert_pr_branch_protected`,
  `feedback_slo_must_be_multi_source`.
