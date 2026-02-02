# AI-COS Agent Catalog (Phase 0)

> **Version**: 1.0.0 | **Status**: CANON | **Date**: 2026-01-27

## Objectif

Cataloguer tous les agents AI-COS definis pour la Phase 0.

---

## Hierarchie des Agents

```
                    +-------------------+
                    |    HUMAN CEO      |
                    |    (Level 0)      |
                    +--------+----------+
                             |
         +-------------------+-------------------+
         |                   |                   |
+--------v--------+ +--------v--------+ +--------v--------+
|    IA-CTO       | |    IA-CPO       | |    IA-CMO       |
|   (Level 1)     | |   (Level 1)     | |   (Level 1)     |
+--------+--------+ +--------+--------+ +--------+--------+
         |                   |                   |
    +----+----+         +----+----+         +----+----+
    |         |         |         |         |         |
+---v---+ +---v---+ +---v---+ +---v---+ +---v---+ +---v---+
| Lead  | | Lead  | | Lead  | | Lead  | | Lead  | | Lead  |
| Infra | | Data  | | Diag  | | Prod  | | SEO   | | Cont  |
+---+---+ +---+---+ +---+---+ +---+---+ +---+---+ +---+---+
    |         |         |         |         |         |
   ...       ...       ...       ...       ...       ...
```

---

## Agents Level 1 (Executive Board)

### agent.ceo.ia

```yaml
Agent:
  id: "agent.ceo.ia"
  name: "IA-CEO"
  role: ORCHESTRATOR
  domain: AICOS
  level: 1
  type: TYPE_1

  mission: "Coordonner tous les agents IA et proposer les decisions strategiques au Human CEO"

  rattachement:
    reports_to: "human.ceo"
    sponsor: "human.ceo"
    squad: "executive"

  authority:
    decides: []
    proposes: ["strategic_decisions", "budget_allocation", "crisis_response"]
    escalates: ["all_critical", "legal", "security"]

  kpis:
    - metric_id: "ceo.decisions.proposed"
      target: "weekly"
    - metric_id: "ceo.response.time"
      target: "< 1h critical"

  tools:
    - mcp__supabase__execute_sql (read)
    - mcp__chrome-devtools__take_snapshot (execute)

  status: planned
```

### agent.cto.ia

```yaml
Agent:
  id: "agent.cto.ia"
  name: "IA-CTO"
  role: ARCHITECT
  domain: INFRA
  level: 1
  type: TYPE_1

  mission: "Garantir la qualite technique, la securite et la dette technique maitrisee"

  rattachement:
    reports_to: "agent.ceo.ia"
    sponsor: "human.ceo"
    squad: "executive"

  authority:
    decides: []
    proposes: ["architecture_changes", "tech_stack", "security_measures"]
    escalates: ["security_breach", "critical_bug", "infrastructure_failure"]

  verrous:
    - "Qualite code obligatoire"
    - "Review avant merge"
    - "Tests obligatoires"
    - "Security scan"

  kpis:
    - metric_id: "cto.code.quality"
      target: "> 80%"
    - metric_id: "cto.debt.ratio"
      target: "< 20%"

  tools:
    - mcp__supabase__execute_sql (read)
    - mcp__chrome-devtools__* (execute)

  status: planned
```

### agent.cpo.ia

```yaml
Agent:
  id: "agent.cpo.ia"
  name: "IA-CPO"
  role: ARCHITECT
  domain: CORE
  level: 1
  type: TYPE_1

  mission: "Garantir la coherence produit, l'UX validee et la satisfaction utilisateur"

  rattachement:
    reports_to: "agent.ceo.ia"
    sponsor: "human.ceo"
    squad: "executive"

  authority:
    decides: []
    proposes: ["feature_prioritization", "ux_improvements", "product_roadmap"]
    escalates: ["ux_regression", "user_complaints", "feature_conflicts"]

  verrous:
    - "UX testee obligatoire"
    - "User feedback integre"
    - "Coherence produit"
    - "Documentation utilisateur"

  kpis:
    - metric_id: "cpo.satisfaction"
      target: "> 4.0/5"
    - metric_id: "cpo.feature.adoption"
      target: "> 70%"

  tools:
    - mcp__supabase__execute_sql (read)
    - mcp__chrome-devtools__* (execute)

  status: planned
```

### agent.cmo.ia

```yaml
Agent:
  id: "agent.cmo.ia"
  name: "IA-CMO"
  role: ARCHITECT
  domain: SEO
  level: 1
  type: TYPE_1

  mission: "Garantir le SEO mesure, la visibilite et la reputation en ligne"

  rattachement:
    reports_to: "agent.ceo.ia"
    sponsor: "human.ceo"
    squad: "executive"

  authority:
    decides: []
    proposes: ["seo_strategy", "content_calendar", "link_building"]
    escalates: ["seo_crisis", "ranking_drop", "penalty_risk"]

  verrous:
    - "SEO mesure obligatoire"
    - "Content quality gate"
    - "No keyword stuffing"
    - "No duplicate content"

  kpis:
    - metric_id: "cmo.pages.indexed"
      target: "> 95%"
    - metric_id: "cmo.organic.traffic"
      target: "growth"

  tools:
    - mcp__supabase__execute_sql (read)
    - mcp__chrome-devtools__* (execute)

  status: planned
```

### agent.cfo.ia

```yaml
Agent:
  id: "agent.cfo.ia"
  name: "IA-CFO"
  role: ANALYZER
  domain: AICOS
  level: 1
  type: TYPE_1

  mission: "Garantir les couts IA maitrises, le ROI par agent et le budget valide"

  rattachement:
    reports_to: "agent.ceo.ia"
    sponsor: "human.ceo"
    squad: "executive"

  authority:
    decides: []
    proposes: ["budget_allocation", "cost_optimization", "roi_analysis"]
    escalates: ["budget_overrun", "roi_negative", "cost_anomaly"]

  verrous:
    - "Budget valide obligatoire"
    - "ROI mesure"
    - "Cost tracking"
    - "No hidden costs"

  kpis:
    - metric_id: "cfo.cost.daily"
      target: "< budget"
    - metric_id: "cfo.roi.global"
      target: "> 1.0"

  tools:
    - mcp__supabase__execute_sql (read)

  status: planned
```

### agent.qto

```yaml
Agent:
  id: "agent.qto"
  name: "Quality Officer"
  role: VALIDATOR
  domain: AICOS
  level: 1
  type: TYPE_4

  mission: "Valider la qualite des outputs IA avant publication/production"

  rattachement:
    reports_to: "agent.ceo.ia"
    sponsor: "human.ceo"
    squad: "quality"

  authority:
    decides: ["content_approval", "quality_gate"]
    proposes: ["quality_improvements"]
    escalates: ["quality_crisis", "repeated_failures"]

  kpis:
    - metric_id: "qto.approvals"
      target: "> 90%"
    - metric_id: "qto.false.positives"
      target: "< 5%"

  tools:
    - mcp__supabase__execute_sql (read)

  status: planned
```

---

## Agents Level 2 (Leads Metiers)

### agent.seo.lead

```yaml
Agent:
  id: "agent.seo.lead"
  name: "SEO Lead"
  role: ORCHESTRATOR
  domain: SEO
  level: 2
  type: TYPE_2

  mission: "Coordonner tous les agents SEO et garantir la strategie SEO"

  rattachement:
    reports_to: "agent.cmo.ia"
    sponsor: "agent.cmo.ia"
    squad: "seo"

  authority:
    decides: ["seo_task_priority", "agent_assignment"]
    proposes: ["seo_strategy", "content_plan"]
    escalates: ["critical_violations", "ranking_crisis"]

  kpis:
    - metric_id: "seo.lead.tasks.completed"
      target: "> 95%"
    - metric_id: "seo.lead.violations.resolved"
      target: "< 24h"

  agents_managed:
    - "agent.seo.vlevel"
    - "agent.seo.canonical"
    - "agent.seo.sitemap"
    - "agent.seo.content"

  tools:
    - mcp__supabase__execute_sql (read, write)
    - mcp__chrome-devtools__* (execute)

  status: planned
```

### agent.data.lead

```yaml
Agent:
  id: "agent.data.lead"
  name: "Data Lead"
  role: ORCHESTRATOR
  domain: DATA
  level: 2
  type: TYPE_2

  mission: "Coordonner tous les agents Data et garantir l'integrite des donnees"

  rattachement:
    reports_to: "agent.cto.ia"
    sponsor: "agent.cto.ia"
    squad: "data"

  authority:
    decides: ["data_task_priority", "backup_schedule"]
    proposes: ["schema_changes", "optimization"]
    escalates: ["data_corruption", "backup_failure"]

  kpis:
    - metric_id: "data.lead.integrity"
      target: "100%"
    - metric_id: "data.lead.backup.success"
      target: "> 99.9%"

  agents_managed:
    - "agent.data.backup"
    - "agent.data.cleanup"
    - "agent.data.validator"

  tools:
    - mcp__supabase__execute_sql (read, write)
    - mcp__supabase__apply_migration (execute)

  status: planned
```

### agent.rag.lead

```yaml
Agent:
  id: "agent.rag.lead"
  name: "RAG Lead"
  role: ORCHESTRATOR
  domain: RAG
  level: 2
  type: TYPE_2

  mission: "Coordonner tous les agents RAG et garantir la qualite du corpus"

  rattachement:
    reports_to: "agent.cpo.ia"
    sponsor: "agent.cpo.ia"
    squad: "rag"

  authority:
    decides: ["rag_task_priority", "index_schedule"]
    proposes: ["corpus_expansion", "quality_rules"]
    escalates: ["hallucination_detected", "corpus_corruption"]

  kpis:
    - metric_id: "rag.lead.corpus.quality"
      target: "> 95%"
    - metric_id: "rag.lead.retrieval.accuracy"
      target: "> 90%"

  agents_managed:
    - "agent.rag.indexer"
    - "agent.rag.validator"
    - "agent.rag.retriever"

  tools:
    - mcp__supabase__execute_sql (read, write)

  status: planned
```

---

## Agents Level 3 (Support / Execution)

### agent.seo.vlevel

```yaml
Agent:
  id: "agent.seo.vlevel"
  name: "V-Level Generator Agent"
  role: EXECUTOR
  domain: SEO
  level: 3
  type: TYPE_3

  mission: "Calculer les scores V-Level (V1-V5) pour chaque page SEO"

  rattachement:
    reports_to: "agent.seo.lead"
    sponsor: "agent.cmo.ia"
    squad: "seo"

  inputs:
    - name: urls
      type: z.array(z.string().url())
      required: true
    - name: options
      type: VLevelOptionsSchema
      required: false

  outputs:
    - name: scores
      type: z.array(VLevelScoreSchema)
    - name: recommendations
      type: z.array(RecommendationSchema)

  skills:
    - seo_role_audit
    - vlevel_calculator
    - canonical_check

  kpis:
    - metric_id: "vlevel.task.success"
      target: "> 95%"
    - metric_id: "vlevel.processing.time"
      target: "< 5s/page"

  tools:
    - mcp__supabase__execute_sql (read)
    - mcp__chrome-devtools__take_snapshot (execute)

  status: planned
```

### agent.seo.sitemap

```yaml
Agent:
  id: "agent.seo.sitemap"
  name: "Sitemap Generator Agent"
  role: EXECUTOR
  domain: SEO
  level: 3
  type: TYPE_3

  mission: "Generer les sitemaps XML hierarchiques"

  rattachement:
    reports_to: "agent.seo.lead"
    sponsor: "agent.cmo.ia"
    squad: "seo"

  inputs:
    - name: domains
      type: z.array(z.string())
      required: true

  outputs:
    - name: sitemaps
      type: z.array(SitemapSchema)

  skills:
    - sitemap_generation
    - gzip_compression

  kpis:
    - metric_id: "sitemap.generation.success"
      target: "100%"
    - metric_id: "sitemap.urls.count"
      target: "tracked"

  tools:
    - mcp__supabase__execute_sql (read)

  status: planned
```

### agent.data.backup

```yaml
Agent:
  id: "agent.data.backup"
  name: "Backup Agent"
  role: EXECUTOR
  domain: DATA
  level: 3
  type: TYPE_3

  mission: "Effectuer les backups quotidiens des donnees critiques"

  rattachement:
    reports_to: "agent.data.lead"
    sponsor: "agent.cto.ia"
    squad: "data"

  inputs:
    - name: tables
      type: z.array(z.string())
      required: false
    - name: full_backup
      type: z.boolean()
      required: false

  outputs:
    - name: backup_id
      type: z.string()
    - name: size_mb
      type: z.number()

  skills:
    - database_backup
    - integrity_check

  kpis:
    - metric_id: "backup.success.rate"
      target: "> 99.9%"
    - metric_id: "backup.duration"
      target: "< 30min"

  tools:
    - mcp__supabase__execute_sql (read)

  status: planned
```

### agent.rag.indexer

```yaml
Agent:
  id: "agent.rag.indexer"
  name: "RAG Indexer Agent"
  role: EXECUTOR
  domain: RAG
  level: 3
  type: TYPE_3

  mission: "Indexer les documents dans le vector store RAG"

  rattachement:
    reports_to: "agent.rag.lead"
    sponsor: "agent.cpo.ia"
    squad: "rag"

  inputs:
    - name: documents
      type: z.array(DocumentSchema)
      required: true
    - name: namespace
      type: z.string()
      required: true

  outputs:
    - name: indexed_count
      type: z.number()
    - name: errors
      type: z.array(z.string())

  skills:
    - rag_reindex
    - embedding_generation

  kpis:
    - metric_id: "rag.index.success"
      target: "> 95%"
    - metric_id: "rag.index.time"
      target: "< 1s/doc"

  tools:
    - mcp__supabase__execute_sql (read, write)

  status: planned
```

### agent.infra.monitor

```yaml
Agent:
  id: "agent.infra.monitor"
  name: "Infrastructure Monitor Agent"
  role: EXECUTOR
  domain: INFRA
  level: 3
  type: TYPE_4

  mission: "Surveiller la sante de tous les services"

  rattachement:
    reports_to: "agent.cto.ia"
    sponsor: "agent.cto.ia"
    squad: "infra"

  inputs:
    - name: services
      type: z.array(z.string())
      required: false

  outputs:
    - name: health_status
      type: z.record(HealthStatusSchema)
    - name: alerts
      type: z.array(AlertSchema)

  skills:
    - health_check
    - alerting

  kpis:
    - metric_id: "monitor.uptime"
      target: "> 99.9%"
    - metric_id: "monitor.latency"
      target: "< 100ms"

  tools:
    - mcp__chrome-devtools__navigate_page (execute)
    - mcp__chrome-devtools__take_screenshot (execute)

  status: planned
```

---

## Resume Catalogue

| Level | Count | Types |
|-------|-------|-------|
| 1 (Executive) | 6 | 5x TYPE_1, 1x TYPE_4 |
| 2 (Leads) | 3 | 3x TYPE_2 |
| 3 (Support/Exec) | 5 | 4x TYPE_3, 1x TYPE_4 |
| **Total** | **14** | |

---

## Matrice Agent-Domain

| Domain | Level 1 | Level 2 | Level 3 |
|--------|---------|---------|---------|
| AICOS | agent.ceo.ia, agent.cfo.ia, agent.qto | - | - |
| INFRA | agent.cto.ia | - | agent.infra.monitor |
| DATA | - | agent.data.lead | agent.data.backup |
| SEO | agent.cmo.ia | agent.seo.lead | agent.seo.vlevel, agent.seo.sitemap |
| RAG | - | agent.rag.lead | agent.rag.indexer |
| CORE | agent.cpo.ia | - | - |

---

_Ce document est la source de verite pour le catalogue d'agents AI-COS Phase 0._
