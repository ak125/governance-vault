---
agent_id: seo-monitor-processor
agent_name: SEO Monitor Processor
status: active
owner: Backend Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SEO Monitor Processor

## Identity

| Field | Value |
|-------|-------|
| ID | `seo-monitor-processor` |
| Name | SEO Monitor Processor |
| Status | active |
| Owner | Backend Team |
| Description | Processes SEO monitoring jobs queued by scheduler |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (per ADR-008) |
| Runtime | NestJS Worker Process |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Database read operations, internal processing |

## Access Rights

- **Read**: __seo_*, __products tables
- **Write**: seo_monitor_results (internal)
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-003, ADR-009, ADR-008
- **Airlock Required**: no (internal service)
- **Audit Trail**: yes (via logs)

## Placement Decision

**MUST run on principal VPS** - Worker process requiring database access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
