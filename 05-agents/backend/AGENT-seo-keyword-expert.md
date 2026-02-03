---
agent_id: seo-keyword-expert
agent_name: SEO Keyword Expert
status: active
owner: SEO Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SEO Keyword Expert

## Identity

| Field | Value |
|-------|-------|
| ID | `seo-keyword-expert` |
| Name | SEO Keyword Expert |
| Status | active |
| Owner | SEO Team |
| Description | JavaScript agent for keyword analysis and suggestions |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (per ADR-008) |
| Runtime | Node.js Script |
| Output | report_only |
| File | `backend/agents/seo-keyword-expert.js` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Keyword analysis, no content modification |

## Access Rights

- **Read**: __seo_keywords, search_queries
- **Write**: none
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (analysis only)
- **Audit Trail**: no (routine analysis)

## Placement Decision

**MUST run on principal VPS** - SEO analysis agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
