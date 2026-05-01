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
- [[seo-operating-matrix-and-nonblocking-bootstrap-20260430]] - SEO Operating Matrix (matrice agents × registry × catalog read-only, PR #222) + non-blocking `onModuleInit` pattern verrouillé par ast-grep (PR #224, exit-124 cascade debrief)
- [[tti-home-multilayer-ssr-fix-20260430]] - Plan TTI home multi-couches (FCP 10.7s → 2.7s = −75 % ; PRs #227/#229/#230/#235) — patterns warmCache audit, RemixApiService DI direct (no HTTP loopback), diagnostic FCP≈LCP≈TTI = SSR-bound, audit `v3_singleFetch` pre-flip

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
- [[runbook-marketing-pilot-rollback]] - Runbook rollback chirurgical Phase 1 Marketing Operating Layer ([[ADR-036-marketing-operating-layer]]) : critères d'échec, désactivation routine + archive briefs + agent status:archived, post-mortem incident obligatoire. Pas de DROP de tables.
- [[r8-rag-control-plane-design-20260423]] - R8 RAG Control Plane design spec (5-layer gates, 3 artefacts par modèle, TemplateRotator)
- [[r8-rag-control-plane-implementation-plan-20260423]] - R8 RAG Control Plane implementation plan (16 artefacts DAG, rollout 8 stages)
- [[r8-vehicle-enrichment-stage1-honest-debrief-20260425]] - R8 Stage 1 vehicle enrichment honest debrief (8h+ session, bricolage scraper Clio III closed, ADR-022 control plane track)
- [[adr-031-migration-runbook-20260428]] - Runbook migration ADR-031 (4-couche raw/wiki/exports/consumers) Phases B-J : inventaire raw, migration physique, refacto scripts, pilote wiki, batch métier, support, diagnostic, deprecate __rag_proposals, cleanup J+30+
- [[adr-031-pre-phase-f-audit-corrections-20260428]] - Audit verdict utilisateur pré-Phase F.x : 5 corrections appliquées (D raw repo private, A §D23 plural amendment, B typos false alarm, C recycler plural, E+F source_refs déférés) + count vehicles corrigé 8 (pas 83)
- [[adr-032-session-empirics-20260429]] - Découvertes empiriques ADR-032 Diagnostic & Maintenance Unification (Phases 0-5 livrées en 1 session) : 5 patterns canonisés — 3 faux problèmes corrigés in-flight, seed silent fail via ON CONFLICT DO NOTHING, frontmatter wiki strict, PostgREST normalise pg_stat_statements (gate ADR-017 J+1 non MCP-validable), extension over creation (6 décisions rejected)
- [[adr-033-wave-2-closed-20260501]] - ADR-033 Phase 2/3 wave closure : 10 PRs livrées (rag #7, wiki #10, monorepo 8 PRs dont PR-B/C/D/F + 3 fixes), verdict READY 6/6 critères C1-C6 atteint 2026-05-01 10:55 UTC (run #25211876381). 6 patterns canonisés — PR-A.app collapsed (find avant supposer), Python > TS pour CI side-canon, `gh secret list` avant référencer, `.strip()` défensif env vars, PR-E déférée (outil sans contenu = bricolage), scope-disjoint firewall via worktrees. Branchement consommateurs Partie 3 débloqué.

## Gouvernance (Historique v1)

- [[single-maintainer-merge-pattern]] - Pattern admin-merge per-PR avec CI gates comme enforcement (vault opéré single-maintainer en attendant un 2ᵉ reviewer)
- [[sandbox-merge-auto-rule-20260428]] - Sandbox auto-merge rule : merges main routiniers en auto (5 conditions trigger), tag PROD + apply prod DB + force-push restent gardés
- [[03-governance]] - Regles canoniques AI-COS v1.3.0 (superseded par [[rules-ai-cos]])
- [[GOVERNANCE-HUMAN]] - Doctrine Human Authority & Zero-Trust (pre-ADR-002)

## Patterns

- [[normalize-order-id-pattern]] - Pattern : normalisation d'identifiants externes (paiements)
- [[validator-engine-spec]] - SPEC-002 Validator Engine
- [[pre-push-local-check-pattern]] - Pattern : hook pre-push local pour éliminer aller-retours CI
- [[typescript-aliases-tsc-alias-gotcha-20260427]] - Pattern : alias TypeScript backend NestJS (tsc-alias build chain, watch race, codemod sed multi-niveaux)
- [[codeql-volume-false-positive-20260427]] - Pattern : CodeQL flag des alerts pré-existantes sur diffs >300 fichiers — procédure intersection diff ∩ alerts
- [[claude-code-dual-workspace-cost-optimization-20260427]] - Pattern : split workspace dev/SEO Claude Code via cwd-bound `.claude/` (~10K tokens/turn économisés en daily dev) + lessons learned (rm symlink trap, Fleet Advisor scope)
- [[supabase-management-token]] - Provisioning + règles strictes pour le secret `SUPABASE_ACCESS_TOKEN` (Management API readonly token, vault-only, scope `organizations:read`, masking + redaction artifact, rotation procédure). Consommé par routine `vault-supabase-cost-check.yml` (PR plan AI-COS rev5).

## References

- [[airlock-decisions-reference]] - Mapping Airlock DEC-002..013 ↔ ADR canoniques (leve l'ambiguite avec les DEC legacy)

## Investigations & honest debriefs

- [[seo-traffic-drop-investigation-20260426]] - Investigation chute trafic SEO 25/04 (verdict INSUFFICIENT_EVIDENCE, GSC non ingéré, follow-up actions A→E)
- [[r5-r3-consolidation-voie-b-session-20260425]] - Audit voie B R5→R3 S2_DIAG (verdict PARTIAL_COVERAGE, ADR-027 + Phase B livrées, phases C/D/E + leviers CRM/ads à exécuter)
- [[fleet-advisor-claude-4-7-status-20260425]] - Fleet advisor + Claude 4.7 session status 2026-04-25 (8 agents UUIDs canon, draft Advisor pending board, AI-COS disk full incident resolved)
- [[adr-026-p0-handoff-completion-20260427]] - ADR-026 P0 Content Repository Separation handoff completion (PR #78 + content#1 livrées, TODO P1-P6 detailed, verdict PARTIAL_COVERAGE)
- [[pr224-exit-124-cascade-debrief-20260430]] - PR #224 perf-gates exit-124 — cascade de 6 bugs distincts révélés en chaîne (BullModule fallback `'redis'` cause racine, +5 collateral fixes), lifecycle NestJS v10 précisé, INIT_TRACE recipe, lock contract ast-grep étendu
- [[marketing-phase1-adr036-cascade-debrief-20260501]] - Phase 1 ADR-036 livrée en cascade 5+1 sous-PRs séquentielles (4 mergées #238/#240/#241/#243 + #245 superseded par ADR-038 #247) — patterns canonisés : pas de duplication des 9 tables `__marketing_*` existantes, convention `brand_gate_level PASS/WARN/FAIL` adoptée, service `MarketingMatrixService` séparé (pas god-object SEO), validation triple verrou (CHECK SQL + DTO Zod + invariant matrix), apply DB différé go user. 5 gotchas documentés (auto-log rebase conflicts, Migration Safety `-- APPROVED:`, TS2352 ProcessEnv, race tsc-alias, in-flight ADR-038 collision)

## Knowledge Sous-Dossier Diagnostics

- [[2026-02-payment-fixes]] - Index des correctifs paiement fevrier 2026
