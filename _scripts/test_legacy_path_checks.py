#!/usr/bin/env python3
"""Tests de check-v1-paths.sh et check-vault-pollution.sh sur un vrai depot git.

Contrat : le check s'execute a la racine d'un depot, que ce soit un clone ou un
worktree (ou `.git` est un fichier, pas un dossier) ; un sous-dossier ou un dossier
hors git est une erreur (exit 2), jamais un vert.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

CHECKS = [
    pytest.param("check-v1-paths.sh", "01-incidents/INC-x.md", id="v1-paths"),
    pytest.param("check-vault-pollution.sh", "seo/brief.md", id="vault-pollution"),
]


def git_env(home):
    # Depot jetable : ni la config globale de la machine (signature, hooks), ni celle du systeme.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({
        "HOME": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
    })
    return env


def git(cwd, env, *args):
    subprocess.run(["git", *args], cwd=cwd, env=env, check=True, capture_output=True)


def commit_file(cwd, env, rel):
    p = Path(cwd) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("x\n", encoding="utf-8")
    git(cwd, env, "add", rel)
    git(cwd, env, "commit", "-q", "-m", f"add {rel}")


@pytest.fixture
def repo(tmp_path):
    env = git_env(tmp_path)
    root = tmp_path / "vault"
    root.mkdir()
    git(root, env, "init", "-q", "-b", "main")
    commit_file(root, env, "ledger/ok.md")
    return root, env


def run_check(script, path, env):
    return subprocess.run(["bash", str(REPO / "_scripts" / script), str(path)],
                          env=env, capture_output=True, text=True)


@pytest.mark.parametrize("script,bad_path", CHECKS)
def test_clone_root_is_accepted(repo, script, bad_path):
    root, env = repo
    r = run_check(script, root, env)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("script,bad_path", CHECKS)
def test_worktree_root_is_accepted(repo, tmp_path, script, bad_path):
    root, env = repo
    wt = tmp_path / "wt"
    git(root, env, "worktree", "add", "-q", str(wt), "-b", "feature")
    assert (wt / ".git").is_file()
    r = run_check(script, wt, env)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("script,bad_path", CHECKS)
def test_worktree_violation_is_detected(repo, tmp_path, script, bad_path):
    root, env = repo
    wt = tmp_path / "wt"
    git(root, env, "worktree", "add", "-q", str(wt), "-b", "feature")
    commit_file(wt, env, bad_path)
    r = run_check(script, wt, env)
    assert r.returncode == 1, r.stdout + r.stderr
    assert bad_path in r.stdout


@pytest.mark.parametrize("script,bad_path", CHECKS)
def test_subdirectory_is_refused(repo, script, bad_path):
    # git ls-files y serait relatif au sous-dossier : les motifs ancres a la racine ne verraient rien.
    root, env = repo
    r = run_check(script, root / "ledger", env)
    assert r.returncode == 2, r.stdout + r.stderr


@pytest.mark.parametrize("script,bad_path", CHECKS)
def test_non_git_directory_is_refused(tmp_path, script, bad_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    r = run_check(script, plain, git_env(tmp_path))
    assert r.returncode == 2, r.stdout + r.stderr
