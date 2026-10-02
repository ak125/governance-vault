---
id: VERIF-CI-{YYYY-MM-DD}-{run_id}-{attempt}
type: verification
date: {YYYY-MM-DD}
time: "{HH:mm:ssZ}"
status: partial
author: "{collector_or_operator}"
scope: single_workflow_run
environment: not_verified
repository: "{owner/repo}"
workflow: "{expected_workflow_name}"
commit: "{full_expected_sha}"
run_id: {github_run_id}
attempt: {github_run_attempt}
source_sha256: "{collector_source_sha256}"
related: []
---

# CI Run Verification: {commit_short}

This is a template, not evidence. Replace every placeholder before review.
`status` starts as `partial`; never promote it from a caller-declared status.

## Collection

From a dedicated governance-vault checkout (clone or worktree), collect a pinned
GitHub run:

```bash
python3 _scripts/capture_verification.py \
  --repo '{owner/repo}' --run-id '{run_id}' --attempt '{attempt}' \
  --commit '{full_expected_sha}' --workflow '{expected_workflow_name}'
```

The helper is read-only and emits JSON on stdout. Keep its exit code and JSON,
including `expected`, `collected_at`, `not_verified`, and, when available,
`source` and `source_sha256`. Invalid command-line arguments return exit 2 with
usage/error text on stderr, without a JSON report; preserve that outcome as
invalid input, not a successful collection.
It neither creates a vault document nor publishes it. It retrieves metadata,
not logs or arbitrary extra fields, using the official `gh run view --json` CLI.

- Exit 0 / `passed`: the requested identity matches, the run is completed and
  successful, and every returned job is completed and successful (non-empty list).
- Exit 1 / `failed`: the run or a job has a failure conclusion.
- Exit 2 / `insufficient_evidence`: arguments, identity, transport, or payload are
  invalid. Do not convert this into `passed`; retain the failure reason.
- Exit 3 / `partial`: incomplete, skipped, neutral, unknown, or absent results.

The SHA-256 covers the projected `source` object serialized with Python
`json.dumps(sort_keys=True, separators=(',', ':'), ensure_ascii=True)` in UTF-8.
It identifies the captured metadata; it is not a GitHub signature or an attestation
that a later rerun has the same result.

## Observed jobs

Copy actual jobs from `source.jobs`; never invent a fixed lint/typecheck/build list.

| Job ID | Actual name | Execution status | Conclusion | Source URL |
|--------|-------------|------------------|------------|------------|
| {job_id} | {name} | {status} | {conclusion} | {job_url} |

## Scope and limitations

- Verified: repository, run ID, attempt, expected full commit SHA, workflow name,
  and returned run/job metadata at collection time.
- Not verified: required branch checks, other workflows, local uncommitted files,
  deployment, PREPROD/PROD runtime health, log contents or test assertions.
- A successful job may contain ignored tests or tolerated step failures. This
  report does not count or certify individual tests; inspect their evidence
  separately before making a claim about them.
- A green run alone does not authorize merge or deployment.
- Health, RPC, deployment and monthly reports are not supported by this collector.
- The retired `_scripts/evidence-pack.sh` and `_scripts/gov` were removed by
  [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]]. Do not restore or invoke
  them. Evidence packs are assembled manually under [[MOC-Compliance]].

## Archival (explicit, separate action)

Follow [[ADR-015-vault-single-source-of-truth]] and the vault's `AGENTS.md`:
successful `_scripts/preflight-write.sh`, dedicated branch, new audit document in
`ledger/audit-trail/`, linked from a MOC or INDEX, signed commit and PR under the
required checks. Follow ADR-102/G4: an agent prepares; a human merges. Collection
is not authorization to archive, publish, merge or deploy.
Use a fresh filename including date, run ID and attempt; never overwrite an
earlier observation. Keep the exact collection JSON alongside the report in the
vault. No archival in the application's `.local/` directory and no CI writes.

## References

- Workflow: [Observed run]({github_run_url})
- Commit: [{sha_short}]({commit_url})
- [GitHub CLI documentation](https://cli.github.com/manual/gh_run_view)
- MOC: [[MOC-AuditTrail]]

*Observed at: {collector_collected_at_UTC} — not a deployment attestation.*
