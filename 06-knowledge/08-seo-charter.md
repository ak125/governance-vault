# SEO Charter: PageRole Taxonomy & Anti-Confusion Rules

> Charte SEO définissant les rôles de pages, règles anti-confusion et structured data.

---

## 1. Taxonomie Officielle des Rôles

| Rôle | Code | Intention | URL Pattern | Index | Maillage Sortant |
|------|------|-----------|-------------|-------|------------------|
| Router | R1 | Navigation/Sélection | `/pieces/{gamme}.html` | ✅ | → R2 only |
| Product | R2 | Transaction/Achat | `/pieces/{g}/{m}/{mo}/{t}.html` | ✅ | → R4 (1), R3 (0-1) |
| Blog | R3 | Pédagogie/Expert | `/blog-pieces-auto/*` | ✅ | → R4, R2 |
| Reference | R4 | Définition/Autorité | `/reference-auto/{slug}` | ✅ | → R3, R5, R1 |
| Diagnostic | R5 | Symptômes/Diagnostic | `/diagnostic-auto/{slug}` | ✅ | → R4, R1 |
| Support | R6 | Aide/Légal | `/support/*`, `/cgv` | ❌ | ∅ (aucun) |

### Descriptions Détaillées

#### R1 - Router (Navigation)
- **Objectif**: Guider l'utilisateur vers le bon produit
- **Contenu**: Liste de catégories, sélecteur de véhicule
- **Longueur**: Max 150 mots
- **Interdit**: Vocabulaire expert, diagnostic, symptômes

#### R2 - Product (Transaction)
- **Objectif**: Convertir en vente
- **Contenu**: Fiche produit, prix, compatibilité
- **Schema**: Product, Offer, AggregateRating
- **Interdit**: Diagnostic, symptômes détaillés

#### R3 - Blog (Pédagogie)
- **Objectif**: Éduquer, établir l'expertise
- **Contenu**: Articles guides, tutoriels
- **Schema**: Article, FAQPage
- **Longueur**: Min 500 mots

#### R4 - Reference (Autorité)
- **Objectif**: Définir, expliquer formellement
- **Contenu**: Définitions techniques, glossaire
- **Schema**: DefinedTerm
- **Longueur**: Min 300 mots
- **Interdit**: CTA commerciaux

#### R5 - Diagnostic (Symptômes)
- **Objectif**: Identifier les problèmes
- **Contenu**: Symptômes observables, check-lists
- **Schema**: HowTo, FAQPage
- **Obligatoire**: Avertissement sécurité si nécessaire

#### R6 - Support (Aide)
- **Objectif**: Assistance, légal
- **Index**: Noindex (pas de SEO)
- **Maillage**: Aucun lien sortant

---

## 2. Règles Anti-Confusion

### R1 vs R4 (Router vs Reference)

> ⚠️ **Risque principal**: Cannibalisation entre pages de navigation et pages de définition.

```typescript
// packages/seo/src/rules/anti-confusion.ts

export const ANTI_CONFUSION_RULES: SeoRule[] = [
  // R1 Router: JAMAIS de vocabulaire expert
  {
    role: PageRole.R1_ROUTER,
    forbiddenKeywords: [
      'bruit', 'usé', 'cassé', 'problème', 'symptôme', 'panne',
      'quand', 'pourquoi', 'comment diagnostiquer',
      'causes', 'risques', 'danger',
      'définition', 'c\'est quoi', 'qu\'est-ce que',
    ],
    maxWords: 150,
    requiredElements: ['h1', 'vehicle_selector'],
  },

  // R4 Reference: Source of truth, formal
  {
    role: PageRole.R4_REFERENCE,
    requiredKeywords: ['définition', 'fonction', 'rôle'],
    forbiddenKeywords: ['acheter', 'prix', 'promotion', 'pas cher', 'commander'],
    requiredElements: ['h1', 'definition_schema', 'breadcrumb'],
    minWords: 300,
  },

  // R5 Diagnostic: Symptoms only
  {
    role: PageRole.R5_DIAGNOSTIC,
    requiredKeywords: ['symptôme', 'signe', 'diagnostic'],
    forbiddenKeywords: ['acheter', 'commander', 'prix', 'promotion'],
    requiredElements: ['h1', 'observable_list', 'safety_warning'],
  },

  // R2 Product: Commercial focus
  {
    role: PageRole.R2_PRODUCT,
    requiredKeywords: ['compatible', 'prix', 'livraison'],
    requiredElements: ['h1', 'price', 'add_to_cart', 'product_schema'],
    forbiddenKeywords: ['symptôme', 'diagnostic', 'panne', 'définition'],
  },

  // R3 Blog: Educational
  {
    role: PageRole.R3_BLOG,
    minWords: 500,
    requiredElements: ['h1', 'article_schema', 'author'],
    allowedKeywords: ['guide', 'tutoriel', 'conseil', 'astuce'],
  },
];
```

---

## 3. Canonical / Breadcrumb / JSON-LD Rules

```typescript
// packages/seo/src/rules/structured-data.ts

export const STRUCTURED_DATA_RULES: Record<PageRole, StructuredDataRule> = {
  [PageRole.R1_ROUTER]: {
    canonical: (page) => `${BASE_URL}/pieces/${page.gammeSlug}.html`,
    breadcrumb: ['Accueil', 'Pièces auto', '{gamme}'],
    schemas: ['BreadcrumbList', 'ItemList'],
    noindex: false,
  },

  [PageRole.R2_PRODUCT]: {
    canonical: (page) => `${BASE_URL}/pieces/${page.gamme}/${page.marque}/${page.modele}/${page.type}.html`,
    breadcrumb: ['Accueil', 'Pièces auto', '{gamme}', '{marque}', '{modele}'],
    schemas: ['Product', 'Offer', 'BreadcrumbList', 'AggregateRating'],
    noindex: false,
  },

  [PageRole.R3_BLOG]: {
    canonical: (page) => `${BASE_URL}/blog-pieces-auto/article/${page.slug}`,
    breadcrumb: ['Accueil', 'Blog', '{category}', '{title}'],
    schemas: ['Article', 'BreadcrumbList', 'FAQPage'],
    noindex: false,
  },

  [PageRole.R4_REFERENCE]: {
    canonical: (page) => `${BASE_URL}/reference-auto/${page.slug}`,
    breadcrumb: ['Accueil', 'Référence', '{term}'],
    schemas: ['DefinedTerm', 'BreadcrumbList'],
    noindex: false,
  },

  [PageRole.R5_DIAGNOSTIC]: {
    canonical: (page) => `${BASE_URL}/diagnostic-auto/${page.slug}`,
    breadcrumb: ['Accueil', 'Diagnostic', '{symptom}'],
    schemas: ['HowTo', 'FAQPage', 'BreadcrumbList'],
    noindex: false,
  },

  [PageRole.R6_SUPPORT]: {
    canonical: (page) => `${BASE_URL}/${page.path}`,
    breadcrumb: ['Accueil', 'Aide', '{page}'],
    schemas: ['BreadcrumbList'],
    noindex: true, // Support pages not indexed
  },
};
```

---

## 4. Audit Automatique

```typescript
// packages/seo/src/validation/audit.ts

export async function runSeoAudit(options: AuditOptions): Promise<AuditReport> {
  const pages = await fetchAllPages(options.filters);
  const violations: Violation[] = [];

  for (const page of pages) {
    // 1. Check role assignment
    const roleCheck = checkRoleAssignment(page);
    if (!roleCheck.valid) {
      violations.push({
        url: page.url,
        type: 'role_mismatch',
        severity: 'critical',
        message: roleCheck.message,
        suggestedFix: roleCheck.suggestion,
      });
    }

    // 2. Check anti-confusion rules
    const confusionCheck = checkAntiConfusion(page);
    violations.push(...confusionCheck.violations);

    // 3. Check canonical
    const canonicalCheck = checkCanonical(page);
    if (!canonicalCheck.valid) {
      violations.push({
        url: page.url,
        type: 'invalid_canonical',
        severity: 'error',
        message: canonicalCheck.message,
      });
    }

    // 4. Check maillage
    const linkCheck = checkInternalLinks(page);
    violations.push(...linkCheck.violations);

    // 5. Check structured data
    const schemaCheck = checkStructuredData(page);
    violations.push(...schemaCheck.violations);
  }

  return {
    totalPages: pages.length,
    violations,
    summary: summarizeByType(violations),
    score: calculateSeoScore(pages.length, violations),
  };
}
```

---

## 5. Maillage Interne Rules

| From | To | Max Links | Note |
|------|-----|-----------|------|
| R1 | R2 | Unlimited | Seul maillage autorisé |
| R2 | R4 | 1 | Référence du produit |
| R2 | R3 | 0-1 | Guide lié optionnel |
| R3 | R4 | 3-5 | Références techniques |
| R3 | R2 | 2-3 | CTA produits |
| R4 | R3 | 2-3 | Articles liés |
| R4 | R5 | 1-2 | Diagnostic lié |
| R4 | R1 | 1 | Navigation retour |
| R5 | R4 | 2-3 | Explications |
| R5 | R1 | 1 | Navigation produits |
| R6 | * | 0 | Aucun lien sortant |

---

## 6. Checklist de Validation

### PageRole (obligatoire)
- [ ] Chaque route a un `handle.pageRole` défini
- [ ] Le PageRole correspond au pattern URL
- [ ] Pas de confusion R1/R4 (router vs reference)

### Canonical (obligatoire)
- [ ] Canonical URL présente
- [ ] Canonical = URL courante (pas de self-referencing manquant)
- [ ] Pas de paramètres tracking dans canonical

### Structured Data (par rôle)
- [ ] R2: Product + Offer schema
- [ ] R3: Article schema
- [ ] R4: DefinedTerm schema
- [ ] R5: HowTo schema
- [ ] Tous: BreadcrumbList

### Maillage Interne
- [ ] R1 → R2 uniquement
- [ ] R2 → max 1 R4, 0-1 R3
- [ ] R6 → aucun lien sortant
- [ ] Pas de liens brisés (404)

### Contenu
- [ ] R1: max 150 mots, pas de vocabulaire expert
- [ ] R4: min 300 mots, définition formelle
- [ ] R5: liste de symptômes, warning sécurité si nécessaire

---

## 7. KPIs par Rôle

| Role | Primary KPI | Target |
|------|-------------|--------|
| R1 | Click-through to R2 | > 25% |
| R2 | Conversion rate | > 2% |
| R3 | Time on page | > 3min |
| R4 | Backlinks acquired | Growing |
| R5 | Exit to R1/R2 | > 40% |
| R6 | - | N/A |

---

## Voir aussi

- [[ADR-006-ai-orchestrator-architecture]] - Architecture globale
- [[seo-pagerole-rules]] - Règles de validation CI
- [[03-skills-registry]] - Skill `seo_role_audit`

---

_Créé: 2026-02-03 | Source: Architecture Report Section 10_
