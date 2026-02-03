---
id: INC-2026-01-11
title: Production Crash - rm/ Module Import Error
severity: critical
status: closed
date_detected: 2026-01-11
date_resolved: 2026-01-11
duration: ~15 minutes
affected_services: [backend, frontend, api]
root_cause: DEV module deployed to PROD
---

# Incident INC-2026-01-11: Production Crash - rm/ Module

## Resume

Crash de production cause par le deploiement du module `rm/` qui importe
`@monorepo/shared-types`, un package non lie dans l'image Docker de production.

## Timeline

| Heure | Evenement |
|-------|-----------|
| T+0 | Push du code contenant rm/ sur main |
| T+2min | CI/CD declenche, build Docker |
| T+5min | Deploiement automatique en production |
| T+6min | Backend crash au demarrage |
| T+7min | Cloudflare retourne 521 (Web server is down) |
| T+10min | Detection et diagnostic |
| T+15min | Rollback execute |
| T+20min | Service restaure |

## Symptome

```
Error: Cannot find module '@monorepo/shared-types'
Require stack:
- /app/backend/dist/modules/rm/services/rm-listing.service.ts
```

Le conteneur Docker ne demarrait pas car le module rm/ tentait d'importer
un package non disponible dans l'environnement de production.

## Impact

| Metrique | Valeur |
|----------|--------|
| Duree d'indisponibilite | ~15 minutes |
| Utilisateurs affectes | Tous |
| Erreur visible | Cloudflare 521 |
| Transactions perdues | Aucune (pas de paiements en cours) |

## Cause Racine

1. Le module `rm/` a ete cree pour du developpement experimental
2. Il importe `@monorepo/shared-types` qui n'est pas lie dans le build Docker
3. Le push sur `main` a declenche le deploiement automatique
4. Aucune verification de l'import n'existait dans le pipeline CI

## Resolution

```bash
# Rollback immediat
git reset --hard 9b4d7ddd
git push --force origin main

# Declenchement rebuild avec code stable
git commit --allow-empty -m "chore: trigger rebuild"
git push origin main
```

## Actions Correctives

| Action | Statut | Responsable |
|--------|--------|-------------|
| Documenter rm/ comme DEV-only | Complete | ADR-004 |
| Ajouter verification CI imports | Planifie | DevOps |
| Creer ADR separation environnements | Complete | ADR-001 |
| Revue des modules experimentaux | Planifie | Architecture |

## Lecons Apprises

1. **Tout module DEV doit etre explicitement documente**
2. Le deploiement automatique sur main necessite des gates supplementaires
3. Les imports de packages internes doivent etre verifies dans CI
4. Un rollback rapide est essentiel (procedure documentee dans CLAUDE.md)

## Prevention Future

1. Classification obligatoire des modules (DEV/PREPROD/PROD)
2. CI gate pour detecter les imports non resolus
3. Tests de demarrage dans l'image Docker avant push
4. Revue periodique des modules experimentaux

## References

- ADR-001: Environment Separation
- ADR-004: rm/ Module Scope
- CLAUDE.md section "Incidents et Post-Mortems"

---
_Post-mortem redige: 2026-02-03_
_Incident clos: 2026-01-11_
