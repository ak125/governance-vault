---
agent_id: agent.qa.functional
agent_name: QA Functional Test Agent
status: active
owner: QA Team
governance_verdict: APPROVED
last_updated: 2026-03-10
execution_engine: Playwright
zone: dev_vps
---

# Agent: QA Functional Test Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.qa.functional` |
| Name | QA Functional Test Agent |
| Status | **active** |
| Owner | QA Team |
| Description | Validates core site functionality: HTTP status, console errors, broken images/links, auth flows, search, cart, navigation, forms, API health |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | dev_vps (46.224.118.55) |
| Runtime | Playwright (Chromium headless) |
| Output | report_only (via Supabase reporter) |
| Schedule | Every 4 hours |
| Test File | `frontend/tests/qa-audit/suites/functional.spec.ts` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | HTTP GET requests only, no form submissions, no data mutations |

## Access Rights

| Resource | Permission | Notes |
|----------|-----------|-------|
| Production pages (50) | READ | Navigate and inspect DOM |
| Production APIs | READ | /health, /api/catalog/families |
| Supabase __qa_audit_* | WRITE | Via reporter |

## Capabilities

- 10 test groups: HTTP status, console errors, broken images, broken links, auth flows, search, cart, navigation, forms, API health
- 3 viewports: desktop (1280), tablet (768), mobile (375)
- Captures JS errors via pageerror event
- Samples up to 20 internal links per page for broken link detection

## Constraints

- No form submissions or data mutations
- No authentication (tests unauthenticated user experience)
- Max 15 pages per check group to limit load
- HEAD requests only for link checking (5s timeout)
