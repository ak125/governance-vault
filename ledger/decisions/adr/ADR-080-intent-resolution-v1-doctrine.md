---
id: ADR-080
title: "Intent Resolution V1 Doctrine — R5 traffic SEO as runtime operational intelligence layer (V1A.0 ship-first ultra-minimal)"
status: accepted
date: 2026-05-23
decision_date: 2026-05-23
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: []
related_adr: [ADR-013, ADR-027, ADR-032, ADR-058, ADR-070, ADR-077]
related_rules: [G1, G2, T1]
related_incidents: []
reviewed_by: "@fafa"
updated_at: 2026-05-24
---

# ADR-080 : Intent Resolution V1 Doctrine — R5 traffic SEO as runtime operational intelligence layer (V1A.0 ship-first ultra-minimal)

## Contexte

Le **2026-05-20** Reality Audit (`project_reality_audit_verdict_conversion_funnel_20260520` ; PR #652) a livré un verdict empirique sans appel : **taux conversion organique = 0,17%**. Cause racine = `conversion_funnel` — pas problème d'acquisition (R5 traffic SEO existe), mais problème de **résolution d'intention métier** entre acquisition (R5) et transaction (R2).

Le Diagnostic Engine V1 (ADR-077) est LIVE en PREPROD depuis 2026-05-19 (PR-A→E mergées) avec EvidencePack canonique riche (`diagnostic_confidence`, `risk_level`, `catalog_guard`, `maintenance_links`, `ui_block_inputs`) mais **sans tunnel R5 → diagnostic → CTA commerce câblé** :
- R5 pages SEO (`/diagnostic-auto/:slug`) servent contenu indexable, l'utilisateur lit puis repart
- Pas de couche `diagnostic_intent` exposée comme **vérité backend déterministe explicable**
- Event taxonomy funnel `diagnostic_to_commerce` défini (PR #676 step 4-A) mais jamais émis

Le **2026-05-23** Reality Audit Block A du moteur (cf. monorepo `audit/diagnostic-engine-reality-2026-05-23`, PR #708) confirme :
- Moteur opérationnel (113 sessions persistées, Mars-burst MVP 91 / Avr 12 / Mai 10)
- Couverture data : 13 systems × 62 symptoms × 58 causes × 162 scoring links × 21 safety rules
- EvidencePack canonique suffit pour Intent Classifier (composition pure, aucune nouvelle inférence métier)
- **Finding #1** : `RagEnrichmentEngine` legacy dans orchestrator pipeline step 8 — viole `feedback_no_rag_for_content_legacy_code_is_not_strategy` (RAG = chatbot UNIQUEMENT). Intent layer V1A.0 ne consomme **JAMAIS** `evidence_pack.rag_facts`
- **Finding #2** : `CAUSE_GAMME_MAP` mismatch `brake_fluid_low → pg_id 479` (Kit d'embrayage) au lieu de pg_id 71 (Liquide de frein). Fix 1-ligne intégré V1A.0 PR ou hotfix séparé

Verdict empirique Block A = **PIVOT** (moteur OK + 2 findings actionnables). V1A.0 wiring autorisé sans REBOOT.

**Risque sans cadrage canon** : drift vers god-engine vehicle-aware ML/RAG/graph (anti-doctrine V1-first stricte, cf. `feedback_v1_first_dont_build_ultimate_engine_too_early`). Cet ADR locke 5 versions séquencées gates-gated avec discipline V1A.0 ship-first ultra-minimal.

## Décision

Locker la **Intent Resolution V1 doctrine** comme canon L4 ADR-013, extends ADR-077 (Diagnostic CP V1 evidence-gated registry). Doctrine en 5 axes :

### 1. R5 traffic SEO devient runtime operational intelligence layer

Architecture layered canon :

| Layer | Rôle | V1A.0 implementation |
|---|---|---|
| R5 (`/diagnostic-auto/:slug`) | Acquisition symptôme (SEO indexable) | Routes existantes, meta/H1/canonical strictement préservés |
| Diagnostic Engine | Raisonnement signal → hypothèse → urgency | Existant V1 LIVE (ADR-077 PR-A→E) |
| **DiagnosticResolutionPipelineService** | **Composition pure ≤50 LOC** — délègue, asserte, émet | NOUVEAU V1A.0 (ast-grep guard `diagnostic-pipeline-composition-only`) |
| IntentClassifier | EvidencePack → `{intent, confidence, reason_codes, safety_rail}` | Pure rule-based, déterministe |
| ActionRecommender | intent + ctx → `recommended_actions[]` ordonné | Pure rule-based, backend = single SoT |
| HumanEscalationBuilder | first-class, jamais optionnel | `available: true` toujours, `priority_boost` contrôle visibilité primaire |
| InvariantAsserter | 5 invariants fail-loud | Throw `ResolutionInvariantViolationError`, aucun fallback silencieux |
| OutcomeEmitter | 1 canonical event tagué | `diagnostic_resolution_outcome` avec discriminator payload |
| VehicleContext | Continuité véhicule cross-domaine | Existant Option A (PR #606) |
| Frontend | Renderer pur (`.map()` payload) | Aucune logique métier, jamais tri/filtre/CTA côté client |

### 2. Backend = single source of truth ; frontend = renderer pur

- Backend retourne `recommended_actions[]` ordonné par `priority` ascending strict (1..N)
- Frontend lit, render, log clicks — **JAMAIS** trie, filtre, ou modifie l'ordre
- `target` = stable IDs only : route params `:gamme_id`, `tel:`, `mailto:`, `/devis-humain`. **JAMAIS** slug literal hardcodé backend
- `label_key` = i18n key. **JAMAIS** texte hardcodé inline
- Discriminator `target_role` ∈ `{R1, R2, R3, human, garage, devis}` permet dérivations runtime `to_commerce` / `to_human` (anti double-truth, pas d'event séparé)

### 3. Intent runtime-only, JAMAIS taxonomy SEO

- 7 intents enum + `safety_rail` flag : `urgence`, `garage`, `maintenance`, `commerce`, `devis`, `education`, `reassurance`
- **INTERDIT** : routes URL/sitemaps/`__seo_keywords` exposant valeurs intent. Anti-rigidité.
- **INTERDIT** : branches `if intent === X` dans composants frontend. Le payload backend est déclaratif.
- Couplage SEO ↔ Intent **INTERDIT** : R5 reste rôle canon (acquisition symptôme), Intent reste runtime/observability uniquement

**Boundary non-indexabilité (anti-drift SEO-implicite)** — Intent resolution output est **runtime state session-scoped non-indexable**. L'Intent layer (`intent`, `confidence`, `safety_rail`, `priority_boost`, `recommended_actions[]`) **NE DOIT JAMAIS** :

- muter le contenu SSR canonique de R5 (titre H1, paragraphes, meta_title/desc préservés cf. `feedback_no_touch_meta_h1_if_optimized`)
- muter ou injecter des balises `<meta>` / Open Graph / Twitter Cards
- muter ou injecter JSON-LD / structured data / schema.org
- muter ou influencer les internal linking graphs ou les anchors canoniques
- générer des variantes HTML crawlables (FAQ dynamique, sections conditionnelles indexées)
- participer aux décisions d'indexation (`<robots>`, `<link rel=canonical>`, sitemap inclusion)
- influencer le `catalog_signature` (ADR-066) ni le `R2InternalDifferenceScore` (ADR-070)

Le payload Intent reste **exclusivement** scopé à : rendu CTA runtime, télémétrie funnel, analytics. **JAMAIS** persistant comme HTML indexable. Pattern conforme ADR-068 §"Pas de filtre auto sur ... Score eligibility, Crawl budget perçu" + ADR-059 §runtime-read isolation.

**Garde mécanique** : ast-grep follow-up V1A.0 (track `__seo_*` table mutations from Intent services) — à scoper hors-PR si gap détecté en review code #711.

### 4. Single canonical event (anti-cardinality, anti double-truth)

`event_type: 'diagnostic_resolution_outcome'` avec 3 outcome_types V1A.0 discriminés par payload :
- `intent_resolved` (safety_rail = false)
- `safety_rail_triggered` (safety_rail = true)
- `action_clicked` (depuis POST /handoff, tagué `target_role`)

Différé V1A.1 : `recommendation_rejected` (negative signal probabilistic).
Différé V1.1 : `issue_resolved_approx` (north-star approximé via cron 24h post-session).

**Pourquoi 1 event au lieu de N** : cardinalité contrôlée, dashboards lisibles via `GROUP BY outcome_type`, migration simple (1 ENUM value), analytics aggregables au runtime.

### 5. Human escalation first-class (anti-cannibalisation, AI-assisted human is the moat futur)

- `available: true` **TOUJOURS** présent dans payload V1A.0 (jamais optionnel/fallback)
- `priority_boost: true` si intent ∈ `{urgence, garage}` OR `safety_rail = true` — frontend rend HumanEscalationCard en position PRIMAIRE
- `priority_boost: false` sinon — rendue en position secondaire (anti-cannibalisation du tunnel commerce)
- **Moat stratégique V1.5+** : AI-assisted human diagnostic escalation routing (specialist matching, SLA tiering, voice/chat/devis canal selection). PAS full autonomous diagnosis. **JAMAIS implémenté avant gates V1.1**.

### Versions séquencées strictes (gates KPI entre chacune)

| Version | Scope | Durée cible | Gates pour activer suivante |
|---|---|---|---|
| **V1A.0** | Reactive intent + Actions + Safety rail + Canonical event + 3 Tier 1 KPIs live | ~2-3 sem | resolved_intent_rate ≥ 55%, intent_to_commerce_rate ≥ baseline+20%, human_escalation_uptake_rate mesuré, 0 incident sev2+, golden regression CI 100% pass, 14j prod observation |
| **V1A.1** | Background outcome job + `commerce_outcome_signal` tagging + `user_affinity_id` + `false_commerce_rate` refined + Negative signals doctrine probabilistic + Confidence calibration audit | ~+1-2 sem après V1A.0 gates | false_commerce_rate ≤ 20%, resolved_intent_rate maintenu, confidence calibration skew < 20%/bucket, 0 sev2+, 14j prod |
| **V1B** | ResolutionBlock R3 + `resolution_payload` structurel stable IDs + Failure taxonomy runtime tracking + severity_weight + Golden dataset governance workflow + Runtime explainability export + Drift alarms runtime | ~+2-3 sem après V1A.1 gates | resolved_intent_rate ≥ 60%, false_commerce_rate ≤ 15%, intent_to_commerce_rate ≥ baseline+30%, 30j prod, drift alarms stables, intent_quality_score pondéré ≥ 0.7 |
| **V1.1** | Predictive mode interval-only + Snapshots + Replay deterministic CI + Decision lineage + Triplet versions + ConflictResolver détaillé + Outcome `issue_resolved_approx` + Tier 2 KPIs + Entropy monitoring + Block B Data Enrichment Pipeline scrape→raw→wiki→DB + Snapshot TTL/partition policy + Vehicle coverage heatmap | ~+4 sem après V1B gates | Tous V1.1 KPIs ≥ targets 30j, replay deterministic ≥ 99%, entropy stable, 0 sev2+, **TOUTES décisions V1A.x émises depuis V1A.0 ship-date replayables depuis inputs immutables (lineage `__diag_resolution_inputs` stocké + `output_hash` = `sha256(canonical(input))` reconstructible, pattern ADR-072 CompositionInput)** |
| **V1.5+** | Temporal context + ML classifier + Graph engine + AI-assisted human escalation moat + Intelligent human routing + Personnalisation historique + Snapshot S3 archive + ML pipeline + KG primary engine | Indéfini | Décision business + ADR vault signed amendant cet ADR |

**Discipline absolue** : aucune ligne de code V1A.1 écrite tant que V1A.0 pas en prod 14j avec gates verts. Idem pour les versions suivantes. STOP-at-Vx + funnel-as-truth (cf. ADR-077 G9).

### Cap reason codes V1A.0 = 14 (5 catégories prefix-strict)

```
DR_INTENT_*    (6 codes) — triggers classification intent
DR_SAFETY_*    (3 codes) — safety rail triggers
DR_OVERRIDE_*  (3 codes) — action recommender overrides
DR_HANDOFF_*   (2 codes) — handoff types (to_commerce, to_human)
```

Ajout d'un code = **ADR amendment + justification empirique requise**. Deprecate = `@deprecated` marker, jamais delete (governance ADR follow-up).

V1.1 cap = 30 (16 codes additionnels `DR_REJECT_*` + `DR_RESOLVED_*`).

### Feature flag canon V1A.0

- `DIAGNOSTIC_PIPELINE_V1_ENABLED` (default `false`) — rollout progressif 5% → 25% → 100%
- Kill-switch env var
- Fallback OFF : page R5 sert HTML actuel pure SEO (**zéro régression par construction**)
- ADR follow-up : graduation vers GrowthBook canon (Phase 2)

### Confidence policy (5 buckets canon)

| Range | Bucket | Sens |
|---|---|---|
| `[0.00, 0.30)` | `weak` | safety rail ON |
| `[0.30, 0.50)` | `ambiguous` | safety rail ON |
| `[0.50, 0.70)` | `plausible` | safety rail OFF si signaux OK |
| `[0.70, 0.85)` | `strong` | fort |
| `[0.85, 1.00]` | `very_strong` | très fort |

Out-of-range → `RangeError` throw (no silent fallback). `SAFETY_RAIL_THRESHOLD = 0.5`.

V1A.1 ajoutera entropy monitoring (distribution + skew + collapse alert + per-intent drift).

### Determinism guarantee V1A.x (pure-rule scoring discipline)

**Invariant déterministe** : étant donné un input snapshot identique (`EvidencePack` canonique + `VehicleContext` v:1 + `pipeline_version`), la pipeline V1A.x **DOIT** produire un output byte-identique. Pattern canon ADR-072 : `output_hash = sha256(canonical(input + pipeline_version))` via `fast-json-stable-stringify` (cf. mémoire `feedback_deterministic_input_hash_canonical_json`).

**Scoring discipline V1A.x — INTERDIT** :
- **Adaptive scoring** (poids variables en fonction d'événements passés)
- **Self-learning weights** (apprentissage en ligne sur outcomes)
- **Online learning** (mise à jour modèle au runtime)
- **Probabilistic feedback loops** (boucle outcome → priorité futurs scores)
- **Heuristique adaptative** (boost comportemental, "petit score dynamique")

Tous scoring V1A.x = **règles déterministes pures**. ML classifier, graph engine, temporal context, AI-assisted routing **explicitement déferrés V1.5+** (cf. §Versions séquencées + ADR-077 STOP-at-V1 G9). Ajout d'une heuristique adaptative en V1A.x = **violation canon = revert immédiat**.

**Garde mécanique** : ast-grep `diagnostic-no-adaptive-scoring-v1ax` follow-up — flag patterns `Math.random`, `score *=`, `weight +=`, `learnedWeights`, `userAffinity`, `boostFactor` dans `intent-classifier.service.ts` / `action-recommender.service.ts` (à compléter au review code #711).

## Options Considérées

### Option A : Pipeline mono-service avec règles métier inline

**Description** : un seul service `IntentResolutionService` contenant classifier + recommender + escalation + assert + emit.

**Avantages** :
- Moins de fichiers à créer

**Inconvénients** :
- God-service pattern interdit doctrine V1 (cf. anti-meta-god-service)
- Difficile à tester unitairement (couplage)
- Drift garanti vers "petite extension légitime" → god-engine

**Rejetée**.

### Option B : Composition pure pipeline + services dédiés (RETENUE)

**Description** : `DiagnosticResolutionPipelineService` ≤50 LOC strict, délègue à services dédiés. ast-grep guard flag tout `if`/`switch`/`for` dans le pipeline.

**Avantages** :
- Aucune règle métier dans le pipeline
- Tests unitaires par service (pure functions)
- Évolution scalable
- Garde mécanique (ast-grep) prévient drift

**Inconvénients** :
- Plus de fichiers (6 services V1A.0)

**Retenue**. Conforme `feedback_v1_first_dont_build_ultimate_engine_too_early` + pattern existant `kg-shadow.service.ts`.

### Option C : Multiple events per outcome type (action_clicked + to_commerce + to_human séparés)

**Description** : N event_types pour discriminer chaque path (un par target).

**Avantages** :
- Schemas séparés
- Cardinalité explicite à l'event-type level

**Inconvénients** :
- Double-truth (un click commerce est à la fois `action_clicked` ET `to_commerce`)
- Cardinality explosion : 6 outcome_types V1A.0 + 16 V1A.1 + N V1B = analytics chaos
- Dashboards illisibles

**Rejetée**. Single canonical event avec discriminator payload retenue.

## Conséquences

### Positives

- **Tunnel R5 → diagnostic → CTA commerce câblé** déterministe explicable
- **Backend = SoT unique** ; frontend = renderer pur (zero double-logique)
- **Composition pure pipeline** ast-grep enforced (anti-meta-god-service mécanique)
- **Anti-cardinality** : 1 canonical event vs N anti double-truth
- **Anti-cannibalisation** : human escalation toujours présent, priority_boost contrôle visibilité
- **Anti-fragilité slug** : stable IDs only dans `target` + `cause_refs.id`
- **Anti-platform-syndrome** : 5 versions séquencées gates-gated, V1.1+ paused jusqu'à evidence prod
- **Replay-ready V1.1** : `pipeline_version` field réservé V1A.0 (triplet V1.1)
- **Doctrine RAG strict** : Intent layer ne consomme JAMAIS `rag_facts` (cf. Finding #1)
- **Zero régression** : feature flag OFF → page R5 sert HTML actuel inchangé

### Négatives

- **Coût initial** : 14 backend files + 6 frontend files + 4 specs + 2 ast-grep rules + 2 migrations = ~2469 LOC V1A.0
- **Coordination versions** : 4 séquences successives (V1A.0 → V1A.1 → V1B → V1.1) avant V1.5+ moat
- **Dépendance Block A audit** : `golden seed bucketed` doit atteindre ≥10 cases/bucket avant V1A.0 ship-gate via validators humains

### Neutres

- **Cap reason codes 14** : amendment ADR requis pour ajout — design intentionnel, prévient explosion taxonomie
- **Single pipeline_version V1A.0** : triplet versions différé V1.1 (replayability primitive complète plus tard)

## Acceptance Criteria

V1A.0 ship-gate :

1. ✅ Block A Reality Audit verdict signé (GO/PIVOT) — DONE 2026-05-23 (verdict PIVOT)
2. ✅ Golden dataset bucketed 5×10 cases ownership defined — Block A livré
3. ⏳ V1A.0 PR mergé sur main monorepo — PR #711 OPEN
4. ⏳ Golden seed extended ≥10 active cases/bucket via validators humains (50+ total)
5. ⏳ 14j prod observation flag ON 5% rollout
6. ⏳ V1A.0 KPI gates verts : `resolved_intent_rate ≥ 55%`, `intent_to_commerce_rate ≥ baseline+20%`, `human_escalation_uptake_rate` mesuré, 0 sev2+

## Verification

- ast-grep CI : `diagnostic-no-string-reasons` + `diagnostic-pipeline-composition-only` = 0 violations
- Backend Tests CI : 4 specs V1A.0 (confidence-policy + intent-classifier + action-recommender + invariant-asserter) = 100% pass
- Golden regression CI : 50+ cases bucketed = 100% pass
- E2E Playwright : 5 scénarios bucketed (urgence/maintenance/flou/benign/vehicle_absent) = green
- Migration applicable idempotente (ENUM ADD VALUE IF NOT EXISTS)
- Feature flag OFF → page R5 HTML actuel inchangé (zéro régression par construction)

## Mémoires Claude liées

- `project_reality_audit_verdict_conversion_funnel_20260520` (verdict source 0,17%)
- `project_diagnostic_control_plane_v1_plan` (V1 LIVE PR-A→E mergées)
- `feedback_v1_first_dont_build_ultimate_engine_too_early` (V1 = seul livrable)
- `feedback_no_rag_for_content_legacy_code_is_not_strategy` (RAG = chatbot only)
- `feedback_vehicle_context_option_a_locked` (Option A schema v:1 figé)
- `feedback_no_autoescalation_after_single_go` (STOP-at-V1)
- `guard_hierarchy_stop_at_v1_funnel_truth` (canon STOP)

## Références

- Plan parent (monorepo) : `/home/deploy/.claude/plans/utiliser-superpower-et-verifier-precious-pebble.md`
- Block A audit (monorepo) : PR ak125/nestjs-remix-monorepo#708
- V1A.0 implementation (monorepo) : PR ak125/nestjs-remix-monorepo#711
- ADR-077 Diagnostic CP V1 evidence-gated registry (10 gates G1-G10) — cadre wider Diagnostic CP
- ADR-027 R5 sub-pages sunset doctrine
- ADR-032 ADR-032 D1-D9 diagnostic-engine wiki submodule contract
- ADR-058 Repository Control Plane
- ADR-070 R8 R1-first R2-second active disambiguation
