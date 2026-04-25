---
category: ui-pattern
doc_family: knowledge
source_type: implementation
title: VehicleSelector — migration vers Radix Select + groupage carburant
slug: vehicle-selector-radix-pattern
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-25"
updated_by: "@fafa"
related_prs:
  - "ak125/nestjs-remix-monorepo#175"
status: live
---

# VehicleSelector — migration vers Radix Select + groupage carburant

> Pattern UI canonique pour les dropdowns véhicule (Marque / Année / Modèle / Motorisation) sur le site automecanik.com.
> Référence implémentation : PR #175 (`feat/vehicle-selector-radix-grouped-fuel`), commit `7ed053ce`.

## 1. Contexte

Le composant `VehicleSelector.tsx` (Hero homepage, Type Mine search, GammeHero, BrandHero) utilisait 12 `<select>` natifs HTML répartis sur 3 modes (`compact`, `mobile-premium`, `full`). Trois problèmes de fond :

1. **Style cross-browser non garanti** — Safari macOS/iOS et plusieurs versions Firefox ignorent la majorité des règles CSS sur `<option>` (couleurs, padding, indicateurs custom). Les `<optgroup>` colorés rendaient incohérent.
2. **Aucune séparation visuelle entre carburants** dans la liste des motorisations. Sur un modèle avec 30+ moteurs (BMW Série 3, VW Golf), trouver "le bon Diesel" était pénible.
3. **Notation incohérente** : la motorisation affichait `90 PS` (notation allemande) alors que tout le reste du site (R8 hero, breadcrumbs, R7 cards, JSON-LD) utilise `90 ch` (chevaux français).

## 2. Décision

Migration vers le **vrai composant shadcn `Select`** basé sur `@radix-ui/react-select`. Pattern officiel shadcn (Radix Primitives + Tailwind), encapsulé dans `frontend/app/components/ui/select-radix.tsx`.

Pour la motorisation spécifiquement : groupage par carburant + tri par puissance + pastille couleur conforme WCAG-AA.

## 3. Implémentation

### 3.1 Composant Radix Select (réutilisable)

Fichier : `frontend/app/components/ui/select-radix.tsx`

Exports : `Select`, `SelectGroup`, `SelectValue`, `SelectTrigger`, `SelectContent`, `SelectLabel`, `SelectItem`, `SelectSeparator`, `SelectScrollUpButton`, `SelectScrollDownButton`.

Pattern standard shadcn :
- `SelectTrigger` = bouton (forwardRef), `SelectValue` placeholder
- `SelectContent` rendu via `SelectPrimitive.Portal` → z-50, animations Tailwind `data-[state=open]:animate-in fade-in-0 zoom-in-95`
- `SelectItem` avec `SelectPrimitive.ItemIndicator` (check icon) + `SelectPrimitive.ItemText`
- `SelectGroup` + `SelectLabel` pour sections

L'ancien `ui/select.tsx` (faux wrapper natif `<select>`) est laissé intact — autres call sites (admin, panier, etc.) continuent à fonctionner sans toucher.

### 3.2 Helpers carburant (canon pour autres pages véhicule)

```typescript
const FUEL_GROUP_ORDER = ["Diesel", "Essence", "Électrique", "Autres"] as const;
type FuelGroup = (typeof FUEL_GROUP_ORDER)[number];

const FUEL_GROUP_COLORS: Record<FuelGroup, string> = {
  Diesel:    "#c2410c", // orange-700  (4.78:1 sur fond blanc)
  Essence:   "#15803d", // green-700   (4.65:1)
  Électrique: "#1d4ed8", // blue-700    (8.59:1)
  Autres:    "#475569", // slate-600   (7.46:1)
};

function getFuelGroup(fuel?: string | null): FuelGroup {
  if (!fuel) return "Autres";
  const f = fuel.toLowerCase();
  if (f.startsWith("diesel"))  return "Diesel";
  if (f.startsWith("essence")) return "Essence";
  if (f.includes("électr") || f.includes("electr")) return "Électrique";
  return "Autres";
}

function groupAndSortTypesByFuel(types: VehicleType[])
  : Array<[FuelGroup, VehicleType[]]> {
  // map → groupes, tri par type_power_ps ASC dans chaque groupe
  // ordre final : FUEL_GROUP_ORDER (Diesel d'abord)
}

function FuelDot({ color }: { color: string }) {
  return (
    <span
      aria-hidden="true"
      className="inline-block h-2 w-2 rounded-full mr-2 flex-shrink-0"
      style={{ backgroundColor: color }}
    />
  );
}
```

### 3.3 Choix de design

**Pourquoi Diesel d'abord** : majorité du parc auto français en pièces détachées, et c'est ce que l'utilisateur a explicitement demandé.

**Pourquoi pastille (`FuelDot`) plutôt que coloration du texte entier** :
- Texte du `<SelectItem>` reste en `slate-900` → contraste 16:1 (largement AA/AAA).
- Pastille 8px est décorative (`aria-hidden="true"`), donc aucune contrainte WCAG.
- Élément sélectionné dans le trigger fermé reste lisible (la couleur du `style` inline n'est plus appliquée à un texte dont la lisibilité dépend du fond du trigger).

**Pourquoi `green-700` et `orange-700` au lieu de `green-600`/`orange-600`** : les variantes 600 sur Tailwind ont des ratios de contraste 3.2-3.5:1 sur fond blanc — échec WCAG AA pour texte normal. Les 700 passent 4.65-4.78:1.

**Format final affiché** : `1.6 CRDi 90 - 90 ch` (compact + mobile-premium). Le mode `full` garde `(Diesel)` entre parenthèses pour parité avec l'ancien layout.

## 4. Vérifications

| Contrôle | Résultat |
|---|---|
| `<select>` natifs restants dans VehicleSelector | **0** |
| `<Select>` Radix usages | **12** (4 dropdowns × 3 modes) |
| `npx tsc --noEmit` sur VehicleSelector / select-radix | **0 erreur** |
| Lazy-load brands au focus (`onSelectorInteraction`) | **préservé** via `onFocus + onPointerDown` sur `SelectTrigger` |
| Pré-sélection `currentVehicle` prop | **préservée** (logic inchangée dans `loadBrands`) |

## 5. Réutilisable pour d'autres pages

Les helpers `FUEL_GROUP_COLORS`, `getFuelGroup`, `groupAndSortTypesByFuel`, `FuelDot` sont actuellement définis localement dans `VehicleSelector.tsx`. Si d'autres composants ont besoin du même groupage (BrandVehiclesSection, R8 sibling list, R7 brand engine cards), extraire vers `frontend/app/lib/fuel-groups.ts` au moment du second usage (règle "trois fois avant abstraction" — ici on est à 1).

## 6. Leçon technique : préférer `Write` atomique pour gros refactors

Pendant cette session, plusieurs `Edit` consécutifs sur `VehicleSelector.tsx` ont été perdus entre commandes — un autre process (worktree partagé `/tmp/claude-cleanup-worktree`, IDE buffer ouvert, ou checkout automatique) re-poussait l'état d'origine. La solution propre :

> Pour un refactor qui touche >5 zones d'un même fichier, faire **un seul `Write` complet** plutôt que des `Edit` successifs. Réduit la fenêtre de race à zéro.

**Coût** : il faut `Read` le fichier complet d'abord (lecture en RAM), puis reconstruire mentalement le fichier final, puis `Write` une fois. Pour les fichiers <1000 lignes c'est gérable.

À ajouter aux patterns d'édition pour ce repo lors d'un prochain ADR sur les conventions agent.

## 7. Hors scope (follow-ups potentiels)

- **Search/filter combobox** pour modèles à ≥20 motorisations (BMW Série 3, VW Golf) — `cmdk` + Popover Radix (déjà installé).
- **Année range** dans la chaîne motorisation : `1.6 CRDi 90 - 90 ch (2007-2012)` pour désambiguïser deux générations du même moteur.
- **Migration des 3 autres dropdowns** (Marque, Année, Modèle) vers le même Radix Select dans d'autres composants utilisant `<select>` natif (`vehicles/TypeSelector.tsx`, `vehicles/VehicleCard.tsx`, etc.) si l'incohérence visuelle gêne.

## Références

- PR : [ak125/nestjs-remix-monorepo#175](https://github.com/ak125/nestjs-remix-monorepo/pull/175)
- Commit : `7ed053ce` sur `feat/vehicle-selector-radix-grouped-fuel`
- Composants impactés :
  - `frontend/app/components/vehicle/VehicleSelector.tsx` (3 modes, 12 dropdowns)
  - `frontend/app/components/ui/select-radix.tsx` (nouveau, shadcn officiel)
  - `frontend/package.json` (+`@radix-ui/react-select@^2.2.6`)
- Tailwind palette WCAG-AA : voir `https://tailwindcss.com/docs/customizing-colors` pour calculs ratio
