---
agent_id: f0-autoimport
agent_name: Auto Import Fixer
status: planned
owner: Analysis Team
governance_verdict: NOT_APPROVED
last_updated: 2026-03-08
execution_engine: Claude API
zone: external
code_status: no_implementation
---

# Agent: Auto Import Fixer

> **WARNING**: No implementation found in codebase. This agent is planned/conceptual only.

## Identity

| Field | Value |
|-------|-------|
| ID | `f0-autoimport` |
| Name | Auto Import Fixer |
| Status | active |
| Owner | Analysis Team |
| Description | Automatically fixes missing and unused imports |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Claude API (Python Script) |
| Output | **bundle_only** |
| File | `f0_autoimport.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | medium |
| Risk Factors | Code modification capability |

## Access Rights

- **Read**: monorepo (full)
- **Write**: via Airlock bundle only
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Conditions**: All changes via Airlock bundle
- **Related ADR**: ADR-002, ADR-009, ADR-007, ADR-008, ADR-011
- **Airlock Required**: **yes**
- **Audit Trail**: yes

## Placement Decision

**MUST run outside principal VPS** - Untrusted fixproof agent.

---

_Last audit: 2026-03-08_
_Auditor: Claude (Governance Analyst)_
