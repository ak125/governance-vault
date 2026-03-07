---
agent_id: agent.rag.validator
agent_name: RAG Validator Agent
status: planned
owner: AI Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-07
execution_engine: Claude API
zone: principal_vps
---

# Agent: RAG Validator Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.rag.validator` |
| Name | RAG Validator Agent |
| Status | **planned** (Phase 0) |
| Owner | AI Team |
| Description | Validates RAG responses for accuracy |

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
| Risk Factors | Response validation |

## Access Rights

- **Read**: RAG responses, knowledge base
- **Write**: validation_logs (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Validation via RPC only
- **Related ADR**: ADR-003, ADR-009
- **Airlock Required**: no (read-only validation)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - Claude API executor (ADR-011) with read access.

---

_Last updated: 2026-03-07_
_Auditor: Claude (Governance Analyst)_
