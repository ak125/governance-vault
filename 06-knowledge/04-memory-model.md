# AI-COS Memory Model (Systeme de Memoire)

> **Version**: 1.0.0 | **Status**: CANON | **Date**: 2026-01-27

## Objectif

Definir le modele de memoire pour les agents AI-COS, incluant memoire court-terme, long-terme et partagee.

---

## Architecture Memoire

```
+-----------------------------------------------------------------------+
|                          MEMORY ARCHITECTURE                           |
+-----------------------------------------------------------------------+
|                                                                        |
|  +------------------+    +------------------+    +------------------+  |
|  |   SHORT-TERM    |    |    LONG-TERM     |    |     SHARED       |  |
|  |    (Context)    |    |   (Persistent)   |    |  (Inter-Agent)   |  |
|  +------------------+    +------------------+    +------------------+  |
|  |                  |    |                  |    |                  |  |
|  | Context Window   |    | Supabase Tables  |    | Redis Pub/Sub   |  |
|  | Max 200k tokens  |    | Vector Store     |    | Namespaced KV   |  |
|  | Session-scoped   |    | Graph DB         |    | Event Bus       |  |
|  |                  |    |                  |    |                  |  |
|  +------------------+    +------------------+    +------------------+  |
|           |                      |                      |             |
|           v                      v                      v             |
|  +------------------------------------------------------------------+ |
|  |                      MEMORY COORDINATOR                          | |
|  |   - Sync between layers                                          | |
|  |   - Eviction policies                                            | |
|  |   - Consistency guarantees                                       | |
|  +------------------------------------------------------------------+ |
|                                                                        |
+-----------------------------------------------------------------------+
```

---

## Schema Memory Contract

```yaml
Memory:
  # ===================================================================
  # SHORT-TERM MEMORY (Context Window)
  # ===================================================================
  short_term:
    enabled: boolean              # Actif ou non
    max_tokens: number            # Limite tokens (ex: 100000)
    eviction_policy: EvictionPolicy  # lru | fifo | priority

    segments:
      - segment_id: string        # Ex: "conversation"
        priority: number          # 1=highest
        max_tokens: number        # Limite par segment
        retention: Retention      # session | task | persistent

    summarization:
      enabled: boolean            # Auto-resume actif ?
      trigger_threshold: number   # % de max_tokens pour declencher
      strategy: SummarizeStrategy # extractive | abstractive | hybrid

  # ===================================================================
  # LONG-TERM MEMORY (Persistent Storage)
  # ===================================================================
  long_term:
    enabled: boolean
    storage_backends:
      - backend_id: string        # Ex: "supabase_main"
        type: StorageType         # supabase | redis | vector | graph
        config:
          connection_string: string
          table_prefix: string    # Ex: "__aicos_memory_"

    schemas:
      - schema_id: string         # Ex: "agent_state"
        backend: string           # Ref to backend_id
        structure: object         # JSON Schema
        indexes: string[]         # Colonnes indexees
        ttl_days: number          # Retention (0 = forever)

    sync:
      strategy: SyncStrategy      # write_through | write_back | read_through
      conflict_resolution: ConflictRes  # last_write | merge | manual

  # ===================================================================
  # SHARED MEMORY (Inter-Agent)
  # ===================================================================
  shared:
    enabled: boolean
    namespaces:
      - namespace: string         # Ex: "seo:audit"
        access_level: AccessLevel # read | write | admin
        agents_allowed: string[]  # Agent IDs autorises

    pubsub:
      enabled: boolean
      channels:
        - channel: string         # Ex: "aicos:events"
          pattern: string         # Pattern de subscription

    coordination:
      lock_strategy: LockStrategy # pessimistic | optimistic | none
      lock_timeout_ms: number     # Timeout pour locks
      retry_count: number         # Retries si lock echoue

  # ===================================================================
  # VECTOR MEMORY (Semantic Search)
  # ===================================================================
  vector:
    enabled: boolean
    embeddings:
      model: string               # Ex: "text-embedding-3-large"
      dimensions: number          # Ex: 3072

    collections:
      - collection_id: string     # Ex: "knowledge_base"
        description: string
        metadata_schema: object   # Metadata structure
        similarity_metric: Metric # cosine | euclidean | dot

    retrieval:
      top_k: number               # Nombre de resultats
      similarity_threshold: number # Score minimum
      rerank_enabled: boolean     # Reranking actif ?
      rerank_model: string        # Modele de rerank

  # ===================================================================
  # GRAPH MEMORY (Relations)
  # ===================================================================
  graph:
    enabled: boolean
    nodes:
      - type: string              # Ex: "Agent", "Task", "Decision"
        properties: string[]      # Proprietes du node

    edges:
      - type: string              # Ex: "DEPENDS_ON", "CREATED_BY"
        from_node: string
        to_node: string
        properties: string[]

    queries:
      - query_id: string          # Ex: "get_agent_dependencies"
        cypher: string            # Requete Cypher/GQL
```

---

## Enums

```typescript
enum EvictionPolicy {
  LRU = 'lru',           // Least Recently Used
  FIFO = 'fifo',         // First In First Out
  PRIORITY = 'priority'  // Based on priority score
}

enum Retention {
  SESSION = 'session',     // Cleared after session
  TASK = 'task',           // Cleared after task
  PERSISTENT = 'persistent' // Never cleared auto
}

enum SummarizeStrategy {
  EXTRACTIVE = 'extractive',   // Key sentences
  ABSTRACTIVE = 'abstractive', // Rewrite
  HYBRID = 'hybrid'            // Both
}

enum StorageType {
  SUPABASE = 'supabase',
  REDIS = 'redis',
  VECTOR = 'vector',
  GRAPH = 'graph'
}

enum SyncStrategy {
  WRITE_THROUGH = 'write_through',  // Sync on write
  WRITE_BACK = 'write_back',        // Async write
  READ_THROUGH = 'read_through'     // Sync on read
}

enum ConflictRes {
  LAST_WRITE = 'last_write',
  MERGE = 'merge',
  MANUAL = 'manual'
}

enum AccessLevel {
  READ = 'read',
  WRITE = 'write',
  ADMIN = 'admin'
}

enum LockStrategy {
  PESSIMISTIC = 'pessimistic',
  OPTIMISTIC = 'optimistic',
  NONE = 'none'
}

enum Metric {
  COSINE = 'cosine',
  EUCLIDEAN = 'euclidean',
  DOT = 'dot'
}
```

---

## Exemple: Configuration Memoire Agent SEO

```yaml
Memory:
  short_term:
    enabled: true
    max_tokens: 100000
    eviction_policy: priority

    segments:
      - segment_id: "task_context"
        priority: 1
        max_tokens: 50000
        retention: task
      - segment_id: "conversation"
        priority: 2
        max_tokens: 30000
        retention: session
      - segment_id: "reference_data"
        priority: 3
        max_tokens: 20000
        retention: persistent

    summarization:
      enabled: true
      trigger_threshold: 80
      strategy: hybrid

  long_term:
    enabled: true
    storage_backends:
      - backend_id: "supabase_main"
        type: supabase
        config:
          connection_string: "${SUPABASE_URL}"
          table_prefix: "__aicos_memory_"

    schemas:
      - schema_id: "seo_audit_history"
        backend: "supabase_main"
        structure:
          type: object
          properties:
            audit_id: { type: string }
            agent_id: { type: string }
            timestamp: { type: string, format: date-time }
            results: { type: object }
            score: { type: number }
        indexes: ["agent_id", "timestamp"]
        ttl_days: 90

    sync:
      strategy: write_through
      conflict_resolution: last_write

  shared:
    enabled: true
    namespaces:
      - namespace: "seo:audit"
        access_level: write
        agents_allowed: ["agent.seo.*"]
      - namespace: "seo:scores"
        access_level: read
        agents_allowed: ["*"]

    pubsub:
      enabled: true
      channels:
        - channel: "aicos:seo:violations"
          pattern: "seo.violation.*"

    coordination:
      lock_strategy: optimistic
      lock_timeout_ms: 5000
      retry_count: 3

  vector:
    enabled: true
    embeddings:
      model: "text-embedding-3-large"
      dimensions: 3072

    collections:
      - collection_id: "seo_knowledge"
        description: "SEO rules and best practices"
        metadata_schema:
          type: object
          properties:
            source: { type: string }
            category: { type: string }
            updated_at: { type: string }
        similarity_metric: cosine

    retrieval:
      top_k: 10
      similarity_threshold: 0.7
      rerank_enabled: true
      rerank_model: "cohere-rerank-v3"

  graph:
    enabled: false
```

---

## Tables Supabase (Schema)

```sql
-- Table: __aicos_memory_short_term
CREATE TABLE __aicos_memory_short_term (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  segment_id TEXT NOT NULL,
  content JSONB NOT NULL,
  tokens INTEGER NOT NULL,
  priority INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  CONSTRAINT fk_agent FOREIGN KEY (agent_id) REFERENCES __aicos_agents(id)
);

CREATE INDEX idx_memory_st_agent ON __aicos_memory_short_term(agent_id);
CREATE INDEX idx_memory_st_session ON __aicos_memory_short_term(session_id);
CREATE INDEX idx_memory_st_expires ON __aicos_memory_short_term(expires_at);

-- Table: __aicos_memory_long_term
CREATE TABLE __aicos_memory_long_term (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,
  schema_id TEXT NOT NULL,
  key TEXT NOT NULL,
  value JSONB NOT NULL,
  metadata JSONB,
  version INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  UNIQUE(agent_id, schema_id, key)
);

CREATE INDEX idx_memory_lt_agent ON __aicos_memory_long_term(agent_id);
CREATE INDEX idx_memory_lt_schema ON __aicos_memory_long_term(schema_id);

-- Table: __aicos_memory_shared
CREATE TABLE __aicos_memory_shared (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  namespace TEXT NOT NULL,
  key TEXT NOT NULL,
  value JSONB NOT NULL,
  owner_agent_id TEXT,
  lock_holder TEXT,
  lock_expires_at TIMESTAMPTZ,
  version INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(namespace, key)
);

CREATE INDEX idx_memory_sh_namespace ON __aicos_memory_shared(namespace);
CREATE INDEX idx_memory_sh_lock ON __aicos_memory_shared(lock_holder);
```

---

## Interface TypeScript

```typescript
// packages/contracts/src/memory.ts

export interface MemoryContract {
  readonly config: MemoryConfig;

  // Short-term
  getContext(segmentId: string): Promise<ContextData>;
  setContext(segmentId: string, data: ContextData): Promise<void>;
  summarize(segmentId: string): Promise<string>;

  // Long-term
  persist(schemaId: string, key: string, value: unknown): Promise<void>;
  retrieve(schemaId: string, key: string): Promise<unknown>;
  query(schemaId: string, filter: QueryFilter): Promise<unknown[]>;

  // Shared
  publish(channel: string, event: Event): Promise<void>;
  subscribe(channel: string, handler: EventHandler): Subscription;
  lock(namespace: string, key: string): Promise<Lock>;
  unlock(lock: Lock): Promise<void>;

  // Vector
  embed(text: string): Promise<number[]>;
  search(query: string, collection: string): Promise<SearchResult[]>;
  upsert(collection: string, doc: Document): Promise<void>;
}

export interface ContextData {
  segmentId: string;
  content: unknown;
  tokens: number;
  createdAt: Date;
  expiresAt?: Date;
}

export interface SearchResult {
  id: string;
  content: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface Lock {
  id: string;
  namespace: string;
  key: string;
  acquiredAt: Date;
  expiresAt: Date;
  release(): Promise<void>;
}
```

---

## Regles de Validation

### R1: Tout acces memoire DOIT etre trace

```typescript
// OBLIGATOIRE
const data = await memory.retrieve('schema', 'key');
// Auto-logged: { agent_id, operation: 'retrieve', schema, key, timestamp }
```

### R2: Les locks DOIVENT avoir un timeout

```typescript
// OBLIGATOIRE
const lock = await memory.lock('ns', 'key'); // Max 5000ms par defaut
// Auto-release si timeout
```

### R3: La memoire partagee DOIT respecter les namespaces

```typescript
// INTERDIT si agent pas dans agents_allowed
await memory.shared.set('seo:audit', 'key', data);
// Throws: AccessDeniedError
```

---

_Ce document est la source de verite pour le modele de memoire AI-COS._
