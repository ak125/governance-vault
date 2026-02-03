---
agent_id: support-analytics-service
agent_name: Support Analytics Service
status: active
owner: Support Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Support Analytics Service

## Identity

| Field | Value |
|-------|-------|
| ID | `support-analytics-service` |
| Name | Support Analytics Service |
| Status | active |
| Owner | Support Team |
| Description | Analyzes support tickets and generates metrics |

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
| Risk Factors | Support data analysis, anonymized metrics |

## Access Rights

- **Read**: support_tickets, resolution_logs
- **Write**: support_metrics (internal)
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (analytics service)
- **Audit Trail**: yes (via logs)

## Placement Decision

**MUST run on principal VPS** - Support analytics with database access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
