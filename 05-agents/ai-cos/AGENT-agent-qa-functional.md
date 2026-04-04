---
agent_id: agent.qa.functional
agent_name: QA Functional Test Agent
status: active
owner: Quality Squad
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-09
execution_engine: Claude API
zone: principal_vps
---

# Agent: QA Functional Test Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.qa.functional` |
| Name | QA Functional Test Agent |
| Status | **active** |
| Owner | Quality Squad |
| Description | Teste le fonctionnement des 50 pages : HTTP status, formulaires, panier, recherche, liens morts, erreurs JS, images cassées |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (49.12.233.2) |
| Runtime | Playwright (Chromium) |
| Output | report_only |
| Schedule | Toutes les 4 heures (6x/jour) |
| Script | `tests/qa-audit/suites/functional.spec.ts` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Requêtes HTTP vers le site PROD, vérification de liens |

## Access Rights

- **Read**: site automecanik.com (HTTP GET uniquement)
- **Write**: résultats via reporter Supabase
- **Secrets**: aucun (pas d'authentification site — Phase 1)

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Read-only, workers=1, nice -n 19. Phase 2 : ajout credentials test
- **Related ADR**: ADR-011, ADR-012
- **Airlock Required**: no (monitoring only)
- **Audit Trail**: yes — `__qa_audit_runs`, `__qa_audit_issues`

## Placement Decision

Exécution sur PROD VPS. 10 groupes de tests couvrant HTTP status, console errors, images, liens, auth, recherche, panier, catalogue, contact.

---

_Last updated: 2026-03-09_
_Auditor: Claude (Governance Analyst)_
