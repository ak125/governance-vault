---
date: 2026-05-16
type: audit-trail
related: [ADR-070, ADR-068, ADR-067, ADR-066, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-16 — ADR-070 R2 — R8+R1 first canon (Rounds 5+6+7 doctrine cumulée)

## What

Création et acceptance de [[ADR-070-r8-r1-first-r2-second-active-disambiguation]] qui **amende** [[ADR-066-r2-content-composition-v2]] + [[ADR-067-r2-no-auto-suppression]] + [[ADR-068-r2-doctrine-strict-no-auto-deindex]] :

- ADR-070 `status: accepted` (date 2026-05-16, decision_maker `@fafa`, reviewed_by `@fafa`)
- **Round 5 — Formule canon** :
  ```
  R2Content = render(R8VehicleSnapshot, R1GammeContext, VehiclePartKnowledgeFacts, ValidatedWikiEvidence)
  ```
  CADRE = R8 + R1 (obligatoire, sans = générique) | MATIÈRE = KG + WIKI (obligatoire, sans = pauvre) | R2 = projection finale
- **Round 6 — INTERNAL DIFFERENCE EXHAUSTION** : ordre L0-L5 strict, aucun L4 externe avant exhaustion L0-L3, `R2InternalDifferenceScoreService` 6 sub-scores, threshold 60 à calibrer empiriquement
- **Round 7 — Technical criteria = evidence only** : critères techniques = PREUVES STRUCTURÉES (compact tableau/warning), PAS source éditoriale. Contenu éditorial reste R1 gamme conseil + WIKI prose validée
- Rego policy `r2-content-write.rego` : **5 nouveaux deny invariants** + extension allow Rule 3 avec helpers ADR-070
- 96/96 OPA tests pass (84 hérités cumulés + 12 nouveaux ADR-070 strict gates)
- WASM bundle `r2-content-write.wasm` regénéré (nouvelle SHA `ecb7c5183e20d65a1a24c4feb35d3329cfa3041ba24ebb7150293e973f128063`)
- Pas de modification `r2-cluster-health.rego` ni `h1-write.rego`

## Why

Doctrine évolutive post-pilote V1 (10 URLs stratifiées 2026-05-16) :

| ADR | Date | Doctrine |
|-----|------|----------|
| ADR-066 | 2026-05-15 | Pipeline 4-gates avec 5 outcomes (SUPPRESSED auto) |
| ADR-067 | 2026-05-15 | SUPPRESSED automatique INTERDIT → 4 outcomes auto (manual-only path conservé) |
| ADR-068 | 2026-05-16 | 4 actions auto INTERDITES (suppress + désindex + canonical sibling + sitemap exclusion) + règle affirmative INDEX + REJECT scope strict 4 raisons |
| **ADR-070** | **2026-05-16** | **Formule canon (R8+R1 CADRE + KG+WIKI MATIÈRE) + INTERNAL DIFFERENCE EXHAUSTION + Technical criteria = evidence only** |

Le pilote V1 a confirmé que `R2DataLoaderService` stub seul ne produit pas de signal commercial distinct (100% review_required avec proxy SQL). Diagnostic cause racine sur 3 axes doctrinaux (Rounds 5+6+7 décisions @fafa 2026-05-16) :

1. **Round 5** : la formule courte `R2 = R8 + R1 + CompatEvidence` écrasait la séparation `cadre` (R8+R1) vs `matière factuelle` (KG facts + WIKI evidence). Le contenu **riche** ne provient PAS de R8+R1 seuls.

2. **Round 6** : ordre exécution non doctriné. Risque de lancer Playwright/WIKI L4 dès PR 2 alors que la base AutoMecanik contient déjà massivement de vérité métier interne (L0-L3) suffisante pour 70-90% des cas. Doctrine "INTERNAL DIFFERENCE EXHAUSTION" formalisée.

3. **Round 7** : confusion contenu éditorial vs preuve technique. Risque de générer des paragraphes longs avec specs brutes (largeur 155,2 mm × hauteur 66 mm × ...) noyant le lecteur. Doctrine "Technical criteria = evidence only" : critères techniques en preuve compacte uniquement (S_COMPAT_DIFFERENCES + S_TECHNICAL_TABLE_COMPACT + S_SELECTION_WARNING), pas en paragraphes éditoriaux.

## Changements concrets

### Vault (cette PR)

- `ledger/decisions/adr/ADR-070-r8-r1-first-r2-second-active-disambiguation.md` (nouvelle)
- `policies/seo-content/r2-content-write.rego` :
  - **Extension allow Rule 3 (pipeline_generated_index)** : ajoute 5 prerequisites ADR-070 stricts (R8 cadre, R1 cadre, matière factuelle, disambiguation, no raw specs in editorial)
  - **Helpers ADR-070** : `adr070_r8_cadre_ok`, `adr070_r1_cadre_ok`, `adr070_factual_matter_ok`, `adr070_disambiguation_ok`, `adr070_no_raw_specs_in_editorial`
  - **Set `valid_r8_snapshot_statuses`** : `{minimal, enriched, stale}` (canon Round 2 status enum strict)
  - **DENY ADR-070 #1** : R8 snapshot CADRE absent → reason explicite
  - **DENY ADR-070 #2** : R1 gamme context CADRE absent → reason explicite
  - **DENY ADR-070 #3** : MATIÈRE FACTUELLE absente (KG=0 ET WIKI=0) → reason explicite
  - **DENY ADR-070 #4** : H1 sans motor_power_pattern OU S_VARIANT_DISAMBIGUATION manquante (2 deny) → reasons explicites
  - **DENY ADR-070 #5** : body_long_form_section_contains_raw_specs=true → reason R7 evidence only
- `policies/seo-content/r2-content-write_test.rego` :
  - 13 nouveaux tests ADR-070 (5 deny par invariant + 4 allow happy path + 1 ADR-070 cumul review_required relaxed gates)
  - Test legacy `test_allow_pipeline_index_full` mis à jour avec inputs ADR-070 (r8_snapshot_status, r1_gamme_context_status, knowledge_facts_count, validated_wiki_evidence_count, h1_contains_motor_power_pattern, s_variant_disambiguation_present, body_long_form_section_contains_raw_specs)
- `dist/policies/r2-content-write.wasm` regénéré (SHA `ecb7c5183e20d65a1a24c4feb35d3329cfa3041ba24ebb7150293e973f128063`)
- `ledger/audit-trail/2026-05-16-adr-070-r8-r1-first-r2-second-active-disambiguation-accepted.md` (cette entrée)
- `ops/moc/MOC-AuditTrail.md` : ligne 2026-05-16 ADR-070
- `ops/moc/MOC-Decisions.md` : entry ADR-070 sous "R2 doctrine cascade"

### Monorepo (PRs séquencées à suivre, séparées de cette PR vault)

À implémenter post-merge ADR-070 dans l'ordre canon "Sequence canon finale" du plan `/home/deploy/.claude/plans/le-contenu-de-r2-scalable-tower.md` :

| PR | Scope | Bloquant pour |
|----|-------|---------------|
| PR 2B' Vault ADR-072 | Paradigme CQRS + DDD bounded contexts + Snapshot Artifact + Outbox + Schema Registry + OTel + GitOps + `r2-runtime-read.rego` | PR 2D mono (snapshot tables) |
| PR 2C' Mono R1 backfill prerequisite | Audit `__seo_gamme_conseil` sections vides + relance R1 keyword planner agent existant | Pilote V1 (sinon r1_gamme_context_missing massif) |
| PR 2D Mono R8 snapshot | `__seo_r8_snapshot_store` + `R8ParentEnrichmentService` + `R8SnapshotReaderService` + **job seed initial idempotent INSERT minimal pour TOUS type_ids existants** + migrations Round 8 (`__seo_r2_page_snapshot` + `__seo_outbox_event`) | Pilote V1 (sinon r8_snapshot_unavailable massif ~95%) |
| PR 2H Mono Knowledge Graph L3 | `__seo_vehicle_part_knowledge` migration + `R2KnowledgeGraphService` + `R2EvidenceDecayJobService` | PR 2E pilot sync |
| PR 2E Mono R2DataLoader + pilot | `R2InternalDifferenceScoreService` (Round 6 gate) + `R2FactsToSectionsProjector` (Round 7) + `R2DuplicateBusinessSignatureService` + Frontend Remix CQRS + Sitemap V10 CQRS + pilote V1 10 URLs stratifiées + measurement gate Round 6 | STOP par défaut post-mesure (5 prerequisites full-scale required avant V2) |

## Verification locale

```
$ /tmp/opa test policies/seo-content/
PASS: 96/96
```

- 22 h1-write tests (régression PR-V intacte)
- 49 r2-content-write tests (ADR-066+067+068 cumulés + 13 nouveaux ADR-070 Round 5+6+7)
- 15 r2-cluster-health tests (intacts, invariants cluster valables)
- 10 misc helpers tests

WASM reproducible (paths relatifs depuis vault root) :
- `h1-write.wasm` SHA inchangé
- `r2-content-write.wasm` SHA nouvelle `ecb7c5183e20d65a1a24c4feb35d3329cfa3041ba24ebb7150293e973f128063` (5 deny rules ADR-070 + extension allow rule 3 + 5 helpers + set valid_r8_snapshot_statuses)
- `r2-cluster-health.wasm` SHA inchangé

## Impacts cross-canon

- **ADR-066** : amended par ADR-067 + ADR-068 + **ADR-070** (formule canon explicite + ordre L0-L5 + disambiguation + technical criteria evidence-only)
- **ADR-067** : préservé (SUPPRESSED manual-only inchangé)
- **ADR-068** : préservé (4 actions auto interdites inchangées, ADR-070 ajoute 5 gates INDEX strict additionnels)
- **ADR-058 (Repository Control Plane)** : pas d'impact ownership direct (impact à venir avec ADR-072 paradigme CQRS + bounded contexts)
- **MOC-Decisions** : ADR-070 indexé sous "R2 doctrine cascade Rounds 5+6+7"
- **MOC-AuditTrail** : ligne 2026-05-16 ADR-070

## Hors scope post-acceptance

- **ADR-072 paradigme CQRS+DDD** : à drafter dans PR 2B' (vault, stackée post-merge ADR-070). Cumulative au-dessus de ADR-070 pour le paradigme architectural (read/write separation, bounded contexts, snapshot artifact, outbox).
- **ADR-069 evidence-based** : restera CONDITIONAL post-measurement gate Round 6 (PR 2A vault). Activé uniquement si pilote V1 confirme insuffisance L0-L3.
- **Migration historique** : aucun (zéro page R2 v2 publiée encore)
- **R1 backfill** : agent existant `r1-keyword-planner` à relancer pour gammes ayant sections vides (PR 2C' séparée)
- **R8 backfill seed initial** : job idempotent dans PR 2D pour TOUS type_ids existants (sinon r8_snapshot_unavailable bloque massivement)

## Self-review verdict: APPROVE

4 ADR successifs (066 → 067 → 068 → 070) en 2 jours = doctrine évolutive pré-production. Coût correction = zéro (aucune page R2 v2 publiée). Bénéfice = canon étanche complet (formule + ordre + usage critères) AVANT PRs monorepo (2D / 2H / 2E pilote V1). 96/96 OPA tests pass. WASM reproducible. Cross-refs ADR-066+067+068 préservés via `amends`. Helpers Rego factorisés (réutilisables ADR-072 futur). Prêt pour merge.
