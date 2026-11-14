---
agent_id: agent.seo.lead
agent_name: SEO Lead
status: disabled
owner: SEO Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: SEO Lead

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.lead` |
| Name | SEO Lead |
| Status | **disabled** |
| Owner | SEO Team |
| Description | Orchestrates SEO execution agents |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | Claude API (quand active) |
| Output | bundle_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | medium |
| Risk Factors | SEO content decisions, sitemap modifications |

## Access Rights

- **Read**: monorepo (full), __seo_* tables
- **Write**: __seo_* tables (via RPC only)
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Retired**: AI-COS agent system retired with the AI-COS machine (stopped in October 2026, exact day unknown) by [[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]]; card and verdict kept as history
- **Related ADR**: ADR-002, ADR-003, ADR-009, ADR-011
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS Level 2 Lead agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
