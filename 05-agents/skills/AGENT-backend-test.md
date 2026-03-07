---
agent_id: skill.backend-test
agent_name: Backend Test
status: active
owner: DevOps
governance_verdict: APPROVED
last_audit: 2026-03-08
zone: local
---

# Agent: Backend Test

## Identity

| Field | Value |
|-------|-------|
| ID | `skill.backend-test` |
| Name | Backend Test |
| Status | active |
| Owner | DevOps |
| Description | Skill de test endpoints backend via curl — validation API responses |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (Claude Code skill) |
| Runtime | Claude Code Skill (.claude/skills/) |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Analysis and reporting only, no direct writes |

## Access Rights

- **Read**: Codebase, documentation, logs
- **Write**: none
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-007
- **Airlock Required**: no (report_only)
- **Audit Trail**: no

## Placement Decision

**MUST run on local_machine** - IDE skill integration, no server-side execution.

---

_Last audit: 2026-03-08_
_Auditor: Claude (Governance Analyst)_
