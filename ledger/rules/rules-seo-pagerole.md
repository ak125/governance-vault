# SEO PageRole Rules

> Règles de validation des PageRoles pour le CI et l'audit SEO.

---

## R-SEO-01: PageRole Obligatoire

**Règle**: Chaque route frontend DOIT avoir un `handle.pageRole` défini.

```typescript
// ✅ Correct
export const handle = {
  pageRole: PageRole.R2_PRODUCT,
};

// ❌ Incorrect
export const handle = {}; // Missing pageRole
```

**CI Check**: Bloque la PR si une route n'a pas de pageRole.

---

## R-SEO-02: Pattern URL Cohérent

**Règle**: Le PageRole DOIT correspondre au pattern URL.

| Pattern | Role Attendu |
|---------|--------------|
| `/pieces/{gamme}.html` | R1_ROUTER |
| `/pieces/{g}/{m}/{mo}/{t}.html` | R2_PRODUCT |
| `/blog-pieces-auto/*` | R3_BLOG |
| `/reference-auto/{slug}` | R4_REFERENCE |
| `/diagnostic-auto/{slug}` | R5_DIAGNOSTIC |
| `/support/*`, `/cgv` | R6_SUPPORT |

---

## R-SEO-03: Anti-Confusion R1/R4

**Règle**: Les pages R1 (Router) ne doivent PAS contenir de vocabulaire expert.

**Mots-clés interdits en R1**:
- `bruit`, `usé`, `cassé`, `problème`, `symptôme`, `panne`
- `quand`, `pourquoi`, `comment diagnostiquer`
- `causes`, `risques`, `danger`
- `définition`, `c'est quoi`, `qu'est-ce que`

**Validation**:
```typescript
if (page.role === 'R1' && containsForbiddenKeywords(page.content)) {
  return { valid: false, message: 'R1 contains expert vocabulary' };
}
```

---

## R-SEO-04: Longueur de Contenu

| Role | Min Words | Max Words |
|------|-----------|-----------|
| R1 | - | 150 |
| R2 | 100 | - |
| R3 | 500 | - |
| R4 | 300 | - |
| R5 | 200 | - |
| R6 | - | - |

---

## R-SEO-05: Maillage Interne

**Règle**: Les liens internes doivent respecter la matrice de maillage.

| From → To | Autorisé | Max |
|-----------|----------|-----|
| R1 → R2 | ✅ | Unlimited |
| R1 → R3/R4/R5 | ❌ | 0 |
| R2 → R4 | ✅ | 1 |
| R2 → R3 | ✅ | 1 |
| R6 → * | ❌ | 0 |

---

## R-SEO-06: Canonical Obligatoire

**Règle**: Chaque page indexée DOIT avoir une URL canonique.

```typescript
// Validation
if (page.role !== 'R6' && !page.canonical) {
  return { valid: false, message: 'Missing canonical URL' };
}

// Self-referencing check
if (page.canonical !== page.url) {
  return { valid: false, message: 'Canonical should self-reference' };
}
```

---

## R-SEO-07: Structured Data

| Role | Required Schemas |
|------|------------------|
| R1 | BreadcrumbList, ItemList |
| R2 | Product, Offer, BreadcrumbList |
| R3 | Article, BreadcrumbList |
| R4 | DefinedTerm, BreadcrumbList |
| R5 | HowTo, BreadcrumbList |
| R6 | BreadcrumbList |

---

## R-SEO-08: Noindex pour R6

**Règle**: Les pages R6 (Support) DOIVENT être en noindex.

```html
<meta name="robots" content="noindex, follow">
```

---

## R-SEO-09: URL Immutability (interdiction stricte de toucher aux URLs)

**Règle absolue**: aucune URL existante en production ne doit être modifiée, renommée,
migrée ou réécrite. Cela inclut **et n'est pas limité à** :

- segments de path (`/pieces/...`, `/constructeurs/...`, `/produit/...`)
- slugs (`pg_alias`, `marque_alias`, `modele_alias`, `type_alias`, etc.)
- suffixes (`.html`, `-{pgId}`, `-{typeId}`)
- séparateurs entre segments (`.` vs `-` vs `/`)
- query strings indexées
- patterns canonical produits par `SeoCanonicalService`
- noms de fichiers route Remix (`pieces.$gamme.$marque.$modele.$type[.]html.tsx`, etc.)
- patterns de sitemap V10
- règles `robots.txt`
- redirections 301 sur des URLs vivantes

**Why**:
- Le SEO d'AutoMecanik repose sur des URLs indexées de longue date par Google. Tout
  changement déclenche : 301 massifs, perte d'autorité, pic "Crawled - not indexed",
  fluctuations de classement, perte de trafic organique.
- État empirique 2026-05 : régression GSC R3 active (`seo-r2-thin-content-root-cause`),
  toucher aux URLs aggrave drastiquement.
- Backlinks externes pointent les URLs actuelles — une URL changée = lien externe cassé,
  non rattrapable.
- Sitemap V10 + canonical + linking interne sont **alignés sur les URLs en place** ;
  modifier nécessite la re-synchronisation de 4-5 systèmes en cascade.
- Précédent réel : commit `369fca35` sur PR-5 a unilatéralement modifié le canonical
  R1_GAMME_ROUTER de `/pieces/{pgAlias}` à `/pieces/{pgAlias}-{pgId}.html`. Reverté en
  `f065e08c`. User a rappelé 2× : « il est strictement interdit de toucher aux URLs ».

**How to apply**:

1. **STOP automatique** — toute proposition contenant un de ces verbes/expressions doit
   être bloquée et signalée à l'utilisateur avant toute exécution :
   `réécrire URL`, `migrer slug`, `moderniser path`, `supprimer .html`, `raccourcir URL`,
   `URL canonique simplifiée`, `rename route file`, `refonte URL`, `harmoniser slugs`,
   `optimize slug`, `slug optimizer`, `url_title_optimizer`, `URL canonical pattern change`.

2. **Si une incohérence apparente est détectée** entre une route Remix et la canonical
   configurée (par exemple, route extrait `pgId` mais canonical n'en produit pas) →
   **STOP**, signaler à l'utilisateur, demander la décision. **Ne pas commit de "fix"
   unilatéral.**

3. **Cibles autorisées** dans le périmètre SEO : surfaces (catalogue), seuils noindex,
   chaîne services (renderer/switch/builder/indexability/canonical), shadow mode
   controllers, feature flags `SEO_CHAIN_*_MODE`, contenu (title/desc/h1/content), tables
   `__seo_*`, fingerprint, linking interne, JSON-LD. **Tout sauf les URLs.**

4. **`SeoSlugService`** : son rôle est de **reproduire** les slugs legacy à l'identique
   via golden tests (≥ 50 URLs production). Pas d'"optimisation" qui produirait des slugs
   différents. Si divergence est détectée pendant l'implémentation, c'est le service qui
   s'aligne sur le legacy, jamais l'inverse.

5. **`SeoCanonicalService`** : produit le canonical **exact** correspondant à l'URL
   legacy pour chaque rôle. Pas de "modernisation" du pattern.

6. **`SeoUnavailablePolicy` (410/412)** : retirer une URL morte = HTTP 410 + page
   contextualisée. **Jamais** de redirection vers une "URL équivalente modernisée".

7. **Exception légitime** (cas rare) : si un chantier exige un changement d'URL pour
   raison technique forte (sécurité critique, duplicate massif documenté), passer par :
   - ADR vault dédié documentant la justification empirique
   - Plan 301 complet avec mapping ancien → nouveau exhaustif
   - Validation explicite utilisateur **avant** exécution
   - PR séparée et taggée `breaking-change-url`

   Pas de glissement silencieux.

**Précédents bloqués** (pour rappel) :
- PR-5 commit `369fca35` reverté `f065e08c` — canonical R1 modifié sans demande.
- R7/R8 canonical envisagés en PR-6 — scope abandonné après rappel utilisateur.

**Référence mémoire DEV** : `feedback_no_url_changes_ever.md` (auto-loaded).

---

## CI Integration

```yaml
# .github/workflows/seo-validation.yml
name: SEO Validation

on:
  pull_request:
    paths:
      - 'frontend/app/routes/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check PageRole defined
        run: npm run seo:check-roles

      - name: Check anti-confusion
        run: npm run seo:check-confusion

      - name: Check maillage
        run: npm run seo:check-links
```

---

## Voir aussi

- [[08-seo-charter]] - Charte SEO complète
- [[ADR-006-ai-orchestrator-architecture]] - Architecture
- [[03-skills-registry]] - Skill `seo_role_audit`

---

_Créé: 2026-02-03 | Source: Architecture Report Section 10_
