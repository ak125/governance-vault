#!/usr/bin/env python3
"""check-canon-backlinks.py — Detecte la reapparition de canon en dehors du vault (G1 drift).

Principe (ADR-015 + G1) :
  - Le canon technique vit exclusivement dans le MONOREPO sous `.spec/00-canon/`
  - Le vault enrichit via ledger/ mais ne duplique pas le canon
  - Si le monorepo contient un `.spec/00-canon/*.md` qui n'est PAS reference depuis le vault,
    c'est un risque de dérive silencieuse (G1 violation latente)

Detection :
  - Scan monorepo/.spec/00-canon/**/*.md
  - Pour chaque fichier, verifier qu'il existe au moins 1 wikilink depuis le vault qui le cite
    (par stem OR path-last-segment)
  - Si aucun backlink -> warning (info si fichier < 7 jours = nouveau, grace period)

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


def strip_code(txt: str) -> str:
    txt = re.sub(r"```[\s\S]*?```", "", txt)
    txt = re.sub(r"`[^`\n]*`", "", txt)
    return txt


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

    vault_links: set[str] = set()
    EXCLUDE_DIRS = {".git", ".obsidian", "_archive"}
    link_re = re.compile(r"\[\[([^\]]+?)\]\]")

    for md in vault_path.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in md.parts):
            continue
        try:
            text = strip_code(md.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        for match in link_re.findall(text):
            name = match.strip().split("|", 1)[0].split("#", 1)[0].strip().rstrip("\\")
            vault_links.add(name.rsplit("/", 1)[-1])
            vault_links.add(name)

    findings: list[dict] = []
    now = time.time()
    GRACE_DAYS = 7
    scanned = 0

    for canon_file in canon_dir.rglob("*.md"):
        scanned += 1
        stem = canon_file.stem
        rel_inside_canon = canon_file.relative_to(canon_dir).with_suffix("").as_posix()

        referenced = (
            stem in vault_links
            or rel_inside_canon in vault_links
            or f".spec/00-canon/{rel_inside_canon}" in vault_links
        )
        if referenced:
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
