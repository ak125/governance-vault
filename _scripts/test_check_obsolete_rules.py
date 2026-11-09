#!/usr/bin/env python3
"""Tests de check-obsolete-rules.py : remplacement requis et ADR `proposed` en attente (Q4)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "check-obsolete-rules.py"
# Date de reference volontairement loin de la date reelle : si `--today` etait
# ignore, les fixtures datees de 2030 seraient dans le futur et rien ne sortirait.
TODAY = "2030-06-15"
STALE = "obsolete/proposed-stale"


def write(vault: Path, rel: str, frontmatter: str, body: str = "# Titre\n") -> None:
    path = vault / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")


def run(vault: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(vault), "--json", *args],
        capture_output=True, text=True, check=False,
    )


def findings(vault: Path, today: str = TODAY) -> tuple[int, list[dict]]:
    proc = run(vault, f"--today={today}")
    return proc.returncode, json.loads(proc.stdout)["findings"]


def test_proposed_adr_older_than_30_days_warns_without_blocking(tmp_path):
    write(tmp_path, "ledger/decisions/adr/ADR-900-x.md", "id: ADR-900\nstatus: proposed\ndate: 2030-05-15\n")
    code, found = findings(tmp_path)
    assert code == 0
    assert [(f["rule"], f["severity"], f["file"]) for f in found] == [
        (STALE, "warning", "ledger/decisions/adr/ADR-900-x.md"),
    ]
    assert "2030-05-15" in found[0]["message"]
    assert "Q4" in found[0]["message"]


@pytest.mark.parametrize("frontmatter", [
    pytest.param("id: ADR-901\nstatus: proposed\ndate: 2030-05-16\n", id="30-jours-pile"),
    pytest.param("id: ADR-901\nstatus: accepted\ndate: 2026-01-01\n", id="accepte-ancien"),
    pytest.param("id: ADR-901\nstatus: deferred\ndate: 2026-01-01\n", id="reporte-ancien"),
    pytest.param("id: ADR-901\nstatus: proposed\ndate: 2031-06-15\n", id="date-future-lointaine"),
    pytest.param("id: ADR-901\nstatus: proposed\n", id="date-absente"),
    pytest.param("id: ADR-901\nstatus: proposed\ndate: bientot\n", id="date-illisible"),
    pytest.param("id: ADR-901\nstatus: proposed\ndate: 12\n", id="date-non-textuelle"),
])
def test_no_stale_warning(tmp_path, frontmatter):
    write(tmp_path, "ledger/decisions/adr/ADR-901-x.md", frontmatter)
    assert findings(tmp_path) == (0, [])


@pytest.mark.parametrize("date_value", [
    pytest.param('"2026-05-24"', id="chaine-entre-guillemets"),
    pytest.param("2026-05-24T10:00:00", id="horodatage-yaml"),
])
def test_date_forms_are_read(tmp_path, date_value):
    write(tmp_path, "ledger/decisions/adr/ADR-902-x.md", f"id: ADR-902\nstatus: proposed\ndate: {date_value}\n")
    code, found = findings(tmp_path)
    assert code == 0
    assert [f["rule"] for f in found] == [STALE]
    assert "2026-05-24" in found[0]["message"]


def test_message_is_identical_from_one_week_to_the_next(tmp_path):
    # vault-weekly-lint.yml deduplique ses issues sur check|file|rule|message.
    write(tmp_path, "ledger/decisions/adr/ADR-904-x.md", "id: ADR-904\nstatus: proposed\ndate: 2030-01-01\n")
    _, first = findings(tmp_path, "2030-06-15")
    _, later = findings(tmp_path, "2030-06-22")
    assert first == later
    assert len(first) == 1


def test_findings_come_out_in_path_order(tmp_path):
    for number in (907, 905, 906):
        write(tmp_path, f"ledger/decisions/adr/ADR-{number}-x.md", f"id: ADR-{number}\nstatus: proposed\ndate: 2030-01-01\n")
    _, found = findings(tmp_path)
    assert [f["file"] for f in found] == [
        f"ledger/decisions/adr/ADR-{number}-x.md" for number in (905, 906, 907)
    ]


@pytest.mark.parametrize("rel", [
    "ledger/rules/rules-x.md",
    "ledger/policies/policy-x.md",
    "ledger/decisions/adr/README.md",
    "ledger/decisions/adr/brouillons/ADR-908-x.md",
])
def test_stale_rule_applies_to_adr_files_only(tmp_path, rel):
    write(tmp_path, rel, "status: proposed\ndate: 2026-01-01\n")
    assert findings(tmp_path) == (0, [])


def test_superseded_without_replacement_still_blocks(tmp_path):
    write(tmp_path, "ledger/decisions/adr/ADR-903-x.md", "id: ADR-903\nstatus: superseded\ndate: 2026-01-01\n")
    code, found = findings(tmp_path)
    assert code == 1
    assert [(f["rule"], f["severity"]) for f in found] == [("obsolete/replacement-required", "error")]


@pytest.mark.parametrize("args", [
    pytest.param(["--today=hier"], id="pas-une-date"),
    pytest.param(["--today=2030-06-15zzz"], id="suffixe-parasite"),
    pytest.param(["--today=2030-02-30"], id="date-inexistante"),
    pytest.param(["--today", "2030-06-15"], id="forme-avec-espace"),
])
def test_malformed_today_is_an_error_not_a_green(tmp_path, args):
    write(tmp_path, "ledger/decisions/adr/ADR-909-x.md", "id: ADR-909\nstatus: proposed\ndate: 2026-01-01\n")
    proc = run(tmp_path, *args)
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert "--today=YYYY-MM-DD" in proc.stderr


def test_default_reference_date_is_today(tmp_path):
    # Sans --today : un ADR `proposed` de 2026-01-01 est en attente a toute date d'execution reelle.
    write(tmp_path, "ledger/decisions/adr/ADR-910-x.md", "id: ADR-910\nstatus: proposed\ndate: 2026-01-01\n")
    proc = run(tmp_path)
    assert proc.returncode == 0
    assert [f["rule"] for f in json.loads(proc.stdout)["findings"]] == [STALE]
