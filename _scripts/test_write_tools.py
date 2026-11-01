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
import shlex
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


@pytest.mark.parametrize("layout", ["vault", "worktree"])
@pytest.mark.parametrize("failure", ["missing", "not-executable", "directory", "bad-interpreter"])
def test_preflight_unusable_validator_is_an_error(request, layout, failure):
    root, env = request.getfixturevalue(layout)
    validator = root / "_scripts/check-v1-paths.sh"
    if failure == "missing":
        validator.unlink()
    elif failure == "not-executable":
        validator.chmod(0o644)
    elif failure == "directory":
        validator.unlink()
        validator.mkdir()
    else:
        validator.write_text("#!/nonexistent/vault-test-interpreter\n", encoding="utf-8")
    # Autoriser un arbre sale ne doit jamais rendre le controle v1 facultatif.
    r = run(root, env, "preflight-write.sh", "--allow-dirty")
    assert r.returncode == 22, r.stdout + r.stderr
    assert "ERR" in r.stdout + r.stderr
    assert "GO" not in r.stdout
    assert "v1 paths détectés" not in r.stdout


@pytest.mark.parametrize("layout", ["vault", "worktree"])
def test_preflight_git_inventory_error_preserves_report(request, layout, tmp_path):
    root, env = request.getfixturevalue(layout)
    report = root / "99-meta/v1-paths-report.md"
    report.parent.mkdir()
    report.write_bytes(b"previous report\n")
    index = tmp_path / "bad-index"
    index.write_bytes(b"invalid git index\n")
    # Le vrai Git lit un index illisible uniquement lors de l'inventaire ;
    # fetch, rev-parse et les autres controles restent fonctionnels.
    real_git = shutil.which("git", path=env["PATH"])
    assert real_git is not None
    bindir = tmp_path / "bin"
    bindir.mkdir()
    wrapper = bindir / "git"
    wrapper.write_text(
        '#!/bin/sh\nif [ "$1" = ls-files ]; then\n'
        f"  export GIT_INDEX_FILE={shlex.quote(str(index))}\nfi\n"
        f'exec {shlex.quote(real_git)} "$@"\n', encoding="utf-8",
    )
    wrapper.chmod(0o755)
    env = {**env, "PATH": str(bindir) + os.pathsep + env["PATH"]}
    r = run(root, env, "preflight-write.sh", "--allow-dirty")
    assert r.returncode == 22, r.stdout + r.stderr
    assert "ERR" in r.stdout + r.stderr
    assert "GO" not in r.stdout
    assert "v1 paths détectés" not in r.stdout
    assert report.read_bytes() == b"previous report\n"


@pytest.mark.parametrize("layout", ["vault", "worktree"])
def test_preflight_actual_v1_violation_is_not_a_control_error(request, layout):
    root, env = request.getfixturevalue(layout)
    bad_path = root / "01-incidents/INC-x.md"
    bad_path.parent.mkdir()
    bad_path.write_text("x\n", encoding="utf-8")
    git(root, env, "add", str(bad_path))
    r = run(root, env, "preflight-write.sh", "--allow-dirty")
    assert r.returncode == 13, r.stdout + r.stderr
    assert "v1 paths détectés" in r.stdout
    assert "GO" not in r.stdout
    assert "01-incidents/INC-x.md" in (root / "99-meta/v1-paths-report.md").read_text()


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
