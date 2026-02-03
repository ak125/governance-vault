---
agent_id: seo-audit-scheduler
agent_name: SEO Audit Scheduler
status: active
owner: Backend Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SEO Audit Scheduler

## Identity

| Field | Value |
|-------|-------|
| ID | `seo-audit-scheduler` |
| Name | SEO Audit Scheduler |
| Status | active |
| Owner | Backend Team |
| Description | Schedules periodic SEO audits and health checks |

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
| Risk Factors | Scheduled operations only |

## Access Rights

- **Read**: __seo_* tables, audit configurations
- **Write**: audit_results (internal)
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-003, ADR-009, ADR-008
- **Airlock Required**: no (internal service)
- **Audit Trail**: yes (via logs)

## Placement Decision

**MUST run on principal VPS** - Cron service with database access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
