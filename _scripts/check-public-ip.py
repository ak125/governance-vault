#!/usr/bin/env python3
"""check-public-ip.py — Signale les adresses IPv4 publiques écrites dans le vault.

Le vault est un dépôt public : une adresse d'infrastructure publiée y reste lisible dans
l'historique Git, même une fois retirée du fichier. Un hôte se désigne par son rôle
(« hôte DEV », `<hote-prod>`), pas par son adresse.

Scope :
  - tous les fichiers texte du vault, quelle que soit leur extension (notes, scripts,
    politiques, fichiers sans extension) ; un fichier qui contient un octet nul est tenu
    pour binaire et n'est pas lu ;
  - hors dossiers `.git/`, `node_modules/` et `__pycache__/`, à toute profondeur ;
  - hors ce script et son fichier de tests, qui portent des adresses d'essai.

Détecte :
  toute adresse IPv4 routable sur Internet (`ipaddress.is_global`). Ne sont pas signalées :
  loopback, plages privées (RFC 1918), link-local, CGNAT, plages de documentation (RFC 5737),
  multicast et réservées ; ni un nombre à quatre segments collé à une lettre ou à un chiffre,
  ou pris dans une suite de cinq segments ou plus (numéro de version).

Limites :
  IPv6, formes déguisées (tirets, `[.]`, points échappés, entier, hexadécimal) et fichiers
  encodés autrement qu'en UTF-8 ne sont pas couverts. Une version à quatre segments sans
  préfixe (`120.0.0.0`) ou un numéro de section à quatre niveaux est signalé à tort : le
  contrôle avertit, il ne tranche pas.

Sévérité : avertissement, jamais bloquant. Aucune règle du vault n'interdit une adresse IP ;
rendre ce contrôle bloquant serait une décision nouvelle, à porter par une règle (G1).

Le message ne contient ni l'adresse (le rapport de lint est publié lui aussi) ni les numéros
de ligne (le lint hebdomadaire déduplique ses issues sur le texte du message, qui doit rester
le même d'une semaine à l'autre). Les lignes sont dans le champ `lines` du finding et dans la
sortie texte.

Usage:
  python3 _scripts/check-public-ip.py [VAULT_PATH] [--json]

Exit 0 : les avertissements ne bloquent pas. Exit 2 : arguments invalides ou VAULT_PATH qui
n'est pas un dossier (un chemin faux ne doit pas passer pour « aucune adresse »).
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import sys
from pathlib import Path

CHECK_NAME = "public-ip"
RULE = "hygiene/public-ip"
EXCLUDED_DIRS = frozenset({".git", "node_modules", "__pycache__"})
EXCLUDED_FILES = frozenset({"_scripts/check-public-ip.py", "_scripts/test_check_public_ip.py"})

# Quatre segments décimaux. Refusés : collés à une lettre ou à un chiffre (v2.0.9.1), ou pris
# dans une suite plus longue (1.2.3.4.5, dans un sens comme dans l'autre). Admis : un point
# final de phrase, un soulignement (italique Markdown, snake_case), un nom d'hôte autour
# (static.<adresse>.example.net).
_IPV4 = re.compile(r"(?<![^\W_])(?<!\d\.)(\d{1,3}(?:\.\d{1,3}){3})(?![^\W_])(?!\.\d)")


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
    # split("\n") et non splitlines() : ce dernier coupe aussi sur le saut de page et d'autres
    # séparateurs Unicode, ce qui décale les numéros par rapport à ceux d'un éditeur.
    return [
        lineno
        for lineno, line in enumerate(text.split("\n"), 1)
        if any(is_public_ipv4(m.group(1)) for m in _IPV4.finditer(line))
    ]


def iter_files(vault_path: Path):
    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in files:
            path = Path(root) / name
            if path.relative_to(vault_path).as_posix() not in EXCLUDED_FILES and path.is_file():
                yield path


def read_text(path: Path) -> str | None:
    """Contenu du fichier, ou None s'il est binaire (octet nul)."""
    data = path.read_bytes()
    if b"\0" in data:
        return None
    return data.decode("utf-8", errors="ignore")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Signale les adresses IPv4 publiques du vault.")
    parser.add_argument("vault_path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", dest="emit_json")
    args = parser.parse_args(argv[1:])

    vault_path = Path(args.vault_path).resolve()
    if not vault_path.is_dir():
        print(f"check-public-ip: not a directory: {vault_path}", file=sys.stderr)
        return 2

    findings: list[dict] = []
    scanned = 0
    for path in iter_files(vault_path):
        text = read_text(path)
        if text is None:
            continue
        scanned += 1
        lines = public_ip_lines(text)
        if lines:
            findings.append({
                "severity": "warning",
                "file": path.relative_to(vault_path).as_posix(),
                "message": "public IPv4 address in a public repository: name the host by its role, not by its address",
                "rule": RULE,
                "lines": lines,
            })
    findings.sort(key=lambda f: f["file"])

    summary = {"error": 0, "warning": len(findings), "info": 0}

    if args.emit_json:
        print(json.dumps({"check": CHECK_NAME, "findings": findings, "summary": summary}, indent=2))
    else:
        for f in findings:
            where = ", ".join(str(n) for n in f["lines"])
            print(f"[WARNING] {f['file']} (line {where}): {f['message']}")
        print(f"\nTotal: 0 error(s), {summary['warning']} warning(s)  ({scanned} text file(s) scanned)")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
