---
agent_id: serp-analyzer
agent_name: SERP Analyzer
status: active
owner: SEO Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SERP Analyzer

## Identity

| Field | Value |
|-------|-------|
| ID | `serp-analyzer` |
| Name | SERP Analyzer |
| Status | active |
| Owner | SEO Team |
| Description | Analyzes Search Engine Results Page data and rankings |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (per ADR-008) |
| Runtime | Node.js Script |
| Output | report_only |
| File | `backend/agents/sources/serp-analyzer.js` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | External API calls for SERP data |

## Access Rights

- **Read**: SERP APIs, ranking data
- **Write**: none
- **Secrets**: SERP_API_KEY (optional)

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (analysis only)
- **Audit Trail**: yes (API calls logged)

## Placement Decision

**MUST run on principal VPS** - SERP analysis agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
