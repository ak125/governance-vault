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
| `03-baseline-snapshot.sql` | SQL : Q1 (169 rows JSON) + Q2 (3 rows bucket aggregate) |
| [[04-trajectory-plan]] | Calendrier T0→T+30, critères décision 2.A, anti-overclaim |
| [[05-bucket-samples-and-smoke]] | A_long n=6 + B_short n=10 + smoke URLs prod |
| `snapshots/2026-05-06-summary.json` | Snapshot T0 capturé via Supabase MCP `execute_sql` |

## Findings T0 (2026-05-06)

### Signal directionnel A vs B (low-confidence)

| Bucket | n_slots | n_with_gsc | clicks_28d | impressions_28d | CTR_28d |
|--------|---------|------------|------------|------------------|---------|
| A_long (≥700c)  | 6   | 4   | 6   | 484    | **1.240%** |
| mid (300-699c)  | 31  | 14  | 8   | 1499   | 0.534% |
| B_short (<300c) | 132 | 90  | 40  | 9432   | 0.424% |

→ **CTR(A) ~2.93x CTR(B)** et **Δ +0.82pt**, mais sample size A_long avec data GSC n'est que de 4 — confiance statistique faible. À confirmer T+30.

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

## Verdict T0

**Trajectoire en cours, pas de canon LIVE déclarable**. Per [`feedback_canon_rule_live_iff_adr_accepted`](../../../../knowledge/feedback_canon_rule_live_iff_adr_accepted.md) le canon ADR-041 status=accepted permet l'usage du canon ; le qualificatif "LIVE" requiert le signal stable T+30 (per `feedback_decision_must_be_signal_proven_not_intuited`).

## Suivi

Cet evidence-pack est **incrémental** — chaque snapshot T+N ajoute un fichier dans `snapshots/`. Le verdict 2.A final sera consigné dans `snapshots/2026-06-05-decision.md` signé @fafa.

## Self-review verdict: APPROVE
