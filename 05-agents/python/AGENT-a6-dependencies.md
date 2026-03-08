---
agent_id: a6-dependencies
agent_name: Dependencies Analyzer
status: planned
owner: Analysis Team
governance_verdict: NOT_APPROVED
last_audit: 2026-03-08
zone: external
code_status: no_implementation
---

# Agent: Dependencies Analyzer

> **WARNING**: No implementation found in codebase. This agent is planned/conceptual only.

## Identity

| Field | Value |
|-------|-------|
| ID | `a6-dependencies` |
| Name | Dependencies Analyzer |
| Status | **planned** (no implementation) |
| Owner | Analysis Team |
| Description | Analyzes npm dependencies, detects vulnerabilities and outdated packages |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python Script |
| Output | report_only |
| File | `a6_dependencies.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only dependency analysis |

## Access Rights

- **Read**: package.json, package-lock.json
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
