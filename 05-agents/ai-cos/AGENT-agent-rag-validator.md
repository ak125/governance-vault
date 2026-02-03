---
agent_id: agent.rag.validator
agent_name: RAG Validator Agent
status: planned
owner: AI Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
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
| Runtime | AI-COS Framework |
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

**Phase 1 eligible** - AI-COS Level 3 Executor with read access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
