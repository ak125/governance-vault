# AI-COS Task Catalog (Phase 0)

> **Version**: 1.0.0 | **Status**: CANON | **Date**: 2026-01-27

## Objectif

Cataloguer toutes les taches automatisables dans le cadre d'AI-COS Phase 0.

---

## Schema Task

```yaml
Task:
  id: string                  # Unique (ex: "task.seo.audit.vlevel")
  name: string                # Display name
  description: string         # Description courte
  domain: Domain              # CORE, INFRA, DATA, SEO, RAG, CART, AICOS
  priority: Priority          # P0 | P1 | P2 | P3
  complexity: Complexity      # trivial | simple | medium | complex | critical

  # Assignation
  assigned_agent: string      # Agent responsable
  required_skills: string[]   # Skills necessaires

  # Execution
  trigger: TriggerType        # manual | scheduled | event | threshold
  frequency: string           # cron expression ou description
  estimated_duration: string  # Ex: "5 minutes", "1 hour"

  # Dependances
  depends_on: string[]        # Tasks prerequises
  blocks: string[]            # Tasks bloquees par celle-ci

  # Validation
  acceptance_criteria: string[] # Criteres de succes
  rollback_plan: string       # Plan de rollback

  # Phase
  phase: Phase                # P0 | P1 | P2 | P3
  status: TaskStatus          # planned | in_progress | completed | blocked
```

---

## Enums

```typescript
enum Priority {
  P0 = 'P0',  // Critique - Bloquant
  P1 = 'P1',  // Haute - A faire rapidement
  P2 = 'P2',  // Moyenne - Planifie
  P3 = 'P3'   // Basse - Nice to have
}

enum Complexity {
  TRIVIAL = 'trivial',     // < 1h, pas de risque
  SIMPLE = 'simple',       // 1-4h, risque faible
  MEDIUM = 'medium',       // 1-3j, risque modere
  COMPLEX = 'complex',     // 1-2sem, risque eleve
  CRITICAL = 'critical'    // Necessite validation humaine
}

enum Phase {
  P0 = 'P0',  // Fondations
  P1 = 'P1',  // MVP
  P2 = 'P2',  // Enrichissement
  P3 = 'P3'   // Excellence
}

enum TaskStatus {
  PLANNED = 'planned',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  BLOCKED = 'blocked'
}
```

---

## Catalogue Phase 0 (Fondations)

### Domain: AICOS (Gouvernance)

```yaml
Tasks:
  - id: "task.aicos.contracts.define"
    name: "Definir les contrats d'agents"
    description: "Creer les schemas YAML pour AgentContract, SkillContract, LoopContract"
    domain: AICOS
    priority: P0
    complexity: medium
    assigned_agent: "agent.aicos.architect"
    required_skills: ["schema_design", "typescript_types"]
    trigger: manual
    frequency: "one-time"
    estimated_duration: "2 days"
    depends_on: []
    blocks: ["task.aicos.agents.create"]
    acceptance_criteria:
      - "Schema AgentContract valide"
      - "Schema SkillContract valide"
      - "Schema LoopContract valide"
      - "Types TypeScript generes"
    rollback_plan: "Revenir aux specs precedentes"
    phase: P0
    status: completed

  - id: "task.aicos.governance.rules"
    name: "Definir les regles de gouvernance"
    description: "Documenter les 7 regles immutables et 16 regles IA"
    domain: AICOS
    priority: P0
    complexity: medium
    assigned_agent: "agent.aicos.governance"
    required_skills: ["documentation", "governance"]
    trigger: manual
    frequency: "one-time"
    estimated_duration: "1 day"
    depends_on: []
    blocks: ["task.aicos.validation.implement"]
    acceptance_criteria:
      - "7 regles immutables documentees"
      - "16 regles IA documentees"
      - "Matrice d'audit definie"
    rollback_plan: "N/A - documentation"
    phase: P0
    status: completed

  - id: "task.aicos.memory.model"
    name: "Definir le modele de memoire"
    description: "Creer le schema de memoire short-term, long-term, shared"
    domain: AICOS
    priority: P0
    complexity: medium
    assigned_agent: "agent.aicos.architect"
    required_skills: ["database_design", "redis", "vector_db"]
    trigger: manual
    frequency: "one-time"
    estimated_duration: "1 day"
    depends_on: ["task.aicos.contracts.define"]
    blocks: ["task.aicos.memory.implement"]
    acceptance_criteria:
      - "Schema memoire short-term"
      - "Schema memoire long-term"
      - "Schema memoire partagee"
      - "Tables Supabase definies"
    rollback_plan: "Revenir au schema precedent"
    phase: P0
    status: completed

  - id: "task.aicos.kpi.system"
    name: "Definir le systeme de KPIs"
    description: "Creer le framework de metriques et alertes"
    domain: AICOS
    priority: P0
    complexity: medium
    assigned_agent: "agent.aicos.architect"
    required_skills: ["metrics_design", "alerting"]
    trigger: manual
    frequency: "one-time"
    estimated_duration: "1 day"
    depends_on: ["task.aicos.contracts.define"]
    blocks: ["task.aicos.dashboard.ceo"]
    acceptance_criteria:
      - "Schema KPI defini"
      - "Dashboard CEO (10 max) defini"
      - "Regles d'alertes definies"
    rollback_plan: "N/A - documentation"
    phase: P0
    status: completed
```

### Domain: SEO

```yaml
Tasks:
  - id: "task.seo.audit.vlevel"
    name: "Audit V-Level des pages"
    description: "Analyser et scorer les pages SEO selon V1-V5"
    domain: SEO
    priority: P0
    complexity: medium
    assigned_agent: "agent.seo.vlevel"
    required_skills: ["seo_role_audit", "vlevel_calculator"]
    trigger: scheduled
    frequency: "0 2 * * *"
    estimated_duration: "30 minutes"
    depends_on: []
    blocks: []
    acceptance_criteria:
      - "Toutes les pages analysees"
      - "Scores V-level calcules"
      - "Violations detectees"
    rollback_plan: "Pas de modification, audit en lecture seule"
    phase: P0
    status: planned

  - id: "task.seo.canonical.check"
    name: "Verification des canonicals"
    description: "Verifier la coherence des balises canonical"
    domain: SEO
    priority: P0
    complexity: simple
    assigned_agent: "agent.seo.canonical"
    required_skills: ["canonical_check"]
    trigger: scheduled
    frequency: "0 3 * * *"
    estimated_duration: "15 minutes"
    depends_on: []
    blocks: []
    acceptance_criteria:
      - "Tous les canonicals verifies"
      - "Conflits detectes"
      - "Rapport genere"
    rollback_plan: "Lecture seule"
    phase: P0
    status: planned

  - id: "task.seo.sitemap.generate"
    name: "Generation des sitemaps"
    description: "Generer les sitemaps XML hierarchiques"
    domain: SEO
    priority: P0
    complexity: medium
    assigned_agent: "agent.seo.sitemap"
    required_skills: ["sitemap_generation"]
    trigger: scheduled
    frequency: "0 4 * * *"
    estimated_duration: "45 minutes"
    depends_on: ["task.seo.canonical.check"]
    blocks: []
    acceptance_criteria:
      - "Index sitemap genere"
      - "Sub-sitemaps < 50k URLs"
      - "Compression GZIP"
    rollback_plan: "Restaurer sitemaps precedents"
    phase: P0
    status: planned
```

### Domain: DATA

```yaml
Tasks:
  - id: "task.data.backup.daily"
    name: "Backup quotidien"
    description: "Backup automatique des tables critiques"
    domain: DATA
    priority: P0
    complexity: simple
    assigned_agent: "agent.data.backup"
    required_skills: ["database_backup"]
    trigger: scheduled
    frequency: "0 1 * * *"
    estimated_duration: "30 minutes"
    depends_on: []
    blocks: []
    acceptance_criteria:
      - "Backup complet"
      - "Verification d'integrite"
      - "Notification de succes"
    rollback_plan: "Alerter admin"
    phase: P0
    status: planned

  - id: "task.data.cleanup.expired"
    name: "Nettoyage donnees expirees"
    description: "Supprimer les donnees au-dela de la retention"
    domain: DATA
    priority: P1
    complexity: simple
    assigned_agent: "agent.data.cleanup"
    required_skills: ["data_cleanup"]
    trigger: scheduled
    frequency: "0 5 * * 0"
    estimated_duration: "1 hour"
    depends_on: ["task.data.backup.daily"]
    blocks: []
    acceptance_criteria:
      - "Donnees expirees identifiees"
      - "Suppression validee"
      - "Espace libere"
    rollback_plan: "Restaurer depuis backup"
    phase: P0
    status: planned
```

### Domain: RAG

```yaml
Tasks:
  - id: "task.rag.index.knowledge"
    name: "Indexation knowledge base"
    description: "Indexer les documents de la knowledge base"
    domain: RAG
    priority: P0
    complexity: medium
    assigned_agent: "agent.rag.indexer"
    required_skills: ["rag_reindex", "embedding_generation"]
    trigger: event
    frequency: "on document_updated"
    estimated_duration: "Variable"
    depends_on: []
    blocks: []
    acceptance_criteria:
      - "Documents indexes"
      - "Embeddings generes"
      - "Recherche fonctionnelle"
    rollback_plan: "Rollback vers version precedente"
    phase: P0
    status: planned

  - id: "task.rag.sync.validate"
    name: "Validation sync RAG"
    description: "Verifier la coherence du corpus RAG"
    domain: RAG
    priority: P0
    complexity: simple
    assigned_agent: "agent.rag.validator"
    required_skills: ["rag_validation"]
    trigger: scheduled
    frequency: "0 6 * * *"
    estimated_duration: "20 minutes"
    depends_on: ["task.rag.index.knowledge"]
    blocks: []
    acceptance_criteria:
      - "Aucune incoherence detectee"
      - "truth_level verifie"
      - "Rapport genere"
    rollback_plan: "Quarantaine documents suspects"
    phase: P0
    status: planned
```

### Domain: INFRA

```yaml
Tasks:
  - id: "task.infra.health.check"
    name: "Health check services"
    description: "Verifier la sante de tous les services"
    domain: INFRA
    priority: P0
    complexity: trivial
    assigned_agent: "agent.infra.monitor"
    required_skills: ["health_check"]
    trigger: scheduled
    frequency: "*/5 * * * *"
    estimated_duration: "1 minute"
    depends_on: []
    blocks: []
    acceptance_criteria:
      - "Tous services up"
      - "Latence < SLA"
      - "Alertes si down"
    rollback_plan: "Alerter on-call"
    phase: P0
    status: planned

  - id: "task.infra.logs.aggregate"
    name: "Agregation des logs"
    description: "Collecter et agreger les logs de tous les services"
    domain: INFRA
    priority: P1
    complexity: simple
    assigned_agent: "agent.infra.logs"
    required_skills: ["log_aggregation"]
    trigger: scheduled
    frequency: "*/15 * * * *"
    estimated_duration: "5 minutes"
    depends_on: []
    blocks: []
    acceptance_criteria:
      - "Logs collectes"
      - "Erreurs detectees"
      - "Metriques calculees"
    rollback_plan: "N/A"
    phase: P0
    status: planned
```

---

## Resume Phase 0

| Domain | Tasks P0 | Status |
|--------|----------|--------|
| AICOS  | 4        | completed |
| SEO    | 3        | planned |
| DATA   | 2        | planned |
| RAG    | 2        | planned |
| INFRA  | 2        | planned |
| **Total** | **13** | **4 completed** |

---

## Dependances (DAG simplifie)

```
task.aicos.contracts.define
    |
    +---> task.aicos.memory.model
    |         |
    |         +---> task.aicos.memory.implement (P1)
    |
    +---> task.aicos.kpi.system
              |
              +---> task.aicos.dashboard.ceo (P1)

task.seo.canonical.check
    |
    +---> task.seo.sitemap.generate

task.data.backup.daily
    |
    +---> task.data.cleanup.expired

task.rag.index.knowledge
    |
    +---> task.rag.sync.validate
```

---

_Ce document est la source de verite pour le catalogue de taches AI-COS Phase 0._
