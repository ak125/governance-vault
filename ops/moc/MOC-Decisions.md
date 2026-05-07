---
type: moc
status: canon
updated: 2026-05-07
---

# MOC: Decisions

Index des **Architecture Decision Records** (ADR) du projet AutoMecanik.

> **Source de verite (verrouille en PR-2 / glossaire canon)** : les **statuts ADR sont canoniques dans le frontmatter de chaque fichier ADR** (`ledger/decisions/adr/ADR-NNN-*.md`). MOC-Decisions est l'**index officiel derive**, pas la SoT. En cas de divergence, le frontmatter ADR fait foi ; l'index est realigne par PR signee. Le check `_scripts/check-moc-integrity.py` (PR-3) detecte mecaniquement les divergences index-vs-frontmatter.

> **Nota (v2 governance)** : Les anciens fichiers `DEC-00X` ont ete reclasses en **April 2026** :
> - DEC-004 **promu** en [[ADR-014-remove-paybox-callback-test]] (seule vraie decision architecturale)
> - DEC-001 **deplace** vers `ledger/compliance/plans/` (plan d'execution d'ADR-001, pas decision)
> - DEC-002, DEC-003 **deplaces** vers `ledger/audit-trail/` (retrospective / audit report)

---

## ADR Actifs

| ID | Titre | Status | Date | Fichier |
|----|-------|--------|------|---------|
| ADR-001 | Environment Separation (DEV/PREPROD/PROD) | Accepted | 2026-02-03 | [[ADR-001-environment-separation]] |
| ADR-002 | Airlock & Zero-Trust Agents | Accepted-Revised (v2.0) | 2026-03-07 | [[ADR-002-airlock-zero-trust]] |
| ADR-003 | RPC Governance via RpcGateService | Accepted | 2026-02-03 | [[ADR-003-rpc-governance]] |
| ADR-004 | rm/ Module Scope (DEV-only) | Accepted | 2026-02-03 | [[ADR-004-rm-module-scope]] |
| ADR-005 | Airlock Observe Mode Activation | Superseded by [[ADR-010-airlock-enforce-activation]] | 2026-02-03 | [[ADR-005-airlock-observe-activation]] |
| ADR-006 | AI Orchestrator Architecture (AI-COS) | Superseded by [[ADR-011-openclaw-claude-api-replacement]] + [[ADR-025-seo-department-architecture]] (de facto joint coverage, 2026-04-27) | 2026-02-03 | [[ADR-006-ai-orchestrator-architecture]] |
| ADR-007 | Location Independence Principle | Accepted | 2026-02-04 | [[ADR-007-location-independence]] |
| ADR-008 | Agent Placement Rules (3 Zones) | Accepted | 2026-02-04 | [[ADR-008-agent-placement-rules]] |
| ADR-009 | Phase 1 Agent Activation Framework | Accepted-Revised (v2.0) | 2026-03-07 | [[ADR-009-agents-phase1-activation]] |
| ADR-010 | Airlock Enforce Mode & CI Authority | Accepted | 2026-02-04 | [[ADR-010-airlock-enforce-activation]] |
| ADR-011 | Remplacement OpenClaw par Claude API | Accepted | 2026-03-07 | [[ADR-011-openclaw-claude-api-replacement]] |
| ADR-012 | AI-COS VPS Architecture & Agent Placement | Accepted | 2026-03-08 | [[ADR-012-aicos-vps-architecture]] |
| ADR-013 | Agent Lifecycle Governance | Accepted | 2026-04-04 | [[ADR-013-agent-lifecycle-governance]] |
| ADR-014 | Suppression /api/paybox/callback-test | Accepted | 2026-02-03 | [[ADR-014-remove-paybox-callback-test]] |
| ADR-015 | Governance Vault — Single Source of Truth | Accepted | 2026-04-18 | [[ADR-015-vault-single-source-of-truth]] |
| ADR-016 | Vehicle Page Data — Persistance par matérialisation | Accepted (2026-04-27, evidence-based promotion) | 2026-04-20 | [[ADR-016-vehicle-page-matview-persistence]] |
| ADR-017 | Nettoyer les casts TEXT↔INTEGER dans RPC pieces_* | Accepted (2026-04-27, Phase 1 LIVE -96%) | 2026-04-21 | [[ADR-017-rpc-pieces-cast-cleanup]] |
| ADR-018 | Consolider schéma dual TEXT/INTEGER auto_*/pieces_* | Deferred | 2026-04-21 | [[ADR-018-dual-column-schema-consolidation]] |
| ADR-019 | AI Content Advisor Escalation (Pattern A) | Accepted | 2026-04-21 | [[ADR-019-ai-content-advisor-escalation]] |
| ADR-020 | Weekly Governance Vault Lint | Accepted | 2026-04-23 | [[ADR-020-weekly-vault-lint]] |
| ADR-021 | Database RLS Hardening — Zero-Trust per-Table | Accepted | 2026-04-23 | [[ADR-021-database-rls-hardening-zero-trust]] |
| ADR-022 | R8 RAG Control Plane — Propose-Before-Write + 5-Layer Gates | Superseded | 2026-04-23 | [[ADR-022-r8-rag-control-plane]] |
| ADR-023 | Hook-Layer Defense for .local/governance-vault/ | Accepted | 2026-04-24 | [[ADR-023-hook-layer-defense]] |
| ADR-024 | R1 Gamme Page Data — Persistance par matérialisation (parité ADR-016) | Proposed | 2026-04-27 | [[ADR-024-r1-gamme-page-matview-persistence]] |
| ADR-025 | SEO Department Architecture (5 modules) | Accepted | 2026-04-25 | [[ADR-025-seo-department-architecture]] |
| ADR-026 | Content Repository Separation — automecanik-content as SEO Refined Layer | Superseded | 2026-04-27 | [[ADR-026-content-separation]] |
| ADR-027 | R5 Diagnostic consolidation into R3 S2_DIAG | Accepted | 2026-04-25 | [[ADR-027-r5-consolidation-into-r3-s2-diag]] |
| ADR-028 | Préprod read-only hardening (sans Supabase branch — Option D) | Accepted | 2026-04-30 | [[ADR-028-preprod-supabase-isolation]] |
| ADR-029 | RAG v2.1 Control Plane Closure — State Machine 7-Stage + Emitter/Detector | Proposed | 2026-04-25 | [[ADR-029-rag-v2.1-control-plane-closure]] |
| ADR-030 | npm ci --ignore-scripts permanent dans Dockerfile (Alpine musl + @ast-grep/cli) | Accepted | 2026-04-30 | [[ADR-030-npm-ignore-scripts-alpine-musl]] |
| ADR-031 | Four-Layer Content Architecture — Raw / Wiki / Exports / Consumers (Unified Flow All R0-R8) | Proposed | 2026-04-28 | [[ADR-031-four-layer-content-architecture]] |
| ADR-032 | Diagnostic & Maintenance Unification — kg_* canon (maintenance/DTC) + content via wiki/exports per ADR-031 | Proposed | 2026-04-29 | [[ADR-032-diagnostic-maintenance-unification]] |
| ADR-033 | Wiki Gamme Diagnostic Relations Contract — references-only from R3/R4 to `__diag_symptom` / `__diag_system` | Proposed | 2026-04-29 | [[ADR-033-wiki-gamme-diagnostic-relations-contract]] |
| ADR-034 | AI-COS Operating Contract — Observatory + Single-Trigger Routines + AP-12 anti-bricolage | Proposed | 2026-04-30 | [[ADR-034-aicos-operating-contract]] |
| ADR-035 | Diagnostic Tool Source Trust Flag — is_trusted + source_origin sur __diag_symptom_cause_link | Proposed | 2026-05-02 | [[ADR-035-diagnostic-tool-source-trust-flag]] |
| ADR-036 | Marketing Operating Layer — 3 agents G1 (LEAD/LOCAL/RETENTION) + business_unit séparé ECOMMERCE/LOCAL/HYBRID + canon brand voice | Proposed | 2026-04-30 | [[ADR-036-marketing-operating-layer]] |
| ADR-037 | Agent Naming Canon — frontmatter `role:` Zod-validated, fail-fast (SEO agents) | Accepted | 2026-05-01 | [[ADR-037-agent-naming-canon]] |
| ADR-038 | Marketing Agent Naming Canon — extension ADR-037 (MarketingRoleId + business_unit) | Accepted | 2026-05-01 | [[ADR-038-marketing-agent-naming-canon]] |
| ADR-039 | Wiki Proposal Frontmatter Zod Canon — TS mirror du JSON Schema canon, CLI validator (PR-C ADR-033) | Accepted | 2026-05-01 | [[ADR-039-wiki-frontmatter-zod-canon]] |
| ADR-040 | SEO Roles Canon R0..R8 — single source of truth côté TypeScript via @repo/seo-roles, pas de DB CHECK | Accepted | 2026-05-05 | [[ADR-040-seo-roles-canon-ts-side-only]] |
| ADR-041 | R1 Router Posture Reaffirmed — empirical validation supersedes hypothesis-driven commerce-safe pivot | Accepted | 2026-05-06 | [[ADR-041-r1-router-posture-empirical-reaffirm]] |
| ADR-042 | Wiki gamme skeleton-generator (Pattern A) — débloquer Étape 6 gammes du pivot ADR-031 sans contournement legacy | Superseded by monorepo PR #332 (direct RAG backfill, 2026-05-06) | 2026-05-06 | [[ADR-042-wiki-gamme-skeleton-generator]] |
| ADR-043 | Plan F (DevSecOps) — cadre Phase 1 threat-model-first sur 3 sprints (NIST SSDF + OWASP SAMM v2 + SLSA L2) | Proposed | 2026-05-06 | [[ADR-043-plan-F-devsecops-phase-1-cadre]] |
| ADR-044 | SEO Strategy 2026 — priorité contenu R6/R8/R7, R3 remediation only, 7 vagues | Proposed | 2026-05-07 | [[ADR-044-seo-strategy-2026-roles-priority]] |
| ADR-045 | SEO Monitoring Cron V0 — daily-fetch GSC/GA4/Links + cron/health endpoint (socle V0.A) | Proposed | 2026-05-07 | [[ADR-045-seo-monitoring-cron-v0]] |
| ADR-046 | R-stack canonique — 1 générateur par rôle + chaîne L0-L5 mécaniquement gouvernée (Phase 0 refondation) | Accepted | 2026-05-07 | [[ADR-046-r-stack-single-generator-and-layers]] |
| ADR-047 | Contract-as-code — `@repo/seo-role-contracts` SoT comportemental, séparé de l'identité (amends ADR-040) | Accepted | 2026-05-07 | [[ADR-047-seo-role-contracts-as-code]] |
| ADR-048 | Canon Enforcement Coverage Audit — combler l'asymétrie d'enforcement entre vault (mécanique) et `.spec/00-canon/` (partiel), Option D hybride 3 sprints | Accepted | 2026-05-07 | [[ADR-048-canon-enforcement-coverage]] |
| ADR-049 | DB Governance Canon Enforcement — sub-projet ADR-048 pour les 20 fichiers `.spec/00-canon/db-governance/*` (densité élevée, expertise SQL/Postgres dédiée) | Proposed | 2026-05-07 | [[ADR-049-db-governance-canon-enforcement]] |
| ADR-050 | Quality history & drift detection — `__seo_quality_history` + RPC outliers + Sentry/OTel enrichers (Phase 0 baseline trou #8) | Accepted | 2026-05-07 | [[ADR-050-quality-history-and-drift-detection]] |

---

## Par Catégorie

### Architecture

- [[ADR-001-environment-separation]] - Séparation des environnements DEV/PREPROD/PROD
- [[ADR-004-rm-module-scope]] - Classification module rm/ comme DEV-only
- [[ADR-006-ai-orchestrator-architecture]] - Architecture AI-COS LangGraph (superseded by [[ADR-011-openclaw-claude-api-replacement]] + [[ADR-025-seo-department-architecture]])
- [[ADR-007-location-independence]] - Règle Maître : Location Independence

### Sécurité

- [[ADR-002-airlock-zero-trust]] - Principe Zero-Trust pour agents IA
- [[ADR-003-rpc-governance]] - Contrôle centralisé des appels RPC
- [[ADR-005-airlock-observe-activation]] - Airlock observe (superseded by [[ADR-010-airlock-enforce-activation]])
- [[ADR-008-agent-placement-rules]] - 3 Zones → 4 zones avec [[ADR-012-aicos-vps-architecture]]
- [[ADR-010-airlock-enforce-activation]] - Airlock Enforce Mode & CI Authority
- [[ADR-014-remove-paybox-callback-test]] - Suppression endpoint vulnérable (T5)
- [[ADR-021-database-rls-hardening-zero-trust]] - Zero-trust per-table policies (RLS + INVOKER views)
- [[ADR-028-preprod-supabase-isolation]] - Préprod read-only hardening Option D ($0/mois, 5 couches de défense, sans Supabase branch — accepted post-PR monorepo #246+#248)
- [[ADR-030-npm-ignore-scripts-alpine-musl]] - `npm ci --ignore-scripts` permanent dans Dockerfile (supply chain hardening + fix Alpine musl @ast-grep/cli, formalise PR monorepo #168)

### Agents

- [[ADR-009-agents-phase1-activation]] - Framework d'activation Phase 1
- [[ADR-011-openclaw-claude-api-replacement]] - Remplacement OpenClaw par Claude API
- [[ADR-012-aicos-vps-architecture]] - AI-COS VPS Observatoire (4e zone)
- [[ADR-013-agent-lifecycle-governance]] - Cycle de vie des agents
- [[ADR-019-ai-content-advisor-escalation]] - AI Content advisor escalation (Pattern A documented)

### Performance & DB

- [[ADR-016-vehicle-page-matview-persistence]] - Vehicle Page persistance par matérialisation (`__vehicle_page_cache`, p99 < 50 ms cible)
- [[ADR-017-rpc-pieces-cast-cleanup]] - Nettoyer casts TEXT↔INTEGER dans RPC `pieces_*` (Phase 1 LIVE, RPC #1 -96%)
- [[ADR-018-dual-column-schema-consolidation]] - Consolider schéma dual TEXT/INTEGER auto_*/pieces_* (deferred)
- [[ADR-024-r1-gamme-page-matview-persistence]] - R1 Gamme Page persistance par matérialisation (`__gamme_page_cache`, parité ADR-016, proposed)
- [[ADR-035-diagnostic-tool-source-trust-flag]] - Flag `is_trusted` + `source_origin` sur `__diag_symptom_cause_link` (INC-2026-013 : 162 scores non sourcés exposés client)

### SEO

- [[ADR-022-r8-rag-control-plane]] - R8 RAG Control Plane (propose-before-write, 5-layer gates, rotation déterministe)
- [[ADR-025-seo-department-architecture]] - Architecture département SEO 5 modules (Observability, On-page, Content ops, Intelligence, GEO/AEO) sur 8 semaines, DB lean (7 tables au lieu de 15 via JSONB discriminated unions)
- [[ADR-026-content-separation]] - Séparation `automecanik-content` (SEO refined layer) du `automecanik-rag` (sources + support chatbot), pattern 2-repos par audience cohérent ADR-015, blue-green Weaviate zéro downtime
- [[ADR-027-r5-consolidation-into-r3-s2-diag]] - R5 Diagnostic consolidation into R3 S2_DIAG (sunset 1176 R5 sub-pages, hub /diagnostic-auto indexable seul, S2_DIAG ancre canonique R3)
- [[ADR-029-rag-v2.1-control-plane-closure]] - RAG v2.1 Control Plane Closure (state machine 7 stages + emitter/detector, proposed)

### Gouvernance

- [[ADR-015-vault-single-source-of-truth]] - Vault canonique unique, dépréciation `.local/governance-vault/`, guardrails agents
- [[ADR-020-weekly-vault-lint]] - Lint hebdomadaire du vault (frontmatter, supersedes, obsolète, canon-backlinks)
- [[ADR-023-hook-layer-defense]] - Défense 3 couches contre écriture `.local/governance-vault/` (hook + CI + cron), enforcement ADR-015

---

## Décisions non-ADR (historique)

Anciens fichiers `DEC-00X` reclasses vers les bonnes zones du ledger :

| Ancien ID | Nouvelle localisation | Raison |
|-----------|----------------------|--------|
| DEC-001 | [[2026-02-hardening-migration-plan]] (`ledger/compliance/plans/`) | Plan d'exécution d'[[ADR-001-environment-separation]], pas une décision |
| DEC-002 | [[2026-02-phase4-post-hardening-summary]] (`ledger/audit-trail/`) | Rétrospective Phase 4, pas une décision |
| DEC-003 | [[2026-02-paybox-compatibility-audit]] (`ledger/audit-trail/`) | Rapport d'audit technique, pas une décision |
| DEC-004 | [[ADR-014-remove-paybox-callback-test]] (promu ADR) | Seule vraie décision parmi les 4 DECs |

---

## Règles Techniques Implicites (non-ADR)

Certaines décisions sont documentées dans les **règles** plutôt qu'en ADR :

| Décision | Règle | Localisation |
|----------|-------|-------------|
| Supabase SDK direct (no Prisma) | T2 | [[rules-technical]] |
| Sessions Redis + Passport | T3 | [[rules-technical]] |
| Validation Zod | T4 | [[rules-technical]] |

> Pour les décisions de type « règle du jeu » permanentes, la canonisation se fait dans `rules-*.md` (voir [[MOC-Rules]]).

---

## Processus ADR

1. **Contexte** identifié (problème, incident, besoin)
2. **Options** analysées (minimum 2 alternatives)
3. **Décision** prise (avec justification)
4. **Conséquences** documentées (positives, négatives, neutres)
5. **Critères de succès** définis (mesurables)
6. **Revue planifiée** (date + critères de reconsidération)
7. **Signature** par decision_makers + commit signé (G3)

---

## Status Semantics (Status Machine)

> Les ADR utilisent l'un des statuts suivants. Toute autre valeur est invalide et doit être normalisée à la première occasion. Auto-checkable via `_scripts/check-frontmatter-schema.py`.

| Status | Sémantique | Critère d'entrée | Transitions sortantes autorisées |
|---|---|---|---|
| `proposed` | Décision rédigée, en attente de revue/approbation | ADR créée avec frontmatter complet, body suivant template `_templates/adr-template.md` | → `accepted` (approuvé) ; → `deferred` (info manquante) ; → `superseded` (rare, ex : remplacée avant approbation) |
| `accepted` | Décision approuvée et active. Code peut être en n'importe quel état d'implémentation | Approuvée par `decision_makers`, commit signé (G3) | → `accepted-revised` (modification substantielle ; bump `version` semver) ; → `superseded` (remplacée par une autre ADR ou un ensemble) ; → `deprecated` (devenue obsolète sans remplacement formel) |
| `accepted-revised` | Acceptée + révisée depuis ; numéro de version semver bumped (ex : v2.0) | Modification substantielle d'une ADR `accepted`, motivée explicitement | → `superseded` ; → `deprecated` |
| `deferred` | Reportée en attente d'information ou de dépendances | Décision en `proposed` qui ne peut conclure faute d'inputs | → `proposed` (reprise) ; → `superseded` ; → `deprecated` (jamais reprise) |
| `superseded` | Remplacée par une autre ADR (ou ensemble d'ADR), partiellement ou totalement | `superseded_by[]` non vide, contient ≥ 1 ADR cible existant | **terminal** (aucune transition sortante) |
| `deprecated` | Plus applicable, sans remplacement formel | Décision morte, mais le contenu garde valeur historique | **terminal** (aucune transition sortante) |

### Règles d'invariance

- **Q1 / G6 anti-BS** : tout passage à `accepted` doit citer evidence d'implémentation (migrations shippées, code refs, mesures perf) dans le frontmatter `implementation_evidence:` ou en body.
- Tout passage à `superseded` doit définir `superseded_by[]` non vide. `_scripts/check-adr-supersedes.py` enforce cette règle.
- Une ADR `proposed` > 30 jours est de la dette de gouvernance (Q4) — déclenche alert dans `weekly-vault-lint` ([[ADR-020-weekly-vault-lint]]) à venir.
- Une ADR `superseded` peut pointer vers **plusieurs** ADR via `superseded_by: [...]` lorsqu'aucune ADR seule ne couvre l'intégralité (cas « de facto joint coverage » — voir [[ADR-006-ai-orchestrator-architecture]] superseded by ADR-011 + ADR-025).

### Champs frontmatter associés

```yaml
status: <one of the 6 above>
supersedes: []          # ADR(s) que cette décision remplace
superseded_by: []       # ADR(s) qui remplacent cette décision (obligatoire si status=superseded)
status_review:          # optionnel, pour transitions
  reviewed_at: YYYY-MM-DD
  reviewed_by: "<actor>"
  reviewed_under_rule: <rule-id>
  reason: |
    <explication libre>
implementation_evidence: # optionnel, recommandé pour status=accepted
  migrations_shipped: []
  code_evidence: []
  notes: |
    <texte libre>
```

---

## Template

Voir [[adr-template]] dans `_templates/`.

---

## Voir aussi

- [[MOC-Rules]] - Règles canoniques T/G/AI/V
- [[MOC-Incidents]] - Post-mortems (sources de nouvelles ADR)
- [[MOC-Compliance]] - Checklists, evidence-packs

---

_Derniere mise a jour: 2026-05-02_

_Synchronisé manuellement vs frontmatter ADR le 2026-05-02. Q4 follow-up :
auto-générer cette table depuis `_scripts/sync-moc-decisions.py` (à créer)
pour éviter dérive future._
