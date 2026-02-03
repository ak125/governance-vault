# AI-COS Contracts: JobEnvelope, GraphState, SkillIO

> Contrats uniques pour l'orchestration AI. Tous les composants utilisent ces types.

---

## 1. JobEnvelope (Entrée du système)

Le JobEnvelope est le contrat d'entrée pour toute exécution dans le système AI-COS.

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
  budget: z.number().optional(), // $ limit
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
  // Identité
  jobId: z.string().uuid(),
  traceId: z.string().uuid(),
  parentJobId: z.string().uuid().optional(),

  // Intent
  intent: z.nativeEnum(JobIntent),

  // Scope
  scope: JobScopeSchema,

  // Constraints
  constraints: JobConstraintsSchema,

  // Context
  context: JobContextSchema,

  // Idempotency
  idempotencyKey: z.string(),
  createdAt: z.string().datetime(),
  expiresAt: z.string().datetime().optional(),
});

export type JobEnvelope = z.infer<typeof JobEnvelopeSchema>;
export type JobScope = z.infer<typeof JobScopeSchema>;
export type JobConstraints = z.infer<typeof JobConstraintsSchema>;
```

---

## 2. GraphState (État du flow LangGraph)

Le GraphState maintient l'état de l'exécution à travers les nœuds du graphe.

```typescript
// packages/contracts/src/graph-state.ts

export const GraphStateSchema = z.object({
  // From JobEnvelope
  job: JobEnvelopeSchema,

  // Execution state
  currentNode: z.string(),
  visitedNodes: z.array(z.string()),
  retryCount: z.number().default(0),

  // Data flow
  input: z.unknown(),
  intermediate: z.record(z.unknown()),
  output: z.unknown().optional(),

  // RAG context
  ragContext: z.object({
    documents: z.array(RagDocumentSchema),
    citations: z.array(z.string()),
    truthLevel: TruthLevelSchema,
    confidence: z.number().min(0).max(1),
  }).optional(),

  // Budget tracking
  budget: z.object({
    tokensUsed: z.number(),
    tokensRemaining: z.number(),
    docsRetrieved: z.number(),
    apiCalls: z.number(),
  }),

  // Error handling
  errors: z.array(z.object({
    node: z.string(),
    message: z.string(),
    timestamp: z.string().datetime(),
    recoverable: z.boolean(),
  })),

  // Artifacts produced
  artifacts: z.array(ArtifactSchema),
});

export type GraphState = z.infer<typeof GraphStateSchema>;
```

---

## 3. Skill IO (Entrée/Sortie des Skills)

Contrats pour l'interface des skills.

```typescript
// packages/contracts/src/skill.ts

export const SkillInputSchema = z.object({
  jobId: z.string().uuid(),
  traceId: z.string().uuid(),
  params: z.record(z.unknown()),
  ragContext: RagContextSchema.optional(),
  constraints: JobConstraintsSchema,
  startTime: z.number(), // timestamp
});

export const SkillOutputSchema = z.object({
  success: z.boolean(),
  data: z.unknown().optional(),
  artifacts: z.array(ArtifactSchema),
  metrics: z.object({
    duration: z.number(),
    tokensUsed: z.number(),
    itemsProcessed: z.number(),
  }),
  nextAction: z.enum(['continue', 'retry', 'escalate', 'complete']).optional(),
});

export type SkillInput = z.infer<typeof SkillInputSchema>;
export type SkillOutput = z.infer<typeof SkillOutputSchema>;

// Handler type
export type SkillHandler = (input: SkillInput) => Promise<SkillOutput>;
```

---

## 4. Artifact Schema

Les artifacts sont les outputs persistés des skills.

```typescript
// packages/contracts/src/artifact.ts

export const ArtifactSchema = z.object({
  type: z.enum(['report', 'migration', 'content', 'code', 'config']),
  name: z.string(),
  format: z.enum(['json', 'markdown', 'sql', 'typescript', 'yaml']),
  content: z.string(),
  metadata: z.record(z.unknown()).optional(),
  createdAt: z.string().datetime(),
});

export type Artifact = z.infer<typeof ArtifactSchema>;
```

---

## 5. Idempotency & Locking Strategy

Configuration pour l'idempotence et le verrouillage distribué.

```typescript
// packages/contracts/src/idempotency.ts

export interface IdempotencyConfig {
  // Key generation
  keyStrategy: 'hash' | 'composite' | 'custom';
  keyFields: string[]; // ['intent', 'scope.entityType', 'scope.entityIds']

  // Lock
  lockTTL: number; // 300000 (5min)
  lockRetry: number; // 3
  lockBackoff: 'linear' | 'exponential';

  // Result cache
  resultTTL: number; // 3600000 (1h)
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

// Key generation helper
export function generateIdempotencyKey(envelope: JobEnvelope): string {
  const parts = [
    envelope.intent,
    envelope.scope.entityType,
    envelope.scope.entityIds?.sort().join(',') || 'all',
    new Date(envelope.createdAt).toISOString().slice(0, 10), // date part
  ];
  return crypto.createHash('sha256').update(parts.join(':')).digest('hex').slice(0, 16);
}
```

---

## 6. RAG Types

Types pour le système RAG.

```typescript
// packages/contracts/src/rag.ts

export const TruthLevelSchema = z.enum(['L1', 'L2', 'L3', 'L4']);

export const RagDocumentSchema = z.object({
  id: z.string(),
  content: z.string(),
  metadata: z.object({
    sourceId: z.string(),
    sourceType: z.enum(['supabase', 'file', 'url']),
    sourcePath: z.string(),
    domain: z.enum(['catalog', 'vehicle', 'diagnostic', 'support']),
    entity: z.string(),
    locale: z.enum(['fr', 'en']),
    truthLevel: TruthLevelSchema,
    verifiedBy: z.string().optional(),
    verifiedAt: z.string().datetime().optional(),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
  }),
  score: z.number().min(0).max(1).optional(),
});

export const RagContextSchema = z.object({
  documents: z.array(RagDocumentSchema),
  citations: z.array(z.string()),
  truthLevel: TruthLevelSchema,
  confidence: z.number().min(0).max(1),
});

export type TruthLevel = z.infer<typeof TruthLevelSchema>;
export type RagDocument = z.infer<typeof RagDocumentSchema>;
export type RagContext = z.infer<typeof RagContextSchema>;
```

---

## Truth Levels

| Level | Description | Validation | Auto-merge |
|-------|-------------|------------|------------|
| L1 | Code/Schema generated | Automated tests | Yes |
| L2 | Computed from DB | Query verification | Yes |
| L3 | RAG-sourced | Human spot-check | Manual |
| L4 | AI-generated content | Full review | Never |

---

## Voir aussi

- [[ADR-006-ai-orchestrator-architecture]] - Décision architecturale
- [[03-skills-registry]] - Registre des skills
- [[05-langgraph-router]] - Utilisation dans LangGraph

---

_Créé: 2026-02-03 | Source: Architecture Report Section 4_
