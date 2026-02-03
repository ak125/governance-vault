---
agent_id: a8-accessibility
agent_name: Accessibility Scanner
status: active
owner: Analysis Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: external
---

# Agent: Accessibility Scanner

## Identity

| Field | Value |
|-------|-------|
| ID | `a8-accessibility` |
| Name | Accessibility Scanner |
| Status | active |
| Owner | Analysis Team |
| Description | Scans for WCAG compliance and accessibility issues |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python Script |
| Output | report_only |
| File | `a8_accessibility.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only accessibility analysis |

## Access Rights

- **Read**: frontend components, HTML templates
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
