---
agent_id: prompt.r1-content-batch
agent_name: Content Batch (R1)
status: active
owner: SEO Team
governance_verdict: APPROVED
last_audit: 2026-03-08
zone: local
execution_engine: Claude Code
---

# Agent: Content Batch (R1)

## Identity

| Field | Value |
|-------|-------|
| ID | `prompt.r1-content-batch` |
| Name | Content Batch (R1) |
| Status | active |
| Owner | SEO Team |
| Description | Generation batch de contenu SEO pour pages R1 (familles) |

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

- **Read**: __seo_r1_keyword_plan, famille pages
- **Write**: R1 content sections (via RPC)
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
