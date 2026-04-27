---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: CodeQL false positive — alerts flagged as "new" on large diffs
slug: codeql-volume-false-positive
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-27"
updated_by: "@fafa"
related_adr: []
related_prs:
  - "ak125/nestjs-remix-monorepo#190"
status: current
---

# CodeQL false positive — large diffs

> Lessons learned PR #190 (2026-04-27, 367 fichiers réécrits par codemod alias TS).
> CodeQL a flaggé 17 alerts "new" qu'il n'aurait pas dû — toutes sur des lignes de
> code business non touchées par la PR.

## 1. Symptôme

Sur la PR :
```
CodeQL — fail (4s)
### New alerts in code changed by this pull request
Security Alerts:
 * 8 critical
 * 9 high

Alerts not introduced by this pull request might have been detected
because the code changes were too large.
```

Note officielle CodeQL : *"code changes too large"*. Le scanner ne fait pas de diff
correct au-delà d'un seuil interne (probablement ~300 fichiers) et flag des alerts
**pré-existantes** comme nouvelles.

## 2. Procédure de diagnostic

### 2.1 Lister les alerts CodeQL pour la PR

```bash
gh api "repos/<owner>/<repo>/code-scanning/alerts?ref=refs/pull/<PR>/merge&state=open&per_page=20" \
  | python3 -c "
import json, sys
for a in json.load(sys.stdin):
    loc = a.get('most_recent_instance',{}).get('location',{})
    rule = a.get('rule',{})
    print(f\"{rule.get('severity','?'):10} {loc.get('path','?'):60}:{loc.get('start_line','?')} rule={rule.get('id','?')}\")"
```

### 2.2 Calculer l'intersection alerts ∩ diff réel

```bash
ALERT_FILES=$(gh api "repos/<owner>/<repo>/code-scanning/alerts?ref=refs/pull/<PR>/merge&state=open&per_page=20" \
  | python3 -c "import json,sys; [print(a.get('most_recent_instance',{}).get('location',{}).get('path','')) for a in json.load(sys.stdin)]" | sort -u)
MY_FILES=$(git diff origin/main --name-only)

# Intersection = fichiers où mon diff touche un fichier alerté
INTERSECT=$(comm -12 <(echo "$ALERT_FILES" | sort) <(echo "$MY_FILES" | sort))

# Pour chaque fichier intersecté, vérifier si le diff touche autre chose que des imports
for f in $INTERSECT; do
  diff_lines=$(git diff origin/main -- "$f" | grep -E "^[-+]" | grep -vE "^[-+]{3}" | wc -l)
  imports_only=$(git diff origin/main -- "$f" | grep -E "^[-+]" | grep -vE "^[-+]{3}" | grep -vE "^[-+]\s*(import |from ')" | wc -l)
  echo "$f: $diff_lines diff lines, $imports_only NON-imports"
done
```

Si `imports_only = 0` pour tous les fichiers intersectés → toutes les alerts sont
sur du code que ta PR n'a pas touché. **False positive volume-induced.**

## 3. Décision

| Test | Verdict |
|---|---|
| `imports_only = 0` ∀ fichier intersecté | False positive — bypass safe |
| `imports_only > 0` sur ≥ 1 fichier | Vérifier manuellement — possible vraie alert |
| Fichiers alertés ∉ ton diff | False positive volume — pure pollution |

Sur PR #190 : 12 fichiers alertés, 5 dans intersection avec PR, 0 lignes non-imports
modifiées sur les 5. Conclusion : 100% false positive. Merge effectué après
validation.

## 4. Quand mitiger pré-merge

Pour une PR qui sera large (rénommage massif, codemod, regroupement modules) :

### 4.1 Splitter en plusieurs PRs

Si possible, découper la PR en chunks de < 200 fichiers chacun. Réduit la probabilité
de déclencher la heuristique CodeQL.

### 4.2 Annoter la PR description

Inclure dès l'ouverture :

```markdown
## CodeQL note

This PR rewrites N files via codemod (purely mechanical, no business logic change).
CodeQL may flag pre-existing alerts as "new" due to diff volume — see procedure to
verify in vault knowledge: codeql-volume-false-positive-20260427.md.
```

### 4.3 Branch protection

Si `CodeQL` est dans `required_status_checks`, le merge sera bloqué. Soit :
- Demander à un admin de bypass (motivé par l'audit intersection)
- Désactiver temporairement la rule pour cette PR (à éviter)
- Mieux : convertir CodeQL en non-bloquant (`continue-on-error: true` workflow level
  ou retiré des required checks pour les PRs)

## 5. Limites de cette procédure

- Ne couvre **pas** les vraies alerts dissimulées dans le bruit. Toujours faire l'audit
  d'intersection avant de conclure "false positive".
- L'heuristique CodeQL "code changes too large" n'est pas documentée publiquement avec
  un seuil exact. Empiriquement, observé sur PR #190 (367 fichiers).
- Pour PRs `< 100` fichiers, la heuristique ne se déclenche pas — les alerts sont
  fiables.

## Références

- PR #190 — 367 fichiers, 17 alerts CodeQL flaggées, 0 vraie nouvelle alert
- [CodeQL docs : large diff handling](https://docs.github.com/en/code-security/code-scanning)
- Companion knowledge : `typescript-aliases-tsc-alias-gotcha-20260427.md`
