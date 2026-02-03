---
agent_id: bmad-master
agent_name: BMad Master
status: active
owner: BMAD Core Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: BMad Master

## Identity

| Field | Value |
|-------|-------|
| ID | `bmad-master` |
| Name | BMad Master |
| Status | active |
| Owner | BMAD Core Team |
| Description | Master Task Executor, Knowledge Custodian, and Workflow Orchestrator |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (per ADR-008) |
| Runtime | Claude Code CLI |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | No direct production access, read-only on monorepo |

## Access Rights

- **Read**: monorepo (full), governance-vault (read-only)
- **Write**: none (bundle_only via Airlock if needed)
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-002, ADR-009, ADR-007, ADR-008
- **Airlock Required**: no (local workflow only)
- **Audit Trail**: no

## Placement Decision

**MUST run on local_machine** - Development workflow orchestrator, no server-side execution required.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
