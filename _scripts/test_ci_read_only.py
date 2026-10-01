#!/usr/bin/env python3
"""Tests de _scripts/check-ci-read-only.py (G4, ADR-102 D4).

Deux contrats :
- les workflows reels du vault sont conformes : ce test tourne dans le check requis
  `Vault Scripts Tests`, donc un workflow qui donnerait a la CI un moyen d'ecrire ne
  passe pas ;
- chaque moyen d'ecrire connu est detecte (fixtures), et une exception ne vaut que
  pour le job qu'elle nomme.
"""
from __future__ import annotations

import importlib.util
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ccro", REPO / "_scripts" / "check-ci-read-only.py")
ccro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ccro)


def _wf(tmp_path: Path, body: str, name: str = "wf.yml") -> Path:
    path = tmp_path / name
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


def test_real_workflows_are_read_only():
    assert ccro.check_repo(REPO) == []


def test_real_workflows_exist():
    assert list((REPO / ".github" / "workflows").glob("*.yml")), "aucun workflow trouve : le test ne prouverait rien"


def test_read_only_workflow_passes(tmp_path):
    wf = _wf(tmp_path, """
        on: pull_request
        permissions:
          contents: read
        jobs:
          lint:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - run: python3 _scripts/check-orphans.py .
                env:
                  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        """)
    assert ccro.check_workflow(wf) == []


def test_missing_top_level_permissions(tmp_path):
    wf = _wf(tmp_path, """
        on: push
        jobs:
          a:
            runs-on: ubuntu-latest
            steps:
              - run: echo ok
        """)
    assert any("pas de `permissions:`" in f for f in ccro.check_workflow(wf))


@pytest.mark.parametrize("perms", ["write-all", "{contents: write}", "{pull-requests: write}"])
def test_write_scope_at_top_level(tmp_path, perms):
    wf = _wf(tmp_path, f"""
        on: push
        permissions: {perms}
        jobs:
          a:
            runs-on: ubuntu-latest
            steps:
              - run: echo ok
        """)
    assert ccro.check_workflow(wf), perms


def test_write_scope_at_job_level(tmp_path):
    wf = _wf(tmp_path, """
        on: push
        permissions:
          contents: read
        jobs:
          a:
            runs-on: ubuntu-latest
            permissions:
              contents: write
            steps:
              - run: echo ok
        """)
    assert any("`contents: write`" in f for f in ccro.check_workflow(wf))


def test_allowed_write_scope(tmp_path):
    wf = _wf(tmp_path, """
        on: schedule
        permissions:
          contents: read
          issues: write
        jobs:
          a:
            runs-on: ubuntu-latest
            steps:
              - run: echo ok
        """)
    assert ccro.check_workflow(wf) == []


@pytest.mark.parametrize("cmd", [
    "git push origin HEAD",
    "git commit -m auto",
    "git -C vault push",
    "set -e\nsync\ngit add -A && git commit -S -m x",
])
def test_git_write_in_run(tmp_path, cmd):
    head = "on: push\npermissions:\n  contents: read\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: |\n"
    body = "".join(f"          {line}\n" for line in cmd.splitlines())
    wf = _wf(tmp_path, head + body)
    assert any("interdit, la CI" in f for f in ccro.check_workflow(wf)), cmd


def test_git_read_commands_pass(tmp_path):
    wf = _wf(tmp_path, """
        on: push
        permissions:
          contents: read
        jobs:
          a:
            runs-on: ubuntu-latest
            steps:
              - run: |
                  git log --format=%G? origin/main..HEAD
                  echo "pushed_at est un champ, pas une commande"
        """)
    assert ccro.check_workflow(wf) == []


def test_secret_token_outside_exception(tmp_path):
    wf = _wf(tmp_path, """
        on: push
        permissions:
          contents: read
        jobs:
          a:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
                with:
                  token: ${{ secrets.VAULT_PAT }}
        """)
    assert any("VAULT_PAT" in f for f in ccro.check_workflow(wf))


def test_secret_token_in_job_env(tmp_path):
    wf = _wf(tmp_path, """
        on: push
        permissions:
          contents: read
        jobs:
          a:
            runs-on: ubuntu-latest
            env:
              GH_TOKEN: ${{ secrets.BOT_TOKEN }}
            steps:
              - run: gh pr list
        """)
    assert any("BOT_TOKEN" in f for f in ccro.check_workflow(wf))


def test_non_token_secret_passes(tmp_path):
    wf = _wf(tmp_path, """
        on: schedule
        permissions:
          contents: read
        jobs:
          a:
            runs-on: ubuntu-latest
            steps:
              - run: ./cost.sh
                env:
                  SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
        """)
    assert ccro.check_workflow(wf) == []


APP_TOKEN_JOB = """
    on: push
    permissions:
      contents: read
    jobs:
      {job}:
        runs-on: ubuntu-latest
        steps:
          - id: app-token
            uses: actions/create-github-app-token@v1
            with:
              app-id: ${{{{ secrets.CANON_APP_ID }}}}
              private-key: ${{{{ secrets.CANON_APP_PRIVATE_KEY }}}}
{repositories}
"""


def test_app_token_outside_exception(tmp_path):
    wf = _wf(tmp_path, APP_TOKEN_JOB.format(job="dispatch", repositories="              repositories: raw"))
    assert any("hors TOKEN_EXCEPTIONS" in f for f in ccro.check_workflow(wf))


def test_app_token_exception_is_per_job(tmp_path):
    wf = _wf(tmp_path, APP_TOKEN_JOB.format(job="other", repositories="              repositories: raw"),
             name="canon-publish.yml")
    assert any("hors TOKEN_EXCEPTIONS" in f for f in ccro.check_workflow(wf))


def test_app_token_in_exception_must_be_scoped(tmp_path):
    wf = _wf(tmp_path, APP_TOKEN_JOB.format(job="dispatch", repositories=""), name="canon-publish.yml")
    assert any("sans `repositories:`" in f for f in ccro.check_workflow(wf))


def test_app_token_in_exception_scoped_passes(tmp_path):
    wf = _wf(tmp_path, APP_TOKEN_JOB.format(job="dispatch", repositories="              repositories: raw"),
             name="canon-publish.yml")
    assert ccro.check_workflow(wf) == []


def test_invalid_yaml_is_reported(tmp_path):
    wf = _wf(tmp_path, "on: [push\npermissions: {")
    assert any("YAML invalide" in f for f in ccro.check_workflow(wf))


def test_main_exit_codes(tmp_path, capsys):
    assert ccro.main(["x", str(tmp_path)]) == 2
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    _wf(wf_dir, "on: push\njobs:\n  a:\n    runs-on: x\n    steps:\n      - run: echo\n")
    assert ccro.main(["x", str(tmp_path)]) == 1
    assert ccro.main(["x", str(REPO)]) == 0
