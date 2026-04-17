---
agent_id: agent.seo.qa.lead
agent_name: SEO QA & Monitoring Lead
status: planned
owner: SEO Team
governance_verdict: NOT_APPROVED
last_audit: 2026-04-04
zone: principal_vps
---

# Agent: SEO QA & Monitoring Lead

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.seo.qa.lead` |
| Name | SEO QA & Monitoring Lead |
| Status | **planned** (Phase 0) |
| Owner | SEO Team |
| Description | Coordonne les agents de monitoring SEO, audit scheduling et vérification qualité sous IA-SEO Master |

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
| seo-monitor-scheduler | backend | active |
| seo-monitor-processor | backend | active |
| seo-audit-scheduler | backend | active |
| seo-interpolation-monitor | backend | active |
| seo-monitoring-service | backend | active |
| agent.qa.seo-tech | ai-cos | active (dotted-line, domain=quality) |
| SEO Sentinel | business | APPROVED_WITH_CONDITIONS |

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
| Risk Factors | Monitoring accuracy, false positive/negative alerts, audit scheduling |

## Access Rights

- **Read**: monorepo (full), `__seo_*` tables, monitoring logs
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
