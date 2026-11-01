---
agent_id: dev
agent_name: Amelia (Developer Agent)
status: disabled
owner: BMAD BMM Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-10-27
execution_engine: Cowork / Claude Desktop
zone: local
---

# Agent: Amelia (Developer Agent)

## Identity

| Field | Value |
|-------|-------|
| ID | `dev` |
| Name | Amelia (Developer Agent) |
| Status | **disabled** |
| Owner | BMAD BMM Team |
| Description | Senior Software Engineer for code implementation |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (per ADR-008) |
| Runtime | Cowork / Claude Desktop |
| Output | **bundle_only** |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | medium |
| Risk Factors | Generates executable code, requires human review |

## Access Rights

- **Read**: monorepo (full), governance-vault (full)
- **Write**: agent-submissions (via bundle)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: All code changes via Airlock bundle
- **Related ADR**: ADR-002, ADR-005, ADR-009, ADR-008, ADR-011
- **Retired**: 2026-10-26, BMAD method withdrawn by [[ADR-118-retrait-methodes-bmad-superpowers-spec-kit|ADR-118]]; card kept as history
- **Airlock Required**: **yes**
- **Audit Trail**: yes

## Placement Decision

**MUST run on local_machine** with Airlock bundle submission for production changes.

---

_Last updated: 2026-10-27_
_Auditor: Claude (Governance Analyst)_
