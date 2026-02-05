# Security Audit Report: OpenClaw VPS Hardening

**Date:** 2026-02-05
**Auditor:** Claude (automated security agent)
**Target:** VPS OpenClaw (46.225.55.16)
**Status:** ✅ FIXES APPLIED

---

## Executive Summary

Security audit and hardening of the OpenClaw VPS hosting AI agents with Chromium browser integration. All P1 issues have been remediated.

---

## 1. Issues Identified

| ID | Issue | Severity | Status |
|----|-------|----------|--------|
| R1 | monorepo-read writable from container | P1 | ✅ FIXED |
| R2 | governance-read writable from container | P1 | ✅ FIXED |
| R3 | UFW firewall disabled | P1 | ✅ FIXED |
| R4 | Browser running as root | P1 | ✅ FIXED |
| R5 | SYS_ADMIN capability on browser | P1 | ✅ FIXED |
| R6 | --remote-allow-origins=* too permissive | P1 | ✅ FIXED |
| R7 | Metadata endpoint accessible | P2 | ✅ FIXED |

---

## 2. Fixes Applied

### 2.1 Filesystem Hardening

**docker-compose.yml changes:**
```yaml
# Gateway service - read-only mounts added
volumes:
  - ${OPENCLAW_WORKSPACE_DIR}/monorepo-read:/home/node/.openclaw/workspace/monorepo-read:ro
  - ${OPENCLAW_WORKSPACE_DIR}/governance-read:/home/node/.openclaw/workspace/governance-read:ro
```

**Validation:**
```
Write to monorepo-read: BLOCKED ✅
Write to governance-read: BLOCKED ✅
Write to agent-submissions: ALLOWED ✅
```

### 2.2 Browser Container Hardening

**Before:**
```yaml
cap_add:
  - SYS_ADMIN
user: root
```

**After:**
```yaml
cap_drop:
  - ALL
# No cap_add
user: "65534:65534"  # nobody:nogroup
read_only: true
security_opt:
  - no-new-privileges:true
tmpfs:
  - /tmp:rw,noexec,nosuid,size=512m
  - /var/tmp:rw,noexec,nosuid,size=256m
ulimits:
  nofile: { soft: 65535, hard: 65535 }
  nproc: { soft: 512, hard: 512 }
```

**Validation:**
```
User: nobody (65534) ✅
Capabilities: 0x0000000000000000 (NONE) ✅
Filesystem: read-only ✅
```

### 2.3 Network Hardening

**UFW enabled:**
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 443/tcp
ufw enable
```

**iptables rules added:**
```bash
# Block metadata endpoint
iptables -I DOCKER-USER -s 172.30.0.0/24 -d 169.254.169.254 -j DROP
# Block LAN access
iptables -I DOCKER-USER -s 172.30.0.10 -d 10.0.0.0/8 -j DROP
iptables -I DOCKER-USER -s 172.30.0.10 -d 192.168.0.0/16 -j DROP
```

**Validation:**
```
Browser -> Internet: BLOCKED ✅
Browser -> Metadata: BLOCKED ✅
Browser -> LAN: BLOCKED ✅
Gateway -> Browser: OK ✅
```

### 2.4 Chromium Entrypoint Hardening

**Removed:**
- `--remote-allow-origins=*`

**Kept (required for operation):**
- `--no-sandbox` (compensated by Docker isolation)
- `--headless=new`
- `--disable-dev-shm-usage`

---

## 3. Current Security Posture

### Container Isolation
| Measure | Status |
|---------|--------|
| Non-root user (65534) | ✅ |
| Zero capabilities | ✅ |
| no-new-privileges | ✅ |
| Read-only filesystem | ✅ |
| tmpfs noexec,nosuid | ✅ |

### Network Isolation
| Measure | Status |
|---------|--------|
| Docker internal network | ✅ |
| No internet access | ✅ |
| Metadata blocked | ✅ |
| LAN blocked | ✅ |
| UFW active | ✅ |

### Git/Push Protection
| Measure | Status |
|---------|--------|
| monorepo-read: no remote | ✅ |
| governance-vault: read-only key | ✅ |
| agent-submissions: write allowed | ✅ |

---

## 4. Residual Risks (Accepted)

| Risk | Mitigation | Acceptance |
|------|------------|------------|
| Chromium --no-sandbox | Docker isolation compensates | ✅ Acceptable |
| Claude API keys in env | Inherent to operation | ✅ Acceptable |
| Public Gateway (443) | Token required + UFW | ✅ Acceptable |

---

## 5. Files Modified

| File | Change |
|------|--------|
| `/opt/openclaw/docker-compose.yml` | Read-only mounts, browser hardening |
| `/opt/openclaw/browser-entrypoint-hardened.sh` | Removed --remote-allow-origins |
| `/etc/iptables/rules.v4` | Metadata + LAN blocking |
| `/etc/systemd/system/iptables-restore.service` | Persistence |
| UFW configuration | Enabled with minimal rules |

---

## 6. Validation Commands

```bash
# Verify read-only mounts
docker exec openclaw-gateway touch /home/node/.openclaw/workspace/monorepo-read/test
# Expected: Read-only file system

# Verify browser user
docker exec openclaw-browser id
# Expected: uid=65534(nobody) gid=65534(nogroup)

# Verify capabilities
docker exec openclaw-browser cat /proc/1/status | grep CapBnd
# Expected: 0000000000000000

# Verify network isolation
docker exec openclaw-browser curl -sf --max-time 3 https://google.com
# Expected: timeout/failure
```

---

## 7. Verdict

**PRODUCTION READY ✅**

All P1 security issues have been remediated. The architecture is now:
- Defensible in security audit
- Compliant with Zero-Trust principles
- Acceptable for production use with AI agents

---

## 8. Recommendations (Optional)

| Improvement | Priority | Status |
|-------------|----------|--------|
| Caddy IP whitelist | P2 | Pending |
| Rate limiting | P2 | Pending |
| Seccomp profile | P3 | Optional |
| Log monitoring | P3 | Optional |

---

*Report generated automatically by security audit agent.*
*No manual intervention required unless noted.*
