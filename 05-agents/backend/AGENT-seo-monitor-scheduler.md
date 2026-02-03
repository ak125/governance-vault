---
agent_id: seo-monitor-scheduler
agent_name: SEO Monitor Scheduler
status: active
owner: Backend Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SEO Monitor Scheduler

## Identity

| Field | Value |
|-------|-------|
| ID | `seo-monitor-scheduler` |
| Name | SEO Monitor Scheduler |
| Status | active |
| Owner | Backend Team |
| Description | Schedules SEO monitoring jobs (30min critical + 6h random sample) |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (per ADR-008) |
| Runtime | NestJS Worker (port 3001) |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Database read operations, internal service |

## Access Rights

- **Read**: __seo_*, __products tables
- **Write**: seo_monitor_results, alerts (internal DB)
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-003, ADR-009, ADR-008
- **Airlock Required**: no (internal service)
- **Audit Trail**: yes (via logs)

## Placement Decision

**MUST run on principal VPS** - Requires database and Redis access for scheduling.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
