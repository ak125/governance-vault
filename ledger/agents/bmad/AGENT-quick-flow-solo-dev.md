---
agent_id: quick-flow-solo-dev
agent_name: Barry (Quick Flow Solo Dev)
status: disabled
owner: BMAD BMM Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: Barry (Quick Flow Solo Dev)

## Identity

| Field | Value |
|-------|-------|
| ID | `quick-flow-solo-dev` |
| Name | Barry (Quick Flow Solo Dev) |
| Status | **disabled** |
| Owner | BMAD BMM Team |
| Description | Fast-track development for small features |

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
| Risk Factors | Rapid prototyping guidance |

## Access Rights

- **Read**: monorepo (full), governance-vault (full)
- **Write**: none
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-002, ADR-009, ADR-008
- **Retired**: 2026-10-26, BMAD method withdrawn by [[ADR-118-retrait-methodes-bmad-superpowers-spec-kit|ADR-118]]; card kept as history
- **Airlock Required**: no
- **Audit Trail**: no

## Placement Decision

**MUST run on local_machine** - Development workflow, no server access needed.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
