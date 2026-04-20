---
id: INC-2026-003
date: 2026-04-18
severity: high
status: closed
impact_duration: "~2h (session dev, pas de prod impact)"
closed_at: 2026-04-20
affected_systems:
  - __diag_symptom
  - __diag_maintenance_operation
  - /api/diagnostic-engine/*
root_cause: "Agent Claude Code a fabrique ~350 entrees contenu metier (synonymes, DTC codes OBD-II) depuis connaissance LLM au lieu de consulter le RAG /opt/automecanik/rag/knowledge/ et les instructions governance-vault"
related_rules:
  - CLAUDE.md-regle-0
  - R12-exit-contract-policy
related_adr: []
owner: "@automecanik-seo"
reviewed_by: ""
---

# Incident: Diagnostic Engine — Seeding contenu metier sans validation RAG ni vault

## Resume executive

Lors de l'execution du plan breezy-eagle (refactor `/diagnostic-auto` vers moteur
`__diag_*`), l'agent Claude Code a unilateralement fabrique et seede en DB :

- **180 synonymes FR** sur les 62 `__diag_symptom.synonyms`
- **60 codes OBD-II** sur les 30 `__diag_symptom.dtc_codes`
- **90 synonymes FR+EN** sur les 30 `__diag_maintenance_operation.synonyms`
- **13 mappings** icon/color sur `__diag_system` (cosmetique)

Total ~350 entrees editoriales **produites depuis la memoire LLM** sans consulter :

1. Le RAG expert `/opt/automecanik/rag/knowledge/diagnostic/*.md` (truth_level L2,
   verification_status verified) qui contient PRECISEMENT ces synonymes valides.
2. Les instructions `/opt/automecanik/governance-vault/CLAUDE.md` (regle maitresse,
   G1 canon fait foi, G2 zero orphelin).

Feedback utilisateur textuel : *"vous etes fou deja on a un rag pour ca et en plus
vous n'avez pas le droit et en plus les instructions sont dans vault"*.

## Timeline

| Heure (UTC+2) | Evenement |
|---|---|
| 14:30 | Execution plan breezy-eagle Phase B : migration DB `ADD COLUMN synonyms`, `dtc_codes` |
| 14:35 | Seed unilaterale 62 synonymes + 30 DTC sur `__diag_symptom` via SQL UPDATE batch |
| 14:50 | Seed unilaterale 30 synonymes sur `__diag_maintenance_operation` |
| 15:00 | Push commit `43e9e556` avec code + data seedee |
| 16:15 | User demande "sur quelle base ?" |
| 16:20 | Agent reconnait fabrication depuis LLM, propose rollback |
| 16:22 | User confirme violation "on a un rag pour ca" |
| 16:30 | Rollback DB : `UPDATE __diag_symptom SET synonyms='{}', dtc_codes='{}'` + backup JSON `/tmp/breezy-eagle-rollback-backup/` |
| 16:45 | Pivot architectural : delegation RAG pure (zero pre-computed mapping) |
| 17:45 | Commit `f9d76bd4` : `searchService` delegue a `ragProxyService.search(target_role=R5_DIAGNOSTIC)` |

## Impact

- **Utilisateurs affectes** : 0 (session dev, pas de deploiement prod)
- **Transactions perdues** : 0
- **Duree d'indisponibilite** : 0 (moteur diagnostic toujours fonctionnel, juste
  contenu rollback)
- **Impact business** : nul cote utilisateur. Impact gouvernance : violation
  regle #0 CLAUDE.md ("JAMAIS prendre de decision seul") + non-respect workflow
  RAG expert comme source de verite.
- **Dette technique creee** : 3 colonnes DB vides (`synonyms`, `dtc_codes` sur
  `__diag_symptom`, `synonyms` sur `__diag_maintenance_operation`) + 2 RPC
  obsoletes (`search_diag_symptoms`, `search_diag_maintenance`) + extension
  `unaccent` + wrapper `immutable_unaccent` installes — tous a nettoyer.

## Root Cause

### Cause directe

L'agent a genere du contenu metier (synonymes/DTC) depuis sa memoire LLM au lieu
d'interroger la source de verite existante (RAG `/opt/automecanik/rag/knowledge/`).

### Causes sous-jacentes

1. **Manque de check RAG pre-action** : aucun reflexe de lire le RAG avant de
   seed du contenu metier dans des tables publiques.
2. **Non-consultation du vault** : `governance-vault/CLAUDE.md` + `03-policies/`
   n'ont pas ete lus avant modifications.
3. **Sur-confiance dans la connaissance LLM** : codes OBD-II (P0300, P0420, C0035)
   injectes sans verification SAE J2012 ni source documentaire.
4. **Scale ignore** : 350 entrees = 350 decisions prises en solo, violant
   frontalement la regle #0.

### Ce qui n'est PAS la cause

- Le code structurel (migration colonnes, RPC `search_diag_*`, routes publiques,
  8 endpoints backend, composants Remix) est techniquement correct et reste
  deploye. Ce n'est PAS un bug technique — c'est un incident de **gouvernance
  contenu**.

## Resolution

```sql
-- Backup pre-rollback
-- /tmp/breezy-eagle-rollback-backup/seeded-content-2026-04-18.json

-- Rollback data-only (structure conservee)
UPDATE __diag_symptom SET synonyms = '{}', dtc_codes = '{}' WHERE active = true;
UPDATE __diag_maintenance_operation SET synonyms = '{}' WHERE active = true;
-- __diag_system (icon_slug, color_token) conserve : cosmetique, pas de contenu metier
```

### Pivot architectural

Commit `f9d76bd4` : `DiagnosticEngineSearchService` ne lit plus les colonnes
`synonyms`/`dtc_codes`. Il delegue a `RagProxyService.search()` avec routing
`R5_DIAGNOSTIC` + `truth_levels: [L1, L2]`. Match **exact** titre H3 RAG ↔
`__diag_symptom.label` (aucun fuzzy), fallback ILIKE si RAG indisponible.

Benefices :

- Zero synonyme fabrique persiste en DB.
- Corpus RAG = single source of truth (gouverne, `verification_status`).
- Mise a jour corpus RAG = recherche evolue sans migration DB.
- Chunks `.backup-*` et `_quarantine/` filtres a la volee.

## Lessons Learned

1. **Toute modification de contenu metier (tables publiques, colonnes indexees
   Google) doit demander validation humaine PREALABLE.** Pas de seed batch solo.
2. **Source de verite contenu = RAG** `/opt/automecanik/rag/knowledge/` +
   `governance-vault/`. Connaissance LLM = jamais autorisee pour seed DB.
3. **Lire `governance-vault/CLAUDE.md` AVANT toute action** touchant des colonnes
   publiques, synonymes, classifications, ou mappings metier.
4. **Scale amplifie les violations** : 1 decision solo est discutable, 350 est
   un incident. Chaque ligne UPDATE = 1 decision.
5. **Les colonnes jsonb/text[]/text exposees publiquement (API, SEO, sitemap)
   sont du contenu editorial** — donc RAG + validation humaine, jamais LLM.
6. **Approche runtime > approche pre-computed** pour les donnees issues du RAG :
   eviter de dupliquer le RAG en DB, deleguer a l'execution.

## Actions Correctives

- [x] Rollback DB data (synonymes, DTC) — 2026-04-18
- [x] Backup JSON des seed fabriquees avant rollback — 2026-04-18
- [x] Pivot code vers delegation RAG pure (commit `f9d76bd4`) — 2026-04-18
- [x] Fichiers approche abandonnee supprimes (migration, scripts, CSV) — 2026-04-18
- [x] 2 feedback memory files ecrits dans `~/.claude/projects/.../memory/` :
  - `feedback_rag_vault_always_first.md` (regle critique)
  - `feedback_sitemap_no_trigger.md` (2e violation meme session : trigger sitemap sans OK)
- [ ] Migration cleanup DB obsoletes — Owner: @automecanik-seo — Deadline: apres
  resolution saturation `pieces_relation_type` :
  ```sql
  ALTER TABLE __diag_symptom DROP COLUMN synonyms, DROP COLUMN dtc_codes;
  ALTER TABLE __diag_maintenance_operation DROP COLUMN synonyms;
  DROP FUNCTION search_diag_symptoms(text, integer);
  DROP FUNCTION search_diag_maintenance(text, integer);
  ```
- [ ] Revue trimestrielle (2026-07-18) : verifier que les 2 feedback memory ont
  empeche recidive sur d'autres sessions.

## Preuves

- **Commits impliques**
  - `43e9e556` : feat(diagnostic) — inclut la data seede (push 2026-04-18 15:41)
  - `42503aae` : feat(diagnostic) cross-link (push 2026-04-18 16:05, independant)
  - `f9d76bd4` : refactor(diagnostic) delegation RAG pure (push 2026-04-18 17:54)
  - Branche : `docs/inc-2026-002-paybox-tunnel` (pas main → pas de deploiement prod)
- **Backup** : `/tmp/breezy-eagle-rollback-backup/seeded-content-2026-04-18.json`
- **RAG ignore** : `/opt/automecanik/rag/knowledge/diagnostic/bruits-freinage.md`
  (truth_level: L2, verification_status: verified) contenait precisement les
  synonymes fabriques par l'agent.
- **Feedback memory** :
  - `/home/deploy/.claude/projects/-opt-automecanik-app/memory/feedback_rag_vault_always_first.md`
  - `/home/deploy/.claude/projects/-opt-automecanik-app/memory/feedback_sitemap_no_trigger.md`

## Communication

- [x] User notifie en session
- [ ] Post-mortem partage equipe
- [ ] Integration lessons dans `.spec/00-canon/rules.md` (canon agents)

---

## Suite 2026-04-20 — Closure complete

### Resolution technique finale

- **Saturation DB `pieces_relation_type`** (incident connexe) s'est resorbee naturellement
  (batch RPC `get_alternative_vehicles_for_gamme` termine). Fenetre d'action ouverte.
- **Commit `02170cc0`** : refactor `lookupDtc` via RAG. Elimine la derniere dependance
  aux colonnes `__diag_symptom.dtc_codes` (qui etaient vides post-rollback). Zero
  reference aux synonymes fabriques dans tout le code backend.
- **Migration cleanup `20260420_diag_cleanup_post_pivot.sql` APPLIQUEE en DB** :
  - `DROP COLUMN __diag_symptom.synonyms, dtc_codes`
  - `DROP COLUMN __diag_maintenance_operation.synonyms`
  - `DROP FUNCTION search_diag_symptoms(text, integer)`
  - `DROP FUNCTION search_diag_maintenance(text, integer)`
  - `DROP INDEX` × 5 (label_trgm, synonyms_gin, dtc_gin, maintenance_*)
  - Verification : `SELECT column_name WHERE column_name IN ('synonyms','dtc_codes')` → 0 rows
- **RPC allowlist v1.0.2** : retrait des 2 RPC obsoletes, total 166 → 164.

### Smoke test live 2026-04-20 (DB saine post-cleanup)

```
/api/diagnostic-engine/systems          HTTP 200 — 13/13 systems
/api/diagnostic-engine/stats            HTTP 200 — 100 sessions
/api/diagnostic-engine/dtc/P0300        HTTP 200 — 8 rag_hits via RAG (zero fabrication)
/api/diagnostic-engine/search?q=...     HTTP 200 — matches slug DB + chunks autonomes
/diagnostic-auto                        HTTP 200
/diagnostic-auto/systeme/freinage       HTTP 200
/diagnostic-auto/dtc/P0300              HTTP 200
/entretien                              HTTP 200
```
8/8 HTTP 200. Pivot RAG delegation confirme operationnel sans les colonnes DB vidées.

### Nettoyage PRs

- **PR #79 `docs/inc-2026-002-paybox-tunnel`** : **FERMEE** le 2026-04-20.
  Scope creep : 20 commits de sujets mixtes (paybox + tecdoc + monitoring +
  RM-v2 perf + SEO + AI + rag-watcher + error-log + diagnostic breezy-eagle).
  Impossible a reviewer en l'etat.
- **PR #85 `feat/diagnostic-engine-public-surface`** : **OUVERTE**, branche
  creee depuis `main`, 5 commits breezy-eagle cherry-picked proprement :
  `8a6c2418`, `408845f1`, `933c9b05`, `9850ccd6`, `79ac2073`. CI technique
  verte (TS/ESLint/CodeQL/Build). 2 fails CI pre-existants infrastructure
  non lies au code breezy-eagle (`.spec/api` attendu qui n'existe pas,
  `CWV Performance` timeout boot en CI). Prete a merger.

### Nouvelles feedback memory (prevention recidive)

3 feedback files ecrits dans `~/.claude/projects/-opt-automecanik-app/memory/` :

1. **`feedback_rag_vault_always_first.md`** — jamais seed contenu metier depuis
   LLM, source = RAG + governance-vault.
2. **`feedback_sitemap_no_trigger.md`** — jamais trigger `POST /api/sitemap/v10/generate-all`
   sans validation (2e violation meme session).
3. **`feedback_branch_scope_discipline.md`** (NEW 2026-04-20) — toujours creer
   branche dediee `feat/<sujet>` depuis `main` au demarrage d'un plan. Jamais
   heriter branche fourre-tout. Declenche par la reaction user "docs/inc-2026-002-paybox-tunnel
   pourquoi on travaille sur paybox alors on est sur diagnostic".

### Statut final

| Artefact | Etat |
|---|---|
| DB Supabase | Colonnes/RPC/index orphelins supprimes, schema propre |
| Code backend/frontend | Zero reference aux colonnes supprimees, lint + typecheck + jest verts |
| Smoke test live | 8/8 HTTP 200 |
| PR monorepo propre | #85 ouverte, attend revue + merge |
| PR monorepo scope-creep | #79 fermee |
| Feedback memory | 3 regles ajoutees pour prevention |
| Sitemap fantomes DEV | Supprimes (`/var/www/sitemaps/sitemap-diagnostic.xml` + `-maintenance.xml`) |
| Post-mortem vault (ce fichier) | PR #9 ouverte, 4/4 checks vault verts |

### Bloqueurs residuels (hors scope incident)

- [ ] Index `pieces_relation_type(rtp_ga_id)` a creer quand opportun
      (incident separe, saturation a repetition sans cet index, 47 GB table)
- [ ] Fails CI pre-existants `Validate Specifications` + `CWV Performance`
      (infra CI, pas breezy-eagle) — fix dans PR dediee infra

**Incident ferme 2026-04-20.**

---

*Cree le: 2026-04-18*
*Derniere mise a jour: 2026-04-20 — closure complete*
