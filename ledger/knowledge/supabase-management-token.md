---
name: supabase-management-token
description: Provisioning + règles strictes pour le secret SUPABASE_ACCESS_TOKEN consommé par la routine vault-supabase-cost-check. Token Management API distinct de SUPABASE_ANON_KEY et SUPABASE_SERVICE_ROLE_KEY.
type: knowledge
status: canon
date: 2026-04-30
related_adr: ["ADR-028", "ADR-034"]
---

# Supabase Management API Token (`SUPABASE_ACCESS_TOKEN`)

## Pourquoi ce token

La routine `vault-supabase-cost-check` (workflow `.github/workflows/vault-supabase-cost-check.yml`) interroge le Management API Supabase (`https://api.supabase.com/v1/organizations/{org_ref}/billing/subscription`) pour mesurer le coût mensuel projeté et alerter en cas de dérive.

Le Management API est **distinct** de l'API REST des projets :

| Type | Usage | Stocké comme |
|---|---|---|
| `SUPABASE_ACCESS_TOKEN` | Management API (billing, usage, branches, projects) | `gh secret` vault uniquement |
| `SUPABASE_SERVICE_ROLE_KEY` | API REST (bypasse RLS) | `gh secret` monorepo (prod uniquement post-ADR-028 Option D) |
| `SUPABASE_ANON_KEY` | API REST (RLS-respecting) | `gh secret` monorepo + vault (preprod via Option D) |

## Provisioning (action manuelle utilisateur)

1. Aller sur https://supabase.com/dashboard/account/tokens
2. Créer un nouveau token nommé `vault-cost-check-readonly` avec scope minimum :
   - `organizations:read` (billing/usage org `fezyshchnnrwwpnzbcwb`)
   - **Aucun scope write** (refuser explicitement `organizations:write`, `projects:write`, etc.)
3. Copier la valeur (affichée une seule fois)
4. Provisionner dans `ak125/governance-vault` UNIQUEMENT :
   ```bash
   gh secret set SUPABASE_ACCESS_TOKEN --repo ak125/governance-vault --body '<TOKEN_VALUE>'
   ```
5. **NE PAS** provisionner dans `ak125/nestjs-remix-monorepo` ni dans aucun autre repo. Le monorepo n'a pas besoin du Management API.
6. Vérifier la provisioning :
   ```bash
   gh secret list --repo ak125/governance-vault | grep SUPABASE_ACCESS_TOKEN
   ```

## Règles strictes (anti-leak)

- ❌ **Jamais log** dans les step outputs (workflow utilise `::add-mask::` pour forcer GitHub Actions à le masquer)
- ❌ **Jamais écrire** dans un artifact upload (workflow utilise `jq walk` redact pour `token|secret|key|password|refresh` pattern avant `actions/upload-artifact@v4`)
- ❌ **Jamais utiliser** dans le monorepo `nestjs-remix-monorepo` (vault-only par convention)
- ❌ **Jamais coller** dans une issue / PR description / commit message
- ✅ **Mask via `::add-mask::`** dès la première step du workflow consommateur
- ✅ **Scope minimum** (`organizations:read` only)
- ✅ **Rotation** : à documenter dans audit-trail si rotation effectuée (date création + date rotation)

## Rotation

En cas de suspicion de leak :

1. Aller sur https://supabase.com/dashboard/account/tokens
2. **Revoke** le token compromis (action irréversible)
3. Créer un nouveau token avec le même nom + même scope
4. `gh secret set SUPABASE_ACCESS_TOKEN --repo ak125/governance-vault --body '<NEW_TOKEN>'`
5. Re-trigger le workflow `vault-supabase-cost-check` via `workflow_dispatch` pour valider
6. Logger la rotation dans `ledger/audit-trail/YYYY-MM-DD-token-rotation.md` (date, raison, opérateur)

## Vérification automatique

Le workflow `vault-supabase-cost-check.yml` fail explicitement si :

- Le secret est absent (`echo "::error::SUPABASE_ACCESS_TOKEN secret missing"`)
- L'endpoint retourne `4xx`/`5xx` (token invalide ou révoqué)
- Le schéma de réponse change (champ `.tier`/`.plan` absent → fail propre, pas silent NaN)

## Références

- ADR-028 (couche 6 cost monitoring) — `ledger/decisions/adr/ADR-028-preprod-supabase-isolation.md`
- ADR-034 (3 axes — Evidence) — `ledger/decisions/adr/ADR-034-aicos-operating-contract.md`
- Workflow consommateur : `.github/workflows/vault-supabase-cost-check.yml`
- Doc Supabase Management API : https://api.supabase.com/api/v1/redoc
- Mémoire `feedback_supabase_cost_traps.md` (utilisateur) — Compute Branching non couvert par Spend Cap
