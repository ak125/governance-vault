---
agent_id: agent.qa.visual
agent_name: QA Visual Test Agent
status: active
owner: QA Team
governance_verdict: APPROVED
last_updated: 2026-03-10
execution_engine: Playwright
zone: dev_vps
---

# Agent: QA Visual Test Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.qa.visual` |
| Name | QA Visual Test Agent |
| Status | **active** |
| Owner | QA Team |
| Description | Validates visual integrity and responsive design: header/footer consistency, horizontal overflow, touch targets, accessibility, CTA visibility, font loading, responsive images |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | dev_vps (46.224.118.55) |
| Runtime | Playwright (Chromium headless) |
| Output | report_only (via Supabase reporter) |
| Schedule | Every 6 hours |
| Test File | `frontend/tests/qa-audit/suites/visual.spec.ts` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | Read-only DOM inspection, no screenshots stored externally |

## Access Rights

| Resource | Permission | Notes |
|----------|-----------|-------|
| Production pages (12 key pages) | READ | Navigate and inspect DOM |
| Supabase __qa_audit_* | WRITE | Via reporter |

## Capabilities

- 7 test groups: header/footer, overflow, touch targets (44px), a11y, CTA visibility, font loading, responsive images
- Touch target threshold: 44px minimum (WCAG 2.5.5)
- Overflow detection via scrollWidth comparison
- Font loading validation via document.fonts API

## Constraints

- No visual regression screenshots (local only on failure)
- No pixel-by-pixel comparison
- Max 12 pages per check group
- Tolerance: up to 15 small touch targets allowed (nav items, inline links)
