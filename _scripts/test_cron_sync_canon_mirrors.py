"""Integration: real Git, real projection and SSH signatures; only GitHub is stubbed.

All repositories, signing keys and Git configuration belong to pytest tmp_path.
No production checkout, global configuration or real GitHub call is used.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

REPO = Path(__file__).resolve().parent.parent
MIRRORS = [".claude/canon-mirrors/a.md", "workspaces/seo-batch/.claude/canon-mirrors/a.md"]
BODY = "# Canon fixture\n\nValidated source.\n"


def git(root, env, *args):
    return subprocess.run(["git", *args], cwd=root, env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def sync(tmp_path):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GH_"))}
    env.update(HOME=str(tmp_path), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0", GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.invalid",
               GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.invalid",
               TMPDIR=str(tmp_path), GH_CALLS=str(tmp_path / "gh-calls"))
    origin = tmp_path / "origin.git"
    git(tmp_path, env, "init", "-q", "--bare", "-b", "main", str(origin))
    root = tmp_path / "checkout"
    git(tmp_path, env, "clone", "-q", str(origin), str(root))
    (root / "work.txt").write_text("base\n")
    for rel in MIRRORS:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("old mirror\n")
    git(root, env, "add", "-A")
    git(root, env, "commit", "-qm", "base")
    git(root, env, "push", "-q", "origin", "HEAD:main")
    key = tmp_path / "signing-key"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
                   env=env, check=True, capture_output=True)
    git(root, env, "config", "gpg.format", "ssh")
    git(root, env, "config", "user.signingkey", str(key))
    git(root, env, "config", "commit.gpgsign", "true")
    allowed = tmp_path / "allowed-signers"
    allowed.write_text("test@example.invalid " + key.with_suffix(".pub").read_text())
    git(root, env, "config", "gpg.ssh.allowedSignersFile", str(allowed))
    vault = tmp_path / "vault"
    (vault / "_scripts").mkdir(parents=True)
    for name in ["cron-sync-canon-mirrors.sh", "sync_canon_mirrors.py"]:
        shutil.copy2(REPO / "_scripts" / name, vault / "_scripts" / name)
    (vault / "source.md").write_text("---\nstatus: canon\n---\n" + BODY)
    (vault / "99-meta").mkdir()
    (vault / "99-meta/canon-hashes.json").write_text(json.dumps({"canons": {"a": {
        "name": "Fixture", "canon_path": "source.md",
        "distribution_sha256": hashlib.sha256(BODY.encode()).hexdigest(),
        "consumers": [{"repo": "ak125/nestjs-remix-monorepo", "path": p} for p in MIRRORS],
    }}}))
    bindir = tmp_path / "bin"
    bindir.mkdir()
    gh = bindir / "gh"
    gh.write_text("#!/bin/sh\n[ \"$1 $2\" = \"pr create\" ] || exit 93\nprintf '%s\\n' \"$*\" >> \"$GH_CALLS\"\ncat >/dev/null\nexit \"${GH_FAIL:-0}\"\n")
    gh.chmod(0o755)
    env.update(PATH=str(bindir) + os.pathsep + env["PATH"], MONOREPO_ROOT=str(root))
    return root, origin, vault, env


def run(sync, *args):
    root, origin, vault, env = sync
    return subprocess.run(["bash", str(vault / "_scripts/cron-sync-canon-mirrors.sh"), *args],
                          env=env, capture_output=True, text=True, timeout=30)


def snapshot(root, env):
    return {
        "head": git(root, env, "rev-parse", "HEAD"),
        "branch": git(root, env, "symbolic-ref", "HEAD"),
        "main": git(root, env, "rev-parse", "refs/heads/main"),
        "status": git(root, env, "status", "--porcelain=v1", "-uall"),
        "index": (root / ".git/index").read_bytes(),
        "files": {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*")
                  if p.is_file() and ".git" not in p.relative_to(root).parts},
    }


def dirty(root, env):
    (root / "local-only.txt").write_text("unpublished commit\n")
    git(root, env, "add", "local-only.txt")
    git(root, env, "commit", "-qm", "local only")
    (root / "work.txt").write_text("staged change\n")
    git(root, env, "add", "work.txt")
    (root / "work.txt").write_text("unstaged change\n")
    (root / "untracked.txt").write_text("untracked change\n")


def worktrees(root, env):
    return [Path(line[9:]) for line in git(root, env, "worktree", "list", "--porcelain").splitlines()
            if line.startswith("worktree ") and Path(line[9:]) != root]


def remote_branches(origin, env):
    return git(origin, env, "for-each-ref", "--format=%(refname:short)", "refs/heads/govvault/").splitlines()


@pytest.mark.parametrize("branch", ["main", "feature"])
def test_sync_preserves_shared_checkout_and_publishes_only_mirrors(sync, branch):
    root, origin, vault, env = sync
    base = git(origin, env, "rev-parse", "main")
    if branch != "main":
        git(root, env, "checkout", "-qb", branch)
    dirty(root, env)
    before = snapshot(root, env)
    r = run(sync)
    assert snapshot(root, env) == before, r.stdout + r.stderr
    assert r.returncode == 0, r.stdout + r.stderr
    branches = remote_branches(origin, env)
    assert len(branches) == 1
    ref = branches[0]
    assert git(origin, env, "rev-parse", ref + "^") == base
    assert git(origin, env, "rev-parse", "main") == base
    assert set(git(origin, env, "diff", "--name-only", base, ref).splitlines()) == set(MIRRORS)
    for rel in MIRRORS:
        assert git(origin, env, "show", ref + ":" + rel) == BODY.strip()
    git(root, env, "verify-commit", ref)
    assert worktrees(root, env) == []


def test_noop_removes_only_its_own_worktree_and_branch(sync):
    root, origin, vault, env = sync
    for rel in MIRRORS:
        (root / rel).write_text(BODY)
    git(root, env, "add", "-A")
    git(root, env, "commit", "-qm", "current mirrors")
    git(root, env, "push", "-q", "origin", "HEAD:main")
    before = snapshot(root, env)
    branches = git(root, env, "for-each-ref", "--format=%(refname)", "refs/heads")
    r = run(sync)
    assert r.returncode == 0, r.stdout + r.stderr
    assert snapshot(root, env) == before
    assert git(root, env, "for-each-ref", "--format=%(refname)", "refs/heads") == branches
    assert worktrees(root, env) == []
    assert not Path(env["GH_CALLS"]).exists()


def test_new_untracked_mirrors_are_included_in_the_commit(sync):
    root, origin, vault, env = sync
    git(root, env, "rm", *MIRRORS)
    git(root, env, "commit", "-qm", "no mirrors yet")
    git(root, env, "push", "-q", "origin", "HEAD:main")
    before = snapshot(root, env)
    r = run(sync)
    assert r.returncode == 0, r.stdout + r.stderr
    assert snapshot(root, env) == before
    refs = remote_branches(origin, env)
    assert len(refs) == 1
    for rel in MIRRORS:
        assert git(origin, env, "show", refs[0] + ":" + rel) == BODY.strip()


@pytest.mark.parametrize("failure", ["signing", "push", "github"])
def test_failure_keeps_recoverable_work_and_never_resets_shared_checkout(sync, failure):
    root, origin, vault, env = sync
    dirty(root, env)
    if failure == "signing":
        git(root, env, "config", "user.signingkey", str(root / "missing-key"))
    elif failure == "push":
        hook = origin / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
    else:
        env["GH_FAIL"] = "1"
    before = snapshot(root, env)
    r = run(sync)
    assert snapshot(root, env) == before, r.stdout + r.stderr
    assert r.returncode != 0
    retained = worktrees(root, env)
    assert len(retained) == 1
    assert str(retained[0]) in r.stderr
    assert (retained[0] / MIRRORS[0]).read_text() == BODY
    if failure == "github":
        # The API may have created the PR before the client failed: retain the pushed ref.
        assert len(remote_branches(origin, env)) == 1
    else:
        assert remote_branches(origin, env) == []


@pytest.mark.parametrize("mode", ["dry", "typo"])
def test_preview_and_invalid_mode_do_not_mutate_git(sync, mode):
    root, origin, vault, env = sync
    dirty(root, env)
    before = snapshot(root, env)
    refs = git(root, env, "show-ref")
    r = run(sync, mode)
    assert r.returncode == (0 if mode == "dry" else 2), r.stdout + r.stderr
    assert snapshot(root, env) == before
    assert git(root, env, "show-ref") == refs
    assert worktrees(root, env) == []
    assert not Path(env["GH_CALLS"]).exists()


def test_failed_projection_keeps_partial_output_in_isolated_worktree(sync):
    root, origin, vault, env = sync
    dirty(root, env)
    manifest = vault / "99-meta/canon-hashes.json"
    data = json.loads(manifest.read_text())
    data["canons"]["missing"] = {**data["canons"]["a"], "canon_path": "missing.md"}
    manifest.write_text(json.dumps(data))
    before = snapshot(root, env)
    r = run(sync)
    assert r.returncode != 0
    assert snapshot(root, env) == before
    retained = worktrees(root, env)
    assert len(retained) == 1
    assert (retained[0] / MIRRORS[0]).read_text() == BODY
    assert remote_branches(origin, env) == []


def test_fetch_failure_does_not_change_shared_checkout(sync):
    root, origin, vault, env = sync
    dirty(root, env)
    git(root, env, "remote", "set-url", "origin", str(origin / "missing"))
    before = snapshot(root, env)
    r = run(sync)
    assert r.returncode != 0
    assert snapshot(root, env) == before
    assert worktrees(root, env) == []
    assert not Path(env["GH_CALLS"]).exists()


def test_concurrent_runs_use_distinct_branches_and_worktrees(sync):
    root, origin, vault, env = sync
    dirty(root, env)
    before = snapshot(root, env)
    args = ["bash", str(vault / "_scripts/cron-sync-canon-mirrors.sh")]
    procs = [subprocess.Popen(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             for _ in range(2)]
    for p in procs:
        out, err = p.communicate(timeout=30)
        assert p.returncode == 0, out + err
    assert snapshot(root, env) == before
    assert len(remote_branches(origin, env)) == 2
    assert worktrees(root, env) == []


def test_cleanup_refuses_to_delete_unexpected_work_left_by_a_hook(sync):
    root, origin, vault, env = sync
    dirty(root, env)
    hook = root / ".git/hooks/post-commit"
    hook.write_text("#!/bin/sh\nprintf 'keep me\\n' > hook-output.txt\n")
    hook.chmod(0o755)
    before = snapshot(root, env)
    r = run(sync)
    assert r.returncode != 0
    assert snapshot(root, env) == before
    retained = worktrees(root, env)
    assert len(retained) == 1
    assert (retained[0] / "hook-output.txt").read_text() == "keep me\n"
    assert len(remote_branches(origin, env)) == 1
