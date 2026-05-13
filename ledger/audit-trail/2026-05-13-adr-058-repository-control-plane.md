---
date: 2026-05-13
type: audit-trail
related: [ADR-058, ADR-015, ADR-048, ADR-049, ADR-053, MOC-Decisions, MOC-AuditTrail, MOC-Repository-Control-Plane]
---

# 2026-05-13 — ADR-058 Repository Control Plane V1

## What

Ouverture ADR-058 dans [[MOC-Decisions]] pour formaliser un Repository Control
Plane V1 sur le monorepo `nestjs-remix-monorepo` : registry canonique
machine-readable couvrant files / db / rpc / runtime / dependencies / ownership,
avec CI gates progressifs (Phase 1 freshness warning-only → Phase 2 block-new
BLOQUANT).

L'ADR définit :

- **D1** : architecture 3 couches — Layer 1 auto (`audit/registry/*.json` produits
  par 5 builders Node.js déterministes) + Layer 2 overlay manuel
  (`.spec/00-canon/repository-registry/*.yaml`) + Layer 3 projection canonique
  générée (`canonical.json`).
- **D2** : SoT = couple Layer 1 + Layer 2 (jamais Layer 3 ; projection
  reproductible depuis sources amont).
- **D3** : 5 invariants V1 (SemVer schema, déterminisme strict, classification
  jamais forcée via `UNKNOWN` + `sourceConfidence`, 4 invariants relationnels
  minimaux, tests round-trip Zod).
- **D4** : DomainIdSchema D1..D15 + UNKNOWN aligné `db-governance/domain-map.md`
  v1.4.2.
- **D5** : CI Phase 1 freshness (warn-only, `continue-on-error`) + Phase 2
  block-new BLOQUANT (refuse tout nouveau fichier sans owner + domain résolus).
  Phase 3 block-all explicitement différée V2.
- **D6** : LLM entrypoint `.claude/knowledge/REPO_MAP.md` (généré, do_not_edit),
  CLAUDE.md step 0 = lire registry AVANT grep. Anti-namespace-parallèle :
  pas de `.spec/00-canon/LLM_REPO_MAP.md`.
- **D7** : tier scoping V1 / V1.5 / V2 strict — V1 livre 6 PRs monorepo +
  1 vault, V1.5 (provenance in-toto, MCP server, fast-check massif) et
  V2 (block-all, SLSA L2, canonical-v2) explicitement out-of-scope.
- **D8** : Schema Evolution Policy SemVer (patch/minor 30j notice/major 60j +
  ADR + migrations versionnées).

Relations cross-canon :

- **ADR-015** : conforme (canon vit dans vault)
- **ADR-048** (canon enforcement coverage) : remédiation partielle du risk
  drift silencieux `.spec/00-canon/` (77 % prose-only)
- **ADR-049** (db-governance canon enforcement) : élargit REG-002 du scope
  canon-files au scope complet files/db/rpc/runtime via `relates-to`
  (pas `supersedes`)
- **ADR-053** (Planning Live System) : réutilise pattern cron VPS DEV + MOC SoT

## Why

ADR-048 (accepté 2026-05-07) avait révélé que `.spec/00-canon/` était à
77 % prose-only sans enforcement mécanique. ADR-049 demandait un registry
queryable mais limité au canon governance. Le monorepo a atteint la taille
(2138 files, 232 tables, 180 RPCs, 470 runtime entrypoints, 15 domaines)
où la perte de connaissance structurelle bloquait cleanup/refactor/upgrade.
ADR-058 répond en élargissant à tout le code monorepo.

## Status au merge PR-A

- `proposed` (pas encore `accepted`)
- 6 PRs monorepo ouvertes (#457-#464) implémentant l'architecture
- Promotion vers `accepted` conditionnée par PR-G (block-new) merge +
  7-14 jours signal empirique vert : 0 false-positive, coverage stable,
  registry_coverage_pct = 100 %, ownership_coverage_pct ≥ 90 %.

## Découvertes pendant l'implémentation

1. **DomainIdSchema D1..D8 → D1..D15** : correction pre-merge en PR-D suite
   à lecture exhaustive de `db-governance/domain-map.md` v1.4.2 (15 domaines,
   pas 8).
2. **Gate self-discovery PR-G** : le block-new gate a détecté 5 paths non
   couverts dans sa propre stack PR-B..F (`.spec/00-canon/repository-registry/*.yaml`
   + `tests/registry/fixtures/rpc-edge-cases.sql`). Fix dans la même PR
   (+2 entrées D15 governance dans ownership.yaml).
3. **Lockfile drift PR-B** : `npm install --package-lock-only` dans worktree
   symlinké a downgradé `linkifyjs@4.3.3 → 4.3.2` (cache stale). Fix par
   commit `52dfaf72` reset + workspace-scoped install.

## Sortie

Cf. ADR-058 body pour le détail technique + plan directeur
`/home/deploy/.claude/plans/verifier-la-vraie-logical-whistle.md`.
