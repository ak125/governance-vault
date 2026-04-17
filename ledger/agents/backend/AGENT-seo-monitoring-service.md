---
agent_id: seo-monitoring-service
agent_name: SEO Monitoring Service
status: active
owner: SEO Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SEO Monitoring Service

## Identity

| Field | Value |
|-------|-------|
| ID | `seo-monitoring-service` |
| Name | SEO Monitoring Service |
| Status | active |
| Owner | SEO Team |
| Description | Core service for SEO health monitoring and reporting |

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
| Risk Factors | SEO data access, monitoring operations |

## Access Rights

- **Read**: __seo_*, __sitemap_* tables
- **Write**: seo_monitoring_results (internal)
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-003, ADR-009, ADR-008
- **Airlock Required**: no (internal monitoring)
- **Audit Trail**: yes (via logs)

## Placement Decision

**MUST run on principal VPS** - Core SEO monitoring with database access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
