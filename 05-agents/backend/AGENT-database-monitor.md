---
agent_id: database-monitor
agent_name: Database Monitor
status: active
owner: Infrastructure Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Database Monitor

## Identity

| Field | Value |
|-------|-------|
| ID | `database-monitor` |
| Name | Database Monitor |
| Status | active |
| Owner | Infrastructure Team |
| Description | Monitors database health, connections, and performance metrics |

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
| Risk Factors | Read-only database access for metrics |

## Access Rights

- **Read**: pg_stat_*, system tables
- **Write**: none
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (monitoring only)
- **Audit Trail**: yes (via metrics)

## Placement Decision

**MUST run on principal VPS** - Database monitoring requires internal access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
