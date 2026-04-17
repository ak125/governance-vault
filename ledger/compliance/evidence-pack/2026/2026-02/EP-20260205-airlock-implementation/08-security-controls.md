---
type: security-controls
---

# Security Controls

## Kill-Switch Status (DEC-004)
- File: /opt/automecanik/airlock/AIRLOCK_DISABLED
- Status: Inactive

## PROD Read-Only (DEC-008)
- Enforcement: Active in all scripts
- Violations: 1

## Access Control (DEC-010)
- [ ] Agents: inbox write only
- [ ] DEV: validate/accept only
- [ ] PREPROD: push allowed
- [ ] PROD: read-only

## Third-Party Controls (DEC-012)
- [ ] No direct repo access for external services
- [ ] All IA access via Airlock
