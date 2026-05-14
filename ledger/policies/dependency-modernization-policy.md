---
id: POLICY-DEPENDENCY-MODERNIZATION
title: Dependency Modernization Policy
status: proposed
version: 1.0.0
date: 2026-05-14
scope: monorepo-dependencies
authority: human
owner: "@fafa"
related_adrs:
  - ADR-062  # Repository Contract System (meta-canon)
  - ADR-058  # Repository Control Plane (Layer 1/2/3 registry)
  - ADR-060  # Repository roles doctrine
  - ADR-061  # Workspace governance
related_rules:
  - rules-engineering-quality
  - rules-governance-process
related_trackers:
  - dependency-upgrade-matrix
tags:
  - policy
  - dependencies
  - governance
  - supply-chain
  - security
---

# Dependency Modernization Policy

## 1. Purpose

Codify **when and how** monorepo dependencies (Node, TypeScript, NestJS, Remix, Supabase, Redis client, session/auth stack, payment libs, tooling) may be upgraded. The policy is the governance layer **above** the operational tracker [[dependency-upgrade-matrix]] and **inside** the meta-framework of [[ADR-062-repository-contract-system-meta-model]].

This policy does **not** trigger any upgrade. It defines the gate every upgrade must pass.

## 2. Scope

All Node-resolvable dependencies declared in:

- `/opt/automecanik/app/package.json` (root + `overrides`)
- `/opt/automecanik/app/backend/package.json`
- `/opt/automecanik/app/frontend/package.json`
- `/opt/automecanik/app/packages/**/package.json`

Out of scope (separate policies apply): system packages on the VPS, Docker base images, CI runner images, GitHub Actions versions, Supabase platform features.

## 3. Classification (criticality tiers)

Every dependency MUST be classified in exactly one of three tiers in [[dependency-upgrade-matrix]].

| Tier | Examples | Upgrade gate |
|------|----------|--------------|
| **high-risk** — runtime kernel | `node`, `typescript`, `@nestjs/core`, `@nestjs/common`, `@remix-run/*`, `@supabase/supabase-js` | ADR required + 6-stage pattern (ADR-062 §1-6) + 2 reviewers + staging soak ≥ 72 h |
| **runtime-critical** — production path | `ioredis`, `connect-redis`, `express-session`, `passport`, `passport-jwt`, `passport-local`, `bcrypt`, `@nestjs/jwt`, `@nestjs/passport`, `bullmq`, `bull`, payment HMAC modules, `@anthropic-ai/sdk` | Risk note + rollback rehearsal documented + 1 reviewer + staging soak ≥ 24 h |
| **tooling** — developer experience | `turbo`, `eslint`, `prettier`, `jest`, `vitest`, `@playwright/test`, `dependency-cruiser`, `madge`, `knip`, `ast-grep`, type definitions (`@types/*`) | Standard PR review, no soak |

**Edge cases :**

- A dep used **both** at runtime and in scripts is classified by its **runtime** role.
- A dep listed in `overrides` (e.g. `zod ^3.25.76`, `path-to-regexp 3.3.0`, `handlebars 4.7.9`) is **high-risk by default** because changes propagate to every workspace.
- Adding a new dep MUST add a matrix row in the same PR.

## 4. Decision template (required fields per upgrade)

Every upgrade PR (or matrix row update) MUST answer all required fields below. Missing field = blocking comment, not a stylistic nit.

| Field | Required content |
|-------|------------------|
| `owner` | GitHub handle accountable end-to-end (not "team"). |
| `risk-level` | `high-risk` / `runtime-critical` / `tooling` per §3. |
| `current-version` | Declared range or pinned override from `package.json` / `overrides` at last review (e.g. `^5.9.3`, `3.3.0`). Lockfile-resolved value is captured in the upgrade PR commit, not in this field. |
| `target-version` | Exact target including pre-release qualifier. |
| `semver-bump` | `patch` / `minor` / `major`. |
| `reason` | Concrete trigger: CVE id, performance regression measured, deprecated API, new feature required by ADR-NNN. No "stay current". |
| `expected-gain` | Quantified where possible (ms saved, MB reduced, CVE closed). |
| `rollback-plan` | Exact `git revert` + `npm ci` commands, or image tag for Docker-level rollback. |
| `test-evidence` | Link to passing CI run, perf bench output, e2e screenshot, or staging soak log. |
| `pr-link` | GitHub PR URL. |
| `status` | `not-planned` / `proposed` / `in-flight` / `landed` / `rolled-back`. |

## 5. Decision rules (before considering an upgrade)

Rules are AND-composed. All must hold.

1. **Existence check :** the dep is already in [[dependency-upgrade-matrix]]. If not → first PR adds the row with `status: not-planned`.
2. **Contract impact :** if the upgrade may invalidate any contract shipped under ADR-062 series (`architecture.yaml`, `db.yaml`, future `rpc.yaml` / `runtime-topology.yaml` / `workers.yaml`), the contract update lands **in the same PR** or a precondition PR — never in a follow-up. Anti-parallel-truth (ADR-062 §9).
3. **Supply chain signal :** consult OpenSSF Scorecard and OSV/CVE before bumping. Score < 5 or unresolved CVE on the target version → BLOCK.
4. **SemVer integrity :** a `major` bump in a high-risk tier dep requires an ADR. A `minor` bump in a high-risk tier dep requires a 24 h soak. A `patch` bump in any tier is fast-track.
5. **N-LTS Node window :** Node target stays within `current` or `current - 1` LTS (today: 22 LTS → 24 LTS allowed; 20 LTS retiring). Stale LTS = ADR + 6-month deprecation window.
6. **Provenance preference :** when the publisher offers npm provenance attestations (npm ≥ 9.5), prefer provenance-attested versions.
7. **Lockfile integrity :** `package-lock.json` must commit alongside any `package.json` change. No floating ranges promoted without lock update.
8. **No feature flag for upgrades :** an upgrade either lands cleanly or is rolled back. No "shadow upgrade behind a flag".
9. **Freshness gate inheritance :** if the dep is referenced by a contract under audit `freshness` window, the upgrade PR must refresh the generated artifact in the same commit.
10. **Dependabot alignment :** if `.github/dependabot.yml` ignores the major (currently: `react`, `react-dom`, `@nestjs/*`, `@remix-run/*`), bypassing the ignore requires explicit ADR exception comment in the PR.

## 6. Promotion ladder (this policy's own lifecycle)

Aligned with ADR-062 §5 (promotion gate):

- `status: proposed` at PR open (this PR).
- → `status: accepted` only after ≥ 1 real upgrade landed cleanly under the policy AND `vault-governance.yml` green for ≥ 3 consecutive runs on `main`.
- → `status: canon` only after the policy has gated ≥ 5 upgrades without incident.
- Any future change to §3 (tiers) or §4 (fields) requires an ADR amending this policy. Editorial fixes (typos, links) bypass via standard PR.

## 7. Anti-patterns (explicit refusals)

These behaviors are bricolage and rejected at review:

- "Stay-current bump" without §4 `reason` → BLOCK.
- Editing `package.json` without updating [[dependency-upgrade-matrix]] in same PR → BLOCK.
- Cumul-go: one "fais le" interpreted as license to upgrade multiple deps → BLOCK.
- Rollback via force-push or `--amend` on `main` → BLOCK; use revert PR.
- Hardcoded version strings in skill/agent/ADR markdown → BLOCK; source is `package.json` + this matrix.
- "Temporary" downgrade left in `overrides` past 14 days → BLOCK; either land the fix or roll back the upgrade.

## 8. Industry frameworks referenced (not duplicated)

This policy is the local doctrine layered on existing standards. We do not reinvent them.

- **OpenSSF Scorecard** — supply chain hygiene metric.
- **OSV.dev** — vulnerability database queried before any upgrade.
- **CycloneDX** — SBOM format expected when an SBOM is requested.
- **SemVer 2.0.0** — version interpretation contract.
- **npm provenance** (Sigstore-backed) — preferred publisher signal.
- **SLSA v1.0** — supply-chain levels used to grade target versions when relevant.
- **Conventional Commits** — upgrade PRs use `chore(deps):` or `feat(deps):` prefix.

## 9. References

- [[ADR-062-repository-contract-system-meta-model]] (meta-canon, Laws A/B, 6-stage pattern)
- [[ADR-058-repository-control-plane]] (Layer 1/2/3 registry that any dep upgrade may dirty)
- [[ADR-060-repository-roles-doctrine]] (which repo owns what)
- [[ADR-061-workspace-governance]] (mini-monorepo anti-pattern, applies to dep boundaries)
- [[rules-engineering-quality]] (review discipline)
- [[dependency-upgrade-matrix]] (operational tracker)
- `.github/dependabot.yml` — operational counterpart (weekly schedule, max 5 PRs, react/nestjs/remix majors frozen).

## 10. Out of scope

- Docker base image upgrades → separate policy (TODO).
- GitHub Actions version pinning → existing `99-meta/ci-policy.md`.
- System packages on the VPS → infra runbooks under `ops/runbooks/`.
- Supabase platform / extension upgrades → ADR-049 (DB Governance).
