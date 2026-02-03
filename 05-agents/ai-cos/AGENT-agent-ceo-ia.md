---
agent_id: agent.ceo.ia
agent_name: IA-CEO
status: planned
owner: AI-COS Architecture Team
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: IA-CEO

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.ceo.ia` |
| Name | IA-CEO |
| Status | **planned** (Phase 0) |
| Owner | AI-COS Architecture Team |
| Description | Coordinates all IA agents, proposes strategic decisions |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (when activated) |
| Runtime | AI-COS Framework |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | **HIGH** |
| Risk Factors | Cross-domain coordination, strategic influence |

## Access Rights

- **Read**: monorepo (full), governance-vault (full), logs/metrics
- **Write**: proposals only (via Airlock)
- **Secrets**: limited (observability tokens only)

## Governance

- **Verdict**: **NOT_APPROVED**
- **Related ADR**: ADR-002, ADR-003, ADR-009
- **Airlock Required**: yes
- **Audit Trail**: yes

## Placement Decision

**FORBIDDEN in Phase 1** - AI-COS Level 1 Executive agent. Requires separate ADR for activation per ADR-009.

## Activation Conditions

- AI-COS module fully deployed
- All Level 2 agents available
- Human CEO explicit approval
- New ADR authorizing Phase 2

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
_Status: BLOCKED - Phase 0 only_
