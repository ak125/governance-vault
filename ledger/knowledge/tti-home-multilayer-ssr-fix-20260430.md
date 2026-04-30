---
type: knowledge
tags: [perf, remix, nestjs, ssr, lighthouse, post-mortem]
created: 2026-04-30
authors: [Claude Code session 2026-04-30, Fafa]
related-prs:
  - ak125/nestjs-remix-monorepo#227
  - ak125/nestjs-remix-monorepo#229
  - ak125/nestjs-remix-monorepo#230
  - ak125/nestjs-remix-monorepo#235
ci-runs:
  - https://github.com/ak125/nestjs-remix-monorepo/actions/runs/25175348869  # baseline
  - https://github.com/ak125/nestjs-remix-monorepo/actions/runs/25178882039  # post-3-layer
---

# TTI home — fix structurel multi-couches (post-mortem session 2026-04-30)

> Plan exécuté le 2026-04-30 sur `nestjs-remix-monorepo`. Réduit FCP home de **10 766 ms → 2 712 ms (−75 %)** sur Lighthouse CI mobile-emulation. Aucun bricolage : 4 PRs structurelles (warmCache, manualChunks + future flags Remix v3, DI direct loader, budget anti-régression).

## Constat de départ

Lighthouse CI sur la home (run `25175348869`, post PR #224 exit-124 fix qui a finalement débloqué les mesures) :

| Métrique | Mesuré | Budget |
|---|---:|---:|
| FCP | 10 766 ms | 11 500 ms |
| LCP | 11 527 ms | 12 500 ms |
| TTI | 11 656 ms | 12 500 ms |
| Script count peak | 44 | 50 |
| Script size peak | 1 197 KB | 1 300 KB |

Hypothèse user au départ : *"33 scripts chargés, navigateur passe trop de temps à exécuter le JS"*.

## Diagnostic

**Réfutation de l'hypothèse JS-bound** par lecture des chiffres : **FCP ≈ LCP ≈ TTI ≈ 11 s** (≤1 s d'écart). Quand les 3 sont collés, le navigateur **n'a rien à rendre avant 10.7 s** = bottleneck SSR/loader, pas bundle JS. Réduire 33→12 scripts économiserait ≤500 ms sur la queue d'hydration mais pas les ≥7 s manquants.

3 causes architecturales identifiées avec preuves dans le code :

### #1 — `warmCache()` ne couvre pas la clé awaited par le loader

`backend/src/modules/catalog/services/homepage-rpc.service.ts:402` ne warme que `getHomepageBelowFold()`. Le home loader `frontend/app/routes/_index.tsx:138` await précisément `/api/catalog/homepage-families` (clé `homepage:families:v1`, ligne 170) — **non couverte**. Premier hit Lighthouse en CI = CACHE MISS garanti → 3 requêtes Supabase parallèles cold + mapping JS pendant que le SSR attend.

### #2 — HTTP loopback dans le loader (anti-pattern auto-documenté)

`frontend/app/utils/internal-api.server.ts:6` se documente lui-même comme anti-pattern : *"Prefer getInternalApiUrlFromRequest() to avoid creating outbound HTTP connections to localhost (causes port exhaustion)"*. Mais `getInternalApiUrlFromRequest()` reste un HTTP loopback. La solution canonique est l'appel DI direct au service NestJS via le `getLoadContext` de `RemixController`.

### #3 — Bundle JS non consolidé au niveau app

Manifest production (`build/client/assets/manifest-*.js`) montrait que `routes/_index` déclarait **20 imports**, dont 17 micro-chunks d'application (`button`, `input`, `tabs`, `card`, `Section`, `Footer`, `useRootData`, `logger`, etc.). `vite.config.ts:37-64` ne splitait que les `node_modules` vendors, pas les chemins `/app/*`. Combiné à `v3_lazyRouteDiscovery` absent, le manifest des 239 routes (~85 KB) était entièrement sérialisé dans `window.__remixManifest` au SSR.

## Fix livré — 4 PRs en couches indépendantes

| Couche | PR | Surface |
|---|---|---|
| 1 | [#227](https://github.com/ak125/nestjs-remix-monorepo/pull/227) | `Promise.all([getHomepageFamilies, getHomepageBelowFold])` dans `warmCache()` |
| 3 | [#229](https://github.com/ak125/nestjs-remix-monorepo/pull/229) | `manualChunks` étendu + 3 future flags Remix v3 |
| 2 | [#230](https://github.com/ak125/nestjs-remix-monorepo/pull/230) | DI `HomepageRpcService` dans `RemixApiService`, loader appelle direct |
| 4 | [#235](https://github.com/ak125/nestjs-remix-monorepo/pull/235) | `lighthouse-budget.json` resserré sur peaks post-3-couches +10 % |

### Détails couche 1 — warm cache complet

`backend/src/modules/catalog/services/homepage-rpc.service.ts:402-415` :

```ts
async warmCache() {
  await Promise.all([
    this.getHomepageFamilies(),     // ← AJOUT (clé homepage:families:v1)
    this.getHomepageBelowFold(),
  ]);
}
```

3 lignes, fix précis. Ramène le first-visit Lighthouse de CACHE MISS (1-3 s cold Supabase) à HIT (12-20 ms Redis).

### Détails couche 3 — bundle + future flags

`frontend/vite.config.ts` étendu avec :

```ts
manualChunks(id) {
  if (id.includes('node_modules')) { /* ... vendors existants ... */ return; }
  // App-level shared chunks (NOUVEAU)
  if (id.includes('/app/components/ui/')) return 'app-ui-primitives';
  if (id.includes('/app/components/layout/') || /\/app\/components\/(Section|SectionHeader|Footer)\.tsx$/.test(id)) return 'app-shell';
  if (id.includes('/app/utils/') || id.includes('/app/lib/')) return 'app-core';
}
```

+ 3 future flags Remix v3 :

```ts
future: {
  v3_fetcherPersist: true,
  v3_lazyRouteDiscovery: true,    // ← levier principal : manifest 85→5 KB
  v3_throwAbortReason: true,
  v3_relativeSplatPath: true,
}
```

`v3_singleFetch` **explicitement reporté** : audit a remonté 18 `useFetcher()` + 6 `headers()` exports qui demandent revue coordonnée avant de basculer (le flag change le format de payload des loaders).

Mesure build local Couche 3 : home route imports **20 → 10 (−50 %)**, home chunk size 51 901 → 43 335 B (−17 %). Nouveaux chunks consolidés : `app-shell` 14 KB, `app-ui-primitives` 55 KB, `app-core` 155 KB. 0 cycle d'import, 0 warning chunkSizeWarningLimit.

### Détails couche 2 — DI direct, plus de HTTP loopback

`backend/src/remix/remix.controller.ts:46-53` exposait déjà le contexte au loader :

```ts
getLoadContext: () => ({
  user: request.user,
  remixService: this.remixService,
  remixIntegration: this.remixApiService,  // ← service DI accessible côté loader
  ...
})
```

Cours : ajout dans `RemixApiService` de `getHomepageFamilies()` et `getHomepageBelowFold()` qui pass-through `HomepageRpcService` (déjà exporté par `CatalogModule`). `RemixModule` importe `CatalogModule` via `forwardRef` (cycle DI évité).

Loader transformé :

```ts
// AVANT
const familiesRes = await fetch(getInternalApiUrl("/api/catalog/homepage-families"));
const familiesRaw = familiesRes.ok ? await familiesRes.json() : null;

// APRÈS
const remixApi = await getRemixApiService(context);
const familiesRaw = await remixApi.getHomepageFamilies();
```

FAQ délibérément laissée sur HTTP loopback : `FaqService` non exporté par `SupportModule` → étendre exports = scope creep. FAQ étant deferred (non-bloquant SSR), impact mineur.

## Mesure d'impact (Lighthouse CI mobile, run `25178882039`)

| Métrique | Avant plan | Après 3 couches | Delta home |
|---|---:|---:|---:|
| **FCP home** | 10 766 ms | **2 712 ms** | **−75 %** |
| LCP home | 11 527 ms | 3 312 ms | −71 % |
| TTI home | 11 656 ms | 8 776 ms | −25 % |
| TTFB home | n/a | 824 ms | — |
| TBT home | n/a | 125 ms | — |
| Script count peak | 44 | 22 | **−50 %** |
| Script size peak | 1 197 KB | 1 117 KB | −7 % |

Le pic se déplace : la home est clean (FCP < 3 s), mais `/pieces/<slug>` (TTFB 3 264 ms) et `/constructeurs/<slug>.html` (TTFB 416 ms) restent contraints par leurs propres loaders. Hors scope du plan TTI home — à attaquer séparément.

## Patterns réutilisables

### Pattern A — vérifier si `warmCache()` couvre TOUTES les clés awaited par les loaders critiques

Anti-pattern : un service expose 3 méthodes (`getHomepageDataOptimized`, `getHomepageFamilies`, `getHomepageBelowFold`) chacune avec sa propre clé Redis, mais `warmCache()` n'en warm qu'une. Premier visit = CACHE MISS sur les autres.

Audit grep proposé pour le repo :
```bash
# Lister toutes les clés cache utilisées
grep -rnE "cacheService\.(get|set)\b.*'[^']+:[^']+'" backend/src
# Lister toutes les méthodes warmCache et leur contenu
grep -rnB2 -A 10 "async warmCache" backend/src
# Croiser : chaque clé cache lue par un loader doit être écrite par un warmCache
```

### Pattern B — `<service>-integration` côté NestJS-Remix

Quand un loader Remix doit appeler un service NestJS, le pattern canonique est :
1. Backend : exposer le service via `RemixApiService` (DI direct, pas HTTP)
2. Wire : `RemixController.getLoadContext()` met `remixService`/`remixIntegration` dans le contexte
3. Frontend : `getRemixApiService(context)` helper récupère et appelle direct

Anti-pattern : `fetch(getInternalApiUrl(...))` dans le loader → coût TCP loopback ~10-50 ms cold + port pressure.

### Pattern C — diagnostic FCP ≈ LCP ≈ TTI

Quand les 3 métriques sont collées (≤1 s d'écart) à une valeur élevée (>5 s), le bottleneck est **côté serveur** (génération HTML lente), pas côté bundle JS. Réduire le JS n'aidera pas FCP. Investiguer :
1. Loader awaits multiples
2. SSR data fetches non-warmed
3. HTTP loopback intra-process
4. RPC Supabase cold

Symptôme inverse : si TTI − FCP > 2 s mais FCP est bas, alors c'est du JS execution / hydration → là on attaque le bundle.

### Pattern D — `v3_singleFetch` audit avant flip

Le flag change le format de sérialisation des loaders (turbo-stream). Avant de l'activer, grepper :
```bash
grep -rcE "useFetcher\(\)" frontend/app/    # tous fetchers (compat à vérifier)
grep -rE "^export const headers" frontend/app/routes/   # consolidation headers nécessaire
grep -rE "return.*\bnew (Map|Set|Date)" frontend/app/routes/   # types non-sérialisables
```

## Anti-patterns évités (confirmés dans le plan)

- **Pas** de `React.lazy()` dans `_index.tsx` (un précédent essai dans `374cba10` avait été reverté `74148c9e` — `React.lazy` casse SSR Remix : rend `null` côté serveur, hydration mismatch).
- **Pas** de `<ClientOnly>` wrapper above-fold (régression SEO sur contenu indexable).
- **Pas** de modification du `defer()` + `<Await>` actuels (déjà bon pattern Remix natif).
- **Pas** de `splitVendorChunkPlugin` (incompatible avec `manualChunks` custom).
- **Pas** de bricolage runtime (intercepteur fetch, monkey-patch Remix internals).

## Suivi à ouvrir comme tickets séparés (hors scope ce plan)

- [ ] Audit `v3_singleFetch` activable (18 useFetcher + 6 headers à reviewer)
- [ ] HTTP loopback `/pieces/<slug>` et `/constructeurs/<slug>.html` loaders — TTFB pieces 3 264 ms suggère même type de cache miss/loopback à investiguer
- [ ] Migration `routes/plan-du-site.tsx` (autre caller de `homepage-families` en HTTP) vers DI
- [ ] Étendre `SupportModule.exports` pour permettre `FaqService` via DI loader (scope tracker hors plan)
- [ ] Réduire HTML SSR payload (251 KB) — couches 5/6 si on veut FCP <2.5 s

## Références

- ADR-016 — vehicle-page-cache (similaire : warm cache + RPC optim)
- `feedback_no_bricolage_analyse_profondeur.md` (mémoire user) — appliqué : audit profond avant plan
- `feedback_no_hybrid_workarounds.md` — appliqué : 4 PRs structurelles, pas hybrid
- `feedback_plan_approved_means_go_to_end.md` — appliqué : plan exécuté jusqu'à merge + post-mortem
