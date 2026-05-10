---
name: rules-marketing-voice
description: Canon brand voice AutoMecanik (ECOMMERCE) + magasin local 93 (LOCAL). Source unique synchronisée vers monorepo via canon-publish. Verrou local_canon obligatoire avant brief LOCAL/HYBRID validable.
type: rules-document
status: canon
date: 2026-04-30
version: 1.0.0
related_adr: ["ADR-036"]
sync:
  target_repo: ak125/nestjs-remix-monorepo
  target_path: .claude/canon-mirrors/marketing-voice.md
  hash_key: marketing_voice
  workflow: canon-publish.yml
  ci_check: marketing-voice-hash.yml
---

# Rules — Marketing Brand Voice (ECOMMERCE + LOCAL)

> **Source de vérité canonique** — règles obligatoires de voix de marque pour
> tous les agents marketing (ADR-036) et toute campagne produite par le module
> backend `marketing/`. Synchronisée vers monorepo via canon-publish.
> **Version** : 1.0.0 | **Status** : `canon` (ratifié par ADR-038)

Ce fichier est l'**unique source canonique** de la voix de marque marketing.
Toute copie dans le monorepo (`.claude/canon-mirrors/marketing-voice.md`) est
**dérivée vérifiée par hash SHA-256** (cf §"Distribution canonique" en fin).

---

## Règles transverses (s'appliquent à TOUS les briefs)

### Interdits absolus

- ❌ Positionnement « casse auto », « pièces d'occasion », « pièces récupérées »
  sauf section dédiée explicitement nommée et balisée. **AutoMecanik vend des
  pièces neuves.**
- ❌ Promesse de stock non vérifiée (« en stock immédiat », « disponible
  aujourd'hui ») si pas confirmée par requête live au moteur de stock.
- ❌ Promesse de prix non validée (« à partir de X € ») si pas issue d'une
  query SQL en temps réel sur le catalogue.
- ❌ Fausse promotion ou urgence artificielle (« plus que 2h ! », « dernière
  pièce ! ») sans justification métier réelle.
- ❌ Fusion des 2 brands ECOMMERCE/LOCAL dans un même message hors
  `business_unit='HYBRID'` strict (cf. §HYBRID).
- ❌ Mention de marques concurrentes ou comparaisons défavorables.
- ❌ Surenchère technique non sourcée (« la meilleure pièce du marché »).

### Obligatoires absolus

- ✅ **Pièces neuves** explicitement mentionné ou implicite dans le contexte.
- ✅ **Vérification compatibilité véhicule** systématiquement proposée :
  « envoyez votre plaque d'immatriculation ou votre carte grise ».
- ✅ **Mention rétractation** pour tout contenu ECOMMERCE soumis aux ventes
  à distance (CTA « commander »).
- ✅ **Conformité RGPD** : tout email/SMS uniquement aux clients ayant donné
  consentement explicite (`marketing_consent_at NOT NULL`). Aucune exception.
- ✅ **Sourcing factuel** : tout chiffre, durée, kilométrage, garantie cité
  doit être vérifiable en RAG `gammes/` ou `wiki/vehicle/` ou DB `__orders`.

---

## Voix `ECOMMERCE` (AutoMecanik / `automecanik.com`)

### Positionnement

- **Marque** : AutoMecanik
- **Domaine canonique** : `https://www.automecanik.com` (vérifié dans
  `backend/src/config/site.constants.ts` `SITE_ORIGIN`)
- **Audience** : automobilistes et professionnels (garages) en France
  métropolitaine, recherche en ligne (SEO national + KW Google Ads).
- **Conversion cible** : achat en ligne (`ORDER`), demande devis (`QUOTE`).

### Ton

- Pédagogique technique mais accessible (vocabulaire mécanique défini ou
  contextualisé).
- Orienté action : verbes à l'impératif (« vérifiez », « trouvez », « commandez »).
- Réassurance : compatibilité, livraison, garantie, retour, expertise.
- 2ᵉ personne du pluriel (« vous »).

### CTA types autorisés

- « Trouvez la pièce compatible avec votre véhicule »
- « Vérifiez la compatibilité avec votre plaque d'immatriculation »
- « Commandez en ligne — livraison sous X jours »
- « Demandez un devis personnalisé »
- « Comparez les références constructeur et équivalentes »

### Channels autorisés

`website_seo`, `email`, `social_facebook`, `social_instagram`.

### Channels interdits

`gbp` (réservé LOCAL), `local_landing` (réservé LOCAL).

---

## Voix `LOCAL` (magasin physique 93)

> ⚠️ **Section `local_canon` à compléter par le métier avant `validated: true`**.
> Tant que `local_canon.validated: false`, **aucun brief LOCAL ou HYBRID
> ne peut passer en `status='reviewed'` ou `status='approved'`**. Le
> `brand-compliance-gate.service.ts` retourne verdict `BLOCK` avec raison
> `local_canon_unvalidated`.

### `local_canon`

```yaml
local_canon:
  legal_name: "TBD — raison sociale exacte RCS Bobigny à confirmer"
  trade_name: "TBD — enseigne commerciale magasin"
  address:
    street: "184 avenue Aristide Briand"
    postal_code: "93320"
    city: "Les Pavillons-sous-Bois"
    country: "FR"
  phone: "TBD — numéro magasin canonique format +33 1 XX XX XX XX"
  opening_hours:
    # Format JSON-LD compatible (schema.org/OpeningHoursSpecification)
    monday:    { opens: "TBD", closes: "TBD" }
    tuesday:   { opens: "TBD", closes: "TBD" }
    wednesday: { opens: "TBD", closes: "TBD" }
    thursday:  { opens: "TBD", closes: "TBD" }
    friday:    { opens: "TBD", closes: "TBD" }
    saturday:  { opens: "TBD", closes: "TBD" }
    sunday:    "closed"
  service_zone:
    # Communes de proximité ciblables par GBP / local landing pages
    - "Les Pavillons-sous-Bois"
    - "Bondy"
    - "Noisy-le-Sec"
    - "Livry-Gargan"
    - "Aulnay-sous-Bois"
    - "Bobigny"
    - "Le Raincy"
    - "Villemomble"
    - "Rosny-sous-Bois"
    - "Montreuil"
  validated: false   # ← passer à true UNIQUEMENT quand TOUS les TBD ci-dessus sont remplis
  validated_by: null
  validated_at: null
```

### Positionnement

- **Audience** : automobilistes et garages de proximité (Seine-Saint-Denis 93
  + frange est de Paris).
- **Conversion cible** : appel (`CALL`), visite magasin (`VISIT`),
  demande devis sur place (`QUOTE`).

### Ton

- Conseil de quartier, proche, humain.
- Disponibilité immédiate (« nous sommes ouverts », « passez nous voir »).
- Réassurance physique : « venez vérifier en magasin », « notre conseiller ».
- Référence locale : nom de commune, repères de proximité.

### CTA types autorisés

- « Appelez le {{ local_canon.phone }} »
- « Venez à {{ local_canon.address.city }} »
- « Demandez conseil à notre équipe »
- « Retrait gratuit en magasin »
- « Ouvert {{ local_canon.opening_hours.* }} »

### Channels autorisés

`gbp`, `local_landing`, `sms`.

### Channels interdits

`website_seo` (réservé ECOMMERCE — risque cannibalisation), `email`
(scope retention national, pas local), `social_facebook`/`social_instagram`
(scope national pour l'instant — Phase 3 si validé).

---

## Voix `HYBRID` (cas exceptionnel cross-business)

### Conditions strictes (toutes obligatoires)

Un brief `business_unit='HYBRID'` est autorisé **uniquement si** :

1. `payload.target_zone = '93'` ou intention magasin physique explicite.
2. `payload.hybrid_reason` non-vide (justification obligatoire, ex :
   « rupture stock e-commerce sur SKU disponible en magasin »).
3. `payload.cta_ecommerce` ET `payload.cta_local` séparés et non identiques.
4. `payload.conversion_goal_ecommerce` ET `payload.conversion_goal_local`
   distincts.
5. `local_canon.validated: true` (sinon BLOCK systématique).

Toute violation → DTO Zod refuse, le brief n'arrive jamais en
`__marketing_brief`.

### Cas d'école

> Client e-commerce dans le 93 ayant abandonné un panier de plaquettes de
> frein → propose `cta_ecommerce: "Reprenez votre commande en ligne"` +
> `cta_local: "Ou venez chercher en magasin sous 30 min"` avec
> `hybrid_reason: "client zone magasin, rupture livraison standard"`.

---

## Distribution canonique

Ce fichier est la **source unique** dans `governance-vault/ledger/rules/`.
Synchronisation vers monorepo via :

1. **Source de vérité** : ce fichier
2. **Hash SHA-256 publié** : `99-meta/canon-hashes.json` clé `marketing_voice`
3. **Copie dérivée monorepo** : `.claude/canon-mirrors/marketing-voice.md` (et
   miroir `workspaces/marketing/.claude/canon-mirrors/marketing-voice.md`)
   — sous `canon-mirrors/` pour ne pas être chargée comme rule Claude Code.
4. **Workflow vault** : `.github/workflows/canon-publish.yml` ouvre une PR auto
   dans le monorepo à chaque modification mergée ici.
5. **Vérification CI monorepo** : workflow `marketing-voice-hash.yml` (miroir
   `agent-exit-contract-hash.yml`) compare hash local vs `99-meta/canon-hashes.json`
   via `gh api`. Fail = blocage merge.
6. **Lecture runtime** : `brand-compliance-gate.service.ts` lit la copie locale
   uniquement (jamais filesystem vault — viole ADR-012 séparation 3-VPS).

---

## Versionnage

| Version | Date | Changements |
|---|---|---|
| 1.0.0 | 2026-04-30 | Création initiale (proposed). 3 voix : ECOMMERCE, LOCAL, HYBRID. Section `local_canon` à compléter par le métier avant `validated: true`. |
| 1.0.1 | 2026-05-04 | Patch path : copies monorepo relocalisées de `.claude/rules/` vers `.claude/canon-mirrors/` pour ne pas alourdir le contexte projet Claude Code (~6K tokens/tour). Backend runtime path à update conjointement (`marketing-matrix.service.ts:48`). Aucune règle modifiée. |

## Référence

- [[ADR-036-marketing-operating-layer]] — création canon
- [[rules-agent-exit-contract]] — AEC v1.0.0 obligatoire pour tout agent
- [[rules-ai-cos]] — AI4 QTO valide AVANT publication
- ADR-012 — 3-VPS architecture (DEV vault SoT, PROD/AI-COS read-only)
- ADR-015 — Vault single source of truth
- Plan rev 5 : `/home/deploy/.claude/plans/verifier-la-strategie-une-piped-hummingbird.md`
