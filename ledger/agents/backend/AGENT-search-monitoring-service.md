---
agent_id: search-monitoring-service
agent_name: Search Monitoring Service
status: active
owner: Backend Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Search Monitoring Service

## Identity

| Field | Value |
|-------|-------|
| ID | `search-monitoring-service` |
| Name | Search Monitoring Service |
| Status | active |
| Owner | Backend Team |
| Description | Monitors search performance and query patterns |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (per ADR-008) |
| Runtime | NestJS Service |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Search analytics, no user data exposure |

## Access Rights

- **Read**: search_logs, query_patterns
- **Write**: search_metrics (internal)
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (monitoring service)
- **Audit Trail**: yes (via metrics)

## Placement Decision

**MUST run on principal VPS** - Search monitoring with database access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
