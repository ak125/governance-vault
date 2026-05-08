---
date: 2026-05-08
type: audit-trail
related: [ADR-053, MOC-Planning-Live]
---

# 2026-05-08 — Planning Live Sync Engine (PR-2)

## What

PR-2 du système Planning Live (ADR-053) — Sync Engine :

- Package Python `_scripts/planning/` (5 modules canon : fetch, schemas, hash_util, stagnation, writers)
- Orchestrator `sync_planning.py` avec dry-run + strict-projections (CLI args `--vault-path`, `--dry-run`, `--strict-projections`, `--strict-alerts`)
- VPS DEV cron `run-cron.sh` (flock concurrency, env source, mask secrets, signed G3 commit, Supabase `__cron_runs` report) — system install (Task 2.9) deferred manual one-shot post-merge
- requirements.txt pinné (`pyyaml==6.0.*`, `requests==2.32.*`)
- Tests pytest TDD : 27 passing + 1 skipped (real_gh integration test, GH_TOKEN-gated)
- check-moc-integrity étendu : valide MOC-Planning-Live (schema_version, semantic_hash coherence avec latest.json, schemas canon presents)

## Verification

- pytest 27/27 pass + 1 skip (sans GH_TOKEN env, attendu)
  - test_schemas.py : 8/8
  - test_hash.py : 6/6 (incl. I3 blacklist source_status)
  - test_stagnation.py : 3/3 (dual-metric)
  - test_writers.py : 7/7 (incl. I1 best-effort + per-item failure isolation)
  - test_fetch.py : 2/2
  - test_sync_planning_integration.py : 1/1 (+1 skip real_gh)
- check-moc-integrity strict mode : 0 error / 0 warning sur MOC-Planning-Live
- Pre-commit G2 (orphans + broken wikilinks) green sur les 9 commits PR-2

## Deferred

Task 2.9 (VPS DEV system provisioning) reportée post-merge :

- Création venv `/opt/automecanik/.venvs/planning-live` + `pip install -r requirements.txt`
- Ownership `/var/log/governance-vault/` et `/var/lock/automecanik/` à `deploy:deploy`
- Install `/etc/cron.d/planning-live` (08:00 UTC daily)
- Smoke test `sudo -u deploy env DRY_RUN=1 run-cron.sh`
- Force first real run : `sudo -u deploy run-cron.sh`
- Document VPS notes en ADR-053 §Annexe C

Raison : steps `sudo` / `systemctl reload cron` / `install -d -o deploy` sortent du périmètre de l'agent (modification system state). Documentés en commit Task 2.8 et dans `_scripts/planning/run-cron.sh` (header).

## Next

PR-3 : alertes Paperclip (cooldown 24h + ack block) + promotion ADR-053 status `proposed → accepted` après +7j observation green sur le cron VPS DEV.

## Refs

- ADR-053 §Architecture, §I1 (best-effort), §I3 (semantic_hash blacklist), §I4 (MOC integrity)
- PR-1 #221 (foundation : ADR + schemas + MOC seed + snapshots scaffolding)
- Plan rev 7 : `/home/deploy/.claude/plans/mettre-en-place-un-shimmering-fern.md`
