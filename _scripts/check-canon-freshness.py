#!/usr/bin/env python3
"""check-canon-freshness.py - Validate canon files freshness via REG-002 registry.

Implemente le critere C3 d'ADR-048 (sprint 1 axe 3) : detecte les fichiers
canon `.spec/00-canon/*` du monorepo qui sont plus vieux que leur seuil
de freshness (par defaut 180j, surcharge per-file via REG-002).

Approche :
  1. Parse REG-002 registry (`ledger/canon-coverage/REG-002-canon-files.md`)
     pour obtenir la liste des fichiers + thresholds per-file
  2. Pour chaque fichier liste, stat le mtime sur le filesystem monorepo
  3. Flag `warning` si mtime < today - threshold_days
  4. Flag `info` si fichier liste dans REG-002 absent du filesystem (ghost row)
  5. Flag `warning` si fichier present sur filesystem absent de REG-002 (drift)

REGLE ANTI-SILENT-OK : si REG-002 introuvable ou parsing impossible,
finding `error` explicite. Pas de retour silencieux OK.

Usage:
  python3 _scripts/check-canon-freshness.py [VAULT_PATH] [--monorepo PATH] [--json]

Modes :
  default : print human-readable summary, exit 0 toujours (warn-only weekly)
  --json  : emit `{check, findings, summary}` sur stdout (orchestrator pattern)
  --strict : eleve warnings en errors, exit 1 si findings (test local)

Reference plan : /home/deploy/.claude/plans/j-ai-localis-les-repos-buzzing-blanket.md
Reference ADR  : ADR-048 §Implementation Sprint 1 axe 3
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

CHECK_NAME = "canon-freshness"

DEFAULT_FRESHNESS_DAYS = 180

# Defaut path canonique du monorepo (cf. ADR-015 + check-canon-backlinks.py pattern)
DEFAULT_MONOREPO = "/opt/automecanik/app"


def parse_reg_002(reg_path: Path) -> tuple[list[dict], list[dict]]:
    """Parse `ledger/canon-coverage/REG-002-canon-files.md` registry.

    Retourne (rows, errors) : rows = liste de dicts {path, state, threshold_days, ...},
    errors = list de findings de parsing si la registry est cassee.

    Approche : scan ligne-par-ligne ancore sur sections ## (anti-silent-OK comme
    check-moc-integrity). Cherche les tables shape `| path | state | mech |
    consumers | mtime | adr | threshold |` (7 colonnes).
    """
    findings: list[dict] = []
    rows: list[dict] = []

    if not reg_path.exists():
        findings.append({
            "severity": "error",
            "file": str(reg_path),
            "rule": f"{CHECK_NAME}.reg-002-missing",
            "message": f"REG-002 registry introuvable a {reg_path}. Le check ne peut pas s'executer.",
        })
        return rows, findings

    try:
        text = reg_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        findings.append({
            "severity": "error",
            "file": str(reg_path),
            "rule": f"{CHECK_NAME}.reg-002-unreadable",
            "message": f"Lecture impossible : {e}",
        })
        return rows, findings

    lines = text.split("\n")
    in_table = False
    table_section = None  # nom de la section pour debug

    for i, line in enumerate(lines):
        # Heading detection
        if re.match(r"^##\s+", line):
            in_table = False
            table_section = line.strip("# ").strip()
            continue

        # Table row detection : "| `path` | state | mech | consumers | YYYY-MM-DD | adr | int |"
        if not line.startswith("|"):
            continue
        # Skip header row "| path | state | ... |"
        if re.search(r"\|\s*path\s*\|", line, re.IGNORECASE):
            in_table = True
            continue
        # Skip separator row "|---|---|..."
        if re.match(r"^\|\s*[-: ]+\s*\|", line):
            continue
        if not in_table:
            continue

        # Parse row : split sur " | "
        parts = [p.strip() for p in line.split(" | ")]
        if parts and parts[0].startswith("|"):
            parts[0] = parts[0].lstrip("|").strip()
        if parts and parts[-1].endswith("|"):
            parts[-1] = parts[-1].rstrip("|").strip()

        if len(parts) != 7:
            findings.append({
                "severity": "warning",
                "file": str(reg_path),
                "line": i + 1,
                "rule": f"{CHECK_NAME}.reg-002-row-shape-broken",
                "message": f"Row REG-002 malformee (section {table_section}) : {len(parts)} colonnes attendues 7. Skipped.",
                "actual_row": line[:120],
            })
            continue

        path_raw, state, mech, consumers, mtime, adr_ref, threshold_raw = parts
        # Strip backticks markdown du path
        path_clean = path_raw.strip("`").strip()
        # Convertir threshold en int
        try:
            threshold_days = int(threshold_raw)
        except ValueError:
            threshold_days = DEFAULT_FRESHNESS_DAYS
        # Date mtime ISO
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", mtime):
            findings.append({
                "severity": "warning",
                "file": str(reg_path),
                "line": i + 1,
                "rule": f"{CHECK_NAME}.reg-002-mtime-malformed",
                "message": f"mtime '{mtime}' pour '{path_clean}' n'est pas au format ISO (YYYY-MM-DD). Skipped.",
            })
            continue

        rows.append({
            "path": path_clean,
            "state": state,
            "enforcement_mechanism": mech,
            "consumers": consumers,
            "registry_mtime": mtime,
            "last_referenced_adr": adr_ref,
            "threshold_days": threshold_days,
            "registry_line": i + 1,
        })

    if not rows and not findings:
        findings.append({
            "severity": "error",
            "file": str(reg_path),
            "rule": f"{CHECK_NAME}.reg-002-empty",
            "message": "Aucune row valide trouvee dans REG-002. Section ## attendue avec table 7 colonnes.",
        })

    return rows, findings


def check_filesystem_freshness(
    rows: list[dict],
    monorepo_canon: Path,
    today: date,
) -> list[dict]:
    """Pour chaque row REG-002, stat le filesystem et compare a threshold."""
    findings: list[dict] = []

    if not monorepo_canon.exists():
        findings.append({
            "severity": "warning",
            "file": str(monorepo_canon),
            "rule": f"{CHECK_NAME}.monorepo-canon-missing",
            "message": f"Monorepo canon path introuvable : {monorepo_canon}. Check skipped (env probablement CI sans monorepo).",
        })
        return findings

    files_on_fs: set[str] = set()
    for fs_path in monorepo_canon.rglob("*"):
        if fs_path.is_file() and fs_path.suffix in {".md", ".json", ".yaml", ".yml"}:
            rel = fs_path.relative_to(monorepo_canon).as_posix()
            files_on_fs.add(rel)

    rows_paths: set[str] = {r["path"] for r in rows}

    # Check 1 : pour chaque row registry, le fichier existe-t-il et est-il frais ?
    for row in rows:
        fs_file = monorepo_canon / row["path"]
        if not fs_file.exists():
            findings.append({
                "severity": "info",
                "file": f".spec/00-canon/{row['path']}",
                "rule": f"{CHECK_NAME}.registry-ghost-row",
                "message": f"Row REG-002 pointe vers fichier inexistant sur filesystem : {row['path']}. Soit fichier supprime, soit row obsolete.",
                "registry_line": row["registry_line"],
            })
            continue

        try:
            mtime_ts = fs_file.stat().st_mtime
            mtime_dt = datetime.fromtimestamp(mtime_ts, tz=timezone.utc).date()
        except OSError as e:
            findings.append({
                "severity": "warning",
                "file": f".spec/00-canon/{row['path']}",
                "rule": f"{CHECK_NAME}.fs-stat-failed",
                "message": f"stat impossible : {e}",
            })
            continue

        age_days = (today - mtime_dt).days
        if age_days > row["threshold_days"]:
            findings.append({
                "severity": "warning",
                "file": f".spec/00-canon/{row['path']}",
                "rule": f"{CHECK_NAME}.canon-stale",
                "message": (
                    f"Fichier canon stale : last_modified={mtime_dt.isoformat()} "
                    f"({age_days}j), threshold={row['threshold_days']}j. "
                    f"Etat: {row['state']}, mecanisme: {row['enforcement_mechanism']}."
                ),
                "age_days": age_days,
                "threshold_days": row["threshold_days"],
                "state": row["state"],
            })

    # Check 2 : fichiers sur filesystem absents de la registry (drift inverse)
    for fs_rel in sorted(files_on_fs - rows_paths):
        findings.append({
            "severity": "warning",
            "file": f".spec/00-canon/{fs_rel}",
            "rule": f"{CHECK_NAME}.registry-missing-row",
            "message": (
                f"Fichier canon present sur filesystem mais absent de REG-002. "
                f"Mettre a jour REG-002 (ajouter row) ou archiver le fichier."
            ),
        })

    return findings


def main(argv: list[str]) -> int:
    args = list(argv[1:])
    emit_json = "--json" in args
    strict = "--strict" in args
    args = [a for a in args if a not in ("--json", "--strict")]

    monorepo_path = Path(DEFAULT_MONOREPO)
    if "--monorepo" in args:
        idx = args.index("--monorepo")
        monorepo_path = Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    vault_path = Path(args[0]).resolve() if args else Path(".").resolve()
    monorepo_canon = monorepo_path / ".spec" / "00-canon"
    reg_path = vault_path / "ledger" / "canon-coverage" / "REG-002-canon-files.md"
    today = date.today()

    findings: list[dict] = []
    rows, parse_findings = parse_reg_002(reg_path)
    findings.extend(parse_findings)

    if rows:
        findings.extend(check_filesystem_freshness(rows, monorepo_canon, today))

    if strict:
        for f in findings:
            if f["severity"] == "warning":
                f["severity"] = "error"

    summary = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        summary[f["severity"]] = summary.get(f["severity"], 0) + 1

    if emit_json:
        print(json.dumps({"check": CHECK_NAME, "findings": findings, "summary": summary}, indent=2))
    else:
        for f in findings:
            loc = f["file"] + (f":L{f['line']}" if "line" in f else "")
            print(f"[{f['severity'].upper()}] {loc} ({f['rule']}): {f['message']}")
        print(f"\nTotal: {summary['error']} error(s), {summary['warning']} warning(s), {summary['info']} info")
        print(f"Registry parsed: {len(rows)} row(s) from {reg_path.name}")

    return 1 if summary["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
