---
id: BUNDLE-REG
title: Agent Bundle Registry
status: active
version: 1.0.0
last_updated: 2026-02-04
signature_algorithm: HMAC-SHA256
---

# Agent Bundle Registry

Official registry for tracking all agent-submitted bundles in the AutoMecanik system.

## Quick Reference

| Field | Description |
|-------|-------------|
| **Signature Algorithm** | HMAC-SHA256 |
| **Verification Script** | `tools/governance/verify-bundle-signature.sh` |
| **Required Fields** | envelope, signature, signedAt, signedBy |
| **Governance ADR** | ADR-010 |

---

## Bundle Structure

### SignedBundle Schema

```typescript
interface SignedBundle {
  envelope: JobEnvelope;
  signature: string;        // HMAC-SHA256(envelope, secret)
  signedAt: ISO8601;
  signedBy: string;         // agent_id
  validUntil?: ISO8601;     // Optional expiry
}

interface JobEnvelope {
  job_id: string;           // Unique bundle ID
  agent_id: string;         // Source agent
  intent: string;           // Purpose (SEO_AUDIT, CODE_FIX, etc.)
  scope: string[];          // Affected paths
  timestamp: ISO8601;
  metadata?: Record<string, unknown>;
}
```

---

## Bundle Lifecycle

```
┌─────────────────┐
│  Agent Creates  │
│     Bundle      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Sign Bundle    │
│  (HMAC-SHA256)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Submit to      │
│  Airlock        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CI Validates   │◄──── governance-check job
│  Signature      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 VALID     INVALID
    │         │
    ▼         ▼
┌───────┐ ┌────────┐
│ MERGE │ │ REJECT │
└───────┘ └────────┘
```

---

## Registry Table

| bundle_id | agent_id | timestamp | intent | signature_status | merge_status |
|-----------|----------|-----------|--------|------------------|--------------|
| *(empty - bundles will be logged here)* | | | | | |

### Status Values

**signature_status:**
- `valid` - Signature verified
- `invalid` - Signature mismatch
- `missing` - No signature present
- `expired` - Bundle past validUntil

**merge_status:**
- `pending` - Awaiting review
- `merged` - Successfully merged
- `rejected` - Rejected (signature or policy violation)

---

## Authorized Bundle Producers

Per REG-001 v2.1.0, only these agents may produce bundles:

| agent_id | output_type | verdict |
|----------|-------------|---------|
| dev | bundle | APPROVED_WITH_CONDITIONS |
| f0_autoimport | bundle | APPROVED_WITH_CONDITIONS |
| f1_dead_code_surgeon | bundle | APPROVED_WITH_CONDITIONS |

---

## Verification Commands

```bash
# Verify a bundle signature
./tools/governance/verify-bundle-signature.sh bundle.json

# Verify from stdin
cat bundle.json | ./tools/governance/verify-bundle-signature.sh /dev/stdin

# In CI (requires BUNDLE_HMAC_KEY secret)
BUNDLE_HMAC_KEY=${{ secrets.BUNDLE_HMAC_KEY }} \
  ./tools/governance/verify-bundle-signature.sh bundle.json
```

---

## Security Requirements

1. **HMAC Key Management**
   - Key stored in GitHub Secrets (`BUNDLE_HMAC_KEY`)
   - Key rotated quarterly
   - Different keys per environment (dev/preprod/prod)

2. **Bundle Constraints**
   - Max 500 lines changed
   - Max 10 files modified
   - No forbidden patterns (exec_sql, secrets, etc.)
   - Must pass CI governance-check

3. **Audit Trail**
   - All bundles logged in this registry
   - Rejected bundles include reason
   - Signature failures trigger alert

---

## References

- ADR-010: Airlock Enforce Mode & CI Authority
- ADR-002: Zero-Trust Agents
- REG-001: Agent Registry v1.4.1
- `tools/governance/verify-bundle-signature.sh`

---

_Registry Version: 1.0.0_
_Last Updated: 2026-02-04_
_Maintainer: Governance Team_
