---
type: knowledge
scope: devex/ci
date: 2026-04-21
owner: Fafa
pr: https://github.com/ak125/governance-vault/pull/18
tags: [devex, ci, hooks, automation, no-bricolage]
---

# Pre-Push Local Check Pattern — Éliminer les Aller-Retours CI

> **Règle candidate pattern réutilisable**
> **Origine** : friction PRs #14/#15/#16 vault (3 aller-retours CI pour downgrade wikilinks + register dans MOC)

---

## Problème

Un contributeur pousse un PR, attend CI (~30s-5min), voit un check échouer (ex: wikilink cassé, fichier orphelin), corrige, re-pousse, attend encore. Cycle typique : 3-5 aller-retours pour des erreurs triviales que le même check aurait détecté localement en <1 seconde.

Coût cumulé :
- Temps contributeur : 5-15 min par PR bloquée
- Compute CI gaspillé
- Revue décorrélée de l'itération (focus cassé)
- Tentation de `--force-push` ou `--admin merge` pour contourner → dette de gouvernance

## Solution

**Déplacer les checks CI critiques côté local via un hook `pre-push`**, utilisant **exactement les mêmes scripts** que CI.

### Implementation minimale (vault exemple)

```bash
#!/usr/bin/env bash
# .githooks/pre-push — identique aux checks CI, exécuté avant push
set -euo pipefail

VAULT_ROOT="$(git rev-parse --show-toplevel)"
has_failure=0

for check in check-orphans.sh check-broken-links.sh; do
  SCRIPT="$VAULT_ROOT/_scripts/$check"
  [ -x "$SCRIPT" ] || continue
  if ! bash "$SCRIPT" "$VAULT_ROOT" > /tmp/pre-push-${check%.sh}.log 2>&1; then
    echo "✗ $check FAIL"
    head -5 /tmp/pre-push-${check%.sh}.log
    has_failure=1
  else
    echo "✓ $check"
  fi
done

if [ "$has_failure" -ne 0 ]; then
  echo ""
  echo "Push refusé : fix avant de re-pousser."
  echo "Bypass urgence (casse PR CI) : git push --no-verify"
  exit 1
fi
```

### Install

```bash
# Une fois par clone, puis persistant
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

Pour contribuer à l'écosystème : engager `.githooks/` dans le repo + documenter l'install dans README.

## Invariants respectés

| Invariant | Comment |
|-----------|---------|
| **Parité CI/local** | Hook appelle les mêmes scripts que CI. Zéro risque de divergence. |
| **Bypass possible** | `git push --no-verify` reste accessible pour cas d'urgence (mais marque la PR CI failed). |
| **Auto-install** | `core.hooksPath=.githooks` configuré une fois par clone, pas de script d'install à maintenir. |
| **Visibilité** | Hook commité dans le repo, visible pour tous les contributeurs. |

## Anti-patterns à éviter

1. **Réimplémenter les checks dans le hook** — divergence garantie. Toujours appeler les scripts CI directement.
2. **Hook bloquant sur des checks lents** (>10s) — frustration utilisateur. Réserver le pre-push aux checks rapides.
3. **Hook silencieux** — si le hook échoue sans message explicite, l'utilisateur perd du temps à deviner. Toujours afficher le rapport + une suggestion de remediation.
4. **Hook sans bypass** — cas d'urgence (rollback, hotfix prod) nécessitent un override. `--no-verify` standard.

## Applicabilité

Ce pattern marche dès qu'un CI a des checks rapides (<5s) et déterministes. Exemples :

| Repo | Checks à migrer local | Bénéfice attendu |
|------|-----------------------|-------------------|
| `nestjs-remix-monorepo` | `eslint --cache`, `tsc --noEmit` (partiellement en pre-commit lint-staged déjà), `npm audit --audit-level=critical` | -70% aller-retours CI sur PRs triviales |
| `governance-vault` | ✅ Implémenté (check-orphans + broken-wikilinks) | Déjà appliqué |
| `rag-corpus` | `yaml-validate`, `check-slugs.sh` | Moyen |

## Règle candidate canon

> **Tout check CI déterministe de <5 secondes doit exister en parallèle en hook git local (`pre-commit` ou `pre-push`) appelant le même script. L'absence de cette duplication est un bug de DX.**

## Références

- Vault hook : [`.githooks/pre-push`](https://github.com/ak125/governance-vault/blob/main/.githooks/pre-push)
- Scripts réutilisés : `_scripts/check-orphans.sh`, `_scripts/check-broken-links.sh`
- Incident déclencheur : PRs #14/#15/#16 aller-retours CI (avant hook) → résolu PR #18
