---
date: 2026-05-14
type: audit-trail
related: [ADR-062, ADR-015, ADR-031, ADR-039, ADR-047, ADR-048, ADR-053, ADR-058, ADR-060, ADR-061, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-14 — ADR-062 Repository Contract System meta-model (création accepted atomique)

## What

Création de **ADR-062 « Repository Contract System — meta-model (9 concepts canon) »** directement en `status: accepted` (decision_date 2026-05-14, signée @fafa, pattern atomique inauguré par ADR-059 + ADR-060 + ADR-061 les 2026-05-13).

L'ADR codifie :

- **2 Lois canoniques §0** opposables AVANT toute application des 9 concepts :
  - **Loi A — Origine canonique** : un contract peut être humain-édité, mais jamais dérivé d'un artifact qu'il est censé gouverner.
  - **Loi B — Représentations spécialisées** : une représentation dérivée peut être optimisée pour un consommateur spécifique (CI, IDE, runtime, doc), mais ne peut jamais devenir éditable comme source primaire.

- **9 concepts canon** : Contract (SoT humaine YAML/JSON/Markdown/TS) → Generator (déterministe, test SHA-256 round-trip obligatoire) → Derived artifact (projection régénérable) → Enforcement engine (config traçable à un contract) → Freshness gate (soumis au ratchet §6) → Ratchet (warn → block après signal empirique N=10 builds ou 7-14j) → Ownership (1 contract = 1 owner, ownership.yaml + CODEOWNERS) → SemVer (Patch/Minor/Major matrix) → Anti-parallel-truth (1 information canonique = 1 contract source, autre représentation = derived OU référence).

- **Formule canonique grepable** : *Contract gouverne, generator transforme, derived projete, engine applique, gate verrouille, ratchet promeut, owner valide, semver versionne, anti-parallel-truth proscrit la double SoT.*

- **Conformity criteria** : 9 points checklist obligatoire pour qu'un chantier soit dit *contract-system-conformant*.

- **Tiers de conformance (3+1 niveaux)** : `fully-conformant` (9/9 + ADR accepted) / `conformant candidate` (9/9 techniques mais ADR `proposed`) / `partial / governed-baseline` (≥5/9 + ownership OK) / `legacy non-conformant` (<5/9, déclenche ADR migration sous 60j).

- **Cross-contract dependencies** : frontmatter `depends_on:`, freshness cascade, anti-cycle.

- **Table classification existants** : Repository Control Plane (ADR-058) = `conformant candidate` (ADR-058 encore `proposed`) ; seo-role-contracts (ADR-047), Wiki frontmatter (ADR-039) = `fully-conformant` ; audit-baseline (ADR-048), dep-cruise (ADR-031) = `partial / governed-baseline`.

## Why

Au 2026-05-14, le monorepo dispose de **plusieurs contracts opérationnels** (registry ADR-058, audit-baseline #267/#449, dep-cruise ADR-031, seo-role-contracts ADR-047, wiki frontmatter ADR-039) mais **aucune doctrine canon** ne définit ce qu'est un contract ni quels invariants tout contract doit satisfaire. Conséquence directe : chaque chantier futur (PR-3 DB Contract en attente, futur API Contract, Schema Contract, Auth Contract) réinvente le vocabulaire et les gates, exposant l'écosystème à drift entre patterns, double SoT, ou cycles de dérivation circulaire.

Le canon de fait existe (memory `feedback_generated_artifact_is_projection_not_sot`, ADR-058 §SoT clarification) mais reste fragile sans canon ratifié (`feedback_canon_rule_live_iff_adr_accepted`). Un grep `repository contract system|contract meta-model|9 concepts` dans `ledger/decisions/adr/` au 2026-05-14 retourne 0 hit.

Motivation immédiate : **PR-3 DB Contract** (monorepo `nestjs-remix-monorepo`, branche `feat/architecture-contract-v1`) ne peut pas s'ouvrir tant que le cadre commun n'est pas formalisé — sinon elle réinvente ses propres conventions et expose le risque de scope creep vs futur API Contract / Schema Contract. Memory `architecture-contract-v1-pr-blockers-20260514` documentait ce blocker (« ADR Repository Contract System à créer »).

L'utilisateur a explicitement structuré l'ordre 2026-05-14 :
> 1. Finaliser/observer PR-2 [✅ PR #449 MERGED]
> 2. Créer ADR-061 [redirigé vers ADR-062 — conflit numéro résolu]
> 3. Faire accepter ADR-062
> 4. Ensuite seulement concevoir PR-3 DB Contract

## How

Création via PR vault `feat/adr-062-repository-contract-system-meta-model` (worktree isolé `/tmp/vault-adr-062` depuis `origin/main`) :

1. `ledger/decisions/adr/ADR-062-repository-contract-system-meta-model.md` : créé directement en `status: accepted`, `decision_date: 2026-05-14`. Frontmatter `related_adr: [ADR-015, ADR-031, ADR-039, ADR-047, ADR-048, ADR-053, ADR-058, ADR-060, ADR-061]` (ADR-054 référencée en texte inline car PR vault #242 non encore mergée).
2. `ops/moc/MOC-Decisions.md` : ligne ADR-062 ajoutée en `Accepted` (section « ADR Actifs » détaillée + section auto-générée).
3. Ce fichier audit-trail créé.
4. `ops/moc/MOC-AuditTrail.md` : entrée ajoutée pour audit-trail file linkage.

**Self-review checklist 10 items** (extension `feedback_vault_self_review_before_admin_merge`) :

- [x] G3 (signed) : commit signé `vault-signing@automecanik.com`
- [x] Frontmatter complet (id, title, status, date, decision_date, decision_makers, related_*)
- [x] Numérotation ADR-062 unique (vérifié `ls ledger/decisions/adr/ | grep ADR-062 | wc -l == 1`)
- [x] MOC-Decisions cohérent (2 sections : manuelle + auto-générée)
- [x] MOC-AuditTrail entry ligne ajoutée
- [x] G2 (zero orphan) : `./scripts/check-orphans.sh .` → `No orphans found`
- [x] Aucune référence à fichier monorepo non existant
- [x] G1 (canon LIVE iff accepted) : conformité G2 + G3 verts → `status: accepted` légitime
- [x] G5 (canon authoritative) : ADR-062 référencée par MOC-Decisions, aucune duplication hors-vault
- [x] Verdict self-review : **APPROVE**

**Aucune modification** des autres ADRs, ni des 5 instances classifiées (ADR-058, ADR-047, ADR-039, ADR-048, ADR-031) — la classification est descriptive, pas normative-rétroactive. Audit des contracts existants vs Conformity criteria 9 points sera un sous-projet PR monorepo distinct si gaps détectés.

## Conflit numérotation résolu

L'utilisateur a écrit dans son ordre 2026-05-14 :
> `governance-vault/ledger/decisions/adr/ADR-061-repository-contract-system-meta-model.md`

Or **ADR-061 était déjà pris** par [[ADR-061-workspace-governance]] (accepted 2026-05-13). Per `feedback_verify_existing_first` (« GREP racine avant inventer ») + memory `architecture-contract-v1-pr-blockers-20260514` (qui documentait déjà ce mismatch), le nouveau ADR a été numéroté **ADR-062** (prochain disponible). Notification au user dans plan local + ce fichier audit-trail.

## What changes downstream

Avec `ADR-062.status == "accepted"` mergée sur `governance-vault/main` :

- **Canon LIVE** : le meta-model devient canon courant. Toute violation future (contract dérivé d'un derived artifact, derived édité comme SoT, generator non-déterministe sans test SHA-256, freshness gate démarrant blocking, schema sans SemVer, contract sans ownership) est régression.
- **PR-3 DB Contract** (monorepo, branche `feat/architecture-contract-v1`) **débloquée** : peut s'ouvrir et doit livrer la table Conformity criteria 9 points en checklist self-review. Gate explicite user : *merge effectif* ADR-062 sur `governance-vault/main` requis avant `gh pr create` PR-3 (pas « PR ouverte » ni « PR approuvée mais non mergée »).
- **ADR-058 Repository Control Plane** : reclassifiable de `conformant candidate` à `fully-conformant` dès `proposed → accepted` (signal CI empirique 7-14j sur Phase 2 block-new attendu).
- **Sous-projets cohérents** :
  - Audit conformity 5 instances classifiées : vérifier conformité 9/9 et plan migration pour `partial / governed-baseline`. PR monorepo si gaps.
  - Futurs contracts (API Contract, Schema Contract, Auth Contract, …) : checklist 9 points + Lois A/B opposables dès draft initial.
- **Memory `architecture-contract-v1-pr-blockers-20260514`** : blocker #3 « ADR-061 scope mismatch » marqué résolu post-merge (mise à jour memory dans session post-merge).

Aucune modification de runtime, hooks, ou code requise par cette ratification — la doctrine est déclarative.

## Refs

- [ADR-062](../decisions/adr/ADR-062-repository-contract-system-meta-model.md) (accepted 2026-05-14)
- [ADR-061](../decisions/adr/ADR-061-workspace-governance.md) (Workspace Governance, ratifiée 2026-05-13 — explique pourquoi ADR-062 et non ADR-061)
- [ADR-060](../decisions/adr/ADR-060-repository-roles-doctrine.md) (doctrine repository roles, pattern atomique accepted parent)
- [ADR-058](../decisions/adr/ADR-058-repository-control-plane.md) (Repository Control Plane monorepo, classifié `conformant candidate`)
- ADR-054 audit-trail convention SoT (PR vault #242 en cours au 2026-05-14, non encore mergée — référence textuelle)
- [ADR-047](../decisions/adr/ADR-047-seo-role-contracts-as-code.md) (seo-role-contracts, classifié `fully-conformant`)
- [ADR-039](../decisions/adr/ADR-039-wiki-frontmatter-zod-canon.md) (wiki frontmatter v1.0.0, classifié `fully-conformant`)
- Plan local : `/home/deploy/.claude/plans/quiet-enchanting-ullman.md`
- Memory : `feedback_canon_rule_live_iff_adr_accepted`, `feedback_no_questionnaire_propose_best`, `feedback_verify_existing_first`, `architecture-contract-v1-pr-blockers-20260514`, `feedback_auto_vault_audit_trail_on_adr`, `pr-3b-promotion-trigger-20260512`, `cross-repo-and-governance-discipline`
