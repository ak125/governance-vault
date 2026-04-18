---
id: VERIF-CI-{YYYY-MM-DD}-{SEQUENCE}
date: {YYYY-MM-DD}
time: "{HH:mm:ssZ}"
type: ci-gate
status: passed | failed | warning
author: "@github-actions"
trigger: push | pr | workflow_dispatch
environment: preprod
commit: {sha}
run_id: {github_run_id}
related: []
---

# CI Gate Verification: {commit_short}

## Summary

| Job | Status | Duration |
|-----|--------|----------|
| lint | ✅/❌ | Xs |
| typecheck | ✅/❌ | Xm Ys |
| core-build | ✅/❌ | Xm Ys |
| import-firewall | ✅/❌ | Xs |
| rpc-gate-check | ✅/⚠️ | Xs |
| build | ✅/❌ | Xm Ys |

## Gate Details

### Lint
- Errors: X
- Warnings: X

### TypeCheck
- Errors: X
- Warnings: X

### Import Firewall
- Violations: X
- Blocked imports: `@repo/ai-orchestrator`, `@repo/contracts`

### RPC Gate Check
- Direct .rpc() files: X (bypass allowed: Y)
- New violations: X

## Verification Commands

```bash
# Reproduce this CI run
gh run view {run_id} --json jobs -q '.jobs[] | {name, conclusion}'

# Check specific job logs
gh run view {run_id} --log --job {job_id}
```

## References

- Workflow: [Link to run]({github_run_url})
- Commit: [{sha_short}]({commit_url})

---

*Generated: {timestamp}*
