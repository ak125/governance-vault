---
agent_id: gh-perf-gates
agent_name: Performance Gates Workflow
status: active
owner: DevOps Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: external
---

# Agent: Performance Gates Workflow

## Identity

| Field | Value |
|-------|-------|
| ID | `gh-perf-gates` |
| Name | Performance Gates Workflow |
| Status | active |
| Owner | DevOps Team |
| Description | GitHub Actions workflow for performance validation |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (GitHub-hosted runner) |
| Runtime | GitHub Actions |
| Output | report_only |
| File | `.github/workflows/perf-gates.yml` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Performance testing only |

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
