---
type: knowledge
status: canon
created: 2026-05-04
updated: 2026-05-04
tags: [audit, claude-md, agents-md, validator, ci-gate, handoff, session2, partial-coverage]
related-adr: [ADR-012, ADR-015]
related-prs: [nestjs-remix-monorepo#293, nestjs-remix-monorepo#294]
related-knowledge: [audit-claude-md-agents-md-validator-20260503]
related-memory: [feedback_no_hardcoded_infra_in_agentsmd]
verdict: PARTIAL_COVERAGE (P1 en cours, session 2 reprend depuis ce point)
---

# Audit `CLAUDE.md` / `AGENTS.md` — Handoff session 2 (2026-05-04)

> Note de session consignant l'**état exact** du chantier P1 (item §4 de
> [[audit-claude-md-agents-md-validator-20260503]]) au moment de la coupure.
> Doit servir de reprise propre pour la session suivante sans perte de contexte.

---

## 1. Contexte de reprise

Session du 2026-05-03 a livré 5 PRs mergées (cf. doc parent `audit-claude-md-agents-md-validator-20260503.md`) + listé 7 améliorations futures P1→P3.

L'utilisateur a choisi **Option A** (item P1) en début de session 2 (2026-05-04) :
> *« Fix workflow trigger paths-filter (cause : PR #273 a été temporairement BLOCKED) »*

**Découverte en cours d'exécution** : la cause réelle de PR #273 BLOCKED n'était **pas** le paths-filter de `agents-md-validation` (vérifié via `gh api repos/.../branches/main/protection` — ce check **n'est pas** dans la liste des 14 required). C'était le pattern général « **BEHIND status** invalide les checks contre la nouvelle base sha » qui touche **tous** les workflows required path-filtered, pas seulement le nôtre.

Le fix P1 reste néanmoins **pertinent et défensif** : si quelqu'un ajoute `agents-md-validation` aux required checks plus tard, il ne réintroduira pas le piège.

---

## 2. État livré dans la session 2

### 2.1 PR #293 ouverte

**URL** : https://github.com/ak125/nestjs-remix-monorepo/pull/293
**Branche** : `fix/agents-md-validator-always-trigger`
**Commit principal** : `828d0571` (puis merges main → `ae0a5e36` → `18cbb763`)

**Diff initial** : `.github/workflows/agents-md-validation.yml` — retire `paths` filter sur les triggers `pull_request` et `push.main`. Ajoute commentaire d'en-tête justificatif référençant le doc parent.

```diff
 on:
   pull_request:
-    paths:
-      - 'agents/**/AGENTS.md'
-      - '**/CLAUDE.md'
-      - '.claude/rules/**'
-      - 'scripts/agents/**'
-      - '.github/workflows/agents-md-validation.yml'
   push:
     branches:
       - main
-    paths:
-      - 'agents/**/AGENTS.md'
-      - '**/CLAUDE.md'
-      - 'scripts/agents/**'
```

### 2.2 État CI au moment du handoff

- **Total** : 1 fail / 16 pass / 8 skipping (24 checks)
- **Required (14)** : tous PASS lors du dernier run complet — confirmé empiriquement
- **Auto-merge queued** : `gh pr merge 293 --auto --squash --delete-branch` exécuté avec succès (silent return = queued)
- **Le seul fail (`🔍 DEV Safety (Observe)`)** : **NOT REQUIRED** (advisory uniquement, pas dans les 14 required)
- **mergeStateStatus** : oscille entre `BEHIND` / `BLOCKED` / `UNKNOWN` selon les merges concurrents sur main

### 2.3 Auto-validation du fix : ✅ confirmée empiriquement

Le workflow `agents-md-validation` lui-même tourne **sur sa propre PR** (puisqu'on a retiré son paths filter). Le check `Validate AGENTS.md / CLAUDE.md` apparaît bien en `pass` sur PR #293 après les 2 re-runs (post-merge main). C'est le **proof empirique** que le fix fonctionne.

---

## 3. Découverte adjacente : bug GATE-3 sur workflow PR #294

### 3.1 Symptôme

`🔍 DEV Safety (Observe)` step **GATE-3 Runner Blast-Radius** échoue sur PR #293 (et continuera à échouer sur toute PR qui inclut le state actuel de main jusqu'à ce qu'il soit fixé) :

```
❌ CRITICAL: .github/workflows/dependabot-claude-review.yml uses
   pull_request_target with actions/checkout
🚫 GATE-3 FAILED (1 critical issue(s))
```

### 3.2 Cause racine

PR #294 (`feat(ci): auto-merge Dependabot avec review intelligente Claude (P0 dry-run)`)
mergée sur main 2026-05-04 vers ~13h45 UTC a introduit le workflow
`.github/workflows/dependabot-claude-review.yml` qui combine
`pull_request_target` + `actions/checkout` — pattern flagged par GATE-3
comme vulnérabilité d'exfiltration de secrets sur PR forkées.

### 3.3 Statut

- **Pas notre bug** — hérité via merge main dans la branche P1
- **Advisory uniquement** — DEV Safety Observe n'est pas required
- **À reporter à l'auteur de PR #294** — risque réel de leak secrets si Dependabot ou autre fork PR exploite `pull_request_target` avec un checkout du SHA fork
- **Doit faire l'objet d'un ticket / fix séparé** — hors scope P1

### 3.4 Pattern correct attendu

```yaml
on:
  pull_request_target:
    types: [opened, synchronize]

jobs:
  review:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.base.sha }}  # base, pas head fork
          # OU pas de checkout du tout — utiliser uniquement les métadonnées PR
```

---

## 4. Pattern « BEHIND merry-go-round » documenté

Pendant cette session, PR #293 est passée 2 fois en `BEHIND` parce que main a avancé pendant que ses checks tournaient. À chaque fois :

1. Tous les required checks passent sur la branche
2. Quelqu'un d'autre merge une PR sur main
3. GitHub recompute le mergeable state contre la nouvelle base sha
4. Les checks restent "valides" mais "stale base" → `BEHIND`
5. Branch protection refuse le merge tant que BEHIND
6. → faut merger main dans la branche
7. → re-run des checks
8. → goto 1 si encore une autre PR merge entre-temps

**Mitigation appliquée** : `gh pr merge --auto` queue l'auto-merge qui re-essaie automatiquement après chaque update de la branche. C'est ce qui tournait au moment du handoff.

**Mitigation alternative** (si auto-merge ne suffit pas) : admin-merge avec
`--admin --squash`. Mais branch protection a `enforce_admins=false` côté
monorepo (cf. mémoire `branch-protection-main-20260502.md`) — donc
`--admin` fonctionne uniquement sur le vault, pas le monorepo. À vérifier.

---

## 5. À faire en session 3

### 5.1 Vérifier statut final PR #293

```bash
gh pr view 293 --repo ak125/nestjs-remix-monorepo --json state,mergedAt,mergeCommit
```

3 cas possibles :
- **MERGED** ✅ → P1 livré, passer à P2
- **OPEN + auto-merge enabled + green** → laisser l'auto-merge faire son travail (peut prendre temps si main bouge beaucoup)
- **OPEN + stale** → re-update branche manuellement (`git merge origin/main` + push) ou admin-merge si gel acceptable

### 5.2 Ouvrir ticket pour le bug GATE-3 / PR #294

PR séparée à ouvrir dans `ak125/nestjs-remix-monorepo` :
- Branche : `fix/dependabot-claude-review-pr-target-checkout`
- Modif : retirer `actions/checkout` du workflow ou le contraindre à `base.sha` au lieu du fork SHA
- Référence : log GATE-3 du run `25325052019` du 2026-05-04

### 5.3 Continuer le backlog P2 / P3 du doc parent

Items restants (cf. `audit-claude-md-agents-md-validator-20260503.md` §4) :
- **P2** Validateur miroir côté `automecanik-wiki` repo
- **P2** Aligner 3 agents (rag-lead / seo-content / seo-qa) sur sections canoniques (3 WARN actuels → 0 WARN)
- **P3** Cleanup rétroactif IP hardcodées (4 AGENTS.md historiques)
- **P3** `shellcheck` pre-commit local
- **P3** Markdown link-checker
- **P3** Auto-bump submodule pointer

---

## 6. Coverage manifest AEC v1.0.0

```yaml
scope_requested: Item P1 du backlog audit-claude-md-agents-md-validator-20260503
scope_actually_scanned:
  - .github/workflows/agents-md-validation.yml (retire paths filter)
  - branch protection api (vérification empirique : agents-md-validation NOT required)
  - PR #294 .github/workflows/dependabot-claude-review.yml (cause adjacente GATE-3 fail)
files_read_count: 3
excluded_paths: []
unscanned_zones: []
corrections_proposed: 1 (PR #293 retire paths filter)
corrections_applied: 0 (PR ouverte, auto-merge queued, pas encore mergée)
validation_executed:
  - bash scripts/agents/validate-agents-md.sh --self-test → 9/9 PASS
  - YAML syntax valide (python yaml.safe_load)
  - Validate AGENTS.md / CLAUDE.md gate sur PR #293 lui-même → PASS (auto-validation)
  - 16 autres checks PASS sur PR #293
remaining_unknowns:
  - Statut final PR #293 (auto-merge en attente — peut être mergée d'ici la session suivante)
  - Conséquences réelles du bug GATE-3 (DEV Safety Observe n'est qu'advisory)
  - Si admin-merge fonctionne sur monorepo (enforce_admins valeur à confirmer)
final_status: PARTIAL_COVERAGE
```

---

## 7. Référence

- **Doc parent** : [[audit-claude-md-agents-md-validator-20260503]] (vault commit `1967fbc4`)
- **PR #293** : https://github.com/ak125/nestjs-remix-monorepo/pull/293
- **PR #294** (cause adjacente) : https://github.com/ak125/nestjs-remix-monorepo/pull/294
- **Run GATE-3 fail** : https://github.com/ak125/nestjs-remix-monorepo/actions/runs/25325052019
- **Mémoire** : `feedback_no_hardcoded_infra_in_agentsmd.md`, `branch-protection-main-20260502.md`
