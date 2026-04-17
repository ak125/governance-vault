# Architecture - AutoMecanik

> **Source de verite** - Architecture technique au 2026-01-06
> **Version**: 2.0.0 | **Status**: CANON

---

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
│              (Navigateurs, Mobile, API externes)                │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────────────────┐
│                    CADDY (Reverse Proxy)                        │
│                    Port 80/443 → 3000                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    NESTJS + REMIX (Port 3000)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Remix SSR (Frontend)                                    │   │
│  │  • Routes, Loaders, Actions                              │   │
│  │  • React 18, Tailwind, shadcn/ui                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  NestJS API (Backend)                                    │   │
│  │  • 40 modules                                            │   │
│  │  • REST + WebSocket                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────────────────────┬───────────────┘
           │                                      │
┌──────────▼──────────┐              ┌────────────▼────────────────┐
│   REDIS (Cache)     │              │   SUPABASE (PostgreSQL)     │
│   Port 6379         │              │   • 4M+ produits            │
│   • Sessions        │              │   • 59k+ utilisateurs       │
│   • Cache API       │              │   • 9k+ categories          │
└─────────────────────┘              └─────────────────────────────┘
```

---

## Stack Technique

| Couche | Technologie | Version |
|--------|-------------|---------|
| **Frontend** | Remix + React | 2.15 + 18.3.1 |
| **Backend** | NestJS | 10.4.20 |
| **Database** | Supabase (PostgreSQL) | - |
| **Cache** | Redis | 7.x |
| **UI** | Tailwind + shadcn/ui + Radix | 3.4.15 |
| **Build** | Turbo + Vite | 2.2.3 + 5.4.11 |
| **Runtime** | Node.js | 20.x |
| **Container** | Docker | - |
| **Proxy** | Caddy | 2.x |

---

## Pattern 3-Tier (OBLIGATOIRE)

Chaque module NestJS suit cette architecture stricte :

```
┌─────────────────────┐
│    Controller       │  ← Validation HTTP (Zod)
│    (HTTP Layer)     │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│    Service          │  ← Business Logic
│    (Logic Layer)    │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│    DataService      │  ← Supabase SDK direct
│    (Data Layer)     │
└─────────────────────┘
```

**Regles :**
- Controller → Service uniquement (jamais DB direct)
- Service → DataService uniquement
- DataService → Supabase SDK (PAS de Prisma)

---

## Flux de donnees

### Requete Page (SSR)

```
1. Client → Caddy (HTTPS)
2. Caddy → NestJS:3000
3. NestJS → RemixModule
4. Remix Loader → API interne (localhost)
5. API → Supabase (requete DB)
6. Supabase → API (data)
7. API → Remix (JSON)
8. Remix → HTML rendu
9. NestJS → Caddy → Client
```

### Requete API

```
1. Client → /api/*
2. NestJS Controller (validation Zod)
3. Service (business logic)
4. DataService → Supabase
5. Response JSON
```

---

## Modules Backend (par domaine)

### Core
| Module | Role |
|--------|------|
| `ConfigModule` | Variables environnement |
| `HealthModule` | Health checks |
| `SystemModule` | Monitoring |
| `ErrorsModule` | Gestion erreurs |
| `CacheModule` | Redis cache |
| `CryptoModule` | Hashing (bcrypt) |

### Authentification
| Module | Role |
|--------|------|
| `AuthModule` | Login/Logout, Sessions |
| `UsersModule` | Gestion utilisateurs |
| `StaffModule` | Personnel interne |

### Catalogue
| Module | Role |
|--------|------|
| `ProductsModule` | Produits (4M+) |
| `CatalogModule` | Categories, filtres |
| `VehiclesModule` | Marques, modeles, types |
| `GammeRestModule` | API gammes produits |

### Commerce
| Module | Role |
|--------|------|
| `CartModule` | Panier |
| `OrdersModule` | Commandes |
| `PaymentsModule` | Paiements (Paybox, SystemPay) |
| `InvoicesModule` | Factures |
| `PromoModule` | Codes promo |
| `CommercialModule` | Ventes |

### Logistique
| Module | Role |
|--------|------|
| `ShippingModule` | Livraisons |
| `SuppliersModule` | Fournisseurs |
| `CustomersModule` | Clients B2B |

### Contenu
| Module | Role |
|--------|------|
| `BlogModule` | Articles blog |
| `SeoModule` | Meta, sitemap, schema.org |
| `AiContentModule` | Generation IA |

### Search & AI
| Module | Role |
|--------|------|
| `SearchModule` | Recherche produits |
| `KnowledgeGraphModule` | Knowledge Graph v2.8 |
| `RagProxyModule` | Proxy vers service RAG |

---

## Base de donnees (Supabase)

### Tables principales

| Prefixe | Domaine | Exemples |
|---------|---------|----------|
| `__products` | Catalogue | produits, variantes |
| `__orders` | Commerce | commandes, lignes |
| `__users` | Auth | utilisateurs, sessions |
| `__seo_*` | SEO | meta, redirects |
| `__blog_*` | Contenu | articles, categories |

### Fonctions RPC

- `get_bestsellers(limit, category_id)`
- `search_products(query, filters)`
- `get_vehicle_compatibility(product_id)`

---

## Sessions & Auth

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   NestJS    │────▶│   Redis     │
│ (Cookie)    │     │ (Passport)  │     │ (Sessions)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Supabase   │
                    │  (Users)    │
                    └─────────────┘
```

- **Cookie**: `connect.sid` (HttpOnly, SameSite: lax)
- **TTL**: 30 jours
- **Strategy**: Passport Local

---

## Paiements

### Gateways

| Gateway | Usage | Signature |
|---------|-------|-----------|
| **Paybox** | Production | HMAC-SHA512 |
| **SystemPay** | Test | HMAC-SHA256 |

### Flux

```
1. Order created
2. Redirect to gateway
3. User pays
4. Gateway callback → /api/payments/*/callback
5. Signature verified (HMAC)
6. Order status updated
7. Redirect success/error
```

---

## Tests

### Strategie

| Type | Outil | Usage |
|------|-------|-------|
| API | `curl` | Tests manuels endpoints |
| E2E | Playwright | Tests bout-en-bout |
| Composants | @testing-library/react | Tests unitaires React |

**PAS de Jest, PAS de Vitest**

### Commandes

```bash
# Tests API avec curl
curl -X GET http://localhost:3000/api/products/123 | jq

# Tests E2E
cd frontend && npm run test:a11y
cd frontend && npm run test:visual

# Tests composants
# Via @testing-library/react dans Playwright
```

---

## Deploiement

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Stack Docker

| Service | Image | Port |
|---------|-------|------|
| `app` | `nestjs-remix-monorepo` | 3001 (interne) |
| `caddy` | `caddy:2` | 80, 443 |
| `redis` | `redis:7-alpine` | 6379 |

### CI/CD

- **Trigger**: Push sur `main` (validation manuelle obligatoire)
- **Runner**: Self-hosted Linux
- **Pipeline**: Lint → TypeCheck → Build → Deploy

---

_Derniere mise a jour: 2026-01-06_
_Status: CANON - Source de verite_
