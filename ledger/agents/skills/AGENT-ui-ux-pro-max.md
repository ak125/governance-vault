---
agent_id: ui-ux-pro-max
agent_name: UI/UX Design Intelligence
status: active
owner: Design Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: UI/UX Design Intelligence

## Identity

| Field | Value |
|-------|-------|
| ID | `ui-ux-pro-max` |
| Name | UI/UX Design Intelligence |
| Status | active |
| Owner | Design Team |
| Description | 67 styles, 96 palettes, 57 font pairings, design system intelligence |

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

- **Read**: monorepo (design files), shadcn/ui registry
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
