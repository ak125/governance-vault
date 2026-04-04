---
agent_id: agent.qa.seo-tech
agent_name: QA SEO & Technical Test Agent
status: active
owner: Quality Squad
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-09
execution_engine: Claude API
zone: principal_vps
---

# Agent: QA SEO & Technical Test Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.qa.seo-tech` |
| Name | QA SEO & Technical Test Agent |
| Status | **active** |
| Owner | Quality Squad |
| Description | Vérifie les balises SEO (title, meta, canonical, H1, robots), les données structurées (Schema.org), le HTTPS, le TTFB, les headers de sécurité, et robots.txt/sitemap.xml |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (49.12.233.2) |
| Runtime | Playwright (Chromium) |
| Output | report_only |
| Schedule | Toutes les 12 heures (2x/jour) |
| Script | `tests/qa-audit/suites/seo-tech.spec.ts` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Requêtes HTTP, lecture headers |

## Access Rights

- **Read**: site automecanik.com (HTTP), headers HTTP, robots.txt, sitemap.xml
- **Write**: résultats via reporter Supabase
- **Secrets**: aucun

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Read-only
- **Related ADR**: ADR-011, ADR-012
- **Airlock Required**: no (monitoring only)
- **Audit Trail**: yes — `__qa_audit_runs`, `__qa_audit_issues`

## Placement Decision

Exécution sur PROD VPS. 8 groupes de tests : meta SEO, TTFB, HTTPS/mixed content, Schema.org, X-Robots-Tag, Open Graph, robots.txt/sitemap, headers sécurité.

---

_Last updated: 2026-03-09_
_Auditor: Claude (Governance Analyst)_
