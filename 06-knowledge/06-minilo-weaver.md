# MiniLo/Weaver: Triggers & Job Management

> Système de déclenchement et de gestion des jobs AI-COS.

---

## 1. Triggers

### Types de Triggers

```typescript
// packages/minilo-weaver/src/triggers/trigger.types.ts

export type TriggerType = 'cron' | 'webhook' | 'event' | 'manual';

export interface TriggerConfig {
  type: TriggerType;
  name: string;
  enabled: boolean;

  // Cron specific
  cron?: {
    expression: string; // '0 2 * * *' = 2am daily
    timezone: string;   // 'Europe/Paris'
  };

  // Webhook specific
  webhook?: {
    path: string;
    method: 'POST' | 'PUT';
    secret?: string;
  };

  // Event specific
  event?: {
    source: string;   // 'supabase', 'redis', 'kafka'
    pattern: string;  // 'product.updated', 'seo.*'
  };

  // Intent mapping
  intentMapping: Record<string, JobIntent>;
  scopeCalculator: (payload: unknown) => JobScope;
}
```

### Exemples de Configuration

```typescript
// packages/minilo-weaver/src/triggers/configs.ts

export const triggerConfigs: TriggerConfig[] = [
  // Daily SEO audit at 2am
  {
    type: 'cron',
    name: 'daily_seo_audit',
    enabled: true,
    cron: {
      expression: '0 2 * * *',
      timezone: 'Europe/Paris',
    },
    intentMapping: { default: JobIntent.SEO_AUDIT },
    scopeCalculator: () => ({
      entityType: 'page',
      filters: { updatedSince: getYesterday() },
      limit: 1000,
    }),
  },

  // Webhook for content updates
  {
    type: 'webhook',
    name: 'content_webhook',
    enabled: true,
    webhook: {
      path: '/api/triggers/content',
      method: 'POST',
      secret: process.env.WEBHOOK_SECRET,
    },
    intentMapping: {
      'create': JobIntent.CONTENT_GENERATE,
      'update': JobIntent.RAG_REINDEX,
    },
    scopeCalculator: (payload: any) => ({
      entityType: 'article',
      entityIds: [payload.articleId],
    }),
  },

  // Event-driven RAG reindex
  {
    type: 'event',
    name: 'product_update_reindex',
    enabled: true,
    event: {
      source: 'supabase',
      pattern: 'product.*',
    },
    intentMapping: {
      'product.created': JobIntent.RAG_REINDEX,
      'product.updated': JobIntent.RAG_REINDEX,
    },
    scopeCalculator: (event: any) => ({
      entityType: 'product',
      entityIds: [event.record.id],
    }),
  },
];
```

---

## 2. Scope Calculator

### Interface

```typescript
// packages/minilo-weaver/src/scope/calculator.ts

export async function calculateScope(
  trigger: TriggerConfig,
  payload: unknown
): Promise<JobScope> {
  switch (trigger.type) {
    case 'cron':
      // Full scope based on schedule
      return {
        entityType: 'all',
        filters: { updatedSince: getLastRunTime(trigger.name) },
        limit: 1000,
      };

    case 'webhook':
      // Scope from webhook payload
      return trigger.scopeCalculator(payload);

    case 'event':
      // Scope from event data
      const event = payload as DomainEvent;
      return {
        entityType: event.entityType as any,
        entityIds: [event.entityId],
      };

    case 'manual':
      // Explicit scope from request
      return (payload as ManualTriggerPayload).scope;

    default:
      throw new Error(`Unknown trigger type: ${trigger.type}`);
  }
}
```

### Bounded Scope Rule

```typescript
// IMPORTANT: Always bound scope to prevent runaway jobs

export function validateScope(scope: JobScope): JobScope {
  // Enforce maximum limit
  const MAX_LIMIT = 10000;

  if (!scope.limit || scope.limit > MAX_LIMIT) {
    console.warn(`Scope limit capped from ${scope.limit} to ${MAX_LIMIT}`);
    scope.limit = MAX_LIMIT;
  }

  // Require filter for 'all' entityType
  if (scope.entityType === 'all' && !scope.filters) {
    throw new Error('Scope with entityType=all requires filters');
  }

  return scope;
}
```

---

## 3. Job Manager

### Core Implementation

```typescript
// packages/minilo-weaver/src/job-manager/manager.ts

export class JobManager {
  constructor(
    private redis: Redis,
    private db: SupabaseClient,
    private orchestrator: RouterGraph,
    private logger: Logger,
  ) {}

  async enqueue(envelope: JobEnvelope): Promise<string> {
    // 1. Check idempotency
    const existingResult = await this.checkIdempotency(envelope.idempotencyKey);
    if (existingResult) {
      this.logger.log(`Job already exists: ${envelope.idempotencyKey}`);
      return existingResult.jobId;
    }

    // 2. Acquire distributed lock
    const lock = await this.acquireLock(envelope.idempotencyKey);
    if (!lock) {
      throw new Error('Failed to acquire job lock - job may be running');
    }

    try {
      // 3. Persist job to database
      await this.persistJob(envelope);

      // 4. Execute via orchestrator
      const result = await this.orchestrator.invoke({
        job: envelope,
        currentNode: 'start',
        visitedNodes: [],
        errors: [],
        artifacts: [],
        retryCount: 0,
        budget: {
          tokensUsed: 0,
          tokensRemaining: envelope.constraints.maxTokens,
          docsRetrieved: 0,
          apiCalls: 0,
        },
      });

      // 5. Store result for idempotency
      await this.storeResult(envelope.jobId, result);

      // 6. Log completion
      this.logger.log(`Job completed: ${envelope.jobId}`);

      return envelope.jobId;

    } catch (error) {
      // 7. Handle failure
      await this.handleFailure(envelope, error);
      throw error;

    } finally {
      // 8. Always release lock
      await this.releaseLock(lock);
    }
  }

  private async checkIdempotency(key: string): Promise<JobResult | null> {
    const cached = await this.redis.get(`job:result:${key}`);
    return cached ? JSON.parse(cached) : null;
  }

  private async acquireLock(key: string): Promise<Lock | null> {
    const lockKey = `job:lock:${key}`;
    const acquired = await this.redis.set(lockKey, 'locked', 'NX', 'PX', 300000);
    return acquired ? { key: lockKey } : null;
  }

  private async releaseLock(lock: Lock): Promise<void> {
    await this.redis.del(lock.key);
  }

  private async persistJob(envelope: JobEnvelope): Promise<void> {
    await this.db.from('ai_jobs').insert({
      id: envelope.jobId,
      trace_id: envelope.traceId,
      intent: envelope.intent,
      scope: envelope.scope,
      constraints: envelope.constraints,
      context: envelope.context,
      status: 'running',
      created_at: envelope.createdAt,
    });
  }

  private async storeResult(jobId: string, result: GraphState): Promise<void> {
    // Update database
    await this.db.from('ai_jobs').update({
      status: result.errors.length > 0 ? 'failed' : 'completed',
      output: result.output,
      artifacts: result.artifacts,
      errors: result.errors,
      completed_at: new Date().toISOString(),
    }).eq('id', jobId);

    // Cache for idempotency
    const key = result.job?.idempotencyKey;
    if (key) {
      await this.redis.set(
        `job:result:${key}`,
        JSON.stringify({ jobId, status: 'completed' }),
        'EX',
        3600 // 1 hour
      );
    }
  }

  private async handleFailure(envelope: JobEnvelope, error: Error): Promise<void> {
    const retryCount = await this.getRetryCount(envelope.jobId);

    if (retryCount < 3) {
      // Exponential backoff retry
      const delay = Math.pow(2, retryCount) * 1000;
      this.logger.log(`Scheduling retry ${retryCount + 1} in ${delay}ms`);
      await this.scheduleRetry(envelope, delay);
    } else {
      // Send to dead letter queue
      this.logger.error(`Job exhausted retries, sending to DLQ: ${envelope.jobId}`);
      await this.sendToDeadLetter(envelope, error);
    }

    // Update status
    await this.db.from('ai_jobs').update({
      status: retryCount >= 3 ? 'dead_letter' : 'retrying',
      errors: [{ message: error.message, timestamp: new Date().toISOString() }],
    }).eq('id', envelope.jobId);
  }

  private async sendToDeadLetter(envelope: JobEnvelope, error: Error): Promise<void> {
    await this.db.from('ai_jobs_dlq').insert({
      job_id: envelope.jobId,
      envelope,
      error: error.message,
      stack: error.stack,
      created_at: new Date().toISOString(),
    });
  }
}
```

---

## 4. Anti-Patterns MiniLo

> Ces patterns sont INTERDITS. Voir [[ai-skill-antipatterns]] pour la liste complète.

### ❌ ANTI-PATTERN 1: Direct execution without envelope

```typescript
// WRONG:
await skillRegistry.execute('seo_audit', { urls: ['...'] });

// CORRECT:
await jobManager.enqueue(createJobEnvelope({
  intent: 'seo_audit',
  scope: { entityType: 'page', entityIds: ['...'] },
}));
```

### ❌ ANTI-PATTERN 2: Scope calculation in trigger

```typescript
// WRONG:
triggers.on('product.updated', async (event) => {
  const relatedProducts = await db.query('...'); // NO DB in trigger!
  await jobManager.enqueue({ scope: { entityIds: relatedProducts } });
});

// CORRECT:
triggers.on('product.updated', async (event) => {
  await jobManager.enqueue({
    intent: 'product_sync',
    scope: scopeCalculator.fromEvent(event), // Delegated
  });
});
```

### ❌ ANTI-PATTERN 3: Ignoring idempotency

```typescript
// WRONG:
await jobManager.enqueue(envelope); // No idempotency key

// CORRECT:
await jobManager.enqueue({
  ...envelope,
  idempotencyKey: `${envelope.intent}:${hash(envelope.scope)}:${dateKey}`,
});
```

### ❌ ANTI-PATTERN 4: Unbounded scope

```typescript
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

## 5. Database Schema

```sql
-- Table for job tracking
CREATE TABLE ai_jobs (
  id UUID PRIMARY KEY,
  trace_id UUID NOT NULL,
  intent VARCHAR(50) NOT NULL,
  scope JSONB NOT NULL,
  constraints JSONB NOT NULL,
  context JSONB NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  output JSONB,
  artifacts JSONB,
  errors JSONB,
  created_at TIMESTAMPTZ NOT NULL,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);

-- Dead letter queue
CREATE TABLE ai_jobs_dlq (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES ai_jobs(id),
  envelope JSONB NOT NULL,
  error TEXT NOT NULL,
  stack TEXT,
  created_at TIMESTAMPTZ NOT NULL
);

-- Indexes
CREATE INDEX idx_ai_jobs_status ON ai_jobs(status);
CREATE INDEX idx_ai_jobs_intent ON ai_jobs(intent);
CREATE INDEX idx_ai_jobs_created ON ai_jobs(created_at);
```

---

## Voir aussi

- [[02-ai-cos-contracts]] - JobEnvelope schema
- [[05-langgraph-router]] - Orchestration target
- [[ai-skill-antipatterns]] - Full anti-patterns list

---

_Créé: 2026-02-03 | Source: Architecture Report Section 8_
