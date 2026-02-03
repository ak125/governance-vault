---
agent_id: agent.seo.vlevel
agent_name: V-Level Generator
status: planned
owner: SEO Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: V-Level Generator

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.vlevel` |
| Name | V-Level Generator |
| Status | **planned** (Phase 0) |
| Owner | SEO Team |
| Description | Calculates V-Level scores (V1-V5) for SEO pages |

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
| Risk Factors | SEO score calculations |

## Access Rights

- **Read**: __seo_*, __sitemap_* tables
- **Write**: __seo_vlevel_scores (via RPC)
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
