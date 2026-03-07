---
agent_id: a1_security
agent_name: Security Scanner
status: planned
owner: Analysis Team
governance_verdict: NOT_APPROVED
last_audit: 2026-03-08
zone: external
code_status: no_implementation
---

# Agent: Security Scanner (a1_security)

> **WARNING**: No implementation found in codebase. This agent is planned/conceptual only.

## Identity

| Field | Value |
|-------|-------|
| ID | `a1_security` |
| Name | Security Scanner |
| Status | active |
| Owner | Analysis Team |
| Description | Scans codebase for security vulnerabilities |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python 3.x |
| Output | report_only |
| File | `a1_security.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only analysis, sandboxed execution |

## Access Rights

- **Read**: monorepo (full)
- **Write**: none
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-002, ADR-009, ADR-007, ADR-008
- **Airlock Required**: no (report_only)
- **Audit Trail**: no

## Placement Decision

**MUST run in External zone** - Analysis agent with no write access, must be sandboxed outside principal VPS per ADR-008.

---

_Last audit: 2026-03-08_
_Auditor: Claude (Governance Analyst)_
