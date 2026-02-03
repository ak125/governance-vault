---
agent_id: agent.cfo.ia
agent_name: IA-CFO
status: planned
owner: AI-COS Architecture Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: IA-CFO

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.cfo.ia` |
| Name | IA-CFO |
| Status | **planned** (Phase 0) |
| Owner | AI-COS Architecture Team |
| Description | Chief Financial Officer - Cost optimization and budgeting |

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
| Risk Factors | Financial decisions, cost data access |

## Access Rights

- **Read**: cost metrics, infrastructure spending
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
