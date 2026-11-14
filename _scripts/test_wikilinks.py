#!/usr/bin/env python3
"""Tests de check-orphans.sh et check-broken-links.sh : un document est identifié par son chemin (ADR-127).

Les fixtures reproduisent le faux négatif d'avant ADR-127 : deux fichiers de même nom se masquaient,
un lien vers l'un rendait l'autre « non orphelin » et un lien de chemin erroné passait sur son seul nom.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import wikilinks

HERE = Path(__file__).resolve().parent
ORPHANS = HERE / "check-orphans.sh"
BROKEN = HERE / "check-broken-links.sh"

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash requis")


def write(vault: Path, rel: str, text: str = "# Doc\n") -> None:
    path = vault / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(script: Path, vault: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(script), str(vault)], capture_output=True, text=True, check=False
    )


def report(vault: Path, name: str) -> str:
    path = vault / "99-meta" / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def orphans(vault: Path) -> tuple[int, str]:
    proc = run(ORPHANS, vault)
    return proc.returncode, report(vault, "orphans-report.md")


def broken(vault: Path) -> tuple[int, str]:
    proc = run(BROKEN, vault)
    return proc.returncode, report(vault, "broken-links-report.md")


# --- Homonymes : le faux négatif d'origine ---------------------------------------------------


def test_homonym_not_linked_is_orphan_when_its_twin_is_linked_by_path(tmp_path):
    """Critère d'acceptation : deux homonymes, un seul lié, le check signale l'autre."""
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n\n- [[ledger/a/note|note A]]\n")
    write(tmp_path, "ledger/a/note.md")
    write(tmp_path, "ledger/b/note.md")
    rc, text = orphans(tmp_path)
    assert rc == 1
    assert "`ledger/b/note.md`" in text
    assert "`ledger/a/note.md`" not in text


def test_every_homonym_is_checked_not_only_the_last_one(tmp_path):
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n\n- [[ledger/b/note]]\n")
    for folder in ("a", "b", "c"):
        write(tmp_path, f"ledger/{folder}/note.md")
    rc, text = orphans(tmp_path)
    assert rc == 1
    assert "`ledger/a/note.md`" in text
    assert "`ledger/c/note.md`" in text
    assert "`ledger/b/note.md`" not in text


def test_short_link_to_homonyms_is_ambiguous_and_credits_none(tmp_path):
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n\n- [[note]]\n")
    write(tmp_path, "ledger/a/note.md")
    write(tmp_path, "ledger/b/note.md")
    rc, text = broken(tmp_path)
    assert rc == 1
    assert "ambigu" in text.lower()
    assert "`ops/moc/MOC-Test.md`" in text
    assert "ledger/a/note" in text and "ledger/b/note" in text
    rc, text = orphans(tmp_path)
    assert rc == 1
    assert "`ledger/a/note.md`" in text and "`ledger/b/note.md`" in text


def test_path_link_to_missing_path_is_broken_even_if_the_name_exists_elsewhere(tmp_path):
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n\n- [[ledger/wrong/note]]\n- [[ledger/a/note]]\n")
    write(tmp_path, "ledger/a/note.md")
    rc, text = broken(tmp_path)
    assert rc == 1
    assert "`[[ledger/wrong/note]]`" in text


# --- Résolution nominale -----------------------------------------------------------------------


def test_unique_short_link_resolves_by_name(tmp_path):
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n\n- [[note|Note]] et [[other#Section]]\n")
    write(tmp_path, "ledger/a/note.md")
    write(tmp_path, "ledger/x/other.md")
    assert orphans(tmp_path)[0] == 0
    assert broken(tmp_path)[0] == 0


def test_path_link_from_vault_root_with_or_without_leading_slash(tmp_path):
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n\n- [[/ledger/a/README|A]]\n- [[ledger/b/README]]\n")
    write(tmp_path, "README.md")
    write(tmp_path, "ledger/a/README.md")
    write(tmp_path, "ledger/b/README.md")
    assert orphans(tmp_path)[0] == 0
    assert broken(tmp_path)[0] == 0


def test_leading_slash_targets_the_root_file_among_homonyms(tmp_path):
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n\n- [[/README|README]]\n- [[ledger/a/README]]\n")
    write(tmp_path, "README.md")
    write(tmp_path, "ledger/a/README.md")
    assert broken(tmp_path)[0] == 0
    assert orphans(tmp_path)[0] == 0


def test_self_link_is_not_an_inbound_link(tmp_path):
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n")
    write(tmp_path, "ledger/a/alone.md", "# Seul\n\nVoir [[alone]] et [[ledger/a/alone|moi]].\n")
    rc, text = orphans(tmp_path)
    assert rc == 1
    assert "`ledger/a/alone.md`" in text
    # Un lien vers soi-même reste un lien valide.
    assert broken(tmp_path)[0] == 0


def test_links_inside_code_are_ignored(tmp_path):
    write(
        tmp_path,
        "ops/moc/MOC-Test.md",
        "# MOC\n\n```\n[[missing-fenced]]\n```\n\n`[[missing-inline]]` et [[note]]\n",
    )
    write(tmp_path, "ledger/a/note.md")
    assert broken(tmp_path)[0] == 0


def test_root_whitelist_and_excluded_dirs_are_kept(tmp_path):
    for rel in ("ops/moc/MOC-Test.md", "99-meta/x.md", "_templates/t.md", "_scripts/s.md",
                "_assets/a.md", "README.md", "CLAUDE.md", "AGENTS.md", ".obsidian/o.md"):
        write(tmp_path, rel)
    assert orphans(tmp_path)[0] == 0
    assert broken(tmp_path)[0] == 0


def test_broken_short_link_is_reported(tmp_path):
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n\n- [[nowhere]]\n")
    rc, text = broken(tmp_path)
    assert rc == 1
    assert "`[[nowhere]]`" in text


def test_clean_run_removes_a_stale_report(tmp_path):
    write(tmp_path, "ops/moc/MOC-Test.md", "# MOC\n\n- [[note]]\n")
    write(tmp_path, "99-meta/orphans-report.md", "stale\n")
    write(tmp_path, "99-meta/broken-links-report.md", "stale\n")
    write(tmp_path, "ledger/a/note.md")
    assert orphans(tmp_path)[0] == 0
    assert broken(tmp_path)[0] == 0
    assert not (tmp_path / "99-meta" / "orphans-report.md").exists()
    assert not (tmp_path / "99-meta" / "broken-links-report.md").exists()


# --- Résolveur (unitaire) ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "target, expected",
    [
        ("note", (wikilinks.OK, ("x/note.md",))),
        ("README", (wikilinks.AMBIGUOUS, ("README.md", "a/README.md"))),
        ("/README", (wikilinks.OK, ("README.md",))),
        ("a/README", (wikilinks.OK, ("a/README.md",))),
        ("b/README", (wikilinks.BROKEN, ())),
        ("absent", (wikilinks.BROKEN, ())),
        ("", (wikilinks.BROKEN, ())),
    ],
)
def test_index_resolution(target, expected):
    index = wikilinks.Index(["README.md", "a/README.md", "x/note.md"])
    assert index.resolve(target) == expected


def test_link_targets_drop_alias_anchor_and_code():
    text = "[[a/b|alias]] [[c#sec]] [[d\\|e]] `[[inline]]`\n```\n[[fenced]]\n```\n"
    assert wikilinks.link_targets(text) == ["a/b", "c", "d"]


def test_cli_usage_error_exits_2(tmp_path):
    script = HERE / "wikilinks.py"
    for args in ([], ["unknown"], ["links", str(tmp_path / "missing")]):
        proc = subprocess.run([sys.executable, str(script), *args],
                              capture_output=True, text=True, check=False)
        assert proc.returncode == 2, args
