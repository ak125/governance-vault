"""check-adr-supersedes.py : unicite des identifiants dans l'arbre et accord
id / nom de fichier (regles adr/unique-id et adr/id-matches-filename).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check-adr-supersedes.py"


def vault(tmp_path, files):
    adr = tmp_path / "ledger" / "decisions" / "adr"
    adr.mkdir(parents=True)
    (tmp_path / "ledger" / "rules").mkdir()
    for name, adr_id in files.items():
        (adr / name).write_text(f"---\nid: {adr_id}\nstatus: proposed\n---\n\n# {adr_id}\n", encoding="utf-8")
    return tmp_path


def run(root):
    proc = subprocess.run([sys.executable, str(SCRIPT), str(root), "--json"], capture_output=True, text=True)
    return proc.returncode, [f["rule"] for f in json.loads(proc.stdout)["findings"]]


def test_distinct_ids_pass(tmp_path):
    assert run(vault(tmp_path, {"ADR-001-a.md": "ADR-001", "ADR-002-b.md": "ADR-002"})) == (0, [])


def test_two_files_with_one_id_fail(tmp_path):
    code, rules = run(vault(tmp_path, {"ADR-001-a.md": "ADR-001", "ADR-001-b.md": "ADR-001"}))
    assert code == 1
    assert rules == ["adr/unique-id"]


def test_frontmatter_id_must_match_file_name(tmp_path):
    code, rules = run(vault(tmp_path, {"ADR-001-a.md": "ADR-001", "ADR-002-b.md": "ADR-001"}))
    assert code == 1
    assert rules == ["adr/id-matches-filename", "adr/unique-id"]
