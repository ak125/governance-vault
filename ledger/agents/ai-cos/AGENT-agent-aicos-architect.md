---
agent_id: agent.aicos.architect
agent_name: AI-COS Architect
status: planned
owner: AI-COS Architecture Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: AI-COS Architect

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.aicos.architect` |
| Name | AI-COS Architect |
| Status | **planned** (Phase 0) |
| Owner | AI-COS Architecture Team |
| Description | Designs AI-COS contracts and architecture |

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
| Risk Factors | Architecture decisions, contract definitions |

## Access Rights

- **Read**: AI-COS specs, contracts
- **Write**: proposals only (via Airlock)
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-002, ADR-009, ADR-011
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS meta-agent with architectural authority.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
