---
type: moc
status: canon
updated: 2026-04-26
---

# MOC: Knowledge

Base de connaissances architecturale.

## Architecture

- [[architecture]] - Architecture technique
- [[repo-map]] - Structure du monorepo
- [[vlevel-current-architecture]] - Architecture V-Level

## AI-COS

### Modèles Conceptuels
- [[00-agent-model]] - Modèle d'agents
- [[01-skill-model]] - Modèle de skills
- [[02-loop-engine]] - Moteur de boucle
- [[04-memory-model]] - Modèle mémoire
- [[05-kpi-system]] - Système KPI
- [[06-rag-system]] - Système RAG
- [[10-task-catalog]] - Catalogue des tâches
- [[11-agent-catalog]] - Catalogue des agents
- [[12-dag-p0]] - DAG Phase 0

### Architecture Technique (2026-02)
- [[02-ai-cos-contracts]] - JobEnvelope, GraphState, SkillIO schemas
- [[03-skills-registry]] - Skill manifest et registry
- [[04-rag-system]] - Chunking, hybrid search, citations
- [[05-langgraph-router]] - Router graph et flows
- [[06-minilo-weaver]] - Triggers et job management
- [[07-mcp-governance]] - PR rules et CI gates
- [[09-implementation-plan]] - Plan d'implémentation 4 steps

### DB / Ops Patterns
- [[mcp-vs-python-direct-pg]] - Quand passer MCP vs Python psycopg2 direct (CONCURRENTLY, > 60s)
- [[3-layer-error-pipeline-pattern]] - Pipeline 3-couches gestion erreur HTTP 404/410/301 (frontend catchall + API bridge + RedirectService/ErrorLogService) — anti-pattern shortcut hardcodé dans RemixController (cf. INC-2026-012)

## SEO

- [[seo-hub-refactoring]] - Refactoring SEO Hub
- [[strategie-filtre-huile]] - Stratégie filtre huile
- [[r7-brand-route-refactoring]] - Patterns frontend refactor route R7 constructeur
- [[08-seo-charter]] - PageRole taxonomy et anti-confusion rules
- [[r7-brand-editorial-live-sync]] - R7 brand live editorial sync (Wikidata + DB)
- [[r7-surface-purity-no-cross-surface-urls]] - R7 pureté surface, pas d'URLs cross-surface
- [[runbook-build-brand-rag]] - Runbook ops build-brand-rag.py (Wikidata + DB + Wikipedia REST)
- [[runbook-download-brand-oem-corpus]] - Runbook ops download-brand-oem-corpus.py (corpus brut multi-source par marque)
- [[runbook-admin-brand-editorial]] - Runbook admin UI curation éditorial R7 (FAQ/issues/maintenance)
- [[runbook-curate-r7-batch]] - Runbook ops curate-r7-batch.py (orchestration drafts → API admin)
- [[runbook-regenerate-sitemap-after-tecdoc-fix]] - Runbook ops régénération sitemap V10 + resubmit GSC après fix TecDoc orphans (lié [[2026-04-23-gsc-411k-404-tecdoc-orphans|INC-2026-012]])
- [[r8-rag-control-plane-design-20260423]] - R8 RAG Control Plane design spec (5-layer gates, 3 artefacts par modèle, TemplateRotator)
- [[r8-rag-control-plane-implementation-plan-20260423]] - R8 RAG Control Plane implementation plan (16 artefacts DAG, rollout 8 stages)
- [[r8-vehicle-enrichment-stage1-honest-debrief-20260425]] - R8 Stage 1 vehicle enrichment honest debrief (8h+ session, bricolage scraper Clio III closed, ADR-022 control plane track)

## Gouvernance (Historique v1)

- [[single-maintainer-merge-pattern]] - Pattern admin-merge per-PR avec CI gates comme enforcement (vault opéré single-maintainer en attendant un 2ᵉ reviewer)
- [[03-governance]] - Regles canoniques AI-COS v1.3.0 (superseded par [[rules-ai-cos]])
- [[GOVERNANCE-HUMAN]] - Doctrine Human Authority & Zero-Trust (pre-ADR-002)

## Patterns

- [[normalize-order-id-pattern]] - Pattern : normalisation d'identifiants externes (paiements)
- [[validator-engine-spec]] - SPEC-002 Validator Engine
- [[pre-push-local-check-pattern]] - Pattern : hook pre-push local pour éliminer aller-retours CI
- [[typescript-aliases-tsc-alias-gotcha-20260427]] - Pattern : alias TypeScript backend NestJS (tsc-alias build chain, watch race, codemod sed multi-niveaux)
- [[codeql-volume-false-positive-20260427]] - Pattern : CodeQL flag des alerts pré-existantes sur diffs >300 fichiers — procédure intersection diff ∩ alerts
- [[claude-code-dual-workspace-cost-optimization-20260427]] - Pattern : split workspace dev/SEO Claude Code via cwd-bound `.claude/` (~10K tokens/turn économisés en daily dev) + lessons learned (rm symlink trap, Fleet Advisor scope)

## References

- [[airlock-decisions-reference]] - Mapping Airlock DEC-002..013 ↔ ADR canoniques (leve l'ambiguite avec les DEC legacy)

## Investigations & honest debriefs

- [[seo-traffic-drop-investigation-20260426]] - Investigation chute trafic SEO 25/04 (verdict INSUFFICIENT_EVIDENCE, GSC non ingéré, follow-up actions A→E)
- [[r5-r3-consolidation-voie-b-session-20260425]] - Audit voie B R5→R3 S2_DIAG (verdict PARTIAL_COVERAGE, ADR-027 + Phase B livrées, phases C/D/E + leviers CRM/ads à exécuter)
- [[fleet-advisor-claude-4-7-status-20260425]] - Fleet advisor + Claude 4.7 session status 2026-04-25 (8 agents UUIDs canon, draft Advisor pending board, AI-COS disk full incident resolved)
- [[adr-026-p0-handoff-completion-20260427]] - ADR-026 P0 Content Repository Separation handoff completion (PR #78 + content#1 livrées, TODO P1-P6 detailed, verdict PARTIAL_COVERAGE)

## Knowledge Sous-Dossier Diagnostics

- [[2026-02-payment-fixes]] - Index des correctifs paiement fevrier 2026
