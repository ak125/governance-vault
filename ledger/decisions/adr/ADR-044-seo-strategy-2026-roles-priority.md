---
id: ADR-044
title: "SEO Strategy 2026 — priorité contenu R6/R8/R7, R3 remediation only, 7 vagues"
status: proposed
date: 2026-05-07
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "Q1", "AP-04", "AP-08"]
related_incidents: []
related_adr: ["ADR-025", "ADR-026", "ADR-027", "ADR-031", "ADR-033", "ADR-036", "ADR-040"]
implementation_status: v0a-in-progress-pr340
---

# ADR-044 — SEO Strategy 2026 (priorité contenu R6/R8/R7, R3 remediation only)

## Contexte

Diagnostic GSC/GA4 backfillé en session 2026-05-06 (33 jours, 2026-04-01 → 2026-05-03,
project Supabase `cxpojprgwgubzjyqzmoq`) :

| Indicateur | Constat |
|---|---|
| Clicks GSC | **2-8/jour** (floor extrêmement bas) |
| Position moyenne | **~33** (toujours hors page 1) |
| CTR | 0.07-0.62% |
| Organic search 7j vs 7j | **-18.3%** (759 → 620 sessions) |
| Direct 7j vs 7j | +5.5% (1667 → 1758) |
| Conversions GA4 | **0 partout** (tracking non câblé) |

**Réinterprétation** : la "chute" R3 conseils (11/15 pages perdantes) est un
**symptôme**, pas le problème central. Le site automecanik.com **n'a jamais eu
de trafic SEO significatif**. Les vrais leviers sont :

- **Couverture sémantique** : 178 gammes sans KW pipeline complet
  (cf. mémoire `kw-pipeline-status.md`)
- **Mismatch d'intent** : R3 saturé sur le web, exposé Core Updates 2025-2026
  (E-E-A-T faible, contenu IA générique facile à dégrader)
- **Confiance Google** : pas de signaux d'autorité différenciants
- **Tracking conversion absent** : tout ROI marketing invisible

L'avantage compétitif différenciant du repo (vs blogs auto saturés) :

- Catalogue 53 959 véhicules + remappage TecDoc (mémoire `tecdoc-integration.md`)
- Moteur diagnostic existant `__diag_*` (13 systèmes, 62 symptômes — mémoire
  `diagnostic-engine-breezy-eagle.md`)
- Compatibilité OEM massive
- Architecture RAG structurée (mémoire `rag-pipeline-strategy.md`)
- Sitemap V2 (1M+ URLs sharding 50K — mémoire `frontend.md`)

## Décision

### Inversion canon des priorités contenu

Le levier de croissance n'est **pas** R3 (saturé, low E-E-A-T post-Core-Updates).
L'ordre canon de priorité contenu pour 2026 est :

| Priorité | Rôle | Justification |
|---|---|---|
| **1** | **R6 Guide Achat** | Intent commercial, meilleur CTR, monétisable, E-E-A-T naturel via catalogue+prix réels, moins exposé Core Updates |
| **2** | **R8 Véhicule** | Long-tail volumique massif, hub structuré, peu d'acteurs canoniques |
| **3** | **R7 Marques** | Autorité, hub transversal, signal trust qui amplifie les autres rôles via maillage |
| 4 | R3 Conseils | **Remediation only** (plafond 20% du trafic). Aucune génération R3 neuve. |
| 5 | R5 Diagnostic | **Pas de pages dédiées** (ADR-027 sunset). Levier = enrichir section S2_DIAG dans R3 (51% → 95% via ADR-027 Phase D `__diag_gamme_system_map`). |

### 7 vagues séquentielles + 12 standards transverses

Plan détaillé hors-vault (monorepo `.claude/plans/utiliser-la-meilleure-approche-zippy-waterfall.md`) :

- **V0** Pilotage de base — cron daily GSC/GA4/Links, GA4 multi-events tracking, alerting
- **V0.5** SEO Intelligence Layer MVP — segmentation par rôle dans `__seo_gsc_daily`, anomaly detection MAD seasonally-adjusted
- **V1** R6 Guide Achat (pilote 10 → top 100)
- **V2** R5 enrichissement S2_DIAG dans R3 + ADR-027 Phase D
- **V3** R8 Véhicule (pilote 10 → top motorisations)
- **V4** R7 Marques
- **V5** Internal Linking Engine (règles déclaratives DB `__seo_link_rules` avec `governance_ref NOT NULL`, intent_drift_check)
- **V6** R3 remediation only (pollution-scanner, surgical-cleaner, legacy-recycler — pas de génération neuve)
- **V7** Marketing G1 (ADR-036)
- **V7-bis** Backlinks via R7 outreach

Standards transverses obligatoires :

- **S0** vérification pré-requis avant chaque vague (PR description bloquante)
- **S1** ADR vault canon `status=accepted` AVANT ship (cet ADR + ADR-045)
- **S4** versionnage sections (`version`/`published_at`/`superseded_by`) pré-requis V1
- **S5** Schema.org véracité (no `AggregateRating` sans source vérifiable)
- **S6** experimentation-first (pilote 10 unités + 14j go/no-go avant scale)
- **S9** feature flags `__seo_role_flags` (kill-switch noindex)
- **S10** RGPD scrubbing PII GA4/Sentry
- **S11** caching HTTP `s-maxage` Caddy (CWV ≤ 2.5s LCP)
- **S12** budget LLM `__llm_usage_budget` plafond 8M tokens/mois (kill-switch à 90%)

### KPI progressifs J+30/J+60/J+90

| KPI | Baseline | J+30 | J+60 | J+90 |
|---|---|---|---|---|
| Clicks GSC/jour | 2-8 | 15-25 | 35-50 | **60-80** |
| Sessions organic /7j | 620 | 900-1100 | 1400-1900 | **2400-3000** |
| Position moy top 100 R6 | inconnue | ≤ 30 | ≤ 22 | **≤ 18** |
| Couverture R6 top 100 commerciales | ~0% | 30% | 70% | **100%** |
| Couverture S2_DIAG dans R3 | 51% | 70% | 85% | **≥ 90%** |
| Tokens Anthropic mensuels | 0 | < 1M | < 4M | **< 8M (plafond)** |

Distribution attendue J+90 : R6 40% / R8 30% / R3 ≤ 20% (plafond dur, incl. S2_DIAG) / R7 5% / R1-R0 5%.

## Statut

- **Statut** : proposed (PR vault en cours)
- **Implémentation** :
  - Plan détaillé écrit (monorepo `.claude/plans/`)
  - V0.A en cours — monorepo PR #340 (cron daily-fetch + cron/health endpoint)
  - V0-bis / V0.B-E / V1-V7-bis : non démarrés
- **Pré-requis ADRs** :
  - ADR-045 (SEO V0 monitoring cron) — drafted simultanément
  - ADR-027 Phase D extension (mapping `__diag_gamme_system_map`) — pré-requis V2
  - ADR-046+ (V5 linking engine, V0.5 intelligence layer) — à rédiger lors des PRs respectives

## Conséquences

### Positives

- **Inversion R3 → R6/R8/R7** réduit le risque d'un catalogue de pages génériques
  saturées qui aggrave le profil E-E-A-T du domaine
- **Experimentation-first** (pilote 10 + 14j go/no-go) évite les batches top 100
  sans signal d'impact (anti-bricolage)
- **Standards transverses** (S0-S12) sont applicables à toute initiative SEO
  ultérieure — réduisent dette technique
- KPI progressifs permettent détection précoce de trajectoire ratée vs cible
  uniquement à J+90

### Négatives / risques

- Cible J+90 (clicks 60-80/jour) reste ambitieuse — peut être manquée si une
  vague (V1 R6) sous-performe et bloque V3/V5
- Plafond R3 ≤ 20% trafic est un **garde-fou**, pas une mesure absolue : si à J+90
  R3 dépasse 20%, déclencher audit V6 scope (suspecter génération R3 neuve cachée)
- 12 standards transverses + 7 vagues = surface de gouvernance large.
  Risque de sur-scope si chaque vague ajoute des sous-PR
- Dépendance forte aux skills SEO existants (40 agents R0-R8 + 16 skills) :
  toute régression d'un skill canon (`v5-guardian`, `seo-content-architect`,
  `pollution-scanner`) bloque la vague qui en dépend

## Anti-patterns à rejeter (futurs)

- ❌ **Génération R3 neuve hors vague V6** = `content-gen --r3` direct → hors-scope
  explicite, à rejeter en review
- ❌ **Pages R5 dédiées** (URL distincte symptom × véhicule) = ADR-027 violation
- ❌ **`AggregateRating` Schema.org sans source vérifiable** en DB = risque manual
  action Google
- ❌ **Règles linking en hardcode** dans le service = doit vivre en DB
  `__seo_link_rules` avec `governance_ref NOT NULL`
- ❌ **Scale top 100 sans pilote 10 + 14j go/no-go** = scale du bricolage
- ❌ **`google.com/ping?sitemap=`** post-publish = endpoint déprécié supprimé par
  Google. Stratégie de remplacement : `lastmod` ISO 8601 fiable + déclaration
  robots.txt/GSC + maillage interne immédiat ; IndexNow pour Bing/Yandex
  (Google **non** IndexNow-compatible)

## Références

- Plan détaillé monorepo : `.claude/plans/utiliser-la-meilleure-approche-zippy-waterfall.md`
- Diagnostic GSC/GA4 : session 2026-05-06 (backfill 33j, project `cxpojprgwgubzjyqzmoq`)
- Mémoires session : `seo-strategy-2026-approved-20260506`,
  `feedback_r5_no_dedicated_pages`, `feedback_seo_methodology_canon_20260506`
- ADRs liés : ADR-025 (SEO Department architecture), ADR-026 (P0 content separation),
  ADR-027 (R5 sub-pages sunset), ADR-031 (canonical 4-layer raw/wiki/exports/consumers),
  ADR-033 (wiki gamme diagnostic relations), ADR-036 (marketing operating layer),
  ADR-040 (seo-roles canon TS-side only)
