---
agent_id: agent.infra.monitor
agent_name: Infrastructure Monitor Agent
status: planned
owner: Infrastructure Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Infrastructure Monitor Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.infra.monitor` |
| Name | Infrastructure Monitor Agent |
| Status | **planned** (Phase 0) |
| Owner | Infrastructure Team |
| Description | Monitors infrastructure health and metrics |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | AI-COS Framework |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Metrics collection |

## Access Rights

- **Read**: infrastructure metrics, logs
- **Write**: none
- **Secrets**: monitoring tokens

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Read-only monitoring
- **Related ADR**: ADR-009
- **Airlock Required**: no (monitoring only)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - AI-COS Level 3 Executor with monitoring access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
