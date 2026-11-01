"""check-adr-id-collisions.py : classement des fichiers ADR des PR ouvertes
et refus de conclure quand une source manque.

git et gh sont remplaces par un faux executant ; aucun appel reseau.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "adr_id_collisions", Path(__file__).resolve().parent / "check-adr-id-collisions.py"
)
col = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(col)

SHA = "a" * 40
ADR = "ledger/decisions/adr/"
MAIN = [ADR + "ADR-001-one.md", ADR + "ADR-002-two.md"]


def pr(number, *paths, total=None):
    return {
        "number": number,
        "title": f"pr {number}",
        "headRefOid": "b" * 40,
        "changedFiles": len(paths) if total is None else total,
        "files": [{"path": p} for p in paths],
    }


def runner(main=MAIN, prs=(), remote=SHA, fail=(), rest=None):
    def run(cmd):
        if cmd[0] == "git":
            step = "rev-parse" if "rev-parse" in cmd else "ls-tree"
        elif cmd[:3] == ["gh", "pr", "list"]:
            step = "list"
        elif "--paginate" in cmd:
            step = "paginate"
        else:
            step = "ref"
        if step in fail:
            raise subprocess.CalledProcessError(1, cmd)
        return {
            "rev-parse": SHA + "\n",
            "ls-tree": "\0".join(main) + "\0",
            "ref": remote + "\n",
            "list": json.dumps(list(prs)),
            "paginate": "\n".join((rest or {}).get(cmd[3], [])),
        }[step]
    return run


def check(capsys, *args, **kw):
    code = col.main(["check", "/vault", *args], runner(**kw))
    return code, capsys.readouterr().out


def kinds(out):
    return [f["kind"] for f in json.loads(out)["findings"]]


def test_complete_without_collision(capsys):
    code, out = check(capsys, prs=[pr(1, ADR + "ADR-003-new.md", "ops/moc/MOC-Decisions.md")])
    assert code == 0
    assert "aucune collision" in out
    assert "ADR-004" in out


def test_collision_with_main(capsys):
    code, out = check(capsys, "--json", prs=[pr(5, ADR + "ADR-002-other.md")])
    assert code == 1
    assert kinds(out) == ["collision-main"]
    assert json.loads(out)["next_free"] == "ADR-003"


def test_modifying_an_existing_adr_is_not_a_collision(capsys):
    code, out = check(capsys, prs=[pr(5, ADR + "ADR-002-two.md")])
    assert code == 0
    assert "1 fichier(s) ADR existant(s) modifie(s)" in out


def test_collision_between_open_prs(capsys):
    prs = [pr(214, ADR + "ADR-052-a.md"), pr(241, ADR + "ADR-052-b.md"), pr(300, ADR + "ADR-053-c.md")]
    code, out = check(capsys, "--json", prs=prs)
    assert code == 1
    found = json.loads(out)["findings"]
    assert [f["kind"] for f in found] == ["collision-pr"]
    assert [e["pr"] for e in found[0]["prs"]] == [214, 241]


def test_duplicates_inside_a_pr_and_on_main(capsys):
    main = MAIN + [ADR + "ADR-002-again.md"]
    prs = [pr(7, ADR + "ADR-009-a.md", ADR + "ADR-009-b.md")]
    code, out = check(capsys, "--json", main=main, prs=prs)
    assert code == 1
    assert kinds(out) == ["doublon-main", "doublon-pr"]


def test_unreadable_pr_list_is_incomplete(capsys):
    code, out = check(capsys, fail={"list"})
    assert code == 2
    assert "INCOMPLET" in out
    assert "aucune collision" not in out
    assert "Prochain identifiant" not in out


def test_incomplete_json_has_no_next_free(capsys):
    code, out = check(capsys, "--json", fail={"ref"})
    assert code == 2
    report = json.loads(out)
    assert report["complete"] is False
    assert report["next_free"] is None


def test_partial_findings_stay_under_incomplete(capsys):
    code, out = check(capsys, prs=[pr(5, ADR + "ADR-002-other.md")], remote="c" * 40)
    assert code == 2
    assert "[COLLISION main] ADR-002" in out
    assert "git fetch origin" in out
    assert "Prochain identifiant" not in out


def test_unreadable_main_is_incomplete(capsys):
    code, out = check(capsys, fail={"rev-parse"})
    assert code == 2
    assert "main illisible" in out


def test_pr_list_at_limit_is_incomplete(capsys):
    code, out = check(capsys, "--limit", "2", prs=[pr(1), pr(2)])
    assert code == 2
    assert "limite 2" in out


def test_truncated_file_list_is_completed_through_rest(capsys):
    truncated = pr(351, "a.md", total=2)
    code, out = check(capsys, "--json", prs=[truncated], rest={"repos/ak125/governance-vault/pulls/351/files": ["a.md", ADR + "ADR-001-x.md"]})
    assert code == 1
    assert kinds(out) == ["collision-main"]


def test_truncated_file_list_without_rest_is_incomplete(capsys):
    code, out = check(capsys, prs=[pr(351, "a.md", total=2)], fail={"paginate"})
    assert code == 2
    assert "#351" in out


def test_missing_file_list_is_incomplete(capsys):
    broken = pr(9)
    broken["files"] = None
    code, out = check(capsys, prs=[broken])
    assert code == 2
    assert "#9" in out


def test_main_listing_is_root_relative_and_nul_separated():
    calls = []
    run = runner()

    def spy(cmd):
        calls.append(cmd)
        return run(cmd)

    col.collect("/vault", col.DEFAULT_REPO, 500, spy)
    ls_tree = next(c for c in calls if "ls-tree" in c)
    assert "--full-tree" in ls_tree and "-z" in ls_tree


def test_main_without_adr_is_incomplete(capsys):
    code, out = check(capsys, main=[], prs=[pr(7, ADR + "ADR-002-x.md")])
    assert code == 2
    assert "aucun ADR" in out
    assert "Prochain identifiant" not in out


def test_unreadable_main_listing_is_incomplete(capsys):
    code, out = check(capsys, fail={"ls-tree"})
    assert code == 2
    assert "main illisible" in out


def test_empty_github_main_is_incomplete(capsys):
    code, out = check(capsys, remote="")
    assert code == 2
    assert "reponse vide" in out


def test_non_ascii_adr_path_on_main_is_read(capsys):
    code, out = check(capsys, "--json", main=[ADR + "ADR-001-d\u00e9cision.md"], prs=[pr(7, ADR + "ADR-001-x.md")])
    assert code == 1
    assert kinds(out) == ["collision-main"]


def test_invalid_arguments_exit_2(capsys):
    for args in (["--limit"], ["--limit", "abc"], ["--repo"]):
        assert col.main(["check", "/vault", *args], runner()) == 2
