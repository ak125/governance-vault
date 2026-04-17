---
agent_id: agent.seo.exec.lead
agent_name: SEO Execution Lead
status: planned
owner: SEO Team
governance_verdict: NOT_APPROVED
last_audit: 2026-04-04
zone: principal_vps
---

# Agent: SEO Execution Lead

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.exec.lead` |
| Name | SEO Execution Lead |
| Status | **planned** (Phase 0) |
| Owner | SEO Team |
| Description | Coordonne l'exécution technique SEO : V-Level scoring, sitemaps, canonicals et orchestration pipeline sous IA-SEO Master |

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
| agent.seo.vlevel | ai-cos | planned |
| agent.seo.sitemap | ai-cos | planned |
| agent.seo.canonical | ai-cos | planned |
| sitemap-delta-service | backend | active |
| worker.pipeline-chain-poller | worker | active |
| a9_seo | python | planned |

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
| Risk Factors | Sitemap modifications, canonical URL decisions, pipeline execution, V-Level scoring |

## Access Rights

- **Read**: monorepo (full), `__seo_*` tables, sitemap data
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
