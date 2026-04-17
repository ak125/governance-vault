---
id: ADR-010
title: Airlock Enforce Mode Activation & CI as Final Authority
status: accepted
date: 2026-02-04
decision_makers:
  - Architecture Team
  - Security Team
version: 1.0.0
supersedes: ADR-005 (observe mode)
---

# ADR-010: Airlock Enforce Mode Activation

## Context

Airlock has been in **observe mode** since 2026-02-03 (ADR-005). Exit criteria met:
- 7+ days observation completed
- RPC metrics analyzed
- Zero critical false positives
- 140 agents formalized, 9 ADRs

## Decision

### 1. Transition to Enforce Mode

| Environment | Mode | Level |
|-------------|------|-------|
| DEV | observe | - |
| PREPROD | enforce | P1 |
| PROD | enforce | P2 |

### 2. Enforcement Rules

| Level | Functions | Policy |
|-------|-----------|--------|
| P0 | 7 critical | BLOCK_ALL |
| P1 | 17 high-risk | SERVICE_ROLE_ONLY |
| P2 | 40 medium-risk | SERVICE_ROLE_ALLOWLIST |

### 3. CI as Final Authority

```yaml
deploy:
  needs: [build, lint, typecheck, governance-check]
```

### 4. Bundle Signatures (HMAC-SHA256)

```typescript
interface SignedBundle {
  envelope: JobEnvelope;
  signature: string;
  signedAt: ISO8601;
  signedBy: string;
}
```

## Consequences

- Hard enforcement on P0 functions
- CI blocks unauthorized changes
- Bundle integrity verified
- 10 attack vectors tested

## References

- ADR-002, ADR-005, ADR-009
- REG-001 v1.4.1

---
_Status: ACCEPTED_
