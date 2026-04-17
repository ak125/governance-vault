---
agent_id: agent.data.lead
agent_name: Data Lead
status: planned
owner: Data Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Data Lead

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.data.lead` |
| Name | Data Lead |
| Status | **planned** (Phase 0) |
| Owner | Data Team |
| Description | Orchestrates data management agents |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | Claude API (quand active) |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | medium |
| Risk Factors | Data access coordination |

## Access Rights

- **Read**: data schemas, ETL configs
- **Write**: proposals only (via Airlock)
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-002, ADR-009, ADR-011
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS Level 2 Lead agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
