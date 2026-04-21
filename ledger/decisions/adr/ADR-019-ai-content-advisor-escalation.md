---
id: ADR-019
title: "AI Content — advisor escalation via documented Pattern A, not the beta Advisor tool"
status: accepted
date: 2026-04-21
decision_makers:
  - automecanik.seo@gmail.com
supersedes: []
superseded_by: []
related_rules:
  - G1-canon
  - G3-signed-commits
related_incidents: []
reviewed_by: ""
---

# ADR-019: AI Content — advisor escalation via documented Pattern A, not the beta Advisor tool

## Contexte

Un billet de blog, remonté le 2026-04-20, annonçait un outil "Advisor" (`advisor_20260301` + header `anthropic-beta: advisor-tool-2026-03-01`) permettant à un exécuteur Sonnet de consulter un conseiller Opus au sein d'un unique appel `/v1/messages`. La promesse — intelligence proche Opus au coût d'un pipeline Sonnet — était séduisante pour nos pipelines LLM (R1-R8, reformulation RAG, polish SEO).

Vérification 2026-04-20 :

- Documentation officielle `platform.claude.com/docs/en/agents-and-tools/tool-use/overview.md` — **aucune mention** de l'Advisor tool, du tool type `advisor_20260301`, ni du header beta `advisor-tool-2026-03-01`.
- `anthropic.com/news/advisor-tool` → HTTP 404.
- Skill `claude-api` (cache 2026-04-15) — aucune référence.

Conclusion : l'API décrite dans le billet de blog n'est pas vérifiable aujourd'hui. Implémenter du code qui en dépend viole la règle "pas de bricolage" posée par le décideur et la règle G1 (canon).

Parallèlement, un audit du module `backend/src/modules/ai-content/` a révélé :

- `claude-sonnet-4-20250514` hardcodé à 2 endroits (dérive de version).
- Estimation de tokens calculée via `content.length / 4` — incompatible avec toute mesure de coût par tier.
- Health check envoyant un vrai message à l'API à chaque boot (gaspillage).
- `cacheService: any` — perte de type safety.
- Duplication de l'interface `AIProvider` entre provider et service.

Enfin, les deux candidats naturels pour un POC (`conseil-enricher`, `buying-guide-seo-draft`) portent `llmPolishEnabled = false` — chemins morts sous l'architecture skills-first.

## Décision

1. **Ne pas implémenter** le beta Advisor tool décrit dans le billet de blog tant qu'il n'est pas documenté dans `platform.claude.com/docs` ou annoncé officiellement avec un changelog vérifiable.
2. **Implémenter Pattern A — escalation subagent documentée** dans `shared/agent-design.md` du skill `claude-api` : deux appels Messages API indépendants, exécuteur (Sonnet) et conseiller (Opus), gate porté par l'appelant.
3. **Découper la livraison** en deux PRs stackées et atomiques :
   - **Phase 0 — hygiène (PR #87, commit `794f1b0c`)** — centralisation des IDs modèle, tokens réels SDK, health-check gratuit, typage `cacheService`.
   - **Phase 1a — infrastructure advisor (PR #90, commit `0540d3b7`)** — ajout de `generateContentWithAdvisor()` sur `AnthropicProvider`, opt-in, zero wiring.
4. **Différer Phase 1b** (wiring sur un service métier) tant qu'un caller actif avec quality gate mesurable n'est pas identifié.

## Options Considérées

### Option A : Implémenter l'Advisor tool du billet de blog (`advisor_20260301`)

**Description** : Étendre `AnthropicProvider` pour déclarer le tool `advisor_20260301` avec le header beta `advisor-tool-2026-03-01`, tel que décrit dans le billet.

**Avantages** :
- Pattern intégré : une seule requête `/v1/messages`, gestion du hand-off côté serveur.
- Facturation séparée annoncée par Anthropic (advisor tokens distincts).

**Inconvénients** :
- API non documentée dans la documentation officielle canon (vérifié 2026-04-20).
- URL source du billet inaccessible (404).
- Code basé sur une spec non reproductible → bricolage pur (G1-canon).
- Risque de rupture silencieuse si la beta évolue ou n'est jamais GA.

**Verdict** : **Rejetée** — viole G1 (canon) et la directive "pas de bricolage".

### Option B : Pattern A — escalation subagent documentée (choisie)

**Description** : Deux appels Messages API indépendants. Sonnet produit une draft ; un gate porté par l'appelant décide d'escalader ; Opus produit une version améliorée avec le même system prompt (préserve prompt cache).

**Avantages** :
- Repose sur des primitives SDK standard (`client.messages.create`), aucune dépendance beta.
- Traçabilité totale : deux entrées `usage` séparées, gate pilotable côté métier.
- Résilient : si l'appel advisor échoue, la draft executor est retournée — jamais d'échec total dû au chemin advisor.
- Prompt cache préservé (system prompt identique aux deux appels).
- Reversible : retirer `AdvisorConfig` revient au comportement standard.

**Inconvénients** :
- Deux appels HTTP au lieu d'un → ~100–300 ms de latence supplémentaire sur le chemin escaladé.
- Moins "magique" que le hand-off côté serveur.

**Verdict** : **Retenue**.

### Option C : Ne rien faire, attendre la GA officielle

**Description** : Laisser les pipelines tels quels, attendre qu'Anthropic publie l'Advisor tool en GA avec documentation.

**Avantages** :
- Aucune dette technique.

**Inconvénients** :
- Délai indéfini.
- Ne règle pas les problèmes d'hygiène du module `ai-content` (versions obsolètes, tokens estimés).

**Verdict** : **Partiellement retenue** — Phase 1b est effectivement différée, mais Phase 0 (hygiène) et Phase 1a (infra) sont livrées pour que l'hygiène ne régresse pas et que l'infra soit prête le jour où un caller actif est identifié.

### Option D : Wirer directement sur `conseil-enricher` (candidat initial)

**Description** : Brancher `generateContentWithAdvisor()` sur la polish de meta descrip R3.

**Avantages** :
- POC mesurable dès le merge.

**Inconvénients** :
- `conseil-enricher` porte `llmPolishEnabled = false` — chemin mort (remplacé par `/content-gen` skill Claude Code).
- Wirer du code dans un chemin mort = bricolage.

**Verdict** : **Rejetée**.

## Justification

- **G1-canon** : ne pas implémenter d'API non vérifiable dans la documentation canonique.
- **Pas de bricolage** (directive du décideur) : deux PRs atomiques, typecheck + lint + pre-commit hooks verts, CI code-gates verts, aucun wiring spéculatif.
- **Architecture skills-first** : respecte le choix déjà acté de basculer les pipelines enrichers sur Claude Code skills ; l'infra advisor reste en réserve pour les rares callers API NestJS encore actifs.
- **Mesurabilité différée mais préservée** : `AdvisorResult` expose `executorUsage`, `advisorUsage`, `escalated`, `escalationSkipped` — le jour où un caller actif est branché, le coût advisor vs executor est traçable immédiatement.

## Conséquences

### Positives

- Hygiène du module `ai-content` restaurée (SoT unique pour les IDs modèle, bump `claude-sonnet-4-6`).
- Tokens réels propagés dans `metadata.tokens` — fin de l'estimation grossière `length/4`.
- Infrastructure advisor prête, testée, typée, documentée — activable quand un caller actif apparaît.
- Aucun risque de régression : Phase 1a ne modifie le comportement d'aucun caller existant.

### Négatives

- Code dormant sur `main` (méthode `generateContentWithAdvisor` sans caller).
- Pas de mesure empirique du ROI advisor tant que Phase 1b n'est pas livrée.

### Neutres

- Deux checks CI (`Validate Specifications`, `CWV Performance Check`) échouent sur `main` pour raisons infra (répertoire `.spec/api/` absent, secret `SYSTEMPAY_CERTIFICATE_PROD` manquant des secrets CI) — observés, non causés par cette décision, à traiter dans un ADR séparé si nécessaire.

## Critères de Succès

- [x] Phase 0 mergée (#87) sans régression fonctionnelle.
- [x] Phase 1a mergée (#90) avec CI code-gates verts (TypeScript, ESLint, Backend Tests, Frontend Tests, Core Build, tous security gates).
- [x] `models.constants.ts` référencé partout (plus de string `claude-sonnet-4-20250514` hardcodé dans `ai-content`).
- [x] `message.usage` réel propagé jusqu'à `ContentResponse.metadata.tokens`.
- [ ] **Phase 1b** : wirage d'un caller actif (probablement `seo-generator` reformulation R4/R5), flag OFF par défaut, mesure sur N≥10 appels.
- [ ] **Critère Phase 1b — coût** : coût par item ≤ baseline Sonnet-solo + 20 %.
- [ ] **Critère Phase 1b — qualité** : score quality-gate ≥ baseline Sonnet-solo + 2 points.
- [ ] **Critère Phase 1b — escalation rate** : < 40 % des appels (sinon l'advisor est abusivement déclenché).

## Implémentation

**PR #87 — `chore(ai-content): phase 0 hygiene`** — commit `794f1b0c` sur `main`
- `backend/src/modules/ai-content/config/models.constants.ts` (nouveau) — `ClaudeModel` enum, `DEFAULT_EXECUTOR_MODEL`, `DEFAULT_ADVISOR_MODEL`, `ADVISOR_BETA_HEADER`.
- `backend/src/modules/ai-content/providers/anthropic.provider.ts` — `generateContentWithUsage()` retourne `message.usage` réel ; health-check sans appel payant ; interface `AIProvider` exportée.
- `backend/src/modules/ai-content/ai-content.service.ts` — propage tokens réels, type `cacheService: AiContentCacheService | null`.
- `backend/.env.example` — bump `claude-sonnet-4-6`.

**PR #90 — `feat(ai-content): advisor escalation infra (Pattern A)`** — commit `0540d3b7` sur `main`
- `backend/src/modules/ai-content/providers/anthropic.provider.ts` — nouvelle méthode `generateContentWithAdvisor(system, user, options, advisor)` retournant `{ content, executorUsage, advisorUsage, escalated, escalationSkipped }`.
- `backend/.env.example` — `ANTHROPIC_ADVISOR_MODEL=claude-opus-4-6`.

**Phase 1b — non planifiée**
- Pré-requis : identification d'un caller `aiContentService` actif en prod, avec quality gate existant exploitable pour décider l'escalation, hors périmètre skills-first.
- Candidat le plus probable : `backend/src/modules/seo/services/seo-generator.service.ts:242` (reformulation RAG R4/R5 anti-hallucination).

## Coverage Manifest (agent-exit-contract)

- `scope_requested` : "Appliquer la stratégie advisor à AutoMecanik."
- `scope_actually_scanned` : module `backend/src/modules/ai-content/` + audit des 6 callers actifs de `aiContentService` + documentation officielle Claude API + skill `claude-api` cache.
- `files_read_count` : ~15 (provider, service, module, cache, DTO, 6 services callers, .env.example, CI workflows).
- `excluded_paths` : pipelines skills-first sur AI-COS (hors périmètre API NestJS), Managed Agents API (hors besoin).
- `unscanned_zones` : volume de prod réel par caller (pas de télémétrie consultée ici), comportement du prompt cache sous charge réelle, réponse latence p95 sous escalation.
- `corrections_proposed` : Phase 0 hygiène (mergée) + Phase 1a infra (mergée).
- `validation_executed` : `tsc --noEmit` vert sur les fichiers modifiés, `eslint` clean, pre-commit hooks (prettier + lint-staged) verts, CI code-gates verts sur PR #87 et #90, vérification WebFetch de l'absence de l'Advisor tool dans la documentation officielle Claude.
- `remaining_unknowns` : ROI réel de l'escalation sur un caller actif (non mesuré — Phase 1b différée), évolution future de la spec Advisor tool si elle devient officielle.
- `final_status` : `PARTIAL_COVERAGE` — Phase 0 et Phase 1a livrées et mergées ; Phase 1b non démarrée, conditions de démarrage explicitées.

## Exit Conditions

- [x] Décision formalisée (cet ADR).
- [x] Deux PRs mergées sur `main` (#87, #90) avec CI code-gates verts.
- [x] Aucune régression détectée (gates passent, pas de caller modifié).
- [x] Infrastructure advisor activable sans modification provider ultérieure.
- [x] Conditions de reprise (Phase 1b) documentées.

**Verdict : PASS** (pour Phase 0 + Phase 1a uniquement — périmètre explicite).

## Références

- PR #87 : https://github.com/ak125/nestjs-remix-monorepo/pull/87
- PR #90 : https://github.com/ak125/nestjs-remix-monorepo/pull/90
- `shared/agent-design.md` (skill claude-api) — Pattern A canonique.
- `platform.claude.com/docs/en/agents-and-tools/tool-use/overview.md` — liste canonique des server tools (aucun advisor).
- ADR-015 — vault comme single source of truth.
- CLAUDE.md du monorepo — pointer vers le vault, anti-patterns gouvernance.
