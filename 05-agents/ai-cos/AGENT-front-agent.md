---
agent_id: front-agent
agent_name: Front Agent (Interface)
status: planned
owner: AI-COS Architecture Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Front Agent (Interface)

## Identity

| Field | Value |
|-------|-------|
| ID | `front-agent` |
| Name | Front Agent (Interface) |
| Status | **planned** (Phase 0) |
| Owner | AI-COS Architecture Team |
| Description | User interface agent for AI-COS interaction |

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
| Risk Factors | User interaction, command interpretation |

## Access Rights

- **Read**: user requests, AI-COS state
- **Write**: none (delegates to other agents)
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-002, ADR-009
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS interface agent with delegation authority.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
