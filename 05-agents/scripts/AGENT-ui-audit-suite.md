---
agent_id: ui-audit-suite
agent_name: UI Audit Suite
status: active
owner: Design Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: UI Audit Suite

## Identity

| Field | Value |
|-------|-------|
| ID | `ui-audit-suite` |
| Name | UI Audit Suite |
| Status | active |
| Owner | Design Team |
| Description | Script suite for UI component auditing |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (per ADR-008) |
| Runtime | Node.js Scripts |
| Output | report_only |
| Directory | `scripts/ui-audit/` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | UI analysis only |

## Access Rights

- **Read**: frontend components
- **Write**: none (reports only)
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (analysis only)
- **Audit Trail**: no

## Placement Decision

**MUST run on local_machine** - Development tooling suite.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
