---
agent_id: agent.seo.sitemap
agent_name: Sitemap Generator
status: planned
owner: SEO Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Sitemap Generator

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.sitemap` |
| Name | Sitemap Generator |
| Status | **planned** (Phase 0) |
| Owner | SEO Team |
| Description | Generates and validates sitemaps |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | AI-COS Framework |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Sitemap generation |

## Access Rights

- **Read**: __sitemap_* tables, URL data
- **Write**: __sitemap_* (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Data operations via RPC only
- **Related ADR**: ADR-003, ADR-009
- **Airlock Required**: no (data operations only)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - AI-COS Level 3 Executor with RPC-only access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
