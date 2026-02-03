---
agent_id: f0-autoimport
agent_name: Auto Import Fixer
status: active
owner: Analysis Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
zone: external
---

# Agent: Auto Import Fixer

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
| Runtime | Python Script |
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

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: All changes via Airlock bundle
- **Related ADR**: ADR-002, ADR-009, ADR-007, ADR-008
- **Airlock Required**: **yes**
- **Audit Trail**: yes

## Placement Decision

**MUST run outside principal VPS** - Untrusted fixproof agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
