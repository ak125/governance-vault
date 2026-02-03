# Skills Registry: Manifest & Registration

> Système de découverte et d'exécution des skills AI-COS.

---

## 1. Skill Manifest Format

Chaque skill est défini par un manifest qui déclare ses capacités et contraintes.

```typescript
// packages/skills/src/manifest.ts

import { z } from 'zod';

export const SkillManifestSchema = z.object({
  // Identity
  name: z.string().regex(/^[a-z_]+$/), // snake_case obligatoire
  version: z.string().regex(/^\d+\.\d+\.\d+$/), // semver
  description: z.string(),

  // IO Schemas (Zod)
  inputSchema: z.instanceof(z.ZodType),
  outputSchema: z.instanceof(z.ZodType),

  // Execution
  timeout: z.number().default(60000), // 1min
  retries: z.number().default(3),
  retryBackoff: z.enum(['none', 'linear', 'exponential']).default('exponential'),

  // Permissions
  permissions: z.object({
    database: z.enum(['none', 'read', 'write']).default('read'),
    rag: z.enum(['none', 'search', 'ingest']).default('search'),
    external: z.array(z.string()).default([]), // allowed domains
    fileSystem: z.enum(['none', 'read', 'write']).default('none'),
  }),

  // Dependencies
  requires: z.array(z.string()).default([]), // other skills

  // Metadata
  tags: z.array(z.string()),
  owner: z.string(),
  deprecated: z.boolean().default(false),
});

export type SkillManifest = z.infer<typeof SkillManifestSchema>;
```

---

## 2. Skill Registry

Le registry centralise la découverte et l'exécution des skills.

```typescript
// packages/skills/src/registry.ts

import { Logger } from '@nestjs/common';

interface RegisteredSkill {
  manifest: SkillManifest;
  handler: SkillHandler;
  stats: SkillStats;
}

interface SkillStats {
  runs: number;
  failures: number;
  avgDuration: number;
}

export class SkillRegistry {
  private skills = new Map<string, RegisteredSkill>();
  private logger = new Logger('SkillRegistry');

  register(manifest: SkillManifest, handler: SkillHandler): void {
    const validated = SkillManifestSchema.parse(manifest);

    if (this.skills.has(validated.name)) {
      throw new Error(`Skill ${validated.name} already registered`);
    }

    this.skills.set(validated.name, {
      manifest: validated,
      handler,
      stats: { runs: 0, failures: 0, avgDuration: 0 },
    });

    this.logger.log(`Registered skill: ${validated.name}@${validated.version}`);
  }

  async execute(name: string, input: SkillInput): Promise<SkillOutput> {
    const skill = this.skills.get(name);
    if (!skill) throw new Error(`Skill ${name} not found`);

    // Validate input against skill's schema
    skill.manifest.inputSchema.parse(input.params);

    // Check permissions
    await this.checkPermissions(skill.manifest.permissions, input);

    // Execute with timeout
    const startTime = Date.now();
    try {
      const result = await Promise.race([
        skill.handler(input),
        this.timeout(skill.manifest.timeout),
      ]);

      // Validate output
      skill.manifest.outputSchema.parse(result.data);

      // Update stats
      skill.stats.runs++;
      skill.stats.avgDuration = this.updateAvg(
        skill.stats.avgDuration,
        Date.now() - startTime,
        skill.stats.runs
      );

      return result;
    } catch (error) {
      skill.stats.failures++;
      throw error;
    }
  }

  list(): SkillManifest[] {
    return Array.from(this.skills.values()).map(s => s.manifest);
  }

  get(name: string): RegisteredSkill | undefined {
    return this.skills.get(name);
  }

  getStats(name: string): SkillStats | undefined {
    return this.skills.get(name)?.stats;
  }

  private async checkPermissions(perms: SkillManifest['permissions'], input: SkillInput): Promise<void> {
    // Implement permission checks based on context
  }

  private timeout(ms: number): Promise<never> {
    return new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Skill timeout')), ms)
    );
  }

  private updateAvg(current: number, newValue: number, count: number): number {
    return current + (newValue - current) / count;
  }
}
```

---

## 3. Exemple: Skill `rag_reindex`

```typescript
// packages/skills/src/skills/rag-reindex.skill.ts

export const ragReindexManifest: SkillManifest = {
  name: 'rag_reindex',
  version: '1.0.0',
  description: 'Reindex documents in RAG vector store',

  inputSchema: z.object({
    namespace: z.enum(['knowledge:faq', 'knowledge:diagnostic', 'knowledge:reference']),
    documentIds: z.array(z.string()).optional(),
    fullRebuild: z.boolean().default(false),
  }),

  outputSchema: z.object({
    indexed: z.number(),
    skipped: z.number(),
    errors: z.array(z.string()),
    duration: z.number(),
  }),

  timeout: 300000, // 5min
  retries: 2,

  permissions: {
    database: 'read',
    rag: 'ingest',
    external: [],
    fileSystem: 'none',
  },

  tags: ['rag', 'indexing', 'maintenance'],
  owner: 'data-team',
  deprecated: false,
  requires: [],
};

export const ragReindexHandler: SkillHandler = async (input) => {
  const { namespace, documentIds, fullRebuild } = input.params as {
    namespace: string;
    documentIds?: string[];
    fullRebuild: boolean;
  };

  // 1. Fetch documents from Supabase
  const docs = await fetchDocuments(namespace, documentIds);

  // 2. Chunk and embed
  const chunks = await chunkDocuments(docs);

  // 3. Upsert to vector store
  const results = await upsertToWeaviate(namespace, chunks);

  return {
    success: true,
    data: {
      indexed: results.success,
      skipped: results.skipped,
      errors: results.errors,
      duration: Date.now() - input.startTime,
    },
    artifacts: [{
      type: 'report',
      name: 'rag-reindex-report',
      format: 'json',
      content: JSON.stringify(results),
      createdAt: new Date().toISOString(),
    }],
    metrics: {
      duration: Date.now() - input.startTime,
      tokensUsed: 0,
      itemsProcessed: docs.length,
    },
  };
};
```

---

## 4. Exemple: Skill `seo_role_audit`

```typescript
// packages/skills/src/skills/seo-role-audit.skill.ts

export const seoRoleAuditManifest: SkillManifest = {
  name: 'seo_role_audit',
  version: '1.0.0',
  description: 'Audit PageRole assignments and detect confusion',

  inputSchema: z.object({
    urls: z.array(z.string()).optional(),
    roles: z.array(z.string()).optional(),
    checkContent: z.boolean().default(true),
  }),

  outputSchema: z.object({
    audited: z.number(),
    violations: z.array(z.object({
      url: z.string(),
      currentRole: z.string(),
      suggestedRole: z.string().optional(),
      violations: z.array(z.string()),
      severity: z.enum(['info', 'warning', 'error', 'critical']),
    })),
    summary: z.object({
      byRole: z.record(z.number()),
      bySeverity: z.record(z.number()),
    }),
  }),

  timeout: 120000,
  retries: 1,

  permissions: {
    database: 'read',
    rag: 'none',
    external: [],
    fileSystem: 'none',
  },

  tags: ['seo', 'audit', 'quality'],
  owner: 'seo-team',
  deprecated: false,
  requires: [],
};

export const seoRoleAuditHandler: SkillHandler = async (input) => {
  const { urls, roles, checkContent } = input.params as {
    urls?: string[];
    roles?: string[];
    checkContent: boolean;
  };

  // 1. Fetch pages with roles
  const pages = await fetchPagesWithRoles(urls, roles);

  // 2. Validate each page
  const violations = [];
  for (const page of pages) {
    const pageViolations = await validatePageRole(page, checkContent);
    if (pageViolations.length > 0) {
      violations.push({
        url: page.url,
        currentRole: page.role,
        suggestedRole: inferCorrectRole(page),
        violations: pageViolations,
        severity: calculateSeverity(pageViolations),
      });
    }
  }

  return {
    success: true,
    data: {
      audited: pages.length,
      violations,
      summary: summarizeViolations(violations),
    },
    artifacts: [{
      type: 'report',
      name: 'seo-role-audit-report',
      format: 'json',
      content: JSON.stringify({ violations }),
      createdAt: new Date().toISOString(),
    }],
    metrics: {
      duration: Date.now() - input.startTime,
      tokensUsed: 0,
      itemsProcessed: pages.length,
    },
    nextAction: violations.length > 0 ? 'escalate' : 'complete',
  };
};
```

---

## 5. Exemple: Skill `routes_sync`

```typescript
// packages/skills/src/skills/routes-sync.skill.ts

export const routesSyncManifest: SkillManifest = {
  name: 'routes_sync',
  version: '1.0.0',
  description: 'Sync Remix routes with SEO database',

  inputSchema: z.object({
    dryRun: z.boolean().default(true),
    includeAdmin: z.boolean().default(false),
  }),

  outputSchema: z.object({
    routes: z.number(),
    added: z.array(z.string()),
    removed: z.array(z.string()),
    updated: z.array(z.string()),
    missingRole: z.array(z.string()),
  }),

  timeout: 60000,
  retries: 2,

  permissions: {
    database: 'write',
    rag: 'none',
    external: [],
    fileSystem: 'read',
  },

  tags: ['seo', 'routes', 'sync'],
  owner: 'platform-team',
  deprecated: false,
  requires: [],
};
```

---

## Catalogue des Skills Prévus

| Skill | Description | Priority |
|-------|-------------|----------|
| `rag_reindex` | Reindex RAG documents | P0 |
| `seo_role_audit` | Audit PageRole assignments | P0 |
| `routes_sync` | Sync Remix routes with DB | P1 |
| `content_generate` | Generate SEO content | P1 |
| `kg_diagnose` | Diagnose KG symptoms | P2 |
| `sitemap_build` | Build sitemaps | P2 |

---

## Voir aussi

- [[02-ai-cos-contracts]] - Types SkillInput, SkillOutput
- [[05-langgraph-router]] - Intégration dans le router
- [[ai-skill-antipatterns]] - Erreurs à éviter

---

_Créé: 2026-02-03 | Source: Architecture Report Section 5_
