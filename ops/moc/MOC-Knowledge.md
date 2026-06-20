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
- [[runbook-rag-sync-user-bootstrap]] - Runbook bootstrap compte système `rag-sync` + groupe `nestjs` + sudoers + SSH key ([[ADR-046-r-stack-single-generator-and-layers]] Layer L3 + [[ADR-050-quality-history-and-drift-detection]]). Prérequis manuel à `scripts/ops/lock-rag-knowledge.sh` (monorepo PR #356).
- [[runbook-disaster-recovery-seo-projection]] - DRP SEO Runtime Projection ([[ADR-059-seo-runtime-projection]] G1/G2). Replay deterministic depuis snapshots tar.zst immutables, validation sha256 STRICT + 5 versions complètes (builder/pipeline/extractor/runner/projection_contract), `--dry-run` défaut + `--apply` explicite, `git checkout` INTERDIT comme source replay. Rollback canonique = UPDATE `active_version_id` (jamais DELETE/TRUNCATE/DROP — audit trail préservé). 36 tests CI regression (PR monorepo PR-6c-a).
- [[sync-canon-mirrors]] - Runbook cron VPS DEV `sync-canon-mirrors.sh` ([[ADR-061-workspace-governance]] §3 canon mirrors read-only). Sync quotidien `governance-vault/ledger/rules/rules-*.md` → `nestjs-remix-monorepo/.claude/canon-mirrors/` + workspaces. Manifeste `99-meta/canon-hashes.json`. Pattern auto-PR signée G3 (jamais push direct main monorepo). Pre-commit hook monorepo bloque édits manuels.
- [[soft-404-telemetry]] - Runbook télémétrie soft-404 R2-PRODUIT ([[ADR-076-soft-404-r2-strategy]]). Table append-only `__soft_404_events` (pg_id, type_id, ts, referrer, ua_class) + vue 30j `v_soft_404_demand_30d` (≥3 hits browsers). Ownership D3/seo-team, rétention 90j. Requêtes utiles : top demand catalogue, enrichi gamme+véhicule, distribution UA, purge manuelle. Alarmes : >5k browsers/j 3j → escalade catalogue ; >50% bot/7j → revoir UA patterns ; p95 alternatives >250ms 5min → cache Redis ; couverture <95% smoke CI → fixture/EXISTS bug. SLO : p95 `/api/rm/alternatives` <200ms, cache hit >70%, couverture alternatives >95%.
- [[cwv-alert-response]] - Runbook réponse alertes Core Web Vitals CrUX field ([[ADR-063-cwv-monitoring-prod-crux-api]] `proposed` 2026-05-14). 3 actions immédiates sous 15 min (corréler déploiement PROD 30j via `gh release list` + `gh pr list merged`, vérifier cache Edge Cloudflare via `curl -sI` + purge sélective `cloudflare-purge-by-pattern.sh` avec `--max-urls` + `--warmup`, décider rollback/investigation/attente selon matrice). Procédure rollback canonique via revert PR (canon `feedback_rollback_via_revert_pr_branch_protected`, main protégé pas force-push) + nouveau tag `v*` pour deploy PROD. **Latence intrinsèque CrUX 7-10j** documentée (publication hebdo + lissage 28j) : ne pas attendre confirmation CrUX immédiate post-rollback, valider via Prometheus runtime + RUM Sentry + Lighthouse synthetic d'abord. Triage incidents : no-fetch > 48h (vérifier quota Google + API key + BullMQ queue `seo-monitor`), alerte permanente non-recoverable (changement Google CrUX algo possible, comparer avec CrUX BigQuery dataset public), origin 404 sticky 21j+ (bug normalisation origin ou trafic Chrome insuffisant). Anti-patterns rejetés : rollback sur seule alerte WARN sans corrélation déploiement, mass purge CF (canon `feedback_cf_purge_requires_warmup`), désactiver le cron CrUX pour calmer le bruit, annoncer "prod fixed" sur 1 seule métrique CrUX retombée.
- [[r8-rag-control-plane-design-20260423]] - R8 RAG Control Plane design spec (5-layer gates, 3 artefacts par modèle, TemplateRotator)
- [[r8-rag-control-plane-implementation-plan-20260423]] - R8 RAG Control Plane implementation plan (16 artefacts DAG, rollout 8 stages)
- [[r8-vehicle-enrichment-stage1-honest-debrief-20260425]] - R8 Stage 1 vehicle enrichment honest debrief (8h+ session, bricolage scraper Clio III closed, ADR-022 control plane track)
- [[adr-031-migration-runbook-20260428]] - Runbook migration ADR-031 (4-couche raw/wiki/exports/consumers) Phases B-J : inventaire raw, migration physique, refacto scripts, pilote wiki, batch métier, support, diagnostic, deprecate __rag_proposals, cleanup J+30+
- [[adr-031-pre-phase-f-audit-corrections-20260428]] - Audit verdict utilisateur pré-Phase F.x : 5 corrections appliquées (D raw repo private, A §D23 plural amendment, B typos false alarm, C recycler plural, E+F source_refs déférés) + count vehicles corrigé 8 (pas 83)
- [[adr-032-session-empirics-20260429]] - Découvertes empiriques ADR-032 Diagnostic & Maintenance Unification (Phases 0-5 livrées en 1 session) : 5 patterns canonisés — 3 faux problèmes corrigés in-flight, seed silent fail via ON CONFLICT DO NOTHING, frontmatter wiki strict, PostgREST normalise pg_stat_statements (gate ADR-017 J+1 non MCP-validable), extension over creation (6 décisions rejected)
- [[rag-to-wiki-sot-pipeline-20260503]] - Pivot architectural session 2026-05-02→03 : `automecanik-wiki/` devient SoT éditorial, `automecanik-rag/knowledge/` devient mirror read-only via CI sync. Plan v3 (9 étapes) avec 3 PRs livrées (#17 wiki audit 329 fiches, #15 raw import 365 fichiers byte-perfect, #270 monorepo refactor placement 6 scripts). Décisions canoniques : pas d'archive rag, scripts au bon emplacement sans réécriture, toute valeur préservée dans raw avant régénération. PARTIAL_COVERAGE 3/9 étapes, 6 restantes pour next session.
- [[plan-v3-step9-deliverable3-20260504]] - Plan v3 §Étape 9 deliverable 3 livré (PR monorepo #290) : pre-commit hook + workflow CI bloquant qui complètent l'ast-grep règle warning de PR #286 (pattern canon 1 script + hook + CI same SoT). Bug POSIX ERE détecté + corrigé pendant tests E2E (`\x27` PCRE-only → `$'\047'` ANSI-C octal). 12 cas E2E + 17/17 CI verts post-fix. Met à jour état réel plan v3 : 8/9 étapes livrées (cross-référencé git log monorepo, incl. PRs #288 cron + #292 mkdir Étape 6). PARTIAL_COVERAGE — reste deliverable 1 d'Étape 9 côté repo automecanik-rag.
- [[adr-033-wave-2-closed-20260501]] - ADR-033 Phase 2/3 wave closure : 10 PRs livrées (rag #7, wiki #10, monorepo 8 PRs dont PR-B/C/D/F + 3 fixes), verdict READY 6/6 critères C1-C6 atteint 2026-05-01 10:55 UTC (run #25211876381). 6 patterns canonisés — PR-A.app collapsed (find avant supposer), Python > TS pour CI side-canon, `gh secret list` avant référencer, `.strip()` défensif env vars, PR-E déférée (outil sans contenu = bricolage), scope-disjoint firewall via worktrees. Branchement consommateurs Partie 3 débloqué.
- [[adr-084-constructeurs-model-410-suppression]] - ADR-084 suppression du niveau-modèle /constructeurs (410 Gone) : 973 URLs 2-segments supprimées (HTTP 410+noindex), R7 marque + R8 véhicule préservés (200), sitemap nettoyé. Déployé + vérifié live PROD 2026-06-14 (monorepo PR #973 + #974, tag v2026.06.14-constructeurs-model-410-suppression).
- [[adr-031-gap-analysis-seo-runtime]] - Gap analysis ADR-031 (status proposed) vs besoin runtime DB projection SEO. Preuves empiriques 2026-05-13 : wiki/exports/seo/ vide (vs exports/rag/ populated), 0/7 tables projection cibles existent, pages R0-R8 lisent legacy sans active_version_id, pattern kg_v3 versioning réutilisable, SEO v9 fondation MERGED (#398/#399/#400). Prépare ADR-059 (supplements ADR-031, pas amends — les 2 ADRs évoluent en tracks parallèles). Wikilink vers ADR-059 sera ajouté par PR-1.

## Gouvernance (Historique v1)

- [[single-maintainer-merge-pattern]] - Pattern admin-merge per-PR avec CI gates comme enforcement (vault opéré single-maintainer en attendant un 2ᵉ reviewer)
- [[sandbox-merge-auto-rule-20260428]] - Sandbox auto-merge rule : merges main routiniers en auto (5 conditions trigger), tag PROD + apply prod DB + force-push restent gardés
- [[vault-self-review-workflow-20260504]] - Self-review obligatoire avant `gh pr merge --admin` sur vault PR Claude-ouvert : 8-item checklist canon (frontmatter, factuel, math, wikilinks, anti-patterns, cohérence, précédent, MOC). Étend single-maintainer + sandbox-merge-auto-rule. Précédent PR #146 (2 erreurs factuelles détectées avant merge)
- [[03-governance]] - Regles canoniques AI-COS v1.3.0 (superseded par [[rules-ai-cos]])
- [[GOVERNANCE-HUMAN]] - Doctrine Human Authority & Zero-Trust (pre-ADR-002)

## Patterns

- [[normalize-order-id-pattern]] - Pattern : normalisation d'identifiants externes (paiements)
- [[validator-engine-spec]] - SPEC-002 Validator Engine
- [[pre-push-local-check-pattern]] - Pattern : hook pre-push local pour éliminer aller-retours CI
- [[vault-prepush-hook-worktree-gotcha-20260504]] - Gotcha : pre-push G3 hook rejette les worktrees (`[[ ! -d .git ]]` faux puisque `.git` est un fichier dans worktrees). Workaround push depuis checkout principal ; fix 1-ligne avec `git rev-parse --is-inside-work-tree`
- [[vault-branch-protection-contexts-vs-checks-gotcha-20260504]] - Gotcha : `gh api PATCH .../required_status_checks -f 'contexts[]=...'` retourne 200 OK mais drop silencieusement les contexts non-encore-observés. Fix : utiliser format `checks` JSON avec `app_id` explicite via `--input -`
- [[typescript-aliases-tsc-alias-gotcha-20260427]] - Pattern : alias TypeScript backend NestJS (tsc-alias build chain, watch race, codemod sed multi-niveaux)
- [[codeql-volume-false-positive-20260427]] - Pattern : CodeQL flag des alerts pré-existantes sur diffs >300 fichiers — procédure intersection diff ∩ alerts
- [[claude-code-dual-workspace-cost-optimization-20260427]] - Pattern : split workspace dev/SEO Claude Code via cwd-bound `.claude/` (~10K tokens/turn économisés en daily dev) + lessons learned (rm symlink trap, Fleet Advisor scope)
- [[claude-code-plugin-enablement-policy-20260504]] - Politique : 8 plugins user-level désactivés (cloudflare/netlify/optibot/qodo/searchfit-seo/pagerduty/adspirer/firecrawl) pour la session app/ + règle « propose-only » (Claude propose la réactivation, jamais en silence)
- [[supabase-management-token]] - Provisioning + règles strictes pour le secret `SUPABASE_ACCESS_TOKEN` (Management API readonly token, vault-only, scope `organizations:read` + `projects:read`, masking + redaction artifact, rotation procédure). Consommé par routine `vault-supabase-cost-check.yml`.
- [[supabase-cost-surface-drift-v1]] - Méthodologie V1 du workflow `vault-supabase-cost-check.yml` (refonte 2026-05-18) : structural drift detection sur la cost surface Supabase (plan tier + projects + add-ons) sans projection $ — Management API v1 ne l'expose pas. Defense-in-depth 5 couches, snapshot canonique sha256 replay-safe, P1/P2 severity ladder.

## References

- [[airlock-decisions-reference]] - Mapping Airlock DEC-002..013 ↔ ADR canoniques (leve l'ambiguite avec les DEC legacy)

## Investigations & honest debriefs

- [[seo-traffic-drop-investigation-20260426]] - Investigation chute trafic SEO 25/04 (verdict INSUFFICIENT_EVIDENCE, GSC non ingéré, follow-up actions A→E)
- [[r5-r3-consolidation-voie-b-session-20260425]] - Audit voie B R5→R3 S2_DIAG (verdict PARTIAL_COVERAGE, ADR-027 + Phase B livrées, phases C/D/E + leviers CRM/ads à exécuter)
- [[fleet-advisor-claude-4-7-status-20260425]] - Fleet advisor + Claude 4.7 session status 2026-04-25 (8 agents UUIDs canon, draft Advisor pending board, AI-COS disk full incident resolved)
- [[adr-026-p0-handoff-completion-20260427]] - ADR-026 P0 Content Repository Separation handoff completion (PR #78 + content#1 livrées, TODO P1-P6 detailed, verdict PARTIAL_COVERAGE)
- [[pr224-exit-124-cascade-debrief-20260430]] - PR #224 perf-gates exit-124 — cascade de 6 bugs distincts révélés en chaîne (BullModule fallback `'redis'` cause racine, +5 collateral fixes), lifecycle NestJS v10 précisé, INIT_TRACE recipe, lock contract ast-grep étendu
- [[marketing-phase1-adr036-cascade-debrief-20260501]] - Phase 1 ADR-036 livrée en cascade 5+1 sous-PRs séquentielles (4 mergées #238/#240/#241/#243 + #245 superseded par ADR-038 #247) — patterns canonisés : pas de duplication des 9 tables `__marketing_*` existantes, convention `brand_gate_level PASS/WARN/FAIL` adoptée, service `MarketingMatrixService` séparé (pas god-object SEO), validation triple verrou (CHECK SQL + DTO Zod + invariant matrix), apply DB différé go user. 5 gotchas documentés (auto-log rebase conflicts, Migration Safety `-- APPROVED:`, TS2352 ProcessEnv, race tsc-alias, in-flight ADR-038 collision)
- [[audit-claude-md-agents-md-validator-20260503]] - Audit + validateur structurel `CLAUDE.md` / `AGENTS.md` monorepo (4 PRs livrées : monorepo #271/#272/#273 + wiki #18) — pattern « validateur bash + 4-gate CI + CODEOWNERS » réutilisable. Discipline mémorielle (« pas d'IP hardcodée ») → discipline structurelle (CI BLOCK + pre-commit). 9 self-tests embarqués, anti-patterns sur lignes ajoutées uniquement, hint mémoire dans la sortie d'erreur. Liste P1-P3 d'améliorations futures (workflow trigger paths-filter, validateur miroir wiki, sections canoniques 3 agents, IP cleanup rétroactif, link-checker, auto-bump submodule)
- [[adr-028-option-d-deploy-cascade-handoff-20260504]] - ADR-028 Option D 7-class deploy main cascade handoff (2026-05-04 ~16:50 UTC). 3-day deploy block triggered par PRs #246/#248 sans audit env-var complet. 7 classes de strict-validation (env-validation/payment/app.config/15-modules-services/4-config-services/RAG-env/SESSION_SECRET). 6/7 PRs merged (#274/#276/#277/#284/#287/#291), PR #298 OPEN auto-merge en attente CI re-run. Pattern canonique : `NODE_ENV === 'production'` + `&& !readOnly` via `isReadOnlyMode()` ; Supabase eager constructors → helper `getEffectiveSupabaseKey()`. Next-session checklist + anti-patterns retex. Phase F.5 ADR-031 orthogonal et déjà ALL MERGED 2026-05-03.
- [[audit-claude-md-handoff-session2-20260504]] - Handoff session 2 du chantier audit AGENTS.md/CLAUDE.md : item P1 (paths-filter agents-md-validation) en cours via PR #293, auto-merge queued — fix défensif validé (auto-validation gate sur sa propre PR ✓) ; cause réelle PR #273 BEHIND identifiée comme « stale checks vs new base sha » général (pas spécifique paths-filter). Découverte adjacente : PR #294 introduit dependabot-claude-review.yml qui échoue GATE-3 Runner Blast-Radius (pull_request_target + actions/checkout = vulnérabilité fork PR exfiltration secrets). Pattern « BEHIND merry-go-round » documenté + reprise session 3 listée (vérifier #293 final, ouvrir ticket GATE-3, continuer P2/P3 backlog).
- [[auto-merge-dependabot-claude-review-architecture-20260504]] - Architecture 4 couches auto-merge Dependabot avec review Claude (PRs #285/#289/#294, ADR-028) — décision d'architecture documentée pour le pipeline auto-merge. Doc adjacente, link MOC ajouté ici par hygiène G2 (orphan détecté lors du commit handoff session 2).
- [[adr-028-8th-class-handoff-20260505]] - ADR-028 cascade 8e classe découverte 2026-05-05 post-merge PR #298 (7e SESSION_SECRET). Combo runtime errors empêche health check 2min : `Invalid API key` Supabase sur 2 services non couverts par sweep classe 4 (RagWebIngestDbService + AdminJobHealthService) + `RPC BLOCKED: get_random_vehicle_gamme_combinations (UNKNOWN_BLOCKED_PROD)` cron seo-monitor + script `seo-audit-weekly.sh` absent du Dockerfile. Run rouge 25377292210 (head SHA 82c1b62). 3 hypothèses + investigation à mener prochaine session (audit `getEffectiveSupabaseKey()` sweep manqué, RPC whitelist canon, Docker COPY scripts/). Verdict PARTIAL_COVERAGE.
- [[adr-028-9th-class-handoff-20260505]] - ADR-028 cascade 9e classe découverte 2026-05-05 post-merge PR #313 (PR-A `guardReadOnly()` helper + 5 services gated). PR-A élimine empiriquement les `Invalid API key` sur les 5 services scope (RagWebIngestDb writes, AdminJobHealth writes, ShippingCalculator, SeoMonitor processor, SeoAudit worker) mais deploy main toujours RED. 1 cause BLOCKING + 4 bruits log : (1) PORT mismatch ci.yml `PORT=3200` vs docker-compose mapping `3200:3000` — Nest écoute sur 3200 inside, rien sur 3000 où Docker route → /health unreachable, régression cachée depuis PR #248 (2026-05-01) derrière les 8 classes précédentes ; (2-5) `LegalService.createDocument` write non gated, `RagWebIngestDbService.listJobsByStatus` SELECT non gated, Meilisearch init fail, CatalogService warming errors. Run rouge 25391923356 (head SHA 1220b4b3). Aucun deploy main success dans 200 derniers runs ci.yml. Verdict PARTIAL_COVERAGE — cause #1 PORT à confirmer empiriquement avant fix séquencé Patch #1 (ci.yml 1 ligne) puis PR-A.1 (sweep services + Meilisearch).
- [[seo-pieces-r2-thin-content-investigation-20260507]] - Forensic /pieces/* thin content (verdict ROOT_CAUSE_IDENTIFIED). 73% URLs `Crawled - currently not indexed` GSC, organic GA4 −48% le 07/05. Cause = migration TTFB `20260128_get_pieces_for_type_gamme_v4_raw_seo.sql` qui a déplacé SEO processing SQL→NestJS pour 10s→1s, contrat receveur jamais honoré (`rm-builder.service.ts:554,671` retourne fallback vide). Effet : meta description tronquée 30c identique entre 18 variantes type_id du même triplet (gamme×marque×modèle) → signal duplicate intra-modèle. R8 `/constructeurs/*` a 37 templates ADR-022 Pilier 2b, R2 n'a aucun équivalent. 50+ tables legacy `__seo_*` (lexique matrice 221, granularity patterns 34, variable patterns 4, zone coefficients, etc.) dorment intactes en `_archive` schema — débranchées du runtime, non écrasées. Voie canon 3 axes : (1) restauration `_archive`→`public` trivial INSERT…SELECT ; (2) implémenter `r2-pieces-enricher.service.ts` calqué sur R8 + `SEO_R2_*_VARIATIONS` ; (3) hardening DB CHECK length(meta_description) BETWEEN 130 AND 200 + CI lint zéro duplicate intra-modèle + snapshot pré-migration obligatoire. Aucun PITR/Wayback nécessaire.
- [[seo-v9-cascade-state-20260508]] - SEO seo-v9 cascade état session 2026-05-08 : 3 PRs drafts livrées (PR #398 audit + finding V4 code mort, PR #399 PR-2a registries+Zod, PR #400 PR-2b policies stacked). Cumul 70/70 tests verts, aucun service métier touché. Findings empiriques : V4 = code mort de prod (0 appel applicatif), volume R2 4M raw / 502K SEO-safe / 1960 sitemap (justifie R2IndexabilityGate ×256). Décision PR-2 : scénario A (refactor majeur). Suite HOLD nouvelle session : PR-2c refactor V4, PR-2d tests + variables marketing, PR-3+ branchement applicatif.

## Knowledge Sous-Dossier Diagnostics

- [[2026-02-payment-fixes]] - Index des correctifs paiement fevrier 2026

- [[ADR-091-wiki-score-recalibration]] — recalibrage confidence_score wiki (vérité>conformité)
