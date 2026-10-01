#!/usr/bin/env python3
"""Tests de preflight-write.sh et new-incident.sh sur un vrai depot git.

Contrat : les outils d'ecriture acceptent la racine d'un depot, clone ou worktree
(ou `.git` est un fichier, pas un dossier) ; hors d'une racine de depot, ils
refusent (preflight : exit 20, new-incident : exit 1) sans rien ecrire.
Les scripts sont copies dans un depot jetable : leur racine est `dirname $0/..`.
"""
from __future__ import annotations

import datetime
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOLS = ["_scripts/preflight-write.sh", "_scripts/new-incident.sh", "_scripts/check-v1-paths.sh",
         "_templates/incident-template.md"]


def git_env(home):
    # Depot jetable : ni la config globale de la machine (signature, hooks), ni celle du systeme.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({
        "HOME": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
        "EDITOR": "",
    })
    return env


def git(cwd, env, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


def install_tools(root):
    for rel in TOOLS:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dst)


@pytest.fixture
def vault(tmp_path):
    """Clone d'un depot `origin` nu, contenant les outils, a jour avec origin/main."""
    env = git_env(tmp_path)
    origin = tmp_path / "origin.git"
    git(tmp_path, env, "init", "-q", "--bare", "-b", "main", str(origin))
    root = tmp_path / "vault"
    git(tmp_path, env, "clone", "-q", str(origin), str(root))
    install_tools(root)
    git(root, env, "add", "-A")
    git(root, env, "commit", "-q", "-m", "tools")
    git(root, env, "push", "-q", "origin", "HEAD:main")
    git(root, env, "fetch", "-q", "origin")
    return root, env


@pytest.fixture
def worktree(vault, tmp_path):
    root, env = vault
    wt = tmp_path / "wt"
    git(root, env, "worktree", "add", "-q", str(wt), "-b", "feature")
    assert (wt / ".git").is_file()
    return wt, env


def run(root, env, script, *args, stdin=""):
    return subprocess.run(["bash", str(root / "_scripts" / script), *args], env=env,
                          input=stdin, capture_output=True, text=True)


# --- preflight-write.sh -------------------------------------------------------------------

def test_preflight_clone_root_is_go(vault):
    root, env = vault
    r = run(root, env, "preflight-write.sh")
    assert r.returncode == 0, r.stdout + r.stderr


def test_preflight_worktree_root_is_go(worktree):
    wt, env = worktree
    r = run(wt, env, "preflight-write.sh")
    assert r.returncode == 0, r.stdout + r.stderr


def test_preflight_outside_git_is_refused(tmp_path):
    env = git_env(tmp_path)
    plain = tmp_path / "plain"
    install_tools(plain)
    r = run(plain, env, "preflight-write.sh")
    assert r.returncode == 20, r.stdout + r.stderr


def test_preflight_subdirectory_of_a_repo_is_refused(vault):
    root, env = vault
    sub = root / "nested"
    install_tools(sub)
    r = run(sub, env, "preflight-write.sh")
    assert r.returncode == 20, r.stdout + r.stderr


# --- new-incident.sh ----------------------------------------------------------------------

def incident_path(root):
    today = datetime.date.today()
    return root / "ledger" / "incidents" / f"{today:%Y}" / f"{today:%Y-%m-%d}-test-slug.md"


def test_new_incident_in_worktree_scaffolds_on_a_branch(worktree):
    wt, env = worktree
    # Un worktree n'est jamais sur main (occupee par le clone) : le script demande confirmation.
    r = run(wt, env, "new-incident.sh", "high", "test-slug", stdin="y\n")
    assert r.returncode == 0, r.stdout + r.stderr
    assert incident_path(wt).is_file()
    assert git(wt, env, "rev-parse", "--abbrev-ref", "HEAD").endswith("-test-slug")


def test_new_incident_outside_git_writes_nothing(tmp_path):
    env = git_env(tmp_path)
    plain = tmp_path / "plain"
    install_tools(plain)
    r = run(plain, env, "new-incident.sh", "high", "test-slug", stdin="y\n")
    assert r.returncode == 1, r.stdout + r.stderr
    assert not (plain / "ledger").exists()
