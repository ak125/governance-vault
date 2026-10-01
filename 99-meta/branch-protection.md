---
type: policy
status: canon
rule: G2,G3,G4
updated: 2026-10-01
---

# Politique de Protection de Branche (main)

**Statut** : Actif depuis 2026-04-18 ; `enforce_admins` effectif depuis une date situee entre le 2026-08-14 et le 2026-09-30 (voir « Pushes directs historiques »)
**Enforcement** : Cote serveur via GitHub Branch Protection Rules
**Regles canoniques** : [[rules-vault]] G2, G3, G4 (G1 n'a pas de check automatique) ; check `No V1 Paths` = ADR-015

---

## Regle

> **La branche `main` est verrouillee cote serveur**. Aucun push direct n'est possible, meme pour les admins (`enforce_admins: true`). Toute modification passe par une PR qui doit satisfaire les required status checks (liste ci-dessous).

Cette protection est la **quatrieme ligne de defense** apres :

1. **Pre-commit hook local** (`.githooks/pre-commit`) — G2 et wikilinks avant chaque commit
2. **Pre-push hook local** (`.githooks/pre-push`) — G2, wikilinks et signatures (G3) avant chaque push
3. **CI workflow** (`.github/workflows/vault-governance.yml`) — verifie chaque PR vers `main` et chaque push sur `main` ou `refactor/**`
4. **Branch protection** (cette doc) — bloque le merge cote GitHub si un check manque

Les deux hooks ne sont actifs que si `core.hooksPath` vaut `.githooks` dans le clone.

---

## Configuration Appliquee

Valeurs declarees par `_scripts/setup-branch-protection.sh` ; les checks requis sont ceux de la section suivante. `setup-branch-protection.sh --check` dit si la protection en vigueur leur est conforme (voir « Verification d'Integrite »).

| Parametre | Valeur | Justification |
|-----------|--------|---------------|
| `required_status_checks.checks` | checks CI lies a GitHub Actions (voir ci-dessous) | Chaque check de la section suivante doit passer |
| `required_status_checks.strict` | `true` | La branche PR doit etre a jour avec `main` |
| `enforce_admins` | `true` | Personne ne contourne, y compris l'owner |
| `required_linear_history` | `true` | Pas de merge commits : squash ou rebase (en pratique squash, voir « Methode de Merge ») |
| `required_pull_request_reviews` | `count: 0`, `dismiss_stale: true` | Solo repo : reviews non requises, mais les reviews obsoletes sont auto-dismissed |
| `required_signatures` | `true` | Chaque commit de la PR doit etre verifie par GitHub. Voir « Signatures Requises » |
| `restrictions` | `null` | Personne n'est explicitement autorise a bypasser |
| `allow_force_pushes` | `false` | Pas de reecriture d'historique sur main |
| `allow_deletions` | `false` | Impossible de supprimer main |
| `required_conversation_resolution` | `true` | Les threads PR doivent etre resolus avant merge |

---

## Required Status Checks

Le merge est bloque tant que l'un de ces checks n'a pas le status **SUCCESS**. Cette table reprend la liste de `_scripts/setup-branch-protection.sh` ; `_scripts/test_setup_branch_protection.py` verifie qu'elles sont identiques et que chaque check est rapporte par un job sur toute PR vers `main`.

| Check name (cote GitHub) | Job key (cote workflow) | Role |
|--------------------------|--------------------------|------|
| `G2: Zero Orphelin` | `g2-orphans` | Execute `check-orphans.sh`, exit 1 si orphelins |
| `Broken Wikilinks` | `broken-links` | Execute `check-broken-links.sh`, exit 1 si liens casses |
| `G3: Commits signes` | `g3-signed-commits` | Execute `check-signatures.sh` : en PR, chaque commit `base..head` ; sur un push, `HEAD~1..HEAD` seulement |
| `G4: CI read-only sur canon` | `g4-canon-write-block` | Marqueur : le job affiche 3 lignes et ne verifie rien. La lecture seule vient de `permissions: contents: read` en tete du workflow |
| `No V1 Paths (ADR-015)` | `v1-paths` | Execute `check-v1-paths.sh`, exit 1 si un fichier suivi est sous un dossier v1 a la racine (`0X-…/`) ou sous `scripts/` |
| `Vault Scripts Tests` | `vault-scripts-tests` | `pytest _scripts` : les validateurs du vault et leurs tests |
| `Vault Lint Gate (ADR-020)` | `vault-lint-gate` | Execute `ci-vault-gate.sh pr` : checks de `weekly-lint.sh` sur le vault seul et `sync_moc_decisions.py --check` (index [[MOC-Decisions]]) |

Les deux derniers ont ete ajoutes par la PR #360 et sont requis depuis le 2026-10-01 (PATCH de la sous-ressource, puis `--check` conforme).

Tournent sans etre requis (ils ne bloquent pas le merge) : `No Operational Sections (ADR-060 §1A inv. 5)` (job `vault-pollution`, meme workflow) et `Self-Review Marker` (`vault-self-review-marker.yml`).

> **Important** : un check requis designe le **display name** du job (`name:` field dans le YAML), pas le job key, et il est lie a l'app GitHub Actions (`app_id` 15368). Renommer un job impose de mettre a jour, dans la meme PR, le script et cette table (le test ci-dessus echoue sinon), puis la protection.

---

## Setup / Re-application

La configuration est versionnee dans `_scripts/setup-branch-protection.sh`.

Verifier que la protection en vigueur est celle du script (lecture seule, sortie 1 et diff si elle differe) :

```bash
_scripts/setup-branch-protection.sh --check
```

Ajouter ou retirer un check requis sur la protection existante : PATCH de la sous-ressource `required_status_checks` avec la liste `checks` complete et l'`app_id`, puis `--check`. Activer ou retirer les signatures requises : POST ou DELETE de la sous-ressource `required_signatures`, puis `--check`. Ne jamais passer par `contexts` : ce champ deprecie ignore sans erreur un nom jamais observe (voir [[vault-branch-protection-contexts-vs-checks-gotcha-20260504]]).

En cas de perte ou de recreation du repo (PUT complet, puis sous-ressource `required_signatures`, puis relecture comparee a la demande : le script sort 1 si GitHub a abandonne un champ) :

```bash
_scripts/setup-branch-protection.sh
```

Le script utilise `gh api` avec un JSON body complet (via `--input -`) pour eviter le piege `-F restrictions=` qui passe une chaine vide au lieu de `null` (bug 422 historique).

Historique : le 2026-09-30, le diff entre le JSON du script et le GET de la protection etait nul. Jusqu'a cette date, le script declarait les **job keys** (`g2-orphans`…) et omettait `No V1 Paths` : le relancer aurait exige 4 checks qu'aucun job ne rapporte, bloquant toutes les PR, et retire le check v1-paths.

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

Declarees par `setup-branch-protection.sh` (`"required_signatures": true`). Ce n'est pas un champ du PUT : le script l'applique par la sous-ressource `branches/main/protection/required_signatures` (POST active, DELETE retire), apres le PUT, puis relit l'ensemble. L'option est disponible : le depot est public, et la limite de plan GitHub ne vise que les depots prives.

### Ce que cela ajoute a G3

| Controle | Ce qu'il exige | Ou |
|----------|----------------|----|
| G3 (`check-signatures.sh`) | Une signature cryptographiquement valide. Une cle absente du [[key-registry]] (`%G?` = `U`) passe | CI, check requis |
| `required_signatures` | Chaque commit **verifie par GitHub** : cle enregistree comme *Signing Key* sur un compte GitHub, e-mail committer verifie sur ce compte | GitHub, au merge |

G3 prouve qu'une cle a signe ; `required_signatures` prouve que cette cle est rattachee a un compte et a une identite verifies. La documentation GitHub precise que des commits non verifies sur la branche de la PR peuvent bloquer un merge squash, meme si GitHub signe le commit squash final : chaque commit pousse sur une branche de PR doit donc etre verifie.

### Preconditions d'activation

1. Chaque cle qui signe des commits de PR est enregistree comme *Signing Key* sur le compte GitHub (etat par cle : [[key-registry]]).
2. L'e-mail committer de ces commits est un e-mail verifie de ce compte. Dans le clone du vault, `user.email` de la config locale le fixe ; un clone ou une session qui committe avec une autre identite produit des commits non verifies, que la protection refusera.
3. Preuve : un commit signe par chaque cle d'agent, pousse apres l'enregistrement, affiche `verified: true` et `reason: valid` dans `gh api repos/ak125/governance-vault/commits/<sha> --jq .commit.verification`.

Sans ces trois points, l'activation bloque toute PR signee par une cle non enregistree. Tant que l'activation n'est pas faite, `--check` sort 1 avec cette seule difference (`required_signatures` : attendu `true`, en vigueur `false`).

### Retrait

`gh api -X DELETE repos/ak125/governance-vault/branches/main/protection/required_signatures` retire l'exigence ; `--check` reste rouge tant que la declaration du script n'est pas modifiee par PR. Le retrait laisse une trace dans les audit logs GitHub : le documenter comme une desactivation d'urgence.

### Hors de ce reglage

Le merge rebase ajoute les commits de la PR « sans verification de signature » (documentation GitHub) et reste autorise au niveau du depot (`allow_rebase_merge: true`). Le desactiver est un reglage du depot, distinct de la protection de branche ; la methode prescrite reste le squash (section suivante).

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
_scripts/setup-branch-protection.sh --check
```

Le script compare a sa demande les checks requis (nom et `app_id`), `strict`, `enforce_admins`, `required_linear_history`, les reviews, `restrictions`, `allow_force_pushes`, `allow_deletions`, `block_creations` et `required_conversation_resolution`. Tout ecart (check absent ou lie a une autre app, `enforce_admins`, `linear_history` ou `required_signatures` a `false`, `force_push` ou `deletions` a `true`…) est affiche en diff et sort 1 : la protection est **compromise** ou la mise a jour d'une sous-ressource n'a pas ete faite.

---

## Voir aussi

- [[rules-vault]] — G1-G4 canoniques (G2-G4 ont un check requis)
- [[signing-policy]] — G3 SSH signing setup
- [[ci-policy]] — G4 CI read-only
- [[key-registry]] — Cles autorisees pour les signatures

---

_Derniere mise a jour: 2026-10-01_
