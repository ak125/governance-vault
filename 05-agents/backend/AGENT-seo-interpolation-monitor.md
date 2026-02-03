---
agent_id: seo-interpolation-monitor
agent_name: SEO Interpolation Monitor
status: active
owner: Backend Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SEO Interpolation Monitor

## Identity

| Field | Value |
|-------|-------|
| ID | `seo-interpolation-monitor` |
| Name | SEO Interpolation Monitor |
| Status | active |
| Owner | Backend Team |
| Description | Monitors SEO template interpolation quality and detects issues |

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
| Risk Factors | Read-only monitoring, alerting |

## Access Rights

- **Read**: __seo_* tables, template configurations
- **Write**: alerts, interpolation_logs (internal)
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-003, ADR-009, ADR-008
- **Airlock Required**: no (internal monitoring)
- **Audit Trail**: yes (via logs)

## Placement Decision

**MUST run on principal VPS** - Monitoring service with database access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
