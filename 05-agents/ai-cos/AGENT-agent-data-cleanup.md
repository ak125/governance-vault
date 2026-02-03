---
agent_id: agent.data.cleanup
agent_name: Data Cleanup Agent
status: planned
owner: Data Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Data Cleanup Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.data.cleanup` |
| Name | Data Cleanup Agent |
| Status | **planned** (Phase 0) |
| Owner | Data Team |
| Description | Cleans up stale and orphan data |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | AI-COS Framework |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | medium |
| Risk Factors | Data deletion capability |

## Access Rights

- **Read**: data tables, cleanup configs
- **Write**: cleanup_logs (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Cleanup via RPC only, human approval for deletions
- **Related ADR**: ADR-003, ADR-009
- **Airlock Required**: yes (for deletions)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - AI-COS Level 3 Executor with controlled access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
