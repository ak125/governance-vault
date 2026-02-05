#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# Evidence Pack Generator (DEC-013)
# Fail-closed, no secrets export
# -----------------------------

VAULT_DIR="${VAULT_DIR:-/opt/automecanik/governance-vault}"
AIRLOCK_DIR="${AIRLOCK_DIR:-/opt/automecanik/airlock}"
REPO_DIR="${REPO_DIR:-/opt/automecanik/app}"

SCOPE="${1:-monthly}"
DATE_UTC="${DATE_UTC:-$(date -u +%Y%m%d)}"
YEAR_UTC="${YEAR_UTC:-$(date -u +%Y)}"
YM_UTC="${YM_UTC:-$(date -u +%Y-%m)}"
NOW_ISO="${NOW_ISO:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"

PACK_DIR="$VAULT_DIR/06-compliance/evidence-pack/$YEAR_UTC/$YM_UTC/EP-${DATE_UTC}-${SCOPE}"

need(){ command -v "$1" >/dev/null 2>&1 || { echo "❌ Missing: $1" >&2; exit 1; }; }
need date; need mkdir; need cat; need printf; need find; need sort; need sed; need awk
need sha256sum

# Optional tools (used if present)
HAS_GIT=0; command -v git >/dev/null 2>&1 && HAS_GIT=1
HAS_GH=0;  command -v gh  >/dev/null 2>&1 && HAS_GH=1

fail_closed_checks(){
  [[ -d "$VAULT_DIR" ]] || { echo "❌ VAULT_DIR not found: $VAULT_DIR" >&2; exit 1; }
  [[ -d "$AIRLOCK_DIR" ]] || { echo "❌ AIRLOCK_DIR not found: $AIRLOCK_DIR" >&2; exit 1; }

  # Security sanity: never include inbox contents as authoritative evidence
  [[ -d "$AIRLOCK_DIR/processed" ]] || { echo "❌ Missing: $AIRLOCK_DIR/processed" >&2; exit 1; }
  [[ -d "$AIRLOCK_DIR/rejected"  ]] || { echo "❌ Missing: $AIRLOCK_DIR/rejected"  >&2; exit 1; }

  # Repo is optional for evidence pack (prefer not to require it), but if present we can capture commit refs
  if [[ -d "$REPO_DIR/.git" ]]; then :; fi
}

mkpack(){
  mkdir -p "$PACK_DIR"
  for f in 01-context.md 02-invariants.md 03-decisions.md 04-changes.md 05-ci-proof.md 06-audit-trail.md 07-incidents.md 08-security-controls.md 09-attestations.md; do
    [[ -f "$PACK_DIR/$f" ]] || : > "$PACK_DIR/$f"
  done
}

# Gather last N processed/rejected bundles as evidence references (not inbox)
list_bundles(){
  local dir="$1" label="$2" max="${3:-50}"
  printf "## %s\n\n" "$label"
  if [[ ! -d "$dir" ]]; then
    printf "_Missing directory: %s_\n\n" "$dir"
    return 0
  fi

  # Expect tamper-proof naming: YYYYMMDD__bundle__hash
  find "$dir" -mindepth 1 -maxdepth 1 -type d -printf "%f\n" \
    | sort -r \
    | head -n "$max" \
    | awk '{print "- " $0}'
  printf "\n"
}

# Try to reference audit-trail entries (expected location)
list_audit_trails(){
  local audit_root="$VAULT_DIR/04-audit-trail/bundles"
  printf "## Audit trail entries (recent)\n\n"
  if [[ ! -d "$audit_root" ]]; then
    printf "_Missing: %s_\n\n" "$audit_root"
    return 0
  fi
  find "$audit_root" -type f -name "*.md" -printf "%T@ %p\n" \
    | sort -nr \
    | head -n 50 \
    | awk '{ $1=""; sub(/^ /,""); print "- " $0 }'
  printf "\n"
}

# Incidents listing
list_incidents(){
  local inc_root="$VAULT_DIR/05-incidents"
  printf "## Incidents (recent)\n\n"
  if [[ ! -d "$inc_root" ]]; then
    printf "_Missing: %s_\n\n" "$inc_root"
    return 0
  fi
  find "$inc_root" -type f -name "*.md" -printf "%T@ %p\n" \
    | sort -nr \
    | head -n 50 \
    | awk '{ $1=""; sub(/^ /,""); print "- " $0 }'
  printf "\n"
}

# Decisions listing
list_decs(){
  local dec_root="$VAULT_DIR/02-decisions"
  printf "## Decisions in force\n\n"
  if [[ ! -d "$dec_root" ]]; then
    printf "_Missing: %s_\n\n" "$dec_root"
    return 0
  fi
  find "$dec_root" -type f -name "DEC-*.md" -printf "%f\n" \
    | sort \
    | awk '{print "- " $0}'
  printf "\n"
}

# CI proof: intentionally minimal (no secrets). If gh present, you can add a manual paste placeholder.
write_ci_proof(){
  cat > "$PACK_DIR/05-ci-proof.md" <<EOF
# 05 — CI Proof

**Generated**: ${NOW_ISO}
**Scope**: ${SCOPE}

## Required evidence
- CI status for merges to \`main\` during this period
- Proof that CI enforces Airlock bundle association (DEC-006)

## Notes / Attachments (paste links or summaries)
- PR links:
  - TODO
- Workflow runs:
  - TODO

> This section is intentionally manual or link-based to avoid exporting tokens/logs that may contain secrets.
EOF
}

# Security controls summary (static + references)
write_security_controls(){
  cat > "$PACK_DIR/08-security-controls.md" <<EOF
# 08 — Security Controls

**Generated**: ${NOW_ISO}

## Core controls (DEC-002 → DEC-013)
- Airlock physical isolation: \`${AIRLOCK_DIR}/inbox\` (agents write only)
- Bundles: BUNDLE-SPEC 5 files required
- Block symlinks / binaries / forbidden paths / rename-to-forbidden
- TOCTOU revalidation on accept
- Tamper-proof naming in \`processed/\` and \`rejected/\`
- Signature auto-detect (where enabled)
- GitHub Gate PREPROD (DEC-003)
- Kill-switch global (DEC-004)
- Rotation keys/secrets policy (DEC-005)
- CI proof required (DEC-006)
- Incident response & rollback (DEC-007)
- Read-only PROD (DEC-008)
- DR & backups (DEC-009)
- Least privilege (DEC-010)
- Monitoring (DEC-011)
- Third-party risk (DEC-012)
- Evidence packaging (DEC-013)

## Kill-switch status
- File: \`${AIRLOCK_DIR}/AIRLOCK_DISABLED\`
- Status: $( [[ -f "${AIRLOCK_DIR}/AIRLOCK_DISABLED" ]] && echo "ENABLED (Airlock halted)" || echo "NOT PRESENT (Airlock active)" )

EOF
}

# Context + invariants + changes + audit trail + attestations
write_context(){
  cat > "$PACK_DIR/01-context.md" <<EOF
# 01 — Context

**Evidence Pack**: EP-${DATE_UTC}-${SCOPE}
**Generated**: ${NOW_ISO}

## Scope
- Period: ${YM_UTC}
- Environment(s): DEV / PREPROD / PROD (as applicable)
- Objective: Provide verifiable compliance evidence for Airlock governance

## System roots
- VAULT_DIR: ${VAULT_DIR}
- AIRLOCK_DIR: ${AIRLOCK_DIR}
- REPO_DIR: ${REPO_DIR}

EOF
}

write_invariants(){
  cat > "$PACK_DIR/02-invariants.md" <<EOF
# 02 — Invariants (Summary)

**Generated**: ${NOW_ISO}

## Non-negotiable invariants
- Agents never access repo or \`.git\`
- Agents write only to \`${AIRLOCK_DIR}/inbox\`
- Bundles must pass validation (paths/patterns/budget/schema)
- Forbidden system paths and blast-radius files are blocked
- TOCTOU integrity check before accept
- PROD is read-only and cannot push/commit/build
- PREPROD is the only environment allowed to push to GitHub
- CI is mandatory with Airlock proof for merges/releases

EOF
}

write_decisions(){
  : > "$PACK_DIR/03-decisions.md"
  printf "# 03 — Decisions\n\n**Generated**: %s\n\n" "$NOW_ISO" >> "$PACK_DIR/03-decisions.md"
  list_decs >> "$PACK_DIR/03-decisions.md"
}

write_changes(){
  : > "$PACK_DIR/04-changes.md"
  printf "# 04 — Changes (Bundle References)\n\n**Generated**: %s\n\n" "$NOW_ISO" >> "$PACK_DIR/04-changes.md"
  list_bundles "$AIRLOCK_DIR/processed" "Processed bundles (recent)" 50 >> "$PACK_DIR/04-changes.md"
  list_bundles "$AIRLOCK_DIR/rejected"  "Rejected bundles (recent)" 50 >> "$PACK_DIR/04-changes.md"

  if [[ $HAS_GIT -eq 1 && -d "$REPO_DIR/.git" ]]; then
    printf "## Repo reference (optional)\n\n" >> "$PACK_DIR/04-changes.md"
    (cd "$REPO_DIR" && git log --oneline -n 30) \
      | sed 's/^/- /' \
      >> "$PACK_DIR/04-changes.md" || true
    printf "\n" >> "$PACK_DIR/04-changes.md"
  fi
}

write_audit_trail(){
  : > "$PACK_DIR/06-audit-trail.md"
  printf "# 06 — Audit Trail\n\n**Generated**: %s\n\n" "$NOW_ISO" >> "$PACK_DIR/06-audit-trail.md"
  list_audit_trails >> "$PACK_DIR/06-audit-trail.md"

  # Include airlock audit.log extract if present
  local audit_log="$AIRLOCK_DIR/audit.log"
  if [[ -f "$audit_log" ]]; then
    printf "## Airlock audit.log (recent)\n\n\`\`\`\n" >> "$PACK_DIR/06-audit-trail.md"
    tail -100 "$audit_log" >> "$PACK_DIR/06-audit-trail.md" 2>/dev/null || true
    printf "\`\`\`\n\n" >> "$PACK_DIR/06-audit-trail.md"
  fi
}

write_incidents(){
  : > "$PACK_DIR/07-incidents.md"
  printf "# 07 — Incidents\n\n**Generated**: %s\n\n" "$NOW_ISO" >> "$PACK_DIR/07-incidents.md"
  list_incidents >> "$PACK_DIR/07-incidents.md"

  # Include kill-switch and PROD violation events from audit.log
  local audit_log="$AIRLOCK_DIR/audit.log"
  if [[ -f "$audit_log" ]]; then
    printf "## Security events from audit.log\n\n" >> "$PACK_DIR/07-incidents.md"
    printf "### Kill-switch activations\n\`\`\`\n" >> "$PACK_DIR/07-incidents.md"
    grep "KILL_SWITCH" "$audit_log" 2>/dev/null | tail -20 >> "$PACK_DIR/07-incidents.md" || echo "(none)"
    printf "\`\`\`\n\n" >> "$PACK_DIR/07-incidents.md"
    printf "### PROD violation attempts\n\`\`\`\n" >> "$PACK_DIR/07-incidents.md"
    grep "PROD_READONLY" "$audit_log" 2>/dev/null | tail -20 >> "$PACK_DIR/07-incidents.md" || echo "(none)"
    printf "\`\`\`\n\n" >> "$PACK_DIR/07-incidents.md"
  fi
}

write_attestations(){
  cat > "$PACK_DIR/09-attestations.md" <<EOF
# 09 — Attestations

**Generated**: ${NOW_ISO}

## Human attestation (required for closure)
I attest that:
- This Evidence Pack reflects the system state for the declared scope.
- Airlock invariants were enforced (fail-closed) during this period.
- Any incidents were recorded and handled according to DEC-007.
- PROD remained read-only (DEC-008), and PREPROD GitHub Gate was respected (DEC-003).

**Name**: ____________________
**Role**: ____________________
**Date**: ____________________
**Signature**: _______________

EOF
}

# Produce a manifest with hashes of the evidence pack files (tamper-evident)
write_pack_manifest(){
  local mf="$PACK_DIR/manifest.sha256"
  (cd "$PACK_DIR" && sha256sum *.md > "$mf")
}

main(){
  fail_closed_checks
  mkpack

  write_context
  write_invariants
  write_decisions
  write_changes
  write_ci_proof
  write_audit_trail
  write_incidents
  write_security_controls
  write_attestations
  write_pack_manifest

  echo "✅ Evidence Pack created: $PACK_DIR"
  echo "ℹ️  Hash manifest: $PACK_DIR/manifest.sha256"
}

main "$@"
