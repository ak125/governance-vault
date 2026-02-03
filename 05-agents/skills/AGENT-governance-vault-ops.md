---
agent_id: governance-vault-ops
agent_name: Governance Vault Operations
status: active
owner: Governance Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: Governance Vault Operations

## Identity

| Field | Value |
|-------|-------|
| ID | `governance-vault-ops` |
| Name | Governance Vault Operations |
| Status | active |
| Owner | Governance Team |
| Description | Vault structure and ADR management skill |

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
| Risk Factors | Documentation guidance only |

## Access Rights

- **Read**: governance-vault (full), ADR templates
- **Write**: none (proposals via conversation)
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
