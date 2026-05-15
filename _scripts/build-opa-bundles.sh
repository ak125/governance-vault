#!/usr/bin/env bash
# =============================================================================
# build-opa-bundles.sh — Compile Rego policies to WASM bundles
# =============================================================================
#
# Génère pour chaque policy déclarée :
#   - dist/policies/<name>.bundle.tar.gz  (bundle OPA complet)
#   - dist/policies/<name>.wasm            (WASM extrait pour embed monorepo)
#
# Usage :
#   ./_scripts/build-opa-bundles.sh           # build all declared policies
#   ./_scripts/build-opa-bundles.sh r2-content-write   # build single policy
#
# Reproductibilité SHA-256 : opa version doit être pinned (cf workflow
# `.github/workflows/opa-policy-build.yml` env OPA_VERSION).
#
# Source : ADR-066 (R2) + PR-V (H1) + futures policies invariants only.
# =============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POLICIES_DIR="${REPO_ROOT}/policies/seo-content"
DIST_DIR="${REPO_ROOT}/dist/policies"
BUILD_OUT="${BUILD_OUT:-/tmp/opa-build-out}"

# Resolve `opa` binary : PATH first, then /tmp/opa fallback (local dev).
OPA_BIN="$(command -v opa 2>/dev/null || echo /tmp/opa)"
if [ ! -x "$OPA_BIN" ]; then
  echo "::error::opa binary not found in PATH nor /tmp/opa"
  echo "Install via: curl -sL -o /tmp/opa https://openpolicyagent.org/downloads/v0.69.0/opa_linux_amd64_static && chmod +x /tmp/opa"
  exit 1
fi

# ── Policy registry ──────────────────────────────────────────────────────────
#
# Each entry : "<name>|<rego_file>|<entrypoint1>,<entrypoint2>,..."
# Entrypoints sont les rules Rego que le monorepo va évaluer (allow + deny).

POLICIES=(
  "h1-write|h1-write.rego|seo/content/h1/write/allow,seo/content/h1/write/deny"
  "r2-content-write|r2-content-write.rego|seo/content/r2/write/allow,seo/content/r2/write/deny"
  "r2-cluster-health|r2-cluster-health.rego|seo/content/r2/cluster_health/cluster_healthy,seo/content/r2/cluster_health/cluster_pollution_detected,seo/content/r2/cluster_health/deny_collision,seo/content/r2/cluster_health/deny_canonical_chain,seo/content/r2/cluster_health/deny_reasons"
)

# ── Filtering : single policy build if argument provided ─────────────────────

FILTER="${1:-}"

build_one() {
  local name="$1"
  local rego_file="$2"
  local entrypoints_csv="$3"

  # Path RELATIVE to REPO_ROOT for reproducibility — opa embeds source paths
  # in the WASM debug section, so absolute paths produce different bytes than
  # relative paths. Workflow uses relative paths from vault root.
  local rego_rel="policies/seo-content/${rego_file}"
  local rego_path="${REPO_ROOT}/${rego_rel}"
  if [ ! -f "$rego_path" ]; then
    echo "::error::Policy file missing: ${rego_path}"
    return 1
  fi

  echo ""
  echo "━━━ Building ${name} ━━━"
  echo "Source     : ${rego_rel}"
  echo "Entrypoints: ${entrypoints_csv}"

  mkdir -p "$BUILD_OUT" "$DIST_DIR"

  # Build args : -e <entrypoint> per entrypoint
  local opa_args=()
  IFS=',' read -ra entrypoints <<<"$entrypoints_csv"
  for ep in "${entrypoints[@]}"; do
    opa_args+=(-e "$ep")
  done

  local bundle_path="${BUILD_OUT}/${name}.bundle.tar.gz"
  local wasm_path="${BUILD_OUT}/${name}.wasm"

  # Run from REPO_ROOT to use relative rego_rel path (reproducibility).
  ( cd "$REPO_ROOT" && "$OPA_BIN" build \
    -t wasm \
    "${opa_args[@]}" \
    -o "$bundle_path" \
    "$rego_rel" )

  # Extract policy.wasm from bundle for direct embed monorepo
  rm -f "${BUILD_OUT}/policy.wasm"
  tar -xzf "$bundle_path" -C "$BUILD_OUT" /policy.wasm
  mv "${BUILD_OUT}/policy.wasm" "$wasm_path"

  # Commit to dist/policies/
  cp "$bundle_path" "${DIST_DIR}/${name}.bundle.tar.gz"
  cp "$wasm_path" "${DIST_DIR}/${name}.wasm"

  local sha
  sha=$(sha256sum "$wasm_path" | cut -d' ' -f1)
  echo "✓ ${name}.wasm  SHA-256: ${sha}"
  echo "  Bundle: ${DIST_DIR}/${name}.bundle.tar.gz"
  echo "  WASM  : ${DIST_DIR}/${name}.wasm"
}

# ── Main ─────────────────────────────────────────────────────────────────────

echo "OPA binary : $OPA_BIN"
"$OPA_BIN" version | head -2
echo ""
echo "Policies dir : ${POLICIES_DIR}"
echo "Dist dir     : ${DIST_DIR}"

built_count=0
for entry in "${POLICIES[@]}"; do
  IFS='|' read -r name rego_file entrypoints_csv <<<"$entry"
  if [ -n "$FILTER" ] && [ "$FILTER" != "$name" ]; then
    continue
  fi
  build_one "$name" "$rego_file" "$entrypoints_csv"
  built_count=$((built_count + 1))
done

if [ "$built_count" -eq 0 ]; then
  echo "::warning::No policy matched filter '${FILTER}'"
  echo "Available: $(printf '%s\n' "${POLICIES[@]}" | cut -d'|' -f1 | tr '\n' ' ')"
  exit 1
fi

echo ""
echo "━━━ Build summary ━━━"
echo "Built ${built_count} policy bundle(s) in ${DIST_DIR}"
ls -la "$DIST_DIR"
