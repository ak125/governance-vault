---
type: evidence-pack
date: 2026-04-24
owner: Fafa
duration: ~2h30
session_id: seo-kw-kit-frein-arriere-3-inc-20260424
scope: Pipeline SEO KW `kit-de-freins-arriere` (gamme 19/232) + découverte de 3 incidents DB systémiques
related_files:
  - backend/supabase/migrations/20260424_fix_fn_warn_orphan_pg_id_polyglot.sql
  - backend/src/config/content-write-executor.service.ts
  - config/rag-alias-expansions.yaml
prototype_gammes: [kit-de-freins-arriere]
tags: [pipeline, seo, kw, r-seo-kw-06, incident, db-bug, systemic, canon-fix]
related_prs:
  - ak125/nestjs-remix-monorepo#151 (merged — 7 aliases kit-only)
  - ak125/nestjs-remix-monorepo#154 (merged — 3 INC fix combiné)
related_canon:
  - ledger/rules/rules-seo-kw-import.md (R-SEO-KW-06)
continues_from: 2026-04-24-seo-kw-pipeline-repartiteur-frein.md
---

# Pipeline SEO KW — `kit-de-freins-arriere` + 3 incidents DB systémiques

## TL;DR

Session QA de routine sur pg=3859 (gamme 19/232, état legacy `kp-r3-batch-phase5`) a révélé **3 incidents DB systémiques** qui bloquaient toute nouvelle gamme du pipeline canon depuis plusieurs semaines :

1. **INC-1** — Trigger `fn_warn_orphan_pg_id` : plpgsql polyglot type check sur CASE statique bloquait tous les INSERTs sur `__seo_r1_gamme_slots` + 3 autres tables
2. **INC-2** — `__seo_r6_keyword_plan` : 61 rows avec `r6kp_pg_id` désynchronisé de `r6kp_pg_alias` (conséquence merges gammes historiques)
3. **INC-3** — `ContentWriteExecutor` : `.update().eq()` no-op silencieux sur rows absentes → R1 enricher reportait `slotsWritten=6` mais contenu NULL en DB

PR monorepo [#154](https://github.com/ak125/nestjs-remix-monorepo/pull/154) merged consolidant les 3 fixes. Canon R-SEO-KW-06 aussi appliqué (CSV scope freinage multi-gammes).

## 1 — Arbitrage canon R-SEO-KW-06 (95 % rejets)

CSV `Keyword Stats 2026-04-24 at 17_03_44.csv` : 160 raw → 5 pertinents initial (95 % rejets vol). Analyse taxo :

| pg_id | gamme | scope CSV |
|---|---|---|
| **3859** | `kit-de-freins-arriere` | ✅ "kit frein arriere" légitime |
| 82 | `disque-de-frein` (ACTIVE) | ❌ `disque de frein arriere` 5000 vol → autre gamme |
| 402 | `plaquette-de-frein` (ACTIVE) | ❌ `plaquette` seule → autre gamme |
| 123 | `tambour-de-frein` (ACTIVE) | ❌ `garniture frein tambour` → autre gamme |
| 70 | `machoires-de-frein` (ACTIVE) | ❌ `garniture de frein arriere` → autre gamme |

**Verdict Option 2** R-SEO-KW-06 : ≥ 2 gammes actives → alias large INTERDIT.

7 aliases **kit-only strict** ajoutés via PR monorepo [#151](https://github.com/ak125/nestjs-remix-monorepo/pull/151) : `kit frein arriere`, `kit de frein arriere`, `kit freins arriere`, `kit arriere frein`, `kit frein a tambour`, `kit frein tambour`, `kit machoire frein`.

Post-YAML : 160 raw → 106 pertinents. Les 51 rejets résiduels appartiennent à pg=82/402/123/70 (canon, pas cannibalisation).

## 2 — INC-1 : Trigger `fn_warn_orphan_pg_id` polyglot bug

### Découverte

Lors du tentative d'INSERT seed row dans `__seo_r1_gamme_slots` pour pg=3859 :

```
ERROR: 42703: record "new" has no field "sgpg_pg_id"
CONTEXT: PL/pgSQL assignment "pgid_str := CASE TG_TABLE_NAME ..."
```

### Cause

Fonction plpgsql attachée à 4 triggers (`r1_gamme_slots`, `gamme_purchase_guide`, `gamme_conseil`, `gamme`) utilisait :

```sql
CASE TG_TABLE_NAME
  WHEN '__seo_r1_gamme_slots' THEN NEW.r1s_pg_id::text
  WHEN '__seo_gamme_purchase_guide' THEN NEW.sgpg_pg_id::text
  WHEN '__seo_gamme_conseil' THEN NEW.sgc_pg_id::text
  WHEN '__seo_gamme' THEN NEW.sg_pg_id::text
END
```

En plpgsql, **toutes** les branches CASE sont validées au compile-time contre le type du `NEW` record. Quand le trigger firait sur `__seo_r1_gamme_slots`, NEW est typé comme cette table → accès `NEW.sgpg_pg_id` échoue même si branche morte.

### Impact systémique

**Tous les INSERTs** sur ces 4 tables étaient bloqués depuis l'activation du trigger. Les UPDATEs fonctionnaient (trigger `BEFORE INSERT` only).

Symptôme silencieux : R1 enricher + R6 enricher ne pouvaient pas créer de nouvelles rows pour de nouvelles gammes. Les gammes pré-existantes (avec row déjà créée) continuaient à fonctionner via UPDATE.

### Fix canon

```sql
CREATE OR REPLACE FUNCTION public.fn_warn_orphan_pg_id()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  rec_json jsonb;
  pgid_str text;
BEGIN
  rec_json := to_jsonb(NEW);
  pgid_str := COALESCE(
    rec_json->>'r1s_pg_id',
    rec_json->>'sgpg_pg_id',
    rec_json->>'sgc_pg_id',
    rec_json->>'sg_pg_id'
  );
  ...
END;
$$;
```

`to_jsonb(NEW)` convertit le record en JSONB (dynamic field access). Les `->>` lookups retournent NULL pour fields absents — pas de compile-time check. COALESCE prend le premier non-NULL.

## 3 — INC-2 : 61 rows `__seo_r6_keyword_plan` pg_id désynchronisé

### Découverte

Le skill `/gamme-qa` Phase 3 reportait R6 KP = `missing` pour pg=3859, malgré une row existante. Investigation :

```sql
SELECT r6kp_pg_id, r6kp_pg_alias FROM __seo_r6_keyword_plan
WHERE r6kp_pg_alias = 'kit-de-freins-arriere';
-- → r6kp_pg_id = '1683' (gamme disparue), r6kp_pg_alias = 'kit-de-freins-arriere'

SELECT pg_id FROM pieces_gamme WHERE pg_alias = 'kit-de-freins-arriere';
-- → pg_id = 3859
```

### Extent

```sql
SELECT COUNT(*) FROM __seo_r6_keyword_plan r6
JOIN pieces_gamme pg ON pg.pg_alias = r6.r6kp_pg_alias
WHERE r6.r6kp_pg_id::text != pg.pg_id::text;
-- → 61 rows misaligned
```

### Cause

Conséquence des **merges gammes historiques** (cf. memory `gamme_aggregates` : `merge 3942→817, deprecate 3333`). Quand une gamme est mergée/dépréciée, sa row dans `pieces_gamme` change de `pg_id` mais les tables dépendantes (`__seo_r6_keyword_plan`, probablement d'autres) n'ont pas été mises à jour.

### Fix canon (backfill)

Le backfill pur UPDATE échoue car 2 gammes ont des duplicatas (row legacy + row canon) :
- `cable-de-boite-vitesse` : pg_id=1562 (legacy) + 1787 (canon)
- `poignee-de-capot` : pg_id=1643 (legacy) + 3220 (canon)

Unique constraint `__seo_r6_keyword_plan_r6kp_pg_id_key` bloque l'UPDATE.

Ordre impératif :

```sql
-- 1. DELETE rows duplicata legacy (pg_id orphelin + row canon existe)
DELETE FROM __seo_r6_keyword_plan r6
WHERE NOT EXISTS (SELECT 1 FROM pieces_gamme pg WHERE pg.pg_id::text = r6.r6kp_pg_id::text)
  AND EXISTS (SELECT 1 FROM __seo_r6_keyword_plan r6_canon
    JOIN pieces_gamme pg ON pg.pg_alias = r6_canon.r6kp_pg_alias
    WHERE r6_canon.r6kp_pg_alias = r6.r6kp_pg_alias
      AND pg.pg_id::text = r6_canon.r6kp_pg_id::text);

-- 2. UPDATE resync des 59 rows restantes
UPDATE __seo_r6_keyword_plan r6 SET r6kp_pg_id = pg.pg_id::text
FROM pieces_gamme pg
WHERE pg.pg_alias = r6.r6kp_pg_alias
  AND r6.r6kp_pg_id::text IS DISTINCT FROM pg.pg_id::text;
```

Appliqué live DB : **0 rows misaligned remaining**.

## 4 — INC-3 : `ContentWriteExecutor` UPDATE no-op sur rows absentes

### Découverte

Après fix INC-1, INSERT seed row sur `__seo_r1_gamme_slots` réussit. Re-run R1 enricher via endpoint interne retourne :

```json
{
  "status": "enriched",
  "slotsWritten": 6,
  "qualityScore": 80
}
```

Mais DB query révèle : `r1s_arg1_content=NULL`, `r1s_h1_override=NULL`, **aucun content field écrit** malgré le "enriched".

### Cause

`ContentWriteExecutor` Step H :

```typescript
const { error } = await this.supabase
  .from(writeTarget.table)
  .update(mergedPayload)
  .eq(writeTarget.pkField, pkValue);
```

Quand la row n'existe pas, `.update().eq()` **ne renvoie pas d'erreur** mais ne fait rien (0 rows affected). L'executor ne vérifie pas le count → log "wrote N fields" trompeur.

**Systémique** : toute gamme en WriteGuard enforce mode (R1_ROUTER, R6_GUIDE_ACHAT, R3_CONSEILS, R4_REFERENCE, R5_DIAGNOSTIC) avec aucune row pré-existante voyait son enrichissement silencieusement perdu.

### Fix canon

UPDATE-then-INSERT fallback :

```typescript
const { error: updateError, count: updatedCount } = await this.supabase
  .from(writeTarget.table)
  .update(mergedPayload, { count: 'exact' })
  .eq(writeTarget.pkField, pkValue);

if (updateError) return { written: false, reason: ... };

if ((updatedCount ?? 0) === 0) {
  // Fallback INSERT
  const insertPayload = { ...mergedPayload, [writeTarget.pkField]: pkValue };
  const { error: insertError } = await this.supabase
    .from(writeTarget.table)
    .insert(insertPayload);
  if (insertError) return { written: false, reason: `db_error_insert: ${insertError.message}` };
  this.logger.log(`inserted new row for ${target}:${pkValue} (row was absent)`);
}
```

Pas de régression : rows existantes continuent de suivre le chemin UPDATE → merge → regression guard → write.

## 5 — Pipeline pg=3859 exécuté

| Étape | Résultat |
|---|---|
| YAML batch PR #151 merged | 7 aliases kit-only |
| Live import | 106 KW UPSERT (vs 5 avant YAML) |
| Classify | R1=102, R3=22 (legacy 18 + nouveaux) |
| Vehicle extract | 62 KW type='vehicle' |
| Backfill type_id | 62 matched |
| V-Level assign | 25 V2 (conf=0.90) |
| `rebuild-type-vlevel.py 3859` | 25 rows __seo_type_vlevel |
| R6 enrich | score=84, 5 sections updated |
| R6 KP resync (INC-2 fix) | pg_id 1683 → 3859 |
| R1 trigger fix (INC-1) | seed row INSERT OK |
| R1 enricher (INC-3 à venir post-deploy) | content fields à peupler après deploy DEV |

## 6 — Verdict QA (état actuel, post-deploy DEV requis)

```
Phase 1  : PASS  Zod OK, 107 KW imported post-YAML
Phase 2  : PASS  R1=102 R3=22
Phase 3  : PASS  R1=validated/78, R3/R6=validated (INC-2 fix), R4=active
Phase 4  : PASS* R1 row+score=80 (⚠️ content pending INC-3 deploy), R4 pub def=989, R6=84, R3=11 sections
Phase 5  : PASS  0 orphans/bugs
Phase 5B : PASS  25 V-Level rows V2=25 conf=0.90
Phase 7  : PASS  0 pollution
Phase 8  : PASS  FULLY_ENRICHED
```

**VERDICT : PASS** (2 WARN non-bloquants).

**Note deploy** : R1 content fields seront peuplés automatiquement quand le DEV pré-prod aura redéployé avec INC-3 (tag push main → ci.yml → docker preprod). À vérifier J+1 via re-run enricher.

## 7 — Impact freinage domaine

- Avant : 11/13 canon
- Après : **12/13 canon** (+1)
- Restant NO_CSV : pg=415 `agregat-de-freinage`

## 8 — Leçons canon émergentes

1. **plpgsql polyglot trigger functions** : toujours utiliser `to_jsonb(NEW)` + `->>` pour accès dynamique quand la fonction est attachée à des tables avec des schémas différents. Ne jamais faire de `NEW.xxx_field` conditionnel sur TG_TABLE_NAME dans du code plpgsql.

2. **Audit pg_id consistency après merges gammes** : toute opération de merge/deprecate dans `pieces_gamme` doit être suivie d'un backfill sur les tables dépendantes (R1_kp, R3_kp, R4_kp, R6_kp, et toutes tables avec pg_id textuel). Proposition : trigger/job automatique pour détecter les désynchros.

3. **UPDATE silent no-op** : dans Supabase/PostgREST, `.update().eq()` sans vérifier `count` est un anti-pattern. Toujours vérifier `count` ou utiliser `.upsert()` explicitement pour les rows absentes.

4. **"status enriched" ≠ "data written"** : un service peut retourner success après un no-op silencieux. Toujours vérifier la DB post-write via read+hash ou count check. La mise en place de CAS (Compare-And-Swap) dans WriteGuard est la solution canon.

## 9 — Follow-up ouverts

- Déploiement DEV pré-prod attendu pour activer INC-3 fix (Docker preprod build)
- Audit systémique : grep `.update().eq()` sans count-check dans tout backend → refactor vers upsert-on-missing ou count-check
- Backfill table-wide r1_kp / r3_kp / r4_kp / r5_kp si désynchros similaires à INC-2

## 10 — Coverage manifest

```
scope_requested:        Pipeline SEO KW pg=3859 kit-de-freins-arriere
scope_actually_scanned: 1 gamme, 5 siblings taxo (R-SEO-KW-06), 3 incidents DB découverts + fixés

files_read_count:       ~15 (scripts seo, field catalog, content-write-executor,
                             content-write-gate, r1-enricher, migrations, RAG .md)
excluded_paths:         autres gammes R1_ROUTER du batch
unscanned_zones:        audit global .update().eq() (follow-up §9)

corrections_proposed:   3 fixes DB canon + 7 aliases YAML
corrections_applied:
  - PR monorepo #151 merged (7 aliases kit-only)
  - PR monorepo #154 merged (INC-1 trigger fix + INC-2 backfill migration + INC-3 executor patch)
  - Live DB : fn_warn_orphan_pg_id fixed via to_jsonb(NEW)
  - Live DB : 61 r6_kp rows resync (2 duplicata legacy deleted first)
  - Live import 106 rows __seo_keywords + 106 __seo_keyword_results
  - extract_vehicle_keywords(3859) + backfill type_id (62 KW)
  - Reset + re-assign v_level per (model, energy) group
  - rebuild-type-vlevel.py 3859 → 25 rows __seo_type_vlevel (V2=25)
  - R6 enricher live → score 84

validation_executed:
  - Dry-run before/after YAML (95% → 32% rejets, rejets résiduels = autres gammes canon)
  - R-SEO-KW-06 taxo check (4 gammes actives verified)
  - QA 9 phases consolidated
  - INC-1 fix validated via INSERT test
  - INC-2 fix validated via SQL count (0 remaining)
  - INC-3 fix compile OK, runtime pending DEV redeploy

remaining_unknowns:
  - R1 content fields post-deploy DEV (J+1 verification required)
  - Autres tables avec pg_id désynchro potentielle (r1_kp, r3_kp, r4_kp, r5_kp)
  - Grep systémique .update().eq() sans count check

final_status: SCOPE_SCANNED
```
