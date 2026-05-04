---
category: knowledge
doc_family: knowledge
source_type: gotcha
title: Pre-push hook G3 — rejette les worktrees git (bug check `.git` directory-only)
slug: vault-prepush-hook-worktree-gotcha
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-04"
updated_by: "@fafa"
related_adr: []
related_prs:
  - "ak125/governance-vault#148"
related_knowledge:
  - "pre-push-local-check-pattern"
  - "vault-self-review-workflow-20260504"
  - "feedback_git_worktree_for_concurrent_governance"
status: current
tags:
  - gotcha
  - hook
  - worktree
  - g3
  - signing
---

# Pre-push hook G3 — rejette les worktrees git

> Gotcha découvert 2026-05-04 sur PR #148. Le pre-push hook `_scripts/check-signatures.sh`
> rejette les git worktrees parce qu'il vérifie `[[ ! -d ".git" ]]` — or dans
> un worktree, `.git` est un **fichier** pointer (pas un répertoire).
> Workaround : push depuis le checkout principal. Fix : 1 ligne.

## Contexte

Le projet recommande l'usage de `git worktree add` pour le travail concurrent
sur le vault (cf. `feedback_git_worktree_for_concurrent_governance` —
multi-fichiers concurrents → worktree obligatoire).

Or le pre-push hook G3 (`_scripts/check-signatures.sh`) rejette ces worktrees
sans message clair :

```
✗ G3 Commits signes FAIL
Error: not a git repo: /tmp/vault-self-review
  Remediation : git rebase --exec 'git commit --amend --no-edit -S' origin/main
```

La remediation suggérée est **trompeuse** : les commits sont déjà signés
correctement (vérifiable par `git log --format='%G?' -1` → `G`). Le vrai
problème est le check de repo dans le script.

## Cause racine

`_scripts/check-signatures.sh:20` :

```bash
if [[ ! -d "$VAULT_PATH/.git" ]]; then
  echo "Error: not a git repo: $VAULT_PATH" >&2
  exit 2
fi
```

Dans un worktree, `.git` n'est **pas** un répertoire — c'est un **fichier
texte** contenant un pointer vers le gitdir réel :

```
$ ls -la /tmp/vault-self-review/.git
-rw-rw-r-- 1 deploy deploy 75 mai 4 16:16 /tmp/vault-self-review/.git

$ cat /tmp/vault-self-review/.git
gitdir: /opt/automecanik/governance-vault/.git/worktrees/vault-self-review
```

Le test `[[ ! -d ... ]]` retourne donc vrai (pas un dir) → le script exit 2 →
le hook reporte échec G3 alors que la signature est valide.

## Workaround utilisé (PR #148)

Push depuis le checkout principal `/opt/automecanik/governance-vault/` (où
`.git` est un répertoire). Les refs sont partagées entre worktrees, donc le
bon commit est poussé :

```bash
# Travail dans le worktree
cd /tmp/vault-self-review
git add ... && git commit -S -m "..."

# Push depuis le checkout principal
git -C /opt/automecanik/governance-vault push -u origin <branch>
```

Output : `✓ G2`, `✓ Broken Wikilinks`, `✓ G3 Commits signes`, `✓ Pre-push OK`.

## Fix proposé (PR séparée _scripts/)

Remplacer le test `-d` par une vérification compatible worktree :

**Option A** (la plus propre) — utiliser git lui-même :

```bash
if ! git -C "$VAULT_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not a git work tree: $VAULT_PATH" >&2
  exit 2
fi
```

**Option B** (minimal change) — accepter `.git` fichier OU répertoire :

```bash
if [[ ! -e "$VAULT_PATH/.git" ]]; then  # -e = exists (file or dir)
  echo "Error: not a git repo: $VAULT_PATH" >&2
  exit 2
fi
```

Option A est préférable car elle gère aussi les cas exotiques (`GIT_DIR`
externe, submodule). Option B est suffisante pour le cas worktree pur.

À vérifier : si d'autres scripts dans `_scripts/` ont la même check naïve
(grep `! -d.*\.git`) — appliquer le même fix uniformément.

## Anti-patterns évités

- ❌ **`git push --no-verify`** — bypass G3 pour pousser malgré le hook.
  Cassait l'esprit du gate (qui doit valider, pas être contourné).
- ❌ **Quitter le worktree** pour faire le travail dans le checkout principal —
  perdait l'isolation et bloquait potentiellement le travail concurrent
  d'autres branches.
- ❌ **Patcher le hook localement** sans amender le canon — bricolage
  invisible aux autres clones du vault.

## Référence

- `pre-push-local-check-pattern` — pattern original (élimination aller-retours CI)
- `vault-self-review-workflow-20260504` — précédent direct (PR #148 où le bug a été rencontré)
- `feedback_git_worktree_for_concurrent_governance` (memory) — règle qui mène à utiliser des worktrees
- Précédent commit signé verifiable : `5fc44c0` (PR #148, signature `G SHA256:qBBgd1ZloPXm0MkTd7L1fWe8OCAs8BjDfw6h7pxQCow`)
