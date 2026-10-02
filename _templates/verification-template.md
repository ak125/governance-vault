---
id: VERIF-{TYPE}-{YYYY-MM-DD}-{SEQUENCE}
type: verification
date: {YYYY-MM-DD}
time: "{HH:mm:ssZ}"
status: partial
author: "{actual_collector_or_operator}"
trigger: "{actual_trigger}"
environment: "{observed_environment_or_not_verified}"
commit: "{full_expected_sha_or_not_verified}"
related:
  - {ADR-XXX}
  - {INC-YYYY-MM-DD}
---

# {Title}

This is an unverified template. Select `passed`, `failed`, `warning`, `partial`
or `insufficient_evidence` only from observed evidence; never default to success.
An unavailable check is not a successful check. A caller-supplied status or a
printed reproduction command does not prove that a check ran.

## Context

{Why this verification was performed; exact target, expected result and scope}

## Checks Performed

| Check | Observed status | Value | Expected | Evidence and collection time |
|-------|-----------------|-------|----------|------------------------------|
| {check} | {actual_status_or_not_verified} | {observed_value} | {expected} | {source} |

## Summary

- **Executed checks**: {count}
- **Passed**: {count}
- **Failed**: {count}
- **Warnings**: {count}
- **Unverified / incomplete**: {count_and_reasons}

Use `not_verified` for unknown counts, not an invented zero. Keep verification
status distinct from authorization to publish, merge or deploy.

## Verification Commands

```bash
# Record the actual command, its exit code, output and UTC observation time.
{command}
```

For CI, use [[ci-gate-template]] and the vault's read-only
`_scripts/capture_verification.py` helper. A CI observation does not prove
deployment or runtime health. Preserve missing evidence explicitly.

## Actions Required

- [ ] {action1}
- [ ] {action2}

## Related Documents

- `{related_doc}` (remplacer par wikilink réel: `[[stem-du-document]]`)
- MOC: [[MOC-AuditTrail]]

---

*Observed: {timestamp_UTC}; coverage: {verified_scope_and_exclusions}*
*Author: {author}*
