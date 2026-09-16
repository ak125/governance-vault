// Executes the real Nest client and RAW producer in a disposable Git corpus.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { execFileSync } = require('node:child_process');
const Module = require('node:module');
const ts = require('/opt/automecanik/app/node_modules/typescript');
const assert = require('node:assert/strict');
const [app, raw, scanner, probe] = process.argv.slice(2);
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'raw-admin-bridge-'));
(async () => {
  fs.mkdirSync(path.join(root, '_scripts'));
  for (const name of ['auto-capture-runner.py', 'capture_http.py', 'gates.py', 'regen-manifests.py']) {
    fs.copyFileSync(path.join(raw, '_scripts', name), path.join(root, '_scripts', name));
  }
  fs.cpSync(path.join(raw, '_schemas'), path.join(root, '_schemas'), { recursive: true });
  fs.mkdirSync(path.join(root, 'manifests'));
  execFileSync('git', ['init', '-q', root]);
  fs.copyFileSync(path.join(raw, 'manifests/ingestion-allowlist.yaml'), path.join(root, 'manifests/ingestion-allowlist.yaml'));
  for (const [ext, codec] of [['mp4', 'libx264'], ['webm', 'libvpx-vp9']]) {
    execFileSync('/usr/bin/ffmpeg', ['-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=16x16:d=1', '-c:v', codec, '-threads', '1', path.join(root, 'fixture.' + ext)]);
  }
  // Test-only launcher replaces the external download with synthetic local bytes.
  // Native policy, probe namespace, scanner, Gate J and manifests remain real.
  const launcher = path.join(root, '_scripts/proof_video.py');
  fs.writeFileSync(launcher, `import importlib.util, pathlib, shutil, sys
spec = importlib.util.spec_from_file_location('producer', pathlib.Path(__file__).with_name('auto-capture-runner.py'))
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
class FixtureTransport:
    def fetch_media(self, url, destination):
        ext = 'webm' if url.endswith('.webm') else 'mp4'
        source = r.REPO_ROOT / ('fixture.' + ext)
        shutil.copyfile(source, destination)
        return {'ext': ext, 'mime': 'video/' + ext, 'size_bytes': source.stat().st_size, 'media_hash': r.file_sha256(source), 'final_url': url, 'redirect_chain': [url]}
r._transport = lambda *args: FixtureTransport()
sys.exit(r.main())
`);

  const filename = path.join(app, 'backend/src/modules/rag-proxy/services/raw-acquisition-client.service.ts');
  const output = ts.transpileModule(fs.readFileSync(filename, 'utf8'), { compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS,
    experimentalDecorators: true, emitDecoratorMetadata: true,
  } }).outputText;
  const compiled = new Module(filename, module);
  compiled.filename = filename;
  compiled.paths = Module._nodeModulePaths(path.dirname(filename));
  compiled._compile(output, filename);
  const client = new compiled.exports.RawAcquisitionClientService({ get: key => ({
    RAW_ACQUISITION_SCRIPT: launcher, RAW_GITLEAKS_BIN: scanner, RAW_FFPROBE_BIN: probe,
  })[key] });
  const receipts = [];
  for (const ext of ['mp4', 'webm']) {
    const doc = { url: 'https://www.bosch.com/fixture.' + ext, gamme: 'freinage', retrievable: true };
    const first = await client.receiveVideo(doc);
    assert.equal(first.action, 'RECEIVED');
    assert.equal(first.retrievable, false);
    assert.equal(first.status, 'to_verify');
    const original = fs.readFileSync(path.join(root, first.raw_path), 'utf8');
    assert.match(original, /source_url_verified: true/);
    assert.match(original, /license_status: unknown/);
    const second = await client.receiveVideo(doc);
    assert.equal(second.id, first.id);
    assert.equal(second.duplicate, true);
    assert.equal(fs.readFileSync(path.join(root, first.raw_path), 'utf8'), original);
    assert.deepEqual(fs.readFileSync(path.join(root, first.media_path)), fs.readFileSync(path.join(root, 'fixture.' + ext)));
    const checksums = JSON.parse(fs.readFileSync(path.join(root, 'manifests/checksums.json')));
    assert.ok(checksums[first.raw_path] && checksums[first.media_path]);
    receipts.push({ ext: first.ext, size_bytes: first.size_bytes, duration_sec: first.duration_sec, duplicate: second.duplicate });
  }
  console.log(JSON.stringify({ nest_client_to_raw_media_cli: 'PASS', receipts,
    real_components: ['Nest client', 'GNU timeout process group', 'RAW CLI', 'native allowlist', 'ffprobe in unshare network namespace', 'gitleaks', 'Gate J', 'native manifests'],
    simulated_components: ['external media HTTP fetch; local synthetic MP4/WebM'],
    database_calls: 0, network_requests: 0, durable_runtime_changes: 0 }, null, 2));

})().catch(error => { console.error(error.constructor.name, error.message); process.exitCode = 1; })
.finally(() => fs.rmSync(root, { recursive: true, force: true }));
