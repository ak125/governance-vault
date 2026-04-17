---
agent_id: skill.content-audit
agent_name: Content Audit
status: active
owner: DevOps
governance_verdict: APPROVED
last_audit: 2026-03-08
zone: local
---

# Agent: Content Audit

## Identity

| Field | Value |
|-------|-------|
| ID | `skill.content-audit` |
| Name | Content Audit |
| Status | active |
| Owner | DevOps |
| Description | Audit contenu R2D2 universel — Intent-First, Evidence-First, Decision-First pour pages R1-R6 |

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
