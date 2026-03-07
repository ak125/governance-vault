---
agent_id: prompt.keyword-planner
agent_name: Keyword Planner (R3)
status: active
owner: SEO Team
governance_verdict: APPROVED
last_audit: 2026-03-08
zone: local
execution_engine: Claude Code
---

# Agent: Keyword Planner (R3)

## Identity

| Field | Value |
|-------|-------|
| ID | `prompt.keyword-planner` |
| Name | Keyword Planner (R3) |
| Status | active |
| Owner | SEO Team |
| Description | Stage 1.5 du pipeline SEO v4 — audit-first keyword planning pour gammes R3 |

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

- **Read**: __seo_r3_keyword_plan, __seo_gamme_purchase_guide
- **Write**: __seo_r3_keyword_plan (via RPC)
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
