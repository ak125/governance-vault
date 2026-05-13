#!/usr/bin/env python3
"""
sync_canon_mirrors.py — Synchronise les canon mirrors vers les repos consommateurs (ADR-061 §3).

Source of truth : `99-meta/canon-hashes.json` (manifeste maintenu par compute-canon-hashes.py).

Pour chaque canon listé dans le manifeste :
  1. Lit le canon source depuis le vault (canon_path).
  2. Strip le frontmatter YAML → corps "distribution" (cf. AEC §"Distribution canonique").
  3. Pour chaque consumer ciblant `ak125/nestjs-remix-monorepo` : écrit le corps dans
     le path consumer du monorepo local. Les autres repos (wiki, raw) sont ignorés
     dans cette V1 (out-of-scope, scope strict du plan étape 4).

Modes :
  --monorepo PATH   : chemin vers le checkout local du monorepo (défaut: /opt/automecanik/app)
  --dry-run         : log les diffs sans écrire (CI / debugging)
  --check           : exit 1 si drift détecté (sans écrire) — pour CI assertion
  --write           : écrit les fichiers en place (cron mode)

Exit :
  0  : opération réussie (no-op OU --write OK)
  1  : drift détecté en --check, ou erreur d'écriture
  2  : erreur fatale (manifeste manquant, canon source introuvable)

Usage :
  python3 _scripts/sync_canon_mirrors.py --check                          # CI assertion
  python3 _scripts/sync_canon_mirrors.py --write --monorepo /opt/automecanik/app
  python3 _scripts/sync_canon_mirrors.py --dry-run                        # preview

Référence : ADR-061 §3, manifeste 99-meta/canon-hashes.json, pattern cron-sync-moc-decisions.sh.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = VAULT_ROOT / "99-meta" / "canon-hashes.json"
MONOREPO_REPO_NAME = "ak125/nestjs-remix-monorepo"

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n*", re.DOTALL)


def strip_frontmatter(text: str) -> str:
    """Strip YAML frontmatter from canon source to produce the distribution body."""
    return FRONTMATTER_RE.sub("", text, count=1)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print(f"ERROR: manifest not found: {MANIFEST_PATH}", file=sys.stderr)
        sys.exit(2)
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def compute_action(
    monorepo_root: Path,
    canon_id: str,
    canon_def: dict,
) -> list[dict]:
    """Compute per-consumer actions: no-op | update | create."""
    canon_source = VAULT_ROOT / canon_def["canon_path"]
    if not canon_source.exists():
        print(f"ERROR: canon source missing: {canon_source}", file=sys.stderr)
        sys.exit(2)

    canon_text = canon_source.read_text(encoding="utf-8")
    distribution_body = strip_frontmatter(canon_text)
    distribution_hash = sha256(distribution_body)

    expected_hash = canon_def["distribution_sha256"]
    if distribution_hash != expected_hash:
        print(
            f"WARN: canon {canon_id} distribution hash {distribution_hash[:8]} != "
            f"manifest expected {expected_hash[:8]}. Manifest may be stale — run compute-canon-hashes.py --write.",
            file=sys.stderr,
        )

    actions = []
    for consumer in canon_def["consumers"]:
        if consumer["repo"] != MONOREPO_REPO_NAME:
            actions.append({"canon": canon_id, "consumer": consumer, "action": "skip", "reason": "out-of-scope (not monorepo)"})
            continue

        target_path = monorepo_root / consumer["path"]
        if not target_path.exists():
            actions.append({"canon": canon_id, "consumer": consumer, "action": "create", "target": target_path, "content": distribution_body})
            continue

        current_content = target_path.read_text(encoding="utf-8")
        if current_content == distribution_body:
            actions.append({"canon": canon_id, "consumer": consumer, "action": "noop", "target": target_path})
        else:
            actions.append({"canon": canon_id, "consumer": consumer, "action": "update", "target": target_path, "content": distribution_body})

    return actions


def apply_actions(actions: list[dict], write: bool) -> int:
    """Apply or simulate actions. Returns number of changes (create+update)."""
    changes = 0
    for action in actions:
        kind = action["action"]
        target = action.get("target")
        canon = action["canon"]
        consumer_path = action["consumer"]["path"]

        if kind == "skip":
            continue
        if kind == "noop":
            print(f"  noop:   {canon:20s} → {consumer_path}")
            continue

        changes += 1
        prefix = "WRITE" if write else "DRY"
        print(f"  {prefix:5s} {kind}: {canon:20s} → {consumer_path}")

        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(action["content"], encoding="utf-8")

    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync canon mirrors from vault to monorepo (ADR-061 §3).")
    parser.add_argument("--monorepo", default="/opt/automecanik/app", help="Path to local monorepo checkout")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--write", action="store_true", help="Write changes to monorepo files in place")
    mode_group.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    mode_group.add_argument("--check", action="store_true", help="Exit 1 if drift detected (CI mode)")
    args = parser.parse_args()

    monorepo_root = Path(args.monorepo).resolve()
    if not monorepo_root.is_dir():
        print(f"ERROR: monorepo path not found: {monorepo_root}", file=sys.stderr)
        return 2

    manifest = load_manifest()
    print(f"# sync_canon_mirrors — manifest version {manifest.get('version')}, updated {manifest.get('updated')}")
    print(f"# monorepo: {monorepo_root}")
    print(f"# mode: {'write' if args.write else 'check' if args.check else 'dry-run'}")
    print()

    total_changes = 0
    all_actions: list[dict] = []
    for canon_id, canon_def in manifest["canons"].items():
        print(f"Canon: {canon_id} ({canon_def['name']})")
        actions = compute_action(monorepo_root, canon_id, canon_def)
        all_actions.extend(actions)
        changes = apply_actions(actions, write=args.write)
        total_changes += changes
        print()

    print(f"Total changes: {total_changes}")

    if args.check and total_changes > 0:
        print(f"FAIL: {total_changes} drift detected (ADR-061 §3 — canon mirrors out of sync).")
        return 1

    if total_changes == 0:
        print("PASS: 0 drift, all canon mirrors in sync.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
