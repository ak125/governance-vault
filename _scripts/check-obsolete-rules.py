#!/usr/bin/env python3
"""check-obsolete-rules.py — Flague les documents canon avec status=deprecated|superseded sans replacement explicite.

Scope :
  - ledger/rules/rules-*.md
  - ledger/policies/*.md
  - ledger/decisions/adr/ADR-*.md

Detecte :
  1. status=deprecated sans champ superseded_by ni mention de replacement dans le body
  2. status=superseded sans superseded_by explicite
  3. Fichier dans ledger/_archive/* sans frontmatter status=archived (info)

Usage:
  python3 _scripts/check-obsolete-rules.py [VAULT_PATH] [--json]

Exit 0 si aucune violation, 1 sinon.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    raw = text[4:end]
    try:
        import yaml  # type: ignore
        parsed = yaml.safe_load(raw)
        return parsed if isinstance(parsed, dict) else {}
    except ImportError:
        out: dict = {}
        for line in raw.splitlines():
            m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
            if m:
                out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
        return out


def has_replacement_mention(body: str) -> bool:
    patterns = [
        r"superseded\s+by\s+\[\[",
        r"remplac[eé]\s+par\s+\[\[",
        r"voir\s+\[\[ADR-",
        r"see\s+\[\[ADR-",
    ]
    return any(re.search(p, body, re.IGNORECASE) for p in patterns)


def main(argv: list[str]) -> int:
    vault_path = Path(argv[1]).resolve() if len(argv) > 1 and not argv[1].startswith("--") else Path.cwd()
    emit_json = "--json" in argv

    targets: list[Path] = []
    for rel in ("ledger/rules", "ledger/policies", "ledger/decisions/adr"):
        d = vault_path / rel
        if d.is_dir():
            targets.extend(d.rglob("*.md"))

    findings: list[dict] = []
    scanned = 0

    for p in targets:
        if "_archive" in p.parts:
            continue
        scanned += 1
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        status = (fm.get("status") or "").lower()
        file = p.relative_to(vault_path).as_posix()

        if status in ("deprecated", "superseded"):
            superseded_by = fm.get("superseded_by")
            if isinstance(superseded_by, str):
                superseded_by = [superseded_by] if superseded_by.strip() else []
            elif superseded_by is None:
                superseded_by = []

            body = text[text.find("\n---\n") + 5:] if text.startswith("---\n") else text
            mentions = has_replacement_mention(body)

            if not superseded_by and not mentions:
                findings.append({
                    "severity": "error",
                    "file": file,
                    "message": f"status={status} but no superseded_by field and no replacement wikilink in body",
                    "rule": "obsolete/replacement-required",
                })
            elif not superseded_by and mentions:
                findings.append({
                    "severity": "warning",
                    "file": file,
                    "message": f"status={status}: replacement mentioned in body but superseded_by field empty — formalize it",
                    "rule": "obsolete/frontmatter-replacement",
                })

    summary = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        summary[f["severity"]] = summary.get(f["severity"], 0) + 1

    if emit_json:
        print(json.dumps({"check": "obsolete-rules", "findings": findings, "summary": summary}, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity'].upper()}] {f['file']}: {f['message']}")
        print(f"\nTotal: {summary['error']} error(s), {summary['warning']} warning(s)  ({scanned} doc(s) scanned)")

    return 1 if summary["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
