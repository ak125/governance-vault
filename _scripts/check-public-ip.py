#!/usr/bin/env python3
"""check-public-ip.py — Signale les adresses IPv4 publiques écrites dans le vault.

Le vault est un dépôt public : une adresse d'infrastructure publiée y reste lisible dans
l'historique Git, même une fois retirée du fichier. Un hôte se désigne par son rôle
(« hôte DEV », `<hote-prod>`), pas par son adresse.

Scope :
  - fichiers texte du vault (.md, .yaml, .yml, .json, .txt) ;
  - hors `.git/`, `.obsidian/`, `node_modules/` et `_scripts/` (code et fixtures de tests).

Détecte :
  toute adresse IPv4 routable sur Internet (`ipaddress.is_global`). Ne sont pas signalées :
  loopback, plages privées (RFC 1918), link-local, CGNAT, plages de documentation (RFC 5737),
  multicast et réservées ; ni un nombre à quatre segments collé à une lettre ou prolongé par
  un cinquième segment (numéro de version). IPv6 n'est pas couvert.

Sévérité : avertissement, jamais bloquant. Aucune règle du vault n'interdit une adresse IP ;
rendre ce contrôle bloquant serait une décision nouvelle, à porter par une règle (G1).

Le message ne contient ni l'adresse (le rapport de lint est publié lui aussi) ni les numéros
de ligne (le lint hebdomadaire déduplique ses issues sur le texte du message, qui doit rester
le même d'une semaine à l'autre). Les lignes sont dans le champ `lines` du finding et dans la
sortie texte.

Usage:
  python3 _scripts/check-public-ip.py [VAULT_PATH] [--json]

Exit 0 : les avertissements ne bloquent pas.
"""

from __future__ import annotations

import ipaddress
import json
import re
import sys
from pathlib import Path

CHECK_NAME = "public-ip"
RULE = "hygiene/public-ip"
TEXT_SUFFIXES = frozenset({".md", ".yaml", ".yml", ".json", ".txt"})
EXCLUDED_DIRS = frozenset({".git", ".obsidian", "node_modules", "_scripts"})

# Quatre segments décimaux, ni collés à un mot ou à un point (v2.0.9.1, x.1.2.3.4),
# ni prolongés par un cinquième segment (1.2.3.4.5). Un point final de phrase est admis.
_IPV4 = re.compile(r"(?<![\w.])(\d{1,3}(?:\.\d{1,3}){3})(?!\w)(?!\.\d)")


def is_public_ipv4(candidate: str) -> bool:
    try:
        address = ipaddress.IPv4Address(candidate)
    except ValueError:
        # Octet > 255 ou zéro initial : ce n'est pas une adresse (numéro de version, etc.).
        return False
    # `is_global` tient le multicast pour routable : il ne désigne pourtant aucun hôte.
    return address.is_global and not address.is_multicast


def public_ip_lines(text: str) -> list[int]:
    """Numéros (1-indexés) des lignes qui contiennent au moins une adresse IPv4 publique."""
    return [
        lineno
        for lineno, line in enumerate(text.splitlines(), 1)
        if any(is_public_ipv4(m.group(1)) for m in _IPV4.finditer(line))
    ]


def iter_text_files(vault_path: Path):
    for path in sorted(vault_path.rglob("*")):
        rel_parts = path.relative_to(vault_path).parts
        if EXCLUDED_DIRS.intersection(rel_parts[:-1]):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES and path.is_file():
            yield path


def main(argv: list[str]) -> int:
    vault_path = Path(argv[1]).resolve() if len(argv) > 1 and not argv[1].startswith("--") else Path.cwd()
    emit_json = "--json" in argv

    findings: list[dict] = []
    scanned = 0
    for path in iter_text_files(vault_path):
        scanned += 1
        lines = public_ip_lines(path.read_text(encoding="utf-8", errors="ignore"))
        if lines:
            findings.append({
                "severity": "warning",
                "file": path.relative_to(vault_path).as_posix(),
                "message": "public IPv4 address in a public repository: name the host by its role, not by its address",
                "rule": RULE,
                "lines": lines,
            })

    summary = {"error": 0, "warning": len(findings), "info": 0}

    if emit_json:
        print(json.dumps({"check": CHECK_NAME, "findings": findings, "summary": summary}, indent=2))
    else:
        for f in findings:
            where = ", ".join(str(n) for n in f["lines"])
            print(f"[WARNING] {f['file']} (line {where}): {f['message']}")
        print(f"\nTotal: 0 error(s), {summary['warning']} warning(s)  ({scanned} file(s) scanned)")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
