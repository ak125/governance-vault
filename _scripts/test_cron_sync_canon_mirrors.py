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


def publish_current_mirrors(root, env):
    """Put up-to-date mirrors on origin/main: the next run finds no drift."""
    for rel in MIRRORS:
        (root / rel).write_text(BODY)
    git(root, env, "add", "-A")
    git(root, env, "commit", "-qm", "current mirrors")
    git(root, env, "push", "-q", "origin", "HEAD:main")


def run_dirs(tmp_path):
    return sorted(tmp_path.glob("canon-sync.*"))


def test_noop_removes_only_its_own_worktree_and_branch(sync):
    root, origin, vault, env = sync
    publish_current_mirrors(root, env)
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
    assert "worktree lock" not in r.stderr and "flock failed" not in r.stderr
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


def lock_probe(tmp_path, env, common_dir):
    """Git shim: record the lock state for the commands that administer worktrees
    (fetch, worktree add, worktree remove) and for the commit and the push that run
    between them, which must find the lock released.

    locked    : the lock on the common Git directory is held while the command runs;
    UNLOCKED  : it is not;
    INHERITED : the command holds the lock's file descriptor, so a process it leaves
                behind (git maintenance) would keep the lock after the command returns;
    NOPROC    : /proc is missing, the inheritance check cannot run.
    """
    real_git = shutil.which("git", path=env["PATH"])
    trace = tmp_path / "git-trace"
    shim = tmp_path / "bin" / "git"
    shim.write_text(
        "#!/bin/sh\n"
        "case \" $* \" in\n"
        "  *' fetch '*) cmd=fetch ;;\n"
        "  *' worktree add '*) cmd=add ;;\n"
        "  *' worktree remove '*) cmd=remove ;;\n"
        "  *' commit '*) cmd=commit ;;\n"
        "  *' push '*) cmd=push ;;\n"
        f"  *) exec '{real_git}' \"$@\" ;;\n"
        "esac\n"
        f"if flock --shared --nonblock '{common_dir}' true; then state=UNLOCKED; else state=locked; fi\n"
        "[ -d /proc/$$/fd ] || state=NOPROC\n"
        "for fd in /proc/$$/fd/*; do\n"
        f"  [ \"$(readlink \"$fd\")\" = '{common_dir}' ] && state=INHERITED\n"
        "done\n"
        f"printf '%s %s\\n' \"$cmd\" \"$state\" >> '{trace}'\n"
        f"exec '{real_git}' \"$@\"\n")
    shim.chmod(0o755)
    return trace


PROBED = ["fetch locked", "add locked", "commit UNLOCKED", "push UNLOCKED", "remove locked"]


def test_worktree_administration_holds_the_shared_repository_lock(sync, tmp_path):
    """Each command that administers worktrees runs under the repository lock,
    and the lock is released between them.

    Git writes and removes .git/worktrees/<id>/ non-atomically: a fetch into a local
    branch, a `worktree add` or a `worktree remove` that runs during another run's
    `worktree add` or `worktree remove` can read a half-written entry and fail
    (exit 128 or 1).
    """
    root, origin, vault, env = sync
    trace = lock_probe(tmp_path, env, root / ".git")
    r = run(sync)
    assert r.returncode == 0, r.stdout + r.stderr
    assert trace.read_text().splitlines() == PROBED
    assert worktrees(root, env) == []


def test_lock_is_the_common_git_directory_when_the_checkout_is_a_linked_worktree(sync, tmp_path):
    """Runs started from two worktrees of one repository must share one lock."""
    root, origin, vault, env = sync
    linked = tmp_path / "linked"
    git(root, env, "worktree", "add", "-q", "-b", "linked", str(linked))
    env["MONOREPO_ROOT"] = str(linked)
    trace = lock_probe(tmp_path, env, root / ".git")
    r = run(sync)
    assert r.returncode == 0, r.stdout + r.stderr
    assert trace.read_text().splitlines() == PROBED
    assert worktrees(root, env) == [linked]


def failing_flock(tmp_path, env, call, code):
    """flock stand-in: the call numbered `call` fails with `code`, the others are real."""
    real_flock = shutil.which("flock", path=env["PATH"])
    count = tmp_path / "flock-calls"
    flock = tmp_path / "bin" / "flock"
    flock.write_text(
        "#!/bin/sh\n"
        f"n=$(( $(cat '{count}' 2>/dev/null || echo 0) + 1 ))\n"
        f"echo \"$n\" > '{count}'\n"
        f"if [ \"$n\" -eq {call} ]; then\n"
        # flock, lock never obtained: exits with the requested conflict code, 1 by default.
        f"  case \" $* \" in *' --timeout 120 --conflict-exit-code 75 '*) exit {code} ;; esac\n"
        "  exit 1\n"
        "fi\n"
        f"exec '{real_flock}' \"$@\"\n")
    flock.chmod(0o755)


def local_sync_branches(root, env):
    return git(root, env, "for-each-ref", "--format=%(refname:short)", "refs/heads/govvault/").splitlines()


def test_lock_not_obtained_at_fetch_fails_the_run_before_any_change(sync, tmp_path):
    root, origin, vault, env = sync
    dirty(root, env)
    failing_flock(tmp_path, env, call=1, code=75)
    before = snapshot(root, env)
    r = run(sync)
    assert r.returncode == 75, r.stdout + r.stderr
    assert "worktree lock not obtained within 120 s" in r.stderr
    assert "git fetch not run" in r.stderr
    assert snapshot(root, env) == before
    assert local_sync_branches(root, env) == []
    assert worktrees(root, env) == []
    assert [list(d.iterdir()) for d in run_dirs(tmp_path)] == [[]]
    assert not Path(env["GH_CALLS"]).exists()


def test_lock_not_obtained_at_worktree_add_leaves_only_the_local_branch(sync, tmp_path):
    root, origin, vault, env = sync
    dirty(root, env)
    failing_flock(tmp_path, env, call=2, code=75)
    before = snapshot(root, env)
    r = run(sync)
    assert r.returncode == 75, r.stdout + r.stderr
    assert "git worktree add not run" in r.stderr
    assert snapshot(root, env) == before
    assert len(local_sync_branches(root, env)) == 1
    assert worktrees(root, env) == []
    assert [list(d.iterdir()) for d in run_dirs(tmp_path)] == [[]]
    assert remote_branches(origin, env) == []
    assert not Path(env["GH_CALLS"]).exists()


def test_lock_not_obtained_at_worktree_remove_keeps_the_worktree_after_the_pr(sync, tmp_path):
    """The PR is already open when cleanup starts: exit 1, not 75, and nothing is undone."""
    root, origin, vault, env = sync
    dirty(root, env)
    failing_flock(tmp_path, env, call=3, code=75)
    before = snapshot(root, env)
    r = run(sync)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "worktree lock not obtained within 120 s" in r.stderr
    assert "git worktree remove not run" in r.stderr
    assert "worktree retained for inspection" in r.stderr
    assert snapshot(root, env) == before
    assert len(worktrees(root, env)) == 1
    assert len(remote_branches(origin, env)) == 1
    assert len(Path(env["GH_CALLS"]).read_text().splitlines()) == 1


def test_lock_not_obtained_at_worktree_remove_without_drift_keeps_worktree_and_branch(sync, tmp_path):
    """No drift, cleanup not run: exit 1, the worktree and the local branch stay, no PR."""
    root, origin, vault, env = sync
    publish_current_mirrors(root, env)
    failing_flock(tmp_path, env, call=3, code=75)
    before = snapshot(root, env)
    r = run(sync)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "OK: no canon mirror drift" in r.stdout
    assert "git worktree remove not run" in r.stderr
    assert "worktree retained for inspection" in r.stderr
    assert snapshot(root, env) == before
    assert len(worktrees(root, env)) == 1
    assert len(local_sync_branches(root, env)) == 1
    assert remote_branches(origin, env) == []
    assert not Path(env["GH_CALLS"]).exists()


def test_flock_error_at_worktree_remove_keeps_the_worktree(sync, tmp_path):
    root, origin, vault, env = sync
    failing_flock(tmp_path, env, call=3, code=66)
    r = run(sync)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "flock failed (code 66)" in r.stderr
    assert "git worktree remove not run" in r.stderr
    assert "worktree lock not obtained" not in r.stderr
    assert len(worktrees(root, env)) == 1
    assert len(Path(env["GH_CALLS"]).read_text().splitlines()) == 1


def test_flock_error_is_not_reported_as_a_lock_timeout(sync, tmp_path):
    root, origin, vault, env = sync
    failing_flock(tmp_path, env, call=1, code=66)
    r = run(sync)
    assert r.returncode == 66, r.stdout + r.stderr
    assert "flock failed (code 66)" in r.stderr
    assert "git fetch not run" in r.stderr
    assert "worktree lock not obtained" not in r.stderr
    assert local_sync_branches(root, env) == []
    assert worktrees(root, env) == []
    assert [list(d.iterdir()) for d in run_dirs(tmp_path)] == [[]]
    assert not Path(env["GH_CALLS"]).exists()


def test_flock_error_at_worktree_add_does_not_run_git(sync, tmp_path):
    root, origin, vault, env = sync
    failing_flock(tmp_path, env, call=2, code=66)
    r = run(sync)
    assert r.returncode == 66, r.stdout + r.stderr
    assert "flock failed (code 66)" in r.stderr
    assert "git worktree add not run" in r.stderr
    assert len(local_sync_branches(root, env)) == 1
    assert worktrees(root, env) == []
    assert [list(d.iterdir()) for d in run_dirs(tmp_path)] == [[]]
    assert not Path(env["GH_CALLS"]).exists()


# Step -> (last Git command the wrapper runs before that step's lock, as the shim's `case`
# pattern; local branches, worktrees and `gh pr create` calls the run leaves).
UNOPENABLE = {
    "fetch": ("*' show-ref '*", 0, 0, 0),
    "worktree add": ("*'^{commit} '*", 1, 0, 0),
    "worktree remove": ("*' push '*", 1, 1, 1),
}


@pytest.mark.parametrize("step", UNOPENABLE)
def test_common_git_directory_that_cannot_be_opened_fails_before_git_runs(sync, tmp_path, step):
    """The lock descriptor cannot be opened: the wrapper says so, exits 1 and runs no
    further Git command, at each of the three steps."""
    if os.geteuid() == 0:
        pytest.skip("root opens a directory whatever its mode")
    root, origin, vault, env = sync
    pattern, branches, kept, prs = UNOPENABLE[step]
    common_dir = root / ".git"
    mode = common_dir.stat().st_mode
    real_git = shutil.which("git", path=env["PATH"])
    trace = tmp_path / "git-calls"
    shim = tmp_path / "bin" / "git"
    # Every call is traced; the directory is closed once the trigger command has run.
    shim.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> '{trace}'\n"
        "case \" $* \" in\n"
        f"  {pattern}) '{real_git}' \"$@\"; rc=$?; chmod 000 '{common_dir}'; exit $rc ;;\n"
        "esac\n"
        f"exec '{real_git}' \"$@\"\n")
    shim.chmod(0o755)
    try:
        r = run(sync)
    finally:
        common_dir.chmod(mode)
    shim.unlink()
    assert r.returncode == 1, r.stdout + r.stderr
    assert "cannot open" in r.stderr and f"git {step} not run" in r.stderr
    assert "flock failed" not in r.stderr and "worktree lock" not in r.stderr
    assert ("worktree retained for inspection" in r.stderr) == (step == "worktree remove")
    # The trigger command is the last Git call: nothing ran once the directory was closed.
    last = " " + trace.read_text().splitlines()[-1] + " "
    assert pattern.strip("*'") in last, last
    assert len(local_sync_branches(root, env)) == branches
    assert len(worktrees(root, env)) == kept
    assert (len(Path(env["GH_CALLS"]).read_text().splitlines())
            if Path(env["GH_CALLS"]).exists() else 0) == prs


@pytest.mark.parametrize("signal", ["TERM", "INT"])
def test_signal_during_cleanup_names_the_run_directory(sync, tmp_path, signal):
    """Signal received while cleanup waits for the lock: exit 1, the worktree stays and
    the message gives the directory to inspect."""
    root, origin, vault, env = sync
    real_flock = shutil.which("flock", path=env["PATH"])
    count = tmp_path / "flock-calls"
    flock = tmp_path / "bin" / "flock"
    # Third call = worktree remove: signal the wrapper, then take the lock for real.
    flock.write_text(
        "#!/bin/sh\n"
        f"n=$(( $(cat '{count}' 2>/dev/null || echo 0) + 1 ))\n"
        f"echo \"$n\" > '{count}'\n"
        f"[ \"$n\" -eq 3 ] && kill -{signal} \"$PPID\"\n"
        f"exec '{real_flock}' \"$@\"\n")
    flock.chmod(0o755)
    r = run(sync)
    assert r.returncode == 1, r.stdout + r.stderr
    retained = worktrees(root, env)
    assert len(retained) == 1
    assert (f"Error: interrupted during cleanup; inspect {retained[0].parent}"
            in r.stderr.splitlines()), r.stderr
    assert len(Path(env["GH_CALLS"]).read_text().splitlines()) == 1


@pytest.mark.parametrize("signal", ["TERM", "INT"])
def test_signal_during_the_last_cleanup_command_does_not_fail_a_cleaned_run(sync, tmp_path, signal):
    """Signal received while the empty run directory is removed: nothing is left to
    report, the run finishes its cleanup and exits 0."""
    root, origin, vault, env = sync
    real_rmdir = shutil.which("rmdir", path=env["PATH"])
    rmdir = tmp_path / "bin" / "rmdir"
    rmdir.write_text(f"#!/bin/sh\nkill -{signal} \"$PPID\"\nexec '{real_rmdir}' \"$@\"\n")
    rmdir.chmod(0o755)
    r = run(sync)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "interrupted during cleanup" not in r.stderr
    assert worktrees(root, env) == []
    assert run_dirs(tmp_path) == []
    assert len(Path(env["GH_CALLS"]).read_text().splitlines()) == 1


@pytest.mark.parametrize("signal,code", [("TERM", 143), ("INT", 130)])
def test_git_keeps_the_default_signal_disposition_during_cleanup(sync, tmp_path, signal, code):
    """Git started with SIGINT or SIGTERM ignored drops its lock files on the signal and
    carries on without them: the branch cleanup must run Git with the default disposition.
    A shell that inherits an ignored signal survives its own `kill`; this one must die."""
    root, origin, vault, env = sync
    publish_current_mirrors(root, env)
    real_git = shutil.which("git", path=env["PATH"])
    shim = tmp_path / "bin" / "git"
    shim.write_text(
        "#!/bin/sh\n"
        "case \" $* \" in\n"
        f"  *' update-ref '*) kill -{signal} $$ ;;\n"
        "esac\n"
        f"exec '{real_git}' \"$@\"\n")
    shim.chmod(0o755)
    r = run(sync)
    shim.unlink()
    assert r.returncode == code, r.stdout + r.stderr
    assert "OK: no canon mirror drift" in r.stdout
    assert len(local_sync_branches(root, env)) == 1
    assert worktrees(root, env) == []
    assert [list(d.iterdir()) for d in run_dirs(tmp_path)] == [[]]


def test_git_exit_code_75_is_not_reported_as_a_lock_timeout(sync):
    """A hook that makes `git worktree add` exit 75 is a Git failure, not a lock timeout.

    The hook runs after the checkout: the worktree exists and is registered.
    """
    root, origin, vault, env = sync
    hook = root / ".git/hooks/post-checkout"
    hook.write_text("#!/bin/sh\nexit 75\n")
    hook.chmod(0o755)
    r = run(sync)
    assert r.returncode == 75, r.stdout + r.stderr
    assert "worktree lock" not in r.stderr and "flock failed" not in r.stderr
    retained = worktrees(root, env)
    assert len(retained) == 1
    assert str(retained[0]) in r.stderr
    assert not Path(env["GH_CALLS"]).exists()


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
