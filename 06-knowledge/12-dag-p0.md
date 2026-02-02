# AI-COS DAG Phase 0 (Dependances)

> **Version**: 1.0.0 | **Status**: CANON | **Date**: 2026-01-27

## Objectif

Definir le graphe de dependances (DAG) pour l'implementation d'AI-COS Phase 0.

---

## DAG Global Phase 0

```
                              START
                                |
                                v
                    +------------------------+
                    |  00-agent-model.md     |
                    |  (Agent Contract)      |
                    +------------------------+
                                |
            +-------------------+-------------------+
            |                   |                   |
            v                   v                   v
+-------------------+  +-------------------+  +-------------------+
| 01-skill-model.md |  | 03-governance.md  |  | 04-memory-model.md|
| (Skill Contract)  |  | (Rules)           |  | (Memory System)   |
+-------------------+  +-------------------+  +-------------------+
            |                   |                   |
            +-------------------+-------------------+
                                |
                                v
                    +------------------------+
                    |  02-loop-engine.md     |
                    |  (Flywheel ODACVLS)    |
                    +------------------------+
                                |
                                v
                    +------------------------+
                    |  05-kpi-system.md      |
                    |  (Metrics & Alerts)    |
                    +------------------------+
                                |
            +-------------------+-------------------+
            |                   |                   |
            v                   v                   v
+-------------------+  +-------------------+  +-------------------+
| 10-task-catalog   |  | 11-agent-catalog  |  | 99-golden-rules   |
| (Tasks P0)        |  | (Agents P0)       |  | (Commandements)   |
+-------------------+  +-------------------+  +-------------------+
            |                   |
            +-------------------+
                    |
                    v
            +-------------------+
            | 12-dag-p0.md      |
            | (This file)       |
            +-------------------+
                    |
                    v
                  DONE
```

---

## Schema DAG Node

```yaml
DAGNode:
  id: string                  # Unique node ID
  name: string                # Display name
  type: NodeType              # spec | task | agent | milestone
  status: NodeStatus          # pending | in_progress | completed | blocked

  dependencies:               # Nodes that must complete first
    - node_id: string
      type: DepType           # hard | soft

  outputs:                    # What this node produces
    - artifact_id: string
      type: ArtifactType

  validation:                 # How to validate completion
    criteria: string[]
    automated: boolean
```

---

## Enums

```typescript
enum NodeType {
  SPEC = 'spec',           // Specification document
  TASK = 'task',           // Implementation task
  AGENT = 'agent',         // Agent creation
  MILESTONE = 'milestone'  // Phase marker
}

enum NodeStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  BLOCKED = 'blocked'
}

enum DepType {
  HARD = 'hard',  // Must complete before
  SOFT = 'soft'   // Should complete before
}
```

---

## DAG Nodes Phase 0

### Specifications (Docs)

```yaml
Nodes:
  - id: "spec.agent.model"
    name: "Agent Model Specification"
    type: spec
    status: completed
    file: "00-agent-model.md"
    dependencies: []
    outputs:
      - artifact_id: "schema.agent.contract"
        type: schema
    validation:
      criteria:
        - "Schema YAML valide"
        - "Types TypeScript definis"
        - "Exemple concret inclus"
      automated: false

  - id: "spec.skill.model"
    name: "Skill Model Specification"
    type: spec
    status: completed
    file: "01-skill-model.md"
    dependencies:
      - node_id: "spec.agent.model"
        type: hard
    outputs:
      - artifact_id: "schema.skill.contract"
        type: schema
    validation:
      criteria:
        - "Schema YAML valide"
        - "MCP compatible"
        - "Exemples concrets"
      automated: false

  - id: "spec.loop.engine"
    name: "Loop Engine Specification"
    type: spec
    status: completed
    file: "02-loop-engine.md"
    dependencies:
      - node_id: "spec.agent.model"
        type: hard
      - node_id: "spec.skill.model"
        type: hard
    outputs:
      - artifact_id: "schema.loop.contract"
        type: schema
    validation:
      criteria:
        - "Phases ODACVLS definies"
        - "Triggers documentes"
        - "Anti-hallucination actif"
      automated: false

  - id: "spec.governance"
    name: "Governance Rules"
    type: spec
    status: completed
    file: "03-governance.md"
    dependencies:
      - node_id: "spec.agent.model"
        type: soft
    outputs:
      - artifact_id: "rules.governance"
        type: documentation
    validation:
      criteria:
        - "7 regles immutables"
        - "16 regles IA"
        - "Kill-switch defini"
      automated: false

  - id: "spec.memory.model"
    name: "Memory Model Specification"
    type: spec
    status: completed
    file: "04-memory-model.md"
    dependencies:
      - node_id: "spec.agent.model"
        type: hard
    outputs:
      - artifact_id: "schema.memory"
        type: schema
    validation:
      criteria:
        - "Short-term defini"
        - "Long-term defini"
        - "Shared defini"
        - "Tables SQL"
      automated: false

  - id: "spec.kpi.system"
    name: "KPI System Specification"
    type: spec
    status: completed
    file: "05-kpi-system.md"
    dependencies:
      - node_id: "spec.agent.model"
        type: hard
      - node_id: "spec.loop.engine"
        type: soft
    outputs:
      - artifact_id: "schema.kpi"
        type: schema
    validation:
      criteria:
        - "Dashboard CEO (10 max)"
        - "Alertes definies"
        - "Seuils documentes"
      automated: false

  - id: "spec.task.catalog"
    name: "Task Catalog"
    type: spec
    status: completed
    file: "10-task-catalog.md"
    dependencies:
      - node_id: "spec.kpi.system"
        type: soft
    outputs:
      - artifact_id: "catalog.tasks"
        type: catalog
    validation:
      criteria:
        - "Tasks P0 definies"
        - "Dependances mappees"
        - "Criteres acceptation"
      automated: false

  - id: "spec.agent.catalog"
    name: "Agent Catalog"
    type: spec
    status: completed
    file: "11-agent-catalog.md"
    dependencies:
      - node_id: "spec.agent.model"
        type: hard
      - node_id: "spec.kpi.system"
        type: soft
    outputs:
      - artifact_id: "catalog.agents"
        type: catalog
    validation:
      criteria:
        - "Hierarchie definie"
        - "14 agents documentes"
        - "KPIs par agent"
      automated: false

  - id: "spec.golden.rules"
    name: "Golden Rules"
    type: spec
    status: completed
    file: "99-golden-rules.md"
    dependencies:
      - node_id: "spec.governance"
        type: hard
    outputs:
      - artifact_id: "rules.golden"
        type: documentation
    validation:
      criteria:
        - "10 regles max"
        - "Non-negociables"
        - "Memorisables"
      automated: false
```

### Milestones

```yaml
Milestones:
  - id: "milestone.p0.specs"
    name: "Phase 0 Specifications Complete"
    type: milestone
    status: completed
    dependencies:
      - node_id: "spec.agent.model"
        type: hard
      - node_id: "spec.skill.model"
        type: hard
      - node_id: "spec.loop.engine"
        type: hard
      - node_id: "spec.governance"
        type: hard
      - node_id: "spec.memory.model"
        type: hard
      - node_id: "spec.kpi.system"
        type: hard
      - node_id: "spec.task.catalog"
        type: hard
      - node_id: "spec.agent.catalog"
        type: hard
      - node_id: "spec.golden.rules"
        type: hard
    validation:
      criteria:
        - "Tous les specs completed"
        - "Review Human CEO"
      automated: false

  - id: "milestone.p0.implementation"
    name: "Phase 0 Implementation Ready"
    type: milestone
    status: pending
    dependencies:
      - node_id: "milestone.p0.specs"
        type: hard
    validation:
      criteria:
        - "Budget approuve"
        - "Equipe assignee"
        - "Timeline definie"
      automated: false
```

---

## Chemin Critique

```
spec.agent.model (2j)
    |
    +---> spec.skill.model (1j)
    |         |
    |         +---> spec.loop.engine (2j)
    |                   |
    |                   +---> spec.kpi.system (1j)
    |                             |
    |                             +---> spec.task.catalog (1j)
    |                             |
    |                             +---> spec.agent.catalog (1j)
    |
    +---> spec.memory.model (1j)
    |
    +---> spec.governance (1j)
              |
              +---> spec.golden.rules (0.5j)

TOTAL CHEMIN CRITIQUE: ~9.5 jours
```

---

## Matrice de Dependances

| Node | Depends On | Blocks |
|------|------------|--------|
| spec.agent.model | - | skill, loop, memory, catalog.agents |
| spec.skill.model | agent.model | loop.engine |
| spec.loop.engine | agent, skill | kpi.system |
| spec.governance | (agent) | golden.rules |
| spec.memory.model | agent.model | - |
| spec.kpi.system | loop.engine | task.catalog, agent.catalog |
| spec.task.catalog | (kpi) | - |
| spec.agent.catalog | agent, (kpi) | - |
| spec.golden.rules | governance | - |

---

## Validation DAG

### Proprietes Requises

1. **Acyclique** : Pas de cycles dans les dependances
2. **Racine unique** : START est la seule source
3. **Terminaison** : Tous les chemins menent a DONE
4. **Coherence** : Toutes les dependances existent

### Script de Validation

```typescript
function validateDAG(nodes: DAGNode[]): ValidationResult {
  const visited = new Set<string>();
  const recStack = new Set<string>();

  function hasCycle(nodeId: string): boolean {
    if (recStack.has(nodeId)) return true;
    if (visited.has(nodeId)) return false;

    visited.add(nodeId);
    recStack.add(nodeId);

    const node = nodes.find(n => n.id === nodeId);
    for (const dep of node?.dependencies || []) {
      if (hasCycle(dep.node_id)) return true;
    }

    recStack.delete(nodeId);
    return false;
  }

  for (const node of nodes) {
    if (hasCycle(node.id)) {
      return { valid: false, error: `Cycle detected at ${node.id}` };
    }
  }

  return { valid: true };
}
```

---

## Status Summary

| Category | Total | Completed | Pending | Blocked |
|----------|-------|-----------|---------|---------|
| Specs | 10 | 10 | 0 | 0 |
| Tasks | 13 | 4 | 9 | 0 |
| Agents | 14 | 0 | 14 | 0 |
| Milestones | 2 | 1 | 1 | 0 |

---

## Next Steps (Phase 1)

Une fois milestone.p0.specs complete:

1. **Implementation Contracts** (2 semaines)
   - Creer `packages/contracts/`
   - Implementer AgentContract
   - Implementer SkillContract
   - Implementer LoopContract

2. **Infrastructure Memory** (1 semaine)
   - Creer tables Supabase
   - Implementer MemoryService
   - Configurer Redis

3. **Premier Agent** (1 semaine)
   - Implementer agent.seo.vlevel
   - Tests unitaires
   - Integration loop

4. **Dashboard CEO** (1 semaine)
   - Frontend Remix
   - 10 KPIs
   - Alertes

---

_Ce document est la source de verite pour le DAG AI-COS Phase 0._
