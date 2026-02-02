# SEO Hub Refactoring - Documentation

> **Date** : 2026-01-30
> **Statut** : Phases 1-2 complétées, Phase 3 en cours

---

## Résumé Exécutif

Consolidation des 9 controllers SEO éparpillés et 6 routes frontend en un **hub unifié** accessible via `/admin/seo-hub`.

### Avant (Fragmentation)
- 9 controllers backend (admin, seo, seo-logs)
- 6 routes frontend distinctes
- 17+ tables BDD avec redondances
- KPIs calculés 3 fois différemment

### Après (Hub Unifié)
- 1 controller principal : `SeoCockpitController`
- 1 hub frontend : `/admin/seo-hub/`
- API consolidée : `/api/admin/seo-cockpit/*`

---

## Fichiers Créés

### Backend (Phase 1)

| Fichier | Description |
|---------|-------------|
| `backend/src/modules/admin/controllers/seo-cockpit.controller.ts` | Controller unifié (12 endpoints) |
| `backend/src/modules/admin/services/seo-cockpit.service.ts` | Service agrégation multi-sources |

**Endpoints API :**
```
GET  /api/admin/seo-cockpit/dashboard       # KPIs unifiés
GET  /api/admin/seo-cockpit/summary         # Résumé exécutif
GET  /api/admin/seo-cockpit/monitoring/crawl    # Activité crawl
GET  /api/admin/seo-cockpit/monitoring/index    # Changements index
GET  /api/admin/seo-cockpit/monitoring/alerts   # Alertes consolidées
GET  /api/admin/seo-cockpit/monitoring/at-risk  # URLs à risque
GET  /api/admin/seo-cockpit/content/stats       # Stats R4/R5/Blog
GET  /api/admin/seo-cockpit/audit/history       # Historique audit
GET  /api/admin/seo-cockpit/audit/stats         # Stats audit
POST /api/admin/seo-cockpit/actions/refresh-risks    # Refresh risks
POST /api/admin/seo-cockpit/actions/trigger-monitor  # Trigger monitoring
```

### Frontend (Phase 2)

| Fichier | Route | Description |
|---------|-------|-------------|
| `admin.seo-hub.tsx` | `/admin/seo-hub` | Layout avec sidebar |
| `admin.seo-hub._index.tsx` | `/admin/seo-hub` | Dashboard unifié |
| `admin.seo-hub.gammes._index.tsx` | `/admin/seo-hub/gammes` | Liste 230 gammes |
| `admin.seo-hub.gammes.$pgId.tsx` | `/admin/seo-hub/gammes/:id` | Détail gamme |
| `admin.seo-hub.monitoring.tsx` | `/admin/seo-hub/monitoring` | Crawl/Index/Alerts |
| `admin.seo-hub.content.tsx` | `/admin/seo-hub/content` | Stats R4/R5/Blog |
| `admin.seo-hub.audit.tsx` | `/admin/seo-hub/audit` | Historique actions |
| `admin.seo-cockpit.tsx` | `/admin/seo-cockpit` | Page cockpit simple (backup) |

---

## Structure Navigation

```
/admin/seo-hub/                      ← HUB UNIFIÉ
├── index.tsx                        ← Dashboard (Health Score, KPIs, Alerts)
├── gammes/
│   ├── _index.tsx                   ← Liste 230 gammes + Smart Actions
│   └── $pgId.tsx                    ← Détail gamme (6 tabs)
├── monitoring.tsx                   ← Crawl + Index + URLs at risk
├── content.tsx                      ← Stats R4 + R5 + Blog
└── audit.tsx                        ← Historique actions unifié
```

---

## Interfaces TypeScript

### DashboardKpis (Backend → Frontend)

```typescript
interface UnifiedDashboardKpis {
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
  healthScore: number;         // 0-100
  queueStats: {
    waiting: number;
    active: number;
    completed: number;
    failed: number;
  };
  totalUrls: number;
  urlsAtRisk: number;
  riskBreakdown: {
    CONFUSION: number;
    ORPHAN: number;
    DUPLICATE: number;
    WEAK_CLUSTER: number;
    LOW_CRAWL: number;
  };
  crawlHealth: {
    last24h: number;
    last7d: number;
    avgResponseMs: number;
    googlebotAbsent14d: boolean;
  };
  contentStats: {
    r4References: number;
    r5Diagnostics: number;
    blogArticles: number;
  };
}
```

### ExecutiveSummary

```typescript
interface ExecutiveSummary {
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
  healthScore: number;
  urlsAtRisk: number;
  mainIssue: string | null;
  actionRecommended: string | null;
}
```

---

## Dépendances Services

Le `SeoCockpitService` agrège les données de :

| Service Source | Module | Données |
|----------------|--------|---------|
| `SeoMonitorSchedulerService` | workers | Queue stats |
| `RiskFlagsEngineService` | seo | Risk breakdown |
| `GooglebotDetectorService` | seo | Crawl activity |
| Direct SQL | - | Content stats, Index changes |

---

## Phases Restantes

### Phase 3 : Redirections (Semaine actuelle)

Créer des redirects depuis les anciennes routes :

```typescript
// frontend/app/routes/admin.gammes-seo._index.tsx
export const loader = () => redirect('/admin/seo-hub/gammes');

// frontend/app/routes/admin.seo-dashboard.tsx
export const loader = () => redirect('/admin/seo-hub/monitoring');

// frontend/app/routes/admin.seo-content.tsx
export const loader = () => redirect('/admin/seo-hub/content');
```

### Phase 4 : Normalisation BDD (Semaine suivante)

Migrations SQL pour éliminer les redondances :

```sql
-- 1. Unifier URLs (une seule source de vérité)
ALTER TABLE __seo_entity_health DROP COLUMN IF EXISTS url;
ALTER TABLE __seo_entity_score_v10 DROP COLUMN IF EXISTS url;
-- Utiliser __seo_page.url via FK

-- 2. Unifier Risk Assessment
ALTER TABLE __seo_entity_health
ADD COLUMN risk_scores JSONB DEFAULT '{}'::jsonb;
-- Contient: orphan_score, duplicate_score, etc.
```

---

## Tests de Validation

### Tests Fonctionnels

- [ ] `/admin/seo-hub` affiche dashboard avec Health Score
- [ ] `/admin/seo-hub/gammes` liste 230 gammes (fonctions existantes)
- [ ] `/admin/seo-hub/monitoring` affiche crawl + index
- [ ] `/admin/seo-hub/content` affiche stats R4/R5/Blog
- [ ] `/admin/seo-hub/audit` affiche historique

### Tests API

```bash
# Dashboard
curl http://localhost:3000/api/admin/seo-cockpit/dashboard | jq

# Summary
curl http://localhost:3000/api/admin/seo-cockpit/summary | jq

# Monitoring
curl http://localhost:3000/api/admin/seo-cockpit/monitoring/crawl?days=7 | jq
curl http://localhost:3000/api/admin/seo-cockpit/monitoring/at-risk?limit=10 | jq

# Actions
curl -X POST http://localhost:3000/api/admin/seo-cockpit/actions/refresh-risks
```

---

## Métriques Attendues

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Endpoints API | 25+ | 12 | -52% |
| Routes Frontend | 6 | 1 hub + 5 sous-routes | Unifié |
| Temps chargement dashboard | ~3s | ~1s | -66% |
| Cohérence KPIs | 3 sources | 1 source | 100% |

---

## Prochaines Étapes Immédiates

1. Tester le hub : `npm run dev` et accéder à `/admin/seo-hub`
2. Vérifier les API endpoints avec curl
3. Ajouter les redirects des anciennes routes
4. Mettre à jour la sidebar admin pour pointer vers le hub

---

**Maintainer** : Claude AI
**Dernière mise à jour** : 2026-01-30
