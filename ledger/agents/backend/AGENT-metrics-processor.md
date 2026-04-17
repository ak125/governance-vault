---
agent_id: worker.metrics-processor
agent_name: Metrics Processor
status: active
owner: Backend Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-03-08
execution_engine: NestJS BullMQ
zone: principal_vps
---

# Agent: Metrics Processor

## Identity

| Field | Value |
|-------|-------|
| ID | `worker.metrics-processor` |
| Name | Metrics Processor |
| Status | active |
| Owner | Backend Team |
| Description | BullMQ processor — collecte et aggregation metriques systeme |
| Source | `backend/src/modules/system/processors/metrics.processor.ts` |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps |
| Runtime | NestJS BullMQ Worker |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Read-only metrics collection |

## Access Rights

- **Read**: System metrics, health endpoints
- **Write**: Metrics storage (via internal service)
- **Secrets**: DATABASE_URL, GROQ_API_KEY (via env)

## Governance

- **Verdict**: APPROVED_WITH_CONDITIONS
- **Conditions**: RPC-gated writes only, feature flag controlled
- **Related ADR**: ADR-003, ADR-009, ADR-011
- **Airlock Required**: no (automated worker, RPC-gated)
- **Audit Trail**: yes (BullMQ job logs)

## Placement Decision

**Runs on principal_vps** - Backend worker process, Docker container.

---

_Last audit: 2026-03-08_
_Auditor: Claude (Governance Analyst)_
