---
id: ADR-009
title: Phase 1 Agent Activation Framework
status: accepted
date: 2026-02-03
decision_makers:
  - Architecture
  - Governance
---

## Context

The system now has:
- A frozen agent registry (REG-001 v1.3.0)
- Formal Zero-Trust rules for agents (ADR-002)
- An operational Airlock in observe mode (ADR-005)
- AutoMecanik-specific constraints enforced by policy

However, **no clear rule existed** defining:
- which agents may be activated
- under what conditions
- in which execution zone

This ADR establishes the **Phase 1 activation perimeter**.

---

## Decision

### Phase 1 Scope

Only agents satisfying **ALL** of the following are eligible:

1. **Verdict**
   - `APPROVED`
   - or `APPROVED_WITH_CONDITIONS`

2. **Output Type**
   - `report_only`
   - `bundle_only`
   - `rpc_only (observe only)`

3. **No Direct Write Access**
   - No Git write access
   - No vault write access
   - No prod deployment capability

4. **Placement Decision Section**
   - Agent fiche MUST include a valid `Placement Decision`
   - Missing section = NOT ACTIVABLE

---

### Authorized Zones per Agent Type

| Agent Type | Allowed Zone |
|-----------|-------------|
| Analysis / Audit | external |
| Code Generation | external |
| Bundle Producers | external |
| Backend Internal Services | principal_vps |
| Monitoring / Observability | principal_vps |
| AI-COS L1 / L2 | NOT ALLOWED |
| PROD Runtime | FORBIDDEN |

---

### Explicitly Forbidden in Phase 1

- AI-COS Executive Agents (Level 1)
- AI-COS Leads (Level 2)
- Any agent with:
  - `write_target = monorepo`
  - `write_target = governance-vault`
  - `output = deploy`
  - autonomous decision authority

---

## Enforcement Rules

- Any agent activation MUST:
  1. Be listed in REG-001
  2. Have an approved fiche
  3. Respect placement rules
  4. Pass Airlock when applicable

- Violations result in:
  - automatic rejection
  - audit-trail entry
  - agent deactivation

---

## Consequences

### Positive
- Clear, enforceable activation boundary
- No ambiguity about agent placement
- Safe scaling of agent ecosystem
- Zero-trust preserved

### Negative
- Slower activation of AI-COS agents
- Additional documentation overhead

This is **intentional and accepted**.

---

## Exit Criteria (Phase 1 to Phase 2)

Transition to Phase 2 requires:
1. 14 days stable operation
2. Zero Airlock violations
3. Review of rejected bundles
4. New ADR explicitly authorizing Phase 2

---

## References

- ADR-002 Airlock Zero-Trust
- ADR-005 Airlock Observe Mode
- REG-001 Agent Registry
- constraints.auto-automecanik.json

---

_Created: 2026-02-03_
_Author: Claude (Governance Analyst)_
