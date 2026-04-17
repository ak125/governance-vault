---
agent_id: mcp-supabase-local
agent_name: Supabase Local MCP Server
status: active
owner: Infrastructure Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: Supabase Local MCP Server

## Identity

| Field | Value |
|-------|-------|
| ID | `mcp-supabase-local` |
| Name | Supabase Local MCP Server |
| Status | active |
| Owner | Infrastructure Team |
| Description | Custom MCP server for local Supabase development |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | local (per ADR-008) |
| Runtime | MCP Protocol |
| Output | report_only |
| Directory | `scripts/mcp-server/` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | low |
| Risk Factors | Local development database access |

## Access Rights

- **Read**: Local Supabase instance
- **Write**: Controlled via MCP permissions
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY (local only)

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-003, ADR-009, ADR-008
- **Airlock Required**: no (local development)
- **Audit Trail**: no

## Placement Decision

**MUST run on local_machine** - Local development MCP server.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
