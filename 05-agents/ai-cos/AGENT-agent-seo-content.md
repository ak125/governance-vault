---
agent_id: agent.seo.content
agent_name: SEO Content Agent
status: planned
owner: SEO Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SEO Content Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.content` |
| Name | SEO Content Agent |
| Status | **planned** (Phase 0) |
| Owner | SEO Team |
| Description | Generates and optimizes SEO content |

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
| Risk Factors | Content generation |

## Access Rights

- **Read**: __seo_* tables, templates
- **Write**: via Airlock bundle
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Content via Airlock bundle
- **Related ADR**: ADR-002, ADR-003, ADR-009
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - AI-COS Level 3 Executor with Airlock.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
