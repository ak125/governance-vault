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

## SEO

- [[seo-hub-refactoring]] - Refactoring SEO Hub
- [[strategie-filtre-huile]] - Stratégie filtre huile
- [[r7-brand-route-refactoring]] - Patterns frontend refactor route R7 constructeur
- [[08-seo-charter]] - PageRole taxonomy et anti-confusion rules
- [[r7-brand-editorial-live-sync]] - R7 brand live editorial sync (Wikidata + DB)
- [[r7-surface-purity-no-cross-surface-urls]] - R7 pureté surface, pas d'URLs cross-surface
- [[runbook-build-brand-rag]] - Runbook ops build-brand-rag.py (Wikidata + DB + Wikipedia REST)
- [[runbook-download-brand-oem-corpus]] - Runbook ops download-brand-oem-corpus.py (corpus brut multi-source par marque)

## Gouvernance (Historique v1)

- [[03-governance]] - Regles canoniques AI-COS v1.3.0 (superseded par [[rules-ai-cos]])
- [[GOVERNANCE-HUMAN]] - Doctrine Human Authority & Zero-Trust (pre-ADR-002)

## Patterns

- [[normalize-order-id-pattern]] - Pattern : normalisation d'identifiants externes (paiements)
- [[validator-engine-spec]] - SPEC-002 Validator Engine
- [[pre-push-local-check-pattern]] - Pattern : hook pre-push local pour éliminer aller-retours CI

## References

- [[airlock-decisions-reference]] - Mapping Airlock DEC-002..013 ↔ ADR canoniques (leve l'ambiguite avec les DEC legacy)

## Knowledge Sous-Dossier Diagnostics

- [[2026-02-payment-fixes]] - Index des correctifs paiement fevrier 2026
