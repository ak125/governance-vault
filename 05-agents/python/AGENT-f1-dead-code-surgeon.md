---
agent_id: f1-dead-code-surgeon
agent_name: Dead Code Surgeon
status: active
owner: Analysis Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-07
execution_engine: Claude API
zone: external
---

# Agent: Dead Code Surgeon

## Identity

| Field | Value |
|-------|-------|
| ID | `f1-dead-code-surgeon` |
| Name | Dead Code Surgeon |
| Status | active |
| Owner | Analysis Team |
| Description | Removes verified dead code with high confidence |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (per ADR-008) |
| Runtime | Claude API (Python Script) |
| Output | **bundle_only** |
| File | `f1_dead_code_surgeon.py` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | untrusted |
| Risk Class | medium |
| Risk Factors | Code deletion capability |

## Access Rights

- **Read**: monorepo (full)
- **Write**: via Airlock bundle only
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: All deletions via Airlock bundle, human review required
- **Related ADR**: ADR-002, ADR-009, ADR-007, ADR-008
- **Airlock Required**: **yes**
- **Audit Trail**: yes

## Placement Decision

**MUST run outside principal VPS** - Untrusted fixproof agent.

---

_Last updated: 2026-03-07_
_Auditor: Claude (Governance Analyst)_
