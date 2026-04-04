---
agent_id: agent.seo.kp.lead
agent_name: SEO Keyword Planning Lead
status: planned
owner: SEO Team
governance_verdict: NOT_APPROVED
last_audit: 2026-04-04
zone: principal_vps
---

# Agent: SEO Keyword Planning Lead

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.kp.lead` |
| Name | SEO Keyword Planning Lead |
| Status | **planned** (Phase 0) |
| Owner | SEO Team |
| Description | Coordonne les agents de recherche de mots-clés, analyse SERP et enrichissement de briefs sous IA-SEO Master |

## Rattachement

| Field | Value |
|-------|-------|
| Reports to | `ia-seo-master` |
| Sponsor | `agent.seo.lead` |
| Squad | seo |
| Level | 2.5 (Sub-Lead) |

## Agents Managed

| Agent | Type | Status |
|-------|------|--------|
| prompt.keyword-planner | prompt | active |
| prompt.r4-keyword-planner | prompt | active |
| prompt.r6-keyword-planner | prompt | active |
| prompt.research-agent | prompt | active |
| prompt.brief-enricher | prompt | active |
| seo-keyword-expert | backend | active |
| serp-analyzer | backend | active |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | Claude API (quand activé) |
| Output | bundle_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | medium |
| Risk Factors | Keyword strategy decisions, search volume analysis, SERP targeting |

## Access Rights

- **Read**: monorepo (full), `__seo_*` tables, `seo_keywords` tables
- **Write**: `__seo_*` tables (via RPC only)
- **Secrets**: none

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-002, ADR-009, ADR-013
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** — AI-COS Level 2.5 Sub-Lead agent. Activation via processus G2 (ADR-013, vague 2a).

---

_Last audit: 2026-04-04_
_Auditor: Claude (Governance Analyst)_
