---
agent_id: agent.qa.orchestrator
agent_name: QA Audit Orchestrator
status: active
owner: QA Team
governance_verdict: APPROVED
last_updated: 2026-03-10
execution_engine: Bash (cron)
zone: dev_vps
---

# Agent: QA Audit Orchestrator

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.qa.orchestrator` |
| Name | QA Audit Orchestrator |
| Status | **active** |
| Owner | QA Team |
| Description | Coordinates H24 QA audit scheduling, dispatches suite runs, aggregates results, sends alerts on critical issues |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | dev_vps (46.224.118.55) |
| Runtime | Bash + Node.js (Playwright) |
| Output | report_only (writes to Supabase) |
| Schedule | Cron: functional/4h, visual/6h, seo-tech/12h |
| Script | `scripts/cron/qa-audit-cron.sh` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Read-only against production, writes to __qa_audit_* tables only |

## Access Rights

| Resource | Permission | Notes |
|----------|-----------|-------|
| Production URL | READ | HTTP requests via Playwright |
| Supabase __qa_audit_runs | WRITE | Via service_role key |
| Supabase __qa_audit_issues | WRITE | Via service_role key |
| Supabase __qa_audit_alerts | WRITE | Via service_role key |
| Supabase __cron_runs | WRITE | Via lib-supabase-report.sh |
| Webhook URL | WRITE | Alert notifications |

## Capabilities

- Dispatch 3 Playwright test suites (functional, visual, seo-tech)
- Report execution results to Supabase
- Send webhook alerts on critical failures
- Manage execution logs in /tmp/qa-audit-*.log

## Constraints

- No write access to production application
- No database mutations beyond __qa_audit_* and __cron_runs
- Sequential execution (workers=1) to avoid overloading production
- Maximum 150 page navigations per full audit cycle
