---
id: ADR-062
title: "Repository Contract System — meta-model (9 concepts canon)"
status: accepted
date: 2026-05-14
decision_date: 2026-05-14
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "G5"]
related_incidents: []
related_adr: ["ADR-015", "ADR-031", "ADR-039", "ADR-047", "ADR-048", "ADR-053", "ADR-058", "ADR-060", "ADR-061"]
---

# ADR-062 : Repository Contract System — meta-model (9 concepts canon)

## Formule canonique grepable

> **Contract gouverne, generator transforme, derived projete, engine applique, gate verrouille, ratchet promeut, owner valide, semver versionne, anti-parallel-truth proscrit la double SoT.**

Cette formule littérale est l'invariant cité par les agents et contributeurs nouveaux. Elle est répétée intentionnellement pour faciliter recherche et grep (pattern [[ADR-060-repository-roles-doctrine]]).

## §0 Lois canoniques d'origine (anti-bricolage top-level)

Deux lois fondamentales **préfacent et conditionnent** les 9 concepts ci-après. Toute exception nécessite un ADR dédié.

> **Loi A — Origine canonique** : Un contract peut être humain-édité, mais jamais dérivé d'un artifact qu'il est censé gouverner.

> **Loi B — Représentations spécialisées** : Une représentation dérivée peut être optimisée pour un consommateur spécifique (CI, IDE, runtime, documentation), mais ne peut jamais devenir éditable comme source primaire.

La **Loi A** verrouille les dérivations circulaires (« on régénère le contract depuis le derived artifact »). La **Loi B** verrouille les patches in-place sur derived artifacts (« on édite directement le generated JSON », « on patch le cache », « on modifie le projection snapshot »). Tout fix doit remonter au contract source ; toute optimisation par-consommateur reste read-only et regénérable.

## Context

L'écosystème AutoMecanik dispose déjà de plusieurs **contracts opérationnels** :

- `@repo/registry` schemas Zod versionnés ([[ADR-058-repository-control-plane]] Layer 1+2+3)
- `audit-reports/phase0-baseline.json` + comparator ratchet ([PR #267 audit-baseline-refresh](https://github.com/ak125/nestjs-remix-monorepo/pull/267), [PR #449 ratchet guardrails](https://github.com/ak125/nestjs-remix-monorepo/pull/449))
- `.dependency-cruiser.cjs` rules + Phase 1/1bis trajectory ([[ADR-031-four-layer-content-architecture]])
- `packages/seo-role-contracts/` ([[ADR-047-seo-role-contracts-as-code]])
- Wiki frontmatter Zod schema v1.0.0 ([[ADR-039-wiki-frontmatter-zod-canon]])

**Mais aucune doctrine canon ne définit *ce qu'est un contract* ni *quels invariants tout contract doit satisfaire*.** Conséquence : chaque chantier futur (DB Contract, API Contract, Schema Contract, Auth Contract, …) **réinvente le vocabulaire et les gates**, avec risque de drift entre patterns, double SoT, ou cycles de dérivation.

Au 2026-05-14, un grep `repository contract system|contract meta-model|9 concepts` dans `ledger/decisions/adr/` retourne 0 hit. Le canon de fait existe (`feedback_generated_artifact_is_projection_not_sot`, ADR-058 §SoT clarification) mais reste **fragile sans canon ratifié** (`feedback_canon_rule_live_iff_adr_accepted`).

**Motivation immédiate** : PR-3 DB Contract (monorepo `nestjs-remix-monorepo`, branche `feat/architecture-contract-v1`) ne peut pas s'ouvrir tant que le cadre commun n'est pas formalisé — sinon elle réinvente ses propres conventions et expose le risque de scope creep vs futur API Contract / Schema Contract.

## Decision

**Adopter le Repository Contract System meta-model à 9 concepts**, conditionné par les 2 Lois §0, comme cadre commun obligatoire opposable à tout contract présent ou futur dans l'écosystème AutoMecanik (monorepo `nestjs-remix-monorepo`, vault `governance-vault`, wiki `automecanik-wiki`, raw `automecanik-raw`, rag `automecanik-rag`).

### Les 9 concepts canon

#### 1. Contract — SoT humaine

**Définition** : artefact **YAML / JSON / Markdown / TypeScript contractuel** édité par humain, sous CODEOWNERS, qui *décrit l'intention canonique*. Jamais auto-généré. Versionné SemVer. Localisé sous `.spec/00-canon/<domain>-contract/` ou équivalent canon de l'écosystème (vault `ledger/`, wiki frontmatter, package `packages/*-contracts/`).

**Invariant grepable** :
> *Un contract est éditable à la main et signé G3 ou via PR humaine validée.*

**Application des Lois §0** : Loi A directement (contract = source primaire humain-éditée, jamais dérivée).

**Instances canon** :
- `.spec/00-canon/repository-registry/{ownership,domains,status-overrides,delete-policy}.yaml` (ADR-058 Layer 2)
- `packages/seo-role-contracts/src/contracts/*.ts` (ADR-047)
- Wiki frontmatter v1.0.0 schema (ADR-039)
- *Futur* : `.spec/00-canon/db-architecture.contract.json` (PR-3 monorepo, post-merge ADR-062)

**Anti-pattern** : générer le contract depuis un script tooling qui lit le derived artifact à canoniser — dérivation circulaire (parallel-truth, viole Loi A), pas un contract.

#### 2. Generator — transformateur déterministe

**Définition** : programme reproductible qui consomme un ou plusieurs contracts (+ optionnellement des données auto Layer 1) et produit un ou plusieurs derived artifacts. **Hermétique idéalement, déterministe obligatoirement.**

**Invariant grepable** :
> *Deux runs successifs d'un generator sur les mêmes entrées produisent un hash SHA-256 identique.*

**Obligation de test** : tout generator doit ship **1 test round-trip SHA-256 obligatoire** (input contract → generator → output → re-run → hash égal). Pattern ADR-058 §V1-5 (tests round-trip Zod). Sans ce test, generator considéré non-conformant (cf. §Tiers de conformance).

**Instances canon** :
- `scripts/registry/build-canonical.js` (ADR-058 Layer 3 projection)
- `scripts/audit/build-deep-inventory.js` (Layer 1 inventory)
- `scripts/audit/build-db-usage-map.js` (Layer 1 db)

**Anti-pattern** : generator qui dépend de `Date.now()`, ordre filesystem non-trié, network sans pin, ou état mutable cross-runs. Bench : si `git diff` après second run est non-vide pour mêmes inputs, generator est non-déterministe.

#### 3. Derived artifact — projection canonique générée

**Définition** : fichier produit par un generator à partir d'un contract. **Jamais SoT primaire.** Régénérable à tout moment. Peut être committé (artifact reproductibility-checked en CI) ou éphémère (artifact CI-only, non-committé).

**Invariant grepable** :
> *Si la projection diverge de ses sources, on rebuild — on ne l'édite jamais à la main.*

**Application des Lois §0** : Loi B directement (derived = représentation spécialisée, never source primaire).

**Instances canon** :
- `audit/registry/canonical.json` (ADR-058 §SoT clarification)
- `.claude/knowledge/REPO_MAP.md` (généré, pre-commit hook `refresh-knowledge.py`)
- `automecanik-wiki/exports/seo/<entity_type>/<slug>.json` (ADR-059)

**Anti-pattern** : éditer manuellement un derived artifact pour patcher un bug — symptôme = contract incomplet, le fix doit remonter au contract source (viole Loi B).

#### 4. Enforcement engine — exécuteur de règles

**Définition** : outil tiers (dep-cruise, ast-grep, jq, Zod schema validators, eslint, SQL linters, sqlfluff, OPA, …) invoqué en CI ou pre-commit qui vérifie qu'un état de code/data satisfait une règle. Configuration **traçable à un contract canon**.

**Invariant grepable** :
> *L'enforcement engine ne décide pas — il applique. Sa configuration doit être traçable à un contract canon (ADR, rule vault, schema versionné).*

**Instances canon** :
- `dep-cruise` rules (`.dependency-cruiser.cjs` configuré depuis `.spec/00-canon/dependency-rules.md`)
- `ast-grep` rules (`.ast-grep/rules/*.yml` configurées depuis ADRs + `feedback_*` memories, ex. `backend-no-remote-io-in-onmoduleinit.yml`)
- `validate-invariants.ts` (ADR-058 §V1-4, 4 invariants relationnels)
- Zod schemas `@repo/registry`, `@repo/seo-role-contracts`

**Anti-pattern** : enforcement engine avec règles hardcodées dans son code source au lieu de chargées depuis un contract. Si la règle évolue, le code change → pas de traçabilité ADR.

#### 5. Freshness gate — verrou anti-drift

**Définition** : workflow CI ou pre-commit hook qui vérifie que le derived artifact committé correspond bien à une régénération from-scratch du generator sur les contracts courants. Échec = artifact stale.

**Invariant grepable** :
> *Une PR qui modifie un contract sans régénérer ses derived artifacts est détectée par le freshness gate.*

**Soumis au ratchet §6** : tout freshness gate démarre en mode **warn-only** (`continue-on-error: true` explicite et borné dans le temps), puis est promu au mode **blocking** (rejet PR) après observation empirique conforme aux critères de promotion §6 (typiquement N=10 builds verts consécutifs ou 7-14 jours sans faux-positif). Lève l'apparente contradiction avec §6 : un gate *peut* être blocking, mais jamais dès la création.

**Instances canon** :
- `.github/workflows/registry-build.yml` Phase 1 freshness warn (ADR-058)
- `.github/workflows/registry-build.yml` Phase 2 block-new (ADR-058, ratchet promu)
- Pre-commit `scripts/knowledge/refresh-knowledge.py` (Knowledge Layer `.claude/knowledge/modules/*.md`)
- `.husky/pre-commit` ast-grep `backend-no-remote-io-in-onmoduleinit` (CLAUDE.md §Non-blocking onModuleInit)

**Anti-pattern** : freshness gate désactivé silencieusement (`continue-on-error: true`) en permanence sans trajectoire ratchet documentée. Autorisé seulement pendant fenêtre warn→error explicite avec date de promotion cible.

#### 6. Ratchet — promotion warn → block

**Définition** : trajectoire formelle d'une règle d'enforcement *du mode warn-only au mode blocking*, conditionnée par observation empirique (0 régression sur fenêtre N=7-14 jours, N=10 builds verts consécutifs typiquement).

**Invariant grepable** :
> *Aucune règle nouvelle ne démarre bloquante ; aucune règle ne reste warn-only au-delà de sa fenêtre de promotion sans ADR de dérogation.*

**Instances canon** :
- Audit-baseline ratchet : PR #267 (PR-1 refresh script) + PR #449 (PR-2 warn-on-regression) + PR-3b promotion 2026-05-28 (warn → blocking)
- Dep-cruise Phase 1/1bis (ADR-031)
- Repository Control Plane Phase 1→Phase 2 (ADR-058 §Gates CI progressifs V1)

**Anti-pattern** : promotion warn→block sans signal empirique ou « pour aller plus vite ». Cf. `pr-3b-promotion-trigger-20260512` memory : tout ratchet a une date trigger explicite + critères de promotion documentés.

#### 7. Ownership — qui valide quoi

**Définition** : mapping explicite `<contract path glob> → <owner team/person>` versionné dans un contract dédié (canon : `.spec/00-canon/repository-registry/ownership.yaml` ADR-058 Layer 2 + `.github/CODEOWNERS`). **Chaque contract a un et un seul owner principal.**

**Invariant grepable** :
> *Toute PR touchant un contract requiert review approuvée par son owner ; toute PR créant un nouveau fichier sans ownership résolu est bloquée (ADR-058 Phase 2 block-new gate).*

**Instances canon** :
- `.github/CODEOWNERS` (monorepo)
- `.spec/00-canon/repository-registry/ownership.yaml` (ADR-058 Layer 2)
- `agents/*/AGENTS.md` ownership des agents Paperclip (ADR-013)
- `governance-vault/.github/CODEOWNERS` (vault)

**Anti-pattern** : « tout le monde owne tout » ou contract sans owner explicite. Statut `ownership: unresolved` autorisé temporairement avec ADR de dérogation + date de résolution cible.

#### 8. Semver — évolution versionnée

**Définition** : tout schema de contract porte `schemaVersion: 'MAJOR.MINOR.PATCH'`. Modifications suivent SemVer strict avec policy de communication.

**Invariant grepable** :
> *Patch = clarification, aucune notice. Minor = ajout champ optionnel ou enum value backward-compat, 30 jours notice via MOC. Major = champ obligatoire ou enum value retirée ou restructure, ADR dédié + 60 jours sunset + migration scripts versionnés.*

**Instances canon** :
- `@repo/registry` (ADR-058 §V1-1 + §Schema evolution policy)
- `packages/seo-role-contracts` (ADR-047)
- Wiki frontmatter v1.0.0 (ADR-039)

**Anti-pattern** : modifier un schema en place sans bump SemVer, ou « breaking change discreto » sans ADR major + sunset. Cf. ADR-058 §Schema evolution policy pour la matrice complète.

#### 9. Anti-parallel-truth — interdiction des doubles SoT

**Définition** : pour toute information canonique, il existe **un et un seul** contract source. Toute autre représentation est soit un derived artifact (généré) soit une référence (lien). Dupliquer un contract dans 2 emplacements = régression.

**Invariant grepable** :
> *Si grep retourne 2 fichiers contenant la même règle/schema/définition canonique, l'un des deux doit être généré OU supprimé. CI guard bloque la création d'un fichier qui duplique un canon existant.*

**Application des Lois §0** : Loi B directement (représentations spécialisées toujours read-only, jamais SoT primaire).

**Instances canon** :
- `feedback_generated_artifact_is_projection_not_sot` (canon memory rule)
- ADR-058 §SoT clarification (Layer 3 canonical.json never primary)
- `.claude/knowledge/` anti-namespace-parallèle (REPO_MAP.md généré, jamais édité)
- CLAUDE.md monorepo pointer-only vers vault (zéro duplication gouvernance)

**Anti-pattern** : « j'ai écrit une rule dans `.spec/` *et* aussi dans `docs/` *et* aussi dans le README pour qu'elle soit visible. » Une seule SoT, le reste linke. Cf. memory `cross-repo-and-governance-discipline`.

### Conformity criteria (annexe normative)

Pour qu'un futur chantier soit dit **contract-system-conformant**, il doit livrer la table suivante en checklist self-review de PR :

| # | Critère | Preuve attendue |
|---|---|---|
| 1 | Contract identifié | Path canon + frontmatter `schemaVersion` + owner CODEOWNERS |
| 2 | Generator identifié | Path script + déterminisme prouvé par test SHA-256 round-trip |
| 3 | Derived artifact identifié | Path + commit OR éphémère + freshness gate associé |
| 4 | Enforcement engine identifié | dep-cruise / ast-grep / Zod / SQL lint / autre + règle traçable au contract |
| 5 | Freshness gate identifié | Workflow CI ou pre-commit hook nommé, soumis au ratchet |
| 6 | Trajectoire ratchet | Warn-only initial + critères promotion documentés + date trigger |
| 7 | Ownership résolu | `ownership.yaml` glob + CODEOWNERS |
| 8 | SchemaVersion SemVer | + politique d'évolution alignée §Semver |
| 9 | Anti-parallel-truth check | Grep prouvant zéro double SoT + respect Lois A/B §0 |

### Tiers de conformance (3+1 niveaux)

Toute instance existante ou future est classée selon :

| Tier | Critère | Exemples au 2026-05-14 |
|---|---|---|
| **`fully-conformant`** | 9/9 points + Lois A/B respectées + test round-trip SHA-256 vert + ADR de référence `accepted` | seo-role-contracts (ADR-047 accepted), wiki frontmatter (ADR-039 accepted) |
| **`conformant candidate`** | 9/9 points techniques + Lois A/B respectées, mais ADR de référence encore `proposed` ou signal empirique non observé | Repository Control Plane (ADR-058 governed, `proposed` au 2026-05-14) — promotion automatique à `fully-conformant` après ADR-058 accepted |
| **`partial / governed-baseline`** | ≥5/9 points + ownership résolu + pas de violation Lois A/B | Audit baseline (`audit-reports/phase0-baseline.json` — gouverné par maintainer, mais contract et derived mélangés) |
| **`legacy non-conformant`** | <5/9 points OU violation Lois A/B | Tout fichier `.spec/` prose-only sans engine (ADR-048 §risk silencieux). Migration via sous-projet audit conformity. |

Les instances `partial / governed-baseline` ne sont **pas** régressions — elles sont reconnues comme pré-existantes et candidates à migration progressive. Statut `legacy non-conformant` doit déclencher un ADR de plan de migration sous 60 jours.

### Cross-contract dependencies

Un contract peut **dépendre** d'un autre. Exemple : `db-architecture.contract.json` (PR-3 monorepo) dépendra de `ownership.yaml` (ADR-058) pour la résolution `owner_team` par schéma DB.

**Convention** : frontmatter contract porte un champ `depends_on:` listant les paths absolus ou IDs des contracts amont :

```yaml
schemaVersion: "1.0.0"
depends_on:
  - .spec/00-canon/repository-registry/ownership.yaml
  - .spec/00-canon/repository-registry/domains.yaml
```

**Conséquence freshness gate** : modification d'un contract amont déclenche freshness check cascade sur tous contracts qui le `depends_on`. Implémentation au niveau du freshness gate de chaque contract aval (responsabilité partagée).

**Anti-pattern** : cycle de dépendance entre contracts. Si A `depends_on` B et B `depends_on` A, l'un des deux doit être splitté. CI guard détecte les cycles (réutilise pattern dep-cruise §V1-4 d'ADR-058 : « Aucun cycle dans `runtime.startup_order` »).

## Instances existantes (annexe descriptive)

Table de conformance des contracts opérationnels au 2026-05-14 :

| Instance | Tier | Contract | Generator | Derived | Engine | Freshness | Ratchet | Owner | SemVer | Anti-// |
|---|---|---|---|---|---|---|---|---|---|---|
| Repository Control Plane (ADR-058) | **conformant candidate** (ADR-058 `proposed`) | `.spec/00-canon/repository-registry/*.yaml` | `scripts/registry/*.js` | `audit/registry/canonical.json` | `validate-invariants.ts` + Zod | `registry-build.yml` | Phase 1→2 (warn→block-new) | `ownership.yaml` | `@repo/registry` v1.0.0 | §SoT clarification |
| seo-role-contracts (ADR-047) | **fully-conformant** | `packages/seo-role-contracts/src/contracts/*.ts` | (Zod inferred) | runtime validators | Zod | `boundary` package | déjà LIVE | @fafa | package.json semver | aucune dup |
| Wiki frontmatter (ADR-039) | **fully-conformant** | wiki frontmatter Zod schema | `wiki-validate` | validation report | Zod + custom | wiki CI | déjà LIVE | wiki owner | v1.0.0 | aucune dup |
| Audit baseline (ADR-048, PR #267+#449) | **partial / governed-baseline** | `audit-reports/phase0-baseline.json` (mêle contract + notes humaines) | `scripts/cleanup/audit-compare-baseline.js` | comparator output JSON | knip + madge + depcruise | `audit.yml` warn | PR-3b promotion 2026-05-28 | maintainer-only | baseline JSON v? | `feedback_audit_baseline_needs_npm_ci` |
| Dep-cruise rules (ADR-031) | **partial / governed-baseline** | `.dependency-cruiser.cjs` + prose | dep-cruise CLI | violations report | dep-cruise | CI Phase 1/1bis | déjà ratchet partiel | @fafa | rule file v? | aucune dup |

## Options considérées

### Option A — Statu quo, doctrine implicite (rejetée)

Continuer sans canon ratifié, laisser chaque chantier réinventer.

**Inconvénients** : drift vocabulary entre PR-3 DB Contract, futur API Contract, Schema Contract ; risque de cycles de dérivation circulaire ; chaque agent réimprovise les Lois A/B à partir de memories éparses ; canon de fait fragile (`feedback_canon_rule_live_iff_adr_accepted`).

### Option B — Étendre ADR-058 (rejetée)

Bundle le meta-model dans ADR-058 (Repository Control Plane).

**Inconvénients** : viole le pattern « une ADR = une décision ». ADR-058 traite de la **cartographie d'un repo** (registry 3-couches du monorepo), pas du **méta-cadre des contracts**. Mélanger les deux concerns rend l'évolution future plus difficile ; complique les cross-references depuis ADRs futurs ; ADR-058 reste `proposed` (signal CI en attente) → couplerait la promotion du meta-model à un gate empirique non nécessaire.

### Option C — Méta-ADR « Repository Operating Plane » bundlée (rejetée)

Bundle doctrine repository roles (ADR-060) + Workspace Governance (ADR-061) + Repository Control Plane (ADR-058) + meta-model en une seule ADR géante.

**Inconvénients** : anti-pattern ADR (bundle). Duplique 3 ADRs existantes. Force ratification couplée de décisions qui doivent évoluer indépendamment.

### Option D — Nouvel ADR-062 meta-model pur (chosen)

Une ADR dédiée au meta-model, sans bundle, sans amendement. Pattern aligné avec ADR-058 / ADR-059 / ADR-060 / ADR-061 (concern unique chacune).

**Avantages** :
- Concern unique, ratification atomique légitime
- Cross-références faciles depuis ADR-058 (instances), ADR-047 (instances), ADR-039 (instances), futurs ADRs DB Contract / API Contract
- Évolution indépendante possible (futur amendement Lois A/B sans toucher Control Plane)
- Lecture rapide pour agents et contributeurs (1 page = 1 doctrine grepable)
- **Débloque PR-3 DB Contract** côté monorepo (gate explicite user 2026-05-14)

## Conséquences

### Positives

- Doctrine ratifiée → `feedback_canon_rule_live_iff_adr_accepted` satisfaite, canon LIVE
- Vocabulaire commun figé pour tous contracts présents et futurs (DB, API, Schema, Auth, …)
- Anti-bricolage explicite (Lois A/B §0) : verrouille mécaniquement dérivations circulaires + patches in-place sur derived
- Tiers de conformance permettent d'auditer existant sans déclasser brutalement (`conformant candidate` pour ADR-058)
- Cross-contract dependencies formalisées → freshness cascade prévisible
- **Débloque PR-3 DB Contract** : 1ʳᵉ instance _explicitement_ structurée selon meta-model

### Négatives / Coûts

- 1 ADR de plus dans le ledger (compensé par lisibilité accrue et grepabilité)
- Obligation de test round-trip SHA-256 pour tout futur generator (~30 min de dev par generator, amorti par CI gain)
- Auto-classification des contracts existants → ADR-058 obtient `conformant candidate` (pas `fully-conformant`), incite à pousser ADR-058 vers `accepted`
- PR-3 DB Contract devra inclure la table de conformité §Conformity criteria en checklist self-review

### Neutres

- ADR-058 / ADR-047 / ADR-039 / ADR-031 inchangées dans le body — l'ADR-062 les classifie sans les modifier
- Aucune modification monorepo, wiki, raw, rag, workspaces dans cette PR vault
- Aucun changement de runtime, hooks, ou code requise par cette ratification — la doctrine est déclarative

## Conformité règles vault

- **G1 (Canon LIVE iff accepted)** : ADR-062 créée directement en `status: accepted` (pattern atomique ADR-059 / ADR-060 / ADR-061 du 2026-05-13). Conformité G2 + G3 vérifiée pré-merge (cf. self-review checklist 10 items audit-trail).
- **G2 (Zéro orphelin)** : MOC-Decisions ligne ADR-062 ajoutée dans la même PR (2 sections : manuelle + auto-générée). MOC-AuditTrail entry ajoutée. `./scripts/check-orphans.sh .` doit retourner `No orphans found`.
- **G3 (Signed commits)** : commit signé via clé `vault-signing@automecanik.com`.
- **G5 (Canon authoritative)** : ADR-062 référencée par MOC-Decisions post-merge. Aucune duplication de la doctrine hors-vault (anti-parallel-truth meta-application).

## Mise en œuvre

ADR-062 créée directement en `status: accepted` (pattern atomique [[ADR-059-seo-runtime-projection]] / [[ADR-060-repository-roles-doctrine]] / [[ADR-061-workspace-governance]] des 2026-05-13/14). Aucune cascade d'implémentation requise — la doctrine est déclarative, ses conséquences (PR-3 DB Contract conformant, futurs contracts conformants) sont des sous-projets futurs avec leurs propres ADRs et PRs.

**Conflit numérotation résolu** : user avait proposé « ADR-061 » dans son ordre 2026-05-14 ; ADR-061 déjà pris par Workspace Governance (accepted 2026-05-13). Redirection vers ADR-062 (prochain disponible) documentée en audit-trail.

Audit-trail vault créée dans la même PR (`ledger/audit-trail/2026-05-14-adr-062-repository-contract-system-meta-model.md`) conformément à `feedback_auto_vault_audit_trail_on_adr` (ADR-054 SoT).

## Downstream unblocked

Avec `ADR-062.status == "accepted"` mergée sur `governance-vault/main` :

- **PR-3 DB Contract** (monorepo `nestjs-remix-monorepo`, branche `feat/architecture-contract-v1`) peut s'ouvrir, structurée explicitement selon le meta-model (1ʳᵉ instance _explicitement_ contract-system-conformant).
- **ADR-058 Repository Control Plane** : reclassifiable en `fully-conformant` dès `proposed → accepted` (signal CI empirique 7-14j sur Phase 2 block-new attendu).
- **Audit conformity sub-project** : sous-projet futur pour migrer `partial / governed-baseline` (audit baseline, dep-cruise) vers `fully-conformant` via PRs dédiées.
- **Futurs contracts** (API Contract, Schema Contract, Auth Contract, …) : checklist 9 points + Lois A/B opposables dès draft initial.

## Références

- [[ADR-015-vault-single-source-of-truth]]
- [[ADR-031-four-layer-content-architecture]]
- [[ADR-039-wiki-frontmatter-zod-canon]]
- [[ADR-047-seo-role-contracts-as-code]]
- [[ADR-048-canon-enforcement-coverage]]
- [[ADR-053-planning-live-system]]
- ADR-054 audit-trail convention (PR vault #242 en cours au 2026-05-14)
- [[ADR-058-repository-control-plane]]
- [[ADR-060-repository-roles-doctrine]]
- [[ADR-061-workspace-governance]]
- [[MOC-Decisions]]
- Memory : `feedback_generated_artifact_is_projection_not_sot`, `feedback_canon_rule_live_iff_adr_accepted`, `feedback_auto_vault_audit_trail_on_adr`, `feedback_no_questionnaire_propose_best`, `feedback_verify_existing_first`, `pr-3b-promotion-trigger-20260512`
- Plan local : `/home/deploy/.claude/plans/quiet-enchanting-ullman.md` (session 2026-05-14)
