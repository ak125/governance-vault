---
type: invariants
---

# Invariants (Vault G1-G4)

## G1: Canon Fait Foi

- [x] Aucun document `status: canon` modifie sans ADR associee
- [x] Les regles T1-T7 restent des miroirs du monorepo `.spec/00-canon/`
- [x] Le README declare explicitement G1 et pointe vers le canon
- [x] CLAUDE.md pour agents IA reaffirme la regle maitresse

## G2: Zero Orphelin

- [x] `_scripts/check-orphans.sh` passe sans erreur (0 orphelin detecte)
- [x] Tous les nouveaux documents (airlock-decisions-reference, branch-protection, EP-20260418-*) sont lies depuis un MOC/INDEX
- [x] Pre-commit hook local installe pour enforcement avant push
- [x] CI job `g2-orphans` execute a chaque PR/push
- [x] Stats README: `Orphelins (G2) | 0`

## G3: Commits Signes

- [x] `~/.ssh/allowed_signers` configure localement et cote CI runner
- [x] Cle K002 (Fafa Windows) ajoutee au `key-registry.md`
- [x] Cle K001 (deploy VPS) deja presente
- [x] CI job `g3-signed-commits` verifie `%G?` sur chaque commit du push/PR
- [x] `required_signatures` cote GitHub non necessaire (plan Free) — le job CI fait le meme travail
- [x] Branch protection interdit le merge si G3 echoue

## G4: CI Read-Only

- [x] Workflows GitHub Actions n'ecrivent jamais le canon
- [x] Kill-switch `AI_VAULT_WRITE=false` respecte
- [x] CI job `g4-canon-write-block` verifie l'invariant a chaque run
- [x] Tokens Actions minimum viable (pas de write sur `.spec/00-canon/`)

## Invariants de nommage

- [x] INDEX-* avec stem unique (pas de collision `INDEX.md`)
- [x] Wikilinks courts prefera (`[[ADR-001-environment-separation]]`) sauf collision
- [x] Pas de `[[path|alias]]` dans tableaux markdown (|-escape casse Obsidian)
- [x] Frontmatter YAML present sur tout document canonique

## Invariants de gouvernance serveur

- [x] Branch protection `main` active (`enforce_admins: true`)
- [x] 4 required status checks verifies (G2 orphans, broken links, G3 signed, G4 canon)
- [x] `required_linear_history: true` — pas de merge commits
- [x] `allow_force_pushes: false`, `allow_deletions: false`
- [x] `required_conversation_resolution: true`
