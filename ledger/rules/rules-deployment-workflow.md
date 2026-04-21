---
type: canon
status: canon
scope: deployment
updated: 2026-04-21
related_adrs: []
related_incidents: [INC-2026-007-false-prod-claim-on-main-merge]
---

# Rules — Deployment Workflow (DEV preprod vs PROD via tag)

> **Source de vérité** : triggers CI/CD au 2026-04-21
> **Version** : 1.0.0 | **Status** : CANON
> **Incident racine** : annonce erronée "déployé en prod" après merge PR #86 sur main (2026-04-21), corrigée explicitement par l'owner.

---

## D1 — Deploy Triggers

Deux environnements, deux triggers git **distincts et non substituables**.

| Trigger git | Workflow GitHub Actions | Image Docker | VPS cible | Environnement |
|-------------|-------------------------|--------------|-----------|----------------|
| `git push origin main` | [`.github/workflows/ci.yml`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/.github/workflows/ci.yml) job `deploy` (condition `github.ref == 'refs/heads/main'`) | `massdoc/nestjs-remix-monorepo:preprod` | DEV 46.224.118.55 | **DEV pré-prod** |
| `git push origin dev` | idem (condition inclut `dev`) | idem | idem | **DEV pré-prod** |
| `git push origin v*` (tag semver) | [`.github/workflows/deploy-prod.yml`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/.github/workflows/deploy-prod.yml) (`on.push.tags: 'v*'`) | promote `preprod` → `massdoc/nestjs-remix-monorepo:production` + tag version | PROD 49.12.233.2 | **PROD** |
| `workflow_dispatch` sur `deploy-prod.yml` | idem | idem | idem | **PROD** |

## D2 — Règle mnémonique

> **`main` = DEV. `v*` = PROD.**

Simple, sans exception. Si tu doutes, regarde le workflow file, pas la doc.

## D3 — Interdictions

- **NE PAS annoncer "déployé en prod"** après un simple merge sur main. C'est factuellement faux. Le merge main déclenche uniquement le deploy DEV.
- **NE PAS pousser directement sur `production` VPS**. Le seul chemin vers prod = tag `v*` ou `workflow_dispatch` manuel.
- **NE PAS utiliser `latest` tag** (commenté dans `build.yml:50`). Toujours `preprod` ou `production` ou semver explicite.

## D4 — Workflow nominal promote DEV → PROD

```bash
# 1. Merger PR sur main → déclenche deploy DEV automatique
gh pr merge {PR} --repo ak125/nestjs-remix-monorepo --squash --admin --delete-branch

# 2. Valider en DEV sur 46.224.118.55 (tests manuels + monitoring)

# 3. Créer un tag semver + push → déclenche deploy PROD
git checkout main && git pull
git tag v2.1.0
git push origin v2.1.0
```

Alternative UI : Actions → "Deploy PROD (via tag)" → Run workflow (utile si hotfix depuis un tag existant).

## D5 — Rollback

| Environnement | Procédure |
|---------------|-----------|
| **DEV** | `git revert HEAD && git push origin main` → redéclenche deploy DEV avec ancien code |
| **PROD** | `ssh 49.12.233.2` + `docker pull massdoc/nestjs-remix-monorepo:v2.0.9 && docker compose up -d` (substituer par le tag à restaurer) |

Ne jamais rollback PROD via `git revert + push main` — ça rollback DEV, pas prod.

## D6 — Sources de vérité

- Workflow files : `.github/workflows/ci.yml` (DEV) + `.github/workflows/deploy-prod.yml` (PROD)
- Dashboard : https://github.com/ak125/nestjs-remix-monorepo/actions
- Rules monorepo : `.claude/rules/deployment.md` (alignée sur cette règle canon)

## Mapping historique

| Date | Événement |
|------|-----------|
| 2026-04-21 | Incident annonce erronée "prod dans 10 min" après merge PR #86 → owner corrige → création de cette règle |
| 2026-04-21 | PR #91 monorepo corrige `.claude/rules/deployment.md` pour refléter cette réalité |

## Références

- ADR-012 (vault) — 3-VPS architecture (DEV/PROD/AI-COS split)
- Rules technical (`rules-technical.md`) — complément docker/caddy/redis
