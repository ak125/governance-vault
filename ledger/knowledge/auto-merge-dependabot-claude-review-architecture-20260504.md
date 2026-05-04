---
category: knowledge
doc_family: knowledge
source_type: architecture-decision
title: "Auto-merge Dependabot avec review Claude — architecture 4 couches"
slug: auto-merge-dependabot-claude-review-architecture-20260504
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-04"
updated_by: "@fafa"
related_adr:
  - "ADR-028"
related_prs:
  - "ak125/nestjs-remix-monorepo#285"
  - "ak125/nestjs-remix-monorepo#289"
  - "ak125/nestjs-remix-monorepo#294"
related_knowledge: []
status: current
tags:
  - governance
  - ci
  - dependabot
  - auto-merge
  - claude
  - review
  - canon
---

# Auto-merge Dependabot avec review Claude — architecture 4 couches

> Session 2026-05-04. Pendant le déblocage de 5 PRs Dependabot bloquées par
> le check CWV, livraison d'une architecture canonique pour automatiser la
> review et le merge des bumps Dependabot non couverts par les règles
> déterministes existantes. À continuer en nouvelle session pour activation
> P0 dry-run.

## Contexte (déclencheur)

5 PRs Dependabot simultanément bloquées par le check `🔍 CWV Performance Check` (#279, #280, #281, #282, #283). Investigation a révélé deux causes structurelles distinctes :

1. **Bug d'infra CI** : `perf-gates.yml` exigeait `SUPABASE_SERVICE_ROLE_KEY` au boot, alors qu'ADR-028 Option D permet `READ_ONLY=true` ; les secrets Supabase ne sont jamais exposés aux PRs Dependabot (politique GitHub 2021 anti-exfiltration), donc backend crash dès `/health`.
2. **Trigger trop large** : `paths:` du workflow matchait `frontend/**` et `packages/**`, ce qui incluait les `package.json` modifiés par les bumps Dependabot dev-only — déclenchait CWV pour des changements ne pouvant pas affecter le rendu frontend.

Au-delà du fix immédiat, le besoin de fond : automatiser la review et le merge des Dependabot PRs que les règles déterministes existantes (`dependabot-auto-merge.yml` : patches + dev-minor + GH-Actions) ne couvrent pas, **avec review intelligente** plutôt qu'auto-merge à l'aveugle (cf. cas `eslint-config-prettier@10` /flat breaking change qui ne nous concerne pas mais qui aurait été risqué sans inspection du repo).

## Architecture livrée — 4 couches

| Couche | Outil | Scope | Coût | Action |
|---|---|---|---|---|
| **1. Préventif** | `dependabot.yml` groups (3 NEW : storybook / tiptap / vite) | Bumps groupés par écosystème, jamais en pièces détachées | 0 | Une seule PR par famille, pas de mismatch major (résout en amont le cas #280) |
| **2. Déterministe** | `dependabot-auto-merge.yml` (existant, **inchangé**) | Patches + dev-minor + GH-Actions | 0 | Auto-merge sans LLM |
| **3. Intelligent** | `dependabot-claude-review.yml` (NOUVEAU) | Dev-majors + runtime-bumps | ~$0.005/PR (Haiku 4.5) | Review Claude → GO + tous checks verts → auto-merge ; HOLD → label + comment |
| **4. Manuel** | Human review | Runtime-majors (production) | n/a | Claude commente seulement, jamais merge auto (human-in-loop maintenu en P3) |

## Fichiers livrés

| PR monorepo | Sujet | Fichier(s) |
|---|---|---|
| `#285` (`bb7ae4a6`) | READ_ONLY=true + mocks Supabase pour boot CI sans secrets | `.github/workflows/perf-gates.yml` |
| `#289` (`3df35d2b`) | `paths:` strict alignés sur intent réel | `.github/workflows/perf-gates.yml` |
| `#294` (`7ccba35b`) | Workflow review Claude + 3 groupes ecosystem | `.github/workflows/dependabot-claude-review.yml` (NEW) + `.github/dependabot.yml` |

Repo settings :
- `allow_update_branch: true` (activé via `gh api -X PATCH /repos/.../...`) — GitHub auto-update les branches avec auto-merge dès que main avance ; résout les race conditions Dependabot vs main qui avance vite.

## Pourquoi c'est canonique (vs bricolage rejeté)

| Aspect | Bricolage (rejeté) | Canon (adopté) |
|---|---|---|
| Appel API Claude | `curl` + `jq` parser custom dans bash | Action officielle `anthropics/claude-code-action@v1` maintenue upstream |
| Prompt | Maintenu dans script shell custom | Inline dans le YAML, lisible et versionné comme code |
| Pré-check ecosystem | Script `dependabot-ecosystem-check.sh` à maintenir | Réalisé par Claude lui-même + prévenu en amont par `dependabot.yml` groups (déterministe natif) |
| Output structuré | Parser JSON custom + validation schema | `outputs.structured_output` natif via `--json-schema` dans `claude_args` |
| Sécurité `pull_request_target` | `actions/checkout@v4` (combinaison flaggée CRITICAL par GATE-3) | Pas de checkout explicite ; `claude-code-action@v1` gère son sandbox isolé en interne |

## Action manuelle restante (à activer en nouvelle session)

```bash
# 1. Créer le secret API
gh secret set ANTHROPIC_API_KEY --repo ak125/nestjs-remix-monorepo

# 2. Variables repo (kill-switch + dry-run flag)
gh variable set CLAUDE_REVIEW_ENABLED --repo ak125/nestjs-remix-monorepo --body true
gh variable set CLAUDE_REVIEW_DRY_RUN --repo ak125/nestjs-remix-monorepo --body true   # P0 dry-run

# 3. Audit rétroactif sur PRs de référence
#    (rejouer en dry-run ou attendre prochaine fournée Dependabot)
#    Verdicts attendus :
#    - vite-tsconfig-paths 4→6     → GO (no intentional breaking)
#    - storybook 9→10               → HOLD (ecosystem coupling)
#    - eslint-config-prettier 9→10 → GO (legacy config, /flat ne concerne pas)

# 4. Si verdicts alignés, passer en P1 actif
gh variable set CLAUDE_REVIEW_DRY_RUN --body false
```

## Garde-fous explicites

| Garde-fou | Implémentation |
|---|---|
| Kill-switch global | `vars.CLAUDE_REVIEW_ENABLED == 'true'` dans le `if:` du job |
| Mode dry-run | `vars.CLAUDE_REVIEW_DRY_RUN == 'true'` dans le prompt Claude |
| Anti-fork | `head.repo.full_name == github.repository` |
| Anti-loop | label `dependabot-hold` skip à la prochaine sync |
| Concurrency | `claude-review-${PR}` cancel-in-progress |
| Timeout | 5 min |
| Runtime-major never auto | logique explicite dans le prompt — Claude commente seulement |
| Modèle | `claude-haiku-4-5-20251001` — ~$0.005/PR, 5-7 PRs/mois → < $0.20/mois |

## Effets transverses observés (preuve empirique)

- **Groupes ecosystem fonctionnent immédiatement** : à peine #294 mergée, Dependabot a fermé #279, #282, #283 et créé `#299` (`tiptap-ecosystem` 5 updates groupé) et `#300` (`vite-ecosystem` 3 updates groupé). Le préventif structurel produit son effet dès le cycle suivant.
- **`actions/setup-node 4→6` (#297)** auto-mergée par `dependabot-auto-merge.yml` (règle GH-Actions, déterministe, sans intervention Claude) — preuve que la séparation de scope entre couche 2 et couche 3 est bien étanche.

## Plan de mise en production en 4 phases

| Phase | Durée | Scope traité par Claude | Action sur GO | Critère de sortie |
|---|---|---|---|---|
| **P0 dry-run** | 2 sem (~4-5 PRs) | dev-major | Comment verdict, **aucun merge** | 100% verdicts alignés avec décision humaine |
| **P1 actif limité** | 4 sem | dev-major | Auto-merge si GO + checks verts | 0 false-GO ; HOLD rate ≤ 40% |
| **P2 étendu** | si P1 stable | + runtime-minor | Auto-merge si GO | mêmes critères |
| **P3 max** | si P2 stable | + runtime-major | **Comment seulement, jamais merge** | n/a (palier final, human-in-loop maintenu) |

## Critères de succès empiriques (à évaluer fin P1, ~6 sem)

- ≥ 80% des PRs Dependabot non-déterministes traitées sans intervention humaine
- 0 incident production traçable à un bump auto-mergé par Claude
- Latence workflow p95 < 60s
- Coût Anthropic mensuel < $1
- HOLD rate sain (10–60%)

## Références

- ADR-028 Option D — `READ_ONLY=true` permet boot Nest sans `SERVICE_ROLE_KEY` (PRs monorepo #246, #274, #276, #277)
- Action officielle Anthropic : https://github.com/anthropics/claude-code-action
- Plan exécution complet (session) : `/home/deploy/.claude/plans/aller-au-contenu-utiliser-dapper-rose.md`
- Mémoire `feedback_no_bricolage_align_existing_contract.md` (créée pendant la session) — quand un check CI fail à cause d'une config CI obsolète vs un contrat backend déjà refactoré, fix le CI pour adopter le contrat (pas admin-merge, pas de skip ciblé)
