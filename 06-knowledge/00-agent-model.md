# AI-COS Agent Model (Contrat Agent)

> **Version**: 1.5.0 | **Status**: CANON | **Date**: 2026-01-27
> **Aligned with**: Architecture Charter v2.1.0
> **Dependencies**: 06-rag-system.md (RagDocumentSchema, TruthLevelSchema)
> **Breaking Changes**: payload field, GraphState defaults, createJobEnvelope helper, Security Warning

## Objectif

Définir le contrat universel que **tout agent AI-COS** doit respecter.

---

## Schema Agent Contract

```yaml
Agent:
  # ═══════════════════════════════════════════════════════════
  # IDENTITÉ
  # ═══════════════════════════════════════════════════════════
  id: string                    # Unique, snake_case (ex: agent.seo.vlevel)
  name: string                  # Display name (ex: "V-Level Generator Agent")
  role: AgentRole               # Enum: voir ci-dessous
  domain: Domain                # Enum: CORE, INFRA, DATA, SEO, RAG, CART, AICOS
  version: semver               # Contract version (ex: "1.0.0")
  owner: string                 # Équipe responsable

  # ═══════════════════════════════════════════════════════════
  # CAPACITÉS (INPUTS/OUTPUTS)
  # ═══════════════════════════════════════════════════════════
  inputs:
    - name: string              # Nom du paramètre
      type: ZodSchema           # Type validé par Zod
      required: boolean         # Obligatoire ou non
      description: string       # Documentation

  outputs:
    - name: string              # Nom de la sortie
      type: ZodSchema           # Type validé par Zod
      description: string

  # ═══════════════════════════════════════════════════════════
  # OUTILS & SKILLS
  # ═══════════════════════════════════════════════════════════
  tools:                        # MCP tools disponibles
    - tool_id: string           # ID MCP (ex: mcp__supabase__execute_sql)
      permissions: Permission   # read | write | execute
      rate_limit: number        # Appels max par minute

  skills:                       # Skills utilisables (ref 01-skill-model)
    - skill_id: string          # ID du skill (ex: seo_role_audit)
      required: boolean         # Obligatoire pour fonctionner

  # ═══════════════════════════════════════════════════════════
  # MÉMOIRE
  # ═══════════════════════════════════════════════════════════
  memory:
    short_term:
      enabled: boolean          # Context window actif
      max_tokens: number        # Limite tokens (ex: 100000)
    long_term:
      enabled: boolean          # Persistence active
      storage: Storage          # supabase | redis | vector
    shared:
      enabled: boolean          # Mémoire inter-agents
      namespaces: string[]      # Namespaces accessibles

  # ═══════════════════════════════════════════════════════════
  # VALIDATION & CONTRÔLE
  # ═══════════════════════════════════════════════════════════
  validation:
    pre_conditions:             # Conditions AVANT exécution
      - expression: string      # Ex: "input.urls.length > 0"
        error_code: string      # Ex: "EMPTY_INPUT"
    post_conditions:            # Conditions APRÈS exécution
      - expression: string      # Ex: "output.violations.length >= 0"
        error_code: string
    invariants:                 # Toujours vrais
      - string                  # Ex: "No URL modification without feature flag"

  escalation:
    triggers:                   # Quand escalader
      - "confidence < 0.7"
      - "error_count > 3"
      - "human_required == true"
    target_agent: string        # Agent de destination
    human_required: boolean     # Escalade humain obligatoire
    timeout_hours: number       # Délai avant auto-escalade

  # ═══════════════════════════════════════════════════════════
  # MÉTRIQUES (KPIs)
  # ═══════════════════════════════════════════════════════════
  kpis:
    - metric_id: string         # Ex: "task_success_rate"
      target: number            # Objectif (ex: 0.95)
      threshold_warning: number # Seuil warning (ex: 0.85)
      threshold_critical: number # Seuil critique (ex: 0.70)
      unit: string              # Ex: "percentage"
```

---

## Enums

### AgentRole

```typescript
enum AgentRole {
  ARCHITECT = 'architect',      // Conception & décisions
  ANALYZER = 'analyzer',        // Analyse & diagnostic
  EXECUTOR = 'executor',        // Exécution de tasks
  VALIDATOR = 'validator',      // Validation & QA
  ORCHESTRATOR = 'orchestrator' // Coordination multi-agents
}
```

### Domain

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

### Permission

```typescript
enum Permission {
  READ = 'read',
  WRITE = 'write',
  EXECUTE = 'execute'
}
```

### Storage

```typescript
enum Storage {
  SUPABASE = 'supabase',
  REDIS = 'redis',
  VECTOR = 'vector'  // Weaviate/Pinecone
}
```

---

## Exemple Concret: `agent.seo.vlevel`

```yaml
Agent:
  id: "agent.seo.vlevel"
  name: "V-Level Generator Agent"
  role: EXECUTOR
  domain: SEO
  version: "1.0.0"
  owner: "seo-team"

  inputs:
    - name: urls
      type: z.array(z.string().url())
      required: true
      description: "URLs to analyze for V-level scoring"
    - name: options
      type: VLevelOptionsSchema
      required: false
      description: "Optional configuration"

  outputs:
    - name: scores
      type: z.array(VLevelScoreSchema)
      description: "V-level scores V1-V5 for each URL"
    - name: recommendations
      type: z.array(RecommendationSchema)
      description: "Improvement recommendations"

  tools:
    - tool_id: mcp__supabase__execute_sql
      permissions: read
      rate_limit: 100
    - tool_id: mcp__chrome-devtools__take_snapshot
      permissions: execute
      rate_limit: 30

  skills:
    - skill_id: seo_role_audit
      required: true
    - skill_id: canonical_check
      required: true
    - skill_id: vlevel_calculator
      required: true

  memory:
    short_term:
      enabled: true
      max_tokens: 50000
    long_term:
      enabled: true
      storage: supabase
    shared:
      enabled: true
      namespaces: ["seo:scores", "seo:audit"]

  validation:
    pre_conditions:
      - expression: "urls.length > 0 && urls.length <= 1000"
        error_code: "INVALID_URL_COUNT"
    post_conditions:
      - expression: "scores.length === urls.length"
        error_code: "SCORE_MISMATCH"
    invariants:
      - "No URL modification without feature flag"
      - "Router pages must not contain expert content"

  escalation:
    triggers:
      - "confidence < 0.7"
      - "error_count > 3"
    target_agent: "agent.seo.architect"
    human_required: false
    timeout_hours: 24

  kpis:
    - metric_id: "task_success_rate"
      target: 0.95
      threshold_warning: 0.85
      threshold_critical: 0.70
      unit: "percentage"
    - metric_id: "avg_processing_time"
      target: 5000
      threshold_warning: 10000
      threshold_critical: 30000
      unit: "milliseconds"
```

---

## Règles de Validation

### R1: Tout agent DOIT avoir un contrat

```typescript
// ❌ INTERDIT
class MyAgent {
  async execute(params: any) { ... }
}

// ✅ OBLIGATOIRE
class MyAgent implements AgentContract {
  static manifest: AgentManifest = { ... };
  async execute(input: ValidatedInput): Promise<ValidatedOutput> { ... }
}
```

### R2: Tout input/output DOIT être validé par Zod

```typescript
// ❌ INTERDIT
function process(data: any) { ... }

// ✅ OBLIGATOIRE
const InputSchema = z.object({ urls: z.array(z.string().url()) });
function process(data: z.infer<typeof InputSchema>) { ... }
```

### R3: Tout agent DOIT produire des artefacts traçables

```
audit/
├── {agent_id}.{timestamp}.audit.md      # Rapport d'exécution
├── {agent_id}.{timestamp}.backlog.json  # Actions restantes
└── {agent_id}.{timestamp}.graph.json    # Dépendances
```

---

## Interface TypeScript

```typescript
// packages/contracts/src/agent.ts

import { z } from 'zod';

export interface AgentContract {
  readonly manifest: AgentManifest;
  execute(input: AgentInput): Promise<AgentOutput>;
  validate(input: unknown): AgentInput;
  escalate(reason: string): Promise<void>;
}

export interface AgentManifest {
  id: string;
  name: string;
  role: AgentRole;
  domain: Domain;
  version: string;
  owner: string;
  inputs: InputSpec[];
  outputs: OutputSpec[];
  tools: ToolSpec[];
  skills: SkillRef[];
  memory: MemoryConfig;
  validation: ValidationConfig;
  escalation: EscalationConfig;
  kpis: KpiSpec[];
}

export interface AgentInput {
  jobId: string;
  traceId: string;
  params: Record<string, unknown>;
  context: AgentContext;
}

export interface AgentOutput {
  success: boolean;
  data: unknown;
  artifacts: Artifact[];
  metrics: ExecutionMetrics;
  nextAction?: 'continue' | 'escalate' | 'complete';
}
```

---

## JobEnvelope (Contrat d'Execution)

> Aligne avec Architecture Charter Section 4.1

```typescript
// packages/contracts/src/job.ts

import { z } from 'zod';

export enum JobIntent {
  SEO_AUDIT = 'seo_audit',
  CONTENT_GENERATE = 'content_generate',
  RAG_REINDEX = 'rag_reindex',
  KG_DIAGNOSE = 'kg_diagnose',
  ROUTES_SYNC = 'routes_sync',
  SITEMAP_BUILD = 'sitemap_build',
}

export const JobScopeSchema = z.object({
  entityType: z.enum(['gamme', 'vehicle', 'article', 'page', 'all']),
  entityIds: z.array(z.string()).optional(),
  filters: z.record(z.unknown()).optional(),
  limit: z.number().max(10000).default(1000),
});

export const JobConstraintsSchema = z.object({
  maxTokens: z.number().default(4000),
  maxDocs: z.number().default(10),
  timeout: z.number().default(300000), // 5min
  budget: z.number().optional(),       // $ limit
  dryRun: z.boolean().default(false),
});

export const JobContextSchema = z.object({
  userId: z.string().optional(),
  source: z.enum(['cron', 'webhook', 'manual', 'event']),
  priority: z.enum(['low', 'normal', 'high', 'critical']).default('normal'),
  ragVersion: z.string().optional(),
  seoRole: z.string().optional(),
});

export const JobEnvelopeSchema = z.object({
  // Identite
  jobId: z.string().uuid(),
  traceId: z.string().uuid(),
  parentJobId: z.string().uuid().optional(),

  // Intent
  intent: z.nativeEnum(JobIntent),

  // Scope (what to process: entityType, entityIds, filters)
  scope: JobScopeSchema,

  // Payload (skill params: params métier spécifiques au skill)
  // RÈGLE: payload ≠ scope. Le scope dit QUOI traiter, payload dit COMMENT.
  payload: z.record(z.unknown()).default({}),

  // Constraints
  constraints: JobConstraintsSchema,

  // Context
  context: JobContextSchema,

  // Idempotency
  // RÈGLE: idempotencyKey = hash(intent + scope + major_inputs)
  // NE PAS utiliser Date.now() - doit être stable pour déduplication
  idempotencyKey: z.string(),
  createdAt: z.string().datetime(),
  expiresAt: z.string().datetime().optional(),
});

export type JobEnvelope = z.infer<typeof JobEnvelopeSchema>;
```

---

## GraphState (Etat du Flow LangGraph)

> Aligne avec Architecture Charter Section 4.2

```typescript
// packages/contracts/src/graph-state.ts

export const GraphStateSchema = z.object({
  // From JobEnvelope
  job: JobEnvelopeSchema,

  // Execution state
  currentNode: z.string().default('start'),
  visitedNodes: z.array(z.string()).default([]),
  retryCount: z.number().default(0), // Pour handle_error

  // Data flow
  input: z.unknown(),
  intermediate: z.record(z.unknown()).default({}),
  output: z.unknown().optional(),

  // RAG context (schemas defined in 06-rag-system.md)
  ragContext: z.object({
    documents: z.array(RagDocumentSchema),      // See 06-rag-system.md
    citations: z.array(CitationSchema),          // See 06-rag-system.md
    truthLevel: TruthLevelSchema,                // L1-L4, see 06-rag-system.md
    confidence: z.number().min(0).max(1),
    searchMethod: z.enum(['vector', 'bm25', 'hybrid']).default('hybrid'),
    indexVersion: z.string(),                    // Ex: '2026.01.0'
  }).optional(),

  // Budget tracking (initialisé depuis job.constraints.maxTokens)
  budget: z.object({
    tokensUsed: z.number().default(0),
    tokensRemaining: z.number(), // Init = job.constraints.maxTokens
    docsRetrieved: z.number().default(0),
    apiCalls: z.number().default(0),
  }),

  // Error handling
  errors: z.array(z.object({
    node: z.string(),
    message: z.string(),
    timestamp: z.string().datetime(),
    recoverable: z.boolean(),
  })).default([]),

  // Artifacts produced
  artifacts: z.array(ArtifactSchema).default([]),
});

export type GraphState = z.infer<typeof GraphStateSchema>;
```

---

## Idempotency + Locking Strategy

> Aligne avec Architecture Charter Section 4.4

```typescript
// packages/contracts/src/idempotency.ts

export interface IdempotencyConfig {
  // Key generation
  keyStrategy: 'hash' | 'composite' | 'custom';
  keyFields: string[]; // ['intent', 'scope.entityType', 'scope.entityIds']

  // Lock
  lockTTL: number;     // 300000 (5min)
  lockRetry: number;   // 3
  lockBackoff: 'linear' | 'exponential';

  // Result cache
  resultTTL: number;   // 3600000 (1h)
  resultStore: 'redis' | 'postgres';
}

export const defaultIdempotency: IdempotencyConfig = {
  keyStrategy: 'composite',
  keyFields: ['intent', 'scope.entityType', 'idempotencyKey'],
  lockTTL: 300000,
  lockRetry: 3,
  lockBackoff: 'exponential',
  resultTTL: 3600000,
  resultStore: 'redis',
};

// Helper pour créer un JobEnvelope avec idempotencyKey STABLE
export function createJobEnvelope(
  partial: Omit<JobEnvelope, 'jobId' | 'traceId' | 'idempotencyKey' | 'createdAt'>
): JobEnvelope {
  return {
    jobId: crypto.randomUUID(),
    traceId: crypto.randomUUID(),
    // RÈGLE: idempotencyKey = hash stable (PAS Date.now() !)
    // Si trigger fournit idempotencyKey, l'utiliser ; sinon hash déterministe
    idempotencyKey: stableHash({
      intent: partial.intent,
      scope: partial.scope,
      payload: partial.payload ?? {},
    }),
    createdAt: new Date().toISOString(),
    ...partial,
  };
}

// Hash stable pour idempotency (ex: SHA-256 des champs triés)
function stableHash(obj: Record<string, unknown>): string {
  const sortedJson = JSON.stringify(obj, Object.keys(obj).sort());
  // En production: utiliser crypto.subtle.digest('SHA-256', ...)
  return `idem_${Buffer.from(sortedJson).toString('base64url').slice(0, 32)}`;
}
```

---

## Security Warning: Service Role Key

```yaml
# ⚠️ DANGER: Ne JAMAIS utiliser SUPABASE_SERVICE_ROLE_KEY dans l'API exposée

Règles:
  api_publique:
    key: SUPABASE_ANON_KEY
    protection: RLS obligatoire
    expose: oui

  worker_interne:
    key: SUPABASE_SERVICE_ROLE_KEY
    protection: réseau privé + IP allowlist + vault
    expose: jamais directement
    logs: aucun secret

  edge_functions:
    key: anon ou service selon besoin
    isolation: oui (Deno runtime)
```

---

## Regle d'Or

```
MiniLo DECLENCHE -> LangGraph DECIDE -> Skills EXECUTENT -> RAG FOURNIT -> MCP GOUVERNE
```

---

_Ce document est la source de verite pour les contrats d'agents AI-COS._
