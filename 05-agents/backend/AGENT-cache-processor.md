---
agent_id: cache-processor
agent_name: Cache Processor
status: disabled
owner: Backend Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Cache Processor

## Identity

| Field | Value |
|-------|-------|
| ID | `cache-processor` |
| Name | Cache Processor |
| Status | **disabled** |
| Owner | Backend Team |
| Description | Processes cache invalidation events |

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
| Risk Factors | Cache operations only |

## Access Rights

- **Read**: cache_events queue
- **Write**: Redis cache (invalidation)
- **Secrets**: REDIS_URL

## Governance

- **Verdict**: APPROVED (when enabled)
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (internal service)
- **Audit Trail**: no (routine operations)

## Placement Decision

**MUST run on principal VPS** - Cache processing requires Redis access.

## Activation Status

Currently **DISABLED**. Enable via environment flag when ready.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
