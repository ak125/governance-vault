---
agent_id: a3-duplications
agent_name: Duplication Detector
status: active
owner: Analysis Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: external
---

# Agent: Duplication Detector

## Identity

| Field | Value |
|-------|-------|
| ID | `a3-duplications` |
| Name | Duplication Detector |
| Status | active |
| Owner | Analysis Team |
| Description | Detects code duplications and DRY violations |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python Script |
| Output | report_only |
| File | `a3_duplications.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only code analysis |

## Access Rights

- **Read**: monorepo (full)
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
