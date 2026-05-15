---
id: ADR-067
title: "R2 Content Composition — Doctrine pivot : SUPPRESSED automatique INTERDIT, compatibilité pièce prime sur similarité texte"
status: accepted
date: 2026-05-15
decision_date: 2026-05-15
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: [ADR-066]
related_rules: [G1, T1, AI1]
related_incidents: []
reviewed_by: "@fafa"
---

# ADR-067 : R2 — SUPPRESSED automatique INTERDIT (amendement ADR-066)

## Contexte

[[ADR-066-r2-content-composition-v2]] (accepted 2026-05-15, vault commit `8a92c49`) a livré une **matrice de décision à 5 sorties** pour le pipeline R2 v2 :

```
INDEX | SUPPRESSED | REVIEW_REQUIRED | REGENERATE | REJECT
```

avec `SUPPRESSED` déclenché **automatiquement** sur catalog_overlap > 0.92 + sibling INDEX fiable (canonical sibling). Le rationale ADR-066 était : éviter le duplicate content massif quand deux motorisations sœurs partagent >92% du catalogue.

### Calibration empirique 2026-05-15 — résultats inattendus

Calibration N=200 stratified (100 G1 + 99 G2) exécutée sur la base prod (Supabase project `cxpojprgwgubzjyqzmoq`) après merge PR 0 vault #281 + PR 1 monorepo #543 a révélé :

| Stratum | N | avg Jaccard piece-overlap | candidats SUPPRESSED auto (>92%) |
|---------|---|---------------------------|----------------------------------|
| G1 | 100 | 49% | 14 / 100 (14%) |
| G2 | 99 | 81% (p50=100%) | **57 / 99 (58%)** |

→ Sous la doctrine ADR-066, **58% des pages G2** seraient devenues SUPPRESSED automatiquement. C'est un volume inacceptable d'aplatissement canonical de pages potentiellement valides.

### Pivot doctrine utilisateur

Décision @fafa 2026-05-15 (post-calibration empirique) : **il est strictement interdit de supprimer (suppress/canonicaliser) automatiquement une page R2**, même si overlap catalog élevé.

Justification métier (e-commerce automobile) — deux motorisations sœurs peuvent partager 93% des pièces ET pourtant requérir des pages distinctes pour :

| Dimension | Pourquoi diverge entre motorisations sœurs |
|-----------|--------------------------------------------|
| Référence OEM | Cross-reference OEM différent même pour pièce identique |
| Montage | Jeu de fixation, couple, sens de montage variant |
| Année / phase | Mise à jour millésime, restylage |
| Équipementier | Bosch vs Continental sur même pièce — origine usine |
| Stock / catalogue | Prix, dispo, conditions de vente |
| Compatibilité réelle | Capteurs / connectique légèrement divergents |
| Risque erreur client | Mauvaise pièce sur mauvais modèle = retour + insat. |

**La compatibilité pièce prime sur la similarité texte.** Catalog overlap > 0.92 = signal pour **enrichir** la page (rendre la motorisation distincte explicite) ou flag REVIEW (validation humaine), **jamais** signal pour suppression automatique.

## Décision (amende ADR-066)

### Nouvelle matrice de décision R2 — 4 sorties

```
INDEX | REVIEW | REGENERATE | REJECT
```

| Décision | Conditions | Action |
|----------|-----------|--------|
| `INDEX` | productCount ≥ 2 ET compatibilité réelle ET eligibilityScore ≥ THRESHOLD | Publish + sitemap + snapshot |
| `REVIEW` | productCount ≥ 2 ET (eligibilityScore < THRESHOLD OU catalog_overlap ≥ 0.92 OU contenu trop proche OU signal faible) | Queue humain `__seo_r2_qa_reviews`, enrichissement contenu obligatoire ou validation manuelle |
| `REGENERATE` | retry pipeline (data complète mais score juste sous seuil) | Re-enqueue, retry_count++, max 2 retries |
| `REJECT` | **Page invalide uniquement** : productCount < 2 OU données corrompues OU erreur fatale parsing | Status `rejected`, no retry, audit-trail `__seo_r2_qa_reviews` |

### `SUPPRESSED` reste — mais manual-only

- Conservé dans l'enum DB `__seo_r2_pages.status` ET dans `__seo_r2_pages.decision`
- **Trigger** : exclusivement admin override via UI review queue (`POST /api/admin/seo/r2/review-queue/:id/suppress` future PR)
- **Cas d'usage** : doublon connu confirmé humainement, page abandonnée legacy, dépublication éditoriale ponctuelle
- **Jamais** émis par eligibility / composition / governance gate automatiquement
- Rego policy `r2-content-write.rego` : path `pipeline_generated → suppressed` = `deny`. Seul `human_curated → suppressed` autorisé

### Conséquences sur catalog_signature early-gate (ADR-066 §Gate 3.a)

ADR-066 disait : "overlap > 0.92 + sibling INDEX fiable → SUPPRESSED". Amendement ADR-067 :

```
overlap > 0.92 (peu importe sibling INDEX) → REVIEW (enrichissement obligatoire)
overlap > 0.92 + sibling humainement confirmé doublon → SUPPRESSED (manual flip via admin UI)
```

Le gate Gate 3.a devient un **signal de prioritisation queue REVIEW**, plus un trigger SUPPRESSED automatique.

### Conséquences sur Rego invariants (vault `r2-content-write.rego`)

À mettre à jour :
- Règle 4 actuelle `pipeline_generated_suppressed` (allow if pipeline + decision=suppressed + canonical_target valid) → **deny** (interdire pipeline → suppressed)
- Nouvelle règle `human_curated_suppressed_override` : allow if `source_kind=human_curated` AND `decision=suppressed` AND `canonical_target valid` (admin override path)
- Anti-canonical-chain invariant reste valable pour les SUPPRESSED manuels (target.decision=INDEX, same pg_id)

### Conséquences code monorepo PR #543 (déjà mergée)

PR fixup nécessaire :
- `R2EligibilityVerdict.verdict` enum : `'eligible' | 'review' | 'reject'` (was `'eligible' | 'suppressed' | 'reject'`)
- `R2EligibilityService.evaluate()` decision tree : retirer la branche SUPPRESSED auto. Si `score < THRESHOLD` ET `productCount ≥ 2` → verdict `review`. Si `productCount < 2` → verdict `reject`.
- `R2DecisionV2Enum` : enum garde `'suppressed'` (DB compat) mais commentaire explicite "manual-only, never emitted by pipeline"
- `r2-eligibility.schema.ts` : `suppressedCanonicalTarget` field renamed / repurposed `manualCanonicalTarget` ou retiré
- Tests : `suppressed when below threshold + sibling exists` → `review when below threshold` (sibling target check moved to manual review queue)
- ADR-066 référence dans le code → ADR-066 + ADR-067 amendement

### Conséquences future PR 2 V1.5

- `R2DiversityService` Gate 3 toujours utile : produit `catalogOverlapScore` + LSH bands + embedding cosine
- `R2GovernanceGate` matrice à 4 décisions
- Frontend SUPPRESSED rendering (canonical link, route 200) : conservé pour le path manual (admin flip)
- Sitemap `excluded SUPPRESSED` : conservé (que SUPPRESSED soit manual ou auto, page exclue sitemap)
- GSC observer V1.5 : continue d'observer canonical (mais cluster doit naturellement converger sans auto-suppression)

## Conséquences

### Positives

- **Conformité doctrine SEO automobile** : la compatibilité pièce différencie même quand catalog overlap haut
- **Sécurité éditoriale** : aucune page valide n'est jamais désindexée automatiquement
- **Path manual préservé** : admin garde le pouvoir de SUPPRESSED en cas de vrais doublons confirmés humainement
- **Pipeline simpler** : 4 décisions auto au lieu de 5 — réduction surface de bugs sur le canonical path
- **Cohérence avec `feedback_no_url_changes_ever` (monorepo memory)** : pas de changement canonical automatique = doctrine sœur

### Négatives

- **REVIEW queue va exploser** sous doctrine V2 : sur la calibration, ~58% des G2 seraient REVIEW (overlap > 0.92). Volume admin à gérer.
  → Mitigation : V1.5 pilot validera le taux REVIEW réel. Si trop élevé, PR 3 V2 introduit batch enrichissement automatique (LLM enrichit le contenu motor-spécifique pour casser l'overlap) avant le gate.
- **Index bloat potentiel** : sans SUPPRESSED auto, le sitemap risque de contenir des pages quasi-identiques. Mitigation = enrichissement contenu (composer doit produire S_MOTOR_DELTA suffisamment distinct pour passer le gate)
- **Retour à un design plus complexe pour le composer** : la pression de produire du contenu motorisation-spécifique unique remonte au composer (S_MOTOR_DELTA, S_FAQ_SPECIFIC). PR 2 V1.5 doit livrer un composer robuste

### Risques résiduels

| Risque | Mitigation |
|--------|------------|
| Duplicate content Google malgré tout (réindexation lente) | GSC observer V1.5 monitore `chosenCanonical` et `duplicateWithoutCanonical` ; alerte si cluster non sain |
| Volume REVIEW queue ingérable | Métrique `__seo_r2_qa_reviews` count daily + alerte si > 5k pending ; PR 3 V2 ajoute LLM enrichissement auto pour les REVIEW à signal faible |
| Composer ne produit pas assez de motor-delta distinct | Property-based test sur ratio specificBlockCount/boilerplateRatio (déjà dans ADR-066 contrat) |

## Rollout

- **Maintenant** : ADR-067 accepted dans le vault
- **PR fixup monorepo** (suivante immédiate) : retirer le path SUPPRESSED auto du code, mettre verdict tree à 4 outcomes
- **PR vault** (cette PR) : mettre à jour Rego policies (`r2-content-write.rego`) : interdire pipeline → suppressed, autoriser human_curated → suppressed
- **PR 2 V1.5 monorepo** (future, déjà gated par pilote V1) : honore la nouvelle doctrine dès le départ. R2DataLoaderService + diversity service + governance gate matrix 4-outcomes

## Hors scope

- Migration des SUPPRESSED historiques (aucun n'existe : PR 1 vient d'arriver sur main, zéro page R2 v2 publiée encore)
- Frontend canonical rendering pour SUPPRESSED manuel : conservé tel quel pour PR 2 V1.5
- Comportement R8 ou autres rôles : ADR-067 scope strict à R2. R8 garde sa propre doctrine (mais memory `feedback_no_auto_page_suppression_ever` flag risque transverse)

## Self-review

**Pourquoi cet ADR maintenant** : la calibration empirique a révélé un comportement doctrinaire indésirable AVANT que la moindre page R2 v2 ne soit produite en prod. Coût correction = très faible (PR 1 vient juste d'être mergée, 0 production data). Bénéfice = doctrine alignée sur réalité métier e-commerce automobile.

**Pourquoi amend et pas supersedes** : ADR-066 reste valide à 95% (architecture 4-gates, scoring, schemas, tests, mémoires fondamentales). Seule la matrice de décision change. Amendement préserve la traçabilité.

**Cross-refs** :
- [[ADR-066-r2-content-composition-v2]] (amended)
- `feedback_no_auto_page_suppression_ever` (monorepo memory) (memory monorepo)
- Calibration empirique session 2026-05-15 (logs Supabase MCP)

## Références

- Mémoires canon monorepo : `feedback_no_auto_page_suppression_ever` (nouvelle, STRICT anti-régression), `feedback_seo_suppressed_canonical_decision` (superseded), `feedback_canonical_chain_prevention` (amended manual-only), `feedback_seo_catalog_signature_before_text_diversity` (amended → REVIEW au lieu de SUPPRESSED)
- Vault PR : (cette PR)
- Monorepo fixup PR : (à suivre)
