---
date: 2026-05-14
type: audit-trail
related: [ADR-063, ADR-045, ADR-028, ADR-044, ADR-050, ADR-058, INC-2026-005, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-14 — ADR-063 CWV Monitoring PROD via CrUX API (création `proposed`)

## What

Création de **[[ADR-063-cwv-monitoring-prod-crux-api]] « CWV Monitoring PROD
via CrUX API (field data 28j) »** en `status: proposed` (decision_date `null`,
proposée par @fafa).

L'ADR définit un pipeline `CrUX History API → Supabase → alerting` quotidien
intégré au cron `seo-monitor` BullMQ existant ([[ADR-045-seo-monitoring-cron-v0]]) :

- **Ingestion** quotidienne via `POST /v1/records:queryHistoryRecord` avec
  `collectionPeriodCount: 40` (~9 mois hebdo). `queryRecord` snapshot 28j
  **exclu V1** pour éviter ambiguïté lecture/source.
- **2 cibles** : origin `https://automecanik.com` × `PHONE`+`DESKTOP` (2 calls)
  + Top-100 URLs PHONE seedé dynamiquement depuis `__seo_gsc_daily` (rolling
  28j clicks, recalculé chaque dimanche). Coût ~102 calls/jour < 1 RPM.
- **Backoff sticky 404** : origin/URL absent → 1d → 7d (J+3) → 30d (J+21).
- **Stockage** : 2 tables partitionnées mensuel, PK utilisant colonnes
  générées `url_key TEXT GENERATED ALWAYS AS (COALESCE(url, '')) STORED`
  (exigence PostgreSQL : pas d'expression dans la PK d'une table partitionnée).
- **Double détecteur** : (A) seuils Google absolus LCP/INP/CLS WARN+CRIT ;
  (B) Δ% current vs `median(trailing 4 periods)`, **V1 origin-level uniquement**
  (URL-level Δ% trop noisy ; URL-level = détecteur A absolu CRIT seul).
- **State machine** alertes `OPEN → STILL_OPEN (J+7) → RESOLVED`, fire-once,
  multi-sink Slack + Sentry + Prometheus.
- **Endpoint admin** sécurisé 2 couches : `@UseGuards(IsAdminGuard)` + RLS
  Supabase authenticated.

L'ADR-063 utilise le champ frontmatter `amends: ["ADR-045"]` pour signaler la
modification partielle d'ADR-045 (volet CWV) sans le superseder totalement.

## Why

`2026-05-14-INC-2026-005-closure` (audit-trail vault en cours de merge sur main, recovery GSC 5xx 30k pages) a révélé un
gap structurel : la régression d'expérience page n'a été détectée qu'à J-7
via GSC clicks plongeant. Aucun signal field user-facing disponible côté
backend ne permettait d'alerter en amont. Les utilisateurs Chrome la voyaient
plusieurs jours auparavant via le dataset CrUX que Google Search utilise pour
informer le facteur page experience.

Les signaux existants sont structurellement insuffisants :

| Signal | Limite |
|---|---|
| `bundle-stats` CI | Proxy code, pas user-facing |
| `CwvFetcherService` PageSpeed | Synthetic lab, variance 13%, **exclu du cron** par ADR-045 (sample top-1k stable manquant) |
| `web-vitals.client.ts` RUM Sentry | Émis mais pas agrégé / pas alerté backend |
| GSC clicks/impressions | Latence J-2 à J-7, secondaire (canon `feedback_gsc_is_secondary_signal_only`) |

ADR-045 V0.D prévoyait une résolution via `gsc-coverage-fetcher` + PageSpeed
synthetic per-URL daily. Approche off-signal (lab ≠ field) et coûteuse
(pré-requis sample top-1k stable inexistant). **CrUX field est strictement
supérieur** pour le signal page experience aligné Search Console :
- Source officielle Google = même dataset que `GSC > Expérience > CWV`
- Pas de pré-requis sample stable (origin couvre 100% du trafic)
- 1 call = 40 périodes hebdo (catch-up automatique, drift detection gratuite)

Canon mémoires consultées :
- `feedback_slo_must_be_multi_source` — CrUX = signal field aligné GSC,
  complète runtime + synthetic + edge + GSC (pas substitution).
- `feedback_no_blind_trust_gsc_first_detection_date` — appliqué aussi à
  CrUX : fenêtre rolling 28j → première détection ≠ date régression code.
- `feedback_check_secret_propagation_when_adding_fail_fast` — `CRUX_API_KEY`
  propagé partout (env, compose, ci.yml, GH secret).
- `feedback_no_overclaim_security_words` — endpoint admin sécurisé par
  2 couches (`IsAdminGuard` + RLS), pas "100% safe".
- `feedback_verify_existing_first` — aucune invention de champ frontmatter
  (`superseded_by_partial` n'existe pas dans `_scripts/schemas/adr.schema.json`,
  signal porté par `amends: ["ADR-045"]`).

## How

Création via PR vault `feat/adr-063-cwv-monitoring-crux-api` (branche dédiée
depuis `origin/main` propre).

Fichiers livrés dans cette PR vault :

1. `ledger/decisions/adr/ADR-063-cwv-monitoring-prod-crux-api.md` : créé
   en `status: proposed`, `decision_date: null`, `amends: ["ADR-045"]`,
   `related_adr: [ADR-028, ADR-044, ADR-045, ADR-050, ADR-058]`,
   `related_incidents: [INC-2026-005]`, `related_rules: [G1, G3, Q1, Q2]`.
2. `ledger/decisions/adr/ADR-045-seo-monitoring-cron-v0.md` : patch corps
   uniquement (paragraphe daté en blockquote inséré juste avant la section
   `## Décision`, à la fin de "Contrat CWV exclu volontairement"). **Frontmatter
   ADR-045 intact** : le champ `superseded_by_partial` n'existe pas dans le
   schema canon ; le signal sémantique est porté côté ADR-063 par `amends`.
3. `ledger/audit-trail/2026-05-14-adr-063-cwv-monitoring-prod-crux-api-proposal.md` :
   ce fichier.
4. `ops/runbooks/cwv-alert-response.md` : runbook ops 3 actions immédiates
   sur réception d'alerte CrUX (check changelog déploiement, check Edge cache
   Cloudflare, rollback si déploiement récent).

### Self-review checklist 8 items (canon `feedback_vault_self_review_before_admin_merge`)

- [x] **G3 (signed)** : commit prévu signé `vault-signing@automecanik.com`
      (sera vérifié `git log --show-signature -1` post-commit avant push)
- [x] **Frontmatter complet ADR-063** : id, title, status, date,
      decision_date (null pour proposed), decision_makers, amends,
      related_rules, related_incidents, related_adr, implementation_status
- [x] **Numérotation ADR-063 unique** :
      `ls ledger/decisions/adr/ | grep ADR-063 | wc -l == 1` (vérifié pré-commit)
- [x] **Frontmatter ADR-045 intact** : seul le corps est modifié
      (paragraphe daté), aucun champ frontmatter touché
- [x] **G2 (zero orphan)** : audit-trail lie à MOC-AuditTrail, ADR-063 lie
      à MOC-Decisions, runbook lie à ADR-063 — `./scripts/check-orphans.sh .`
      lancé pré-push
- [x] **Aucune référence à fichier monorepo non existant** : le plan
      `.claude/plans/adr-cwv-monitoring-prod-wobbly-swan.md` est référencé
      mais hébergé hors vault (plan local d'implémentation)
- [x] **G1 (canon LIVE iff accepted)** : ADR-063 est `proposed`, donc le
      chantier impl monorepo (PR-2 à PR-5) est gated sur acceptance
      ultérieure — conforme `feedback_canon_rule_live_iff_adr_accepted`
- [x] **Verdict self-review** : **APPROVE** (sous réserve `check-orphans.sh`
      vert + commit signé vérifié)

### MOC updates (à compléter dans la PR si nécessaire)

- `ops/moc/MOC-Decisions.md` : ligne ADR-063 dans section "ADR Actifs" en
  `proposed` (à vérifier convention exacte au moment du commit)
- `ops/moc/MOC-AuditTrail.md` : entrée audit-trail file (à vérifier)

## What happens next

- **Cette PR vault** mergeable dès self-review vert + check-orphans vert +
  signature OK. ADR-063 entre en `status: proposed` sur `main` du vault.
- **Tant que ADR-063 reste `proposed`** : aucun chantier monorepo n'est
  ouvert (canon `feedback_canon_rule_live_iff_adr_accepted` — chantier LIVE
  ssi ADR.status=accepted).
- **Décision attendue @fafa** : promotion `proposed → accepted` (ou
  `proposed → rejected` / `proposed → deferred`) après revue contradictoire
  des 3 options considérées (CrUX History, PageSpeed ADR-045 V0.D, RUM
  Sentry agrégat) — voir section "Options Considérées" de l'ADR-063.
- **Si promu `accepted`** : enchaînement PR monorepo séquentielles (PR-2
  types+migration, PR-3 ingestion, PR-4 alerting, PR-5 wiring) selon plan
  local `.claude/plans/adr-cwv-monitoring-prod-wobbly-swan.md`. Pré-requis :
  merge préalable branche actuelle `fix/gsc-5xx-30k-recovery-and-tactical-hardening`
  pour respect canon `feedback_branch_scope_discipline`.
- **Post-PROD** : 30 jours sans incident requis avant promotion `accepted`
  finale + check `vault-weekly-lint.yml`.

## Refs

- [ADR-063](../decisions/adr/ADR-063-cwv-monitoring-prod-crux-api.md) (proposed 2026-05-14)
- [ADR-045](../decisions/adr/ADR-045-seo-monitoring-cron-v0.md) (proposed 2026-05-07, amended par ADR-063 sur volet CWV)
- [ADR-028](../decisions/adr/ADR-028-preprod-supabase-isolation.md) (Option D READ_ONLY gate, réutilisé)
- [ADR-044](../decisions/adr/ADR-044-seo-strategy-2026-roles-priority.md) (SEO Strategy 2026 master)
- [ADR-050](../decisions/adr/ADR-050-quality-history-and-drift-detection.md) (cadre drift detection)
- [ADR-058](../decisions/adr/ADR-058-repository-control-plane.md) (overlay ownership Layer 2)
- Incident déclencheur : INC-2026-005 (GSC 5xx 30k pages, closure 2026-05-14)
- Runbook ops : [[cwv-alert-response]]
- Plan local implémentation : `.claude/plans/adr-cwv-monitoring-prod-wobbly-swan.md` (monorepo)
- Mémoires canon : `feedback_slo_must_be_multi_source`,
  `feedback_gsc_is_secondary_signal_only`,
  `feedback_no_blind_trust_gsc_first_detection_date`,
  `feedback_check_secret_propagation_when_adding_fail_fast`,
  `feedback_no_overclaim_security_words`,
  `feedback_verify_existing_first`,
  `feedback_canon_rule_live_iff_adr_accepted`,
  `feedback_branch_scope_discipline`,
  `feedback_vault_self_review_before_admin_merge`,
  `feedback_auto_vault_audit_trail_on_adr`.
