---
title: Matrice Image × Type de Page (V1)
status: canon
version: 1.0
date: 2026-02-23
scope: Contrat visuel — regle les choix image pour chaque type de page
---

# Matrice Image × Type de Page (V1)

> Ce document est le **contrat** qui gouverne tous les choix image du site.
> Aucun code ne doit prendre de decision image sans s'y referer.

---

## 1. Intent Classes

8 classes couvrent tous les types de pages du site.

| Class | Pages concernees | Intention utilisateur |
|-------|-----------------|----------------------|
| TRANSACTION | Fiche produit, panier, checkout | Acheter |
| SELECTION | Selecteur vehicule, selecteur piece, gamme R1 | Choisir / naviguer |
| GUIDE_ACHAT | Guides d'achat (R3) | Comparer / decider |
| BLOG_CONSEIL | Conseils, articles pedagogiques (R3) | Apprendre / comprendre |
| DIAGNOSTIC | Pages diagnostic (R5) | Diagnostiquer / resoudre |
| PANNE_SYMPTOME | Pages panne, symptome | Identifier un probleme |
| GLOSSAIRE_REFERENCE | Definitions, encyclopedie (R4) | Definir / referencer |
| OUTIL | Outils interactifs | Utiliser un outil |

---

## 2. Specifications par Class

### Champs

- **hero_policy** : type de hero autorise pour cette class
  - `none` : pas de hero image (texte seul ou gradient minimal)
  - `gradient` : gradient CSS uniquement (pas de photo/illustration)
  - `photo` : photo reelle (stock ou produit)
  - `illustration` : illustration/schema technique
  - `ui-screenshot` : capture d'ecran ou mockup UI

- **og_policy** : strategie de generation de l'image OG (1200x630)
  - `asset` : image statique pre-definie par intent class
  - `derived-from-pg_img` : generee depuis l'image gamme/produit via imgproxy
  - `derived-from-model` : generee depuis l'image vehicule/modele
  - `logo` : logo seul (dernier recours)

- **inline_image_density** : densite d'images dans le corps du contenu
  - `0` : aucune image inline
  - `low` : 0-1 image inline
  - `medium` : 1-3 images inline
  - `high` : 3+ images inline (schemas, comparatifs, etapes)

### Matrice

| Class | hero_policy | og_policy | inline_density | Type image | Ratio hero | Traitement |
|-------|------------|-----------|----------------|-----------|-----------|------------|
| **TRANSACTION** | photo | derived-from-pg_img | medium | Photo produit/rack | 16:9 | Overlay leger + badge famille |
| **SELECTION** | gradient | derived-from-model | low | Visuel vehicule | 3:1 | Sobre, gradient + icone famille |
| **GUIDE_ACHAT** | photo | derived-from-pg_img | high | Photo + pictos criteres | 16:9 | Clair, professionnel |
| **BLOG_CONSEIL** | photo | asset | medium | Photo technique | 16:9 | Warm, pedagogique |
| **DIAGNOSTIC** | illustration | asset | medium | Schema/icone securite | 16:9 | Contraste fort |
| **PANNE_SYMPTOME** | illustration | asset | low | Visuel alerte soft | 16:9 | Pas d'effet pub |
| **GLOSSAIRE_REFERENCE** | none | asset | low | Coupe technique/neutre | — | Minimal |
| **OUTIL** | ui-screenshot | asset | low | UI screenshot/illustration | 16:9 | Tres clean |

---

## 3. Regles OG Image

### Format
- Dimensions : **1200 x 630 px** (ratio 1.91:1, recommande Facebook/LinkedIn/Twitter)
- Format : WebP (qualite 85)
- URL : **absolue obligatoire** (`https://www.automecanik.com/...`)
- Parametres imgproxy stables (ne pas changer sans raison — evite le re-scrape social)

### Resolution
1. Si `og_policy = derived-from-pg_img` et `pg_img` existe et != 'no.webp' → imgproxy transform
2. Si `og_policy = derived-from-model` et image modele existe → imgproxy transform
3. Si `og_policy = asset` → image statique `/images/og/{intent-class}.webp`
4. Fallback ultime → `https://www.automecanik.com/logo-og.webp`

### Assets statiques OG (8 fichiers)
```
public/images/og/
  transaction.webp
  selection.webp
  guide-achat.webp
  blog-conseil.webp
  diagnostic.webp
  panne-symptome.webp
  glossaire-reference.webp
  outil.webp
```

---

## 4. Politique texte dans les images

**AUCUN texte dans les images hero ou OG.**

- Le texte est dans le HTML (H1, description, badges)
- Exception unique : logo de marque en coin (petit, discret)
- Raisons : accessibilite, traduction, SEO (Google ne lit pas le texte dans les images)

---

## 5. Scoring image par intent class

La penalite `MISSING_IMAGE` dans le scoring qualite varie selon la class :

| Class | MISSING_IMAGE | MISSING_ALT_TEXT | Image obligatoire ? |
|-------|--------------|-----------------|---------------------|
| TRANSACTION | -8 pts | -5 pts | Oui |
| GUIDE_ACHAT | -8 pts | -5 pts | Quasi-obligatoire |
| BLOG_CONSEIL | -8 pts | -5 pts | Oui |
| DIAGNOSTIC | -5 pts | -3 pts | Recommandee |
| PANNE_SYMPTOME | -5 pts | -3 pts | Recommandee |
| SELECTION | -3 pts | -3 pts | Optionnelle |
| GLOSSAIRE_REFERENCE | 0 pts | -3 pts | Non requise |
| OUTIL | 0 pts | -3 pts | Non requise |

---

## 6. Mapping route → intent class

| Pattern route | Intent class |
|--------------|-------------|
| `pieces.$slug` (fiche gamme/produit) | TRANSACTION |
| `constructeurs.$brand.$model.$type` | SELECTION |
| `enhanced-vehicle-catalog.*` | SELECTION |
| `blog-pieces-auto.guide-achat.*` | GUIDE_ACHAT |
| `blog-pieces-auto.conseils.*` | BLOG_CONSEIL |
| `diagnostic-auto.*` | DIAGNOSTIC |
| `panne-auto.*`, `symptome-auto.*` | PANNE_SYMPTOME |
| `reference-auto.*`, `glossaire.*` | GLOSSAIRE_REFERENCE |
| `outil.*` | OUTIL |
| `panier.*`, `checkout.*` | TRANSACTION |

---

## 7. Aliases et composants Hero (P2)

6 composants Hero couvrent les 8 intent classes :

| Composant | Intent classes couvertes | hero_policy |
|-----------|------------------------|-------------|
| `HeroTransaction` | TRANSACTION | photo |
| `HeroSelection` | SELECTION | gradient |
| `HeroGuide` | GUIDE_ACHAT | photo |
| `HeroBlog` | BLOG_CONSEIL | photo |
| `HeroDiagnostic` | DIAGNOSTIC, PANNE_SYMPTOME | illustration |
| `HeroReference` | GLOSSAIRE_REFERENCE | none |

**Aliases :**
- PANNE_SYMPTOME → `HeroDiagnostic` (meme structure visuelle, prop `severity` pour ajuster l'accent)
- OUTIL → aucun composant (pas de route active en production, differe)

---

## 8. Fallback images

Quand aucune image specifique n'est disponible :

| Contexte | Fallback |
|----------|----------|
| Gamme sans `pg_img` | `/images/pieces/default.png` |
| Vehicule sans image modele | Gradient + logo marque |
| Famille sans SVG | `default.svg` (a completer — top 20 familles en priorite) |
| OG sans image derivable | Asset statique par intent class |
| Asset OG manquant | `logo-og.webp` |
