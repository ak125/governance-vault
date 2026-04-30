---
type: knowledge
status: active
date: 2026-04-29
related_adr: ["ADR-032", "ADR-031", "ADR-017", "ADR-016"]
related_rules: ["G1", "G2", "G3", "Q1", "Q3"]
audience: ["@fafa", "claude-code", "cowork", "future-sessions"]
---

# Découvertes empiriques session ADR-032 (2026-04-29)

> Knowledge canonisée des leçons de la session ADR-032 Diagnostic & Maintenance Unification (Phases 0-5 livrées en une session, 11 PRs monorepo + 1 PR vault + 2 PRs wiki/raw mergées). 5 découvertes à conserver pour les futures sessions et pour l'équipe.

## Contexte

ADR-032 a été décidée puis implémentée intégralement sur une journée. La session a produit 5 découvertes empiriques structurelles qui dépassent le scope d'une seule ADR — elles documentent des **pièges récurrents** et des **patterns de gouvernance** utiles à tout futur travail sur le domaine diagnostic/maintenance, sur la chaîne ADR-031 wiki, ou sur les RPCs Supabase.

---

## 1. Pattern « 3 faux problèmes successifs » corrigés in-flight

ADR-032 V1 proposait 3 fusions structurelles qui se sont révélées invalides à l'audit empirique des consommateurs :

| Faux problème | Hypothèse V1 | Empirie | Fix |
|---|---|---|---|
| **PR-2 prompts intent dynamic** | "Les 6 intents `DiagnosticIntentEnum` sont hardcoded dans des prompts LLM, refactor préalable obligatoire" | `grep -rln "diagnostic_symptom.*warning_light"` retourne 0 fichier hors `diagnostic-contract.schema.ts` (Zod canon unique). `validate-phase0.ts:54,84,106,123` = fixtures de test cas particulier `diagnostic_symptom`, pas énumération. | PR supprimée. Ajouter `breakdown` = 1 ligne Zod, sans grep+patch. |
| **PR-2bis safety RPC rewire** | "`__diag_safety_rule` redondant avec `kg_safety_triggers` + `kg_check_safety_gate`, à fusionner" | `__diag_safety_rule` (21 rules) consommé par `risk-safety.engine.ts` avec `RULE_CAUSE_MAP` (8 mappings cause-by-cause). `kg_check_safety_gate(p_observable_ids uuid[])` retourne 1 row aggregate. **Sémantiques distinctes** : interactif cause-by-cause vs KG observable check. | PR supprimée. Conserver les 2 canons complémentaires. |
| **PR-3 wire `kg_record_case`** | "RPC créée jamais appelée → wire dans `diagnostic-engine.orchestrator.ts` post-`validateSession()`" | `__diag_*` (slugs `freinage`/`battery_drains_overnight`) et `kg_*` (UUIDs `turbo-hs`/`fumee-noire`) = **univers disjoints**, aucun mapping. Corpus diag déjà persisté dans `__diag_session.result jsonb` (`saveSession()` orchestrator ligne 144). | PR supprimée. `kg_record_case` reste pour service KG-driven futur (turbo/EGR), pas diag interactif. |

**Pattern récurrent** : ADR proposée sur projection abstraite (« deux choses se ressemblent → fusionner »). L'audit empirique des consommateurs (engines, services, schémas) révèle que la similitude est apparente, pas réelle.

**Règle émergente** :

> Avant de proposer toute fusion / DROP / refactor préalable dans une ADR :
> 1. **Lire les consommateurs** (`grep -l <table_name> backend/src/`) — pas seulement le schéma DB.
> 2. **Comparer les univers d'identifiants** (slugs/UUIDs/IDs cross-table) — différents univers = pas redondants même si même domaine métier.
> 3. **Vérifier que l'« unused » l'est vraiment** — une RPC jamais appelée par un consommateur peut être prévue pour un consommateur futur (ex `kg_record_case` pour service KG-driven turbo/EGR).

Cette règle a évité 3 régressions structurelles ADR-032 V1 → V5 (5 amendments). Voir [diag-intent-enum-canonical-only.md](https://github.com/ak125/governance-vault/) (mémoire Claude Code archivée).

---

## 2. Pattern « seed silent fail » via `ON CONFLICT DO NOTHING`

**Symptôme** : migration SQL `INSERT INTO __diag_maintenance_operation (...) ON CONFLICT (id) DO NOTHING` qui prétend insérer 30 rows. La table n'existe pas. L'INSERT échoue avec `relation does not exist`. **`ON CONFLICT DO NOTHING` masque l'erreur** — la migration retourne success, le hook CI pass, mais 0 row insérée. Détection retardée de plusieurs semaines.

**Investigation 2026-04-29** (ADR-032 PR-1 préparation) :

```bash
# 1. Repérer les INSERTs sans CREATE TABLE en amont
grep -rn "INSERT INTO __diag_maintenance" backend/supabase/migrations/
# → migration 20260321_diagnostic_engine_10_systems.sql:119, :129
grep -rn "CREATE TABLE.*__diag_maintenance" backend/supabase/migrations/
# → 0 résultat

# 2. Confirmer table inexistante en prod
# psql/MCP : SELECT to_regclass('public.__diag_maintenance_operation') → NULL
```

**Conséquences** :
- 105 rows seedées **fictives** (30 + 75 sur 2 ghost tables) depuis création migration `20260321`.
- Aucun consommateur frontend (vérifié : `grep -rn "__diag_maintenance_operation" frontend/` → 0).
- ADR-032 V1 prévoyait `CREATE TABLE IF NOT EXISTS` + backfill + DROP. **Bricolage évité** : on a réécrit le seed directement dans `kg_*` en PR-1 (table existante, données canon).

**Règle émergente** :

> Tout `INSERT ... ON CONFLICT DO NOTHING` dans une migration doit être précédé d'un `CREATE TABLE IF NOT EXISTS` correspondant **dans le même fichier** ou un fichier antérieur grep-able. Sinon = pattern de seed silent fail à corriger structurellement (réécrire vers la bonne table, pas matérialiser la ghost).

Pattern réutilisable pour audits DB futurs (chercher d'autres ghosts éventuelles dans le codebase).

---

## 3. Schema frontmatter wiki strict — gotchas auto-promote ADR-031

Lors de la promotion auto `proposals/` → `wiki/<entity_type>/` en RG-1 (Phase 4 ADR-032), 6 fichiers wiki ont été refusés par CI vault (`pre-commit validate-frontmatter`) sur 4 erreurs de schema :

| Erreur | V1 (refusée) | V2 (acceptée) | Source schema |
|---|---|---|---|
| `kind` pour `source_refs[]` | `snapshot` (inventé) | `raw` + `path: sources/<entity>/<slug>.md` | `_meta/schema/frontmatter.schema.json` enum `raw\|external_url\|manual\|recycled` |
| `review_status` | `published` (inventé) | `approved` | enum `draft\|proposed\|in_review\|approved\|deprecated` |
| `reviewed_at` / `promoted_at` | `'2026-04-29'` (date) | `'2026-04-29T17:00:00Z'` (ISO date-time) | format strict `date-time` |
| `target_classes[]` | `['schema_org:FAQPage']` | `[]` (ou `KB_*` Weaviate) | enum `KB_Knowledge\|KB_Catalog\|KB_Diagnostic\|KB_Media\|KB_RouterMemory` |
| `origin_lines/origin_repo/origin_path` | propriétés ad-hoc | retiré (dans body) | `unevaluatedProperties: false` sur `source_refs[]` |

Plus 1 erreur `mdformat` (auto-fix : reformate les blocs YAML inline).

**Règle émergente** :

> Avant de générer du frontmatter wiki en bulk (auto-promote, batch curate), lire `_meta/schema/frontmatter.schema.json` pour valider :
> 1. Les enums (`kind`, `review_status`, `target_classes`).
> 2. Les `format: date-time` (jamais `format: date`).
> 3. Les `unevaluatedProperties: false` (refusent les propriétés non-déclarées dans le `oneOf` matching).

Test rapide avant push : `cd automecanik-wiki && pre-commit run validate-frontmatter --files wiki/<entity>/*.md`.

---

## 4. PostgREST normalisation des queries dans `pg_stat_statements`

**Découverte 2026-04-30** (ADR-017 RPC #2 préparation) :

`pg_stat_statements` enregistre les queries normalisées (`$1`, `$2`...). PostgREST emballe **tous les RPC calls** dans le même template :

```sql
WITH pgrst_source AS (SELECT "pgrst_call".* FROM (SELECT $1 AS json_data) pgrst_payload, LATERAL (SELECT * FROM pgrst_call(...)) ...
```

Le **nom de la RPC** (`get_alternative_vehicles_for_gamme`, `kg_get_smart_maintenance_schedule`, etc.) est **dans le payload `$1`**, **pas dans `query_short`**. Conséquence : impossible de filtrer par RPC name via `WHERE query LIKE '%rpc_name%'` sur `pg_stat_statements`.

**Conséquence ADR-017** : la gate « valider RPC #1 -96% à J+1 via `pg_stat_statements` AVANT de toucher RPC #2 » mentionnée dans la mémoire `adr-017-rpc-cleanup.md` est **non vérifiable depuis Supabase MCP**. Toutes les calls PostgREST RPC partagent le même `query_short` template.

**Alternative** : utiliser **Supabase Studio → Function Performance** (UI dashboard) qui parse les payloads et regroupe par RPC name. Ou activer `pg_stat_statements.track = 'all'` + augmenter `pg_stat_statements.track_planner` (stats par template explicit, non normalisé).

**Règle émergente** :

> Toute gate « valider perf RPC X via `pg_stat_statements` » doit passer par Supabase Studio Function Performance, pas par MCP `execute_sql`. Documenter dans les mémoires d'ops : MCP est aveugle aux noms de RPC PostgREST.

Impact : ADR-017 RPC #2 reste **bloqué sur validation J+1** que seul le user peut faire via dashboard. À noter dans toute future ADR avec gate metric pg_stat_statements.

---

## 5. Pattern « extension over creation » validé empiriquement

ADR-032 a appliqué « extension over creation » à 6 décisions où la V1 proposait de créer du nouveau et où l'audit a montré que l'extension de l'existant suffisait :

| V1 (création) | V5 (extension) | Économie |
|---|---|---|
| Wrapper RPC `kg_get_smart_maintenance_schedule_by_type_id` | Étendre RPC existante avec `p_type_id INT DEFAULT NULL` | -1 RPC, -1 doc, -1 test |
| RPC `get_vehicle_diagnostic_context` | Réutiliser API véhicule R8 (ADR-016) | -1 RPC, -1 endpoint |
| Skill `.claude/skills/diagnostic-ops/` | Étendre `vehicle-ops` SKILL.md (frontmatter v1.0 → v1.1) | -1 skill à maintenir |
| Table `__diag_dtc` | Vue `v_dtc_lookup` consolidée + RPC `kg_get_dtc_lookup` | -1 table |
| Table `__content_exports` (cache DB du wiki) | Submodule git `automecanik-wiki/wiki/<entity_type>/` + parse runtime gray-matter | -1 table, -1 CI sync workflow |
| Tables `__diag_context_questions / __diag_safe_phrases / __diag_wizard_steps` (3) | Wiki content `wiki/diagnostic/{wizard-steps,safety-config,vocab-clusters,signs,faq}.md` + endpoints lus via FS submodule | -3 tables, conforme ADR-031 |

**Règle émergente** (déjà dans `feedback_no_hybrid_workarounds.md`, renforcée ici) :

> Avant toute proposition « créer X » dans une ADR, parcourir explicitement les options « étendre Y existant » :
> 1. RPCs : ajouter param avec `DEFAULT NULL` (rétrocompat) plutôt que créer un wrapper.
> 2. Skills DEV : étendre frontmatter version + section nouvelle plutôt que créer un skill séparé.
> 3. Contenu UI : passer par wiki + exports markdown (ADR-031) plutôt que créer une table DB de cache.
> 4. Tables : vue + RPC suffisent souvent (DTC, lookup, jointure dérivée).

ADR-032 §"Decisions actively rejected" liste les 9 propositions rejetées avec leur justification — gabarit pour ADR futures.

---

## Suivi & follow-ups

- **Routine remote J+8 ADR-016 acceptance check** schedulée : `trig_01E78rqRjBZm9YN3fKHgMJhT`, fires 2026-05-03 07:00 UTC. Vérifie `__vehicle_page_cache` + 3 routes R8 + log.md regression watch.
- **ADR-017 RPC #2** bloqué sur validation J+1 (point 4 ci-dessus). User doit confirmer via Supabase Studio avant nouvelle session.
- **Phase 4 RG-2/RG-3** (10 gammes wiki entretien `wiki/gamme/<slug>.md` avec frontmatter `entity_data.maintenance.educational_advice` + `related_pages`) reste à faire. Débloquera la jointure D9 dans `MaintenanceCalculatorService.getCalendar()` pour afficher les conseils par pièce.

## Références session

- ADR-032 [ak125/governance-vault#107](https://github.com/ak125/governance-vault/pull/107) commit `3fd78208`
- 11 PRs monorepo : #207 #210 #211 #212 #213 #214 #215 #216 #217 #218 #219 #220
- 2 PRs wiki/raw : ak125/automecanik-raw#5 (`57cbbada`), ak125/automecanik-wiki#7 (`02cb4326`)
- Plan d'exécution session : `/home/deploy/.claude/plans/ameliorer-corriger-tout-et-stateless-kahan.md` (local DEV VPS)
