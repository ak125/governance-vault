---
agent_id: a11-tests
agent_name: Test Coverage Analyzer
status: planned
owner: Analysis Team
governance_verdict: NOT_APPROVED
last_audit: 2026-03-08
zone: external
code_status: no_implementation
---

# Agent: Test Coverage Analyzer

> **WARNING**: No implementation found in codebase. This agent is planned/conceptual only.

## Identity

| Field | Value |
|-------|-------|
| ID | `a11-tests` |
| Name | Test Coverage Analyzer |
| Status | active |
| Owner | Analysis Team |
| Description | Analyzes test coverage and identifies untested code |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python Script |
| Output | report_only |
| File | `a11_tests.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only coverage analysis |

## Access Rights

- **Read**: test files, coverage reports
- **Write**: none
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-009, ADR-007, ADR-008
- **Airlock Required**: no (read-only analysis)
- **Audit Trail**: no

## Placement Decision

**MUST run outside principal VPS** - Untrusted analysis agent.

---

_Last audit: 2026-03-08_
_Auditor: Claude (Governance Analyst)_
