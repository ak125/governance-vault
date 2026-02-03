# AI-COS Documentation (AI-Driven Company Operating System)

> **Version**: 1.0.0 | **Status**: CANON | **Date**: 2026-02-03
> **Description**: Systeme d'exploitation d'entreprise pilote par l'IA pour AutoMecanik

---

## Vision

AI-COS transforme AutoMecanik en une **AI-Driven Company** ou l'IA augmente (sans remplacer) les capacites humaines. L'objectif est d'automatiser les taches repetitives, d'ameliorer la prise de decision et de scaler les operations de 4M+ produits.

---

## Axiome Zero (INVIOLABLE)

```
+=====================================================================+
||                                                                     ||
||                L'IA NE CREE PAS LA VERITE.                         ||
||                                                                     ||
||   Elle produit, analyse, propose.                                   ||
||   La verite = validee par Structure + Humain.                      ||
||                                                                     ||
+=====================================================================+
```

---

## Index des Documents

### Fondations (Contrats)

| Doc | Titre | Description | Version |
|-----|-------|-------------|---------|
| [00-agent-model](./00-agent-model.md) | Agent Contract | Contrat universel pour tous les agents AI-COS | v1.5.0 |
| [01-skill-model](./01-skill-model.md) | Skill Contract | Contrat des skills MCP-Ready (Model Context Protocol) | v1.3.0 |
| [02-loop-engine](./02-loop-engine.md) | Flywheel ODACVLS | Moteur de boucle d'auto-amelioration avec LangGraph | v1.2.0 |

### Gouvernance & Memoire

| Doc | Titre | Description | Version |
|-----|-------|-------------|---------|
| [03-governance](./03-governance.md) | Governance Rules | Regles de gouvernance canoniques | v1.3.0 |
| [04-memory-model](./04-memory-model.md) | Memory System | Modele de memoire (court-terme, long-terme, partagee) | v1.0.0 |
| [99-golden-rules](./99-golden-rules.md) | Golden Rules | Les 10 regles d'or non-negociables | v1.0.0 |

### Systemes Techniques

| Doc | Titre | Description | Version |
|-----|-------|-------------|---------|
| [05-kpi-system](./05-kpi-system.md) | KPI System | Systeme de KPIs et alertes | v1.0.0 |
| [06-rag-system](./06-rag-system.md) | RAG System | Retrieval-Augmented Generation avec Truth Levels | v1.0.0 |

### Catalogues Phase 0

| Doc | Titre | Description | Version |
|-----|-------|-------------|---------|
| [10-task-catalog](./10-task-catalog.md) | Task Catalog | Catalogue des taches automatisables P0 | v1.0.0 |
| [11-agent-catalog](./11-agent-catalog.md) | Agent Catalog | Catalogue des agents AI-COS P0 | v1.0.0 |
| [12-dag-p0](./12-dag-p0.md) | DAG Phase 0 | Graphe de dependances pour l'implementation | v1.0.0 |

---

## Architecture AI-COS

```
+=========================================================================+
|                           AI-COS ARCHITECTURE                            |
+=========================================================================+
|                                                                          |
|   HUMAN CEO (Level 0)                                                    |
|        |                                                                 |
|        v                                                                 |
|   +----------------------+                                               |
|   |  Executive Board     |  IA-CEO, IA-CTO, IA-CPO, IA-CMO              |
|   |  (Level 1)          |  Decision strategique assistee                |
|   +----------+-----------+                                               |
|              |                                                           |
|              v                                                           |
|   +----------------------+                                               |
|   |  Leads Metiers       |  SEO Lead, Data Lead, Infra Lead...         |
|   |  (Level 2)          |  Pilotage domaine specifique                  |
|   +----------+-----------+                                               |
|              |                                                           |
|              v                                                           |
|   +----------------------+                                               |
|   |  Squads & Agents    |  Executeurs de taches                        |
|   |  (Level 3+)         |  Skills MCP, LangGraph flows                 |
|   +----------------------+                                               |
|                                                                          |
+=========================================================================+
```

---

## Flux de Donnees

```
MiniLo DECLENCHE -> LangGraph DECIDE -> Skills EXECUTENT -> RAG FOURNIT -> MCP GOUVERNE
```

### Pattern ODACVLS (Flywheel)

```
OBSERVE -> DETECT -> ANALYZE -> DECIDE -> VALIDATE -> ACT -> LEARN -> STORE
    ^                                                                    |
    +--------------------------------------------------------------------+
```

---

## Regles d'Or (Resume)

| # | Regle |
|---|-------|
| R1 | PAS D'INDICATEUR = SUPPRESSION |
| R2 | IA-CEO PROPOSE, HUMAN CEO DECIDE |
| R3 | DOUTE = BLOCAGE |
| R4 | PRODUCTION SANS VALIDATION = INTERDIT |
| R5 | AUCUN AGENT HORS HIERARCHIE |
| R6 | 1 CREATION = 1 FUSION OU SUPPRESSION |
| R7 | DIAGNOSTIC = MULTI-VALIDATION |
| R8 | CONTENU CRITIQUE = QUALITY OFFICER |
| R9 | KILL-SWITCH = HUMAN CEO EXCLUSIF |
| R10 | TRACABILITE = OBLIGATOIRE |

---

## Truth Levels (RAG)

| Level | Nom | Description | Auto-Publish |
|-------|-----|-------------|--------------|
| L1 | Constructeur | Donnees officielles (TecDoc, ETAI) | Oui |
| L2 | Expert Valide | Valide par expert humain | Oui |
| L3 | IA Genere | Genere par IA, non valide | Non |
| L4 | Brouillon | Draft, en attente review | Non |

---

## Domaines

```typescript
enum Domain {
  CORE = 'core',       // Fondations monorepo
  INFRA = 'infra',     // Docker, CI/CD, Perf
  DATA = 'data',       // Postgres, Redis, Supabase
  SEO = 'seo',         // SEO Enterprise
  RAG = 'rag',         // Knowledge & RAG
  CART = 'cart',       // Commerce & Checkout
  AICOS = 'aicos'      // AI-COS Governance
}
```

---

## Quick Start

1. **Comprendre les contrats**: Lire [00-agent-model](./00-agent-model.md) et [01-skill-model](./01-skill-model.md)
2. **Maitriser la gouvernance**: Lire [03-governance](./03-governance.md) et [99-golden-rules](./99-golden-rules.md)
3. **Implementer**: Suivre le DAG dans [12-dag-p0](./12-dag-p0.md)

---

## Liens Externes

- **Architecture Charter**: `.spec/00-canon/architecture.md`
- **Rules Projet**: `.spec/00-canon/rules.md`
- **RAG Knowledge**: `/opt/automecanik/rag/knowledge/`

---

_Ce document est la source de verite pour la documentation AI-COS._
_Derniere mise a jour: 2026-02-03_
