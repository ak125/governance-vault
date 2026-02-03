---
agent_id: agent.qto
agent_name: QTO (Quality Technical Officer)
status: planned
owner: AI-COS Architecture Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: QTO

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.qto` |
| Name | QTO (Quality Technical Officer) |
| Status | **planned** (Phase 0) |
| Owner | AI-COS Architecture Team |
| Description | Quality assurance and testing strategy |

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
| Risk Factors | Quality gate decisions |

## Access Rights

- **Read**: test results, quality metrics
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
