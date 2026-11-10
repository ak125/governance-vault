---
type: runbook
status: canon
updated: 2026-11-10
related: [ADR-061, ADR-015]
---

# Runbook — sync-canon-mirrors

> Synchronisation cron quotidienne des **canon mirrors** depuis le vault vers les repos consommateurs (ADR-061 §3).

## Vue d'ensemble

| Composant | Path | Rôle |
|-----------|------|------|
| **Manifeste** | `governance-vault/99-meta/canon-hashes.json` | Liste des canons + consumers + hashes attendus |
| **Script Python** | `governance-vault/_scripts/sync_canon_mirrors.py` | Logique sync (read manifeste, strip frontmatter, write consumers) |
| **Wrapper bash** | `governance-vault/_scripts/cron-sync-canon-mirrors.sh` | Entry point cron VPS DEV, worktree Git isolé + commit signé + auto-PR |
| **Pre-commit hook** | `nestjs-remix-monorepo/.husky/canon-mirrors-verify.sh` | Bloque édits manuels de `.claude/canon-mirrors/*` côté monorepo |
| **Cron entry** | crontab du compte DEV | Exécute le wrapper si configuré ; activation à vérifier |

## Direction de flux (ADR-061 §3 — canon mirrors are read-only)

```
governance-vault/ledger/rules/rules-*.md  (SoT — édité par humain via PR vault)
            │
            ▼
governance-vault/99-meta/canon-hashes.json  (généré par compute-canon-hashes.py)
            │
            ▼ [cron-sync-canon-mirrors.sh]
            ▼ [sync_canon_mirrors.py --write]
            │
            ▼
<worktree Git temporaire du monorepo>/
  ├── .claude/canon-mirrors/<canon>.md             (read-only mirror)
  └── workspaces/<domain>/.claude/canon-mirrors/<canon>.md  (read-only mirror)
```

**Jamais** d'édit manuel direct dans `.claude/canon-mirrors/` — le pre-commit hook côté monorepo bloque les diffs sortant de la sync auto.

## Préservation du checkout partagé

Le wrapper lit le dépôt indiqué par `MONOREPO_ROOT` (défaut : checkout DEV), puis récupère
`origin/main` dans une branche unique et crée un **worktree Git temporaire**. Projection,
indexation, commit signé et push s’exécutent dans ce worktree. Il ne change ni la branche,
ni le HEAD, ni l’index, ni les fichiers du checkout partagé, même s’il contient des commits
non poussés, des modifications indexées/non indexées ou des fichiers non suivis.

- `dry` reste sans écriture Git ni appel GitHub. Un argument inconnu est refusé.
- Sans changement, seul le worktree créé par le run et sa ref inchangée sont supprimés.
- Après création réussie de la PR, le worktree propre est retiré par `git worktree remove`,
  sans `--force`. La branche de PR est conservée.
- En cas d’erreur de projection, signature, push ou création de PR, la branche et le worktree
  sont conservés ; leur chemin est indiqué sur stderr. Aucun effacement de branche distante :
  une erreur API peut survenir après création effective de la PR.
- Les exécutions concurrentes ont des noms distincts. Elles peuvent proposer deux PR pour le
  même écart ; l’isolation protège les fichiers, elle ne déduplique pas les PR.

Les refs et objets Git de la synchronisation sont partagés avec le dépôt. Aucune configuration
Git globale, identité de signature, clé ou entrée cron n’est modifiée par le wrapper.

### Verrou des worktrees

Git n’écrit ni ne retire `.git/worktrees/<id>/` de façon atomique. Pendant un `git worktree add`
ou un `git worktree remove`, une commande Git qui énumère les worktrees peut lire une entrée
incomplète, ou un dossier disparu, et échouer :

| Message de Git | Code |
|---|---|
| `failed to read .git/worktrees/<id>/commondir` | 128 |
| `could not create directory of '.git/worktrees/<id>'` | 128 |
| `bad object worktrees/<id>/HEAD` | 1 |

Le wrapper passe donc ses trois commandes concernées (fetch vers la branche du run,
`worktree add`, `worktree remove`) sous un verrou `flock` posé sur le répertoire Git commun du
dépôt. Aucun fichier n’est créé. Le verrou est tenu par le wrapper, pas par Git : un processus
que Git laisse derrière lui (maintenance) ne le garde pas.

- Deux runs du wrapper ne se gênent plus : le second attend le verrou.
- L’attente est bornée à 120 s (`LOCK_TIMEOUT` dans le wrapper). Au-delà, la commande Git n’est pas lancée et le wrapper écrit
  `worktree lock not obtained within 120 s … (git <commande> not run)`. Le fetch réseau se fait
  sous le verrou : un fetch lent d’un run peut faire expirer l’attente d’un autre.
- Un signal d’arrêt (SIGTERM) envoyé au seul processus du wrapper n’est traité qu’à la fin de
  la commande en cours : l’attente du verrou (120 s au plus) ou la commande Git lancée sous le
  verrou (un fetch lent, par exemple). Envoyé au groupe de processus, il arrête aussi `flock` ou
  Git, et le wrapper sort aussitôt. Reçu pendant le nettoyage final, il fait sortir le wrapper
  en code 1 avec le message `interrupted during cleanup; inspect <dossier canon-sync.*>`. Seule
  la toute dernière commande, qui retire ce dossier une fois vide, se fait signaux ignorés : le
  wrapper sort alors en 0.
- Un SIGKILL envoyé au seul processus du wrapper pendant une commande Git libère le verrou alors
  que cette commande tourne encore : un autre run peut alors la croiser.
- Le verrou ne protège que les runs du wrapper. Un `git worktree add` ou `remove` lancé par une
  autre session dans le même dépôt peut encore faire échouer un run. Dans l’autre sens, le
  `worktree add` et le `worktree remove` du wrapper peuvent faire échouer, pendant un court
  instant, un `fetch` ou une commande `git worktree` d’une session voisine. Ces échecs sont
  transitoires : relancer la commande.

Ce qu’un run laisse quand le verrou n’est pas obtenu dépend de l’étape. Le dossier
`canon-sync.*` est dans `$TMPDIR`, ou dans `/tmp` si la variable n’est pas définie (cas du cron).

| Étape | Code de sortie (verrou non obtenu) | Ce qui reste |
|---|---|---|
| fetch | 75 | un dossier `canon-sync.*` vide ; aucune branche |
| `worktree add` | 75 | la branche locale `govvault/cron-sync-canon-mirrors-…` et un dossier `canon-sync.*` vide |
| `worktree remove` | 1 | le worktree dans `canon-sync.*/worktree` et la branche locale ; si le run a trouvé un écart, la branche distante et la PR, déjà ouverte |

Au `worktree remove`, le code est 1 et non 75 : le run a déjà produit son résultat (PR ouverte,
ou « aucun écart »), seul le nettoyage a échoué. Le message `worktree retained for inspection`
donne le chemin. Un code 75 sans le message `worktree lock not obtained` vient de Git ou d’un
hook, pas du verrou.

Une erreur de `flock` (message `flock failed`) laisse les mêmes restes ; le code de sortie est
alors celui rendu par l’appel à `flock` au fetch et au `worktree add`, 1 au `worktree remove`.
Il en va de même si le répertoire Git commun ne peut pas être ouvert pour le verrou (message
`cannot open … for locking`, code 1 à chaque étape).

Quand c’est la commande Git qui échoue, ce tableau ne s’applique pas : le reste dépend du point
où Git s’est arrêté. Un `worktree add` qui échoue après le checkout (hook `post-checkout` en
échec, par exemple) laisse un worktree complet et inscrit. Le message `sync failed; retain
branch … and worktree …` donne la branche et le chemin ; `git -C <monorepo> worktree list` dit
si le worktree est inscrit.

Un run arrêté par un signal laisse lui aussi ce qu’il avait créé à cet instant (dossier
`canon-sync.*`, branche locale, worktree). Après un SIGKILL, aucun message ne le dit.

Le run suivant ne reprend aucun de ces restes : il repart d’une branche neuve. Les supprimer à la
main après inspection, dans cet ordre :

```bash
git -C <monorepo> worktree remove <dossier canon-sync.*>/worktree   # si le worktree est resté
rmdir <dossier canon-sync.*>
git -C <monorepo> branch -D <branche>                               # branche locale sans PR
```

Si le worktree contient du travail non commité, `git worktree remove` refuse : relire ce
travail, puis ajouter `--force`. La branche locale d’une PR ouverte peut rester : un run réussi
la laisse aussi.

Un signal envoyé au groupe de processus pendant le `worktree remove` final peut laisser un
worktree à moitié supprimé, encore inscrit. Si son fichier `.git` a disparu, `git worktree
remove` répond `validation failed, cannot remove working tree`, même avec `--force`, et les deux
autres commandes échouent aussi. Remplacer alors la première commande par ces deux-ci, puis
reprendre la suite :

```bash
rm -rf <dossier canon-sync.*>/worktree
git -C <monorepo> worktree prune
```

Le wrapper lance `worktree remove` sans `--force` : Git ne commence à supprimer qu’un worktree
sans modification ni fichier non suivi (les fichiers ignorés par `.gitignore` ne comptent pas).

## Activation initiale (à exécuter UNE fois par VPS DEV)

### 1. Vérifier les prérequis

```bash
# Token GitHub avec write:repo monorepo
echo $GH_TOKEN | gh auth status --hostname github.com

# Clé G3 chargée pour commits signés
gpg --list-secret-keys --keyid-format=long

# Python 3.11+
python3 --version

# flock (util-linux), pour le verrou des worktrees
flock --version

# Monorepo + vault clones synchronisés
ls /opt/automecanik/governance-vault /opt/automecanik/app
```

### 2. Test manuel en dry-run

```bash
bash /opt/automecanik/governance-vault/_scripts/cron-sync-canon-mirrors.sh dry
```

Attendu : preview des canons en drift, aucun fichier modifié, aucune PR ouverte.

### 3. Test manuel write

```bash
bash /opt/automecanik/governance-vault/_scripts/cron-sync-canon-mirrors.sh
```

Attendu si drift : auto-PR ouverte sur `ak125/nestjs-remix-monorepo` (label `auto`).
Attendu si pas de drift : `OK: no canon mirror drift, no PR opened`.

### 4. Ajouter le cron VPS DEV (deploy@VPS-DEV)

```bash
crontab -e
```

Ajouter la ligne :

```
# Sync canon mirrors quotidien (ADR-061 §3) — 06:00 UTC = 07:00 Europe/Paris
0 6 * * *  /opt/automecanik/governance-vault/_scripts/cron-sync-canon-mirrors.sh >> /var/log/governance-vault/sync-canon-mirrors.log 2>&1
```

Vérifier :

```bash
crontab -l | grep sync-canon-mirrors
```

## Vérification end-to-end (post-activation)

1. **Premier cycle (T+1 jour)** : vérifier `/var/log/governance-vault/sync-canon-mirrors.log` pour le run automatique. Vérifier `gh pr list --repo ak125/nestjs-remix-monorepo --label auto`.

2. **3 cycles consécutifs (T+3 jours)** : 0 erreur log, drift géré (PR ouverte + mergée OU no-op).

3. **Gate strict (Phase B, post-observation)** : ajouter un job CI monorepo `canon-mirrors-verify` qui exécute `python3 governance-vault/_scripts/sync_canon_mirrors.py --check --monorepo .` et bloque tout PR introduisant un drift non-auto.

## Triage en cas d'incident

### Le cron a tourné mais aucune PR ouverte

- Vérifier `/var/log/governance-vault/sync-canon-mirrors.log` : message `OK: no canon mirror drift, no PR opened` = pas de drift, comportement attendu.
- Si erreur Python : vérifier `99-meta/canon-hashes.json` est cohérent (`python3 _scripts/compute-canon-hashes.py --check` doit pass).

### Le run a échoué (signature, push ou création de PR)

- Le run échoue et conserve le worktree ainsi que la branche affichés dans stderr. Inspecter leur diff et les PR distantes avant toute reprise ; une réponse API en erreur ne prouve pas que la PR est absente. Ne pas supprimer automatiquement la branche distante.
- Vérifier `GH_TOKEN` (expiration, scope `write:repo` sur monorepo).
- Vérifier label `auto` existe sur le monorepo : `gh label list --repo ak125/nestjs-remix-monorepo | grep auto`.

### Le run a échoué sur le verrou ou sur une entrée de worktree

- Message `worktree lock not obtained within 120 s` : un autre run du wrapper tenait le verrou.
  Le message nomme la commande qui n’a pas été lancée. Vérifier qu’aucun run n’est bloqué
  (`pgrep -af cron-sync-canon-mirrors`).
  - `git fetch not run` ou `git worktree add not run` (code 75) : aucun commit ni PR ; laisser
    le cycle suivant s’exécuter.
  - `git worktree remove not run` (code 1) : le run a abouti, son worktree est resté. Si une PR
    a été ouverte, elle est valide. Inspecter le worktree indiqué, puis le retirer.
- Message `flock failed (code N)` : l’appel à `flock` a échoué (commande absente, par exemple).
  Corriger la cause ; le run n’a pas lancé la commande Git de cette étape.
- Message `cannot open … for locking` : le répertoire Git commun n’a pas pu être ouvert (droits,
  dépôt déplacé pendant le run). Le run n’a pas lancé la commande Git de cette étape.
- Message `interrupted during cleanup` : le run a reçu un signal pendant son nettoyage. Son
  résultat (PR ouverte, ou « aucun écart ») est acquis ; le dossier indiqué reste à retirer. Il
  peut être vide ou contenir le worktree, entier ou à moitié supprimé. Sans écart, la branche
  locale du run peut rester aussi.
- Message `failed to read .git/worktrees/<id>/commondir`, `could not create directory of
  '.git/worktrees/<id>'` ou `bad object worktrees/<id>/HEAD` : une autre session administrait un
  worktree au même instant. Le cycle suivant repart d’une branche neuve.
- « Verrou des worktrees » liste ce qu’un run laisse après un verrou non obtenu ou une erreur
  de `flock`, et donne les commandes de retrait, y compris pour un worktree à moitié supprimé.

### Drift permanent (PR auto mergée puis re-créée demain)

- Symptôme : même drift réapparaît chaque jour.
- Cause probable : édit manuel quotidien dans `.claude/canon-mirrors/` (le pre-commit hook devrait bloquer — vérifier qu'il est actif).
- Action : audit `git log .claude/canon-mirrors/` pour identifier l'origine, désactiver le manuel.

### Commit signé fail

- Vérifier `gpg-agent` est running pour le user `deploy`.
- Vérifier `GPG_KEY_ID` dans l'environnement cron (`crontab -e` peut nécessiter un `GPG_TTY=$(tty); export GPG_TTY` ou un agent persistant).

## Références

- [[ADR-061-workspace-governance]] §3 — canon mirrors read-only
- [[ADR-015-vault-single-source-of-truth]] — vault SoT
- `_scripts/compute-canon-hashes.py` — génère le manifeste
- `_scripts/cron-sync-moc-decisions.sh` — pattern modèle (sync intra-vault Phase A)
