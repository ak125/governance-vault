# Phase 3 — Catalog Structural Audit

> **Version** : 1.0.0
> **Date** : 2026-03-14
> **Scope** : 30 tables catalogue TecDoc (pieces_*, auto_*, __cross_*)
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`
> **Objectif** : documenter l'etat structurel du noyau catalogue avant update TecDoc

---

## Vue d'ensemble

| Metrique | Valeur |
|----------|--------|
| Tables dans le scope | 30 |
| Espace total | ~68 GB (79% de la base) |
| Tables sans PK | **2** (pieces_relation_type, pieces_media_img) |
| Tables avec FK | **1** (pieces, 2 FK) |
| Tables 100% TEXT | **3** (pieces_media_img, pieces_criteria_link, pieces_details) |
| Tables avec PK TEXT | **15** (sur 28 avec PK) |
| Tables vides ou quasi-vides (≤1 row) | **4** (pieces_details, pieces_ref_oem, auto_modele_robot, auto_type_motor_code) |
| Tables legacy | **2** (__cross_gamme_car_new, pieces_marque_next) |

---

## Audit table par table

### Tier 1 — Tables critiques (>1 GB, hot path)

#### pieces_relation_criteria — 33 GB, 158M rows

| Aspect | Etat | Risque |
|--------|------|--------|
| PK | composite (rcp_type_id, rcp_piece_id, rcp_pg_pid, rcp_cri_id, rcp_cri_value, rcp_sort) | OK (6 colonnes) |
| FK | **aucune** | jointure implicite vers pieces_relation_type.rtp_type_id |
| Types | 9 INTEGER + 1 TEXT (rcp_cri_value) | OK — types coherents |
| Consumers | 10 fichiers backend | hot path (U1 listing) |

**Verdict** : `SAFE_TO_UPDATE` — schema propre, PK composite coherente. Seul risque : FK implicite vers pieces_relation_type.

---

#### pieces_ref_search — 16 GB, 73M rows

| Aspect | Etat | Risque |
|--------|------|--------|
| PK | composite (prs_piece_id, prs_search, prs_kind) — **TEXT** | PK TEXT sur 73M rows |
| FK | **aucune** | jointure implicite vers pieces.piece_id |
| Types | 7 colonnes, **toutes TEXT** sauf 2 INTEGER | |
| Consumers | 7 fichiers backend | search path |

**Verdict** : `DOCUMENT_ONLY` — table de recherche derivee. Les types TEXT sont intentionnels (index de recherche). Pas de correction avant update.

---

#### pieces_relation_type — 9.7 GB, 146M rows — CRITIQUE

| Aspect | Etat | Risque |
|--------|------|--------|
| PK | **AUCUNE** | **CRITIQUE** — 146M rows sans identifiant unique |
| FK | **aucune** | jointures implicites vers pieces, pieces_gamme, pieces_marque |
| Types | **7 INTEGER + 1 VARCHAR** | OK — types coherents |
| Consumers | 10 fichiers backend | hot path (U1 listing, cross-selling) |
| Colonnes | rtp_type_id, rtp_piece_id, rtp_pm_id, rtp_pg_id, rtp_pg_pid, rtp_ga_id, rtp_psf_id, rtp_inside | |

> Table de jonction piece↔vehicule. La PK naturelle serait probablement `(rtp_type_id, rtp_piece_id)` ou `(rtp_type_id, rtp_piece_id, rtp_pg_pid)`. A verifier : y a-t-il des doublons sur ces combinaisons ?

**Verdict** : `FIX_SCHEMA_FIRST` — ajouter une PK avant update TecDoc. Priorite P0.

---

#### pieces_criteria — 5.4 GB, 17.6M rows

| Aspect | Etat | Risque |
|--------|------|--------|
| PK | composite (pc_piece_id, pc_pg_pid, pc_cri_id, pc_cri_value) — **TEXT** | PK TEXT sur 17.6M rows |
| FK | **aucune** | |
| Types | **9/10 colonnes TEXT** (dont pc_piece_id, pc_cri_id, pc_pg_id, pc_ga_id) | casts TEXT→INT dans les RPCs |
| Consumers | 0 fichiers backend directs | acces uniquement via RPC |

**Verdict** : `FIX_SCHEMA_FIRST` — les colonnes ID sont TEXT alors qu'elles contiennent des entiers. Les expression indexes Phase 2A (`idx_pieces_criteria_cri100_piece_int`) compensent, mais la cause racine reste. Correction ideale avant update TecDoc.

---

#### pieces — 1.4 GB, 4M rows

| Aspect | Etat | Risque |
|--------|------|--------|
| PK | piece_id (INTEGER, serial) | OK |
| FK | **2 FK** : piece_ga_id → ?, piece_pm_id → ? | **seule table avec FK** |
| Types | 24 colonnes, mix INTEGER + TEXT | acceptable |
| Consumers | via RPC principalement | |

**Verdict** : `SAFE_TO_UPDATE` — table reference principale, schema relativement propre.

---

#### pieces_media_img — 953 MB, 4.6M rows — CRITIQUE

| Aspect | Etat | Risque |
|--------|------|--------|
| PK | **AUCUNE** | **CRITIQUE** — 4.6M rows sans identifiant unique |
| FK | **aucune** | jointure implicite vers pieces via pmi_piece_id |
| Types | **6/6 colonnes TEXT** | tout est TEXT, y compris pmi_piece_id et pmi_pm_id |
| Consumers | 5 fichiers backend | images produit |
| Colonnes | pmi_piece_id, pmi_pm_id, pmi_folder, pmi_name, pmi_sort, pmi_display | |

> PK naturelle probable : `(pmi_piece_id, pmi_pm_id, pmi_sort)` ou `(pmi_piece_id, pmi_name)`. A verifier : doublons ?

**Verdict** : `FIX_SCHEMA_FIRST` — ajouter PK + convertir pmi_piece_id/pmi_pm_id en INTEGER. Priorite P0.

---

### Tier 2 — Tables moyennes (100 MB - 1 GB)

#### pieces_ref_ean — 512 MB, 3M rows

| PK | FK | Types | Consumers | Verdict |
|----|----|-------|-----------|---------|
| composite (pre_piece_id, pre_code_ean) — TEXT | aucune | 2 TEXT | 1 (database.types) | `DOCUMENT_ONLY` — lookup EAN, acces RPC |

#### pieces_price — 354 MB, 442K rows — ATTENTION

| PK | FK | Types | Consumers | Verdict |
|----|----|-------|-----------|---------|
| composite (pri_piece_id, pri_type) — TEXT | aucune | **40/44 TEXT** | **18 fichiers** (hot path pricing) | `FIX_SCHEMA_FIRST` |

> **40 colonnes TEXT** dont : prix (pri_achat_ht, pri_vente_ht, pri_public_ht), dates (pri_date_from, pri_date_to), dimensions, remises. Tout devrait etre NUMERIC/DATE/INTEGER. C'est la table la plus mal typee du catalogue et l'une des plus consultees (18 consumers).

#### pieces_list — 302 MB, 1.8M rows

| PK | FK | Types | Consumers | Verdict |
|----|----|-------|-----------|---------|
| composite (pli_piece_id, pli_piece_component, pli_sort) — TEXT | aucune | 5 TEXT | 1 (database.types) | `DOCUMENT_ONLY` — acces RPC uniquement |

---

### Tier 3 — Tables de reference (<100 MB)

| Table | Taille | Rows | PK | Types TEXT | Consumers | Verdict |
|-------|--------|------|----|-----------|-----------|---------|
| auto_type | 37 MB | 49K | type_id **TEXT** | **18/21 TEXT** | 0 direct (RPC) | `FIX_SCHEMA_FIRST` |
| auto_type_number_code | 37 MB | 165K | composite TEXT | 3/3 TEXT | 0 direct (RPC) | `DOCUMENT_ONLY` |
| pieces_criteria_link | 18 MB | 77K | composite TEXT | **12/12 TEXT** | 0 direct | `DOCUMENT_ONLY` |
| __cross_gamme_car | 13 MB | 75K | cgc_id INT | mix | 3 | `SAFE_TO_UPDATE` |
| pieces_gamme | 10 MB | 9.7K | pg_id INT | 15/20 TEXT | 0 direct (RPC) | `DOCUMENT_ONLY` |
| pieces_criteria_group | 1.5 MB | 4.3K | cri_id TEXT | 8/8 TEXT | 0 direct | `DOCUMENT_ONLY` |
| pieces_ref_brand | 1.4 MB | 5.9K | prb_id TEXT | 8/8 TEXT | 3 | `DOCUMENT_ONLY` |
| auto_modele | 1.1 MB | 5.7K | modele_id INT | mix | 0 direct | `SAFE_TO_UPDATE` |
| pieces_marque | 656 KB | 992 | pm_id INT | 14/16 TEXT | **20 fichiers** | `DOCUMENT_ONLY` |
| pieces_gamme_cross | 416 KB | 1.4K | pgc_id TEXT | 6/6 TEXT | 0 direct | `DOCUMENT_ONLY` |
| auto_modele_group | 600 KB | 2K | mdg_id INT | mix | 0 direct | `SAFE_TO_UPDATE` |
| auto_type_motor_fuel | 160 KB | 26 | tmf_id TEXT | 6/6 TEXT | 0 direct | `DOCUMENT_ONLY` |

### Tier 4 — Tables vides ou legacy

| Table | Rows | Verdict | Action |
|-------|------|---------|--------|
| pieces_details | 1 | `DOCUMENT_ONLY` — table de staging jamais peuplee | |
| pieces_ref_oem | 1 | `DOCUMENT_ONLY` — OEM refs non importees | |
| pieces_marque_next | 0 | `ARCHIVE_BEFORE_UPDATE` — table vide avec suffixe _next | DROP candidate |
| auto_modele_robot | 1 | `DOCUMENT_ONLY` — robot/scraping reference | |
| auto_type_motor_code | 1 | `DOCUMENT_ONLY` — codes moteur non importes | |
| __cross_gamme_car_new | 175K | `DOCUMENT_ONLY` — table active malgre suffixe _new | verifier vs __cross_gamme_car |
| pieces_side_filtre | 5 | `SAFE_TO_UPDATE` — lookup statique | |
| pieces_status | 13 | `SAFE_TO_UPDATE` — lookup statique | |

---

## Synthese des problemes structurels

### P0 — Tables sans PK (bloquant pour update TecDoc)

| Table | Rows | Action requise |
|-------|------|----------------|
| `pieces_relation_type` | 146M | Identifier PK naturelle + ADD CONSTRAINT |
| `pieces_media_img` | 4.6M | Identifier PK naturelle + ADD CONSTRAINT |

### P1 — Colonnes TEXT qui devraient etre typees (dette technique)

| Table | Colonnes TEXT / Total | Impact | Priorite |
|-------|----------------------|--------|----------|
| `pieces_price` | 40/44 | prix, dates, dimensions en TEXT — 18 consumers | **haute** |
| `auto_type` | 18/21 | IDs vehicule en TEXT (type_id PK = TEXT) | moyenne |
| `pieces_criteria` | 9/10 | IDs en TEXT, expression indexes compensent | moyenne |
| `pieces_media_img` | 6/6 | tout TEXT, pas de PK | haute (combine avec P0) |
| `pieces_criteria_link` | 12/12 | 100% TEXT, acces RPC | basse |

> **Pattern general** : l'import TecDoc historique a stocke toutes les donnees en TEXT sans conversion de type. Seules `pieces` (table principale) et `pieces_relation_type`/`pieces_relation_criteria` (tables de jonction) ont des types corrects.

### P2 — Absence de FK (dette structurelle acceptee)

28/30 tables n'ont aucune FK. Toutes les jointures sont implicites via conventions de nommage (_id, _type_id, _piece_id). Ce choix est probablement intentionnel (performance import TecDoc bulk), mais augmente le risque d'incoherence lors d'un update.

### P3 — Tables doublons suspects

| Paire | Verdict |
|-------|---------|
| `__cross_gamme_car` (75K) vs `__cross_gamme_car_new` (175K) | A investiguer — meme role, tailles differentes |
| `pieces_marque_next` (0 rows) | DROP candidate — table vide |

---

## Verdicts par table

| Verdict | Tables | Count |
|---------|--------|-------|
| `SAFE_TO_UPDATE` | pieces, pieces_relation_criteria, __cross_gamme_car, auto_modele, auto_modele_group, pieces_side_filtre, pieces_status | **7** |
| `FIX_SCHEMA_FIRST` | pieces_relation_type, pieces_media_img, pieces_price, pieces_criteria, auto_type | **5** |
| `DOCUMENT_ONLY` | pieces_ref_search, pieces_ref_ean, pieces_list, pieces_criteria_link, pieces_criteria_group, pieces_ref_brand, pieces_gamme, pieces_gamme_cross, auto_type_number_code, auto_type_motor_fuel, pieces_details, pieces_ref_oem, auto_modele_robot, auto_type_motor_code, __cross_gamme_car_new, pieces_marque | **16** |
| `ARCHIVE_BEFORE_UPDATE` | pieces_marque_next | **1** |
| `MERGE_BEFORE_UPDATE` | — | **0** |

---

## Recommandations avant update TecDoc

### Obligatoire (P0)

1. **Ajouter PK sur `pieces_relation_type`** — verifier unicite de `(rtp_type_id, rtp_piece_id)` ou `(rtp_type_id, rtp_piece_id, rtp_pg_pid)`, puis ADD CONSTRAINT
2. **Ajouter PK sur `pieces_media_img`** — verifier unicite de `(pmi_piece_id, pmi_pm_id, pmi_sort)`, puis ADD CONSTRAINT

### Hautement recommande (P1)

3. **Convertir colonnes prix TEXT→NUMERIC sur `pieces_price`** — au minimum `pri_achat_ht`, `pri_vente_ht`, `pri_public_ht`, `pri_gros_ht`
4. **Convertir dates TEXT→DATE sur `pieces_price`** — `pri_date_from`, `pri_date_to`
5. **DROP `pieces_marque_next`** — table vide, aucun consumer

### Souhaitable (P2)

6. **Convertir IDs TEXT→INTEGER sur `auto_type`** — `type_id`, `type_marque_id`, `type_modele_id`
7. **Investiguer doublon `__cross_gamme_car` vs `__cross_gamme_car_new`**
8. **Ajouter FK explicites** sur les jointures les plus critiques (pieces_relation_type → pieces, pieces_media_img → pieces)

### Reporte apres update (P3)

9. Nettoyage types TEXT sur tables secondaires (criteria_link, criteria_group, gamme_cross, ref_brand)
10. Graphe relationnel complet avec FK formelles

---

## Refs croisees

| Document | Role |
|----------|------|
| domain-map.md V1.4.3 | Classification domaines D1/D3 |
| final-exec-summary.md V1.4.2 | Baseline monitoring |
| perf-findings.md V1.0.3 | F1-F4 performance mesurees |
| table-remediation-matrix.md V1.4.2 | Decisions Phase 1 |
