# ADR-006: AI Orchestrator Architecture (AI-COS Evolution)

## Metadata

| Champ | Valeur |
|-------|--------|
| ID | ADR-006 |
| Titre | AI Orchestrator Architecture |
| Status | Proposed |
| Date | 2026-02-03 |
| Decision Makers | @ak125 |
| Tags | architecture, ai-cos, langgraph, rag, seo |

---

## Contexte

Le monorepo AutoMecanik présente plusieurs problèmes architecturaux bloquants identifiés lors de l'audit du 2026-01-06:

### Structure Actuelle

```
/opt/automecanik/app/
├── backend/                 # NestJS API (40 modules)
│   ├── src/modules/        # Feature modules
│   ├── agents/             # IA agents (SEO keyword expert, SERP analyzer)
│   └── supabase/migrations/ # 50+ migrations
├── frontend/               # Remix SSR (169 routes)
├── packages/               # 9 shared packages
└── .spec/                  # Documentation canonique
```

### Top 10 Problèmes Bloquants

| # | Problème | Impact | Sévérité |
|---|----------|--------|----------|
| 1 | God Module SEO : 30+ services, 19 controllers | Maintenance impossible | CRITIQUE |
| 2 | Circular deps : Catalog↔Vehicles (ForwardRef) | Tests fragiles | CRITIQUE |
| 3 | God Services : VehiclesService 2,145 lignes | Untestable | HIGH |
| 4 | Cache fragmentation : 5 implémentations différentes | Incohérence TTL | HIGH |
| 5 | Pas de Skills Registry : Agents définis ad-hoc | Pas d'orchestration | CRITIQUE |
| 6 | RAG Proxy externe : Pas de version locale | Single point of failure | HIGH |
| 7 | Pas de JobEnvelope : Pas de contrat d'exécution | Pas de replay/audit | HIGH |
| 8 | KG↔Catalog couplage : Imports directs possibles | Violation boundaries | MEDIUM |
| 9 | Confusion R1/R4 : Routeur vs Expert mal délimité | Cannibalisation SEO | CRITIQUE |
| 10 | Pas de validation PageRole CI : Assignation manuelle | Erreurs de rôle | HIGH |

---

## Décision

Adopter une architecture d'orchestration AI en 5 couches avec la règle d'or:

> **MiniLo DÉCLENCHE → LangGraph DÉCIDE → Skills EXÉCUTENT → RAG FOURNIT → MCP GOUVERNE**

### Diagramme de Flux

```
                    ┌─────────────────────────────────────────────────────┐
                    │                    TRIGGERS                          │
                    │  (Cron, Webhook, Manual, Event)                      │
                    └──────────────────────┬──────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MINILO / WEAVER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Scope Calc   │  │ Job Envelope │  │ Idempotency  │  │ Dead Letter  │    │
│  │ (what to do) │  │ (contract)   │  │ (lock/check) │  │ (failures)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────┬────────────────────────────────────┘
                                         │ JobEnvelope
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            LANGGRAPH ROUTER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Intent Parse │  │ Route Select │  │ Budget Check │  │ Error Handle │    │
│  │ (NLU/rules)  │  │ (graph node) │  │ (tokens/$$)  │  │ (retry/skip) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────┬────────────────────────────────────┘
                                         │ GraphState
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SKILLS LAYER                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ rag_reindex  │  │ seo_audit    │  │ kg_diagnose  │  │ content_gen  │    │
│  │ (vector sync)│  │ (role check) │  │ (symptoms)   │  │ (AI write)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                          ↓ RAG Query                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         RAG SYSTEM                                    │  │
│  │  Hybrid Search | Truth Levels L1-L4 | Source Citation | Namespaces   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────┬────────────────────────────────────┘
                                         │ Artifacts
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MCP GOVERNANCE                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ PR Creation  │  │ CI Checks    │  │ Human Review │  │ Auto Merge   │    │
│  │ (artifacts)  │  │ (lint/type)  │  │ (L4 content) │  │ (L1-L2 only) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Packages à Créer

```
packages/
├── contracts/              # Types partagés IA (JobEnvelope, GraphState, SkillIO)
├── skills/                 # Skills unitaires avec registry
├── rag/                    # RAG standalone (ingestion, retrieval, governance)
├── ai-orchestrator/        # LangGraph flows
├── minilo-weaver/          # Triggers + job management
├── observability/          # Run tracking, metrics, traces
└── seo/                    # SEO extracted (roles, matrix, validation)
```

---

## Options Considérées

### Option A: Refactoring Incrémental (Rejeté)
- Corriger les modules existants un par un
- **Contre**: Ne résout pas le couplage fondamental, risque de régression

### Option B: Architecture Microservices (Rejeté)
- Séparer chaque composant en service indépendant
- **Contre**: Overkill pour la taille actuelle, complexité opérationnelle

### Option C: Architecture Modulaire + Orchestration (Choisi)
- Packages partagés avec contrats stricts
- Orchestration centralisée via LangGraph
- **Pour**: Balance entre découplage et simplicité

---

## Justification

1. **JobEnvelope**: Contrat unique d'exécution permettant replay, audit, idempotency
2. **Skills Registry**: Découverte et validation automatique des capacités
3. **RAG Local**: Élimination du SPOF externe, truth levels pour anti-hallucination
4. **LangGraph**: Orchestration déclarative avec état persistant
5. **MCP Governance**: Artifacts → PRs avec CI gates par type

---

## Conséquences

### Positives
- Testabilité: Chaque skill isolé et mockable
- Observabilité: Traces complètes de chaque job
- Évolutivité: Nouveaux skills sans modifier le router
- SEO: Validation automatique des PageRoles

### Négatives
- Migration: Effort initial significatif
- Apprentissage: Nouvelle stack (LangGraph, Weaviate)
- Temporaire: Période de coexistence ancien/nouveau

---

## Métriques Cibles

| Métrique | Baseline | Target | Timeline |
|----------|----------|--------|----------|
| Job success rate | - | >95% | Step 1 |
| RAG p95 latency | - | <200ms | Step 2 |
| SEO violations | ~100 | <10 | Step 3 |
| Auto-merge rate | 0% | >60% | Step 4 |
| Time to production | Manual | <1h | Step 4 |

---

## Plan d'Implémentation

Voir [[09-implementation-plan]] pour le détail en 4 steps (10 semaines).

| Step | Focus | Durée |
|------|-------|-------|
| 0 | Instrumentation & Contracts | 2 semaines |
| 1 | Router Graph + 2 Skills | 2 semaines |
| 2 | RAG V1 Stable | 2 semaines |
| 3 | SEO Audit + Role Enforcement | 2 semaines |
| 4 | MCP PR Automation | 2 semaines |

---

## Documents Associés

### Spécifications Techniques (06-knowledge/)
- [[02-ai-cos-contracts]] - JobEnvelope, GraphState, SkillIO schemas
- [[03-skills-registry]] - Skill manifest et registry
- [[04-rag-system]] - Chunking, hybrid search, citations
- [[05-langgraph-router]] - Router graph et flows
- [[06-minilo-weaver]] - Triggers et job management
- [[07-mcp-governance]] - PR rules et CI gates
- [[08-seo-charter]] - PageRole taxonomy et anti-confusion

### Règles (03-rules/technical/)
- [[seo-pagerole-rules]] - Validation PageRole
- [[ai-skill-antipatterns]] - Anti-patterns à éviter

---

## Critères de Succès

- [ ] 100% des types compilent (packages/contracts)
- [ ] RunStore persiste les jobs
- [ ] Graph route vers skills
- [ ] Hybrid search p95 < 200ms
- [ ] 0 violations critiques SEO
- [ ] CI bloque PR sans PageRole
- [ ] 80% artifacts → PR automatique

---

## Revue Planifiée

- **Date**: 2026-03-15 (après Step 2)
- **Critères**: RAG fonctionnel, 2 skills en production

---

_Créé: 2026-02-03 | Auteur: Claude Opus 4.5_
