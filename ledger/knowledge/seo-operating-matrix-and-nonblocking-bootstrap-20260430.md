---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: SEO Operating Matrix (PR #222) + non-blocking onModuleInit pattern (PR #224)
slug: seo-operating-matrix-and-nonblocking-bootstrap-20260430
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-30"
updated_by: "@fafa"
related_adr: []
related_prs:
  - "ak125/nestjs-remix-monorepo#222"
  - "ak125/nestjs-remix-monorepo#224"
  - "ak125/nestjs-remix-monorepo#227"
status: current
---

# Session 2026-04-30 — SEO Operating Matrix + non-blocking `onModuleInit`

> Session entre @fafa et Claude Code (Opus 4.7 1M). Deux livrables structurels
> orthogonaux issus du même fil : un service de gouvernance SEO en lecture
> seule (matrice agents × registry × catalog) et un pattern d'init non-bloquant
> codifié + verrouillé par ast-grep.

## 1. Objectif initial — SEO Agent Operating Matrix (PR #222)

### Contexte
Le monorepo possède déjà un système de gouvernance fort (Write Guard,
`EXECUTION_REGISTRY`, `FIELD_CATALOG` avec auto-derivation `deriveWriteScope`).
Manquait un **lens humain** : une vue scannable qui croise registry × catalog ×
inventaire `.claude/agents/` pour exposer qui écrit où, sans wildcard, sans
copier-coller, et sans nouvelle source de vérité.

### Décision d'architecture (anti-bricolage)
- **Une seule source** : `OperatingMatrixService` (NestJS, co-localisé avec
  `WriteGuardModule` dans `backend/src/config/`). Le service réutilise
  `deriveWriteScope`, `GROUP_TABLE_MAP`, `ROLE_ID_LIST` — zéro re-parsing.
- **JSON committé strictement déterministe** — pas de `generatedAt`, ordre
  clés stable via helper `canonicalize()` 8 lignes inline (pas de dep
  `json-stable-stringify`).
- **R5 prod-safe** : `NODE_ENV=production` skippe le scan filesystem
  `.claude/agents/` (pas embarqué en image Docker). Override via
  `OPERATING_MATRIX_SCAN_AGENTS=1`.
- **R2 mapping strict + disambiguation par suffixe** : `r3-conseils-validator`
  → `R3_CONSEILS`, `r6-guide-achat-validator` → `R6_GUIDE_ACHAT`,
  `r6-support-validator` → `R6_SUPPORT`. Filenames sans suffixe canonique
  (`r3-keyword-planner`) restent `UNKNOWN` par design.
- **Hash sur fichiers TS bruts** (`fs.readFileSync` UTF-8) — jamais
  `JSON.stringify(obj)` (instable).

### Findings opérationnels exposés par la matrice
1. **Gaps** : `R0_HOME` (2 agents), `R6_SUPPORT` (1 agent), `R7_BRAND` (4
   agents) écrivent hors `EXECUTION_REGISTRY` → non gouvernés par WriteGuard.
2. **Anomaly** : `R3_GUIDE` marqué `@deprecated` dans `role-ids.ts` mais
   toujours présent dans `EXECUTION_REGISTRY`.
3. **Naming hygiene** : 15 agents (`agentic-*`, `r3-keyword-*`, `r6-image-prompt`,
   etc.) restent en `unmappableAgents` — disambiguation manuelle requise.

### Fichiers livrés (purement additifs)
- `backend/src/config/operating-matrix.{types,service,module}.ts`
- `backend/src/config/operating-matrix.service.test.ts` (23 tests)
- `scripts/seo/dump-agent-matrix.ts` (CLI standalone, `npx tsx`)
- `audit-reports/seo-agent-matrix.{md,json}`

Pas de wiring dans `AdminModule` ni `WriteGuardModule.onModuleInit` —
chaque intégration = décision séparée (`formatBootLog()` est prête mais
non câblée pour préserver le boot invariant existant byte-pour-byte).

## 2. Détour technique — non-blocking `onModuleInit` (PR #224 mergée)

### Cause racine du flake CWV `exit 124`
Plusieurs services faisaient `await this.<remote-io>(...)` dans
`onModuleInit`. NestJS exécute tous les `onModuleInit` **sérialement durant
`app.listen()`**. Sur runner CI à froid (Supabase distant + Meilisearch
inexistant + Bull cold path), un seul hook bloque suffisamment longtemps
pour que `/health` reste muet 60-280s → exit 124 sur `perf-gates.yml`.

### Services convertis au pattern non-bloquant
| Service | Bloquait via |
|---|---|
| `CatalogService` | `preloadMainCategories + preloadAutoBrands + preloadGlobalStats` |
| `InternalLinkingService` | `preloadGammeCarSwitches + preloadPopularGammes` (≈176 gammes) |
| `ShippingCalculatorService` | preload Supabase |
| `RagPipelineService` / `RagIngestionService` | warmup remote RAG endpoint |
| `MeilisearchService` / `LogIngestionService` | `index.updateSettings()` HTTP vers `localhost:7700` (Meilisearch absent en CI) |
| Services Bull-backed | enqueue scheduler jobs sur Redis cold |

### Pattern canonique (codifié dans `.claude/rules/backend.md`)
```ts
@Injectable()
export class MyService implements OnModuleInit {
  onModuleInit(): void {
    this.logger.log('🚀 Init MyService — travail différé en arrière-plan');
    void this.warmCache();
  }

  private async warmCache(): Promise<void> {
    try {
      await this.supabase.from('foo').select('*');
      // ...
    } catch (e) {
      this.logger.error('warm failed:', e);
    }
  }
}
```

### Verrou structurel (anti-régression)
- **Règle** : `.claude/rules/backend.md` § "Non-blocking onModuleInit".
- **Garde mécanique** : `.ast-grep/rules/backend-no-remote-io-in-onmoduleinit.yml`
  (severity `error`) bloque tout `await this.supabase.*`, `await fetch()`,
  Bull/Meilisearch/HTTP dans un `onModuleInit`. Exécutée par `.husky/pre-commit`
  + job lint en CI.
- **Cas d'admin path qui veut attendre** : extraire la logique dans une
  méthode `warmCache()` privée, l'appeler `void warmCache()` depuis
  `onModuleInit` (fire-and-forget) et `await this.warmCache()` depuis
  `refreshCache()` ou équivalent (pattern utilisé par `InternalLinkingService`).

### PRs annexes du fil CWV (toutes mergées via #224)
- BullMQ alignée sur `REDIS_URL` cohérent
- CSP sources sanitize (whitespace/control chars)
- Lighthouse URLs corrigées + budgets calibrés sur baseline mesurée
- `uploadArtifacts: false` (treosh action utilise `actions/upload-artifact@v3`
  déprécié — `temporaryPublicStorage: true` suffit)

### PR séparée pour les permissions perf-gates (`fix/perf-gates-permissions`)
La permission `pull-requests: write` requise par le step "Comment PR" + le
self-trigger paths du workflow sur lui-même ont été extraits dans une PR
dédiée propre (commit `351b585d`). Pattern correct : tout fix de workflow
doit ajouter `.github/workflows/<name>.yml` à son propre `paths:` trigger
sinon les changements ne sont jamais re-validés sur la PR qui les introduit.

## 3. Anti-patterns documentés
- ❌ Bumper le timeout `300 → 600s` dans le workflow (band-aid)
- ❌ Admin-merge avec bypass des gates CI
- ❌ Re-runner sans diagnostic (loterie sur la charge runner)
- ❌ Inventer un nouveau script qui re-parse les constants TypeScript
  (2e source de vérité divergeable)
- ❌ Ajouter une dépendance externe (`json-stable-stringify`) pour
  remplacer 8 lignes de helper inline

## 4. État final session
- **PR #224 MERGED** sur main (`e66f2637`) — cache-warm fix end-to-end
- **PR #222 OPEN** — matrix rebasée sur main (`b7230225`), CI démarre,
  CWV doit passer nativement (cause racine éliminée)
- **PR #227 OPEN** — `perf(home): warm homepage:families cache key` (suite
  optimisation cache, hors scope matrix)
- **`fix/perf-gates-permissions` OPEN** — permissions GHA + self-trigger
  workflow paths (cleanup CI)

## 5. Reprise en nouvelle session
1. Vérifier que CI sur PR #222 passe (CWV en particulier — désormais natif
   grâce au cache-warm fix mergé).
2. Une fois verte, merger #222 (squash, branch protection respectée).
3. Optionnel : ouvrir une PR follow-up pour les findings opérationnels
   exposés par la matrice (R0_HOME / R6_SUPPORT / R7_BRAND non gouvernés,
   R3_GUIDE deprecated dans registry).
4. Optionnel : wirer `OperatingMatrixModule` dans `AdminModule` pour
   exposer l'endpoint REST + page admin Remix consommatrice.

## 6. Références
- `nestjs-remix-monorepo#222` — feat: SEO Agent Operating Matrix
- `nestjs-remix-monorepo#224` — fix: non-blocking cache-warm
- `nestjs-remix-monorepo#227` — perf: warm homepage:families cache
- Plan détaillé : `~/.claude/plans/verifier-analyse-plus-delegated-globe.md`
- Rule : `.claude/rules/backend.md` § Non-blocking onModuleInit
- Enforcer : `.ast-grep/rules/backend-no-remote-io-in-onmoduleinit.yml`
