---
id: BUNDLE-SPEC
version: 1.0.0
status: active
date: 2026-02-04
scope: airlock-bundles
authority: human
---

# Airlock Bundle Spec v1 (Machine-Verifiable Contract)

## Purpose
A bundle is the ONLY accepted format for agent-proposed changes.
Agents are NON-TRUSTED (ADR-002). A bundle is "candidate-only" until accepted by Airlock + CI + Human.

## Directory Layout (bundle root)
bundle/
  manifest.json
  constraints.json
  changes.patch
  evidence.json
  report.md

## Hard Rules (MUST / MUST NOT)

### MUST
- MUST include all 5 files listed above.
- MUST validate against JSON schema `bundle.schema.v1.json` for:
  - `manifest.json`
  - `constraints.json`
  - `evidence.json`
- MUST be patch-applicable (unified diff) with `git apply --check`.
- MUST contain only text files (no binaries).
- MUST declare explicit scope via `constraints.json`.
- MUST include audit evidence in `evidence.json` (even if minimal).

### MUST NOT
- MUST NOT modify canonical truth or governance sources by default:
  - `.spec/00-canon/**` (unless an approved ADR explicitly allows)
  - `governance-vault/**` (unless an approved ADR explicitly allows)
- MUST NOT contain secrets or credential material.
- MUST NOT propose direct `.rpc(` or `exec_sql(` calls unless explicitly allowed by constraints profile.
- MUST NOT include commands that the agent expects to be executed automatically.

## File Contracts

### 1) manifest.json
Declares bundle identity, intent, and exact included artefacts.

Required fields:
- bundle_id (string, unique)
- created_at (ISO8601 string)
- author (string) e.g. "claude-api"
- target_repo (string) e.g. "nestjs-remix-monorepo"
- title (string)
- summary (string)
- files (array of included filenames with sha256)
- patch (object: path + sha256)

### 2) constraints.json
Defines what the bundle is allowed to touch and what is forbidden.

Required fields:
- profile: "default" | "auto-automecanik" | custom
- allowed_paths: glob[]
- forbidden_paths: glob[]
- forbidden_patterns: regex/string[]
- diff_budget: max_files, max_lines, max_additions, max_deletions
- flags:
  - no_canon_change: boolean (default true)
  - no_vault_change: boolean (default true)
  - no_exec_sql_change: boolean (default true)

### 3) changes.patch
Unified diff patch. MUST be applicable.
- MUST include file paths relative to repo root
- MUST NOT include binary diffs

### 4) evidence.json
Machine-verifiable claims, not free-form promises.

Required fields:
- checks: array of checks with status + proof
- scanned_for_secrets: { tool, status, proof }
- forbidden_patterns_scan: { status, matches[] }
- patch_apply_check: { status, proof }
- diff_stats: { files_changed, lines_added, lines_deleted }
Optional:
- lint, typecheck, tests (if available)

### 5) report.md
Human-readable explanation.
- MUST contain: scope, risk, reasoning, what changed, how to rollback.

## Standard Airlock Flow (contractual)
Agent → Bundle → Airlock Import → CI Validation → Human Review → Merge

Airlock Import MUST:
1) Validate structure + schema
2) Validate scope (paths, patterns, budgets)
3) Validate patch applicability
4) Create isolated branch + apply patch
5) Run checks (lint/typecheck/build/tests as configured)
6) If pass → create PR with bundle metadata attached

## Failure Behavior
If any gate fails, Airlock MUST:
- reject bundle (no repo write to main)
- emit structured rejection reason (gate + rule + evidence)

## Versioning
- Spec changes require a governance decision (ADR).
- Bundles MUST declare spec version `1.0.0` in manifest.
