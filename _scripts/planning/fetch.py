"""Fetch sources: GitHub PRs (vault + monorepo) + ADRs proposed (MOC-Decisions parse)."""
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def _gh_api_pr_list(repo: str) -> str:
    result = subprocess.run(
        ["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "200",
         "--json", "number,title,labels,state,url,updatedAt,author,isDraft"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout


_PRIORITY_LABEL_RE = re.compile(r"^P[0-8]$")


def _priority_from_labels(labels: list[dict[str, Any]]) -> str:
    for lbl in labels:
        name = lbl.get("name", "")
        if _PRIORITY_LABEL_RE.match(name):
            return name
    return "P5"  # triage default


def fetch_prs(repo: str) -> list[dict[str, Any]]:
    raw = _gh_api_pr_list(repo)
    prs = json.loads(raw)
    org, name = repo.split("/", 1)
    return [
        {
            "canonical_id": f"github:{org}/{name}:pr:{p['number']}",
            "item_type": "PR",
            "priority": _priority_from_labels(p.get("labels", [])),
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
