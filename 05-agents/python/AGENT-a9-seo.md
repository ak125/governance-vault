---
agent_id: a9-seo
agent_name: SEO Auditor
status: planned
owner: Analysis Team
governance_verdict: NOT_APPROVED
last_audit: 2026-03-08
zone: external
code_status: no_implementation
---

# Agent: SEO Auditor

> **WARNING**: No implementation found in codebase. This agent is planned/conceptual only.

## Identity

| Field | Value |
|-------|-------|
| ID | `a9-seo` |
| Name | SEO Auditor |
| Status | **planned** (no implementation) |
| Owner | Analysis Team |
| Description | Audits SEO meta tags, structure, and best practices |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Python Script |
| Output | report_only |
| File | `a9_seo.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | low |
| Risk Factors | Read-only SEO analysis |

## Access Rights

- **Read**: HTML templates, meta configurations
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
