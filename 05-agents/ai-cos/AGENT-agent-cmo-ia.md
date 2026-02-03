---
agent_id: agent.cmo.ia
agent_name: IA-CMO
status: planned
owner: AI-COS Architecture Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: IA-CMO

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.cmo.ia` |
| Name | IA-CMO |
| Status | **planned** (Phase 0) |
| Owner | AI-COS Architecture Team |
| Description | Chief Marketing Officer - Marketing strategy and SEO |

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
| Risk Class | **HIGH** |
| Risk Factors | Marketing decisions, SEO strategy |

## Access Rights

- **Read**: monorepo (full), SEO data, analytics
- **Write**: proposals only (via Airlock)
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-002, ADR-009
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS Level 1 Executive agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
