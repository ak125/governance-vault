---
id: VERDICT-2026-001
metric: conversion_funnel_organic
value: 0.0017
measured_at: 2026-05-20
expires_at: 2026-08-12
methodology: |
  Reality Audit Business-First Phase 0.5 (run réel site-wide).
  Source : GA4 events filter ?utm_medium=organic + funnel events table (#676)
  cross-référencés sur fenêtre 28 jours glissante (2026-04-22 → 2026-05-20).
  Mesure : 2308 sessions organiques → 4 commandes attribuables.
  Sanity check : benchmark e-commerce auto-parts sain = 1-3% conversion ;
  AutoMecanik mesuré à 0.17% = facteur ~10-15x sous norme.
  Le trafic organique EXISTE (1897 pages indexées GSC) mais ne convertit pas.
pr_ref: 652
blocks_until_expiry:
  - r5-diagnostic-engine
  - new-seo-platform
  - new-meta-architecture-adr
---

# Verdict empirique : conversion_funnel_organic = 0.17%

## Contexte

Reality Audit 2026-05-20 (PR #652 Phase 0.5 du plan Business-First) a mesuré
empiriquement le bottleneck SEO réel d'AutoMecanik avant tout investissement
supplémentaire dans la sophistication acquisition (R5 diagnostic engine,
nouvelle plateforme SEO, nouvelle méta-architecture ADR).

Le verdict mesuré contredit l'hypothèse implicite "plus de SEO → plus de
business" et justifie le pivot stratégique Commerce-Loop V1 décidé le
2026-05-20.

## Méthodologie détaillée

**Source data** :
- GA4 events filter `utm_medium=organic` sur fenêtre 28 jours (2026-04-22 → 2026-05-20)
- Funnel events table (#676 step 4-A, instrumentée 2026-05-21 — mesure 05-20 = baseline pré-instrumentation, biais d'attribution possible mais cohérent avec ordre de grandeur)
- Cross-ref GSC indexation : 1897 pages `index,follow` actives au 2026-05-20

**Calcul** :
- 2308 sessions organiques (28j glissants)
- 4 commandes attribuables au trafic organique (cross-ref order_id × session_id × utm_source)
- Conversion = 4 / 2308 = **0.001733 ≈ 0.17%**

**Sanity check** :
- Benchmark e-commerce auto-parts sain (sources Profound 2025, BigCommerce industry report) : 1.0% - 3.0%
- AutoMecanik 0.17% = facteur ~6× à ~17× sous la norme
- Hypothèse alternative "petit échantillon" : 4/2308 → intervalle confiance 95% [0.05%, 0.45%] → reste très sous-normal même au sup borne

**Caveats** :
- Mesure pré-instrumentation funnel (#676 mergé 2026-05-21) → attribution exacte des leaks pas connue à l'époque du verdict
- Possible sous-estimation conversion (ex. commandes téléphone post-recherche organique non trackées)
- Conversion mobile vs desktop pas segmentée (PR #694 INP fix mobile post-verdict pourrait avoir bougé l'aiguille)

## Résultats

| Métrique | Valeur | Source |
|---|---|---|
| Sessions organiques (28j) | 2 308 | GA4 |
| Commandes attribuables | 4 | Cross-ref order_id × session_id |
| **Conversion** | **0.17%** | calc |
| Pages indexées `index,follow` | 1 897 | GSC sitemap |
| Benchmark industry sain | 1.0%-3.0% | Profound 2025 + BigCommerce |

## Implications stratégiques

Le verdict justifie les 3 `DO_NOT_START` suivants (canon `top-priorities.md` 05-23) :

1. **`r5-diagnostic-engine`** — investir dans un nouveau moteur diagnostic SEO
   pré-conversion ne corrigera pas le funnel (trafic existe déjà, pas la
   conversion).
2. **`new-seo-platform`** — refactor architecture SEO complète sans preuve
   que le canal SEO convertit reproduit le pattern "build first, measure
   after" qui a produit le 0.17%.
3. **`new-meta-architecture-adr`** — toute réforme architecture méta-niveau
   au-dessus du Control Plane existant (ADR-058) sans preuve business
   reproduit le même biais.

Le pivot prioritaire (TOP `top-priorities.md`) devient **Commerce-Loop V1**
(funnel instrumentation #676, retour signals 5B, sticky-buy #647, etc.) qui
attaque directement le bottleneck mesuré (0.17% conversion).

## Sunset / renouvellement (G9 ADR-081)

**Expires_at = 2026-08-12** (84 jours = 12 semaines post-mesure, règle G9).

**Renouvellement valide = ré-instrumentation explicite** :
- Nouveau run Reality Audit identique méthodologie (28j glissants, GA4 organic + funnel cross-ref)
- Mesurer conversion organique mise à jour
- Si conversion ≥ 1.0% (cible benchmark) → DO_NOT_START libérés (mais besoin d'arbitrage owner explicite)
- Si conversion reste < 0.5% → renouveler verdict pour 12 nouvelles semaines (commit nouveau fichier `2026-08-12-conversion-funnel-organic.md` avec `renewed_from: VERDICT-2026-001`)

**Signal qui pourrait invalider plus tôt** :
- Commerce-Loop V1 instrumentation fine (#676 + suivants) révèle un leak spécifique fixable rapidement (ex. checkout abandon 80%) → conversion mesurée peut bouger en quelques semaines, déclencher re-instrumentation avant le sunset
- Tag PROD critique qui change comportement conversion (ex. nouveau provider paiement) → trigger re-mesure

**Non-renouvellement** :
- Si à 2026-08-12 aucune ré-instrumentation publiée → `r5-diagnostic-engine`,
  `new-seo-platform`, `new-meta-architecture-adr` passent automatiquement de
  `blocked` à `OPEN_FOR_REVIEW` via `scripts/governance/check-verdict-expirations.sh`
  (cron weekly + alerte `__seo_event_log`).

## Notes

- Premier verdict formalisé sous le mécanisme G9 ADR-081 (header YAML
  obligatoire). Établit le précédent pour tous les futurs verdicts empiriques
  cités comme justification d'un `DO_NOT_START` ou pivot stratégique.
- Cross-refs : ADR-081 (G9 origine), `_templates/empirical-verdict-header.md`
  (template appliqué), PR monorepo #652 (mesure source), PR monorepo #676
  (instrumentation funnel post-verdict).
