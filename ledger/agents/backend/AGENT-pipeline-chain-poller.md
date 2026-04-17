---
agent_id: worker.pipeline-chain-poller
agent_name: Pipeline Chain Poller
status: active
owner: Backend Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-03-08
execution_engine: NestJS BullMQ
zone: principal_vps
---

# Agent: Pipeline Chain Poller

## Identity

| Field | Value |
|-------|-------|
| ID | `worker.pipeline-chain-poller` |
| Name | Pipeline Chain Poller |
| Status | active |
| Owner | Backend Team |
| Description | Poller service — auto-chain pipeline SEO stages via __pipeline_chain_queue |
| Source | `backend/src/modules/admin/services/pipeline-chain-poller.service.ts` |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps |
| Runtime | NestJS BullMQ Worker |
| Output | rpc_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | medium |
| Risk Factors | Auto-triggers downstream pipeline stages, DB writes |

## Access Rights

- **Read**: __pipeline_chain_queue, pipeline status
- **Write**: BullMQ job dispatch, __pipeline_chain_queue (via RPC)
- **Secrets**: DATABASE_URL, GROQ_API_KEY (via env)

## Governance

- **Verdict**: APPROVED_WITH_CONDITIONS
- **Conditions**: RPC-gated writes only, feature flag controlled
- **Related ADR**: ADR-003, ADR-009, ADR-011
- **Airlock Required**: no (automated worker, RPC-gated)
- **Audit Trail**: yes (BullMQ job logs)

## Placement Decision

**Runs on principal_vps** - Backend worker process, Docker container.

---

_Last audit: 2026-03-08_
_Auditor: Claude (Governance Analyst)_
