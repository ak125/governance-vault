"""Tests for writers.py — snapshot append-only, MOC skip-on-hash, GH project best-effort."""
import json


from _scripts.planning import writers


def test_snapshot_path_includes_date_and_time(tmp_path):
    items = [{"canonical_id": "vault:adr:ADR-001", "priority": "P1", "item_type": "ADR",
              "status": "review", "title": "x", "blocked_reason": None, "owner": None,
              "depends_on": [], "adr_link": None}]
    p = writers.write_snapshot(items, vault_path=tmp_path,
                                 generated_at="2026-05-08T08:00:12Z",
                                 semantic_hash_value="abc123")
    assert "2026-05-08" in str(p)
    assert "run-080012Z" in str(p)


def test_two_runs_same_day_create_two_snapshots(tmp_path):
    items = [{"canonical_id": "x", "priority": "P1", "item_type": "ADR",
              "status": "review", "title": "x", "blocked_reason": None, "owner": None,
              "depends_on": [], "adr_link": None}]
    a = writers.write_snapshot(items, vault_path=tmp_path,
                                generated_at="2026-05-08T08:00:12Z",
                                semantic_hash_value="abc")
    b = writers.write_snapshot(items, vault_path=tmp_path,
                                generated_at="2026-05-08T20:00:35Z",
                                semantic_hash_value="abc")
    assert a != b
    assert a.exists() and b.exists()


def test_latest_pointer_updated(tmp_path):
    items = [{"canonical_id": "x", "priority": "P1", "item_type": "ADR",
              "status": "review", "title": "x", "blocked_reason": None, "owner": None,
              "depends_on": [], "adr_link": None}]
    writers.write_snapshot(items, vault_path=tmp_path,
                            generated_at="2026-05-08T08:00:12Z",
                            semantic_hash_value="abc")
    latest = tmp_path / "ledger/snapshots/planning/2026-05-08/latest.json"
    assert latest.exists()
    payload = json.loads(latest.read_text())
    assert payload["semantic_hash"] == "abc"


def test_moc_writer_skips_when_hash_unchanged(tmp_path):
    moc_path = tmp_path / "MOC.md"
    moc_path.write_text("---\nsemantic_hash: abc123\n---\nbody\n")
    changed = writers.write_moc(moc_path, items=[], semantic_hash_value="abc123",
                                  ack_block={})
    assert changed is False  # no rewrite


def test_moc_writer_writes_when_hash_changes(tmp_path):
    moc_path = tmp_path / "MOC.md"
    moc_path.write_text("---\nsemantic_hash: old\n---\nbody\n")
    changed = writers.write_moc(moc_path, items=[], semantic_hash_value="new",
                                  ack_block={})
    assert changed is True
    assert "new" in moc_path.read_text()


def test_gh_project_writer_returns_best_effort_on_failure(monkeypatch, tmp_path):
    def boom(*a, **kw):
        raise RuntimeError("API down")
    monkeypatch.setattr(writers, "_gh_project_upsert_one", boom)
    result = writers.write_gh_project(items=[{"canonical_id": "x"}], project_number=42,
                                        strict=False)
    assert result.ok is False
    assert "API down" in result.error


def test_gh_project_writer_partial_failure_continues(monkeypatch):
    """When 1/3 items fails, write 2 successfully and report last error (I1 best-effort)."""
    calls = []
    def upsert(item, project_number):
        calls.append(item["canonical_id"])
        if item["canonical_id"] == "fail":
            raise RuntimeError("transient 502")
    monkeypatch.setattr(writers, "_gh_project_upsert_one", upsert)
    result = writers.write_gh_project(
        items=[{"canonical_id": "ok1"}, {"canonical_id": "fail"}, {"canonical_id": "ok2"}],
        project_number=42, strict=False,
    )
    assert result.items_written == 2
    assert "fail" in (result.error or "")
    assert calls == ["ok1", "fail", "ok2"]
