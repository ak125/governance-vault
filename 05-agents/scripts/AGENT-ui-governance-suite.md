---
agent_id: ui-governance-suite
agent_name: UI Governance Suite
status: active
owner: Design Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: UI Governance Suite

## Identity

| Field | Value |
|-------|-------|
| ID | `ui-governance-suite` |
| Name | UI Governance Suite |
| Status | active |
| Owner | Design Team |
| Description | Script suite for UI governance rules enforcement |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (per ADR-008) |
| Runtime | Node.js Scripts |
| Output | report_only |
| Directory | `scripts/ui-governance/` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Governance validation only |

## Access Rights

- **Read**: frontend components, design tokens
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
