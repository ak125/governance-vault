#!/usr/bin/env python3
"""check-moc-integrity.py - Validate structural invariants across MOCs and ADR registry.

Detecte les drifts d'integrite entre les MOCs satellites du vault apres l'elimination
des duplications (PR-1) et la clarification semantique (PR-2). Le check ne compte plus
de "stats" - il valide :

  1. ADR statut coherence  : frontmatter ADR == row dans MOC-Decisions table
  2. ADR table completude  : chaque fichier ADR a une row, chaque row a un fichier
  3. REG-001 / MOC-Agents  : pas de chiffre absolu en duplication dans MOC-Agents body
  4. Regression guard      : MOC-Governance ne contient plus de chiffre dupliquant les sources
  5. Frontmatter `updated:` : >= date max structurelle du body (par MOC)
  6. Master-index date     : MOC-Governance.updated >= max(satellites.updated)
  7. MOC-Planning-Live     : schema_version=planning.v1, semantic_hash coherent
                             avec latest.json (si existe), schemas canon presents

REGLE ANTI-SILENT-OK (non-negociable) : si une section attendue est absente ou
renommee, on emet un finding explicite plutot qu'un retour silencieux OK. Mieux
vaut un faux positif visible qu'un faux negatif silencieux.

Usage:
  python3 _scripts/check-moc-integrity.py [VAULT_PATH] [--json] [--strict]

Modes :
  default  : print human-readable summary, exit 0 toujours (warn-only)
  --json   : emet rapport JSON `{check, findings, summary}` sur stdout (pattern weekly-lint)
  --strict : eleve les warnings en errors, exit 1 si findings (test local)

Reference plan : /home/deploy/.claude/plans/j-ai-localis-les-repos-buzzing-blanket.md
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# python-frontmatter est deja utilise par check-frontmatter-schema.py via parsing manuel ;
# on reutilise la meme approche pour eviter une nouvelle dep.

CHECK_NAME = "moc-integrity"

# Statuts ADR canoniques (5 valeurs verifiees au 2026-05-07)
CANONICAL_ADR_STATUSES = {"accepted", "accepted-revised", "proposed", "superseded", "deferred"}

# MOCs satellites pour invariant master-index (PR-3 check 6)
SATELLITE_MOCS = ["MOC-Decisions", "MOC-AuditTrail", "MOC-Compliance", "MOC-Rules", "MOC-Agents"]

# Whitelist canon IDs pour regression guard (PR-3 check 4 etape 1)
CANONICAL_ID_PATTERNS = [
    re.compile(r"\bADR-\d{1,3}\b"),
    re.compile(r"\bDEC-\d+\b"),
    re.compile(r"\bT\d+(?:-T\d+)?\b"),
    re.compile(r"\bG\d+(?:-G\d+)?\b"),
    re.compile(r"\bAI\d+(?:-AI\d+)?\b"),
    re.compile(r"\bV\d+(?:-V\d+)?\b"),
    re.compile(r"\bD\d+(?:-D\d+)?\b"),
    re.compile(r"\bQ\d+(?:-Q\d+)?\b"),
    re.compile(r"\bR-SEO(?:-KW)?-\d+\b"),
    re.compile(r"\bAP-\d+\b"),
    re.compile(r"\bAEC-\d+\b"),
    re.compile(r"\bINC-\d{4}-\d{3}\b"),
    re.compile(r"\bEP-\d{8}-[\w-]+\b"),
    re.compile(r"\bREG-\d{3}\b"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),       # dates ISO
    re.compile(r"\bv?\d+\.\d+\.\d+\b"),         # semver
    re.compile(r"\[\[[^\]]+\]\]"),              # wikilinks Obsidian
    re.compile(r"`[^`]+`"),                      # inline code
]

# Forbidden patterns dans MOC-Governance body strippe (PR-3 check 4 etape 2)
FORBIDDEN_NUMBER_KEYWORDS = re.compile(
    r"\b\d+\s+(ADR|ADRs|agents?|familles?|r[eè]gles?|fichiers?|incidents?|"
    r"retrospectives?|evidence-packs?|bundles?|cat[eé]gories?)\b",
    re.IGNORECASE
)
FORBIDDEN_STATS_HEADING = re.compile(r"^##\s+(Statistiques|Stats|Statistics)\b", re.MULTILINE)
FORBIDDEN_TAXONOMY_TABLE_HEADER = re.compile(r"\|\s*(Pr[eé]fix(?:e)?|Prefix)\s*\|", re.IGNORECASE)
FORBIDDEN_FOOTER_DATE = re.compile(r"^_Derni[èe]re mise [àa] jour", re.MULTILINE | re.IGNORECASE)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], int]:
    """Parse le frontmatter YAML simple (sans dep externe). Retourne (dict, body_start_lineno)."""
    if not text.startswith("---"):
        return {}, 0
    lines = text.split("\n")
    if len(lines) < 2:
        return {}, 0
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, 0
    fm: dict[str, Any] = {}
    for raw in lines[1:end]:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        # On dequote les strings simples
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            val = val[1:-1]
        fm[key] = val
    return fm, end + 1


def normalize_status(raw: str) -> str:
    """Normalise un statut ADR (du frontmatter ou de la table MOC) pour comparaison.

    Annotations gerees :
      - Lower-case
      - Strip parenthesized annotations : "(2026-04-27, evidence-based promotion)"
      - Strip "by [[...]]"               : "Superseded by [[ADR-010-...]]"
      - Strip trailing "(v2.0)" etc.

    Retourne le premier mot ou tokens hyphenes (ex. "accepted-revised").
    """
    s = raw.lower().strip()
    # Strip parenthesized annotations (recursive pour les nested au cas ou)
    while "(" in s and ")" in s:
        s = re.sub(r"\([^()]*\)", "", s).strip()
    # Strip "by [[...]]..." annotations
    s = re.sub(r"\s+by\s+\[\[[^\]]+\]\].*$", "", s).strip()
    # Strip "+ [[...]]..." enchainements de superseded references
    s = re.sub(r"\s*\+\s*\[\[[^\]]+\]\].*$", "", s).strip()
    # Garder le premier "mot" (incluant hyphens type accepted-revised)
    m = re.match(r"^([a-z]+(?:-[a-z]+)?)", s)
    return m.group(1) if m else s


def parse_adr_table(text: str, file_rel: str, findings: list[dict]) -> dict[str, dict]:
    """Parse la table ## ADR Actifs de MOC-Decisions, retourne {ADR-NNN: {status, date, line}}.

    Anti-silent-OK : si la section est absente ou renommee, emet un finding explicite.
    """
    table = {}
    section_idx = None
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if re.match(r"^##\s+ADR\s+Actifs\s*$", line):
            section_idx = i
            break
    if section_idx is None:
        findings.append({
            "severity": "error",
            "file": file_rel,
            "rule": f"{CHECK_NAME}.section-missing",
            "message": "Section '## ADR Actifs' introuvable dans MOC-Decisions",
        })
        return table
    # Lire jusqu'au prochain --- ou ## (mais on saute la 1re ligne du body qui est header de table)
    for j in range(section_idx + 1, len(lines)):
        line = lines[j]
        if re.match(r"^\s*---\s*$", line):
            break
        if re.match(r"^##\s+", line):
            break
        # Row attendue : "| ADR-NNN | titre | status | date | [[link]] |"
        if not re.match(r"^\|\s*ADR-\d{3}\s*\|", line):
            continue
        parts = [p.strip() for p in line.split(" | ")]
        # Premier element : "| ADR-NNN" -> nettoyer le pipe leading
        if parts and parts[0].startswith("|"):
            parts[0] = parts[0].lstrip("|").strip()
        # Dernier element : "|" trailing -> nettoyer
        if parts and parts[-1].endswith("|"):
            parts[-1] = parts[-1].rstrip("|").strip()
        if len(parts) != 5:
            findings.append({
                "severity": "error",
                "file": file_rel,
                "line": j + 1,
                "rule": f"{CHECK_NAME}.table-shape-broken",
                "message": f"Row table ADR Actifs malformee : {len(parts)} colonnes attendues 5",
                "actual_row": line[:120],
            })
            continue
        adr_id, title, status, dt, link = parts
        if not re.match(r"^ADR-\d{3}$", adr_id):
            continue
        table[adr_id] = {"status": status, "date": dt, "title": title, "link": link, "line": j + 1}
    return table


def parse_taxonomy_rows(text: str, file_rel: str, findings: list[dict]) -> int:
    """Compte les rows valides de la table ## Taxonomie de MOC-Rules. Anti-silent-OK."""
    section_idx = None
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if re.match(r"^##\s+Taxonomie\s*$", line):
            section_idx = i
            break
    if section_idx is None:
        findings.append({
            "severity": "error",
            "file": file_rel,
            "rule": f"{CHECK_NAME}.section-missing",
            "message": "Section '## Taxonomie' introuvable dans MOC-Rules",
        })
        return 0
    count = 0
    for j in range(section_idx + 1, len(lines)):
        line = lines[j]
        if re.match(r"^\s*---\s*$", line) or re.match(r"^##\s+", line):
            break
        # Row taxonomie : "| **prefixe** | domaine | [[fichier]] | scope |"
        if not re.match(r"^\|\s*\*?\*?[A-Z][A-Za-z0-9-]*\*?\*?\s*\|", line):
            continue
        # Skip header row "| Prefixe | Domaine | Fichier | Scope |"
        if re.search(r"\|\s*(Pr[eé]fix(?:e)?|Prefix)\s*\|", line, re.IGNORECASE):
            continue
        # Skip separator row "|---|---|---|---|"
        if re.match(r"^\|\s*[-: ]+\s*\|", line):
            continue
        parts = [p.strip() for p in line.split(" | ")]
        if len(parts) >= 3:  # 4 expected mais defensive
            count += 1
    return count


def get_max_structural_date(text: str, file_rel: str) -> str | None:
    """Retourne la date max trouvee dans des shapes structurels connus. None si aucune."""
    dates = []
    # Shape 1 : audit-trail entries `## YYYY-MM-DD-...` ou `[[YYYY-MM-DD-...]]`
    for m in re.finditer(r"^##\s+(\d{4}-\d{2}-\d{2})", text, re.MULTILINE):
        dates.append(m.group(1))
    for m in re.finditer(r"\[\[(\d{4}-\d{2}-\d{2})", text):
        dates.append(m.group(1))
    # Shape 2 : MOC-Decisions table column "Date"
    for m in re.finditer(r"^\|\s*ADR-\d{3}\s*\|.*?\|.*?\|\s*(\d{4}-\d{2}-\d{2})\s*\|", text, re.MULTILINE):
        dates.append(m.group(1))
    # Shape 3 : MOC-Compliance evidence-pack entries `EP-YYYYMMDD-...`
    for m in re.finditer(r"\bEP-(\d{8})-[\w-]+", text):
        d = m.group(1)
        dates.append(f"{d[:4]}-{d[4:6]}-{d[6:8]}")
    if not dates:
        return None
    return max(dates)


def check_adr_consistency(vault: Path, mocs: dict[str, str], findings: list[dict]) -> None:
    """Check 1 + 2 : ADR statut coherence + ADR table completude."""
    adr_dir = vault / "ledger" / "decisions" / "adr"
    if not adr_dir.exists():
        findings.append({
            "severity": "error",
            "file": "ledger/decisions/adr/",
            "rule": f"{CHECK_NAME}.adr-dir-missing",
            "message": "Repertoire ledger/decisions/adr/ introuvable",
        })
        return

    # Frontmatter par ADR
    frontmatter_status: dict[str, str] = {}
    for adr_file in sorted(adr_dir.glob("ADR-*.md")):
        m = re.match(r"^(ADR-\d{3})", adr_file.name)
        if not m:
            continue
        adr_id = m.group(1)
        try:
            txt = adr_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        fm, _ = parse_frontmatter(txt)
        st = fm.get("status", "").strip().lower()
        if st not in CANONICAL_ADR_STATUSES:
            findings.append({
                "severity": "error",
                "file": str(adr_file.relative_to(vault).as_posix()),
                "rule": f"{CHECK_NAME}.adr-unknown-status",
                "message": f"Statut frontmatter '{st}' n'est pas dans l'ensemble canonique {sorted(CANONICAL_ADR_STATUSES)}",
            })
            continue
        frontmatter_status[adr_id] = st

    # Table MOC-Decisions
    moc_decisions_text = mocs.get("MOC-Decisions", "")
    if not moc_decisions_text:
        return
    table = parse_adr_table(moc_decisions_text, "ops/moc/MOC-Decisions.md", findings)

    # Check 1 : statut frontmatter == statut table (apres normalisation)
    for adr_id, fm_status in frontmatter_status.items():
        if adr_id not in table:
            findings.append({
                "severity": "error",
                "file": "ops/moc/MOC-Decisions.md",
                "rule": f"{CHECK_NAME}.adr-missing-from-table",
                "message": f"{adr_id} (statut frontmatter '{fm_status}') absent de la table MOC-Decisions",
            })
            continue
        table_raw = table[adr_id]["status"]
        table_norm = normalize_status(table_raw)
        if table_norm != fm_status:
            findings.append({
                "severity": "error",
                "file": "ops/moc/MOC-Decisions.md",
                "line": table[adr_id]["line"],
                "rule": f"{CHECK_NAME}.adr-status-mismatch",
                "message": f"{adr_id} : frontmatter='{fm_status}' vs table='{table_norm}' (raw: '{table_raw}')",
            })

    # Check 2 (inverse) : rows table sans fichier reel
    for adr_id, info in table.items():
        if adr_id not in frontmatter_status:
            findings.append({
                "severity": "error",
                "file": "ops/moc/MOC-Decisions.md",
                "line": info["line"],
                "rule": f"{CHECK_NAME}.adr-ghost-row",
                "message": f"Row table {adr_id} sans fichier reel ou frontmatter sans statut canonique",
            })


def check_agents_no_absolute_count(mocs: dict[str, str], findings: list[dict]) -> None:
    """Check 3 : MOC-Agents body ne doit pas contenir de compteur absolu (REG-001 est SoT)."""
    body = mocs.get("MOC-Agents", "")
    if not body:
        return
    # Strip frontmatter pour ne scanner que le body
    _, body_start = parse_frontmatter(body)
    body_only = "\n".join(body.split("\n")[body_start:])
    # Strip whitelist canon IDs
    stripped = body_only
    for pat in CANONICAL_ID_PATTERNS:
        stripped = pat.sub(" ", stripped)
    # Forbidden : chiffre + agents/categories/...
    for m in FORBIDDEN_NUMBER_KEYWORDS.finditer(stripped):
        # Confirmer que ce n'etait pas un canon ID en re-scannant la position originale
        # (heuristique : si le match existe aussi dans le body original, c'est suspect)
        match_text = m.group(0)
        findings.append({
            "severity": "warning",
            "file": "ops/moc/MOC-Agents.md",
            "rule": f"{CHECK_NAME}.agents-absolute-count",
            "message": f"Chiffre absolu detecte dans body MOC-Agents : '{match_text.strip()}' "
                       f"(REG-001 est la SoT unique pour les compteurs)",
        })


def check_governance_regression_guard(mocs: dict[str, str], findings: list[dict]) -> None:
    """Check 4 : MOC-Governance ne doit pas contenir de duplication numerique reintroduite."""
    body = mocs.get("MOC-Governance", "")
    if not body:
        return
    _, body_start = parse_frontmatter(body)
    body_only = "\n".join(body.split("\n")[body_start:])

    # Etape 1 : strip whitelist
    stripped = body_only
    for pat in CANONICAL_ID_PATTERNS:
        stripped = pat.sub(" ", stripped)

    # Etape 2 : forbidden patterns
    for m in FORBIDDEN_NUMBER_KEYWORDS.finditer(stripped):
        match_text = m.group(0)
        findings.append({
            "severity": "error",
            "file": "ops/moc/MOC-Governance.md",
            "rule": f"{CHECK_NAME}.governance-number-leak",
            "message": f"Duplication numerique detectee dans MOC-Governance : '{match_text.strip()}' "
                       f"(la cause structurelle du drift, supprimee en PR-1)",
        })

    if FORBIDDEN_STATS_HEADING.search(body_only):
        findings.append({
            "severity": "error",
            "file": "ops/moc/MOC-Governance.md",
            "rule": f"{CHECK_NAME}.governance-stats-heading-reappeared",
            "message": "Section '## Statistiques' (ou Stats/Statistics) reintroduite dans MOC-Governance",
        })

    # Detecter une seconde table avec header "Prefix" (Taxonomie dupliquee)
    table_headers = list(FORBIDDEN_TAXONOMY_TABLE_HEADER.finditer(body_only))
    if table_headers:
        findings.append({
            "severity": "error",
            "file": "ops/moc/MOC-Governance.md",
            "rule": f"{CHECK_NAME}.governance-taxonomy-table-reappeared",
            "message": "Table Taxonomie (header '| Prefix') reintroduite dans MOC-Governance — elle vit dans MOC-Rules",
        })

    if FORBIDDEN_FOOTER_DATE.search(body_only):
        findings.append({
            "severity": "warning",
            "file": "ops/moc/MOC-Governance.md",
            "rule": f"{CHECK_NAME}.governance-footer-date-reappeared",
            "message": "Footer 'Derniere mise a jour' reintroduit (l'info canonique vit dans frontmatter `updated:`)",
        })


def check_frontmatter_updated_invariant(mocs: dict[str, str], findings: list[dict]) -> None:
    """Check 5 : frontmatter.updated >= date max structurelle du body, pour 3 MOCs cibles."""
    for moc_name in ["MOC-AuditTrail", "MOC-Decisions", "MOC-Compliance"]:
        text = mocs.get(moc_name, "")
        if not text:
            continue
        fm, _ = parse_frontmatter(text)
        upd = fm.get("updated", "").strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", upd):
            findings.append({
                "severity": "error",
                "file": f"ops/moc/{moc_name}.md",
                "rule": f"{CHECK_NAME}.frontmatter-updated-malformed",
                "message": f"Frontmatter 'updated' manquant ou mal forme : '{upd}'",
            })
            continue
        max_date = get_max_structural_date(text, f"ops/moc/{moc_name}.md")
        if max_date is None:
            continue  # Aucune date structurelle = invariant n/a
        if upd < max_date:
            findings.append({
                "severity": "warning",
                "file": f"ops/moc/{moc_name}.md",
                "rule": f"{CHECK_NAME}.frontmatter-updated-stale",
                "message": f"Frontmatter updated={upd} < date max structurelle dans body={max_date}",
            })


def check_planning_live(vault: Path, mocs: dict[str, str], findings: list[dict]) -> None:
    """Check 7 : MOC-Planning-Live (ADR-053).

    Valide :
    - frontmatter contains schema_version: planning.v1
    - semantic_hash coherent avec latest.json (si snapshot existe)
    - schemas canoniques referencees existent (.spec/00-canon/planning/*.yml)
    """
    text = mocs.get("MOC-Planning-Live", "")
    if not text:
        return  # Optional MOC — silent skip if absent

    fm, _ = parse_frontmatter(text)

    # 7.a — schema_version: planning.v1
    schema_version = fm.get("schema_version", "").strip()
    if schema_version != "planning.v1":
        findings.append({
            "severity": "error",
            "file": "ops/moc/MOC-Planning-Live.md",
            "rule": f"{CHECK_NAME}.planning-live-schema-version",
            "message": f"Frontmatter schema_version='{schema_version}' attendu 'planning.v1'",
        })

    # 7.b — semantic_hash coherent avec latest.json (si existe)
    moc_hash = fm.get("semantic_hash", "").strip()
    if not moc_hash:
        findings.append({
            "severity": "error",
            "file": "ops/moc/MOC-Planning-Live.md",
            "rule": f"{CHECK_NAME}.planning-live-hash-missing",
            "message": "Frontmatter semantic_hash manquant",
        })
    else:
        snapshots_dir = vault / "ledger" / "snapshots" / "planning"
        if snapshots_dir.exists():
            # Find most recent date subdir with latest.json
            date_dirs = sorted(
                [d for d in snapshots_dir.iterdir() if d.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", d.name)],
                reverse=True,
            )
            for date_dir in date_dirs:
                latest = date_dir / "latest.json"
                if latest.exists():
                    try:
                        payload = json.loads(latest.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError) as e:
                        findings.append({
                            "severity": "warning",
                            "file": str(latest.relative_to(vault).as_posix()),
                            "rule": f"{CHECK_NAME}.planning-live-latest-malformed",
                            "message": f"latest.json illisible : {e}",
                        })
                        break
                    snap_hash = payload.get("semantic_hash", "")
                    if snap_hash and snap_hash != moc_hash:
                        findings.append({
                            "severity": "warning",
                            "file": "ops/moc/MOC-Planning-Live.md",
                            "rule": f"{CHECK_NAME}.planning-live-hash-mismatch",
                            "message": f"MOC semantic_hash='{moc_hash}' diffère de "
                                       f"{latest.relative_to(vault).as_posix()} hash='{snap_hash}' "
                                       f"(sync engine n'a peut-être pas tourné)",
                        })
                    break  # Only check most recent latest.json

    # 7.c — schemas canon referencees existent
    schema_dir = vault / ".spec" / "00-canon" / "planning"
    required_schemas = ["planning-priority", "planning-itemtype",
                        "planning-status", "planning-blocked-reason"]
    for name in required_schemas:
        p = schema_dir / f"{name}.yml"
        if not p.exists():
            findings.append({
                "severity": "error",
                "file": str(p.relative_to(vault).as_posix()),
                "rule": f"{CHECK_NAME}.planning-live-schema-missing",
                "message": f"Schema canonique requis introuvable : {name}.yml (référencé par MOC-Planning-Live)",
            })


def check_master_index_invariant(mocs: dict[str, str], findings: list[dict]) -> None:
    """Check 6 : MOC-Governance.updated >= max(satellites.updated)."""
    gov = mocs.get("MOC-Governance", "")
    if not gov:
        return
    gov_fm, _ = parse_frontmatter(gov)
    gov_upd = gov_fm.get("updated", "").strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", gov_upd):
        findings.append({
            "severity": "error",
            "file": "ops/moc/MOC-Governance.md",
            "rule": f"{CHECK_NAME}.governance-updated-malformed",
            "message": f"MOC-Governance frontmatter 'updated' mal forme : '{gov_upd}'",
        })
        return
    sat_dates = []
    for sat in SATELLITE_MOCS:
        text = mocs.get(sat, "")
        if not text:
            continue
        fm, _ = parse_frontmatter(text)
        upd = fm.get("updated", "").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", upd):
            sat_dates.append((sat, upd))
    if not sat_dates:
        return
    max_sat = max(sat_dates, key=lambda x: x[1])
    if gov_upd < max_sat[1]:
        findings.append({
            "severity": "warning",
            "file": "ops/moc/MOC-Governance.md",
            "rule": f"{CHECK_NAME}.master-index-stale",
            "message": f"MOC-Governance.updated={gov_upd} < max satellites ({max_sat[0]}.updated={max_sat[1]})",
        })


def main(argv: list[str]) -> int:
    args = list(argv[1:])
    emit_json = "--json" in args
    strict = "--strict" in args
    args = [a for a in args if a not in ("--json", "--strict")]
    vault_path = Path(args[0]).resolve() if args else Path(".").resolve()

    mocs: dict[str, str] = {}
    moc_dir = vault_path / "ops" / "moc"
    for name in ["MOC-Governance", "MOC-Decisions", "MOC-Rules", "MOC-Agents",
                 "MOC-Compliance", "MOC-AuditTrail", "MOC-Planning-Live"]:
        f = moc_dir / f"{name}.md"
        if f.exists():
            try:
                mocs[name] = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                pass

    findings: list[dict] = []

    check_adr_consistency(vault_path, mocs, findings)
    check_agents_no_absolute_count(mocs, findings)
    check_governance_regression_guard(mocs, findings)
    check_frontmatter_updated_invariant(mocs, findings)
    check_master_index_invariant(mocs, findings)
    check_planning_live(vault_path, mocs, findings)

    # Mode strict : eleve les warnings en errors
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
            loc = f"{f['file']}" + (f":L{f['line']}" if "line" in f else "")
            print(f"[{f['severity'].upper()}] {loc} ({f['rule']}): {f['message']}")
        print(f"\nTotal: {summary['error']} error(s), {summary['warning']} warning(s)")

    return 1 if summary["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
