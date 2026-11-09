#!/usr/bin/env python3
"""Tests de check-obsolete-rules.py : remplacement requis et ADR `proposed` en attente (Q4)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "check-obsolete-rules.py"
TODAY = "2026-11-10"


def write(vault: Path, rel: str, frontmatter: str, body: str = "# Titre\n") -> None:
    path = vault / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")


def run(vault: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(vault), "--json", *args],
        capture_output=True, text=True, check=False,
    )


def findings(vault: Path) -> tuple[int, list[dict]]:
    proc = run(vault, f"--today={TODAY}")
    return proc.returncode, json.loads(proc.stdout)["findings"]


def test_proposed_adr_older_than_30_days_warns_without_blocking(tmp_path):
    write(tmp_path, "ledger/decisions/adr/ADR-900-x.md", "id: ADR-900\nstatus: proposed\ndate: 2026-10-10\n")
    code, found = findings(tmp_path)
    assert code == 0
    assert [(f["rule"], f["severity"], f["file"]) for f in found] == [
        ("obsolete/proposed-stale", "warning", "ledger/decisions/adr/ADR-900-x.md"),
    ]
    assert "31 days" in found[0]["message"]


@pytest.mark.parametrize("frontmatter", [
    pytest.param("id: ADR-901\nstatus: proposed\ndate: 2026-10-11\n", id="30-jours-pile"),
    pytest.param("id: ADR-901\nstatus: accepted\ndate: 2026-01-01\n", id="accepte-ancien"),
    pytest.param("id: ADR-901\nstatus: deferred\ndate: 2026-01-01\n", id="reporte-ancien"),
    pytest.param("id: ADR-901\nstatus: proposed\ndate: 2026-12-01\n", id="date-future"),
])
def test_no_stale_warning(tmp_path, frontmatter):
    write(tmp_path, "ledger/decisions/adr/ADR-901-x.md", frontmatter)
    assert findings(tmp_path) == (0, [])


def test_quoted_date_is_read(tmp_path):
    write(tmp_path, "ledger/decisions/adr/ADR-902-x.md", 'id: ADR-902\nstatus: proposed\ndate: "2026-05-24"\n')
    _, found = findings(tmp_path)
    assert [f["rule"] for f in found] == ["obsolete/proposed-stale"]


def test_stale_rule_applies_to_adrs_only(tmp_path):
    write(tmp_path, "ledger/rules/rules-x.md", "status: proposed\ndate: 2026-01-01\n")
    assert findings(tmp_path) == (0, [])


def test_superseded_without_replacement_still_blocks(tmp_path):
    write(tmp_path, "ledger/decisions/adr/ADR-903-x.md", "id: ADR-903\nstatus: superseded\ndate: 2026-01-01\n")
    code, found = findings(tmp_path)
    assert code == 1
    assert [(f["rule"], f["severity"]) for f in found] == [("obsolete/replacement-required", "error")]


def test_invalid_today_is_an_error_not_a_green(tmp_path):
    proc = run(tmp_path, "--today=hier")
    assert proc.returncode == 2
    assert proc.stdout == ""
