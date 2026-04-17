# AI-COS Governance Rules (Canonical)

> **Version**: 1.3.0 | **Status**: CANON | **Date**: 2026-01-27
> **Aligned with**: Architecture Charter v2.1.0 Section 9
> **Breaking Changes**: ESLint rule PageRole, SEO package extraction pattern

## Objectif

Definir les regles de gouvernance canoniques pour le systeme AI-COS.

---

## Axiome Zero (INVIOLABLE)

```
+---------------------------------------------------------------------+
|                                                                      |
|   L'IA NE CREE PAS LA VERITE.                                       |
|                                                                      |
|   Elle produit, analyse, propose.                                    |
|   La verite = validee par Structure + Humain.                       |
|                                                                      |
+---------------------------------------------------------------------+
```

---

## Schema Governance Contract

```yaml
Governance:
  # ===================================================================
  # STRUCTURE HIERARCHIQUE
  # ===================================================================
  hierarchy:
    levels:
      - level: 0
        name: "Human CEO"
        max_instances: 1
        protection: absolute
        authority: decision_final
      - level: 1
        name: "Executive Board"
        max_instances: 7
        protection: high
        authority: propose_strategic
      - level: 2
        name: "Leads Metiers"
        max_instances: 1_per_domain
        protection: high
        authority: coordinate_domain
      - level: 3
        name: "Agents Support (TYPE 2)"
        max_instances: variable
        protection: protected
        authority: analyze_execute
      - level: 4
        name: "Agents Execution (TYPE 3)"
        max_instances: variable
        protection: jetable
        authority: execute_only

  # ===================================================================
  # REGLES IMMUTABLES (7 regles)
  # ===================================================================
  immutable_rules:
    interdits:
      - rule_id: "R1_NO_SOLO_DECISION"
        statement: "Aucun agent ne decide seul"
        enforcement: hard_block

      - rule_id: "R2_NO_ORPHAN_AGENT"
        statement: "Aucun agent hors hierarchie"
        enforcement: hard_block

      - rule_id: "R3_NO_UNMETERED_AGENT"
        statement: "Aucun agent sans indicateur"
        enforcement: hard_block

      - rule_id: "R4_NO_DETACHED_TRANSVERSAL"
        statement: "Aucun agent transversal sans rattachement"
        enforcement: hard_block

    obligatoires:
      - rule_id: "R5_MULTI_VALIDATION"
        statement: "Diagnostic = multi-validation obligatoire"
        enforcement: hard_block

      - rule_id: "R6_QUALITY_OFFICER"
        statement: "Contenu critique = Quality Officer obligatoire"
        enforcement: hard_block

      - rule_id: "R7_EQUILIBRIUM"
        statement: "1 creation = 1 fusion ou suppression"
        enforcement: soft_warn

  # ===================================================================
  # REGLES IA (16 regles par categorie)
  # ===================================================================
  ia_rules:
    anti_hallucination:
      - rule_id: "IA1"
        condition: "confidence < 0.8"
        action: flag_review
      - rule_id: "IA2"
        condition: "source_count < 2"
        action: require_validation
      - rule_id: "IA3"
        condition: "doubt_score > 0.2"
        action: hard_block
      - rule_id: "IA4"
        condition: "factual_claim && !verifiable"
        action: hard_block

    anti_seo_drift:
      - rule_id: "SEO1"
        condition: "keyword_density > 3%"
        action: flag_stuffing
      - rule_id: "SEO2"
        condition: "duplicate_score > 80%"
        action: hard_block
      - rule_id: "SEO3"
        condition: "same_keyword_multiple_pages"
        action: review_cmo
      - rule_id: "SEO4"
        condition: "claim_without_source"
        action: flag_qto

    anti_illegal:
      - rule_id: "LEG1"
        condition: "legal_reference && !source"
        action: hard_block
      - rule_id: "LEG2"
        condition: "warranty_promise"
        action: human_review
      - rule_id: "LEG3"
        condition: "rgpd_data"
        action: dpo_validation
      - rule_id: "LEG4"
        condition: "civil_criminal_liability"
        action: hard_block

    anti_danger:
      - rule_id: "DNG1"
        condition: "infrastructure_change"
        action: double_validation
      - rule_id: "DNG2"
        condition: "mass_deletion"
        action: double_validation
      - rule_id: "DNG3"
        condition: "security_piece"
        action: human_mandatory
      - rule_id: "DNG4"
        condition: "production_write"
        action: feature_flag_required

  # ===================================================================
  # MODES OPERATOIRES
  # ===================================================================
  operational_modes:
    - mode_id: "SAFE"
      autonomy: read_only
      human_validation: none_required
      description: "Lecture seule, aucune action"

    - mode_id: "ASSISTED"
      autonomy: propose_only
      human_validation: always_required
      description: "Propose, validation humaine obligatoire"
      default: true

    - mode_id: "AUTO_DRIVE"
      autonomy: weak_actions
      human_validation: medium_critical_only
      description: "Actions faibles auto, moyen/critique = humain"

    - mode_id: "FORECAST"
      autonomy: simulation_only
      human_validation: none_required
      description: "Simulation uniquement, aucune execution"

  # ===================================================================
  # KILL-SWITCH
  # ===================================================================
  kill_switch:
    levels:
      - level: "N1"
        trigger: "human_ceo_exclusive"
        action: "full_immediate_shutdown"
        reversible: true

      - level: "N2"
        trigger: "grave_anomaly_detected"
        action: "automatic_isolation"
        reversible: true

      - level: "N3"
        trigger: "critical_kpi_threshold"
        action: "alert_and_freeze"
        reversible: true

  # ===================================================================
  # ESCALATION
  # ===================================================================
  escalation:
    chain:
      - criticality: low
        delay_hours: 24
        target: manager
      - criticality: medium
        delay_hours: 4
        target: clevel_concerned
      - criticality: high
        delay_hours: 1
        target: human_ceo
      - criticality: urgent
        delay_hours: 0
        target: kill_switch

    rules:
      - "Vert = Ne pas toucher (confiance)"
      - "Jaune = Observer (pas d'action)"
      - "Rouge = Agir (arbitrage obligatoire)"
      - "1 alerte = 1 decision"
      - "Pas de preventif"
```

---

## C-Level Roles (4 verrous chacun)

```yaml
CLevelRoles:
  ia_cto:
    domain: Tech
    responsibilities:
      - "Code qualite"
      - "Dette technique"
      - "Securite"
    verrou: "Qualite code obligatoire"
    authority: propose_only

  ia_cpo:
    domain: Product
    responsibilities:
      - "UX validee"
      - "Satisfaction"
      - "Coherence produit"
    verrou: "UX testee obligatoire"
    authority: propose_only

  ia_cmo:
    domain: Marketing
    responsibilities:
      - "SEO mesure"
      - "Visibilite"
      - "Reputation"
    verrou: "SEO mesure obligatoire"
    authority: propose_only

  ia_cfo:
    domain: Finance
    responsibilities:
      - "Couts IA"
      - "ROI par agent"
      - "Budget"
    verrou: "Budget valide obligatoire"
    authority: propose_only
```

---

## Agent Types (4 types)

```yaml
AgentTypes:
  TYPE_1:
    name: "Decisionnel"
    indicators:
      - "ROI"
      - "Impact business"
      - "Decision validee"
    protection: high

  TYPE_2:
    name: "Analyse/Redaction"
    indicators:
      - "Validation rate"
      - "Clarte"
      - "Utilisation reelle"
    protection: protected

  TYPE_3:
    name: "Execution"
    indicators:
      - "Temps gagne"
      - "Volume traite"
      - "Erreur/succes"
    protection: jetable

  TYPE_4:
    name: "Controle"
    indicators:
      - "Scans executes"
      - "Alertes levees"
      - "Resolution rapide"
    protection: high
```

---

## Audit Matrix (5 criteres)

```yaml
AuditMatrix:
  criteria:
    - id: 1
      name: "UTILITE"
      question: "Est-il utilise ?"
      weight: 2

    - id: 2
      name: "POSITION"
      question: "Decide / Analyse / Execute ?"
      weight: 2

    - id: 3
      name: "REDONDANCE"
      question: "Existe-t-il un clone ?"
      weight: 2

    - id: 4
      name: "INDICATEUR"
      question: "Mesure-t-on sa valeur ?"
      weight: 2

    - id: 5
      name: "RATTACHEMENT"
      question: "A-t-il un Lead ?"
      weight: 2

  scoring:
    - range: [0, 3]
      status: red
      action: supprimer
    - range: [4, 6]
      status: yellow
      action: risque
    - range: [7, 9]
      status: orange
      action: surveiller
    - range: [10, 10]
      status: green
      action: conforme
```

---

## Crisis Protocols

```yaml
CrisisProtocols:
  seo_crisis:
    trigger: "-15% pages indexees/24h"
    steps:
      - "SEO Monitor detecte"
      - "QTO verifie"
      - "CMO analyse"
      - "AI-CEO propose"
      - "HUMAN decide"

  legal_crisis:
    trigger: "mise_en_demeure OR signalement_rgpd"
    steps:
      - "BLOCAGE publication"
      - "GEL contenus lies"
      - "AUDIT interne"
      - "HUMAN + Juridique"

  data_crisis:
    trigger: "incoherence_multi_sources OR injection_suspectee"
    steps:
      - "QUARANTAINE RAG"
      - "AGENTS mode lecture seule"
      - "REVALIDATION sources"
      - "REPRISE progressive"

  hallucination_crisis:
    trigger: "hallucination_publiee OR erreur_securite_vehicule"
    steps:
      - "RETRAIT immediat"
      - "MARQUAGE incident"
      - "ANALYSE cause"
      - "AJUSTEMENT seuils"
      - "NOTIFICATION humaine"
```

---

## Golden Rules (4 commandements)

```yaml
GoldenRules:
  - "PAS D'INDICATEUR = SUPPRESSION"
  - "IA-CEO propose, Human CEO decide"
  - "Doute = Escalade Human CEO"
  - "Production sans validation = Interdit"
```

---

## Interface TypeScript

```typescript
// packages/contracts/src/governance.ts

export interface GovernanceContract {
  readonly rules: ImmutableRule[];
  readonly iaRules: IaRule[];
  readonly modes: OperationalMode[];
  readonly killSwitch: KillSwitch;
  validateAction(action: AgentAction): ValidationResult;
  escalate(reason: string, criticality: Criticality): Promise<void>;
  audit(agent: Agent): AuditResult;
}

export interface ValidationResult {
  allowed: boolean;
  blockedBy?: string[];
  warnings?: string[];
  requiredApprovals?: string[];
}

export interface AuditResult {
  agentId: string;
  score: number;
  status: 'red' | 'yellow' | 'orange' | 'green';
  recommendation: 'supprimer' | 'fusionner' | 'retrograder' | 'verrouiller' | 'conserver';
  details: AuditCriterion[];
}
```

---

## MCP Governance: PR Automation (Architecture Charter Section 9)

### Artifacts to PR Rules

```typescript
// packages/mcp/src/governance/pr-rules.ts

export const PR_TRIGGER_RULES: PrTriggerRule[] = [
  {
    artifactType: 'migration',
    artifactPattern: '*.sql',
    action: 'create_pr',
    branch: 'auto/migrations/{date}',
    reviewers: ['dba-team'],
    labels: ['database', 'auto-generated'],
    checks: ['sql-lint', 'migration-dry-run'],
  },
  {
    artifactType: 'seo-fix',
    artifactPattern: 'seo-*.json',
    action: 'create_pr',
    branch: 'auto/seo-fixes/{date}',
    reviewers: ['seo-team'],
    labels: ['seo', 'auto-generated'],
    checks: ['seo-validation', 'url-check'],
  },
  {
    artifactType: 'content',
    artifactPattern: 'content-*.md',
    action: 'draft_pr', // Draft, not ready for review
    branch: 'auto/content/{date}',
    reviewers: ['content-team'],
    labels: ['content', 'l4-review-required'],
    checks: ['spell-check', 'plagiarism-check'],
    requireHumanApproval: true, // L4 content
  },
  {
    artifactType: 'code',
    artifactPattern: '*.ts',
    action: 'create_pr',
    branch: 'auto/code/{feature}',
    reviewers: ['tech-lead'],
    labels: ['code', 'auto-generated'],
    checks: ['lint', 'typecheck', 'test'],
  },
];
```

### CI Gates by Artifact Type

```yaml
# .github/workflows/ai-artifact-check.yml

on:
  pull_request:
    labels: [auto-generated]

jobs:
  validate:
    steps:
      # Migration checks
      - name: SQL Lint
        if: artifactType == 'migration'
        run: sqlfluff lint backend/supabase/migrations/

      # SEO checks (ESLint rule, pas grep)
      - name: SEO Validation
        if: artifactType == 'seo'
        run: npm run seo:validate

      # Routes checks (ESLint AST, pas grep)
      - name: PageRole Required
        run: npm run lint -- --rule '@automecanik/require-page-role: error'
        # Note: grep est FRAGILE (sous-dossiers, .ts/.tsx, handle export)
        # Utiliser ESLint custom rule qui parse l'AST

      # Content checks (script TS, pas grep)
      - name: Truth Level Check
        if: artifactType == 'content'
        run: npx tsx scripts/validate-truth-levels.ts
```

### ESLint Rule: require-page-role (Recommandé)

```typescript
// eslint-local-rules/require-page-role.ts
// Plus robuste que grep -rL "pageRole:" (gère sous-dossiers, .ts/.tsx, handle export)

import { ESLintUtils } from '@typescript-eslint/utils';

export const requirePageRole = ESLintUtils.RuleCreator.withoutDocs({
  meta: {
    type: 'problem',
    messages: {
      missingPageRole: 'Route file must export handle with pageRole',
    },
    schema: [],
  },
  defaultOptions: [],
  create(context) {
    const filename = context.getFilename();
    if (!filename.includes('/routes/')) return {};

    let hasPageRole = false;

    return {
      ExportNamedDeclaration(node) {
        // Check for: export const handle = { pageRole: '...' }
        if (node.declaration?.declarations) {
          for (const decl of node.declaration.declarations) {
            if (decl.id.name === 'handle' && decl.init?.properties) {
              hasPageRole = decl.init.properties.some(
                p => p.key?.name === 'pageRole'
              );
            }
          }
        }
      },
      'Program:exit'() {
        if (!hasPageRole) {
          context.report({ messageId: 'missingPageRole', loc: { line: 1, column: 0 } });
        }
      },
    };
  },
});
```

### Auto-Merge Rules

| Truth Level | Auto-Merge | Condition |
|-------------|------------|-----------|
| L1 (Constructeur) | YES | All checks pass |
| L2 (Expert valide) | YES | All checks pass |
| L3 (IA supervisee) | NO | Human review required |
| L4 (IA non validee) | NO | Draft PR only |

### Branch Naming Convention

```
auto/migrations/{YYYY-MM-DD}  - Database migrations
auto/seo-fixes/{YYYY-MM-DD}   - SEO corrections
auto/content/{slug}           - Generated content
auto/code/{feature-name}      - Generated code
```

### Commit Message Format

```
chore(auto): [skill-name] description

Examples:
- fix(seo): [seo_role_audit] correct PageRole for /pieces/*
- feat(content): [content_gen] add guide for embrayage
- chore(db): [rag_reindex] update vector index version
```

---

## Package Extraction: SEO (Pattern Canonique)

### Règle d'Or: Separation of Concerns

```
packages/seo (PURE)          →   backend/src/modules/seo-* (ADAPTERS)
├── rules/                       ├── seo-meta/
├── validators/                  ├── seo-sitemap/
├── types/                       ├── seo-linking/
└── utils/                       └── seo-monitoring/
                                      ↓
                              Lit DB → Transforme → Appelle @repo/seo
```

### packages/seo (Pure Policy + Validation)

```typescript
// packages/seo/src/index.ts
// ⚠️ PAS d'accès DB, PAS de NestJS - pure TypeScript testable

// Rules
export * from './rules/anti-confusion.rules';
export * from './rules/structured-data.rules';
export * from './rules/canonical.rules';

// Validators
export * from './validators/role.validator';
export * from './validators/canonical.validator';
export * from './validators/schema.validator';

// Types
export * from './types/page-role.types';
export * from './types/seo-rule.types';
export * from './types/seo-violation.types';

// Utils
export * from './utils/url.utils';
export * from './utils/meta.utils';
```

```typescript
// packages/seo/src/types/page-role.types.ts

export enum PageRole {
  R1_ROUTER = 'R1',      // Navigation, liens
  R2_AUTHORITY = 'R2',   // Best-sellers, avis
  R3_PRODUCT = 'R3',     // Fiches produit
  R4_REFERENCE = 'R4',   // Guides techniques
  R5_DIAGNOSTIC = 'R5',  // Diagnostic véhicule
  R6_SUPPORT = 'R6',     // FAQ, contact
}

export interface SeoViolation {
  rule: string;
  severity: 'error' | 'warning' | 'info';
  url: string;
  currentRole?: PageRole;
  suggestedRole?: PageRole;
  message: string;
  fix?: string;
}

export interface PageModel {
  url: string;
  role: PageRole;
  title?: string;
  description?: string;
  h1?: string;
  hasExpertContent: boolean;
  structuredData?: object[];
  canonical?: string;
}
```

```typescript
// packages/seo/src/validators/role.validator.ts
// Pure function - NO DB access

export function validatePageRole(page: PageModel): SeoViolation[] {
  const violations: SeoViolation[] = [];

  // R1 = Router, ne doit PAS avoir de contenu expert
  if (page.role === PageRole.R1_ROUTER && page.hasExpertContent) {
    violations.push({
      rule: 'R1_NO_EXPERT_CONTENT',
      severity: 'error',
      url: page.url,
      currentRole: page.role,
      suggestedRole: PageRole.R4_REFERENCE,
      message: 'Router pages (R1) must not contain expert content',
      fix: 'Move content to R4 Reference page or change role',
    });
  }

  // R4 = Reference, DOIT avoir du contenu expert
  if (page.role === PageRole.R4_REFERENCE && !page.hasExpertContent) {
    violations.push({
      rule: 'R4_REQUIRES_EXPERT_CONTENT',
      severity: 'warning',
      url: page.url,
      currentRole: page.role,
      message: 'Reference pages (R4) should contain expert content',
    });
  }

  return violations;
}
```

### backend/src/modules/seo-meta (Adapter)

```typescript
// backend/src/modules/seo-meta/services/seo-meta.service.ts
// Adapter: lit DB → transforme → appelle @repo/seo

import { Injectable } from '@nestjs/common';
import { SupabaseService } from '@/modules/database/supabase.service';
import {
  validatePageRole,
  PageModel,
  SeoViolation,
} from '@repo/seo';

@Injectable()
export class SeoMetaService {
  constructor(private readonly supabase: SupabaseService) {}

  async auditPageRole(urls: string[]): Promise<SeoViolation[]> {
    // 1. Fetch from DB
    const { data: pages } = await this.supabase
      .from('__seo_pages')
      .select('url, role, has_expert_content, title, description')
      .in('url', urls);

    // 2. Transform to PageModel (pure TS interface)
    const pageModels: PageModel[] = pages.map(p => ({
      url: p.url,
      role: p.role as PageRole,
      hasExpertContent: p.has_expert_content,
      title: p.title,
      description: p.description,
    }));

    // 3. Call pure validator from @repo/seo
    return pageModels.flatMap(validatePageRole);
  }
}
```

### Avantages

| Aspect | Résultat |
|--------|----------|
| **Unit Tests** | `packages/seo` testable sans Nest/DB |
| **Réutilisation** | Frontend peut importer types/utils |
| **Isolation** | Règles métier isolées des adapters |
| **CI/CD** | Validation SEO dans CI sans backend |

### Tests Purs (sans Nest)

```typescript
// packages/seo/src/__tests__/role.validator.test.ts

import { validatePageRole, PageRole, PageModel } from '../';

describe('validatePageRole', () => {
  it('should flag R1 with expert content', () => {
    const page: PageModel = {
      url: '/pieces/freinage',
      role: PageRole.R1_ROUTER,
      hasExpertContent: true, // ❌ Violation
    };

    const violations = validatePageRole(page);

    expect(violations).toHaveLength(1);
    expect(violations[0].rule).toBe('R1_NO_EXPERT_CONTENT');
    expect(violations[0].suggestedRole).toBe(PageRole.R4_REFERENCE);
  });
});
```

---

_Ce document est la source de verite pour les regles de gouvernance AI-COS._
