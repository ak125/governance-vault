---
agent_id: agent.rag.retriever
agent_name: RAG Retriever Agent
status: disabled
owner: AI Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-07
execution_engine: Claude API
zone: principal_vps
---

# Agent: RAG Retriever Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.rag.retriever` |
| Name | RAG Retriever Agent |
| Status | **disabled** |
| Owner | AI Team |
| Description | Retrieves relevant documents for RAG queries |

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
| Risk Factors | Document retrieval |

## Access Rights

- **Read**: embeddings, document corpus
- **Write**: retrieval_logs (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Retired**: AI-COS agent system retired with the AI-COS machine (stopped in October 2026, exact day unknown) by [[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]]; card and verdict kept as history
- **Conditions**: Retrieval via RPC only
- **Related ADR**: ADR-003, ADR-009, ADR-011
- **Airlock Required**: no (read operations)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - Claude API executor (ADR-011) with read access.

---

_Last updated: 2026-03-07_
_Auditor: Claude (Governance Analyst)_
