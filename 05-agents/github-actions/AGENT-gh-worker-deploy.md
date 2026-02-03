---
agent_id: gh-worker-deploy
agent_name: Worker Deploy Workflow
status: active
owner: DevOps Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: external
---

# Agent: Worker Deploy Workflow

## Identity

| Field | Value |
|-------|-------|
| ID | `gh-worker-deploy` |
| Name | Worker Deploy Workflow |
| Status | active |
| Owner | DevOps Team |
| Description | GitHub Actions workflow for worker deployment |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | external (GitHub-hosted runner) |
| Runtime | GitHub Actions |
| Output | report_only |
| File | `.github/workflows/worker-deploy.yml` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | medium |
| Risk Factors | Worker deployment access |

## Access Rights

- **Read**: monorepo (full)
- **Write**: Worker deployment target
- **Secrets**: DOCKERHUB_TOKEN, worker secrets

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-001, ADR-009, ADR-008
- **Airlock Required**: no (CI/CD pipeline)
- **Audit Trail**: yes (GitHub Actions logs)

## Placement Decision

**Runs on GitHub** - External zone per ADR-008, sandboxed GitHub-hosted runners.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
