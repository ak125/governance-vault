---
id: ADR-068
title: "R2 — Doctrine STRICT : 4 actions auto INTERDITES (suppress + désindex + canonical sibling + sitemap exclusion). Une page valide DOIT rester candidate INDEX."
status: accepted
date: 2026-05-16
decision_date: 2026-05-16
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: [ADR-066, ADR-067]
related_rules: [G1, T1, AI1]
related_incidents: []
reviewed_by: "@fafa"
---

# ADR-068 : R2 — Doctrine STRICT renforcée, 4 actions auto interdites + règle affirmative INDEX

## Contexte

[[ADR-066-r2-content-composition-v2]] (accepted 2026-05-15, `8a92c49`) puis [[ADR-067-r2-no-auto-suppression]] (accepted 2026-05-15, `74f45919`) ont successivement :

1. Établi le pipeline 4-gates avec matrice **5 outcomes** dont SUPPRESSED auto
2. Amendé pour **4 outcomes auto** (interdire SUPPRESSED auto, conserver path manual)

### Pourquoi renforcer encore

Décision @fafa 2026-05-16 : la doctrine ADR-067 reste **incomplète** sur 3 dimensions :

1. **Scope d'interdiction limité à SUPPRESSED uniquement** — alors qu'une suppression de fait peut aussi se faire via désindexation (decision='noindex_follow' sur page valide), canonicalisation auto (rel=canonical → sibling), exclusion sitemap auto. **Ces 4 actions doivent être STRICTEMENT interdites en automatique** pour une page valide.

2. **Pas de règle affirmative** — ADR-067 dit "no auto suppressed" mais ne stipule pas positivement que productCount ≥ 2 + compatibilité réelle = **DOIT rester candidate INDEX**. Cette règle positive doit être canonique.

3. **REJECT scope ambigu** — ADR-067 a listé reject pour "page invalide" mais sans énumération exhaustive. Doctrine ADR-068 énumère les 4 raisons UNIQUES de REJECT et exclut explicitement la similarité.

### Trigger

Décision @fafa 2026-05-16 après revue de la calibration et de l'amendement ADR-067. Renforcement préventif : la doctrine doit fermer toutes les portes dérobées d'auto-désindexation avant la livraison de PR 2 V1.5 (R2DiversityService, R2GovernanceGate, sitemap shards).

## Décision

### A. 4 actions auto STRICTEMENT INTERDITES (anti-régression renforcée)

Pour le pipeline R2 v2 (et tout futur rôle SEO transactionnel par analogie), il est **strictement interdit** d'effectuer **automatiquement** sur une page valide (`productCount ≥ 2` ET compatibilité réelle) l'une des actions suivantes :

1. **SUPPRESSION automatique** — `status='suppressed'` émis par le pipeline (déjà ADR-067)
2. **DÉSINDEXATION automatique** — `decision='noindex_follow'` ou meta robots noindex sur page valide
3. **CANONICALISATION automatique vers sœur** — `<link rel="canonical" href="<sibling_url>">` automatique
4. **EXCLUSION SITEMAP automatique** — omission de la page du sitemap XML par pipeline

### B. Règle affirmative R2 (canon)

> **Une page R2 avec `productCount ≥ 2` ET `compatibilité réelle` DOIT rester candidate INDEX.**

Pas de filtre auto sur :
- Similarité texte (semantic cosine, LSH MinHash)
- Overlap catalog (Jaccard piece-overlap > 0.92)
- Score eligibility en dessous du seuil
- Crawl budget perçu

Si la page existe avec des pièces compatibles, elle a le droit d'être **indexée** (verdict INDEX) ou au minimum **REVIEW_REQUIRED** (queue admin enrichissement, mais **reste candidate sitemap**, **pas de noindex auto**, **pas de canonical auto**).

### C. Matrice de décision pipeline R2 — canon 4 outcomes (renommage explicite)

```
INDEX | REVIEW_REQUIRED | REGENERATE | REJECT
```

| Décision | Conditions | Publication |
|----------|-----------|-------------|
| `INDEX` | productCount ≥ 2 ET compatibilité réelle ET score ≥ THRESHOLD_V1 | Publish + sitemap include + canonical self |
| `REVIEW_REQUIRED` | productCount ≥ 2 ET compatibilité réelle ET (score < THRESHOLD_V1 OU contenu trop proche OU signal faible) | Status review_required, queue admin enrichissement, **sitemap INCLUS**, **canonical self**, **pas de noindex** |
| `REGENERATE` | data complète mais score juste sous seuil, retry pipeline | Re-enqueue, retry_count++, max 2 retries |
| `REJECT` | **page invalide UNIQUEMENT** (4 raisons exhaustives ci-dessous) | Status rejected, noindex+exclu sitemap, page invalide → 404/410 |

**Renommage `review` → `review_required`** : le code monorepo après ADR-067 utilisait `verdict: 'review'`. ADR-068 standardise en `verdict: 'review_required'` aligné avec `R2DecisionV2Enum.review_required` déjà existant. Évite l'ambiguïté entre `'review'` (verdict eligibility) et `'review_required'` (decision DB) — désormais identique partout.

### D. REJECT scope strict — 4 raisons UNIQUES

REJECT pipeline ne peut être émis QUE pour l'une des 4 raisons suivantes :

1. **`productCount < 2`** (legacy noindex rule preserved, page sans pieces inutile)
2. **Donnée invalide** (corruption JSONB, fingerprint manquant, schema parse error, sha256 cassé)
3. **URL techniquement impossible** (slug invalide, type_id introuvable, gamme inexistante)
4. **Compatibilité absente** (RPC `get_pieces_for_type_gamme_v4` retourne `count=0` et `pieces=[]` — pas de pièce compatible avec ce type)

**PAS pour similarité.** PAS pour overlap > 0.92. PAS pour cluster pollué. PAS pour score < threshold si productCount valide (→ REVIEW_REQUIRED).

### E. Conséquences code monorepo (PR fixup à suivre)

1. `R2EligibilityVerdictEnum` : `['eligible', 'review', 'reject']` → **`['eligible', 'review_required', 'reject']`** (renommage cohérence canon)
2. `R2EligibilityService.evaluate()` :
   - Below threshold + productCount ≥ 2 → verdict `'review_required'` (was `'review'`)
   - REJECT scope : explicit error messages pour les 4 raisons strict (productCount<2 / data invalid / URL impossible / compat absente)
3. DTO `R2EnrichSingleResponse.eligibility.verdict` : `'review'` → `'review_required'`
4. Tests Jest mis à jour
5. `R2DecisionV2Enum` (DB enum) : pas de changement, `'review_required'` déjà présent
6. Migration : pas de DDL nécessaire (status='review' / decision='review_required' déjà supportés dans CHECK constraints — vérifier alignement après PR)

### F. Conséquences Rego policies (vault)

`r2-content-write.rego` à durcir :

- **Nouveau deny** : `pipeline_generated` AND `decision='noindex_follow'` AND `productCount >= 2` → deny reason `ADR-068 — page valide ne peut être noindexée automatiquement`
- **Nouveau deny** : `pipeline_generated` AND `decision='index'` mais output emit `<link rel="canonical" href="<sibling>">` → deny reason `ADR-068 — canonical sibling auto interdit, doit être self`
- **Existing deny conservés** : `pipeline_generated → suppressed`, anti-canonical-chain
- **Nouveau deny** : `pipeline_generated` AND `decision='reject'` AND `reject_reason NOT IN [productCount_under_2, data_invalid, url_impossible, compatibility_absent]` → deny reason `ADR-068 — REJECT scope strict (4 raisons UNIQUES)`

### G. Conséquences sitemap

`SitemapV10Service.generateR2Shards()` (future PR 2) :
- INCLUS : `decision IN ('index', 'review_required')`
- EXCLUS : `decision IN ('reject', 'suppressed')` (suppressed = admin manuel, reject = invalide)
- Pas d'exclusion auto basée sur catalog overlap / similarité

## Conséquences

### Positives

- **Anti-régression complète** : 4 actions auto interdites couvrent toutes les voies de désindexation cachées
- **Règle positive affirmative** : guide non-ambigu pour les futurs développeurs / agents — page valide = INDEX candidate point
- **REJECT scope énumérable** : audit-trail clair pour chaque rejection, pas de "fourre-tout similarité"
- **Renommage cohérent** : `review` → `review_required` aligne le verdict eligibility avec l'enum DB decision

### Négatives

- **Volume REVIEW_REQUIRED élevé** prévu : la calibration N=200 a montré que 58% des G2 (catalog overlap > 0.92) seraient REVIEW_REQUIRED. Volume admin à gérer.
  → Mitigation V2 (PR 3) : enrichissement LLM automatique pour les REVIEW_REQUIRED à signal faible (composer rend les motorisations explicitement distinctes via S_MOTOR_DELTA + S_FAQ_SPECIFIC enrichies)

- **Sitemap potentiellement gros** : INDEX + REVIEW_REQUIRED → sitemap inclut les ~58% G2 REVIEW que la doctrine ADR-066 aurait suppressed. Google reçoit plus d'URLs.
  → Acceptable : Google gère le crawl budget. Mieux que désindexer à tort.

### Risques résiduels

| Risque | Mitigation |
|--------|------------|
| Google clusterise lui-même les pages similaires REVIEW_REQUIRED | Acceptable — Google choisit canonical, on ne lui force pas la main |
| Sitemap énorme dégradation crawl | Sitemap sharding V10 supporte 50K URLs / shard, robots.txt mention sitemap, normal pour 500K URLs |
| REVIEW queue overflow admin | Métrique daily count + alerte si > 10k pending ; PR 3 V2 ajoute enrichissement LLM auto |

## Rollout

- **Maintenant** : ADR-068 accepted dans le vault
- **Rego policies durcies** (cette PR) : 3 nouveaux deny invariants
- **PR fixup monorepo** (suivante) : verdict rename + REJECT reasons exhaustifs
- **PR 2 V1.5** (future) : honore ADR-068 dès le départ. R2DataLoaderService + diversity + governance gate matrice 4 outcomes avec REVIEW_REQUIRED par défaut quand productCount valide

## Hors scope

- Migration historique : zéro page R2 v2 produite encore (feature flag OFF)
- Page R2 héritée pré-v2 : ADR-068 scope strict pipeline v2 uniquement. Pages legacy conservent leur statut courant
- Comportement R8 ou autres rôles : ADR-068 scope strict R2, mais doctrine 4-actions-interdites est documentée comme **canon transverse** dans `feedback_no_auto_page_suppression_ever` (memory)

## Cross-refs

- [[ADR-066-r2-content-composition-v2]] (initial, amended by ADR-067 + ADR-068)
- [[ADR-067-r2-no-auto-suppression]] (amended by ADR-068, scope étendu)
- Memoire canon monorepo : `feedback_no_auto_page_suppression_ever` (STRICT, mise à jour 2026-05-16 avec 4 interdictions + règle affirmative + REJECT scope)
- Calibration empirique N=200 (Supabase project `cxpojprgwgubzjyqzmoq`, 2026-05-15)

## Self-review

**Pourquoi 3 ADR successifs (066 → 067 → 068)** : preuve que la doctrine évolue rapidement post-calibration empirique pré-production. Coût correction = très faible (zéro page R2 v2 publiée). Bénéfice = doctrine alignée et étanche avant PR 2 V1.5 (pipeline complet) qui sera coûteux à corriger après production.

**Pourquoi amend et pas supersedes** : ADR-066 + ADR-067 restent valides à ~90% (architecture, scoring, schemas, tests, mémoires fondamentales). Seules les invariants doctrine évoluent. Amendement préserve traçabilité chronologique.

**Self-review verdict: APPROVE** — Doctrine STRICT renforcée, 4 actions auto interdites énoncées explicitement, règle affirmative INDEX canon, REJECT scope énumérable. Code et Rego invariants alignés. Mémoire canon monorepo mise à jour. Pas de migration DDL. Cross-refs ADR-066 + ADR-067 préservés.
