---
type: audit-trail
date: 2026-05-07
session_id: design-pack-mobile-v5-pivot-2026-05-07
domain: frontend-design-pack
related_knowledge: ["design-pack-handling-canon-20260507"]
related_prs:
  - "ak125/nestjs-remix-monorepo#360"
  - "ak125/nestjs-remix-monorepo#368"
  - "ak125/governance-vault#215"
status: shipped
---

# Design pack mobile V5 — pivot d'approche après rejet PR #360

> Session 2026-05-07. Le design pack `Automecanik Design System.zip`
> (`v5/parcours.html` — 4 écrans mobile : Home, Liste, Produit, Panier) a été
> livré comme prototype HTML. Première implémentation rejetée pour mauvaise
> direction architecturale. Pivot effectué dans la même session.

## 1. Erreur initiale (PR #360 rejetée)

**Approche** : créer un parcours `/v5/*` parallèle complet au funnel V4.

| Surface créée | Volume |
|---|---|
| Routes `/v5/*` | 4 (`/v5`, `/v5/liste`, `/v5/produit/:ref`, `/v5/panier`) |
| Composants `frontend/app/components/v5/` | 14 (Header, BottomBar, Plaque, ProductCard, atoms, etc.) |
| Hooks adapters | 2 (`useV5Cart` localStorage, `useV5Vehicle`) |
| Mock data + ESLint anti-leak | 1 fichier `data.ts` + règle dédiée |
| Total | **+2781 LOC** |

**Verdict Fafa** (citation directe) :
> "vous voulez touché au url alors que cela est strictement interdit, vous
> changer le funnel alors que tout est deja existant, vous cre des new fichir
> alors qur tout existe, mon objectife etais juste d'ameliorer l'existant"

**Action** : PR #360 fermée, branche distante supprimée.

## 2. Pivot : pattern preview noindex + migration in-place

**Approche** : routes preview **noindex** temporaires, à supprimer au profit
d'upgrade in-place des composants V4 existants.

| Asset | Localisation | Statut |
|---|---|---|
| Routes preview | `frontend/app/routes/preview-mobile.{tsx,catalog,produit.$ref,panier}.tsx` | ✓ shipped (PR #368) |
| Composants temporaires | `frontend/app/components/mobile-v5/` (`MV5*`) | ✓ shipped — **à migrer V4** |
| Fixtures preview | `preview-fixtures.ts` + `usePreviewCart.ts` | ✓ shipped — **anti-leak ESLint** + à supprimer ship suivant |
| CSS signatures | `frontend/app/styles/mobile-signatures.css` (~900 lignes scopées `.mobile-v5`) | ✓ shipped — **à promouvoir DS** au moment migration |
| Tokens DS additionnels | `accent.signatureYellow`, `shadow.plate`, `shadow.cta` | ✓ shipped — réutilisables hors preview |
| Knowledge canon | `ledger/knowledge/design-pack-handling-canon-20260507.md` | ✓ shipped (vault PR #215) |
| Mémoire Claude | `feedback_design_pack_improves_existing_not_replaces.md` | ✓ shipped (auto-loaded sessions) |

## 3. Ce qui reste à faire (ship 2 — migration in-place)

Le chantier de migration des composants `MV5*` vers leurs emplacements V4 finaux est **à planifier**. Pas encore ouvert. Critères de déclenchement :

- ✅ Validation visuelle Fafa des 4 routes preview (`/preview-mobile/*`) sur viewport iPhone SE 375×667 + iPhone 14 Pro 393×852
- ✅ Décision sur les écarts à corriger avant migration (si écart vs design pack)
- ✅ Lighthouse a11y mobile ≥ 95 mesuré sur les 4 routes preview

Migration cible (ship 2) :

| Composant preview `MV5*` | Cible V4 in-place | Routes V4 consommatrices |
|---|---|---|
| `MV5Plaque` | `app/components/home/Plaque.tsx` | `_index.tsx` via `HeroSection.tsx` |
| `MV5FitmentBand` | `app/components/ecommerce/FitmentBand.tsx` | `pieces.$gamme.$marque.$modele.$type[.]html.tsx` |
| `MV5StickyCTA` | `app/components/cart/StickyCTA.tsx` | `cart.tsx` |
| `MV5BottomBar` | `app/components/layout/MobileBottomBar.tsx` | montée conditionnelle `root.tsx` (commerce only) |
| `MV5ProductCard` | variant mobile de `app/components/ecommerce/ProductCard.tsx` | catalog + home featured |
| `MV5QuantityStepper` | `app/components/ecommerce/QuantityStepper.tsx` | catalog + cart |

Suppression complète du namespace `/preview-mobile/*` + `components/mobile-v5/` + `usePreviewCart` + `preview-fixtures.ts` + ESLint guard dans la même PR de migration.

## 4. Patterns canonisés (à appliquer aux prochains design packs)

Repris en 7 sections dans la knowledge note canon :

1. **Le piège** — réflexe IA-générique de créer un parcours parallèle
2. **La règle** — URLs SEO sacrées, funnel intouchable, mapping pack→V4 obligatoire
3. **Pattern preview noindex** accepté temporairement
4. **Tests de plausibilité au plan** — 5 alarmes (>2 nouvelles routes, >5 nouveaux composants, nouveau hook redondant, modif URL, mock fixtures sans plan suppression)
5. **Application** (start design task, PR review, brief agents Paperclip)
6. **Précédents** (PR #360 rejetée, PR #368 correcte)
7. **Maintenance** — note vivante, append à chaque incident

## 5. Métriques session

| Item | Valeur |
|---|---|
| LOC créés (preview corrigé, PR #368) | ~2900 lignes (+ scoped + temporaire) |
| LOC évités (PR #360 rejetée vs ship in-place V4) | ~2781 lignes de duplication funnel |
| URLs SEO créées | **0** (preview noindex) |
| Composants V4 modifiés | **0** au ship 1 (preview pur) |
| Knowledge canon documenté | 135 lignes, 7 sections |
| Mémoires Claude créées | 1 (feedback auto-applicable sessions futures) |

## 6. Prochaines actions ordonnancées

1. **Validation visuelle Fafa** sur `localhost:3000/preview-mobile/*` (iPhone SE / 14 Pro DevTools).
2. **Merger PR #368** une fois validation OK + lighthouse a11y ≥ 95 mesuré.
3. **Merger vault PR #215** (knowledge canon).
4. **Planifier ship 2** (migration in-place) seulement après go visuel — créer plan local Claude Code pour cette étape (nouvelle PR monorepo).
5. **Supprimer entièrement** le namespace preview au moment du ship 2 (PR de migration = PR de cleanup).

## 7. Lien chantiers MOC-Roadmap-2026

Ce travail s'inscrit principalement dans le **chantier A — Runtime e-commerce / business core** (UX mobile-first du funnel = leverage conversion direct). Effets indirects sur :

- **D — SEO indexation** : préservation URLs SEO sacralisée (renforce la discipline du chantier)
- **E — Performance** : signature CSS scoped + a11y ≥ 95 cible Lighthouse mobile

À tracker dans MOC-Roadmap "État des plans dédiés" comme sous-axe UX/Design du chantier A.
