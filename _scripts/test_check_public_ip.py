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


def run(vault: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(vault), *args],
        capture_output=True, text=True, check=False,
    )


def findings(vault: Path) -> tuple[int, list[dict]]:
    proc = run(vault, "--json")
    return proc.returncode, json.loads(proc.stdout)["findings"]


def test_public_address_warns_without_blocking_and_without_republishing_it(tmp_path):
    write(tmp_path, "ledger/knowledge/note.md", f"# Note\n\nServeur sur {PUBLIC}.\n")
    proc = run(tmp_path, "--json")
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
    code, found = findings(tmp_path)
    assert code == 0
    assert [(f["file"], f["lines"]) for f in found] == [("a.md", [1, 3])]


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
])
def test_non_public_or_non_address_is_ignored(tmp_path, line):
    write(tmp_path, "note.md", line + "\n")
    assert findings(tmp_path) == (0, [])


@pytest.mark.parametrize("rel", ["rules.yaml", "ci.yml", "policy.json", "notes.txt", "DOC.MD"])
def test_text_formats_are_scanned(tmp_path, rel):
    write(tmp_path, rel, f"host: {PUBLIC}\n")
    _, found = findings(tmp_path)
    assert [f["file"] for f in found] == [rel]


@pytest.mark.parametrize("rel", [
    "_scripts/fixture.md",
    ".git/COMMIT_EDITMSG.txt",
    ".obsidian/workspace.json",
    "node_modules/pkg/README.md",
    "ledger/diagram.png",
    "ledger/script.sh",
])
def test_out_of_scope_paths_are_not_scanned(tmp_path, rel):
    write(tmp_path, rel, f"{PUBLIC}\n")
    assert findings(tmp_path) == (0, [])


def test_excluded_name_only_excludes_directories(tmp_path):
    # Un fichier nommé comme un dossier exclu reste dans le périmètre.
    write(tmp_path, "ledger/node_modules.md", f"{PUBLIC}\n")
    _, found = findings(tmp_path)
    assert [f["file"] for f in found] == ["ledger/node_modules.md"]


def test_text_output_gives_lines_but_not_the_address(tmp_path):
    write(tmp_path, "note.md", f"x\n{PUBLIC}\n")
    proc = run(tmp_path)
    assert proc.returncode == 0
    assert "[WARNING] note.md (line 2)" in proc.stdout
    assert "1 warning(s)" in proc.stdout
    assert PUBLIC not in proc.stdout


def test_undecodable_bytes_do_not_crash(tmp_path):
    path = tmp_path / "note.md"
    path.write_bytes(b"\xff\xfe invalide\n" + PUBLIC.encode() + b"\n")
    code, found = findings(tmp_path)
    assert code == 0
    assert [f["lines"] for f in found] == [[2]]
