#!/usr/bin/env bash
# weekly-lint.sh — Orchestrateur du lint hebdomadaire du governance-vault (ADR-020).
#
# Chaine :
#   1. check-orphans.sh              (G2 — Zero Orphelin, existant)
#   2. check-broken-links.sh         (wikilinks cassés, existant)
#   3. check-v1-paths.sh             (ADR-015 drift, existant)
#   4. check-vault-pollution.sh      (ADR-060 §1A invariant 5, ajouté par #267)
#   Les signatures G3 ne sont pas contrôlées ici : _scripts/check-signatures.sh les vérifie
#   sur chaque PR (workflow vault-governance) et au pre-push.
#   5. check-frontmatter-schema.py   (nouveau — conformité YAML)
#   6. check-adr-supersedes.py       (nouveau — chaînes supersedes)
#   7. check-obsolete-rules.py       (nouveau — status deprecated sans replacement)
#   8. check-canon-backlinks.py      (nouveau — G1 drift cross-canon)
#   9. check-moc-integrity.py        (nouveau — invariants structurels MOC, anti-drift PR-3)
#  10. check-canon-freshness.py      (nouveau — fichiers .spec/00-canon/ stales vs REG-002 thresholds, ADR-048 sprint 1)
#  11. check-canon-cross-repo.py     (nouveau — vault ADRs/MOCs refs vers monorepo .spec/00-canon/, ADR-048 sprint 3 axe transverse)
#  12. test_governance_constants.py  (parité enums constants ↔ schemas, PR-2)
#  13. check-no-direct-schema-enum-access.sh (PR-2)
#  8, 10 et 11 sont « skipped » (visible dans le rapport) quand --monorepo n'existe pas, ce qui est le cas en CI.
#
# Un check moderne qui plante (pas de JSON exploitable sur stdout) produit un finding
# `weekly-lint/check-crashed` de severite error ; un check legacy est jugé sur son vrai code de sortie.
#
# N'écrit JAMAIS dans le vault (exception : check-orphans.sh réécrit 99-meta/orphans-report.md
# quand il trouve des orphelins). Produit :
#   - findings.json   (agrégat structure par check)
#   - report.md       (résumé humain-readable pour issue GitHub)
#
# Exit 0 toujours — on n'échoue pas le workflow, on remonte les findings via issue.
#
# Usage :
#   _scripts/weekly-lint.sh --output findings.json --markdown report.md [--monorepo PATH]
#
# ADR-022 scope note (2026-04-23) :
#   Les schemas `_scripts/schemas/vehicle-{model,variations,role-map}.schema.json`
#   s'appliquent aux fichiers du monorepo `rag/knowledge/vehicles/**` et NON au vault.
#   Leur enforcement est délégué au workflow monorepo `.github/workflows/rag-vehicle-lint.yml`
#   (CI sur chaque PR modifiant ces fichiers), PAS à weekly-vault-lint — évite la
#   duplication de gate.
#   Si un fichier vehicle-* apparait accidentellement dans le vault, check-orphans
#   le flagguera (G2) et check-frontmatter-schema.py ne le classifiera pas
#   (classify() ne match aucun pattern vehicle → skip silencieux, non-bloquant).

set -euo pipefail

OUTPUT_JSON=""
OUTPUT_MD=""
MONOREPO_PATH="${MONOREPO_PATH:-/opt/automecanik/app}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) OUTPUT_JSON="$2"; shift 2 ;;
    --markdown) OUTPUT_MD="$2"; shift 2 ;;
    --monorepo) MONOREPO_PATH="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$OUTPUT_JSON" || -z "$OUTPUT_MD" ]]; then
  echo "Usage: $0 --output findings.json --markdown report.md [--monorepo PATH]" >&2
  exit 2
fi

VAULT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$VAULT_ROOT"

find_python() {
  for candidate in python3 py python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" -c "import sys; sys.exit(0 if sys.version_info[0]>=3 else 1)" >/dev/null 2>&1; then
        echo "$candidate"; return 0
      fi
    fi
  done
  return 1
}
PY_BIN="$(find_python || true)"
if [[ -z "$PY_BIN" ]]; then
  echo "Error: Python 3 required" >&2; exit 2
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

RUN_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
RUN_DATE="$(date -u +%Y-%m-%d)"

# --- Legacy checks (bash, parse stdout) ---

LEGACY_RESULTS="$TMP_DIR/legacy.jsonl"
: > "$LEGACY_RESULTS"

run_legacy() {
  local name="$1"; local cmd="$2"; local exit_meaning="$3"
  local out rc
  # `out="$(... || true)"; rc=$?` donnait toujours rc=0 : un echec n'etait jamais remonte.
  if out="$($cmd 2>&1)"; then rc=0; else rc=$?; fi
  $PY_BIN -c "
import json, sys
print(json.dumps({
    'check': sys.argv[1],
    'exit_code': int(sys.argv[2]),
    'status': 'fail' if int(sys.argv[2]) != 0 else 'pass',
    'exit_meaning': sys.argv[3],
    'output': sys.argv[4][:8000],
}))
" "$name" "$rc" "$exit_meaning" "$out" >> "$LEGACY_RESULTS"
}

run_legacy "orphans"          "_scripts/check-orphans.sh ."          "exit1=orphans found" || true
run_legacy "broken-links"     "_scripts/check-broken-links.sh ."     "exit1=broken wikilinks" || true
run_legacy "v1-paths"         "_scripts/check-v1-paths.sh ."         "exit1=v1 paths found" || true
run_legacy "vault-pollution"  "_scripts/check-vault-pollution.sh ."  "exit1=operational sections detected (ADR-060 §1A inv. 5)" || true

# --- Modern checks (Python, JSON native) ---

MODERN_RESULTS="$TMP_DIR/modern.jsonl"
: > "$MODERN_RESULTS"

run_modern() {
  local name="$1"; shift
  local out rc errfile="$TMP_DIR/$name.stderr"
  # stderr a part : melange a stdout, le moindre message rendait le JSON illisible.
  if out="$("$@" --json 2>"$errfile")"; then rc=0; else rc=$?; fi
  # Un check qui ne produit pas de JSON a plante : c'est une erreur, jamais un « 0 finding ».
  $PY_BIN -c "
import json, sys
name, raw, rc, errfile = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
try:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError('JSON root is not an object')
except Exception as e:
    try:
        err_lines = open(errfile, encoding='utf-8', errors='replace').read().strip().splitlines()
    except OSError:
        err_lines = []
    stderr_tail = ' | '.join(err_lines[-3:])
    data = {
        'check': name,
        'findings': [{
            'severity': 'error',
            'file': '_scripts',
            'message': f'check crashed (exit {rc}, no usable JSON: {e}) stderr: {stderr_tail}'[:600],
            'rule': 'weekly-lint/check-crashed',
        }],
        'summary': {'error': 1, 'warning': 0, 'info': 0},
        'parse_error': str(e),
    }
print(json.dumps(data))
" "$name" "$out" "$rc" "$errfile" >> "$MODERN_RESULTS"
}

run_modern "frontmatter-schema" $PY_BIN _scripts/check-frontmatter-schema.py .
run_modern "adr-supersedes"     $PY_BIN _scripts/check-adr-supersedes.py .
run_modern "obsolete-rules"     $PY_BIN _scripts/check-obsolete-rules.py .
run_modern "moc-integrity"      $PY_BIN _scripts/check-moc-integrity.py .

# Parité enums constants ↔ schemas (PR-2 SoT invariant).
PARITY_OUT="$($PY_BIN -m unittest discover -v -s _scripts -p 'test_governance_constants.py' 2>&1 || true)"
if echo "$PARITY_OUT" | grep -q "^OK"; then
  echo '{"check":"governance-constants-parity","findings":[],"summary":{"error":0,"warning":0,"info":0}}' >> "$MODERN_RESULTS"
else
  PARITY_MSG="$(echo "$PARITY_OUT" | tail -3 | head -1 | tr -d '"' | head -c 200)"
  echo "{\"check\":\"governance-constants-parity\",\"findings\":[{\"severity\":\"error\",\"file\":\"_scripts/governance_constants.py\",\"message\":\"drift vs _scripts/schemas/*.schema.json: ${PARITY_MSG}\",\"rule\":\"governance/constants-parity\"}],\"summary\":{\"error\":1,\"warning\":0,\"info\":0}}" >> "$MODERN_RESULTS"
fi

# No-direct-schema-enum-access guard (PR-2 invariant).
NDS_OUT="$(_scripts/check-no-direct-schema-enum-access.sh 2>&1 || true)"
if echo "$NDS_OUT" | grep -q "^OK:"; then
  echo '{"check":"no-direct-schema-enum-access","findings":[],"summary":{"error":0,"warning":0,"info":0}}' >> "$MODERN_RESULTS"
else
  NDS_MSG="$(echo "$NDS_OUT" | tail -1 | tr -d '"' | head -c 200)"
  echo "{\"check\":\"no-direct-schema-enum-access\",\"findings\":[{\"severity\":\"error\",\"file\":\"_scripts\",\"message\":\"${NDS_MSG}\",\"rule\":\"governance/no-direct-schema-enum-access\"}],\"summary\":{\"error\":1,\"warning\":0,\"info\":0}}" >> "$MODERN_RESULTS"
fi

if [[ -d "$MONOREPO_PATH/.spec/00-canon" ]]; then
  run_modern "canon-backlinks" $PY_BIN _scripts/check-canon-backlinks.py . --monorepo "$MONOREPO_PATH"
  run_modern "canon-freshness" $PY_BIN _scripts/check-canon-freshness.py . --monorepo "$MONOREPO_PATH"
  run_modern "canon-cross-repo" $PY_BIN _scripts/check-canon-cross-repo.py . --monorepo "$MONOREPO_PATH"
else
  echo '{"check": "canon-backlinks", "findings": [], "summary": {"error":0,"warning":0,"info":0}, "skipped": "monorepo path not available in this environment"}' >> "$MODERN_RESULTS"
  echo '{"check": "canon-freshness", "findings": [], "summary": {"error":0,"warning":0,"info":0}, "skipped": "monorepo path not available in this environment"}' >> "$MODERN_RESULTS"
  echo '{"check": "canon-cross-repo", "findings": [], "summary": {"error":0,"warning":0,"info":0}, "skipped": "monorepo path not available in this environment"}' >> "$MODERN_RESULTS"
fi

# --- Aggregate ---

$PY_BIN - "$LEGACY_RESULTS" "$MODERN_RESULTS" "$OUTPUT_JSON" "$OUTPUT_MD" "$RUN_TS" "$RUN_DATE" <<'PY'
import json, sys
from pathlib import Path

legacy_path, modern_path, out_json, out_md, run_ts, run_date = sys.argv[1:7]

legacy = [json.loads(l) for l in open(legacy_path).read().splitlines() if l.strip()]
modern = [json.loads(l) for l in open(modern_path).read().splitlines() if l.strip()]

total_error = 0
total_warning = 0
total_info = 0

for m in modern:
    s = m.get("summary", {})
    total_error += s.get("error", 0)
    total_warning += s.get("warning", 0)
    total_info += s.get("info", 0)

legacy_fails = [l for l in legacy if l.get("status") == "fail"]

aggregate = {
    "run_id": run_ts,
    "run_date": run_date,
    "legacy_checks": legacy,
    "modern_checks": modern,
    "totals": {
        "error": total_error,
        "warning": total_warning,
        "info": total_info,
        "legacy_failures": len(legacy_fails),
    },
}

Path(out_json).write_text(json.dumps(aggregate, indent=2, ensure_ascii=False))

md = []
md.append(f"# Weekly Governance Lint — {run_date}")
md.append("")
md.append(f"**Run:** {run_ts}  ")
md.append(f"**Errors:** {total_error} &nbsp; **Warnings:** {total_warning} &nbsp; **Info:** {total_info} &nbsp; **Legacy failures:** {len(legacy_fails)}")
md.append("")
md.append("## Summary")
md.append("")
md.append("| Check | Errors | Warnings | Info | Status |")
md.append("|-------|-------:|---------:|-----:|:------:|")
for m in modern:
    s = m.get("summary", {})
    name = m.get("check", "?")
    if m.get("skipped"):
        md.append(f"| `{name}` | - | - | - | skipped ({m.get('skipped')}) |")
    else:
        status = ":red_circle:" if s.get("error", 0) else (":yellow_circle:" if s.get("warning", 0) else ":green_circle:")
        md.append(f"| `{name}` | {s.get('error', 0)} | {s.get('warning', 0)} | {s.get('info', 0)} | {status} |")
for l in legacy:
    name = l.get("check", "?")
    status = ":red_circle:" if l.get("status") == "fail" else ":green_circle:"
    md.append(f"| `{name}` (legacy) | - | - | - | {status} |")
md.append("")

for m in modern:
    findings = m.get("findings", [])
    if not findings:
        continue
    md.append(f"## {m.get('check', '?')}")
    md.append("")
    for f in findings[:100]:
        sev = f.get("severity", "?").upper()
        md.append(f"- **[{sev}]** `{f.get('file', '?')}` — {f.get('message', '?')} _({f.get('rule', '?')})_")
    if len(findings) > 100:
        md.append(f"- _(+{len(findings) - 100} more — see findings.json artifact)_")
    md.append("")

if legacy_fails:
    md.append("## Legacy check failures")
    md.append("")
    for l in legacy_fails:
        md.append(f"### {l.get('check', '?')} (exit {l.get('exit_code', '?')})")
        md.append("")
        md.append("```")
        md.append(l.get("output", "")[:2000])
        md.append("```")
        md.append("")

md.append("---")
md.append("")
md.append("_Generated by `_scripts/weekly-lint.sh` — see [[ADR-020-weekly-vault-lint]] for governance._")

Path(out_md).write_text("\n".join(md))

print(f"OK: {total_error} error(s), {total_warning} warning(s), {total_info} info, {len(legacy_fails)} legacy fail(s)")
print(f"  JSON: {out_json}")
print(f"  MD:   {out_md}")
PY

exit 0
