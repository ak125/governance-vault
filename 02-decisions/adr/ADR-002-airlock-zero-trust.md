---
id: ADR-002
title: Airlock & Zero-Trust Agents
status: accepted
date: 2026-02-03
decision_makers: [Architecture Team]
supersedes: null
---

# ADR-002: Airlock & Zero-Trust Agents

## Contexte

Le projet utilise des agents IA (Claude Code, agents autonomes) pour assister le developpement.
Ces agents peuvent generer du code, des configurations, et des modifications de fichiers.

**Probleme identifie**:
- Un agent peut produire du code non valide ou dangereux
- Aucun mecanisme de validation avant integration
- Risque d'injection de vulnerabilites

## Decision

Adoption du principe **Zero-Trust Agents**:

> **Tous les agents sont consideres comme non fiables par defaut.**

### Architecture Airlock

```
Agent Output → Airlock Bundle → PR Obligatoire → CI Gate → Merge
```

1. **Aucun agent n'ecrit directement** dans les repos critiques
2. Toute contribution passe par un **Airlock bundle**
3. **CI agit comme gate finale** avant tout merge

### Modes d'operation

| Mode | Comportement | Usage |
|------|--------------|-------|
| `disabled` | Aucune restriction | Tests locaux uniquement |
| `observe` | Log sans bloquer | Phase d'apprentissage |
| `enforce` | Bloque les violations | Production |

### Perimetre protege

- Monorepo principal (`backend/`, `frontend/`, `packages/`)
- Governance vault (`.local/governance-vault/`)
- Fichiers de configuration critiques (`.env`, `docker-compose.*.yml`)

## Consequences

### Positives
- Tracabilite complete des contributions agents
- Validation humaine obligatoire
- Reduction du risque d'erreur automatisee

### Negatives
- Friction dans le workflow de developpement
- Latence accrue pour les contributions agents

### Neutres
- Necessite une infrastructure de bundle/PR

## Implementation

Voir `RpcGateService` dans `backend/src/security/rpc-gate/` pour l'implementation existante
du controle d'acces aux fonctions RPC.

## References

- ADR-003 (RPC Governance)
- CLAUDE.md section "AI-COS Governance"

---
_Derniere mise a jour: 2026-02-03_
