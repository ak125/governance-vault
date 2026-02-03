---
agent_id: metrics-processor
agent_name: Metrics Processor
status: active
owner: Infrastructure Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Metrics Processor

## Identity

| Field | Value |
|-------|-------|
| ID | `metrics-processor` |
| Name | Metrics Processor |
| Status | active |
| Owner | Infrastructure Team |
| Description | Aggregates and processes application metrics for dashboards |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (per ADR-008) |
| Runtime | NestJS Worker |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Metrics aggregation, no sensitive data access |

## Access Rights

- **Read**: metrics tables, Redis counters
- **Write**: aggregated_metrics (internal)
- **Secrets**: REDIS_URL

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (internal processing)
- **Audit Trail**: yes (via logs)

## Placement Decision

**MUST run on principal VPS** - Metrics processing requires internal access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
