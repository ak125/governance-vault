---
agent_id: mcp-shadcn
agent_name: shadcn/ui MCP Server
status: active
owner: Design Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: shadcn/ui MCP Server

## Identity

| Field | Value |
|-------|-------|
| ID | `mcp-shadcn` |
| Name | shadcn/ui MCP Server |
| Status | active |
| Owner | Design Team |
| Description | MCP server for shadcn/ui component registry access |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (per ADR-008) |
| Runtime | MCP Protocol |
| Output | report_only |
| Config | `.mcp.json` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | External registry access (read-only) |

## Access Rights

- **Read**: shadcn/ui registry (external)
- **Write**: none
- **Secrets**: none

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (read-only)
- **Audit Trail**: no

## Placement Decision

**MUST run on local_machine** - Development tooling, MCP server for IDE integration.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
