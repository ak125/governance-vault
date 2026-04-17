# Implementation Plan: AI-COS Architecture (4 Steps)

> Plan d'implémentation en 4 étapes sur 10 semaines.

---

## Overview

| Step | Focus | Duration | Key Deliverables |
|------|-------|----------|------------------|
| 0 | Instrumentation & Contracts | 2 weeks | Types, RunStore, Tracing |
| 1 | Router Graph + 2 Skills | 2 weeks | LangGraph, rag_reindex, seo_audit |
| 2 | RAG V1 Stable | 2 weeks | Hybrid search, Safe reindex |
| 3 | SEO Audit + Role Enforcement | 2 weeks | CI validation, KPIs |
| 4 | MCP PR Automation | 2 weeks | Auto-PR, CI gates |

---

## Step 0: Instrumentation & Contracts (Semaines 1-2)

### Objectif
Établir les fondations avec des contrats typés et l'observabilité.

### Tâches

| Tâche | Livrable | Validation |
|-------|----------|------------|
| Créer `packages/contracts/` | Types JobEnvelope, GraphState, SkillIO | TypeScript compile |
| Créer `packages/observability/` | RunStore + métriques | Logs visibles |
| Ajouter tracing OpenTelemetry | Spans dans chaque service | Jaeger dashboard |

### Structure packages/contracts/

```
packages/contracts/
├── src/
│   ├── job.ts           # JobEnvelope, JobScope, JobConstraints
│   ├── graph-state.ts   # GraphState
│   ├── skill.ts         # SkillInput, SkillOutput, SkillManifest
│   ├── artifact.ts      # Artifact schema
│   ├── rag.ts           # RagDocument, TruthLevel, RagContext
│   ├── idempotency.ts   # IdempotencyConfig
│   └── index.ts         # Exports
├── package.json
└── tsconfig.json
```

### Critères de Succès

- [ ] 100% des types compilent sans erreur
- [ ] RunStore persiste les jobs en DB
- [ ] Traces visibles dans Jaeger/console
- [ ] Documentation des types générée

---

## Step 1: Router Graph Minimal + 2 Skills (Semaines 3-4)

### Objectif
Mettre en place le router LangGraph avec 2 skills fonctionnels.

### Tâches

| Tâche | Livrable | Validation |
|-------|----------|------------|
| Créer `packages/ai-orchestrator/` | RouterGraph de base | Flow compile |
| Créer `packages/skills/` | Registry + manifest | Skills listables |
| Implémenter `rag_reindex` skill | Reindex fonctionnel | Documents indexés |
| Implémenter `seo_role_audit` skill | Audit fonctionnel | Violations détectées |

### Structure packages/ai-orchestrator/

```
packages/ai-orchestrator/
├── src/
│   ├── router-graph.ts     # Main router
│   ├── nodes/              # Graph nodes
│   │   ├── parse-intent.ts
│   │   ├── check-budget.ts
│   │   ├── execute-skill.ts
│   │   └── handle-error.ts
│   ├── flows/              # Sub-flows
│   │   └── seo-audit.flow.ts
│   └── patterns/           # Reusable patterns
│       └── corrective-rag.ts
├── package.json
└── tsconfig.json
```

### Structure packages/skills/

```
packages/skills/
├── src/
│   ├── manifest.ts         # SkillManifest type
│   ├── registry.ts         # SkillRegistry class
│   └── skills/
│       ├── rag-reindex.skill.ts
│       ├── seo-role-audit.skill.ts
│       └── routes-sync.skill.ts
├── package.json
└── tsconfig.json
```

### Critères de Succès

- [ ] Graph route vers 2 skills correctement
- [ ] Skills exécutables via API REST
- [ ] Artifacts générés et persistés
- [ ] Logs de trace complets

---

## Step 2: RAG V1 Stable + Indexer (Semaines 5-6)

### Objectif
RAG local stable avec hybrid search et safe reindex.

### Tâches

| Tâche | Livrable | Validation |
|-------|----------|------------|
| Créer `packages/rag/` | Ingestion + retrieval | Search fonctionne |
| Hybrid search | Vector + BM25 | Score > 0.7 |
| Truth levels | L1-L4 tagging | Filtrage correct |
| Safe reindex | Atomic swap | Zero downtime |

### Structure packages/rag/

```
packages/rag/
├── src/
│   ├── ingestion/
│   │   ├── chunker.ts      # Document chunking
│   │   ├── embedder.ts     # Embedding generation
│   │   └── loader.ts       # Document loaders
│   ├── retrieval/
│   │   ├── search.ts       # Hybrid search
│   │   ├── rerank.ts       # Reranking
│   │   └── filters.ts      # Filter builders
│   ├── governance/
│   │   ├── versioning.ts   # Version management
│   │   ├── citation.ts     # Citation formatting
│   │   └── truth-level.ts  # Truth level utils
│   └── index.ts
├── package.json
└── tsconfig.json
```

### Performance Targets

| Metric | Target |
|--------|--------|
| Hybrid search p50 | < 100ms |
| Hybrid search p95 | < 200ms |
| Reindex 1k docs | < 60s |
| Min relevance score | 0.70 |

### Critères de Succès

- [ ] Hybrid search p95 < 200ms
- [ ] Truth levels filtrables via API
- [ ] Reindex sans interruption de service
- [ ] Citations formatées correctement

---

## Step 3: SEO Audit + Role Enforcement (Semaines 7-8)

### Objectif
Validation automatique des PageRoles avec CI enforcement.

### Tâches

| Tâche | Livrable | Validation |
|-------|----------|------------|
| Extraire SEO module | 4 sous-modules | Imports OK |
| Créer `packages/seo/` | Rules + validation | Audit passe |
| CI check PageRole | GitHub Action | PRs bloquées |
| Dashboard KPIs | Grafana panels | Métriques visibles |

### Structure packages/seo/

```
packages/seo/
├── src/
│   ├── roles/
│   │   ├── types.ts        # PageRole enum
│   │   ├── rules.ts        # Role-specific rules
│   │   └── validator.ts    # Role validator
│   ├── matrix/
│   │   ├── patterns.ts     # URL patterns
│   │   └── mapping.ts      # Pattern → Role mapping
│   ├── validation/
│   │   ├── audit.ts        # Full audit
│   │   ├── canonical.ts    # Canonical checker
│   │   └── structured.ts   # Schema.org checker
│   └── monitoring/
│       ├── kpis.ts         # KPI definitions
│       └── alerts.ts       # Alert rules
├── package.json
└── tsconfig.json
```

### CI Workflow Addition

```yaml
# .github/workflows/seo-check.yml
- name: PageRole Validation
  run: npm run seo:validate-roles

- name: Block if violations
  if: failure()
  run: |
    echo "PageRole violations detected!"
    exit 1
```

### Critères de Succès

- [ ] 0 violations critiques SEO en production
- [ ] CI bloque PR sans PageRole défini
- [ ] KPIs par rôle trackés dans Grafana
- [ ] Alertes configurées pour regressions

---

## Step 4: MCP PR Automation + CI Gates (Semaines 9-10)

### Objectif
Automatisation complète artifacts → PR avec governance.

### Tâches

| Tâche | Livrable | Validation |
|-------|----------|------------|
| PR automation | Artifacts → PRs | PRs créées auto |
| CI gates par type | Checks spécifiques | Gates passent |
| Auto-merge L1-L2 | Merge automatique | PRs mergées |
| Human review L4 | Draft PRs | Reviews requises |

### PR Rules Configuration

```typescript
const rules = [
  { type: 'migration', checks: ['sql-lint', 'dry-run'], autoMerge: true },
  { type: 'seo-fix', checks: ['seo-validate'], autoMerge: true },
  { type: 'content', checks: ['spell', 'plagiarism'], autoMerge: false },
  { type: 'code', checks: ['lint', 'type', 'test'], autoMerge: false },
];
```

### Critères de Succès

- [ ] 80% des artifacts génèrent une PR automatiquement
- [ ] 100% L4 content en draft PR avec review requise
- [ ] CI gates spécifiques par type d'artifact
- [ ] Temps moyen artifact → production < 1h (L1-L2)

---

## Métriques Globales

| Métrique | Baseline | Target | Step |
|----------|----------|--------|------|
| Job success rate | - | >95% | 1 |
| RAG p95 latency | - | <200ms | 2 |
| SEO violations | ~100 | <10 | 3 |
| Auto-merge rate | 0% | >60% | 4 |
| Time to production | Manual | <1h | 4 |

---

## Packages à Créer (Résumé)

```
packages/
├── contracts/              # Step 0
├── observability/          # Step 0
├── ai-orchestrator/        # Step 1
├── skills/                 # Step 1
├── rag/                    # Step 2
├── seo/                    # Step 3
└── mcp/                    # Step 4
```

---

## Risques et Mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| LangGraph learning curve | Delay Step 1 | Pair programming, documentation |
| Weaviate setup complexity | Delay Step 2 | Docker-compose ready, fallback to local |
| SEO module trop couplé | Delay Step 3 | Extraction progressive, feature flags |
| CI checks trop lents | Poor DX | Parallélisation, caching |

---

## Voir aussi

- [[ADR-006-ai-orchestrator-architecture]] - Décision architecturale
- [[02-ai-cos-contracts]] - Détails des contrats
- [[03-skills-registry]] - Registre des skills

---

_Créé: 2026-02-03 | Source: Architecture Report Section 11_
