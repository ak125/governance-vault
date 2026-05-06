---
id: ADR-041
title: "R1 Router Posture Reaffirmed — empirical validation supersedes hypothesis-driven commerce-safe pivot"
status: accepted
date: 2026-05-06
decision_date: 2026-05-06
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["R-SEO-01", "R-SEO-02"]
related_incidents: []
related_adr: ["ADR-016", "ADR-024", "ADR-040"]
implementation_status: in_progress
---

# ADR-041: R1 Router Posture — Empirical Reaffirm

## Contexte

Le 2026-05-06, un audit externe a proposé un pivot stratégique du rôle
`R1_ROUTER` vers une variante hybride `R1_ROUTER_COMMERCE_SAFE` autorisant
des micro-signaux catalogue (livraison, marques, prix) au-dessus de la
posture actuelle "router pur" définie par
[`workspaces/seo-batch/.claude/agents/r1-router-validator.md`](../../../monorepo/workspaces/seo-batch/.claude/agents/r1-router-validator.md).

Trois hypothèses sous-tendaient le plan d'audit :
1. **H1** : "Slots seedés au split R1/R6 (2026-03-17) jamais ré-enrichis,
   `r1s_gatekeeper_score` souvent NULL → couverture QA inconnue."
2. **H2** : "Drift transactionnel massif du contenu R1 produit
   (`micro_seo_block` contient prix/stock/panier/livraison/promo)."
3. **H3** : "Pages R1 trop courtes pour ranker (~150 mots) → besoin
   d'enrichissement substantiel et/ou pivot commerce."

Le plan recommandait 5 requêtes SQL pour mesurer ces hypothèses. Les
queries ont été versionnées dans
[`scripts/seo/audit-r1-coverage.sql`](../../../monorepo/scripts/seo/audit-r1-coverage.sql)
(monorepo PR #326) et exécutées contre Supabase prod le 2026-05-06.

## Mesures empiriques (snapshot 2026-05-06)

Source : `__seo_r1_gamme_slots` (169 lignes) + `pieces_gamme` +
`__cross_gamme_car_new`.

### Q1 — Coverage globale R1

| Métrique | Valeur | Verdict H1 |
|----------|--------|------------|
| total_slots | 169 | — |
| has_micro_seo / compat / equip / cross_sell | 169 / 169 (100%) | — |
| has_safe_table_rows | 26 / 169 (**15.4%**) | gap inattendu |
| missing_gatekeeper (NULL score) | **0 / 169** | **H1 réfutée** |
| low_score (<65) | **0 / 169** | **H1 réfutée** |
| passable (≥65) | **169 / 169 (100%)** | gate working |

### Q3 — Drift transactionnel dans `r1s_micro_seo_block`

| Mot interdit | Occurrences |
|--------------|-------------|
| `commander` | 10 |
| `stock` (\\b...\\b) | 3 |
| `livraison` | 3 |
| `paiement` | 3 |
| `prix` (\\b...\\b) | 0 |
| `promo` | 0 |
| `panier` | 0 |
| `acheter` | 0 |

**Total avec ≥1 vocab interdit : 13 / 169 (7.7%)**. H2 partiellement vraie
mais quantitativement marginale — pas un drift "massif".

### Q4 — Distribution longueur `r1s_micro_seo_block`

| Bucket | Count | % |
|--------|-------|---|
| NULL | 0 | 0% |
| <300 chars | 132 | **78.1%** |
| 300-699 chars (sous le min de la règle) | 31 | 18.3% |
| ≥700 chars (rule de `r1-content-batch.md`) | 6 | **3.5%** |
| avg / min / max | 221 / 141 / 1250 | — |

**96.5% des slots échouent la règle "Min 700 chars"** définie dans
`r1-content-batch.md` rule #6. La règle est de facto fictionnelle —
soit elle est abandonnée silencieusement, soit la production est
fortement sous-enrichie.

### Q5 — Maillage R1 → R8 via `__cross_gamme_car_new`

Top 5 par couverture motorisations :

| pg_alias | modeles | marques | motorisations |
|----------|---------|---------|---------------|
| filtre-d-habitacle | 564 | 28 | **8 094** |
| bras-de-suspension | 412 | 25 | 6 416 |
| compresseur-de-climatisation | 445 | 25 | 6 163 |
| condenseur-de-climatisation | 404 | 22 | 5 893 |
| rotule-de-direction | 385 | 24 | 5 849 |

Les 30 premières gammes ont 3 000 - 8 094 motorisations compatibles —
H3 confirme un levier R1 → R8 sous-exploité (cross-link goldmine).

## Décision

### 1. Posture R1_ROUTER strict reaffirmée

`R1_ROUTER` reste **router pur** au sens de `r1-router-validator.md`
section ROLE PURITY (L34-43). Le pivot vers `R1_ROUTER_COMMERCE_SAFE`
proposé par l'audit est **rejeté** sur les bases suivantes :

- H1 (gatekeeper non-couvert) **réfutée empiriquement** : 100% des
  slots passent le gate, 0 NULL, 0 low_score. L'argument "QA inconnue"
  ne tient pas — la QA fonctionne.
- H2 (drift transactionnel) **quantitativement marginale** : 7.7%
  vs hypothèse "massive". Une PR ciblée nettoie 13 slots ; pas besoin
  de pivot stratégique pour absorber 13 anomalies.
- Le canon `r1-router-validator.md` (FORBIDDEN section L54-77) est
  **discipliné, prouvé fonctionnel** par les données. Le drift résiduel
  vient de templates legacy, pas d'un défaut de canon.

### 2. Trois corrections empiriquement justifiées (pas de pivot)

Les données révèlent **trois écarts actionnables** distincts du pivot
proposé par l'audit :

#### Décision 2.A — Aligner la règle longueur sur la production

La règle "Min 700 chars" de [`r1-content-batch.md`](../../../monorepo/workspaces/seo-batch/.claude/agents/r1-content-batch.md) rule #6
est échouée par 96.5% des slots (avg 221 chars). **Décider** :

- **Option 1 (préférée)** : abaisser la règle à `Min 200 chars, Max 800 chars`.
  Cohérent avec la posture "router court" et la production réelle.
- **Option 2** : maintenir 700 chars et ré-enrichir 163/169 slots.
  Coût élevé pour bénéfice SEO incertain (router ≠ article long).

L'arbitrage entre 1 et 2 doit être basé sur GSC CTR / SERP visibility
test sur un échantillon — **pas sur intuition rédactionnelle**.

#### Décision 2.B — Prioriser couverture `safe_table_rows`

Section R1_S6_SAFE_TABLE est populée à **15.4%** (26/169) vs 100% pour
les 4 autres sections. C'est le **vrai gap de couverture** que l'audit
a manqué. `safe_table_rows` est consommé par
[`SafeCompatTable.tsx`](../../../monorepo/frontend/app/components/pieces/SafeCompatTable.tsx)
(rendering frontend) et porte la valeur "vérifications compatibilité
acheteur" du router.

**Action** : enrichir 143 slots manquants via batch r1-content-batch
mode `batch 50` × 3 itérations.

#### Décision 2.C — Cleanup ciblé des 13 slots avec vocab interdit

13 slots contiennent `commander`, `stock`, `livraison` ou `paiement`
en violation de `r1-router-validator.md` FORBIDDEN. Cleanup ciblé via
script SQL UPDATE one-shot ou re-génération via r1-content-batch sur
ces 13 pg_id. Pas un pivot.

### 3. Pas de pivot vers R1_ROUTER_COMMERCE_SAFE

**Rejeté.** Les justifications :

- **Audit hypotheses partiellement réfutées** (H1 réfutée, H2 marginale).
- **Le canon fonctionne** (gate à 100%, validator clair).
- **Les vrais leviers SERP** (longueur fiction + safe_table gap +
  cross-link maillage) sont absorbables dans la posture strict actuelle.
- Un pivot introduirait une **3e identité R1** (router pur, batch
  transactionnel legacy, commerce-safe) — combine governance complexity
  pour gain incertain.

## Conséquences

### Positives

- Discipline canon préservée. Pas de fork de rôle, pas de duplicate
  validator, pas de migration DB.
- Actions empiriquement priorisées (2.A/2.B/2.C) — chacune adressable
  dans une PR ≤100 lignes.
- L'artifact `audit-r1-coverage.sql` permet de re-mesurer la trajectoire
  après chaque action — feedback loop empirique.

### Négatives

- 2.A demande un test A/B SERP pour trancher Option 1 vs Option 2 —
  délai de mesure (~30 jours minimum pour signal GSC stable).
- 2.B nécessite ré-exécution batch sur 143 slots — coût compute
  Anthropic API ~30 min de batch + review.

### Risques résiduels

- Si une nouvelle vague de production R1 introduit > 10% drift
  transactionnel, la posture strict aura besoin d'un guard CI
  (ast-grep pattern sur `r1s_micro_seo_block`) — hors scope ADR-041,
  à proposer en ADR-041-followup si signal.

## Mise en œuvre

| Étape | Owner | Livrable | Cible |
|-------|-------|----------|-------|
| 2.A — A/B test règle longueur | @fafa + SEO | Décision Option 1/2 + update `r1-content-batch.md` rule #6 | 2026-06-15 |
| 2.B — Backfill safe_table | r1-content-batch agent | 143 slots enrichis | 2026-05-20 |
| 2.C — Cleanup 13 slots drift | UPDATE SQL ou agent re-run | 0 slot avec vocab interdit | 2026-05-13 |
| Re-mesure | `audit-r1-coverage.sql` | Snapshot avant/après | T+1 chaque action |

## Références

- Audit externe : sans signature, présenté 2026-05-06 (verifier-premier-constat-atomic-turtle session).
- Plan de vérification : `~/.claude/plans/verifier-premier-constat-atomic-turtle.md` rev 2.
- Données : `scripts/seo/audit-r1-coverage.sql` (monorepo PR #326), snapshot 2026-05-06.
- Canon validator : `workspaces/seo-batch/.claude/agents/r1-router-validator.md`.
- Mémoires associées :
  - `feedback_audit_hypotheses_must_be_data_validated.md`
  - `feedback_decision_must_be_signal_proven_not_intuited.md`
  - `feedback_canon_rule_live_iff_adr_accepted.md`
- ADR liés :
  - ADR-040 : SEO Roles Canon R0..R8 TS-side only (cadre canon)
  - ADR-024 : R1 Gamme Page Data — matview persistence (proposed, parité ADR-016)
  - ADR-016 : Vehicle Page Data — persistance par matérialisation
