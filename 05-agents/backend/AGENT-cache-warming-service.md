---
agent_id: cache-warming-service
agent_name: Cache Warming Service
status: active
owner: Backend Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Cache Warming Service

## Identity

| Field | Value |
|-------|-------|
| ID | `cache-warming-service` |
| Name | Cache Warming Service |
| Status | active |
| Owner | Backend Team |
| Description | Pre-warms Redis cache with frequently accessed data |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (per ADR-008) |
| Runtime | NestJS Cron Service |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Cache operations, no sensitive data modification |

## Access Rights

- **Read**: __products, __catalog tables
- **Write**: Redis cache keys
- **Secrets**: REDIS_URL, SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (cache operations)
- **Audit Trail**: no (routine operations)

## Placement Decision

**MUST run on principal VPS** - Requires database and Redis access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
