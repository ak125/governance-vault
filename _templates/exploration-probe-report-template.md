---
# ============================================================
# Exploration Probe Report — G10 Exploration Budget (ADR-081)
# ============================================================
# Tout rapport empirique issu d'une probe EXPLORATION_BUDGET
# DOIT respecter ce template.
#
# Path canonique : docs/research/YYYY-MM-DD-<topic>-empirical-report.md
# (dans le monorepo, pas dans le vault — c'est de la recherche
# operationnelle, pas du canon).
# ============================================================

slot: <probe-slug-active>
# Slug du slot EXPLORATION_BUDGET (top-priorities.md).
# Exemple : geo-discovery-probe-2026-05

started_at: YYYY-MM-DD
completed_at: YYYY-MM-DD
duration_days: <N>
# duration_days ≤ 5 (lock G10).

governance_cost_ratio: <0.XX>
# Temps planification/gouvernance / temps execution.
# DOIT etre ≤ 0.20 (lock G10 anti complexity-gravity).

owner: "@<owner>"
status: <success | partial | abandoned>

# Decision matrix output (obligatoire)
decision: <go_product | arbitrage_owner | close>
# go_product : signal fort, ouverture cycle complet brainstorm → spec → plan
# arbitrage_owner : signal moyen, decision humaine necessaire
# close : signal faible, vault doc justifiant

next_action: |
  <Action concrete suivante.>
  <Si go_product : quel cycle complet ouvre, quel scope.>
  <Si arbitrage : qui decide quoi, sur quels criteres.>
  <Si close : 12 semaines avant re-mesure (G9 sunset), quel signal le rouvrirait.>
---

# Probe Report : <Titre humain court>

## Contexte

<Pourquoi cette probe ?>
<Quelle hypothese strategique elle teste ?>
<Quel risque business non-mesure elle leve ?>

## Scope respecte (lock G10)

- [x] ≤ 5 jours-agent total
- [x] Measurement only — aucune nouvelle table prod
- [x] Aucun service NestJS cree
- [x] Aucun admin UI cree
- [x] Aucune migration DB
- [x] Aucune modification R-role / @repo/seo-roles
- [x] Lecture seule des tables existantes
- [x] Output unique = ce rapport markdown

## Methodologie

<Detail reproductible : sampling, sources, pipeline mesure, cross-refs.>
<Inclure les assumptions explicites (ex. pondations sampling, seuils confidence).>
<Lister les ENV vars / APIs externes utilisees.>

### Work breakdown interne (checkpoints logiques, pas slots gouvernance)

<Liste des checkpoints logiques de la probe (B1, B2, B3, ...).>
<Pour chaque checkpoint : input, scope, output, gate.>

## Resultats

### Section <Checkpoint 1>

<Resultats brutes.>
<Sanity checks effectues.>

### Section <Checkpoint 2>

<Resultats analyses.>

### (si applicable) Section <Checkpoint 3 conditional>

<Si checkpoint conditional execute, resultats ici.>
<Sinon, expliquer pourquoi gate non-franchi.>

## Decision matrix appliquee

| Critere | Seuil | Mesure | Decision |
|---|---|---|---|
| <Critere principal> | <Seuil> | <Mesure reelle> | <go / arbitrage / close> |

**Recommandation explicite** : <go_product / arbitrage_owner / close>

**Justification** :

<Pourquoi cette decision ?>
<Quel signal precis la justifie ?>

## Risques identifies (non-corriges en V1)

<Liste des risques observes pendant la probe qui ne sont pas corriges maintenant.>
<Pour chacun : pourquoi pas maintenant + quel evenement le declencherait.>

## Anti-creep verification

- [x] Aucune fuite vers prod (table / service / UI / migration)
- [x] Governance cost ratio ≤ 20%
- [x] 1 rapport unique (pas N rapports partiels)
- [x] Naming scripts respecte la responsabilite

## Cross-refs

- Slot `EXPLORATION_BUDGET` : <slug>
- Plan agent : <path/to/plan>
- ADR-081 (G10 origine)
- (si applicable) Verdict empirique source : VERDICT-YYYY-NNN
- (si decision go_product) Nouveau cycle ouvert : <link spec>

## Closure

- [x] Slot `EXPLORATION_BUDGET` libere (slug deplace historique)
- [x] Session-log entry `app/log.md`
- [x] (si applicable) Verdict empirique cree `ledger/verdicts/`
- [x] (si applicable) Cycle suivant ouvert
