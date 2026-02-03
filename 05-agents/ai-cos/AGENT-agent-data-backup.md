---
agent_id: agent.data.backup
agent_name: Data Backup Agent
status: planned
owner: Data Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Data Backup Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.data.backup` |
| Name | Data Backup Agent |
| Status | **planned** (Phase 0) |
| Owner | Data Team |
| Description | Manages data backup and recovery |

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
| Risk Factors | Backup data access |

## Access Rights

- **Read**: backup configs, schedules
- **Write**: backup_logs (via RPC)
- **Secrets**: backup credentials (limited)

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Backup operations via RPC only
- **Related ADR**: ADR-003, ADR-009
- **Airlock Required**: no (backup operations)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - AI-COS Level 3 Executor with controlled access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
