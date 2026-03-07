---
agent_id: prompt.research-agent
agent_name: Research Agent
status: active
owner: SEO Team
governance_verdict: APPROVED
last_audit: 2026-03-08
zone: local
execution_engine: Claude Code
---

# Agent: Research Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `prompt.research-agent` |
| Name | Research Agent |
| Status | active |
| Owner | SEO Team |
| Description | Research et brief enrichment pour contenu SEO — web search + corpus RAG |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (Claude Code agent prompt) |
| Runtime | Claude Code (.claude/agents/) |
| Model | Sonnet |
| Output | rpc_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | LLM content generation, DB writes via RPC only |

## Access Rights

- **Read**: RAG corpus, web search results
- **Write**: __seo_research_brief (via RPC)
- **Secrets**: GROQ_API_KEY (via env)

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-007, ADR-011
- **Airlock Required**: no (RPC-gated writes)
- **Audit Trail**: yes (pipeline logs)

## Placement Decision

**MUST run on local_machine** - Claude Code agent prompt, executed via IDE.

---

_Last audit: 2026-03-08_
_Auditor: Claude (Governance Analyst)_
