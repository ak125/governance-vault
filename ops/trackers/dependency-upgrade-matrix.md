<!-- markdownlint-disable MD013 -->
---
id: TRACKER-DEPENDENCY-UPGRADE-MATRIX
title: Dependency Upgrade Matrix
status: active
version: 1.0.0
date: 2026-05-14
scope: monorepo-dependencies
authority: human
owner: "@fafa"
governed_by:
  - dependency-modernization-policy
related_adrs:
  - ADR-062
  - ADR-058
tags:
  - tracker
  - dependencies
  - operations
---

# Dependency Upgrade Matrix

> Operational tracker governed by [[dependency-modernization-policy]]. One row per dependency. **Never edit a row without filling §4 of the policy.** Append new rows when introducing a dependency in the same PR.

## How to read this file

- **risk-tier** : `high-risk` / `runtime-critical` / `tooling` (cf. policy §3)
- **current-version** : declared range or pinned override from `package.json` / `overrides` at last review (e.g. `^5.9.3`, `3.3.0`). Lockfile-resolved value is captured in the upgrade PR commit, not in this matrix.
- **target-version** : `—` if no planned upgrade
- **status** : `not-planned` / `proposed` / `in-flight` / `landed` / `rolled-back`
- **owner** : single accountable GitHub handle
- **last-reviewed** : ISO date of last manual reconciliation against the declared ranges in `package.json` manifests (root + `backend/` + `frontend/` + `packages/*`)

## Matrix — High-risk tier

| Dependency | risk-tier | current-version | target-version | semver-bump | reason | expected-gain | rollback-plan | test-evidence | pr-link | owner | status | last-reviewed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `node` (engines) | high-risk | `>=22.0.0` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `typescript` | high-risk | `^5.9.3` (root + `overrides`) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@nestjs/core` | high-risk | `^10.4.20` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@nestjs/common` | high-risk | `^10.0.0` (backend) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@remix-run/express` | high-risk | `^2.17.4` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@remix-run/node` | high-risk | `^2.17.4` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@remix-run/react` | high-risk | `^2.17.4` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@remix-run/serve` | high-risk | `^2.17.4` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@remix-run/server-runtime` | high-risk | `^2.17.4` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@supabase/supabase-js` | high-risk | `^2.95.0` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `zod` (overrides-pinned) | high-risk | `^3.25.76` (root override) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `path-to-regexp` (overrides-pinned) | high-risk | `3.3.0` (root override) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `handlebars` (overrides-pinned) | high-risk | `4.7.9` (root override) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |

## Matrix — Runtime-critical tier

| Dependency | risk-tier | current-version | target-version | semver-bump | reason | expected-gain | rollback-plan | test-evidence | pr-link | owner | status | last-reviewed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ioredis` | runtime-critical | `^5.8.2` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `connect-redis` | runtime-critical | `^5.2.0` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `express-session` | runtime-critical | `^1.17.3` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `passport` | runtime-critical | `^0.7.0` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `passport-jwt` | runtime-critical | `^4.0.1` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `passport-local` | runtime-critical | `^1.0.0` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `bcrypt` | runtime-critical | `^6.0.0` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@nestjs/passport` | runtime-critical | `^10.0.3` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@nestjs/jwt` | runtime-critical | `^11.0.1` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `bullmq` | runtime-critical | `^5.63.0` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `bull` (legacy, dual support) | runtime-critical | `^4.16.5` | retire | major (removal) | dual queue coexists with bullmq | smaller bundle | revert PR | — | — | @fafa | not-planned | 2026-05-14 |
| `@nestjs/bullmq` | runtime-critical | `^11.0.4` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@anthropic-ai/sdk` | runtime-critical | `^0.71.0` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |

## Matrix — Tooling tier

| Dependency | risk-tier | current-version | target-version | semver-bump | reason | expected-gain | rollback-plan | test-evidence | pr-link | owner | status | last-reviewed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `turbo` | tooling | `^2.9.12` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `eslint` | tooling | `^8.57.1` (root) / `^8.0.0` (workspaces) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `prettier` | tooling | `^3.8.3` | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `jest` | tooling | `^29.5.0` (backend) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `vitest` | tooling | `^4.0.2` (frontend) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `@playwright/test` | tooling | `^1.59.1` (frontend) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `dependency-cruiser` | tooling | `17.4.0` (pinned) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `madge` | tooling | `8.0.0` (pinned) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `knip` | tooling | `6.12.2` (pinned) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |
| `ast-grep` | tooling | `0.42.2` (pinned) | — | — | — | — | — | — | — | @fafa | not-planned | 2026-05-14 |

## Reconciliation procedure

Every 30 days OR on every dep-touching PR:

1. Read declared ranges from each manifest (root, backend, frontend, `packages/*`) — see snippet below.
2. Diff each declared range against the matrix `current-version` column. Any mismatch (the range moved in a manifest) → update the column + bump `last-reviewed`.
3. If a row is missing (a new dep landed without matrix entry) → file a back-fill PR and tag the original PR author.
4. Run [[dependency-modernization-policy]] §5 decision rules on any row whose `target-version` differs from `current-version`.

Snippet for step 1 (read-only manifest sweep):

```bash
for f in package.json backend/package.json frontend/package.json packages/*/package.json; do
  jq '{file:"'"$f"'", deps:(.dependencies // {}), devDeps:(.devDependencies // {}), overrides:(.overrides // {})}' "$f"
done
```

Lockfile-resolved values (`npm ls --depth=0 --json`) are reconciled inside each upgrade PR, not in this tracker — that keeps the matrix at the governance layer (declared intent) and lets the lockfile be the operational layer (resolved reality).

## Open questions tracked here (not in policy)

- Should `tooling` deps still emit a notification when `@playwright/test` minor bumps land via grouped Dependabot? — [Open, owner @fafa]
- Storybook ecosystem grouping incident 2026-05-04 → consider explicit ratchet for `@storybook/*` (currently dev-only, classified `tooling`). — [Open, owner @fafa]
<!-- markdownlint-enable MD013 -->
