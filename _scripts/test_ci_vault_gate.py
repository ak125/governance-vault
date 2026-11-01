#!/usr/bin/env python3
"""Tests du gate de PR du vault (_scripts/ci-vault-gate.sh) et du mode --no-monorepo de weekly-lint.

Le gate est teste en boite noire : le vrai script est copie dans un vault factice ou
weekly-lint.sh et sync_moc_decisions.py sont remplaces par des stubs pilotes par
l'environnement. Le contrat verifie : vert seulement si la sortie des checks est lisible
ET sans finding bloquant ; une sortie absente, illisible ou perimee n'est jamais un vert.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "_scripts" / "ci-vault-gate.sh"
WEEKLY_LINT = REPO / "_scripts" / "weekly-lint.sh"

STUB_WEEKLY_LINT = """#!/usr/bin/env bash
set -euo pipefail
out=""; md=""; no_monorepo=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) out="$2"; shift 2 ;;
    --markdown) md="$2"; shift 2 ;;
    --no-monorepo) no_monorepo=1; shift ;;
    *) exit 9 ;;
  esac
done
# Le gate doit toujours demander le mode vault-only.
[[ "$no_monorepo" -eq 1 ]] || exit 7
if [[ -n "${STUB_FINDINGS:-}" ]]; then cp "$STUB_FINDINGS" "$out"; fi
echo "# stub report" > "$md"
exit "${STUB_LINT_RC:-0}"
"""

STUB_SYNC_MOC = """import os, sys
if sys.argv[1:] != ["--check"]:
    sys.exit(9)
print("stub sync_moc_decisions")
sys.exit(int(os.environ.get("STUB_MOC_RC", "0")))
"""


def make_findings(error=0, warning=0, legacy_failures=0, modern_findings=(), legacy=()):
    return {
        "run_id": "2026-09-30T00:00:00Z",
        "run_date": "2026-09-30",
        "legacy_checks": list(legacy),
        "modern_checks": [{
            "check": "frontmatter-schema",
            "findings": list(modern_findings),
            "summary": {"error": error, "warning": warning, "info": 0},
        }],
        "totals": {"error": error, "warning": warning, "info": 0, "legacy_failures": legacy_failures},
    }


@pytest.fixture
def fake_vault(tmp_path):
    scripts = tmp_path / "vault" / "_scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(GATE, scripts / "ci-vault-gate.sh")
    (scripts / "weekly-lint.sh").write_text(STUB_WEEKLY_LINT, encoding="utf-8")
    (scripts / "sync_moc_decisions.py").write_text(STUB_SYNC_MOC, encoding="utf-8")
    return tmp_path / "vault"


def clean_env(**extra):
    # Sous GitHub Actions, le gate teste ne doit ni annoter ni ecrire dans le resume du vrai job.
    env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_ACTIONS", "GITHUB_STEP_SUMMARY")}
    env.update({k: str(v) for k, v in extra.items()})
    return env


def run_gate(vault, findings=None, moc_rc=0, lint_rc=0, args=("pr",), **env_extra):
    env = clean_env(STUB_MOC_RC=moc_rc, STUB_LINT_RC=lint_rc, **env_extra)
    if findings is not None:
        src = vault.parent / "stub-findings.json"
        src.write_text(findings if isinstance(findings, str) else json.dumps(findings), encoding="utf-8")
        env["STUB_FINDINGS"] = str(src)
    return subprocess.run(
        ["bash", str(vault / "_scripts" / "ci-vault-gate.sh"), *args],
        capture_output=True, text=True, env=env, timeout=60,
    )


# --------------------------------------------------------------------------- #
# 1. Verdicts
# --------------------------------------------------------------------------- #

def test_clean_vault_is_green(fake_vault):
    r = run_gate(fake_vault, make_findings())
    assert r.returncode == 0, r.stdout + r.stderr
    assert "VERT" in r.stdout


def test_warnings_alone_do_not_block(fake_vault):
    r = run_gate(fake_vault, make_findings(warning=3))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "3 avertissement(s)" in r.stdout


def test_error_finding_blocks_and_is_reported(fake_vault):
    finding = {"severity": "error", "file": "ledger/decisions/adr/ADR-999-x.md",
               "message": "missing required field 'date'", "rule": "frontmatter/required"}
    r = run_gate(fake_vault, make_findings(error=1, modern_findings=[finding]))
    assert r.returncode == 1
    assert "ADR-999-x.md" in r.stdout and "missing required field 'date'" in r.stdout
    assert "ROUGE" in r.stdout


def test_error_total_blocks_even_without_listed_finding(fake_vault):
    """Le verdict suit les totaux de weekly-lint, pas seulement les findings listes."""
    r = run_gate(fake_vault, make_findings(error=2))
    assert r.returncode == 1


def test_legacy_failure_blocks(fake_vault):
    legacy = [{"check": "orphans", "exit_code": 1, "status": "fail",
               "exit_meaning": "exit1=orphans found", "output": "FAIL: 1 orphan\nledger/x.md"}]
    r = run_gate(fake_vault, make_findings(legacy_failures=1, legacy=legacy))
    assert r.returncode == 1
    assert "weekly-lint/orphans" in r.stdout


def test_moc_index_drift_blocks(fake_vault):
    r = run_gate(fake_vault, make_findings(), moc_rc=1)
    assert r.returncode == 1
    assert "moc-decisions/index-drift" in r.stdout
    assert "sync_moc_decisions.py --write" in r.stdout


# --------------------------------------------------------------------------- #
# 2. Jamais de vert par defaut
# --------------------------------------------------------------------------- #

def test_missing_findings_is_never_green(fake_vault):
    r = run_gate(fake_vault, findings=None)
    assert r.returncode == 2
    assert "ci-vault-gate/infra" in r.stdout


@pytest.mark.parametrize("payload", [
    "not json",
    json.dumps({"modern_checks": [], "legacy_checks": []}),
    json.dumps({**make_findings(), "totals": {"error": "0", "warning": 0, "info": 0, "legacy_failures": 0}}),
    json.dumps({**make_findings(), "totals": {"error": False, "warning": 0, "info": 0, "legacy_failures": 0}}),
    json.dumps({k: v for k, v in make_findings().items() if k != "modern_checks"}),
])
def test_unreadable_findings_is_never_green(fake_vault, payload):
    r = run_gate(fake_vault, findings=payload)
    assert r.returncode == 2, r.stdout + r.stderr


def test_lint_crash_is_never_green(fake_vault):
    r = run_gate(fake_vault, make_findings(), lint_rc=1)
    assert r.returncode == 2


def test_moc_check_crash_is_never_green(fake_vault):
    r = run_gate(fake_vault, make_findings(), moc_rc=2)
    assert r.returncode == 2


def test_missing_pyyaml_gives_no_verdict(fake_vault, tmp_path):
    """Sans PyYAML, les checks liraient les frontmatters ligne a ligne : aucun verdict."""
    blocker = tmp_path / "no-yaml"
    (blocker / "yaml").mkdir(parents=True)
    (blocker / "yaml" / "__init__.py").write_text("raise ImportError('PyYAML absent (test)')\n", encoding="utf-8")
    r = run_gate(fake_vault, make_findings(), PYTHONPATH=blocker)
    assert r.returncode == 2
    assert "PyYAML absent" in r.stdout


def test_stale_findings_from_a_previous_run_are_not_reused(fake_vault, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "findings.json").write_text(json.dumps(make_findings()), encoding="utf-8")
    r = run_gate(fake_vault, findings=None, args=("pr", "--out-dir", str(out)))
    assert r.returncode == 2


@pytest.mark.parametrize("args", [(), ("weekly",), ("pr", "--bogus"), ("pr", "--out-dir")])
def test_usage_errors(fake_vault, args):
    r = run_gate(fake_vault, make_findings(), args=args)
    assert r.returncode == 2


# --------------------------------------------------------------------------- #
# 3. GitHub Actions
# --------------------------------------------------------------------------- #

def test_github_annotations_are_escaped_and_summary_written(fake_vault, tmp_path):
    finding = {"severity": "error", "file": "ops/a:b,c.md",
               "message": "line1\n::warning::injected 100%", "rule": "moc/x"}
    summary = tmp_path / "step-summary.md"
    r = run_gate(fake_vault, make_findings(error=1, modern_findings=[finding]),
                 GITHUB_ACTIONS="true", GITHUB_STEP_SUMMARY=summary)
    assert r.returncode == 1
    assert "::error file=ops/a%3Ab%2Cc.md,title=moc/x::line1%0A::warning::injected 100%25" in r.stdout
    # Un message ne peut pas ouvrir une seconde commande de workflow.
    assert not any(line.startswith("::warning") for line in r.stdout.splitlines())
    text = summary.read_text(encoding="utf-8")
    assert "ci-vault-gate pr : ROUGE" in text and "# stub report" in text


# --------------------------------------------------------------------------- #
# 4. weekly-lint --no-monorepo (vrai script, vrai vault)
# --------------------------------------------------------------------------- #

def _canon_checks(out_json):
    data = json.loads(out_json.read_text(encoding="utf-8"))
    return {m["check"]: m for m in data["modern_checks"] if m["check"].startswith("canon-")}


def test_no_monorepo_skips_cross_repo_checks_even_when_the_monorepo_exists(tmp_path):
    fake_monorepo = tmp_path / "monorepo"
    (fake_monorepo / ".spec" / "00-canon").mkdir(parents=True)
    env = clean_env(MONOREPO_PATH=fake_monorepo)

    def lint(*extra):
        out = tmp_path / f"f{len(extra)}.json"
        subprocess.run(["bash", str(WEEKLY_LINT), "--output", str(out), "--markdown", str(tmp_path / "r.md"), *extra],
                       check=True, capture_output=True, text=True, env=env, timeout=300)
        return _canon_checks(out)

    # Temoin : sans le drapeau, le monorepo present est bien lu.
    control = lint()
    assert set(control) == {"canon-backlinks", "canon-freshness", "canon-cross-repo"}
    assert not any(m.get("skipped") for m in control.values())

    vault_only = lint("--no-monorepo")
    assert set(vault_only) == set(control)
    assert all("--no-monorepo" in m.get("skipped", "") for m in vault_only.values())
