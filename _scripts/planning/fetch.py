"""Fetch sources: GitHub PRs (vault + monorepo) + ADRs proposed (MOC-Decisions parse)."""
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def _gh_api_pr_list(repo: str) -> str:
    result = subprocess.run(
        ["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "200",
         "--json", "number,title,labels,state,url,updatedAt,author,isDraft"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout


_PRIORITY_LABEL_RE = re.compile(r"^P[0-8]$")

# Title-based heuristics (lower-priority = higher number, P0 wins)
_TITLE_INCIDENT_RE = re.compile(r"\bincident\b|\bINC-\d|\boutage\b|\bSEV[0-9]\b", re.IGNORECASE)
_TITLE_CRITICAL_RE = re.compile(r"\b(critical|urgent|blocker|p0|hotfix|regression|security)\b", re.IGNORECASE)
_TITLE_FIX_RE = re.compile(r"^fix(?:\([^)]+\))?:|^bug:", re.IGNORECASE)
_TITLE_FEAT_RE = re.compile(r"^(feat|refactor|perf)(?:\([^)]+\))?:", re.IGNORECASE)
_TITLE_DEPS_RE = re.compile(r"^chore\(deps", re.IGNORECASE)
_TITLE_CHORE_RE = re.compile(r"^(chore|docs|test|ci|build)(?:\([^)]+\))?:", re.IGNORECASE)


def _classify_priority(pr: dict[str, Any], *, now: Optional[datetime] = None) -> str:
    """Smart priority classifier (Option C : heuristique + label override).

    Decision order :
      1. Label P0..P8 exact (manual override, wins all)
      2. Label-based : security/incident → P0, regression/blocker → P1, bug → P2
      3. Title-based : INC-/incident → P0, critical/urgent → P1, fix: → P2,
                       feat:/refactor:/perf: → P3, chore(deps) → P6,
                       chore:/docs:/test: → P5
      4. Draft + age >30j → P7 (deferred)
      5. Default → P5 (triage)
    """
    labels = pr.get("labels") or []
    label_names = [(lbl.get("name") or "").lower() for lbl in labels]

    # Rule 1 : exact P0..P8 label override (case-sensitive in registry but match either case)
    for lbl in labels:
        name = lbl.get("name", "")
        if _PRIORITY_LABEL_RE.match(name):
            return name
        # Also accept lowercase variant
        if _PRIORITY_LABEL_RE.match(name.upper()) and len(name) == 2:
            return name.upper()

    title = (pr.get("title") or "")

    # Rule 2 : label-based criticality
    if any(n in label_names for n in ("security", "incident", "outage", "sev0", "sev1")):
        return "P0"
    if any(n in label_names for n in ("regression", "blocker", "critical")):
        return "P1"
    if "bug" in label_names:
        return "P2"

    # Rule 3a : title-based incidents
    if _TITLE_INCIDENT_RE.search(title):
        return "P0"
    if _TITLE_CRITICAL_RE.search(title):
        return "P1"

    # Rule 3b : conventional commit prefixes
    if _TITLE_FIX_RE.search(title):
        return "P2"
    if _TITLE_DEPS_RE.search(title):  # chore(deps) — Dependabot
        return "P6"
    if _TITLE_CHORE_RE.search(title):
        return "P5"
    if _TITLE_FEAT_RE.search(title):
        return "P3"

    # Rule 4 : stale draft → deferred
    if pr.get("isDraft"):
        updated_at = pr.get("updatedAt")
        if updated_at and now is not None:
            try:
                ts = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                age_days = (now - ts).days
                if age_days > 30:
                    return "P7"
            except (ValueError, TypeError):
                pass

    # Rule 5 : default
    return "P5"


def fetch_prs(repo: str) -> list[dict[str, Any]]:
    raw = _gh_api_pr_list(repo)
    prs = json.loads(raw)
    org, name = repo.split("/", 1)
    now = datetime.now(timezone.utc)
    return [
        {
            "canonical_id": f"github:{org}/{name}:pr:{p['number']}",
            "item_type": "PR",
            "priority": _classify_priority(p, now=now),
            "status": "review" if not p.get("isDraft") else "in-progress",
            "title": p["title"],
            "owner": (p.get("author") or {}).get("login"),
            "depends_on": [],
            "adr_link": None,
            "blocked_reason": None,
            "url": p["url"],
            "updated_at": p["updatedAt"],
        }
        for p in prs
    ]


_ADR_ROW_RE = re.compile(r"^\|\s*ADR-(\d{3})\s*\|\s*([^|]+?)\s*\|\s*proposed\s*\|", re.M)


def parse_proposed_adrs(moc_decisions_path: Path) -> list[dict[str, Any]]:
    """Best-effort parser of MOC-Decisions ADR table.

    Assumes table format `| ADR-NNN | Title | proposed |`. Renforcer après PR-2 si
    le MOC réel diffère (p.ex. colonnes additionnelles, espaces variables, lignes
    multilignes). Pour l'instant, MVP suffisant — un échec de match ne casse rien
    (juste 0 ADRs renvoyés).

    Note `source_status` vs `status` : `source_status` capture l'état brut amont
    (ADR `proposed`), `status` est la projection canon (planning-status.yml).
    Mapping : `proposed` (amont) → `review` (canon, "PR opened, awaiting review/merge"
    metaphor : ADR awaiting promotion). Voir tableau mapping en tête du plan.
    `source_status` est exclu du semantic_hash (volatile).
    """
    text = moc_decisions_path.read_text()
    matches = _ADR_ROW_RE.findall(text)
    return [
        {
            "canonical_id": f"vault:adr:ADR-{num}",
            "item_type": "ADR",
            "priority": "P1",  # all proposed ADRs are P1 by default
            "status": "review",      # canon (planning-status.yml)
            "source_status": "proposed",  # raw upstream — excluded from semantic_hash
            "title": title.strip(),
            "owner": None,
            "depends_on": [],
            "adr_link": f"ADR-{num}",
            "blocked_reason": None,
        }
        for num, title in matches
    ]
