---
id: ADR-008
title: Agent Placement Rules (3 Zones)
status: accepted
date: 2026-02-04
decision_makers:
  - Architecture
  - Governance
supersedes: null
---

# ADR-008: Agent Placement Rules (3 Zones)

## Contexte

Bien que ADR-007 établisse que la localisation n'impacte pas les droits,
une organisation en zones reste utile pour:
- La planification opérationnelle
- L'isolation réseau
- La gestion des ressources
- Le monitoring

## Décision

### Les 3 Zones Officielles

```
┌─────────────────────────────────────────────────────────────┐
│                    ZONE 1: EXTERNAL                         │
│                    (Agents Untrusted)                       │
├─────────────────────────────────────────────────────────────┤
│  Localisation: Local machine, External VPS, GitHub Actions  │
│  Trust Level: untrusted                                     │
│  Output: report_only, bundle_only                           │
│  Exemples: Python Analysis (a1-a12), Fixproof (f0-f15)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Airlock Bundle
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ZONE 2: PRINCIPAL VPS                    │
│                    (Controlled Environment)                 │
├─────────────────────────────────────────────────────────────┤
│  Localisation: Principal VPS (backend services)             │
│  Trust Level: trusted (internal services)                   │
│  Output: report_only, rpc_only                              │
│  Exemples: SEO Monitor, Cache Warming, Metrics Processor    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ RPC Gate (observe)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ZONE 3: PRODUCTION                       │
│                    (Runtime - NO AI ACCESS)                 │
├─────────────────────────────────────────────────────────────┤
│  Localisation: Production runtime (Docker containers)       │
│  Trust Level: N/A (humans only)                             │
│  AI Output: FORBIDDEN                                       │
│  Accès: Via déploiement CI/CD uniquement                    │
└─────────────────────────────────────────────────────────────┘
```

### Règles de Placement par Type d'Agent

| Agent Category | Zone | Justification |
|----------------|------|---------------|
| BMAD Agents | External | Workflow local, pas d'accès serveur |
| Python Analysis | External | Sandboxed, report_only |
| Python Fixproof | External | Bundle_only via Airlock |
| Skills | External | Local IDE integration |
| Backend Services | Principal VPS | Accès DB/Redis requis |
| MCP Servers | External | Local tooling |
| GitHub Actions | External | CI/CD sandboxed |
| AI-COS L1/L2 | FORBIDDEN | Phase 0 only |
| AI-COS L3 | Principal VPS | Conditional (ADR-006) |

### Flux Inter-Zones

```
External ──[bundle]──► Airlock ──[PR]──► Human Review ──[merge]──► Git
                                                                    │
Principal ──[rpc]──► RPC Gate ──[audit]──► Database                │
VPS           │                                                     │
              └──[report]──► Logs/Metrics                          │
                                                                    │
Production ◄──[deploy]──────────────────────────────────────────────┘
(NO DIRECT AI ACCESS)
```

### Validation en CI

Les agents doivent déclarer leur zone dans leur fiche:

```yaml
# Dans AGENT-xxx.md
placement:
  zone: external | principal_vps | forbidden
  justification: "..."
```

CI vérifie:
1. Zone déclarée correspond au type d'agent
2. Output type compatible avec la zone
3. Aucun agent en zone "forbidden" n'est activé

## Conséquences

### Positives
- Organisation claire des agents
- Isolation réseau prévisible
- Monitoring par zone
- Compliance avec ADR-006 (Phase 1 restrictions)

### Négatives
- Overhead de documentation
- Rigidité potentielle pour cas edge

### Neutres
- Pas d'impact sur les droits (cf. ADR-007)

## Exceptions

Toute exception aux règles de placement nécessite:
1. Justification documentée
2. Approbation Architecture Team
3. Revue dans audit-trail

## Références

- ADR-006: Phase 1 Agent Activation Framework
- ADR-007: Location Independence Principle
- REG-001: Agent Registry

---

_Créé: 2026-02-04_
_Auteur: Claude (Governance Analyst)_
