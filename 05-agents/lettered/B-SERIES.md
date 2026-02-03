---
series_id: B-SERIES
series_name: Ethics Agents
status: planned
total_agents: 1
governance_verdict: NOT_APPROVED
last_audit: 2026-02-04
zone: external
---

# B-Series: Ethics Agents (1 agent)

## Overview

The B-Series consists of ethics-focused agents for PII protection, license compliance, and ethical code practices.

**Status**: All agents in Phase 0 (planned) - NOT APPROVED for activation.

## Agents

| ID | Name | Role | Zone | Verdict |
|----|------|------|------|---------|
| B7 | Ethics Guard | PII/License compliance | external | NOT_APPROVED |

## Agent Details: B7 Ethics Guard

### Responsibilities
- Detect hardcoded PII (emails, phones, addresses)
- Validate license headers and compliance
- Check for sensitive data exposure
- Verify GDPR/CCPA compliance patterns

### Risk Factors
- Access to sensitive code patterns
- May flag false positives

## Common Attributes

- **Trust Level**: untrusted
- **Risk Class**: low (analysis only)
- **Output**: report_only
- **Airlock Required**: no
- **Activation Condition**: Requires separate ADR

## Governance Decision

**NOT APPROVED** - B-Series agents are Phase 0 planned only. Requires ADR for activation.

---

_Last audit: 2026-02-04_
_Auditor: Claude (Governance Analyst)_
