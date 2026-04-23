---
type: runbook
date: 2026-04-22
owner: Fafa
scope: Rollout d'une gamme SEO — ingestion CSV Google Ads KP → contenu R1/R3/R4/R6 publiable
tags: [runbook, seo, rollout, gamme, pipeline]
version: 1.0
---

# Runbook — Rollout d'une gamme SEO

> Procédure canonique pour passer d'un CSV Google Ads Keyword Planner à une gamme entièrement enrichie (R1/R3/R4/R6) en DB, validée par QA 9 phases.

## Pré-requis

1. **CSV Google Ads KP** exporté au format UTF-16 natif
2. **pg_alias** de la gamme cible (existe dans `pieces_gamme` avec pg_level 1 ou 2)
3. **Backend NestJS tourne** sur `localhost:3000` (vérifier via `curl -m 3 localhost:3000/health`)
4. **INTERNAL_API_KEY** dans `backend/.env`

---

## Workflow 5 étapes

### Étape 1 — Déposer le CSV

```bash
# Path canonique
cp "<source>.csv" /opt/automecanik/app/data/keywords/inbox/<pg_alias>_YYYY-MM-DD.csv
```

Le fichier doit matcher le pattern `<pg_alias>_<date>.csv` pour que le slug soit détecté auto.

### Étape 2 — Import + filtrage RAG

```bash
python3 /opt/automecanik/app/scripts/seo/import-gads-kp.py \
  /opt/automecanik/app/data/keywords/inbox/<pg_alias>_YYYY-MM-DD.csv
```

**Output attendu** :
- Log `[N] raw → [M] pertinents`
- CSV déplacé vers `processed/<timestamp>__<name>.csv`
- Snapshot JSON dans `output/<timestamp>__<alias>__import-summary.json`
- Rows upserted dans `__seo_keywords` (pg_id, source='google-ads-kp')

**Si `pertinents / raw < 50%`** → voir Troubleshooting § "Ratio faible".

### Étape 3 — Classification SQL heuristique

```sql
-- Exécuter via MCP Supabase ou psql
-- Remplacer PG_ID et PG_ALIAS
WITH kw_pool AS (
  SELECT keyword, lower(keyword_normalized) AS k, COALESCE(volume::int,0) AS vol
  FROM __seo_keywords WHERE pg_id = {PG_ID} AND source = 'google-ads-kp' AND keyword IS NOT NULL
),
classified AS (
  SELECT kp.keyword AS kw, kp.vol,
    CASE
      WHEN kp.k ~ '\y(prix|tarif|pas cher|acheter|commande|cout|euro|achat|oscaro|norauto|feu vert|midas)\y' THEN 'R1'
      WHEN kp.k ~ '\y(bosch|brembo|ate|trw|ferodo|textar|valeo|mann|mahle|purflux|hengst|filtron|wix|ufi|febi|delphi|pagid|bendix)\y' THEN 'R6'
      WHEN kp.k ~ '\y(comment|changer|remplacer|tutoriel|tuto|monter|demonter|poser|remplacement|procedure|etapes|purger|nettoyer)\y' THEN 'R3'
      WHEN kp.k ~ '\y(c est quoi|cest quoi|quoi sert|quel role|role du|fonction|pourquoi|quand changer|duree de vie|difference)\y' THEN 'R4'
      ELSE 'R1' END AS role FROM kw_pool kp
),
percentiled AS (
  SELECT kw, role, CASE role WHEN 'R1' THEN 'transactional' WHEN 'R3' THEN 'how_to' WHEN 'R4' THEN 'informational' WHEN 'R6' THEN 'investigation' END AS intent,
    CASE WHEN PERCENT_RANK() OVER (PARTITION BY role ORDER BY vol) >= 0.9 THEN 'HIGH'
         WHEN PERCENT_RANK() OVER (PARTITION BY role ORDER BY vol) >= 0.6 THEN 'MED' ELSE 'LOW' END AS vol_cat
  FROM classified
)
INSERT INTO __seo_keyword_results (pg_id, pg_alias, role, kw, intent, vol, source)
SELECT {PG_ID}, '{PG_ALIAS}', role, kw, intent, vol_cat, 'google-ads-kp' FROM percentiled
ON CONFLICT (pg_id, kw, role) DO UPDATE SET vol = EXCLUDED.vol, intent = EXCLUDED.intent, source = EXCLUDED.source;
```

### Étape 4 — V-Level (extraction véhicule + recalcul)

```sql
-- Extract vehicle KW from pool
SELECT COUNT(*) AS matched FROM extract_vehicle_keywords({PG_ID});
```

```bash
# Calcul V-Level canonique
python3 /opt/automecanik/app/scripts/seo/recalculate_vlevel.py {PG_ID}
```

**Output attendu** : `V2 (champions): X, V3 (variantes): Y, V4 (catalogue): Z`.

**Si total = 0 et corpus très niche** → WARN acceptable (pas bloquant pour Phase 5B).

### Étape 5 — Enrich R1 + R4 + R6

```bash
IK='<INTERNAL_API_KEY>'
for role in R1_ROUTER R4_REFERENCE R6_GUIDE_ACHAT; do
  target="{PG_ID}"
  [ "$role" = "R4_REFERENCE" ] && target="{PG_ALIAS}"
  curl -sS -m 90 -X POST http://localhost:3000/api/internal/pipeline/execute \
    -H "X-Internal-Key: $IK" -H "Content-Type: application/json" \
    -d "{\"roleId\":\"$role\",\"targetIds\":[\"$target\"],\"dryRun\":false}"
done
```

---

## QA 9 phases (skill `/gamme-qa`)

Lancer systématiquement après Étape 5 :

```
/gamme-qa {pg_alias}
```

Les 9 phases :

| Phase | Gate | Source |
|---|---|---|
| 1 | RAG + ingestion (Zod valid) | parser SSOT |
| 2 | Classification (R1 majoritaire) | `__seo_keyword_results` |
| 3 | Keyword plans R1/R3/R4/R6 (score ≥ 70) | `__seo_r{1,3,4,6}_keyword_plan` |
| 4 | Content enrichment (R1 gk ≥ 80, R4 def ≥ 400, R6 OK, R3 12 sections) | DB content tables |
| 5 | Invariants DB (0 orphan, 0 bug args=title) | CHECK constraints |
| 5B | V-Level canonique (couverture types) | `__seo_type_vlevel` |
| 6 | Images (SKIPPED — module dédié) | — |
| 7 | Pollution + vocab interdit | regex scan |
| 8 | Pipeline stage = FULLY_ENRICHED | `v_kw_pipeline_status` |
| 9 | Qualité éditoriale (accents, titres, compo, anti_mistakes, empty strings, scraping) | regex + cross-role |

**Verdict PASS** = 0 BLOCK sur toutes les phases.

---

## Fix Q5 (anti_mistakes) — souvent requis

Si Phase 9 reporte `q5=1` (R6 anti_mistakes vide alors que R3 S5 est rempli), injecter manuellement 5 anti-mistakes spécifiques à la gamme :

```sql
UPDATE __seo_gamme_purchase_guide
SET sgpg_anti_mistakes = ARRAY[
  '<anti-mistake 1 spécifique à la gamme>',
  '<anti-mistake 2>',
  '<anti-mistake 3>',
  '<anti-mistake 4>',
  '<anti-mistake 5>'
]
WHERE sgpg_pg_id::text = '{PG_ID}';
```

Utiliser des anti-mistakes **vraiment spécifiques** à la pièce (ex: pour filtre à huile : "Ne pas trop serrer le filtre", "Graisser le joint neuf", etc.). Pas de génériques.

---

## Troubleshooting

### Ratio `pertinents/raw < 50%` → ajouter aliases SEO au dict central

1. Inspecter échantillon des KW rejetés (volume élevé)
2. Identifier synonymes commerciaux absents du core words
3. Ajouter dans `/opt/automecanik/app/config/rag-alias-expansions.yaml` :
   ```yaml
   <pg_alias>:
     - synonyme 1
     - synonyme 2
   ```
4. Re-importer (idempotent) depuis `processed/<timestamp>__<name>.csv`

### Pipeline stage `KP_INCOMPLETE`

Vérifier status des 4 KP. R4 KP est optionnel. Si R1/R3/R6 missing :
```sql
SELECT rkp_status FROM __seo_r1_keyword_plan WHERE rkp_pg_id::text='{PG_ID}';
```
Si null → relancer l'agent `r1-keyword-planner` correspondant.

### Phase 4 R4 flags `GENERIC_DEFINITION` / `THIN_CHECKLIST`

Normal pour beaucoup de gammes. Enrichir le RAG `domain.role` (≥ 300 chars de description factuelle) + relancer R4 enrich.

### R6 `anti_mistakes` persist bug

Connu (P3 backlog). L'API retourne les items mais DB reste vide. Contournement : UPDATE direct comme décrit § "Fix Q5".

### Corpus niche (< 100 KW) → V-Level = 0

Normal si pas de KW véhicule matchable. Pas bloquant. Les pages R8 véhicule ne seront pas routées pour cette gamme, mais R1/R3/R4/R6 restent fonctionnels.

---

## Fichiers de référence

| Path | Rôle |
|---|---|
| `config/rag-alias-expansions.yaml` | Dict aliases SEO centralisé |
| `scripts/seo/import-gads-kp.py` | Import CSV + filtre RAG + lifecycle |
| `scripts/seo/recalculate_vlevel.py` | Calcul V-Level canonique |
| `.claude/skills/gamme-qa/SKILL.md` | QA 9 phases |
| `.claude/skills/kw-classify/SKILL.md` | Classification contextuelle (alternative à SQL heuristique) |
| `data/keywords/inbox/` | Dépôt CSV |
| `data/keywords/processed/` | CSV archivés post-import |
| `data/keywords/output/` | JSON snapshots |

---

## Cheatsheet — recette one-liner

```bash
# Variables
PG_ID=X
PG_ALIAS=...
CSV_PATH=/opt/automecanik/app/data/keywords/inbox/${PG_ALIAS}_$(date +%F).csv
IK='<key>'

# Étape 1-2
python3 /opt/automecanik/app/scripts/seo/import-gads-kp.py $CSV_PATH

# Étape 3 (via SQL ou /kw-classify skill)
# Étape 4
python3 /opt/automecanik/app/scripts/seo/recalculate_vlevel.py $PG_ID

# Étape 5 (enrich triple)
for role in R1_ROUTER R4_REFERENCE R6_GUIDE_ACHAT; do
  t=$PG_ID; [ "$role" = "R4_REFERENCE" ] && t=$PG_ALIAS
  curl -sS -X POST http://localhost:3000/api/internal/pipeline/execute \
    -H "X-Internal-Key: $IK" -H "Content-Type: application/json" \
    -d "{\"roleId\":\"$role\",\"targetIds\":[\"$t\"],\"dryRun\":false}"
done

# QA 9 phases
# /gamme-qa $PG_ALIAS
```

---

_Runbook v1.0 — 2026-04-22. Réf evidence packs :_
- _2026-04-21-pipeline-content-hardening (P0/P0.5/P1/P1.6)_
- _2026-04-22-pipeline-quality-hardening-p2 (accents triggers + Phase 9)_
- _2026-04-22-alias-expansions-batch-preventif (dict central + bug apostrophe)_
- _2026-04-22-r6-antimistakes-cross-contamination-fix_
- _2026-04-22-rollout-9-gammes-pipeline-state_
