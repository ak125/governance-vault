---
agent_id: agent.data.cleanup
agent_name: Data Cleanup Agent
status: disabled
owner: Data Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-07
execution_engine: Claude API
zone: principal_vps
---

# Agent: Data Cleanup Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.data.cleanup` |
| Name | Data Cleanup Agent |
| Status | **disabled** |
| Owner | Data Team |
| Description | Cleans up stale and orphan data |

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
| Risk Class | medium |
| Risk Factors | Data deletion capability |

## Access Rights

- **Read**: data tables, cleanup configs
- **Write**: cleanup_logs (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Retired**: AI-COS agent system retired with the AI-COS machine (stopped in October 2026, exact day unknown) by [[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]]; card and verdict kept as history
- **Conditions**: Cleanup via RPC only, human approval for deletions
- **Related ADR**: ADR-003, ADR-009, ADR-011
- **Airlock Required**: yes (for deletions)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - Claude API executor (ADR-011) with controlled access.

---

_Last updated: 2026-03-07_
_Auditor: Claude (Governance Analyst)_
