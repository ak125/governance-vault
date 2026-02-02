# V-Level Rules (SEO Classification)

> **Version**: 3.0.0 | **Status**: CANON | **Date**: 2026-02-01

## Prérequis : type_id OBLIGATOIRE

```
V1, V2, V3, V4, V5, V6 = TOUS exigent type_id NOT NULL
```

**Pourquoi ?** Le `type_id` permet de générer les URLs SEO :
```
/constructeurs/{marque}-{marque_id}/{modele}-{modele_id}/{variant}-{type_id}.html
```

**Keywords génériques SANS motorisation** (ex: "filtre huile clio 4") :
- Si `type_id = NULL` → **AUCUN V-Level assigné** (v_level = NULL)
- Ces keywords doivent d'abord être matchés avec la base `auto_type`

---

## Classification V-Level v3.0

| V-Level | Définition | Critère | Prérequis |
|---------|------------|---------|-----------|
| **V1** | Super-champion inter-gammes | V3 présent dans **2+ gammes** | Promu automatiquement |
| **V2** | Champion stratégique | **TOP 20** par `score_seo` dans la gamme | type_id NOT NULL |
| **V3** | Champion local | TOP 1 par (modèle + énergie) | type_id NOT NULL |
| **V4** | Variant secondaire | Volume > 0, non champion | type_id NOT NULL |
| **V5** | Sans demande | Volume = 0 ou NULL | type_id NOT NULL |
| **V6** | Bloc B catalogue | Spécificités techniques | Assignation manuelle |
| **NULL** | Non classifiable | - | type_id IS NULL |

---

## Formule Score SEO

```
score_seo = volume × (1 + nb_v4 / 5)
```

- `volume` = recherches mensuelles Google
- `nb_v4` = nombre de variants V4 associés au même (modèle + énergie)

**Exemple:**
- "filtre a huile 207 1.6 hdi" : volume=500, nb_v4=20 → score_seo = 500 × (1 + 20/5) = **2500**
- "filtre a huile 206 1.4 hdi" : volume=500, nb_v4=14 → score_seo = 500 × (1 + 14/5) = **1900**

---

## Algorithme de classification

### Étape 1 : Identifier les Champions (V3)

Pour chaque groupe **(gamme + modèle + énergie)** :
1. Trier les keywords par volume DESC
2. Le TOP 1 devient **V3** (champion local)
3. Les autres deviennent **V4** (variants secondaires)

### Étape 2 : Promouvoir les TOP 20 (V3 → V2)

Pour chaque gamme :
1. Calculer le `score_seo` de chaque V3
2. Trier par score_seo DESC
3. Les **TOP 20** deviennent **V2** (champions stratégiques)

### Étape 3 : Promouvoir inter-gammes (V3 → V1)

Un V3 présent dans **2+ gammes** est promu **V1** automatiquement.

### Flowchart

```
┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 1 : Pour chaque (gamme + modèle + énergie)           │
│   → Trier keywords par volume DESC                          │
│   → TOP 1 = V3 (champion local)                             │
│   → Autres = V4 (variants secondaires)                      │
│                                                             │
│ ÉTAPE 2 : Pour chaque gamme                                 │
│   → Calculer score_seo = volume × (1 + nb_v4/5)            │
│   → TOP 20 V3 par score_seo → promouvoir en V2              │
│                                                             │
│ ÉTAPE 3 : Inter-gammes                                      │
│   → V3 présent dans 2+ gammes → promouvoir en V1            │
└─────────────────────────────────────────────────────────────┘
```

---

## Exemple : Filtre à huile (pg_id=7)

### TOP 6 V2 stratégiques

| Rang | Score | Vol | V4 | Marque | Modèle | Keyword V2 |
|------|-------|-----|-----|--------|--------|------------|
| 1 | 2500 | 500 | 20 | Peugeot | 207 | filtre a huile 207 1.6 hdi |
| 2 | 1900 | 500 | 14 | Peugeot | 206 | filtre a huile 206 1.4 hdi |
| 3 | 1700 | 500 | 12 | Citroën | c4 | filtre a huile c4 1.6 hdi |
| 4 | 1500 | 500 | 10 | Citroën | c3 | filtre huile c3 1.4 hdi |
| 5 | 1400 | 500 | 9 | Renault | clio 3 | filtre à huile clio 3 1.5 dci |
| 6 | 1100 | 500 | 6 | Citroën | berlingo | filtre a huile berlingo 1.6 hdi |

### Distribution attendue

| V-Level | Count | Description |
|---------|-------|-------------|
| V2 | 20 | TOP 20 stratégiques |
| V3 | 54 | Autres champions (74 - 20) |
| V4 | 267 | Variants secondaires |
| V5 | ? | Volume = 0 |

---

## Règles métier

### Une seule variante V3 par groupe

Pour une gamme donnée + un modèle + une énergie, il ne peut y avoir qu'**un seul V3**.

Exemple :
- "Plaquettes + Clio 3 + Diesel" → V3 = **1.5 dCi 90** (si TOP 1 par volume)
- "Plaquettes + Clio 3 + Essence" → V3 = **1.2 16v 75** (si TOP 1)

### Séparation Essence / Diesel

Les variantes sont comparées **au sein de leur famille énergétique** :
- Essence vs Essence
- Diesel vs Diesel

On ne compare jamais un diesel avec une essence.

### TOP 20 par gamme

Chaque gamme a **exactement 20 V2** (ou moins si < 20 V3 disponibles).

---

## Tables Supabase

| Table | Colonne | Usage | Status |
|-------|---------|-------|--------|
| `__seo_keywords` | `v_level` | V1/V2/V3/V4/V5/V6/NULL | ✅ Actif |
| `__seo_keywords` | `type_id` | Lien vers `auto_type.type_id` | ✅ Actif |
| `__seo_keywords` | `volume` | Volume de recherche Google | ✅ Actif |
| `__seo_keywords` | `score_seo` | Score calculé pour priorisation | ✅ **Nouveau v3.0** |
| `gamme_aggregates` | `v2_count` | Nombre de V2 par gamme (max 20) | ✅ Actif |

---

## Migration depuis v2.1

| Avant (v2.1) | Après (v3.0) |
|--------------|--------------|
| V2 (tous les champions) | V3 (champions locaux) ou V2 (TOP 20) |
| V3 (variants secondaires) | V4 |
| V4 (volume = 0) | V5 |
| V5 (Bloc B) | V6 |

**Script de migration :**
```sql
-- 1. Renommer V5 → V6 (Bloc B)
UPDATE __seo_keywords SET v_level = 'V6' WHERE v_level = 'V5';

-- 2. Renommer V4 → V5 (volume = 0)
UPDATE __seo_keywords SET v_level = 'V5' WHERE v_level = 'V4';

-- 3. Renommer V3 → V4 (variants)
UPDATE __seo_keywords SET v_level = 'V4' WHERE v_level = 'V3';

-- 4. Renommer V2 → V3 (champions locaux)
UPDATE __seo_keywords SET v_level = 'V3' WHERE v_level = 'V2';

-- 5. Promouvoir TOP 20 V3 → V2 (par gamme)
-- Voir script insert-missing-keywords.ts
```

---

_Ce document est la source de vérité pour la classification V-Level SEO v3.0._
