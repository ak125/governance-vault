#!/usr/bin/env python3
"""check-canon-backlinks.py — Detecte la reapparition de canon en dehors du vault (G1 drift).

Principe (G1, ADR-101) :
  - Le vault decide ; les fichiers `.spec/00-canon/` du monorepo sont des contrats
    (consommes, font foi dans leur domaine) ou de la prose de reference (aucune autorite)
  - Si le monorepo contient un `.spec/00-canon/*.md` qui n'est PAS reference depuis le vault,
    son rang n'est trace nulle part : risque de derive silencieuse (G1 violation latente)

Detection (identite par chemin, comme ADR-127) :
  - Scan monorepo/.spec/00-canon/**/*.md
  - Un fichier est reference si un document du vault (hors `_archive`) cite son chemin exact
    `.spec/00-canon/<chemin>` (extension `.md` facultative), en texte ou entre backticks.
    Un wikilink se resout dans le vault : `[[architecture]]` designe un document du vault et
    ne reference pas `.spec/00-canon/architecture.md`. Citer un dossier ne reference pas ses fichiers.
  - Si aucune reference -> warning (info si fichier < 7 jours = nouveau, grace period)

Usage:
  python3 _scripts/check-canon-backlinks.py [VAULT_PATH] --monorepo PATH [--json]

Exit 0 si aucune violation bloquante (tous les findings sont warning/info), 1 sinon.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path


EXCLUDE_DIRS = frozenset({".git", ".obsidian", "_archive"})
CANON_PATH_RE = re.compile(r"\.spec/00-canon/([A-Za-z0-9_.\-/]+)")


def canon_paths_cited(vault_path: Path) -> set[str]:
    """Chemins sous `.spec/00-canon/`, sans `.md`, cites par les documents du vault."""
    cited: set[str] = set()
    for md in vault_path.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in md.relative_to(vault_path).parts):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for path in CANON_PATH_RE.findall(text):
            path = path.rstrip("./")
            cited.add(path[:-3] if path.endswith(".md") else path)
    return cited


def main(argv: list[str]) -> int:
    vault_path: Path | None = None
    monorepo_path: Path | None = None
    emit_json = "--json" in argv

    positional = [a for a in argv[1:] if not a.startswith("--")]
    if positional:
        vault_path = Path(positional[0]).resolve()
    else:
        vault_path = Path.cwd()

    for i, arg in enumerate(argv):
        if arg == "--monorepo" and i + 1 < len(argv):
            monorepo_path = Path(argv[i + 1]).resolve()

    if monorepo_path is None:
        default = Path("/opt/automecanik/app")
        if default.is_dir():
            monorepo_path = default
        else:
            if emit_json:
                print(json.dumps({"check": "canon-backlinks", "findings": [], "summary": {"error": 0, "warning": 0, "info": 0}, "skipped": "monorepo path not provided"}))
            else:
                print("INFO: --monorepo not provided and /opt/automecanik/app not found; skipping.")
            return 0

    canon_dir = monorepo_path / ".spec" / "00-canon"
    if not canon_dir.is_dir():
        if emit_json:
            print(json.dumps({"check": "canon-backlinks", "findings": [], "summary": {"error": 0, "warning": 0, "info": 0}, "skipped": f"{canon_dir} not found"}))
        else:
            print(f"INFO: {canon_dir} not found; skipping.")
        return 0

    cited = canon_paths_cited(vault_path)

    findings: list[dict] = []
    now = time.time()
    GRACE_DAYS = 7
    scanned = 0

    for canon_file in canon_dir.rglob("*.md"):
        scanned += 1
        if canon_file.relative_to(canon_dir).with_suffix("").as_posix() in cited:
            continue

        try:
            age_days = (now - os.path.getmtime(canon_file)) / 86400
        except OSError:
            age_days = 999

        severity = "info" if age_days < GRACE_DAYS else "warning"
        findings.append({
            "severity": severity,
            "file": str(canon_file.relative_to(monorepo_path)),
            "message": f"canon file not backlinked from vault (age: {age_days:.0f}d)",
            "rule": "G1/canon-backlinks",
        })

    summary = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        summary[f["severity"]] = summary.get(f["severity"], 0) + 1

    if emit_json:
        print(json.dumps({"check": "canon-backlinks", "findings": findings, "summary": summary, "scanned": scanned}, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity'].upper()}] {f['file']}: {f['message']}")
        print(f"\nTotal: {summary['warning']} warning(s), {summary['info']} info  ({scanned} canon file(s) scanned)")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
