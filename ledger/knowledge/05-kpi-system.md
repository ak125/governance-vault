# AI-COS KPI System (Systeme d'Indicateurs)

> **Version**: 1.0.0 | **Status**: CANON | **Date**: 2026-01-27

## Objectif

Definir le systeme de KPIs pour mesurer, alerter et piloter les agents AI-COS.

---

## Principe Fondamental

```
+---------------------------------------------------------------------+
|                                                                      |
|   PAS D'INDICATEUR = SUPPRESSION                                    |
|                                                                      |
|   Tout agent DOIT avoir au moins 1 KPI mesurable.                   |
|   Un agent sans KPI est un agent inexistant.                        |
|                                                                      |
+---------------------------------------------------------------------+
```

---

## Schema KPI Contract

```yaml
KPI:
  # ===================================================================
  # IDENTITE
  # ===================================================================
  metric_id: string           # Unique (ex: "seo.violations.count")
  name: string                # Display name
  description: string         # Description courte
  domain: Domain              # CORE, INFRA, DATA, SEO, RAG, CART, AICOS
  owner: string               # Equipe responsable

  # ===================================================================
  # TYPE & CALCUL
  # ===================================================================
  type: MetricType            # counter | gauge | histogram | summary
  unit: string                # Ex: "count", "percentage", "ms", "tokens"
  aggregation: Aggregation    # sum | avg | max | min | count | p95 | p99

  calculation:
    formula: string           # Expression de calcul
    sources:                  # Sources de donnees
      - source_type: string   # database | api | metric | log
        query: string         # Requete ou endpoint
        refresh_interval_s: number

  # ===================================================================
  # SEUILS & ALERTES
  # ===================================================================
  thresholds:
    target: number            # Objectif (vert)
    warning: number           # Seuil warning (jaune)
    critical: number          # Seuil critique (rouge)
    direction: Direction      # lower_is_better | higher_is_better

  alerts:
    - level: AlertLevel       # info | warning | error | critical
      condition: string       # Expression de condition
      channels: string[]      # ["slack", "email", "pagerduty"]
      cooldown_minutes: number # Delai entre alertes
      auto_escalate: boolean  # Escalade auto si non resolu

  # ===================================================================
  # RETENTION & HISTORIQUE
  # ===================================================================
  retention:
    raw_days: number          # Donnees brutes
    hourly_days: number       # Agregation horaire
    daily_days: number        # Agregation journaliere
    monthly_years: number     # Agregation mensuelle

  # ===================================================================
  # VISUALISATION
  # ===================================================================
  visualization:
    chart_type: ChartType     # line | bar | gauge | heatmap | table
    display_format: string    # Ex: "{value}%" ou "{value} ms"
    color_scheme: ColorScheme # traffic_light | gradient | custom
```

---

## Enums

```typescript
enum MetricType {
  COUNTER = 'counter',       // Incrementing (ex: requests)
  GAUGE = 'gauge',           // Point-in-time (ex: CPU %)
  HISTOGRAM = 'histogram',   // Distribution
  SUMMARY = 'summary'        // Quantiles
}

enum Aggregation {
  SUM = 'sum',
  AVG = 'avg',
  MAX = 'max',
  MIN = 'min',
  COUNT = 'count',
  P95 = 'p95',
  P99 = 'p99'
}

enum Direction {
  LOWER_IS_BETTER = 'lower_is_better',
  HIGHER_IS_BETTER = 'higher_is_better'
}

enum AlertLevel {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

enum ChartType {
  LINE = 'line',
  BAR = 'bar',
  GAUGE = 'gauge',
  HEATMAP = 'heatmap',
  TABLE = 'table'
}

enum ColorScheme {
  TRAFFIC_LIGHT = 'traffic_light',  // Red/Yellow/Green
  GRADIENT = 'gradient',             // Continuous
  CUSTOM = 'custom'
}
```

---

## Dashboard CEO (10 indicateurs max)

```yaml
DashboardCEO:
  name: "CEO Dashboard"
  max_indicators: 10
  refresh_interval_s: 60

  sections:
    - section_id: "sante_ia"
      name: "Sante IA"
      indicators:
        - metric_id: "aicos.cost.daily"
          display: "Cout IA/jour"
        - metric_id: "aicos.alerts.qto"
          display: "Alertes QTO"
        - metric_id: "aicos.conflicts.agents"
          display: "Conflits agents"

    - section_id: "diagnostic"
      name: "Diagnostic"
      indicators:
        - metric_id: "diagnostic.accuracy"
          display: "Taux justesse"
        - metric_id: "diagnostic.blocked"
          display: "Cas bloques"

    - section_id: "seo"
      name: "SEO"
      indicators:
        - metric_id: "seo.pages.indexed"
          display: "Pages indexees"
        - metric_id: "seo.content.rejected"
          display: "Rejets contenu"

    - section_id: "business"
      name: "Business"
      indicators:
        - metric_id: "business.conversion"
          display: "Conversion"
        - metric_id: "business.basket.avg"
          display: "Panier moyen"
        - metric_id: "business.roi.marketing"
          display: "ROI marketing"

  rules:
    - "D1: Max 10 indicateurs"
    - "D2: Seuil vert + rouge obligatoire"
    - "D3: 1 action par indicateur rouge"
    - "D4: Vue quotidienne minimum"
    - "D5: Tendance 7j visible"
```

---

## KPIs par Type d'Agent

```yaml
KPIsByAgentType:
  TYPE_1_DECISIONAL:
    required_kpis:
      - metric_id: "agent.roi"
        description: "ROI genere par l'agent"
        target: "> 0"
      - metric_id: "agent.impact.business"
        description: "Impact business mesurable"
        target: "defined"
      - metric_id: "agent.decisions.validated"
        description: "Decisions validees par humain"
        target: "> 95%"

  TYPE_2_ANALYSIS:
    required_kpis:
      - metric_id: "agent.validation.rate"
        description: "Taux de validation"
        target: "> 90%"
      - metric_id: "agent.clarity.score"
        description: "Score de clarte"
        target: "> 80%"
      - metric_id: "agent.usage.real"
        description: "Utilisation reelle"
        target: "> 0"

  TYPE_3_EXECUTION:
    required_kpis:
      - metric_id: "agent.time.saved"
        description: "Temps gagne"
        target: "> 0"
      - metric_id: "agent.volume.processed"
        description: "Volume traite"
        target: "> threshold"
      - metric_id: "agent.error.rate"
        description: "Taux d'erreur"
        target: "< 5%"

  TYPE_4_CONTROL:
    required_kpis:
      - metric_id: "agent.scans.executed"
        description: "Scans executes"
        target: "scheduled"
      - metric_id: "agent.alerts.raised"
        description: "Alertes levees"
        target: "when_needed"
      - metric_id: "agent.resolution.time"
        description: "Temps de resolution"
        target: "< SLA"
```

---

## Exemples KPIs Concrets

### KPI 1: SEO Violations Count

```yaml
KPI:
  metric_id: "seo.violations.count"
  name: "SEO Violations"
  description: "Nombre de violations SEO detectees"
  domain: SEO
  owner: "seo-team"

  type: gauge
  unit: "count"
  aggregation: sum

  calculation:
    formula: "COUNT(violations WHERE status = 'open')"
    sources:
      - source_type: database
        query: "SELECT COUNT(*) FROM __seo_violations WHERE status = 'open'"
        refresh_interval_s: 300

  thresholds:
    target: 0
    warning: 10
    critical: 50
    direction: lower_is_better

  alerts:
    - level: warning
      condition: "value > 10"
      channels: ["slack"]
      cooldown_minutes: 60
      auto_escalate: false
    - level: critical
      condition: "value > 50"
      channels: ["slack", "email"]
      cooldown_minutes: 30
      auto_escalate: true

  retention:
    raw_days: 7
    hourly_days: 30
    daily_days: 365
    monthly_years: 3

  visualization:
    chart_type: line
    display_format: "{value} violations"
    color_scheme: traffic_light
```

### KPI 2: Agent Success Rate

```yaml
KPI:
  metric_id: "agent.success.rate"
  name: "Agent Success Rate"
  description: "Pourcentage de taches reussies"
  domain: AICOS
  owner: "platform-team"

  type: gauge
  unit: "percentage"
  aggregation: avg

  calculation:
    formula: "(successful_tasks / total_tasks) * 100"
    sources:
      - source_type: database
        query: |
          SELECT
            (COUNT(*) FILTER (WHERE status = 'success') * 100.0 / NULLIF(COUNT(*), 0))
          FROM __aicos_task_executions
          WHERE created_at > NOW() - INTERVAL '24 hours'
        refresh_interval_s: 60

  thresholds:
    target: 95
    warning: 85
    critical: 70
    direction: higher_is_better

  alerts:
    - level: warning
      condition: "value < 85"
      channels: ["slack"]
      cooldown_minutes: 30
      auto_escalate: false
    - level: critical
      condition: "value < 70"
      channels: ["slack", "pagerduty"]
      cooldown_minutes: 15
      auto_escalate: true

  retention:
    raw_days: 7
    hourly_days: 30
    daily_days: 365
    monthly_years: 3

  visualization:
    chart_type: gauge
    display_format: "{value}%"
    color_scheme: traffic_light
```

### KPI 3: Cost per Token

```yaml
KPI:
  metric_id: "aicos.cost.per.token"
  name: "AI Cost per Token"
  description: "Cout moyen par token utilise"
  domain: AICOS
  owner: "finance-team"

  type: gauge
  unit: "EUR"
  aggregation: avg

  calculation:
    formula: "total_cost / total_tokens"
    sources:
      - source_type: api
        query: "/api/billing/usage"
        refresh_interval_s: 3600

  thresholds:
    target: 0.00001
    warning: 0.00002
    critical: 0.00005
    direction: lower_is_better

  alerts:
    - level: warning
      condition: "value > 0.00002"
      channels: ["email"]
      cooldown_minutes: 1440
      auto_escalate: false

  retention:
    raw_days: 30
    hourly_days: 90
    daily_days: 365
    monthly_years: 5

  visualization:
    chart_type: line
    display_format: "{value} EUR/token"
    color_scheme: gradient
```

---

## Tables Supabase (Schema)

```sql
-- Table: __aicos_metrics_raw
CREATE TABLE __aicos_metrics_raw (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_id TEXT NOT NULL,
  value NUMERIC NOT NULL,
  labels JSONB,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metrics_raw_metric ON __aicos_metrics_raw(metric_id);
CREATE INDEX idx_metrics_raw_ts ON __aicos_metrics_raw(timestamp);

-- Table: __aicos_metrics_hourly (agregation)
CREATE TABLE __aicos_metrics_hourly (
  metric_id TEXT NOT NULL,
  hour TIMESTAMPTZ NOT NULL,
  count INTEGER,
  sum NUMERIC,
  avg NUMERIC,
  min NUMERIC,
  max NUMERIC,
  p95 NUMERIC,
  p99 NUMERIC,
  PRIMARY KEY (metric_id, hour)
);

-- Table: __aicos_alerts
CREATE TABLE __aicos_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_id TEXT NOT NULL,
  level TEXT NOT NULL,
  value NUMERIC NOT NULL,
  threshold NUMERIC NOT NULL,
  message TEXT,
  acknowledged BOOLEAN DEFAULT FALSE,
  acknowledged_by TEXT,
  acknowledged_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_metric ON __aicos_alerts(metric_id);
CREATE INDEX idx_alerts_level ON __aicos_alerts(level);
CREATE INDEX idx_alerts_ack ON __aicos_alerts(acknowledged);
```

---

## Interface TypeScript

```typescript
// packages/contracts/src/kpi.ts

export interface KpiContract {
  readonly definition: KpiDefinition;
  record(value: number, labels?: Record<string, string>): Promise<void>;
  query(timeRange: TimeRange): Promise<MetricData[]>;
  checkThresholds(): Promise<ThresholdCheck>;
  alert(level: AlertLevel, message: string): Promise<void>;
}

export interface KpiDefinition {
  metricId: string;
  name: string;
  type: MetricType;
  unit: string;
  thresholds: Thresholds;
  alerts: AlertConfig[];
}

export interface MetricData {
  timestamp: Date;
  value: number;
  labels?: Record<string, string>;
}

export interface ThresholdCheck {
  metricId: string;
  currentValue: number;
  status: 'green' | 'yellow' | 'red';
  threshold: number;
  direction: Direction;
}

export interface KpiRegistry {
  register(kpi: KpiContract): void;
  get(metricId: string): KpiContract | undefined;
  list(domain?: Domain): KpiContract[];
  validate(): ValidationResult;
}
```

---

## Regles de Validation

### R1: Tout agent DOIT avoir au moins 1 KPI

```typescript
// Validation au demarrage
function validateAgent(agent: AgentContract): boolean {
  if (!agent.manifest.kpis || agent.manifest.kpis.length === 0) {
    throw new Error(`Agent ${agent.manifest.id} has no KPIs - DELETION REQUIRED`);
  }
  return true;
}
```

### R2: Tout KPI DOIT avoir des seuils definis

```typescript
// OBLIGATOIRE
const kpi: KpiDefinition = {
  metricId: 'example.metric',
  thresholds: {
    target: 100,
    warning: 80,
    critical: 50,
    direction: 'higher_is_better'
  }
};
```

### R3: Les alertes critiques DOIVENT escalader automatiquement

```typescript
// OBLIGATOIRE pour level = 'critical'
alerts: [
  {
    level: 'critical',
    auto_escalate: true, // OBLIGATOIRE
    channels: ['slack', 'pagerduty'] // Au moins 2 canaux
  }
]
```

---

_Ce document est la source de verite pour le systeme de KPIs AI-COS._
