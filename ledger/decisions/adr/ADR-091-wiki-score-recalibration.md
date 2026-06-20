---
id: ADR-091
title: "Recalibrage du confidence_score wiki (vérité > conformité) + activation tiered du gate de régression"
status: proposed
date: "2026-06-20"
decision_date: ""
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: ["ADR-083"]
related_adr: ["ADR-033", "ADR-046", "ADR-059", "ADR-083", "ADR-088"]
related_rules: []
related_incidents: []
version: "1.0.0"
---

# ADR-091 — Recalibrage du confidence_score wiki + activation tiered du gate de régression

## Statut

Proposed.

## Contexte

Le scoring des fiches wiki (`automecanik-wiki/_scripts/compute-confidence-score.py`,
formule §4 de `_meta/quality-gates.md`) **sous-récompense le bon contenu sourcé OE** :

- `source_refs[]` sans champ `confidence` → comptées « medium » (0.6) par défaut, même
  quand les sources sont OE/TecDoc (= high) — incitation perverse déjà signalée par la
  PR #49 « anti-inflation » (report-only).
- titres de sections non canoniques non comptés (matching partiel) ;
- liens externes (sources) non comptés (seuls les `[[wikilinks]]` internes le sont) ;
- bonus diversité raté si une seule famille de sources.

Conséquence mesurée : `disque-de-frein` (83 faits, 64 sources OE) score **0.36** vs seuil
de promotion TIER A **0.84** (ADR-083). Le score reflète la *forme*, pas la *vérité*.

Un gate de comparaison « score-and-compare-before-overwrite » est livré
(`compare-proposal-versions.py`, **report-only**, mergé sur `main` 2026-06-20, PR #60) :
il compare une fiche à sa version git précédente (NEW/IMPROVED/NEUTRAL/REGRESSED) mais
**ne bloque pas** tant que le score ment — sinon il punirait de bonnes fiches.

## Décision

1. **Dériver la confiance des sources** depuis le `source-catalog` (`source_type → max
   confidence`, déjà défini dans `SOURCE_TYPE_TO_MAX_CONFIDENCE`), et **supprimer le défaut
   « medium »**. Prérequis : les `source_refs[]` portent un **slug catalogué** (cataloguer
   les sources OE du scrape).
2. **Exiger des titres de sections canoniques** (template gamme) pour le décompte sections.
3. **Activer le gate de régression en bloquant** (`--fail-on-regression`, tolérance 0.0)
   après recalibrage + **baseline-resync** de tout le corpus (≈14 fiches).
4. **Activer la promotion auto** : seuil `promote.py` **1.01 → 0.80** pour les pièces
   **NON-sécurité** (extends ADR-083) ; les pièces **sécurité** (freinage, direction,
   airbag, suspension) restent **HUMAN_SPOT_CHECK** — invariant déjà gravé
   (`auto_review_wiki_proposal.py`), inchangé.

## Conséquences

- Le score change pour l'ensemble des fiches (≈14) → **baseline-resync obligatoire** (commit
  audité `compute-confidence-score.py --fix` sur le corpus) avant tout passage bloquant.
- Rollout par paliers réversibles : report-only (fait) → observer → resync → bloquant →
  activer promote (non-sécurité).
- Aucune pièce de sécurité n'est publiée sans revue humaine (principe « no auto-approval »).
- N'affecte ni URLs, ni schéma de fiches, ni module payments.

## Alternatives écartées

- Marquer `confidence: high` à la main sur les fiches = bricolage (l'incitation perverse
  que la PR #49 dénonce) → écarté.
- Garder le score tel quel et activer le gate bloquant = punirait le bon contenu OE → écarté.

## Rollout & rollback

- Rollback à tout palier : revert du commit de formule / baseline ; remettre `promote.py`
  à 1.01 (no-op) ; le gate redevient report-only en retirant `--fail-on-regression`.

## Références

- Gate Phase A : `ak125/automecanik-wiki` PR #60 (mergé) — `_scripts/compare-proposal-versions.py`.
- ADR-083 (promotion tiered, seuil dormant activé), ADR-033 (schéma fiches),
  ADR-059 (projection SEO), ADR-088 (gate substance shadow).
  (Relations structurées : voir `related_adr` / `extends` dans le frontmatter.)
