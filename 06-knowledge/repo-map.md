# Repo Map - AutoMecanik Monorepo

> **Source de verite** - Structure reelle du code au 2026-01-06
> **Version**: 2.0.0 | **Status**: CANON

---

## Vue d'ensemble

```
/opt/automecanik/app/
├── backend/          # NestJS API (40 modules)
├── frontend/         # Remix SSR (158 routes)
├── packages/         # 9 packages partages
├── .spec/            # Documentation technique
├── scripts/          # Scripts utilitaires
└── docs/             # Documentation publique
```

**Note**: Le corpus RAG est dans `/opt/automecanik/rag/knowledge/` (15 docs).

---

## Backend - NestJS API

**Chemin**: `backend/src/modules/`
**Total**: 40 modules

### Modules par domaine

| Domaine | Modules |
|---------|---------|
| **Core** | `config`, `health`, `system`, `errors`, `cache` |
| **Auth** | `auth`, `users`, `staff` |
| **Catalog** | `products`, `catalog`, `vehicles`, `gamme-rest` |
| **Commerce** | `cart`, `orders`, `payments`, `invoices`, `promo`, `commercial` |
| **Logistics** | `shipping`, `suppliers`, `customers` |
| **Content** | `blog`, `blog-metadata`, `seo`, `seo-logs`, `ai-content` |
| **Support** | `messages`, `support` |
| **Analytics** | `analytics`, `dashboard` |
| **Search** | `search`, `knowledge-graph`, `rag-proxy` |
| **Media** | `upload`, `metadata` |
| **Navigation** | `navigation`, `layout` |
| **Admin** | `admin` |

### Liste complete

```
admin          ai-content     analytics      auth
blog           blog-metadata  cache          cart
catalog        commercial     config         customers
dashboard      errors         gamme-rest     health
invoices       knowledge-graph layout        messages
metadata       navigation     orders         payments
products       promo          rag-proxy      search
seo            seo-logs       shipping       staff
suppliers      support        system         upload
users          vehicles
```

---

## Frontend - Remix SSR

**Chemin**: `frontend/app/`
**Routes**: 158 fichiers

### Structure

```
frontend/app/
├── routes/           # 158 routes Remix (flat routes)
├── components/       # Composants React
│   ├── ui/          # shadcn/ui components
│   └── ...          # Composants metier
├── services/         # Services API
├── stores/           # Zustand stores
├── hooks/            # React hooks
├── utils/            # Utilitaires
└── styles/           # CSS/Tailwind
```

### Routes principales

| Pattern | Description |
|---------|-------------|
| `_index.tsx` | Homepage |
| `admin.*` | Dashboard admin |
| `panier.*` | Pages panier |
| `pieces.*` | Catalogue produits |
| `api.*` | API routes Remix |

---

## Packages partages

**Chemin**: `packages/`
**Total**: 9 packages

| Package | Description |
|---------|-------------|
| `@repo/database-types` | Types Supabase generes |
| `@monorepo/shared-types` | Types TypeScript + Zod schemas |
| `@fafa/ui` | Composants React (Radix + Tailwind) |
| `@fafa/design-tokens` | Design system tokens |
| `@fafa/typescript-config` | tsconfig partage |
| `@fafa/eslint-config` | ESLint rules partagees |
| `theme-admin` | Theme admin dashboard |
| `theme-vitrine` | Theme vitrine publique |
| `patterns` | Patterns reutilisables |

---

## Configuration

### Fichiers racine

| Fichier | Role |
|---------|------|
| `package.json` | Dependencies monorepo |
| `turbo.json` | Pipeline Turbo |
| `Dockerfile` | Build production |
| `docker-compose.prod.yml` | Stack production |
| `CLAUDE.md` | Instructions Claude Code |

### Docker Compose disponibles

- `docker-compose.prod.yml` - Production
- `docker-compose.dev.yml` - Developpement
- `docker-compose.caddy.yml` - Reverse proxy
- `docker-compose.redis.yml` - Cache Redis
- `docker-compose.meilisearch.yml` - Search engine
- `docker-compose.vector.yml` - Vector DB
- `docker-compose.worker.yml` - Workers

---

## Statistiques

| Metrique | Valeur |
|----------|--------|
| Backend modules | 40 |
| Frontend routes | 158 |
| Shared packages | 9 |
| Docker configs | 7 |
| Produits DB | 4M+ |
| Utilisateurs | 59k+ |
| Categories | 9k+ |

---

## Chemins critiques

```
backend/src/main.ts              # Bootstrap NestJS
backend/src/app.module.ts        # Root module
frontend/app/root.tsx            # Remix root
frontend/app/routes/_index.tsx   # Homepage
packages/shared-types/src/       # Types partages
```

---

## RAG Corpus (externe)

**Chemin**: `/opt/automecanik/rag/knowledge/`
**Total**: 15 documents

Voir `.spec/bmad/output/rag_diagnosis.md` pour details.

---

_Derniere mise a jour: 2026-01-06_
_Status: CANON - Source de verite_
