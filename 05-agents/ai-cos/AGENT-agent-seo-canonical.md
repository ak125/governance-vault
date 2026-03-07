---
agent_id: agent.seo.canonical
agent_name: Canonical Manager
status: planned
owner: SEO Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-07
execution_engine: Claude API
zone: principal_vps
---

# Agent: Canonical Manager

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.canonical` |
| Name | Canonical Manager |
| Status | **planned** (Phase 0) |
| Owner | SEO Team |
| Description | Manages canonical URLs and duplicate content |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | Claude API |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Canonical URL decisions |

## Access Rights

- **Read**: __seo_* tables
- **Write**: canonical_urls (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Data operations via RPC only
- **Related ADR**: ADR-003, ADR-009
- **Airlock Required**: no (data operations only)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - Claude API executor (ADR-011) with RPC-only access.

---

_Last updated: 2026-03-07_
_Auditor: Claude (Governance Analyst)_
