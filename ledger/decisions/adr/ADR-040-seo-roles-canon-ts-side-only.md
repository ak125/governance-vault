---
id: ADR-040
title: "SEO Roles Canon R0..R8 — single source of truth côté TypeScript via @repo/seo-roles, pas de DB CHECK"
status: accepted
date: 2026-05-05
decision_date: 2026-05-05
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["R-SEO-01", "R-SEO-02", "G3"]
related_incidents: []
related_adr: ["ADR-031", "ADR-037", "ADR-039"]
---

# ADR-040: SEO Roles Canon R0..R8 — TS-side only

## Contexte

Le monorepo expose le canon SEO R0..R8 (`R0_HOME`, `R1_ROUTER`, `R2_PRODUCT`,
`R3_CONSEILS`, `R4_REFERENCE`, `R5_DIAGNOSTIC`, `R6_GUIDE_ACHAT`, `R6_SUPPORT`,
`R7_BRAND`, `R8_VEHICLE`) comme vocabulaire de classification des pages SEO,
formalisé dans `legacy-canon-map.md` v1.2.0 (monorepo `.spec/00-canon/db-governance/`).

Avant 2026-05, deux helpers parallèles vivaient côté backend
(`backend/src/config/role-ids.ts`) et frontend
(`frontend/app/utils/page-role.types.ts`), avec des dérives mineures
(`'R3'` mappé vers `R3_CONSEILS` côté frontend mais dans `FORBIDDEN_ROLE_IDS`
côté backend). 6 routes admin frontend dupliquaient `PAGE_TYPE_LABELS`
inline avec différents niveaux de couverture des aliases legacy.

Le plan stratégique initial (PR-4B) prévoyait 5 couches d'enforcement
incluant DB CHECK + trigger PostgreSQL réutilisant `assign_page_role_from_url()`
PL/pgSQL. **Inventaire MCP du 2026-05-05 a invalidé cette hypothèse** :
- `__seo_page.page_role` colonne n'existe pas en prod
- Migration `20260124_add_page_role.sql` jamais appliquée
- Fonction `assign_page_role_from_url()` absente de `pg_proc`
- ENUM `seo_page_role` consommé uniquement par `__seo_observable.page_role`
  (1176 lignes mono-valuées R5)

## Décision

### 1. SoT canonique côté TS

Le canon R0..R8 vit **exclusivement côté TypeScript** dans le package
`@repo/seo-roles@0.2.0` (monorepo `packages/seo-roles/`). Frontend et backend
consomment via `import` depuis ce package — plus de dérive parallèle possible.

Exports principaux :
- `RoleId` enum (canonical R0..R8 + R6_SUPPORT)
- `LEGACY_ROLE_ALIASES` (mapping `R3_BLOG → R3_CONSEILS`, etc.)
- `FORBIDDEN_ROLE_IDS` = `['R3', 'R6', 'R9', 'R3_GUIDE']` (bare ambigus)
- `normalizeRoleId(input)` : tolérant, retourne `RoleId | null`
- `assertCanonicalRole(role)` / `assertCanonicalRoleStrict(role)` : strict, retourne branded `CanonicalRoleId`
- `tolerantRoleSchema` / `canonicalRoleSchema` : Zod schemas pour boundary validation
- `getRoleDisplayLabel` / `getRoleShortLabel` : FR labels admin UI
- `ROLE_BADGE_COLORS` : Tailwind classes par rôle

### 2. Architecture 4 couches d'enforcement (no DB CHECK)

| # | Couche | Mécanisme | Détecte |
|---|--------|-----------|---------|
| 1 | TypeScript | Branded type `CanonicalRoleId = RoleId & { __brand }` | Compile-time : impossible de retourner un `string` brut |
| 2 | Runtime API | Zod `.parse()` explicite ou `parseResponseOrSoft<T>` au boundary controller | Request : valeur non-canonique normalisée ou loggée |
| 3 | Lint statique | ast-grep `seo-no-bare-role-literal.yml` (multi-lang) + ESLint `no-restricted-syntax` (TS/TSX) | Bare/forbidden + suffixed legacy en sortie |
| 4 | Observability | Compteur `seo_role_normalization_failed_total{controller, endpoint}` | Métriques Prometheus, kill switch `SEO_ROLE_NORMALIZE_RESPONSE=false` |

**La couche 5 DB CHECK + trigger initialement prévue est explicitement retirée**.
La DB stocke des worker page_types courts (`R3_guide_howto`, `R1_pieces`, etc.)
qui sont un vocabulaire interne au pipeline content-refresh, distinct du canon
R0..R8. Le mapping `pageTypeToRoleId()` traduit au boundary TS quand un canon
RoleId est requis.

### 3. Séparation worker page_type vs canon RoleId

| Layer | Vocabulaire | Source de vérité |
|-------|-------------|-------------------|
| DB tables (`__rag_content_refresh_log.page_type`, etc.) | worker page_type courts (`R3_guide_howto`, `R1_pieces`, ...) | Migrations Supabase + CHECK constraints |
| Code TS application | canonical RoleId (R0_HOME..R8_VEHICLE + R6_SUPPORT) | `@repo/seo-roles` |
| API responses + UI | canonical RoleId obligatoire | Zod boundary + branded type compile-time |

Cette séparation est **intentionnelle**, pas une fuite à corriger. Migrer
`R3_guide_howto → R3_conseils` en DB serait du bricolage : aplaitirait deux
concepts worker distincts (how-to procédural vs conseil pédagogique) qui
partagent un canon (R3_CONSEILS) mais ont des sources/traitements différents.

### 4. Migration `20260124_add_page_role.sql` annotée NEVER APPLIED

La migration originale prévoyait colonne `__seo_page.page_role` typée
`seo_page_role` ENUM + fonction `assign_page_role_from_url()` PL/pgSQL.
Ne pas l'appliquer — son hypothèse architecturale (DB stocke canon direct)
est obsolète.

## Conséquences

### Positives

- **Single source of truth** : `@repo/seo-roles` est l'unique source canonique
- **Type safety end-to-end** : branded `CanonicalRoleId` empêche les retours bruts
- **Pas de duplication** : frontend et backend consomment le même package
- **Pas de bricolage DB** : pas de trigger PL/pgSQL à maintenir, pas de cascade ENUM
- **Observability mesurable** : compteurs Prometheus pour valider la précondition de promotion lint warning → error

### Risques résiduels

- Les workers continuent d'émettre leur vocabulaire courte (`R3_guide_howto`).
  Si un futur consumer se met à pattern-matcher strict sur `'R3_guide_howto'`
  hors normalisation, il pourrait casser une migration ultérieure du worker.
  **Mitigation** : les workers documentent leurs vocabulaires dans
  `content-refresh.types.ts:WorkerPageType`, et tout consumer d'API doit
  passer par Zod boundary (couche 2).
- L'ENUM `seo_page_role` reste orphelin de fait (1 consumer mono-valué R5).
  Drop possible en PR future après audit `__seo_observable` consumers, mais
  pas urgent.

## Implémentation livrée

9 PRs cumulées mergées sur main 2026-05-05 :

| PR # | Squash | Contenu |
|------|--------|---------|
| #305 | `179bbfdb` | PR-4A scripts Python + canon-map v1.2.0 |
| #311 | `d06677ae` | Dead-code `PAGE_TYPE_TO_CANONICAL_ROLE` removal |
| #312 | `0545f36c` | MCP inventory + Option C pivot |
| #304 | `7f139d91` | PR-0A foundation + PR-0B branded/Zod #307 + PR-1 admin display #306 + PR-2 backend boundary #308 (cascade) |
| #309 | `0a792dcc` | PR-3a lint observe + PR-3a-cleanup #310 (cascade) |

3 vagues de review automatique (4 + 4 + 3 reviews) avec 14 commits follow-up
appliqués. Tous les findings actionables addressed, faux positifs documentés,
cosmétiques skip avec justification.

## Suite (hors scope ADR-040)

- **PR-3b future** : ≥7j observation post-merge → promotion ast-grep + ESLint
  `severity: warning → error`. Précondition : compteur `seo_role_normalization_failed_total = 0/7j`
  sur les controllers décorés.
- **Followups différés** : 4 routes blog publiques R3_BLOG → R3_CONSEILS (cosmetic GTM),
  `R6GuidePayload.intentType` 3-fichiers refactor coordonné.
- **GSC Reality Check** (chantier parallèle, hors ADR-040) : audit GSC réel
  par rôle canonique pour mesurer l'impact trafic — distinct du chantier
  stabilité-canon.

## Référence d'implémentation

- Package : `packages/seo-roles/` (commit `7f139d91`)
- Plan stratégique : `~/.claude/plans/ton-architecture-canonique-est-silly-crab.md`
- Inventaire MCP : `.spec/00-canon/db-governance/pr4b-mcp-inventory-2026-05-05.md` (PR #312)
- Canon map : `.spec/00-canon/db-governance/legacy-canon-map.md` v1.2.0 (PR #305)
- Memory entries : `worker-vocab-vs-canon-roleid.md`, `seo-roles-canon-shipped-20260505.md`
