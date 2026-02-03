---
agent_id: f15-risk-scorer
agent_name: Risk Scorer
status: active
owner: Analysis Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: external
---

# Agent: Risk Scorer

## Identity

| Field | Value |
|-------|-------|
| ID | `f15-risk-scorer` |
| Name | Risk Scorer |
| Status | active |
| Owner | Analysis Team |
| Description | Calculates risk scores for code changes and PRs |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python Script |
| Output | report_only |
| File | `f15_risk_scorer.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only risk analysis |

## Access Rights

- **Read**: git history, code changes
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
