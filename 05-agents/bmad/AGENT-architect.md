---
agent_id: architect
agent_name: Winston (System Architect)
status: active
owner: BMAD BMM Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: Winston (System Architect)

## Identity

| Field | Value |
|-------|-------|
| ID | `architect` |
| Name | Winston (System Architect) |
| Status | active |
| Owner | BMAD BMM Team |
| Description | System Architect and Technical Design Leader |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (per ADR-008) |
| Runtime | BMAD Framework |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Architecture guidance only |

## Access Rights

- **Read**: monorepo (full), governance-vault (full)
- **Write**: none
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-002, ADR-009, ADR-008
- **Airlock Required**: no
- **Audit Trail**: no

## Placement Decision

**MUST run on local_machine** - Development workflow, no server access needed.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
