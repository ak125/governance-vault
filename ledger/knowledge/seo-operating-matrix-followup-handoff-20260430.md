---
category: knowledge
doc_family: knowledge
source_type: session-handoff
title: SEO Operating Matrix — follow-up wave (5 PRs merged/in-flight) + PR-D3 deferred to ADR
slug: seo-operating-matrix-followup-handoff-20260430
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-30"
updated_by: "@fafa"
related_adr: []
related_prs:
  - "ak125/nestjs-remix-monorepo#231"
  - "ak125/nestjs-remix-monorepo#232"
  - "ak125/nestjs-remix-monorepo#233"
  - "ak125/nestjs-remix-monorepo#234"
  - "ak125/nestjs-remix-monorepo#237"
related_knowledge:
  - "seo-operating-matrix-and-nonblocking-bootstrap-20260430"
status: current
---

# Session 2026-04-30 (suite) — Vague follow-up Operating Matrix

> Suite directe du knowledge `seo-operating-matrix-and-nonblocking-bootstrap-20260430.md`.
> Cette session traite la dette infra exposée par la matrice (PR #222) en 4 PRs structurels indépendants + 1 décision différée.

## 1. Plan exécuté (4 PRs livrés sur 5 prévus)

Plan source : `~/.claude/plans/je-parle-de-ce-enumerated-octopus.md` (approuvé via ExitPlanMode).

| PR | Statut | Concern |
|----|--------|---------|
| **#231 PR-A** | ✅ MERGED `edbd6f2e` | Determinism guard CI (`audit:seo-matrix:check`) |
| **#232 PR-C** | ✅ MERGED `902b4110` | `WriteGuardModule.onModuleInit` réutilise `formatBootLog()` (single source) |
| **#233 PR-B** | ✅ MERGED `b8fdc009` | Endpoint admin `/api/admin/governance/seo-operating-matrix` |
| **#234 PR-D2** | 🟡 OPEN (CI re-run flake `ECONNRESET` npmjs) | Retrait `R3_GUIDE` de `EXECUTION_REGISTRY` |
| **#237 PR-D1** | 🟡 OPEN (CI démarre) | Close 3 gaps (R7_BRAND register, R0/R6_SUPPORT non-writing, R3 dep-aware mapping) |
| **PR-D3** | ⏸ **DEFER** | 12 unmappable agents — voir §3 |

## 2. Empirique post-merge (audit JSON régénéré localement sur la branche PR-D1)

```
gaps[]              : 0  (était 3)
unmappableAgents[]  : 12 (était 15 — les 3 r3-* auto-résolus via DEPRECATED-aware extractRoleId)
anomalies[]         : 1  (R3_GUIDE — fermé au merge de #234)
```

## 3. PR-D3 — décision différée (motivations)

### Inventaire (cf. session handoff précédent)
12 agents `unmappableAgents` restants, 2 catégories :

**A. 8 agents sans préfixe `r\d_`** :
- `agentic-critic.md`, `agentic-planner.md`, `agentic-solver.md` — orchestrateurs du moteur agentique (écrivent `__agentic_*`)
- `brief-enricher.md` — bridge multi-rôle (R3/R4/R6 briefs, écrit `__seo_page_brief`)
- `conseil-batch.md` — R3_CONSEILS batch (écrit `__seo_gamme_conseil`)
- `keyword-planner.md` — dispatcher canon-aware (read-only, route)
- `phase1-auditor.md` — validateur RAG (read-only)
- `research-agent.md` — foundation multi-rôle (écrit `__seo_research_brief`)
- `blog-hub-planner.md` — auditeur de hub (read-only)

**B. 4 agents préfixe R6 ambigu** (R6_SUPPORT vs R6_GUIDE_ACHAT) :
- `r6-content-batch.md`, `r6-image-prompt.md`, `r6-keyword-planner.md` — écrivent côté R6_GUIDE_ACHAT
- (4ème agent à confirmer dans l'inventaire R6)

### Pourquoi différer

3 stratégies sont envisageables, **et le choix entre elles est canonique** (impact sur les 39 agents R0-R8) — donc mérite un ADR avant exécution :

#### Option A — Frontmatter `role:` déclarée
```yaml
---
name: agentic-critic
role: AGENTIC_ENGINE       # nouveau rôle non-R*
description: ...
---
```
- ✅ Plus expressif que la regex de nom
- ✅ Permet un rôle non-R* (orchestrateur, validator, foundation)
- ❌ Exige un parser YAML côté `OperatingMatrixService` (vs regex pur)
- ❌ Introduit un nouveau concept de rôle (`AGENTIC_ENGINE`, `FOUNDATION`, `VALIDATOR`)
- ❌ Casse le contrat actuel "le nom de fichier est la source de vérité"

#### Option B — Renames suffixés
- `agentic-critic.md` → `r-orchestration-agentic-critic.md` (préfixe inventé `r-orchestration`)
- `r6-content-batch.md` → `r6-guide-achat-content-batch.md`
- ✅ Pas de nouveau concept — étend la convention existante
- ❌ Pour les 8 sans préfixe : invention d'un préfixe `r-orchestration` / `r-foundation` non-canon (pas dans `RoleId` enum)
- ❌ Tatoue la décision d'orchestration dans 8 noms de fichiers à perpétuité
- ❌ Renames cassent les historiques `git blame` et les éventuels imports/tests par chemin

#### Option C — Role overrides explicites (Map)
```ts
const AGENT_ROLE_OVERRIDES: Record<string, RoleId | 'AGENTIC_ENGINE'> = {
  'agentic-critic': 'AGENTIC_ENGINE',
  'r6-content-batch': RoleId.R6_GUIDE_ACHAT,
  ...
};
```
- ✅ Le moins invasif (1 fichier source ajouté)
- ✅ Préserve identité fichier
- ❌ Source de vérité éparpillée : nom de fichier ↔ override map ↔ frontmatter potentiel
- ❌ Maintenance manuelle au fil des nouveaux agents

### Trois questions architecturales sous-jacentes (pour l'ADR)

1. Les **orchestrateurs/validators non-R\*** doivent-ils être un nouveau **concept de rôle canonique** (e.g. `AGENTIC_ENGINE`, `FOUNDATION`, `VALIDATOR`) ou rester en **dehors** de `EXECUTION_REGISTRY` (comme R0_HOME/R6_SUPPORT le font déjà via `NON_WRITING_ROLES` après PR-D1) ?

2. Les **agents multi-rôles** (`brief-enricher`, `research-agent`) qui contribuent à R3/R4/R6 simultanément — comment les classer ? 1 entrée par rôle ? 1 entrée "FOUNDATION" partagée ? `agentFiles[]` redondant entre rôles ?

3. **R6 ambiguïté** post-PR-D1 (`r6-content-batch`, `r6-image-prompt`, `r6-keyword-planner` sont confirmés R6_GUIDE_ACHAT par l'inventaire) — rename + suffixe `r6-guide-achat-*` (fix tactique, scope étroit) **ou** attendre que la stratégie A/B/C soit tranchée pour les autres ?

### Recommandation pour l'ADR

Ouvrir un ADR `ADR-NNN-agent-naming-canon` qui :
1. Énumère les 3 catégories d'agent (writer/orchestrator/validator)
2. Décide entre A/B/C (option C semble la moins invasive si scope reste petit)
3. Définit les rôles canoniques additionnels si A ou C choisis (ex : `AGENTIC_ENGINE`, `FOUNDATION_RESEARCH`, ou rester sur `EXECUTION_REGISTRY` strictement écriveur)
4. Procédure de migration des 12 unmappables avec checklist par agent

## 4. Reprise en nouvelle session

Pré-requis avant toute reprise :
- [ ] PR-D2 (#234) mergée — re-run CI après flake `ECONNRESET`, attendre vert
- [ ] PR-D1 (#237) mergée — CI complète encore en cours
- [ ] (Optionnel) Vérifier sur DEV pré-prod : endpoint `/api/admin/governance/seo-operating-matrix` répond 401/200, boot logs `WriteGuard:` byte-équivalents

À la reprise :
1. Ouvrir un ADR `ADR-NNN-agent-naming-canon` dans le vault (`ledger/decisions/adr/`)
2. Trancher A/B/C avec discussion explicite des trois questions §3
3. PR monorepo follow-up : applique la décision aux 12 unmappables → après merge, `unmappableAgents[] = 0`, matrice 100% saine

## 5. Coverage manifest (AEC)

```
scope_requested        : compléter le projet SEO Operating Matrix (4 PRs follow-up)
scope_actually_scanned : 5 PRs ouvertes (4 mergées + 1 en CI re-run + 1 nouveau plan)
files_read_count       : ~30 (agent files inventaire + execution-registry + operating-matrix.* + admin module + write-guard)
excluded_paths         : .claude/agents/r1-*, r2-*, r4-*, r5-*, r8-* (déjà mappés correctement)
unscanned_zones        : Frontend Remix admin UI (déféré explicite plan §79), e2e test admin (test/ dir n'existe pas)
corrections_proposed   : 4 PRs livrées (#231, #232, #233, #234, #237) + 1 ADR à ouvrir (PR-D3)
validation_executed    : 4 PRs squash-mergées (#231-233 verts, #234/237 en cours), audit JSON régénéré localement, typecheck propre sur chaque branche
remaining_unknowns     : décision A/B/C agent-naming-canon, classification multi-rôle bridges (brief-enricher/research-agent), 4ème agent R6 ambigu à confirmer dans le 12-uplet
final_status           : SCOPE_SCANNED — 4 PRs merged ou in-flight, 1 décision canon différée à ADR
```

## 6. Références

- Knowledge précédent : `seo-operating-matrix-and-nonblocking-bootstrap-20260430.md`
- Plan exécution : `~/.claude/plans/je-parle-de-ce-enumerated-octopus.md`
- Plan source matrice : `~/.claude/plans/verifier-analyse-plus-delegated-globe.md`
- Rule canon : `nestjs-remix-monorepo/.claude/rules/backend.md` § "Non-blocking onModuleInit"
- Enforcer : `nestjs-remix-monorepo/.ast-grep/rules/backend-no-remote-io-in-onmoduleinit.yml`
