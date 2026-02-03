---
agent_id: a10-i18n
agent_name: i18n Checker
status: active
owner: Analysis Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: external
---

# Agent: i18n Checker

## Identity

| Field | Value |
|-------|-------|
| ID | `a10-i18n` |
| Name | i18n Checker |
| Status | active |
| Owner | Analysis Team |
| Description | Checks internationalization compliance and missing translations |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python Script |
| Output | report_only |
| File | `a10_i18n.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only i18n analysis |

## Access Rights

- **Read**: translation files, source code
- **Write**: none
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-007, ADR-008
- **Airlock Required**: no (read-only analysis)
- **Audit Trail**: no

## Placement Decision

**MUST run outside principal VPS** - Untrusted analysis agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
