---
title: "ADR-084: Gouvernance de l'écriture pieces_price + visibilité storefront (Pricing Control Plane)"
status: proposed
version: 1.0.0
authors: [Fafa]
created: 2026-06-13
updated: 2026-06-13
supersedes: []
superseded-by: []
tags: [architecture, pricing, governance, commerce]
---

# ADR-084: Gouvernance de l'écriture `pieces_price` + visibilité storefront

> **DRAFT hors-vault (`/tmp/`) — relire, signer G3, ouvrir en PR `governance-vault` (owner).**
> Numéro `084` provisoire (vus jusqu'à ADR-083 ; confirmer le libre contre le vault).
> **Enregistre des décisions déjà shippées + déjà enforced** (record rétroactif), pas une
> nouvelle architecture. **Une seule décision** : le cycle d'écriture coût→vente→dispo→
> affichage de `pieces_price`. L'architecture des *surfaces de collecte* dispo = **ADR-085**.

## 📊 Status
**Status:** Proposed · **Date:** 2026-06-13 · **Decision Makers:** Fafa (owner)

## 🎯 Context
`pieces_price` est lue par tous les chemins de prix (search, products, RPC R2). Un mauvais
chemin d'écriture a déjà coûté cher : le 1er load NK via un **worker INSERT direct**
(`pri_dispo=null`) a laissé **30 621 prix invisibles** (inertes, hors invariants/historique/
rollback). Il faut un **chemin d'écriture unique gouverné** et des invariants économiques
lisibles (doctrine *Economic Governance System* — gouvernance, pas pricing-engine).

## 🤔 Decision
Le cycle tarif de `pieces_price` est gouverné par **un seul chemin** et 4 invariants, déjà
en vigueur :

1. **Écriture = PricingModule gouverné UNIQUEMENT.** INSERT/UPDATE direct (worker, script,
   SQL standalone) **interdit**. Endpoints canon `POST /api/admin/pricing/import|activate|
   display/*` ; les écritures réelles passent par **RPC** (`pricing_commit_chunk` /
   `pricing_activate_chunk`), jamais le query-builder.
   *Enforcement :* (a) supabase-guard G6 (#879) bloque le `UPDATE/DELETE` **brut via MCP
   execute_sql** ; (b) **guard ast-grep `commerce-no-direct-pieces-price-write` (PR #962)**
   bannit `.from('pieces_price').{insert,update,upsert,delete}` hors `modules/pricing/` —
   0 faux positif (tous les writes actuels = RPC ; les 9 `from('pieces_price')` du code =
   `.select`). Avant #962 = doctrine-only (incident NK = preuve du trou).
2. **Jamais à perte** : `vente_HT ≥ achat_HT`. *Enforced :* `pricing-invariants.service.ts`
   → `VENTE_BELOW_ACHAT` (+ `ACHAT_NOT_POSITIVE`, `MARGE_EXCEEDS_MAX`, `TVA_NOT_WHITELISTED`,
   `DELTA_EXCEEDS_MAX`). Quantités via `pri_qte_cond`/`pri_qte_vente` (pas de « ÷2 » bricolé).
3. **Import ≠ activation ≠ affichage** (3 états séparés) : commit met le **coût** en base en
   **PENDING** (`pri_dispo='0'`, défaut `activate:false`, `pri_ref` persisté #913) ;
   l'activation (`'1'`/`'2'`/`'3'`) ne porte que sur les réfs **CONFIRMED au portail** ;
   l'affichage (`piece_display`) est un 3ᵉ gate (gate gamme `pg_display` #915).
4. **R2-bruit** : une réf **non-vendable ne s'affiche pas sur R2** (page mince = bruit SEO/UX).
   *Enforced :* `display/quarantine` (piece_display true→false, brand-locké, réversible) +
   gate `can_sell` #850 ; complément SEO = flag R2-noindex #916 (catalogue-wide, owner-gated).

## 🔍 Considered Options
### Option 1 — Chemin unique gouverné (RPC) + invariants L2 — **RETENUE**
**Pros:** auditabilité/historique/rollback ; 0 prix invisible ; 0 vente à perte ;
compréhensible humainement (≤15 min d'audit des règles actives).
**Cons:** plus de cérémonie (gates owner) qu'un INSERT direct. **Cost:** faible (déjà bâti).
### Option 2 — Workers/scripts standalone (INSERT direct) — **REJETÉE**
**Cons:** système parallèle, pas d'invariants/historique/rollback ; **incident NK réel**
(30 621 prix invisibles). **Cost:** dette + incidents.
### Option 3 — Lire le prix depuis l'observatoire `supplier_offer_snapshot` — **REJETÉE**
**Cons:** confond observatoire ↔ SoT coût (`pieces_price.pri_achat_ht_n`) ; supplier-sync
dormant + observations brutes (cf. ADR-085). **Cost:** dérive de SoT.

## 🎯 Decision Rationale
1. **No silent fallback / no parallel system** (CLAUDE.md). 2. **Compréhensibilité humaine
   d'abord** (gouvernance économique, pas engine ; anti-patterns dynamic/ML/auto-repricing
   interdits par défaut). 3. **Réutiliser si meilleur, sinon meilleure solution, zéro
   bricolage**. **Trade-off accepté** : cérémonie de gates contre auditabilité + réversibilité.

## 📈 Consequences
**Positive :** toute MAJ dry-runnable/atomique/réversible/historisée ; 0 prix invisible /
0 vente à perte / 0 bruit R2 par construction. **Negative :** pas de repricing dynamique
(volontaire). **Neutral :** activation du flag #916 = décision séparée.

## 🔧 Implementation (en grande partie DÉJÀ LIVRÉ)
- [x] PricingModule + endpoints + invariants L2 (#707/#709) · `pri_ref` (#913) · display gamme
  (#915) · `can_sell` (#850) · supabase-guard G6 (#879) · méthode figée skill+runbook (#926).
- [x] **Guard ast-grep `commerce-no-direct-pieces-price-write` (#962)** — invariant 1 rendu mécanique.
- **Rollback :** chaque étape a un rollback batch LIFO (`import|activate|display|display/quarantine /rollback`).

## ⚠️ Risks
- **Contournement par futur worker** — *Prob. Low / Impact High* — mitigé par #962 + G6 + cet ADR.
- **Vente sous coût marché (non à perte mais non-compétitif)** — *Med/Med* — étape 2 vérif
  concurrence (séparée du gate anti-perte).

## 🔗 Related Decisions
- Depends on: Pricing Control Plane V1 (#707/#709). · Relates to: **ADR-085** (surfaces dispo).
- Source legacy: `MARGE_NEW_2021.xls` (grille marge).

## 📚 References
- Skill : `.claude/skills/supplier-price-load/SKILL.md` · Runbook (8 gates) :
  `.claude/knowledge/ops/supplier-brand-price-load-procedure.md` · Doctrine :
  `docs/pricing/economic-governance-system.md`.
- PRs : #707/#709 #850 #879 #913 #915 #926 #962.
- MEMORY : `reference_supplier_pricing_via_governed_module`,
  `feedback_never_sell_at_loss_pricing_invariant`, `reference_supplier_remise_per_brand_per_subfamily`,
  `feedback_pricing_is_economic_governance_not_engine`.

## 📝 Notes
Méthode opératoire **non dupliquée** : l'ADR enregistre la **décision** ; le **comment** =
skill + runbook (liens).

## 🔄 Review
**Review Date:** 2026-12-13 · **Criteria:** demande de dynamic/auto-repricing, ou nouveau
chemin d'écriture `pieces_price`.

## 🔄 Change Log
### v1.0.0 (2026-06-13) — ADR initial (record canon de décisions shippées + enforced).
