# AI-COS Loop Engine (Flywheel ODACVLS + LangGraph)

> **Version**: 1.2.0 | **Status**: CANON | **Date**: 2026-01-27
> **Aligned with**: Architecture Charter v2.1.0 Sections 7-8
> **Breaking Changes**: executeSkillNode uses job.payload

## Objectif

Definir le moteur de boucle d'auto-amelioration AI-COS, inspire du pattern **Agentic Flywheel** et implemente avec **LangGraph**.

---

## Le Pattern ODACVLS

```
    ┌──────────────────────────────────────────────────────┐
    │                     FLYWHEEL                          │
    │                                                       │
    │   ┌─────────┐                          ┌─────────┐   │
    │   │ OBSERVE │ ────────────────────────▶│ DETECT  │   │
    │   └─────────┘                          └────┬────┘   │
    │        ▲                                    │        │
    │        │                                    ▼        │
    │   ┌────┴────┐                          ┌─────────┐   │
    │   │  STORE  │                          │ ANALYZE │   │
    │   └─────────┘                          └────┬────┘   │
    │        ▲                                    │        │
    │        │                                    ▼        │
    │   ┌────┴────┐                          ┌─────────┐   │
    │   │  LEARN  │◀─────────────────────────│ DECIDE  │   │
    │   └─────────┘                          └────┬────┘   │
    │        ▲                                    │        │
    │        │          ┌─────────┐               │        │
    │        └──────────│VALIDATE │◀──────────────┘        │
    │                   └────┬────┘                        │
    │                        │                             │
    │                   ┌────▼────┐                        │
    │                   │   ACT   │                        │
    │                   └─────────┘                        │
    │                                                       │
    └──────────────────────────────────────────────────────┘
```

---

## Schema Loop Contract

```yaml
Loop:
  # ═══════════════════════════════════════════════════════════
  # IDENTITÉ
  # ═══════════════════════════════════════════════════════════
  id: string                    # Unique (ex: seo_audit_loop)
  name: string                  # Display name
  domain: Domain                # CORE, INFRA, DATA, SEO, RAG, CART, AICOS
  description: string           # Description courte

  # ═══════════════════════════════════════════════════════════
  # TRIGGER (Déclenchement)
  # ═══════════════════════════════════════════════════════════
  trigger:
    type: TriggerType           # cron | event | manual | threshold
    config:
      # Pour cron
      expression: string        # Ex: "0 2 * * *" (2am daily)
      timezone: string          # Ex: "Europe/Paris"
      # Pour event
      event_pattern: string     # Ex: "seo.page.updated"
      # Pour threshold
      metric: string            # Ex: "seo.violations.count"
      operator: string          # >, <, >=, <=, ==
      value: number             # Seuil de déclenchement

  # ═══════════════════════════════════════════════════════════
  # PHASE 1: DETECT (Observer et détecter)
  # ═══════════════════════════════════════════════════════════
  detect:
    sources:
      - type: SourceType        # metric | log | event | alert | database
        name: string            # Nom de la source
        filter: string          # Filtre optionnel
        freshness_hours: number # Données max X heures

    conditions:                 # Conditions pour continuer
      - expression: string      # Ex: "metrics.seo_violations > 0"
        threshold: number       # Seuil optionnel
        aggregation: string     # sum | avg | max | min | count

    skip_if:                    # Ne pas exécuter si...
      - expression: string      # Ex: "last_run < 1_hour_ago"

  # ═══════════════════════════════════════════════════════════
  # PHASE 2: ANALYZE (Analyser le contexte)
  # ═══════════════════════════════════════════════════════════
  analyze:
    strategy: AnalysisStrategy  # rule_based | ml | hybrid | llm

    context_required:           # Contexte nécessaire
      - context_type: string    # Ex: "seo_rules", "page_data"
        source: string          # D'où le récupérer
        ttl_seconds: number     # Durée de cache

    analysis_steps:
      - name: string            # Nom de l'étape
        skill_id: string        # Skill à utiliser
        params: object          # Paramètres du skill

    timeout_ms: number          # Timeout max pour l'analyse
    max_retries: number         # Retries si échec

  # ═══════════════════════════════════════════════════════════
  # PHASE 3: DECIDE (Prendre une décision)
  # ═══════════════════════════════════════════════════════════
  decide:
    decision_tree:
      - condition: string       # Condition à évaluer
        confidence_required: number # Confiance min (0-1)
        action: string          # Action à prendre
        priority: Priority      # low | normal | high | critical

    fallback_action: string     # Action si aucune condition

    human_approval:
      required_for: string[]    # Actions nécessitant approbation
      timeout_hours: number     # Délai avant escalade
      escalation_target: string # Agent d'escalade

  # ═══════════════════════════════════════════════════════════
  # PHASE 4: ACT (Exécuter l'action)
  # ═══════════════════════════════════════════════════════════
  act:
    actions:
      - action_id: string       # ID unique de l'action
        skill_id: string        # Skill à exécuter
        params: object          # Paramètres
        rollback_skill: string  # Skill de rollback (optionnel)
        max_affected: number    # Limite d'items affectés
        feature_flag: string    # Feature flag requis (optionnel)

    execution_mode: ExecMode    # sequential | parallel | batch
    batch_size: number          # Taille des batches (si batch)
    dry_run_first: boolean      # Faire un dry-run d'abord ?

  # ═══════════════════════════════════════════════════════════
  # PHASE 5: VALIDATE (Vérifier le résultat)
  # ═══════════════════════════════════════════════════════════
  validate:
    assertions:
      - expression: string      # Assertion à vérifier
        severity: Severity      # error | warning | info
        retry_on_fail: boolean  # Réessayer si échec ?
        max_retries: number     # Nombre max de retries

    success_criteria:
      - metric: string          # Métrique à vérifier
        operator: string        # >, <, >=, <=, ==
        expected: number        # Valeur attendue

    auto_rollback:
      enabled: boolean          # Rollback auto si échec ?
      trigger_conditions:
        - string                # Ex: "error_rate > 5%"
      max_rollback_time_ms: number

  # ═══════════════════════════════════════════════════════════
  # PHASE 6: LEARN (Apprendre du résultat)
  # ═══════════════════════════════════════════════════════════
  learn:
    feedback_sources:
      - type: FeedbackType      # metric | human | outcome | a_b_test
        name: string            # Nom de la source
        weight: number          # Poids (0-1)

    learning_config:
      rate: number              # Learning rate (0-1)
      max_adjustment: number    # Ajustement max par cycle
      min_samples: number       # Échantillons min avant ajustement
      cooldown_hours: number    # Cooldown entre ajustements

    anti_hallucination:
      enabled: boolean          # Protection anti-hallucination
      confidence_floor: number  # Confiance min (ex: 0.7)
      human_review_threshold: number # Seuil pour review humain

  # ═══════════════════════════════════════════════════════════
  # PHASE 7: STORE (Persister les résultats)
  # ═══════════════════════════════════════════════════════════
  store:
    artifacts:
      - type: ArtifactType      # log | metric | decision | outcome | audit
        name: string            # Nom de l'artefact
        storage: Storage        # supabase | redis | file
        retention_days: number  # Durée de conservation
        indexed: boolean        # Indexé pour recherche ?

    audit_trail:
      enabled: boolean          # Audit trail actif ?
      fields:                   # Champs à logger
        - timestamp
        - loop_id
        - trigger_type
        - decision_made
        - actions_taken
        - outcome
        - confidence
```

---

## Enums

```typescript
enum TriggerType {
  CRON = 'cron',
  EVENT = 'event',
  MANUAL = 'manual',
  THRESHOLD = 'threshold'
}

enum SourceType {
  METRIC = 'metric',
  LOG = 'log',
  EVENT = 'event',
  ALERT = 'alert',
  DATABASE = 'database'
}

enum AnalysisStrategy {
  RULE_BASED = 'rule_based',
  ML = 'ml',
  HYBRID = 'hybrid',
  LLM = 'llm'
}

enum ExecMode {
  SEQUENTIAL = 'sequential',
  PARALLEL = 'parallel',
  BATCH = 'batch'
}

enum FeedbackType {
  METRIC = 'metric',
  HUMAN = 'human',
  OUTCOME = 'outcome',
  AB_TEST = 'a_b_test'
}

enum ArtifactType {
  LOG = 'log',
  METRIC = 'metric',
  DECISION = 'decision',
  OUTCOME = 'outcome',
  AUDIT = 'audit'
}
```

---

## Exemple Concret: `seo_audit_loop`

```yaml
Loop:
  id: "seo_audit_loop"
  name: "SEO Audit Loop"
  domain: SEO
  description: "Continuous SEO audit and auto-correction loop"

  trigger:
    type: cron
    config:
      expression: "0 2 * * *"  # Daily at 2am
      timezone: "Europe/Paris"

  detect:
    sources:
      - type: database
        name: "__seo_pages"
        filter: "updated_at > now() - interval '24 hours'"
        freshness_hours: 24
      - type: metric
        name: "seo.violations.count"
        freshness_hours: 1

    conditions:
      - expression: "pages.count > 0"
        threshold: 1
      - expression: "violations.count > 0"
        aggregation: sum

    skip_if:
      - expression: "last_run < 6_hours_ago"

  analyze:
    strategy: hybrid

    context_required:
      - context_type: "page_role_rules"
        source: "seo_role_rules"
        ttl_seconds: 3600
      - context_type: "canonical_rules"
        source: "canonical_rules_engine"
        ttl_seconds: 3600

    analysis_steps:
      - name: "audit_roles"
        skill_id: "seo_role_audit"
        params: { check_content: true }
      - name: "check_canonicals"
        skill_id: "canonical_check"
        params: {}

    timeout_ms: 300000
    max_retries: 2

  decide:
    decision_tree:
      - condition: "violations.critical.count > 0"
        confidence_required: 0.9
        action: "escalate_to_human"
        priority: critical
      - condition: "violations.error.count > 10"
        confidence_required: 0.8
        action: "auto_fix_batch"
        priority: high
      - condition: "violations.warning.count > 0"
        confidence_required: 0.7
        action: "log_and_notify"
        priority: normal

    fallback_action: "log_only"

    human_approval:
      required_for: ["auto_fix_batch", "escalate_to_human"]
      timeout_hours: 24
      escalation_target: "agent.seo.architect"

  act:
    actions:
      - action_id: "fix_role_violations"
        skill_id: "seo_role_fix"
        params: { dry_run: false }
        rollback_skill: "seo_role_rollback"
        max_affected: 100
        feature_flag: "seo_auto_fix"

    execution_mode: batch
    batch_size: 10
    dry_run_first: true

  validate:
    assertions:
      - expression: "violations.after <= violations.before"
        severity: error
        retry_on_fail: true
        max_retries: 1

    success_criteria:
      - metric: "violations.count"
        operator: "<="
        expected: 0

    auto_rollback:
      enabled: true
      trigger_conditions:
        - "error_rate > 5%"
        - "new_violations > old_violations"
      max_rollback_time_ms: 60000

  learn:
    feedback_sources:
      - type: outcome
        name: "fix_success_rate"
        weight: 0.6
      - type: metric
        name: "violations_trend"
        weight: 0.4

    learning_config:
      rate: 0.1
      max_adjustment: 0.05
      min_samples: 10
      cooldown_hours: 24

    anti_hallucination:
      enabled: true
      confidence_floor: 0.7
      human_review_threshold: 0.5

  store:
    artifacts:
      - type: audit
        name: "seo_audit_report"
        storage: supabase
        retention_days: 90
        indexed: true
      - type: metric
        name: "loop_metrics"
        storage: redis
        retention_days: 30
        indexed: false

    audit_trail:
      enabled: true
      fields:
        - timestamp
        - loop_id
        - trigger_type
        - decision_made
        - actions_taken
        - outcome
        - confidence
```

---

## Interface TypeScript

```typescript
// packages/contracts/src/loop.ts

export interface LoopContract {
  readonly manifest: LoopManifest;
  run(): Promise<LoopExecution>;
  pause(): Promise<void>;
  resume(): Promise<void>;
  getStatus(): LoopStatus;
}

export interface LoopExecution {
  executionId: string;
  loopId: string;
  startedAt: Date;
  completedAt?: Date;
  phases: PhaseResult[];
  outcome: LoopOutcome;
  artifacts: Artifact[];
}

export interface PhaseResult {
  phase: 'detect' | 'analyze' | 'decide' | 'act' | 'validate' | 'learn' | 'store';
  startedAt: Date;
  completedAt: Date;
  success: boolean;
  data: unknown;
  errors?: Error[];
}
```

---

## LangGraph Router (Architecture Charter Section 7.1)

```typescript
// packages/ai-orchestrator/src/router-graph.ts

import { StateGraph, END } from '@langchain/langgraph';

export function createRouterGraph() {
  const graph = new StateGraph<GraphState>({
    channels: graphStateChannels,
  });

  // Nodes
  graph.addNode('parse_intent', parseIntentNode);
  graph.addNode('validate_input', validateInputNode);
  graph.addNode('check_budget', checkBudgetNode);
  graph.addNode('route_to_flow', routeToFlowNode);
  graph.addNode('execute_skill', executeSkillNode);
  graph.addNode('validate_output', validateOutputNode);
  graph.addNode('handle_error', handleErrorNode);
  graph.addNode('finalize', finalizeNode);

  // Entry
  graph.setEntryPoint('parse_intent');

  // Conditional Edges
  graph.addConditionalEdges('validate_input', (state) => {
    if (state.errors.length > 0) return 'handle_error';
    return 'check_budget';
  });

  graph.addConditionalEdges('check_budget', (state) => {
    if (state.budget.tokensRemaining <= 0) return 'handle_error';
    return 'route_to_flow';
  });

  graph.addConditionalEdges('route_to_flow', (state) => {
    return state.job.intent; // Routes to specific flow
  }, {
    'seo_audit': 'seo_audit_flow',
    'content_generate': 'content_gen_flow',
    'rag_reindex': 'execute_skill',
    'kg_diagnose': 'kg_diagnose_flow',
  });

  graph.addEdge('execute_skill', 'validate_output');
  graph.addEdge('finalize', END);

  return graph.compile();
}

// executeSkillNode: utilise job.payload (pas job.scope!)
async function executeSkillNode(state: GraphState): Promise<GraphState> {
  const skill = skillRegistry.get(state.job.intent);

  const input: SkillInput = {
    jobId: state.job.jobId,
    traceId: state.job.traceId,
    // RÈGLE: params = job.payload (params métier), PAS job.scope
    params: state.job.payload,
    constraints: state.job.constraints,
    startedAt: new Date().toISOString(),
    ragContext: state.ragContext,
  };

  const output = await skill.execute(input);

  return {
    ...state,
    output: output.data,
    artifacts: [...state.artifacts, ...output.artifacts],
    budget: {
      ...state.budget,
      tokensUsed: state.budget.tokensUsed + (output.metrics.tokens_used ?? 0),
      tokensRemaining: state.budget.tokensRemaining - (output.metrics.tokens_used ?? 0),
    },
  };
}
```

---

## Corrective-RAG Pattern (Architecture Charter Section 7.2)

```typescript
// packages/ai-orchestrator/src/patterns/corrective-rag.ts

export async function correctiveRagNode(state: GraphState): Promise<GraphState> {
  // 1. Initial retrieval
  const docs = await ragSearch(state.input.query, {
    maxResults: state.job.constraints.maxDocs,
    minScore: 0.70,
  });

  // 2. Grade documents for relevance
  const graded = await Promise.all(
    docs.map(async (doc) => ({
      doc,
      grade: await gradeDocument(state.input.query, doc),
    }))
  );

  const relevant = graded.filter(g => g.grade === 'relevant');

  // 3. If not enough relevant, transform query and retry
  if (relevant.length < 3) {
    const transformedQuery = await transformQuery(state.input.query);
    const additionalDocs = await ragSearch(transformedQuery, {
      maxResults: 5,
      minScore: 0.65,
    });
    relevant.push(...additionalDocs.map(d => ({ doc: d, grade: 'relevant' })));
  }

  // 4. ANTI-HALLUCINATION: Refuse if no relevant docs
  if (relevant.length === 0) {
    return {
      ...state,
      errors: [...state.errors, {
        node: 'corrective_rag',
        message: 'No relevant documents found - refusing to generate',
        recoverable: false,
      }],
    };
  }

  return {
    ...state,
    ragContext: {
      documents: relevant.map(r => r.doc),
      citations: relevant.map(r => r.doc.metadata.sourcePath),
      confidence: calculateConfidence(relevant),
    },
  };
}
```

---

## MiniLo/Weaver Triggers (Architecture Charter Section 8)

```typescript
// packages/minilo-weaver/src/triggers/trigger.types.ts

export type TriggerType = 'cron' | 'webhook' | 'event' | 'manual';

export interface TriggerConfig {
  type: TriggerType;

  cron?: {
    expression: string;  // '0 2 * * *' = 2am daily
    timezone: string;
  };

  webhook?: {
    path: string;
    method: 'POST' | 'PUT';
    secret?: string;
  };

  event?: {
    source: string;      // 'supabase', 'redis', 'kafka'
    pattern: string;     // 'product.updated', 'seo.*'
  };

  intentMapping: Record<string, string>;
  scopeCalculator: (payload: unknown) => JobScope;
  enabled: boolean;
}
```

---

## Anti-Patterns MiniLo (INTERDIT)

```typescript
// ANTI-PATTERN 1: Execution directe sans envelope
// WRONG:
await skillRegistry.execute('seo_audit', { urls: ['...'] });

// CORRECT:
await jobManager.enqueue(createJobEnvelope({
  intent: 'seo_audit',
  scope: { entityType: 'page', entityIds: ['...'] },
}));

// ANTI-PATTERN 2: Scope calculation in trigger
// WRONG:
triggers.on('product.updated', async (event) => {
  const relatedProducts = await db.query('...'); // NO DB in trigger!
  await jobManager.enqueue({ scope: { entityIds: relatedProducts } });
});

// CORRECT:
triggers.on('product.updated', async (event) => {
  await jobManager.enqueue({
    intent: 'product_sync',
    scope: scopeCalculator.fromEvent(event),
  });
});

// ANTI-PATTERN 3: Unbounded scope
// WRONG:
scope: { entityType: 'all' } // Will process millions of items

// CORRECT:
scope: {
  entityType: 'page',
  filters: { updatedSince: lastRunTime },
  limit: 1000, // Always bounded
}
```

---

## Regle d'Or

```
MiniLo DECLENCHE -> LangGraph DECIDE -> Skills EXECUTENT -> RAG FOURNIT -> MCP GOUVERNE
```

---

_Ce document est la source de verite pour le Loop Engine AI-COS (Flywheel + LangGraph)._
