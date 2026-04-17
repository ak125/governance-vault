---
agent_id: worker.video-execution
agent_name: Video Execution Processor
status: active
owner: Backend Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-03-08
execution_engine: NestJS BullMQ
zone: principal_vps
---

# Agent: Video Execution Processor

## Identity

| Field | Value |
|-------|-------|
| ID | `worker.video-execution` |
| Name | Video Execution Processor |
| Status | active |
| Owner | Backend Team |
| Description | BullMQ processor — execution pipeline video (RAG video management) |
| Source | `backend/src/workers/processors/video-execution.processor.ts` |

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
| Risk Factors | External API calls, media processing |

## Access Rights

- **Read**: Video queue jobs, RAG video metadata
- **Write**: Video processing results (via RPC)
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
