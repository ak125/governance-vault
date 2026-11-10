#!/usr/bin/env python3
"""Tests de check-public-ip.py : adresses IPv4 publiques signalées, sans bloquer ni les republier."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "check-public-ip.py"
RULE = "hygiene/public-ip"
# Résolveurs DNS publics connus : adresses routables qui ne désignent aucun hôte du projet.
PUBLIC = "8.8.8.8"
OTHER_PUBLIC = "1.1.1.1"


def write(vault: Path, rel: str, text: str) -> None:
    path = vault / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, check=False, cwd=cwd,
    )


def findings(vault: Path) -> tuple[int, list[dict]]:
    proc = run(str(vault), "--json")
    return proc.returncode, json.loads(proc.stdout)["findings"]


def test_public_address_warns_without_blocking_and_without_republishing_it(tmp_path):
    write(tmp_path, "ledger/knowledge/note.md", f"# Note\n\nServeur sur {PUBLIC}.\n")
    proc = run(str(tmp_path), "--json")
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["check"] == "public-ip"
    assert data["summary"] == {"error": 0, "warning": 1, "info": 0}
    assert [(f["rule"], f["severity"], f["file"], f["lines"]) for f in data["findings"]] == [
        (RULE, "warning", "ledger/knowledge/note.md", [3]),
    ]
    assert PUBLIC not in proc.stdout


def test_one_finding_per_file_with_every_line(tmp_path):
    write(tmp_path, "a.md", f"{PUBLIC}\nrien\n{OTHER_PUBLIC} et {PUBLIC}\n")
    write(tmp_path, "b.md", "rien\n")
    proc = run(str(tmp_path), "--json")
    data = json.loads(proc.stdout)
    assert proc.returncode == 0
    assert [(f["file"], f["lines"]) for f in data["findings"]] == [("a.md", [1, 3])]
    # Le résumé compte les fichiers (un finding par fichier), pas les lignes.
    assert data["summary"]["warning"] == 1


def test_findings_are_sorted_by_path(tmp_path):
    for rel in ("z.md", "a/b.md", "m.md", "a.md"):
        write(tmp_path, rel, f"{PUBLIC}\n")
    _, found = findings(tmp_path)
    assert [f["file"] for f in found] == ["a.md", "a/b.md", "m.md", "z.md"]


def test_message_is_stable_across_files_and_lines(tmp_path):
    write(tmp_path, "a.md", f"{PUBLIC}\n")
    write(tmp_path, "sub/b.md", f"\n\n{OTHER_PUBLIC}\n")
    _, found = findings(tmp_path)
    assert len(found) == 2
    assert len({f["message"] for f in found}) == 1


@pytest.mark.parametrize("line", [
    pytest.param(f"curl http://{PUBLIC}:3000/health", id="url-avec-port"),
    pytest.param(f"ssh root@{PUBLIC} uptime", id="apres-arobase"),
    pytest.param(f"affected_systems: [vps-dev-{PUBLIC}, redis]", id="apres-tiret"),
    pytest.param(f"allow {PUBLIC}/32", id="cidr"),
    pytest.param(f"Le serveur est {PUBLIC}.", id="fin-de-phrase"),
    pytest.param(f"VPS ({PUBLIC})", id="parentheses"),
    pytest.param(f"`{PUBLIC}`", id="code"),
    pytest.param(f"| DEV {PUBLIC} |", id="cellule-de-table"),
    pytest.param(f"_{PUBLIC}_", id="italique-markdown"),
    pytest.param(f"redis_host_{PUBLIC}", id="apres-soulignement"),
    pytest.param(f"{PUBLIC}_redis", id="avant-soulignement"),
    pytest.param(f"static.{PUBLIC}.clients.example.net", id="nom-rdns"),
    pytest.param(f"voir...{PUBLIC}", id="apres-points-de-suspension"),
    pytest.param(f"de 10.0.0.5 vers {PUBLIC}", id="apres-une-adresse-privee"),
    pytest.param(f'{{"log": "connexion\\n{PUBLIC} refusee"}}', id="apres-echappement-n"),
    pytest.param(f'printf "hote\\t{PUBLIC}"', id="apres-echappement-t"),
    pytest.param(f"https://example.net/?u=http%3A%2F%2F{PUBLIC}%2Fhealth", id="url-encodee"),
    pytest.param(f"mailto:root%40{PUBLIC}", id="arobase-encodee"),
])
def test_public_address_is_found_in_context(tmp_path, line):
    write(tmp_path, "note.md", line + "\n")
    _, found = findings(tmp_path)
    assert [f["lines"] for f in found] == [[1]]


@pytest.mark.parametrize("line", [
    pytest.param("127.0.0.1:6379", id="loopback"),
    pytest.param("10.0.0.5", id="prive-10"),
    pytest.param("172.16.0.2", id="prive-172"),
    pytest.param("192.168.1.10", id="prive-192"),
    pytest.param("169.254.169.254", id="link-local"),
    pytest.param("100.64.0.1", id="cgnat"),
    pytest.param("192.0.2.1", id="documentation"),
    pytest.param("0.0.0.0:3000", id="non-specifiee"),
    pytest.param("255.255.255.255", id="diffusion"),
    pytest.param("224.0.0.1", id="multicast"),
    pytest.param("Chromium 120.0.6099.109", id="version-octet-trop-grand"),
    pytest.param("image v2.0.9.1", id="version-prefixee"),
    pytest.param("build 1.2.3.4.5", id="cinq-segments"),
    pytest.param("08.8.8.8", id="zero-initial"),
    pytest.param("section 8.8.8", id="trois-segments"),
    pytest.param(f"{PUBLIC}a", id="suivie-d-une-lettre"),
    pytest.param("8.8.8.1234", id="dernier-segment-trop-long"),
    pytest.param(f"x{PUBLIC}", id="precedee-d-une-lettre"),
    pytest.param(f"n{PUBLIC}", id="lettre-n-sans-barre-oblique"),
])
def test_non_public_or_non_address_is_ignored(tmp_path, line):
    write(tmp_path, "note.md", line + "\n")
    assert findings(tmp_path) == (0, [])


@pytest.mark.parametrize("rel", [
    "rules.yaml", "ci.yml", "policy.json", "notes.txt", "DOC.MD",
    "_scripts/deploy.sh", "_scripts/tool.py", "policies/vault.rego", "ops/fix.patch",
    "ops/query.sql", ".githooks/pre-push", "Makefile", "notes.md.bak",
    ".obsidian/workspace.json",           # non ignoré par git : peut être publié
])
def test_every_text_file_is_scanned_whatever_its_extension(tmp_path, rel):
    write(tmp_path, rel, f"host: {PUBLIC}\n")
    _, found = findings(tmp_path)
    assert [f["file"] for f in found] == [rel]


@pytest.mark.parametrize("rel", [
    ".git/COMMIT_EDITMSG",
    "node_modules/pkg/README.md",
    "ledger/node_modules/pkg/README.md",
    "_scripts/__pycache__/x.txt",
    "_scripts/check-public-ip.py",
    "_scripts/test_check_public_ip.py",
])
def test_excluded_paths_are_not_scanned(tmp_path, rel):
    write(tmp_path, rel, f"{PUBLIC}\n")
    assert findings(tmp_path) == (0, [])


@pytest.mark.parametrize("rel", [
    "ledger/node_modules",                # fichier qui porte le nom d'un dossier exclu
    "ledger/node_modules.md",
    "ledger/check-public-ip.py",          # même nom que le script, ailleurs que dans _scripts/
    "ledger/_scripts/test_check_public_ip.py",
])
def test_exclusions_are_exact(tmp_path, rel):
    write(tmp_path, rel, f"{PUBLIC}\n")
    _, found = findings(tmp_path)
    assert [f["file"] for f in found] == [rel]


def test_note_with_null_bytes_is_still_read(tmp_path):
    # Une note abîmée (octets nuls en fin de fichier) ne sort pas du contrôle.
    (tmp_path / "note.md").write_bytes(b"x" * 20000 + b"\n" + PUBLIC.encode() + b"\n" + b"\0" * 504)
    _, found = findings(tmp_path)
    assert [(f["file"], f["lines"]) for f in found] == [("note.md", [2])]


def test_utf16_file_is_read(tmp_path):
    (tmp_path / "export.txt").write_bytes(f"hote\n{PUBLIC}\n".encode("utf-16"))
    _, found = findings(tmp_path)
    assert [(f["file"], f["lines"]) for f in found] == [("export.txt", [2])]


def test_symlinked_directory_is_not_followed(tmp_path):
    vault, outside = tmp_path / "vault", tmp_path / "ailleurs"
    write(outside, "note.md", f"{PUBLIC}\n")
    vault.mkdir()
    (vault / "lien").symlink_to(outside, target_is_directory=True)
    assert findings(vault) == (0, [])


def test_non_utf8_file_name_does_not_crash_text_output(tmp_path):
    name = b"note-\xff.md"
    with open(bytes(tmp_path) + b"/" + name, "wb") as handle:
        handle.write(PUBLIC.encode() + b"\n")
    proc = run(str(tmp_path))
    assert proc.returncode == 0
    assert "1 warning(s)" in proc.stdout


def test_directory_named_like_a_file_is_not_read(tmp_path):
    (tmp_path / "dossier.md").mkdir()
    write(tmp_path, "dossier.md/note.md", f"{PUBLIC}\n")
    _, found = findings(tmp_path)
    assert [f["file"] for f in found] == ["dossier.md/note.md"]


def test_dangling_symlink_is_ignored(tmp_path):
    (tmp_path / "casse.md").symlink_to(tmp_path / "absent.md")
    assert findings(tmp_path) == (0, [])


def test_line_numbers_follow_newlines_only(tmp_path):
    # Saut de page et séparateur de ligne Unicode : un éditeur n'y voit pas une fin de ligne.
    write(tmp_path, "note.md", f"a\x0cb c\n{PUBLIC}\n")
    _, found = findings(tmp_path)
    assert [f["lines"] for f in found] == [[2]]


def test_text_output_gives_lines_but_not_the_address(tmp_path):
    write(tmp_path, "note.md", f"x\n{PUBLIC}\n")
    proc = run(str(tmp_path))
    assert proc.returncode == 0
    assert "[WARNING] note.md (line 2)" in proc.stdout
    assert "1 warning(s)" in proc.stdout
    assert "(1 file(s) scanned)" in proc.stdout
    assert PUBLIC not in proc.stdout


def test_undecodable_bytes_do_not_crash(tmp_path):
    path = tmp_path / "note.md"
    path.write_bytes(b"\xff\xfe invalide\n" + PUBLIC.encode() + b"\n")
    code, found = findings(tmp_path)
    assert code == 0
    assert [f["lines"] for f in found] == [[2]]


def test_json_flag_may_come_before_the_path(tmp_path):
    write(tmp_path, "note.md", f"{PUBLIC}\n")
    proc = run("--json", str(tmp_path))
    assert proc.returncode == 0
    assert [f["file"] for f in json.loads(proc.stdout)["findings"]] == ["note.md"]


def test_default_path_is_the_current_directory(tmp_path):
    write(tmp_path, "note.md", f"{PUBLIC}\n")
    proc = run("--json", cwd=tmp_path)
    assert proc.returncode == 0
    assert [f["file"] for f in json.loads(proc.stdout)["findings"]] == ["note.md"]


@pytest.mark.parametrize("target", ["absent", "note.md"])
def test_path_that_is_not_a_directory_is_an_error_not_a_clean_result(tmp_path, target):
    write(tmp_path, "note.md", f"{PUBLIC}\n")
    proc = run(str(tmp_path / target), "--json")
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert "not a directory" in proc.stderr


def test_unknown_option_is_an_error(tmp_path):
    proc = run(str(tmp_path), "--jsno")
    assert proc.returncode == 2
    assert proc.stdout == ""
