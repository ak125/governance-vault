---
id: VERIF-{TYPE}-{YYYY-MM-DD}-{SEQUENCE}
type: verification
date: {YYYY-MM-DD}
time: "{HH:mm:ssZ}"
status: passed | failed | warning | partial
author: "@github-actions" | "@cron" | "@manual"
trigger: push | pr | cron | manual | deploy
environment: dev | preprod | production
commit: {sha}
related:
  - {ADR-XXX}
  - {INC-YYYY-MM-DD}
---

# {Title}

## Context

{Why this verification was performed}

## Checks Performed

| Check | Status | Value | Expected | Details |
|-------|--------|-------|----------|---------|
| {check1} | PASS | {value} | {expected} | {details} |
| {check2} | FAIL | {value} | {expected} | {details} |
| {check3} | WARN | {value} | {expected} | {details} |

## Summary

- **Total checks**: X
- **Passed**: X
- **Failed**: X
- **Warnings**: X

## Verification Commands

```bash
# Command to reproduce this verification
{command}
```

## Actions Required

- [ ] {action1}
- [ ] {action2}

## Related Documents

- `{related_doc}` (remplacer par wikilink réel: `[[stem-du-document]]`)
- MOC: [[MOC-AuditTrail]]

---

*Verified: {timestamp}*
*Author: {author}*
