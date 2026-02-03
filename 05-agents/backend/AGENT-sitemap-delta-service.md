---
agent_id: sitemap-delta-service
agent_name: Sitemap Delta Service
status: active
owner: SEO Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Sitemap Delta Service

## Identity

| Field | Value |
|-------|-------|
| ID | `sitemap-delta-service` |
| Name | Sitemap Delta Service |
| Status | active |
| Owner | SEO Team |
| Description | Tracks sitemap changes and generates delta reports |

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
| Risk Factors | Sitemap analysis, no content modification |

## Access Rights

- **Read**: __sitemap_* tables, URL logs
- **Write**: sitemap_delta_logs (internal)
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-003, ADR-009, ADR-008
- **Airlock Required**: no (analysis service)
- **Audit Trail**: yes (via logs)

## Placement Decision

**MUST run on principal VPS** - Sitemap tracking with database access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
