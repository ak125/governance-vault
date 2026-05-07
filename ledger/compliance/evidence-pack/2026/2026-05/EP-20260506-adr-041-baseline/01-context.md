# 01 — Contexte

## Pourquoi cet evidence-pack

Suite à l'acceptance d'[ADR-041](../../../../decisions/adr/ADR-041-r1-router-posture-empirical-reaffirm.md) (status `accepted` 2026-05-06, vault PR #178, commit `e676072`), il faut mesurer empiriquement la trajectoire SERP des pages R1 sur ≥30 jours pour qualifier le canon "LIVE" et arbitrer la sous-décision 2.A (règle longueur Option 1 vs Option 2).

Cet evidence-pack pose la **baseline T0** (snapshot 2026-05-06) et planifie les snapshots subséquents (T+7, T+14, T+30) jusqu'au 2026-06-05.

## Périmètre mesuré

- 169 pg_id R1 dans `__seo_r1_gamme_slots` (snapshot audit `audit-r1-coverage.sql` Q1).
- Métriques GSC : `clicks`, `impressions`, `ctr`, `position` agrégés 28j rolling.
- Source : table prod `__seo_gsc_daily` populée par `gsc-daily-fetcher.service.ts` (mod. `seo-monitoring`).
- SA Owner GSC : opérationnel sur `sc-domain:automecanik.com` depuis 2026-05-06 (mémoire `gsc-sa-resolved-20260506`).

## Hypothèses à valider sur 30j

| ID | Hypothèse | Critère décision |
|----|-----------|------------------|
| H-2A.1 | "Bucket A (≥700c, n=6) surperforme Bucket B (<300c, n=8-10)" | Δ CTR ≥ 1pt OU Δ position ≤ -2 sur 28j rolling à T+30 |
| H-2A.2 | "Pages R1 ranking ne dépendent pas de la longueur ≥700c" | Pas de Δ significatif → règle 700c abaissable (Option 1) |
| H-2B | "Backfill `safe_table_rows` (143 slots) augmente CTR" | Mesuré séparément après PR backfill (cible 2026-05-20) |
| H-2C | "Cleanup vocab interdit (13 slots) n'affecte pas le ranking" | Mesuré séparément après PR cleanup (cible 2026-05-13) |

## Garanties méthodologiques

Per [`feedback_seo_methodology_canon_20260506`](../../../../knowledge/feedback_seo_methodology_canon_20260506.md) :

- ⏱ Fenêtre ≥ 30j minimum (volatilité GSC < 7j non significative).
- 🔁 Sample rotatif via URL Inspection (échantillon différent par snapshot pour éviter biais).
- 📊 KPI progressifs (impressions d'abord, CTR ensuite, position en consolidation).
- 🚫 Pas de promesse "100%" — formulation "trajectoire mesurable" only.

## Hors scope

- Modification du code R1 (les sous-décisions 2.A/2.B/2.C ont leurs propres PRs).
- A/B test côté serveur (pas d'expérimentation Optimize / split traffic — observation passive).
- Extension à R6/R8 (focus R1 pur ici).
