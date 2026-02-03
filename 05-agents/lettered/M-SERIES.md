---
series_id: M-SERIES
series_name: Mutation Agents
status: planned
total_agents: 2
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: external
---

# M-Series: Mutation Agents (2 agents)

## Overview

The M-Series consists of mutation testing agents for code quality and regression prevention.

**Status**: All agents in Phase 0 (planned) - NOT APPROVED for activation.

## Agents

| ID | Name | Role | Zone | Verdict |
|----|------|------|------|---------|
| M2 | Mutation Testing | Code mutation analysis | external | NOT_APPROVED |
| M4 | Shadow Traffic | Traffic replay testing | external | NOT_APPROVED |

## Common Attributes

- **Trust Level**: untrusted
- **Risk Class**: medium (code modification for testing)
- **Output**: report_only
- **Airlock Required**: yes (mutation results)
- **Activation Condition**: Requires separate ADR

## Governance Decision

**NOT APPROVED** - All M-Series agents are Phase 0 planned only. Requires ADR for activation.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
