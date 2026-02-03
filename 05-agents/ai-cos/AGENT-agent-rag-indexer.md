---
agent_id: agent.rag.indexer
agent_name: RAG Indexer Agent
status: planned
owner: AI Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: RAG Indexer Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.rag.indexer` |
| Name | RAG Indexer Agent |
| Status | **planned** (Phase 0) |
| Owner | AI Team |
| Description | Indexes documents for RAG retrieval |

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
| Risk Factors | Document processing |

## Access Rights

- **Read**: document corpus
- **Write**: embeddings (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Indexing via RPC only
- **Related ADR**: ADR-003, ADR-009
- **Airlock Required**: no (data operations)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - AI-COS Level 3 Executor with RPC access.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
