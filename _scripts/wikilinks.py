#!/usr/bin/env python3
"""Wikilinks du vault : résolution par chemin, G2 (orphelins) et liens cassés ou ambigus (ADR-127).

Usage :
    wikilinks.py orphans [VAULT]   # G2 ; rapport 99-meta/orphans-report.md
    wikilinks.py links   [VAULT]   # liens cassés ou ambigus ; rapport 99-meta/broken-links-report.md

Lancé par `check-orphans.sh` et `check-broken-links.sh`, qui restent les points d'entrée de la CI et
des hooks. Codes de sortie : 0 = conforme, 1 = constat (rapport écrit), 2 = usage.

Un document est identifié par son chemin relatif à la racine du vault, sans l'extension `.md`.
Résolution d'un lien `[[cible|alias]]` ou `[[cible#ancre]]` :
- la cible contient `/` : chemin depuis la racine du vault (un `/` initial est accepté) ; il résout
  s'il existe exactement, sinon le lien est cassé ;
- la cible ne contient pas `/` : nom ; il résout si un seul document porte ce nom, il est ambigu si
  plusieurs le portent, cassé si aucun.
Un lien ambigu ne compte pour aucune cible. Un lien d'un document vers lui-même est valide mais ne
compte pas comme lien entrant (G2). Les `[[...]]` des blocs de code (``` et `inline`) sont ignorés.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

EXCLUDE_DIRS = frozenset({".git", ".obsidian"})
# Documents racines de G2 : non orphelins par nature.
ROOT_DIRS = ("ops/moc", "99-meta", "_assets", "_templates", "_scripts")
ROOT_FILES = frozenset({"README.md", "CLAUDE.md", "AGENTS.md"})

OK = "ok"
BROKEN = "broken"
AMBIGUOUS = "ambiguous"

ORPHANS_REPORT = "99-meta/orphans-report.md"
LINKS_REPORT = "99-meta/broken-links-report.md"

_LINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")
_FENCED_RE = re.compile(r"```[\s\S]*?```")
_INLINE_RE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class Link:
    source: str                # document source, chemin avec `.md`
    target: str                # cible telle qu'écrite, sans alias ni ancre
    status: str                # OK, BROKEN ou AMBIGUOUS
    resolved: tuple[str, ...]  # document résolu (OK) ou candidats (AMBIGUOUS), chemins avec `.md`


def is_root_path(rel: str) -> bool:
    if rel in ROOT_FILES:
        return True
    return any(rel == prefix or rel.startswith(prefix + "/") for prefix in ROOT_DIRS)


def markdown_files(root: Path) -> list[str]:
    """Chemins relatifs (séparateur `/`) des .md du vault, hors dossiers exclus, triés."""
    files = []
    for p in root.rglob("*.md"):
        rel = p.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        files.append(rel.as_posix())
    return sorted(files)


def strip_code(text: str) -> str:
    return _INLINE_RE.sub("", _FENCED_RE.sub("", text))


def link_targets(text: str) -> list[str]:
    """Cibles des wikilinks d'un texte, sans alias ni ancre, hors code."""
    targets = []
    for raw in _LINK_RE.findall(strip_code(text)):
        target = raw.strip().split("|", 1)[0].split("#", 1)[0]
        targets.append(target.strip().rstrip("\\"))
    return targets


class Index:
    def __init__(self, files: list[str]):
        self._by_path = {f[:-3]: f for f in files}
        self._by_name: dict[str, list[str]] = {}
        for f in files:
            self._by_name.setdefault(f.rsplit("/", 1)[-1][:-3], []).append(f)

    def resolve(self, target: str) -> tuple[str, tuple[str, ...]]:
        if "/" in target:
            hit = self._by_path.get(target.lstrip("/"))
            return (OK, (hit,)) if hit else (BROKEN, ())
        candidates = self._by_name.get(target, [])
        if len(candidates) == 1:
            return OK, (candidates[0],)
        if candidates:
            return AMBIGUOUS, tuple(candidates)
        return BROKEN, ()


def scan(root: Path) -> tuple[list[str], list[Link]]:
    """Documents du vault et tous leurs liens résolus."""
    files = markdown_files(root)
    index = Index(files)
    links = []
    for source in files:
        try:
            text = (root / source).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for target in link_targets(text):
            status, resolved = index.resolve(target)
            links.append(Link(source, target, status, resolved))
    return files, links


def find_orphans(root: Path) -> list[str]:
    """Documents non racines sans lien entrant résolu depuis un autre document (G2)."""
    files, links = scan(root)
    inbound = {
        link.resolved[0]
        for link in links
        if link.status == OK and link.resolved[0] != link.source
    }
    return [f for f in files if not is_root_path(f) and f not in inbound]


def find_link_problems(root: Path) -> tuple[list[Link], list[Link]]:
    """Liens cassés, liens ambigus."""
    _, links = scan(root)
    return (
        [link for link in links if link.status == BROKEN],
        [link for link in links if link.status == AMBIGUOUS],
    )


def _header(fields: dict[str, int]) -> list[str]:
    lines = ["---", "type: report", "status: generated",
             f"generated: {datetime.now().isoformat(timespec='seconds')}"]
    lines += [f"{key}: {value}" for key, value in fields.items()]
    return lines + ["---", ""]


def _publish(root: Path, rel: str, lines: list[str] | None) -> Path:
    """Écrit le rapport, ou supprime un rapport périmé quand il n'y a rien à signaler."""
    path = root / rel
    if lines is None:
        path.unlink(missing_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_orphans(root: Path) -> int:
    orphans = find_orphans(root)
    if not orphans:
        _publish(root, ORPHANS_REPORT, None)
        print("PASS: 0 orphan (G2 respected)")
        return 0
    lines = _header({"orphan_count": len(orphans)}) + [
        "# Orphans Report (G2 violation)", "",
        f"**Orphelins detectes**: {len(orphans)}", "",
        "## Documents orphelins", "",
        *[f"- `{rel}`" for rel in orphans],
        "", "## Action requise", "",
        "1. Lier ce document depuis un MOC (`ops/moc/MOC-*.md`), OU",
        "2. Lier depuis un INDEX-* local, OU",
        "3. Archiver dans `ledger/_archive/` (voir G8 Obsolete Handling)",
        "",
        "Un nom porte par plusieurs documents se lie par son chemin : `[[dossier/nom|alias]]` (ADR-127).",
    ]
    path = _publish(root, ORPHANS_REPORT, lines)
    print(f"FAIL: {len(orphans)} orphan(s) detected")
    print(f"Report: {path.relative_to(root).as_posix()}")
    return 1


def run_links(root: Path) -> int:
    broken, ambiguous = find_link_problems(root)
    if not broken and not ambiguous:
        _publish(root, LINKS_REPORT, None)
        print("PASS: 0 broken wikilink")
        return 0
    lines = _header({"broken_count": len(broken), "ambiguous_count": len(ambiguous)})
    lines += ["# Broken Wikilinks Report", "", f"**Liens casses detectes**: {len(broken)}", ""]
    if broken:
        lines += ["| Fichier source | Cible (cassee) |", "|----------------|----------------|"]
        lines += [f"| `{link.source}` | `[[{link.target}]]` |" for link in broken]
        lines.append("")
    lines += [f"**Liens ambigus detectes**: {len(ambiguous)}", ""]
    if ambiguous:
        lines += [
            "Nom porte par plusieurs documents : lier par le chemin, `[[dossier/nom|alias]]` (ADR-127).", "",
            "| Fichier source | Cible (ambigue) | Candidats |",
            "|----------------|-----------------|-----------|",
        ]
        for link in ambiguous:
            candidates = ", ".join(f"`{c[:-3]}`" for c in link.resolved)
            lines.append(f"| `{link.source}` | `[[{link.target}]]` | {candidates} |")
    path = _publish(root, LINKS_REPORT, lines)
    print(f"FAIL: {len(broken)} broken wikilink(s), {len(ambiguous)} ambiguous wikilink(s) detected")
    print(f"Report: {path.relative_to(root).as_posix()}")
    return 1


COMMANDS = {"orphans": run_orphans, "links": run_links}


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in COMMANDS or len(argv) > 2:
        print(f"Usage: wikilinks.py {{{'|'.join(COMMANDS)}}} [VAULT]", file=sys.stderr)
        return 2
    root = Path(argv[1] if len(argv) == 2 else Path(__file__).resolve().parent.parent).resolve()
    if not root.is_dir():
        print(f"Error: vault path not found: {root}", file=sys.stderr)
        return 2
    return COMMANDS[argv[0]](root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
