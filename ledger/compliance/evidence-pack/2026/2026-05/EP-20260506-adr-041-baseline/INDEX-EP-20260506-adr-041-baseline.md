---
id: EP-20260506-adr-041-baseline
title: "ADR-041 R1 Router Posture — Baseline T0 + 30j trajectory plan"
type: evidence-pack
date: 2026-05-06
adr: ADR-041
status: in_progress
window: 2026-05-06 → 2026-06-05
owner: "@fafa"
---

# Evidence Pack — ADR-041 Baseline T0

Suit l'acceptance d'[ADR-041](../../../../decisions/adr/ADR-041-r1-router-posture-empirical-reaffirm.md) (vault PR #178, 2026-05-06).

Pose la baseline empirique T0 (snapshot GSC 28j ending 2026-05-04) et planifie les snapshots T+7/T+14/T+30 jusqu'au 2026-06-05, date de la décision finale 2.A (règle longueur Option 1 vs Option 2).

## Sommaire

| Fichier | Contenu |
|---------|---------|
| [[01-context]] | Périmètre, hypothèses H-2A.1/2/3, garanties méthodo |
| [[02-data-source]] | Pipeline GSC existant + tables/services réutilisés |
| `03-baseline-snapshot.sql` | SQL : Q1 (169 rows JSON) + Q2 (3 rows bucket aggregate) — **CORRIGÉ 2026-05-07 : filtre URL R1 PURE** |
| [[04-trajectory-plan]] | Calendrier T0→T+30, critères décision 2.A, anti-overclaim |
| [[05-bucket-samples-and-smoke]] | A_long n=6 + B_short n=10 + smoke URLs prod |
| [[06-decision-recommendations]] | **Recommandations 2.A (Option 1) + 2.C (cleanup now) empiriquement justifiées** |
| `snapshots/2026-05-06-summary.json` | Snapshot T0 + smoke prod 4/4 + correction R1 PURE |

## Findings T0 (2026-05-06, corrigés 2026-05-07)

### ⚠️ Correction filtre URL — R1 PURE seulement

Le snapshot initial utilisait un filtre `LIKE 'https://www.automecanik.com/pieces/%'` qui agrégeait par erreur les URLs **R8 vehicle-scoped** (`/pieces/{slug}-{pg_id}/{marque}.../{type}.html`) sous le `pg_id` R1. Filtre corrigé via regex ancrée `^.../pieces/[^/]+-(\d+)\.html$`.

### Signal réel R1 PURE

| Bucket | n_slots | n_with_gsc | clicks_28d | impressions_28d | CTR_28d |
|--------|---------|------------|------------|------------------|---------|
| A_long (≥700c)  | 6   | **2**  | **0**  | **5**    | 0% |
| mid (300-699c)  | 31  | 6      | 0      | 177      | 0% |
| B_short (<300c) | 132 | 53     | 2      | 1551     | 0.129% |

→ **Bucket A_long : 5 impressions sur 28j, 0 clicks**. Sample impossible à utiliser même T+30. Trafic R1 PUR ~6.5× inférieur à l'estimation initiale (R8 imputé à tort).

### Smoke prod 2026-05-07 (Playwright auto)

4 URLs réellement indexées testées : 4/4 render OK. Structure DOM riche (H1 + 5 H2 + multi-marques + multi-véhicules + tableaux compat). Le `r1s_micro_seo_block` est **un bloc parmi ~10 sections** rendues. 1 finding cross-cutting : Sentry CSP bloqué (hors scope ADR-041).

### Effets confirmés des sous-décisions

| Sous-décision | État T0 | Source |
|---|---|---|
| 2.B — backfill `safe_table_rows` | ✅ DONE 169/169 (vs 26/169 audit) | monorepo PR #332 merged 2026-05-06 |
| 2.C — cleanup vocab interdit | 🟡 partiel : 10 slots `commander` (vs 13 audit, 3 termes nettoyés par effet de bord 2.B) | execute_sql 2026-05-07 |
| 2.A — règle longueur | ⏳ pending T+30 | observation 30j en cours |

### Globaux R1 T0

- 108/169 slots (63.9%) ont des données GSC sur 28j.
- 61/169 slots (36.1%) sans aucune impression — candidats pour analyse "long tail" séparée.
- 54 clicks total, 11,415 impressions, CTR global = 0.473%.
- Position moyenne pondérée par impressions : variable selon slot (1 à 92, médiane ~30).

## Verdict T0 (revisé 2026-05-07)

Avec la baseline R1 PURE corrigée, **les volumes sont trop faibles pour qu'un A/B test 30j produise un signal exploitable** (bucket A_long = 5 impressions). La data déjà disponible suffit à recommander Option 1 pour 2.A — pas besoin d'attendre T+30 (per `feedback_decision_must_be_signal_proven_not_intuited` : la décision est signal-proven, simplement le signal n'est pas "ranking", c'est "volume insuffisant pour mesurer un effet").

Voir [[06-decision-recommendations]] pour 2.A (Option 1) et 2.C (cleanup now).

## Suivi

Cet evidence-pack est **incrémental** — chaque snapshot T+N ajoute un fichier dans `snapshots/`. T+30 reste utile **comme contrôle anti-régression** après application 2.A/2.C, pas comme critère de décision.

## Self-review verdict: APPROVE
