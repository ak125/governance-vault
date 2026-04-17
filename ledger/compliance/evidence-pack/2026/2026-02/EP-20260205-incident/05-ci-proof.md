# 05 — CI Proof

**Generated**: 2026-02-05T01:59:58Z
**Scope**: incident
**Updated**: 2026-03-07

## Required evidence
- CI status for merges to `main` during this period
- Proof that CI enforces Airlock bundle association (DEC-006)

## Notes / Attachments

- **Repository**: https://github.com/ak125/governance-vault
- **CI Pipeline**: GitHub Actions (self-hosted runner on production server)
- **Airlock Mode**: observe (ADR-005) — upgraded to enforce (ADR-010)

### PR / Commit Evidence (Feb 2026)
- Governance vault initialized: commits 2026-02-03 to 2026-02-06
- 7 bundles submitted and reviewed (all REJECTED — see `04-audit-trail/bundles/`)
- ADR-001 through ADR-010 accepted during this period

### CI Enforcement
- Lint + TypeCheck gates active on main branch
- Docker build pipeline: `massdoc/nestjs-remix-monorepo:production`
- No bypass detected during period

> This section is intentionally manual or link-based to avoid exporting tokens/logs that may contain secrets.
