# Architecture V-Level (Production)

> **Version**: 1.0.0 | **Status**: CANON | **Date**: 2026-01-28

Ce document decrit l'architecture V-Level actuellement en production.

---

## Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE V-LEVEL (Production)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  COLLECTE                 STOCKAGE                   UTILISATION            │
│  ────────                 ────────                   ───────────            │
│                                                                              │
│  ┌─────────────┐         ┌─────────────┐          ┌─────────────┐         │
│  │ Google      │         │             │          │             │         │
│  │ Keyword     │─────────▶│ __seo_     │─────────▶│ Admin UI    │         │
│  │ Planner     │  CSV     │ keywords   │          │ /admin/     │         │
│  │ (manuel)    │ import   │            │  API     │ gammes-seo  │         │
│  └─────────────┘         └─────────────┘          └─────────────┘         │
│                                 │                                          │
│                                 │ Trigger                                  │
│                                 ▼                                          │
│                          ┌─────────────┐                                  │
│                          │ v2_reps     │                                  │
│                          │ auto-calc   │                                  │
│                          └─────────────┘                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Composants

### 1. Source de Donnees

| Source | Methode | Frequence |
|--------|---------|-----------|
| **Google Keyword Planner** | Export CSV manuel | Ad-hoc |

**Colonnes CSV requises:**
- `keyword` - Requete de recherche
- `volume` - Volume de recherche mensuel
- `gamme` - Nom de la gamme (ou pg_id)
- `model` - Modele vehicule
- `variant` - Variante (motorisation)
- `energy` - Essence / Diesel

### 2. Table Principale

**Table:** `__seo_keywords`

```sql
-- Colonnes V-Level pertinentes
keyword       TEXT      -- "plaquette frein clio 3 1.5 dci 90"
type          TEXT      -- 'vehicle' | 'gamme' | 'brand'
pg_id         INTEGER   -- FK vers __gammes (piece/gamme)
model         TEXT      -- "Clio 3"
variant       TEXT      -- "1.5 dCi 90"
energy        TEXT      -- "Diesel" | "Essence"
v_level       TEXT      -- 'V1' | 'V2' | 'V3' | 'V4' | 'V5'
best_rank     INTEGER   -- Position Google Suggest (1-10)
search_volume INTEGER   -- Volume mensuel
v2_repetitions INTEGER  -- Nombre de gammes ou cette variante est V2
```

### 3. Triggers Automatiques

**Trigger:** `trg_update_v2_repetitions_insert`
- **Declencheur:** INSERT ou UPDATE de `v_level`
- **Action:** Recalcule `v2_repetitions` pour la variante

**Trigger:** `trg_update_v2_repetitions_delete`
- **Declencheur:** DELETE
- **Action:** Recalcule `v2_repetitions` pour la variante

**Migration:** `20260128_backfill_v2_repetitions.sql`

### 4. API Backend

**Module:** `backend/src/modules/admin/`

| Endpoint | Description |
|----------|-------------|
| `GET /api/admin/gammes-seo` | Liste des gammes avec stats SEO |
| `GET /api/admin/gammes-seo/:pgId/detail` | Detail V-Level d'une gamme |
| `POST /api/admin/gammes-seo/:pgId/keywords` | Import CSV keywords |

**Service:** `admin-gammes-seo.service.ts`
- Query V-Level avec deduplication par (model+variant+energy)
- Mapping `best_rank` vers `rank` dans la reponse

### 5. Interface Admin

**Route:** `/admin/gammes-seo/:pgId`
**Onglet:** V-Level

**Fonctionnalites:**
- Affichage V2/V3/V4 par energie (Essence/Diesel)
- Rank colore (#1-3 vert, #4-7 jaune, #8+ gris)
- Badge `x{n}` si v2_repetitions > 1
- Export CSV

**Fichiers:**
- `frontend/app/routes/admin.gammes-seo_.$pgId.tsx`
- `frontend/app/components/admin/gamme-seo/VLevelCard.tsx`
- `frontend/app/components/admin/gamme-seo/types.ts`
- `frontend/app/components/admin/gamme-seo/utils.ts`

---

## Process d'Import V-Level

### Etape 1: Export Google Keyword Planner

1. Aller sur Google Ads > Keyword Planner
2. Rechercher les keywords par gamme (ex: "plaquette frein clio")
3. Exporter en CSV

### Etape 2: Preparation CSV

Format attendu:
```csv
keyword,volume,gamme,model,variant,energy,v_level,best_rank
plaquette frein clio 3 1.5 dci 90,320,Plaquettes de frein,Clio 3,1.5 dCi 90,Diesel,V2,1
plaquette frein clio 3 1.5 dci 105,180,Plaquettes de frein,Clio 3,1.5 dCi 105,Diesel,V4,3
```

### Etape 3: Import via Admin UI

1. Naviguer vers `/admin/gammes-seo/:pgId`
2. Cliquer "Importer CSV"
3. Selectionner le fichier
4. Valider l'import

### Etape 4: Verification

Les triggers recalculent automatiquement `v2_repetitions`.

```sql
-- Verifier les V2 avec repetitions
SELECT model, variant, energy, v2_repetitions
FROM __seo_keywords
WHERE v_level = 'V2' AND v2_repetitions > 1
ORDER BY v2_repetitions DESC;
```

---

## Classification V-Level

Voir `.spec/00-canon/seo/vlevel-rules.md` pour les regles detaillees.

| V-Level | Definition | Critere |
|---------|------------|---------|
| **V1** | Inter-gamme dominant | >= 30% des gammes G1 en V2 |
| **V2** | Champion gamme | Plus haut volume Google |
| **V3** | Challenger | Volume > 0, pas V2 |
| **V4** | Non recherche | Volume = 0 ou tres faible |
| **V5** | Force SEO | Assignation manuelle |

---

## Limitations

| Limitation | Impact | Contournement |
|------------|--------|---------------|
| Import manuel | Donnees pas temps reel | Process mensuel recommande |
| Pas de Search Console | Pas de donnees CTR/position | Focus sur volumes |
| Pas de Google Trends | Pas de tendances | Historique manuel |

---

## Migration depuis Architecture n8n (jamais implementee)

L'architecture n8n documentee dans `.spec/workflows/v-level-pipeline.md` n'a jamais ete implementee.

| Prevu (n8n) | Reel (CSV) |
|-------------|------------|
| `__v_level_raw` | Non cree |
| `__v_level_computed` | Non cree |
| Collecte automatique | Import manuel |
| pytrends + Search Console | Google Keyword Planner |

---

## Fichiers de Reference

| Fichier | Role |
|---------|------|
| `.spec/00-canon/seo/vlevel-rules.md` | Regles metier V-Level |
| `backend/supabase/migrations/20260128_backfill_v2_repetitions.sql` | Triggers v2_repetitions |
| `backend/src/modules/admin/services/admin-gammes-seo.service.ts` | API Backend |

---

_Ce document est la source de verite pour l'architecture V-Level en production._
