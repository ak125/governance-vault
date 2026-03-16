# Phase 3 — Full Structural Audit (265 tables)

> **Version** : 1.5.0
> **Date** : 2026-03-15
> **Statut** : **CLOTURE** — Toutes vagues (2-6) terminees. 9 FK validees, 3 PK ajoutees, 15 shadow cols, 14 tables droppees (3 legacy + 1 deprecated + 1 backup + 9 orphelines). auto_type code DEFERRED (gain nul).
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`
> **Methode** : `information_schema` + `pg_constraint` + `pg_stat_user_tables` + grep backend
> **Perimetre** : toutes les 265 tables du schema `public` (177 avec donnees, 88 vides)
> **Conventions** : evidence = measured / inferred / suspected. Aucun verdict d'action sans gate prealable.

---

## 1. Executive Summary

| Metrique | Valeur | Evidence |
|----------|--------|----------|
| Tables schema public | **265** (342 tous schemas incl. auth/storage/extensions + 38 vues) | measured |
| Taille totale | **~86 GB** | measured |
| Tables avec donnees (>0 rows) | **177** | measured (post-cleanup 2026-03-15) |
| Tables vides (0 rows) | **88** | measured (post-cleanup — 13 orphelines droppees) |
| Tables sans PK | **0** (~~3~~ — toutes fixees V4a) | measured |
| Tables avec FK | **~34** (~~25~~ + 6 Cat A + 3 Cat B/C validees) | measured |
| Tables avec dette type TEXT | **~12** (~~15~~ — `pieces_price` fixee V4b/V5a, `auto_type` shadow cols exists) | measured |

### Problemes critiques (P0)

| # | Probleme | Tables | Impact | Evidence |
|---|----------|--------|--------|----------|
| P0-1 | ~~**PK manquante**~~ | ~~`pieces_relation_type`, `pieces_media_img`~~ | ✅ FIXED V4a (PK ajoutees) | measured |
| P0-2 | ~~**Prix en TEXT**~~ | ~~`pieces_price` (11 prix)~~ | ✅ FIXED V4b (shadow cols _n) + V5a (code migre) | measured |
| P0-3 | **IDs en TEXT** | `___xtr_msg` (7 ID), `auto_type` (4 ID) — code deferred | Shadow cols existent, code V5 partiel | measured |
| P0-4 | **~100 tables vides** | Voir section 5 | Classification requise | measured |

### Problemes importants (P1)

| # | Probleme | Tables | Impact | Evidence |
|---|----------|--------|--------|----------|
| P1-1 | ~~**0 FK sur catalogue**~~ | ~~6 tables pieces_*~~ | ✅ FIXED V4c (FK validees sur *_piece_id_i) | measured |
| P1-2 | **Dates en TEXT** | `auto_type` (4 dates) — `pieces_price` ✅ FIXED (shadow cols) | auto_type deferred | measured |
| P1-3 | ~~**Tables legacy**~~ | ~~`___config_old`, `pieces_marque_next`~~ droppees, `__cross_gamme_car` depreciee | ✅ FIXED V3+V5d | measured |

---

## 2. Tables Tier 1 — Catalogue MassDoc (>100 MB) — Etat final post-remediation

| Table | Taille | Rows | PK | FK | ID TEXT | Prix TEXT | SoT | MassDoc Role | Verdict | Gate | Readiness MassDoc |
|-------|--------|------|----|----|--------|----------|-----|-------------|---------|------|-----------------|
| pieces_relation_criteria | 33 GB | 157M | ✓ | **1** | 0 | 0 | source | source_catalog | ✅ FK DONE (rcp_type_id→auto_type) | ready | **ready** |
| pieces_ref_search | 16 GB | 73M | ✓ | **1** | 0 | 0 | derived | derived | ✅ FK DONE | ready | **ready** |
| ___xtr_msg | 11 GB | 15M | ✓ | 0 | **7** | 0 | legacy | non_tecdoc | TYPE_MIGRATION_REQUIRED | needs_validation | out_of_scope |
| pieces_relation_type | 9.7 GB | 146M | ✓ | **2** | 0 | 0 | source | source_catalog | ✅ PK+FK DONE | ready | **ready** |
| pieces_criteria | 5.4 GB | 17.6M | ✓ | **1** | **5** | 0 | source | source_catalog | ✅ FK DONE (IDs TEXT deferred) | ready | **ready** |
| pieces | 1.4 GB | 4M | ✓ | **2** | 0 | 0 | **source** | source_catalog | REFERENCE | ready | **ready** |
| pieces_media_img | 953 MB | 4.6M | ✓ | **1** | 0 | 0 | source | source_catalog | ✅ PK+FK DONE | ready | **ready** |
| pieces_ref_ean | 512 MB | 3M | ✓ | **1** | 0 | 0 | source | source_catalog | ✅ FK DONE | ready | **ready** |
| pieces_price | 354 MB | 442K | ✓ | **1** | 0 | 0 | source | source_catalog | ✅ FK+SHADOW DONE (code V5a) | ready | **ready** |
| pieces_list | 302 MB | 1.8M | ✓ | **1** | 0 | 0 | source | source_catalog | ✅ FK DONE | ready | **ready** |
| __seo_page | 114 MB | 322K | ✓ | 1 | 0 | 0 | reference | seo_dep | OK | ready | ready_with_guardrails |

**Legende** :
- **Verdict** = nature du probleme structurel (PK_STRATEGY_REQUIRED, TYPE_MIGRATION_REQUIRED, FK_CANDIDATE_A/B/C, OK, REFERENCE)
- **Gate** = statut d'execution immediat (`ready` = action possible, `needs_validation` = audit prealable requis, `blocked` = prerequis non rempli)
- **Readiness MassDoc** = statut metier vis-a-vis de l'update MassDoc (`ready`, `ready_with_guardrails`, `blocked_by_pk`, `blocked_by_type_debt`, `blocked_by_fk_uncertainty`, `blocked_by_duplicate_risk`, `out_of_scope`)
- **SoT** = `source` (table primaire canonique) / `derived` (projection/recherche, pas source d'integrite) / `reference` (surface dependante, jamais source catalogue) / `legacy` / `unknown`

> `ready_with_guardrails` = exploitable dans le pipeline MassDoc comme surface derivee/projection, jamais comme source canonique catalogue.

### Strategie PK — ✅ TOUTES RESOLUES V4a

| Table | Rows | Strategy appliquee | Status |
|-------|------|--------------------|--------|
| `pieces_relation_type` | 146M | table swap batch (v2 with composite PK `rtp_type_id, rtp_piece_id`) | ✅ DONE |
| `pieces_media_img` | 4.6M | dedup 10 CSV headers + composite PK `(pmi_piece_id, pmi_name)` | ✅ DONE |
| `rm_rebuild_queue` | 0 | trivial PK `(rmrq_gamme_id, rmrq_vehicle_id)` | ✅ DONE |

---

## 3. Tables Tier 2 — Metier (1 MB — 100 MB)

| Table | Taille | Rows | PK | FK | Domaine | MassDoc Role | Verdict | Gate |
|-------|--------|------|----|----|---------|-------------|---------|------|
| __sitemap_p_link | 92 MB | 473K | ✓ | 0 | SEO | seo_dep | OK | ready |
| __cross_gamme_car_new | 41 MB | 182K | ✓ | 0 | Cross | derived | ✅ UNIFIED (sole table) | ready |
| auto_type_number_code | 37 MB | 165K | ✓ | 0 | Vehicle | lookup | OK | ready |
| auto_type | 37 MB | 49K | ✓ | 0 | Vehicle | source_catalog | TYPE_MIGRATION_REQUIRED | needs_validation |
| ___xtr_customer | 34 MB | 59K | ✓ | 0 | XTR | non_tecdoc | TYPE_MIGRATION_REQUIRED | needs_validation |
| ___xtr_customer_*_address | 29 MB x2 | 59K | ✓ | 0 | XTR | non_tecdoc | OK | ready |
| seo_link_impressions | 25 MB | 104K | ✓ | 0 | SEO | non_tecdoc | OK | ready |
| __seo_gamme_conseil | 18 MB | 2.2K | ✓ | 0 | SEO | seo_dep | OK | ready |
| pieces_criteria_link | 18 MB | 77K | ✓ | 0 | Catalog | source_catalog | TYPE_MIGRATION_REQUIRED | needs_validation |
| ~~__cross_gamme_car_deprecated~~ | — | — | — | — | Cross | — | ✅ DROPPED (2026-03-15) | — |
| __seo_keywords | 11 MB | 4.6K | ✓ | 0 | SEO | seo_dep | OK | ready |
| __seo_keyword_type_mapping | 11 MB | **0** | ✓ | 1 | SEO | seo_dep | EMPTY_ACTIVE_DESIGN | ready |
| pieces_gamme | 10 MB | 9.7K | ✓ | 0 | Catalog | source_catalog | TYPE_MIGRATION_REQUIRED | needs_validation |
| cars_engine | 10 MB | 36K | ✓ | 0 | Vehicle | lookup | OK | ready |

---

## 4. Tables Tier 3 — Config/Lookup/Small (<1 MB, >0 rows)

~60 tables actives. Toutes ont des PK. Points notables :

| Table | Rows | Probleme | MassDoc Role | Verdict | Gate |
|-------|------|----------|-------------|---------|------|
| ___xtr_order_line | 2.5K | 20 prix TEXT | non_tecdoc | TYPE_MIGRATION_REQUIRED | needs_validation |
| ___xtr_order | 1.6K | 8 prix TEXT | non_tecdoc | TYPE_MIGRATION_REQUIRED | needs_validation |
| ~~___config_old~~ | — | ~~Legacy~~ | — | ✅ DROPPED V3 | — |
| pieces_marque | 992 | 15 TEXT | source_catalog | TYPE_MIGRATION_REQUIRED | needs_validation |
| pieces_criteria_group | 4.3K | 3 ID TEXT | source_catalog | TYPE_MIGRATION_REQUIRED | needs_validation |
| auto_modele | 5.7K | 21 TEXT | source_catalog | TYPE_MIGRATION_REQUIRED | needs_validation |
| ___xtr_invoice* | 1 | 8 prix TEXT | non_tecdoc | TYPE_MIGRATION_REQUIRED | needs_validation |
| pieces_details | 1 | 5 ID TEXT | source_catalog | NEAR_EMPTY | needs_validation |
| pieces_ref_oem | 1 | — | source_catalog | NEAR_EMPTY | needs_validation |
| rm_rebuild_queue | 0 | ~~no PK~~ | non_tecdoc | ✅ PK DONE V4a | ready |

---

## 5. Tables vides (0 rows) — Classification

| Classification | Count | Critere | Action |
|---------------|-------|---------|--------|
| **EMPTY_ACTIVE_DESIGN** | **~36** | Infrastructure deployee, consumers code/RPCs confirmes | KEEP |
| **EMPTY_STAGING_REQUIRED** | ~10 | `stg_*`, `__staging_*`, `import_*` — pipeline import | KEEP |
| **EMPTY_OPTIONAL_FEATURE** | **~19** | Features non activees (marketing, video, commerce/support) | KEEP, monitor |
| ~~**EMPTY_ORPHAN_SUSPECT**~~ | **0** | ~~10~~ — tous reclasses (ACTIVE_DESIGN ou DROPPED) | ✅ RESOLVED |
| ~~**EMPTY_DROP_CANDIDATE**~~ | **0** | ~~8~~ — 9 droppees (monitoring + misc), 4 reclassees OPTIONAL | ✅ RESOLVED |

### Detail par groupe

| Groupe | Classification | Tables | Exemples |
|--------|---------------|--------|----------|
| Import pipeline | EMPTY_STAGING_REQUIRED | 10 | `import_batch`, `stg_*`, `__staging_*`, `__import_*` |
| Normalization | EMPTY_ACTIVE_DESIGN | 6 | `norm_article/brand/vehicle`, `natural_key_*` |
| Cross-reference | EMPTY_ACTIVE_DESIGN | 3 | `xref_article/brand/vehicle` |
| Decision engine | EMPTY_ACTIVE_DESIGN | 3 | `decision_article/brand/compat` |
| RM partitions | EMPTY_ACTIVE_DESIGN | 7 | `rm_listing_products_g*` |
| Knowledge graph | EMPTY_OPTIONAL_FEATURE | 8 | `kg_cases`, `kg_*_history`, `kg_*_log` |
| Marketing | EMPTY_OPTIONAL_FEATURE | 6 | `__marketing_campaigns/weekly_plans/...` |
| Video | EMPTY_OPTIONAL_FEATURE | 3 | `__video_assets/variants/templates` |
| ~~Monitoring~~ | ~~DROP_CANDIDATE~~ → **DROPPED** | 4 | ~~`__lighthouse_alerts`, `__lighthouse_runs`, `__cron_runs`, `__airlock_bundles`~~ — DROPPED 2026-03-15 |
| SEO empty | ~~ORPHAN~~ → **ACTIVE_DESIGN** | 5 | `__seo_quality_log` (scoring), `__seo_diagnostic` (cockpit), `__seo_crawl_log` (googlebot), `__seo_interpolation_alerts` (RPC purge), `__seo_index_history` (cockpit+sitemap) — consumers confirmes |
| Quarantine/Pipeline | ~~ORPHAN~~ → **ACTIVE_DESIGN** | 4 | `__quarantine_items` (10+ RPCs), `__quarantine_history` (5+ RPCs), `pipeline_event_log` (2 RPCs), `seo_link_metrics_daily` (1 RPC) |
| Killswitch | ~~ORPHAN~~ → **ACTIVE_DESIGN** | 2 | `_killswitch_audit` (3 RPCs), `_killswitch_breakglass` (4 RPCs) |
| ~~Misc orphan~~ | ~~DROP_CANDIDATE~~ → **DROPPED** | 5 | ~~`__seo_sitemap_file`, `__sitemap_gamme`, `vehicule_v1_dominant`, `__agent_metrics`, `ticket_responses`~~ — DROPPED 2026-03-15 |
| Commerce/Support | ~~EMPTY_DROP_CANDIDATE~~ → **EMPTY_OPTIONAL_FEATURE** | 4 | `reviews` (SupportModule), `support_tickets` (SupportModule), `error_logs` (ErrorLogService + SEO), `error_statistics` (types) — **consumers confirmes, KEEP** |

> **Regle** : aucune table classee EMPTY_DROP_CANDIDATE ne peut etre supprimee sans double validation :
> 1. Absence de consumer technique (grep backend + RPCs + vues)
> 2. Absence d'intention produit confirmee (backlog)

> **Cas special** : `__seo_keyword_type_mapping` (11 MB, 0 rows) — table vide mais 1 FK entrante. Classee EMPTY_ACTIVE_DESIGN.

---

## 6. Tables legacy / doublons

| Table | Taille | Rows | Flag | Evidence | Verdict | Gate |
|-------|--------|------|------|----------|---------|------|
| ~~`___config_old`~~ | — | — | OLD | ✅ DROPPED V3 (2026-03-15) | — | — |
| ~~`pieces_marque_next`~~ | — | — | NEXT | ✅ DROPPED V3 (2026-03-15) | — | — |
| ~~`golden_set_products`~~ | — | — | — | ✅ DROPPED V3 (2026-03-15) | — | — |
| `__cross_gamme_car_new` | 41 MB | 182K | — | ✅ UNIFIED V5d — sole table, 182611 rows | **OK** | ready |
| ~~`__cross_gamme_car_deprecated`~~ | — | — | OLD | ✅ DROPPED (2026-03-15) — data in `_new` (superset) | — | — |
| `gate_thresholds` | 96 KB | 17 | — | measured (config active) | KEEP | ready |

### Doublons suspects — RESOLVED

| Paire | Resolution | Date |
|-------|-----------|------|
| ~~`__cross_gamme_car` vs `_new`~~ | ✅ 7087 old_only migres, old renamed `_deprecated`, `_new2` dropped | 2026-03-15 |
| `___meta_tags_ariane` vs `__blog_meta_tags_ariane` | DISJOINT — meme schema, donnees differentes (catalog vs blog). Pas de doublon. | 2026-03-14 |

---

## 7. Matrice TEXT critique — Tables prioritaires pour shadow columns

| Table | Taille | IDs TEXT | Prix TEXT | Dates TEXT | MassDoc Role | Priorite |
|-------|--------|---------|----------|-----------|-------------|----------|
| ~~`pieces_price`~~ | 354 MB | ~~4~~ | ~~**11**~~ | ~~2~~ | source_catalog | ✅ **DONE** V4b+V5a |
| `pieces_criteria` | 5.4 GB | **5** | 0 | 1 | source_catalog | P1 |
| `___xtr_msg` | 11 GB | **7** | 0 | 1 | non_tecdoc | P1 |
| `auto_type` | 37 MB | **4** | 0 | **4** | source_catalog | ✅ **DONE** V4b (shadow cols, code deferred) |
| `___xtr_order_line` | 2.6 MB | 7 | **20** | 1 | non_tecdoc | P2 |
| `___xtr_order` | 1.8 MB | 7 | **8** | 2 | non_tecdoc | P2 |
| `___xtr_invoice*` | 304 KB x2 | 10 | **16** | 1 | non_tecdoc | P2 |
| `pieces_criteria_link` | 18 MB | 3 | 0 | 0 | source_catalog | P2 |
| `pieces_gamme` | 10 MB | 1 | 0 | 0 | source_catalog | P3 |
| `pieces_marque` | 656 KB | 0 | 0 | 0 | source_catalog | P3 |
| `auto_modele` | 1.1 MB | 0 | 0 | 0 | source_catalog | P3 |

---

## 8. Jointures implicites candidates a formalisation FK

### Categorie A — ✅ DONE (FK validees V4c, code migre V5a/V5b)

| Table source | Colonne shadow | FK constraint | Status |
|-------------|---------------|---------------|--------|
| pieces_media_img | pmi_piece_id_i | fk_pieces_media_img_piece_i | ✅ VALIDATED |
| pieces_ref_ean | pre_piece_id_i | fk_pieces_ref_ean_piece_i | ✅ VALIDATED |
| pieces_ref_search | prs_piece_id_i | fk_pieces_ref_search_piece_i | ✅ VALIDATED |
| pieces_price | pri_piece_id_i | fk_pieces_price_piece_i | ✅ VALIDATED |
| pieces_list | pli_piece_id_i | fk_pieces_list_piece_i | ✅ VALIDATED |
| pieces_criteria | pc_piece_id_i | fk_pieces_criteria_piece_i | ✅ VALIDATED |

> 6 FK vers `pieces(piece_id)` via shadow cols INTEGER. Code backend migre (V5a/V5b). 707 orphelins supprimes prealablement.

### Categorie B+C — ✅ DONE (FK validees 2026-03-15)

| Table source | Colonne | Table cible | Colonne cible | FK constraint | Status |
|-------------|---------|-------------|---------------|---------------|--------|
| pieces_relation_criteria | rcp_type_id | auto_type | type_id_i | fk_pieces_relation_criteria_type | ✅ VALIDATED |
| pieces_relation_type | rtp_piece_id | pieces | piece_id | fk_pieces_relation_type_piece | ✅ VALIDATED |
| pieces_relation_type | rtp_type_id | auto_type | type_id_i | fk_pieces_relation_type_type | ✅ VALIDATED |

> Tous INTEGER→INTEGER, 0 orphelins (sampled). UNIQUE index `idx_auto_type_type_id_i_unique` cree sur auto_type(type_id_i) comme cible FK.
> Validation completee via pg_cron (146M + 157M rows, confirme `convalidated = true`).

**Rappel** : toute FK ajoutee utilisera le pattern `NOT VALID` + `VALIDATE` en background (zero lock).

---

## 9. Verdicts par table — Resume

| Verdict | Count | Description |
|---------|-------|-------------|
| **OK / DONE** | **~95** | Aucune action structurelle ou deja fixe (~~80~~ + 9 PK/FK/shadow + 6 resolved) |
| **TYPE_MIGRATION_REQUIRED** | **~12** | Shadow columns (TEXT → type natif) — `auto_type` code deferred, `___xtr_*` out_of_scope |
| ~~**PK_STRATEGY_REQUIRED**~~ | **0** | ~~3~~ — toutes fixees V4a |
| ~~**FK_CANDIDATE_A**~~ | **0** | ~~6~~ — toutes validees V4c |
| ~~**FK_CANDIDATE_B**~~ | **0** | ~~2~~ — resolues (rtp_piece_id→pieces, rcp_type_id→auto_type) |
| ~~**FK_CANDIDATE_C**~~ | **0** | ~~1~~ — resolue (rtp_type_id→auto_type.type_id_i) |
| **EMPTY_ACTIVE_DESIGN** | **~36** | Tables vides, infrastructure deployee + reclassees (quarantine, killswitch, SEO) |
| **EMPTY_STAGING_REQUIRED** | ~10 | Tables import/staging |
| **EMPTY_OPTIONAL_FEATURE** | **~19** | Features non activees (marketing, video, commerce/support) |
| ~~**EMPTY_ORPHAN_SUSPECT**~~ | **0** | ~~10~~ — tous reclasses ou droppees |
| ~~**EMPTY_DROP_CANDIDATE**~~ | **0** | ~~9~~ — toutes droppees (monitoring + misc) |
| ~~**DROP_READY**~~ | **0** | ~~3 V3 + 1 deprecated~~ — toutes droppees |
| ~~**DUPLICATE_SCOPE**~~ | **0** | ~~3~~ — tous resolus V5d |
| **NEAR_EMPTY** | ~8 | 1 row, probablement init/test |

---

## 10. Preconditions before any schema change

1. **Aucune PK ajoutee** sans audit d'unicite (SELECT count(*) vs count(DISTINCT ...))
2. **Aucune FK ajoutee** sans audit d'orphelins (valeurs sans correspondance dans la table cible)
3. **Aucune shadow column** sans mapping de cast deterministe (compter les valeurs non-castables)
4. **Aucune fusion de table** sans preuve de couverture fonctionnelle (grep + consumers)
5. **Aucun renommage** de table active sans cartographie complete des consumers (backend + RPCs + vues)
6. **Aucune decision MassDoc** sans classification source_of_truth confirmee

---

## 11. Criteres de sortie — Vague 2

Une table peut passer en Vague 4 (corrections structurelles) **seulement si** :

1. `source_of_truth` confirmee (pas `unknown`)
2. `readiness_tecdoc` ≠ `out_of_scope`
3. **PK** : unicite prouvee ou strategie validee (V2.1)
4. **FK** : orphelins mesures et plan traitable (V2.2)
5. **Types** : taux de cast invalide mesure et < 0.1% (V2.3)
6. **Consumers** cartographies si table active metier (V2.5)

> Detail de l'execution dans `phase-3-v2-validation-plan.md`.

### Priorite operationnelle V2 — ✅ TOUTES RESOLUES

| # | Table | Probleme initial | Resolution | Date |
|---|-------|-----------------|------------|------|
| 1 | `pieces_relation_type` | blocked_by_pk (146M) | ✅ PK + 2 FK | 2026-03-15 |
| 2 | `pieces_media_img` | blocked_by_pk (4.6M) | ✅ PK + FK | 2026-03-15 |
| 3 | `pieces_price` | type_debt P0 (11 prix TEXT) | ✅ Shadow cols + code V5a + FK | 2026-03-15 |
| 4 | `pieces_criteria` | type_debt (5 IDs TEXT) | ✅ FK (IDs deferred) | 2026-03-15 |
| 5 | `auto_type` | type_migration (4 IDs + 4 dates) | ✅ Shadow cols + UNIQUE idx (code deferred) | 2026-03-15 |
| 6 | `__cross_gamme_car` | duplicate_scope | ✅ Unified + DROPPED | 2026-03-15 |
| 7 | `___config_old` et al. | drop_ready | ✅ DROPPED V3 | 2026-03-15 |

---

## 12. Plan d'action recommande (Vagues 2-6)

### Vague 2 — Validation structurelle (READ-ONLY)

| # | Action | Cible | Methode |
|---|--------|-------|---------|
| 2.1 | Audit candidate PK (unicite) | `pieces_relation_type`, `pieces_media_img` | SQL GROUP BY/HAVING + sampled/full validation selon volumetrie |
| 2.2 | Audit orphelins FK | 6 FK cat. A + 2 FK cat. B | SQL LEFT JOIN ... WHERE cible IS NULL |
| 2.3 | Audit colonnes TEXT critiques | 11 tables P0-P2 | SQL cast test (count non-castable) |
| 2.4 | Audit doublons table/table | `__cross_gamme_car*`, `___meta_tags_ariane*` | Schema comparison + row overlap |
| 2.5 | Classification source de verite | Tier 1+2 tables | Grep backend + RPC analysis |
| 2.6 | Verdict readiness MassDoc par table | Tables source_catalog | Synthese 2.1-2.5 |

**Livrable** : enrichissement de ce document V1.2.0 avec resultats mesures.

### Vague 3 — Nettoyage trivial (0 risque) — DONE 2026-03-15

1. ~~DROP `___config_old`, `pieces_marque_next`, `golden_set_products`~~ — migration `vague3_drop_obsolete_tables` appliquee
2. ~~Documenter decision `__cross_gamme_car` vs `_new`~~ — DONE : 7087 old_only migres, table renommee `_deprecated`, `_new2` droppee

### Vague 4 — Corrections structurelles non-destructives

4a. ADD PK (apres V2.1 unicite confirmee) — PARTIAL 2026-03-15
    - ✅ `rm_rebuild_queue` PK (rmrq_gamme_id, rmrq_vehicle_id)
    - ✅ `pieces_media_img` PK (pmi_piece_id, pmi_name) — 10 headers CSV deleted first
    - ✅ `pieces_relation_type` — 146M rows, table swap batch (v2 with PK, old renamed `_old`). Index `popular` recréé, `type_composite` pending (timeout)
4b. ADD shadow columns + batch backfill (apres V2.3 cast valide) — DONE 2026-03-15
    - ✅ `pieces_price` : 15 shadow cols (13 NUMERIC + 1 TIMESTAMPTZ + 1 DATE), 442K rows backfilled
    - ✅ `auto_type` : 8 shadow cols (INTEGER), 49K rows backfilled
4c. ADD FK NOT VALID + VALIDATE (apres V2.2 orphelins resolus) — PARTIAL 2026-03-15
    - ✅ 707 orphelins supprimés (6 tables Cat A)
    - ✅ Shadow cols `*_piece_id_i INTEGER` ajoutées + backfillées sur 6 tables (442K+1.8M+3M+4.6M+17.6M+73M)
    - `pieces_ref_search` : table swap v2 (avec prs_piece_id_i), old gardée. Index kind recréé, autres index pending (timeout 70M+)
    - ✅ FK VALIDATED sur 6 tables (`*_piece_id_i` → `pieces(piece_id)`)
    - ✅ Tables _old droppées (pieces_relation_type_old, pieces_ref_search_old)
    - ✅ Index `pieces_ref_search` recréés (7/7) via pg_cron background
    - ✅ Index `type_composite` `pieces_relation_type` recréé via pg_cron background

### Vague 5 — Migration code (backend) — DONE 2026-03-15 (sauf auto_type)

~~Column swap en DB~~ : **REVERT** — PK/index suivent le column OID, pas le nom. Le swap cassait les queries (résultats vides → 404 prod).

**Strategie correcte appliquee** : modifier le code backend pour lire les shadow cols directement.

5a. **pieces_price shadow cols** (15 fichiers migres) — DONE 2026-03-15
    - ✅ `pri_vente_ttc` → `pri_vente_ttc_n`, `pri_consigne_ttc` → `pri_consigne_ttc_n`, etc.
    - ✅ `pri_piece_id` → `pri_piece_id_i` (INTEGER, plus de `.toString()`)
    - ✅ `parseFloat()` supprime partout (valeurs NUMERIC natives)
    - Fichiers : pricing.service, cart-data.service, order-actions.service, search-simple.service, catalog.service, working-stock.service, products.service, products-admin.service, search-enhanced-existing.service, mcp-query.service, shipping-calculator.service, stock.service

5b. **piece_id FK shadow cols** (6 fichiers migres) — DONE 2026-03-15
    - ✅ `pmi_piece_id` → `pmi_piece_id_i` (pieces_media_img)
    - ✅ `prs_piece_id` → `prs_piece_id_i` (pieces_ref_search)
    - ✅ `pc_piece_id` → `pc_piece_id_i` (pieces_criteria)
    - Fichiers : search-enhanced-existing, search-simple, catalog, mcp-query, products-technical, search-debug.controller, vehicle-pieces-compatibility

5c. **auto_type shadow cols** — DEFERRED DEFINITIVEMENT
    - 26 fichiers impactes, `type_id` est la PK TEXT (fonctionne correctement)
    - Shadow cols `_i` existent en DB + UNIQUE index sur `type_id_i`
    - Gain quasi nul sur 49K rows, risque de regression reel
    - **Decision finale** : ne pas migrer le code. Les shadow cols servent de cible FK uniquement.

5d. **Cross gamme unification** — DONE 2026-03-15
    - ✅ 7087 old_only rows migrees vers `__cross_gamme_car_new` (182611 total)
    - ✅ RPCs `refresh_gamme_aggregates` + `get_substitution_data` recreees sur `_new`
    - ✅ `gamme-detail-enricher.service.ts` mis a jour
    - ✅ `__cross_gamme_car` renommee `__cross_gamme_car_deprecated`
    - ✅ `__cross_gamme_car_new2` droppee
    - Migration : `20260315_unify_cross_gamme_car_new.sql`

### Vague 6 — MassDoc Update Readiness — DONE 2026-03-15

| Table | V2.6 Avant | Actions V3-V4 | **Classification** |
|-------|-----------|---------------|-------------------|
| **pieces** | ready_for_v4 | — | **SAFE** |
| **pieces_relation_type** | conditional_ready | PK (table swap 146M) | **FIXED** |
| **pieces_media_img** | ready_after_cleanup | 10 CSV headers deleted + PK + FK validated | **FIXED** |
| **pieces_price** | ready_after_cleanup | 12 orphelins deleted + FK validated + 15 shadow cols NUMERIC | **FIXED** |
| **pieces_criteria** | ready_after_cleanup | 309 orphelins deleted + FK validated | **FIXED** |
| **pieces_ref_search** | ready_after_cleanup | 219 orphelins deleted + table swap 73M + FK validated | **FIXED** |
| **pieces_ref_ean** | ready_after_cleanup | 83 orphelins deleted + FK validated | **FIXED** |
| **pieces_list** | ready_after_cleanup | 7 orphelins deleted + FK validated | **FIXED** |
| **pieces_relation_criteria** | ready_for_v4 | — | **SAFE** |
| **auto_type** | ready_for_v4 | 8 shadow cols INTEGER | **FIXED** |
| **__cross_gamme_car** | deferred | 7087 rows migrees + table renamed _deprecated | **DONE** |

> **Verdict global : 11/11 tables SAFE, FIXED ou DONE. 0 bloquante.**
> MassDoc update peut proceder sur toutes les tables.

---

## 13. Resultats Vague 2 — Validation Structurelle (2026-03-14)

> Toutes les mesures ci-dessous sont **read-only**. Aucune modification schema n'a ete effectuee.

### V2.5 — Source de Verite (measured)

| Table | Backend consumers | RPC consumers | SoT verdict | Confidence |
|-------|-------------------|---------------|-------------|------------|
| `__cross_gamme_car_new` | 2 (blog-article-relation, gamme-detail-enricher) | 6+ RPCs (unified) | **derived** (sole table) | high |
| ~~`__cross_gamme_car_deprecated`~~ | 0 | 0 | **DROPPED** (2026-03-15) | measured |
| `pieces_ref_search` | 6 services | 4 RPCs | **derived** (search index) | high |

> Aucune des tables n'est source de verite. `__cross_gamme_car` a ete depreciee (renommee `_deprecated` le 2026-03-15). Tout le code et RPCs pointent sur `_new`.

### V2.4 — Doublons (measured)

**Paire 1 : `__cross_gamme_car` vs `__cross_gamme_car_new`**

| Metrique | Valeur |
|----------|--------|
| Schema | Compatible (6 cols vs 7 cols — `_new` a `cgc_mdg_id` en plus) |
| Key | `(cgc_pg_id, cgc_type_id)` |
| Old rows | 75 289 |
| New rows | 175 524 |
| Common | 68 202 |
| Old only | 7 087 |
| New only | 105 540 |
| **Verdict** | **candidate_successor** — couvre 90.6% de old + 105K lignes additionnelles, mais 7 087 lignes old_only restent a migrer (quasi-superset non strict) |

> ~~Decision : migrer les 7 087 orphelins `old_only` vers `_new`, puis deprecer `__cross_gamme_car`.~~
> **DONE 2026-03-15** : 7087 rows migrees (182611 total dans `_new`), table old renommee `_deprecated`, `_new2` droppee. Migration `20260315_unify_cross_gamme_car_new.sql`.

**Paire 2 : `___meta_tags_ariane` vs `__blog_meta_tags_ariane`**

| Metrique | Valeur |
|----------|--------|
| Schema | **Identique** (9 cols, memes noms/types) |
| Key | `mta_id` |
| Total triple | 5 |
| Total blog | 5 |
| Common | 0 |
| **Verdict** | **DISJOINT** — meme structure, donnees totalement differentes |

> Pas de doublon de donnees. Tables distinctes par domaine (catalog vs blog).

### V2.1 — Audit PK (measured)

| Table | Total rows | Candidate key | Duplicate groups | Duplicate rows | Strategy | Gate |
|-------|-----------|---------------|-----------------|---------------|----------|------|
| `pieces_relation_type` | 146 371 196 | `(rtp_type_id, rtp_piece_id)` | **0** (5% sample = 7.3M rows) | 0 | **composite_pk_candidate_high_confidence** | conditional_ready |
| `pieces_media_img` | 4 623 813 | `(pmi_piece_id, pmi_name)` | **1** (10 header rows CSV) | 9 | **deduplicate_first(10) + validate_key_semantics** | ready_after_cleanup |
| `rm_rebuild_queue` | 0 | `(rmrq_gamme_id, rmrq_vehicle_id)` | — | — | **trivial_empty_table_pk** | ready |

> `pieces_relation_type` : full scan timeout (146M), mais 5% sample (7.3M rows) = 0 doublons. Confidence high mais non exhaustive — full validation requise avant ADD CONSTRAINT.
> `pieces_media_img` : 10 rows sont des headers CSV importes comme donnees (`pmi_piece_id = 'pmi_piece_id'`). 9 lignes excedentaires a supprimer (1 canonique conservee). Cle candidate `(pmi_piece_id, pmi_name)` valide sous hypothese que `pmi_name` identifie une image de maniere stable par piece — a confirmer contre usage applicatif.

### V2.3 — Castability TEXT (measured)

**`pieces_price`** (442 173 rows) :

| Colonne | Type cible | Total | Empty | Castable | Invalid | Ratio | Verdict |
|---------|-----------|-------|-------|----------|---------|-------|---------|
| pri_public_ht | NUMERIC | 442K | 0 | 442 173 | 0 | 0% | **cast_safe** |
| pri_gros_ht | NUMERIC | 442K | 0 | 442 173 | 0 | 0% | **cast_safe** |
| pri_achat_ht | NUMERIC | 442K | 0 | 442 173 | 0 | 0% | **cast_safe** |
| pri_vente_ht | NUMERIC | 442K | 0 | 442 173 | 0 | 0% | **cast_safe** |
| pri_vente_ttc | NUMERIC | 442K | 0 | 442 173 | 0 | 0% | **cast_safe** |
| pri_consigne_ht | NUMERIC | 442K | — | — | 0 | 0% | **cast_safe** |
| pri_consigne_ttc | NUMERIC | 442K | — | — | 0 | 0% | **cast_safe** |
| pri_remise | NUMERIC | 442K | — | — | 0 | 0% | **cast_safe** |
| pri_marge | NUMERIC | 442K | — | — | 0 | 0% | **cast_safe** |
| pri_frais_port_ht | NUMERIC | 442K | — | — | 0 | 0% | **cast_safe** |
| pri_frais_supp_ht | NUMERIC | 442K | — | — | 0 | 0% | **cast_safe** |
| pri_tva | NUMERIC | 442K | — | — | 0 | 0% | **cast_safe** |
| pri_vente_tn_ttc | NUMERIC | 442K | — | — | 0 | 0% | **cast_safe** |
| pri_date_from | TIMESTAMPTZ | 442K | 0 | 442 173 | 0* | 0% | **cast_safe** |
| pri_date_to | DATE | 442K | — | — | 0 | 0% | **cast_safe** |

> *`pri_date_from` : format ISO timestamp (`2022-07-01T00:00:00.000Z`), pas `YYYY-MM-DD`. Cast safe en TIMESTAMPTZ (pas DATE simple).

**`auto_type`** (48 918 rows) :

| Colonne | Type cible | Invalid | Verdict |
|---------|-----------|---------|---------|
| type_id | INTEGER | 0 | **cast_safe** |
| type_tmf_id | INTEGER | 0 | **cast_safe** |
| type_modele_id | INTEGER | 0 | **cast_safe** |
| type_marque_id | INTEGER | 0 | **cast_safe** |
| type_month_from | INTEGER | 0 | **cast_safe** |
| type_year_from | INTEGER | 0 | **cast_safe** |
| type_month_to | INTEGER | 0 | **cast_safe** |
| type_year_to | INTEGER | 0 | **cast_safe** |

> **Verdict global V2.3** : 0% invalid sur toutes les colonnes testees. Shadow columns safe pour les 2 tables P0-P1.

### V2.2 — FK Orphelins (measured)

**Cat. A — vers `pieces.piece_id`** :

| Table | Colonne | Non-castable | Orphans | Total | Ratio | Verdict |
|-------|---------|-------------|---------|-------|-------|---------|
| pieces_media_img | pmi_piece_id | 10 (headers) | 77 | 4.6M | 0.002% | **FK_READY_AFTER_CLEANUP** |
| pieces_ref_ean | pre_piece_id | 0 | 83 | 3M | 0.003% | **FK_READY_AFTER_CLEANUP** |
| pieces_ref_search | prs_piece_id | 0 | 219 | 73M | 0.0003% | **FK_READY_AFTER_CLEANUP** |
| pieces_price | pri_piece_id | 0 | 12 | 442K | 0.003% | **FK_READY_AFTER_CLEANUP** |
| pieces_list | pli_piece_id | 0 | 7 | 1.8M | 0.0004% | **FK_READY_AFTER_CLEANUP** |
| pieces_criteria | pc_piece_id | 0 | 309 | 17.6M | 0.002% | **FK_READY_AFTER_CLEANUP** |

> Tous < 0.01%. Total orphelins Cat A : **707 rows** sur ~100M. Plan : DELETE orphelins avant ADD FK.

**Cat. B — jointures inter-catalogue** :

| FK candidate | Non-castable | Orphans | Evidence | Verdict |
|-------------|-------------|---------|----------|---------|
| `rcp_type_id → rtp_type_id` | 0 (same type) | **0** (exhaustif) | measured | **FK_READY** |
| `rtp_piece_id → piece_id` | 0 (INTEGER) | **0** (sample 10K) | sampled | **FK_READY** (confidence medium) |

### V2.6 — Matrice Readiness MassDoc (SYNTHESE)

| Table | SoT (V2.5) | Doublons (V2.4) | PK (V2.1) | Types (V2.3) | FK (V2.2) | **Readiness V2** |
|-------|-----------|----------------|-----------|-------------|-----------|-----------------|
| **pieces** | source | — | ✓ | OK | ✓ (ref) | ✅ **ready** |
| **pieces_relation_type** | source | — | ✅ PK done | OK (INTEGER) | FK_READY (B) | ✅ **ready** |
| **pieces_media_img** | source | — | ✅ PK done | OK | ✅ FK validated | ✅ **ready** |
| **pieces_price** | source | — | ✓ | ✅ shadow cols + code V5a | ✅ FK validated | ✅ **ready** |
| **pieces_criteria** | source | — | ✓ | cast_safe (0%) | ✅ FK validated | ✅ **ready** |
| **pieces_ref_search** | derived | — | ✓ | cast_safe (0%) | ✅ FK validated | ✅ **ready** |
| **pieces_ref_ean** | source | — | ✓ | — | ✅ FK validated | ✅ **ready** |
| **pieces_list** | source | — | ✓ | — | ✅ FK validated | ✅ **ready** |
| **pieces_relation_criteria** | source | — | ✓ | OK | FK_READY (B) | ✅ **ready** |
| **auto_type** | source | — | ✓ | ✅ shadow cols (code deferred) | — | ✅ **ready** |
| **__cross_gamme_car_new** | derived | ✅ unified (182K) | ✓ | TEXT | — | ✅ **ready** |

> **Resultat final V1.5.0** : **11/11 tables ready.** Toutes les PK, FK, shadow cols et migrations donnees sont terminees. Code backend migre pour pieces_price (V5a) et piece_id FK (V5b). auto_type code deferred (shadow cols existent en DB).

---

## Refs croisees

| Document | Role |
|----------|------|
| domain-map.md V1.4.3 | Classification 15 domaines |
| final-exec-summary.md V1.4.2 | Baseline perf Phase 1-2 |
| db-monitoring-runbook.md V1.0.0 | Monitoring M1-M6 |
| table-remediation-matrix.md V1.4.2 | Decisions Phase 1 |
| perf-findings.md V1.0.3 | F1-F4, T1-T6 |
