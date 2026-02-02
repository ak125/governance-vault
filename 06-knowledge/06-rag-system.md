# AI-COS RAG System (Retrieval-Augmented Generation)

> **Version**: 1.0.0 | **Status**: CANON | **Date**: 2026-01-27
> **Aligned with**: Architecture Charter v2.1.0 Section 6
> **Dependencies**: 00-agent-model.md (GraphState.ragContext), 02-loop-engine.md (Corrective-RAG)

## Objectif

Definir le systeme RAG canonique pour AI-COS, incluant Truth Levels, Hybrid Search, Chunking, et Citations.

---

## Axiome RAG

```
+=====================================================================+
||                                                                     ||
||              RAG FOURNIT, IL NE CREE PAS.                          ||
||                                                                     ||
||   Le RAG recupere des faits valides.                               ||
||   L'IA synthetise, mais ne fabrique jamais de faits.               ||
||   Pas de source = Pas de reponse.                                  ||
||                                                                     ||
+=====================================================================+
```

---

## Truth Levels (Niveaux de Verite)

### Schema Zod

```typescript
// packages/contracts/src/rag/truth-level.ts

import { z } from 'zod';

export const TruthLevelSchema = z.enum(['L1', 'L2', 'L3', 'L4']);

export type TruthLevel = z.infer<typeof TruthLevelSchema>;

export const TRUTH_LEVEL_CONFIG: Record<TruthLevel, TruthLevelConfig> = {
  L1: {
    name: 'Constructeur',
    description: 'Donnees officielles constructeur (TecDoc, ETAI)',
    autoPublish: true,
    humanReview: false,
    minConfidence: 0.95,
    sources: ['tecdoc', 'etai', 'oem_catalog'],
  },
  L2: {
    name: 'Expert Valide',
    description: 'Contenu valide par expert humain',
    autoPublish: true,
    humanReview: false,
    minConfidence: 0.85,
    sources: ['expert_review', 'validated_content', 'curated_guides'],
  },
  L3: {
    name: 'IA Supervisee',
    description: 'Genere par IA, supervise par humain',
    autoPublish: false,
    humanReview: true,
    minConfidence: 0.70,
    sources: ['ai_generated', 'semi_validated'],
  },
  L4: {
    name: 'IA Non Validee',
    description: 'Genere par IA, en attente de validation',
    autoPublish: false,
    humanReview: true,
    minConfidence: 0.50,
    sources: ['ai_draft', 'unvalidated'],
  },
};

export interface TruthLevelConfig {
  name: string;
  description: string;
  autoPublish: boolean;
  humanReview: boolean;
  minConfidence: number;
  sources: string[];
}
```

### Regles par Niveau

```
+-----------------------------------------------------------------------+
|                         TRUTH LEVELS                                   |
+-----------------------------------------------------------------------+
|                                                                        |
|  L1 - CONSTRUCTEUR (Source officielle)                                |
|  ├── Auto-publish: OUI                                                |
|  ├── Human review: NON                                                |
|  ├── Confidence min: 0.95                                             |
|  └── Ex: Specs TecDoc, Donnees ETAI, Catalogues OEM                   |
|                                                                        |
|  L2 - EXPERT VALIDE (Valide par humain)                               |
|  ├── Auto-publish: OUI                                                |
|  ├── Human review: NON (deja fait)                                    |
|  ├── Confidence min: 0.85                                             |
|  └── Ex: Guides valides, FAQ curees, Conseils experts                 |
|                                                                        |
|  L3 - IA SUPERVISEE (IA + supervision)                                |
|  ├── Auto-publish: NON                                                |
|  ├── Human review: OUI obligatoire                                    |
|  ├── Confidence min: 0.70                                             |
|  └── Ex: Descriptions generees, SEO auto, Diagnostics assists         |
|                                                                        |
|  L4 - IA NON VALIDEE (IA brut)                                        |
|  ├── Auto-publish: NON                                                |
|  ├── Human review: OUI obligatoire                                    |
|  ├── Confidence min: 0.50                                             |
|  └── Ex: Brouillons, Suggestions, Hypotheses                          |
|                                                                        |
+-----------------------------------------------------------------------+
```

---

## RAG Document Schema

### Schema Zod Complet

```typescript
// packages/contracts/src/rag/document.ts

import { z } from 'zod';
import { TruthLevelSchema } from './truth-level';

export const RagDocumentMetadataSchema = z.object({
  // Source identification
  sourceType: z.enum(['tecdoc', 'etai', 'oem', 'expert', 'ai', 'user']),
  sourcePath: z.string(),           // Ex: '/guides/freinage/plaquettes.md'
  sourceUrl: z.string().url().optional(),

  // Truth & validation
  truthLevel: TruthLevelSchema,
  validatedBy: z.string().optional(),   // User ID si L2+
  validatedAt: z.string().datetime().optional(),

  // Versioning
  version: z.string(),              // Semver: '1.0.0'
  indexVersion: z.string(),         // Index version: 'v2024.01'
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),

  // Domain context
  domain: z.enum(['product', 'vehicle', 'diagnostic', 'guide', 'faq', 'legal']),
  entities: z.array(z.object({
    type: z.enum(['gamme', 'brand', 'model', 'oem_ref', 'symptom']),
    id: z.string(),
    name: z.string().optional(),
  })).default([]),

  // Chunking info
  chunkIndex: z.number(),           // Position in parent doc
  totalChunks: z.number(),          // Total chunks in parent
  parentDocId: z.string().uuid(),   // Reference to parent

  // Search optimization
  keywords: z.array(z.string()).default([]),
  language: z.string().default('fr'),
});

export const RagDocumentSchema = z.object({
  id: z.string().uuid(),
  content: z.string(),              // Chunk content (max 500 tokens)
  embedding: z.array(z.number()).optional(), // Vector (3072 dims)
  metadata: RagDocumentMetadataSchema,

  // Retrieval stats
  retrievalCount: z.number().default(0),
  lastRetrievedAt: z.string().datetime().optional(),
  avgRelevanceScore: z.number().min(0).max(1).default(0),
});

export type RagDocument = z.infer<typeof RagDocumentSchema>;
export type RagDocumentMetadata = z.infer<typeof RagDocumentMetadataSchema>;
```

---

## Chunking Strategy

### Configuration

```typescript
// packages/contracts/src/rag/chunking.ts

export const CHUNKING_CONFIG = {
  // Token limits
  maxChunkTokens: 500,        // Max tokens per chunk
  overlapTokens: 50,          // Overlap between chunks
  minChunkTokens: 100,        // Min tokens (avoid tiny chunks)

  // Semantic boundaries
  splitOn: [
    '\n## ',                   // H2 headers
    '\n### ',                  // H3 headers
    '\n\n',                    // Double newlines
    '. ',                      // Sentences (fallback)
  ],

  // Metadata preservation
  preserveHeaders: true,       // Keep parent headers in chunk
  includeContext: true,        // Add doc title/section to chunk

  // Model config
  tokenizer: 'cl100k_base',    // OpenAI tokenizer
  embeddingModel: 'text-embedding-3-large',
  embeddingDimensions: 3072,
};
```

### Algorithme de Chunking

```typescript
// packages/rag/src/chunking/semantic-chunker.ts

export function semanticChunk(
  content: string,
  config: ChunkingConfig = CHUNKING_CONFIG
): Chunk[] {
  const chunks: Chunk[] = [];
  let currentChunk = '';
  let chunkIndex = 0;

  // 1. Split on semantic boundaries
  const sections = splitOnBoundaries(content, config.splitOn);

  for (const section of sections) {
    const sectionTokens = countTokens(section, config.tokenizer);
    const currentTokens = countTokens(currentChunk, config.tokenizer);

    // 2. If adding section exceeds limit, finalize current chunk
    if (currentTokens + sectionTokens > config.maxChunkTokens) {
      if (currentChunk.length >= config.minChunkTokens) {
        chunks.push({
          index: chunkIndex++,
          content: currentChunk.trim(),
          tokens: currentTokens,
        });
      }

      // 3. Start new chunk with overlap
      currentChunk = getOverlap(currentChunk, config.overlapTokens);
    }

    currentChunk += section;
  }

  // 4. Don't forget last chunk
  if (currentChunk.trim()) {
    chunks.push({
      index: chunkIndex,
      content: currentChunk.trim(),
      tokens: countTokens(currentChunk, config.tokenizer),
    });
  }

  return chunks;
}
```

---

## Hybrid Search (Vector + BM25)

### Architecture

```
+-----------------------------------------------------------------------+
|                        HYBRID SEARCH                                   |
+-----------------------------------------------------------------------+
|                                                                        |
|   Query: "plaquettes frein VAG 1K0615301M Golf 7"                     |
|                                                                        |
|   ┌─────────────────────────────────────────────────────────────────┐ |
|   │                     QUERY PROCESSOR                              │ |
|   │  - Tokenize                                                      │ |
|   │  - Embed (text-embedding-3-large)                               │ |
|   │  - Extract keywords                                              │ |
|   └──────────────────────────┬──────────────────────────────────────┘ |
|                              │                                        |
|              ┌───────────────┼───────────────┐                       |
|              │               │               │                       |
|              ▼               │               ▼                       |
|   ┌──────────────────┐      │      ┌──────────────────┐             |
|   │   VECTOR SEARCH  │      │      │   BM25 SEARCH    │             |
|   │   (pgvector)     │      │      │   (ts_vector)    │             |
|   │                  │      │      │                  │             |
|   │  cosine <=>      │      │      │  to_tsvector     │             |
|   │  Top-K: 20       │      │      │  Top-K: 20       │             |
|   └────────┬─────────┘      │      └────────┬─────────┘             |
|            │                │               │                        |
|            │    Results     │    Results    │                        |
|            │    [A,B,C,D]   │    [B,D,E,F]  │                        |
|            │                │               │                        |
|            └────────────────┼───────────────┘                        |
|                             │                                        |
|                             ▼                                        |
|   ┌─────────────────────────────────────────────────────────────────┐ |
|   │                  RRF FUSION                                      │ |
|   │  (Reciprocal Rank Fusion)                                       │ |
|   │                                                                  │ |
|   │  score(d) = Σ 1/(k + rank_i(d))                                 │ |
|   │  k = 60 (constant)                                              │ |
|   │                                                                  │ |
|   │  Avantage: Pas de tuning alpha!                                 │ |
|   └──────────────────────────┬──────────────────────────────────────┘ |
|                              │                                        |
|                              ▼                                        |
|   ┌─────────────────────────────────────────────────────────────────┐ |
|   │                  RERANKER (optional)                             │ |
|   │  - Cohere rerank-v3                                             │ |
|   │  - Cross-encoder scoring                                        │ |
|   └──────────────────────────┬──────────────────────────────────────┘ |
|                              │                                        |
|                              ▼                                        |
|                     Final Results [B,A,D,C,E]                        |
|                                                                        |
+-----------------------------------------------------------------------+
```

### Implementation Supabase

```sql
-- Migration: 20260127_hybrid_search.sql

-- 1. Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. RAG documents table
CREATE TABLE __rag_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL,
  embedding vector(3072),

  -- Metadata (JSONB for flexibility)
  metadata JSONB NOT NULL DEFAULT '{}',

  -- Full-text search
  content_tsv tsvector GENERATED ALWAYS AS (
    to_tsvector('french', content)
  ) STORED,

  -- Stats
  retrieval_count INTEGER DEFAULT 0,
  last_retrieved_at TIMESTAMPTZ,
  avg_relevance_score NUMERIC(3,2) DEFAULT 0,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Indexes
CREATE INDEX idx_rag_embedding ON __rag_documents
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX idx_rag_tsv ON __rag_documents
  USING gin (content_tsv);

CREATE INDEX idx_rag_metadata ON __rag_documents
  USING gin (metadata jsonb_path_ops);

-- 4. Hybrid search RPC function
CREATE OR REPLACE FUNCTION hybrid_search(
  query_text TEXT,
  query_embedding vector(3072),
  match_count INT DEFAULT 10,
  rrf_k INT DEFAULT 60
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  metadata JSONB,
  vector_rank INT,
  bm25_rank INT,
  rrf_score NUMERIC
) AS $$
WITH vector_results AS (
  SELECT
    id,
    ROW_NUMBER() OVER (ORDER BY embedding <=> query_embedding) AS rank
  FROM __rag_documents
  ORDER BY embedding <=> query_embedding
  LIMIT match_count * 2
),
bm25_results AS (
  SELECT
    id,
    ROW_NUMBER() OVER (ORDER BY ts_rank(content_tsv, plainto_tsquery('french', query_text)) DESC) AS rank
  FROM __rag_documents
  WHERE content_tsv @@ plainto_tsquery('french', query_text)
  LIMIT match_count * 2
),
combined AS (
  SELECT
    COALESCE(v.id, b.id) AS id,
    v.rank AS vector_rank,
    b.rank AS bm25_rank,
    -- RRF: score = 1/(k + rank_vector) + 1/(k + rank_bm25)
    COALESCE(1.0 / (rrf_k + v.rank), 0) +
    COALESCE(1.0 / (rrf_k + b.rank), 0) AS rrf_score
  FROM vector_results v
  FULL OUTER JOIN bm25_results b ON v.id = b.id
)
SELECT
  d.id,
  d.content,
  d.metadata,
  c.vector_rank::INT,
  c.bm25_rank::INT,
  c.rrf_score
FROM combined c
JOIN __rag_documents d ON c.id = d.id
ORDER BY c.rrf_score DESC
LIMIT match_count;
$$ LANGUAGE sql STABLE;
```

### TypeScript Wrapper

```typescript
// packages/rag/src/search/hybrid-search.ts

import { SupabaseClient } from '@supabase/supabase-js';

export interface HybridSearchOptions {
  query: string;
  maxResults?: number;
  minScore?: number;
  truthLevelFilter?: TruthLevel[];
  domainFilter?: string[];
  rerank?: boolean;
}

export interface HybridSearchResult {
  document: RagDocument;
  vectorRank: number | null;
  bm25Rank: number | null;
  rrfScore: number;
  finalScore: number;  // After reranking
}

export async function hybridSearch(
  supabase: SupabaseClient,
  embedder: Embedder,
  options: HybridSearchOptions
): Promise<HybridSearchResult[]> {
  const {
    query,
    maxResults = 10,
    minScore = 0.01,
    truthLevelFilter,
    domainFilter,
    rerank = true,
  } = options;

  // 1. Generate query embedding
  const queryEmbedding = await embedder.embed(query);

  // 2. Call hybrid search RPC
  const { data, error } = await supabase.rpc('hybrid_search', {
    query_text: query,
    query_embedding: queryEmbedding,
    match_count: maxResults * 2, // Get more for filtering
    rrf_k: 60,
  });

  if (error) throw new Error(`Hybrid search failed: ${error.message}`);

  // 3. Apply filters
  let results = data.filter((r: any) => r.rrf_score >= minScore);

  if (truthLevelFilter?.length) {
    results = results.filter((r: any) =>
      truthLevelFilter.includes(r.metadata.truthLevel)
    );
  }

  if (domainFilter?.length) {
    results = results.filter((r: any) =>
      domainFilter.includes(r.metadata.domain)
    );
  }

  // 4. Optional reranking
  if (rerank && results.length > 0) {
    results = await rerankResults(query, results);
  }

  // 5. Limit and return
  return results.slice(0, maxResults).map((r: any) => ({
    document: {
      id: r.id,
      content: r.content,
      metadata: r.metadata,
    },
    vectorRank: r.vector_rank,
    bm25Rank: r.bm25_rank,
    rrfScore: r.rrf_score,
    finalScore: r.final_score ?? r.rrf_score,
  }));
}
```

---

## Citation Format

### Schema

```typescript
// packages/contracts/src/rag/citation.ts

import { z } from 'zod';

export const CitationSchema = z.object({
  // Reference
  documentId: z.string().uuid(),
  chunkIndex: z.number(),

  // Source info
  sourcePath: z.string(),
  sourceType: z.string(),
  truthLevel: TruthLevelSchema,

  // Quote
  quotedText: z.string().max(500),
  startOffset: z.number(),
  endOffset: z.number(),

  // Display
  displayText: z.string(),        // Ex: "[1] Guide Freinage, Section 2.1"
  url: z.string().url().optional(),
});

export type Citation = z.infer<typeof CitationSchema>;
```

### Format Standard

```
+-----------------------------------------------------------------------+
|                      CITATION FORMAT                                   |
+-----------------------------------------------------------------------+
|                                                                        |
|  Format inline:                                                        |
|  "Les plaquettes de frein doivent etre remplacees tous les            |
|   30 000 km en moyenne [1]."                                          |
|                                                                        |
|  Format references:                                                    |
|  [1] Guide Freinage - Section 2.1 (L1 - TecDoc)                       |
|      URL: /guides/freinage/plaquettes                                 |
|      "Les plaquettes ceramiques offrent une duree de vie..."          |
|                                                                        |
|  Format JSON:                                                          |
|  {                                                                     |
|    "index": 1,                                                        |
|    "source": "Guide Freinage",                                        |
|    "section": "2.1",                                                  |
|    "truthLevel": "L1",                                                |
|    "quote": "Les plaquettes ceramiques...",                          |
|    "url": "/guides/freinage/plaquettes"                              |
|  }                                                                     |
|                                                                        |
+-----------------------------------------------------------------------+
```

### Citation Builder

```typescript
// packages/rag/src/citation/citation-builder.ts

export function buildCitation(
  doc: RagDocument,
  quotedText: string,
  index: number
): Citation {
  return {
    documentId: doc.id,
    chunkIndex: doc.metadata.chunkIndex,
    sourcePath: doc.metadata.sourcePath,
    sourceType: doc.metadata.sourceType,
    truthLevel: doc.metadata.truthLevel,
    quotedText: quotedText.slice(0, 500),
    startOffset: doc.content.indexOf(quotedText),
    endOffset: doc.content.indexOf(quotedText) + quotedText.length,
    displayText: formatCitationDisplay(doc, index),
    url: doc.metadata.sourceUrl,
  };
}

function formatCitationDisplay(doc: RagDocument, index: number): string {
  const levelLabel = TRUTH_LEVEL_CONFIG[doc.metadata.truthLevel].name;
  const source = doc.metadata.sourcePath.split('/').pop()?.replace('.md', '');
  return `[${index}] ${source} (${levelLabel})`;
}
```

---

## Versioning

### Document Versioning

```typescript
// packages/contracts/src/rag/versioning.ts

export const RAG_VERSION_CONFIG = {
  // Index version format: YYYY.MM.patch
  currentIndexVersion: '2026.01.0',

  // Document version format: semver
  documentVersionFormat: /^\d+\.\d+\.\d+$/,

  // Retention
  keepPreviousVersions: 3,
  archiveOlderThan: 90, // days

  // Reindex triggers
  reindexOn: [
    'embedding_model_change',
    'chunking_config_change',
    'schema_migration',
  ],
};

export interface DocumentVersion {
  version: string;           // '1.2.0'
  indexVersion: string;      // '2026.01.0'
  createdAt: string;
  changes: string[];
  previousVersionId?: string;
}
```

### Index Versioning

```sql
-- Migration: 20260127_rag_versioning.sql

-- Version history table
CREATE TABLE __rag_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES __rag_documents(id),
  version TEXT NOT NULL,
  index_version TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding vector(3072),
  metadata JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(document_id, version)
);

-- Auto-version on update
CREATE OR REPLACE FUNCTION archive_rag_version()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO __rag_versions (document_id, version, index_version, content, embedding, metadata)
  VALUES (
    OLD.id,
    OLD.metadata->>'version',
    OLD.metadata->>'indexVersion',
    OLD.content,
    OLD.embedding,
    OLD.metadata
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_archive_rag_version
  BEFORE UPDATE ON __rag_documents
  FOR EACH ROW
  WHEN (OLD.content IS DISTINCT FROM NEW.content)
  EXECUTE FUNCTION archive_rag_version();
```

---

## RagContext (Export pour GraphState)

```typescript
// packages/contracts/src/rag/index.ts
// Re-export all RAG types for use in GraphState

export { TruthLevelSchema, TruthLevel, TRUTH_LEVEL_CONFIG } from './truth-level';
export { RagDocumentSchema, RagDocument, RagDocumentMetadata } from './document';
export { CitationSchema, Citation } from './citation';
export { CHUNKING_CONFIG } from './chunking';
export { RAG_VERSION_CONFIG } from './versioning';

// RagContext type for GraphState
export interface RagContext {
  documents: RagDocument[];
  citations: Citation[];
  truthLevel: TruthLevel;      // Lowest truth level in context
  confidence: number;          // 0-1, based on relevance scores
  searchMethod: 'vector' | 'bm25' | 'hybrid';
  indexVersion: string;
}
```

---

## Anti-Patterns RAG

```typescript
// ANTI-PATTERN 1: Generer sans source
// WRONG:
if (ragContext.documents.length === 0) {
  return generateFromLLM(query); // Hallucination!
}

// CORRECT:
if (ragContext.documents.length === 0) {
  return {
    success: false,
    error: 'NO_RELEVANT_SOURCES',
    message: 'Aucune source pertinente trouvee',
  };
}

// ANTI-PATTERN 2: Ignorer le Truth Level
// WRONG:
const allDocs = await search(query);

// CORRECT:
const docs = await search(query, {
  truthLevelFilter: ['L1', 'L2'], // Production only
});

// ANTI-PATTERN 3: Pas de citations
// WRONG:
return { answer: "Les plaquettes durent 30000 km." };

// CORRECT:
return {
  answer: "Les plaquettes durent 30000 km [1].",
  citations: [{ index: 1, source: 'Guide Freinage', ... }],
};

// ANTI-PATTERN 4: Vector-only search
// WRONG (pour references techniques):
const results = await vectorSearch("VAG 1K0615301M");

// CORRECT:
const results = await hybridSearch("VAG 1K0615301M"); // BM25 capte exact match
```

---

## Regles d'Or RAG

```
+=========================================================================+
|                          RAG GOLDEN RULES                               |
+=========================================================================+
|                                                                          |
|  R1  PAS DE SOURCE = PAS DE REPONSE (Anti-hallucination)               |
|  R2  TRUTH LEVEL L1/L2 UNIQUEMENT EN PRODUCTION                        |
|  R3  TOUTE REPONSE DOIT AVOIR DES CITATIONS                            |
|  R4  HYBRID SEARCH POUR REFERENCES TECHNIQUES                          |
|  R5  CHUNKING MAX 500 TOKENS AVEC 50 OVERLAP                           |
|  R6  VERSIONING OBLIGATOIRE (document + index)                         |
|                                                                          |
+=========================================================================+
```

---

## Integration avec GraphState

```typescript
// Exemple d'utilisation dans 00-agent-model.md GraphState

import {
  RagDocumentSchema,
  TruthLevelSchema,
  RagContext
} from './rag';

export const GraphStateSchema = z.object({
  // ... autres champs ...

  ragContext: z.object({
    documents: z.array(RagDocumentSchema),
    citations: z.array(CitationSchema),
    truthLevel: TruthLevelSchema,
    confidence: z.number().min(0).max(1),
    searchMethod: z.enum(['vector', 'bm25', 'hybrid']),
    indexVersion: z.string(),
  }).optional(),
});
```

---

_Ce document est la source de verite pour le systeme RAG AI-COS._
