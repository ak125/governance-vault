---
date: 2026-05-14
type: audit-trail
related: [ADR-040, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-14 — PR-3b SEO role lint promotion (warn → error) — bare forms only

## What

Promotion de la règle ast-grep `seo-no-bare-role-literal` de `severity: warning` → `severity: error`. **Scope minimal : 1 fichier, +14/-4 lignes**, sur les bare forms uniquement (`R3 / R6 / R9 / R3_GUIDE`).

PR monorepo : [ak125/nestjs-remix-monorepo#522](https://github.com/ak125/nestjs-remix-monorepo/pull/522), commit `b21a1241`.

## Why

Précondition documentée dans ADR-040 § "Suite (hors scope)" + mémoire `seo-roles-canon-shipped-20260505` : règle shippée en mode `warning` (PR-3a, commit `0a792dcc`, mergée 2026-05-05) avec ≥ 7 jours d'observation propre avant promotion `error`. Earliest trigger : 2026-05-12. Exécution : 2026-05-14 (J+9, canon `feedback_decision_must_be_signal_proven_not_intuited`).

### Signal empirique mesuré

`ast-grep scan --rule .ast-grep/rules/seo-no-bare-role-literal.yml frontend/app backend/src` (ast-grep@0.42.2 pinned via root devDep) → **0 rule findings** sur le full corpus. Aucune ligne de code à migrer.

## Pourquoi minimal — historique des 4 rounds itératifs

La memory `pr-3b-promotion-trigger-20260512` listait initialement 2 fichiers à flipper :
1. `.ast-grep/rules/seo-no-bare-role-literal.yml` (severity warn → error)
2. `frontend/.eslintrc.cjs` (no-restricted-syntax warn → error sur sélecteur SEO)

Tentative #1 a fait les deux flips simultanément. ESLint flip s'est révélé **bricolage en cascade** :

### Bricolage cascade observée

- **Round 1** : flip ESLint warn → error a immédiatement cassé CI sur `frontend/app/components/ui/command.tsx:28` — la sélecteur sœur `hidden sans breakpoint responsive` (regex JSXAttribute) matche `[hidden]` attribute selectors **dans** Tailwind arbitrary-value classnames comme `[&_[cmdk-group]:not([hidden])_~...]`. C'est un faux positif documentable.
- **Round 2** : tentative de patcher le regex avec un lookbehind `(?<!\[)hidden(?!\])`. Patch correct techniquement, mais regex-on-regex sur un sélecteur déjà fragile = bricolage par-dessus bricolage. Canon `feedback_no_bricolage_escalate_to_industry_standard` flagge le pattern (3ᵉ « no bricolage » consécutif user).
- **Round 3** : escalade architecturale vers absorption complete du SEO suffixed-form coverage dans ast-grep (extension du `rule.all.any` patterns + 2 nouvelles ignores `admin.seo-hub.page-briefs.tsx` + `blog-pieces-auto.guide-achat.$pg_alias.tsx`). Probe local : **61 findings dans 11 fichiers** dont des canon-defining Zod enums (`page-brief.dto.ts` : `z.enum(['R1', 'R3_guide', 'R3_conseils', 'R4'])`), INPUT switch handlers (`seo-canonical.service.ts:75` : `case 'R6_BUYING_GUIDE':`), config constants typés (`buying-guide-quality.constants.ts` : `'R1_pieces' | 'R3_guide_howto' | ...`). Chacun de ces fichiers nécessite un audit per-file pour classer légitime (à exempter via ignores) vs debt (à migrer canonical).
- **Round 4** : décision = ramener PR-3b au **scope minimal documenté par la memory** : flip ast-grep bare forms seulement. Tout le reste (ESLint flip, audit des 11 fichiers, R6GuidePayload contract divergence) déféré à **PR-3c** séparé.

### Force-push effectué

Branche `chore/seo-roles-pr3b-lint-error` reset à `origin/main` puis re-commit unique `b21a1241`. Les 2 commits intermédiaires (`eeb06ac6` flip combiné + `4947695d` regex hack) sont **abandonnés** — uniquement présents dans l'historique de la PR #522 force-pushée.

## Changements (state final)

- `.ast-grep/rules/seo-no-bare-role-literal.yml` : `severity: warning` → `severity: error`.
- Section `note:` mise à jour pour documenter la 0-findings baseline ET la déferral explicite de la promotion ESLint.
- Section `message:` mise à jour pour mentionner `ignores:` au lieu de `files:` (typo correction inline).

**Aucune modification source-code**. Aucune nouvelle ignore. Aucun exemption ESLint. Aucun regex hack.

## Impacts

- **Anti-régression durci** : tout nouveau commit introduisant un literal SEO bare form (R3, R6, R9, R3_GUIDE) en OUTPUT context fera **fail CI** au lieu d'un warning silencieux.
- **Couverture suffixed forms** : maintenue via ESLint `no-restricted-syntax` regex selector à severity `warn`. Pas de régression de couverture, juste pas d'enforcement strict.
- **Impact runtime** : nul (flip lint-time uniquement).

## Follow-ups (PR-3c, séparé)

1. Architectural split : extraire le sélecteur SEO de l'ESLint `no-restricted-syntax` block pour qu'il puisse être promu indépendamment des sélecteurs Tailwind (sans patcher de regex).
2. Audit des 11 fichiers surfacés par la probe absorption (classer légitime vs debt, ajouter aux `ignores:` ou migrer canonical).
3. R6GuidePayload contract unification : `R6GuidePayload.pageRole` declaré `"R6_BUYING_GUIDE"` ≠ enum canon `PageRole.R6_GUIDE_ACHAT = "R6_GUIDE"`. Migration coordonnée frontend type + backend service.
4. Évaluation `eslint-plugin-tailwindcss@3.18.3` comme remplacement du regex maison pour les sélecteurs Tailwind.

## Décideur

@fafa (2026-05-14), après 4 rounds d'itération empirique. Direction canon : « meilleure approche pas de bricolage » répétée 4× a forcé le retour au scope minimal après identification du bricolage cascade en Round 2-3.

## Références

- PR monorepo : [ak125/nestjs-remix-monorepo#522](https://github.com/ak125/nestjs-remix-monorepo/pull/522) (force-pushed à commit `b21a1241`)
- ADR parent : [[ADR-040-seo-roles-canon-ts-side-only]] (proposed initial rule semantics)
- Précédent atomique : commit `0a792dcc` PR-3a (warn shipping 2026-05-05)
- Canon mémoire : `seo-roles-canon-shipped-20260505`, `feedback_decision_must_be_signal_proven_not_intuited`, `pr-3b-promotion-trigger-20260512`, `feedback_no_bricolage_escalate_to_industry_standard`
