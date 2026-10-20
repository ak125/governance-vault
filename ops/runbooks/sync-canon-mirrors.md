---
type: runbook
status: canon
updated: 2026-10-21
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

## Activation initiale (à exécuter UNE fois par VPS DEV)

### 1. Vérifier les prérequis

```bash
# Token GitHub avec write:repo monorepo
echo $GH_TOKEN | gh auth status --hostname github.com

# Clé G3 chargée pour commits signés
gpg --list-secret-keys --keyid-format=long

# Python 3.11+
python3 --version

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
