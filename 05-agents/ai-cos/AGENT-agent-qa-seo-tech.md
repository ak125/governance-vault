---
agent_id: agent.qa.seotech
agent_name: QA SEO Technical Test Agent
status: active
owner: QA Team
governance_verdict: APPROVED
last_updated: 2026-03-10
execution_engine: Playwright
zone: dev_vps
---

# Agent: QA SEO Technical Test Agent

## Identity

| Field | Value |
|-------|-------|
| ID | `agent.qa.seotech` |
| Name | QA SEO Technical Test Agent |
| Status | **active** |
| Owner | QA Team |
| Description | Validates technical SEO standards: meta tags, TTFB, HTTPS redirects, Schema.org JSON-LD, robots.txt, sitemap.xml, HTTP security headers, Open Graph tags |

## Execution Environment

| Field | Value |
|-------|-------|
| Zone | dev_vps (46.224.118.55) |
| Runtime | Playwright (Chromium headless) |
| Output | report_only (via Supabase reporter) |
| Schedule | Every 12 hours |
| Test File | `frontend/tests/qa-audit/suites/seo-tech.spec.ts` |

## Trust & Risk

| Field | Value |
|-------|-------|
| Trust Level | restricted |
| Risk Class | low |
| Risk Factors | HTTP requests only, validates public-facing metadata |

## Access Rights

| Resource | Permission | Notes |
|----------|-----------|-------|
| Production pages (15 SEO pages) | READ | Navigate and inspect meta tags |
| /robots.txt, /sitemap.xml | READ | Validate SEO technical files |
| HTTP headers | READ | Verify security/cache headers |
| Supabase __qa_audit_* | WRITE | Via reporter |

## Capabilities

- 8 test groups: meta tags, TTFB, HTTPS, Schema.org, robots.txt, sitemap.xml, security headers, Open Graph
- TTFB threshold: 3000ms (via Navigation Timing API)
- Title length: 20-70 chars, description: 50-170 chars
- JSON-LD validation: parse and verify @type fields
- HTTPS redirect verification (301/302/307/308)

## Constraints

- No crawling beyond defined page list
- No external link validation
- No Lighthouse/PageSpeed integration (uses native Playwright metrics)
- Max 15 pages per SEO check group
