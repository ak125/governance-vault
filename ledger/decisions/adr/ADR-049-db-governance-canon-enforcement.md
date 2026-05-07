---
id: ADR-049
title: "DB Governance Canon Enforcement — sub-projet ADR-048"
status: proposed
date: 2026-05-07
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G1]
related_incidents: []
reviewed_by: ""
---

# ADR-049: DB Governance Canon Enforcement (sub-projet ADR-048)

## Contexte

Suite au sprint 1 d'[[ADR-048-canon-enforcement-coverage|ADR-048]] (axe 1 audit + axe 3 freshness check, livrés en PRs vault #193 et #194), l'évaluation **fin de sprint 1** du scope `db-governance/*` (cf. [[REG-002-canon-files]]) confirme la nécessité d'un ADR fils dédié.

### Données factuelles

20 fichiers dans `.spec/00-canon/db-governance/` :

| Type fichier | Nb | Récemment modifiés (mai 2026) |
|---|---|---|
| Maps (domain, role-implementation, role-migration, legacy-canon, schema-governance) | 5 | 4 |
| Rules SQL (sql-governance-rules, sql-migration-checklist, change-control-plan) | 3 | 0 |
| Audit results (phase-2a/2b RPC audits, perf-findings, full-structural-audit) | 5 | 0 |
| Inventaires (pr4b-mcp-inventory, role-migration-registry) | 2 | 2 |
| Misc (execution-map, final-exec-summary, phase-2b-first-monitoring-review) | 5 | 0 |

État REG-002 : **0 enforced, 4 prose-with-derivation (récemment modifiés), 16 prose-only**. Cite ADR-040 (3 fichiers) — pas d'enforcement mécanique formel.

### Pourquoi un ADR fils plutôt que l'inclure dans ADR-048 sprint 3

1. **Densité élevée** : 20 fichiers = 57% du canon total (35 fichiers). Trop pour absorber dans le sprint 3 d'ADR-048 déjà chargé (P2 schemas + check-canon-cross-repo).
2. **Domaine spécifique** : DB governance ≠ canon documentaire/applicatif générique. Enforcement requiert expertise SQL/Postgres dédiée (validation queries, schema invariants, RLS policies, RPC contracts).
3. **Pattern précédent** : ADR-028 cascade 9 classes a fonctionné en plan-stack séparé (memory `adr-028-cascade-handoff-20260504`). Réutilisable.
4. **Sprint 3 ADR-048 reste cohérent** : C2 (P0+P1 5 fichiers) + C5 (≥80% coverage) sans `db-governance/*` reste atteignable sur les 15 fichiers racine + 5 prose-with-derivation = 20 fichiers cible (vs 35 total). 80% de 35 = 28, en excluant db-governance, on a 15 racine — incompatibilité numérique. **À reformuler** : C5 d'ADR-048 cible désormais "≥80% du canon hors db-governance" (15 fichiers racine + 5 prose-with-derivation = 20 fichiers, dont ≥16 enforced/deprecated requis). Le scope db-governance/* (20 fichiers) devient critère de succès propre à ADR-049.

### Risques spécifiques au DB canon

1. **Drift schéma DB ↔ canon** : un changement Supabase migration peut diverger arbitrairement de `sql-governance-rules.md` ou `domain-map.md` sans signal automatique
2. **Audits stales** : fichiers `phase-2a-rpc-audit-results.md` (mars 2026) prétendent décrire l'état RPC actuel — peuvent être totalement obsolètes
3. **Single-signer SPOF aggravé** : DB canon modifications ont impact production direct (queries, RLS), peer review encore plus critique

## Décision (TBD)

À élaborer dans une PR de finalisation. Direction proposée :

### Sub-axe 1 — Audit fichier-par-fichier db-governance/*

Étendre [[REG-002-canon-files]] avec un sous-registry détaillé pour les 20 fichiers, ou créer REG-003 dédié si la volumétrie le justifie.

### Sub-axe 2 — Migration prose → enforcement priorisée

Pré-classification proposée (à valider en finalisation) :

- **DB-P0** (forte criticité applicative) : `sql-governance-rules.md`, `domain-map.md`, `schema-governance-matrix.md` → SQL invariants en CI (script `validate-db-schema-invariants.sql` ou Postgres unit tests)
- **DB-P1** (registry actifs) : `role-migration-registry.md`, `pr4b-mcp-inventory-2026-05-05.md` → schema YAML/JSON validable
- **DB-P2** (audits ponctuels) : phase-2a/2b audits, perf-findings → considérer status `historical-snapshot` (acceptent la staleness, freshness_threshold infini ou archived)
- **DB-P3** (migration plans clos) : change-control-plan, sql-migration-checklist → considérer `deprecated` si plus actifs

### Sub-axe 3 — Cron freshness étendu

`check-canon-freshness.py` (PR #194) lit déjà REG-002 — les 20 fichiers db-governance/* y sont. Pas de nouveau script nécessaire, juste ajustement des `freshness_threshold_days` per-file après audit.

### Sub-axe 4 — Cross-validation Supabase ↔ canon

Nouveau check potentiel : pour les SQL governance rules, valider via MCP Supabase que les contraintes décrites en prose sont effectivement appliquées en DB (RLS active, FKs, triggers).

## Options Considérées (TBD)

À élaborer en finalisation :
- **DB-A** : ADR fils complet avec stack 4-5 PRs sur 2 sprints
- **DB-B** : refactor `historical-snapshot` first (déclasser P2 audits stales) puis enforcement minimal sur P0/P1
- **DB-C** : intégration directe via Supabase MCP cross-validation (axe 4 dominant)

## Conséquences (TBD)

À élaborer en finalisation. Estimation effort initial :
- Sub-axe 1 audit : 0.5j
- Sub-axe 2 migration P0+P1 : 2-3j (SQL invariants + schémas registries)
- Sub-axe 3 freshness ajust : 0.25j
- Sub-axe 4 cross-validation : 1-2j (selon profondeur)
- **Total estimé** : 4-6j sur 2 sprints

## Critères de Succès (TBD)

À élaborer. Cibles initiales :
- [ ] **DB-C1** : sous-registry db-governance/* complet (20/20 fichiers classifiés)
- [ ] **DB-C2** : ≥3 fichiers DB-P0 migrés vers enforcement mécanique (SQL invariants)
- [ ] **DB-C3** : audits P2 stales reclassés `historical-snapshot` ou archivés
- [ ] **DB-C4** : cron freshness ajusté avec thresholds per-file appropriés
- [ ] **DB-C5** : ≥80% coverage db-governance/* (enforced + historical-snapshot + deprecated)

## Implémentation

À planifier en finalisation. Sprint 1 ADR-049 = audit + reclassement stales. Sprint 2 = migration enforcement P0/P1.

**Trigger** : cette ADR est `proposed` au 2026-05-07. Pour passer `accepted` :
1. Review humaine par Fafa (decision_makers signataire)
2. Validation des critères DB-C1 à DB-C5
3. Validation phasing (2 sprints additionnels en parallèle d'ADR-048 sprints 2-3)
4. Merge PR avec status flip `proposed → accepted`

## Suivi

- **Owner principal** : Fafa
- **Deadline finalisation décision** : 2026-05-21 (T+14j depuis création draft, aligné deadline ADR-048 originale qui a été honorée 14j d'avance via PR #191)
- **Métrique de progression** : reporting weekly via `99-meta/canon-coverage-snapshot.json` (à produire par check-canon-freshness étendu)
- **Ne bloque pas** : sprints 2-3 d'ADR-048 sur les fichiers racine peuvent procéder en parallèle

## Références

- [[ADR-048-canon-enforcement-coverage]] — décision parente, dichotomie vault SoT / canon architectural
- [[REG-002-canon-files]] — audit factuel, 20 rows db-governance/*
- [[ADR-040-seo-roles-canon-ts-side-only]] — pattern enforcement TS package + 4 layers (à étendre éventuellement DB-side)
- [[ADR-028-preprod-supabase-isolation]] — précédent pattern cascade 9 classes
- `_scripts/check-canon-freshness.py` (PR #194) — cron freshness consomme REG-002

---

*Proposé le: 2026-05-07*
*Statut: proposed (cadre, sections détaillées en finalisation)*
*Dernière revue: 2026-05-07*
