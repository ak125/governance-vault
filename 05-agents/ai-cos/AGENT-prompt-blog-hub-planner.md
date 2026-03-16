---
agent_id: prompt.blog-hub-planner
agent_name: Blog Hub Planner (R3 HUB)
status: active
owner: SEO Team
governance_verdict: APPROVED
last_audit: 2026-03-10
zone: local
execution_engine: Claude Code
---

# Agent: Blog Hub Planner (R3 HUB)

## Identity

| Field | Value |
|-------|-------|
| ID | `prompt.blog-hub-planner` |
| Name | Blog Hub Planner (R3 HUB) |
| Status | active |
| Owner | SEO Team |
| Description | Audite la page HUB /blog-pieces-auto : intent coverage, anti-cannibalisation, content gaps. Rapport MD + JSON inline. |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (Claude Code agent prompt) |
| Runtime | Claude Code (.claude/agents/) |
| Model | Sonnet |
| Output | inline (MD + JSON, pas de DB write) |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Read-only analysis, no DB writes, no LLM content generation |

## Access Rights

- **Read**: __blog_advice, __seo_gamme_purchase_guide, frontend source files
- **Write**: aucun (output inline uniquement)
- **Secrets**: aucun

## Scope

- **Cible** : 1 seule page — `/blog-pieces-auto` (HUB blog)
- **Pas de batch** : pas de pipeline multi-gammes
- **Upstream de** : keyword-planner, content-batch, conseil-batch, frontend-design
- **Trigger** : demande audit hub blog, structure blog homepage, SEO hub

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-011
- **Airlock Required**: no (read-only, output inline)
- **Audit Trail**: no (one-shot analysis, pas de pipeline)

## Placement Decision

**MUST run on local_machine** - Claude Code agent prompt, executed via IDE.

---

_Last audit: 2026-03-10_
_Auditor: Claude (Governance Analyst)_
