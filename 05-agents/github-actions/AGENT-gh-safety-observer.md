---
agent_id: gh-safety-observer
agent_name: Safety Observer Workflow
status: active
owner: DevOps Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: external
---

# Agent: Safety Observer Workflow

## Identity

| Field | Value |
|-------|-------|
| ID | `gh-safety-observer` |
| Name | Safety Observer Workflow |
| Status | active |
| Owner | DevOps Team |
| Description | GitHub Actions workflow for security observation |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (GitHub-hosted runner) |
| Runtime | GitHub Actions |
| Output | report_only |
| File | `.github/workflows/validator-dev-safety-observe.yml` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Security observation only |

## Access Rights

- **Read**: monorepo (full)
- **Write**: none (reports only)
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (CI/CD pipeline)
- **Audit Trail**: yes (GitHub Actions logs)

## Placement Decision

**Runs on GitHub** - External zone per ADR-008, sandboxed GitHub-hosted runners.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
