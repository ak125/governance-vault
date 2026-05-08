---
date: 2026-05-08
type: audit-trail
related: [ADR-053, MOC-Planning-Live]
---

# 2026-05-08 — Planning Live Alerts (PR-3)

## What

PR-3 du système Planning Live (ADR-053) — Alerts + ADR promotion :

- `_scripts/planning/alerts.py` :
  - `compute_alert_targets()` : cooldown 24h + `mute_until` suppression
  - `send_alert_github_issue()` : `gh issue create` label=`planning-p0-stagnant` + dedup natif via existing-open-issue check (`gh issue list --search "<canonical_id> in:title"`)
  - `send_alert_email()` : SMTP fallback (TLS, env vars `SMTP_HOST`/`SMTP_PORT`/`SMTP_USER`/`SMTP_PASSWORD`/`SMTP_FROM`/`EMAIL_ALERT_TO`)
  - `fetch_closed_alert_issues()` : ack via close detection (`gh issue list --state closed`)
  - `fire_alerts()` orchestrator : GH Issues primary, email fallback, exit 0 sauf `--strict-alerts`
- 3 helpers ack persistence : `read_ack_block()` / `update_last_alert_at()` / `write_ack_update()`
- `sync_planning.py` wired : compute targets + fire + closed-issue ack merge + technical commit `chore(planning): ack update [no-hash-change]` (distinct des business updates I3)
- ADR-053 promu `status: proposed → accepted` (canon LIVE règle générale respectée)
- ADR-053 §6 finalisé : décision GitHub Issues primary + email SMTP fallback (cf. rationale)
- ADR-053 I1 + I5 + Decision §3 mis à jour (Paperclip → GH Issues + email)
- `planning_live_state` reste `observing`, `live_since: null` — système accepté mais en obs ; promotion `live` post +7j obs green via audit-trail dédié futur

Tests : 10/10 passing (5 cooldown/mute/dispatch Task 3.2 + 5 ack helpers Task 3.3).
Suite complète planning : 37 passing + 1 skipped (real_gh, GH_TOKEN-gated).

## Decision Paperclip vs GitHub Issues

Bascule de Paperclip (option (a) initial du plan) vers GitHub Issues (option retenue PR-3) :

- **Paperclip mode observation** chez l'opérateur ⇒ pas d'auto-action sur dashboard, ack structuré gaspillé. Token + URL = nouveau secret à gérer.
- **GitHub Issues** : cohérence SoT (vault + monorepo déjà sur GitHub), notification email + mobile push native (l'opérateur watch déjà le repo), ack via `gh issue close` (UX standard CLI ou bouton mobile), pas de nouveau secret (gh CLI scope `repo` couvre `issues:write`), dedup natif via existing-open-issue check (l'issue elle-même est le rate-limiter, pas besoin de cooldown 24h en mémoire).
- **Email SMTP** garde son rôle de fallback only (déclenché si `gh issue create` fail : rate limit, scope manquant, network).

## Verification

- pytest `_scripts/planning/tests/test_alerts.py` : 10/10 pass
- pytest full planning suite : 37 pass + 1 skip
- pre-commit G2 (orphans + broken wikilinks) green sur tous les commits PR-3
- `check-moc-integrity.py --strict` exit 0
- ADR-053 frontmatter `status: accepted`, `planning_live_state: observing`, `live_since: null`

## Provisioning différé

- `/etc/automecanik/planning.env` (SMTP secrets) : à créer manuellement par opérateur sur VPS DEV (sudo, hors scope agent). Sans ce fichier, fallback email silently skip (best-effort I5).
- Label `planning-p0-stagnant` sur `ak125/governance-vault` : à créer one-shot via `gh label create` (idempotent ; l'absence rend `gh issue create` fail → email fallback uniquement).
- VPS DEV venv + crontab `/etc/cron.d/planning-live` (PR-2 Task 2.9) : encore deferred manual one-shot post-merge.

Note : ces 3 items sortent du périmètre agent (sudo / system state). Sans eux, le système silently-degrade en mode best-effort (I5) — exit 0, log warnings, MOC reste à jour avec ack block vide.

## Next

+7j observation green sans incident (pas de spam d'issues, pas d'incident SMTP, pas de drift MOC vs snapshots) → audit-trail dédié promote :

- `planning_live_state: observing → live`
- `live_since: <ISO date>` (date du signoff Fafa)

Système alors LIVE canon ET LIVE opérationnel.

## Refs

- ADR-053 §Decision §3 (GH Issues + email best-effort), §I1 (SoT ranking), §I5 (alert mechanism détaillé), §6 (rationale décision)
- PR-1 #221 (foundation : ADR-053 + schemas + MOC seed + snapshots scaffolding)
- PR-2 #222 (sync engine : 5 modules + orchestrator + cron + 27 tests)
- Plan rev 8 : `/home/deploy/.claude/plans/mettre-en-place-un-shimmering-fern.md`
- `feedback_canon_rule_live_iff_adr_accepted.md` (canon LIVE rule respectée : status `accepted` ⇒ règle générale LIVE)
