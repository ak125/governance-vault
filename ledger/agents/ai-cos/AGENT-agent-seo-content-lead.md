---
agent_id: agent.seo.content.lead
agent_name: SEO Content Lead
status: planned
owner: SEO Team
governance_verdict: NOT_APPROVED
last_audit: 2026-04-04
zone: principal_vps
---

# Agent: SEO Content Lead

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.content.lead` |
| Name | SEO Content Lead |
| Status | **planned** (Phase 0) |
| Owner | SEO Team |
| Description | Coordonne les agents de génération de contenu, image prompts, content refresh et vidéo sous IA-SEO Master |

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
| agent.seo.content | ai-cos | planned |
| prompt.content-batch | prompt | active |
| prompt.r1-content-batch | prompt | active |
| prompt.r4-content-batch | prompt | active |
| prompt.r6-content-batch | prompt | active |
| prompt.conseil-batch | prompt | active |
| prompt.r3-image-prompt | prompt | active |
| prompt.r6-image-prompt | prompt | active |
| seo-content-architect | skill | active (coordinated) |
| worker.content-refresh | worker | active |
| worker.video-execution | worker | active |

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
| Risk Factors | Content generation decisions, multi-role content strategy, image/video pipeline |

## Access Rights

- **Read**: monorepo (full), `__seo_*` tables, `seo_contents` tables
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
