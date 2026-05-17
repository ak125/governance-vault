---
id: ADR-074
title: "Unified Indexability Decision Plane (UIDP) V1"
status: proposed
date: 2026-05-18
decision_makers: ["@ak125", "automecanik.seo@gmail.com"]
supersedes: []
superseded_by: []
related_rules:
  - feedback_duplication_is_root_cause_signal
  - feedback_no_bricolage_escalate_to_industry_standard
  - feedback_single_write_path_needs_bypass_scanner
  - feedback_v1_first_dont_build_ultimate_engine_too_early
  - feedback_no_url_changes_ever
  - feedback_no_auto_page_suppression_ever
  - feedback_r_seo_09_phase1_path_based_block
related_incidents:
  - GSC noindex 336k snapshot 2026-05-11
reviewed_by: "@ak125"
---

# ADR-074: Unified Indexability Decision Plane (UIDP) V1

## Contexte

Le rapport Google Search Console du 2026-05-11 a remonté **336 k pages
« Exclues par la balise noindex »** sur `automecanik.com`, concentrées sur
`/pieces/*` (R2_PRODUCT_LIST) et `/constructeurs/*` (R8_VEHICLE). Date de
cohorte GSC : 2022-08-16 (PAS une date de régression code — cf. mémoire
`feedback_no_blind_trust_gsc_first_detection_date`).

Le diagnostic forensic (3 Explore agents read-only + spot-check curl
5 URLs) a confirmé que ces 336 k pages sont **majoritairement
intentionnelles** (quality gates + TecDoc legacy range non-validé), mais
a aussi révélé une **fragmentation structurelle** de l'autorité sur
l'émission `robots` :

1. **5 colonnes DB TEXT/INT sans FK** (`auto_type.type_display`,
   `auto_marque.marque_relfollow`, `auto_modele.modele_relfollow`,
   `auto_type.type_relfollow`, `pieces_gamme.pg_display`) — anti-pattern
   confirmé par le skill `vehicle-ops` (TEXT columns, no FK).
2. **7+ règles code éparses** (R1/R8 thresholds, R2 gate, canonical
   mismatch, no-products fallback, malformed URLs, R2 eligibility,
   V-Level).
3. **Range hardcodé `[60000, 83456]`** dans
   `frontend/app/components/vehicle/r8/r8-transform.ts:198-208`, qui
   override `is_indexable` sans déclaration explicite ni sunset path.
4. **Header ≠ meta sur `/constructeurs/*`** : type 76550 émet header
   `X-Robots-Tag: index, follow` MAIS meta `noindex, nofollow` — anomalie
   confirmée par curl. Google applique le plus restrictif, mais le
   signal contradictoire gâche du crawl budget.
5. **Aucun audit trail** : impossible de chiffrer ou replay la décision
   pour une URL donnée → debug GSC laborieux.

Le service `SeoIndexabilityPolicyService.computeIndexability()` existe
déjà comme cascade canonique côté backend, mais **n'est pas consommé**
par les 3 émetteurs (meta R2, meta R8, header backend). Pattern
« duplication = abstraction manquante »
(cf. `feedback_duplication_is_root_cause_signal`).

## Décision

Établir un **Unified Indexability Decision Plane (UIDP)** : un pipeline
canonique pure-function exposable backend NestJS ET frontend Remix SSR,
mécaniquement scellé par AST guardrail + snapshot baseline + governance
ADR. Livraison en 2 PRs strictement scoped (V1).

**Topologie canon** :
```
Composer pure (compute) → Verdict typé (enum + reasonCodes ≤ 1)
     → Emitter unique (meta = header) → Remix Response.headers
```

Trois émetteurs consommateurs sont wirés derrière le composer canonique :
- `frontend/app/components/vehicle/r8/r8-transform.ts` (R8 — remplace
  range hardcodé `[60000, 83456]` par flag `tecdocReleaseGateOpen`)
- `frontend/app/utils/pieces-vehicle.loader.server.ts` (R2 — `meta robots`
  via `data.robots` + `X-Robots-Tag` via `Response.headers`)
- `backend/src/modules/seo/interceptors/seo-headers.interceptor.ts`
  (étend `delete X-Robots-Tag` aux `/constructeurs/*`, garantissant
  que **le loader Remix est l'unique autorité d'émission**)

Une règle AST `seo-no-direct-robots-emission.yml` (severity `error`,
BLOCKING au pre-commit + CI) interdit toute émission directe de `name:
"robots"`, `"X-Robots-Tag"`, ou clé `robots:` dans un objet `seo` Remix
hors des émetteurs whitelisted.

**Cascade décisionnelle** (préservation behaviour-identique vs. version
pré-UIDP) :
1. `CANONICAL_MISMATCH` (strict, exclusif) → `NOINDEX_NOFOLLOW`
2. `R2_CONDITIONS_MISSING` (R2 surface, exclusif fail-safe) → `NOINDEX_NOFOLLOW`
3. `R2_GATE_FAIL` (≥1 condition R2 manquante) → `NOINDEX_NOFOLLOW`
4. `FAMILIES_BELOW_THRESHOLD` → `NOINDEX_FOLLOW`
5. `GAMMES_BELOW_THRESHOLD` → `NOINDEX_FOLLOW`
6. `FINGERPRINT_DUPLICATE` (PR-9) → `NOINDEX_FOLLOW`
7. `TECDOC_RELEASE_GATE` (caller flag) → `NOINDEX_NOFOLLOW`
8. Default → `INDEX_FOLLOW`

**Invariants V1 (enforced par test)** :
- `reasonCodes.length === 0` ↔ `kind === INDEX_FOLLOW`
- `reasonCodes.length === 1` ↔ `kind ∈ {NOINDEX_FOLLOW, NOINDEX_NOFOLLOW}`
- `reasonCodes.length ≤ 1` (limite stricte V1 — secondaires V1.5+ gated)

## Options Considérées

### Option A — UIDP unified plane (RETENUE)

**Description** : Extraire la cascade existante en pure function package
`@repo/seo-role-contracts`, wirer les 3 émetteurs, ajouter AST guardrail +
snapshot baseline. 2 PRs V1, behaviour-preserving 100%.

**Avantages** :
- Réutilise l'autorité canonique existante, ne reconstruit pas
- Meta == header par construction (élimine l'anomalie type 76550)
- Mécaniquement scellé par AST → drift PR future bloqué
- Snapshot lock → comportement actuel verrouillé, changements forcent
  revue ADR
- Pattern réutilisable pour les autres control planes SEO (canonical,
  hreflang, schema.org, sitemap inclusion)

**Inconvénients** :
- 2 PRs au lieu de 1 (split composer/wiring)
- Légère dette legacy : `RobotsValue` string union conservée `@deprecated`
  pour 1 release
- Hardcoded range `[60000, 83456]` reste (transformé en flag, sunset = V2+)

### Option B — Patch ponctuel header/meta uniquement

**Description** : Ajouter `delete X-Robots-Tag` pour `/constructeurs/*`
dans l'interceptor (~10 lignes). Fix le bug observé sans toucher au
reste.

**Avantages** :
- Minimal, immédiat
- Risque très faible

**Inconvénients** :
- Bricolage par définition (cf. mémoire
  `feedback_no_bricolage_escalate_to_industry_standard`)
- Ne résout pas la fragmentation d'autorité — le pattern se ré-installera
  ailleurs
- Pas de pattern réutilisable pour les futurs control planes
- Aucun audit / replay possible

### Option C — Plate-forme SEO complète (DDD + Event sourcing)

**Description** : Refondre toute l'émission SEO (robots + canonical +
hreflang + schema) en plate-forme événementielle avec audit log,
replay, et policy engine.

**Avantages** :
- Architecturalement parfait
- Capacités V2+ disponibles dès le départ

**Inconvénients** :
- Over-engineering massif pour résoudre un problème robots
- Coût d'implémentation 10x+
- Plateforme abstraite prématurée
- Maintenance lourde, risque "framework SEO maison incontrôlable"

## Justification

L'Option A est retenue parce qu'elle :

1. **Résout le bug observé** (header ≠ meta, type 76550) par construction
   (single emission point + typage strict)
2. **Adresse la cause structurelle** (fragmentation d'autorité) sans
   sur-ingénierie
3. **Préserve le comportement actuel** (snapshot lock) → rollout sans
   risque de désindex accidentelle
4. **Reste boring & small** : 2 PRs ~750 LOC + tests cumul, lisible,
   réversible par revert
5. **Devient un template** réutilisable pour les autres décisions SEO
   (canonical, hreflang, schema.org) — mais cette extension reste
   **gouvernée par ADR dédiée**, pas auto-promotion
6. **Mécanise l'anti-bypass** : AST rule BLOCKING + snapshot baseline
   garantissent que la régression PR future = CI rouge

## Conséquences

### Positives

- Symétrie meta == header garantie par typage et construction (le code
  consomme la même `IndexabilityVerdict` pour les deux émissions)
- Audit possible via `verdict.reasonCodes[0]` (debug GSC déterministe)
- Pattern réutilisable canonical, hreflang, schema (V2+ governance-gated)
- Discipline d'expansion : nouveau control plane = nouvel ADR vault
  (point de friction structurel, prévient l'expansion incontrôlée)
- Sunset path clair pour le range hardcodé `[60000, 83456]` (V2+ remplacé
  par `tecdoc_release_status` column, gouverné par ADR séparée)

### Négatives

- Légère dette de migration : `RobotsValue` string union conservée
  `@deprecated` 1 release, retrait V1.5
- Hardcoded range `[60000, 83456]` reste en V1 (transformé en flag
  `tecdocReleaseGateOpen`, mais le calcul reste côté caller)
- Pas d'audit log persistant en V1 (V1.5 evidence-gated)

### Neutres

- Le composer reste accessible directement pour les tests + replay V1.5
  (pas de "compute-and-bind" wrapper imposé — Remix `Response.headers`
  natif remplace l'AsyncLocalStorage envisagé initialement)

## Critères de Succès

- [ ] PR-UIDP-1 mergée : tsc 0 erreur, 131/131 tests pass, snapshot lock
- [ ] PR-UIDP-2 mergée : AST rule active, parity E2E 50/50 URLs,
      type 76550 vérifié (header == meta == `noindex, nofollow`)
- [ ] DEV preprod 48h sans erreur 5xx liée à seo
- [ ] PROD 7 jours sans régression Sentry / Grafana sur trafic catalog
- [ ] Aucune nouvelle émission directe de `robots` / `X-Robots-Tag`
      détectée par AST rule sur les 10 PRs suivantes

## Implémentation

**PR-UIDP-1** (~250 LOC + tests) — composer extraction + emitter helpers
- `packages/seo-role-contracts/src/robots-verdict.ts` (enums + types)
- `packages/seo-role-contracts/src/compose-indexability.ts` (pure cascade)
- `packages/seo-role-contracts/src/emit-robots.ts` (single emission point)
- `packages/seo-role-contracts/src/__fixtures__/indexability-snapshot.json`
  (50 inputs stratifiés INPUT-based — replay-safe)
- Tests `node:test` : 131/131 pass (52 cascade + 4 emit + 55 snapshot +
  20 existants)
- `backend/src/modules/seo/services/policies/seo-indexability-policy.service.ts`
  refactoré en thin wrapper (backward compat 100%)

**PR-UIDP-2** (~400 LOC + tests) — wire emitters + AST anti-bypass
- `frontend/app/utils/pieces-vehicle.loader.server.ts` (loader R2 émet
  `Response.headers['X-Robots-Tag']` + `data.robots`)
- `frontend/app/components/vehicle/r8/r8-transform.ts` (remplace hardcoded
  range par flag `tecdocReleaseGateOpen`)
- `backend/src/modules/seo/interceptors/seo-headers.interceptor.ts`
  (étend `delete X-Robots-Tag` aux `/constructeurs/*`)
- `.ast-grep/rules/seo-no-direct-robots-emission.yml` (3 patterns
  bloqués + whitelist explicite)
- Parity E2E test 50 URLs DEV preprod

## Sunset Plan (V2+, NON-engagé)

Documenté ici pour mémoire — **pas d'engagement de date** :

1. **TecDoc release gate** : remplacer `[60000, 83456]` hardcodé par
   colonne `tecdoc_release_status` (BOOL ou ENUM avec FK). Migration
   forward-only, gouvernée par ADR séparée.
2. **Legacy DB TEXT flags** : migrer `type_display`, `pg_display` de
   TEXT('1') vers BOOLEAN. Migration concurrent-safe (CREATE bool col +
   triggers sync + cutover atomique).
3. **Audit log persistant** : table `__seo_indexability_audit` (append-only,
   `verdict_kind`, `reason_codes`, `surface_payload_hash`, `computed_at`)
   pour replay/forensic — V1.5 evidence-gated.
4. **Split transport/representation** : `RobotsDirectiveSet` typé +
   `HttpEmitter` + `HtmlEmitter` séparés, quand les directives
   bot-specific (`nosnippet`, `max-image-preview`, `unavailable_after`)
   nécessitent une divergence légitime.

## Discipline d'expansion (gouvernance d'auto-régulation)

Toute future surface consommatrice (canonical, hreflang, schema.org,
sitemap inclusion, crawl directives) **qui voudra réutiliser ce
pattern** devra :

1. Ouvrir un ADR vault dédié référençant ADR-074 comme template
2. Définir son propre enum `XxxVerdictKind` + `ReasonCode` (PAS de
   réutilisation : chaque domaine son enum structurel)
3. Ajouter sa propre AST rule anti-bypass + ses émetteurs whitelisted
4. Inscrire ses chemins dans `ownership.yaml` + `runtime-topology.yaml`
5. Fournir un fixture snapshot INPUT-based

Ce point de friction structurel **prévient l'expansion incontrôlée**
(bind paths / emitters / contexts multipliés sans gouvernance).

## ReasonCode — discipline anti-explosion

`ReasonCode` est un **invariant structurel** de la cascade, PAS un
événement métier granulaire.

Critères d'admission stricts pour ajout futur :
- Représente une **branche de cascade décisionnelle** (étape produisant
  un `kind` distinct)
- PAS un sous-cas métier d'une branche existante
  (ex : `R2_GATE_FAIL_NO_IMAGE` serait du bruit ; les sub-reasons R2
  restent internes au verdict R2 et ne remontent pas dans
  `ReasonCode[]` de niveau supérieur)
- Tout ajout requiert un test d'invariant dédié + amendement ADR

Garde mécanique optionnelle V1.5+ : test conformance qui échoue si
l'enum dépasse N entrées sans amendement ADR.

---

## Self-review verdict: APPROVE

Checklist 8 items (cf. `feedback_vault_self_review_before_admin_merge`) :

1. ✅ **Statut clair** : `proposed`, daté 2026-05-18, decision_makers nommés
2. ✅ **Contexte chiffré** : 336 k pages (GSC), 5 colonnes DB + 7+ règles
   code + 1 range hardcodé identifiés
3. ✅ **Décision non-ambiguë** : 2 PRs scoped, fichiers nommés, cascade
   documentée, invariants enforced par test
4. ✅ **Options alternatives présentées** (B = bricolage, C =
   over-engineering) avec justification du rejet
5. ✅ **Conséquences positives ET négatives** explicitées (pas
   d'overclaim, cf. `feedback_no_overclaim_security_words`)
6. ✅ **Critères de succès mesurables** (5 checkboxes empiriques :
   tsc, tests, AST, DEV 48h, PROD 7j)
7. ✅ **Sunset path documenté** (V2+ NON-engagé, gated par ADRs futures)
8. ✅ **Discipline expansion + ReasonCode anti-explosion** documentées
   (auto-régulation gouvernance)

ADR prête pour admin-merge après validation @ak125.
