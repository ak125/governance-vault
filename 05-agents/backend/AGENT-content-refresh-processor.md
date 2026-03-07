---
agent_id: worker.content-refresh
agent_name: Content Refresh Processor
status: active
owner: Backend Team
governance_verdict: APPROVED_WITH_CONDITIONS
last_audit: 2026-03-08
execution_engine: NestJS BullMQ
zone: principal_vps
---

# Agent: Content Refresh Processor

## Identity

| Field | Value |
|-------|-------|
| ID | `worker.content-refresh` |
| Name | Content Refresh Processor |
| Status | active |
| Owner | Backend Team |
| Description | BullMQ processor — refresh contenu SEO gammes via Groq LLM pipeline |
| Source | `backend/src/workers/processors/content-refresh.processor.ts` |

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
| Risk Factors | LLM calls via Groq, DB writes via RPC |

## Access Rights

- **Read**: __seo_gamme_purchase_guide, __seo_gamme_conseil, RAG corpus
- **Write**: __seo_gamme_purchase_guide, __seo_gamme_conseil (via RPC)
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
