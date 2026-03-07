---
agent_id: agent.data.validator
agent_name: Data Validator Agent
status: planned
owner: Data Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-07
execution_engine: Claude API
zone: principal_vps
---

# Agent: Data Validator Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.data.validator` |
| Name | Data Validator Agent |
| Status | **planned** (Phase 0) |
| Owner | Data Team |
| Description | Validates data quality and integrity |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | Claude API |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Read-only data validation |

## Access Rights

- **Read**: all data tables
- **Write**: validation_logs (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Read-only access, logs via RPC
- **Related ADR**: ADR-003, ADR-009
- **Airlock Required**: no (read-only)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - Claude API executor (ADR-011) with read-only access.

---

_Last updated: 2026-03-07_
_Auditor: Claude (Governance Analyst)_
