# AI-COS Skill Model (Contrat Skill MCP-Ready)

> **Version**: 1.3.0 | **Status**: CANON | **Date**: 2026-01-27
> **Aligned with**: Architecture Charter v2.1.0 Section 5
> **Breaking Changes**: SkillInput.startedAt (ISO string), params typing

## Objectif

Définir le contrat universel que **tout skill AI-COS** doit respecter, compatible MCP (Model Context Protocol).

---

## Schema Skill Contract

```yaml
Skill:
  # ═══════════════════════════════════════════════════════════
  # IDENTITÉ
  # ═══════════════════════════════════════════════════════════
  id: string                    # Unique, snake_case (ex: seo_role_audit)
  name: string                  # Display name (ex: "SEO Role Audit")
  description: string           # Description courte (< 200 chars)
  version: semver               # Version du skill
  domain: Domain                # CORE, INFRA, DATA, SEO, RAG, CART, AICOS
  owner: string                 # Équipe responsable

  # ═══════════════════════════════════════════════════════════
  # SCHEMAS I/O (Zod)
  # ═══════════════════════════════════════════════════════════
  input_schema: ZodSchema       # Schema Zod d'entrée
  output_schema: ZodSchema      # Schema Zod de sortie

  # ═══════════════════════════════════════════════════════════
  # CONTRAT D'EXÉCUTION
  # ═══════════════════════════════════════════════════════════
  preconditions:                # Conditions AVANT exécution
    - condition: string         # Expression à évaluer
      error_code: string        # Code erreur si échoue
      message: string           # Message d'erreur

  postconditions:               # Conditions APRÈS exécution
    - assertion: string         # Assertion à vérifier
      rollback_action: string   # Action si échoue (optionnel)

  # ═══════════════════════════════════════════════════════════
  # EFFETS DE BORD
  # ═══════════════════════════════════════════════════════════
  side_effects:
    - type: SideEffectType      # database | file | api | event | cache
      target: string            # Table/fichier/endpoint affecté
      operation: Operation      # read | write | delete | upsert
      reversible: boolean       # Peut être annulé ?
      description: string       # Explication

  # ═══════════════════════════════════════════════════════════
  # VALIDATION
  # ═══════════════════════════════════════════════════════════
  validation_rules:
    - rule_id: string           # Ex: "no_url_modification"
      expression: string        # Expression de validation
      severity: Severity        # error | warning | info
      message: string           # Message si violation

  # ═══════════════════════════════════════════════════════════
  # RÉUTILISATION & PERMISSIONS
  # ═══════════════════════════════════════════════════════════
  reusable_by:                  # Qui peut utiliser ce skill ?
    - agent_role: AgentRole     # ARCHITECT, EXECUTOR, etc.
      permission_level: PermLevel # read | execute | admin

  # ═══════════════════════════════════════════════════════════
  # EXÉCUTION
  # ═══════════════════════════════════════════════════════════
  execution:
    timeout_ms: number          # Timeout max (défaut: 60000)
    retries: number             # Nombre de retries (défaut: 3)
    retry_backoff: Backoff      # none | linear | exponential
    idempotent: boolean         # Réexécution safe ?

  # ═══════════════════════════════════════════════════════════
  # MCP (Model Context Protocol)
  # ═══════════════════════════════════════════════════════════
  mcp:
    exposed: boolean            # Exposé comme MCP tool ?
    tool_name: string           # Nom MCP (ex: ai_cos_seo_audit)
    permissions: string[]       # Permissions MCP requises
```

---

## Enums

```typescript
enum SideEffectType {
  DATABASE = 'database',
  FILE = 'file',
  API = 'api',
  EVENT = 'event',
  CACHE = 'cache'
}

enum Operation {
  READ = 'read',
  WRITE = 'write',
  DELETE = 'delete',
  UPSERT = 'upsert'
}

enum Severity {
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info'
}

enum PermLevel {
  READ = 'read',
  EXECUTE = 'execute',
  ADMIN = 'admin'
}

enum Backoff {
  NONE = 'none',
  LINEAR = 'linear',
  EXPONENTIAL = 'exponential'
}
```

---

## Exemples Concrets

### Skill 1: `seo_role_audit`

```yaml
Skill:
  id: "seo_role_audit"
  name: "SEO Role Audit"
  description: "Audit PageRole assignments and detect R1/R4 confusion"
  version: "1.0.0"
  domain: SEO
  owner: "seo-team"

  input_schema:
    type: object
    properties:
      urls:
        type: array
        items: { type: string, format: uri }
        maxItems: 1000
      check_content:
        type: boolean
        default: true
    required: [urls]

  output_schema:
    type: object
    properties:
      audited:
        type: integer
      violations:
        type: array
        items:
          type: object
          properties:
            url: { type: string }
            current_role: { type: string }
            suggested_role: { type: string }
            violations: { type: array, items: { type: string } }
            severity: { type: string, enum: [info, warning, error, critical] }
      summary:
        type: object
    required: [audited, violations]

  preconditions:
    - condition: "urls.length > 0"
      error_code: "EMPTY_INPUT"
      message: "At least one URL is required"
    - condition: "urls.length <= 1000"
      error_code: "TOO_MANY_URLS"
      message: "Maximum 1000 URLs per audit"

  postconditions:
    - assertion: "output.audited === input.urls.length"
      rollback_action: null

  side_effects:
    - type: database
      target: "__seo_audit_log"
      operation: write
      reversible: true
      description: "Log audit results"

  validation_rules:
    - rule_id: "no_r1_expert_content"
      expression: "!violations.some(v => v.current_role === 'R1' && v.has_expert_content)"
      severity: error
      message: "Router pages must not contain expert content"

  reusable_by:
    - agent_role: EXECUTOR
      permission_level: execute
    - agent_role: VALIDATOR
      permission_level: execute

  execution:
    timeout_ms: 120000
    retries: 2
    retry_backoff: exponential
    idempotent: true

  mcp:
    exposed: true
    tool_name: "ai_cos_seo_role_audit"
    permissions: ["database:read", "seo:audit"]
```

### Skill 2: `rag_reindex`

```yaml
Skill:
  id: "rag_reindex"
  name: "RAG Reindex"
  description: "Reindex documents in RAG vector store with safe atomic swap"
  version: "1.0.0"
  domain: RAG
  owner: "data-team"

  input_schema:
    type: object
    properties:
      namespace:
        type: string
        enum: ["knowledge:faq", "knowledge:diagnostic", "knowledge:reference"]
      document_ids:
        type: array
        items: { type: string }
      full_rebuild:
        type: boolean
        default: false
    required: [namespace]

  output_schema:
    type: object
    properties:
      indexed: { type: integer }
      skipped: { type: integer }
      errors: { type: array, items: { type: string } }
      duration_ms: { type: integer }
      version: { type: string }
    required: [indexed, skipped, errors]

  preconditions:
    - condition: "namespace in allowed_namespaces"
      error_code: "INVALID_NAMESPACE"
      message: "Namespace not allowed in production"

  postconditions:
    - assertion: "output.indexed + output.skipped >= input.document_ids.length"
      rollback_action: "rollback_to_previous_version"

  side_effects:
    - type: database
      target: "weaviate::{namespace}"
      operation: upsert
      reversible: true
      description: "Upsert vectors to Weaviate"
    - type: cache
      target: "redis::rag_version"
      operation: write
      reversible: true
      description: "Update version cache"

  validation_rules:
    - rule_id: "min_documents"
      expression: "output.indexed >= input.document_ids.length * 0.95"
      severity: error
      message: "At least 95% of documents must be indexed"

  reusable_by:
    - agent_role: EXECUTOR
      permission_level: execute
    - agent_role: ORCHESTRATOR
      permission_level: admin

  execution:
    timeout_ms: 300000
    retries: 2
    retry_backoff: exponential
    idempotent: true

  mcp:
    exposed: true
    tool_name: "ai_cos_rag_reindex"
    permissions: ["rag:ingest", "database:read"]
```

### Skill 3: `vlevel_calculator`

```yaml
Skill:
  id: "vlevel_calculator"
  name: "V-Level Calculator"
  description: "Calculate V1-V5 levels for SEO pages based on vehicle specificity"
  version: "1.0.0"
  domain: SEO
  owner: "seo-team"

  input_schema:
    type: object
    properties:
      page_data:
        type: object
        properties:
          url: { type: string }
          gamme: { type: string }
          marque: { type: string }
          modele: { type: string }
          type: { type: string }
          ktypnr: { type: string }
        required: [url, gamme]
    required: [page_data]

  output_schema:
    type: object
    properties:
      vlevel:
        type: string
        enum: ["V1", "V2", "V3", "V4", "V5"]
      score:
        type: integer
        minimum: 0
        maximum: 100
      breakdown:
        type: object
        properties:
          gamme_score: { type: integer }
          vehicle_score: { type: integer }
          specificity_score: { type: integer }
      recommendations:
        type: array
        items: { type: string }
    required: [vlevel, score]

  preconditions:
    - condition: "page_data.url is valid URL"
      error_code: "INVALID_URL"
      message: "URL must be valid"

  postconditions:
    - assertion: "output.vlevel in ['V1', 'V2', 'V3', 'V4', 'V5']"
      rollback_action: null

  side_effects: []  # Pure function, no side effects

  validation_rules:
    - rule_id: "score_consistency"
      expression: "(vlevel === 'V5' && score >= 80) || (vlevel !== 'V5')"
      severity: warning
      message: "V5 pages should have score >= 80"

  reusable_by:
    - agent_role: EXECUTOR
      permission_level: execute
    - agent_role: ANALYZER
      permission_level: read

  execution:
    timeout_ms: 5000
    retries: 1
    retry_backoff: none
    idempotent: true

  mcp:
    exposed: true
    tool_name: "ai_cos_vlevel_calc"
    permissions: ["seo:read"]
```

---

## Interface TypeScript

```typescript
// packages/contracts/src/skill.ts

import { z } from 'zod';

export interface SkillContract {
  readonly manifest: SkillManifest;
  execute(input: SkillInput): Promise<SkillOutput>;
  validate(input: unknown): SkillInput;
  rollback?(output: SkillOutput): Promise<void>;
}

export interface SkillManifest {
  id: string;
  name: string;
  description: string;
  version: string;
  domain: Domain;
  owner: string;
  inputSchema: z.ZodType;
  outputSchema: z.ZodType;
  preconditions: Precondition[];
  postconditions: Postcondition[];
  sideEffects: SideEffect[];
  validationRules: ValidationRule[];
  reusableBy: ReusableSpec[];
  execution: ExecutionConfig;
  mcp: McpConfig;
}

export interface SkillInput {
  jobId: string;
  traceId: string;
  // RÈGLE: params DOIT correspondre au inputSchema du skill
  // Ne pas passer scope brut si le schema attend autre chose
  params: z.infer<typeof manifest.inputSchema>;
  constraints: ExecutionConstraints;
  // startedAt injecté par le SkillRegistry (new Date().toISOString())
  startedAt: string; // ISO datetime
  // ragContext optionnel si le skill a besoin de RAG
  ragContext?: RagContext;
}

export interface SkillOutput {
  success: boolean;
  data: unknown;
  artifacts: Artifact[];
  metrics: {
    duration_ms: number;
    tokens_used?: number;
    items_processed: number;
  };
  nextAction?: 'continue' | 'retry' | 'escalate' | 'complete';
}
```

---

## Règles de Validation

### R1: Tout skill DOIT avoir un manifest

```typescript
// ❌ INTERDIT
async function doSomething(params: any) { ... }

// ✅ OBLIGATOIRE
export const manifest: SkillManifest = { ... };
export async function execute(input: SkillInput): Promise<SkillOutput> { ... }
```

### R2: Les side effects DOIVENT être déclarés

```typescript
// ❌ INTERDIT - Side effect non déclaré
async function execute(input) {
  await db.insert('logs', { ... }); // Non déclaré !
}

// ✅ OBLIGATOIRE - Déclaré dans le manifest
sideEffects: [
  { type: 'database', target: 'logs', operation: 'write', reversible: true }
]
```

### R3: Les skills avec side effects DOIVENT être réversibles si possible

---

## Skill Registry (Architecture Charter Section 5.2)

```typescript
// packages/skills/src/registry.ts

export class SkillRegistry {
  private skills = new Map<string, RegisteredSkill>();
  private logger: Logger;

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

  async execute(name: string, input: Omit<SkillInput, 'startedAt'>): Promise<SkillOutput> {
    const skill = this.skills.get(name);
    if (!skill) throw new Error(`Skill ${name} not found`);

    // Validate input params against skill's inputSchema
    skill.manifest.inputSchema.parse(input.params);

    // Check permissions
    await this.checkPermissions(skill.manifest.permissions, input);

    // Inject startedAt (ISO string) - le handler ne doit pas le calculer lui-même
    const enrichedInput: SkillInput = {
      ...input,
      startedAt: new Date().toISOString(),
    };

    // Execute with timeout
    const startTime = Date.now();
    try {
      const result = await Promise.race([
        skill.handler(enrichedInput),
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

  getStats(name: string): SkillStats {
    return this.skills.get(name)?.stats;
  }
}
```

---

## Skill 4: `routes_sync` (Architecture Charter)

```yaml
Skill:
  id: "routes_sync"
  name: "Routes Sync"
  description: "Sync Remix routes with SEO database"
  version: "1.0.0"
  domain: SEO
  owner: "platform-team"

  input_schema:
    type: object
    properties:
      dryRun:
        type: boolean
        default: true
      includeAdmin:
        type: boolean
        default: false
    required: []

  output_schema:
    type: object
    properties:
      routes: { type: integer }
      added: { type: array, items: { type: string } }
      removed: { type: array, items: { type: string } }
      updated: { type: array, items: { type: string } }
      missingRole: { type: array, items: { type: string } }
    required: [routes, added, removed, updated]

  preconditions:
    - condition: "user.role === 'admin' || dryRun === true"
      error_code: "PERMISSION_DENIED"
      message: "Only admins can sync routes without dry run"

  postconditions:
    - assertion: "missingRole.length === 0 || dryRun === true"
      rollback_action: "revert_route_changes"

  side_effects:
    - type: database
      target: "__seo_routes"
      operation: upsert
      reversible: true
      description: "Sync routes to SEO database"

  validation_rules:
    - rule_id: "no_orphan_routes"
      expression: "missingRole.length === 0"
      severity: error
      message: "All routes must have a PageRole assigned"

  reusable_by:
    - agent_role: EXECUTOR
      permission_level: execute
    - agent_role: ORCHESTRATOR
      permission_level: admin

  execution:
    timeout_ms: 60000
    retries: 2
    retry_backoff: linear
    idempotent: true

  mcp:
    exposed: true
    tool_name: "ai_cos_routes_sync"
    permissions: ["seo:write", "filesystem:read"]
```

---

## Anti-Patterns (INTERDIT)

```typescript
// ANTI-PATTERN 1: Execution directe sans envelope
// WRONG:
await skillRegistry.execute('seo_audit', { urls: ['...'] });

// CORRECT:
await jobManager.enqueue(createJobEnvelope({
  intent: 'seo_audit',
  scope: { entityType: 'page', entityIds: ['...'] },
}));

// ANTI-PATTERN 2: Skill sans manifest
// WRONG:
async function doSeoAudit(params: any) { ... }

// CORRECT:
export const manifest: SkillManifest = { ... };
export async function execute(input: SkillInput): Promise<SkillOutput> { ... }

// ANTI-PATTERN 3: Side effects non declares
// WRONG:
async function execute(input) {
  await db.insert('audit_log', { ... }); // Side effect cache!
}

// CORRECT:
sideEffects: [
  { type: 'database', target: 'audit_log', operation: 'write', reversible: true }
]

// ANTI-PATTERN 4: Calcul de durée incorrect
// WRONG:
async function execute(input: SkillInput) {
  const start = Date.now(); // Local start = incorrect!
  // ... work ...
  const duration = Date.now() - start;
}

// CORRECT:
async function execute(input: SkillInput) {
  // startedAt est injecté par le SkillRegistry (ISO string)
  const startMs = new Date(input.startedAt).getTime();
  // ... work ...
  const duration = Date.now() - startMs; // Correct!
}
```

---

_Ce document est la source de verite pour les contrats de skills AI-COS._
