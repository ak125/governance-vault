---
title: "Sentry+SOPS go-live PROD — 4 PRs livrées, observability complète"
date: 2026-05-06
type: session-trail
related_chantier: F
related_adr: ["ADR-021", "ADR-028", "ADR-030", "ADR-043"]
related_moc: ["MOC-Roadmap-2026"]
related_prs:
  - "ak125/nestjs-remix-monorepo#324"
  - "ak125/nestjs-remix-monorepo#327"
  - "ak125/nestjs-remix-monorepo#329"
  - "ak125/nestjs-remix-monorepo#334"
related_audit_trails:
  - "2026-05-06-signal-A-empirical-correction"
status: closed
session_closed_at: 2026-05-06
---

# Sentry + SOPS go-live PROD — session 2026-05-06

## Synthèse

Cette session prolonge l'audit-trail précédent
[[2026-05-06-signal-A-empirical-correction]] qui constatait que Sentry
était provisionné en **DEV uniquement** (encrypted DSN dans
`secrets/sentry.dev.sops.env` + pas encore wired dans le code).

Cette session **livre l'activation complète** : code wiring (instrument.ts,
SentryGlobalFilter decorator, frontend SDK), infrastructure SOPS+age
multi-recipient, déploiement preprod validé, extension PROD via tag push
et alert rules email.

**État final** : Sentry actif sur **les 4 projets** Sentry
(`automecanik-{backend,frontend}-{dev,prod}`), event capture validée par
3 events réels en preprod (issue `2a32cd25` "Invalid API key" ADR-028 surfacée),
PROD wiring confirmé par `window.ENV.VITE_SENTRY_DSN` populé sur
`https://www.automecanik.com/`, email alerts canoniques configurées.

## Décisions architecturales

### 1. SOPS + age vs GitHub Secrets — choix canonique

Le pattern initial proposé était GitHub Actions secrets (`SENTRY_DSN`,
`SENTRY_AUTH_TOKEN` via `secrets.*` dans workflows). Réfusé par
l'utilisateur (« on utilise pas github secret mais autre solution
meilleure »).

Comparaison faite et arbitrée vers **SOPS+age** :

| Critère | SOPS+age | GitHub Secrets | dotenvx | Doppler/Infisical | Vault |
|---------|----------|----------------|---------|-------------------|-------|
| Self-hosted | ✅ | ❌ | ✅ | ❌ | ✅ |
| Encrypted at rest in git | ✅ | n/a | ✅ | ❌ | ❌ |
| Audit via git log | ✅ | UI | ✅ | UI | UI |
| Multi-recipient | ✅ | ❌ | ⚠️ | ✅ | ✅ |
| Sans deps réseau au deploy | ✅ | ✅ | ✅ | ❌ | ❌ |
| Maturité 2026 | ✅ | ✅ | ⚠️ jeune | ✅ | ✅ |
| Complexité ops | Faible | Faible | Faible | Faible | **Élevée** |

Aligné mémoire `feedback_cron_vps_canon_pour_mono_vps_setup` — mono-VPS
self-hosted, no SaaS au deploy, no PAT cross-repo rotation.

### 2. Multi-recipient (dev_vps + runner_vps)

Plutôt que single-recipient, deux clés age :

- **`dev_vps`** (`age17p8cdc...`) — sur 46.224.118.55. **Triage**
  uniquement (cette VPS ne fait pas tourner le runtime). Permet à
  l'opérateur de `sops decrypt` localement sans SSH'er au runner.
- **`runner_vps`** (`age14v0s0qhn...`) — sur 49.12.233.2 (`hetzner-prod`,
  GitHub Actions self-hosted runner + container preprod port 3200 +
  container PROD port 80/443). **Décryption au déploy** via
  `sops exec-env` dans CI workflows.

Backup operator key (`owner_fafa`) **encore manquant** — SPOF si les 2 VPS
Hetzner partent simultanément. Prévu en follow-up : génération sur laptop
perso + Bitwarden backup + `sops updatekeys`.

### 3. Wrapper `sops exec-env` dans CI workflows

Pattern guarded shell-side dans `ci.yml` (preprod) et `deploy-prod.yml` :

```bash
SOPS_FILE="$GITHUB_WORKSPACE/secrets/sentry.{dev,prod}.sops.env"
AGE_KEY_FILE="${SOPS_AGE_KEY_FILE:-$HOME/.config/sops/age/keys.txt}"
if command -v sops >/dev/null 2>&1 \
   && [ -f "$SOPS_FILE" ] \
   && [ -r "$AGE_KEY_FILE" ]; then
  sops exec-env "$SOPS_FILE" 'docker compose ... up -d'
else
  echo "::warning::sops/secrets/key missing — Sentry SDK no-op"
  docker compose ... up -d
fi
```

Fallback canonique : si sops/age/secrets absents sur runner, deploy
**continue** sans Sentry (no-op SDK), avec annotation `::warning::`.
Observability ne bloque jamais un deploy.

### 4. Source `.env` avant `docker compose up` (PR #329 hotfix)

Bug surfacé pendant la session : `docker-compose.preprod.yml` utilise
`environment: - SUPABASE_URL` (bare), ce qui **override env_file** quand
le shell n'a pas la variable. CI's `env:` block fournit normalement les
SUPABASE_*, mais une rerun manuelle `sudo -u deploy ...` sans `env:` les a
strippées du container, déclenchant un cascade 401 "Invalid API key" sur
Supabase RPC. **Sentry l'a capturé en moins de 30s** — exactement la
valeur recherchée d'observabilité.

Fix : `set -a; . "$PREPROD_DIR/.env"; set +a` immédiatement après le
heredoc d'env file. Idempotent en CI, corrective pour reruns manuels.
Appliqué dans ci.yml et deploy-prod.yml.

## PRs livrées

| PR | Titre | État |
|----|-------|------|
| [monorepo #324](https://github.com/ak125/nestjs-remix-monorepo/pull/324) | feat(observability): Sentry wiring + SOPS+age secret management infra | ✅ merged |
| [monorepo #327](https://github.com/ak125/nestjs-remix-monorepo/pull/327) | feat(observability): activate Sentry on CI deploy via sops exec-env (PR-B) | ✅ merged |
| [monorepo #329](https://github.com/ak125/nestjs-remix-monorepo/pull/329) | fix(ci): source preprod .env in deploy step to prevent env stripping | ✅ merged |
| [monorepo #334](https://github.com/ak125/nestjs-remix-monorepo/pull/334) | feat(observability): extend Sentry+SOPS to PROD via deploy-prod.yml wrapper (PR-D) | ✅ merged |

Tag `v2026.05.06-sentry-prod` poussé 17:15 UTC → `deploy-prod.yml` run
[#25450146001](https://github.com/ak125/nestjs-remix-monorepo/actions/runs/25450146001)
completed/success.

## Validation empirique

| Surface | État | Evidence |
|---------|------|----------|
| DEV preprod (`http://49.12.233.2:3200`) | 🟢 Sentry actif | 3 events captés, issue [`2a32cd25`](https://auto-pieces-equipement.sentry.io/issues/?project=automecanik-backend-dev) "Invalid API key" surfaced — exactly the 401 cascade caused by hotfix #329 root cause, validates capture chain |
| PROD (`https://www.automecanik.com/`) | 🟢 Sentry actif | `curl` retourne `window.ENV = {"VITE_SENTRY_DSN":"https://1c22cd2869cce7328a65c998e88e2188@o4511342880555008.ingest.de.sentry.io/4511343650013264","SENTRY_ENVIRONMENT":"production"}` |
| Health endpoints | 🟢 OK | `/health` returns 200 sur preprod ET prod |
| Email alerts | 🟢 4 rules sur 4 projets | 2× default "high priority issues" + 2× custom "Email on first error PROD canonical" (level≥error, 30min throttle) |
| Notification destination | 🟢 IssueOwners → ActiveMembers fallback | `automecanik.seo@gmail.com` (sole org member) |

## Impact sur Plan F (Chantier F DevSecOps)

[[ADR-043-plan-F-devsecops-phase-1-cadre]] Sprint 1 inclut "Signal A
(error rate Sentry)" comme partie observability stack. Cette session
**débloque empiriquement** ce signal — Sentry était provisioné mais
inactif.

Conséquences pour Plan F :

- **Signal A maintenant mesurable** sur DEV et PROD. La query proposée
  dans ADR-043 (`event.type:error url:"/api/payments/*" url:"/panier/*"`)
  est désormais exécutable.
- Le script `scripts/observability/sentry-signal-a.sh` (livré PR-A #324,
  encore non-cron'd) peut être planifié sur 49.12.233.2 pour émission
  d'un JSON status horaire, qui devient la source de vérité du signal A
  pour les arbitrages sprint suivants.
- **NOT RED réaffirmé empiriquement** : 0 events PROD à go-live (uptime
  ~2 min au moment du curl validate), donc thresholds de surveillance
  futurs partent d'un baseline propre.

## Follow-ups documentés (non-bloquants pour clore cette session)

1. **`owner_fafa` age key** — élimine le SPOF 2-VPS Hetzner. Génération
   sur laptop opérateur + Bitwarden backup + `sops updatekeys -y` sur les 2
   `secrets/sentry.{dev,prod}.sops.env`.
2. **Source-map upload via sentry-cli post-deploy** — ajoute step CI qui
   upload les sourcemaps Sentry pour symboliser les stack traces (sans ça,
   les events frontend afficheront les noms minifiés). Pattern documenté
   dans [`docs/runbooks/sentry-vps-setup.md`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/docs/runbooks/sentry-vps-setup.md).
3. **Signal A cron** — `scripts/observability/sentry-signal-a.sh` à brancher
   en cron horaire sur 49.12.233.2 pour metering daily checkout error rate.
4. **Sentry mobile app** — install + push notifs PROD pour alertes
   temps-réel (alternative/complément aux emails).

## Lien runbook canon

Le runbook `docs/runbooks/sentry-vps-setup.md` (livré PR-A #324, étendu
PR-D #334) est la source canonique opérationnelle. Cet audit-trail décrit
**ce qui a été décidé et exécuté** ; le runbook décrit **comment opérer
au quotidien**.
