---
agent_id: email-processor
agent_name: Email Processor
status: disabled
owner: Backend Team
governance_verdict: APPROVED
last_audit: 2026-02-04
zone: principal_vps
---

# Agent: Email Processor

## Identity

| Field | Value |
|-------|-------|
| ID | `email-processor` |
| Name | Email Processor |
| Status | **disabled** |
| Owner | Backend Team |
| Description | Processes email queue and sends transactional emails |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | principal_vps (per ADR-008) |
| Runtime | NestJS Worker |
| Output | report_only |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | trusted |
| Risk Class | medium |
| Risk Factors | Email sending capability, PII in emails |

## Access Rights

- **Read**: email_queue, user_preferences
- **Write**: email_logs (internal)
- **Secrets**: SMTP_CREDENTIALS, SENDGRID_API_KEY

## Governance

- **Verdict**: APPROVED (when enabled)
- **Related ADR**: ADR-009, ADR-008
- **Airlock Required**: no (internal service)
- **Audit Trail**: yes (email logs)

## Placement Decision

**MUST run on principal VPS** - Email processing requires secrets access.

## Activation Status

Currently **DISABLED**. Enable via environment flag when ready.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
