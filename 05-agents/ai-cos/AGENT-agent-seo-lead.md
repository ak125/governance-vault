---
agent_id: agent.seo.lead
agent_name: SEO Lead
status: planned
owner: SEO Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SEO Lead

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.lead` |
| Name | SEO Lead |
| Status | **planned** (Phase 0) |
| Owner | SEO Team |
| Description | Orchestrates SEO execution agents |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | AI-COS Framework |
| Output | bundle_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | medium |
| Risk Factors | SEO content decisions, sitemap modifications |

## Access Rights

- **Read**: monorepo (full), __seo_* tables
- **Write**: __seo_* tables (via RPC only)
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-002, ADR-003, ADR-009
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS Level 2 Lead agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
