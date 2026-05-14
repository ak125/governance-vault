---
date: 2026-05-14
type: audit-trail
related: [ADR-063, ADR-045, ADR-028, ADR-044, ADR-050, ADR-058, INC-2026-005, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-14 — ADR-063 CWV Monitoring PROD via CrUX API (acceptance)

## What

Promotion de **[[ADR-063-cwv-monitoring-prod-crux-api]]** :

- `status: proposed → accepted`
- `decision_date: null → 2026-05-14`
- decision_maker : @fafa

L'ADR-063 entre en canon LIVE (`feedback_canon_rule_live_iff_adr_accepted`).
Le chantier implémentation monorepo (5 PRs atomiques séquentielles) est
**débloqué**.

## Why

Revue contradictoire des 3 options présentées dans ADR-063 § "Options
Considérées" :

- **Option A — CrUX History API (retenue)** : source officielle Google,
  alignée rapports Search Console *Expérience*, fenêtre 28j = baseline
  CWV officielle, pas de pré-requis sample top-1k stable
- **Option B — Étendre ADR-045 V0.D (PageSpeed cron complet)** : synthetic
  lab ≠ field, pré-requis `gsc-coverage-fetcher` bloquant, off-signal
  vs ranking
- **Option C — RUM Sentry agrégat client-only** : Sentry pas conçu pour
  servir de moteur analytique perf, divergence systémique avec rapports
  GSC garantie

Verdict : Option A retenue (4 rounds revue critique sur plan local + ADR
ont validé le design technique, notamment la PK `url_key` GENERATED, le
détecteur B Δ% origin-only V1, le `collectionPeriodCount: 40`, et
l'amendement par référence vs faux champ `superseded_by_partial`).

## How

PR vault `feat/adr-063-acceptance` (branche dédiée depuis `origin/main`
post-merge PR #271). 3 modifications atomiques :

1. `ledger/decisions/adr/ADR-063-cwv-monitoring-prod-crux-api.md`
   frontmatter patché : `status: accepted`, `decision_date: 2026-05-14`
2. `ops/moc/MOC-Decisions.md` table "ADR Actifs" : ligne ADR-063
   colonne Status `Proposed → Accepted`, texte mis à jour pour refléter
   le déblocage du chantier impl monorepo
3. Ce fichier audit-trail créé

### Self-review checklist 8 items (canon `feedback_vault_self_review_before_admin_merge`)

- [x] G3 signed : commit signé `vault-signing@automecanik.com` (vérifié
      `git log --show-signature -1` post-commit)
- [x] Frontmatter ADR-063 complet et cohérent (status `accepted` →
      decision_date renseigné non-null)
- [x] Pas d'autre fichier ADR touché (frontmatter ADR-045 reste intact,
      pattern atomique acceptance-only)
- [x] G2 zero orphan : `./_scripts/check-orphans.sh` lancé pré-push
- [x] Aucune référence à fichier non existant
- [x] G1 canon LIVE iff accepted : ADR-063 est désormais accepted → canon
      LIVE → chantier impl monorepo autorisé
- [x] G5 canon authoritative : ADR-063 référencé par MOC-Decisions
      (manuelle + auto-generated), MOC-AuditTrail (acceptance + proposal),
      MOC-Knowledge (runbook lié)
- [x] Verdict self-review : **APPROVE**

## What changes downstream

Avec `ADR-063.status == "accepted"` mergé sur `governance-vault/main` :

- **Canon LIVE** : la doctrine CWV Monitoring via CrUX devient canon
  courant. Toute régression future (PageSpeed synthetic ré-introduit dans
  cron daily ; détecteur B Δ% étendu URL-level V1 sans révision baseline ;
  PK directe sur table partitionnée sans `url_key` GENERATED ; phrasing
  over-claim "ce que Google ranking utilise" ; etc.) est régression.

- **Chantier monorepo débloqué** — 5 PRs atomiques séquentielles
  documentées dans `.claude/plans/adr-cwv-monitoring-prod-wobbly-swan.md`,
  séquence :
  1. Merge préalable branche `fix/gsc-5xx-30k-recovery-and-tactical-hardening`
     (canon `feedback_branch_scope_discipline` — branche dédiée depuis
     main propre obligatoire)
  2. Création branche `feat/adr-063-cwv-monitoring-crux-api` depuis main
  3. PR-2 monorepo : migration `__seo_crux_field_history` + `__seo_crux_alert_state`
     (avec `url_key TEXT GENERATED ALWAYS AS (COALESCE(url, '')) STORED`)
     + types Zod `packages/seo-types/src/crux.ts` + env vars
     (`CRUX_API_KEY` propagé partout)
  4. PR-3 monorepo : `CruxApiClient` + `CruxFieldFetcherService` (sampling
     top-100 dynamique + backoff sticky 1d→7d→30d)
  5. PR-4 monorepo : `CruxAlerterService` (détecteur A absolu + détecteur
     B Δ% origin-only V1 + state machine OPEN→STILL_OPEN→RESOLVED + sinks)
  6. PR-5 monorepo : wiring processor + endpoint admin 2 couches
     (`IsAdminGuard` + RLS) + extension `/cron/health`
  7. Validation preprod DEV 7j → tag PROD `v2.X.0` → 14j PROD silencieux
     avant status `accepted` finale post-runtime (canon
     `feedback_canon_rule_live_iff_adr_accepted` étendu à la phase
     runtime).

- **Runbook [[cwv-alert-response]]** entre en service dès PR-5 mergée
  (post-PROD). Ops opérationnel pour répondre aux alertes CrUX.

- **ADR-045** amends signalé (paragraphe daté corps déjà mergé via PR #271).
  Volet CWV synthetic V0.D officiellement résolu différemment. Reste
  d'ADR-045 (cron GSC/GA4/Links daily) inchangé.

- **Memory monorepo** à mettre à jour post-runtime PROD : nouveau memory
  feedback `feedback_crux_monitoring_canon_2026-05` synthétisant les
  4 rounds de revue (weekly granularité, faux champ `superseded_by_partial`
  rejeté, PK `url_key` GENERATED, `collectionPeriodCount: 40`, alerting
  V1 origin-only).

Aucune modification de runtime, hooks, ou code monorepo requise par cette
acceptance — la doctrine est déclarative. Les changements code arriveront
dans les 5 PRs atomiques séquentielles ci-dessus.

## Refs

- [ADR-063](../decisions/adr/ADR-063-cwv-monitoring-prod-crux-api.md) (Accepted 2026-05-14)
- [Audit-trail proposal](2026-05-14-adr-063-cwv-monitoring-prod-crux-api-proposal.md) (création `proposed` même journée, PR vault #271)
- ADR-045 [seo-monitoring-cron-v0](../decisions/adr/ADR-045-seo-monitoring-cron-v0.md) (amends sur volet CWV — paragraphe daté corps mergé via PR #271)
- ADR-028 [preprod-supabase-isolation](../decisions/adr/ADR-028-preprod-supabase-isolation.md) (Option D READ_ONLY gate réutilisé par CrUX fetcher)
- ADR-044 [seo-strategy-2026-roles-priority](../decisions/adr/ADR-044-seo-strategy-2026-roles-priority.md) (SEO Strategy 2026 master parent)
- ADR-050 [quality-history-and-drift-detection](../decisions/adr/ADR-050-quality-history-and-drift-detection.md) (cadre drift detection)
- ADR-058 [repository-control-plane](../decisions/adr/ADR-058-repository-control-plane.md) (overlay ownership Layer 2)
- Runbook [[cwv-alert-response]]
- Incident déclencheur : INC-2026-005 (GSC 5xx 30k pages recovery, audit-trail closure `2026-05-14-INC-2026-005-closure` séparé)
- Plan local implémentation : `.claude/plans/adr-cwv-monitoring-prod-wobbly-swan.md` (monorepo, 5 PRs atomiques)
- Mémoires canon : `feedback_canon_rule_live_iff_adr_accepted`,
  `feedback_branch_scope_discipline`,
  `feedback_no_questionnaire_propose_best`,
  `feedback_slo_must_be_multi_source`,
  `feedback_verify_existing_first`,
  `feedback_no_overclaim_security_words`.
