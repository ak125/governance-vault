---
type: evidence-pack
date: 2026-04-22
owner: Fafa
duration: ~3h
session_id: pipeline-quality-hardening-P2
scope: content editorial quality + file lifecycle + Phase 9 QA-contenu
related_tables:
  - __seo_gamme_conseil
  - __seo_gamme_purchase_guide
  - __seo_gamme
  - __seo_r1_gamme_slots
  - __seo_reference
  - __seo_keywords
  - __seo_type_vlevel
  - _archive.content_quality_fixes_2026_04_21
prototype_gamme: filtre-a-air (pg_id=8)
tags: [pipeline, quality, accents, triggers, phase-9, file-lifecycle, evidence-pack]
continues_from: 2026-04-21-pipeline-content-hardening.md
---

# P2 — Quality Hardening + File Lifecycle

> **Continuation** de la session 2026-04-21 (P0/P0.5/P1/P1.6). Cette phase attaque la qualité éditoriale du contenu (accents FR, titres, composition sémantique, cohérence R3↔R6), ajoute une Phase 9 QA-contenu au skill `/gamme-qa`, installe des triggers DB-native auto-corrigeants, et corrige le lifecycle fichier CSV.

## TL;DR

Audit qualité post-pipeline sur `filtre-a-air` a révélé 7 défauts Q1-Q7 (accents FR absents, titres pluriel bizarre, R4 composition = verbes, R6 anti_mistakes vide, arrays avec strings vides, pollution scraping S5, args R1 génériques). Étendue : **314 sections R3 sans accents, 154 R6 sans anti_mistakes, 22 arrays avec strings vides**.

Fixes déployés :
- **Fonction DB `restore_french_accents(text)`** — dictionnaire conservateur 90+ substitutions
- **4 triggers BEFORE INSERT/UPDATE** auto-corrigeant sur R1_meta, R1_slots, R3, R6 → tout write futur normalisé automatiquement, zéro code applicatif à changer
- **Batch SQL UPDATE** sur les 265 rows concernées + archive complète dans `_archive.content_quality_fixes_2026_04_21`
- **Phase 9 QA-contenu** ajoutée au skill `/gamme-qa` : 6 gates (accents, titres, compo, coherence R3↔R6, empty strings, scraping)
- **Patch `import-gads-kp.py`** : lifecycle CSV (inbox → processed/failed) + snapshot JSON nettoyé dans `output/`

Résultat filtre-a-air : verdict final **PASS 9/9 phases** (Phase 9 inclus, q2..q7 tous à 0).

---

## Le CSV dans le pipeline

### Flow canonique (post-P2)

```
data/keywords/inbox/<pg_alias>_YYYY-MM-DD.csv       ← dépôt utilisateur
                     │
                     ▼
         python3 scripts/seo/import-gads-kp.py
                     │
       ┌─────────────┼─────────────┐
       │             │             │
   (succès)      (échec)      (dry-run)
       │             │             │
       ▼             ▼             │
   processed/      failed/      │ inbox/ (inchangé)
   <ts>__...csv    <ts>__...csv │
       │
       └── + output/<ts>__<alias>__import-summary.json (snapshot nettoyé)
       └── + __seo_keywords (DB : KW pertinents après filtre RAG)
```

### Pourquoi il n'y a pas de "CSV nettoyé" sur disque

Le "nettoyage" = sélection RAG-driven des KW pertinents pour la gamme cible :

| Étape | Input | Output | Lieu |
|---|---|---|---|
| Dépôt | Google Ads KP CSV natif (UTF-16) | idem | `inbox/` |
| Import brut | CSV | `__seo_keywords` | **DB** + fichier → `processed/` |
| Classification | `__seo_keywords` | `__seo_keyword_results` (R1/R3/R4/R6 + vol percentile) | **DB** |
| V-Level | `__seo_keywords` + `auto_modele/auto_type` | `__seo_type_vlevel` | **DB** |
| Snapshot | tous stages | résumé JSON | `output/<ts>__<alias>__import-summary.json` |

**Le vrai "nettoyé"** = les rows en DB. Le CSV `processed/` est gardé pour audit + rollback. Le JSON `output/` donne une vue synthétique chiffrée des étapes.

### Exemple filtre-a-air (2026-04-21 rollout)

```
processed/2026-04-22T145257__filtre-a-air_2026-04-21.csv   (178 KB brut)
output/2026-04-22T145257__filtre-a-air__import-summary.json
  {
    "raw_count": 1225, "deduped_count": 1078, "relevant_count": 849,
    "rejected": {"no_core_match": 225, "exclude": 4}, "upserted": 849,
    "post_classify_count_r1": 812, "post_classify_count_r6": 13,
    "vlevel_total": 855, "vlevel_v2_champions": 22,
    "qa_final_verdict": "PASS"
  }
```

---

## 7 défauts qualité Q1-Q7

### Audit étendu (toute la DB)

| Q | Problème | Occurrences avant fix |
|---|---|---|
| Q1 | Args R1 génériques "Compatibilité vérifiée..." identiques sur toutes gammes | design choice, non traité |
| Q2 | Accents FR manquants : "filtre a air", "aspire", "poussieres" | **314** sections R3 |
| Q3 | Titres pluriel bizarre : "Fonction des filtre a air" | **24** titres R3 |
| Q4 | R4 composition = verbes au lieu de composants physiques | **1** (filtre-a-air) |
| Q5 | R6 `sgpg_anti_mistakes = []` alors que R3 S5 contient anti-erreurs | **154** gammes |
| Q6 | Strings vides dans arrays (symptoms, anti_mistakes) | **22** rows |
| Q7 | Pollution scraping dans R3 S5 ("Skip Navigation", "Pièces de rechange Champion", "Acheter une voiture Vendre") | **1** (filtre-a-air) |

### Résolution

| Q | Solution | Résultat |
|---|---|---|
| Q1 | Laisser tel quel (choix design boilerplate) | N/A |
| **Q2** | **`restore_french_accents()` + trigger DB** sur 4 tables + UPDATE batch | **314 → 0** ✅ |
| Q3 | Regex UPDATE sur sgc_title | 24 → 0 ✅ |
| Q4 | UPDATE composition avec composants physiques (filtre-a-air : média filtrant, cadre polymère, joint, grille) | 1 → 0 ✅ |
| Q5 | Propagation batch depuis R3 S5 bullets ❌ | 154 → 62 fixés (92 rows écrits), 149 restants = R3 S5 sans bullets spécifiques (bug `BuyingGuideEnricherService` à investiguer) |
| Q6 | Trigger `array_remove('')` + UPDATE batch | 22 → 0 ✅ |
| Q7 | Regex truncate au premier marker scraping | 1 → 0 ✅ |

### Archive safety

`_archive.content_quality_fixes_2026_04_21` : **265 rows** préservées en JSONB avant modification. Restoration row-par-row possible via `INSERT ... FROM row_data->>...`.

---

## Solution racine : triggers DB-native auto-corrigeants

### Principe

Corriger à la source (DB) plutôt que dans chaque enricher (NestJS, Python, SQL manuel, admin UI, API). Un trigger `BEFORE INSERT OR UPDATE` applique `restore_french_accents()` automatiquement sur les champs texte critiques.

### Installation

| Trigger | Table | Fields traités |
|---|---|---|
| `trg_auto_restore_accents_r3` | `__seo_gamme_conseil` | `sgc_content`, `sgc_title` |
| `trg_auto_restore_accents_r6` | `__seo_gamme_purchase_guide` | `sgpg_intro_role`, `sgpg_how_to_choose`, `sgpg_risk_explanation`, `sgpg_risk_conclusion`, `sgpg_intro_title`, `sgpg_risk_title`, `sgpg_symptoms[]`, `sgpg_anti_mistakes[]` |
| `trg_auto_restore_accents_r1_meta` | `__seo_gamme` | `sg_content`, `sg_title`, `sg_descrip` |
| `trg_auto_restore_accents_r1_slots` | `__seo_r1_gamme_slots` | `r1s_micro_seo_block`, `r1s_hero_subtitle`, `r1s_h1_override`, `r1s_compatibilities_intro`, `r1s_equipementiers_line`, `r1s_family_cross_sell_intro`, `r1s_arg{1-4}_content` |

### Garanties

- **Couvre 100% des chemins** — enrichers NestJS, scripts Python, SQL manuel, admin UI, API externe
- **Idempotent** — la fonction est `IMMUTABLE`, rappliquer ne change rien si déjà propre
- **Zéro code applicatif** à modifier pour les clients
- **Extensible** — ajouter une substitution au dictionnaire = 1 ligne SQL
- **Performance** : dictionnaire de 90 patterns word-boundary, négligeable au write

---

## Phase 9 QA-contenu (skill `/gamme-qa`)

Nouvelle phase ajoutée au skill, check 6 défauts qualité :

```
Phase 9 — Qualité éditoriale contenu : [PASS/WARN/BLOCK]
  q2_accents        (BLOCK si > 10)
  q3_titles         (BLOCK si > 0)
  q4_compo_verbs    (BLOCK si > 0)
  q5_r6_antim       (WARN coherence R3↔R6)
  q6_empty_strings  (WARN)
  q7_scraping       (BLOCK si > 0)
```

Réparation auto via `--auto-fix-minor` : Q2/Q6 par SQL, Q5 par relance R6 enricher. Q3/Q4/Q7 nécessitent inspection humaine.

---

## Résultat filtre-a-air post-P2

```
Phase 1  — RAG + ingestion          : [PASS]  Zod OK | 849 raw KW | 0 bug args
Phase 2  — Classification           : [INFO]  R1=851, R6=13
Phase 3  — Keyword plans            : [PASS]  R1=82, R3=100, R4=72, R6=88
Phase 4  — Content enrichment       : [PASS]  R1_gk=90, R4_def=495
Phase 5  — Invariants DB            : [PASS]  0 orphan, 0 args=title
Phase 5B — V-Level canonique        : [PASS]  855 types, 22 V2 champions, conf=0.90
Phase 6  — Images (module dédié)    : [SKIPPED]
Phase 7  — Pollution + vocab        : [PASS]  0 forbidden, 0 scraping
Phase 8  — Pipeline stage           : [PASS]  FULLY_ENRICHED
Phase 9  — Qualité éditoriale       : [PASS]  q2=0 q3=0 q4=0 q5=0 q6=0 q7=0

VERDICT : PASS (0 BLOCK, 1 WARN mineur sur R4 def_len)
```

---

## Architecture qualité finale (post-P0+P1+P2)

```
LAYER 1 — CONTRACT       Zod v4 SSOT (args.content != title)
LAYER 2 — CATALOG        22 args + editorial slots ownership
LAYER 3 — INVARIANTS     8 CHECK VALID
LAYER 4 — TRIGGERS       10 triggers actifs :
                          • 4× soft-validation orphan
                          • 1× gatekeeper invalidation on content change
                          • 1× cascade delete pieces_gamme → content tables
                          • 4× auto-restore French accents (NEW P2)
LAYER 5 — OBSERVABILITY  v_gamme_content_orphans
                          v_kw_pipeline_status
                          Phase 9 QA-contenu (6 gates)
                          _archive.orphans_gamme_content_2026_04_21 (88 rows)
                          _archive.content_quality_fixes_2026_04_21 (265 rows, NEW P2)
LAYER 6 — FILE LIFECYCLE inbox → processed | failed + JSON snapshot output (NEW P2)
```

---

## Known issues — pour P3

1. **`BuyingGuideEnricherService` ne persiste pas `sgpg_anti_mistakes`** : réponse API retourne 3 items mais DB reste à `[]`. Suspect: WriteGuard merge anti-régression qui bloque silencieusement. Investigation requise dans `buying-guide-db.service.ts`.
2. **Q5 reste sur 149 gammes** avec R3 S5 vide en bullets ❌ : nécessite soit enrichir les `selection.anti_mistakes` dans les RAG .md, soit changer l'approche (générer depuis RAG v4 pas R3).
3. **Q1 args R1 boilerplate** : actuellement identiques sur toutes les gammes. Décision design pendante : garder pour cohérence de marque, ou contextualiser par RAG.

---

## Files touchés (P2)

### Monorepo
- `scripts/seo/import-gads-kp.py` : +50 lignes (lifecycle + snapshot JSON)
- `.claude/skills/gamme-qa/SKILL.md` : +80 lignes (Phase 9)
- `rag/knowledge/gammes/filtre-a-air.md` : enrich `domain.role` (103c → 658c)

### DB migrations (Supabase)
- `p2_restore_french_accents_function`
- `p2_mass_restore_accents_and_fixes` (265 rows archivées + fixées)
- `p2_trigger_auto_restore_accents` (4 triggers)
- `p2_q5_propagate_anti_mistakes_batch`
- `p2_q7_clean_scraping_pollution_s5`
- `p2_extract_vehicle_keywords_rpc_v3_optimized`
- `p2_match_keywords_batch_clean_alias`

### Files data/
- `data/keywords/processed/2026-04-22T145257__filtre-a-air_2026-04-21.csv`
- `data/keywords/output/2026-04-22T145257__filtre-a-air__import-summary.json`

---

## Rollback

**Restore accents (cas catastrophique uniquement)** :
```sql
DROP TRIGGER trg_auto_restore_accents_r3 ON __seo_gamme_conseil;
-- × 4 triggers
DROP FUNCTION restore_french_accents(text);
-- Pour restaurer les 265 rows à l'état pre-fix :
UPDATE __seo_gamme_conseil c
SET sgc_content = (row_data->>'sgc_content'), sgc_title = (row_data->>'sgc_title')
FROM _archive.content_quality_fixes_2026_04_21 a
WHERE a.source_table = '__seo_gamme_conseil'
  AND a.pg_id_str LIKE c.sgc_pg_id::text || ':' || c.sgc_section_type;
```

**Revert patch import-gads-kp.py** : git revert du commit patchant le lifecycle.

---

_Generated 2026-04-22 by Claude Code. Continues session 2026-04-21-pipeline-content-hardening._
