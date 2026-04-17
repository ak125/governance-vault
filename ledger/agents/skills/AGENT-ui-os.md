---
agent_id: ui-os
agent_name: UI Operating System
status: active
owner: Design Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: UI Operating System

## Identity

| Field | Value |
|-------|-------|
| ID | `ui-os` |
| Name | UI Operating System |
| Status | active |
| Owner | Design Team |
| Description | Core UI framework skill for component architecture |

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
| Risk Factors | Design guidance only, no code execution |

## Access Rights

- **Read**: monorepo (design files), component library
- **Write**: none
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
