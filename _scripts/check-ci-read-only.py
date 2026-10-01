#!/usr/bin/env python3
"""check-ci-read-only.py — G4 : la CI du vault n'ecrit aucun contenu (ADR-102 D3).

Verifie chaque workflow `.github/workflows/*.yml` / `*.yaml` :
  1. un bloc `permissions:` au niveau racine. Sans lui, le jeton du workflow prend
     la permission par defaut du depot, un reglage qui vit hors du depot ;
  2. aucun scope en `write`, a la racine ou dans un job, sauf ceux de
     ALLOWED_WRITE_SCOPES ; `write-all` est interdit ;
  3. aucune etape `run:` ne lance `git commit` ni `git push` ;
  4. aucun jeton autre que le GITHUB_TOKEN du workflow : un jeton d'App GitHub
     (`actions/create-github-app-token`) ou un secret passe en `token:`,
     `github-token:`, `GH_TOKEN` ou `GITHUB_TOKEN` echappe au bloc `permissions:`.
     Seuls les jobs de TOKEN_EXCEPTIONS en ont un, et un jeton d'App doit y etre
     limite a des depots nommes (`repositories:`).

Usage :
  python3 _scripts/check-ci-read-only.py [VAULT_PATH] [--json]

Exit 0 si conforme, 1 sinon, 2 si le dossier des workflows est introuvable.
Ne modifie aucun fichier.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

# Scope -> raison. Un scope ajoute ici passe en revue comme toute modification de _scripts/.
ALLOWED_WRITE_SCOPES = {
    "issues": "ouverture d'issues de suivi (weekly-lint, cout Supabase) : aucun contenu du depot",
}

# (workflow, job) -> raison.
TOKEN_EXCEPTIONS = {
    ("canon-publish.yml", "dispatch"): (
        "repository_dispatch `canon-updated` vers les depots consommateurs (ADR-061 §3) ; "
        "jeton d'App limite au depot cible de chaque iteration, jamais au vault"
    ),
}

READ_VALUES = {"read", "none"}
TOKEN_KEYS = {"token", "github-token", "GH_TOKEN", "GITHUB_TOKEN"}
SECRET_REF = re.compile(r"secrets\.([A-Za-z_][A-Za-z0-9_]*)")
GIT_WRITE = re.compile(r"\bgit\b(?:\s+-[Cc]\s+\S+)*\s+(commit|push)\b")
APP_TOKEN_ACTION = "actions/create-github-app-token"


def _permission_findings(perms, where: str) -> list[str]:
    if isinstance(perms, str):
        return [f"{where} : `permissions: write-all` interdit"] if perms == "write-all" else []
    if not isinstance(perms, dict):
        return []
    out = []
    for scope, value in perms.items():
        if value in READ_VALUES:
            continue
        if value == "write" and scope in ALLOWED_WRITE_SCOPES:
            continue
        out.append(f"{where} : `{scope}: {value}` interdit (seuls read/none, ou write sur {sorted(ALLOWED_WRITE_SCOPES)})")
    return out


def _secret_tokens(mapping) -> list[str]:
    """Noms des secrets (hors GITHUB_TOKEN) passes sous une cle de jeton."""
    if not isinstance(mapping, dict):
        return []
    names = []
    for key, value in mapping.items():
        if key in TOKEN_KEYS and isinstance(value, str):
            names += [n for n in SECRET_REF.findall(value) if n != "GITHUB_TOKEN"]
    return names


def check_workflow(path: Path) -> list[str]:
    name = path.name
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{name} : YAML invalide ({exc.__class__.__name__})"]
    if not isinstance(doc, dict):
        return [f"{name} : workflow vide ou invalide"]

    findings = []
    if "permissions" not in doc:
        findings.append(f"{name} : pas de `permissions:` au niveau racine")
    else:
        findings += _permission_findings(doc["permissions"], f"{name} (racine)")

    top_secrets = _secret_tokens(doc.get("env"))
    if top_secrets:
        findings.append(f"{name} (racine) : jeton tire du secret {top_secrets} hors GITHUB_TOKEN")

    for job_id, job in (doc.get("jobs") or {}).items():
        if not isinstance(job, dict):
            continue
        where = f"{name} job `{job_id}`"
        if "permissions" in job:
            findings += _permission_findings(job["permissions"], where)

        excepted = (name, job_id) in TOKEN_EXCEPTIONS
        secrets = _secret_tokens(job.get("env"))
        for i, step in enumerate(job.get("steps") or []):
            if not isinstance(step, dict):
                continue
            label = f"{where} etape {i + 1}"
            run = step.get("run")
            if isinstance(run, str):
                for verb in GIT_WRITE.findall(run):
                    findings.append(f"{label} : `git {verb}` interdit, la CI n'ecrit pas dans le depot")
            uses = step.get("uses")
            if isinstance(uses, str) and uses.split("@")[0] == APP_TOKEN_ACTION:
                if not excepted:
                    findings.append(f"{label} : jeton d'App GitHub hors TOKEN_EXCEPTIONS")
                elif not (step.get("with") or {}).get("repositories"):
                    findings.append(f"{label} : jeton d'App sans `repositories:` (non limite a des depots nommes)")
            secrets += _secret_tokens(step.get("with")) + _secret_tokens(step.get("env"))
        if secrets and not excepted:
            findings.append(f"{where} : jeton tire du secret {sorted(set(secrets))} hors GITHUB_TOKEN et hors TOKEN_EXCEPTIONS")
    return findings


def check_repo(vault: Path) -> list[str]:
    wf_dir = vault / ".github" / "workflows"
    files = sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")))
    findings = []
    for wf in files:
        findings += check_workflow(wf)
    return findings


def main(argv: list[str]) -> int:
    vault = Path(argv[1]).resolve() if len(argv) > 1 and not argv[1].startswith("--") else Path.cwd()
    emit_json = "--json" in argv
    wf_dir = vault / ".github" / "workflows"
    if not wf_dir.is_dir():
        print(f"Error: workflows dir not found: {wf_dir}", file=sys.stderr)
        return 2
    findings = check_repo(vault)
    if emit_json:
        print(json.dumps({"check": "ci-read-only", "findings": findings}, indent=2, ensure_ascii=False))
    else:
        for f in findings:
            print(f"[ERROR] {f}")
        count = len(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")))
        print(f"\nG4 CI read-only : {len(findings)} violation(s) ({count} workflow(s) verifie(s))")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
