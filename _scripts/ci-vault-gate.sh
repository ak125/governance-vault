#!/usr/bin/env bash
# ci-vault-gate.sh — Gate des PR du governance-vault : la « PR-4 » de la série
# « Vault Documentaire → Vault Exécutable » (couche L2 de 99-meta/governance-runtime-map.md).
#
# Sans ce gate, les checks de weekly-lint (ADR-020) ne tournaient qu'une fois par semaine,
# après la fusion : une PR pouvait casser un frontmatter, une chaîne supersedes ou un MOC
# en passant tous les checks requis.
#
# Mode `pr` (le seul implémenté) :
#   1. weekly-lint.sh --no-monorepo : les checks du vault seulement. Les trois checks
#      cross-repo (canon-*) lisent le monorepo, absent en CI, et deux d'entre eux dépendent
#      de la date : un verdict de PR ne doit dépendre que du contenu de la PR.
#   2. sync_moc_decisions.py --check : l'index auto-généré de MOC-Decisions correspond aux
#      frontmatters des ADR (la ligne « Dernier sync » est ignorée).
# Rouge si weekly-lint compte au moins une erreur ou un check legacy en échec, ou si l'index
# MOC-Decisions a dérivé. Les avertissements sont affichés, jamais bloquants.
#
# Pas encore implémentés (prévus par la carte runtime) : le mode `weekly` et l'issue `infra-fail`.
#
# Codes de sortie : 0 = vert ; 1 = findings bloquants ; 2 = usage, PyYAML absent, ou sortie
# d'un check absente ou illisible. Une sortie illisible n'est jamais lue comme un vert.
#
# Sous GitHub Actions : une annotation ::error par finding bloquant, et report.md dans le
# résumé du job.
#
# Usage :
#   _scripts/ci-vault-gate.sh pr [--out-dir DIR]
#     --out-dir : garde findings.json et report.md dans DIR (défaut : dossier temporaire supprimé)

set -euo pipefail

usage() {
  echo "Usage: $0 pr [--out-dir DIR]" >&2
  exit 2
}

[[ $# -ge 1 ]] || usage
MODE="$1"; shift
if [[ "$MODE" != "pr" ]]; then
  echo "Unknown mode: $MODE (seul le mode 'pr' est implémenté)" >&2
  usage
fi

OUT_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-dir) [[ $# -ge 2 ]] || usage; OUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; usage ;;
  esac
done

VAULT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$VAULT_ROOT"

# Sans PyYAML, les checks du vault et sync_moc_decisions.py se rabattent sur une lecture
# ligne à ligne des frontmatters : les listes deviennent des chaînes (des centaines de
# fausses erreurs) et un YAML invalide n'est plus détecté. Pas de verdict dans ce cas.
if ! python3 -c 'import yaml' >/dev/null 2>&1; then
  MSG="PyYAML absent : aucun verdict (pip install -r _scripts/requirements-ci.txt)"
  if [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
    echo "::error title=ci-vault-gate/infra::$MSG"
  else
    echo "ERROR: (ci-vault-gate/infra) — $MSG"
  fi
  exit 2
fi

if [[ -z "$OUT_DIR" ]]; then
  OUT_DIR="$(mktemp -d)"
  trap 'rm -rf "$OUT_DIR"' EXIT
else
  mkdir -p "$OUT_DIR"
fi
FINDINGS="$OUT_DIR/findings.json"
REPORT="$OUT_DIR/report.md"
# Un fichier d'un run précédent ne doit jamais être lu comme la sortie de celui-ci.
rm -f "$FINDINGS" "$REPORT"

LINT_RC=0
bash _scripts/weekly-lint.sh --no-monorepo --output "$FINDINGS" --markdown "$REPORT" || LINT_RC=$?

MOC_RC=0
MOC_OUT="$(python3 _scripts/sync_moc_decisions.py --check 2>&1)" || MOC_RC=$?

python3 - "$FINDINGS" "$REPORT" "$LINT_RC" "$MOC_RC" "$MOC_OUT" <<'PY'
import json
import os
import sys
from pathlib import Path

findings_path, report_path, lint_rc, moc_rc, moc_out = sys.argv[1:6]
lint_rc, moc_rc = int(lint_rc), int(moc_rc)
on_gha = os.environ.get("GITHUB_ACTIONS") == "true"


def esc_data(s):
    # Échappement des commandes de workflow GitHub : une valeur ne peut pas ouvrir
    # une nouvelle ligne, donc ni une autre annotation ni une autre commande.
    return str(s).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def esc_prop(s):
    return esc_data(s).replace(":", "%3A").replace(",", "%2C")


def annotate(level, message, file=None, title=None):
    if on_gha:
        props = []
        if file:
            props.append(f"file={esc_prop(file)}")
        if title:
            props.append(f"title={esc_prop(title)}")
        sep = " " + ",".join(props) if props else ""
        print(f"::{level}{sep}::{esc_data(message)}")
    else:
        where = " ".join(x for x in (file, f"({title})" if title else None) if x)
        print(f"{level.upper()}: {where} — {message}" if where else f"{level.upper()}: {message}")


def infra_fail(message):
    annotate("error", message, title="ci-vault-gate/infra")
    sys.exit(2)


if lint_rc != 0:
    infra_fail(f"weekly-lint.sh a échoué (exit {lint_rc}) : aucun verdict")
try:
    data = json.loads(Path(findings_path).read_text(encoding="utf-8"))
    totals = data["totals"]
    errors = totals["error"]
    warnings = totals["warning"]
    legacy_failures = totals["legacy_failures"]
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in (errors, warnings, legacy_failures)):
        raise ValueError("totals non entiers")
    modern = data["modern_checks"]
    legacy = data["legacy_checks"]
except (OSError, ValueError, KeyError, TypeError) as e:
    infra_fail(f"sortie de weekly-lint absente ou illisible ({findings_path}) : {e}")

if moc_rc not in (0, 1):
    infra_fail(f"sync_moc_decisions.py --check a échoué (exit {moc_rc}) : {moc_out[-500:]}")

for check in modern:
    for f in check.get("findings", []):
        if f.get("severity") == "error":
            annotate("error", f.get("message", "?"), file=f.get("file"), title=f.get("rule") or check.get("check"))
for check in legacy:
    if check.get("status") == "fail":
        lines = [l for l in str(check.get("output", "")).splitlines() if l.strip()]
        annotate("error", " | ".join(lines[-5:]) or "échec sans sortie", title=f"weekly-lint/{check.get('check', '?')}")
moc_drift = moc_rc == 1
if moc_drift:
    annotate(
        "error",
        "l'index auto-généré ne correspond plus aux frontmatters des ADR ; "
        "le régénérer avec : python3 _scripts/sync_moc_decisions.py --write",
        file="ops/moc/MOC-Decisions.md",
        title="moc-decisions/index-drift",
    )

blocking = errors > 0 or legacy_failures > 0 or moc_drift
verdict = "ROUGE" if blocking else "VERT"
summary = (
    f"ci-vault-gate pr : {verdict} — {errors} erreur(s), {legacy_failures} check(s) legacy en échec, "
    f"index MOC-Decisions {'en dérive' if moc_drift else 'à jour'} ; {warnings} avertissement(s), non bloquants"
)
print(summary)

step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
if step_summary:
    report = Path(report_path).read_text(encoding="utf-8") if Path(report_path).is_file() else ""
    with open(step_summary, "a", encoding="utf-8") as fh:
        fh.write(f"**{summary}**\n\n{report}\n")

sys.exit(1 if blocking else 0)
PY
