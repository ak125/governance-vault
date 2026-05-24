---
id: ADR-081
title: "Doctrine Agility Amendments — Sunset Clause + Exploration Budget"
status: proposed
date: 2026-05-24
decision_date: 2026-05-24
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: [rules-governance-process]
extends: [ADR-013]
related_adr: [ADR-013, ADR-058]
related_rules: [rules-governance-process, rules-engineering-quality]
related_incidents: []
reviewed_by: "@fafa"
---

# ADR-081 : Doctrine Agility Amendments — Sunset Clause + Exploration Budget

## Contexte

La doctrine canon actuelle (`top-priorities.md` 05-23 : `TOP`, `DO_NOT_START`, `ACTIVE_INCIDENTS`, `STRUCTURAL_CONSTRAINTS` + verdict empirique `conversion_funnel` 05-20 PR #652) **produit les bons garde-fous** mais souffre de **3 gaps structurels** identifiés lors d'un challenge stratégique (session brainstorm 2026-05-24, brief utilisateur GEO/AI visibility marché 2026) :

1. **Aucune sunset clause sur les verdicts empiriques** — un verdict mesuré une fois (ex. `conversion_funnel = 0.17%` PR #652) devient permanent et bloque par effet de cliquet tous les `DO_NOT_START` qu'il justifie. Risque : doctrine devient dogme, path-dependency garantie, angles morts paradigmatiques (ex. shift GEO 2026) non-instrumentés.

2. **Aucun budget exploration alloué** — toute divergence stratégique exige PR vault + débat de cadrage (frottement social élevé). Conséquence observée : 11 rounds de brainstorm pour décider d'investir 5 jours-agent dans un probe empirique. Le coût de gouvernance d'une exploration > coût d'exécution = anti-pattern (cf. `complexity-gravity` ci-dessous).

3. **Asymétrie de preuve** — démarrer du neuf exige preuve empirique forte ; continuer l'existant n'exige aucune preuve continue. Le canal SEO classique reste autorisé sans re-validation alors que le verdict 0.17% conversion qui le justifie pourrait avoir évolué.

Ces gaps ne sont pas théoriques. Le verdict 05-20 a été mesuré 4 jours avant que le funnel soit instrumenté (#676) ; sans sunset auto, il continuera à justifier des décisions stratégiques indéfiniment. Et chaque trimestre sans validation marché aveugle augmente le risque d'angle mort.

## Décision

**Amender la doctrine canon avec 2 amendements (AM-1, AM-2) gravés dans `rules-governance-process.md` comme G9 et G10.** Un troisième amendement initialement envisagé (AM-3 Reality Audit trimestriel) est **explicitement retiré** par anti-pattern `complexity-gravity` : prématuré sans plusieurs probes et baselines accumulés ; ré-introduire seulement quand le besoin se manifeste empiriquement.

### AM-1 — Sunset Clause sur les verdicts empiriques (devient G9)

**Règle canonique** :

> Tout verdict empirique cité comme justification d'un `DO_NOT_START`, d'un pivot stratégique ou d'une priorité `TOP` **expire 12 semaines après sa date de mesure**, sauf renouvellement explicite par ré-instrumentation et nouveau commit verdict.

**Implémentation** :

1. **Header YAML obligatoire** dans tout fichier verdict empirique (`governance-vault/ledger/verdicts/YYYY-MM-DD-<topic>.md`) :
   ```yaml
   ---
   id: VERDICT-2026-001
   metric: conversion_funnel_organic
   value: 0.0017
   measured_at: 2026-05-20
   expires_at: 2026-08-12   # measured_at + 12 weeks
   methodology: "GA4 events filter ?utm_medium=organic + funnel #676 cross-ref over 28d"
   pr_ref: 652
   blocks_until_expiry: [r5-diagnostic-engine, new-seo-platform, new-meta-architecture-adr]
   ---
   ```

2. **Verdict expiré non-renouvelé → escalation auto** : les `DO_NOT_START` qu'il bloque passent de `blocked` à `OPEN_FOR_REVIEW` automatiquement. Implémentation : script `scripts/governance/check-verdict-expirations.sh` lancé par cron weekly + alerte vers `__seo_event_log` (réutilise l'observabilité existante, pas de nouveau canary externe — cf. mémoire `feedback_no_external_canary_when_internal_observability_exists.md`).

3. **Précédent immédiat à formaliser** : le verdict `conversion_funnel` (05-20 PR #652) doit recevoir son header YAML rétroactif avec `expires_at: 2026-08-12`. Si à cette date la conversion n'a pas été re-mesurée, les 3 `DO_NOT_START` qu'il bloque deviennent `OPEN_FOR_REVIEW`.

**Pourquoi 12 semaines** : 1 trimestre = cadence naturelle de business review + suffisant pour que les fixes downstream (Commerce-Loop V1 en cours) puissent montrer leur impact, mais pas si long que la doctrine se fossilise. Ajustable par futur amend si pratique empirique le justifie.

### AM-2 — Budget Exploration alloué (devient G10)

**Règle canonique** :

> La doctrine canon réserve un slot machine-readable `EXPLORATION_BUDGET` dans `top-priorities.md` (max 3 entrées, 1 active à la fois). Toute probe stratégique légère (≤ 5 jours-agent total, measurement-only) peut occuper ce slot sans PR vault préalable, à condition de respecter le scope lint + livrer un rapport empirique.

**Implémentation** :

1. **Nouveau slot dans `top-priorities.md`** :
   ```
   ## EXPLORATION_BUDGET
   - <probe-slug-active>
   ```
   Max 3 entrées historiques (rolling), 1 entrée active. Bornes enforced par `scripts/governance/validate-top-priorities.sh` (sister-rule de l'existant validateur).

2. **Scope strict** (enforced par `scripts/governance/validate-exploration-probe.sh` au PR final, **single check**, pas per-checkpoint — anti over-governance creep) :
   - ≤ 5 jours-agent total
   - **Measurement only** : aucune nouvelle table production, aucun service NestJS, aucun admin UI, aucune migration DB, aucune modification R-role / `@repo/seo-roles`
   - Lecture seule sur tables existantes
   - Output unique = 1 rapport markdown final `docs/research/YYYY-MM-DD-<topic>-empirical-report.md` avec chiffrage € ou abandon explicite

3. **Trigger** : owner ou agent senior peut ouvrir une probe sans PR vault. La doctrine pré-autorise dans la bande. Le PR final (à la closure) sera reviewable normalement.

4. **Governance cost ratio ≤ 20%** : invariant non-négociable. Le temps total passé à planifier/gouverner une probe ne doit pas excéder 20% du temps d'exécution. Test simple au démarrage : "le plan tient sur 1 page A4 ? oui = ratio OK, non = simplifier." Au-delà = signal `complexity-gravity` (cf. anti-patterns G10.X ci-dessous).

5. **Anti-patterns explicites de la probe (anti-creep)** :
   - 3 slots séparés par sous-checkpoint = sur-gouvernance (utiliser 1 slot, work breakdown interne).
   - 3 rapports partiels = sur-gouvernance (1 rapport final avec sections).
   - Lint AST par sous-checkpoint = sur-gouvernance (single check au PR final).
   - Pré-construire l'extension produit (admin UI, table, service) "au cas où signal positif" = anti-pattern, viole le scope measurement-only.

### AM-3 — RETIRÉ (Reality Audit trimestriel)

Initialement envisagé : audit trimestriel ré-validant que le canal stratégique principal reste optimal. **Retiré par discipline anti-complexity-gravity** : prématuré sans plusieurs probes / baselines / décisions stratégiques contradictoires accumulées. Aujourd'hui = ritualisation prématurée. Ré-introduire seulement quand le besoin se manifeste empiriquement (probable après ≥ 4 cycles AM-2 accumulés sur ≥ 2 canaux distincts).

## Conséquences

**Bénéfices** :
- Doctrine évolutive : verdicts vieillissants n'asphyxient plus la roadmap par cliquet permanent.
- Coût d'exploration stratégique réduit : 11 rounds de débat → 1 slot pré-autorisé pour ≤ 5 jours mesurés.
- Garde-fous intacts : scope `measurement-only` + lint au PR + governance ratio empêchent qu'une probe dérive en mini-produit caché.
- Anti-pattern `complexity-gravity` codifié et applicable à toute future réforme doctrine (méta-protection contre la dérive de cette ADR elle-même).
- Premier usage = probe GEO empirique (slot `geo-discovery-probe-2026-05`) en parallèle de ce vault PR (cf. plan associé `utiliser-superpower-le-joyful-shamir.md`).

**Coûts / limitations** :
- 1 fichier verdict par mesure (header YAML obligatoire) : friction documentation marginale, mais traçabilité gagnée.
- Cron weekly + script `check-verdict-expirations.sh` à maintenir : trivial (1 fichier, ~30 lignes shell).
- Possibilité qu'un verdict expiré débloque un `DO_NOT_START` qui aurait dû rester bloqué : risque mitigé car le passage est `blocked` → `OPEN_FOR_REVIEW`, pas `OPEN_FOR_REVIEW` → automatically `TOP`. Le re-débat est requis avant action.

**Risques explicitement traités** :
- Sur-gouvernance par cette ADR elle-même → AM-3 retiré, ratio ≤ 20% gravé, anti-patterns explicites G10.X.
- Verdict expiré silencieusement → escalation auto via `__seo_event_log` (observabilité existante).
- Probe qui dérive en produit caché → scope `measurement-only` + `validate-exploration-probe.sh` au PR final.

## Anti-patterns canonisés (méta)

| Anti-pattern | Garde |
|---|---|
| Verdict empirique cité ad vitam aeternam | AM-1 sunset 12 semaines + escalation auto |
| Toute exploration exige PR vault préalable | AM-2 slot pré-autorisé `EXPLORATION_BUDGET` |
| Probe qui devient produit caché | Scope `measurement-only` + lint final |
| Multiplication des amendements gouvernance | `complexity-gravity` codifié, AM-3 retiré comme précédent |
| Ratio gouvernance > exécution sur une probe | Test "tient sur 1 page A4" + ratio ≤ 20% |

## Cross-refs

- **Étend** : [[ADR-013-agent-lifecycle-governance|ADR-013]] (canon SoT, signed G3, hash-locked mirrors).
- **Amende** : [[rules-governance-process]] (ajout G9 Sunset Clause + G10 Exploration Budget).
- **Cohérence** : [[ADR-058-repository-control-plane|ADR-058]] (Control Plane L1/L2/L3 reste inchangé — cette ADR ajoute un layer de méta-gouvernance temporelle au-dessus, pas un 4ᵉ layer Control Plane).
- **Précédent verdict à formaliser** : `conversion_funnel` (05-20 PR #652) → header YAML rétroactif `expires_at: 2026-08-12`.
- **Premier usage AM-2** : probe `geo-discovery-probe-2026-05` (work breakdown B1 capture / B2 operational fulfillment overlay / B3 wiki extraction conditional) — voir plan agent `utiliser-superpower-le-joyful-shamir.md`.

## Files livrés par cette ADR (dans la PR vault)

| Fichier | Action |
|---|---|
| `ledger/decisions/adr/ADR-081-doctrine-agility-amendments.md` | NEW (ce fichier, signé G3) |
| `ledger/rules/rules-governance-process.md` | AMEND (ajout G9 Sunset Clause + G10 Exploration Budget) |
| `ledger/policies/exploration-budget.md` | NEW (exec contract détaillé, scope strict, kill-switches, anti-creep) |
| `_templates/empirical-verdict-header.md` | NEW (header YAML obligatoire AM-1) |
| `_templates/exploration-probe-report-template.md` | NEW (template rapport AM-2) |

## Suivi monorepo (PR séparé post-merge vault)

| Fichier monorepo | Action |
|---|---|
| `app/.claude/top-priorities.md` | AMEND (ajout section `EXPLORATION_BUDGET`, max 3 entrées) |
| `app/.claude/canon-mirrors/exploration-budget.md` | AUTO-GENERATED (sync depuis vault, hash-locked) |
| `app/scripts/governance/validate-exploration-probe.sh` | NEW (lint scope probe, single check au PR) |
| `app/scripts/governance/check-verdict-expirations.sh` | NEW (cron weekly, escalation `__seo_event_log`) |
| `app/.github/workflows/governance-checks.yml` | AMEND (call validate-exploration-probe.sh) |

Self-review verdict: APPROVE
