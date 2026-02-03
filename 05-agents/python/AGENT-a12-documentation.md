---
agent_id: a12-documentation
agent_name: Documentation Analyzer
status: active
owner: Analysis Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: external
---

# Agent: Documentation Analyzer

## Identity

| Field | Value |
|-------|-------|
| ID | `a12-documentation` |
| Name | Documentation Analyzer |
| Status | active |
| Owner | Analysis Team |
| Description | Analyzes documentation coverage and quality |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python Script |
| Output | report_only |
| File | `a12_documentation.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only documentation analysis |

## Access Rights

- **Read**: README, JSDoc, markdown files
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
