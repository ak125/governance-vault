---
type: moc
status: canon
updated: 2026-04-23
---

# MOC: Decisions

Index des **Architecture Decision Records** (ADR) du projet AutoMecanik.

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
| ADR-005 | Airlock Observe Mode Activation | Accepted-Revised (v1.1) | 2026-03-07 | [[ADR-005-airlock-observe-activation]] |
| ADR-006 | AI Orchestrator Architecture (AI-COS) | Proposed | 2026-02-03 | [[ADR-006-ai-orchestrator-architecture]] |
| ADR-007 | Location Independence Principle | Accepted | 2026-02-04 | [[ADR-007-location-independence]] |
| ADR-008 | Agent Placement Rules (3 Zones) | Accepted | 2026-02-04 | [[ADR-008-agent-placement-rules]] |
| ADR-009 | Phase 1 Agent Activation Framework | Accepted-Revised (v2.0) | 2026-03-07 | [[ADR-009-agents-phase1-activation]] |
| ADR-010 | Airlock Enforce Mode & CI Authority | Accepted | 2026-02-04 | [[ADR-010-airlock-enforce-activation]] |
| ADR-011 | Remplacement OpenClaw par Claude API | Accepted | 2026-03-07 | [[ADR-011-openclaw-claude-api-replacement]] |
| ADR-012 | AI-COS VPS Architecture & Agent Placement | Accepted | 2026-03-08 | [[ADR-012-aicos-vps-architecture]] |
| ADR-013 | Agent Lifecycle Governance | Accepted | 2026-03-15 | [[ADR-013-agent-lifecycle-governance]] |
| ADR-014 | Suppression /api/paybox/callback-test | Accepted | 2026-02-03 | [[ADR-014-remove-paybox-callback-test]] |
| ADR-015 | Governance Vault — Single Source of Truth | Accepted | 2026-04-18 | [[ADR-015-vault-single-source-of-truth]] |
| ADR-019 | AI Content Advisor Escalation (Pattern A) | Proposed | 2026-04-21 | [[ADR-019-ai-content-advisor-escalation]] |
| ADR-020 | Weekly Governance Vault Lint | Accepted | 2026-04-23 | [[ADR-020-weekly-vault-lint]] |
| ADR-021 | Database RLS Hardening — Zero-Trust per-Table | Accepted | 2026-04-23 | [[ADR-021-database-rls-hardening-zero-trust]] |
| ADR-022 | R8 RAG Control Plane — Propose-Before-Write + 5-Layer Gates | Proposed | 2026-04-23 | [[ADR-022-r8-rag-control-plane]] |

---

## Par Catégorie

### Architecture

- [[ADR-001-environment-separation]] - Séparation des environnements DEV/PREPROD/PROD
- [[ADR-004-rm-module-scope]] - Classification module rm/ comme DEV-only
- [[ADR-006-ai-orchestrator-architecture]] - Architecture AI-COS (LangGraph, Skills, RAG)
- [[ADR-007-location-independence]] - Règle Maître : Location Independence

### Sécurité

- [[ADR-002-airlock-zero-trust]] - Principe Zero-Trust pour agents IA
- [[ADR-003-rpc-governance]] - Contrôle centralisé des appels RPC
- [[ADR-005-airlock-observe-activation]] - Airlock observe (superseded by [[ADR-010-airlock-enforce-activation]])
- [[ADR-008-agent-placement-rules]] - 3 Zones → 4 zones avec [[ADR-012-aicos-vps-architecture]]
- [[ADR-010-airlock-enforce-activation]] - Airlock Enforce Mode & CI Authority
- [[ADR-014-remove-paybox-callback-test]] - Suppression endpoint vulnérable (T5)
- [[ADR-021-database-rls-hardening-zero-trust]] - Zero-trust per-table policies (RLS + INVOKER views)

### Agents

- [[ADR-009-agents-phase1-activation]] - Framework d'activation Phase 1
- [[ADR-011-openclaw-claude-api-replacement]] - Remplacement OpenClaw par Claude API
- [[ADR-012-aicos-vps-architecture]] - AI-COS VPS Observatoire (4e zone)
- [[ADR-013-agent-lifecycle-governance]] - Cycle de vie des agents

### SEO

- [[ADR-006-ai-orchestrator-architecture]] - Inclut SEO Charter et PageRole validation
- [[ADR-022-r8-rag-control-plane]] - R8 RAG Control Plane (propose-before-write, 5-layer gates, rotation déterministe)

### Gouvernance

- [[ADR-015-vault-single-source-of-truth]] - Vault canonique unique, dépréciation `.local/governance-vault/`, guardrails agents
- [[ADR-020-weekly-vault-lint]] - Lint hebdomadaire du vault (frontmatter, supersedes, obsolète, canon-backlinks)

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
|----------|-------|--------------|
| Supabase SDK direct (no Prisma) | T2 | [[rules-technical]] |
| Sessions Redis + Passport | T3 | [[rules-technical]] |
| Validation Zod | T4 | [[rules-technical]] |

> Pour les décisions de type "règle du jeu" permanentes, la canonisation se fait dans `rules-*.md` (voir [[MOC-Rules]]).

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

## Template

Voir [[adr-template]] dans `_templates/`.

---

## Voir aussi

- [[MOC-Rules]] - Règles canoniques T/G/AI/V
- [[MOC-Incidents]] - Post-mortems (sources de nouvelles ADR)
- [[MOC-Compliance]] - Checklists, evidence-packs

---

_Derniere mise a jour: 2026-04-23_
