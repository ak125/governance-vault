# Image Matrix v2 — Visual Intent System

> Addendum a image-matrix-v1.md. Source unique pour le systeme image unifie.
> Date: 2026-02-25

## S9. Visual Intent Tiers

3 tiers visuels mappent chaque intent class a une ambiance coherente.

| Tier | Temperature | Contraste | Overlay | Intent classes |
|------|-------------|-----------|---------|----------------|
| neutral | neutral/cool | low-medium | leger/aucun | transaction, selection, glossaire-reference, outil |
| pedagogical | warm | medium | modere | guide-achat, blog-conseil, role-piece |
| alert | cool | high | aucun | diagnostic, panne-symptome |

**Config centrale :** `frontend/app/config/visual-intent.ts`

## S10. Animation Budget

| Level | Classes Tailwind | Intent classes |
|-------|-----------------|----------------|
| none | (aucune) | diagnostic, panne-symptome, glossaire-reference |
| subtle | `transition-opacity duration-200` | selection, guide-achat, blog-conseil, role-piece, outil |
| moderate | `transition-[opacity,transform] duration-200` | transaction |

**Regle :** Jamais depasser `duration-200`. Pas de `transition-all`.

## S11. Slogan System

Templates avec interpolation `{gamme}`. Si gammeName absent, fallback = "pieces auto".

| Intent Class | Slogan template | Exemple |
|---|---|---|
| transaction | "{gamme} au meilleur prix — livraison rapide" | "Kit d'embrayage au meilleur prix — livraison rapide" |
| selection | "Trouvez les {gamme} compatibles avec votre vehicule" | "Trouvez les pieces auto compatibles..." |
| guide-achat | "Comment bien choisir vos {gamme}" | "Comment bien choisir vos plaquettes de frein" |
| blog-conseil | "Tout savoir sur les {gamme}" | "Tout savoir sur les alternateurs" |
| diagnostic | "Diagnostic {gamme} — identifiez la cause" | "Diagnostic pieces auto — identifiez la cause" |
| panne-symptome | "{gamme} en panne — agissez vite" | "Pieces auto en panne — agissez vite" |
| role-piece | "Comprendre le role des {gamme}" | "Comprendre le role des amortisseurs" |
| glossaire-reference | "" (pas de slogan) | — |
| outil | "Outil {gamme}" | "Outil pieces auto" |

**Regles :**
- Max 60 caracteres
- Rendu dans `<p>`, jamais dans `<h1>` ni dans les images
- API : `resolveSlogan(intentClass, gammeName?)`
- Risque SEO : negligeable avec 221 gammes actives

## S12. Section Image Matrix

Budget max : 3 images section par page (hors hero), 300KB total.

### Guide d'achat (guide-achat)

| Section | Placement | Size | Source | maxSectionImages: 3 |
|---|---|---|---|---|
| intro | right | md | pg_img | P1 |
| risk | left | sm | static | P2 |
| howToChoose | full | lg | pg_img | P2 |
| symptoms | left | sm | static | P3 |

### Blog Conseil (blog-conseil)

| Section | Placement | Size | Source | maxSectionImages: 2 |
|---|---|---|---|---|
| signsOfWear | right | md | pg_img | P2 |
| removal | full | lg | static | P3 |
| reassembly | full | lg | static | P3 |

### Reference (glossaire-reference)

| Section | Placement | Size | Source | maxSectionImages: 3 |
|---|---|---|---|---|
| roleMecanique | right | md | pg_img | P1 |
| composition | left | md | static | P2 |
| confusions | center | md | static | P2 |
| installation | full | lg | static | P3 |

### Role Piece (role-piece)

| Section | Placement | Size | Source | maxSectionImages: 3 |
|---|---|---|---|---|
| roleInVehicle | right | lg | pg_img | P1 |
| mechanicalInteractions | center | md | static | P2 |
| checkpoints | left | sm | static | P3 |

### Diagnostic (diagnostic)

| Section | Placement | Size | Source | maxSectionImages: 2 |
|---|---|---|---|---|
| symptom | right | md | static | P2 |
| technicianCheck | left | md | static | P3 |
| recommendedActions | left | sm | static | P3 |

### Panne-symptome

| Section | Placement | Size | Source | maxSectionImages: 1 |
|---|---|---|---|---|
| symptom | right | md | static | P2 |

### Transaction

| Section | Placement | Size | Source | maxSectionImages: 1 |
|---|---|---|---|---|
| buyingGuide | right | md | pg_img | P1 |

### Selection / Outil

Pas d'images section (maxSectionImages: 0).

## S13. Image Sourcing Strategy

3 niveaux de sourcing, progressifs :

### Niveau 1 — Images gamme existantes (immediat)
- Source : `pg_img` en base via `ImageOptimizer.getOptimizedUrl()`
- Stockage : Supabase Storage
- Couvre ~80% des 221 gammes
- Sections : intro guide, role mecanique, buyingGuide pieces

### Niveau 2 — Illustrations statiques par intent class
- SVGs/WebP generiques dans `frontend/public/images/sections/`
- ~10-15 illustrations a creer
- Exemples : `risk-alert.svg`, `comparison-ab.svg`, `vehicle-zone.svg`, `step-by-step.svg`
- Couvre toutes les gammes sans image specifique

### Niveau 3 — Images recreees par IA (pipeline RAG → SD)
- Pipeline : RAG extrait images docs pro → `describeImage()` genere prompt anti-copyright → Stable Diffusion self-hosted recree → Supabase Storage
- SD = decoratif/atmospherique/schemas SEULEMENT
- Photos produit reelles = pg_img (JAMAIS genere par SD)
- Table index : `__media_assets` (pg_id, section_type, storage_url, prompt_used, source_hash)

## S14. Alt-text SEO (Google Images)

Pattern structure par intent class avec `{gamme}` :

| Intent Class | Pattern |
|---|---|
| transaction | "{gamme} — vue produit" |
| guide-achat | "Comparaison de {gamme} — criteres de choix" |
| blog-conseil | "{gamme} — conseil d'entretien" |
| glossaire-reference | "{gamme} — schema de fonctionnement" |
| role-piece | "{gamme} — role dans le vehicule" |
| diagnostic | "Zone du vehicule affectee par une panne de {gamme}" |
| panne-symptome | "Symptomes de panne {gamme}" |
| selection | "{gamme} — selection vehicule" |

API : `resolveAltText(intentClass, gammeName?)`

## S15. SectionImage Component

**Composant :** `frontend/app/components/content/SectionImage.tsx`

**Responsive mobile-first :**
- Mobile (< 640px) : toutes les images → full-width au-dessus du texte
- Desktop (>= 640px) : placement configure (left float, right float, center, full)

**Tailles :** sm=160px, md=240px, lg=400px

**srcset :** Genere automatiquement via `generateImgproxySrcSet()` pour les URLs imgproxy.

**Wrapper :** `SectionWithImage` pour clearfix apres float left/right.

## S16. HeroRole vs HeroReference

**Critere objectif :** Si `role_mecanique` > 100 mots ET `cross_gammes` >= 2 → HeroRole. Sinon → HeroReference.

| Aspect | HeroRole | HeroReference |
|---|---|---|
| Intent class | role-piece | glossaire-reference |
| Tier | pedagogical | neutral |
| hero_policy | illustration | none |
| Gradient | chaud (famille) | gris (bg-gray-50) |
| Animation | subtle | none |
| Illustration | technique (optionnelle) | aucune |

## Fichiers crees/modifies

### Crees
- `frontend/app/config/visual-intent.ts` — Config centrale
- `frontend/app/components/content/SectionImage.tsx` — Composant image section
- `frontend/app/components/heroes/HeroRole.tsx` — Nouveau hero pedagogique

### Modifies
- `frontend/app/utils/og-constants.ts` — +role-piece dans IntentClass
- `frontend/app/components/heroes/Hero*.tsx` — +slogan prop (6 heroes)
- `frontend/app/components/heroes/_hero.contract.md` — +regles 9-10-11
- 6 routes — Import resolveSlogan + prop slogan sur hero
