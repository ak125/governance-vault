---
category: methodology
doc_family: knowledge
source_type: lesson-learned
title: Design pack handling — improve existing, never duplicate the funnel
slug: design-pack-handling-canon
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-07"
updated_by: "@fafa"
related_prs:
  - "ak125/nestjs-remix-monorepo#360"
  - "ak125/nestjs-remix-monorepo#368"
related_memories:
  - "feedback_design_pack_improves_existing_not_replaces.md"
  - "feedback_no_questionnaire_propose_best.md"
  - "feedback_no_bricolage_align_existing_contract.md"
status: live
---

# Design pack handling — canon méthodologique

> Lesson learned : 2026-05-07. Pivot après l'erreur de PR #360.
> Mots de Fafa : *"vous voulez touché au url alors que cela est strictement
> interdit, vous changer le funnel alors que tout est deja existant, vous cre
> des new fichir alors qur tout existe, mon objectife etais juste d'ameliorer
> l'existant"*.

## 1. Le piège

Quand un design pack arrive (Figma, ZIP HTML proto, design system livré), le
réflexe IA-générique est d'**incarner le design dans une nouvelle surface**
(nouveau namespace `/v5/*`, nouvelle modalité, parcours parallèle). Ce
réflexe est dangereux pour un site e-commerce SEO mature :

- 4M+ pages indexées sur le funnel V4 (`/`, `/pieces/$gamme/$brand/$model/$type[.]html`, `/cart`, `/checkout`)
- 714k+ pages SEO trackées dans Search Console
- Le funnel commercial est testé, instrumenté, monitored ; le dupliquer = risque double maintenance + dérive incoming-links + perte tracking

**PR #360 (rejetée)** illustre l'échec : 4 routes `/v5/*`, 14 composants
parallèles, 2 hooks adapters, mock cart isolé, ESLint anti-leak guard.
Surface ajoutée : **+2781 LOC pour zéro valeur business** — le design pack
existait déjà côté repo, seuls les composants V4 manquaient l'upgrade visuel.

## 2. La règle

**Un design pack = un vocabulaire visuel à appliquer aux composants V4
existants.** Ce n'est pas un parcours à reconstruire.

### 2.1 URLs SEO = sacrées

| Ne jamais | Faire à la place |
|---|---|
| Créer `/v5/*`, `/m/*`, `/mobile/*` parallèles | Modifier les routes existantes (`/`, `/pieces*`, `/cart`) en mobile-first responsive |
| Renommer `/pieces/$gamme.$brand.$model.$type[.]html` | Garder l'URL, upgrader le composant qu'elle rend |
| Inventer un endpoint backend pour faire fonctionner le design | Réutiliser les loaders/services existants (`PiecesService`, `useCart`, `useVehicleContext`) |
| Dupliquer le cart en localStorage isolé | Brancher sur `useCart` réel SSR |

### 2.2 Le funnel commercial = intouchable

home → catalog → produit → panier → checkout : **toute modification se fait
in-place dans les composants existants**. Si le design induit un parcours
fonctionnel nouveau (ex. wizard diagnostic), c'est un **projet métier
séparé** — exiger validation explicite avant code.

### 2.3 Lecture par défaut d'un pack

Quand un pack arrive, mapper d'abord :

| Élément du pack | Composant V4 existant qui va le recevoir |
|---|---|
| Hero V5 | `frontend/app/components/home/HeroSection.tsx` |
| Liste V5 | route `pieces.$gamme.$marque.$modele.$type[.]html.tsx` + `ProductCard.tsx` |
| Produit V5 | même route (V4 le sert sur la même URL) |
| Panier V5 | `frontend/app/routes/cart.tsx` + `CartItemRow.tsx` |
| Bottom-bar mobile | nouveau `MobileBottomBar.tsx` monté conditionnel dans `root.tsx` |

**Si la table de mapping reste vide** sur un écran, alors l'écran demande
réellement un nouveau composant — mais pas une nouvelle URL.

## 3. Le pattern de validation accepté

Pour valider visuellement un design avant migration in-place, le pattern
**preview noindex** est acceptable temporairement :

1. Créer routes `/preview-mobile/*` (ou équivalent) **noindex+nofollow** dans
   le `<meta name="robots">`. Pas de SEO, pas de liens internes V4 vers ces
   routes.
2. Écrire les composants visuels (`MV5*`, `PreviewX`) avec préfixe explicite
   "à migrer" et anti-leak ESLint (`no-restricted-imports` qui bloque tout
   import des fixtures preview hors namespace preview).
3. Une fois validé visuellement par le décideur produit, **migrer in-place**
   les composants vers `components/home/`, `components/ecommerce/`,
   `components/cart/`, `components/layout/` et les consommer depuis les
   routes V4 réelles.
4. **Supprimer entièrement le namespace preview** (routes + composants
   preview-only + fixtures + ESLint guard) dans la même PR de migration.

**PR #368** illustre ce pattern correctement.

## 4. Tests de plausibilité au moment de planifier

Avant de soumettre un plan d'intégration de design pack, vérifier :

- [ ] Le plan crée-t-il **plus de 2 nouveaux fichiers route** ? Si oui, alarme — c'est probablement du parallel-build.
- [ ] Le plan crée-t-il **plus de 5 nouveaux composants** sans en référencer leur correspondance V4 ? Si oui, idem.
- [ ] Le plan introduit-il **un nouveau hook cart, vehicle, search** alors que V4 a déjà ses équivalents ? Si oui, ajouter une justification technique (incompatibilité de contrat) ou abandonner.
- [ ] Le plan **modifie-t-il une URL existante** ? Si oui, **STOP** — exiger validation SEO avant.
- [ ] Le plan crée-t-il **des données mock fixtures** ? Si oui, comment seront-elles supprimées au ship suivant ? (Anti-leak guard + commentaire de tête + issue de tracking obligatoires.)

## 5. Application

Cette knowledge note canon doit être référencée :

- Au début de chaque task qui touche un design pack ou une livraison Figma
- Dans les PRs de frontend qui introduisent des composants visuels
  signature (vérification reviewer : la PR upgrade V4 ou crée du parallèle ?)
- Dans le brief des agents Paperclip CMO / SEO Content quand un design est
  associé à leur output

## 6. Précédents

- **2026-05-07** PR #360 rejetée par Fafa (parcours `/v5/*` parallèle).
- **2026-05-07** PR #368 ouverte (preview noindex + plan de migration in-place).
- **Mémoire Claude** : `feedback_design_pack_improves_existing_not_replaces.md`
  (auto-loaded par Claude Code, applique la règle automatiquement aux
  prochaines tasks design).

## 7. Maintenance

Cette note est **canon vivante** : à mettre à jour à chaque incident où la
règle a été (ou a manqué d'être) appliquée. Les PRs concrètes vont en
`related_prs:`. Les ADRs en `related_adr:` quand une décision plus large
émerge (ex. ADR sur "policy de namespace mobile" si on en arrive à un
arbitrage canon).
