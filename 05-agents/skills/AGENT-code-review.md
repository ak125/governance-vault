---
agent_id: skill.code-review
agent_name: Code Review
status: active
owner: DevOps
governance_verdict: APPROVED
last_audit: 2026-03-08
zone: local
---

# Agent: Code Review

## Identity

| Field | Value |
|-------|-------|
| ID | `skill.code-review` |
| Name | Code Review |
| Status | active |
| Owner | DevOps |
| Description | Systematic PR/code review — security, architecture, performance, business compliance |

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
