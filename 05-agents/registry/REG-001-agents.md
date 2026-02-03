---
id: REG-001
title: Agent Registry
status: active
version: 1.4.0
last_audit: 2026-02-04
total_agents: 140
---

# Agent Registry

Official source of truth for all agents in the AutoMecanik system.

## Quick Stats

| Verdict | Count |
|---------|-------|
| APPROVED | 54 |
| APPROVED_WITH_CONDITIONS | 15 |
| NOT_APPROVED | 46 |
| PENDING_FICHE | 25 |
| **TOTAL** | **140** |

## Related ADRs

- ADR-002: Zero-Trust Agents
- ADR-009: Phase 1 Agent Activation
- ADR-007: Location Independence
- ADR-008: Agent Placement Rules (3 Zones)

---

## Registry Table

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
| agent.ceo.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cto.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cpo.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cmo.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.cfo.ia | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.qto | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.seo.lead | planned | principal_vps | restricted | bundle | NOT_APPROVED |
| agent.data.lead | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.rag.lead | planned | principal_vps | restricted | report | NOT_APPROVED |
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
| agent.aicos.architect | planned | principal_vps | restricted | report | NOT_APPROVED |
| agent.aicos.governance | planned | principal_vps | restricted | report | NOT_APPROVED |
| front-agent | planned | principal_vps | restricted | report | NOT_APPROVED |
| a1_security | active | external | untrusted | report | APPROVED |
| a2_massive_files | active | external | untrusted | report | APPROVED |
| a3_duplications | active | external | untrusted | report | APPROVED |
| a4_dead_code | active | external | untrusted | report | APPROVED |
| a5_complexity | active | external | untrusted | report | APPROVED |
| a6_dependencies | active | external | untrusted | report | APPROVED |
| a7_performance | active | external | untrusted | report | APPROVED |
| a8_accessibility | active | external | untrusted | report | APPROVED |
| a9_seo | active | external | untrusted | report | APPROVED |
| a10_i18n | active | external | untrusted | report | APPROVED |
| a11_tests | active | external | untrusted | report | APPROVED |
| a12_documentation | active | external | untrusted | report | APPROVED |
| f0_autoimport | active | external | untrusted | bundle | APPROVED_WITH_CONDITIONS |
| f1_dead_code_surgeon | active | external | untrusted | bundle | APPROVED_WITH_CONDITIONS |
| f15_risk_scorer | active | external | untrusted | report | APPROVED |
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
| metrics-processor | active | principal_vps | trusted | report | APPROVED |
| cache-warming-service | active | principal_vps | trusted | report | APPROVED |
| ui-os | active | local | trusted | report | APPROVED |
| ui-ux-pro-max | active | local | trusted | report | APPROVED |
| seo-content-architect | active | local | trusted | report | APPROVED |
| governance-vault-ops | active | local | trusted | report | APPROVED |
| frontend-design | active | local | trusted | report | APPROVED |
| seo-keyword-expert | active | principal_vps | trusted | report | APPROVED |
| serp-analyzer | active | principal_vps | trusted | report | APPROVED |
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

## Lettered Series (Planned - NOT_APPROVED)

| Series | Count | Status |
|--------|-------|--------|
| G-Series (Governance) | 18 | planned |
| F-Series (Testing) | 6 | planned |
| M-Series (Mutation) | 2 | planned |
| A-Series (Architecture) | 7 | planned |
| B-Series (Ethics) | 1 | planned |
| **Total Lettered** | **34** | NOT_APPROVED |

---

## Enforcement Rules

1. **APPROVED**: Agent can operate freely within documented scope
2. **APPROVED_WITH_CONDITIONS**: Agent requires Airlock/RPC gate
3. **NOT_APPROVED**: Agent MUST NOT be activated without new ADR

## Validation Schema

For CI integration:
- `status`: active | planned | disabled
- `zone`: local | principal_vps | external (per ADR-008)
- `trust`: trusted | restricted | untrusted
- `output`: report | bundle | rpc
- `verdict`: APPROVED | APPROVED_WITH_CONDITIONS | NOT_APPROVED

---

_Registry Version: 1.4.0_
_Last Updated: 2026-02-04_
_Maintainer: Governance Team_
