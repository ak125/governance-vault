"""Characterize missing retirement using real loops on disposable files/fake index."""
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path
import frontmatter
from pytest import MonkeyPatch

app, rag = map(Path, sys.argv[1:3])
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
sync = load('sync', app / 'scripts/rag-sync/sync-wiki-exports-to-rag.py')
sys.path.insert(0, str(rag))
proof = load('proof', rag / 'tests/test_f5_import_body.py')
report = {'fixture_only': True, 'database_calls': 0, 'network_requests': 0}
with tempfile.TemporaryDirectory() as tmp, MonkeyPatch.context() as patcher:
    root = Path(tmp)
    wiki, mirror = root / 'wiki', root / 'rag'
    exports = wiki / 'exports/rag/gamme'
    exports.mkdir(parents=True)
    for name in ['kept', 'withdrawn']:
        (exports / (name + '.md')).write_text('Fixture ' + name)
    patcher.setattr(sys, 'argv', ['sync', '--wiki-repo', str(wiki), '--rag-repo', str(mirror), '--apply'])
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert sync.main() == 0
        first = json.loads((mirror / 'knowledge/.last-sync.json').read_text())
        (exports / 'withdrawn.md').unlink()  # only the disposable fixture
        assert sync.main() == 0
        second = json.loads((mirror / 'knowledge/.last-sync.json').read_text())
    report['mirror_withdrawal'] = {'exports_remaining': second['stats']['exports_total'],
        'withdrawn_still_present': (mirror / 'knowledge/gamme/withdrawn.md').exists(),
        'success_timestamp_advanced': second['synced_at'] > first['synced_at']}
with tempfile.TemporaryDirectory() as tmp, MonkeyPatch.context() as patcher:
    path, rows, calls = proof.pipeline.__wrapped__(Path(tmp), patcher)
    assert proof.run()['imported'] == 1
    post = frontmatter.load(path)
    old_hash = post['content_hash']
    post['content_hash'] = 'b' * 64
    post.content = 'Fixture changed editorial text.'
    path.write_text(frontmatter.dumps(post))
    assert proof.run()['imported'] == 1
    path.unlink()  # only the disposable export fixture
    after = proof.run()
    report['index_withdrawal'] = {'rows_before_withdrawal': len(rows), 'old_version_present': any(row['content_hash'] == old_hash for row in rows),
        'rows_after_withdrawal': len(rows), 'run_errors': after['errors'], 'index_is_in_memory_fake': True}
assert report['mirror_withdrawal']['withdrawn_still_present']
assert report['index_withdrawal']['old_version_present']
print(json.dumps(report, indent=2))
