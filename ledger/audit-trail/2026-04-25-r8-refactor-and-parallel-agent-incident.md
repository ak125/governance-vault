---
type: audit-trail
date: 2026-04-25
session: r8-route-refactor-phases-1-2b
related_pr:
  - "ak125/nestjs-remix-monorepo#126"
  - "ak125/nestjs-remix-monorepo#140"
  - "ak125/nestjs-remix-monorepo#173"
related_rules: ["G2-zero-orphelin"]
proposed_rules: ["R-AGENT-01-isolation"]
status: closed
---

# Audit Trail: R8 vehicle route refactor + parallel-agent interference incident

## Synthèse R8 refactor

Décomposition progressive du fichier monolithique `frontend/app/routes/constructeurs.$brand.$model.$type.tsx` (2020 lignes) en modules + sous-composants par `data-section`. Pure extraction mécanique, **zéro changement de comportement** : 301/410/503, canonicalisation, remap TecDoc ≥100K, `noindex` 60000-83456 préservés.

| PR | Phase | Contenu | Lignes route | Cumul |
|---|---|---|---|---|
| [#126](https://github.com/ak125/nestjs-remix-monorepo/pull/126) | 1 | Types + transform + schema + constants | 2020 → 1559 | −23% |
| [#140](https://github.com/ak125/nestjs-remix-monorepo/pull/140) | 2a | Breadcrumb + Hero | 1559 → 1464 | −28% |
| [#173](https://github.com/ak125/nestjs-remix-monorepo/pull/173) | 2b | 5 sections JSX pures (SeoIntro, R8Enriched, AntiErrors, Howto, Trust) | 1464 → 1258 | **−38%** |

**Résultat final : 7 sections sur 13 extraites, 762 lignes retirées.** Architecture stable dans `frontend/app/components/vehicle/r8/` : 4 modules + barrel + 7 sous-composants.

Détail technique : voir descriptions des PR GitHub (commit messages + bodies).

## Décision Phase 2c (non livrée)

Phase 2c (S_BESTSELLERS + S_SAFE_TABLE) **abandonnée** par décision utilisateur après 3-4 tentatives perdues à cause d'interférence agent parallèle (cf. section suivante). Les 6 sections restantes (S_IDENTITY, S_FAST_ACCESS, S_CATALOG, S_BESTSELLERS, S_SAFE_TABLE, S_FAQ) **restent inline dans la route**. Cost/benefit défavorable au-delà de 38% dans cet environnement.

## Incident: parallel-agent interference

### Pattern observé

Au cours de la session, **3 à 4 tentatives Phase 2c successives ont été invalidées** par une autre instance Claude Code travaillant simultanément sur le même working tree `/opt/automecanik/app`.

Séquence reproductible :

1. Création de branche locale (ex. `refactor/r8-sections-phase2c`)
2. Édition de fichiers en cours
3. **Autre agent** : `git checkout` vers une autre branche dans le même working tree
4. Mes éditions perdues (working tree écrasé) ou index marqué unmerged
5. Reprise impossible sans repartir de zéro

Reflog révélateur d'une fenêtre de 3 minutes :

```
17:13:23  feat/seo-kw-vehicle-extract-rpc → refactor/r8-vehicle-sections-phase2
17:14:35  reset HEAD
17:14:36  refactor/r8-vehicle-sections-phase2 → fix/r8-vehicle-html-links-f5
17:14:36  reset + rebase pick + rebase finish
17:14:37  fix/r8-vehicle-html-links-f5 → main
```

### Causes

- Working tree partagé entre sessions Claude Code concurrentes
- Aucune isolation de branche par session
- Aucun lock ni détection de concurrence
- Stashes accumulés (9+ pendant la session) signe d'un environnement chaotique

### Impact

- **3-4 tentatives perdues** sur Phase 2c (~30 min de travail effectif)
- Index Git laissé en état unmerged orphelin (sans `MERGE_HEAD`)
- Mes commits Phase 2 ont survécu uniquement parce qu'ils avaient été push vers GitHub avant l'intrusion suivante
- Confiance dans l'environnement dégradée : besoin de vérifier l'état entre chaque commande

### Mitigation appliquée pendant la session

- Backup systématique des nouveaux composants vers `/tmp/r8-phase2b-backup/sections/`
- Vérification `git branch --show-current` entre chaque opération
- Refus de tout `git merge --abort` ou `git reset --hard` sans validation utilisateur (préserve le travail de l'autre agent)

## Recommandation gouvernance

### Règle proposée: R-AGENT-01 (isolation worktree)

> **Toute session Claude Code (ou agent SDK) opérant en parallèle d'autres sessions sur le même monorepo doit utiliser un `git worktree` dédié** sous `.worktrees/<session-name>/` ou `/tmp/<session-name>-worktree/`. Le working tree principal `/opt/automecanik/app` reste réservé aux opérations utilisateur ou aux sessions seules.

Justification :
- `git worktree add` est natif et léger
- Le repo utilise déjà ce pattern (`.worktrees/seo-department-phase-0`, `.worktrees/seo-department-phase-1`, `.worktrees/seo-vault-verify-evals`, `/tmp/claude-cleanup-worktree`)
- Élimine 100% des race conditions sur HEAD/index

### Skill suggéré

`/agent-isolation` qui :
1. Détecte les sessions Claude Code actives via fichiers de lock (`.claude/scheduled_tasks.lock` déjà observé)
2. Crée automatiquement un worktree pour la session courante si une autre session est active
3. Bascule le `cwd` Claude vers le worktree

### Lien G2 Zero Orphelin

Cette règle complète G2 (Zero Orphelin) du vault : un agent qui échoue à isoler son worktree produit du **travail orphelin** (commits non poussés perdus, branches locales obsolètes, stashes empilés).

## Coverage Manifest (R12)

- **scope_requested**: refactor R8 vehicle page jusqu'à Phase 2c
- **scope_actually_scanned**: Phase 1 + 2a + 2b livrées et mergées (3 PRs sur main)
- **files_read_count**: route R8 (2020 lignes), 7 sous-composants créés, 4 modules extraits
- **excluded_paths**: 6 sections restantes (S_IDENTITY, S_FAST_ACCESS, S_CATALOG, S_BESTSELLERS, S_SAFE_TABLE, S_FAQ) — non extraites par décision conservatrice
- **unscanned_zones**: aucune (scope refactor délimité ; reste hors-scope par décision explicite)
- **corrections_proposed**: aucune (extraction pure, pas de correctif comportemental)
- **validation_executed**: tsc 0 erreur sur diff, eslint 0 warning, hooks lint-staged + prettier passés, smoke-test post-merge non exécuté
- **remaining_unknowns**: stabilité GSC sur DEV pré-prod J+1 après merge des 3 PRs (à vérifier hors session)
- **final_status**: SCOPE_SCANNED — Phase 1+2a+2b livrées, Phase 2c+ non livrée par décision

## Reliquats à nettoyer (post-session)

- Branche locale `refactor/r8-sections-phase2c` (HEAD = Phase 2b, vide en pratique)
- Branche locale `refactor/r8-vehicle-sections-phase2b-fresh`
- 9+ stashes accumulés (`git stash list`)
- Working tree files Phase 2c sur disque (`BestsellersSection.tsx`, `SafeTableSection.tsx`) — à dropper ou réutiliser si reprise Phase 2c
- `/tmp/r8-phase2b-backup/` (7 fichiers backup)

## Liens

- PR refactor : [#126](https://github.com/ak125/nestjs-remix-monorepo/pull/126), [#140](https://github.com/ak125/nestjs-remix-monorepo/pull/140), [#173](https://github.com/ak125/nestjs-remix-monorepo/pull/173)
- Audit-trail session précédente : [[2026-04-23-seo-kp-alias-maitre-cylindre-frein]]
- Règles vault : G1 (canon), G2 (zero orphelin), G3 (signed commits), G4 (CI read-only)
