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
  4. ledger/decisions/adr/ADR-*.md en status=proposed dont la `date` a plus de
     30 jours (warning) : regle Q4 de rules-engineering-quality (« Les ADR
     `proposed` > 30 jours doivent etre traitees »). Un ADR `proposed` n'a aucune
     autorite (G5) ; le laisser en attente entretient l'ambiguite. Avertissement,
     jamais bloquant : trancher le statut est une decision de l'owner.
     Le message ne contient pas l'age : le lint hebdomadaire deduplique ses
     issues sur le texte du message, qui doit donc rester le meme d'une semaine
     a l'autre. Une `date` absente ou illisible n'est pas signalee ici : c'est
     une erreur de check-frontmatter-schema.py (champ requis, AAAA-MM-JJ).

Usage:
  python3 _scripts/check-obsolete-rules.py [VAULT_PATH] [--json] [--today=YYYY-MM-DD]

  --today=YYYY-MM-DD  date de reference de la regle 4 (defaut : aujourd'hui en UTC,
                      comme les runners CI). Sert aux tests.

Exit 0 si aucune erreur (les avertissements ne bloquent pas), 1 si au moins une
erreur, 2 si --today est mal forme.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from governance_constants import ADR_STATUSES_ARCHIVED

# Narrow ARCHIVED → only statuses that semantically imply a successor.
# rejected/deferred ne demandent pas de replacement (jamais accepté / décision
# postponée). Dérivé de la SoT pour résister au drift sans étendre l'API.
_REQUIRES_REPLACEMENT = ADR_STATUSES_ARCHIVED & frozenset({"deprecated", "superseded"})

# Seuil de la regle Q4 (rules-engineering-quality, « Process »). Le changer = amender Q4.
PROPOSED_MAX_AGE_DAYS = 30
_ADR_FILE = re.compile(r"ledger/decisions/adr/ADR-[^/]+\.md")
_TODAY_ARG = re.compile(r"--today=(\d{4}-\d{2}-\d{2})")


def to_date(value: object) -> date | None:
    """Date du frontmatter : PyYAML rend un `date`, le repli sans PyYAML une chaine."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


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
    today = datetime.now(timezone.utc).date()
    for arg in argv[1:]:
        if arg.startswith("--today"):
            match = _TODAY_ARG.fullmatch(arg)
            parsed = to_date(match.group(1)) if match else None
            if parsed is None:
                print(f"Error: expected --today=YYYY-MM-DD, got: {arg}", file=sys.stderr)
                return 2
            today = parsed

    targets: list[Path] = []
    for rel in ("ledger/rules", "ledger/policies", "ledger/decisions/adr"):
        d = vault_path / rel
        if d.is_dir():
            targets.extend(d.rglob("*.md"))

    findings: list[dict] = []
    scanned = 0

    for p in sorted(targets):
        if "_archive" in p.parts:
            continue
        scanned += 1
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        status = (fm.get("status") or "").lower()
        file = p.relative_to(vault_path).as_posix()

        if status in _REQUIRES_REPLACEMENT:
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

        if status == "proposed" and _ADR_FILE.fullmatch(file):
            proposed_on = to_date(fm.get("date"))
            if proposed_on is not None and (today - proposed_on).days > PROPOSED_MAX_AGE_DAYS:
                findings.append({
                    "severity": "warning",
                    "file": file,
                    "message": (
                        f"status=proposed since {proposed_on.isoformat()}, past the "
                        f"{PROPOSED_MAX_AGE_DAYS}-day limit of rule Q4: owner decision pending"
                    ),
                    "rule": "obsolete/proposed-stale",
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
