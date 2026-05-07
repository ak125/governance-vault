---
id: ADR-049
title: "DB Governance Canon Enforcement — sub-projet ADR-048"
status: accepted
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
4. **Sprint 3 ADR-048 reste cohérent** sur fichiers racine après reformulation C5 (cible : "≥80% du canon hors db-governance" = 15 racine + 5 prose-with-derivation, dont ≥16 enforced/deprecated requis). Le scope db-governance/* devient critère propre à ADR-049.

### Risques spécifiques au DB canon

1. **Drift schéma DB ↔ canon** : un changement Supabase migration peut diverger arbitrairement de `sql-governance-rules.md` ou `domain-map.md` sans signal automatique
2. **Audits stales** : fichiers `phase-2a-rpc-audit-results.md` (mars 2026) prétendent décrire l'état RPC actuel — peuvent être totalement obsolètes
3. **Single-signer SPOF aggravé** : DB canon modifications ont impact production direct (queries, RLS), peer review encore plus critique

## Décision

**Option DB-D — Hybride reclassement-first + migration enforcement priorisée + freshness ajusté + cross-validation Supabase MCP**.

4 sub-axes parallèles sur 2 sprints additionnels (parallèles aux sprints 2-3 d'ADR-048 sur les fichiers racine) :

### Sub-axe 1 — Audit fichier-par-fichier db-governance/* (sprint DB-1)

Étendre [[REG-002-canon-files]] avec une colonne supplémentaire `db_classification` pour les 20 rows db-governance/* :

- `active-rule` : règle SQL/governance active (ex. `sql-governance-rules.md`, `domain-map.md`)
- `active-registry` : registry vivant (ex. `role-migration-registry.md`, `pr4b-mcp-inventory-2026-05-05.md`)
- `historical-snapshot` : audit ponctuel datable, accepte staleness (ex. `phase-2a-rpc-audit-results.md`)
- `closed-plan` : plan de migration achevé, candidat `deprecated` (ex. `change-control-plan.md`, `sql-migration-checklist.md`)

Pas de REG-003 séparé — éviter la fragmentation registry. Extension d'une colonne dans REG-002 suffit.

### Sub-axe 2 — Migration prose → enforcement priorisée (sprint DB-2)

**Priorité DB-P0** (haute criticité applicative — cible enforcement formel) :
- `sql-governance-rules.md` → invariants SQL en CI : script `validate-db-schema-invariants.sql` exécuté via Supabase MCP
- `domain-map.md` → généré automatiquement depuis `information_schema.tables` + commentaires
- `schema-governance-matrix.md` → tests d'intégration sur les invariants matrix

**Priorité DB-P1** (registries actifs) :
- `role-migration-registry.md` → schema YAML/JSON Zod côté backend, validateur CLI
- `pr4b-mcp-inventory-2026-05-05.md` → idem, vérification cross-repo Supabase MCP

**Priorité DB-P2** (audits historiques — reclassement, pas migration enforcement) :
- `phase-2a-rpc-audit-results.md`, `phase-2b-rpc-audit-results.md`, `phase-2b-first-monitoring-review.md`, `perf-findings.md`, `full-structural-audit.md` → status `historical-snapshot` dans REG-002, `freshness_threshold_days: 730+`, accepte explicitement la staleness

**Priorité DB-P3** (plans clos — candidate `deprecated`) :
- `change-control-plan.md`, `sql-migration-checklist.md`, `execution-map.md`, `final-exec-summary.md` → si confirmés clos, `deprecated`. Sinon `historical-snapshot`.

### Sub-axe 3 — Cron freshness étendu (sprint DB-1, ajustement only)

`check-canon-freshness.py` (PR #194) lit déjà REG-002. Ajustement minimal :
- `historical-snapshot` (DB-P2, ~5 fichiers) : threshold 730j (2 ans)
- `closed-plan` (DB-P3, ~4 fichiers) : passage `deprecated` ou `historical-snapshot` selon DB-P3 evaluation
- `active-rule` (DB-P0, 3 fichiers) : threshold serré 60j
- `active-registry` (DB-P1, 2 fichiers) : 90j (déjà OK)

Pas de nouveau script. Une PR vault d'ajustement REG-002.

### Sub-axe 4 — Cross-validation Supabase MCP ↔ canon (sprint DB-2)

Nouveau script `_scripts/check-canon-db-cross-validation.py` :
- Lit les fichiers DB-P0 active-rule
- Pour chaque règle SQL énoncée (RLS active sur table X, FK Y → Z, trigger T...), interroge Supabase MCP (`execute_sql` ou `list_tables`) pour vérifier l'existence réelle
- Flag `error` si règle prose non confirmée par DB réelle (drift critique)
- Flag `warning` si règle DB réelle non documentée dans canon prose (drift inverse)

Branché en weekly-lint comme 11e check, mode `--warn` initial (cohérent stratégie escalade J+30).

### Reformulation C5 d'ADR-048 (alignement post-extraction)

ADR-048 §Critères de Succès C5 doit être amendé : `≥80% coverage canon` → `≥80% coverage canon hors db-governance/*` (= 15 fichiers racine + 5 prose-with-derivation = 20 fichiers cible, dont ≥16 enforced/deprecated requis). Le coverage db-governance/* est tracké via DB-C5, pas via C5 d'ADR-048. Reformulation matérialisée dans une PR vault `chore(adr-048): amend C5 scope post ADR-049 extraction` (low-cost, 1 ligne).

## Options Considérées

### Option DB-A — ADR fils complet avec stack 4-5 PRs sur 2 sprints

**Description** : pattern "9 PRs canon SEO" appliqué aux 20 fichiers. Chaque fichier P0/P1 = 1 PR dédiée.

**Avantages** : traçabilité maximale, pattern qui a marché.

**Inconvénients** : surcharge cognitive (5+ PRs supplémentaires), traite tous les fichiers à égalité même les audits stales qui méritent reclassement.

### Option DB-B — Reclassement `historical-snapshot` first, puis enforcement minimal

**Description** : commencer par marquer ~10 fichiers DB-P2/DB-P3 comme `historical-snapshot` ou `deprecated` (réduit le scope "actif" à ~10 fichiers), puis enforcement P0+P1 seulement.

**Avantages** : effort initial très faible.

**Inconvénients** : les audits stales restent canon (juste reclassés), pas d'invariant cross-validé Supabase. Risque que de futurs audits divergent silencieusement.

### Option DB-C — Cross-validation Supabase MCP dominante

**Description** : axe 4 prend l'essentiel du sprint, vérification automatique DB ↔ canon prose en CI. Migration prose → schemas en parallèle minimaliste.

**Avantages** : adresse la cause profonde directement.

**Inconvénients** : effort initial élevé pour le script. Ne reclasse pas les audits stales.

### Option DB-D — Hybride (RETENUE)

**Description** : combine forces des 3 options ci-dessus. Reclassement-first (sub-axe 1, faible coût) + migration P0/P1 ciblée (sub-axe 2) + freshness ajusté (sub-axe 3) + cross-validation Supabase MCP (sub-axe 4).

**Avantages** :
- Coût initial proportionné (reclassement avant migration lourde)
- Adresse drift DB ↔ canon (sub-axe 4) sans tout migrer
- Réutilise infra existante (REG-002, check-canon-freshness)
- Coverage explicite par catégorie
- Pattern cohérent avec ADR-048 Option D (hybride parent)

**Inconvénients** :
- 4 sub-axes en parallèle = coordination
- Sub-axe 4 = nouvelle infra script

## Conséquences

### Positives attendues

- **Détection automatique** drift DB ↔ canon prose sur les 3 fichiers DB-P0 (sub-axe 4)
- **Reclassement honnête** : ~10 fichiers stales explicitement marqués `historical-snapshot` ou `deprecated`
- **Coverage clair par catégorie** : 3 active-rule enforced + 2 active-registry enforced + ~5 historical-snapshot acceptés stales + ~4 deprecated = 14/20 explicitement gouvernés (70%), reste 6 fichiers à statuer en finalisation
- **Cron freshness adapté** : thresholds par catégorie évite le noise
- **Single-signer SPOF mitigé** : sub-axe 4 cross-valide DB réelle

### Négatives attendues

- **Coût sub-axe 1** (audit + reclassement) : 0.5j
- **Coût sub-axe 2** (migration P0+P1) : 2-3j
- **Coût sub-axe 3** (freshness ajustement) : 0.25j
- **Coût sub-axe 4** (cross-validation Supabase) : 1-2j
- **Total estimé** : 4-6 jours sur 2 sprints
- **Charge récurrente** : weekly-lint passe de 10 à 11 checks (+1)
- **Dépendance Supabase MCP** : sub-axe 4 requiert que le MCP reste disponible

### Neutres

- Aucun impact sur sprint 3 d'ADR-048 (fichiers racine indépendants)
- Aucun impact sur ADRs DB-related existants (ADR-021, ADR-017, ADR-028)
- Compatible trajectoire ADR-039 / ADR-040

## Critères de Succès

Quantifiés et auditables :

- [ ] **DB-C1** (fin sprint DB-1) : extension REG-002 avec colonne `db_classification` pour les 20 rows db-governance/*. 100% classifiés.
- [ ] **DB-C2** (fin sprint DB-2) : ≥3 fichiers DB-P0 active-rule migrés vers enforcement mécanique.
- [ ] **DB-C3** (fin sprint DB-1) : ≥5 fichiers DB-P2 reclassés `historical-snapshot` avec threshold ≥730j. ≥3 fichiers DB-P3 reclassés `deprecated` (si confirmés clos).
- [ ] **DB-C4** (fin sprint DB-1) : thresholds REG-002 ajustés par catégorie.
- [ ] **DB-C5** (fin sprint DB-2) : ≥80% coverage db-governance/* (= ≥16/20 en état explicite enforced ou historical-snapshot ou deprecated). Aucun `prose-only` non-justifié.
- [ ] **DB-C6** (fin sprint DB-2) : `_scripts/check-canon-db-cross-validation.py` LIVE en weekly-lint mode `--warn`, vérifie ≥3 invariants DB-P0 par interrogation Supabase MCP.

## Implémentation

### Sprint DB-1 (S+1 ADR-048 sprint 2 parallèle, 1 sem, ~1j effort)

- [ ] PR vault : `feat(adr-049): REG-002 extension db_classification column + 20 rows classified` (sub-axes 1+3)
- [ ] PR vault : `chore(adr-048): amend C5 scope post ADR-049 extraction` (1 ligne, alignement)

### Sprint DB-2 (S+2 ADR-048 sprint 3 parallèle, 1 sem, ~3-4j effort)

- [ ] PR monorepo : `feat(spec-canon-db): SQL invariants enforcing sql-governance-rules.md` (DB-P0)
- [ ] PR monorepo : `feat(spec-canon-db): domain-map.md auto-generator from information_schema` (DB-P0)
- [ ] PR monorepo : `feat(spec-canon-db): integration tests for schema-governance-matrix.md` (DB-P0)
- [ ] PR vault : `feat(scripts): check-canon-db-cross-validation.py + weekly-lint integration` (sub-axe 4)
- [ ] PR vault : `feat(adr-049): role-migration-registry + pr4b-mcp-inventory Zod schemas` (DB-P1, optionnel selon temps)

## Suivi

- **Owner principal** : Fafa
- **Reviewers potentiels** : à identifier en sprint DB-1 (peer review G3, possiblement avec un agent SQL/Postgres)
- **Trigger sprint DB-1** : dès que sprint 2 d'ADR-048 démarre (chantiers parallèles)
- **Métrique de progression** : reporting weekly via check-canon-freshness existant + extension REG-002
- **Escalation** : si sub-axe 4 > 2j d'effort, déléguer à un ADR-050 fils dédié

## Références

- [[ADR-048-canon-enforcement-coverage]] — décision parente (Option D hybride)
- [[REG-002-canon-files]] — audit factuel, 20 rows db-governance/*
- [[ADR-040-seo-roles-canon-ts-side-only]] — pattern enforcement TS package + 4 layers
- [[ADR-021-database-rls-hardening-zero-trust]] — précédent enforcement DB (RLS per-table)
- [[ADR-028-preprod-supabase-isolation]] — précédent pattern cascade 9 classes
- `_scripts/check-canon-freshness.py` (PR #194) — cron freshness consomme REG-002
- Memory `roadmap-p0-p3-canon-repos-20260501.md` — P3 dep-cruiser planifié, complémentaire

---

*Proposé le: 2026-05-07*
*Finalisé (sections élaborées) le: 2026-05-07*
*Accepté le: 2026-05-07*
*Dernière revue: 2026-05-07*
