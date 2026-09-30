---
type: policy
status: canon
rule: G2,G3,G4
updated: 2026-09-30
---

# Politique de Protection de Branche (main)

**Statut** : Actif depuis 2026-04-18 ; `enforce_admins` effectif depuis une date situee entre le 2026-08-14 et le 2026-09-30 (voir « Pushes directs historiques »)
**Enforcement** : Cote serveur via GitHub Branch Protection Rules
**Regles canoniques** : [[rules-vault]] G2, G3, G4 (G1 n'a pas de check automatique) ; check `No V1 Paths` = ADR-015

---

## Regle

> **La branche `main` est verrouillee cote serveur**. Aucun push direct n'est possible, meme pour les admins (`enforce_admins: true`). Toute modification passe par une PR qui doit satisfaire les 5 required status checks.

Cette protection est la **quatrieme ligne de defense** apres :

1. **Pre-commit hook local** (`.githooks/pre-commit`) — G2 et wikilinks avant chaque commit
2. **Pre-push hook local** (`.githooks/pre-push`) — G2, wikilinks et signatures (G3) avant chaque push
3. **CI workflow** (`.github/workflows/vault-governance.yml`) — verifie chaque PR vers `main` et chaque push sur `main` ou `refactor/**`
4. **Branch protection** (cette doc) — bloque le merge cote GitHub si un check manque

Les deux hooks ne sont actifs que si `core.hooksPath` vaut `.githooks` dans le clone.

---

## Configuration Appliquee

Valeurs lues par `gh api repos/ak125/governance-vault/branches/main/protection` le 2026-09-30.

| Parametre | Valeur | Justification |
|-----------|--------|---------------|
| `required_status_checks.contexts` | 5 checks CI (voir ci-dessous) | G2, G3, G4 et No V1 Paths doivent passer |
| `required_status_checks.strict` | `true` | La branche PR doit etre a jour avec `main` |
| `enforce_admins` | `true` | Personne ne contourne, y compris l'owner |
| `required_linear_history` | `true` | Pas de merge commits : squash ou rebase (en pratique squash, voir « Methode de Merge ») |
| `required_pull_request_reviews` | `count: 0`, `dismiss_stale: true` | Solo repo : reviews non requises, mais les reviews obsoletes sont auto-dismissed |
| `required_signatures` | `false` | Voir « Signatures Requises » |
| `restrictions` | `null` | Personne n'est explicitement autorise a bypasser |
| `allow_force_pushes` | `false` | Pas de reecriture d'historique sur main |
| `allow_deletions` | `false` | Impossible de supprimer main |
| `required_conversation_resolution` | `true` | Les threads PR doivent etre resolus avant merge |

---

## Required Status Checks (5 jobs)

Le merge est bloque tant que l'un de ces 5 checks n'a pas le status **SUCCESS** :

| Check name (cote GitHub) | Job key (cote workflow) | Role |
|--------------------------|--------------------------|------|
| `G2: Zero Orphelin` | `g2-orphans` | Execute `check-orphans.sh`, exit 1 si orphelins |
| `Broken Wikilinks` | `broken-links` | Execute `check-broken-links.sh`, exit 1 si liens casses |
| `G3: Commits signes` | `g3-signed-commits` | Execute `check-signatures.sh` : en PR, chaque commit `base..head` ; sur un push, `HEAD~1..HEAD` seulement |
| `G4: CI read-only sur canon` | `g4-canon-write-block` | Marqueur : le job affiche 3 lignes et ne verifie rien. La lecture seule vient de `permissions: contents: read` en tete du workflow |
| `No V1 Paths (ADR-015)` | `v1-paths` | Execute `check-v1-paths.sh`, exit 1 si un fichier suivi est sous un dossier v1 a la racine (`0X-…/`) ou sous `scripts/` |

Tournent sans etre requis (ils ne bloquent pas le merge) : `No Operational Sections (ADR-060 §1A inv. 5)` (job `vault-pollution`, meme workflow) et `Self-Review Marker` (`vault-self-review-marker.yml`).

> **Important** : les `contexts` de la protection matchent le **display name** du job (`name:` field dans le YAML), pas le job key. Si tu renommes un job dans le workflow, il faut mettre a jour la protection en consequence.

---

## Setup / Re-application

La configuration est versionnee dans `_scripts/setup-branch-protection.sh`. En cas de perte ou de recreation du repo :

```bash
_scripts/setup-branch-protection.sh
```

Le script utilise `gh api` avec un JSON body complet (via `--input -`) pour eviter le piege `-F restrictions=` qui passe une chaine vide au lieu de `null` (bug 422 historique).

Le JSON du script decrit l'etat en vigueur : le 2026-09-30, le diff entre ce JSON et le GET de la protection (champs du PUT) est nul, donc relancer le script ne change rien. Jusqu'a cette date, le script declarait les **job keys** (`g2-orphans`…) et omettait `No V1 Paths` : le relancer aurait exige 4 checks qu'aucun job ne rapporte, bloquant toutes les PR, et retire le check v1-paths.

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

`required_signatures` vaut `false` (GET du 2026-09-30). L'option est disponible : le depot est public, et la limite de plan GitHub ne vise que les depots prives. Le job `g3-signed-commits` verifie les commits de la PR ; il ne couvre pas le commit que GitHub cree au merge (voir section suivante).

Activer `required_signatures` (endpoint distinct `branches/main/protection/required_signatures`, non gere par le script) est une **decision owner**.

---

## Methode de Merge et Chaine de Signature

### Observation (2026-09-30)

Les trois methodes de merge sont autorisees au niveau du depot (`allow_squash_merge`, `allow_rebase_merge`, `allow_merge_commit` a `true`) ; `required_linear_history: true` exclut les commits de merge, restent squash et rebase.

En pratique, les PR sont fusionnees en **squash** : les 10 PR fusionnees depuis le 2026-07-01 ont toutes GitHub pour committer, un seul parent et une signature GitHub valide (ex. `2f150ef`, PR #353 : `verification.verified = true`, `reason = valid`). Methode prescrite :

```bash
gh pr merge <N> --squash --match-head-commit <sha-de-tete-revu>
```

`--match-head-commit` refuse la fusion si la tete de la PR a bouge depuis la revue.

### Chaine de custody (squash)

| Couche | Artefact | Ou verifier |
|--------|----------|-------------|
| Local pre-push | Commits de la branche signes K001/K002 | `git log --show-signature` sur la branche de travail ; hook `.githooks/pre-push` |
| CI sur PR | G3 : chaque commit `base..head` signe | GitHub Actions, job `g3-signed-commits` |
| GitHub merge | Commit squash signe par GitHub | `gh api repos/ak125/governance-vault/commits/<sha> --jq .commit.verification` |
| Main apres merge | Commit squash (committer GitHub) | `git log` sur main |

Un `git verify-commit` local sur un commit squash echoue : la cle de GitHub n'est pas dans `allowed_signers`. Ce n'est pas une violation ; la preuve est `verification.verified` dans l'API.

### Historique : merges rebase et commits de merge

- **Merges rebase** : 22 commits de PR fusionnees en rebase n'ont pas de signature (PR #3 a #25 du 2026-04-18 au 2026-04-21, puis `b51f69e`, PR #336, le 2026-07-05). Le rebase reecrit les commits ; la signature K001/K002 de la branche ne survit pas. Trace compensatoire : le run G3 de la PR.
- **Commits de merge** : 7 commits de merge PR #316 a #324 (2026-06-14 au 2026-06-19, dernier `636642d`), malgre `required_linear_history`. Coherent avec un contournement admin a une date ou `enforce_admins` n'etait pas effectif.

### Pushes directs historiques (sans PR)

Avant qu'`enforce_admins` soit effectif, des pushes admin ont atteint `main` sans PR :

- **Cron planning** (`_scripts/planning/run-cron.sh`, ADR-053) : 63 commits `chore(planning)` pousses directement du 2026-05-08 au 2026-08-14 ; son journal compte 61 lignes `Bypassed rule violations for refs/heads/main` (derniere le 2026-08-14 : « Changes must be made through a pull request », « 5 of 5 required status checks are expected »). Aucun ruleset n'existe (`gh api …/rulesets` → `[]`) : le contournement vient donc de la protection classique avec `enforce_admins` inactif. Commits signes K001, cle non enregistree sur GitHub (`unknown_key`).
- **Commits de contenu sans PR** apres le 2026-04-18 : `7237868`, `7bd9cb8` (2026-04-30, knowledge), `b786b93` (2026-06-26, amendement ADR-045 / ADR-063), `fc9f0b3` (2026-06-27, runbook), `871ecc2` (2026-06-28, statut d'ADR-095). Verifie par `gh api repos/ak125/governance-vault/commits/<sha>/pulls` → `[]`. Leur ratification (ou leur rejeu par PR) est une **decision owner**.

### Lecture d'un audit de signatures sur `main`

Un audit local (`_scripts/audit-signatures.sh`) sur `main` doit classer chaque commit :

- **Squash signe par GitHub** : normal ; verifier par l'API, pas par `git verify-commit`
- **Push direct avant la protection** (< 2026-04-18) : aucune PR n'etait requise ; 8 de ces commits ne sont pas signes (2026-02-02 au 2026-03-08, commit initial `d80c845` compris) : amorcage, pas d'action
- **Non signe, merge rebase** (liste ci-dessus) : artefact, trace compensee par le run G3 de la PR
- **Signe K001, push direct sans PR** (liste ci-dessus) : contournement admin historique, a ratifier
- **Non signe inattendu** (sans PR associee) : **vraie anomalie**, a investiguer

Evidence-pack d'origine : [[INDEX-EP-20260418-governance-hardening]].

---

## Interaction avec les Hooks Locaux

| Niveau | Fichier | Executions |
|--------|---------|------------|
| Local (machine dev) | `.githooks/pre-commit` | A chaque `git commit` (G2, wikilinks) |
| Local (machine dev) | `.githooks/pre-push` | A chaque `git push` (G2, wikilinks, signatures G3) |
| CI serveur | `.github/workflows/vault-governance.yml` | A chaque PR vers `main` ; a chaque push sur `main` ou `refactor/**` |
| Branch protection | Cote GitHub (cette doc) | Au moment du merge |

Les niveaux sont **redondants par conception**. Le local attrape la plupart des erreurs sans cout CI. Le CI attrape ce qui passe a travers le local (machine sans hook, bypass `--no-verify`, etc.). La branch protection est la gardienne ultime — elle empeche le merge meme si les autres niveaux ont echoue a detecter.

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
    "G4: CI read-only sur canon",
    "No V1 Paths (ADR-015)"
  ],
  "force_push": false,
  "deletions": false
}
```

Si l'une de ces valeurs differe (`enforce_admins` ou `linear_history` a `false`, un check absent, `force_push` ou `deletions` a `true`), la protection est **compromise** — relancer `setup-branch-protection.sh`.

---

## Voir aussi

- [[rules-vault]] — G1-G4 canoniques (G2-G4 ont un check requis)
- [[signing-policy]] — G3 SSH signing setup
- [[ci-policy]] — G4 CI read-only
- [[key-registry]] — Cles autorisees pour les signatures

---

_Derniere mise a jour: 2026-09-30_
