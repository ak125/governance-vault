---
id: VERIF-HEALTH-{YYYY-MM-DD}-{SEQUENCE}
date: {YYYY-MM-DD}
time: "{HH:mm:ssZ}"
type: health-check
status: passed | failed | degraded
author: "@cron" | "@manual"
trigger: cron | manual
environment: production
---

# Health Check: {YYYY-MM-DD HH:mm}

## Overall Status: {PASSED | DEGRADED | FAILED}

## Service Health

| Service | Status | Latency | Details |
|---------|--------|---------|---------|
| API | ✅/❌ | Xms | OK |
| Database | ✅/❌ | Xms | Pool: X/Y |
| Redis | ✅/❌ | Xms | Memory: XMB |
| RPC Gate | ✅/❌ | - | mode/level, X blocks |

## RPC Gate Metrics

| Metric | Value | Baseline | Delta |
|--------|-------|----------|-------|
| mode | enforce | enforce | - |
| enforceLevel | P2 | P2 | - |
| allowlistSize | X | 154 | +/- X |
| denylistP0Size | X | 7 | +/- X |
| denylistP1Size | X | 17 | +/- X |
| denylistP2Size | X | 40 | +/- X |
| totalBlocks | X | 0 | +/- X |

## Verification Commands

```bash
# Reproduce this health check
curl -s https://www.automecanik.com/health | jq '.status'
curl -s https://www.automecanik.com/health/rpc-gate | jq '{mode, enforceLevel, totalBlocks}'

# Compare with baseline
curl -s https://www.automecanik.com/health/rpc-gate | jq '{
  allowlistSize,
  denylistP2Size,
  totalBlocks,
  diff_allowlist: (.allowlistSize - 154),
  diff_denylist: (.denylistP2Size - 40)
}'
```

## Alerts

- None

---

*Captured: {timestamp}*
*Baseline: 2026-02-03_p2-enforce-baseline.md*
