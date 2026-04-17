# 08 — Security Controls

**Generated**: 2026-02-05T01:59:54Z

## Core controls (DEC-002 → DEC-013)
- Airlock physical isolation: `/opt/automecanik/airlock/inbox` (agents write only)
- Bundles: BUNDLE-SPEC 5 files required
- Block symlinks / binaries / forbidden paths / rename-to-forbidden
- TOCTOU revalidation on accept
- Tamper-proof naming in `processed/` and `rejected/`
- Signature auto-detect (where enabled)
- GitHub Gate PREPROD (DEC-003)
- Kill-switch global (DEC-004)
- Rotation keys/secrets policy (DEC-005)
- CI proof required (DEC-006)
- Incident response & rollback (DEC-007)
- Read-only PROD (DEC-008)
- DR & backups (DEC-009)
- Least privilege (DEC-010)
- Monitoring (DEC-011)
- Third-party risk (DEC-012)
- Evidence packaging (DEC-013)

## Kill-switch status
- File: `/opt/automecanik/airlock/AIRLOCK_DISABLED`
- Status: NOT PRESENT (Airlock active)

