---
agent_id: agent.qa.visual
agent_name: QA Visual & Responsive Test Agent
status: active
owner: Quality Squad
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-09
execution_engine: Claude API
zone: principal_vps
---

# Agent: QA Visual & Responsive Test Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.qa.visual` |
| Name | QA Visual & Responsive Test Agent |
| Status | **active** |
| Owner | Quality Squad |
| Description | Teste le responsive (3 viewports), l'accessibilité (axe-core), les touch targets, la cohérence design (CTA orange) et les états d'erreur |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (49.12.233.2) |
| Runtime | Playwright (Chromium, 3 viewports) |
| Output | report_only |
| Schedule | Toutes les 6 heures (4x/jour) |
| Script | `tests/qa-audit/suites/visual.spec.ts` |
| Viewports | 320x568 (mobile-small), 375x812 (mobile), 1440x900 (desktop) |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Requêtes HTTP, captures d'écran en cas d'échec |

## Access Rights

- **Read**: site automecanik.com (HTTP)
- **Write**: résultats via reporter Supabase
- **Secrets**: aucun

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Read-only. Dépendance optionnelle @axe-core/playwright pour a11y
- **Related ADR**: ADR-011, ADR-012
- **Airlock Required**: no (monitoring only)
- **Audit Trail**: yes — `__qa_audit_runs`, `__qa_audit_issues`

## Placement Decision

Exécution sur PROD VPS. 7 groupes de tests : header/footer, overflow horizontal, touch targets, font-size inputs, états d'erreur, a11y axe-core, CTA orange.

---

_Last updated: 2026-03-09_
_Auditor: Claude (Governance Analyst)_
