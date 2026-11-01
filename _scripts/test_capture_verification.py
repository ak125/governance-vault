"""Real CLI tests with only the external GitHub transport substituted."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).with_name('capture_verification.py')
SHA = 'a' * 40


def run_data():
    return {
        'databaseId': 123, 'attempt': 2, 'headSha': SHA,
        'workflowName': 'CI', 'url': 'https://github.com/owner/repo/actions/runs/123/attempts/2',
        'status': 'completed', 'conclusion': 'success',
        'jobs': [{'databaseId': 456, 'name': 'lint', 'status': 'completed',
                  'conclusion': 'success',
                  'url': 'https://github.com/owner/repo/actions/runs/123/job/456'}],
    }


class CaptureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        gh = self.bin / 'gh'
        gh.write_text('#!/usr/bin/env python3\nimport json, os, sys\n'
                      'from pathlib import Path\n'
                      'Path("called.json").write_text(json.dumps(sys.argv[1:]))\n'
                      'print(os.environ["GH_RESPONSE"])\n'
                      'sys.exit(int(os.environ.get("GH_EXIT", "0")))\n')
        gh.chmod(0o755)

    def invoke(self, data=None, *, extra=(), env=None, raw=None):
        proc_env = {**os.environ, 'PATH': str(self.bin) + os.pathsep + os.environ['PATH'],
                    'GH_RESPONSE': raw if raw is not None else json.dumps(data or run_data()),
                    **(env or {})}
        result = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), '--repo', 'owner/repo', '--run-id', '123',
             '--attempt', '2', '--commit', SHA, '--workflow', 'CI', *extra],
            cwd=self.root, env=proc_env, capture_output=True, text=True, timeout=10)
        return result

    def evidence(self, data=None, code=0, **kwargs):
        result = self.invoke(data, **kwargs)
        self.assertEqual(code, result.returncode, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        self.assertNotIn('Traceback', result.stderr)
        # The collector cannot overwrite evidence or write to the vault.
        self.assertEqual(['bin', 'called.json'], sorted(p.name for p in self.root.iterdir()))
        return report

    def test_success_has_observed_jobs_pinned_identity_and_limited_scope(self):
        report = self.evidence()
        self.assertEqual('passed', report['status'])
        self.assertEqual('single_workflow_run', report['scope'])
        self.assertEqual(['lint'], [j['name'] for j in report['source']['jobs']])
        self.assertEqual(SHA, report['expected']['commit'])
        self.assertIn('deployment', report['not_verified'])
        self.assertRegex(report['source_sha256'], r'^[a-f0-9]{64}$')
        argv = json.loads((self.root / 'called.json').read_text())
        self.assertEqual(['run', 'view', '123', '--repo', 'owner/repo', '--attempt', '2'], argv[:7])

    def test_failure_is_retained_and_returns_nonzero(self):
        data = run_data()
        data['conclusion'] = 'failure'
        data['jobs'][0]['conclusion'] = 'failure'
        self.assertEqual('failed', self.evidence(data, code=1)['status'])

    def test_url_of_another_attempt_is_not_accepted(self):
        data = run_data()
        data['url'] = 'https://github.com/owner/repo/actions/runs/123/attempts/1'
        self.assertEqual('insufficient_evidence', self.evidence(data, code=2)['status'])

    def test_missing_gh_is_an_explicit_nonzero_result(self):
        result = self.invoke(env={'PATH': '/nonexistent-capture-test-bin'})
        self.assertEqual(2, result.returncode)
        self.assertEqual('insufficient_evidence', json.loads(result.stdout)['status'])
        self.assertFalse((self.root / 'called.json').exists())

    def test_transport_has_a_deadline_and_no_stderr_disclosure(self):
        spec = importlib.util.spec_from_file_location('capture_verification', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = argparse.Namespace(repo='owner/repo', run_id=123, attempt=2,
                                  commit=SHA, workflow='CI')
        error = subprocess.TimeoutExpired(['gh'], 30, stderr='private-data')
        with mock.patch.object(module.subprocess, 'run', side_effect=error) as transport:
            report, code = module.collect(args)
        self.assertEqual(2, code)
        self.assertEqual(30, transport.call_args.kwargs['timeout'])
        self.assertNotIn('private-data', json.dumps(report))

    def test_incomplete_run_is_partial(self):
        data = run_data()
        data.update(status='in_progress', conclusion='')
        self.assertEqual('partial', self.evidence(data, code=3)['status'])

    def test_skipped_job_cannot_pass(self):
        data = run_data()
        data['jobs'][0]['conclusion'] = 'skipped'
        self.assertEqual('partial', self.evidence(data, code=3)['status'])

    def test_empty_jobs_cannot_pass(self):
        data = run_data()
        data['jobs'] = []
        self.assertEqual('partial', self.evidence(data, code=3)['status'])

    def test_non_success_conclusions_never_pass(self):
        for conclusion in ('cancelled', 'timed_out', 'action_required', 'stale', 'neutral', 'unknown', ''):
            with self.subTest(conclusion=conclusion):
                data = run_data()
                data['conclusion'] = conclusion
                result = self.invoke(data)
                self.assertNotEqual(0, result.returncode)
                self.assertNotEqual('passed', json.loads(result.stdout)['status'])

    def test_inconsistent_success_and_failed_job_is_failed(self):
        data = run_data()
        data['jobs'][0]['conclusion'] = 'failure'
        self.assertEqual('failed', self.evidence(data, code=1)['status'])

    def test_binding_mismatches_are_insufficient_evidence(self):
        for key, value in [('headSha', 'b' * 40), ('databaseId', 124), ('attempt', 1),
                           ('workflowName', 'Other'), ('url', 'https://github.com/other/repo/actions/runs/123')]:
            with self.subTest(key=key):
                data = run_data()
                data[key] = value
                self.assertEqual('insufficient_evidence', self.evidence(data, code=2)['status'])

    def test_missing_required_fields_cannot_pass(self):
        for key in run_data():
            with self.subTest(key=key):
                data = run_data()
                del data[key]
                self.assertEqual('insufficient_evidence', self.evidence(data, code=2)['status'])

    def test_invalid_json_types_cannot_pass(self):
        for raw in ('null', '[]', '42', '{}', '{broken'):
            with self.subTest(raw=raw):
                self.assertEqual('insufficient_evidence', self.evidence(code=2, raw=raw)['status'])

    def test_duplicate_json_keys_are_rejected(self):
        raw = json.dumps(run_data()).replace('"conclusion": "success"',
                                            '"conclusion": "failure", "conclusion": "success"', 1)
        self.assertEqual('insufficient_evidence', self.evidence(code=2, raw=raw)['status'])

    def test_invalid_job_shapes_cannot_pass(self):
        for jobs in (None, {}, [None], [{}], [dict(run_data()['jobs'][0], databaseId=True)],
                     [run_data()['jobs'][0]] * 2):
            with self.subTest(jobs=jobs):
                data = run_data()
                data['jobs'] = jobs
                self.assertEqual('insufficient_evidence', self.evidence(data, code=2)['status'])

    def test_transport_error_cannot_pass_even_with_success_json(self):
        self.assertEqual('insufficient_evidence', self.evidence(code=2, env={'GH_EXIT': '1'})['status'])

    def test_arbitrary_fields_and_logs_are_not_exported(self):
        data = run_data()
        data['unrequested_token'] = 'not-for-output'
        data['jobs'][0]['steps'] = [{'secret': 'not-for-output'}]
        report = self.evidence(data)
        self.assertNotIn('not-for-output', json.dumps(report))

    def test_status_override_and_writing_are_not_supported(self):
        for extra in (['--status', 'passed'], ['--output', 'proof.json'], ['--write']):
            with self.subTest(extra=extra):
                result = self.invoke(extra=extra)
                self.assertNotEqual(0, result.returncode)
                self.assertFalse((self.root / 'called.json').exists())

    def test_invalid_identity_rejected_before_github(self):
        for extra in (['--repo', '../repo'], ['--commit', 'abc123'], ['--attempt', '0'],
                      ['--run-id', '-1'], ['--workflow', '\n'], ['--repo', 'owner/repo;evil']):
            with self.subTest(extra=extra):
                result = self.invoke(extra=extra)
                self.assertNotEqual(0, result.returncode)
                self.assertFalse((self.root / 'called.json').exists())


if __name__ == '__main__':
    unittest.main()
