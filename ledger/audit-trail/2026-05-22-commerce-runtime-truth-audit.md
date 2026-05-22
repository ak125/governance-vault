---
date: 2026-05-22
type: audit-trail
related: [ADR-058, ADR-062, MOC-Knowledge, MOC-AuditTrail]
sources:
  - repo: ak125/php (legacy PHP site) @ 8b601e237ecc92ae12e70a706cbdb4ba62ced3c5
  - repo: ak125/nestjs-remix-monorepo @ main (2026-05-22)
  - db: Supabase cxpojprgwgubzjyqzmoq (live, read-only probes)
---

# 2026-05-22 — Commerce Reconciliation & Runtime Truth Audit (legacy PHP ↔ runtime actuel)

> **Doctrine.** Le PHP legacy **n'est pas une cible d'implémentation** — c'est un **témoin
> historique**. On ne migre pas le code ; on récupère uniquement les **invariants métier prouvés**,
> puis on les **reconstruit *mieux*** dans l'architecture actuelle (Redis lock, events, audit trail,
> observabilité, tests, DB contract). **Jamais** de PHP recopié. Cet audit *constate* — il ne change
> aucun comportement ; les fixes sont des décisions owner séparées (candidats issue/ADR).

## Pourquoi cet audit

Le NestJS réimplémente la logique commerce legacy, mais une comparaison `legacy ↔ code` est
**statique** : un code peut exister sans être câblé, ou écrire dans un schéma qui n'existe pas. Audit
à **4 couches** (Legacy behavior · Current code · **Runtime wiring** · Business impact), enrichi d'une
**chaîne de propagation** (Capture→Persistence→Propagation→Consumption→Monitoring). Contexte
empirique : trafic SEO présent, conversion ~0.17 %, attribution faible (cf. reality-audit PR #652).
**Clé** : legacy et prod partagent le **même schéma `___xtr_*`** → l'état DB réel est la preuve
d'exécution la plus forte (colonne 100 % NULL = invariant mort, quoi qu'en dise le code).

## Légende

**Verdict** : `Préservé-identique` · `Préservé-différemment` · `Simplification acceptable` ·
`Supprimé volontairement` · `Abstraction spéculative` (jamais un invariant prouvé) ·
`Anti-pattern legacy` (à constater, jamais reconstruire) · `Régression involontaire` ·
`Régression critique` · `Inconnu`.
**Wiring** : `Actif` · `Partiellement câblé` · `Mort/cassé` · `Inconnu`.
**Priorité** : `P0` conversion/paiement/fulfillment · `P1` attribution/funnel · `P2` UX/admin · `P3` secondaire.

## Synthèse des findings

| # | Invariant | Legacy @8b601e23 | Current | Wiring | Verdict | Risk | Prio |
|---|-----------|------------------|---------|--------|---------|------|------|
| F1 | Add-to-cart source par-ligne (`urltakentoadd`) | `shopping_cart.function.php:16` | `___xtr_order_line.orl_website_url` (aucun code) | **Mort** (orphelin) | Régression involontaire | critique | **P1** |
| F2 | Verrou panier checkout (`verrouille`) | `shopping_cart.function.php:8,31` | absent | **Mort** | Régression involontaire | moyen | P1 |
| F3 | State-machine statut ligne (sémantique) | `commande.line.status.{1..6,91..94}.php` | `order-status.service.ts:5-36` vs `order-actions.service.ts:34-134` | **Doublon : 1 cassé / 1 actif** | Régression critique | critique | **P0** |
| F4 | Scoring + auto-assign fournisseur | `supplier.affect.to.pm.php` | `suppliers.service.ts:433-510` | **Mort** (colonnes absentes) + non câblé au flux commande | Abstraction spéculative | critique | **P0** |
| F5 | Autorité de prix (`custom_price` / `prix`) | `shopping_cart.function.php:14` | `cart-items.controller.ts:88-95` (OptionalAuthGuard) | Actif (non audité) | Régression involontaire (sécu) | critique | **P1** |
| F6 | Frais de port | `commande.shippingfee.php` (par département) | `shipping-calculator.service.ts` (zones postales Colissimo) | Actif | Préservé-différemment / Amélioré | faible | P2 |

---

## F1 — Add-to-cart source par-ligne (`urltakentoadd`) · **P1, régression involontaire, risk critique**

- **Legacy** : `config/shopping_cart.function.php:16` — `$_SESSION['amcnkCart']['urltakentoadd'][] =& $select['urltakentoadd']` : chaque article du panier mémorise **l'URL d'où il a été ajouté** (page/listing/gamme/compatibilité véhicule → intention).
- **Current code** : la colonne `___xtr_order_line.orl_website_url` existe et porte cette sémantique, mais **aucun code backend/frontend ne la lit ni ne l'écrit** (grep `orl_website_url|website_url|urltakentoadd` → 0 hit hors SEO `sourceUrl`, concept distinct).
- **DB live** : 2506 lignes, `orl_website_url` peuplé à **71 %** (732 vides). Donnée historiquement présente.
- **Attribution moderne existante mais à un autre grain** : `___xtr_order.{ga_client_id,landing_source,landing_path}` capturée (`orders.controller.ts:382-388,565-573`) et propagée à GA4 (`paybox-callback.controller.ts:289-340`). Mais c'est **niveau commande (landing)**, pas **par-ligne (source d'ajout)**.

**Chaîne de propagation** : Capture (legacy/inconnue) → **Persistence ✅ (71 %)** → Propagation ❌ → Consumption ❌ → Monitoring ❌ ⇒ **vivant en DB, mort dans le système décisionnel.** C'est le cas d'école « trafic OK, conversion non attribuée » : on ne sait pas quelle page/quelle requête SEO génère réellement les add-to-cart par pièce.

**Cible de reconstruction** : attribution event graph — câbler la source d'ajout par-ligne (capture front à l'add-to-cart → event → `__seo_event_log` / funnel #676 → dashboard) afin de mesurer les add-to-cart SEO réels et nourrir le funnel R5→R3→R2. Granularité ligne complémentaire au landing commande.

## F2 — Verrou panier pendant checkout (`verrouille`) · **P1, régression involontaire, risk moyen**

- **Legacy** : `shopping_cart.function.php:8` et `:31` — `ajout()` et `supprim_article()` ne mutent le panier que si `$_SESSION['amcnkCart']['verrouille'] != true`. Invariant : **pendant la finalisation, le panier est gelé** (intégrité prix/quantité, anti-double-mutation, sémantique d'abandon).
- **Current** : aucun équivalent (grep `verrouill|cartlock|lockCart` → seul un commentaire SEO sans rapport). Le panier serveur (Redis/session) reste mutable pendant le checkout.
- **Verdict** : invariant perdu silencieusement (ni `Supprimé volontairement` documenté, ni remplacé).

**Cible de reconstruction** : **Redis distributed lock + TTL** posé à l'entrée du checkout, libéré au paiement/abandon — reconstruction *meilleure* que le flag session legacy (atomique, multi-instance, expirant).

## F3 — State-machine statut ligne · **P0, régression critique, risk critique**

**Vérité canonique (DB lookup `___xtr_order_line_status`)** — modèle **statut-pièce + workflow équivalence** :

| id | label réel | id | label réel |
|----|-----------|----|-----------|
| 1 | Pièce en attente | 6 | Pièce commandée chez fournisseur |
| 2 | Pièce annulée | 91 | Proposition d'équivalence |
| 3 | Pièce non compatible | 92 | Équivalence acceptée |
| 4 | Pièce non disponible | 93 | Équivalence refusée |
| 5 | Pièce disponible | 94 | Valider l'équivalence |

Distribution réelle (2506 lignes) : `1`=1494, `null`=673, `2`=184, `6`=115, `4`=18, `92`=10, `91`=4, `93`=4, `5`=3, `3`=1. **Aucun** « expédié/livré/retour/remboursé ».

**Deux implémentations concurrentes** :
- ✅ **`order-actions.service.ts:34-134` (ACTIVE)** — colonnes réelles `orl_orls_id`, `orl_equiv_id`, `orl_spl_*` ; statut 6 = commande fournisseur ; reset équivalence ; **émet `ORDER_EVENTS.LINE_STATUS_CHANGED` + audit trail**. Sémantique correcte (équivalence). Câblée via `order-actions.controller.ts`.
- ❌ **`order-status.service.ts:5-36` (MORTE/CASSÉE)** — enum **faux** (`SHIPPED`/`DELIVERED`/`RETURNED`/`REFUNDED`, modèle colis Amazon-like) ; lit/écrit des colonnes **inexistantes** (`.eq('id',…)`, `currentLine.status`, `.update({status,updated_at})`, `order_id` — la table physique a `orl_id`/`orl_orls_id`/`orl_ord_id`/`orl_updated_at`) ; insère l'historique dans `___xtr_order_line_status` qui est une **table de lookup** (pas d'historique) → l'écriture échouerait. Exposée via `order-status.controller.ts`.

**Verdict** : régression critique = **double source de vérité** + un service qui véhicule un **modèle mental faux** (colis) contredisant le modèle réel (statut-pièce/équivalence), opérant sur un schéma fictif.

**Cible de reconstruction** : retirer `OrderStatusService`/`OrderLineStatusCode`/`order-status.controller` ; **single SoT event-driven** = `OrderActionsService`, enum aligné sur la lookup DB, transitions validées contre la sémantique réelle (incl. sous-workflow équivalence 91→92/93→94), audit trail conservé.

## F4 — Scoring + auto-assign fournisseur · **P0, abstraction spéculative, risk critique (fulfillment)**

- **Legacy (vérité schéma)** : `supplier.affect.to.pm.php:78-79` insère dans `___XTR_SUPPLIER_LINK_PM (SLPM_ID, SLPM_PM_ID, SLPM_SPL_ID, SLPM_DISPLAY)` ; `:164-167` lit `SPL_ID, SPL_NAME FROM ___XTR_SUPPLIER WHERE SPL_DISPLAY=1`. **Le legacy n'a jamais eu** discount_rate / delivery_delay / is_preferred.
- **DB live** : `___xtr_supplier` = `spl_id, spl_name, spl_alias, spl_display, spl_sort` ; `___xtr_supplier_link_pm` = `slpm_id, slpm_pm_id, slpm_spl_id, slpm_display`. Aucune des colonnes du scoring n'existe.
- **Current code** : `suppliers.service.ts:433-510` `calculateSupplierScore` lit `supplier.discount_rate`, `supplier.delivery_delay`, filtre `___xtr_supplier_link_pm.eq('supplier_id', …)` et `link.is_preferred`. **Tous ces champs/colonnes sont inexistants** → chaque conditionnel lit `undefined` ⇒ **chaque fournisseur score exactement 50** (base) ⇒ l'« auto-assign meilleur fournisseur » est une **illusion no-op**.
- **Wiring** : `autoAssignSuppliers` exposé en **HTTP manuel** (`suppliers.controller.ts:509,562`) mais **jamais appelé depuis la création/validation de commande**. DB confirme : `orl_spl_id` vide à **95 %** (2386/2506).

**Verdict** : abstraction spéculative (fields inventés au-delà même du legacy) + non câblée au fulfillment. Risque : décision d'approvisionnement non outillée.

**Cible de reconstruction** : (a) décider si l'enrichissement fournisseur (délai/remise/préféré) est un vrai besoin → si oui, **DB contract** explicite (colonnes + migration gouvernée), sinon **supprimer le scoring fictif** ; (b) **fulfillment projection** câblée à la création de commande (lecture seule, observable).

## F5 — Autorité de prix (`custom_price`) · **P1, régression involontaire (sécurité), risk critique**

- **Legacy** : `shopping_cart.function.php:14` — le panier session porte `prix` par article (origine serveur, page produit).
- **Current** : `cart-items.controller.ts` est sous **`@UseGuards(OptionalAuthGuard)`** (auth facultative) ; `add-item.dto.ts:39` / `update-item.dto.ts:10` acceptent `custom_price: z.number().positive().optional()` ; `cart-items.controller.ts:88-95` le passe tel quel à `addCartItem(...)`. Aucun audit trail ni guard admin visible sur ce paramètre.
- **Risque** : prix potentiellement fixé côté client sur un endpoint non-authentifié. **Revue sécurité price-authority requise** (l'audit ne démontre pas l'exploitabilité de bout en bout, mais l'invariant « le prix de vente est autorité serveur » n'est pas visiblement garanti).

**Cible de reconstruction** : prix = **autorité serveur** (catalogue) ; tout override = **admin-guard + signé + audit trail** ; `custom_price` jamais accepté d'un client anonyme.

## F6 — Frais de port · **P2, préservé-différemment / amélioré, risk faible**

- **Legacy** : `commande.shippingfee.php` calcule par **département** (`ord_dept_id` existe encore en DB).
- **Current** : `shipping-calculator.service.ts` — zones postales Colissimo (France/Corse/DOM-TOM), seuil franco 150 €, paliers poids, multi-colis ≥30 kg. Câblé au panier (`cart-items.controller.ts` `computeShippingAndTotal`).
- **Verdict** : redesign volontaire plus fin que le legacy. Pas de régression apparente. (Note connexe hors-scope : TVA codée en dur `1.2` dans `order-actions.service.ts:81` — `TODO: récupérer taux réel`.)

---

## Couche DB contract / invariants (récapitulatif)

| Colonne / invariant | Existe DB | Peuplée | Écrite par le code actuel | Statut |
|---------------------|-----------|---------|---------------------------|--------|
| `orl_website_url` (add-source) | ✅ | 71 % | ❌ aucun code | orphelin |
| `orl_equiv_id` (équivalence) | ✅ | 1.2 % | ✅ `order-actions` | actif (peu utilisé) |
| `orl_spl_id` (fournisseur) | ✅ | 5 % | ✅ `order-actions` (statut 6 manuel) | sous-utilisé |
| panier `verrouille` | ❌ | — | ❌ | invariant perdu |
| `___xtr_supplier.discount_rate/delivery_delay` | ❌ | — | lu (fictif) `suppliers.service` | fictif |
| `___xtr_supplier_link_pm.is_preferred/supplier_id` | ❌ | — | lu (fictif) `suppliers.service` | fictif |
| `ga_client_id/landing_source/landing_path` | ✅ | — | ✅ `orders.controller`→GA4 | actif (commande) |

## Coverage manifest (anti-overclaim)

- **Lu & vérifié** : legacy `shopping_cart.function.php`, `supplier.affect.to.pm.php`, `commande.line.status.91.php`, `commande.shippingfee.php` (en-tête) @8b601e23 ; current `order-status.service.ts`, `order-actions.service.ts`, `suppliers.service.ts` (scoring), `cart-items.controller.ts`, `add/update-item.dto.ts`, fragments `orders.controller.ts`/`paybox-callback.controller.ts` ; DB live `___xtr_order_line`, `___xtr_order_line_status`, `___xtr_order`, `___xtr_supplier`, `___xtr_supplier_link_pm`.
- **Non lu (hors scope / différé)** : ~234 autres `.php` legacy (blog/SEO, sélecteur véhicule, paiement). `core/_payment/` **lecture seule** (règle stricte `payments/`). Frontend `panier.*` Remix : appel client add-to-cart non tracé ligne-à-ligne (F1 reste `Régression involontaire` — la capture front exacte est `Inconnu`, à confirmer si reconstruction).
- **Verdicts `Inconnu` assumés** : capture exacte de `orl_website_url` (qui l'écrit aujourd'hui ?).

## Triage (P0/P1 — candidats issue/ADR, décision build = owner)

| Prio | Finding | Reconstruction moderne | Couplage stratégie |
|------|---------|------------------------|--------------------|
| **P0** | F3 double SoT statut | retirer `OrderStatusService`, single SoT event-driven aligné lookup DB | intégrité fulfillment + équivalence |
| **P0** | F4 scoring fournisseur fictif | DB contract réel ou suppression + fulfillment projection câblée | fulfillment |
| **P1** | F1 add-source orphelin | attribution event graph (capture→event→funnel→dashboard) | **funnel/conversion** |
| **P1** | F5 autorité de prix | prix autorité serveur + override signé/admin/audit | sécurité commande |
| **P1** | F2 verrou checkout | Redis lock + TTL | intégrité panier |

## Hors scope — évolution future (NE PAS faire maintenant)

Cet audit s'arrête à *capté → propagé → consommé → monitoré*. Il **ne traite pas** la **Commerce
Feedback Loop** (`Signal → Propagation → Consumption → **Decision** → **Learning**`) : le système
change-t-il une action et s'améliore-t-il grâce au signal ? Différé délibérément (discipline
STOP-après-livraison / V1-first) : prouver d'abord que les signaux sont vivants et propagés ; la boucle
décision/learning sera un chantier gouverné **séparé**, gated par ces findings.

## Constat central

Le vrai problème n'est ni PHP ni NestJS/Remix, mais la **perte de propagation des signaux business**
(F1 attribution orpheline, F3 modèle de statut faux, F4 fournisseur fictif). C'est ce qui explique le
mieux : trafic présent, commandes faibles, attribution faible. On reconstruit ces invariants *mieux*
(control plane commerce, compatible ADR-058/062) — sans ressusciter le legacy.
