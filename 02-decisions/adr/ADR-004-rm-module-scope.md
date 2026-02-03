---
id: ADR-004
title: rm/ Module Scope (DEV-only)
status: accepted
date: 2026-02-03
decision_makers: [Architecture Team]
supersedes: null
related_incident: INC-2026-01-11
---

# ADR-004: rm/ Module Scope

## Contexte

Le module `backend/src/modules/rm/` a ete cree pour des fonctionnalites de gestion
de listings/produits en mode experimental.

**Incident 2026-01-11**:
Le module rm/ a ete accidentellement deploye en production, causant un crash
car il importe `@monorepo/shared-types` qui n'est pas lie dans l'image Docker.

```
Error: Cannot find module '@monorepo/shared-types'
Require stack:
- /app/backend/dist/modules/rm/services/rm-listing.service.ts
```

**Impact**: Site down ~15 minutes (Cloudflare 521)

## Decision

Le module `rm/` est classifie comme **DEV-only**:

| Environnement | Statut |
|---------------|--------|
| DEV | Autorise |
| PREPROD | Interdit |
| PROD | Interdit |

### Regles

1. `rm/` ne doit **jamais** etre importe en PROD
2. Toute exception necessite une **nouvelle ADR** avec justification
3. L'import du module en PROD est considere comme un **incident**

### Mecanisme de protection

Le module rm/ doit etre exclu du build Docker production:
- Soit via `.dockerignore`
- Soit via configuration TypeScript conditionnelle
- Soit via guard au runtime

## Consequences

### Positives
- Clarification du scope du module
- Protection contre les deploiements accidentels
- Documentation de la decision

### Negatives
- Limitation de l'utilisation du module
- Necessite de maintenance de la separation

### Neutres
- Le module reste disponible en DEV pour experimentation

## Verification

```bash
# Verifier que rm/ n'est pas dans le build Docker
docker run --rm automecanik-app ls /app/backend/dist/modules/ | grep -c "rm"
# Resultat attendu: 0

# Verifier les imports dans le code compile
grep -r "rm-listing" backend/dist/ && echo "ALERT: rm/ detected in dist"
```

## Actions futures

Si le module rm/ doit etre promu en PROD:
1. Resoudre l'import `@monorepo/shared-types`
2. Creer ADR-00X documentant la promotion
3. Tests E2E complets
4. Revue securite

## References

- Incident INC-2026-01-11
- ADR-001 (Environment Separation)
- CLAUDE.md section "Modules en Developpement"

---
_Derniere mise a jour: 2026-02-03_
