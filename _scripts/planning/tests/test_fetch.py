"""Tests for fetch.py — GH PRs via gh api + ADRs via MOC-Decisions parse."""
from pathlib import Path

import pytest

from _scripts.planning import fetch


GH_PR_FIXTURE = """[
  {
    "number": 149,
    "title": "Worktree script fix",
    "labels": [{"name": "P1"}],
    "state": "OPEN",
    "url": "https://github.com/ak125/governance-vault/pull/149",
    "updatedAt": "2026-05-07T10:00:00Z",
    "author": {"login": "fafa"},
    "isDraft": false
  }
]"""


def test_fetch_prs_parses_gh_json(monkeypatch):
    monkeypatch.setattr(fetch, "_gh_api_pr_list", lambda repo: GH_PR_FIXTURE)
    prs = fetch.fetch_prs("ak125/governance-vault")
    assert len(prs) == 1
    assert prs[0]["canonical_id"] == "github:ak125/governance-vault:pr:149"
    assert prs[0]["priority"] == "P1"
    assert prs[0]["item_type"] == "PR"


def test_parse_adrs_from_moc_decisions(tmp_path):
    moc = tmp_path / "MOC-Decisions.md"
    moc.write_text("""# MOC-Decisions

## ADR Actifs

| ADR | Title | Status |
|-----|-------|--------|
| ADR-052 | SQL Role Canon | accepted |
| ADR-053 | Planning Live System | proposed |
""")
    adrs = fetch.parse_proposed_adrs(moc)
    assert len(adrs) == 1
    assert adrs[0]["canonical_id"] == "vault:adr:ADR-053"
    assert adrs[0]["item_type"] == "ADR"
    assert adrs[0]["status"] == "review"           # canon planning-status.yml
    assert adrs[0]["source_status"] == "proposed"  # raw upstream
