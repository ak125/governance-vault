#!/usr/bin/env python3
"""check-adr-supersedes.py — Valide les chaines supersedes / superseded_by des ADRs.

Detecte :
  1. supersedes pointe vers un ADR qui n'existe pas
  2. supersedes cycle (A supersedes B supersedes A)
  3. superseded_by pointe vers un ADR qui n'existe pas
  4. Asymetrie : A.supersedes = [B] mais B.superseded_by ne contient pas A
  5. ADR avec status=superseded mais superseded_by vide
  6. ADR avec status!=superseded mais superseded_by non vide

Usage:
  python3 _scripts/check-adr-supersedes.py [VAULT_PATH] [--json]

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
        current_key = None
        for line in raw.splitlines():
            m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
            if m:
                key, val = m.group(1), m.group(2).strip()
                if val.startswith("[") and val.endswith("]"):
                    inner = val[1:-1].strip()
                    out[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
                elif val in ("", "~", "null"):
                    out[key] = None
                    current_key = key
                else:
                    out[key] = val.strip('"').strip("'")
                    current_key = None
            elif line.strip().startswith("- ") and current_key:
                out.setdefault(current_key, [])
                if not isinstance(out[current_key], list):
                    out[current_key] = []
                out[current_key].append(line.strip()[2:].strip('"').strip("'"))
        return out


def main(argv: list[str]) -> int:
    vault_path = Path(argv[1]).resolve() if len(argv) > 1 and not argv[1].startswith("--") else Path.cwd()
    emit_json = "--json" in argv
    adr_dir = vault_path / "ledger" / "decisions" / "adr"

    if not adr_dir.is_dir():
        print(f"Error: adr dir not found: {adr_dir}", file=sys.stderr)
        return 2

    adrs: dict[str, dict] = {}
    for p in sorted(adr_dir.glob("ADR-*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        adr_id = fm.get("id")
        if not adr_id:
            m = re.match(r"^(ADR-\d{3})", p.name)
            if m:
                adr_id = m.group(1)
        if not adr_id:
            continue
        fm["_file"] = p.relative_to(vault_path).as_posix()
        adrs[adr_id] = fm

    findings: list[dict] = []

    def add(severity: str, file: str, msg: str, rule: str) -> None:
        findings.append({"severity": severity, "file": file, "message": msg, "rule": rule})

    for adr_id, fm in adrs.items():
        file = fm["_file"]
        supersedes = fm.get("supersedes") or []
        superseded_by = fm.get("superseded_by") or []
        status = fm.get("status", "")

        if isinstance(supersedes, str):
            supersedes = [supersedes] if supersedes else []
        if isinstance(superseded_by, str):
            superseded_by = [superseded_by] if superseded_by else []

        for target in supersedes:
            if target not in adrs:
                add("error", file, f"{adr_id}.supersedes references missing {target}", "supersedes/target-exists")
            else:
                back = adrs[target].get("superseded_by") or []
                if isinstance(back, str):
                    back = [back]
                if adr_id not in back:
                    add("warning", file, f"{adr_id}.supersedes={target} but {target}.superseded_by does not list {adr_id}", "supersedes/bidirectional")

        for target in superseded_by:
            if target not in adrs:
                add("error", file, f"{adr_id}.superseded_by references missing {target}", "superseded_by/target-exists")

        if status == "superseded" and not superseded_by:
            add("error", file, f"{adr_id}.status=superseded but superseded_by is empty", "superseded_by/required-when-superseded")
        if status != "superseded" and superseded_by and status != "deprecated":
            add("warning", file, f"{adr_id}.status={status} but superseded_by={superseded_by}", "status/consistency-with-superseded_by")

    def detect_cycle(start: str, visited: set[str], path: list[str]) -> list[str] | None:
        if start in path:
            return path[path.index(start):] + [start]
        if start in visited or start not in adrs:
            return None
        visited.add(start)
        nxt = adrs[start].get("supersedes") or []
        if isinstance(nxt, str):
            nxt = [nxt]
        for n in nxt:
            cyc = detect_cycle(n, visited, path + [start])
            if cyc:
                return cyc
        return None

    seen_cycles: set[tuple[str, ...]] = set()
    for adr_id in adrs:
        cyc = detect_cycle(adr_id, set(), [])
        if cyc:
            key = tuple(sorted(cyc))
            if key in seen_cycles:
                continue
            seen_cycles.add(key)
            add("error", adrs[adr_id]["_file"], f"cycle detected in supersedes: {' -> '.join(cyc)}", "supersedes/acyclic")

    summary = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        summary[f["severity"]] = summary.get(f["severity"], 0) + 1

    if emit_json:
        print(json.dumps({"check": "adr-supersedes", "findings": findings, "summary": summary}, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity'].upper()}] {f['file']}: {f['message']}")
        print(f"\nTotal: {summary['error']} error(s), {summary['warning']} warning(s)  ({len(adrs)} ADR(s) scanned)")

    return 1 if summary["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
