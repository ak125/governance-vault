---
type: ci-proof
---

# CI Proof

## Workflow

**Fichier**: `.github/workflows/vault-governance.yml`
**Trigger**: push, pull_request sur `main`
**Jobs** (4):

| Job key | Display name (context) | Script | Exit criterion |
|---------|------------------------|--------|-----------------|
| `g2-orphans` | `G2: Zero Orphelin` | `_scripts/check-orphans.sh` | 0 orphelin |
| `broken-links` | `Broken Wikilinks` | `_scripts/check-broken-links.sh` | 0 lien casse |
| `g3-signed-commits` | `G3: Commits signes` | Verification `%G?` via git log | Tous commits signes ET verifies |
| `g4-canon-write-block` | `G4: CI read-only sur canon` | Verification structurelle du workflow | Pas d'ecriture canon |

## Preuves par PR

### PR #3 — refactor/governance-v2 (Phase 5 + 6)

- Status: merged, fast-forward via rebase
- 4 checks: SUCCESS
- Commits: tous signes K002
- Lien: https://github.com/ak125/governance-vault/pull/3

### PR #4 — allowed_signers fix

- Status: merged, fast-forward via rebase
- Contexte: correction de l'echec G3 sur PR #3 (CI runner sans allowed_signers)
- 4 checks: SUCCESS apres fix
- Lien: https://github.com/ak125/governance-vault/pull/4

### PR #5 — cleanup/residuels-v2

- Status: merged, fast-forward via rebase
- Scope: Task #12 (airlock-decisions-reference), #13 (MOC-Incidents enrichi), #14 (branch-protection)
- 4 checks: SUCCESS
- Lien: https://github.com/ak125/governance-vault/pull/5

## Branch protection (cote serveur)

**Verification**:

```bash
gh api repos/ak125/governance-vault/branches/main/protection \
  | jq '{
      enforce_admins: .enforce_admins.enabled,
      linear_history: .required_linear_history.enabled,
      checks: [.required_status_checks.contexts[]],
      force_push: .allow_force_pushes.enabled,
      deletions: .allow_deletions.enabled
    }'
```

**Resultat attendu**:

```json
{
  "enforce_admins": true,
  "linear_history": true,
  "checks": [
    "G2: Zero Orphelin",
    "Broken Wikilinks",
    "G3: Commits signes",
    "G4: CI read-only sur canon"
  ],
  "force_push": false,
  "deletions": false
}
```

## Notes

- Aucun secret Actions utilise pour le job G3: la cle publique est hardcodee dans le workflow (cle **publique**, non-sensible)
- Le job `g4-canon-write-block` est une verification structurelle: il inspecte le workflow lui-meme pour detecter toute tentative de write canon
- `required_signatures` cote GitHub est **non** active (plan Free); le job CI remplit la fonction equivalente **au niveau PR**

## Artefact Connu — G3 enforced au PR level

L'audit retroactif `audit-signatures.sh` execute le 2026-04-18 a trouve **20 commits non signes sur 70** sur `main`. Ce n'est pas une violation mais un **artefact structurel** :

- Plan GitHub Free → `required_signatures: false`
- `required_linear_history: true` → merges en rebase obligatoires
- `gh pr merge --rebase` reecrit les commits sans re-signer → signatures perdues sur main

La chaine de custody reste **distribuee** :

| Couche | Artefact | Ou verifier |
|--------|----------|-------------|
| Local pre-push | Commit signe K002 | `git log --show-signature` sur branche de travail |
| PR CI | `%G?` = G valide | GitHub Actions logs, job `g3-signed-commits` |
| GitHub merge | Strategy + merger identity | `gh api /repos/ak125/governance-vault/pulls/N` |
| Main historique | SHA + committer (sans gpgsig) | `git log` (attendu sans signature) |

Compensating control : les PRs #3, #4, #5 ont toutes passe CI G3 avec 4 checks verts avant merge. Aucun commit non signe n'a pu atteindre main sans passage par le filtre CI.

Documentation complete : voir [[branch-protection]] section "Artefact Connu : Signature Chain au Merge Rebase".

## Voir aussi

- [[branch-protection]] — Policy serveur complete
- [[signing-policy]] — G3 et allowed_signers
- [[ci-policy]] — G4 et kill-switch
