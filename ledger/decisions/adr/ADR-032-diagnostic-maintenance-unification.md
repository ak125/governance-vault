---
id: ADR-032
title: "Diagnostic & Maintenance Unification — kg_* canon for maintenance/safety/DTC, content via wiki/exports per ADR-031"
status: proposed
date: 2026-04-29
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "Q1", "Q3", "AP-10"]
related_incidents: []
related_adr: ["ADR-016", "ADR-022", "ADR-026", "ADR-027", "ADR-031"]
reviewed_by: null
---

# ADR-032: Diagnostic & Maintenance Unification

## Contexte

Au 2026-04-29, le domaine diagnostic/entretien souffre de **deux mondes parallèles non fusionnés** dans la base de données et de **>800 lignes de constants TypeScript hardcodées** côté frontend, en violation directe du principe utilisateur "tout dynamique, pas de bricolage".

### Audit empirique (session 2026-04-29)

**Côté DB** :

| Constat | Évidence |
|---|---|
| Tables `__diag_maintenance_operation` + `__diag_maintenance_symptom_link` n'existent pas en DB | `SELECT to_regclass('public.__diag_maintenance_operation')` → `NULL`. Migration `20260321_diagnostic_engine_10_systems.sql` lignes 119+129 fait `INSERT` sans `CREATE TABLE` correspondant. `ON CONFLICT (id) DO NOTHING` masque l'erreur `relation does not exist`. **Les 105 rows seedées sont fictives** depuis la création de la migration. |
| `__diag_safety_rule` (21 rows) coexiste avec `kg_safety_triggers` (24 rows) + RPC `kg_check_safety_gate` | Le service `backend/src/modules/diagnostic-engine/diagnostic-engine.data-service.ts:236, :375` lit en SQL direct `from('__diag_safety_rule')` au lieu d'appeler la RPC canonique. |
| `__diag_symptom.dtc_codes` n'a jamais existé | Constat user "DROPPED" inexact — la colonne n'a pas été créée. |
| Types TS `__diag_context_questions`, `__diag_safe_phrases`, `__diag_wizard_steps` orphelins dans `database.types.ts` | Aucune `CREATE TABLE` correspondante en migrations. |
| `kg_nodes` contient seulement **83 rows total** dont **13 `MaintenanceInterval`** | Pas de `node_type='maintenance'`. Le canon réel est `MaintenanceInterval`. |
| Mapping véhicule → moteur **inopérant** | `auto_type_motor_code` = 1 row vide (`tmc_type_id="0", tmc_code=""`). `kg_engine_families` = 10 familles techniques (BLUEHDI, K9K, TDI, …). **Overlap = 0**. Aucun chemin `type_id → family_code` praticable. |
| `auto_type.type_engine` ≠ code moteur technique | Contient `Essence`/`Diesel`/`Hybride`/… (carburant), pas `BLUEHDI`/`K9K`. Pas comparable à `kg_engine_families.family_code`. |
| RPC `kg_record_case` créée mais **jamais appelée** | `grep -rn "kg_record_case" backend/src/` → 0 hit. Corpus `kg_cases` vide. |
| 13 `MaintenanceInterval` `kg_*` vs 13 slugs hardcodés frontend | **5 validés** (filtre-air, filtre-habitacle, liquide-frein, distribution, liquide-refroidissement), **4 splits fuel-aware** (huile-moteur ↔ vidange-essence/diesel, bougies ↔ essence/préchauffage, freinage = contrôle uniquement, pas remplacement plaquettes/disques), **4 missing** (filtre-a-huile, batterie, amortisseur, pneu). |

**Côté Backend** :

| Constat | Évidence |
|---|---|
| `DiagnosticIntentEnum` énumère 6 intents en dur | `backend/src/modules/diagnostic-engine/types/diagnostic-contract.schema.ts:16-23`. Pas de `breakdown` (urgence routière). |
| Sites consommateurs hardcodent les intents | `validate-phase0.ts:54,84,106,123` + prompts LLM. Aucun consommateur lit `DiagnosticIntentEnum.options` dynamiquement → ajouter un intent demande grep+patch. |
| Pas de route `/depannage*` côté backend ou frontend | grep exhaustif. |

**Côté Frontend (Remix)** :

| Constat | Volume hardcoded |
|---|---|
| `frontend/app/routes/blog-pieces-auto.calendrier-entretien.tsx` | 212 lignes (`ENTRETIEN_PERIODIQUE` 13 entrées + `CONTROLES_MENSUELS` 6 + `ALERTES_KM` 5). 0 loader Remix. |
| `frontend/app/routes/diagnostic-auto._index.tsx` | 602 lignes (`CLUSTERS`, `SIGNS_DATA`, `FAQ_DATA`, `PERCEPTION_ICONS`, `RISK_CONFIG`). |
| `frontend/app/routes/diagnostic-auto.$slug.tsx` | `SAFETY_GATE_CONFIG`, `RISK_CONFIG`, `URGENCY_CONFIG`, `CTX_*_LABELS` hardcodés. |
| `frontend/app/components/diagnostic-wizard/DiagnosticWizard.tsx` | `STEPS` + `LOADING_STEPS` hardcodés. |

**Côté Wiki/RAG/Skills** :

| Constat | Évidence |
|---|---|
| 3 guides RAG entretien existants | `entretien-batterie.md`, `freinage__purge.md`, `freinage__quand-changer.md`. Pas de structure gamme×opération. |
| Pas de skill DEV diagnostic dédié | `vehicle-ops` couvre lookup+compatibility+V-Level mais **pas diagnostic** ni entretien interventionnel. |
| 5 entity_types wiki figés (ADR-031) | `gamme`, `vehicle`, `constructeur`, `support`, `diagnostic`. Pas d'entity séparée `maintenance` ou `entretien`. |

### Pré-tasks empiriques (résultats)

**Pré-task 1 — Coverage `type_id → engine_family_code`** :

```sql
-- via auto_type_motor_code (chemin présumé)
-- Résultat : 0% — overlap nul entre amc.tmc_code et kef.family_code

-- via auto_type.type_engine direct (chemin alternatif)
-- Résultat : 0% — type_engine = "Essence/Diesel/Hybride", pas BLUEHDI/K9K
```

**Conclusion** : la personnalisation par moteur technique (`engine_family_code`) **est impossible** dans l'état actuel de la DB. Un enrichissement éditorial massif de `auto_type_motor_code` (53 959 véhicules) serait nécessaire et **est hors scope ADR-032**.

**Pré-task 2 — Validation éditoriale 13 slugs vs `kg_nodes` (MaintenanceInterval)** :

| Frontend slug (calendrier-entretien.tsx) | kg_nodes node_alias | Statut |
|---|---|---|
| huile-moteur (vidange) | vidange-essence (15000km/12mo) + vidange-diesel (20000km/24mo) | ⚠️ **fuel-aware split** (intentionnel, pas drift) |
| filtre-a-huile | (absent) | ❌ **missing** |
| filtre-a-air | filtre-air (30000km/24mo) | ✅ |
| filtre-habitacle | filtre-habitacle (15000km/12mo) | ✅ |
| liquide-de-frein | liquide-frein (-/24mo) | ✅ |
| plaquettes-de-frein-avant | controle-freinage (20000km/12mo) | ⚠️ **drift** (contrôle ≠ remplacement) |
| disques-de-frein-avant | controle-freinage | ⚠️ **drift** |
| bougies-d-allumage | bougies-essence (60000km) + bougies-prechauffage (100000km, diesel) | ⚠️ **fuel-aware split** (intentionnel) |
| kit-de-distribution | distribution (120000km/72mo) | ✅ |
| liquide-de-refroidissement | liquide-refroidissement (60000km/48mo) | ✅ |
| batterie | (absent) | ❌ **missing** |
| amortisseur | (absent) | ❌ **missing** |
| pneu | (absent) | ❌ **missing** |

Total : 5 validés, 2 splits fuel-aware (intentionnels), 2 drifts à corriger, 4 missing à seeder.

**Bonus `kg_nodes`** : 3 nodes `MaintenanceInterval` non couverts par le frontend actuel (`recharge-clim`, `vidange-bva`, `vidange-bvm`). À conserver dans le canon `kg_*`.

---

## Principe directeur

> Le diagnostic et l'entretien doivent être **dynamiques de bout en bout** : aucune constante de contenu métier en TypeScript, un seul canon par sous-domaine en DB, contenu UI servi via la chaîne ADR-031 (`automecanik-raw → automecanik-wiki → exports`), pas de coexistence ou de bricolage hybride/transitoire.

---

## Décisions structurelles

### D1 — Canon par sous-domaine

| Sous-domaine | Canon retenu | Conséquence |
|---|---|---|
| Sessions / symptômes / causes / safety triggers interactifs | `__diag_*` (system, symptom, cause, symptom_cause_link, session) | Inchangé. C'est le bon canon. |
| Maintenance / intervalles / wear factors / risque | `kg_nodes` (`node_type='MaintenanceInterval'`) + RPCs `kg_*` existantes | Le seed fictif `20260321_*_10_systems.sql` (INSERTs sur tables inexistantes) est **réécrit** : INSERTs canon dans `kg_nodes`. Pas de DROP TABLE (les tables n'existent pas). |
| Safety rules normatives (gates) | `kg_safety_triggers` + RPC `kg_check_safety_gate` | DROP `__diag_safety_rule` après backfill 21 rows. SQL direct dans `data-service.ts:236, :375` retiré au profit de la RPC. |
| DTC codes consolidation | `kg_nodes.dtc_code` + vue `v_dtc_lookup` consolidant `__seo_observable.dtc_codes[]` avec colonne `source ENUM('kg', 'seo_only', 'merged')` | Pas de table `__diag_dtc`. |
| Cases learning | RPC `kg_record_case` (existante, jamais appelée) → table `kg_cases` | Wire dans `diagnostic-engine.orchestrator.ts` post-`validateSession()`. |
| Vocab UI / wizard / safety phrases / FAQ / CLUSTERS / SIGNS / **Contrôles mensuels** | `automecanik-raw/sources/diagnostic/*` → `automecanik-wiki/proposals/` → `automecanik-wiki/wiki/diagnostic/<slug>.md` (Markdown + frontmatter YAML structuré). **Contrôles mensuels** vivent dans `automecanik-wiki/wiki/support/controles-mensuels.md` (entity_type `support` car conseil client générique, pas diagnostic interactif). Backend lit via **submodule git** `automecanik-wiki/wiki/{diagnostic,support}/` → `backend/content/{diagnostic,support}/`, parsed runtime avec `gray-matter`, cache LRU. | Pas de tables DB pour le contenu UI. Pas d'exports JSON. Pas de table `__content_exports`. Le `.md` est la source unique. |
| **Conseil pédagogique par pièce d'entretien** (advice marketing 1-2 lignes par slug, ex: "Utiliser l'huile recommandée par le constructeur") | `automecanik-wiki/wiki/gamme/<slug>.md` frontmatter `entity_data.maintenance.educational_advice` | **Pas dans `kg_nodes`** (séparation stricte : DB = data structurée, wiki = contenu pédagogique). Joint au runtime via `kg_nodes.node_alias` ↔ filename wiki gamme. |
| **Alertes par palier kilométrique** (10k, 30k, 60k, 100k, 150k actions[]) | **RPC dérivée** `kg_get_maintenance_alerts_by_milestone(p_milestones INT[] DEFAULT ARRAY[10000,30000,60000,100000,150000])` | **Zéro hardcode des paliers** : la RPC groupe les `MaintenanceInterval` selon `km_interval ≤ milestone`. Ajouter/modifier un node dans `kg_nodes` recalcule automatiquement les paliers. Modifiable via paramètre RPC (admin pourra exposer un sélecteur de paliers). |

### D2 — Personnalisation véhicule (fuel-aware seulement)

Le mapping `type_id → engine_family_code` étant inopérant (0% coverage), **la personnalisation par moteur technique est exclue du scope ADR-032**. Le calendrier dynamique opère uniquement par `fuel_type` :

- Frontend transmet `type_id` au backend.
- Backend dérive `fuel_type` via `auto_type.type_fuel` (normalisation : "Essence-Électrique" + "Essence-Electrique" → "Essence-Hybride", etc.).
- RPC consomme `p_fuel_type` pour différencier vidange-essence vs vidange-diesel, bougies-essence vs bougies-prechauffage.
- Pas de `wear_factors` automatiques par véhicule. Profil usage (urbain/agressif/charge) reste **explicite** côté frontend (sélection user) ou défaut neutre.

### D3 — Extension RPC plutôt que wrapper

La RPC existante `kg_get_smart_maintenance_schedule(p_engine_family_code TEXT, p_current_km INT, …)` est **étendue** avec deux paramètres optionnels :

- `p_type_id INT DEFAULT NULL` — sert uniquement à dériver `fuel_type` via `auto_type.type_fuel`.
- `p_fuel_type TEXT DEFAULT NULL` — explicite, override l'auto-détection.

Pas de wrapper distinct `kg_get_smart_maintenance_schedule_by_type_id`. Un seul point d'entrée.

### D4 — Intent breakdown ajout direct (audit empirique invalide le refactor préalable)

L'audit empirique 2026-04-29 a invalidé l'hypothèse initiale d'un bricolage de prompts hardcodés : `grep -rln "diagnostic_symptom.*warning_light" backend/src/` → **0 fichier** énumère plusieurs intents en dur hors `DiagnosticIntentEnum` Zod (le seul site canonique). Les références à un intent literal dans `validate-phase0.ts` sont des **fixtures de test** (cas particulier `diagnostic_symptom`), pas une énumération exhaustive. `admin-keyword-planner.controller.ts:1797` utilise `r('diagnostic', 'symptoms')` comme **lookup RAG**, pas comme `DiagnosticIntent` literal.

Conséquence : ajouter `'breakdown'` à `DiagnosticIntentEnum` = **1 ligne de modification**, aucun refactor préalable nécessaire. Pas de bricolage à corriger préventivement.

Voir mémoire Claude Code `diag-intent-enum-canonical-only.md`.

### D5 — Distribution exports support → backend via submodule git

`backend/content/diagnostic/` est un submodule git pointant vers `automecanik-wiki/wiki/diagnostic/` (sparse-checkout shallow). Le `Dockerfile` exécute `git submodule update --init --recursive --depth 1` au build. L'image embarque les fichiers `.md` au moment du build.

Pas de table `__content_exports`. Pas de CI sync cross-repo. Pas de Storage SDK. Pas de cache à invalider hors LRU mémoire backend.

### D6 — Skill DEV : extension de `vehicle-ops`

Le skill existant `.claude/skills/vehicle-ops/SKILL.md` est étendu avec une section diagnostic (RPCs `kg_*`, canon `__diag_*` interactif, content via FS submodule, anti-patterns). Pas de skill `diagnostic-ops` séparé.

### D7 — Backfill éditorial + dérivations dans Phase 1

Le seed canon dans `kg_nodes` (Phase 1 PR-1) doit ajouter :

- 4 `MaintenanceInterval` missing : `filtre-huile`, `batterie`, `amortisseur`, `pneu`.
- 2 `MaintenanceInterval` séparés du `controle-freinage` existant : `remplacement-plaquettes-frein-avant`, `remplacement-disques-frein-avant`.

Total : 13 `MaintenanceInterval` actuels + 6 ajoutés = **19**. Les 13 slugs frontend hardcoded sont alors couverts (avec splits fuel-aware légitimes).

PR-1 ajoute également :

- Champ `maintenance_priority TEXT CHECK (maintenance_priority IN ('critique','important','normal'))` sur `kg_nodes` (aligné sur les 3 niveaux frontend hardcoded actuels). Backfill des 19 nodes avec valeurs éditorialement validées.
- RPC `kg_get_maintenance_alerts_by_milestone(p_milestones INT[] DEFAULT ARRAY[10000,30000,60000,100000,150000], p_fuel_type TEXT DEFAULT NULL)` qui retourne `(milestone_km, actions JSONB)` où `actions` est la liste des `MaintenanceInterval` dont `km_interval ≤ milestone_km`, classés par `maintenance_priority`. Conforme D2 (fuel-aware filtering optionnel).

### D9 — Endpoint backend agrégé pour calendrier-entretien

Pour éviter que le frontend `calendrier-entretien.tsx` fasse 3 fetches séparés (entretien périodique + contrôles mensuels + alertes paliers), le backend expose **un endpoint unique** :

```
GET /api/diagnostic-engine/calendar?type_id=X&current_km=Y
```

Le `MaintenanceCalculatorService.getCalendar(typeId, currentKm)` (Phase 2 PR-3) :

1. Appelle `kg_get_smart_maintenance_schedule(p_type_id, p_fuel_type)` pour entretien périodique (intervalles + risk levels).
2. Appelle `kg_get_maintenance_alerts_by_milestone(p_fuel_type)` pour alertes paliers.
3. Lit `backend/content/support/controles-mensuels.md` via `DiagnosticContentService` (PR-6) pour les 6 contrôles mensuels.
4. Joint chaque `MaintenanceInterval` retourné par `kg_*` avec son `wiki/gamme/<node_alias>.md` frontmatter pour récupérer `entity_data.maintenance.educational_advice` et `entity_data.maintenance.related_pages`.
5. Retourne JSON consolidé conforme contrat Zod (à définir dans `types/calendar-output.schema.ts`).

Le frontend (Phase 5 PR-7) fait **un seul fetch**. Pas de logique de jointure côté loader Remix.

### D8 — Fallback strategy (coverage 0%)

Tant que `auto_type_motor_code` n'est pas alimenté éditorialement (hors scope ADR-032), **aucun véhicule n'est personnalisé par moteur technique**. Le frontend affiche systématiquement le calendrier fuel-aware. Ce n'est **pas** une régression : la page actuelle est statique pour tous, donc tout client gagne au minimum la fuel-awareness automatique.

---

## Décisions activement rejetées

| Proposition rejetée | Raison |
|---|---|
| Table `__diag_dtc` dédiée | Vue `v_dtc_lookup` + RPC `kg_get_dtc_lookup` suffisent. Évite duplication source canon `kg_nodes.dtc_code`. |
| Tables `__diag_context_questions`, `__diag_safe_phrases`, `__diag_wizard_steps` | Contenu UI = wiki + exports markdown, pas DB. Conforme ADR-031. |
| Table `__content_exports` (cache DB des fichiers wiki) | Duplication DB↔FS. Submodule git suffit, build-time injection. |
| Wrapper `kg_get_smart_maintenance_schedule_by_type_id` | Extension de la RPC existante (D3). Un seul point d'entrée. |
| RPC `get_vehicle_diagnostic_context` | API véhicule R8 (ADR-016) déjà disponible côté frontend. Pas de RPC nouvelle. |
| Skill `.claude/skills/diagnostic-ops/` séparé | Extension `vehicle-ops` (D6). Un seul skill maintenu. |
| Double-passage `__rag_proposals` pour entretien | Hors scope ADR-022 (R8 véhicule uniquement). Chaîne ADR-031 directe (raw → wiki → exports/rag → sync-from-wiki) suffit pour entretien. |
| Coexistence `__diag_maintenance_*` ↔ `kg_*` | Réécriture du seed dans `kg_*` direct. Pas de migration des "105 rows" (qui n'existent pas en DB). |
| Matérialisation des ghost tables avant DROP | Inutile : les tables n'existent pas, le seed plante silencieusement. Pas de bricolage rétroactif. |
| Enrichissement massif `auto_type_motor_code` (53 959 véhicules) | Hors scope. Si demande future, ouvrir RFC séparée. |
| Feature flag `MAINTENANCE_DYNAMIC_ENABLED` | Pas de bricolage transitoire (règle utilisateur `feedback_no_hybrid_workarounds`). Big-bang quand la chaîne est prête. |
| Audit gate drift-check à seuil arbitraire (10%) | Validation éditoriale `kg_*` faite en pré-task ADR-032 ; corrections dans Phase 1 PR-1. À ce stade, `kg_*` est canon, pas de comparaison vs hardcoded. |
| Tests pgTAP pour migrations DB | Convention vérifiée du projet : Jest backend (`backend/tests/unit/*.test.ts`), Vitest frontend (`frontend/tests/unit/*.test.ts*`). Pas de pgTAP. |
| Exports JSON | ADR-031 figé sur Markdown avec frontmatter YAML structuré. Pas de format alternatif. |

---

## Implications par phase

### Phase 1 — DB consolidation (1 PR monorepo)

**PR-1** : nouvelle migration qui :

1. INSERT direct dans `kg_nodes` (`node_type='MaintenanceInterval'`) pour les 6 nouveaux slugs (D7).
2. Ajoute colonne `maintenance_priority` (D7) + backfill des 19 nodes.
3. Étend `kg_get_smart_maintenance_schedule` avec `p_type_id` + `p_fuel_type` (D3, D2).
4. Crée RPC dérivée `kg_get_maintenance_alerts_by_milestone(p_milestones INT[], p_fuel_type TEXT)` (D7).
5. Crée vue `v_dtc_lookup` + RPC `kg_get_dtc_lookup`.
6. Backfill 21 rows `__diag_safety_rule` → `kg_safety_triggers` + DROP `__diag_safety_rule` (validation gate transactionnelle).
7. Cleanup `database.types.ts` : suppression types orphelins.
8. Tests Jest dans `backend/tests/unit/diagnostic-engine.kg-extensions.test.ts` (incluant test RPC alerts-by-milestone sur 5 paliers).

### Phase 2 — Backend unification (2 PRs, simplifiée post-audit empirique)

- PR-2 (`MaintenanceCalculatorService` avec méthode `getCalendar(typeId, currentKm)` agrégée D9 + endpoint `/api/diagnostic-engine/calendar` + safety RPC rewire).
- PR-3 (wire `kg_record_case` + ajout direct `breakdown` intent au Zod enum + endpoint `/api/diagnostic-engine/breakdown`).

### Phase 3 — Skill DEV étendu (1 PR)

PR-5 : extension `vehicle-ops` SKILL.md (D6).

### Phase 4 — Contenu wiki + backend FS service (3 release groups + 1 PR)

- RG-1 : vocab diagnostic + support (5 fichiers `.md` dans `wiki/diagnostic/` + 1 fichier `wiki/support/controles-mensuels.md` D1).
- RG-2 : gammes entretien batch 1 (5 gammes, raw+wiki+rag) — frontmatter `entity_data.maintenance.educational_advice` + `related_pages` obligatoires (D1).
- RG-3 : gammes entretien batch 2 (5 gammes) — même schéma frontmatter.
- PR-6 : `DiagnosticContentService` via submodule git (D5).

### Phase 5 — Frontend dynamique (5 PRs)

PR-7 à PR-11 : suppression des 800+ lignes de constants TypeScript, remplacement par loaders Remix.

---

## Critères de succès

1. `SELECT to_regclass('public.__diag_safety_rule')` → `NULL` (droppée en Phase 1).
2. `SELECT COUNT(*) FROM kg_nodes WHERE node_type='MaintenanceInterval'` → ≥ **19** (13 actuels + 6 ajoutés).
2bis. `SELECT COUNT(*) FROM kg_nodes WHERE node_type='MaintenanceInterval' AND maintenance_priority IS NOT NULL` → **19** (backfill D7 complet).
2ter. `SELECT * FROM kg_get_maintenance_alerts_by_milestone(ARRAY[10000,30000,60000,100000,150000])` → 5 rows non vides (RPC dérivée fonctionnelle, D7).
3. `SELECT COUNT(*) FROM kg_safety_triggers` → ≥ **45** (24 + 21 backfillés).
4. `SELECT COUNT(*) FROM kg_cases` → ≥ 1 après une session validée (corpus alimenté par PR-4).
5. `grep -rE "^const [A-Z_]+ = (\{|\[)" frontend/app/routes/diagnostic-auto*.tsx frontend/app/routes/blog-pieces-auto.calendrier-entretien.tsx frontend/app/components/diagnostic-wizard/DiagnosticWizard.tsx` → **0 résultat de contenu métier** (UI tokens type `URGENCY_COLORS` map limitée ≤10 lignes acceptés).
6. `grep -rnE "from\(['\\\"\`]__diag_safety_rule|__diag_maintenance_operation|__diag_maintenance_symptom_link|__diag_context_questions|__diag_safe_phrases|__diag_wizard_steps" backend/src/` → **0 résultat**.
7. `grep -rn "kg_record_case" backend/src/modules/diagnostic-engine/` → ≥ 1 (orchestrator).
8. `cat .gitmodules | grep automecanik-wiki` → entrée présente.
9. `ls automecanik-wiki/wiki/diagnostic/*.md | wc -l` → ≥ 5.
9bis. `ls automecanik-wiki/wiki/support/controles-mensuels.md` → présent (D1).
9ter. Pour 5 gammes entretien batch 1, `yq '.entity_data.maintenance.educational_advice' wiki/gamme/<slug>.md` → non vide (D1 schéma frontmatter).
10. `cat .claude/skills/vehicle-ops/SKILL.md | grep -i "diagnostic\|kg_get_smart\|breakdown"` → ≥ 3 références.

---

## Suivi

- **Plan d'exécution détaillé** : `/home/deploy/.claude/plans/ameliorer-corriger-tout-et-stateless-kahan.md` (session 2026-04-29).
- **Mémoires Claude Code** : `diag-maintenance-canon-decisions.md`, `seed-20260321-silent-fail.md`.
- **Audit ghost tables seed** : pattern réutilisable (`INSERT … ON CONFLICT DO NOTHING` non précédé de `CREATE TABLE` correspondant).
- **Si futur enrichissement `auto_type_motor_code`** : ouvrir RFC séparée, ne pas amender ADR-032.
