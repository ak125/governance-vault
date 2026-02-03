# RAG System: Chunking, Hybrid Search, Citations

> Système RAG standalone avec anti-hallucination et truth levels.

---

## 1. Chunking Strategy

### Configuration

```typescript
// packages/rag/src/ingestion/chunker.ts

export interface ChunkConfig {
  strategy: 'fixed' | 'semantic' | 'hybrid';
  maxTokens: 512;
  overlap: 50;
  separators: ['\n\n', '\n', '. ', ' '];
}

export interface Chunk {
  id: string;
  content: string;
  metadata: ChunkMetadata;
  embedding?: number[];
}

export interface ChunkMetadata {
  // Source tracking
  sourceId: string;
  sourceType: 'supabase' | 'file' | 'url';
  sourcePath: string;

  // Position
  chunkIndex: number;
  totalChunks: number;
  startOffset: number;
  endOffset: number;

  // Domain context
  domain: 'catalog' | 'vehicle' | 'diagnostic' | 'support';
  entity: string; // e.g., 'embrayage', 'peugeot-308'
  locale: 'fr' | 'en';

  // Truth level
  truthLevel: TruthLevel;
  verifiedBy?: string;
  verifiedAt?: string;

  // Freshness
  createdAt: string;
  updatedAt: string;
  expiresAt?: string;
}
```

### Chunking Implementation

```typescript
export async function chunkDocument(
  doc: Document,
  config: ChunkConfig
): Promise<Chunk[]> {
  const chunks: Chunk[] = [];
  let currentOffset = 0;

  // Split by separators
  const segments = splitBySeparators(doc.content, config.separators);

  // Merge until maxTokens
  let currentChunk = '';
  let chunkStart = 0;

  for (const segment of segments) {
    const tokenCount = countTokens(currentChunk + segment);

    if (tokenCount > config.maxTokens && currentChunk) {
      // Save current chunk
      chunks.push(createChunk(
        currentChunk,
        doc,
        chunks.length,
        chunkStart,
        currentOffset
      ));

      // Start new chunk with overlap
      currentChunk = getOverlap(currentChunk, config.overlap) + segment;
      chunkStart = currentOffset - config.overlap;
    } else {
      currentChunk += segment;
    }

    currentOffset += segment.length;
  }

  // Don't forget last chunk
  if (currentChunk) {
    chunks.push(createChunk(currentChunk, doc, chunks.length, chunkStart, currentOffset));
  }

  // Add total count to all chunks
  return chunks.map(c => ({
    ...c,
    metadata: { ...c.metadata, totalChunks: chunks.length }
  }));
}
```

---

## 2. Hybrid Search

### Configuration

```typescript
// packages/rag/src/retrieval/search.ts

export interface SearchConfig {
  // Search type
  mode: 'vector' | 'keyword' | 'hybrid';
  hybridAlpha: 0.7; // 70% vector, 30% keyword

  // Limits
  maxResults: 10;
  minScore: 0.70;

  // Strict filters (AND logic)
  filters: {
    domain?: string[];
    entity?: string[];
    locale?: string[];
    truthLevel?: TruthLevel[];
    freshnessHours?: number;
  };

  // Reranking
  rerank: boolean;
  rerankModel?: string;
}
```

### Hybrid Search Implementation

```typescript
export async function hybridSearch(
  query: string,
  config: SearchConfig
): Promise<SearchResult[]> {
  // 1. Vector search (semantic)
  const vectorResults = await weaviate.search({
    collection: config.namespace,
    vector: await embed(query),
    limit: config.maxResults * 2, // Oversample for reranking
    filters: buildFilters(config.filters),
  });

  // 2. Keyword search (BM25)
  const keywordResults = await weaviate.search({
    collection: config.namespace,
    query: query,
    type: 'bm25',
    limit: config.maxResults * 2,
    filters: buildFilters(config.filters),
  });

  // 3. Reciprocal Rank Fusion
  const fused = reciprocalRankFusion(
    vectorResults,
    keywordResults,
    config.hybridAlpha
  );

  // 4. Filter by min score
  const filtered = fused.filter(r => r.score >= config.minScore);

  // 5. Optional reranking
  if (config.rerank) {
    return await rerank(query, filtered, config.rerankModel);
  }

  return filtered.slice(0, config.maxResults);
}

function reciprocalRankFusion(
  vectorResults: SearchResult[],
  keywordResults: SearchResult[],
  alpha: number
): SearchResult[] {
  const k = 60; // RRF constant
  const scores = new Map<string, number>();
  const docs = new Map<string, SearchResult>();

  // Score from vector results
  vectorResults.forEach((r, rank) => {
    const score = alpha * (1 / (k + rank));
    scores.set(r.id, (scores.get(r.id) || 0) + score);
    docs.set(r.id, r);
  });

  // Score from keyword results
  keywordResults.forEach((r, rank) => {
    const score = (1 - alpha) * (1 / (k + rank));
    scores.set(r.id, (scores.get(r.id) || 0) + score);
    docs.set(r.id, r);
  });

  // Sort by combined score
  return Array.from(scores.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([id, score]) => ({ ...docs.get(id)!, score }));
}
```

---

## 3. Versioning & Safe Reindex

### Version Schema

```typescript
// packages/rag/src/governance/versioning.ts

export interface RagVersion {
  version: string; // semver
  namespace: string;
  status: 'building' | 'active' | 'deprecated';
  documentCount: number;
  buildStartedAt: string;
  buildCompletedAt?: string;
  checksums: Record<string, string>; // sourceId -> hash
}
```

### Safe Reindex (Zero Downtime)

```typescript
export async function safeReindex(
  namespace: string,
  documents: Document[]
): Promise<RagVersion> {
  const newVersion = incrementVersion(await getCurrentVersion(namespace));
  const newNamespace = `${namespace}_v${newVersion}`;

  // 1. Build new index in parallel namespace
  await buildIndex(newNamespace, documents);

  // 2. Validate new index
  const validation = await validateIndex(newNamespace, {
    minDocuments: documents.length * 0.95, // 95% must succeed
    sampleQueries: getValidationQueries(namespace),
  });

  if (!validation.success) {
    await deleteNamespace(newNamespace);
    throw new Error(`Reindex validation failed: ${validation.errors}`);
  }

  // 3. Atomic swap via alias
  await swapAlias(namespace, newNamespace);

  // 4. Deprecate old versions (keep 2 for rollback)
  await deprecateOldVersions(namespace, 2);

  return {
    version: newVersion,
    namespace: newNamespace,
    status: 'active',
    documentCount: documents.length,
    buildCompletedAt: new Date().toISOString(),
    checksums: generateChecksums(documents),
  };
}
```

---

## 4. Citation Sans Hallucination

### Citation Format

```typescript
// packages/rag/src/governance/citation.ts

export interface Citation {
  sourceId: string;
  sourceType: string;
  sourcePath: string;
  truthLevel: TruthLevel;
  excerpt: string;
  relevanceScore: number;
}

export interface FormattedResponse {
  answer: string;
  citations: Citation[];
  references: Reference[];
  warnings: string[];
  trustScore: number;
}
```

### Anti-Hallucination Implementation

```typescript
export function formatResponseWithCitations(
  answer: string,
  citations: Citation[]
): FormattedResponse {
  // 1. Verify each claim has a citation
  const claims = extractClaims(answer);
  const unsupportedClaims = claims.filter(
    c => !citations.some(cit => supportsClaim(cit, c))
  );

  if (unsupportedClaims.length > 0) {
    // RULE: Never invent - flag unsupported claims
    return {
      answer: markUnsupportedClaims(answer, unsupportedClaims),
      citations,
      references: [],
      warnings: [`${unsupportedClaims.length} claims without citation support`],
      trustScore: calculateTrustScore(citations, unsupportedClaims),
    };
  }

  // 2. Inline citations [1], [2], etc.
  const annotatedAnswer = inlineCitations(answer, citations);

  // 3. Build reference list
  const references = citations.map((c, i) => ({
    index: i + 1,
    source: c.sourcePath,
    truthLevel: c.truthLevel,
    excerpt: c.excerpt.substring(0, 100) + '...',
  }));

  return {
    answer: annotatedAnswer,
    citations,
    references,
    warnings: [],
    trustScore: calculateTrustScore(citations, []),
  };
}

function calculateTrustScore(
  citations: Citation[],
  unsupportedClaims: string[]
): number {
  if (citations.length === 0) return 0;

  const avgRelevance = citations.reduce((sum, c) => sum + c.relevanceScore, 0) / citations.length;
  const truthBonus = citations.filter(c => c.truthLevel === 'L1' || c.truthLevel === 'L2').length / citations.length;
  const unsupportedPenalty = unsupportedClaims.length * 0.1;

  return Math.max(0, Math.min(1, avgRelevance * 0.6 + truthBonus * 0.4 - unsupportedPenalty));
}
```

---

## 5. Namespaces

| Namespace | Content | TTL | Truth Level |
|-----------|---------|-----|-------------|
| `knowledge:faq` | FAQ content | 7d | L2 |
| `knowledge:diagnostic` | Diagnostic guides | 30d | L2-L3 |
| `knowledge:reference` | Technical references | 90d | L1-L2 |
| `catalog:products` | Product descriptions | 1d | L1 |
| `blog:articles` | Blog content | 7d | L3-L4 |

---

## 6. Performance Targets

| Metric | Target |
|--------|--------|
| Hybrid search p95 | < 200ms |
| Reindex (1k docs) | < 60s |
| Min relevance score | 0.70 |
| Citation coverage | > 95% |

---

## Voir aussi

- [[02-ai-cos-contracts]] - Types RagDocument, TruthLevel
- [[05-langgraph-router]] - Corrective-RAG pattern
- [[ADR-006-ai-orchestrator-architecture]] - Architecture globale

---

_Créé: 2026-02-03 | Source: Architecture Report Section 6_
