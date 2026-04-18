---
type: policy
status: canon
rule: G1,G2,G3,G4
updated: 2026-04-18
---

# Politique de Protection de Branche (main)

**Statut** : Actif depuis 2026-04-18
**Enforcement** : Cote serveur via GitHub Branch Protection Rules
**Regles canoniques** : [[rules-vault]] G1, G2, G3, G4

---

## Regle

> **La branche `main` est verrouillee cote serveur**. Aucun push direct n'est possible, meme pour les admins. Toute modification passe par une PR qui doit satisfaire les 4 required status checks.

Cette protection est la **troisieme ligne de defense** apres :

1. **Pre-commit hook local** (`.githooks/pre-commit`) — attrape les erreurs avant commit
2. **CI workflow** (`.github/workflows/vault-governance.yml`) — verifie chaque push/PR
3. **Branch protection** (cette doc) — bloque le merge cote GitHub si un check manque

---

## Configuration Appliquee

| Parametre | Valeur | Justification |
|-----------|--------|---------------|
| `required_status_checks.contexts` | 4 jobs CI (voir ci-dessous) | Les 4 regles G1-G4 doivent passer |
| `required_status_checks.strict` | `true` | La branche PR doit etre a jour avec `main` |
| `enforce_admins` | `true` | Personne ne contourne, y compris l'owner |
| `required_linear_history` | `true` | Pas de merge commits (rebase obligatoire) |
| `required_pull_request_reviews` | `count: 0`, `dismiss_stale: true` | Solo repo : reviews non requises, mais les reviews obsoletes sont auto-dismissed |
| `restrictions` | `null` | Personne n'est explicitement autorise a bypasser |
| `allow_force_pushes` | `false` | Pas de reecriture d'historique sur main |
| `allow_deletions` | `false` | Impossible de supprimer main |
| `required_conversation_resolution` | `true` | Les threads PR doivent etre resolus avant merge |

---

## Required Status Checks (4 jobs)

Le merge est bloque tant que l'un de ces 4 checks n'a pas le status **SUCCESS** :

| Check name (cote GitHub) | Job key (cote workflow) | Role |
|--------------------------|--------------------------|------|
| `G2: Zero Orphelin` | `g2-orphans` | Execute `check-orphans.sh`, exit 1 si orphelins |
| `Broken Wikilinks` | `broken-links` | Execute `check-broken-links.sh`, exit 1 si liens casses |
| `G3: Commits signes` | `g3-signed-commits` | Verifie `%G?` sur chaque commit de la PR/push |
| `G4: CI read-only sur canon` | `g4-canon-write-block` | Verifie que le workflow ne peut pas ecrire le canon |

> **Important** : les `contexts` de la protection matchent le **display name** du job (`name:` field dans le YAML), pas le job key. Si tu renommes un job dans le workflow, il faut mettre a jour la protection en consequence.

---

## Setup / Re-application

La configuration est versionnee dans `_scripts/setup-branch-protection.sh`. En cas de perte ou de recreation du repo :

```bash
_scripts/setup-branch-protection.sh
```

Le script utilise `gh api` avec un JSON body complet (via `--input -`) pour eviter le piege `-F restrictions=` qui passe une chaine vide au lieu de `null` (bug 422 historique).

Verifier la configuration en vigueur :

```bash
gh api repos/ak125/governance-vault/branches/main/protection | jq .
```

---

## Procedure de Desactivation d'Urgence

Si un incident critique necessite un push direct sur `main` (dernier recours), le protocole est :

1. **Documenter** la raison dans un ticket / incident (severite Critical)
2. **Desactiver** la protection :
   ```bash
   gh api -X DELETE repos/ak125/governance-vault/branches/main/protection
   ```
3. **Faire** le push d'urgence en commit **signe** (G3 reste imperatif meme en urgence)
4. **Re-activer** la protection IMMEDIATEMENT :
   ```bash
   _scripts/setup-branch-protection.sh
   ```
5. **Post-mortem** dans [[MOC-Incidents]] expliquant pourquoi la protection a ete levee et quelle correction systemique empechera la recurrence

Chaque desactivation laisse une trace dans les **audit logs GitHub** (irreversible). Ce n'est pas un geste banal.

---

## Signatures Requises

`required_signatures` (cote GitHub) n'est **pas** inclus dans notre config actuelle — ce parametre necessite un plan **GitHub Pro/Team** pour les repos prives. Le job `g3-signed-commits` fait le meme travail en verifiant `%G?` sur chaque commit du push/PR. Resultat equivalent pour bloquer le merge, **mais avec un artefact a connaitre** (voir section suivante).

Si le plan evolue un jour, il suffit d'ajouter `"required_signatures": true` au JSON du script et de le relancer. Idempotent.

---

## Artefact Connu : Signature Chain au Merge Rebase

### Observation

Sur plan GitHub Free, quand une PR est mergee via `gh pr merge --rebase` (strategie imposee par `required_linear_history: true`), **GitHub reecrit chaque commit avec un nouveau SHA et n'en re-signe pas l'objet**. Resultat :

- `git verify-commit <sha>` sur `main` retourne "No principal matched" pour les commits post-merge
- `git cat-file commit <sha>` ne contient **aucun champ `gpgsig`**
- Les commits sur la **branche PR originale** (avant merge) etaient bien signes — CI G3 les a verifies

### Ce que ca veut dire

G3 est **enforced au niveau PR**, pas au niveau main. La chaine de custody existe mais est **distribuee** :

| Couche | Artefact | Ou verifier |
|--------|----------|-------------|
| Local pre-push | Commit signe K001/K002 | `git log --show-signature` sur la branche de travail |
| CI sur PR | `%G?` = G valide | GitHub Actions logs, job `g3-signed-commits` |
| GitHub merge | Qui a mergee, quand, quelle strategie | GitHub audit log |
| Main apres merge | SHA + committer (sans gpgsig) | `git log` sur main |

### Pourquoi ce n'est PAS une faille

- Le merge sur `main` est bloque si le CI G3 echoue sur la PR → aucun commit non signe ne peut atteindre main sans contournement explicite
- `enforce_admins: true` + `required_linear_history: true` + `allow_force_pushes: false` rendent impossible tout contournement
- L'audit log GitHub est tamper-evident (irreversible) et conserve l'identite du merger

### Consequence pour l'audit retro

Un audit local style `_scripts/audit-signatures.sh` sur `main` trouvera **des commits non signes pour chaque PR mergee en rebase**. C'est un **artefact attendu**, pas une violation. Le rapport doit etre lu comme :

- **Non signes pre-policy** (< 2026-02-02) : bootstrap historique, pas d'action
- **Non signes post-rebase** : artefact GitHub Free, trace compensee par CI logs de la PR
- **Non signes inattendus** (post-policy, pas de PR associee) : **vraie anomalie**, a investiguer

### Options de resolution (si gap inacceptable un jour)

1. **GitHub Pro** (~4€/mois) → activer `required_signatures: true` → GitHub auto-signe les rebased commits avec sa cle verifiee
2. **Changer strategie `--merge`** → preserve les signatures mais casse `required_linear_history`
3. **Rebase local + push** avant de merger via PR → permet de signer chaque commit rebase (lourd manuellement)

Choix actuel : **Option B** (documenter le gap, compter sur CI + audit log GitHub comme controle compensatoire). Decision tracee dans [[signing-policy]] et dans l'evidence-pack [[INDEX-EP-20260418-governance-hardening]].

---

## Interaction avec les Hooks Locaux

| Niveau | Fichier | Executions |
|--------|---------|------------|
| Local (machine dev) | `.githooks/pre-commit` | A chaque `git commit` |
| CI serveur | `.github/workflows/vault-governance.yml` | A chaque push et PR |
| Branch protection | Cote GitHub (cette doc) | Au moment du merge |

Les trois niveaux sont **redondants par conception**. Le local attrape 99% des erreurs sans cout CI. Le CI attrape ce qui passe a travers le local (machine sans hook, bypass `--no-verify`, etc.). La branch protection est la gardienne ultime — elle empeche le merge meme si les 2 autres ont echoue a detecter.

---

## Verification d'Integrite

```bash
# Verifier que la protection est bien active
gh api repos/ak125/governance-vault/branches/main/protection \
  | jq '{
      enforce_admins: .enforce_admins.enabled,
      linear_history: .required_linear_history.enabled,
      checks: [.required_status_checks.contexts[]],
      force_push: .allow_force_pushes.enabled,
      deletions: .allow_deletions.enabled
    }'
```

Resultat attendu :

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

Si l'une de ces valeurs est `false` (sauf `force_push`/`deletions` qui sont dans le bon sens), la protection est **compromise** — relancer `setup-branch-protection.sh`.

---

## Voir aussi

- [[rules-vault]] — G1-G4 canoniques
- [[signing-policy]] — G3 SSH signing setup
- [[ci-policy]] — G4 CI read-only
- [[key-registry]] — Cles autorisees pour les signatures

---

_Derniere mise a jour: 2026-04-18_
