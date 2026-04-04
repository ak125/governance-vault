---
id: REG-001
title: Agent Registry
status: active
version: 2.3.0
last_audit: 2026-04-04
total_agents: 144
---

# Agent Registry

Official source of truth for all agents in the AutoMecanik system.

## Quick Stats

| Verdict | Count |
|---------|-------|
| APPROVED | 59 |
| APPROVED_WITH_CONDITIONS | 20 |
| NOT_APPROVED | 31 |
| CONCEPTUAL (lettered) | 34 |
| **TOTAL** | **144** |

## Domain Coverage

> Counts include all agents (active + planned + conceptual). Lettered series counted as group (34).

| Domain | Active | Planned | Total | Key agents |
|--------|--------|---------|-------|------------|
| SEO | 24 | 10 | 34 | keyword-planner, content-batch, seo-monitor-*, seo-vlevel, sitemap-delta, 4 sub-leads |
| Infrastructure | 15 | 20 | 35 | backend-test, db-migration, gh-ci-deploy, metrics-processor, a1-a12 |
| BMAD | 10 | 0 | 10 | bmad-master, analyst, architect, dev |
| Gouvernance | 3 | 6 | 9 | governance-vault-ops, code-review, content-audit |
| UI/Frontend | 7 | 2 | 9 | frontend-design, ui-os, ui-ux-pro-max, responsive-audit |
| RAG | 1 | 4 | 5 | rag-ops, rag-indexer, rag-validator, rag-retriever |
| Marketing | 1 | 1 | 2 | marketing-hub, agent.cmo.ia |
| Vehicules | 1 | 0 | 1 | vehicle-ops |
| Paiements | 1 | 0 | 1 | payment-review |
| Quality/QA | 4 | 0 | 4 | agent.qa.orchestrator, agent.qa.functional, agent.qa.visual, agent.qa.seo-tech |
| **Sous-total** | **67** | **43** | **110** | Individual agents |
| Lettered Series | 0 | 34 | 34 | G/F/M/A/B-Series (conceptual) |
| **TOTAL** | **67** | **77** | **144** | |

## Related ADRs

- ADR-002: Zero-Trust Agents
- ADR-009: Phase 1 Agent Activation
- ADR-007: Location Independence
- ADR-008: Agent Placement Rules (3 Zones → 4 Zones)
- ADR-011: OpenClaw to Claude API Replacement
- ADR-012: AI-COS VPS Architecture & Agent Placement

---

## Registry Table — BMAD Agents

| agent_id | domain | status | zone | trust | output | verdict |
|----------|--------|--------|------|-------|--------|---------|
| bmad-master | bmad | active | local | trusted | report | APPROVED |
| analyst | bmad | active | local | trusted | report | APPROVED |
| architect | bmad | active | local | trusted | report | APPROVED |
| dev | bmad | active | local | restricted | bundle | APPROVED_WITH_CONDITIONS |
| pm | bmad | active | local | trusted | report | APPROVED |
| quick-flow-solo-dev | bmad | active | local | trusted | report | APPROVED |
| sm | bmad | active | local | trusted | report | APPROVED |
| tea | bmad | active | local | trusted | report | APPROVED |
| tech-writer | bmad | active | local | trusted | report | APPROVED |
| ux-designer | bmad | active | local | trusted | report | APPROVED |

## Registry Table — AI-COS Planned Agents

| agent_id | domain | status | zone | trust | output | verdict |
|----------|--------|--------|------|-------|--------|---------|
| agent.ceo.ia | governance | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cto.ia | infra | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cpo.ia | governance | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cmo.ia | marketing | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cfo.ia | governance | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.qto | governance | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.seo.lead | seo | planned | principal_vps | restricted | bundle | NOT_APPROVED |
| agent.data.lead | infra | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.rag.lead | rag | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.aicos.architect | governance | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.aicos.governance | governance | planned | principal_vps | restricted | report | NOT_APPROVED |
| front-agent | ui | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.seo.vlevel | seo | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.seo.sitemap | seo | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.seo.canonical | seo | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.seo.content | seo | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.seo.kp.lead | seo | planned | principal_vps | restricted | bundle | NOT_APPROVED |
| agent.seo.content.lead | seo | planned | principal_vps | restricted | bundle | NOT_APPROVED |
| agent.seo.qa.lead | seo | planned | principal_vps | restricted | bundle | NOT_APPROVED |
| agent.seo.exec.lead | seo | planned | principal_vps | restricted | bundle | NOT_APPROVED |
| agent.data.cleanup | infra | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.data.validator | infra | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.data.backup | infra | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.rag.indexer | rag | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.rag.validator | rag | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.rag.retriever | rag | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.infra.monitor | infra | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.infra.logs | infra | planned | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.qa.orchestrator | quality | active | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.qa.functional | quality | active | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.qa.visual | quality | active | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |
| agent.qa.seo-tech | quality | active | principal_vps | restricted | report | APPROVED_WITH_CONDITIONS |

## Registry Table — Agent Prompts (.claude/agents/)

| agent_id | domain | status | zone | trust | output | verdict |
|----------|--------|--------|------|-------|--------|---------|
| prompt.keyword-planner | seo | active | local | restricted | rpc | APPROVED |
| prompt.r4-keyword-planner | seo | active | local | restricted | rpc | APPROVED |
| prompt.r6-keyword-planner | seo | active | local | restricted | rpc | APPROVED |
| prompt.research-agent | seo | active | local | restricted | rpc | APPROVED |
| prompt.brief-enricher | seo | active | local | restricted | rpc | APPROVED |
| prompt.content-batch | seo | active | local | restricted | rpc | APPROVED |
| prompt.r1-content-batch | seo | active | local | restricted | rpc | APPROVED |
| prompt.r4-content-batch | seo | active | local | restricted | rpc | APPROVED |
| prompt.r6-content-batch | seo | active | local | restricted | rpc | APPROVED |
| prompt.conseil-batch | seo | active | local | restricted | rpc | APPROVED |
| prompt.r3-image-prompt | seo | active | local | restricted | report | APPROVED |
| prompt.r6-image-prompt | seo | active | local | restricted | report | APPROVED |

## Registry Table — Skills (.claude/skills/)

| agent_id | domain | status | zone | trust | output | verdict |
|----------|--------|--------|------|-------|--------|---------|
| ui-os | ui | active | local | trusted | report | APPROVED |
| ui-ux-pro-max | ui | active | local | trusted | report | APPROVED |
| seo-content-architect | seo | active | local | trusted | report | APPROVED |
| governance-vault-ops | governance | active | local | trusted | report | APPROVED |
| frontend-design | ui | active | local | trusted | report | APPROVED |
| skill.backend-test | infra | active | local | trusted | report | APPROVED |
| skill.code-review | governance | active | local | trusted | report | APPROVED |
| skill.content-audit | governance | active | local | trusted | report | APPROVED |
| skill.db-migration | infra | active | local | trusted | report | APPROVED |
| skill.marketing-hub | marketing | active | local | trusted | report | APPROVED |
| skill.payment-review | payment | active | local | trusted | report | APPROVED |
| skill.rag-ops | rag | active | local | trusted | report | APPROVED |
| skill.responsive-audit | ui | active | local | trusted | report | APPROVED |
| skill.vehicle-ops | vehicle | active | local | trusted | report | APPROVED |

## Registry Table — Backend Workers

| agent_id | domain | status | zone | trust | output | verdict |
|----------|--------|--------|------|-------|--------|---------|
| worker.content-refresh | seo | active | principal_vps | restricted | rpc | APPROVED_WITH_CONDITIONS |
| worker.video-execution | seo | active | principal_vps | restricted | rpc | APPROVED_WITH_CONDITIONS |
| worker.pipeline-chain-poller | seo | active | principal_vps | restricted | rpc | APPROVED_WITH_CONDITIONS |
| worker.metrics-processor | infra | active | principal_vps | trusted | report | APPROVED |
| seo-monitor-scheduler | seo | active | principal_vps | trusted | report | APPROVED |
| seo-monitor-processor | seo | active | principal_vps | trusted | report | APPROVED |
| seo-audit-scheduler | seo | active | principal_vps | trusted | report | APPROVED |
| seo-interpolation-monitor | seo | active | principal_vps | trusted | report | APPROVED |
| seo-monitoring-service | seo | active | principal_vps | trusted | report | APPROVED |
| sitemap-delta-service | seo | active | principal_vps | trusted | report | APPROVED |
| search-monitoring-service | infra | active | principal_vps | trusted | report | APPROVED |
| support-analytics-service | infra | active | principal_vps | trusted | report | APPROVED |
| mcp-alerting-service | infra | active | principal_vps | trusted | report | APPROVED |
| database-monitor | infra | active | principal_vps | trusted | report | APPROVED |
| cache-warming-service | infra | active | principal_vps | trusted | report | APPROVED |
| seo-keyword-expert | seo | active | principal_vps | trusted | report | APPROVED |
| serp-analyzer | seo | active | principal_vps | trusted | report | APPROVED |

## Registry Table — MCP / GitHub Actions / Scripts

| agent_id | domain | status | zone | trust | output | verdict |
|----------|--------|--------|------|-------|--------|---------|
| mcp-shadcn | ui | active | local | trusted | report | APPROVED |
| mcp-supabase | infra | active | local | trusted | report | APPROVED |
| mcp-supabase-local | infra | active | local | trusted | report | APPROVED |
| gh-ci-deploy | infra | active | external | trusted | report | APPROVED |
| gh-worker-deploy | infra | active | external | trusted | report | APPROVED |
| gh-perf-gates | infra | active | external | trusted | report | APPROVED |
| gh-spec-validation | infra | active | external | trusted | report | APPROVED |
| gh-safety-observer | infra | active | external | trusted | report | APPROVED |
| ui-audit-suite | ui | active | local | trusted | report | APPROVED |
| ui-governance-suite | ui | active | local | trusted | report | APPROVED |

## Registry Table — Python Analysis Agents (NO IMPLEMENTATION)

> These agents were planned but NO scripts exist in the codebase. Status: NOT_APPROVED.

| agent_id | domain | status | zone | trust | output | verdict |
|----------|--------|--------|------|-------|--------|---------|
| a1_security | infra | planned | external | untrusted | report | NOT_APPROVED |
| a2_massive_files | infra | planned | external | untrusted | report | NOT_APPROVED |
| a3_duplications | infra | planned | external | untrusted | report | NOT_APPROVED |
| a4_dead_code | infra | planned | external | untrusted | report | NOT_APPROVED |
| a5_complexity | infra | planned | external | untrusted | report | NOT_APPROVED |
| a6_dependencies | infra | planned | external | untrusted | report | NOT_APPROVED |
| a7_performance | infra | planned | external | untrusted | report | NOT_APPROVED |
| a8_accessibility | ui | planned | external | untrusted | report | NOT_APPROVED |
| a9_seo | seo | planned | external | untrusted | report | NOT_APPROVED |
| a10_i18n | infra | planned | external | untrusted | report | NOT_APPROVED |
| a11_tests | infra | planned | external | untrusted | report | NOT_APPROVED |
| a12_documentation | infra | planned | external | untrusted | report | NOT_APPROVED |
| f0_autoimport | infra | planned | external | untrusted | bundle | NOT_APPROVED |
| f1_dead_code_surgeon | infra | planned | external | untrusted | bundle | NOT_APPROVED |
| f15_risk_scorer | infra | planned | external | untrusted | report | NOT_APPROVED |

## Lettered Series (Conceptual - NOT_APPROVED)

> Conceptual agent series. No implementation exists in the codebase.

| Series | Domain | Count | Status |
|--------|--------|-------|--------|
| G-Series (Governance) | governance | 18 | conceptual |
| F-Series (Testing) | infra | 6 | conceptual |
| M-Series (Mutation) | infra | 2 | conceptual |
| A-Series (Architecture) | infra | 7 | conceptual |
| B-Series (Ethics) | governance | 1 | conceptual |
| **Total Lettered** | — | **34** | NOT_APPROVED |

---

## Enforcement Rules

1. **APPROVED**: Agent can operate freely within documented scope
2. **APPROVED_WITH_CONDITIONS**: Agent requires Airlock/RPC gate
3. **NOT_APPROVED**: Agent MUST NOT be activated without new ADR

## Validation Schema

For CI integration:
- `status`: active | planned | disabled | conceptual
- `zone`: local | principal_vps | aicos_vps | external (per ADR-008, ADR-012)
- `trust`: trusted | restricted | untrusted
- `output`: report | bundle | rpc
- `domain`: seo | rag | vehicle | payment | ui | infra | marketing | governance | bmad | quality
- `verdict`: APPROVED | APPROVED_WITH_CONDITIONS | NOT_APPROVED

---

_Registry Version: 2.3.0_
_Last Updated: 2026-04-04_
_Maintainer: Governance Team_
