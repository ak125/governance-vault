---
type: audit-trail
date: 2026-05-07
incident_severity: blocking
chantier: F (DevSecOps / sécurité prod) + side-effect A (Runtime)
status: fix_in_flight
related_prs: [339, 344, 351]
related_memories:
  - feedback_check_secret_propagation_when_adding_fail_fast
  - feedback_read_backend_before_modifying_ci
  - feedback_check_sops_encrypted_secrets_too
---

# Audit-trail — PR #339 deploy regression (SESSION_SECRET propagation)

## Synthèse

PR #339 (`chore(auth): session secret fail-fast in prod + random fallback in dev (Sprint 1)`, commit `6c7df152`, mergée 2026-05-06 18:03 UTC) a activé un fail-fast sur `SESSION_SECRET` (≥32 chars + non-placeholder) dans `backend/src/main.ts:102`, mais a touché **uniquement `main.ts` (1 fichier modifié, 41+/12-)**. La propagation infrastructure (CI workflow, docker-compose, GH secret) a été oubliée.

Conséquence : 5 deploys main consécutifs failed du 2026-05-06 18:03 UTC au 2026-05-07 ~12:25 UTC. Tag PROD impossible. Ship Sentry CSP fix (PR #344) bloqué en cascade.

## Timeline

| Heure UTC | Évènement |
|---|---|
| 2026-05-06 18:03 | PR #339 mergée → push main `6c7df152` → 1er deploy fail (run `25382...`) |
| 2026-05-06+ | 2 autres push main (commits non-secret-related) → fails identiques |
| 2026-05-07 11:40 | PR #344 (Sentry CSP) mergée → fail (run `25494784099`) — non-causal |
| 2026-05-07 12:16 | PR #346 (R1 micro-seo 1500-3000c) mergée → fail (run `25495187241`) |
| 2026-05-07 12:25 | Diagnostic complet : root cause confirmé `SESSION_SECRET MANQUANT` |
| 2026-05-07 ~13:00 | GH secret `PREPROD_SESSION_SECRET` créé via `openssl rand -base64 48` |
| 2026-05-07 ~13:05 | PR monorepo #351 ouverte (fix ci.yml + compose) |

## Root cause

### Chain causale

```
PR #339 main.ts:102
  if (process.env.NODE_ENV === 'production') {
    throw new Error(`SESSION_SECRET MANQUANT en production. ...`);
  }
              ▲
              │ trigger en runtime preprod parce que :
              │
Dockerfile:39+63               docker-compose.preprod.yml:9
  ENV NODE_ENV="production"      - NODE_ENV=production
              │                              │
              └──── override ─────►──────────┘
                            │
                            ▼
       Container preprod exécute en NODE_ENV=production
                            │
                            ▼
ci.yml:716                       ci.yml:732 heredoc
  env: NODE_ENV: preprod          .env contient SUPABASE_*, READ_ONLY,
       SUPABASE_URL: ...           RAG_SERVICE_URL — PAS SESSION_SECRET
                            │
                            ▼
                     SESSION_SECRET undefined
                            │
                            ▼
                 main.ts:102 throw → boot crash
                            │
                            ▼
        Health check `curl localhost:3200/health` unreachable
                            │
                            ▼
                   ci.yml job step FAILURE
```

### Ce qui n'a pas été fait dans PR #339

- ❌ `ci.yml` env block `SESSION_SECRET: ${{ secrets.* }}`
- ❌ `ci.yml` heredoc `.env.preprod` ligne `SESSION_SECRET=`
- ❌ `docker-compose.preprod.yml` listing `- SESSION_SECRET`
- ❌ Création GH secret `PREPROD_SESSION_SECRET`
- ❌ Test deploy preprod ON CETTE BRANCHE (le job `🧪 Deploy PREPROD` ne tourne que sur `push main`, pas sur PRs)

## Pourquoi le merge est passé

`ci.yml` job `deploy` a la condition :
```yaml
if: ${{ (github.ref == 'refs/heads/main') && github.event_name == 'push' }}
```

→ Le deploy preprod **ne tourne pas sur les PRs**. Tous les checks de protection branch passent (lint/typecheck/tests/security audit) mais aucun ne valide le boot du container avec la nouvelle ENV var. Le fail apparaît au push main suivant le merge.

C'est un trou structurel CI : pas de "deploy preview" pour les PRs touchant le boot. Note pour roadmap chantier F.

## Fix appliqué (PR monorepo #351)

```diff
# .github/workflows/ci.yml job deploy
+ SESSION_SECRET: ${{ secrets.PREPROD_SESSION_SECRET }}
  ...
  cat > "$PREPROD_DIR/.env" <<EOF
+ SESSION_SECRET=${SESSION_SECRET}
  ...

# docker-compose.preprod.yml
+ - SESSION_SECRET    # bare → inherit shell, pattern SUPABASE_URL
```

GH secret côté admin :
```bash
openssl rand -base64 48 | tr -d '\n' | gh secret set PREPROD_SESSION_SECRET --repo ak125/nestjs-remix-monorepo
# Verified: gh secret list | grep SESSION → PREPROD_SESSION_SECRET 2026-05-07
```

## Pourquoi pas SOPS

Pattern existant DEV preprod (verified 2026-05-07) :
- Secrets app (SUPABASE_*) → GH secrets directs → heredoc `.env.preprod`
- Secrets Sentry → SOPS `secrets/sentry.dev.sops.env` (établi PR-D #324, 2026-05-06)
- Secrets PROD → `~/production/.env` plain text sur VPS PROD (provisionné manuel)

→ SESSION_SECRET = secret app, suit pattern SUPABASE_* (GH secret), PAS pattern Sentry (SOPS). Aligné canon `feedback_no_bricolage_align_existing_contract`.

PROD inchangé : `~/production/.env` a déjà SESSION_SECRET (sinon `deploy-prod.yml:109 REQUIRED_VARS` aurait fail historiquement → pas le cas).

## Pourquoi pas revert PR #339

- PR #339 implémente STRIDE 03-sessions critique #3 (audit-trail vault `#163`/`#164`/ADR-043). Régression sécurité = inacceptable.
- Le code est correct, c'est l'oubli de propagation infra qui a cassé.
- Fix forward via PR #351 = restaure l'invariant fail-fast SANS rendre infra incohérente.

## Mesures préventives (futur)

1. **Memory `feedback_check_secret_propagation_when_adding_fail_fast.md`** créée 2026-05-07.

2. **Suggestion CI gate** (à proposer en ADR séparé) : workflow `secret-propagation-check` qui parse les `getOrThrow<string>` et `throw new Error(.*required)` du backend et croise avec `.env.example` + `ci.yml` + compose. Fail si décalage. Évite récurrence.

3. **Suggestion preprod boot smoke** sur PRs : faire tourner un `docker compose -f docker-compose.preprod.yml config --quiet` + boot ephemeral container avec env vars CI sur les PRs touchant `backend/src/main.ts`, `*.env*`, `docker-compose.*.yml`, `.github/workflows/ci.yml`. Détection structurelle vs aujourd'hui détection post-merge.

## Liens

- Commit fail-fast : [`6c7df152`](https://github.com/ak125/nestjs-remix-monorepo/commit/6c7df152)
- PR fix : [#351](https://github.com/ak125/nestjs-remix-monorepo/pull/351)
- PR Sentry CSP bloquée : [#344](https://github.com/ak125/nestjs-remix-monorepo/pull/344)
- Run failure exemple : [25495187241](https://github.com/ak125/nestjs-remix-monorepo/actions/runs/25495187241)
