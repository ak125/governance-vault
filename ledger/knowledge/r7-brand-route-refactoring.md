---
type: knowledge
scope: frontend/routes
surface: R7_BRAND
route: /constructeurs/{alias}-{id}.html
date: 2026-04-20
owner: Fafa
tags: [refactoring, frontend, remix, seo, r7, patterns]
---

# R7 Brand Route — Refactoring Pattern

> **Fichier** : `frontend/app/routes/constructeurs.$brand[.]html.tsx`
> **Surface SEO** : R7 — Hub marque constructeur
> **Date** : 2026-04-20

---

## Contexte

La route R7 (page catalogue constructeur, ex : `/constructeurs/alfa-romeo-13.html`) contenait :

- 11 occurrences de `any` sur les blocks R7 enrichis
- 12 appels `.find()` redondants sur le même tableau
- 6 occurrences hardcodées du domaine `https://www.automecanik.com`
- Magic strings `R7_S2_MICRO_SEO`, `R7_S7_COMPATIBILITY`…
- Trust badges dupliqués (4 × `<div>` quasi identiques)
- Mapping logo no-op (`"alfa-romeo": "alfa-romeo"`)
- Import mort (`RelatedBrandsSection as _RelatedBrandsSection`)
- Interface morte (`_PopularPart`)

## Patterns appliqués

### 1. Typage des blocks R7 (anti-`any`)

```ts
interface R7Block {
  id: string;
  type: string;
  title: string;
  renderedText: string;
}
```

### 2. Map O(1) au lieu de `.find()` répétés

```ts
const r7Blocks: R7Block[] = r7Content?.rendered_json?.blocks || [];
const r7ById = new Map(r7Blocks.map((b) => [b.id, b]));
const r7MicroSeo = r7ById.get(R7_BLOCK_ID.MICRO_SEO);
const r7Compat = r7ById.get(R7_BLOCK_ID.COMPATIBILITY);
// …
```

### 3. Bloc de constantes centralisé

```ts
const SITE_URL = "https://www.automecanik.com";
const BRAND_LOGO_BASE_PATH = "/img/uploads/constructeurs-automobiles/marques-logos";
const DEFAULT_BRAND_IMG = "/images/default-brand.png";
const DEFAULT_VEHICLE_IMG = "/images/default-vehicle.png";
const DEFAULT_PART_IMG = "/images/default-part.png";

const R7_BLOCK_ID = {
  MICRO_SEO: "R7_S2_MICRO_SEO",
  COMPATIBILITY: "R7_S7_COMPATIBILITY",
  SAFE_TABLE: "R7_S8_SAFE_TABLE",
  FAQ: "R7_S9_FAQ",
  RELATED: "R7_S10_RELATED",
} as const;

const SCHEMA_LIMITS = { VEHICLES: 10, PARTS: 8 } as const;
const DISPLAY_LIMITS = { RELATED_BRANDS: 8 } as const;
const CACHE_HEADERS = {
  DEFAULT: "public, max-age=300, stale-while-revalidate=3600",
  GONE_410: "public, max-age=3600",
} as const;

function getBrandLogoUrl(alias: string, absolute = false): string {
  const logoAlias = LOGO_ALIAS_OVERRIDES[alias] ?? alias;
  const path = `${BRAND_LOGO_BASE_PATH}/${logoAlias}.webp`;
  return absolute ? `${SITE_URL}${path}` : path;
}
```

### 4. Badges data-driven

```ts
interface TrustBadge {
  icon: LucideIcon;
  label: string;
  iconColor: string;
}

const TRUST_BADGES: ReadonlyArray<TrustBadge> = [
  { icon: Car, label: "400 000+ pièces", iconColor: "text-green-300" },
  { icon: Settings, label: "Livraison 24-48h", iconColor: "text-blue-300" },
  { icon: Wrench, label: "Paiement sécurisé", iconColor: "text-purple-300" },
  { icon: Zap, label: "Experts gratuits", iconColor: "text-orange-300" },
];
```

### 5. Extraction de sous-composants R7

- `R7CompatibilitySection({ block })` — parse markdown → 3 étapes
- `R7SafeTableSection({ block })` — parse table pipe `| col1 | col2 |`
- `R7FaqSection({ block })` — parse `**Q**\nA` en `<details>`

Parsing markdown sorti du JSX → fonction pure testable + rendu propre.

## Dette résiduelle

| Item | Raison |
|------|--------|
| `SITE_URL` dupliqué avec `utils/seo/pieces-schema.utils.ts` | À centraliser dans `frontend/app/config/site.ts` (refactor dédié) |
| FAQ / HowTo JSON-LD : copy marketing templated dans la route | Meilleure place = API backend (hors scope) |
| Parsing markdown client-side pour blocks R7 | Fragile, meilleur format = JSON structuré côté API |
| `defer()` utilisé sans promesse différée | Peut passer en `json()` ou retour direct (hors scope) |

## Règles dérivées (candidates canon)

1. **Zéro `any` sur données API typées** — si le contrat de réponse est connu (ex : `brandApi.getR7Content`), créer une interface locale plutôt qu'utiliser `any`.
2. **Map pour lookups répétés** — `.find()` appelé ≥ 2 fois sur le même tableau = signal pour passer en `Map`.
3. **Magic strings = constantes** — tout identifiant de block SEO (`R*_S*_*`) doit venir d'une constante typée `as const`.
4. **Domaine jamais hardcodé** — utiliser `SITE_URL` (à extraire dans `frontend/app/config/site.ts`).
5. **UI répétée ≥ 3 fois = array + map** — badges, cards, items similaires.

## Références

- Route modifiée : [`constructeurs.$brand[.]html.tsx`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/frontend/app/routes/constructeurs.%24brand%5B.%5Dhtml.tsx)
- API R7 : `brandApi.getR7Content(marqueId)` → `services/api/brand.api.ts:914`
- Types : `frontend/app/types/brand.types.ts`
- Pipeline R7 : `r7-keyword-planner` → `r7-brand-rag-generator` → `r7-brand-validator`
