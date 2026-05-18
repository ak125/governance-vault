---
name: supabase-management-token
description: Provisioning + règles strictes pour le secret SUPABASE_ACCESS_TOKEN consommé par la routine vault-supabase-cost-check (cost surface drift detection V1). Token Management API distinct de SUPABASE_ANON_KEY et SUPABASE_SERVICE_ROLE_KEY.
type: knowledge
status: canon
date: 2026-04-30
last_updated: 2026-05-18
related_adr: ["ADR-028", "ADR-034"]
related_knowledge: ["supabase-cost-surface-drift-v1"]
---

# Supabase Management API Token (`SUPABASE_ACCESS_TOKEN`)

## Pourquoi ce token

La routine `vault-supabase-cost-check` (workflow `.github/workflows/vault-supabase-cost-check.yml`) interroge 3 endpoints du Management API Supabase pour capturer un snapshot de la **cost surface** (plan tier + project list + per-project add-ons) et alerter sur toute mutation structurelle. Méthodologie détaillée dans [[supabase-cost-surface-drift-v1]].

Endpoints consommés (V1, vérifiés 2026-05-18) :

- `GET /v1/organizations/{slug}` — plan tier (`organizations:read`)
- `GET /v1/organizations/{slug}/projects` — project list (`organizations:read`)
- `GET /v1/projects/{ref}/billing/addons` — per-project add-ons (`projects:read`)

Le Management API est **distinct** de l'API REST des projets :

| Type | Usage | Stocké comme |
|---|---|---|
| `SUPABASE_ACCESS_TOKEN` | Management API (billing, usage, branches, projects) | `gh secret` vault uniquement |
| `SUPABASE_SERVICE_ROLE_KEY` | API REST (bypasse RLS) | `gh secret` monorepo (prod uniquement post-ADR-028 Option D) |
| `SUPABASE_ANON_KEY` | API REST (RLS-respecting) | `gh secret` monorepo + vault (preprod via Option D) |

## Provisioning (action manuelle utilisateur)

1. Aller sur https://supabase.com/dashboard/account/tokens
2. Créer un nouveau token nommé `vault-cost-check-readonly` avec **scope minimum strict** :
   - ✅ `organizations:read` — pour `/v1/organizations/{slug}` et `/v1/organizations/{slug}/projects`
   - ✅ `projects:read` — pour `/v1/projects/{ref}/billing/addons` (sans ce scope, le workflow obtient HTTP 403 sur les add-ons)
   - ❌ **Aucun scope write** (refuser explicitement `organizations:write`, `projects:write`, `secrets:*`, etc.)
3. Copier la valeur (affichée une seule fois)
4. Provisionner dans `ak125/governance-vault` UNIQUEMENT (via stdin, pas via `--body` pour éviter shell history) :
   ```bash
   printf '%s' '<TOKEN_VALUE>' | gh secret set SUPABASE_ACCESS_TOKEN --repo ak125/governance-vault
   ```
5. **NE PAS** provisionner dans `ak125/nestjs-remix-monorepo` ni dans aucun autre repo. Le monorepo n'a pas besoin du Management API.
6. Vérifier la provisioning :
   ```bash
   gh secret list --repo ak125/governance-vault | grep SUPABASE_ACCESS_TOKEN
   ```
7. Tester immédiatement (ne pas attendre le cron lundi suivant) :
   ```bash
   gh workflow run vault-supabase-cost-check.yml --repo ak125/governance-vault
   gh run watch --repo ak125/governance-vault
   ```

## Règles strictes (anti-leak)

- ❌ **Jamais log** dans les step outputs (workflow utilise `::add-mask::` pour forcer GitHub Actions à le masquer)
- ❌ **Jamais écrire** dans un artifact upload (workflow applique `jq walk` redact sur le pattern `token|secret|key|password|refresh|access` avant `actions/upload-artifact@v5`)
- ❌ **Jamais utiliser** dans le monorepo `nestjs-remix-monorepo` (vault-only par convention)
- ❌ **Jamais coller** dans une issue / PR description / commit message / chat assistant
- ✅ **Mask via `::add-mask::`** dès la première step du workflow consommateur
- ✅ **Scope minimum** (`organizations:read` + `projects:read`, jamais plus)
- ✅ **Provisioning via stdin** (`printf | gh secret set`), pas `--body` (shell history)
- ✅ **Rotation** : documenter dans audit-trail (date création + date rotation + raison)

## Rotation

En cas de suspicion de leak (ex : token collé en chat, commit, log non masqué) :

1. Aller sur https://supabase.com/dashboard/account/tokens
2. **Revoke** le token compromis (action irréversible)
3. Créer un nouveau token avec le même nom + même scope (`organizations:read` + `projects:read`)
4. `printf '%s' '<NEW_TOKEN>' | gh secret set SUPABASE_ACCESS_TOKEN --repo ak125/governance-vault`
5. Re-trigger le workflow via `gh workflow run vault-supabase-cost-check.yml --repo ak125/governance-vault` pour valider
6. Logger la rotation dans `ledger/audit-trail/YYYY-MM-DD-token-rotation.md` (date, raison, opérateur)

### Rotation pending — incident 2026-05-18

Le token initial provisionné le 2026-05-18T11:15:24Z a transité en clair dans un chat assistant lors du fix du workflow (endpoint inexistant). Standard : considérer compromis, rotation obligatoire dès que l'org owner est disponible. Workflow opérationnel en attendant (token toujours valide jusqu'à revoke explicite).

## Vérification automatique

Le workflow `vault-supabase-cost-check.yml` fail explicitement (no silent skip — governance-critical job) si :

- Le secret est absent (`echo "::error::SUPABASE_ACCESS_TOKEN secret missing"` + exit 1)
- N'importe lequel des 3 endpoints retourne un code non attendu :
  - `/v1/organizations/{slug}` : attendu 200 — sinon fail
  - `/v1/organizations/{slug}/projects` : attendu 200 — sinon fail
  - `/v1/projects/{ref}/billing/addons` : attendu 200 ou 403 (free-tier projects) — sinon fail
- Le schéma de réponse change (champs canoniques absents → fail propre, pas silent NaN)

## Références

- ADR-028 — `ledger/decisions/adr/ADR-028-preprod-supabase-isolation.md` (preprod isolation, cost-aware defense)
- ADR-034 — `ledger/decisions/adr/ADR-034-aicos-operating-contract.md` (3 axes Trigger/Execution/Evidence)
- Méthodologie : [[supabase-cost-surface-drift-v1]] (`ledger/knowledge/supabase-cost-surface-drift-v1.md`)
- Workflow consommateur : `.github/workflows/vault-supabase-cost-check.yml`
- Doc Supabase Management API v1 : https://api.supabase.com/api/v1/redoc
