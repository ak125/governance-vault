---
type: evidence-pack
date: 2026-04-23
owner: Fafa
duration: ~2h
session_id: seo-kw-pipeline-cable-frein-main-20260423
scope: Pipeline SEO KW end-to-end pour `cable-de-frein-a-main` + restauration V-Level + détection gap R6 gatekeeper
related_files:
  - scripts/seo/import-gads-kp.py
  - config/rag-alias-expansions.yaml
  - scripts/insert-missing-keywords.ts
  - backend/src/modules/admin/services/buying-guide-enricher.service.ts
prototype_gammes: [cable-de-frein-a-main]
tags: [pipeline, seo, kw, r1-router, vlevel, r6-gatekeeper-gap, canon]
related_prs:
  - ak125/nestjs-remix-monorepo#117 (closed, superseded)
  - ak125/nestjs-remix-monorepo#124 (merged — --suggest-aliases canon)
  - ak125/nestjs-remix-monorepo#125 (merged — YAML aliases batch)
related_canon:
  - ledger/rules/rules-seo-kw-import.md
continues_from: 2026-04-22-alias-expansions-batch-preventif.md
---

# Pipeline SEO KW end-to-end — `cable-de-frein-a-main`

## TL;DR

Gamme 15/232 traitée canon bout-en-bout : `R-SEO-KW-01` déclenchée (12.56 % vol rejeté), 5 aliases ajoutés via PR batch R-SEO-KW-03, import live 142 KW, classification skills-first, QA 9 phases PASS. Incident : PR #117 (alias enrichment) en état `dirty` depuis merge PR #122 → rebase propre en PR #124. Gap systémique identifié : `sgpg_gatekeeper_score` NULL pour 235 / 241 rows (97.5 %) — aucun service R6 gatekeeper n'est wired côté code. Pipeline V-Level canon restauré en SQL direct (le script Python `recalculate_vlevel.py` pointait vers la table `__seo_keywords_clean` désormais archivée).

## 1 — Rebase PR #117 → PR #124 (canon)

### Diagnostic

PR #117 (`feat/seo-kw-alias-enrichment-system`) contenait deux commits :
- `4024fd60` — loader `config/rag-alias-expansions.yaml` (déjà mergé via PR #122 `91284915`)
- `ee6199a1` — `--suggest-aliases` (non mergé)

État GitHub : `mergeable: false`, `mergeable_state: dirty`, `rebaseable: false`. Tentative de rebase → conflits dans `normalize_kw` et `load_alias_expansions` (déjà présents sur main).

### Solution canon

Worktree neuf `/tmp/seokw-rebase` depuis `origin/main` → cherry-pick **sélectif** de `ee6199a1` (le seul commit nouveau) → résolution conflit `main()` en **supprimant** la logique lifecycle CSV (processed/failed/output) bundled dans le commit mais hors-sujet du titre (`--suggest-aliases`). Focus strict sur la feature nommée.

- Push `fix/seo-kw-suggest-aliases-rebase` → PR #124 → CI green → squash merge (`a1eb9e82`)
- Close PR #117 en pointant sur PR #124 (`Superseded by #124`).

## 2 — Batch YAML aliases (R-SEO-KW-03)

Dry-run `--suggest-aliases --threshold-vol 50` :

```
9 rejets, vol cumulé = 1350 (ratio = 1350/10750 = 12.56 %)
→ R-SEO-KW-01 : review obligatoire (seuil 5 %)
```

Arbitrage par `R-SEO-KW-02` (arbre de décision) :

| Décision | KW | Rationale |
|---|---|---|
| Alias YAML | `cable de frein` | Générique catalogue = frein à main |
| Alias YAML | `cables de frein a main` | Variation morphologique pluriel |
| Alias YAML | `cable frein de stationnement` | Syn FR |
| Alias YAML | `cable frein parking` | Syn anglicisme (substring `scenic 2`) |
| Alias YAML | `cable frein voiture` | Forme commerciale |
| Hors-scope | `cable frein tambour` | Gamme `frein-tambour` distincte |
| Couverts | `cable de frein timonerie prix`, `cable de frein voiture` | Match via substring `cable de frein` |

Post-YAML : 142 pertinents, 1 rejet vol 50 → **0.47 %** (≪ 5 %). R-SEO-KW-01 satisfaite.

Branche `fix/seo-kw-aliases-r1-router-20260423` → PR #125 → CI green → squash merge (`4e87e3fa`).

## 3 — Import + classify + content

| Étape | Script / service | Résultat |
|---|---|---|
| Import | `import-gads-kp.py --pg-id 124` | 152 raw → 142 pertinents upsert |
| Classification | skill `/kw-classify` (skills-first) | R1=127 (HIGH=13 MED=38 LOW=76), R3=15 (HIGH=2 MED=4 LOW=9), R4=0, R6=0 |
| Contenu R1/R3/R4/R6 | pré-existant | KP validated, scores ≥ 70, 12 sections R3 |

Règle R4/R6 = 0 avec `source=google-ads-kp` → `INFO` canon (les intents how-to et informationnels viennent de GSC, pas de Google Ads KP générique).

## 4 — R6 enricher — gap systémique identifié

### Run canonique

```bash
POST /api/admin/buying-guides/enrich
{"pgIds":["124"], "dryRun": false}
→ 4 sections updated, avgConfidence=1.0
```

`sgpg_source_verified_at` mis à jour (`2026-04-23 14:32:40 UTC`). Contenu RAG propagé : `intro_role`, `decision_tree`, `selection_criteria`, `symptoms`, `anti_mistakes`, `faq`, `how_to_choose`, `risk_*`.

### Gap détecté

```sql
SELECT COUNT(*) FILTER (WHERE sgpg_gatekeeper_score IS NOT NULL)
FROM __seo_gamme_purchase_guide;
→ 6 / 241 rows (2.5 %)
```

Recherche code :

```bash
grep -rn "sgpg_gatekeeper_score" backend/src \
  | grep -v 'types.ts'
→ 0 occurrences (uniquement déclarations de types)
```

**Diagnostic** : `r1s_gatekeeper_score/flags` est peuplé par `R1EnricherService` ligne 192-193. Aucun service équivalent pour R6 (`BuyingGuideQualityGatesService` existe mais ne persiste rien). C'est une asymétrie architecturale, pas spécifique à une gamme.

### Action

Hors-scope QA gamme. À tracker en ticket de suivi : wire un service R6 symétrique à R1, qui compute `sgpg_gatekeeper_score/flags/checks` après chaque enrich.

## 5 — V-Level pipeline — restauration canon

### Diagnostic

Script `scripts/seo/recalculate_vlevel.py` lit `__seo_keywords_clean`. Cette table a été déplacée vers le schéma `_archive` (vérifié via `information_schema.tables.table_schema = '_archive'`). Le script est cassé.

Pipeline canon actuel :

1. `extract_vehicle_keywords(pg_id)` (RPC SQL) — match model+energy via `auto_modele` (avec alias romain/arabe depuis PR #122)
2. `scripts/insert-missing-keywords.ts --recalc` — calcule V2/V3/V4/V5 et les écrit dans `__seo_keywords.v_level`
3. **Écriture `__seo_type_vlevel`** — aucun script live ne le fait depuis l'archivage de `__seo_keywords_clean`

### Fix canon SQL

UPSERT via DISTINCT ON depuis `__seo_keywords` :

```sql
INSERT INTO __seo_type_vlevel (pg_id, type_id, v_level, source, model, energy, confidence, updated_at)
SELECT DISTINCT ON (sk.pg_id, sk.type_id)
  sk.pg_id, sk.type_id, sk.v_level,
  CASE sk.v_level
    WHEN 'V2' THEN 'champion' WHEN 'V3' THEN 'variant'
    WHEN 'V4' THEN 'catalog'  WHEN 'V5' THEN 'sibling'
  END,
  sk.model,
  NULLIF(sk.energy, 'unknown'),
  CASE WHEN sk.volume > 0 THEN 0.90 ELSE NULL END,
  now()
FROM __seo_keywords sk
WHERE sk.pg_id = :pg_id
  AND sk.type_id IS NOT NULL
  AND sk.v_level IN ('V2','V3','V4','V5')
ORDER BY sk.pg_id, sk.type_id,
  CASE sk.v_level WHEN 'V2' THEN 1 WHEN 'V3' THEN 2 WHEN 'V4' THEN 3 WHEN 'V5' THEN 4 END,
  sk.volume DESC
ON CONFLICT (pg_id, type_id) DO UPDATE SET
  v_level    = EXCLUDED.v_level,
  source     = EXCLUDED.source,
  model      = EXCLUDED.model,
  energy     = EXCLUDED.energy,
  confidence = EXCLUDED.confidence,
  updated_at = EXCLUDED.updated_at;
```

Règle de priorité : V2 (champion) > V3 (variant with volume) > V4 (catalog-only) > V5 (sibling). Un `type_id` qui a à la fois V3 et V4 KW garde V3 (meilleur).

### Résultat pg_id=124

```
48 rows : V2=10 champions, V3=24 variants, V4=0, V5=14 siblings
avg_confidence = 0.90
newest = 2026-04-23
kw_vehicle_without_vlevel = 0 (0 orphelin)
```

### Follow-up canon

À porter en script live (Python ou TS) + doc MOC pour que `/gamme-qa` Phase 5B ne déclenche plus WARN sur les imports Google Ads KP :

```
scripts/seo/rebuild-type-vlevel.py <pg_id>
```

Qui exécute le SQL ci-dessus + invalide cache Redis `vlevel:{pg_id}:*`.

## 6 — Verdict final /gamme-qa

| Phase | Avant fixes | Après fixes |
|---|---|---|
| 1 RAG+ingest | PASS | PASS |
| 2 Classification | PASS | PASS |
| 3 KP R1/R3/R4/R6 | PASS | PASS |
| 4 Content | PASS (WARN R6 score NULL) | PASS (WARN systémique) |
| 5 Invariants | PASS | PASS |
| **5B V-Level** | **WARN (total=0)** | **PASS (48 rows, 0 orphan)** |
| 7 Pollution | PASS | PASS |
| 8 pipeline_stage | PASS | PASS |
| 9 Qualité éditoriale | PASS | PASS |

**PASS** final. Progression : 14 → 15 / 232.

## 7 — Leçons et règles à re-appliquer

1. **PR dirty → rebase sélectif**, pas cherry-pick aveugle : identifier les commits déjà appliqués sur main (`git log --oneline origin/main -- <file>`) et skip.
2. **Focus commit** : si un commit bundle une feature nommée + un bonus hors-sujet, résoudre le conflit en gardant uniquement la feature nommée. Le bonus doit faire l'objet d'une PR dédiée.
3. **Scripts Python > 3 mois → suspicion de stale**. Toujours vérifier `information_schema.tables.table_schema` pour les tables référencées (ex : `__seo_keywords_clean` → `_archive`).
4. **Gaps symétriques** : quand un R* possède un champ `gatekeeper_*`, tous les autres R* devraient avoir le service correspondant. Audit à faire : `grep -rn "_gatekeeper_score\b" backend/src/modules/admin/services/`.

## 8 — Coverage manifest

```
scope_requested:       QA + 2 WARN fixes pour pg_id=124
scope_actually_scanned: 1 gamme (cable-de-frein-a-main), 9 phases QA, 2 fixes

files_read_count:      ~18 fichiers (scripts/seo/*, backend/src/modules/admin/services/buying-guide*, /scripts/insert-missing-keywords.ts, RAG .md)
excluded_paths:        aucun (scope strict gamme 124)
unscanned_zones:       autres gammes du batch R1_ROUTER (hors scope)

corrections_proposed:  5 aliases YAML, rebase PR #117, SQL port __seo_type_vlevel, enricher run
corrections_applied:
  - PR #124 merged (+86/-2 lines scripts/seo/import-gads-kp.py)
  - PR #125 merged (+6 lines config/rag-alias-expansions.yaml)
  - UPSERT 48 rows __seo_type_vlevel (pg_id=124 scope)
  - Enricher run (POST /api/admin/buying-guides/enrich pg=124)

validation_executed:
  - Dry-run before/after R-SEO-KW-01 (12.56% → 0.47%)
  - QA 9 phases re-run post-fixes
  - kw_vehicle_without_vlevel = 0 check

remaining_unknowns:
  - R6 gatekeeper service implementation (follow-up ticket)
  - Port script live `rebuild-type-vlevel.py` (follow-up)
  - Distribution V4 dans __seo_type_vlevel (0 vs 21 reportés par insert-missing-keywords — métriques différentes à réconcilier)

final_status: SCOPE_SCANNED
```
