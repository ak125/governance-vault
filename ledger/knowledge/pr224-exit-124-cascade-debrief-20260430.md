---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: PR #224 — Exit-124 cascade debrief (boot non-blocking + 5 collateral fixes)
slug: pr224-exit-124-cascade-debrief-20260430
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-30"
updated_by: "@fafa"
related_adr: []
related_prs:
  - "ak125/nestjs-remix-monorepo#224"
related_issues:
  - "ak125/nestjs-remix-monorepo#226"
status: current
---

# PR #224 — Exit-124 cascade debrief

> Session 2026-04-30 entre @fafa et Claude Code (Opus 4.7 1M).
> Contexte : `🔍 CWV Performance Check` (`.github/workflows/perf-gates.yml`) tombait
> systématiquement en `exit 124` après 5 min de silence backend. Le PR #224 avait
> déjà tenté 4 fixes successifs (commits `a0a67c66`, `5d503e1a`, `e489ecbe`,
> `abc6cd6a`) sans débloquer le merge.

## 1. Cause racine réelle (vs cause apparente)

**Cause apparente initiale** : services backend qui font de l'I/O Supabase distante
dans `onModuleInit` → bloque `app.listen()`. C'est ce que les 4 fixes précédents
avaient adressé en migrant 5 services (`CatalogService`, `InternalLinkingService`,
`ShippingCalculatorService`, `RagPipelineService`, `RagIngestionService`,
`MeilisearchService`, `LogIngestionService`) au pattern canonique `void this.warmer()`.

**Cause racine réelle** (établie par INIT_TRACE markers commit `abc6cd6a`) :
`backend/src/workers/worker.module.ts:46` configurait `BullModule.forRootAsync`
avec un fallback hardcodé `redis: { host: configService.get('REDIS_HOST', 'redis'), … }`.
Le literal `'redis'` est le hostname du service docker-compose en prod ; en CI
seul `REDIS_URL=redis://localhost:6379` était défini, `REDIS_HOST` non set →
fallback `'redis'` → DNS échoue sur runner GitHub Actions (services CI exposés
sur `localhost`, pas via leur nom Docker) → ioredis avec `enableOfflineQueue:true`
retry forever → tout `await emailQueue.add(...)` ou
`await seoMonitorQueue.getRepeatableJobs()` reste bloqué.

Preuves empiriques par INIT_TRACE (run `25172104783`) :
```
14:51:27.524  INIT_TRACE: shipping-calculator
14:51:27.524  INIT_TRACE: abandoned-cart           ← début hook
              [3 min 53 s de silence]
14:55:20.573  INIT_TRACE: seo-audit-scheduler      ← module suivant
14:55:20.626  INIT_TRACE: rag-change-watcher
14:55:20.626  INIT_TRACE: seo-monitor-scheduler
              [70 s]
14:56:30      exit 124
```

`Promise.all` dans `callModuleInitHook` attend toutes les promesses du module
en parallèle ; `abandoned-cart` (qui awaitait `emailQueue.add`) bloquait pendant
~4 min → modules suivants ne démarraient pas → app.listen() jamais retournait.

## 2. Lifecycle NestJS v10 — précision capitale

`NestFactory.create()` ne lance **PAS** les hooks `onModuleInit`. C'est
`app.listen()` qui les lance, via `app.init() → callInitHook()` puis
`callBootstrapHook()`. Référence : `node_modules/@nestjs/core/nest-application.js:90-103`
(version 10.4.22) :

```js
async init() {
  if (this.isInitialized) return this;
  this.applyOptions();
  await this.httpAdapter?.init();
  // ...
  await this.callInitHook();        // ← onModuleInit fire ICI
  await this.registerRouterHooks();
  await this.callBootstrapHook();   // ← onApplicationBootstrap fire ICI
  this.isInitialized = true;
  // ...
}
```

→ Tout `await` d'I/O distante dans n'importe quel `onModuleInit` bloque
`app.listen()` avant que le HTTP server bind. C'est ce que la règle ast-grep
`backend-no-remote-io-in-onmoduleinit.yml` enforce.

## 3. Cascade de 5 bugs collatéraux révélés en chaîne

Chaque fix débloquait le bug suivant — **les bugs collatéraux étaient masqués
par l'exit-124 systématique** (jamais Lighthouse n'avait tourné end-to-end en
100+ runs CI consécutifs sur ce repo, cf. `gh run list --workflow=perf-gates.yml --limit 100`).

| # | Bug | Fix structurel | Commit |
|---|-----|----------------|--------|
| 1 | `BullModule` fallback `'redis'` | Consume `REDIS_URL` puis `getAppConfig()` (host fallback `'localhost'`) | `919ba33a` |
| 2 | `Helmet CSP` retourne 500 sur toutes requêtes (`Invalid character in header content`) | `sanitizeCspSource()` strip whitespace/control chars sur env URLs (`process.env.SUPABASE_URL` avait `\n` final dans le secret GitHub) | `5a6e63b4` |
| 3 | Lighthouse 404 sur `/constructeurs/renault.html` | URL workflow corrigée en `/constructeurs/renault-140.html` (route Remix `constructeurs.$brand[.]html.tsx` exige format `{brand}-{id}`) | `74c9305e` |
| 4 | Lighthouse v10 rejette `lighthouse-budget.json` (champ `name` non-standard) | Drop `"name"` cosmétique des entrées per-path | `96fa0553` |
| 5 | Artifact upload 400 (`Create Artifact Container failed`) | `uploadArtifacts: false` (treosh action utilise `upload-artifact@v3` déprécié par GitHub 2024) ; `temporaryPublicStorage: true` suffit | `96fa0553` |
| 6 | Budgets perfs dépassés (FCP 10.7s vs 4s, LCP 11.4s vs 5s, JS 1MB vs 400KB) | **Hors scope PR #224** → issue #226 (3 axes : calibrer budgets / `/health/ready` warmer-completion / refactor frontend bundle) | n/a |

## 4. Defense-in-depth (mes commits PR #224)

### 4.1 Refactor `onModuleInit` non-bloquant pour les 2 services Bull restants

Commit `20d8e294` — même pattern canonique que les 5 services patchés
précédemment (sync `onModuleInit` + `void warmer()`) appliqué à
`AbandonedCartService` et `SeoMonitorSchedulerService`. Justification :
même si BullModule est correctement configuré (commit `919ba33a`), un
Redis lent au boot ne doit jamais hanger `app.listen()`. Le HTTP server
bind avant la registration des jobs Bull ; les premiers requests qui
arrivent avant que les schedules soient armés tombent gracefully (les
events Bull sont aussi peuplés par les actions utilisateur, pas seulement
par ces schedulers).

### 4.2 Lock contract — extension règle ast-grep

Commit `fdf691af` étend `.ast-grep/rules/backend-no-remote-io-in-onmoduleinit.yml` :

- Ajoute `this.meilisearch` et `this.httpService` à la liste des subjects
  flagés (avant : seulement `this.supabase`)
- Ajoute pattern Bull/BullMQ : `\bthis\.[A-Za-z_$][A-Za-z0-9_$]*[Qq]ueue\b`
  combiné avec method names `.(add|getRepeatableJobs|removeRepeatableByKey|
  getJob|getJobs|removeJobs|drain|empty|count|isReady)\b`

Validation : fixture 4 patterns → 4/4 hits ; codebase backend/src → 0 hits
(les 2 services patchés ne match plus, aucun faux positif).

→ La prochaine fois qu'un dev ajoute un `await this.someQueue.add(...)`
dans un `onModuleInit`, le pre-commit + CI lint refusent.

## 5. Leçons opérationnelles (méta)

### 5.1 Diagnostic empirique > spéculation statique

Le pattern `console.warn('INIT_TRACE: …')` de `abc6cd6a` (un par service avec
`onModuleInit`) a permis d'identifier en **un seul run CI** quel(s) service(s)
hangaient — alors que 4 fix précédents avaient deviné sans preuve. Recipe
réutilisable pour tout incident de boot Nest opaque :
- Insérer `console.warn('INIT_TRACE: <service-name>')` (pas Pino — bypass
  bufferLogs et stdout block-buffering Docker) au tout début de chaque
  `onModuleInit` suspect
- Run CI une fois, observer la séquence + les gaps
- Le service avant le gap est celui qui hang

### 5.2 « Fixer la cause apparente » ≠ « fixer la cause racine »

Les 4 fixes précédents ont migré 7 services au pattern non-bloquant. Tous
corrects mais aucun n'adressait la cause racine : la config Bull cassée.
Les services Bull-using (`AbandonedCartService`, `SeoMonitorSchedulerService`)
n'avaient pas été touchés parce que la règle backend.md autorisait
explicitement `await this.emailQueue.add(...)` (« BullMQ local OK »). La
règle suppose une config Bull localhost ; elle était cassée.

### 5.3 Chaque fix débloquait le suivant — never assume only one bug

Quand un gate est rouge depuis 100+ runs, il **cache potentiellement plusieurs
bugs en cascade**, pas un seul. Stratégie : fixer le bug le plus en amont
(boot), laisser la CI tourner end-to-end, observer le prochain bug, répéter.
Ne **jamais** présumer que fixer le premier bug suffira (cf. ce debrief : 6
bugs distincts, dont 1 réel hors-scope).

### 5.4 « Gate jamais vert » = signal informatif déguisé en guard

`perf-gates.yml` était configuré comme guard mais 0/100 runs success. Soit :
- Le gate était mal calibré dès le début (cas ici — budgets irréalistes pour
  runner GitHub Actions cold-start)
- Soit la régression était intervenue tôt et personne n'a tracé

Dans les deux cas le gate ne pouvait plus signaler une régression réelle car
il était déjà rouge en permanence — bruit total. Action : soit recalibrer,
soit formaliser comme non-required dans branch protection. Issue #226 ouverte.

### 5.5 Anti-bricolage strict en pratique

Validé pendant cette session : ne jamais
- Relâcher des budgets pour faire passer (masque la régression)
- Admin-merger en bypass (court-circuite le signal)
- Inventer un nom Docker pour résoudre DNS (`'redis'` → bricolage)
- Sleep arbitraire pour attendre la connexion Bull (bricolage)
- Repro local sur port alternatif (le port 3000 est canonique)

À la place :
- Aligner les conventions (BullModule lit `REDIS_URL` comme tout le reste)
- Sanitize aux frontières (`process.env` → trim avant injection dans header)
- Découpler les responsabilités (`/health` vs `/health/ready` proposé)
- Documenter les debts perf en issue séparée (scope hygiénique)

## 6. État final

- PR #224 mergée (squash `e66f2637` à 16:06:39 UTC)
- Branche `fix/cache-warm-non-blocking` supprimée côté remote
- `app.listen()` revient en ~5 s en CI (vs 5 min hang)
- Lighthouse mesure end-to-end les 3 URLs (premier succès en 100+ runs)
- Issue #226 ouverte pour la dette perf (3 axes documentés, hors scope PR #224)
- Lock contract ast-grep durci pour empêcher la récurrence

## 7. Références techniques

- `node_modules/@nestjs/core/nest-application.js:90-103` (lifecycle init/listen)
- `node_modules/@nestjs/core/hooks/on-module-init.hook.js` (Promise.all parallel)
- `node_modules/@nestjs/core/nest-factory.js:88-103` (initialize ne fait que scan + create)
- `.claude/rules/backend.md § "Non-blocking onModuleInit"` (pattern canonique)
- `.ast-grep/rules/backend-no-remote-io-in-onmoduleinit.yml` (lock contract étendu)
- `frontend/lighthouse-budget.json` (budgets actuels — calibration à faire dans #226)
- Run CI baseline (premier success Lighthouse end-to-end) : `25174518429`
- Run CI INIT_TRACE preuve : `25172104783`
