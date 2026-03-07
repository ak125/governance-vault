---
id: REG-001
title: Agent Registry
status: active
version: 2.0.0
last_audit: 2026-03-08
total_agents: 165
---

# Agent Registry

Official source of truth for all agents in the AutoMecanik system.

## Quick Stats

| Verdict | Count |
|---------|-------|
| APPROVED | 67 |
| APPROVED_WITH_CONDITIONS | 19 |
| NOT_APPROVED | 46 |
| PLANNED (no code) | 15 |
| CONCEPTUAL (lettered) | 34 |
| **TOTAL** | **165** |

## Related ADRs

- ADR-002: Zero-Trust Agents
- ADR-009: Phase 1 Agent Activation
- ADR-007: Location Independence
- ADR-008: Agent Placement Rules (3 Zones)
- ADR-011: OpenClaw to Claude API Replacement

---

## Registry Table — BMAD Agents

| agent_id | status | zone | trust | output | verdict |
|----------|--------|------|-------|--------|---------|
| bmad-master | active | local | trusted | report | APPROVED |
| analyst | active | local | trusted | report | APPROVED |
| architect | active | local | trusted | report | APPROVED |
| dev | active | local | restricted | bundle | APPROVED_WITH_CONDITIONS |
| pm | active | local | trusted | report | APPROVED |
| quick-flow-solo-dev | active | local | trusted | report | APPROVED |
| sm | active | local | trusted | report | APPROVED |
| tea | active | local | trusted | report | APPROVED |
| tech-writer | active | local | trusted | report | APPROVED |
| ux-designer | active | local | trusted | report | APPROVED |

## Registry Table — AI-COS Planned Agents

| agent_id | status | zone | trust | output | verdict |
|----------|--------|------|-------|--------|---------|
| agent.ceo.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cto.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cpo.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cmo.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cfo.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.qto | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.seo.lead | planned | principal_vps | restricted | bundle | NOT_APPROVED |
| agent.data.lead | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.rag.lead | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.aicos.architect | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.aicos.governance | planned | principal_vps | restricted | report | NOT_APPROVED |
| front-agent | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.seo.vlevel | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.seo.sitemap | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.seo.canonical | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.seo.content | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.data.cleanup | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.data.validator | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.data.backup | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.rag.indexer | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.rag.validator | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.rag.retriever | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.infra.monitor | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.infra.logs | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |

## Registry Table — Agent Prompts (.claude/agents/) — NEW

| agent_id | status | zone | trust | output | verdict |
|----------|--------|------|-------|--------|---------|
| prompt.keyword-planner | active | local | restricted | rpc | APPROVED |
| prompt.r4-keyword-planner | active | local | restricted | rpc | APPROVED |
| prompt.r6-keyword-planner | active | local | restricted | rpc | APPROVED |
| prompt.research-agent | active | local | restricted | rpc | APPROVED |
| prompt.brief-enricher | active | local | restricted | rpc | APPROVED |
| prompt.content-batch | active | local | restricted | rpc | APPROVED |
| prompt.r1-content-batch | active | local | restricted | rpc | APPROVED |
| prompt.r4-content-batch | active | local | restricted | rpc | APPROVED |
| prompt.r6-content-batch | active | local | restricted | rpc | APPROVED |
| prompt.conseil-batch | active | local | restricted | rpc | APPROVED |
| prompt.r3-image-prompt | active | local | restricted | report | APPROVED |
| prompt.r6-image-prompt | active | local | restricted | report | APPROVED |

## Registry Table — Skills (.claude/skills/)

| agent_id | status | zone | trust | output | verdict |
|----------|--------|------|-------|--------|---------|
| ui-os | active | local | trusted | report | APPROVED |
| ui-ux-pro-max | active | local | trusted | report | APPROVED |
| seo-content-architect | active | local | trusted | report | APPROVED |
| governance-vault-ops | active | local | trusted | report | APPROVED |
| frontend-design | active | local | trusted | report | APPROVED |
| skill.backend-test | active | local | trusted | report | APPROVED |
| skill.code-review | active | local | trusted | report | APPROVED |
| skill.content-audit | active | local | trusted | report | APPROVED |
| skill.db-migration | active | local | trusted | report | APPROVED |
| skill.marketing-hub | active | local | trusted | report | APPROVED |
| skill.payment-review | active | local | trusted | report | APPROVED |
| skill.rag-ops | active | local | trusted | report | APPROVED |
| skill.responsive-audit | active | local | trusted | report | APPROVED |
| skill.vehicle-ops | active | local | trusted | report | APPROVED |

## Registry Table — Backend Workers

| agent_id | status | zone | trust | output | verdict |
|----------|--------|------|-------|--------|---------|
| worker.content-refresh | active | principal_vps | restricted | rpc | APPROVED_WITH_CONDITIONS |
| worker.video-execution | active | principal_vps | restricted | rpc | APPROVED_WITH_CONDITIONS |
| worker.pipeline-chain-poller | active | principal_vps | restricted | rpc | APPROVED_WITH_CONDITIONS |
| worker.metrics-processor | active | principal_vps | trusted | report | APPROVED |
| seo-monitor-scheduler | active | principal_vps | trusted | report | APPROVED |
| seo-monitor-processor | active | principal_vps | trusted | report | APPROVED |
| seo-audit-scheduler | active | principal_vps | trusted | report | APPROVED |
| seo-interpolation-monitor | active | principal_vps | trusted | report | APPROVED |
| seo-monitoring-service | active | principal_vps | trusted | report | APPROVED |
| sitemap-delta-service | active | principal_vps | trusted | report | APPROVED |
| search-monitoring-service | active | principal_vps | trusted | report | APPROVED |
| support-analytics-service | active | principal_vps | trusted | report | APPROVED |
| mcp-alerting-service | active | principal_vps | trusted | report | APPROVED |
| database-monitor | active | principal_vps | trusted | report | APPROVED |
| cache-warming-service | active | principal_vps | trusted | report | APPROVED |
| seo-keyword-expert | active | principal_vps | trusted | report | APPROVED |
| serp-analyzer | active | principal_vps | trusted | report | APPROVED |

## Registry Table — MCP / GitHub Actions / Scripts

| agent_id | status | zone | trust | output | verdict |
|----------|--------|------|-------|--------|---------|
| mcp-shadcn | active | local | trusted | report | APPROVED |
| mcp-supabase | active | local | trusted | report | APPROVED |
| mcp-supabase-local | active | local | trusted | report | APPROVED |
| gh-ci-deploy | active | external | trusted | report | APPROVED |
| gh-worker-deploy | active | external | trusted | report | APPROVED |
| gh-perf-gates | active | external | trusted | report | APPROVED |
| gh-spec-validation | active | external | trusted | report | APPROVED |
| gh-safety-observer | active | external | trusted | report | APPROVED |
| ui-audit-suite | active | local | trusted | report | APPROVED |
| ui-governance-suite | active | local | trusted | report | APPROVED |

## Registry Table — Python Analysis Agents (NO IMPLEMENTATION)

> These agents were planned but NO scripts exist in the codebase. Status: NOT_APPROVED.

| agent_id | status | zone | trust | output | verdict |
|----------|--------|------|-------|--------|---------|
| a1_security | planned | external | untrusted | report | NOT_APPROVED |
| a2_massive_files | planned | external | untrusted | report | NOT_APPROVED |
| a3_duplications | planned | external | untrusted | report | NOT_APPROVED |
| a4_dead_code | planned | external | untrusted | report | NOT_APPROVED |
| a5_complexity | planned | external | untrusted | report | NOT_APPROVED |
| a6_dependencies | planned | external | untrusted | report | NOT_APPROVED |
| a7_performance | planned | external | untrusted | report | NOT_APPROVED |
| a8_accessibility | planned | external | untrusted | report | NOT_APPROVED |
| a9_seo | planned | external | untrusted | report | NOT_APPROVED |
| a10_i18n | planned | external | untrusted | report | NOT_APPROVED |
| a11_tests | planned | external | untrusted | report | NOT_APPROVED |
| a12_documentation | planned | external | untrusted | report | NOT_APPROVED |
| f0_autoimport | planned | external | untrusted | bundle | NOT_APPROVED |
| f1_dead_code_surgeon | planned | external | untrusted | bundle | NOT_APPROVED |
| f15_risk_scorer | planned | external | untrusted | report | NOT_APPROVED |

## Lettered Series (Conceptual - NOT_APPROVED)

> Conceptual agent series. No implementation exists in the codebase.

| Series | Count | Status |
|--------|-------|--------|
| G-Series (Governance) | 18 | conceptual |
| F-Series (Testing) | 6 | conceptual |
| M-Series (Mutation) | 2 | conceptual |
| A-Series (Architecture) | 7 | conceptual |
| B-Series (Ethics) | 1 | conceptual |
| **Total Lettered** | **34** | NOT_APPROVED |

---

## Enforcement Rules

1. **APPROVED**: Agent can operate freely within documented scope
2. **APPROVED_WITH_CONDITIONS**: Agent requires Airlock/RPC gate
3. **NOT_APPROVED**: Agent MUST NOT be activated without new ADR

## Validation Schema

For CI integration:
- `status`: active | planned | disabled | conceptual
- `zone`: local | principal_vps | external (per ADR-008)
- `trust`: trusted | restricted | untrusted
- `output`: report | bundle | rpc
- `verdict`: APPROVED | APPROVED_WITH_CONDITIONS | NOT_APPROVED

---

_Registry Version: 2.0.0_
_Last Updated: 2026-03-08_
_Maintainer: Governance Team_
