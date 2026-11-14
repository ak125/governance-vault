#!/usr/bin/env python3
"""Tests de check-canon-backlinks.py : un fichier canon du monorepo est référencé par son chemin.

Un wikilink du vault se résout dans le vault (ADR-127) : il ne désigne jamais un fichier du monorepo.
Les fixtures reproduisent les faux positifs d'avant le correctif : `[[architecture]]` vers le document
du vault créditait `.spec/00-canon/architecture.md`, `[[README]]` créditait tout `README.md` canon,
et un chemin cité entre backticks n'était pas lu.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check-canon-backlinks.py"


def write(root: Path, rel: str, text: str = "# Doc\n") -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def unreferenced(vault: Path, mono: Path) -> dict[str, str]:
    """Fichiers canon signalés, chemin relatif au monorepo → sévérité."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(vault), "--monorepo", str(mono), "--json"],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    return {f["file"]: f["severity"] for f in report["findings"]}


def canon(mono: Path, rel: str) -> str:
    write(mono, f".spec/00-canon/{rel}")
    return f".spec/00-canon/{rel}"


# --- Faux positifs d'origine -----------------------------------------------------------------------


def test_wikilink_to_a_vault_homonym_does_not_credit_the_canon_file(tmp_path):
    vault, mono = tmp_path / "vault", tmp_path / "mono"
    write(vault, "ledger/knowledge/architecture.md")
    write(vault, "ops/moc/MOC-Knowledge.md", "# MOC\n\n[[architecture]]\n")
    target = canon(mono, "architecture.md")
    assert target in unreferenced(vault, mono)


def test_readme_link_does_not_credit_a_canon_readme(tmp_path):
    vault, mono = tmp_path / "vault", tmp_path / "mono"
    write(vault, "ops/moc/MOC-Governance.md", "# MOC\n\n[[/README|README]] et [[README]]\n")
    target = canon(mono, "commerce-runtime/README.md")
    assert target in unreferenced(vault, mono)


def test_path_cited_in_code_span_is_a_reference(tmp_path):
    vault, mono = tmp_path / "vault", tmp_path / "mono"
    write(vault, "99-meta/ci-policy.md", "Règles : `.spec/00-canon/rules.md` (monorepo).\n")
    canon(mono, "rules.md")
    assert unreferenced(vault, mono) == {}


# --- Identité par chemin -----------------------------------------------------------------------


def test_path_with_or_without_extension_and_repo_prefix(tmp_path):
    vault, mono = tmp_path / "vault", tmp_path / "mono"
    write(vault, "ledger/a.md", "Voir .spec/00-canon/role-matrix, puis app/.spec/00-canon/db/map.md.\n")
    canon(mono, "role-matrix.md")
    canon(mono, "db/map.md")
    assert unreferenced(vault, mono) == {}


def test_same_name_in_another_folder_is_not_a_reference(tmp_path):
    vault, mono = tmp_path / "vault", tmp_path / "mono"
    write(vault, "ledger/a.md", "Voir `.spec/00-canon/seo/README.md`.\n")
    canon(mono, "seo/README.md")
    other = canon(mono, "commerce/README.md")
    assert set(unreferenced(vault, mono)) == {other}


def test_directory_mention_does_not_credit_the_files_inside(tmp_path):
    vault, mono = tmp_path / "vault", tmp_path / "mono"
    write(vault, "ledger/a.md", "Dossier `.spec/00-canon/db-governance/`.\n")
    target = canon(mono, "db-governance/domain-map.md")
    assert target in unreferenced(vault, mono)


def test_archived_mentions_do_not_count(tmp_path):
    vault, mono = tmp_path / "vault", tmp_path / "mono"
    write(vault, "ledger/_archive/old.md", "`.spec/00-canon/rules.md`\n")
    target = canon(mono, "rules.md")
    assert target in unreferenced(vault, mono)


# --- Contrat inchangé ----------------------------------------------------------------------------


def test_grace_period_info_then_warning(tmp_path):
    vault, mono = tmp_path / "vault", tmp_path / "mono"
    write(vault, "README.md")
    recent = canon(mono, "new.md")
    old = canon(mono, "old.md")
    ten_days_ago = time.time() - 10 * 86400
    os.utime(mono / old, (ten_days_ago, ten_days_ago))
    assert unreferenced(vault, mono) == {recent: "info", old: "warning"}


def test_missing_canon_dir_is_skipped(tmp_path):
    vault, mono = tmp_path / "vault", tmp_path / "mono"
    write(vault, "README.md")
    mono.mkdir()
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(vault), "--monorepo", str(mono), "--json"],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0
    assert "skipped" in json.loads(proc.stdout)
