---
id: ADR-023
title: "Hook-Layer Defense for .local/governance-vault/"
status: accepted
date: 2026-04-24
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G1, G2]
related_incidents: [INC-2026-002]
reviewed_by: "Claude Code Opus 4.7"
---

# ADR-023: Hook-Layer Defense for .local/governance-vault/

## Contexte

L'audit de configuration du 2026-04-24 (post-PR #55) a révélé deux gaps liés au chemin interdit `/opt/automecanik/app/.local/governance-vault/` :

**Gap 1 — Promesse non tenue.** Le `CLAUDE.md` du monorepo (ligne 35) affirme :

> "Un hook `pre-commit` côté monorepo refuse tout fichier sous `app/.local/governance-vault/`."

Vérification au 2026-04-24 :

```bash
$ ls /opt/automecanik/app/.githooks/       → No such file or directory
$ ls /opt/automecanik/app/.git/hooks/pre-commit  → No such file or directory
$ git -C /opt/automecanik/app config --get core.hooksPath  → .husky/_
```

Husky est configuré mais aucune règle ne bloque `.local/governance-vault/`. La promesse est fausse depuis [[ADR-015-vault-single-source-of-truth|ADR-015]].

**Gap 2 — Incident sev1 orphelin.** Le fichier `/opt/automecanik/app/.local/governance-vault/01-incidents/2026-04-14-paybox-tunnel-sev1-ipn-blocked.md` existe (mtime 2026-04-18), contient [[2026-04-14-paybox-tunnel-sev1-ipn-blocked|INC-2026-002]] (Paybox tunnel sev1, 25j downtime). Le vault a sa propre copie autoritative dans `ledger/incidents/2026/2026-04-14-paybox-tunnel-sev1-ipn-blocked.md` (mtime 2026-04-20). La version `.local/` est donc un fantôme post-migration [[ADR-015-vault-single-source-of-truth|ADR-015]] qui n'a jamais été purgé.

**Pourquoi c'est dangereux** :

1. Le chemin `.local/` est `.gitignored` — aucun commit ne peut le versionner, aucune trace git.
2. Si un agent ou humain lit ce fichier (wikilinks `03-rules/...` et `02-decisions/...` sont structure v1 obsolète depuis [[ADR-013-agent-lifecycle-governance|ADR-013]]), il peut créer une PR basée sur cette version fantôme.
3. Un `git clean -fdx` sur le monorepo efface irrémédiablement toute donnée qui y traîne encore — même si c'est un post-mortem sev1 non encore migré.
4. La règle [[rules-vault|G2]] (Zéro Orphelin) s'applique au vault ; par extension, tout fichier de gouvernance dans le monorepo qui n'est pas migré vers le vault viole l'esprit G2.

Le gap est structurel : une règle déclarée dans `CLAUDE.md` sans enforcement est du théâtre. Il faut un mécanisme de défense en profondeur qui rende l'anti-pattern impossible, pas juste interdit.

## Décision

**Instaurer un enforcement à trois couches pour l'anti-pattern `app/.local/governance-vault/`, formalisé par cet ADR et implémenté dans le monorepo `nestjs-remix-monorepo`.**

### Couche 1 — Hook local (husky pre-commit)

Fichier `scripts/governance/block-local-vault.sh` appelé depuis `.husky/pre-commit`. Rejette (exit 1) tout `git commit` dont le staging contient un fichier matchant `^\.local/governance-vault/`.

Message d'erreur explicite qui référence ADR-023 + ADR-015 + la procédure de migration vers le vault.

### Couche 2 — CI monorepo (GitHub Actions)

Workflow `.github/workflows/guard-local-governance.yml` déclenché sur `pull_request: [main]`. Fail si `git diff --name-only origin/main...HEAD` matche `^\.local/governance-vault/`. Défense en profondeur contre les bypass `git commit --no-verify`.

Doit être **required status check** sur la branch protection `main` du monorepo.

### Couche 3 — Weekly cleanup audit (cron DEV VPS)

Cron entry (user `deploy`, DEV VPS) qui exécute chaque lundi 03:00 UTC :

```bash
find /opt/automecanik/app/.local/governance-vault/ -type f 2>/dev/null | tee /var/log/governance-vault/weekly-local-scan.log
```

Si non-vide, envoie un email à `automecanik.seo@gmail.com` via `/usr/bin/mail`. Documenté dans [[cron-setup]].

### Script de prune initial (versionné)

`scripts/governance/prune-local-mirror.sh` (monorepo) :

- **Dry-run par défaut** (liste des fichiers concernés, aucune modification).
- `--apply` requis pour exécuter la suppression.
- Pour chaque fichier sous `.local/governance-vault/` : calcule SHA-256 et cherche une correspondance dans `/opt/automecanik/governance-vault/ledger/incidents/**/*.md`. Si identique → `rm`. Si absent du vault → refuse (migration vers vault requise). Si différent → produit un diff et refuse (review humaine).
- Loggue chaque suppression dans `/opt/automecanik/governance-vault/ledger/audit-trail/YYYY-MM-DD-prune-local-mirror.md` (signé G3).

Utilisé une fois pour purger l'état actuel (INC-2026-002 fantôme), puis les 3 couches empêchent le gap de revenir.

### Test de non-régression

`scripts/governance/test-hook.sh` (monorepo) crée un fichier temporaire sous `.local/governance-vault/test-$(date +%s).md`, tente un `git add` + `git commit -m "test"`, vérifie que le commit **échoue** (couche 1). Puis teste que `gh workflow run guard-local-governance` déclenché sur une PR fictive fail aussi (couche 2). Intégré au CI monorepo.

## Options Considérées

### Option A — Documentation only (statu quo plus clair)

Éditer CLAUDE.md monorepo pour retirer la promesse de hook et remplacer par "responsabilité humaine/agent de ne pas écrire sous `.local/`".

**Avantages** : simple, 1 commit, zéro risque de régression.

**Inconvénients** : admet qu'aucun enforcement n'existe ; le problème revient dès qu'un agent IA fait l'erreur. Viole le principe "zéro bricolage, règle non enforced = pas de règle".

### Option B — Hook local seul (1 couche)

Implémenter le hook husky mais pas de CI ni cron.

**Avantages** : bloque l'erreur humaine la plus commune, faible effort.

**Inconvénients** : `git commit --no-verify` bypass trivial. Un agent IA qui ne respecte pas les hooks (ou les désactive) passe au travers. Faux sentiment de sécurité.

### Option C — Trois couches de défense (retenue)

Hook + CI + cron. Cf. section Décision.

**Avantages** : 3 indépendants, chaque couche rattrape les bypass des autres. Conforme au principe "défense en profondeur" de ce vault. Prune script versionné = reproductible, auditable.

**Inconvénients** : effort initial plus élevé (3 artefacts + 1 test + 1 doc). Complexité maintenance (mais faible, les 3 couches restent simples).

### Option D — Supprimer `.local/` du gitignore monorepo

Rendre `.local/governance-vault/` visible au git → forcer migration immédiate puis le supprimer du filesystem.

**Avantages** : force la question.

**Inconvénients** : cassera d'autres usages légitimes de `.local/` (caches, artifacts). Et n'empêche pas la recréation.

## Justification

L'Option C est la seule qui rend l'anti-pattern réellement impossible à introduire **sans** casser des usages adjacents de `.local/`. Les 3 couches sont indépendantes (hook = local, CI = github, cron = VPS), donc la compromission d'une n'invalide pas les autres. Le script de prune versionné garantit la reproductibilité et l'auditabilité de la migration initiale.

Le coût d'implémentation (1 ADR + 4 fichiers monorepo + 1 CI workflow + 1 cron + 1 test) est amorti dès la première tentative d'écriture fantôme bloquée.

Le principe s'aligne avec :

- [[rules-vault|G2]] (Zéro Orphelin) : étendu au monorepo par symétrie.
- [[ADR-015-vault-single-source-of-truth|ADR-015]] : gouvernance vit uniquement dans le vault.
- [[ADR-020-weekly-vault-lint]] : défense en profondeur déjà établie côté vault (weekly-lint + 4 CI checks).

## Conséquences

### Positives

- L'incident fantôme `INC-2026-002` est purgé proprement avec trace audit.
- Impossible de créer un fichier sous `.local/governance-vault/` via commit normal (3 barrières).
- `CLAUDE.md` monorepo redevient fiable (promesse tenue).
- Les futurs gaps similaires (`.local/governance-vault-v2/`, etc.) se détectent via weekly scan sans intervention humaine.

### Négatives

- +1 CI workflow à maintenir côté monorepo.
- Cron DEV VPS à configurer + documenter (faible charge mais ne doit pas être oublié lors d'un rebuild VPS).
- `git commit --no-verify` reste possible localement → repose sur CI pour rattraper. Acceptable vu la couche 2.

### Neutres

- Aucun impact Obsidian (le vault côté Windows n'interagit pas avec le monorepo).
- Aucun impact CI vault (ADR concerne uniquement le monorepo `nestjs-remix-monorepo`).
- Charge ops quasi nulle (les 3 scripts sont courts, stable, shellcheck-clean).

## Critères de Succès

- [ ] `scripts/governance/block-local-vault.sh` existe dans le monorepo, mode 100755, appelé depuis `.husky/pre-commit`
- [ ] `scripts/governance/test-hook.sh` passe (le hook rejette bien un staging interdit)
- [ ] `.github/workflows/guard-local-governance.yml` existe et est `required` sur la branch protection `main` du monorepo
- [ ] `scripts/governance/prune-local-mirror.sh --dry-run` détecte les fichiers actuels sous `.local/governance-vault/` (au moins INC-2026-002)
- [ ] Après `--apply` : `find /opt/automecanik/app/.local/governance-vault/ -type f` retourne vide
- [ ] Cron weekly-local-scan configuré sur DEV VPS, documenté dans [[cron-setup]]
- [ ] `CLAUDE.md` monorepo mis à jour avec référence à ADR-023 et description des 3 couches

## Implémentation

Répartition en deux PRs :

**PR vault** (ADR seule) :
- `ledger/decisions/adr/ADR-023-hook-layer-defense.md` (ce fichier)
- `ops/moc/MOC-Decisions.md` (ajout lien vers ADR-023)

**PR monorepo** (implémentation) :
- `scripts/governance/block-local-vault.sh` (nouveau, 100755)
- `scripts/governance/test-hook.sh` (nouveau, 100755)
- `scripts/governance/prune-local-mirror.sh` (nouveau, 100755, dry-run par défaut)
- `.husky/pre-commit` (update pour appeler block-local-vault.sh)
- `.github/workflows/guard-local-governance.yml` (nouveau)
- `CLAUDE.md` (section anti-patterns référence ADR-023 + décrit 3 couches)

**Prune initial** (post-merge PR monorepo) :
- Exécuter `scripts/governance/prune-local-mirror.sh --dry-run` depuis DEV VPS
- Validation humaine
- Exécuter `--apply`
- Vérifier audit-trail créé dans le vault

**Cron setup** (post-merge) :
- Ajouter entry cron user `deploy` sur DEV VPS
- Mettre à jour `99-meta/cron-setup.md` du vault (PR vault de suivi)

## Revue Planifiée

**Date**: 2026-10-24 (6 mois)
**Critères de revue**: 
- Zéro incident de régression `.local/governance-vault/` (weekly scan reste vide)
- Hook + CI + cron toujours actifs et documentés
- Si un cas légitime d'écriture sous `.local/governance-vault/` émerge (improbable) : reconsidérer en ADR-successeur

---

*Proposé le: 2026-04-24*
*Accepté le: 2026-04-24*
*Dernière revue: 2026-04-24*
