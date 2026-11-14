---
agent_id: agent.data.validator
agent_name: Data Validator Agent
status: disabled
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
| Status | **disabled** |
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
- **Retired**: AI-COS agent system retired with the AI-COS machine (stopped in October 2026, exact day unknown) by [[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]]; card and verdict kept as history
- **Conditions**: Read-only access, logs via RPC
- **Related ADR**: ADR-003, ADR-009, ADR-011
- **Airlock Required**: no (read-only)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - Claude API executor (ADR-011) with read-only access.

---

_Last updated: 2026-03-07_
_Auditor: Claude (Governance Analyst)_
