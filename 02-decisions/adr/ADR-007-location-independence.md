---
id: ADR-007
title: Location Independence Principle (Règle Maître)
status: accepted
date: 2026-02-04
decision_makers:
  - Architecture
  - Governance
supersedes: null
---

# ADR-007: Location Independence Principle

## Contexte

Le système gère 140+ agents répartis sur plusieurs zones d'exécution:
- Local machine (développement)
- External VPS (agents untrusted)
- Principal VPS (backend services)
- GitHub Actions (CI/CD)

Une confusion récurrente existe entre **où un agent s'exécute** et **ce qu'il peut faire**.
Cette confusion mène à des discussions sans fin sur le placement plutôt que sur les droits.

## Décision

### Règle Maître (Golden Rule)

> **L'emplacement n'a AUCUNE importance. Seul compte le canal de sortie.**

```
┌─────────────────────────────────────────────────────────────┐
│                    RÈGLE MAÎTRE                             │
│                                                             │
│   La LOCATION d'un agent (local, VPS, GitHub) est          │
│   SANS IMPORTANCE pour la gouvernance.                      │
│                                                             │
│   Ce qui compte UNIQUEMENT:                                 │
│   → OUTPUT TYPE (report_only, bundle_only, rpc_only)        │
│   → WRITE TARGET (none, airlock, rpc_gate)                  │
│                                                             │
│   Git = vérité humaine validée                              │
│   Airlock = sas obligatoire                                 │
│   Agents = JAMAIS de write direct sur Git                   │
└─────────────────────────────────────────────────────────────┘
```

### Principes Dérivés

1. **Git est la Source de Vérité**
   - Seuls les humains (ou humains via PR approuvée) écrivent dans Git
   - Git représente la "vérité validée" du système

2. **Airlock est le Sas Unique**
   - Tout output d'agent vers Git passe par Airlock
   - Airlock produit des bundles, pas des commits directs

3. **Agents Sans Write Direct**
   - Aucun agent n'a de `git push` direct
   - Le canal de sortie détermine les droits, pas la localisation

### Classification des Canaux de Sortie

| Output Type | Description | Write Access |
|-------------|-------------|--------------|
| `report_only` | Rapports, logs, métriques | None |
| `bundle_only` | Bundles Airlock (PR candidates) | Via Airlock |
| `rpc_only` | Appels RPC contrôlés | Via RPC Gate |
| `deploy` | Déploiement (INTERDIT Phase 1) | Forbidden |

### Implications pour REG-001

Le registre des agents (REG-001) doit:
- Documenter `output_type` pour chaque agent
- Documenter `write_target` pour chaque agent
- La colonne `location` reste informative mais non-restrictive

## Conséquences

### Positives
- Fin des débats sur "où doit tourner cet agent"
- Focus sur les droits réels (canaux de sortie)
- Simplification des règles de gouvernance
- Cohérence avec Zero-Trust (ADR-002)

### Négatives
- Peut sembler contre-intuitif initialement
- Nécessite mise à jour de la documentation existante

## Références

- ADR-002: Airlock & Zero-Trust Agents
- ADR-009: Phase 1 Agent Activation Framework
- ADR-011: Remplacement OpenClaw par Claude API
- REG-001: Agent Registry

---

_Créé: 2026-02-04_
_Auteur: Claude (Governance Analyst)_
