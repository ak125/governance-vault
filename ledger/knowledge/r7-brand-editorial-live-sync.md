---
type: knowledge
scope: backend/seo/r7
surface: R7_BRAND
date: 2026-04-21
owner: Fafa
pr: https://github.com/ak125/nestjs-remix-monorepo/pull/86
tags: [r7, editorial, rag, wikidata, architecture, no-bricolage]
---

# R7 Brand — Editorial Live-Sync + Canonical RAG

> **PR** : #86 nestjs-remix-monorepo — `feat/r7-brand-editorial-live-sync`
> **Date** : 2026-04-21

---

## Contexte

Audit initial des 36 pages R7 constructeur : 100% boilerplate en DB malgré un RAG existant. Trois défauts structurels cumulés :

1. **Mismatch frontmatter/enricher** : les 36 `.md` utilisaient `pays`, `groupe`, l'enricher lisait `country`, `group` → **0% injection RAG effective**
2. **Scraping HTML** avec regex fragiles pour extraire country/group (récupérait "Turin" au lieu d'"Italie", "BlackRock" au lieu du groupe)
3. **Friction curation éditoriale** : 3 étapes manuelles (`PUT editorial` → script Python → API batch) → personne ne le ferait → FAQ identique pour toutes marques indéfiniment

## Architecture livrée

### Une source canonique par champ

| Champ | Source | Justification |
|-------|--------|---------------|
| `country`, `founded_year`, `group`, `headquarters`, `logo_uri` | **Wikidata SPARQL** (P17/P571/P749/P159/P154) | Structuré, CC0, filtrage P31/P279 pour exclure actionnaires |
| `top_models`, `top_engines` | **DB RPC** `get_brand_bestsellers_optimized` + agrégation client | Déjà en DB TecDoc, pas de scraping |
| `history` | **Wikipedia REST** `/api/rest_v1/page/summary` | Prose propre, pas de regex HTML |
| `faq`, `common_issues`, `maintenance_tips` | **Table DB** `__seo_brand_editorial` (live) | Curé humain via admin UI, éditable sans rebuild |

### Séparation des sources dans le stockage

```
┌─ /rag/knowledge/constructeurs/{alias}.md ─┐   ┌─ __seo_brand_editorial ─┐
│  Frontmatter YAML (stable)                │   │  JSONB (éditable live)  │
│  - Wikidata facts                         │   │  - faq                  │
│  - DB top_models/top_engines              │   │  - common_issues        │
│  - Wikipedia history                      │   │  - maintenance_tips     │
│  Rafraîchi : script à la demande          │   │  Curé : admin UI        │
└───────────────────────────────────────────┘   └─────────────────────────┘
                       ↓                                      ↓
                       └────────┬─────────────────────────────┘
                                ↓
                 R7BrandEnricherService.enrichSingle()
                                ↓
                       __seo_r7_pages (rendered_json.blocks[])
                                ↓
                       /constructeurs/{alias}-{id}.html
```

### Flow de curation — 1 clic

```
PUT /api/admin/r7/editorial/:marqueId
  1. Zod validate payload
  2. Upsert __seo_brand_editorial
  3. Auto-trigger R7BrandEnricherService.enrichSingle(marqueId)
  4. Merge editorial live dans brandRag (pas via .md)
  5. Compose 11 blocs R7
  6. Upsert __seo_r7_pages + versions + fingerprints
  7. Retour : { editorial, enrichment: {decision, score} }
```

Query param `?skipEnrich=true` pour batch imports sans auto-enrich.

## Patterns appliqués

### 1. Schéma Zod canonique exporté

```ts
// backend/src/config/brand-rag-frontmatter.schema.ts
export const BrandRagFrontmatterSchema = z.object({
  slug: z.string().regex(/^[a-z0-9]+(-[a-z0-9]+)*$/),
  brand_id: z.number().int().positive(),
  country: z.string().min(2).optional(),
  top_models: z.array(BrandTopModelSchema).max(20).default([]),
  source_of_truth: BrandSourceOfTruthSchema,
  lifecycle: BrandLifecycleSchema,
  // ...
});
export function safeParseBrandRagFrontmatter(raw: unknown) {
  return BrandRagFrontmatterSchema.safeParse(raw);
}
```

Validator dans `loadBrandRag` : `safeParse` + warn + fallback empty si invalide (fail-safe, pas plantage).

### 2. SPARQL avec filtre P31 pour exclure personnes physiques

```sparql
OPTIONAL {
  ?entity wdt:P749 ?parent .
  FILTER(?parent != ?entity)
}
```

Volontairement **pas de P127** (owned by) : remonte BlackRock & actionnaires institutionnels sur sociétés cotées. Seul P749 (parent organization) est autorisé.

### 3. Merge editorial live dans l'enricher

```ts
const brandRag: BrandRagData = this.loadBrandRag(brandAlias);
const editorialRow = await this.editorial.findOne(marqueId).catch(() => null);
if (editorialRow) {
  brandRag.faq = editorialRow.faq;
  brandRag.common_issues = editorialRow.common_issues;
  brandRag.maintenance_tips = editorialRow.maintenance_tips;
}
```

Pas de resync `.md` ↔ DB à gérer. Le `.md` ne contient que des facts. L'éditorial est lu JIT au runtime.

### 4. Table DB pour contenu curé + RLS

```sql
CREATE TABLE __seo_brand_editorial (
  marque_id      integer PRIMARY KEY REFERENCES auto_marque,
  faq            jsonb NOT NULL DEFAULT '[]',
  common_issues  jsonb NOT NULL DEFAULT '[]',
  maintenance_tips jsonb NOT NULL DEFAULT '[]',
  curated_by     text,
  updated_at     timestamptz DEFAULT now()
);
-- RLS : SELECT public, write service_role only
```

Écriture côté controller via `IsAdminGuard`, lecture publique pour compat éventuelle frontend.

### 5. Script Python sans scraping

- Wikidata SPARQL (pas d'HTML)
- Wikipedia REST `/api/rest_v1/page/summary` (pas d'HTML parsing)
- Supabase PostgREST (pas de RPC custom)
- Validation structurelle avant écriture
- Préserve le body markdown existant

## Preuves runtime

| Test | Avant | Après |
|------|-------|-------|
| Couverture `.md` valide | 0/36 (`country` mal mappé) | 36/36 Zod-valid |
| PUBLISH en DB | 36/36 boilerplate | 36/36 enrichies |
| `diversity_score` moyen | 79.40 | 80.86 |
| PUT Alfa Romeo (2 FAQ custom) | — | 80.86 → **85.41** en 1 appel |
| Contenu `S9_FAQ` Alfa Romeo | 5 Q/R identiques pour toutes marques | Multiair, plaque constructeur (spécifique) |
| Contenu `S11_ABOUT` Alfa Romeo | Boilerplate identique | Prose Wikipedia "fondé 1910 à Milan, Stellantis depuis 2021" |
| Frontend `/constructeurs/bmw-33.html` | 5 blocs rendus | 7 blocs (+ S3_SHORTCUTS, + S11_ABOUT) |

## Règles dérivées (candidates canon)

1. **Une source par champ** — pas de fallback "Wikipedia sinon scraping sinon LLM". Si la source canonique manque, le champ reste vide.
2. **Séparer factuel et éditorial** — facts stables (Wikidata/DB) → fichier versionné ; contenu curé humain → table DB éditable live.
3. **Friction zéro pour la curation** — si un workflow demande 3 étapes séparées pour publier, il ne sera jamais utilisé. Auto-trigger les étapes aval du controller.
4. **Zod validator à la frontière I/O** — tous les payloads externes (API, YAML, JSON) passent par un schema typé. Fail-safe (warn + fallback) côté lecture, throw côté écriture.
5. **SPARQL > scraping HTML** — quand une source structurée existe (Wikidata), l'utiliser même si Wikipedia extrait quelques champs similaires. Regex HTML = dette immédiate.

## Dette résiduelle (PR polish futur)

- S2 composer : "constructeur automobile **Italie**" au lieu de "italien" (adjectif par pays)
- S3_SHORTCUTS URLs : pointent vers `/constructeurs/{alias}/` au lieu de page modèle spécifique
- Admin UI frontend pour `__seo_brand_editorial` (endpoints REST prêts, UI à faire)
- Résolution QID Wikidata via `wbsearchentities` : 2 overrides manuels (`volkswagen`, `toyota`) pour désambiguïser groupe vs marque

## Références

- PR : https://github.com/ak125/nestjs-remix-monorepo/pull/86
- Schéma : [`backend/src/config/brand-rag-frontmatter.schema.ts`](https://github.com/ak125/nestjs-remix-monorepo/blob/feat/r7-brand-editorial-live-sync/backend/src/config/brand-rag-frontmatter.schema.ts)
- Table migration : `backend/supabase/migrations/20260420_seo_brand_editorial_table.sql`
- Build script : `scripts/rag/build-brand-rag.py`
- Liée : PR #14 (vault, patterns frontend du même refactor)
