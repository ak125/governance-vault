---
id: ADR-058
title: Repository Control Plane — registry canonique 3 couches (data auto + overlay manuel + projection)
status: proposed
date: 2026-05-13
deciders: [Fafa]
decision_makers: [Fafa]
amended_by: ["ADR-097"]
related: [ADR-015, ADR-048, ADR-049, ADR-053, MOC-Decisions, MOC-Repository-Control-Plane]
---

# ADR-058 : Repository Control Plane — registry canonique 3 couches

## Context

ADR-048 (canon enforcement coverage, accepté 2026-05-07) a révélé que `.spec/00-canon/`
du monorepo `nestjs-remix-monorepo` est **77 % prose-only, zéro enforcement mécanique**
(3/35 fichiers seulement sont enforcés). ADR-049 (db-governance canon enforcement, accepté
2026-05-07) demande explicitement un `REG-002-canon-files.md` registry queryable, mais
limité au scope canon governance.

Le monorepo a atteint une taille (2112 source files, 1116 entrypoints runtime, 339
dead-code candidates, 15 cycles, 60 tables orphan-candidates, 8 domaines D1..D8) où
la **perte de connaissance structurelle** — qui possède quoi, ce qui est LIVE / LEGACY /
MORT — bloque cleanup, refactor et upgrade. Tout chantier classique tenté sans cette
couche prend des décisions à l'aveugle.

Les PRs d'audit récentes (monorepo PR #441 deep-inventory, PR #447 db-usage-map +
risk-register + cleanup-plan-by-domain) ont livré **6 JSON déterministes + 2 MD curés**
dans `audit/` — c'est ~70 % du chemin vers un Repository Control Plane. Les 30 % manquants :

1. **Schéma unifié registry** agrégeant les 6 JSON existants + ownership / status / risk
2. **Gates CI progressifs** (V1 livre 2 phases : warning → block-new ; block-all différé V2)
3. **LLM entrypoint queryable** indexant les 42 modules MD `.claude/knowledge/`
4. **Couche merge canonique générée** : auto + manuel couplés = SoT ; canonical = projection

## Decision

**Adopter un Repository Control Plane à 3 couches** :

### Layer 1 — Data auto-générée (jamais éditer à la main)
`audit/registry/{files,db,rpc,deps,runtime}.json` produits par 5 builders dans
`scripts/registry/` qui étendent les producteurs existants `scripts/audit/build-deep-inventory.js`
et `build-db-usage-map.js`. Schémas Zod versionnés dans `@repo/registry`.

### Layer 2 — Canon overlay (manuel, humain édite)
`.spec/00-canon/repository-registry/{ownership,domains,status-overrides,delete-policy}.yaml`
auto-dérivés initialement depuis `CODEOWNERS` + `agents/*/AGENTS.md` + `@repo/seo-roles`.

### Layer 3 — Canonical projection (générée, reproductible)
`audit/registry/canonical.json` = projection du couple Layer 1 + Layer 2.
**Jamais SoT primaire** — si elle diverge, on rebuild ; on ne l'édite jamais.

### Gates CI progressifs V1 (2 phases)
- **Phase 1 (warning-only)** : `registry-fresh.yml` détecte drift entre L1/L2 et L3, warn
- **Phase 2 (block-new)** : `registry-new-file-gate.yml` bloque toute PR introduisant un fichier
  sans owner+domain résolus dans `ownership.yaml` / `domains.yaml`

### LLM entrypoint
`.claude/knowledge/REPO_MAP.md` généré depuis `canonical.json` — extension du système
`.claude/knowledge/` existant, **pas de namespace parallèle** (`.spec/00-canon/LLM_REPO_MAP.md`
explicitement interdit, anti-duplication).

## SoT clarification

> **Règle invariante** : Source de vérité = **couple Layer 1 auto + Layer 2 overlay**.
> Layer 3 (`canonical.json`) est une **projection canonique générée**, jamais SoT primaire.
> Si la projection diverge des sources amont, on rebuild ; on ne l'édite jamais à la main.

Cf. memory `feedback_generated_artifact_is_projection_not_sot.md`.

## Invariants V1 (5 obligatoires)

**V1-1. Versioning de schéma (SemVer)** — Chaque entry porte `schemaVersion: '1.0.0'`.
Package `@repo/registry` versionne. Toute modification respecte SemVer.

**V1-2. Déterminisme strict** — Tous les `.json` triés par `id`, JSON.stringify 2-space,
newline final. Hash SHA-256 stable entre 2 runs. Test CI bloquant.

**V1-3. Classification jamais forcée** — `status: UNKNOWN`, `sourceConfidence: low|medium|high`,
RPC parse modes (`parsed/partially_parsed/unknown_signature`). Builders ne throw jamais.
Cf. memory `feedback_coverage_per_dimension_thresholds.md`.

**V1-4. Schema invariants (lint relationnel minimal)** — `validate-invariants.ts` V1 vérifie
4 invariants critiques :
- Unicité des `id` cross-registry
- `status: ARCHIVED` ⇒ `runtime: false`
- Aucun cycle dans `runtime.startup_order` (confirme dep-cruiser)
- Tout glob `ownership.yaml` résout ≥ 1 fichier existant

**V1-5. Tests round-trip Zod** — Pour chaque schema : 1 test valide + 1 test invalide.
`fast-check` étendu = V1.5.

## Schema evolution policy

Modifications du schema `@repo/registry` suivent SemVer strict :

- **Patch** (clarification, doc, typo) : aucune notice.
- **Minor** (ajout champ optionnel, nouvelle enum value backward-compat) : 30 jours
  notice via vault MOC + documentation dans `MOC-Repository-Control-Plane.md`.
- **Major** (champ obligatoire, enum value retirée, restructure) : ADR dédié + 60 jours
  sunset + migration scripts versionnés (`packages/registry/migrations/` introduit V1.5+).
  Les anciens canonical-vN.json restent lisibles via les migrations.

## Scope V1 / V1.5 / V2 (tiers explicites)

### V1 — Cœur obligatoire (ce plan, 8 PRs A→H)
- Registry 3 couches + overlay + projection canonique
- 2 gates CI (warn → block-new)
- LLM entrypoint REPO_MAP.md
- Acceptance ADR-058 après gate block-new + 7-14 jours signal vert

### V1.5 — Polish (plan séparé post-PR-H stable, hors scope ADR-058)
- Provenance per artifact (in-toto v0.1 sidecar)
- Diff PR comments
- JSON Schema export (zod-to-json-schema)
- Property-based testing étendu (fast-check ≥ 500 props)
- RefId URN format (`kind:domain:id`)
- Generated `.d.ts` complets
- Hermetic builders (NETWORK_BLOCK)
- Budget runtime + CI fail si dépassé
- classificationTrail per entry

### V2 — Platform Engineering complet (plan futur signal-proven, hors scope ADR-058)
- MCP server `@repo/registry-mcp` (5 tools : `registry_find_owner`, `registry_query`, etc.)
- SLSA L2 complet (signed provenance, builder isolation)
- Versioned canonical artifacts (`canonical-v2.json`)
- CI Phase 3 block-all

Cf. memory `feedback_v1_v1_5_v2_tiered_scoping.md` pour la discipline de tier scoping.

## Acceptance criteria

Status `proposed` → `accepted` après **PR-G mergée + 7-14 jours signal empirique vert** :

- `block-new` actif et 0 false-positive bloquant un PR légitime sur la fenêtre
- `registry_coverage_pct` (files inventory) = 100 %
- `ownership_coverage_pct` ≥ 90 %
- `ownership_high_confidence_pct` ≥ 70 %
- `status_known_pct` (non-`UNKNOWN`) ≥ 85 %
- `registry_orphan_count` stable ou décroissant

**Aucune dépendance MCP / V1.5 / V2.** Le Control Plane est jugé sur sa capacité à bloquer
les nouveaux fichiers sans owner+domain, point.

Pour activer V2 block-all (Phase 3), seuils plus stricts requis sur 30 jours consécutifs :
ownership ≥ 95 %, status-known ≥ 95 %, ownership high-confidence ≥ 80 %. Décision V2 hors
scope ADR-058 — fera l'objet d'un ADR dédié signal-proven.

## Consequences

### Positives
- Le monorepo devient auto-descriptif et auto-vérifiable
- Cleanup / refactor / upgrade peuvent commencer sur base de données fiables
- Les agents LLM lisent le registry avant grep (réduit drastique des explorations brouillonnes)
- Les nouveaux fichiers sans ownership sont mécaniquement refusés
- ADR-048 §risk drift silencieux est partiellement remédié pour `.spec/00-canon/` lié

### Négatives
- Coût d'entrée : 8 PRs sur ~3 semaines pour livrer V1
- Discipline scope obligatoire (cf. anti-patterns : ne pas activer V1.5/V2 par discipline)
- Maintenance ownership.yaml : ~30 entries glob à maintenir manuellement
- Risque de drift entre `.claude/knowledge/` prose et registry — atténué par `REPO_MAP.md`
  généré depuis canonical et anti-namespace-parallèle

### Risques mitigés
- **Scope creep V1 → Platform Engineering complet** : tier discipline V1/V1.5/V2 explicite
- **canonical.json édité à la main** : hook pre-commit refuse `git add` sauf reproductibilité
  prouvée (recompute hash, pas marker env forgeable). Cf. memory
  `feedback_hook_reproducibility_proof_over_env_marker.md`.
- **Forcer classification** : `status: UNKNOWN` + `sourceConfidence: low` autorisés, jamais
  inventer LEGACY/LIVE quand signal ambigu.

## Relation aux ADRs voisins

- **ADR-015** (Governance Vault — SoT) : ADR-058 vit dans le vault canon, conforme.
- **ADR-048** (canon enforcement coverage) : ADR-058 implémente une remédiation partielle
  via registry queryable (vs prose-only).
- **ADR-049** (DB governance canon enforcement) : ADR-058 élargit la portée de REG-002
  demandé par ADR-049 (canon files only) vers tout le monorepo (files / db / rpc / runtime).
  Relation `relates-to`, **pas `supersedes`**.
- **ADR-053** (Planning Live System) : ADR-058 réutilise le pattern « cron VPS DEV + MOC
  SoT + GH Project best-effort » pour la sync canonical.

## Plan d'exécution

Plan directeur détaillé : `/home/deploy/.claude/plans/verifier-la-vraie-logical-whistle.md`
(monorepo-side, scope V1 explicite).

Séquence PRs V1 : A (cette PR vault) → B (schemas `@repo/registry`) → C (5 builders Layer 1)
→ D (overlay Layer 2 YAML) → E (canonical merge + freshness CI warn) → F (REPO_MAP.md
LLM entrypoint) → G (CI block-new gate Phase 2) → H (vault PR : ADR-058 `proposed` →
`accepted`).

Cf. MOC `ops/moc/MOC-Repository-Control-Plane.md` (cette PR) pour suivi opérationnel.
