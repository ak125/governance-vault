# LangGraph Router: Graph & Flows

> Orchestration déclarative avec LangGraph pour le routage d'intents et l'exécution de flows.

---

## 1. Router Graph Principal

Le router graph est le point d'entrée pour toutes les exécutions.

```typescript
// packages/ai-orchestrator/src/router-graph.ts

import { StateGraph, END } from '@langchain/langgraph';

export function createRouterGraph() {
  const graph = new StateGraph<GraphState>({
    channels: graphStateChannels,
  });

  // === NODES ===

  graph.addNode('parse_intent', parseIntentNode);
  graph.addNode('validate_input', validateInputNode);
  graph.addNode('check_budget', checkBudgetNode);
  graph.addNode('route_to_flow', routeToFlowNode);
  graph.addNode('execute_skill', executeSkillNode);
  graph.addNode('validate_output', validateOutputNode);
  graph.addNode('handle_error', handleErrorNode);
  graph.addNode('finalize', finalizeNode);

  // Sub-flows (imported)
  graph.addNode('seo_audit_flow', seoAuditFlow);
  graph.addNode('content_gen_flow', contentGenFlow);
  graph.addNode('kg_diagnose_flow', kgDiagnoseFlow);

  // === ENTRY ===

  graph.setEntryPoint('parse_intent');

  // === EDGES ===

  graph.addEdge('parse_intent', 'validate_input');

  graph.addConditionalEdges('validate_input', (state) => {
    if (state.errors.length > 0) return 'handle_error';
    return 'check_budget';
  });

  graph.addConditionalEdges('check_budget', (state) => {
    if (state.budget.tokensRemaining <= 0) return 'handle_error';
    return 'route_to_flow';
  });

  // Route based on intent
  graph.addConditionalEdges('route_to_flow', (state) => {
    return state.job.intent;
  }, {
    'seo_audit': 'seo_audit_flow',
    'content_generate': 'content_gen_flow',
    'rag_reindex': 'execute_skill',
    'kg_diagnose': 'kg_diagnose_flow',
    'routes_sync': 'execute_skill',
    'sitemap_build': 'execute_skill',
  });

  graph.addEdge('execute_skill', 'validate_output');

  graph.addConditionalEdges('validate_output', (state) => {
    if (state.errors.length > 0) return 'handle_error';
    return 'finalize';
  });

  graph.addConditionalEdges('handle_error', (state) => {
    const lastError = state.errors[state.errors.length - 1];
    if (lastError?.recoverable && state.retryCount < 3) {
      return 'execute_skill'; // Retry
    }
    return 'finalize'; // Give up
  });

  graph.addEdge('finalize', END);

  return graph.compile();
}
```

---

## 2. Nodes Implementation

### Parse Intent Node

```typescript
async function parseIntentNode(state: GraphState): Promise<GraphState> {
  // Validate JobEnvelope
  const validated = JobEnvelopeSchema.safeParse(state.job);

  if (!validated.success) {
    return {
      ...state,
      errors: [...state.errors, {
        node: 'parse_intent',
        message: `Invalid job envelope: ${validated.error.message}`,
        timestamp: new Date().toISOString(),
        recoverable: false,
      }],
    };
  }

  return {
    ...state,
    currentNode: 'parse_intent',
    visitedNodes: [...state.visitedNodes, 'parse_intent'],
  };
}
```

### Check Budget Node

```typescript
async function checkBudgetNode(state: GraphState): Promise<GraphState> {
  const { constraints } = state.job;

  // Check token budget
  if (state.budget.tokensUsed >= constraints.maxTokens) {
    return {
      ...state,
      errors: [...state.errors, {
        node: 'check_budget',
        message: `Token budget exhausted: ${state.budget.tokensUsed}/${constraints.maxTokens}`,
        timestamp: new Date().toISOString(),
        recoverable: false,
      }],
    };
  }

  // Check monetary budget if set
  if (constraints.budget && calculateCost(state.budget) >= constraints.budget) {
    return {
      ...state,
      errors: [...state.errors, {
        node: 'check_budget',
        message: `Monetary budget exhausted`,
        timestamp: new Date().toISOString(),
        recoverable: false,
      }],
    };
  }

  return {
    ...state,
    currentNode: 'check_budget',
    visitedNodes: [...state.visitedNodes, 'check_budget'],
  };
}
```

### Execute Skill Node

```typescript
async function executeSkillNode(state: GraphState): Promise<GraphState> {
  const skillName = intentToSkill(state.job.intent);
  const skill = skillRegistry.get(skillName);

  if (!skill) {
    return {
      ...state,
      errors: [...state.errors, {
        node: 'execute_skill',
        message: `Skill not found: ${skillName}`,
        timestamp: new Date().toISOString(),
        recoverable: false,
      }],
    };
  }

  try {
    const result = await skillRegistry.execute(skillName, {
      jobId: state.job.jobId,
      traceId: state.job.traceId,
      params: state.input,
      ragContext: state.ragContext,
      constraints: state.job.constraints,
      startTime: Date.now(),
    });

    return {
      ...state,
      output: result.data,
      artifacts: [...state.artifacts, ...result.artifacts],
      budget: {
        ...state.budget,
        tokensUsed: state.budget.tokensUsed + result.metrics.tokensUsed,
        tokensRemaining: state.budget.tokensRemaining - result.metrics.tokensUsed,
      },
      currentNode: 'execute_skill',
      visitedNodes: [...state.visitedNodes, 'execute_skill'],
    };
  } catch (error) {
    return {
      ...state,
      retryCount: state.retryCount + 1,
      errors: [...state.errors, {
        node: 'execute_skill',
        message: error.message,
        timestamp: new Date().toISOString(),
        recoverable: state.retryCount < 3,
      }],
    };
  }
}
```

---

## 3. Corrective-RAG Pattern

Pattern pour améliorer la qualité des réponses RAG.

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
  const irrelevant = graded.filter(g => g.grade === 'irrelevant');

  // 3. If not enough relevant, try query transformation
  if (relevant.length < 3) {
    const transformedQuery = await transformQuery(state.input.query);
    const additionalDocs = await ragSearch(transformedQuery, {
      maxResults: 5,
      minScore: 0.65, // Lower threshold for retry
    });

    const additionalGraded = await Promise.all(
      additionalDocs.map(async (doc) => ({
        doc,
        grade: await gradeDocument(state.input.query, doc),
      }))
    );

    relevant.push(...additionalGraded.filter(g => g.grade === 'relevant'));
  }

  // 4. CRITICAL: Refuse to generate if no relevant docs
  if (relevant.length === 0) {
    return {
      ...state,
      errors: [...state.errors, {
        node: 'corrective_rag',
        message: 'No relevant documents found - refusing to generate to prevent hallucination',
        timestamp: new Date().toISOString(),
        recoverable: false,
      }],
    };
  }

  // 5. Update state with RAG context
  return {
    ...state,
    ragContext: {
      documents: relevant.map(r => r.doc),
      citations: relevant.map(r => r.doc.metadata.sourcePath),
      truthLevel: calculateCompositeTruthLevel(relevant),
      confidence: calculateConfidence(relevant),
    },
    currentNode: 'corrective_rag',
    visitedNodes: [...state.visitedNodes, 'corrective_rag'],
  };
}

async function gradeDocument(query: string, doc: RagDocument): Promise<'relevant' | 'irrelevant'> {
  // Use LLM to grade relevance
  const response = await llm.invoke({
    prompt: `Is this document relevant to the query?
Query: ${query}
Document: ${doc.content.substring(0, 500)}

Answer only "relevant" or "irrelevant".`,
  });

  return response.toLowerCase().includes('relevant') ? 'relevant' : 'irrelevant';
}
```

---

## 4. SEO Audit Flow

Flow complet pour l'audit SEO.

```typescript
// packages/ai-orchestrator/src/flows/seo-audit.flow.ts

export function createSeoAuditFlow() {
  const flow = new StateGraph<SeoAuditState>({
    channels: seoAuditChannels,
  });

  // Step 1: Fetch pages to audit
  flow.addNode('fetch_pages', async (state) => {
    const pages = await fetchPagesForAudit(state.job.scope);
    return { ...state, pages, currentPageIndex: 0 };
  });

  // Step 2: Validate PageRole
  flow.addNode('validate_role', async (state) => {
    const page = state.pages[state.currentPageIndex];
    const roleValidation = await validatePageRole(page);

    return {
      ...state,
      validations: [...state.validations, {
        url: page.url,
        role: page.role,
        ...roleValidation,
      }],
    };
  });

  // Step 3: Check content against role
  flow.addNode('validate_content', async (state) => {
    const page = state.pages[state.currentPageIndex];
    const contentValidation = await validateContentForRole(page);

    const lastValidation = state.validations[state.validations.length - 1];
    return {
      ...state,
      validations: [
        ...state.validations.slice(0, -1),
        { ...lastValidation, content: contentValidation },
      ],
    };
  });

  // Step 4: Check internal links
  flow.addNode('validate_links', async (state) => {
    const page = state.pages[state.currentPageIndex];
    const linkValidation = await validateInternalLinks(page);

    const lastValidation = state.validations[state.validations.length - 1];
    return {
      ...state,
      validations: [
        ...state.validations.slice(0, -1),
        { ...lastValidation, links: linkValidation },
      ],
      currentPageIndex: state.currentPageIndex + 1,
    };
  });

  // Step 5: Loop or finalize
  flow.addConditionalEdges('validate_links', (state) => {
    if (state.currentPageIndex < state.pages.length) {
      return 'validate_role'; // Next page
    }
    return 'generate_report'; // Done
  });

  // Step 6: Generate report
  flow.addNode('generate_report', async (state) => {
    const report = generateAuditReport(state.validations);

    return {
      ...state,
      artifacts: [{
        type: 'report',
        name: 'seo-audit-report',
        format: 'markdown',
        content: report,
        createdAt: new Date().toISOString(),
      }],
    };
  });

  // Step 7: Decide action based on severity
  flow.addConditionalEdges('generate_report', (state) => {
    const criticalCount = state.validations.filter(
      v => v.severity === 'critical'
    ).length;

    if (criticalCount > 0) return 'create_pr';
    return 'notify_only';
  });

  flow.addNode('create_pr', createPrNode);
  flow.addNode('notify_only', notifyNode);

  flow.addEdge('create_pr', END);
  flow.addEdge('notify_only', END);

  flow.setEntryPoint('fetch_pages');

  return flow.compile();
}
```

---

## 5. Usage Example

```typescript
// Instantiate router
const router = createRouterGraph();

// Create job envelope
const job: JobEnvelope = {
  jobId: uuidv4(),
  traceId: uuidv4(),
  intent: JobIntent.SEO_AUDIT,
  scope: {
    entityType: 'page',
    filters: { role: ['R1', 'R2'] },
    limit: 100,
  },
  constraints: {
    maxTokens: 4000,
    maxDocs: 10,
    timeout: 300000,
    dryRun: false,
  },
  context: {
    source: 'cron',
    priority: 'normal',
  },
  idempotencyKey: generateIdempotencyKey(job),
  createdAt: new Date().toISOString(),
};

// Execute
const result = await router.invoke({
  job,
  currentNode: 'start',
  visitedNodes: [],
  errors: [],
  artifacts: [],
  retryCount: 0,
  budget: {
    tokensUsed: 0,
    tokensRemaining: job.constraints.maxTokens,
    docsRetrieved: 0,
    apiCalls: 0,
  },
});

console.log('Artifacts:', result.artifacts);
console.log('Errors:', result.errors);
```

---

## Voir aussi

- [[02-ai-cos-contracts]] - GraphState schema
- [[03-skills-registry]] - Skills execution
- [[04-rag-system]] - RAG integration
- [[06-minilo-weaver]] - Job triggering

---

_Créé: 2026-02-03 | Source: Architecture Report Section 7_
