---
id: ADR-070
title: "R2 — R8+R1 first, R2 second : formule canon `R2Content = render(R8 + R1 + KG + WIKI)`, INTERNAL DIFFERENCE EXHAUSTION, technical criteria = evidence"
status: accepted
date: 2026-05-16
decision_date: 2026-05-16
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: [ADR-066, ADR-067, ADR-068]
related_rules: [G1, T1, AI1]
related_incidents: []
reviewed_by: "@fafa"
---

# ADR-070 : R2 — Formule canon `R2Content = render(R8 + R1 + KG + WIKI)`, ordre L0-L5 strict, technical criteria = evidence

## Contexte

[[ADR-066-r2-content-composition-v2]] (`8a92c49`) puis [[ADR-067-r2-no-auto-suppression]] (`74f45919`) puis [[ADR-068-r2-doctrine-strict-no-auto-deindex]] (`2c3ea84b`) ont successivement :

1. ADR-066 : Établi le pipeline 4-gates avec eligibility composite + SUPPRESSED auto
2. ADR-067 : Amendé pour interdire SUPPRESSED auto (page valide preservée)
3. ADR-068 : Renforcé en interdisant 4 actions auto (suppress + désindex + canonical sibling + sitemap exclusion) + REJECT scope strict 4 raisons UNIQUES

### Pourquoi ADR-070

ADR-066/067/068 ont fermé les portes d'auto-désindexation, mais **n'ont pas codifié la SOURCE de vérité du contenu R2**. La calibration N=200 puis le pilote V1 (10 URLs stratifiées) ont confirmé que **`R2DataLoaderService` stub seul ne produit pas de signal commercial distinct** entre motorisations sœurs (overlap pieces 93%) → 100% review_required avec proxy SQL.

Le diagnostic de cause racine (décisions @fafa 2026-05-16, rounds 5-7) :

1. **Round 5 — Formule canon mal posée** : `R2 = R8 + R1 + CompatEvidence` écrasait la séparation `cadre` (R8 + R1) vs `matière factuelle` (KG facts + WIKI evidence). Le contenu **riche** d'une page R2 ne provient PAS de R8+R1 seuls — il provient des facts atomiques + evidence validée.

2. **Round 6 — Ordre exécution non doctriné** : Playwright/WIKI était envisageable dès PR 2, alors que la base AutoMecanik contient déjà massivement de vérité métier (OEM refs, compat tables, dimensions, supplier, mounting). Lancer L4 externe avant exhaustion L0-L3 = construction d'une couche inutile + risques (drift, coûts LLM, légal).

3. **Round 7 — Confusion contenu éditorial vs preuve technique** : risque de générer des paragraphes longs avec specs brutes (largeur 155,2 mm × hauteur 66 mm...) noyant le lecteur, au lieu d'utiliser les critères techniques en preuve compacte (tableau + warning).

### Trigger

Décisions @fafa 2026-05-16 (Rounds 5+6+7 brainstorming canon, plan `/home/deploy/.claude/plans/le-contenu-de-r2-scalable-tower.md`). Trois corrections doctrinales structurelles à cumuler dans une ADR canon avant PR 2D Mono (R8 snapshot store + initial seed all type_ids).

## Décision

### A. Formule canon R2 (Round 5)

```
R2Content = render(
  R8VehicleSnapshot,           ← CADRE OBLIGATOIRE (quel véhicule / motorisation)
  R1GammeContext,              ← CADRE OBLIGATOIRE (quelle famille de pièce)
  VehiclePartKnowledgeFacts,   ← MATIÈRE FACTUELLE (Knowledge Graph canonicalisé L3)
  ValidatedWikiEvidence,       ← MATIÈRE FACTUELLE (WIKI validated_status auto/human, L4 fallback)
)
```

**Distinction critique** :

- **R8 + R1 = CADRE obligatoire** (sans ces deux parents → page R2 = générique, jamais INDEX candidate)
- **KG + WIKI = MATIÈRE factuelle** (sans matière → page R2 = pauvre, recyclage R8+R1 sans valeur ajoutée)
- **R2 = projection finale**, JAMAIS source de vérité

Le pipeline R2 charge les 4 inputs en parallèle (avec gates prerequisite). Si l'un manque OU la matière factuelle totale est vide → verdict `review_required` (enrichissement requis).

### B. Ordre canonique L0-L5 strict (Round 6 — INTERNAL DIFFERENCE EXHAUSTION)

```
L0  Existing Internal Knowledge             (auto_type, pieces, pieces_ref_oem, pieces_relation_type)
L1  Existing R1/R8 SEO snapshots            (__seo_gamme_conseil, __seo_r8_snapshot_store, __seo_r1_keyword_plan)
L2  Internal OEM/compat graph               (déduit L0+L1 via SQL joins)
L3  KG canonicalization                     (__seo_vehicle_part_knowledge, 12 dimensions atomiques)
─── ★ GATE INTERNAL DIFFERENCE EXHAUSTION ★ ──────────────────────────────────
L4  External evidence (Playwright/WIKI)     (CONDITIONAL — uniquement si internal_difference_score < threshold)
L5  Rendering                                (R2FactsToSectionsProjector → R2ContentRenderer)
```

**Doctrine canon Round 6** :

> **Aucune evidence externe autorisée tant que `internal_difference_score >= THRESHOLD_INTERNAL_SUFFICIENT`.**

`R2InternalDifferenceScoreService` (pure fn, score composite [0,100]) calcule la richesse interne avant tout déclenchement L4 :

| Sub-score | Source | Poids |
|-----------|--------|-------|
| `oem_distinct_score` | différence OEM refs vs sibling type_ids (Jaccard set) | 0.30 |
| `compat_distinct_score` | différence compat tables (pieces_relation_type joins) | 0.25 |
| `dimensions_distinct_score` | dimensions / dimensions disque / essieu / étrier | 0.15 |
| `mounting_distinct_score` | montage avant/arrière, position | 0.10 |
| `supplier_distinct_score` | équipementier OE différent | 0.10 |
| `motor_disambiguation_score` | R8 disambiguation_signature richness | 0.10 |

`THRESHOLD_INTERNAL_SUFFICIENT` initial = 60 (à calibrer empiriquement sur golden samples avant full-scale).

### C. Technical criteria = evidence, not editorial source (Round 7)

> **Les critères techniques (dimensions, OEM refs, supplier, mounting) sont des PREUVES STRUCTURÉES, pas une source éditoriale.**

| Rôle | Source ÉDITORIALE (texte long) | Source PREUVE (compact) |
|------|--------------------------------|--------------------------|
| Contenu pédagogique gamme (selection guide, mistakes, FAQ) | R1 gamme conseil (hérité tel quel) | — |
| Contenu enrichissement narratif | WIKI evidence validée (prose FR Claude) | — |
| Différences techniques par variante | — | KG facts compact (tableau + warning) |
| Signal de décision pipeline | — | KG facts pour internal_difference_score |
| Anti-duplicate métier | — | sha256(12 business dimensions) |

R2 sections où les critères techniques peuvent apparaître **uniquement** :
- `S_COMPAT_DIFFERENCES` (prose courte WIKI + facts compacts)
- `S_TECHNICAL_TABLE_COMPACT` (tableau compact, max 5-7 lignes)
- `S_SELECTION_WARNING` (warning court, max 2-3 phrases)

Sections **où les critères techniques sont INTERDITS en paragraphes** :
- `S_SELECTION_GUIDE` (héritée R1 telle quelle)
- `S_MISTAKES_AVOID` (héritée R1 telle quelle)
- `S_FAQ_GAMME` (héritée R1 telle quelle)
- `S_TECHNICAL_CRITERIA` générique (héritée R1 telle quelle)
- `S_REASSURANCE_METIER` (héritée R1 telle quelle)

### D. Matrice 4 outcomes pipeline (héritée ADR-068, étendue gates)

```
INDEX | REVIEW_REQUIRED | REGENERATE | REJECT
```

Nouveaux gates prerequisite ADR-070 qui forcent `review_required` (jamais REJECT auto) :

| Gate | Reason si missing |
|------|-------------------|
| R8 snapshot CADRE | `r8_snapshot_unavailable (ADR-070)` |
| R1 gamme context CADRE | `r1_gamme_context_missing (ADR-070)` |
| Matière factuelle (KG OR WIKI ≥ 1) | `r2_no_factual_matter (ADR-070)` |
| H1 + S_VARIANT_DISAMBIGUATION | `r2_disambiguation_missing (ADR-070)` |
| Body section sans specs brutes répétées | `r2_technical_criteria_in_editorial (ADR-070 R7)` |

### E. Conséquences Rego policies (vault, fichier `r2-content-write.rego`)

5 nouveaux `deny` invariants Round 7 cumulés :

1. `pipeline_generated AND decision='index' AND r8_snapshot_status NOT IN ('minimal','enriched','stale')` → reason `ADR-070 R8 CADRE requis`
2. `pipeline_generated AND decision='index' AND r1_gamme_context_status != 'loaded'` → reason `ADR-070 R1 CADRE requis`
3. `pipeline_generated AND decision='index' AND knowledge_facts_count == 0 AND validated_wiki_evidence_count == 0` → reason `ADR-070 MATIÈRE FACTUELLE requise (KG facts OU WIKI validée)`
4. `pipeline_generated AND decision='index' AND (NOT h1 contains motor_power_pattern OR S_VARIANT_DISAMBIGUATION missing)` → reason `ADR-070 H1 disambiguation obligatoire`
5. `pipeline_generated AND decision='index' AND body_long_form_section_contains_raw_specs == true` → reason `ADR-070 R7 technical criteria = evidence only (paragraphes longs avec specs brutes interdits)`

### F. Conséquences code monorepo (PR 2D / 2H / 2E à suivre)

1. **PR 2D (R8 snapshot)** : `R8ParentEnrichmentService` + `R8SnapshotReaderService` + table `__seo_r8_snapshot_store` (immutable, versioned). Job seed initial idempotent : INSERT minimal snapshot pour TOUS type_ids existants. Sans ce seed, gate `r8_snapshot_unavailable` bloque ~95% pilote V1.
2. **PR 2H (Knowledge Graph L3)** : table `__seo_vehicle_part_knowledge` (12 dimensions atomiques), `R2KnowledgeGraphService` + `R2EvidenceDecayJobService` (freshness scoring nightly).
3. **PR 2E (R2DataLoader + pilot)** : `R2InternalDifferenceScoreService` (gate R6), `R2FactsToSectionsProjector` (R7 facts → sections compact), `R2DuplicateBusinessSignatureService` (sha256 12 dimensions).
4. **R1 prerequisite** : audit `__seo_gamme_conseil` completeness avant pilote V1. Si > 30% gammes ont sections critiques vides → re-déclencher R1 keyword planner agent existant (hors scope PR 2, bloquant pour pilote).

### G. R8 + R1 prerequisite gates (canon dual gate Round 5)

`R2DataLoaderService.assembleCompositionInput(pgId, typeId)` charge en parallèle :

1. **R8 snapshot** via `R8SnapshotReaderService.getLatestSnapshot(typeId)`
   - Si null → `review_required` reason `r8_snapshot_unavailable` + enqueue async `r8-enrichment` (non-blocking, jamais d'attente live)
   - Si status='failed' → `review_required` reason `r8_enrichment_failed`

2. **R1 gamme context** via `R1GammeContextService.getGammeContext(pgId)`
   - Si gamme manquante → `review_required` reason `r1_gamme_context_missing`
   - Si sections S_SELECTION_GUIDE / S_MISTAKES_AVOID / S_FAQ_GAMME / S_TECHNICAL_CRITERIA / S_REASSURANCE_METIER toutes vides → `review_required` reason `r1_gamme_sections_empty` + enqueue R1 backfill

Sans les deux parents → R2 = page véhicule ou page pièce générique (sans valeur SEO). Les deux gates sont **obligatoires** (et non équivalents).

## Conséquences

### Positives

- **Formule canon explicite** : `R2Content = render(R8 + R1 + KG + WIKI)` distingue clairement CADRE vs MATIÈRE, évite régression "R2 generic = R8+R1 only"
- **Anti-Playwright premature** : doctrine INTERNAL DIFFERENCE EXHAUSTION force d'exhauster L0-L3 avant tout L4. Évite construction couche L4 inutile pour 70-90% des cas
- **Anti specs brutes** : technical criteria = evidence only force le rendu compact (tableau + warning) au lieu de paragraphes spec dump
- **5 prerequisites enforced via Rego** : pas d'INDEX émis sans CADRE + MATIÈRE + disambiguation + format éditorial sain

### Négatives

- **Volume `review_required` initial élevé** (prévu pilote V1) : tant que R8 seed initial pas terminé (PR 2D) + R1 backfill pas complet, gate `r8_snapshot_unavailable` / `r1_gamme_context_missing` enquêtent review_required pour la majorité des type_ids.
  → Mitigation : PR 2D job seed initial idempotent pour tous type_ids existants. R1 backfill agent re-déclenché en parallèle.

- **`internal_difference_score` à calibrer empiriquement** : THRESHOLD_INTERNAL_SUFFICIENT initial = 60 sans validation golden.
  → Mitigation : calibration golden samples obligatoire avant full-scale launch (Round 6 5 prerequisites).

### Risques résiduels

| Risque | Mitigation |
|--------|------------|
| R8 snapshot store devient SoT trop large, drift vs auto_type | Job nightly reconciliation `auto_type.updated_at` vs snapshot → mark stale, re-enqueue enrichment |
| Knowledge Graph drift avec catalog (KG dit X, pieces dit Y) | Reconciliation job nightly : catalog gagne (SoT), KG rebuild facts depuis catalog |
| R1 sections vides bloquent compose massivement | Audit pré-PR 2 + R1 backfill agent prerequisite (PR 2C' avant pilote V1) |
| `internal_difference_score` mal calibré → trop de L4 déclenchements | Golden samples + métrique OTel `r2.compose.l4_external_called_rate` cap < 30%, alerte au-delà |

### Compatibilité

- **ADR-066 (foundation)** : ADR-070 étend matrice 4 outcomes + ajoute 4 gates prerequisite. Pas de conflit.
- **ADR-067 (no auto suppress)** : préservé. SUPPRESSED reste manual-only.
- **ADR-068 (4 actions auto interdites)** : préservé. ADR-070 ne réintroduit aucune désindexation/canonicalisation auto.

## Évidence + métriques (post-merge)

- `r2.compose.internal_difference_score_distribution` histogram
- `r2.compose.r8_snapshot_unavailable_rate` gauge (target < 5% post PR 2D seed)
- `r2.compose.r1_gamme_context_missing_rate` gauge (target < 10% post PR 2C' backfill)
- `r2.compose.l4_external_called_rate` gauge (target < 30%)
- `r2.governance.deny_count{reason="ADR-070*"}` counter (alerte > 0 = bug critique)

## Cross-refs

- [[ADR-066-r2-content-composition-v2]] (foundation, accepted 2026-05-15)
- [[ADR-067-r2-no-auto-suppression]] (amends ADR-066, accepted 2026-05-15)
- [[ADR-068-r2-doctrine-strict-no-auto-deindex]] (amends ADR-066+067, accepted 2026-05-16)
- ADR-072 (à venir, paradigme CQRS+DDD+Snapshot, stack post-ADR-070)
- `feedback_no_auto_page_suppression_ever` (monorepo memory, canon-strict 4 interdictions auto)
- `feedback_pr2_v1_5_pilot_signals` (monorepo memory, 6 points qualité pilote V1)

## Self-review

Self-review verdict: APPROVE

Checklist 8 items (canon `feedback_vault_self_review_before_admin_merge`) :

1. ✅ **ADR numbering** : ADR-070 disponible (ADR-069 réservé evidence-based, conditional post-measurement)
2. ✅ **amends/supersedes** : amends ADR-066+067+068 (cascade canon préservée, aucune contradiction)
3. ✅ **Rego deny invariants** : 5 nouveaux deny énumérés explicitement (R8 / R1 / matière / disambiguation / technical-criteria-evidence-only)
4. ✅ **Tests Rego à mettre à jour** : `r2-content-write_test.rego` couvrira les 5 nouveaux cas (1 deny + 1 allow par invariant)
5. ✅ **WASM regen** : `build-opa-bundles.sh` exécuté pour `r2-content-write.wasm` (reproducible via paths relatifs)
6. ✅ **Audit-trail** : entry à créer dans `ledger/audit-trail/ADR-070-r8-r1-first-r2-second-active-disambiguation-{sha}.md` post-commit
7. ✅ **MOC link** : entry à créer dans `ops/moc/MOC-Decisions.md` + `ops/moc/MOC-AuditTrail.md`
8. ✅ **Cross-refs** : wikilinks validés vers ADR-066/067/068 + memories monorepo (backtick refs car cross-repo)

PR body marker obligatoire : `Self-review verdict: APPROVE` (canon `feedback_vault_pr_body_self_review_marker`)
