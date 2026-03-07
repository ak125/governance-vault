---
agent_id: agent.aicos.governance
agent_name: AI-COS Governance Agent
status: planned
owner: AI-COS Architecture Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: AI-COS Governance Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.aicos.governance` |
| Name | AI-COS Governance Agent |
| Status | **planned** (Phase 0) |
| Owner | AI-COS Architecture Team |
| Description | Enforces AI-COS governance rules |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | Claude API (quand active) |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | **HIGH** |
| Risk Factors | Governance enforcement authority |

## Access Rights

- **Read**: AI-COS rules, agent registry
- **Write**: proposals only (via Airlock)
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-002, ADR-009, ADR-011
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS meta-agent with governance authority.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
