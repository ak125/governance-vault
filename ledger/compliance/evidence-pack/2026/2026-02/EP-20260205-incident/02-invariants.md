# 02 — Invariants (Summary)

**Generated**: 2026-02-05T01:59:58Z

## Non-negotiable invariants
- Agents never access repo or `.git`
- Agents write only to `/opt/automecanik/airlock/inbox`
- Bundles must pass validation (paths/patterns/budget/schema)
- Forbidden system paths and blast-radius files are blocked
- TOCTOU integrity check before accept
- PROD is read-only and cannot push/commit/build
- PREPROD is the only environment allowed to push to GitHub
- CI is mandatory with Airlock proof for merges/releases

