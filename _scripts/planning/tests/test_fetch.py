"""Tests for fetch.py — GH PRs via gh api + ADRs via MOC-Decisions parse."""
from datetime import datetime, timezone

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


NOW = datetime(2026, 5, 8, 12, 0, 0, tzinfo=timezone.utc)


def _pr(title="x", labels=None, is_draft=False, updated_at="2026-05-08T00:00:00Z"):
    return {"title": title, "labels": labels or [], "isDraft": is_draft, "updatedAt": updated_at}


def test_fetch_prs_parses_gh_json(monkeypatch):
    monkeypatch.setattr(fetch, "_gh_api_pr_list", lambda repo: GH_PR_FIXTURE)
    prs = fetch.fetch_prs("ak125/governance-vault")
    assert len(prs) == 1
    assert prs[0]["canonical_id"] == "github:ak125/governance-vault:pr:149"
    assert prs[0]["priority"] == "P1"  # label P1 wins (rule 1)
    assert prs[0]["item_type"] == "PR"


def test_classify_priority_label_p0_wins():
    assert fetch._classify_priority(_pr(labels=[{"name": "P0"}]), now=NOW) == "P0"


def test_classify_priority_security_label_to_p0():
    assert fetch._classify_priority(_pr(labels=[{"name": "security"}]), now=NOW) == "P0"


def test_classify_priority_incident_title_to_p0():
    assert fetch._classify_priority(_pr(title="incident: outage GSC API"), now=NOW) == "P0"


def test_classify_priority_critical_title_to_p1():
    assert fetch._classify_priority(_pr(title="hotfix: critical race condition"), now=NOW) == "P1"


def test_classify_priority_fix_prefix_to_p2():
    assert fetch._classify_priority(_pr(title="fix(seo): broken meta description"), now=NOW) == "P2"


def test_classify_priority_feat_prefix_to_p3():
    assert fetch._classify_priority(_pr(title="feat(planning): new module"), now=NOW) == "P3"


def test_classify_priority_chore_prefix_to_p5():
    assert fetch._classify_priority(_pr(title="chore: cleanup unused imports"), now=NOW) == "P5"


def test_classify_priority_dependabot_to_p6():
    assert fetch._classify_priority(_pr(title="chore(deps): bump react from 18 to 19"), now=NOW) == "P6"


def test_classify_priority_stale_draft_to_p7():
    # Draft + updated_at >30j ago → P7
    pr = _pr(title="WIP something", is_draft=True, updated_at="2026-04-01T00:00:00Z")
    assert fetch._classify_priority(pr, now=NOW) == "P7"


def test_classify_priority_default_p5():
    assert fetch._classify_priority(_pr(title="random untagged title"), now=NOW) == "P5"


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
