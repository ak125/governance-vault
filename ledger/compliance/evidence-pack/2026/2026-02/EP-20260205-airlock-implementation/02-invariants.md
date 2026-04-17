---
type: invariants
---

# Invariants (DEC-002 → DEC-013)

## Airlock Invariants (DEC-002)
- [ ] All bundles processed through /opt/automecanik/airlock/inbox
- [ ] No bundles inside repository
- [ ] Symlink detection active
- [ ] Blast radius files protected
- [ ] TOCTOU protection active

## Environment Invariants
- [ ] DEV: validate/accept allowed, push blocked (DEC-003)
- [ ] PREPROD: push allowed (DEC-003)
- [ ] PROD: read-only enforced (DEC-008)

## Kill-Switch (DEC-004)
- [ ] AIRLOCK_DISABLED file checked on all operations
- [ ] No bypass possible

## Observability (DEC-011)
- [ ] audit.log captures all events
- [ ] Timestamp, env, user, action, bundle, outcome logged
