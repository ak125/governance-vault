---
agent_id: a7-performance
agent_name: Performance Analyzer
status: active
owner: Analysis Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: external
---

# Agent: Performance Analyzer

## Identity

| Field | Value |
|-------|-------|
| ID | `a7-performance` |
| Name | Performance Analyzer |
| Status | active |
| Owner | Analysis Team |
| Description | Detects performance anti-patterns and bottlenecks |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python Script |
| Output | report_only |
| File | `a7_performance.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only performance analysis |

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
