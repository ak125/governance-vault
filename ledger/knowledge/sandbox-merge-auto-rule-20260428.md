---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: Sandbox auto-merge rule — relaxation per-PR GO sur main (DEV pré-prod)
slug: sandbox-merge-auto-rule-20260428
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-04"
updated_by: "@fafa"
related_adr: []
related_prs: []
related_knowledge:
  - "single-maintainer-merge-pattern"
  - "vault-self-review-workflow-20260504"
status: current
---

# Sandbox auto-merge rule — relaxation per-PR GO sur main (DEV pré-prod)

> Décision opérationnelle 2026-04-28, scope = comportement agent Claude Code sur DEV VPS 46.224.118.55.
> Modifie la politique de demande d'autorisation textuelle pour les merges routiniers vers `main`.
> N'affecte ni le vault ni les déploiements PROD.

## 1. Friction observée

Avant 2026-04-28, l'agent Claude Code suivait la règle `feedback_sandbox_destructive_actions` (memory locale, rev 2026-04-27) qui imposait un GO textuel **par PR** pour toute action destructive, y compris les merges routiniers vers `main`.

Symptôme typique en fin de session : longs murs façon

> *"PR #167 attend ton GO — push #167 vers merge sur main, ou tu mergeas toi-même et je m'occupe ensuite du tag PROD ? Je n'agis pas avant ton GO explicite."*

…alors que (a) la session entière avait porté sur cette PR, (b) la CI était verte, (c) il n'y avait aucun blocker.

Effet : friction réelle en fin de session, exécution ralentie, mainteneur (single, `@ak125`) frustré de devoir donner un GO sur chaque PR alors qu'il vient lui-même de demander le travail.

## 2. Décision

Le mode auto **kick** uniquement si **(A) OU (B)** :

**(A)** Plan approuvé via `ExitPlanMode` listant explicitement l'action (merge, push, admin-merge).

**(B)** PR ouverte/finie dans la session courante ET **toutes** les 5 conditions ci-dessous :

| # | Condition | Vérif |
|---|---|---|
| 1 | `mergeStateStatus: CLEAN` | `gh pr view --json mergeStateStatus` (ou `UNSTABLE` toléré uniquement si seuls checks rouges = optionnels documentés) |
| 2 | Pas draft | `isDraft: false` |
| 3 | Aucun review thread non résolu | `reviewDecision != CHANGES_REQUESTED`, `reviewThreads.unresolved == 0` |
| 4 | Base à jour | pas de commit sur `main` postérieur au dernier merge-base qui invaliderait les checks |
| 5 | Pas de "wait" récent du user | aucun message session avec "wait", "ne pas merger", "pause", "hold", "attendre", review humaine pending |

**Si une seule condition n'est pas claire → repasser en mode GO textuel par PR (comportement gardé).**

## 3. Périmètre auto vs gardé

### Auto (sans GO textuel par PR)

- `gh pr merge --squash` sur `main` (DEV pré-prod, [deployment.md](https://github.com/ak125/nestjs-remix-monorepo/blob/main/.claude/rules/deployment.md))
- `gh pr merge --admin --squash` sur `main` — **uniquement si CI verte** (single-maintainer ADR-026 P0, cf. [single-maintainer-merge-pattern](single-maintainer-merge-pattern.md))
- `git push --force-with-lease`

**Garde-fou critique :** admin-merge ne sert qu'à passer les CODEOWNERS / required-reviewers. **Jamais** pour bypass un gate CI rouge. Si check CI rouge → STOP, fixer le code, ne pas auto-tamponner.

### Gardé (GO textuel obligatoire, jamais cumulatif)

| Action | Raison |
|---|---|
| `git tag v* && git push --tags` (= PROD, deployment.md) | promote DEV → PROD, GO nominatif obligatoire |
| `git push -f` sans `--force-with-lease` | trop large |
| `gh api PUT .../branches/main/protection` | modif gouvernance, jamais via agent |
| `mcp__supabase__apply_migration` sur projet prod | per-migration approval |
| `git reset --hard` / `git reset --mixed HEAD~N` | besoin GO nominatif sur la branche |
| `--no-verify`, `--no-gpg-sign`, bypass hooks/CI gates | governance non-négociable |
| `update-config` skill (self-modif `settings.json`) | self-modification de l'environnement |

Pas de GO cumulatif sur le périmètre gardé : un GO sur tag v2.1.0 ne couvre pas v2.1.1 ; un GO sur apply migration N ne couvre pas N+1.

## 4. Compatibilité avec les règles existantes

**`feedback_no_autoescalation_after_single_go` (2026-04-22)** reste **stricte** sur tag PROD, apply prod DB successifs, `git reset --hard`, force-push sans lease, branch protection PUT, bypass de CI gates. Elle ne s'applique **plus** aux merges main routiniers couverts par le mode auto. Distinction clé : "passer les CODEOWNERS sur PR clean" (auto OK) vs "auto-tamponner un bypass CI rouge" (interdit).

**`feedback_plan_approved_means_go_to_end` (2026-04-23)** : le plan approuvé reste un trigger valide ; le mode auto en ajoute un second hors-plan.

**`feedback_branch_scope_discipline` (2026-04-20)** : inchangé. Le mode auto ne change pas les règles de création de branche.

## 5. Pourquoi cette relaxation est sûre

1. **5 conditions trigger strictes** : la première non remplie ramène au comportement gardé. Pas de zone grise.
2. **PROD reste cadenassée** : tag PROD + apply DB prod restent par-cible. Le worst-case d'un mauvais merge auto est un revert sur `main` (DEV pré-prod), pas une casse PROD.
3. **CI gates non-négociables** : admin-merge auto ne contourne jamais une CI rouge. Le seul effet est de passer required-reviewers quand le user est seul mainteneur.
4. **Réversibilité** : la règle vit en memory locale (4 fichiers `.claude/projects/.../memory/`). Reverser = un Edit.

## 6. Fichiers memory édités (locaux, non-trackés)

- `feedback_sandbox_destructive_actions.md` réécrit : tableau auto vs gardé, 5 conditions trigger, admin-merge auto **uniquement si CI verte**.
- `feedback_no_autoescalation_after_single_go.md` : section compat ajoutée (PROD/apply prod restent stricts, merges main relaxés).
- `feedback_plan_approved_means_go_to_end.md` : cross-ref vers le second trigger hors-plan.
- `MEMORY.md` : description inline mise à jour avec marqueur "Rev 2026-04-28".

## 7. Test rapide (5 scénarios canon)

| Scénario | Résultat attendu |
|---|---|
| PR #N prête, CI verte, pas draft, pas de thread, session courante | Merge auto via `gh pr merge --squash` |
| `git tag v2.1.0 && git push --tags` (promote PROD) | STOP, demande GO textuel nommant le tag |
| `mcp__supabase__apply_migration` sur projet prod | STOP, GO par migration |
| PR avec CODEOWNERS bloquant + CI verte | Admin-merge auto OK |
| PR avec un check CI rouge | STOP, jamais admin-merge pour bypass |
| PR session, CI verte, mais user a dit "attends, je veux relire" 5 messages plus tôt | STOP (condition trigger #5) |

## 8. Références

- Memory locale révisée : `/home/deploy/.claude/projects/-opt-automecanik-app/memory/feedback_sandbox_destructive_actions.md`
- Pattern lié : [single-maintainer-merge-pattern](single-maintainer-merge-pattern.md)
- Self-review pré-`--admin` (vault scope) : [[vault-self-review-workflow-20260504]]
  ajoute pour les PRs vault Claude-ouvertes une 6ᵉ exigence checklist sémantique
  (8 items) en plus des 5 conditions trigger ci-dessus. Hors scope vault, les 5
  conditions restent suffisantes pour auto-merge (monorepo).
- Règle déploiement monorepo : `nestjs-remix-monorepo/.claude/rules/deployment.md` (push main = DEV, tag = PROD)
