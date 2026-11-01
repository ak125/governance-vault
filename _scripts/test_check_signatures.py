#!/usr/bin/env python3
"""G3: distinguer un inventaire Git en erreur d'une plage vraiment vide.

Depots, clones, worktrees et signatures SSH sont reels et jetables. Seul
rev-list est remplace pour injecter une panne apres une sortie partielle.
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "check-signatures.sh"


def git(root, env, *args):
    return subprocess.run(
        ["git", *args], cwd=root, env=env, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def commit(root, env, *, signed):
    git(root, env, "commit", "-q", "--allow-empty",
        "-S" if signed else "--no-gpg-sign", "-m", "fixture commit")
    return git(root, env, "rev-parse", "HEAD")


@pytest.fixture(params=["clone", "worktree"])
def repo(tmp_path, request):
    # Ne lit ni la configuration de signature ni les cles de l'operateur.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": "G3 fixture",
        "GIT_AUTHOR_EMAIL": "g3@example.invalid",
        "GIT_COMMITTER_NAME": "G3 fixture",
        "GIT_COMMITTER_EMAIL": "g3@example.invalid",
    })
    seed = tmp_path / "seed"
    seed.mkdir()
    git(seed, env, "init", "-q", "-b", "main", "--template=")
    commit(seed, env, signed=False)
    root = tmp_path / "clone"
    git(tmp_path, env, "clone", "-q", "--template=", str(seed), str(root))
    if request.param == "worktree":
        worktree = tmp_path / "worktree"
        git(root, env, "worktree", "add", "-q", "-b", "feature", str(worktree))
        root = worktree
        assert (root / ".git").is_file()
    else:
        git(root, env, "checkout", "-q", "-b", "feature")

    key = tmp_path / "signing-key"
    subprocess.run(
        ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
        env=env, check=True, capture_output=True,
    )
    allowed = tmp_path / "allowed-signers"
    allowed.write_text(
        "g3@example.invalid " + key.with_suffix(".pub").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    git(root, env, "config", "gpg.format", "ssh")
    git(root, env, "config", "user.signingkey", str(key))
    git(root, env, "config", "gpg.ssh.allowedSignersFile", str(allowed))
    return root, env


def run_check(root, env, revision_range=None):
    args = ["bash", str(SCRIPT), str(root)]
    if revision_range is not None:
        args.append(revision_range)
    return subprocess.run(args, env=env, capture_output=True, text=True)


@pytest.mark.parametrize("revision_range", ["missing-base..HEAD", "HEAD..missing-head"])
def test_invalid_reference_is_an_error_not_a_pass(repo, revision_range):
    root, env = repo
    result = run_check(root, env, revision_range)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "fatal:" in result.stderr
    assert "git rev-list" in result.stderr
    assert "PASS" not in result.stdout


@pytest.mark.parametrize("partial_output", [False, True], ids=["empty", "partial"])
def test_inventory_failure_stops_before_signature_checks(repo, tmp_path, partial_output):
    root, env = repo
    sha = git(root, env, "rev-parse", "HEAD")
    real_git = shutil.which("git", path=env["PATH"])
    assert real_git is not None
    bindir = tmp_path / "bin"
    bindir.mkdir()
    wrapper = bindir / "git"
    output = f"printf '%s\\n' {shlex.quote(sha)}\n" if partial_output else ""
    wrapper.write_text(
        '#!/bin/sh\n'
        'if [ "$1" = rev-list ]; then\n'
        + output
        + "printf '%s\\n' 'injected inventory failure' >&2\n"
        'exit 73\n'
        'fi\n'
        'if [ "$1" = log ]; then\n'
        "printf '%s\\n' 'signature inspection reached' >&2\n"
        'fi\n'
        f'exec {shlex.quote(real_git)} "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    fault_env = {**env, "PATH": str(bindir) + os.pathsep + env["PATH"]}
    result = run_check(root, fault_env, "HEAD")
    assert result.returncode == 2, result.stdout + result.stderr
    assert "injected inventory failure" in result.stderr
    assert "git rev-list" in result.stderr
    assert "signature inspection reached" not in result.stderr
    assert "PASS" not in result.stdout
    assert "FAIL" not in result.stdout


def test_successfully_empty_range_passes(repo):
    root, env = repo
    result = run_check(root, env, "HEAD..HEAD")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
    assert not result.stderr


@pytest.mark.parametrize("signed,expected", [(True, 0), (False, 1)])
@pytest.mark.parametrize("revision_range", ["HEAD^..HEAD", None], ids=["explicit", "default"])
def test_signed_and_unsigned_commits_are_classified(repo, signed, expected, revision_range):
    root, env = repo
    commit(root, env, signed=signed)
    assert git(root, env, "log", "-1", "--format=%G?") == ("G" if signed else "N")
    result = run_check(root, env, revision_range)
    assert result.returncode == expected, result.stdout + result.stderr
    if signed:
        assert "PASS" in result.stdout
    else:
        assert "status=N" in result.stdout
        assert "PASS" not in result.stdout


@pytest.mark.parametrize("unsigned_first", [False, True])
def test_unsigned_commit_anywhere_in_range_is_rejected(repo, unsigned_first):
    root, env = repo
    commit(root, env, signed=not unsigned_first)
    commit(root, env, signed=unsigned_first)
    result = run_check(root, env, "origin/main..HEAD")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "status=N" in result.stdout
    assert "PASS" not in result.stdout
