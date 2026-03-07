---
agent_id: agent.cto.ia
agent_name: IA-CTO
status: planned
owner: AI-COS Architecture Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: IA-CTO

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.cto.ia` |
| Name | IA-CTO |
| Status | **planned** (Phase 0) |
| Owner | AI-COS Architecture Team |
| Description | Ensures technical quality, security, and managed technical debt |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | Claude API (quand active) |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | **HIGH** |
| Risk Factors | Security audit access, infrastructure decisions |

## Access Rights

- **Read**: monorepo (full), governance-vault (full), logs/metrics
- **Write**: proposals only (via Airlock)
- **Secrets**: limited (security scan tokens)

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-001, ADR-002, ADR-003, ADR-004, ADR-011
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS Level 1 Executive agent.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
