---
agent_id: agent.qa.orchestrator
agent_name: QA Audit Orchestrator
status: active
owner: Quality Squad
governance_verdict: APPROVED_WITH_CONDITIONS
last_updated: 2026-03-09
execution_engine: Claude API
zone: principal_vps
---

# Agent: QA Audit Orchestrator

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.qa.orchestrator` |
| Name | QA Audit Orchestrator |
| Status | **active** |
| Owner | Quality Squad |
| Description | Orchestre les 3 suites QA (functional, visual, seo-tech), agrège les résultats et déclenche les alertes H24 |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (49.12.233.2) |
| Runtime | Bash + Playwright |
| Output | report_only |
| Schedule | Coordonne 12 cycles/jour |
| Script | `tests/qa-audit/qa-audit-cron.sh` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Lecture HTTP du site, écriture Supabase (tables QA uniquement) |

## Access Rights

- **Read**: site automecanik.com (HTTP), Supabase `__qa_audit_*`
- **Write**: Supabase `__qa_audit_runs`, `__qa_audit_issues`, `__qa_audit_alerts`, `__cron_runs`
- **Secrets**: `SUPABASE_SERVICE_ROLE_KEY`, `QA_ALERT_WEBHOOK_URL`

## Governance

- **Verdict**: **APPROVED_WITH_CONDITIONS**
- **Conditions**: Aucune écriture sur la DB PROD, uniquement tables `__qa_*`. Workers=1, nice -n 19
- **Related ADR**: ADR-011, ADR-012
- **Airlock Required**: no (monitoring only)
- **Audit Trail**: yes — `__qa_audit_runs`

## Placement Decision

Exécution sur PROD VPS pour accès direct Playwright/Chromium. Résultats lus par le dashboard AI-COS via Supabase (READ-ONLY).

---

_Last updated: 2026-03-09_
_Auditor: Claude (Governance Analyst)_
