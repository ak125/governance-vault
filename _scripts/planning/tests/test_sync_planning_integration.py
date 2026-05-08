"""End-to-end dry-run test of sync_planning orchestrator.

Mocks fetch.fetch_prs and fetch.parse_proposed_adrs so the test runs offline,
without GH_TOKEN, without network. Real GH API contract is covered in
test_fetch.py. Real cron run is exercised manually via `sudo -u deploy run-cron.sh`.
"""
import os
from pathlib import Path

import pytest


def test_sync_planning_dry_run_exits_zero(monkeypatch, tmp_path):
    from _scripts.planning import fetch, sync_planning

    fake_pr = {
        "canonical_id": "github:ak125/governance-vault:pr:149",
        "item_type": "PR", "priority": "P1", "status": "review",
        "title": "fake", "owner": "fafa", "depends_on": [],
        "adr_link": None, "blocked_reason": None,
        "url": "https://github.com/ak125/governance-vault/pull/149",
        "updated_at": "2026-05-07T10:00:00Z",
    }
    fake_adr = {
        "canonical_id": "vault:adr:ADR-053",
        "item_type": "ADR", "priority": "P1",
        "status": "review", "source_status": "proposed",
        "title": "Planning Live", "owner": None, "depends_on": [],
        "adr_link": "ADR-053", "blocked_reason": None,
    }
    monkeypatch.setattr(fetch, "fetch_prs", lambda repo: [fake_pr] if "governance-vault" in repo else [])
    monkeypatch.setattr(fetch, "parse_proposed_adrs", lambda p: [fake_adr])

    # sys.argv shim — argparse reads from sys.argv unless we pass it
    monkeypatch.setattr("sys.argv", [
        "sync_planning", "--vault-path", "/opt/automecanik/governance-vault", "--dry-run",
    ])
    rc = sync_planning.main()
    assert rc == 0


@pytest.mark.skipif(
    not os.environ.get("GH_TOKEN"),
    reason="Real-GH integration test : requires GH_TOKEN. Run manually with `GH_TOKEN=... pytest -m real_gh`.",
)
def test_sync_planning_real_gh_dry_run():
    """Optional smoke test against real GH API. Skipped by default."""
    from _scripts.planning import sync_planning
    import sys
    sys.argv = ["sync_planning", "--vault-path", "/opt/automecanik/governance-vault", "--dry-run"]
    assert sync_planning.main() == 0
