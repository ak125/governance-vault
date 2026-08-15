#!/usr/bin/env python3
"""
compute-canon-hashes.py — Generate or verify 99-meta/canon-hashes.json.

Source of truth: AEC §"Distribution canonique" (rules-agent-exit-contract.md).

For each canon entry:
  canon_sha256        — SHA-256 of full canon file (frontmatter included)
  distribution_sha256 — selon hash_mode (voir ci-dessous)

Modes:
  --check   read 99-meta/canon-hashes.json, recompute, fail on drift (CI gate)
  --write   recompute and overwrite 99-meta/canon-hashes.json (signed commit)
  --print   print computed hashes to stdout (no file IO)

=== hash_mode, DECLARE PAR ENTREE (F2c, ADR-096 §D3) ===

  text_sha256  (defaut, comportement historique inchange)
      distribution_sha256 = sha256(texte UTF-8 prive de son frontmatter YAML).

  json_jcs
      distribution_sha256 = sha256(document JSON canonicalise, prive des chemins
      declares dans excluded_paths).

Pourquoi ce mode existe : un contrat JSON n'a pas de frontmatter YAML. Lui appliquer
strip_frontmatter ne retire RIEN, donc distribution_sha256 vaudrait le hash des octets
bruts — pas la forme canonique que le contrat declare. Publier et verifier auraient alors
calcule deux empreintes differentes sous un seul nom, et l'ecart ne se serait vu qu'au
moment de la comparaison cote consommateur.

SOUS-ENSEMBLE JCS SUPPORTE, ET SA GARDE. On implemente le sous-ensemble de RFC 8785
sur lequel Python et ECMAScript coincident exactement, et on REFUSE le reste plutot que
de produire une empreinte plausible mais divergente :
  - cles d'objet ASCII uniquement — RFC 8785 trie par unites de code UTF-16, Python par
    point de code ; les deux ordres ne divergent que hors BMP ;
  - AUCUNE propriete dupliquee — RFC 8785 l'interdit, mais json.loads accepte
    {"a":1,"a":2} et ne garde que la derniere valeur : la duplication devient invisible
    APRES parsing. Le refus doit donc avoir lieu AU PARSING (strict_json_loads), pas
    dans le guard ;
  - nombres ENTIERS uniquement, et dans la plage SUREMENT representable en IEEE-754
    double : |n| <= 2^53 - 1. Un int Python est de precision arbitraire ; un Number
    ECMAScript ne l'est pas. 9007199254740993 est exact en Python et ne l'est pas en JS.
    La borne retenue est plus restrictive que le maximum theorique IEEE-754, mais elle
    est garantie et simple ;
  - flottants REFUSES — le formatage ECMAScript differe de repr() Python sur certains cas ;
  - booleens, null, chaines et tableaux : serialisation identique.
Tout document hors de ce sous-ensemble est REFUSE (exit non-zero), jamais serialise au
mieux. La limite est mecanique, pas documentaire.

Limite connue et assumee : les chaines contenant des surrogates isoles ne sont pas
rejetees explicitement — l'encodage UTF-8 echoue deja dans la plupart de ces cas.
Durcissement secondaire, non livre ici.

=== GATE DE STATUT, FAIL-CLOSED (F2c) ===

Un canon n'est publie que si le statut qu'il DECLARE figure dans `publishable_when` de
son entree. Le vocabulaire differe par classe de document — les rules du vault declarent
`status: canon`, les ADR et contrats `proposed|accepted|...` — donc la liste admissible
est declaree PAR ENTREE, jamais codee en dur.

Refus (exit non-zero) si : `publishable_when` absent de l'entree · statut absent du
document · statut hors de la liste. Aucun de ces cas ne doit pouvoir passer en silence :
livrer la CAPACITE de projeter ne vaut pas AUTORISATION de projeter ce contrat-ci.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HASHES_PATH = REPO_ROOT / "99-meta" / "canon-hashes.json"

# Canon registry — extend here when a new canon distribution is added.
#
# hash_mode        : "text_sha256" (defaut) | "json_jcs"
# publishable_when : liste FERMEE des statuts declares qui autorisent la publication.
#                    OBLIGATOIRE — son absence est un refus (fail-closed).
# excluded_paths   : json_jcs uniquement — chemins pointes retires avant canonicalisation.
CANONS: dict[str, dict] = {
    "aec": {
        "name": "Agent Exit Contract",
        "canon_path": "ledger/rules/rules-agent-exit-contract.md",
        "version": "1.0.1",
        "hash_mode": "text_sha256",
        "publishable_when": ["canon"],
        "consumers": [
            {"repo": "ak125/automecanik-wiki", "path": "_meta/agent-exit-contract.md"},
            {"repo": "ak125/automecanik-raw", "path": "agent-exit-contract.md"},
            {"repo": "ak125/nestjs-remix-monorepo", "path": ".claude/canon-mirrors/agent-exit-contract.md"},
            {"repo": "ak125/nestjs-remix-monorepo", "path": "workspaces/seo-batch/.claude/canon-mirrors/agent-exit-contract.md"},
            {"repo": "ak125/nestjs-remix-monorepo", "path": "workspaces/marketing/.claude/canon-mirrors/agent-exit-contract.md"},
        ],
    },
    "marketing_voice": {
        "name": "Marketing Brand Voice",
        "canon_path": "ledger/rules/rules-marketing-voice.md",
        "version": "1.0.1",
        "hash_mode": "text_sha256",
        "publishable_when": ["canon"],
        "consumers": [
            {"repo": "ak125/nestjs-remix-monorepo", "path": ".claude/canon-mirrors/marketing-voice.md"},
            {"repo": "ak125/nestjs-remix-monorepo", "path": "workspaces/marketing/.claude/canon-mirrors/marketing-voice.md"},
        ],
    },
    # source-score-weights@v1 (ADR-096 §D3) : PAS ENCORE ENREGISTRE.
    # La capacite technique existe depuis cette PR, mais le contrat est `proposed`.
    # Son enregistrement est un acte owner distinct, apres passage a `accepted`.
    # L'entree serait :
    #   "source-score-weights": {
    #       "name": "Source Score Weights",
    #       "canon_path": "ledger/policies/source-score-weights.v1.json",
    #       "version": "1.0.0",
    #       "hash_mode": "json_jcs",
    #       "publishable_when": ["accepted"],
    #       "excluded_paths": ["metadata.distribution_sha256"],
    #       "consumers": [{"repo": "ak125/automecanik-raw", "path": "_schemas/source-score-weights.v1.json"}],
    #   }
}

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n*", re.DOTALL)
STATUS_RE = re.compile(r"^status:\s*(\S+)\s*$", re.M)


# --------------------------------------------------------------------------- #
# Hachage
# --------------------------------------------------------------------------- #
def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class JcsUnsupported(Exception):
    """Document hors du sous-ensemble JCS supporte — refuse, jamais approxime."""


# Plage d'entiers SUREMENT exacte en IEEE-754 double, donc en Number ECMAScript.
SAFE_INT_MAX = 2**53 - 1


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    """object_pairs_hook : RFC 8785 interdit les proprietes dupliquees. json.loads les
    accepte et ne garde que la derniere — la duplication devient invisible apres
    parsing, donc le refus doit avoir lieu ICI."""
    seen: set[str] = set()
    for key, _ in pairs:
        if key in seen:
            raise JcsUnsupported(
                f"propriete dupliquee '{key}' — RFC 8785 l'interdit, et json.loads "
                f"n'en garderait silencieusement que la derniere valeur"
            )
        seen.add(key)
    return dict(pairs)


def strict_json_loads(text: str):
    """Parse JSON en refusant les proprietes dupliquees. Utilise partout ou un document
    JSON est lu pour etre hache ou pour declarer un statut."""
    return json.loads(text, object_pairs_hook=_reject_duplicate_keys)


def _jcs_guard(node, path: str = "$") -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if not isinstance(key, str):
                raise JcsUnsupported(f"{path}: cle non-chaine")
            if not key.isascii():
                raise JcsUnsupported(
                    f"{path}.{key}: cle non-ASCII — RFC 8785 trie par unites UTF-16, "
                    f"Python par point de code ; l'ordre peut diverger"
                )
            _jcs_guard(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            _jcs_guard(value, f"{path}[{i}]")
    elif isinstance(node, bool) or node is None or isinstance(node, str):
        return
    elif isinstance(node, int):
        if not -SAFE_INT_MAX <= node <= SAFE_INT_MAX:
            raise JcsUnsupported(
                f"{path}: entier hors de la plage suremement exacte en IEEE-754 double "
                f"(|n| <= 2^53-1). Un int Python est de precision arbitraire, un Number "
                f"ECMAScript non : les deux serialisations divergeraient"
            )
        return
    elif isinstance(node, float):
        raise JcsUnsupported(
            f"{path}: nombre flottant — le formatage ECMAScript differe de repr() Python"
        )
    else:
        raise JcsUnsupported(f"{path}: type non serialisable ({type(node).__name__})")


def _delete_path(obj: dict, dotted: str) -> None:
    """Retire un chemin pointe s'il existe. Absent = no-op (le champ est optionnel)."""
    parts = dotted.split(".")
    node = obj
    for part in parts[:-1]:
        node = node.get(part) if isinstance(node, dict) else None
        if node is None:
            return
    if isinstance(node, dict):
        node.pop(parts[-1], None)


def canonical_json(doc: dict, excluded_paths: list[str]) -> str:
    """Sous-ensemble RFC 8785 : cles triees, separateurs compacts, UTF-8 non echappe."""
    pruned = copy.deepcopy(doc)
    for dotted in excluded_paths:
        _delete_path(pruned, dotted)
    _jcs_guard(pruned)
    return json.dumps(pruned, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


# --------------------------------------------------------------------------- #
# Gate de statut
# --------------------------------------------------------------------------- #
def declared_status(path: Path, text: str) -> str | None:
    """Statut declare par le document lui-meme. None si absent."""
    if path.suffix == ".json":
        try:
            return (strict_json_loads(text).get("metadata") or {}).get("status")
        except json.JSONDecodeError:
            return None
    if text.startswith("---"):
        head = text.split("---", 2)
        if len(head) >= 2:
            found = STATUS_RE.search(head[1])
            return found.group(1) if found else None
    return None


def enforce_publishable(key: str, meta: dict, path: Path, text: str) -> None:
    allowed = meta.get("publishable_when")
    if not allowed:
        sys.exit(
            f"ERROR: canon '{key}' n'a pas de `publishable_when`. Toute entree doit "
            f"declarer les statuts qui autorisent sa publication (fail-closed) — voir "
            f"_scripts/compute-canon-hashes.py §GATE DE STATUT."
        )
    status = declared_status(path, text)
    if status is None:
        sys.exit(
            f"ERROR: canon '{key}' ne declare aucun statut ({meta['canon_path']}). "
            f"Un canon sans statut n'est pas publiable."
        )
    if status not in allowed:
        sys.exit(
            f"ERROR: canon '{key}' a status='{status}', hors de publishable_when="
            f"{allowed}. Livrer la CAPACITE de projeter ne vaut pas AUTORISATION de "
            f"projeter ce contrat : le passage de statut est un acte owner distinct."
        )


# --------------------------------------------------------------------------- #
def compute() -> dict:
    canons_out: dict[str, dict] = {}
    for key, meta in CANONS.items():
        canon_file = REPO_ROOT / meta["canon_path"]
        if not canon_file.exists():
            sys.exit(f"ERROR: canon file missing: {meta['canon_path']}")
        consumers = meta.get("consumers") or []
        if not consumers:
            sys.exit(
                f"ERROR: canon '{key}' has no consumers declared. "
                f"Every distributed canon MUST list at least one consumer "
                f"(repo+path) in CANONS — see _scripts/compute-canon-hashes.py."
            )
        text = canon_file.read_text(encoding="utf-8")

        try:
            enforce_publishable(key, meta, canon_file, text)
        except JcsUnsupported as exc:
            sys.exit(f"ERROR: canon '{key}' illisible strictement — {exc}")

        mode = meta.get("hash_mode", "text_sha256")
        if mode == "text_sha256":
            distribution = sha256_text(strip_frontmatter(text))
        elif mode == "json_jcs":
            try:
                doc = strict_json_loads(text)
            except json.JSONDecodeError as exc:
                sys.exit(f"ERROR: canon '{key}' hash_mode=json_jcs mais JSON invalide: {exc}")
            except JcsUnsupported as exc:
                sys.exit(f"ERROR: canon '{key}' refuse au parsing — {exc}")
            try:
                distribution = sha256_text(
                    canonical_json(doc, meta.get("excluded_paths") or [])
                )
            except JcsUnsupported as exc:
                sys.exit(
                    f"ERROR: canon '{key}' hors du sous-ensemble JCS supporte — {exc}. "
                    f"Refuse plutot que hache de facon potentiellement divergente."
                )
        else:
            sys.exit(f"ERROR: canon '{key}' hash_mode inconnu: {mode!r}")

        canons_out[key] = {
            "name": meta["name"],
            "canon_path": meta["canon_path"],
            "canon_sha256": sha256_text(text),
            "distribution_sha256": distribution,
            "hash_mode": mode,
            "version": meta["version"],
            "consumers": meta["consumers"],
        }
    return {
        "$comment": "Generated by _scripts/compute-canon-hashes.py — do not edit by hand.",
        "version": "1.0.0",
        "updated": date.today().isoformat(),
        "canons": canons_out,
    }


def write_json(data: dict) -> None:
    HASHES_PATH.parent.mkdir(parents=True, exist_ok=True)
    HASHES_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--print", action="store_true")
    args = ap.parse_args()

    computed = compute()

    if args.print:
        print(json.dumps(computed, indent=2, ensure_ascii=False))
        return 0

    if args.write:
        write_json(computed)
        print(f"WROTE {HASHES_PATH.relative_to(REPO_ROOT)}")
        return 0

    # --check
    if not HASHES_PATH.exists():
        sys.exit(f"ERROR: {HASHES_PATH.relative_to(REPO_ROOT)} missing — run with --write")
    on_disk = json.loads(HASHES_PATH.read_text(encoding="utf-8"))
    # Ignore `updated` field for drift detection — only hashes matter.
    drift = []
    for key, meta in computed["canons"].items():
        disk = on_disk.get("canons", {}).get(key)
        if not disk:
            drift.append(f"  + {key}: missing in canon-hashes.json")
            continue
        if disk["canon_sha256"] != meta["canon_sha256"]:
            drift.append(
                f"  ! {key}.canon_sha256 drift: disk={disk['canon_sha256'][:12]}… "
                f"computed={meta['canon_sha256'][:12]}…"
            )
        if disk["distribution_sha256"] != meta["distribution_sha256"]:
            drift.append(
                f"  ! {key}.distribution_sha256 drift: disk={disk['distribution_sha256'][:12]}… "
                f"computed={meta['distribution_sha256'][:12]}…"
            )
    if drift:
        print("DRIFT detected — re-run `_scripts/compute-canon-hashes.py --write`:")
        print("\n".join(drift))
        return 1
    print("OK — canon-hashes.json in sync with canon files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
