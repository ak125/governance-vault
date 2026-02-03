---
agent_id: frontend-design
agent_name: Frontend Design Excellence
status: active
owner: Design Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: Frontend Design Excellence

## Identity

| Field | Value |
|-------|-------|
| ID | `frontend-design` |
| Name | Frontend Design Excellence |
| Status | active |
| Owner | Design Team |
| Description | High-quality frontend interface design skill |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (per ADR-008) |
| Runtime | Claude Code Skill |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Design guidance and code generation only |

## Access Rights

- **Read**: design system, component library
- **Write**: none (code via conversation)
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-007, ADR-008
- **Airlock Required**: no (report_only)
- **Audit Trail**: no

## Placement Decision

**MUST run on local_machine** - IDE skill integration, no server-side execution.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
