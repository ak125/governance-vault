---
adr: 073
status: proposed
date: 2026-05-17
supersedes: []
extends: [ADR-066, ADR-070, ADR-072]
related: [ADR-050, ADR-058, ADR-064, ADR-068]
authors: [fafa]
self_review_verdict: APPROVE
self_review_date: 2026-05-17
---

# ADR-073 — Canonical Fact Graph (L3) + Editorial Evidence Cache (L4) — Extension to ADR-070

## Context

ADR-070 (R8+R1 first canon, R2 prerequisite doctrine, merged 2026-05-16) prescrit la formule canon :

```
R2Content = render(R8 + R1 + KG + WIKI)
```

avec 5 deny invariants Rego enforced :

1. R8 cadre (vehicle disambiguation)
2. R1 cadre (gamme completeness)
3. **Matière factuelle** : `knowledge_facts_count > 0 OR validated_wiki_evidence_count > 0` ← critique
4. Disambiguation (uniqueness signatures)
5. No raw specs

**Problème observé** : les couches L3 (Knowledge Graph) et L4 (Wiki evidence) ne sont **pas implémentées**. Tables `__seo_vehicle_part_knowledge` et `__seo_r2_wiki_evidence` absentes des migrations 20260515-20260518. Services `R2KnowledgeGraphService`, `R2InternalDifferenceScoreService`, `R2FactsToSectionsProjector` (prescrits par ADR-070 Round 7) non créés.

**Conséquence runtime** : tous les compose ADR-066 retournent `review_required` (gate Rego `r2_no_factual_matter` ne peut être satisfait). Le pipeline R2 V2 est gouvernance-ready mais factuellement bloqué.

**Audit gap 2026-05-17** confirme : sur 18 composants candidats pour comblement L3-L4, 11 sont totalement absents, 2 partiels, 5 existants. Plan initial `seo-quality-r-stack` proposait construction from-scratch incluant des composants déjà mergés (ADR-066/070/072). Repositionnement nécessaire vers extension L3-L4 minimaliste.

## Decision

Introduire 3 PRs séquentielles sur branche `feat/seo-quality-r-stack` pour matérialiser L3-L4 d'ADR-070 :

### L3 — Canonical Fact Graph (PR-V1-KG)

4 tables append-only + 1 service + 1 worker BullMQ pour matérialiser les vérités métier extraites des sources canoniques (DB catalog + WIKI knowledge graph `kg_nodes`/`kg_edges` existants) :

| Table | Rôle |
|-------|------|
| `__seo_canonical_entities` | Entités canoniques (vehicle/gamme/brand/piece) indexées par `source_table + source_row_id` |
| `__seo_canonical_facts` | Facts atomiques typés (engine, year_range, oem_ref, …) avec `fact_hash` déterministe (`fast-json-stable-stringify + sha256`) + `superseded_by_fact_id` chain append-only |
| `__seo_fact_lineage` | Relations parent → derived facts (R8 → R1 → R2 derivations), lineage borné `max_depth=3` |
| `__seo_fact_invalidation_events` | Queue d'invalidation propagée via PG NOTIFY triggers sur 5 tables sources (`auto_type`, `auto_modele`, `pieces_relation_brand`, `pieces_gamme`, `pieces_relation_type`) |

Service `CanonicalFactGraphService` (4 méthodes minimales) :
- `register_entity(source_table, source_row) → entity_id` (idempotent)
- `register_fact(entity_id, fact_type, value, provenance) → fact_id` (append-only)
- `derive_fact(parent_fact_ids[], derivation_rule, derived_value) → derived_fact_id` (crée lineage row)
- `invalidate(source_fact_id) → invalidation_event` (transitive closure simple)

Worker BullMQ `fact-invalidation-propagator` : consume `__seo_fact_invalidation_events`, update `superseded_by_fact_id` chain, flag affected snippets via simple JOIN. Cluster lock Redis `concurrency=1 per cluster_key`.

### L4 — Editorial Evidence Cache (PR-V1-WIKI)

2 tables append-only + 3 services pour matérialiser les snippets éditoriaux validés réutilisables avec revalidation déterministe :

| Table | Rôle |
|-------|------|
| `__seo_editorial_snippets` | Snippets versioned avec `fact_tokens[]` + `canonical_fact_ids[]` (dénormalisé pour cascade) + `fact_hash` déterministe + `evidence_tier ∈ {human_curated, human_validated_llm, legacy_recovery}` + `source_quality_score` snapshot |
| `__seo_editorial_snippet_usage` | Tracking cannibalisation (snippet_id × cluster_key) |

Services :
- `FactTokenExtractor` : rule-based déterministe (pas LLM), extrait `fact_tokens[]` du `content_text`, résout chaque token vers `canonical_fact_id` via lookup
- `FactRevalidator` V2 : token-based déterministe, compare `fact_hash` snippet vs DB live via lookups ciblés (pas re-parsing NLP texte), latence p95 < 50ms par snippet
- `EditorialSnippetCacheService` : `harvest()` / `query()` / `invalidate_by_fact()` (consume invalidation events via GIN index `canonical_fact_ids`)

### Wire (PR-V1-WIRE)

Extension du `r2-composition.service.ts` existant (ADR-066) — **pas refonte** :

- Invocation `FactRevalidator.revalidate(snippet)` pré-consommation snippets (refus si drift détecté)
- Snapshot `__seo_r2_composition_inputs` étendu avec `canonical_fact_ids[]` + `fact_revalidation_result`
- Inscription du compositor comme `deterministic_builder` dans field authority registry (PR-B SEO Governance Control Plane #535)
- Écriture via OPA gateway (PR-C SEO Governance Control Plane #538) — single write path
- Hard gate Rego existant `r2_no_factual_matter` devient opérationnel (knowledge_facts_count > 0 fourni par L3 + validated_wiki_evidence_count > 0 fourni par L4)

## Explicit Non-Goals V1

**Tout ce qui suit est explicitement HORS scope V1 et nécessite ADR séparée pour activation** :

- ❌ Graph inference (fact derivation automatique au-delà de `derive_fact()` explicite)
- ❌ Semantic ranking (PageRank-like, centrality, recommendation engine)
- ❌ Adaptive composition (intent-aware, context-aware, interaction-aware)
- ❌ Interaction runtime (SSE/WebSocket, session adaptation, live recomposition)
- ❌ Realtime personalization (per-user/per-session composition)
- ❌ LLM orchestration layer dans extraction/revalidation (rule-based strict)
- ❌ Graph recommendation engine (similar facts, related entities suggestions)
- ❌ SSE composition delta updates (full SSR seulement V1)
- ❌ Cross-session adaptation (stateless per-request)
- ❌ Multi-tenant Fact Graph (single-tenant V1)
- ❌ Cross-token references claim/intent/context/interaction/governance (heptachotomie = V1.5+)
- ❌ Graph queries avancées Cypher-like / GraphQL endpoint
- ❌ Auto-resolution conflicts / merges
- ❌ Pathfinding / shortest-path graph traversal
- ❌ Versioning multi-branche (linéaire append-only seulement, supersede chain)

Toute proposition d'ajout dans cette liste exige **nouvelle ADR + signal métier empirique + provisionnement dette opérabilité explicite** (cf. règle "nouveau token = nouvelle dette opérabilité").

## Verrou "boring & small" PR-V1-KG

PR-V1-KG = cœur runtime (invalidation + lineage + replay + propagation). Toute extension explose la surface de bug et compromet le déterminisme V1.

**Critère qualité strict** : `boring + deterministic + append-only + observable + small`.

**Garde-fou** : si la PR dépasse 1500 LoC ou ajoute des features hors liste IN ci-dessus → **STOP et splitter**. Revue scope IN/OUT par 2 reviewers Eng senior avec accord écrit obligatoire pré-merge.

## Consequences

### Positives

- ADR-070 doctrine devient opérationnelle (L3 + L4 réellement présents, gate Rego `r2_no_factual_matter` satisfait)
- R2 composition existant (ADR-066) bénéficie de matière factuelle vérifiable **sans refonte**
- Replay-safety préservée (déterminisme fact_hash + append-only chain)
- Cascade invalidation cross-role automatique via lineage (PG NOTIFY → propagation < 5s p95 cible)
- Pattern compatible V2+ heptachotomie future (extensions `canonical_fact_id` partout — claims, intents, contexts, interactions, governance pourront référencer)
- Aucun conflit avec 7 PRs SEO Governance Control Plane OPEN (synergies : field authority registry + OPA gateway + event store)
- Réduction scope V1 : 6 PRs → 3 PRs, 6-8 semaines → 3-4 semaines

### Négatives

- 6 tables nouvelles → **+3-8 GB Supabase initial + 1-2 GB/mois croissance** (validé Spend Cap Pro $25/mo)
- PG NOTIFY triggers sur 5 tables sources → coût propagation latency ajouté (cible p95 < 5s)
- Worker BullMQ supplémentaire → resource consumption (mitigé par cluster lock `concurrency=1`)
- Surface opérabilité étendue (dette à provisionner via V1-Ops Semantic Control Plane post-V1 stable 30j)

### Mitigation

- **Verrou "boring & small"** sur PR-V1-KG (max 1500 LoC, périmètre strict IN/OUT, 2 reviewers Eng senior signoff)
- Tests load obligatoires pré-merge PR-V1-KG (k6/Artillery 100k+ rows + propagation < 5s p95)
- Plan de rollback global V1 documenté avec GrowthBook kill switch + DDL revert script versionné
- V1-Ops Semantic Control Plane planifié post-V1 stable 30j (lineage explorer + composition debugger + replay visualizer + propagation observatory)

## Implementation

3 PRs séquentielles sur branche `feat/seo-quality-r-stack` (depuis main monorepo) :

| # | PR | Sub-branche | Précondition | Statut Phase 0 |
|---|-----|-------------|--------------|----------------|
| 1 | **PR-V1-KG** | `feat/seo-quality-r-stack/canonical-fact-graph` | ADR-073 mergée vault + Phase 0 verte | ⏳ |
| 2 | **PR-V1-WIKI** | `feat/seo-quality-r-stack/editorial-cache` | PR-V1-KG mergée | ⏳ |
| 3 | **PR-V1-WIRE** | `feat/seo-quality-r-stack/r2-compose-wire-l3-l4` | PR-V1-WIKI mergée | ⏳ |

## Validation

- Gate Rego ADR-070 `r2_no_factual_matter` passe en `index` (au lieu de `review_required`) sur top 100 R2 pages cohorte canary
- Replay test : 100 compositions snapshot fixe → diff structurel = 0 (déterminisme)
- Propagation cascade test : `UPDATE auto_type SET puissance = X WHERE id = Y` → snippets liés flagged < 5s p95
- Coverage tests ≥ 80% sur fichiers nouveaux
- Bench load staging : 100k+ rows `canonical_facts` + 1M `fact_lineage` → propagation_latency_p95 < 5s + GIN query response p95 < 100ms

## Validation V1 stable (gate pre-V1-Ops)

Les 5 critères doctrine traduits en métriques quantitatives :

| Critère | Métrique | Seuil |
|---------|----------|-------|
| **stable** | Error rate Prometheus all V1 services | < 0.1% sur 30j roulant |
| **stable** | PR V1 merged en prod | ≥ 90j |
| **observable** | % services V1 avec metrics Prometheus + Grafana panels | 100% |
| **rejouable** | % `__seo_r2_composition_inputs` avec snapshot replay-safe | ≥ 95% |
| **explicable** | Lineage query `query_lineage(fact_id)` retourne arbre complet | < 5 min/cas |
| **rollbackable** | Drill rollback staging testé + GrowthBook kill switch | OK |

## References

### ADRs existants étendus
- ADR-066 — R2 content composition v2 (foundation mergée 2026-05-15, PR #543)
- ADR-070 — R8+R1 first canon (R2 prerequisite doctrine mergée 2026-05-16, PR #284)
- ADR-072 — R2 CQRS + DDD + snapshot + outbox + OTel + GitOps (architecture mergée 2026-05-16, PR #285)

### ADRs apparentés
- ADR-050 — Quality history + drift detection
- ADR-058 — Repository Control Plane (PR-9a)
- ADR-064 — SEO Production Control Plane
- ADR-068 — R2 doctrine strict no auto-deindex

### PRs SEO Governance Control Plane OPEN (synergies confirmées)
- PR #532 PR-A1 H1 forensic audit
- PR #533 PR-A2 audit persistence
- PR #535 PR-B field authority registry (socle authoritative_writers pour PR-V1-WIRE)
- PR #538 PR-C OPA write gateway (single write path pour PR-V1-WIRE)
- PR #539 PR-D event store atomic
- PR #541 PR-E recovery rollout
- PR #542 PR-E+1 wire real deps (GrowthBook SDK + BullMQ — Phase 0 #6 couvert)

### Plan détaillé
- Plan d'implémentation : `/home/deploy/.claude/plans/utiliser-superpower-et-verifier-misty-kettle.md` (~80 KB, doctrine verrouillée + 24 décisions tranchées + Phase 0 11 items + DoD par PR + matrice V1 stable + plan rollback global)
- Mémoire canon : `[[seo-composition-engine-doctrine-verrouillee-202605]]`
- Mémoire règle d'or : `[[feedback_v1_first_dont_build_ultimate_engine_too_early]]`
- Mémoire dette opérabilité : `[[feedback_new_token_type_equals_operational_debt]]`

## Self-review checklist (canon ADR vault)

- [x] Frontmatter complet (adr, status, date, extends, authors, self_review_verdict)
- [x] Contexte explicite (pourquoi cette ADR, problème observé)
- [x] Decision claire avec scope IN précisément délimité
- [x] **Explicit Non-Goals V1** section dédiée (15 items HORS scope V1)
- [x] Consequences positives + négatives + mitigation
- [x] Verrou qualité (boring & small) explicite
- [x] Implementation séquencée avec préconditions
- [x] Validation critères mesurables chiffrés
- [x] References ADRs existants + PRs OPEN + plan détaillé + mémoires canon
- [x] Self-review verdict APPROVE marker

**Verdict** : APPROVE (auto-vault canon `feedback_vault_self_review_before_admin_merge`)
