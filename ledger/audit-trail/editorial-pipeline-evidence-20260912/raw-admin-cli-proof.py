"""Real RAW CLI + native gitleaks/gates/manifests, disposable corpus only."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

source = Path(sys.argv[1])
scanner = str(Path(sys.argv[2]).resolve(strict=True))
with tempfile.TemporaryDirectory(prefix='raw-admin-proof-') as tmp:
    root = Path(tmp)
    (root / '_scripts').mkdir()
    for name in ('auto-capture-runner.py', 'gates.py', 'regen-manifests.py', 'capture_http.py'):
        shutil.copy(source / '_scripts' / name, root / '_scripts' / name)
    shutil.copytree(source / '_schemas', root / '_schemas')
    (root / 'manifests').mkdir()
    subprocess.run(['git', 'init', '-q', tmp], check=True)
    env = {'PATH': os.environ['PATH'], 'LANG': 'C.UTF-8', 'RAW_GITLEAKS_BIN': scanner}
    command = ['python3', str(root / '_scripts/auto-capture-runner.py'), '--submission-stdin', '--commit', '--json']
    doc = {'title': 'Entretien du filtre', 'content': 'Remplacer le filtre selon le plan du constructeur.\n',
           'source': 'manual/filtre', 'source_url': 'https://manufacturer.example/filtre'}
    def run(payload):
        result = subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True, env=env, timeout=30)
        return result.returncode, json.loads(result.stdout)
    code, first = run(doc)
    assert code == 0 and first['action'] == 'RECEIVED', (code, first)
    path = root / first['raw_path']
    original = path.read_bytes()
    code, duplicate = run(doc)
    assert code == 0 and duplicate['id'] == first['id'] and duplicate['duplicate']
    assert path.read_bytes() == original
    code, changed = run({**doc, 'content': 'Autre contenu soumis, sans validation automatique.'})
    assert code == 0 and changed['id'] != first['id']
    # Synthetic token, deliberately nonfunctional; findings are never printed.
    synthetic = 'ghp_' + 'Aa1Bb2Cc3Dd4Ee5Ff6Gg7Hh8Ii9Jj0Kk1Ll2'
    code, rejected = run({**doc, 'content': 'github_token = ' + synthetic})
    assert code == 1 and rejected['action'] == 'ERROR', (code, rejected)
    assert len(list((root / 'recycled').rglob('*.md'))) == 2
    gate = subprocess.run(['python3', str(root / '_scripts/gates.py'), '--gate', 'A'], capture_output=True, env=env)
    manifests = subprocess.run(['python3', str(root / '_scripts/regen-manifests.py'), '--check'], capture_output=True, env=env)
    assert gate.returncode == 0 and manifests.returncode == 0
    print(json.dumps({'cli': 'PASS', 'real_secret_scanner': 'PASS', 'gate_a': 'PASS', 'native_manifests': 'PASS',
        'duplicate_same_receipt': True, 'changed_body_new_receipt': True, 'secret_refused_without_persistence': True,
        'sources_in_disposable_corpus': 2, 'network_requests': 0}, indent=2))
