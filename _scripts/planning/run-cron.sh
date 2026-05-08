#!/usr/bin/env bash
# Cron entry pour Planning Live sync (ADR-053).
# Invoqué par /etc/cron.d/planning-live (cf. Task 2.9).
# Lock via flock pour éviter runs concurrents (équivalent `concurrency: vault-write` GHA).
set -euo pipefail

VAULT_PATH="/opt/automecanik/governance-vault"
LOCK_FILE="/var/lock/automecanik/planning-live-sync.lock"
LOG_DIR="/var/log/governance-vault"
LOG_FILE="${LOG_DIR}/planning-sync.log"
ENV_FILE="/etc/automecanik/planning.env"
VENV_DIR="/opt/automecanik/.venvs/planning-live"

# Flag DRY_RUN (read-only smoke test) : génère hash + items count, pas de write/commit/push.
# Usage : DRY_RUN=1 /opt/automecanik/governance-vault/_scripts/planning/run-cron.sh
DRY_RUN="${DRY_RUN:-0}"

mkdir -p "${LOG_DIR}"

# Source secrets (PAPERCLIP_API_*, PLANNING_WEBHOOK_URL) si présents — sinon alerts.py
# tombera en best-effort silencieux (cf. I5).
if [ -f "${ENV_FILE}" ]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

# Activate dedicated venv (provisionned in Task 2.9 Step 0 — provisioning is one-shot)
if [ ! -d "${VENV_DIR}" ]; then
  echo "[$(date -u +%FT%TZ)] ERROR: venv missing at ${VENV_DIR}. Run Task 2.9 Step 0 to provision."
  exit 1
fi
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# Mask secrets dans tout output potentiel (équivalent ::add-mask:: GHA)
mask_secrets() {
  sed -E 's/(Bearer\s+)[A-Za-z0-9_-]+/\1***REDACTED***/g; s/(token=)[A-Za-z0-9_-]+/\1***REDACTED***/g'
}

run_sync() {
  cd "${VAULT_PATH}"

  # DRY_RUN early exit : invoque l'orchestrator avec --dry-run, AUCUN write/commit/push.
  if [ "${DRY_RUN}" = "1" ]; then
    echo "[$(date -u +%FT%TZ)] DRY_RUN=1 — read-only smoke test, no git ops"
    python3 -m _scripts.planning.sync_planning --vault-path "${VAULT_PATH}" --dry-run
    return 0
  fi

  # Pull latest main avant sync (idempotence cross-runs)
  git fetch origin main --quiet
  git reset --hard origin/main --quiet

  # Run orchestrator
  python3 -m _scripts.planning.sync_planning --vault-path "${VAULT_PATH}"

  # Stage potential changes
  git add ops/moc/MOC-Planning-Live.md ledger/snapshots/planning/

  if [ -z "$(git status --porcelain ops/moc/MOC-Planning-Live.md ledger/snapshots/planning/)" ]; then
    echo "[$(date -u +%FT%TZ)] No changes to commit"
    return 0
  fi

  # Detect business vs technical (I3 convention)
  if git diff --staged --quiet -- ops/moc/MOC-Planning-Live.md; then
    MSG="chore(planning): snapshot only [no-moc-change]"
  else
    HASH=$(grep -oP '(?<=^semantic_hash: )\S+' ops/moc/MOC-Planning-Live.md || echo "unknown")
    MSG="chore(planning): business update [hash:${HASH}]"
  fi

  # Commit signé G3 (config global VPS deploy user a déjà user.signingkey + commit.gpgsign=true)
  git commit -S -m "${MSG}"

  # Push (deploy user a déjà SSH key authorized sur ak125/governance-vault)
  if ! git push origin main 2>&1 | mask_secrets; then
    echo "[$(date -u +%FT%TZ)] ERROR: git push failed — manual intervention required"
    return 1
  fi

  echo "[$(date -u +%FT%TZ)] OK: ${MSG}"
}

# Lock + run + report Supabase
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "[$(date -u +%FT%TZ)] Another planning-sync run is in progress, skipping."
  exit 0
fi

STATUS="ok"
START_TS=$(date +%s)
{
  if ! run_sync 2>&1 | mask_secrets | tee -a "${LOG_FILE}"; then
    STATUS="error"
  fi
} || STATUS="error"
END_TS=$(date +%s)
DURATION=$((END_TS - START_TS))

# Report to Supabase __cron_runs (canon pattern)
LIB="/opt/automecanik/app/scripts/cron/lib-supabase-report.sh"
if [ -f "${LIB}" ]; then
  # shellcheck disable=SC1090
  source "${LIB}"
  report_cron_run \
    --routine "planning-live-sync" \
    --status "${STATUS}" \
    --duration "${DURATION}" \
    --message "$(tail -n 1 "${LOG_FILE}" | mask_secrets)"
fi

[ "${STATUS}" = "ok" ] || exit 1
