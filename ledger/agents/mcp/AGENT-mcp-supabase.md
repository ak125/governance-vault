---
agent_id: mcp-supabase
agent_name: Supabase MCP Server
status: active
owner: Infrastructure Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: local
---

# Agent: Supabase MCP Server

## Identity

| Field | Value |
|-------|-------|
| ID | `mcp-supabase` |
| Name | Supabase MCP Server |
| Status | active |
| Owner | Infrastructure Team |
| Description | MCP server for Supabase database operations |

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
| Risk Class | medium |
| Risk Factors | Database access via MCP protocol |

## Access Rights

- **Read**: Supabase tables (via MCP)
- **Write**: Controlled via MCP permissions
- **Secrets**: SUPABASE_SERVICE_ROLE_KEY (via env)

## Governance

- **Verdict**: APPROVED
- **Related ADR**: ADR-003, ADR-009, ADR-008
- **Airlock Required**: no (MCP controlled)
- **Audit Trail**: yes (MCP logs)

## Placement Decision

**MUST run on local_machine** - Development tooling, MCP server for IDE integration.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
