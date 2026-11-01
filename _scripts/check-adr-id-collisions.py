#!/usr/bin/env python3
"""check-adr-id-collisions.py — Collisions d'identifiants ADR entre main et
les PR ouvertes du vault.

Classe chaque fichier ADR d'une PR ouverte :
  - modification : le chemin existe sur main (aucun nouvel identifiant) ;
  - collision avec main : nouveau chemin dont l'identifiant existe sur main ;
  - collision entre PR : meme identifiant ajoute par au moins deux PR ;
  - doublon dans une PR : la PR ajoute deux fichiers de meme identifiant.
Signale aussi les doublons de l'arbre de main (garde CI equivalente :
check-adr-supersedes.py, regle adr/unique-id).

La liste des fichiers d'une PR que gh pr list tronque (une page) est relue
par l'API REST paginee. Le controle est INCOMPLET (sortie 2) si main ou la
liste des PR n'est pas lisible, si main ne porte aucun ADR lisible, si la
reponse de GitHub pour main est vide, si la liste atteint la limite demandee, si
les fichiers lus d'une PR sont moins nombreux que son changedFiles, ou si
origin/main local differe de main sur GitHub. Un controle incomplet n'affiche jamais « aucune collision » ni de
prochain identifiant libre.

L'identifiant est lu dans le nom de fichier ; l'accord nom/id est verifie
par check-adr-supersedes.py (regle adr/id-matches-filename).

Lecture seule : ni fetch, ni ecriture. Lancer `git fetch origin` avant ;
le clone runtime, realigne par cron, peut etre lu tel quel.

Usage:
  python3 _scripts/check-adr-id-collisions.py [VAULT_PATH]
      [--repo ak125/governance-vault] [--limit 500] [--json]

Sortie 0 = complet sans collision, 1 = complet avec collision(s),
2 = incomplet ou arguments invalides.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

ADR_PATH = re.compile(r"^ledger/decisions/adr/(ADR-\d{3})[^/]*\.md$")
DEFAULT_REPO = "ak125/governance-vault"
DEFAULT_LIMIT = 500

Runner = Callable[[list[str]], str]


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def adr_id(path: str) -> str | None:
    m = ADR_PATH.match(path)
    return m.group(1) if m else None


def collect(vault: str, repo: str, limit: int, runner: Runner) -> dict:
    """Lit main et les PR ouvertes ; chaque lecture manquee rend incomplet."""
    data: dict = {"main_sha": None, "remote_sha": None, "main_paths": [], "prs": [], "incomplete": []}
    try:
        data["main_sha"] = runner(["git", "-C", vault, "rev-parse", "--verify", "origin/main"]).strip()
        # --full-tree : chemins depuis la racine, meme lance d'un sous-dossier ;
        # -z : chemins non ASCII sans guillemets.
        listing = runner([
            "git", "-C", vault, "ls-tree", "--full-tree", "-z", "--name-only", data["main_sha"], "ledger/decisions/adr/",
        ])
        data["main_paths"] = [path for path in listing.split("\0") if path]
        if not any(adr_id(path) for path in data["main_paths"]):
            data["incomplete"].append("main illisible (aucun ADR dans ledger/decisions/adr/)")
    except (OSError, subprocess.CalledProcessError) as exc:
        data["incomplete"].append(f"main illisible ({exc})")
    try:
        data["remote_sha"] = runner(["gh", "api", f"repos/{repo}/git/ref/heads/main", "--jq", ".object.sha"]).strip()
        if not data["remote_sha"]:
            data["incomplete"].append("main GitHub illisible (reponse vide)")
    except (OSError, subprocess.CalledProcessError) as exc:
        data["incomplete"].append(f"main GitHub illisible ({exc})")
    if data["main_sha"] and data["remote_sha"] and data["main_sha"] != data["remote_sha"]:
        data["incomplete"].append(
            f"origin/main local {data['main_sha'][:12]} != main GitHub {data['remote_sha'][:12]} (git fetch origin)"
        )
    try:
        out = runner([
            "gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", str(limit),
            "--json", "number,title,headRefOid,changedFiles,files",
        ])
        data["prs"] = json.loads(out)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        data["incomplete"].append(f"PR ouvertes illisibles ({exc})")
        return data
    if len(data["prs"]) >= limit:
        data["incomplete"].append(f"{len(data['prs'])} PR lues = limite {limit} (relancer avec --limit plus grand)")
    unread: list[int] = []
    for pr in data["prs"]:
        files, total = pr.get("files"), pr.get("changedFiles")
        if not isinstance(files, list) or not isinstance(total, int):
            unread.append(pr["number"])
            continue
        if len(files) < total:
            try:
                listing = runner([
                    "gh", "api", "--paginate", f"repos/{repo}/pulls/{pr['number']}/files", "--jq", ".[].filename",
                ])
                pr["files"] = [{"path": p} for p in listing.splitlines() if p]
            except (OSError, subprocess.CalledProcessError):
                pass
            if len(pr["files"]) < total:
                unread.append(pr["number"])
    if unread:
        data["incomplete"].append(
            f"fichiers des PR {', '.join(f'#{n}' for n in unread)} lus en partie ou pas du tout"
        )
    return data


def analyse(main_paths: list[str], prs: list[dict]) -> dict:
    main_ids: dict[str, list[str]] = {}
    for path in main_paths:
        i = adr_id(path)
        if i:
            main_ids.setdefault(i, []).append(path)
    main_set = set(main_paths)

    findings: list[dict] = []
    for i, files in sorted(main_ids.items()):
        if len(files) > 1:
            findings.append({"kind": "doublon-main", "id": i, "main": files})

    added: dict[str, list[dict]] = {}
    modified: list[dict] = []
    for pr in sorted(prs, key=lambda p: p["number"]):
        own: dict[str, list[str]] = {}
        for f in pr.get("files") or []:
            i = adr_id(f["path"])
            if not i:
                continue
            if f["path"] in main_set:
                modified.append({"pr": pr["number"], "path": f["path"]})
            else:
                own.setdefault(i, []).append(f["path"])
        for i, paths in sorted(own.items()):
            if len(paths) > 1:
                findings.append({"kind": "doublon-pr", "id": i, "pr": pr["number"], "paths": paths})
            if i in main_ids:
                findings.append({"kind": "collision-main", "id": i, "pr": pr["number"], "paths": paths, "main": main_ids[i]})
            added.setdefault(i, []).append({"pr": pr["number"], "head": pr.get("headRefOid"), "paths": paths})

    for i, entries in sorted(added.items()):
        if len(entries) > 1:
            findings.append({"kind": "collision-pr", "id": i, "prs": entries})

    used = set(main_ids) | set(added)
    next_free = f"ADR-{max(int(i[4:]) for i in used) + 1:03d}" if used else "ADR-001"
    return {"findings": findings, "modified": modified, "next_free": next_free}


def render(data: dict, result: dict) -> str:
    lines = [
        f"Identifiants ADR — origin/main {str(data['main_sha'])[:12]}, main GitHub {str(data['remote_sha'])[:12]}, "
        f"{len(data['prs'])} PR ouverte(s) lue(s), {len(result['modified'])} fichier(s) ADR existant(s) modifie(s)"
    ]
    for f in result["findings"]:
        if f["kind"] == "doublon-main":
            lines.append(f"[DOUBLON main] {f['id']} : {', '.join(f['main'])}")
        elif f["kind"] == "doublon-pr":
            lines.append(f"[DOUBLON PR] {f['id']} : PR #{f['pr']} ajoute {', '.join(f['paths'])}")
        elif f["kind"] == "collision-main":
            lines.append(f"[COLLISION main] {f['id']} : PR #{f['pr']} ajoute {', '.join(f['paths'])} ; main porte {', '.join(f['main'])}")
        else:
            prs = " ; ".join(f"PR #{e['pr']} ajoute {', '.join(e['paths'])}" for e in f["prs"])
            lines.append(f"[COLLISION PR] {f['id']} : {prs}")
    if data["incomplete"]:
        lines.append("Verdict : INCOMPLET — " + " ; ".join(data["incomplete"]))
        lines.append("Les constats ci-dessus sont partiels ; aucune conclusion sur l'absence de collision ni sur le prochain identifiant.")
    elif result["findings"]:
        lines.append(f"Verdict : {len(result['findings'])} constat(s). Prochain identifiant libre : {result['next_free']} (max main ∪ PR ouvertes + 1).")
    else:
        lines.append(f"Verdict : aucune collision. Prochain identifiant libre : {result['next_free']} (max main ∪ PR ouvertes + 1).")
    return "\n".join(lines)


def main(argv: list[str], runner: Runner = run) -> int:
    args = argv[1:]
    vault = str(Path(args[0]).resolve()) if args and not args[0].startswith("--") else str(Path.cwd())
    try:
        repo = args[args.index("--repo") + 1] if "--repo" in args else DEFAULT_REPO
        limit = int(args[args.index("--limit") + 1]) if "--limit" in args else DEFAULT_LIMIT
    except (IndexError, ValueError):
        print("Usage: check-adr-id-collisions.py [VAULT_PATH] [--repo OWNER/NAME] [--limit N] [--json]", file=sys.stderr)
        return 2

    data = collect(vault, repo, limit, runner)
    result = analyse(data["main_paths"], data["prs"])
    complete = not data["incomplete"]
    if "--json" in args:
        print(json.dumps({
            "check": "adr-id-collisions",
            "complete": complete,
            "incomplete": data["incomplete"],
            "main_sha": data["main_sha"],
            "remote_sha": data["remote_sha"],
            "open_prs": len(data["prs"]),
            "findings": result["findings"],
            "next_free": result["next_free"] if complete else None,
        }, indent=2, ensure_ascii=False))
    else:
        print(render(data, result))
    if not complete:
        return 2
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
