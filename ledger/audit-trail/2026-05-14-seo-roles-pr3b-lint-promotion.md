---
date: 2026-05-14
type: audit-trail
related: [ADR-040, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-14 — PR-3b SEO role lint promotion (warn → error)

## What

Promotion de la règle de lint `seo-no-bare-role-literal` de `severity: warning` → `severity: error` à la fois côté ast-grep (`.ast-grep/rules/seo-no-bare-role-literal.yml`) et côté ESLint (`frontend/.eslintrc.cjs` rule `no-restricted-syntax` sélecteur `Literal[value=/^(R3_BLOG|R3_guide|R6_BUYING_GUIDE|R3_guide_achat|R3_guide_howto|R3_conseils|R1_pieces|R6_GUIDE)$/]`).

PR monorepo : [ak125/nestjs-remix-monorepo#522](https://github.com/ak125/nestjs-remix-monorepo/pull/522).

## Why

Per la condition de promotion documentée dans ADR-040 § "Suite (hors scope)" et la mémoire `seo-roles-canon-shipped-20260505` : la règle a été shippée en mode `warning` (PR-3a, commit `0a792dcc`, mergée 2026-05-05) avec une précondition empirique de **≥ 7 jours d'observation propre** avant promotion vers `error`. Earliest trigger : 2026-05-12. Exécution : 2026-05-14 (2 jours après le trigger, canon `feedback_decision_must_be_signal_proven_not_intuited`).

### Signal empirique mesuré

1. **ast-grep scan** sur full corpus (`frontend/app` + `backend/src`) avec la règle en mode `warning` : **0 rule findings** (sortie 0, identique sur origin/main et sur la branche PR-3b après flip).
2. **grep regex eslint** : 3 literals OUTPUT-context restants — tous justifiés exemptés :
   - 2× `admin.seo-hub.page-briefs.tsx:406-407` (`<option value="R3_guide">` / `value="R3_conseils">`) = INPUT context (filter UI binding URL `searchParams`)
   - 1× `blog-pieces-auto.guide-achat.$pg_alias.tsx:210` (`pageRole: "R6_BUYING_GUIDE"`) = type-contract divergence : `R6GuidePayload.pageRole` déclaré comme literal type `"R6_BUYING_GUIDE"` dans `app/types/r6-guide.types.ts:181`

## Changements

- `.ast-grep/rules/seo-no-bare-role-literal.yml` : `severity: warning` → `severity: error`. Section `note:` mise à jour pour documenter le promotion rationale + 0-findings baseline.
- `frontend/.eslintrc.cjs` : `'no-restricted-syntax': ['warn', …]` → `['error', …]`. Message rule `⚠️` → `❌`. Comment block updated.
- `frontend/.eslintrc.cjs` : nouveau bloc `overrides[]` pour les 2 fichiers légitimement exemptés (avec commentaires inline expliquant INPUT context vs type-contract divergence).
- **PAS** de modification des fichiers sources (pas de bricolage : on ne reformule pas le code pour dodger la règle ; on l'exempte avec justification documentée).

## Impacts

- **Anti-régression durci** : tout nouveau commit introduisant un literal SEO role legacy en OUTPUT context fera **fail CI** (ESLint job + ast-grep) au lieu de produire un warning silencieux.
- **Surface canon `@repo/seo-roles`** désormais protégée par 2 layers d'enforcement (ast-grep bare forms + ESLint suffixed forms), union testée par `__regression__/seo-role-canon-guard.test.ts`.
- **Aucun changement runtime** : flip lint-time uniquement, aucune modification des artefacts générés ou du comportement du serveur.

## Follow-ups (out of scope post-acceptance)

- **`R6GuidePayload` ↔ `PageRole` enum unification** : `R6GuidePayload.pageRole` déclare `"R6_BUYING_GUIDE"`, l'enum canonique `PageRole.R6_GUIDE_ACHAT` vaut `"R6_GUIDE"`. Cette divergence est tracée par l'exemption documentée + référence dans le commit message. Chantier R6 V2 contract migration séparé.
- **Backend `.eslintrc.js` audit** : règle déjà mirrorée côté backend ; pas de bare literal en OUTPUT context au scan actuel, pas de promotion nécessaire ; à revérifier si nouveau code introduit la classe.

## Décideur

@fafa (2026-05-14), après pré-flight empirique (ast-grep 0 findings + grep manuel 3 matches tous justifiables) confirmant la précondition `seo_role_normalization_failed_total = 0` cumulé 7j.

## Références

- PR monorepo : [ak125/nestjs-remix-monorepo#522](https://github.com/ak125/nestjs-remix-monorepo/pull/522)
- ADR parent : [[ADR-040-seo-roles-canon-ts-side-only]] (proposed initial rule semantics)
- Précédent atomique : commit `0a792dcc` PR-3a (warn shipping 2026-05-05)
- Canon mémoire : `seo-roles-canon-shipped-20260505`, `feedback_decision_must_be_signal_proven_not_intuited`, `pr-3b-promotion-trigger-20260512`
