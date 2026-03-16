# TecDoc Apply Mapping — Document B

> **Version** : 1.0.0
> **Date** : 2026-03-15
> **Pre-requis** : E5 SAFE_TO_UPSERT confirme, Document A (tecdoc-source-mapping.md)
> **Scope** : Phase 1 (t001, t100, t200, t209, t210)

---

## Principe

Ce document definit comment les donnees TecDoc normalisees (`tecdoc_norm`) sont appliquees aux tables de production AutoMecanik. Aucun apply sans ce mapping valide.

## Cle d'UPSERT principale

| Source TecDoc | Table AutoMecanik | Cle UPSERT | Evidence |
|--------------|-------------------|------------|----------|
| (ARTNR, DLNR) | `pieces` | `(piece_ref, piece_pm_id)` | E5 SAFE_TO_UPSERT, UNIQUE constraint en place |

---

## t200 → pieces (articles principaux)

| Colonne TecDoc | Colonne AutoMecanik | Type AM | Overwrite | Null handling | Notes |
|---------------|--------------------|---------|-----------|----|-------|
| ARTNR | piece_ref | VARCHAR | NEVER_OVERWRITE | — | Cle UPSERT, jamais modifie |
| DLNR | piece_pm_id | SMALLINT | NEVER_OVERWRITE | — | Cle UPSERT, jamais modifie |
| BEZNR | piece_des | VARCHAR | UPDATE_IF_DIFFERENT | KEEP_EXISTING | Description, via table 030 |
| KZSB | — | — | IGNORE | — | Self-service packing, pas utilise |
| KZMAT | — | — | IGNORE | — | Certification materiau, pas utilise |
| KZAT | — | — | IGNORE | — | Piece remanufacturee, pas utilise |
| KZZUB | — | — | IGNORE | — | Accessoire, pas utilise |
| LOSGR1 | piece_qty_pack | SMALLINT | UPDATE_IF_DIFFERENT | KEEP_EXISTING | Taille lot |
| LOSGR2 | — | — | IGNORE | — | Taille lot 2, pas utilise |
| LOSCH_FLAG | — | — | Voir politique LOSCH_FLAG | — | Soft delete |

**Colonnes AutoMecanik NON alimentees par TecDoc** (a preserver) :
- `piece_id` — ID interne, JAMAIS touche
- `piece_ref_clean` — genere par le backend
- `piece_name`, `piece_name_comp`, `piece_name_side` — enrichissement interne
- `piece_fil_id`, `piece_fil_name` — famille interne
- `piece_ga_id`, `piece_pg_id`, `piece_pg_pid` — mappings internes (via t211/t320)
- `piece_qty_sale` — logique commerciale interne
- `piece_weight_kgm` — poids (source separee)
- `piece_has_oem`, `piece_has_img` — flags calcules
- `piece_year` — annee (logique interne)
- `piece_display` — visibilite (gere par LOSCH_FLAG)
- `piece_sort` — tri interne
- `piece_update` — flag update interne
- `piece_psf_id` — filtre cote
- `search_vector` — tsvector genere

---

## t100 → pieces_marque (fournisseurs)

| Colonne TecDoc | Colonne AutoMecanik | Overwrite | Null handling | Notes |
|---------------|--------------------|-----------|----|-------|
| HERNR | pm_id | NEVER_OVERWRITE | — | Cle UPSERT |
| HKZ | pm_code | UPDATE_IF_DIFFERENT | KEEP_EXISTING | Code court |
| LBEZNR | — | IGNORE | — | Ref description (table 012) |
| PKW/NKW/VGL/... | — | IGNORE | — | Flags type fabricant |

**Cle UPSERT** : `pm_id` = HERNR (a confirmer par audit)

---

## t209 → pieces_ref_ean (codes EAN)

| Colonne TecDoc | Colonne AutoMecanik | Overwrite | Null handling | Notes |
|---------------|--------------------|-----------|----|-------|
| ARTNR+DLNR | pre_piece_id | — | — | Resolu via lookup pieces (ARTNR,DLNR) → piece_id |
| EANNR | pre_code_ean | ALWAYS | — | Code EAN |
| LOSCH_FLAG | — | Voir politique LOSCH_FLAG | — | |

**Cle UPSERT** : `(pre_piece_id, pre_code_ean)` — PK existante.
**Lookup obligatoire** : ARTNR+DLNR → piece_id via `pieces`.

---

## t210 → pieces_criteria (criteres article)

| Colonne TecDoc | Colonne AutoMecanik | Overwrite | Null handling | Notes |
|---------------|--------------------|-----------|----|-------|
| ARTNR+DLNR | pc_piece_id | — | — | Resolu via lookup pieces |
| KRITNR | pc_cri_id | ALWAYS | — | Numero critere |
| KRITWERT | pc_cri_value | ALWAYS | — | Valeur critere |
| SORTNR | pc_sort | UPDATE_IF_DIFFERENT | KEEP_EXISTING | Ordre affichage |
| LOSCH_FLAG | — | Voir politique LOSCH_FLAG | — | |

**Cle UPSERT** : `(pc_piece_id, pc_cri_id)` ou `(pc_piece_id, pc_sort)` — a confirmer.
**Lookup obligatoire** : ARTNR+DLNR → piece_id via `pieces`.

---

## t001 — Header (pas d'apply direct)

La table t001 sert uniquement a :
- Identifier la version du lot fournisseur
- Determiner si c'est un envoi complet ou delta
- Documenter le manifest

**Pas d'apply vers une table AutoMecanik.** Les donnees restent dans `tecdoc_norm.t001` pour reference.

---

## Politique LOSCH_FLAG

| LOSCH_FLAG | Action | Condition |
|-----------|--------|-----------|
| 0 | UPSERT normal | — |
| 1 (article sans commande active) | `piece_display = false` | Soft delete |
| 1 (article avec commande active) | **REVIEW** — journal dans `__tecdoc_losch_log` | Pas de soft delete automatique |
| 1 (article avec contenu SEO) | **REVIEW** — journal | Pas de soft delete automatique |

**Journal LOSCH_FLAG** : table `__tecdoc_losch_log` (artnr, dlnr, table_id, action, batch_id, created_at).

---

## Ordre d'apply (respect des FK)

1. `pieces_marque` (t100) — pas de FK entrantes
2. `pieces` (t200) — cible de toutes les FK
3. `pieces_ref_ean` (t209) — FK vers pieces
4. `pieces_criteria` (t210) — FK vers pieces

> t001 n'est pas applique en production.

---

## Regles de securite apply

1. **Jamais de TRUNCATE** — toujours UPSERT
2. **Jamais de modification de piece_id** — ID interne preservee
3. **Jamais de DELETE reel** — LOSCH_FLAG = soft delete uniquement
4. **Lookup ARTNR+DLNR → piece_id** obligatoire avant toute ecriture satellite
5. **Articles nouveaux** (pas de match) : INSERT avec nouveau piece_id auto-genere
6. **ANALYZE apres chaque table** appliquee
