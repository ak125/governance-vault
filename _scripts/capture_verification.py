#!/usr/bin/env python3
"""Collect one pinned GitHub workflow run, read-only; JSON on stdout.

No caller-declared verdict, vault writes, publication, logs, or runtime probes.
Exit: 0 observed success; 1 observed failure; 2 invalid/unavailable evidence;
3 partial evidence. A success is NOT a branch-protection or deployment verdict.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
import sys

FIELDS = ('databaseId', 'attempt', 'headSha', 'workflowName', 'url',
          'status', 'conclusion', 'jobs')
JOB_FIELDS = ('databaseId', 'name', 'url', 'status', 'conclusion')
FAILURES = {'failure', 'cancelled', 'timed_out', 'action_required', 'startup_failure', 'stale'}
NOT_VERIFIED = ['required_branch_checks', 'other_workflows', 'local_worktree',
                'deployment', 'runtime_health']


class InvalidEvidence(ValueError):
    pass


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise InvalidEvidence('Duplicate JSON field')
        obj[key] = value
    return obj


def positive_id(value):
    if not re.fullmatch(r'[1-9][0-9]*', value):
        raise argparse.ArgumentTypeError('Expected a positive integer')
    return int(value)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='GitHub owner/repo (github.com)')
    parser.add_argument('--run-id', required=True, type=positive_id)
    parser.add_argument('--attempt', required=True, type=positive_id)
    parser.add_argument('--commit', required=True, help='Expected full 40-character SHA')
    parser.add_argument('--workflow', required=True, help='Expected exact workflow name')
    args = parser.parse_args()
    part = r'[A-Za-z0-9][A-Za-z0-9_.-]*'
    if not re.fullmatch(part + '/' + part, args.repo):
        parser.error('Expected owner/repo, not a URL or path')
    if not re.fullmatch(r'[a-fA-F0-9]{40}', args.commit):
        parser.error('Expected full commit SHA')
    if (not args.workflow.strip() or len(args.workflow) > 300
            or any(ord(c) < 32 for c in args.workflow)):
        parser.error('Expected a non-empty single-line workflow name')
    args.commit = args.commit.lower()
    return args


def project_source(data):
    if not isinstance(data, dict) or not set(FIELDS) <= data.keys():
        raise InvalidEvidence('Missing workflow evidence fields')
    source = {key: data[key] for key in FIELDS}
    for key in ('databaseId', 'attempt'):
        if type(source[key]) is not int or source[key] <= 0:
            raise InvalidEvidence('Invalid workflow identity')
    for key in ('headSha', 'workflowName', 'url', 'status', 'conclusion'):
        if not isinstance(source[key], str):
            raise InvalidEvidence('Invalid workflow field type')
    if not isinstance(source['jobs'], list):
        raise InvalidEvidence('Missing job list')
    jobs, seen = [], set()
    for job in source['jobs']:
        if not isinstance(job, dict) or not set(JOB_FIELDS) <= job.keys():
            raise InvalidEvidence('Missing job evidence fields')
        job = {key: job[key] for key in JOB_FIELDS}
        if (type(job['databaseId']) is not int or job['databaseId'] <= 0
                or job['databaseId'] in seen):
            raise InvalidEvidence('Invalid or duplicated job identity')
        seen.add(job['databaseId'])
        if any(not isinstance(job[key], str) for key in ('name', 'url', 'status', 'conclusion')):
            raise InvalidEvidence('Invalid job field type')
        if not job['name'].strip():
            raise InvalidEvidence('Missing job name')
        jobs.append(job)
    source['jobs'] = jobs
    return source


def assess(data, args):
    source = project_source(data)
    url = f'https://github.com/{args.repo}/actions/runs/{args.run_id}'
    if (source['databaseId'] != args.run_id or source['attempt'] != args.attempt
            or source['headSha'].lower() != args.commit
            or source['workflowName'] != args.workflow
            or source['url'] != f'{url}/attempts/{args.attempt}'):
        raise InvalidEvidence('Workflow identity does not match the requested scope')
    for job in source['jobs']:
        if job['url'] != f"{url}/job/{job['databaseId']}":
            raise InvalidEvidence('Job URL does not match the requested run')
    records = [source, *source['jobs']]
    if any(record['conclusion'] in FAILURES for record in records):
        return source, 'failed', 1
    if (source['jobs'] and all(record['status'] == 'completed'
                              and record['conclusion'] == 'success' for record in records)):
        return source, 'passed', 0
    return source, 'partial', 3


def collect(args):
    report = {
        'schema_version': 1, 'scope': 'single_workflow_run',
        'collected_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'expected': {'repository': args.repo, 'run_id': args.run_id, 'attempt': args.attempt,
                     'commit': args.commit, 'workflow': args.workflow},
        'not_verified': NOT_VERIFIED,
    }
    try:
        result = subprocess.run(
            ['gh', 'run', 'view', str(args.run_id), '--repo', args.repo,
             '--attempt', str(args.attempt), '--json', ','.join(FIELDS)],
            capture_output=True, text=True, timeout=30, check=False,
            env={**os.environ, 'GH_HOST': 'github.com', 'GH_PROMPT_DISABLED': '1'},
        )
        if result.returncode:
            raise InvalidEvidence('GitHub collection failed; check gh authentication and run access')
        data = json.loads(result.stdout, object_pairs_hook=unique_object)
        source, status, code = assess(data, args)
        encoded = json.dumps(source, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')
        report.update(status=status, source=source, source_sha256=hashlib.sha256(encoded).hexdigest())
        if status == 'partial':
            report['reason'] = 'Run or jobs incomplete, skipped, neutral, unknown, or absent'
    except (OSError, subprocess.TimeoutExpired, UnicodeError, ValueError) as error:
        # Do not leak CLI stderr, credentials, or arbitrary malformed payloads.
        reason = str(error) if isinstance(error, InvalidEvidence) else 'Evidence unavailable or invalid'
        report.update(status='insufficient_evidence', reason=reason)
        code = 2
    return report, code


def main():
    report, code = collect(arguments())
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return code


if __name__ == '__main__':
    sys.exit(main())
