---
type: state-snapshot
date: 2026-04-22
owner: Fafa
session_id: rollout-9-gammes-consolidation
scope: État final pipeline SEO + 9 gammes validées PASS 9/9 phases
tags: [pipeline, rollout, snapshot, seo, state]
continues_from:
  - 2026-04-21-pipeline-content-hardening.md
  - 2026-04-22-pipeline-quality-hardening-p2.md
  - 2026-04-22-alias-expansions-batch-preventif.md
  - 2026-04-22-r6-antimistakes-cross-contamination-fix.md
---

# Rollout 9 gammes + État final du pipeline SEO

## TL;DR

9 gammes ont été rolloutées avec succès (PASS 9/9 phases QA) depuis l'installation de la Phase 9 QA éditoriale. Le pipeline est maintenant production-ready avec 9 layers de protection, un dictionnaire d'aliases SEO centralisé (73 gammes / 228 aliases), et un fix majeur du bug de cross-contamination anti_mistakes qui polluait 7+ gammes.

## 9 gammes validées

| # | Gamme | pg_id | Raw KW | Classifiés | V-Level | Verdict |
|---|---|---|---|---|---|---|
| 1 | filtre-a-huile | 7 | 1978 | 1522 | — | ✅ PASS |
| 2 | filtre-a-air | 8 | 849 | 864 | 855 (22 V2) | ✅ PASS |
| 3 | filtre-a-carburant | 9 | 940 | 977 | 888 (27 V2) | ✅ PASS |
| 4 | filtre-de-boite-auto | 416 | 10 | 10 | 0 (niche) | ✅ PASS |
| 5 | filtre-d-habitacle | 424 | 1616 | 1477 | 1014 (11 V2) | ✅ PASS |
| 6 | etrier-de-frein | 78 | 630 | 630 | 455 (6 V2) | ✅ PASS |
| 7 | temoin-d-usure | 407 | 39 | 39 | 0 (niche) | ✅ PASS |
| 8 | machoires-de-frein | 70 | 47 | 47 | 0 (niche) | ✅ PASS |
| 9 | cylindre-de-roue | 277 | 69 | 69 | 0 (niche) | ✅ PASS |
| 10 | interrupteur-des-feux-de-freins | 806 | 170 | 170 | 241 (5 V2) | ✅ PASS |

**Total** : 6348 KW bruts traités, 5805 classifiés, 3553 V-Level rows produites (72 V2 champions).

## Stack final du pipeline

```
╔══════════════════════════════════════════════════════════════════════════╗
║  9 LAYERS DE PROTECTION                                                  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  1. Contrat Zod v4 SSOT           (refuse args content==title)           ║
║  2. Field catalog ×22 args         (WriteGuard ownership)                ║
║  3. CHECK constraints ×8 VALID     (invariants DB)                       ║
║  4. Triggers DB ×10 actifs         (accents + gatekeeper + cascade)      ║
║  5. Observability                  (v_gamme_content_orphans,             ║
║                                     v_kw_pipeline_status, Phase 9 QA)    ║
║  6. File lifecycle                 (inbox → processed/failed + JSON)     ║
║  7. Alias expansions centralisé    (73 gammes / 228 aliases)             ║
║  8. Bug apostrophe fix             (+546% matching pour d'/a')           ║
║  9. R6 anti-contamination          (4 sources neutralisées)              ║
╚══════════════════════════════════════════════════════════════════════════╝
```

## Phase 9 QA éditoriale (gates systémiques)

| Gate | Règle | Impact |
|---|---|---|
| q2 | Accents FR normalisés | trigger DB auto-correctif |
| q3 | Titres non pluriel bizarre | UPDATE ciblé + monitoring |
| q4 | R4 composition ≠ verbes | fix manuel par gamme |
| q5 | R6 anti_mistakes cohérent R3↔R6 | fix Q5 manuel (voir P3 backlog) |
| q6 | 0 string vide dans arrays | trigger DB auto-correctif |
| q7 | 0 fragment scraping | UPDATE ciblé + regex detection |

## 4 sources R6 contamination neutralisées (2026-04-22)

1. **`findGuideDocId` fuzzy match** — blacklist mots génériques + seuil adaptatif (1 ou 2 selon len)
2. **Extraction regex "Erreurs à éviter"** — retirée, source unique v4Data.antiMistakes
3. **Extraction regex "Solutions"** — retirée (bloc diagnostic partagé)
4. **`sanitizeStringArray`** — +2 regex parasitic (`**Symptôme**:`, `**Coût**:` etc.)

## Observations pattern

### Pluriel vs singulier SEO

CSV Google Ads utilise souvent le singulier alors que pg_alias est pluriel (`machoires-de-frein` vs kw "machoire de frein"). Dict étendu systématiquement avec variantes singulier.

### Gammes freinage fragiles

Les gammes freinage non-disques (machoires, étrier, flexible, tambour, cylindre-roue, temoin-usure, interrupteur-feux, cable-frein-main, maître-cylindre) sont systématiquement contaminées par `choisir-disques-frein.md` via le fuzzy match faible. Fix #1 (blacklist GENERIC_WORDS) les sauve.

### Corpus niche (< 100 KW)

Plusieurs gammes ont un corpus Google Ads très petit (filtre-de-boite-auto: 15, temoin-d-usure: 53, machoires-de-frein: 56, cylindre-de-roue: 71, interrupteur-feux: 188). Ces gammes sont pleinement fonctionnelles mais **V-Level reste souvent à 0** faute de KW véhicule matchables dans le petit pool.

## Fichiers touchés (cumul 3 sessions)

### Backend (code TS)
- `backend/src/config/rag-gamme-contract-v4.schema.ts` (nouveau, Zod SSOT)
- `backend/src/modules/admin/services/rag-gamme-parser.service.ts` (nouveau, parser unifié)
- `backend/src/modules/rag-shared/rag-shared.module.ts` (nouveau)
- `backend/src/modules/seo/services/reference.service.ts` (writer clean)
- `backend/src/modules/admin/services/r1-enricher.service.ts` (parser v4)
- `backend/src/modules/admin/services/buying-guide/buying-guide-rag-fetcher.service.ts` (apostrophe + fuzzy + fallback retirés)
- `backend/src/modules/admin/services/buying-guide/buying-guide-section-extractor.service.ts` (parasitic patterns)
- `backend/src/config/field-catalog.constants.ts` (+22 args fields)

### Config
- `config/rag-alias-expansions.yaml` (nouveau, 73 gammes / 228 aliases)

### Scripts
- `scripts/seo/import-gads-kp.py` (load dict + fix normalize_kw apostrophes + lifecycle)
- `scripts/seo/recalculate_vlevel.py` (unchanged, utilise RPC extract_vehicle_keywords)

### DB (8 migrations Supabase appliquées)
- `p1_check_args_content_differs_from_title`
- `p1_2_orphan_monitoring_and_soft_validation`
- `p1_3_trigger_invalidate_gatekeeper_on_content_change`
- `p1_4_archive_and_cleanup_orphans`
- `p1_4_3_validate_r1_check_constraints_strict`
- `p1_4_4_cascade_gamme_delete_content_archive`
- `p1_6_deprecate_shadow_fields_and_monitor_pipeline`
- `p2_restore_french_accents_function` + `p2_trigger_auto_restore_accents`
- `p2_extract_vehicle_keywords_rpc_v3_optimized`
- `p2_match_keywords_batch_clean_alias`
- `p2b_v_kw_pipeline_status_r4_kp_optional`

### RAG (7 fichiers .md modifiés ou fixés)
- 3 variants ad-hoc ajoutés puis retirés (migration vers dict central)
- 4 phase5_enrichment blocs cassés retirés (YAML valide)
- 3 arguments[].content injectés (filtre-a-huile family)

### Évidence packs vault (4 documents)
- `2026-04-21-pipeline-content-hardening.md`
- `2026-04-22-pipeline-quality-hardening-p2.md`
- `2026-04-22-alias-expansions-batch-preventif.md`
- `2026-04-22-r6-antimistakes-cross-contamination-fix.md`
- `2026-04-22-rollout-9-gammes-pipeline-state.md` (celui-ci)

## Backlog P3 (non traité)

1. Nettoyer `selection.anti_mistakes` des RAG pour contenir de vraies erreurs à éviter (pas des mots interdits de publicité).
2. Investiguer `BuyingGuideEnricherService.upsertBuyingGuide` qui ne persiste pas `sgpg_anti_mistakes` même quand la réponse API en contient.
3. Ajouter tests fixtures snapshot (filtre-a-huile comme canonical) pour prévenir régressions.
4. Dashboard admin `/admin/pipeline-status` consommant `v_kw_pipeline_status` + `v_gamme_content_orphans`.

## Rollout status

**9/232 gammes G1/G2 validées PASS 9/9 phases** (3.9%). Prêt pour rollout accéléré des 223 restantes — le pipeline durci élimine désormais les frictions rencontrées sur les 4 premières.

---

_Snapshot 2026-04-22, fin de session rollout filtres + freinage niche._
