---
id: ADR-022
title: "R8 RAG Control Plane — Propose-Before-Write + 5-Layer Gates"
status: proposed
date: 2026-04-23
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
related_rules: ["G1", "G2", "G3"]
related_incidents: []
related_adr: ["ADR-015", "ADR-020", "ADR-021"]
reviewed_by: ""
---

# ADR-022: R8 RAG Control Plane — Propose-Before-Write + 5-Layer Gates

## Contexte

Le pipeline R8 (fiche motorisation, route `constructeurs/{brand}/{model}/{type}.html`,
53 959 types véhicules) souffre de deux problèmes simultanés :

1. **Duplicate content inter-motorisations d'un même modèle** (ex: Clio III 1.5 dCi 90 ch
   vs 106 ch : H1/intro/meta/H2 quasi identiques). Risque SEO Google.
2. **Pipeline R8 non contrôlé** : generator écrit directement dans `/rag/knowledge/`,
   aucun gate CI sur JSON Schema / forbidden terms / FK, aucune traçabilité qui a modifié
   quoi quand, aucun rollback autre que `git revert` manuel.

Le précédent R7 (hub marque, 36/36 indexées, avg quality 84.71/100) a été explicitement
**rejeté comme référence solide** par le décisionnaire @fafa : "pas contrôlé". La décision
consiste donc à concevoir R8 avec un plan de contrôle strict de bout en bout, et non à
répliquer R7.

RAG véhicule actuel : 8 fichiers `.md` au niveau MODEL pour 53K types — pipeline
partiellement déployé (1 seule page dans `__seo_r8_pages`).

## Décision

Adopter un **plan de contrôle 5 couches (L0-L5)** avec pattern **propose-before-write** et
**3 artefacts RAG par modèle** (split data / templates / role_map), rollout incrémental en
8 stages.

### Éléments structurants

1. **1 fichier RAG par model_group** (~500 fichiers), pas 53K, pas 1 500, pas
   hiérarchique 3-niveaux
2. **Split 3 artefacts** : `{slug}.md` (données auto-gen) + `{slug}.variations.yaml`
   (templates éditoriaux) + `{slug}.role_map.json` (mapping sections → blocs R8)
3. **L0 — Source contract** : DB + TecDoc, FK strictes
4. **L1 — Propose-before-write** : `VehicleRagGenerator` insère dans `__rag_proposals`
   (lifecycle pending|validating|approved|rejected|merged|expired|superseded), jamais
   d'écriture disque directe
5. **L2 — Content repository** : commit via PR signée G3 uniquement
6. **L3 — Enricher v2** : lit `git HEAD` du RAG, hard gates diversity ≥ 70 +
   no duplicate fingerprint avant UPSERT `__seo_r8_pages`
7. **L4 — Publish gate** : `seo_decision` explicite INDEX|REVIEW|REGENERATE|REJECT,
   endpoint `POST /api/admin/r8/:typeId/publish`
8. **L5 — Observability** : metrics per page, drift detection, weekly canary
9. **TemplateRotator** : rotation déterministe par `type_id` via SHA-256(salt:slug:typeId)
10. **JSON Schema canon** : 3 fichiers dans `/opt/automecanik/governance-vault/_scripts/schemas/`
    (`vehicle-model.schema.json`, `vehicle-variations.schema.json`, `vehicle-role-map.schema.json`)
11. **Classification risk_level** : low (auto-approve CI) / medium (humain éditorial) /
    high (humain + CODEOWNER vehicle-schema)
12. **Idempotence** : `input_fingerprint` unique partial index sur proposals actives →
    regen répété = no-op

### Rollout 8 stages

Chaque stage réversible via feature flag :
- Stage 0 : parallel build (table + schemas + workflows off)
- Stage 1 : shadow mode (`RAG_PROPOSAL_MODE=shadow`)
- Stage 2 : canary 10 modèles low-profile (PAS Clio/208/Golf)
- Stage 3 : CI auto-approve low-risk
- Stage 4 : enricher v2 (`R8_ENRICHER_V2_ENABLED`)
- Stage 5 : top 100 modèles (inclut Clio 3)
- Stage 6 : publish gate
- Stage 7 : full rollout + cleanup legacy
- Stage 8 : observability L5

Timeline ~5 semaines complet, ~3 semaines pour L1-L4 sur top 100.

## Options Considérées

### Option A : Status quo (rejected)

Corriger uniquement les symptômes (variation meta, H2 dynamique, fallback S_ENTRETIEN)
sans plan de contrôle.

**Inconvénients** : répète le problème R7 "pas contrôlé", drift revient dès prochain
regen, aucune gouvernance du RAG.

### Option B : Plan de contrôle 5 couches + 3 artefacts RAG (chosen)

Propose-before-write + gates à chaque étape + split data/templates/role_map.

**Avantages** :
- Traçabilité 100% : `__rag_proposals` + signed commits G3 + audit_trail vault
- Idempotence : regen sans risque d'écrase curated (`locked_fields`)
- Rollback atomique : feature flags par stage + git revert
- Pas de régression R8 pendant chantier (page existante servie tout au long)
- Aucune migration destructive (ADD only)
- Canary avant prod (10 modèles low-profile, pas Clio)

**Inconvénients** :
- ~5 semaines de chantier vs 3j pour Option A
- 16 artefacts à produire (migration, 3 schemas, 3 workflows, 2 refactors, endpoint,
  rotator, dashboard, alertes, ADR, extension ADR-020)
- Complexité additionnelle (table `__rag_proposals`, CI workflows) à maintenir

### Option C : 1 fichier RAG par type_id (~53 000 fichiers) (rejected)

Maximal variation natively distincte.

**Inconvénients** : volume ingérable (diff git illisible), redondance massive
(Clio 1.5 dCi 90 ch ≈ 95% identique à 1.5 dCi 106 ch), RAG search pollué, aucun
pattern AutoMecanik approche ce volume.

### Option D : Hiérarchique brand + model + motorisation overlay (rejected)

3 niveaux RAG mergés à l'enrich.

**Inconvénients** : 0 précédent dans codebase, gold-plating, motorisations[] déjà dans
model.md, complexité × 3 pour gain zéro.

### Option E : R7-like pattern (1 RAG / modèle, direct write) (rejected)

Répliquer R7 comme proposé initialement.

**Inconvénients** : @fafa a rejeté "R7 pas contrôlé" — le direct-write sans gate est
précisément le problème à éviter. Prendre R7 comme référence = répéter l'erreur.

## Conséquences

### Positives

- Pipeline R8 gouverné de bout en bout (de la DB source jusqu'à l'indexation)
- Cohérence avec ADR-015 (vault SoT), ADR-020 (weekly lint), ADR-021 (RLS zero-trust)
- Pattern réutilisable pour R4, R5, R6 si besoin de refactor contrôlé ultérieur
- Duplicate content éliminé par design (rotation déterministe + fingerprint gate)
- Observabilité drift : baisse qualité détectée en J+1, pas post-mortem

### Négatives / Coûts

- Chantier 5 semaines avec 16 artefacts
- Nouvelle table `__rag_proposals` à maintenir (migration + RLS + cleanup cron)
- 2 services NestJS refactorés (VehicleRagGenerator, r8-vehicle-enricher)
- CI workflow additionnel : temps runner + maintenance
- Formation équipe éditorial au nouveau flow (proposal review via Paperclip)

### Neutres

- Frontend R8 inchangé (route continue de servir via `r8Content` RPC)
- Pas de multilingue (lang: fr fixé schema 1.0.0, extension future)
- Pas de LLM (TemplateRotator déterministe, aligné skills-first)

## Mise en œuvre

### Prérequis

- [ ] Approbation explicite @fafa sur ADR-022 et design spec
  [[r8-rag-control-plane-design-20260423]]
- [ ] Validation planning 5 semaines acceptable (vs autres priorités roadmap)
- [ ] Confirmation non-régression souhaitée : R7 reste tel quel

### Ordre d'exécution

Artefacts listés section 9 du design spec, ordonnés par dépendance :
1. Migration SQL `__rag_proposals` (L0→L1)
2. JSON Schemas × 3 dans vault (L0 contract)
3. Workflows CI × 3 (L1 gates)
4. Refactor `VehicleRagGeneratorService` propose mode (L1)
5. Refactor `r8-vehicle-enricher` v2 (L3)
6. `TemplateRotator` class (L3)
7. Endpoint `POST /api/admin/r8/:typeId/publish` (L4)
8. Dashboard Grafana + alertes (L5)
9. Extension ADR-020 weekly-vault-lint scope `/rag/knowledge/vehicles/`

### Validation

- Stage 2 canary 10 modèles : cycle complet propose → validate → approved → PR → merged
  sans rejet éditorial a posteriori
- Stage 4 enricher v2 : distribution diversity_score médian ≥ 70 sur 10 modèles canary
- Stage 5 top 100 : < 5% baisse quality_score vs baseline pendant 7j monitoring
- Stage 7 cleanup : grep `writeFileSync` dans `VehicleRagGeneratorService` retourne 0
- Stage 8 : dashboard Grafana accessible, alertes armées

### Rollback

- Stages 1-5 : feature flag OFF-able sans deploy (env var)
- Stage 6 : `R8_PUBLISH_GATE_ENABLED=false`
- Stage 7 : `git revert` PRs cleanup (fenêtre 30j)

Plan d'urgence incident P1 :
1. `RAG_PROPOSAL_MODE=off` + `R8_ENRICHER_V2_ENABLED=false`
2. Legacy reprend immédiatement
3. Pages DB intactes
4. Proposals pending expirent J+14

## Notes

- Memory Claude Code : `adr-020-weekly-vault-lint`, `vault-sot-adr013`,
  `feedback_rag_vault_always_first`, `feedback_no_autoescalation_after_single_go`
- Phase A (quick fix blog list hardcoded intro variation) livrée indépendamment
  [monorepo PR #139](https://github.com/ak125/nestjs-remix-monorepo/pull/139).
  N'est PAS dans le scope de ADR-022 (différente route, hors R8).
- Design spec complet : [[r8-rag-control-plane-design-20260423]]
