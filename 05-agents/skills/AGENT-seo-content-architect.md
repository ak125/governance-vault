---
agent_id: seo-content-architect
agent_name: SEO Content Architect
status: active
owner: SEO Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: SEO Content Architect

## Identity

| Field | Value |
|-------|-------|
| ID | `seo-content-architect` |
| Name | SEO Content Architect |
| Status | active |
| Owner | SEO Team |
| Description | SEO content strategy and V-Level optimization skill |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (per ADR-008) |
| Runtime | Claude Code Skill |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Content guidance only, anti-hallucination rules |

## Access Rights

- **Read**: SEO documentation, content templates
- **Write**: none
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-007, ADR-008
- **Airlock Required**: no (report_only)
- **Audit Trail**: no

## Placement Decision

**MUST run on local_machine** - IDE skill integration, no server-side execution.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
