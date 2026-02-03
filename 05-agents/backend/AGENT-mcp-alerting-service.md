---
agent_id: mcp-alerting-service
agent_name: MCP Alerting Service
status: active
owner: Infrastructure Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: MCP Alerting Service

## Identity

| Field | Value |
|-------|-------|
| ID | `mcp-alerting-service` |
| Name | MCP Alerting Service |
| Status | active |
| Owner | Infrastructure Team |
| Description | Sends alerts for MCP server events and anomalies |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (per ADR-008) |
| Runtime | NestJS Service |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Alerting only, no data modification |

## Access Rights

- **Read**: MCP logs, health metrics
- **Write**: none (alerts via external channels)
- **Secrets**: SLACK_WEBHOOK_URL (optional)

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (alerting service)
- **Audit Trail**: yes (via logs)

## Placement Decision

**MUST run on principal VPS** - Infrastructure alerting service.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
