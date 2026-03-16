---
id: REG-001
title: Agent Registry
status: active
version: 3.0.0
last_audit: 2026-03-16
reconciled_from: P1 Governance Hygiene
total_operational: 77
total_inactive: 93
total_entries: 170
---

# Agent Registry

Official source of truth for all agents in the AutoMecanik system.

> **v3.0.0 — P1 Reconciliation (2026-03-16)**
> Registry reconciled with actual implementations in `.claude/agents/` (39 files) and `.claude/skills/` (19 dirs).
> Split into OPERATIONAL (verified implementations) and INACTIVE (no implementation or conceptual).

## Quick Stats

| Category | Count |
|----------|-------|
| Operational — Agent Prompts | 39 |
| Operational — Skills | 19 |
| Operational — Backend Workers | 15 |
| Operational — MCP/GH Actions | 4 |
| **Total Operational** | **77** |
| Inactive — BMAD (no impl) | 10 |
| Inactive — AI-COS Planned | 24 |
| Inactive — Python Analysis | 15 |
| Inactive — Lettered Series | 34 |
| Inactive — Legacy MCP/GH/UI | 6 |
| Inactive — Legacy Skills | 4 |
| **Total Inactive** | **93** |
| **GRAND TOTAL** | **170** |

## Related ADRs

- ADR-002: Zero-Trust Agents
- ADR-009: Phase 1 Agent Activation
- ADR-007: Location Independence
- ADR-008: Agent Placement Rules (3 Zones → 4 Zones)
- ADR-011: OpenClaw to Claude API Replacement
- ADR-012: AI-COS VPS Architecture & Agent Placement

---

# PART 1 — OPERATIONAL (Verified Implementations)

## Agent Prompts (.claude/agents/) — 39 agents

All have verified `.md` definition files in `/opt/automecanik/app/.claude/agents/`.

| agent_id | domain | zone | trust | output | verdict | impl_file |
|----------|--------|------|-------|--------|---------|-----------|
| keyword-planner | seo | local | restricted | rpc | APPROVED | keyword-planner.md |
| r1-keyword-planner | seo | local | restricted | rpc | APPROVED | r1-keyword-planner.md |
| r1-content-batch | seo | local | restricted | rpc | APPROVED | r1-content-batch.md |
| r1-router-validator | seo | local | restricted | report | APPROVED | r1-router-validator.md |
| r2-keyword-planner | seo | local | restricted | rpc | APPROVED | r2-keyword-planner.md |
| r2-product-validator | seo | local | restricted | report | APPROVED | r2-product-validator.md |
| r3-keyword-planner | seo | local | restricted | rpc | APPROVED | r3-keyword-planner.md |
| r3-conseils-validator | seo | local | restricted | report | APPROVED | r3-conseils-validator.md |
| r3-image-prompt | seo | local | restricted | report | APPROVED | r3-image-prompt.md |
| r4-keyword-planner | seo | local | restricted | rpc | APPROVED | r4-keyword-planner.md |
| r4-content-batch | seo | local | restricted | rpc | APPROVED | r4-content-batch.md |
| r4-reference-execution | seo | local | restricted | rpc | APPROVED | r4-reference-execution.md |
| r4-reference-validator | seo | local | restricted | report | APPROVED | r4-reference-validator.md |
| r5-keyword-planner | seo | local | restricted | rpc | APPROVED | r5-keyword-planner.md |
| r5-diagnostic-execution | seo | local | restricted | rpc | APPROVED | r5-diagnostic-execution.md |
| r5-diagnostic-validator | seo | local | restricted | report | APPROVED | r5-diagnostic-validator.md |
| r6-keyword-planner | seo | local | restricted | rpc | APPROVED | r6-keyword-planner.md |
| r6-content-batch | seo | local | restricted | rpc | APPROVED | r6-content-batch.md |
| r6-guide-achat-validator | seo | local | restricted | report | APPROVED | r6-guide-achat-validator.md |
| r6-support-validator | seo | local | restricted | report | APPROVED | r6-support-validator.md |
| r6-image-prompt | seo | local | restricted | report | APPROVED | r6-image-prompt.md |
| r7-keyword-planner | seo | local | restricted | rpc | APPROVED | r7-keyword-planner.md |
| r7-brand-execution | seo | local | restricted | rpc | APPROVED | r7-brand-execution.md |
| r7-brand-validator | seo | local | restricted | report | APPROVED | r7-brand-validator.md |
| r7-brand-rag-generator | seo | local | restricted | rpc | APPROVED | r7-brand-rag-generator.md |
| r8-keyword-planner | seo | local | restricted | rpc | APPROVED | r8-keyword-planner.md |
| r8-vehicle-execution | seo | local | restricted | rpc | APPROVED | r8-vehicle-execution.md |
| r8-vehicle-validator | seo | local | restricted | report | APPROVED | r8-vehicle-validator.md |
| r0-home-execution | seo | local | restricted | rpc | APPROVED | r0-home-execution.md |
| r0-home-validator | seo | local | restricted | report | APPROVED | r0-home-validator.md |
| research-agent | seo | local | restricted | rpc | APPROVED | research-agent.md |
| brief-enricher | seo | local | restricted | rpc | APPROVED | brief-enricher.md |
| content-batch | seo | local | restricted | rpc | APPROVED | content-batch.md |
| conseil-batch | seo | local | restricted | rpc | APPROVED | conseil-batch.md |
| blog-hub-planner | seo | local | restricted | rpc | APPROVED | blog-hub-planner.md |
| agentic-planner | infra | local | restricted | rpc | APPROVED | agentic-planner.md |
| agentic-solver | infra | local | restricted | rpc | APPROVED | agentic-solver.md |
| agentic-critic | infra | local | restricted | report | APPROVED | agentic-critic.md |
| phase1-auditor | governance | local | restricted | report | APPROVED | phase1-auditor.md |

## Skills (.claude/skills/) — 19 skills

All have verified directories with SKILL.md in `/opt/automecanik/app/.claude/skills/`.

| skill_id | domain | zone | trust | output | verdict | impl_dir |
|----------|--------|------|-------|--------|---------|----------|
| backend-test | infra | local | trusted | report | APPROVED | backend-test/ |
| code-review | governance | local | trusted | report | APPROVED | code-review/ |
| content-audit | governance | local | trusted | report | APPROVED | content-audit/ |
| content-gen | seo | local | restricted | rpc | APPROVED | content-gen/ |
| db-migration | infra | local | trusted | report | APPROVED | db-migration/ |
| frontend-design | ui | local | trusted | report | APPROVED | frontend-design/ |
| governance-vault-ops | governance | local | trusted | report | APPROVED | governance-vault-ops/ |
| keyword-planner | seo | local | restricted | rpc | APPROVED | keyword-planner/ |
| marketing-hub | marketing | local | trusted | report | APPROVED | marketing-hub/ |
| payment-review | payment | local | trusted | report | APPROVED | payment-review/ |
| pipeline-orchestrator | seo | local | restricted | rpc | APPROVED | pipeline-orchestrator/ |
| rag-check | rag | local | trusted | report | APPROVED | rag-check/ |
| rag-ops | rag | local | trusted | report | APPROVED | rag-ops/ |
| responsive-audit | ui | local | trusted | report | APPROVED | responsive-audit/ |
| seo-content-architect | seo | local | trusted | report | APPROVED | seo-content-architect/ |
| seo-gamme-audit | seo | local | restricted | report | APPROVED | seo-gamme-audit/ |
| ui-os | ui | local | trusted | report | APPROVED | ui-os/ |
| ui-ux-pro-max | ui | local | trusted | report | APPROVED | ui-ux-pro-max/ |
| vehicle-ops | vehicle | local | trusted | report | APPROVED | vehicle-ops/ |

## Backend Workers — 15 workers

Backend services, not agent prompt files. Verified via NestJS module structure.

| agent_id | domain | zone | trust | output | verdict |
|----------|--------|------|-------|--------|---------|
| worker.content-refresh | seo | principal_vps | restricted | rpc | APPROVED_WITH_CONDITIONS |
| worker.video-execution | seo | principal_vps | restricted | rpc | APPROVED_WITH_CONDITIONS |
| worker.pipeline-chain-poller | seo | principal_vps | restricted | rpc | APPROVED_WITH_CONDITIONS |
| worker.metrics-processor | infra | principal_vps | trusted | report | APPROVED |
| seo-monitor-scheduler | seo | principal_vps | trusted | report | APPROVED |
| seo-monitor-processor | seo | principal_vps | trusted | report | APPROVED |
| seo-audit-scheduler | seo | principal_vps | trusted | report | APPROVED |
| seo-interpolation-monitor | seo | principal_vps | trusted | report | APPROVED |
| seo-monitoring-service | seo | principal_vps | trusted | report | APPROVED |
| sitemap-delta-service | seo | principal_vps | trusted | report | APPROVED |
| search-monitoring-service | infra | principal_vps | trusted | report | APPROVED |
| support-analytics-service | infra | principal_vps | trusted | report | APPROVED |
| mcp-alerting-service | infra | principal_vps | trusted | report | APPROVED |
| database-monitor | infra | principal_vps | trusted | report | APPROVED |
| cache-warming-service | infra | principal_vps | trusted | report | APPROVED |

## MCP Integrations — 4 entries

External tool integrations, verified via MCP configuration.

| agent_id | domain | zone | trust | output | verdict |
|----------|--------|------|-------|--------|---------|
| mcp-shadcn | ui | local | trusted | report | APPROVED |
| mcp-supabase | infra | local | trusted | report | APPROVED |
| mcp-supabase-local | infra | local | trusted | report | APPROVED |
| gh-ci-deploy | infra | external | trusted | report | APPROVED |

---

# PART 2 — INACTIVE (No Implementation or Conceptual)

> These entries are preserved for reference but have NO verified implementation.
> They MUST NOT be activated without a new ADR or implementation.

## BMAD Agents — 10 entries (DORMANT)

Registered as "active" in v2.1.0 but zero implementation files found.

| agent_id | domain | original_verdict | reason_inactive |
|----------|--------|-----------------|-----------------|
| bmad-master | bmad | APPROVED | No implementation file |
| analyst | bmad | APPROVED | No implementation file |
| architect | bmad | APPROVED | No implementation file |
| dev | bmad | APPROVED_WITH_CONDITIONS | No implementation file |
| pm | bmad | APPROVED | No implementation file |
| quick-flow-solo-dev | bmad | APPROVED | No implementation file |
| sm | bmad | APPROVED | No implementation file |
| tea | bmad | APPROVED | No implementation file |
| tech-writer | bmad | APPROVED | No implementation file |
| ux-designer | bmad | APPROVED | No implementation file |

## AI-COS Planned Agents — 24 entries (PENDING ADR)

| agent_id | domain | original_verdict | reason_inactive |
|----------|--------|-----------------|-----------------|
| agent.ceo.ia | governance | NOT_APPROVED | No implementation, requires ADR |
| agent.cto.ia | infra | NOT_APPROVED | No implementation, requires ADR |
| agent.cpo.ia | governance | NOT_APPROVED | No implementation, requires ADR |
| agent.cmo.ia | marketing | NOT_APPROVED | No implementation, requires ADR |
| agent.cfo.ia | governance | NOT_APPROVED | No implementation, requires ADR |
| agent.qto | governance | NOT_APPROVED | No implementation, requires ADR |
| agent.seo.lead | seo | NOT_APPROVED | No implementation, requires ADR |
| agent.data.lead | infra | NOT_APPROVED | No implementation, requires ADR |
| agent.rag.lead | rag | NOT_APPROVED | No implementation, requires ADR |
| agent.aicos.architect | governance | NOT_APPROVED | No implementation, requires ADR |
| agent.aicos.governance | governance | NOT_APPROVED | No implementation, requires ADR |
| front-agent | ui | NOT_APPROVED | No implementation, requires ADR |
| agent.seo.vlevel | seo | APPROVED_WITH_CONDITIONS | No implementation |
| agent.seo.sitemap | seo | APPROVED_WITH_CONDITIONS | No implementation |
| agent.seo.canonical | seo | APPROVED_WITH_CONDITIONS | No implementation |
| agent.seo.content | seo | APPROVED_WITH_CONDITIONS | No implementation |
| agent.data.cleanup | infra | APPROVED_WITH_CONDITIONS | No implementation |
| agent.data.validator | infra | APPROVED_WITH_CONDITIONS | No implementation |
| agent.data.backup | infra | APPROVED_WITH_CONDITIONS | No implementation |
| agent.rag.indexer | rag | APPROVED_WITH_CONDITIONS | No implementation |
| agent.rag.validator | rag | APPROVED_WITH_CONDITIONS | No implementation |
| agent.rag.retriever | rag | APPROVED_WITH_CONDITIONS | No implementation |
| agent.infra.monitor | infra | APPROVED_WITH_CONDITIONS | No implementation |
| agent.infra.logs | infra | APPROVED_WITH_CONDITIONS | No implementation |

## Python Analysis Agents — 15 entries (CONCEPTUAL)

| agent_id | domain | original_verdict | reason_inactive |
|----------|--------|-----------------|-----------------|
| a1_security | infra | NOT_APPROVED | No implementation |
| a2_massive_files | infra | NOT_APPROVED | No implementation |
| a3_duplications | infra | NOT_APPROVED | No implementation |
| a4_dead_code | infra | NOT_APPROVED | No implementation |
| a5_complexity | infra | NOT_APPROVED | No implementation |
| a6_dependencies | infra | NOT_APPROVED | No implementation |
| a7_performance | infra | NOT_APPROVED | No implementation |
| a8_accessibility | ui | NOT_APPROVED | No implementation |
| a9_seo | seo | NOT_APPROVED | No implementation |
| a10_i18n | infra | NOT_APPROVED | No implementation |
| a11_tests | infra | NOT_APPROVED | No implementation |
| a12_documentation | infra | NOT_APPROVED | No implementation |
| f0_autoimport | infra | NOT_APPROVED | No implementation |
| f1_dead_code_surgeon | infra | NOT_APPROVED | No implementation |
| f15_risk_scorer | infra | NOT_APPROVED | No implementation |

## Lettered Series — 34 entries (CONCEPTUAL)

| Series | Domain | Count | Status |
|--------|--------|-------|--------|
| G-Series (Governance) | governance | 18 | conceptual |
| F-Series (Testing) | infra | 6 | conceptual |
| M-Series (Mutation) | infra | 2 | conceptual |
| A-Series (Architecture) | infra | 7 | conceptual |
| B-Series (Ethics) | governance | 1 | conceptual |
| **Total Lettered** | — | **34** | NOT_APPROVED |

## Legacy Entries — 10 entries (REMOVED FROM OPERATIONAL)

Entries from v2.1.0 that had no verified implementation or were superseded.

| agent_id | reason |
|----------|--------|
| gh-worker-deploy | Merged into gh-ci-deploy workflow |
| gh-perf-gates | GitHub Action, not an agent |
| gh-spec-validation | GitHub Action, not an agent |
| gh-safety-observer | GitHub Action, not an agent |
| ui-audit-suite | No implementation found |
| ui-governance-suite | No implementation found |
| seo-keyword-expert | Backend service, not agent/worker — no verified use |
| serp-analyzer | Backend service, not agent/worker — no verified use |
| skill.keybindings-help | Built-in Claude Code feature, not a custom skill |
| skill.loop | Built-in Claude Code feature, not a custom skill |

---

## Enforcement Rules

1. **APPROVED**: Agent can operate freely within documented scope
2. **APPROVED_WITH_CONDITIONS**: Agent requires Airlock/RPC gate
3. **NOT_APPROVED**: Agent MUST NOT be activated without new ADR
4. **INACTIVE**: No implementation — preserved for reference only

## Validation Schema

- `status`: active | planned | disabled | conceptual | inactive
- `zone`: local | principal_vps | aicos_vps | external (per ADR-008, ADR-012)
- `trust`: trusted | restricted | untrusted
- `output`: report | bundle | rpc
- `domain`: seo | rag | vehicle | payment | ui | infra | marketing | governance | bmad
- `verdict`: APPROVED | APPROVED_WITH_CONDITIONS | NOT_APPROVED

---

_Registry Version: 3.0.0_
_Reconciled: 2026-03-16 (P1 Governance Hygiene)_
_Maintainer: Governance Team_
