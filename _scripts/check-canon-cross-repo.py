#!/usr/bin/env python3
"""check-canon-cross-repo.py - Validate vault ADR refs to monorepo .spec/00-canon/ are alive.

Sens inverse de `check-canon-backlinks.py` (qui detecte les canon files orphans
cote monorepo). Ce script verifie l'integrite cross-repo dans le sens
**vault -> monorepo** : pour chaque mention `.spec/00-canon/<path>` dans un
ADR ou MOC du vault, verifie que le fichier existe physiquement dans le
monorepo. Si dead ref -> drift critique (vault prétend canon-aligned alors
que le path cite n'existe plus).

Implemente l'axe transverse d'ADR-048 sprint 3 :
  - check vault ADR -> monorepo cross-validation
  - mode warn-only initial (escalade J+30)
  - couples avec check-canon-backlinks.py (monorepo -> vault) pour
    couverture bidirectionnelle complete

Approche :
  1. Scan tous les ledger/decisions/adr/ADR-*.md + ops/moc/*.md du vault
  2. Pour chaque, extraire les mentions `.spec/00-canon/<path>` via regex
  3. Filtrer paths avec `{slug}`, `*`, `...` (templates/notations)
  4. Verifier existence (monorepo / .spec/00-canon/<path>).exists()
  5. Flag dead ref comme `error` (canon path cite mais introuvable)

Usage:
  python3 _scripts/check-canon-cross-repo.py [VAULT_PATH] [--monorepo PATH] [--json] [--strict]

Reference :
  - ADR-048 §Implementation Sprint 3 axe transverse
  - REG-002 (governance-vault) : check-canon-freshness.py couvre vault
    REG-002 vers monorepo filesystem ; ce script couvre vault ADRs/MOCs
    vers monorepo (refs textuelles)
  - check-canon-backlinks.py : sens inverse (monorepo orphans)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CHECK_NAME = "canon-cross-repo"

DEFAULT_MONOREPO = Path("/opt/automecanik/app")

# Scope de scan vault : ADRs (decisions canoniques) + MOCs (indices)
VAULT_SCAN_GLOBS = [
    "ledger/decisions/adr/ADR-*.md",
    "ops/moc/MOC-*.md",
]

# Pattern de mention canon : `.spec/00-canon/path/file.ext`
# Capture le path complet incluant sous-dossiers (ex. db-governance/sql-rules.md)
CANON_REF_PATTERN = re.compile(r"\.spec/00-canon/([\w./-]+\.(?:md|json|yaml|yml))")


def _is_template_or_dynamic(path: str) -> bool:
    """Skip paths avec templates/wildcards/notation canon."""
    if "..." in path:
        return True
    return any(c in path for c in ("{", "}", "*", "$"))


def scan_vault_for_canon_refs(vault_path: Path) -> dict[str, set[str]]:
    """Scan vault ADRs+MOCs, return mapping {canon_path: {source_files...}}."""
    refs: dict[str, set[str]] = {}
    for glob_pattern in VAULT_SCAN_GLOBS:
        for md_file in sorted(vault_path.glob(glob_pattern)):
            try:
                text = md_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel_source = str(md_file.relative_to(vault_path))
            for m in CANON_REF_PATTERN.finditer(text):
                canon_path = m.group(1).strip()
                if _is_template_or_dynamic(canon_path):
                    continue
                refs.setdefault(canon_path, set()).add(rel_source)
    return refs


def check_canon_paths_exist(
    refs: dict[str, set[str]],
    monorepo: Path,
) -> tuple[list[str], list[tuple[str, set[str]]]]:
    """Returns (alive, dead_with_sources)."""
    alive: list[str] = []
    dead: list[tuple[str, set[str]]] = []
    for canon_path, sources in sorted(refs.items()):
        full = monorepo / ".spec" / "00-canon" / canon_path
        if full.exists():
            alive.append(canon_path)
        else:
            dead.append((canon_path, sources))
    return alive, dead


def main(argv: list[str]) -> int:
    vault_path: Path | None = None
    monorepo_path: Path = DEFAULT_MONOREPO
    emit_json = "--json" in argv
    strict = "--strict" in argv

    positional = [a for a in argv[1:] if not a.startswith("--")]
    if positional:
        vault_path = Path(positional[0]).resolve()
    else:
        vault_path = Path.cwd()

    for i, arg in enumerate(argv):
        if arg == "--monorepo" and i + 1 < len(argv):
            monorepo_path = Path(argv[i + 1]).resolve()

    findings: list[dict] = []
    refs: dict[str, set[str]] = {}
    alive: list[str] = []
    dead: list[tuple[str, set[str]]] = []

    monorepo_canon = monorepo_path / ".spec" / "00-canon"
    if not monorepo_canon.exists():
        findings.append({
            "severity": "warning",
            "file": str(monorepo_canon),
            "rule": f"{CHECK_NAME}.monorepo-canon-missing",
            "message": (
                f"Monorepo canon path introuvable : {monorepo_canon}. "
                f"Check skipped (env probablement CI sans monorepo)."
            ),
        })
    else:
        refs = scan_vault_for_canon_refs(vault_path)
        if not refs:
            findings.append({
                "severity": "warning",
                "file": str(vault_path),
                "rule": f"{CHECK_NAME}.no-canon-refs-found",
                "message": (
                    "Aucune mention `.spec/00-canon/<path>` extraite des ADRs/MOCs "
                    "du vault. Le scan a peut-etre echoue ou aucun ADR ne reference "
                    "le canon (improbable)."
                ),
            })
        else:
            alive, dead = check_canon_paths_exist(refs, monorepo_path)
            for canon_path, sources in dead:
                sources_str = ", ".join(sorted(sources))
                findings.append({
                    "severity": "error",
                    "file": sources_str,
                    "rule": f"{CHECK_NAME}.dead-canon-ref",
                    "canon_path": canon_path,
                    "sources": sorted(sources),
                    "message": (
                        f"Vault cite `.spec/00-canon/{canon_path}` (source(s) : "
                        f"{sources_str}) mais ce path n'existe pas dans le monorepo. "
                        f"Drift cross-repo : ADR/MOC pointe vers un canon supprime "
                        f"ou renomme."
                    ),
                })

    if strict:
        for f in findings:
            if f["severity"] == "warning":
                f["severity"] = "error"

    summary = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        summary[f["severity"]] = summary.get(f["severity"], 0) + 1

    if emit_json:
        print(json.dumps({
            "check": CHECK_NAME,
            "findings": findings,
            "summary": summary,
            "stats": {
                "total_canon_refs_scanned": len(refs),
                "alive": len(alive),
                "dead": len(dead),
            },
        }, indent=2))
    else:
        print(f"# Canon Cross-Repo Drift Check (vault ADRs/MOCs -> monorepo .spec/00-canon/)")
        print()
        print(f"Vault path    : {vault_path}")
        print(f"Monorepo path : {monorepo_path}")
        print(f"Refs scanned  : {len(refs)}")
        print(f"Alive         : {len(alive)}")
        print(f"Dead          : {len(dead)}")
        print()
        if findings:
            for f in findings:
                marker = "[ERROR]" if f["severity"] == "error" else "[WARN]"
                print(f"{marker} {f['rule']}: {f['message']}")
            print()
        if dead:
            print("## Dead canon refs cross-repo")
            for canon_path, sources in dead:
                sources_str = ", ".join(sorted(sources))
                print(f"- `.spec/00-canon/{canon_path}` cite par : {sources_str}")
        print(f"\nTotal: {summary['error']} error(s), {summary['warning']} warning(s)")

    return 1 if summary["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
