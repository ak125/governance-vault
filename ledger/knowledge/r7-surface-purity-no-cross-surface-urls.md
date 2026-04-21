---
type: knowledge
scope: backend/seo
surface: R7_BRAND
date: 2026-04-21
owner: Fafa
pr: https://github.com/ak125/nestjs-remix-monorepo/pull/86
tags: [r7, r8, surface-purity, architecture, no-bricolage, rule-candidate]
---

# R7 Surface Purity — No Cross-Surface URL Construction in Enrichers

> **Règle candidate canon issue d'une dérive corrigée en flagrant délit**
> **PR** : #86 nestjs-remix-monorepo — commit `60386066`
> **Incident** : 2026-04-21, dérive R7 → R8 détectée et corrigée en revue

---

## Incident

En réparant le bug "S3_SHORTCUTS URLs pointent toutes vers `/constructeurs/alfa-romeo/` (404)" dans l'enricher R7, première tentative de fix a construit des URLs de la forme :

```
/constructeurs/alfa-romeo-13/156-13004/1-9-jtd-8812.html
```

en imitant le pattern de `brand-bestsellers.service.ts:225`. Enrichissement 36/36 PUBLISH, score stable.

**Problème** : cette URL appartient à la surface **R8_VEHICLE**, pas à R7. L'enricher R7 a généré du contenu qui route vers une autre surface éditoriale — **violation de pureté**.

## Preuve de la dérive

Le route frontend [`constructeurs.$brand.$model.$type.tsx:65`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/frontend/app/routes/constructeurs.%24brand.%24model.%24type.tsx#L65) déclare elle-même :

```tsx
export const handle = {
  pageRole: createPageRoleMeta(PageRole.R8_VEHICLE, { ... }),
};
```

L'enricher R7 construisait donc des liens vers R8 — responsabilité d'une autre surface.

## Ce qui aurait dû alerter dès le départ

1. **Matrice éditoriale R0-R8** : R7 = hub marque uniquement. R8 = hub véhicule+motorisation. Un enricher référence toujours sa surface ou des hubs de même niveau, jamais une surface aval.
2. **Module V-Level existant** : le routing vers les pages type est déjà géré par `VehicleSelector` branché sur le module V-Level, présent dans le hero R7. Dupliquer cette logique côté enricher = redondance + dérive.
3. **Sémantique du label** : carte "Pièces Alfa Romeo 156" envoyait vers `.../156-13004/1-9-jtd-8812.html` (motorisation spécifique). Label ≠ URL = symptôme d'erreur de scope.

## Correction appliquée (commit `60386066`)

```ts
// AVANT — dérive R7 → R8
const url = `/constructeurs/${v.marque_alias}-${v.marque_id}/${v.modele_alias}-${v.modele_id}/${v.type_alias}-${typeId}.html`;
shortcuts.push(`- [Pièces ${brandName} ${v.modele_name}](${url})`);

// APRÈS — R7 pure
// Commentaire explicite sur la séparation des surfaces
// Les topModels sont conservés uniquement pour semanticPayload,
// plus de construction d'URL R8 côté enricher R7.
```

S3_SHORTCUTS contient maintenant uniquement des liens **R7-purs** :
- Gammes de pièces hors véhicule (`/pieces/{alias}`)
- Potentiellement autres hubs R7 via S10_RELATED

Le routing R7 → R8 reste la responsabilité exclusive du `VehicleSelector` + module V-Level.

## Règle candidate canon

> **Un enricher ne construit jamais une URL appartenant à une autre surface éditoriale. Le cross-surface passe par un composant UI branché sur le module responsable de cette surface.**

### Application par surface

| Enricher | URLs autorisées | URLs interdites |
|----------|-----------------|------------------|
| **R0_HOME** | liens navigation globale | toute URL de hub spécifique |
| **R1_ROUTER** | `/pieces/{gamme}`, autre R1 sœur | R2 fiche produit, R8 véhicule |
| **R2_PRODUCT** | R2 sœurs (pièces compatibles) | R1 router, R3 how-to |
| **R3_CONSEILS** | R3 sœurs, R1 gamme cible | R2, R8 |
| **R4_REFERENCE** | R4 sœurs | R3 how-to, R5 diag |
| **R5_DIAGNOSTIC** | R5 sœurs, R3 procédures associées | R2, R8 |
| **R6_GUIDE_ACHAT** | R1 gammes comparées | R2 SKU, R8 |
| **R7_BRAND** | R1 gammes, R7 sœurs, ancres internes vers VehicleSelector | **R8 (dérive)**, R2, R5 |
| **R8_VEHICLE** | R1 gammes spécifiques véhicule, R8 motorisations sœurs | R7 hub marque, R2 |

### Exceptions explicites autorisées

- **Ancre interne** (`#vehicle-selector`) dans la même page → reste sur la surface courante, UI-driven
- **Breadcrumb reverse** (R8 vers R7, R3 vers R1 gamme) → navigation hiérarchique, pas un shortcut cross-surface

## Signaux de détection préventive

Avant de committer un enricher qui construit une URL, se poser :

1. Cette URL correspond-elle à un `pageRole` différent de celui de l'enricher ? → **alerte rouge**
2. Un composant UI existe-t-il déjà pour faire ce routing (VehicleSelector, BrandSelector, etc.) ? → utiliser le composant, pas l'URL
3. Le label du lien décrit-il précisément la page cible ? → si label générique + URL spécifique, le lien ne sert pas l'utilisateur

## Gate CI candidat (à implémenter)

Validator R7 (`r7-brand-validator`) devrait rejeter les blocs dont `renderedText` contient des URLs matchant un pattern d'une autre surface. Pseudo-règle :

```ts
const R8_URL_RE = /\/constructeurs\/[a-z0-9-]+-\d+\/[a-z0-9-]+-\d+\/[a-z0-9-]+-\d+\.html/;
if (block.renderedText.match(R8_URL_RE)) {
  throw new Error(`R7 block ${block.id} contains R8 URL: surface purity violation`);
}
```

Équivalents par surface à définir dans `r{N}-*-validator`.

## Références

- PR code : [nestjs-remix-monorepo #86](https://github.com/ak125/nestjs-remix-monorepo/pull/86) commit `60386066`
- Incident de dérive : commit parent `7a09ca51` (annulé par `60386066`)
- Matrice éditoriale : R1-router-merge-policy (à créer pour R0-R8 complet)
- Lié : [[r7-brand-editorial-live-sync]] (vault PR #15 — architecture R7)
- Lié : PR #14 (vault, patterns frontend R7)
