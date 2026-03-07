---
series_id: A-SERIES
series_name: Architecture Agents
status: conceptual
total_agents: 7
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: external
code_status: no_implementation
---

# A-Series: Architecture Agents (7 agents)

> **WARNING**: Conceptual series only. No implementation exists in the codebase.

## Overview

The A-Series consists of architecture analysis agents for code quality, maintainability, and technical debt management.

**Status**: All agents in Phase 0 (planned) - NOT APPROVED for activation.

## Agents

| ID | Name | Role | Zone | Verdict |
|----|------|------|------|---------|
| A-CARTO | Architecture Cartography | System mapping | external | NOT_APPROVED |
| A2 | Dead Code Detection | Unused code finder | external | NOT_APPROVED |
| A3 | Duplication Detector | DRY violation finder | external | NOT_APPROVED |
| A4 | Complexity Analyzer | Complexity metrics | external | NOT_APPROVED |
| A5 | Type Coverage | TypeScript coverage | external | NOT_APPROVED |
| A6 | Dependency Graph | Dependency analysis | external | NOT_APPROVED |
| A7 | Performance Analyzer | Performance profiling | external | NOT_APPROVED |

## Common Attributes

- **Trust Level**: untrusted
- **Risk Class**: low (analysis only)
- **Output**: report_only
- **Airlock Required**: no
- **Activation Condition**: Requires separate ADR

## Governance Decision

**NOT APPROVED** - All A-Series agents are Phase 0 planned only. Requires ADR for activation.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
