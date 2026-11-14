---
agent_id: agent.rag.lead
agent_name: RAG Lead
status: disabled
owner: AI Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: RAG Lead

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.rag.lead` |
| Name | RAG Lead |
| Status | **disabled** |
| Owner | AI Team |
| Description | Orchestrates RAG (Retrieval Augmented Generation) agents |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | Claude API (quand active) |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | medium |
| Risk Factors | Knowledge base access |

## Access Rights

- **Read**: knowledge corpus, embeddings
- **Write**: proposals only (via Airlock)
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Retired**: AI-COS agent system retired with the AI-COS machine (stopped in October 2026, exact day unknown) by [[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]]; card and verdict kept as history
- **Related ADR**: ADR-002, ADR-009, ADR-011
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS Level 2 Lead agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
