---
agent_id: agent.rag.indexer
agent_name: RAG Indexer Agent
status: disabled
owner: AI Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-07
execution_engine: Claude API
zone: principal_vps
---

# Agent: RAG Indexer Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.rag.indexer` |
| Name | RAG Indexer Agent |
| Status | **disabled** |
| Owner | AI Team |
| Description | Indexes documents for RAG retrieval |

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
| Risk Factors | Document processing |

## Access Rights

- **Read**: document corpus
- **Write**: embeddings (via RPC)
- **Secrets**: none

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Retired**: AI-COS agent system retired with the AI-COS machine (stopped in October 2026, exact day unknown) by [[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]]; card and verdict kept as history
- **Conditions**: Indexing via RPC only
- **Related ADR**: ADR-003, ADR-009, ADR-011
- **Airlock Required**: no (data operations)
- **Audit Trail**: yes

## Placement Decision

**Phase 1 eligible** - Claude API executor (ADR-011) with RPC access.

---

_Last updated: 2026-03-07_
_Auditor: Claude (Governance Analyst)_
