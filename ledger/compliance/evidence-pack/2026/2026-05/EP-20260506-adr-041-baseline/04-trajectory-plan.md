# 04 — Trajectory plan T0 → T+30

## Calendrier de mesure

| Snapshot | Date | Action | Owner |
|----------|------|--------|-------|
| T0 | 2026-05-06 | Baseline capturée — `snapshots/2026-05-06-summary.json` | Claude (cette PR) |
| T+7 | 2026-05-13 | Re-run `03-baseline-snapshot.sql` Q1+Q2 + `audit-r1-coverage.sql` Q1+Q3+Q4 — capturer `snapshots/2026-05-13-{summary,audit}.json` | @fafa ou agent cron |
| T+14 | 2026-05-20 | Idem + tag corrélation avec PR backfill 2.B (déjà DONE 2026-05-06) | idem |
| T+30 | 2026-06-05 | **Décision 2.A** — comparer Δ CTR / Δ position bucket A vs B vs T0 | @fafa |

## Critères de décision pour 2.A à T+30

Per [`feedback_decision_must_be_signal_proven_not_intuited`](../../../../knowledge/feedback_decision_must_be_signal_proven_not_intuited.md), pas de décision sur intuition.

| Signal observé T+30 vs T0 | Décision 2.A |
|---------------------------|--------------|
| Δ CTR(A) − Δ CTR(B) ≥ +1pt **et** Δ position(A) − Δ position(B) ≤ −2 | **Option 2** : maintenir règle ≥700c, re-enrich 132+31 slots <700c via `r1-content-batch` |
| |Δ CTR(A) − Δ CTR(B)| < 0.5pt **ou** position(A) ≈ position(B) ± 1 | **Option 1** : abaisser règle à `Min 200, Max 800` (cohérent avec posture router court ADR-041) |
| Cas intermédiaire | Étendre fenêtre à T+60 (per `risque W2` du plan) |

Where `Δ X = X_t30 − X_t0` per bucket.

## Considérations méthodologiques

- **Volatilité GSC** : positions <7j non significatives. T+30 est le minimum acceptable (per ADR-041 §Conséquences).
- **Sample size A_long** : seulement 4/6 slots ont GSC data à T0. Si ≤2 ont des impressions à T+30, conclusion impossible — passer à T+60 ou élargir bucket A à `>=600c`.
- **Confounders** :
  - Backfill 2.B (`r1s_safe_table_rows`) DONE 2026-05-06 → effet sur tous les slots, pas un confondant entre A/B (uniforme).
  - 2.C cleanup vocab interdit `commander` (10 slots restants) : à exécuter avant T+30 OU exclure ces 10 slots de l'analyse.

## Garde anti-overclaim

Per [`feedback_no_overclaim_security_words`](../../../../knowledge/feedback_no_overclaim_security_words.md) :

- ❌ Ne PAS dire "ADR-041 LIVE 100%" même si signal positif T+30. Dire "ADR-041 trajectoire validée empiriquement à T+30j sur métrique X".
- ❌ Ne PAS extrapoler au-delà de la fenêtre mesurée.
- ✅ Documenter le sample size + variance dans chaque snapshot.

## Snapshot file format convention

```
snapshots/
  2026-05-06-summary.json    ← T0 baseline (cette PR)
  2026-05-13-summary.json    ← T+7
  2026-05-13-audit.json      ← Re-run audit-r1-coverage.sql à T+7
  2026-05-20-summary.json    ← T+14
  2026-05-20-audit.json
  2026-06-05-summary.json    ← T+30 (décision 2.A)
  2026-06-05-audit.json
  2026-06-05-decision.md     ← Synthèse + verdict 2.A signed @fafa
```
