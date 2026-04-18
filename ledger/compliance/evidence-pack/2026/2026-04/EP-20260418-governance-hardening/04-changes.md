---
type: changes
---

# Changes

## Phase 5 — Orphelins R-Vault-02 + Refs cassees evidence-pack

**Objectif**: ramener le compteur d'orphelins G2 a zero et reparer les wikilinks casses vers les EP 2026-02.

- Creation des INDEX-EP-20260205-* (4 fichiers) pour chaque evidence-pack 2026-02
- Ajout liens depuis MOC-Compliance vers les 4 INDEX
- Resolution de 100% des orphelins R-Vault-02 identifies (compteur: 14 → 0)

## Phase 6 — Enforcement (pre-commit + CI + README + CLAUDE.md)

**Objectif**: rendre les regles G1-G4 automatiquement verifiables avant push et a chaque PR.

- `.githooks/pre-commit` cree — execute check-orphans + check-broken-links
- `.github/workflows/vault-governance.yml` cree — 4 jobs CI (g2, broken-links, g3, g4)
- README.md etoffe avec commandes utiles et structure v2
- CLAUDE.md ajoute pour briefer les agents IA (G1-G4 + conventions)
- Documentation `git config core.hooksPath .githooks` pour bootstrap nouvelle machine

## Residuels v2 (task #12, #13, #14)

**Objectif**: completer les 3 items flagges comme "non-bloquants mais a finir" dans le rapport de gouvernance final.

### Task #12 — airlock-decisions-reference

- Creation de `ledger/knowledge/airlock-decisions-reference.md`
- Documente le mapping complet DEC-002..013 (Airlock) ↔ ADR-001..014 (monorepo)
- Explique pourquoi deux systemes DEC coexistent (vault legacy reclasse en Phase 4 vs Airlock canonique)
- Link ajoute depuis MOC-Knowledge et MOC-Compliance

### Task #13 — MOC-Incidents enrichi

- Taxonomie de severite (Critical/High/Medium/Low) avec criteres + SLA detection + SLA post-mortem
- Lifecycle en 8 etapes avec responsables et artefacts
- Matrice RACI pour chaque activite
- Workflow detaille pour declarer un nouvel incident
- Link vers airlock-decisions-reference (DEC-004 kill-switch + DEC-007 incident response)
- Stats enrichies

### Task #14 — branch-protection policy

- Creation de `99-meta/branch-protection.md`
- Table complete des parametres applicables (enforce_admins, linear_history, etc.)
- Mapping display name ↔ job key pour `required_status_checks.contexts`
- Procedure de desactivation d'urgence (5 etapes)
- Verification d'integrite via `gh api | jq`
- Links depuis signing-policy.md et README.md

## Fix CI G3 (allowed_signers)

**Objectif**: le CI runner ne voyait pas les signatures (`%G? = N`) car il n'avait pas de fichier `allowed_signers`.

- Etape "Configure SSH signature verification" ajoutee au job `g3-signed-commits` dans le workflow
- Cle K002 (Fafa-Windows) ajoutee au `key-registry.md` (elle manquait de la base)
- Format `allowed_signers` mis a jour dans `signing-policy.md`

## Setup branch protection (serveur)

**Objectif**: bloquer cote GitHub tout merge sur `main` qui ne satisferait pas G1-G4.

- Creation de `_scripts/setup-branch-protection.sh` (idempotent)
- Utilise `gh api --input -` avec JSON body (evite le piege `-F restrictions=` qui cause 422)
- Re-execute une fois apres decouverte que `contexts` matche par display name, pas job key
- 4 contexts corrects: "G2: Zero Orphelin", "Broken Wikilinks", "G3: Commits signes", "G4: CI read-only sur canon"
- `enforce_admins: true`, `required_linear_history: true`, `allow_force_pushes: false`

## Fix scripts pour Windows

**Objectif**: les scripts .sh doivent marcher sur Windows via Git Bash sans shimming Microsoft Store.

- `find_python()` ajoute dans `check-orphans.sh` et `check-broken-links.sh`
- Sonde `sys.version_info` pour rejeter l'alias Store qui exit 9009
- Pre-commit hook gere distinctement exit 2 (Python manquant) vs exit 1 (violations)

## PRs mergees durant cette periode

- PR #3 (refactor/governance-v2) — Phase 5 + Phase 6 → main (fast-forward via rebase)
- PR #4 (cleanup follow-up) — allowed_signers fix + fixes CI → main
- PR #5 (cleanup/residuals-v2) — Task #12, #13, #14 → main

Toutes signees K002, toutes avec 4 checks verts, historique lineaire preserve.

## Commits signes durant la periode

Verifiable via `_scripts/audit-signatures.sh --report` (genere `99-meta/reports/2026-04-signature-audit.md`).
