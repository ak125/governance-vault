---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: Sprint perf bundle — leçons signal-proven (2026-05-08)
slug: sprint-perf-bundle-lessons-20260508
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-08"
updated_by: "@fafa"
related_adr:
  - "ADR-051"
related_prs:
  - "ak125/governance-vault#211"
  - "ak125/nestjs-remix-monorepo#382"
  - "ak125/nestjs-remix-monorepo#387"
  - "ak125/nestjs-remix-monorepo#391"
  - "ak125/nestjs-remix-monorepo#393"
  - "ak125/nestjs-remix-monorepo#394"
  - "ak125/nestjs-remix-monorepo#395"
  - "ak125/nestjs-remix-monorepo#396"
  - "ak125/nestjs-remix-monorepo#397"
status: current
tags:
  - performance
  - bundle
  - lighthouse
  - signal-proven
  - vite
  - remix
  - methodology
---

# Sprint perf bundle — consignes méthodo signal-proven

> Date : 2026-05-08
> Contexte : refus de PR #382 (recalibration arbitraire 1250 → 3500 KB) +
> sprint 7 PRs cascade pour produire la donnée gouvernée.

## Consigne 1 — Matrice raw / gzipped / per-page (NON-NÉGOCIABLE)

Avant de comparer une mesure bundle à un budget Lighthouse, **identifier
la sémantique de chaque côté** :

| Mesure | Sémantique | Comparable à `lighthouse-budget.json` `script: 1250` ? |
|---|---|---|
| `du -shc build/client/assets/*.js` | Bundle entier raw, toutes pages | ❌ Non |
| `audit-reports/bundle-top10.json` `total.size` | Idem (raw) | ❌ Non |
| `audit-reports/bundle-top10.json` `total.gzip` | Bundle entier gzippé | ❌ Non (per-page only) |
| Lighthouse `resource-summary.script.size` | Scripts chargés sur **une URL**, transferred bytes (gzip/brotli) | ✅ Oui |

**Précédent évité** : PR #382 a comparé "bundle 3128 KB raw" à "budget
1250 KB gzipped per-page" et conclu à un dépassement de +1.85 MB. La
mesure CI réelle était **+9 KB** (1289 vs 1280 KB). 7 PRs ont été
nécessaires pour étouffer cette confusion sémantique.

## Consigne 2 — Vérifier le plancher technique avant d'optimiser

Sur un bundle Remix v2.17 + React 18 + 15 Radix + html-parser, certaines
optimisations populaires sont **des gains fantômes** :

| Levier | Gain attendu | Gain réel | Pourquoi |
|---|---:|---:|---|
| Lazy-load admin routes | -300 à -500 KB | **0 KB** | `vite.config.ts:117-123` exclut `admin.*` du build prod |
| Tree-shake lucide-react | -45 KB | **0-25 KB** | Lucide v0.462 a déjà `sideEffects: false` + ESM, Vite tree-shake déjà optimal |
| Splitter @remix-run/react | -50 KB | **race condition** | Cycles d'init React documentés vite.config.ts:35-36 |
| Vendor splitting fin (zod, @tanstack) | KB net | **fragmentation cache** | Pas de KB net mais TBT amélioré sur navigations |
| Lazy modal off-viewport | -14 KB initial | **-13.8 KB** | Confirmé empirique PR-4 |

**Règle dérivée** : avant tout sprint perf, audit empirique :
1. Quels routes sont dans le build prod ? `grep ignoredRouteFiles vite.config.ts`
2. Quels libs ont déjà `sideEffects: false` ? `cat node_modules/<lib>/package.json | jq .sideEffects`
3. Quels chunks sont dupliqués ? `find node_modules -name "<lib>" -type d`
4. Quelle est la mesure CI **réelle** (pas extrapolée) ? `gh run view <id> --log | grep maxNumeric`

## Consigne 3 — 9 hypothèses à vérifier avant de recalibrer un budget

Le script `scripts/perf/vendor-breakdown.mjs` (PR #395) automatise les
checks. Manuellement, vérifier dans cet ordre :

1. **React DevTools embarqué prod** : `grep '__REACT_DEVTOOLS_GLOBAL_HOOK__' build/client/assets/*.js` → présence ≠ leak (React 18 le détecte par design)
2. **Duplications React** : `find node_modules -name 'react' -type d -exec test -f {}/package.json \;` puis filtrer par `pkg.name === 'react'` (ignorer `@mdx-js/react`, `@remix-run/react`, etc.)
3. **react-dom-server fuite client** : `grep 'renderToPipeableStream' build/client/assets/*.js` (doit retourner 0)
4. **JSX dev runtime fuite prod** : `grep 'jsx-dev-runtime' build/client/assets/*.js` (doit retourner 0)
5. **PropTypes runtime** : présence dans node_modules ≠ bundlé (vérifier dans bundle final)
6. **html-react-parser justification** : compter routes consommatrices via `<HtmlContent>` wrapper (10+ chez AutoMecanik = légitime)
7. **framer-motion presence** : si présent, lib lourde 50-100 KB, alternative `motion-one` ~5 KB
8. **Duplications utilitaires** : versions multiples `clsx`, `tailwind-merge`, `zod`, `nanoid`, `uuid` (ignorer dev-tool nested comme `node_modules/knip/node_modules/zod`)
9. **manifest bloat** : avec `v3_lazyRouteDiscovery: true` doit être ~5 KB initial. >20 KB = bug Remix ou config

Tous ces checks doivent passer **avant** d'invoquer Branche B (recalibration).

## Consigne 4 — Audit Remix payloads obligatoire avant arbitrage budget

Le bundle JS n'est **qu'une partie** du coût CWV. `window.__remixContext`
+ hydration JSON + loaders dupliqués peuvent représenter 100-500 KB
transférés invisibles à `bundle-top10.json`.

Script canon : `scripts/perf/remix-payload-audit.mjs` (PR #396). Mesures :
- HTML SSR size (raw + gzip + brotli)
- `__remixContext` size raw
- Top 5 `loaderData` routes par taille sérialisée
- Détection entités dupliquées (≥ 500 octets en ≥ 2 routes)

**Seuil signal-proven** : `__remixContext > 120 KB` → investiguer.
`duplicates.length > 0` → extraire en parent loader + `useRouteLoaderData`.

Mesure baseline 2026-05-08 sur prod : **12-29 KB par URL**, **0 dups**.
Stack hydration saine, ne pas chercher d'optimisation Remix-side sans
nouveau signal.

## Consigne 5 — Branchement décisionnel A vs B (ADR-051)

Toute proposition d'amender `lighthouse-budget.json` doit traverser ce
branchement :

```
Mesure CI réelle dépasse budget ?
├─ Oui
│   ├─ Plancher technique (PR-5 + PR-5bis) prouve > budget actuel ?
│   │   ├─ Oui → Branche B : ADR successeur ADR-051 recalibre signal-proven
│   │   │       (evidence-pack joint : bundle-top10.json + vendor-breakdown.json
│   │   │        + remix-payload-report.json + critical-path-analysis.json)
│   │   └─ Non → Branche A : optimiser, ne PAS toucher au budget
│   └─ ...
└─ Non → ne RIEN faire (le budget remplit son rôle anti-régression)
```

**Pattern de bricolage refusé** (PR #382) : recalibrer pour débloquer N
PRs OPEN sans evidence-pack. Refus systématique.

## Consigne 6 — Stacked PR cascade max 3 niveaux

Pattern utilisé pour ce sprint :
- Niveau 1 : PR-1 (foundation, base = main)
- Niveau 2 : PR-2/3/4/5/5bis/6 (parallèles, base = PR-1 branch)
- Niveau 3 : (aucun)

**Gotcha GitHub** :
- Auto-merge GraphQL **refuse** sur niveau 2+ avec message
  `"Pull request Protected branch rules not configured for this branch"`.
- Workaround : auto-merge fire sur PR enfant si base = parent stacked
  (pas main directement). Squash combine dans commit final.
- Quand parent merge, GitHub re-cible automatiquement les enfants vers main.
- Conflits `audit-reports/bundle-top10.json` quasi-systématiques entre
  PRs sur le même base — résolution canon : `git checkout --theirs` +
  régénérer via `npm run bundle:report`.

## Consigne 7 — Dual-build visualizer limitation

`rollup-plugin-visualizer 6.0.5` ne capture qu'**une partie** des chunks
dans Vite + Remix dual-build (server + client). Vendor chunks
typiquement absents du raw-data JSON :
- `react-vendor`, `radix-vendor`, `lucide-vendor`, `html-parser-vendor`,
  `manifest`, `carousel-vendor`, `cmdk-vendor`

Workaround : checks file-based via grep direct sur `build/client/assets/*.js`
couvrent les hypothèses critiques (devtools, dev-runtime, react-dom-server)
indépendamment du visualizer. Module-by-module breakdown limité aux
chunks effectivement capturés.

Follow-up envisageable (hors scope sprint) : fix visualizer config pour
capturer les 2 passes rollup, ou parser directement le `.vite/manifest.json`
si activé via `build.manifest: true`.

## Références canon

- **ADR-051** (vault) : méthodologie complète + branchement A/B + ADR-052 conditionnel
- `audit-reports/bundle-top10.json` (monorepo) : SoT mesure bundle
- `audit-reports/vendor-breakdown.json` (PR #395) : 9 hypothesis checks
- `audit-reports/remix-payload-report.json` (PR #396) : hydration audit
- `frontend/lighthouse-budget.README.md` : matrice raw/gzip/per-page
- `.github/workflows/perf-gates.yml` : CI gate Lighthouse + bundle freshness
- Mémoire monorepo : Index `MEMORY.md`, entry "sprint perf bundle 2026-05-08"

## Anti-pattern interdit

- Recalibrer un budget pour débloquer une PR sans evidence-pack mesuré
- Comparer bundle raw total à budget per-page gzipped
- Optimiser des routes exclues du build prod (`ignoredRouteFiles`)
- Bypass CWV temporaire (`gh pr merge --admin` sur perf-gates rouge)
- Commit `bundle-report.html` versionné (1 MB HTML, regénérable)
