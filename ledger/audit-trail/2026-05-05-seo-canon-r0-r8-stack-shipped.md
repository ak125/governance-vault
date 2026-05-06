---
title: "Session 2026-05-05 — SEO Canon R0..R8 stack livré (9 PRs mergées)"
date: 2026-05-05
type: session-trail
related_chantier: D
related_adr: ["ADR-040"]
related_prs:
  - "ak125/nestjs-remix-monorepo#304"
  - "ak125/nestjs-remix-monorepo#305"
  - "ak125/nestjs-remix-monorepo#306"
  - "ak125/nestjs-remix-monorepo#307"
  - "ak125/nestjs-remix-monorepo#308"
  - "ak125/nestjs-remix-monorepo#309"
  - "ak125/nestjs-remix-monorepo#310"
  - "ak125/nestjs-remix-monorepo#311"
  - "ak125/nestjs-remix-monorepo#312"
status: closed
session_closed_at: 2026-05-05
---

# 2026-05-05 — SEO Canon R0..R8 stack livré (9 PRs mergées)

> **Chantier de rattachement** : `D` (SEO indexation / crawl budget) per
> roadmap pre-canon `MOC-Roadmap-2026` (vault PR #128 OPEN) et plan-directeur
> local `~/.claude/plans/plan-directeur-roadmap-globale-automecanik-2026.md`.
> ADR-040 consacre R0..R8 comme socle TS-side ; le résultat *business
> indexation* (D1-D7) reste TBD — distinct de cette livraison.

## Synthèse

Stack complet du canon SEO mergé sur `main` du monorepo `ak125/nestjs-remix-monorepo` :
- 9 PRs (#304, #305, #306, #307, #308, #309, #310, #311, #312)
- 5 commits squash visibles sur main (cascade auto-merge a fusionné les stacked PRs dans leurs bases)
- 14 commits follow-up cumulés sur 3 vagues de review automatique
- ADR-040 (cette session) consigne la décision architecturale finale

## Commits sur main

```
0a792dcc feat(seo-roles): lint enforcement phase 3a — observe (PR-3a) (#309)
7f139d91 feat(seo-roles): foundation package @repo/seo-roles@0.1.0 (PR-0A) (#304)
0545f36c docs(canon): MCP inventory + PR-4B plan revision (#312)
d06677ae chore(seo-roles): drop dead-code PAGE_TYPE_TO_CANONICAL_ROLE map (#311)
179bbfdb docs(seo-canon): align scripts + skill doc + canon-map v1.2.0 (PR-4A) (#305)
```

## Architecture livrée

`@repo/seo-roles@0.2.0` — package partagé frontend/backend :
- `RoleId` enum canonical R0..R8 + R6_SUPPORT
- Branded type `CanonicalRoleId` (compile-time safety)
- Zod schemas `tolerantRoleSchema` (input) et `canonicalRoleSchema` (output)
- `normalizeRoleId`, `assertCanonicalRole(Strict)`, `pageTypeToRoleId`, `roleIdToPageType`
- `getRoleDisplayLabel` (FR), `getRoleShortLabel`, `ROLE_BADGE_COLORS`

4 couches d'enforcement (DB CHECK retirée du plan initial — cf. ADR-040 §2) :
1. TypeScript branded type compile-time
2. Runtime Zod au boundary controller (`parseResponseOrSoft<T>` + observability)
3. Lint statique ast-grep + ESLint (warning observe → error en PR-3b future)
4. Compteurs Prometheus `seo_role_normalization_failed_total{controller, endpoint}`

## Décision architecturale clé

**Le canon SEO R0..R8 vit côté TypeScript uniquement, pas en DB.**

L'inventaire MCP read-only du 2026-05-05 a révélé :
- `__seo_page.page_role` colonne n'existe pas en prod (migration `20260124_add_page_role.sql` jamais appliquée)
- ENUM `seo_page_role` orphelin sauf 1 consumer mono-valué (`__seo_observable.page_role` = 1176 R5)
- La DB stocke des worker page_types courts (`R3_guide_howto`, `R1_pieces`, etc.) qui sont un vocabulaire pipeline distinct du canon

→ Pivot Option C : aucune migration DB, aucun trigger PL/pgSQL, aucune
recréation de `assign_page_role_from_url()`. Le mapping
`PAGE_TYPE_TO_ROLE` côté TS traduit worker → canonical au boundary.

ADR-040 formalise cette décision.

## Process

### 3 vagues de review automatique (10 reviews cumulées)

- Wave 1 (4 reviews) : PR-0A, PR-0B, PR-1, PR-2 — tous APPROVE avec findings mineurs
- Wave 2 (4 reviews) : PR-4A, PR-3a, PR-3a-cleanup, PR #311 follow-up
  — 1 REQUEST_CHANGES sur PR-3a-cleanup (target_role 'R6' OUTPUT leak), levée
- Wave 3 (3 reviews) : suivi des fix wave 2 — APPROVE sur tous

### Follow-up commits clés

- Set<string> O(1) lookup canonical (PR-0B perf) — `3a3f9c26`
- Cluster mode JSDoc on counters (PR-2) — `cb8a0553`
- Migration r6-guide.service.ts target_role canonical (PR-3a-cleanup) — `28bec732`
- Frontend ROLE_CONFIG R6_GUIDE_ACHAT key (PR-3a-cleanup follow-up) — `28bec732`
- ast-grep __regression__/ scope + frontend ESLint overrides (PR-3a) — `576d9dff`
- README __regression__ verification command (PR-3a) — `012721c8`
- Inventory doc Option A→C contradiction fix (PR #312) — `8dbc6f1b`
- ADR-040 formalisation (cette session, vault PR)

### Décisions « no bricolage » prises

- **Pas de `RoleDisambiguationService`** : la PL/pgSQL retourne short forms aujourd'hui ; recréer côté TS dupliquerait des patterns URL (interdit)
- **Pas de trigger DB** : worker vocab et canon RoleId sont 2 vocabulaires distincts par design
- **Pas de migration `__rag_content_refresh_log`** : `R3_guide_howto` est worker how-to, pas un mismatch canon
- **Pas de DROP ENUM `seo_page_role`** : 1 consumer (`__seo_observable`)
- **Annotation migration jamais-appliquée** : guardrail documentaire pour éviter futures applications par erreur

## Followups différés (intentionnels)

- **PR-3b future** : promotion lint observe → error après 7j observation propre
- **4 routes blog publiques** : `PageRole.R3_BLOG → R3_CONSEILS` (cosmetic GTM, non-leaky)
- **R6GuidePayload `intentType: 'R6'`** : 3-fichiers coordinated refactor (interfaces backend + types frontend + service)
- **GSC Reality Check** : chantier parallèle de croissance trafic (distinct de stabilité-canon)

## Références

- ADR-040 (vault) : `ledger/decisions/adr/ADR-040-seo-roles-canon-ts-side-only.md`
- Plan stratégique : monorepo `~/.claude/plans/ton-architecture-canonique-est-silly-crab.md` (4 couches enforcement)
- Inventaire MCP : monorepo `.spec/00-canon/db-governance/pr4b-mcp-inventory-2026-05-05.md`
- Canon map v1.2.0 : monorepo `.spec/00-canon/db-governance/legacy-canon-map.md`
- Package : monorepo `packages/seo-roles/`

## Métriques

- 9 PRs livrées + 14 commits follow-up = 23 commits cumulés sur cette livraison
- 99 tests `node:test` package + 40 tests Jest backend + 12 tests Jest `parseResponseOrSoft` = 151 tests
- 0 erreurs typecheck sur fichiers nouveaux/migrés
- 18 → 0 warnings ast-grep baseline (PR-3a-cleanup)
- 11 reviews automatiques cumulées sur 9 PRs monorepo (Wave 1: 4, Wave 2: 4, Wave 3: 3) — la rédaction de cette ADR-040 vault est une session distincte non comptée dans les reviews de PRs monorepo
