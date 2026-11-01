#!/usr/bin/env python3
"""Tests de _scripts/setup-branch-protection.sh.

Trois contrats :
- la liste des checks requis ne designe que des jobs rapportes sur chaque PR vers main
  (un check qu'aucun job ne rapporte bloque toutes les PR), et la doc la reprend telle quelle ;
- le merge rebase est interdit au niveau du depot (il recree les commits sans signature) ;
- le script ne declare jamais conforme une configuration qui differe de sa demande
  (`gh` est remplace par un stub : aucun appel reseau).
"""
from __future__ import annotations

import json
import os
import re
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "_scripts" / "setup-branch-protection.sh"
WORKFLOWS = REPO / ".github" / "workflows"
DOC = REPO / "99-meta" / "branch-protection.md"
ACTIONS_APP_ID = 15368


def declared_body():
    m = re.search(r"<<'JSON'\n(.*?)\nJSON\n", SCRIPT.read_text(encoding="utf-8"), re.S)
    assert m, "bloc JSON introuvable dans setup-branch-protection.sh"
    return json.loads(m.group(1))


def declared_merge():
    m = re.search(r"^MERGE='(.*)'$", SCRIPT.read_text(encoding="utf-8"), re.M)
    assert m, "declaration MERGE introuvable dans setup-branch-protection.sh"
    return json.loads(m.group(1))


def required_contexts():
    return [c["context"] for c in declared_body()["required_status_checks"]["checks"]]


def jobs_reported_on_every_pr_to_main():
    """Noms de check des jobs d'un workflow declenche par toute PR vers main."""
    names = {}
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        doc = yaml.safe_load(wf.read_text(encoding="utf-8"))
        on = doc.get("on", doc.get(True))  # PyYAML lit la cle `on` comme le booleen True
        if isinstance(on, str):
            on = {on: None}
        if isinstance(on, list):
            on = {k: None for k in on}
        if "pull_request" not in on:
            continue
        pr = on["pull_request"] or {}
        if "paths" in pr or "paths-ignore" in pr:
            continue
        if "branches" in pr and "main" not in pr["branches"]:
            continue
        for key, job in doc["jobs"].items():
            names[job.get("name", key)] = (wf.name, job)
    return names


def test_body_shape():
    body = declared_body()
    rsc = body["required_status_checks"]
    assert rsc["strict"] is True
    assert "contexts" not in rsc, "`contexts` est deprecie et ignore sans erreur un nom jamais observe"
    contexts = required_contexts()
    assert len(contexts) == len(set(contexts)), "check requis en double"
    assert {c["app_id"] for c in rsc["checks"]} == {ACTIONS_APP_ID}
    assert body["enforce_admins"] is True
    assert body["restrictions"] is None


def test_each_required_check_is_reported_on_every_pr():
    jobs = jobs_reported_on_every_pr_to_main()
    missing = [c for c in required_contexts() if c not in jobs]
    assert not missing, f"aucun job ne rapporte ces checks sur une PR vers main : {missing}"
    # Un job saute par `if:` rapporte « skipped », que GitHub compte comme un succes.
    conditional = [c for c in required_contexts() if "if" in jobs[c][1]]
    assert not conditional, f"checks requis conditionnels : {conditional}"


def test_signatures_are_required():
    # G3 accepte toute signature valide ; seul GitHub verifie que la cle est rattachee
    # a un compte dont l'e-mail committer est verifie (99-meta/signing-policy.md).
    assert declared_body()["required_signatures"] is True


def test_rebase_merge_is_forbidden():
    # Le merge rebase recree les commits de la PR sans signature (99-meta/branch-protection.md).
    assert declared_merge() == {"allow_squash_merge": True, "allow_rebase_merge": False}


def test_doc_merge_rows_match_script():
    text = DOC.read_text(encoding="utf-8")
    for field, value in declared_merge().items():
        row = re.search(rf"^\| `{field}` \| `(true|false)` \|", text, re.M)
        assert row, f"ligne `{field}` introuvable dans la configuration de branch-protection.md"
        assert json.loads(row.group(1)) is value


def test_doc_config_row_matches_script():
    text = DOC.read_text(encoding="utf-8")
    row = re.search(r"^\| `required_signatures` \| `(true|false)` \|", text, re.M)
    assert row, "ligne `required_signatures` introuvable dans la configuration de branch-protection.md"
    assert json.loads(row.group(1)) is declared_body()["required_signatures"]


def test_doc_table_matches_script():
    text = DOC.read_text(encoding="utf-8")
    section = re.search(r"^## Required Status Checks.*?$(.*?)^## ", text, re.S | re.M)
    assert section, "section « Required Status Checks » introuvable"
    in_doc = re.findall(r"^\| `([^`]+)` \|", section.group(1), re.M)
    assert sorted(in_doc) == sorted(required_contexts())


# --- comportement du script, `gh` remplace par un stub -------------------------------------

STUB_GH = """#!/usr/bin/env bash
# api -X <methode> <ep> ... : journalise, et le corps envoye s'il y en a un (--input),
# dans $STUB_LOG.<methode>.body ;
# api <ep> : renvoie $STUB_GET pour la protection, $STUB_REPO pour le depot
# (echoue si le fichier correspondant est absent).
echo "$*" >> "$STUB_LOG"
if [[ "$1" == api && "$2" == -X ]]; then
  if [[ " $* " == *" --input "* ]]; then cat > "$STUB_LOG.$3.body"; fi
  exit 0
fi
case "$2" in
  */protection) f="${STUB_GET:-}" ;;
  *) f="${STUB_REPO:-}" ;;
esac
[[ -n "$f" ]] || exit 1
cat "$f"
"""


def get_response(body):
    """Forme de GET .../branches/main/protection correspondant a une demande PUT."""
    rsc = body["required_status_checks"]
    return {
        "required_status_checks": {
            "strict": rsc["strict"],
            "contexts": [c["context"] for c in rsc["checks"]],
            "checks": rsc["checks"],
        },
        "required_pull_request_reviews": {**body["required_pull_request_reviews"],
                                          "require_last_push_approval": False},
        "required_signatures": {"enabled": body["required_signatures"]},
        "enforce_admins": {"enabled": body["enforce_admins"]},
        "required_linear_history": {"enabled": body["required_linear_history"]},
        "allow_force_pushes": {"enabled": body["allow_force_pushes"]},
        "allow_deletions": {"enabled": body["allow_deletions"]},
        "block_creations": {"enabled": body["block_creations"]},
        "required_conversation_resolution": {"enabled": body["required_conversation_resolution"]},
        "lock_branch": {"enabled": False},
        "allow_fork_syncing": {"enabled": False},
    }


def repo_response(merge):
    """Forme (abregee) de GET repos/<depot> correspondant a une demande PATCH."""
    return {"full_name": "ak125/governance-vault", "allow_merge_commit": True,
            "allow_auto_merge": True, "delete_branch_on_merge": True, **merge}


@pytest.fixture
def gh(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    stub = bindir / "gh"
    stub.write_text(STUB_GH, encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "gh.log"
    log.touch()
    env = {**os.environ, "PATH": f"{bindir}:{os.environ['PATH']}", "STUB_LOG": str(log)}

    def run(*args, get=None, repo=repo_response(declared_merge())):
        for var, value in (("STUB_GET", get), ("STUB_REPO", repo)):
            if value is not None:
                p = tmp_path / f"{var}.json"
                p.write_text(json.dumps(value), encoding="utf-8")
                env[var] = str(p)
        r = subprocess.run(["bash", str(SCRIPT), *args], env=env, capture_output=True, text=True)
        return r, log.read_text(encoding="utf-8")

    return run


def test_check_conforming_protection_is_green_and_read_only(gh):
    r, log = gh("--check", get=get_response(declared_body()))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "-X" not in log


def test_check_detects_missing_check(gh):
    got = get_response(declared_body())
    got["required_status_checks"]["checks"] = got["required_status_checks"]["checks"][:-1]
    r, log = gh("--check", get=got)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "-X" not in log


def test_check_detects_check_bound_to_another_app(gh):
    got = get_response(declared_body())
    got["required_status_checks"]["checks"][0]["app_id"] = None
    r, _ = gh("--check", get=got)
    assert r.returncode == 1, r.stdout + r.stderr


def test_check_detects_admin_bypass(gh):
    got = get_response(declared_body())
    got["enforce_admins"]["enabled"] = False
    r, _ = gh("--check", get=got)
    assert r.returncode == 1, r.stdout + r.stderr


def test_check_detects_signatures_not_enforced(gh):
    got = get_response(declared_body())
    got["required_signatures"]["enabled"] = False
    r, log = gh("--check", get=got)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "-X" not in log


def test_check_detects_rebase_merge_allowed(gh):
    r, log = gh("--check", get=get_response(declared_body()),
                repo=repo_response({**declared_merge(), "allow_rebase_merge": True}))
    assert r.returncode == 1, r.stdout + r.stderr
    assert "methodes de merge" in r.stderr
    assert "-X" not in log


def test_check_detects_squash_merge_disabled(gh):
    r, _ = gh("--check", get=get_response(declared_body()),
              repo=repo_response({**declared_merge(), "allow_squash_merge": False}))
    assert r.returncode == 1, r.stdout + r.stderr


def test_check_reports_both_differences(gh):
    # Une protection non conforme ne masque pas des methodes de merge non conformes.
    got = get_response(declared_body())
    got["enforce_admins"]["enabled"] = False
    r, _ = gh("--check", get=got, repo=repo_response({**declared_merge(), "allow_rebase_merge": True}))
    assert r.returncode == 1, r.stdout + r.stderr
    assert "la protection" in r.stderr and "methodes de merge" in r.stderr


def test_unreadable_repo_settings_are_not_green(gh):
    r, _ = gh("--check", get=get_response(declared_body()), repo=None)
    assert r.returncode == 2, r.stdout + r.stderr


def test_apply_sets_signatures_and_merge_methods(gh, tmp_path):
    # Le PUT ne porte pas required_signatures : la sous-ressource est appelee apres lui ;
    # les methodes de merge sont un reglage du depot (PATCH), applique ensuite.
    r, log = gh(get=get_response(declared_body()))
    assert r.returncode == 0, r.stdout + r.stderr
    calls = [line for line in log.splitlines() if " -X " in f" {line} "]
    assert [c.split()[2] for c in calls] == ["PUT", "POST", "PATCH"]
    assert calls[1].split()[3].endswith("/protection/required_signatures")
    assert calls[2].split()[3] == "repos/ak125/governance-vault"
    sent = json.loads((tmp_path / "gh.log.PUT.body").read_text(encoding="utf-8"))
    expected = {k: v for k, v in declared_body().items() if k != "required_signatures"}
    assert sent == expected
    patched = json.loads((tmp_path / "gh.log.PATCH.body").read_text(encoding="utf-8"))
    assert patched == declared_merge()


def test_apply_fails_when_merge_methods_readback_differs(gh):
    r, log = gh(get=get_response(declared_body()),
                repo=repo_response({**declared_merge(), "allow_rebase_merge": True}))
    assert r.returncode == 1, r.stdout + r.stderr
    assert "-X PATCH" in log


def test_apply_fails_when_readback_differs(gh):
    # Le PUT « reussit » mais la relecture montre un check abandonne : jamais un vert.
    got = get_response(declared_body())
    got["required_status_checks"]["checks"] = got["required_status_checks"]["checks"][1:]
    r, log = gh(get=got)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "-X PUT" in log


def test_apply_green_when_readback_matches(gh):
    r, log = gh(get=get_response(declared_body()))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "-X PUT" in log


def test_unreadable_protection_is_not_green(gh):
    r, _ = gh("--check")
    assert r.returncode == 2, r.stdout + r.stderr


def test_unknown_argument_is_refused(gh):
    r, log = gh("--force")
    assert r.returncode == 2
    assert log == ""
