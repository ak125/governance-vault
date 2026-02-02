---
id: DEC-001
title: "Hardening DEV / PREPROD / PROD"
status: implemented
date: 2026-02-02
decision_makers: ["@admin"]
category: security
related_incidents: ["INC-2026-001"]
execution_plan: "[[DEC-001-execution-plan]]"
---

# DEC-001: Hardening DEV / PREPROD / PROD

## Contexte

Le monorepo NestJS + Remix (~300k lignes) souffrait de pollution runtime :
- Modules DEV importés en PROD (RmModule crash incident 2026-01-11)
- Scripts OPS dangereux sans garde-fous (75+ fichiers backend/*.js)
- Fichiers CSV de production versionnés dans git
- .dockerignore incomplet (scripts/CSV embarqués en prod)

## Décision

Mettre en place une séparation stricte DEV / PREPROD / PROD via deux barrières :

1. **Barrière IMPORTS** : ESLint no-restricted-imports + CI check
2. **Barrière PACKAGING** : .dockerignore allowlist strict

## Conséquences

### Positives
- DEV CORE démarre toujours (24 modules essentiels)
- DEV FULL / PREPROD inclut le cockpit admin complet (35+ modules)
- PROD n'embarque JAMAIS les outils DEV
- Scripts OPS protégés par kill-switch
- CSV exclus du versionning

### Négatives
- Modules AI/RAG désactivés en PROD (fonctionnalités futures)
- 2 profils à maintenir (dev:core / dev:full)

## Critères de Succès

- [ ] Build PROD sans modules DEV
- [ ] CI bloque imports interdits
- [ ] Scripts OPS refusent d'exécuter en PROD sans flag explicite

## Implémentation

- **Phase P0** : Stop risques critiques ✅
- **Phase P1** : Rendre DEV incassable ✅
- **Phase P2** : Industrialiser OPS (TODO)

Voir [[DEC-001-execution-plan]] pour le détail des actions.

## Preuves d'Exécution

- Commit P0 : `7551ea3c`
- Commit P1.1-P1.3 : `b1ce836b`
- Commit P1.4-P1.5 : `397df387`

## Revue Planifiée

Date: 2026-03-02 (30 jours)

---

*Validée le 2026-02-02*
