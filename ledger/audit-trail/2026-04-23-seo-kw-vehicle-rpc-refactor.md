---
type: evidence-pack
date: 2026-04-23
owner: Fafa
duration: ~1h
session_id: seo-kw-vehicle-rpc-refactor-20260423
scope: Refactor insert-missing-keywords.ts — delegation de l'extraction vehicule a une RPC SQL dynamique
related_files:
  - backend/supabase/migrations/20260423_match_keyword_text_to_vehicle.sql
  - scripts/insert-missing-keywords.ts
prototype_gammes: [maitre-cylindre-de-frein, cable-de-frein-a-main]
tags: [pipeline, seo, kw, vlevel, rpc, dynamic-catalog, no-hardcode]
related_prs:
  - ak125/nestjs-remix-monorepo#132 (merged — delegation to SQL RPC)
related_canon:
  - ledger/audit-trail/2026-04-23-seo-kw-pipeline-maitre-cylindre.md (découverte du bug)
  - ledger/audit-trail/2026-04-23-seo-kw-pipeline-cable-frein-main.md (premier cas rencontré)
continues_from: 2026-04-23-seo-kw-pipeline-maitre-cylindre.md
---

# Refactor `insert-missing-keywords.ts` — extraction véhicule dynamique

## TL;DR

Session précédente (gamme 258 `maitre-cylindre-de-frein`) avait documenté que le script `scripts/insert-missing-keywords.ts` ratait **100 % des modèles anciens** (2cv, c15, c25, xantia, saxo, twingo i, etc.) à cause de regex hardcodées. Cette session traite le ticket de suivi : **refactor complet** pour déléguer l'extraction véhicule à une RPC SQL dynamique qui lit le full catalog `auto_modele` (1482+ modèles).

Évidence sur pg_id=258 :
- **Avant** : 0 vehicles matched → V2=0 V3=0 V4=0 V5=0 (v_level NULL pour 313 KW)
- **Après** : 66 vehicles matched → V2=8 V3=23 V4=15 V5=0 (46 type_ids classifiés)

PR merged : [ak125/nestjs-remix-monorepo#132](https://github.com/ak125/nestjs-remix-monorepo/pull/132) — squash commit `9a73cc58` 2026-04-23 15:32 UTC.

## 1 — Problème initial

Le script TS embarquait lignes 302-350 des regex hardcodées :

```typescript
const modelsWithGeneration = [
  /\b(clio)\s+(\d+|[ivx]+)\b/i,
  /\b(megane)\s+(\d+|[ivx]+)\b/i,
  /\b(scenic)\s+(\d+|[ivx]+)\b/i,
  /\b(twingo)\s+(\d+|[ivx]+)\b/i,
  /\b(golf)\s+(\d+|[ivx]+)\b/i,
];
// ... ~40 modèles hardcodés au total
```

**Conséquences** :

1. Les modèles anciens (2cv, 4l, c15, c25, espace, xantia, saxo, yaris, twingo i, laguna, fiat 500, ford s max, bmw e46) **ne matchaient jamais**.
2. Maintenance : chaque nouveau modèle = modification code + PR + deploy.
3. Divergence avec le canon : la RPC SQL `extract_vehicle_keywords` utilisait déjà `auto_modele` full catalog (1482 modèles) avec aliases romain/arabe (PR monorepo #122). Le script TS était stale.

Sur gamme 258 :
- `scripts/insert-missing-keywords.ts` (regex) → 0 vehicles détectés
- RPC SQL `extract_vehicle_keywords(258)` → 59 vehicles détectés

Et le script TS **écrasait** le `v_level` à NULL sur 313 rows, supprimant les assignations précédentes.

## 2 — Solution canon

### Nouvelle migration SQL

`20260423_match_keyword_text_to_vehicle.sql` ajoute deux RPCs `STABLE` (no DB write) :

- `match_keyword_text_to_vehicle(p_text text)` → `(matched_model, matched_energy)`
- `match_keyword_text_to_vehicle_batch(p_texts text[])` → batch variant

Logique identique à `extract_vehicle_keywords` (CTE `base_modeles` + `active_modeles` avec 3 match_forms) mais **per-text**, sans nécessiter de row `__seo_keywords` préalable.

**3 match_forms par modèle** :

| Form | Exemple stored | Match variant |
|---|---|---|
| original | `clio iii`, `2 cv`, `c15` | identique |
| arabic from roman | `clio iii` | `clio 3` |
| digit-letter collapsed | `2 cv` | `2cv` |

**Energy detection** : `hdi/tdi/dci` → diesel, `tce/thp/gti/vti` → essence, `phev/hybrid` → hybride, `electrique/electric/bev/ev` → electrique, `gpl/lpg/bifuel` → gpl.

### Refactor TS script

```typescript
// Nouvelle fonction async — 1 round-trip DB par chunk de 500 KW
async function buildVehicleExtractionCache(keywords: string[]): Promise<void> {
  // ... calls match_keyword_text_to_vehicle_batch RPC
}

// extractVehicleInfo() lit désormais depuis la Map (no regex)
function extractVehicleInfo(keyword, gamme) {
  const cached = vehicleExtractionCache.get(keyword);
  const model = cached?.model ?? null;
  // ... variant extraction préservée (strip model + gamme + displacement)
}
```

Appelé deux fois dans `main()` :
1. Juste après `parseGoogleAdsCSV` (pre-triage)
2. Juste avant la boucle `recalc` (refresh existing KW avec modèle stale)

**Sections supprimées** :
- ~100 lignes de regex `modelsWithGeneration`, `modelsOptionalGeneration`, `modelsCompound`, `modelsNoGeneration`
- Helper `generationToRoman()` (la RPC retourne la forme canonique)

## 3 — Sanity tests SQL

```sql
SELECT * FROM match_keyword_text_to_vehicle_batch(ARRAY[
  'maitre cylindre 2cv',         -- → 2 cv           ✅
  'maitre cylindre c15',         -- → c15            ✅
  'maitre cylindre c25',         -- → c25            ✅
  'cable frein a main clio 3',   -- → clio iii       ✅ (arabic→roman)
  'cable frein a main xantia',   -- → xantia         ✅
  'cable frein a main saxo',     -- → saxo           ✅
  'cable frein a main espace 4', -- → espace iv      ✅
  'cable frein a main 306 hdi',  -- → 306 / diesel   ✅
  'cable frein a main twingo 1', -- → twingo i       ✅
  'cable frein a main yaris',    -- → yaris          ✅
  'prix maitre cylindre'         -- → NULL / NULL    ✅ (pas de model)
]);
```

**11 / 11 cas validés**, incluant tous ceux qui échouaient avec le script précédent.

### Edge case : `4l`, `bmw e46`, `most`

- `4l` est stocké comme `R4` dans `auto_modele` (alias commercial ≠ alias technique)
- `bmw e46` est stocké comme `Série 3 (E46)` (chassis code entre parenthèses)
- `most` = marque (pas un modèle)

Ces cas ne sont pas adressés par ce refactor — nécessitent une table `auto_modele_aliases` (follow-up hors scope).

## 4 — Évidence runtime pg_id=258

```
AVANT refactor :
  Phase T: T3/T4 véhicule: 45 (triage uniquement, 0 extraction)
  Phase V: V2=0 V3=0 V4=0 V5=0
  Phase V-PROPAGATE: 0 keywords réalignés
  Stats par VEHICULE: V2=0 V3=0 V4=0 V5=0
  → 313 KW avec v_level=NULL

APRÈS refactor :
  Pré-fetch RPC : 66 / 314 KW avec modèle véhicule détecté
  Phase T: T3/T4 véhicule: 66
  Phase V: V2=8 V3=23 V4=15 V5=0
  Stats par VEHICULE: V2=8 V3=23 V4=15 V5=0 (46 distinct type_ids)
  Phase V1: xantia apparaît comme candidat V1 inter-gammes
  Phase V6: 25982 véhicules catalog (vs 26041 avant = +59 matched)
```

**Delta** : +66 vehicles détectés, +46 type_ids classifiés, +1 candidat V1 inter-gammes (xantia détecté comme V2 dans 2/5 gammes).

## 5 — Impact prévu sur le batch R1_ROUTER (232 gammes)

Le script a été utilisé sur 2 gammes du batch avant ce refactor :

| Gamme | Pre-refactor V-Level | Post-refactor V-Level (estimé) |
|---|---|---|
| `cable-de-frein-a-main` (pg_id=124) | V2=10 V3=26 V4=27 V5=14 | Probablement +20-30% couverture (plusieurs 2cv/4l/c15 dans le CSV) |
| `maitre-cylindre-de-frein` (pg_id=258) | V2=0 V3=0 V4=0 V5=0 | V2=8 V3=23 V4=15 V5=0 (+46 type_ids) |

Pour les 230 gammes restantes, ce refactor évite le scenario où le script efface les V-Level existants quand il ne matche aucun véhicule.

## 6 — Follow-up tickets

Notés dans ce document + propagés vers les deux evidences précédentes :

1. **Table `auto_modele_aliases`** — pour couvrir les surnoms commerciaux FR (4L → R4, E46 → Série 3, etc.). Structure proposée :
   ```sql
   CREATE TABLE auto_modele_aliases (
     modele_id INTEGER REFERENCES auto_modele(modele_id),
     alias TEXT,
     source TEXT, -- 'commercial', 'chassis', 'nickname'
     PRIMARY KEY (modele_id, alias)
   );
   ```
   Seed initial : R4=4l, R5=5gtl, Série 3 (E46)=e46, Série 3 (E90)=e90, etc.

2. **Script `scripts/seo/rebuild-type-vlevel.py`** — combine RPC + UPSERT `__seo_type_vlevel` en un seul CLI. Canon alignment pour remplacer le workflow manuel utilisé sur gamme 124 et 258.

3. **Relax `match_keywords_batch`** — accepter `energy IS NULL`. Aujourd'hui restrictif (exige les deux).

## 7 — Coverage manifest

```
scope_requested:        Refactor insert-missing-keywords.ts — no hardcode,
                        dynamic, meilleure solution pas de bricolage
scope_actually_scanned: 1 fichier TS (scripts/insert-missing-keywords.ts)
                        + 1 migration SQL (match_keyword_text_to_vehicle)

files_read_count:       3 (script TS, extract_vehicle_keywords RPC def,
                           CSV de test)
excluded_paths:         autres scripts SEO (out of scope)
unscanned_zones:        pg_id autre que 258 (pas re-run depuis refactor)

corrections_proposed:   1 RPC SQL + 1 batch variant + refactor script
corrections_applied:
  - DB : CREATE FUNCTION match_keyword_text_to_vehicle (live)
  - DB : CREATE FUNCTION match_keyword_text_to_vehicle_batch (live)
  - Migration file : 20260423_match_keyword_text_to_vehicle.sql
  - Script refactor : -100 lignes regex, +50 lignes RPC cache
  - PR merged : ak125/nestjs-remix-monorepo#132 (9a73cc58)
  - UPSERT __seo_type_vlevel pour pg_id=258 post-refactor

validation_executed:
  - Sanity SQL : 11/11 test cases pass (2cv/c15/xantia/espace 4/...)
  - TypeScript compile : tsc --noEmit OK
  - Runtime pg_id=258 : 0 → 66 vehicles, V-Level 0 → 46 type_ids
  - CI GitHub : TypeScript / ESLint / Tests / CodeQL / Migration Safety — SUCCESS

remaining_unknowns:
  - Retraitement pg_id=124 avec le script refactoré (pas re-run)
  - Couverture du cas 4l / e46 / commercial aliases
  - Impact sur les 230 gammes R1_ROUTER non encore traitées

final_status: SCOPE_SCANNED
```

## 8 — Leçons

1. **Toujours préférer DB-driven over hardcode** pour les catalogues qui changent (modèles véhicules, marques, etc.). Une regex hardcodée = dette technique invisible qui bloque silencieusement 100 % des cas non couverts.

2. **Detecter les écrasements silencieux** : le script TS écrivait `v_level=NULL` sur 313 rows existantes quand il ne matchait rien. La bonne règle canon = ne JAMAIS écraser une valeur pré-existante sans vérification explicite. Follow-up : ajouter un guard dans le script.

3. **Comparer deux implémentations du même concept** révèle les drifts. Le script TS était divergent de la RPC SQL depuis PR #122 (2 semaines). Les audits périodiques "la DB et le code disent-ils la même chose ?" doivent être récurrents.
