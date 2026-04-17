> **[ARCHIVED — ADR-011, 2026-03-07]** OpenClaw supprime. Voir ADR-011 pour details.

# ADR: DEC-OPENCLAW-CHROMIUM-NO-SANDBOX

## Architecture Decision Record

**ID:** DEC-OPENCLAW-CHROMIUM-NO-SANDBOX

**Date:** 2026-02-05

**Status:** ACCEPTED

**Decision Makers:** Security Review Team

---

## Context

OpenClaw requires a headless Chromium browser for web scraping and automation tasks performed by untrusted AI agents. Running Chromium inside Docker containers presents a security challenge: Chromium's built-in sandbox requires either `--privileged` mode or `SYS_ADMIN` capability, both of which significantly increase the attack surface.

### The Problem

| Option | Security Risk |
|--------|---------------|
| `--privileged` | Full host access - **UNACCEPTABLE** |
| `SYS_ADMIN` capability | Container escape risk - **HIGH RISK** |
| `--no-sandbox` | Chromium sandbox disabled - **REQUIRES COMPENSATION** |

### Constraints

- Agents are untrusted (may execute malicious prompts)
- Browser must be isolated from host and other services
- Configuration must be audit-defensible
- Production uptime requirements

---

## Decision

**We accept `--no-sandbox` with comprehensive Docker-level compensations.**

---

## Rationale

The Chromium sandbox provides process-level isolation within a single Linux namespace. When running inside a properly hardened Docker container, Docker itself provides equivalent (or stronger) isolation through:

- Linux namespaces (PID, NET, USER, MNT, IPC, UTS)
- cgroups for resource limiting
- seccomp syscall filtering
- Capability dropping
- Read-only filesystem

By removing `SYS_ADMIN` and applying defense-in-depth, we achieve isolation parity with Chromium's sandbox while eliminating container escape vectors.

---

## Implementation

### Compensation Measures Applied

| Layer | Measure | Purpose |
|-------|---------|---------|
| Capabilities | `cap_drop: ALL` + zero cap_add | No privileged operations |
| User | `user: 65534:65534` (nobody) | Non-root execution |
| Filesystem | `read_only: true` | No persistent modifications |
| Privileges | `no-new-privileges:true` | Block privilege escalation |
| Processes | `pids_limit: 512` | Prevent fork bombs |
| Files | `ulimit nofile: 65535` | Controlled file descriptors |
| Network | Internal Docker network | Isolated from external |
| Metadata | iptables DROP 169.254.169.254 | Block cloud metadata |
| Memory | `shm_size: 2gb` + tmpfs | Controlled shared memory |
| Temp | `tmpfs /tmp noexec,nosuid` | No executable temp files |

### Docker Compose Configuration

```yaml
browser:
  image: openclaw-sandbox-browser:bookworm-slim
  cap_drop:
    - ALL
  user: "65534:65534"
  read_only: true
  security_opt:
    - no-new-privileges:true
  tmpfs:
    - /tmp:rw,noexec,nosuid,size=512m,uid=65534,gid=65534
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
        pids: 512
  networks:
    openclaw_internal:
      ipv4_address: 172.30.0.10
```

### Chromium Flags

```bash
# REQUIRED for Docker
--no-sandbox
--disable-setuid-sandbox
--disable-dev-shm-usage

# SECURITY hardening
--disable-gpu
--disable-software-rasterizer
--disable-extensions
--disable-background-networking
--disable-sync
--no-first-run

# REMOVED (security risk)
# --remote-allow-origins=*  ← NEVER USE
```

---

## Consequences

### Positive

- ✅ No `SYS_ADMIN` capability required
- ✅ No `--privileged` mode
- ✅ Container escape risk minimized
- ✅ Audit-defensible configuration
- ✅ Defense-in-depth architecture

### Negative

- ⚠️ Relies on Docker isolation (must keep Docker updated)
- ⚠️ Chromium 0-day could compromise container (but not host)
- ⚠️ Slightly more complex configuration

### Residual Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Chromium 0-day exploit | MEDIUM | Docker isolation contains blast radius |
| Container escape via kernel bug | LOW | Keep kernel and Docker updated |
| Resource exhaustion | LOW | Strict limits enforced |

---

## Validation

### Tests Performed

```bash
# 1. Verify zero capabilities
docker exec browser cat /proc/1/status | grep CapEff
# Expected: 0000000000000000

# 2. Verify non-root user
docker exec browser whoami
# Expected: nobody

# 3. Verify read-only filesystem
docker exec browser touch /test 2>&1
# Expected: Read-only file system

# 4. Verify network isolation
docker exec browser curl -s --max-time 2 http://169.254.169.254
# Expected: timeout/blocked

# 5. Verify browser functional
curl http://localhost:19222/json/version
# Expected: Chromium version JSON
```

**All Tests:** ✅ PASSED

---

## Alternatives Considered

| Alternative | Verdict | Reason |
|-------------|---------|--------|
| Keep SYS_ADMIN | REJECTED | Container escape risk too high |
| Use --privileged | REJECTED | Equivalent to root on host |
| Use gVisor/Kata | DEFERRED | Added complexity, consider for future |
| External browser service | REJECTED | Data leaves trusted perimeter |
| Native sandbox on host | REJECTED | No isolation from other services |

---

## References

- [Chromium Sandbox Design](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/design/sandbox.md)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Running Chromium in Docker](https://github.com/nickstenning/docker-chromium)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Security Lead | _______________ | 2026-02-__ | _______ |
| DevOps Lead | _______________ | 2026-02-__ | _______ |
| Project Owner | _______________ | 2026-02-__ | _______ |

---

**Decision Status:** ACCEPTED

**Implementation Status:** COMPLETE

**Production Ready:** YES
