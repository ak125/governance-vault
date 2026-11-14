#!/usr/bin/env python3
"""Résolution des wikilinks du vault, partagée par check-orphans.sh et check-broken-links.sh (ADR-127).

Un document est identifié par son chemin relatif à la racine du vault, sans l'extension `.md`.

Règles de résolution d'un lien `[[cible|alias]]` ou `[[cible#ancre]]` :
- la cible contient `/` : c'est un chemin depuis la racine du vault (un `/` initial est accepté) ;
  il résout s'il existe exactement, sinon le lien est cassé ;
- la cible ne contient pas `/` : c'est un nom ; il résout si un seul document porte ce nom,
  il est ambigu si plusieurs le portent, cassé si aucun.

Un lien ambigu ne compte pour aucune cible. Un lien d'un document vers lui-même est valide
mais ne compte pas comme lien entrant (G2).

Les `[[...]]` des blocs de code (``` et `inline`) sont ignorés.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

EXCLUDE_DIRS = frozenset({".git", ".obsidian"})
# Documents racines de G2 : non orphelins par nature.
ROOT_DIRS = ("ops/moc", "99-meta", "_assets", "_templates", "_scripts")
ROOT_FILES = frozenset({"README.md", "CLAUDE.md", "AGENTS.md"})

OK = "ok"
BROKEN = "broken"
AMBIGUOUS = "ambiguous"

_LINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")
_FENCED_RE = re.compile(r"```[\s\S]*?```")
_INLINE_RE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class Link:
    source: str              # chemin du document source, avec `.md`
    target: str              # cible telle qu'écrite, sans alias ni ancre
    status: str              # OK, BROKEN ou AMBIGUOUS
    resolved: tuple[str, ...]  # document résolu (OK) ou candidats (AMBIGUOUS), avec `.md`


def is_root_path(rel: str) -> bool:
    if rel in ROOT_FILES:
        return True
    return any(rel == prefix or rel.startswith(prefix + "/") for prefix in ROOT_DIRS)


def markdown_files(root: Path) -> list[str]:
    """Chemins relatifs (séparateur `/`) des .md du vault, hors dossiers exclus, triés."""
    files = []
    for p in root.rglob("*.md"):
        rel_parts = p.relative_to(root).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        files.append(p.relative_to(root).as_posix())
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
        self.files = files
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
    """Retourne les documents du vault et tous leurs liens résolus."""
    root = Path(root)
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


def orphans(root: Path) -> list[str]:
    """Documents non racines sans lien entrant résolu depuis un autre document (G2)."""
    files, links = scan(root)
    inbound = {
        link.resolved[0]
        for link in links
        if link.status == OK and link.resolved[0] != link.source
    }
    return [f for f in files if not is_root_path(f) and f not in inbound]


def link_problems(root: Path) -> tuple[list[Link], list[Link]]:
    """Liens cassés et liens ambigus."""
    _, links = scan(root)
    return (
        [link for link in links if link.status == BROKEN],
        [link for link in links if link.status == AMBIGUOUS],
    )
