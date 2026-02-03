---
id: ADR-001
title: Environment Separation (DEV / PREPROD / PROD)
status: accepted
date: 2026-02-03
decision_makers: [Architecture Team]
supersedes: null
---

# ADR-001: Environment Separation

## Contexte

Le projet AutoMecanik utilise plusieurs environnements avec des niveaux de risque differents.
L'incident du 2026-01-11 (crash production module rm/) a demontre les risques d'un manque
de separation claire entre les environnements.

**Probleme identifie**:
- Code destine au developpement deploye accidentellement en production
- Absence de regles formelles sur le perimetre de chaque environnement
- Confusion entre outils internes et fonctionnalites production

## Decision

Trois environnements distincts avec regles explicites:

| Environnement | Usage | Restrictions |
|---------------|-------|--------------|
| **DEV** | Experimentation, observation, outils internes | Aucune restriction technique |
| **PREPROD** | Validation fonctionnelle et securite | Donnees anonymisees, pas de paiements reels |
| **PROD** | Execution stricte, acces restreint | Enforcement actif, audit obligatoire |

### Regles de separation

1. Tout module DEV-only doit etre explicitement documente (ADR)
2. Les imports de modules DEV sont interdits en PROD
3. Les comportements `observe/enforce` sont lies a l'environnement:
   - DEV: `observe` par defaut
   - PREPROD: `observe` avec metriques
   - PROD: `enforce` apres validation

## Consequences

### Positives
- Risque reduit de deploiement accidentel de code DEV
- Tracabilite des decisions de scope
- Processus de promotion clair

### Negatives
- Complexite accrue de configuration
- Maintenance de documentation supplementaire

### Neutres
- Necessite une revue periodique des classifications

## Verification

```bash
# Verifier qu'aucun module DEV n'est importe en PROD
grep -r "@monorepo/shared-types" backend/dist/ && echo "ALERT: DEV import detected"
```

## References

- Incident INC-2026-01-11 (rm/ crash)
- ADR-004 (rm/ Module Scope)

---
_Derniere mise a jour: 2026-02-03_
