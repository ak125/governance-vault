---
agent_id: agent.rag.retriever
agent_name: RAG Retriever Agent
status: planned
owner: AI Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: RAG Retriever Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.rag.retriever` |
| Name | RAG Retriever Agent |
| Status | **planned** (Phase 0) |
| Owner | AI Team |
| Description | Retrieves relevant documents for RAG queries |

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
| Risk Factors | Document retrieval |

## Access Rights

- **Read**: embeddings, document corpus
- **Write**: retrieval_logs (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Retrieval via RPC only
- **Related ADR**: ADR-003, ADR-009
- **Airlock Required**: no (read operations)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - AI-COS Level 3 Executor with read access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
