# MIGRATION PLAN — DEV / PREPROD / PROD Hardening

> **Branche**: `feat/hardening-dev-preprod-prod`
> **Créé le**: 2026-02-02
> **Dernière MAJ**: 2026-02-02

---

## Contexte & objectifs

Ce monorepo NestJS + Remix (~300k lignes) souffre de pollution runtime :
- Modules DEV importés en PROD (RmModule crash incident 2026-01-11)
- Scripts OPS dangereux sans garde-fous (75+ fichiers backend/*.js)
- Fichiers CSV de production versionnés dans git
- .dockerignore incomplet (scripts/CSV embarqués en prod)

**Objectif** : Garantir que :
1. DEV CORE démarre toujours (modules essentiels uniquement)
2. DEV FULL / PREPROD inclut le cockpit admin complet
3. PROD n'embarque JAMAIS les outils DEV

---

## Résumé de l'audit (points critiques)

| Risque | Fichier | Impact | Priorité |
|--------|---------|--------|----------|
| **CRASH PROD** | `app.module.ts:51,178` importe `RmModule` | Incident 2026-01-11 | P0 |
| **CRASH PROD** | `app.module.ts:48-50,169-175` importe AI modules | Deps Python/LLM en prod | P0 |
| **Build pollué** | `.dockerignore` incomplet | Scripts/CSV en image prod | P0 |
| **Data leak** | `backend/*.csv` versionnés | Données prod dans git | P0 |
| **Scripts dangereux** | 75+ scripts sans kill-switch | Mutation prod sans audit | P0 |

---

## Stratégie cible (barrières : import + packaging)

```
┌─────────────────────────────────────────────────────────┐
│                    BARRIÈRE 1: IMPORTS                  │
│  ESLint no-restricted-imports + CI check                │
│  apps/* ──X──> tools/*                                  │
│  apps/* ──X──> packages/ai-orchestrator                 │
│  apps/* ──X──> packages/contracts                       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 BARRIÈRE 2: PACKAGING                   │
│  .dockerignore allowlist strict                         │
│  Seuls apps/ + packages/core embarqués                  │
└─────────────────────────────────────────────────────────┘
```

---

## Profils d'exécution (dev:core / dev:full)

| Profil | Modules | Usage | Mémoire |
|--------|---------|-------|---------|
| `dev:core` | 24 modules PROD_RUNTIME | Dev rapide, CI | <512MB |
| `dev:full` | 35+ modules (+ cockpit) | PREPROD, admin | <2GB |

---

## Plan par phases

### Phase P0 — Stop risques critiques (immédiat)

| # | Action | Effort | Risque | Safe? | Statut |
|---|--------|--------|--------|-------|--------|
| P0.1 | Commenter imports RmModule dans app.module.ts | S | Low | Yes | ✅ DONE |
| P0.2 | Commenter imports AiContentModule, KnowledgeGraphModule, RagProxyModule | S | Low | Yes | ✅ DONE |
| P0.3 | Compléter .dockerignore (scripts, CSV, tools) | S | Low | Yes | ✅ DONE |
| P0.4 | Compléter .gitignore (CSV exports) | S | Low | Yes | ✅ DONE |
| P0.5 | Ajouter kill-switch aux 5 scripts OPS les plus dangereux | M | Low | Yes | ✅ DONE |

#### P0.1 — Commenter RmModule

**Fichier**: `backend/src/app.module.ts`

```diff
- import { RmModule } from './modules/rm/rm.module'; // 🏗️ NOUVEAU - Read Model pour listings optimisés !
+ // import { RmModule } from './modules/rm/rm.module'; // ⛔ DÉSACTIVÉ P0.1 - Crash prod 2026-01-11, import @monorepo/shared-types échoue en Docker

// Dans imports array:
-     RmModule, // 🏗️ ACTIVÉ - Module RM pour accès aux listings optimisés !
+     // RmModule, // ⛔ DÉSACTIVÉ P0.1 - DEV ONLY
```

**Rollback**: Décommenter les 2 lignes

---

#### P0.2 — Commenter modules AI/RAG

**Fichier**: `backend/src/app.module.ts`

```diff
- import { AiContentModule } from './modules/ai-content/ai-content.module';
+ // import { AiContentModule } from './modules/ai-content/ai-content.module'; // ⛔ DÉSACTIVÉ P0.2 - DEV ONLY (LLM deps)

- import { KnowledgeGraphModule } from './modules/knowledge-graph/knowledge-graph.module';
+ // import { KnowledgeGraphModule } from './modules/knowledge-graph/knowledge-graph.module'; // ⛔ DÉSACTIVÉ P0.2 - DEV ONLY

- import { RagProxyModule } from './modules/rag-proxy/rag-proxy.module';
+ // import { RagProxyModule } from './modules/rag-proxy/rag-proxy.module'; // ⛔ DÉSACTIVÉ P0.2 - DEV ONLY (Python dep)

// Dans imports array:
-     AiContentModule,
+     // AiContentModule, // ⛔ DÉSACTIVÉ P0.2

-     KnowledgeGraphModule,
+     // KnowledgeGraphModule, // ⛔ DÉSACTIVÉ P0.2

-     RagProxyModule,
+     // RagProxyModule, // ⛔ DÉSACTIVÉ P0.2
```

**Rollback**: Décommenter les 6 lignes

---

#### P0.3 — Compléter .dockerignore

**Fichier**: `.dockerignore`

```diff
+ # ============================================
+ # P0.3 - Exclusions DEV/TOOLING (2026-02-02)
+ # ============================================
+
+ # Scripts OPS (ne doivent jamais être en prod)
+ backend/*.js
+ backend/*.csv
+ scripts/
+
+ # Packages AI non utilisés en prod
+ packages/ai-orchestrator/
+ packages/contracts/
+
+ # Tooling Python
+ ai-agents-python/
+
+ # Claude Code skills
+ .claude/
+
+ # Specs et documentation interne
+ .spec/
+
+ # Data artifacts
+ data/external/
+ data/*.csv
+ *.csv
+
+ # UX research
+ ux-*/
+
+ # Screenshots et captures
+ screenshots/
```

**Rollback**: Supprimer le bloc ajouté

---

#### P0.4 — Compléter .gitignore

**Fichier**: `.gitignore`

```diff
+ # ============================================
+ # P0.4 - Exclusions CSV/Data (2026-02-02)
+ # ============================================
+
+ # CSV exports (Google Ads, Keyword Stats, etc.)
+ Keyword Stats*.csv
+ backend/*.csv
+ data/external/*.csv
+ *.keywords.csv
+ *_volumes.csv
+ *_trends.csv
```

**Rollback**: Supprimer le bloc ajouté

---

#### P0.5 — Kill-switch scripts OPS dangereux

**Scripts cibles** (top 5 par risque):
1. `backend/generate_all_seo_switches.js`
2. `backend/populate_seo_gamme_car_switch.js`
3. `backend/fix-seo-switches.js`
4. `backend/import_agent2_data.js`
5. `backend/recalculate-vlevel.js`

**Code à injecter en tête de chaque script**:

```javascript
// ============================================
// KILL-SWITCH PRODUCTION (P0.5 - 2026-02-02)
// ============================================
if (process.env.NODE_ENV === 'production' && process.env.ALLOW_PROD_MUTATION !== '1') {
  console.error('\\n⛔ ERREUR: Ce script ne peut pas s\\'exécuter en production.');
  console.error('   Pour forcer: ALLOW_PROD_MUTATION=1 node script.js');
  console.error('   Environnement détecté: NODE_ENV=' + process.env.NODE_ENV);
  process.exit(1);
}
// ============================================
```

**Rollback**: Supprimer le bloc en tête de chaque script

---

### Vérifications P0

```bash
# V1: RmModule non importé
grep -n "RmModule" backend/src/app.module.ts
# Attendu: lignes commentées uniquement

# V2: AI modules non importés
grep -n "AiContentModule\|KnowledgeGraphModule\|RagProxyModule" backend/src/app.module.ts
# Attendu: lignes commentées uniquement

# V3: .dockerignore contient exclusions
grep -c "backend/\*.js\|backend/\*.csv\|packages/ai-orchestrator" .dockerignore
# Attendu: >= 3

# V4: .gitignore contient exclusions CSV
grep -c "Keyword Stats\|backend/\*.csv" .gitignore
# Attendu: >= 2

# V5: Kill-switch présent dans scripts
head -15 backend/generate_all_seo_switches.js | grep -c "KILL-SWITCH"
# Attendu: 1

# V6: Build TypeScript OK
cd backend && npm run build 2>&1 | tail -5
# Attendu: pas d'erreur

# V7: Health check après restart
curl -s http://localhost:3000/health | jq .status
# Attendu: "ok"
```

---

### Phase P1 — Rendre DEV incassable

| # | Action | Effort | Risque | Safe? | Statut |
|---|--------|--------|--------|-------|--------|
| P1.1 | Créer script `npm run dev:core` | S | Low | Yes | ✅ DONE |
| P1.2 | Créer script `npm run dev:full:all` | S | Low | Yes | ✅ DONE |
| P1.3 | Ajouter ESLint import-firewall | M | Low | Yes | ✅ DONE |
| P1.4 | Ajouter CI check `core-build-only` | M | Low | Yes | ✅ DONE |
| P1.5 | Ajouter CI check `import-firewall` | M | Low | Yes | ✅ DONE |

#### P1.1-P1.2 — Scripts npm dev:core / dev:full:all

**Fichier**: `package.json`

```json
"dev:core": "turbo dev --filter=@fafa/backend --filter=@fafa/frontend",
"dev:full:all": "turbo dev"
```

#### P1.3 — ESLint Import Firewall

**Fichier**: `backend/.eslintrc.js`

Règle `no-restricted-imports` ajoutée pour bloquer:
- `**/modules/rm/**` → Crash prod 2026-01-11
- `@repo/ai-orchestrator` → DEV ONLY
- `@repo/contracts` → DEV ONLY

#### P1.4-P1.5 — CI Checks

**Fichier**: `.github/workflows/ci.yml`

Deux nouveaux jobs ajoutés:

1. **core-build**: Build uniquement les modules PROD_RUNTIME
   - Vérifie que app.module.ts ne contient pas de modules DEV
   - Bloque le deploy si modules DEV détectés

2. **import-firewall**: Vérifie les imports interdits
   - Scan de `backend/src/**/*.ts`
   - Bloque si imports vers rm/, ai-orchestrator, contracts

Ces checks sont **requis** avant le deploy PREPROD.

---

### Phase P2 — Industrialiser OPS scripts + data

| # | Action | Effort | Risque | Safe? | Statut |
|---|--------|--------|--------|-------|--------|
| P2.1 | Créer structure `tools/scripts/` | S | Low | Yes | ✅ DONE |
| P2.2 | Créer `tools/README.md` avec inventaire (76 scripts) | S | Low | Yes | ✅ DONE |
| P2.3 | Déplacer CSV vers RAG Knowledge | S | Low | Yes | ✅ DONE |
| P2.4 | Convertir top 10 scripts en migrations SQL | L | Medium | No | ⏸️ DEFERRED |

### Phase 3 — Performance & Sécurité

| Tâche | Description | Effort | Risque | Reversible | Status |
|-------|-------------|--------|--------|------------|--------|
| P3.1 | Rate Limiting endpoints sensibles | M | Low | Yes | ✅ DONE |
| P3.2 | SEO Module Decomposition | L | Medium | Yes | TODO |
| P3.3 | N+1 Query Optimization | M | Low | Yes | TODO |

#### P3.1 — Rate Limiting endpoints

**Commit**: `b381d95a`

**Fichiers créés**:
- `backend/src/common/decorators/rate-limit.decorator.ts` — 6 décorateurs
- `backend/src/common/interceptors/rate-limit-headers.interceptor.ts` — Headers X-RateLimit-*
- `backend/src/common/guards/custom-throttler.guard.ts` — Guard avec bypass admin

**Décorateurs disponibles**:
| Décorateur | Limite | Usage |
|------------|--------|-------|
| `@RateLimit(n, ttl)` | Custom | Personnalisé |
| `@RateLimitStrict()` | 5/min | Opérations coûteuses |
| `@RateLimitModerate()` | 30/min | API standard |
| `@RateLimitSitemap()` | 3/min | Génération sitemaps |
| `@RateLimitSearch()` | 20/min | Recherche full-text |

**Controllers protégés (9)**:
- Sitemap: `sitemap-v10`, `sitemap-unified`, `sitemap-streaming`, `sitemap-delta`
- Search: `search.controller.ts`
- Catalog: `catalog-gamme`, `vehicle-hierarchy`, `compatibility`, `family-gamme-hierarchy`

**Bypass automatique**: Admin users (level >= 7) + Localhost/Docker

---

#### P2.1-P2.2 — Structure tools/ et inventaire

**Fichier**: `tools/README.md`

Inventaire complet des 76 scripts avec :
- Catégorisation (SEO, V-Level, Data, Diagnostic, Deploy, Clio)
- Niveau de risque (HIGH/MEDIUM/LOW)
- Description courte
- Instructions d'usage avec kill-switch

**Note**: Les scripts restent dans `backend/` pour éviter un big bang.
Migration progressive vers `tools/scripts/` planifiée.

#### P2.3 — CSV vers RAG Knowledge

**Destination**: `/opt/automecanik/rag/knowledge/seo-data/`

Fichiers migrés depuis `backend/*.csv` :
- `gammes_keywords.csv` - Mots-clés SEO par gamme
- `gammes_seo_expert.csv` - Données SEO enrichies
- `gammes_search_volumes.csv` - Volumes de recherche
- `gammes_with_trends.csv` - Tendances Google
- `gammes_editable.csv` - Gammes éditables

Exports Google Ads dans `seo-data/google-ads/`.

**Avantage RAG** : Données accessibles pour enrichissement des réponses Claude et génération de contenu SEO.

---

## Questions ouvertes

*(Aucune pour P0 - toutes les actions sont SAFE et réversibles)*

---

## Journal de progression

| Date | Action | Résultat |
|------|--------|----------|
| 2026-02-02 | Création branche `feat/hardening-dev-preprod-prod` | ✅ OK |
| 2026-02-02 | Création plan MIGRATION_PLAN_DEV_PREPROD_PROD.md | ✅ OK |
| 2026-02-02 | P0.1 - Commenter RmModule (lignes 50-53, 172-175) | ✅ DONE |
| 2026-02-02 | P0.2 - Commenter AI modules (AiContent, KnowledgeGraph, RagProxy) | ✅ DONE |
| 2026-02-02 | P0.3 - Compléter .dockerignore (+25 lignes exclusions) | ✅ DONE |
| 2026-02-02 | P0.4 - Compléter .gitignore (+10 lignes CSV) | ✅ DONE |
| 2026-02-02 | P0.5 - Kill-switch 5 scripts OPS (generate_all_seo_switches, recalculate-vlevel, populate_seo_gamme_car_switch, fix-seo-switches, import_agent2_data) | ✅ DONE |
| 2026-02-02 | Build TypeScript backend | ✅ OK (0 erreurs) |
| 2026-02-02 | **PHASE P0 TERMINÉE** | ✅ VALIDÉE |
| 2026-02-02 | Commit P0 (`7551ea3c`) | ✅ OK |
| 2026-02-02 | P1.1 - Script `npm run dev:core` ajouté | ✅ DONE |
| 2026-02-02 | P1.2 - Script `npm run dev:full:all` ajouté | ✅ DONE |
| 2026-02-02 | P1.3 - ESLint import-firewall ajouté | ✅ DONE |
| 2026-02-02 | Commit P1 (`b1ce836b`) | ✅ OK |
| 2026-02-02 | P1.4 - CI check `core-build-only` ajouté | ✅ DONE |
| 2026-02-02 | P1.5 - CI check `import-firewall` ajouté | ✅ DONE |
| 2026-02-02 | **PHASE P1 TERMINÉE** | ✅ VALIDÉE |
| 2026-02-02 | Merge P0+P1 sur main (`431b7029`) | ✅ OK |
| 2026-02-02 | Push governance-vault (DEC-001) | ✅ OK |
| 2026-02-02 | P2.1 - Créer structure tools/scripts/ | ✅ DONE |
| 2026-02-02 | P2.2 - Créer tools/README.md (inventaire 76 scripts) | ✅ DONE |
| 2026-02-02 | Commit P2.1-P2.2 (`a0ea773e`) | ✅ OK |
| 2026-02-02 | **PHASE P2.1-P2.2 TERMINÉE** | ✅ VALIDÉE |
| 2026-02-02 | P2.3 - Déplacer CSV vers RAG Knowledge | ✅ DONE |
| 2026-02-02 | **PHASE P2.3 TERMINÉE** | ✅ VALIDÉE |
| 2026-02-02 | P3.1 - Rate Limiting endpoints (9 controllers, 6 décorateurs) | ✅ DONE |
| 2026-02-02 | Commit P3.1 (`b381d95a`) | ✅ OK |
| 2026-02-02 | **PHASE P3.1 TERMINÉE** | ✅ VALIDÉE |
