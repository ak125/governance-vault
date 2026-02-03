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
