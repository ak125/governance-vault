---
title: "ADR-085: Architecture des surfaces de disponibilité fournisseur (3 surfaces + couches partagées)"
status: proposed
version: 1.0.0
authors: [Fafa]
created: 2026-06-13
updated: 2026-06-13
supersedes: []
superseded-by: []
tags: [architecture, supplier, availability, anti-redundancy]
---

# ADR-085: Architecture des surfaces de disponibilité fournisseur

> **DRAFT hors-vault (`/tmp/`) — relire, signer G3, ouvrir en PR `governance-vault` (owner).**
> Numéro `085` provisoire (confirmer contre le vault). **Record d'une architecture déjà
> shippée** (#908/#960). **Une seule décision** : comment la *disponibilité fournisseur* est
> collectée/classifiée (couche portail). La gouvernance d'**écriture du prix** = **ADR-084**.

## 📊 Status
**Status:** Proposed · **Date:** 2026-06-13 · **Decision Makers:** Fafa (owner)

## 🎯 Context
Plusieurs besoins fournisseur touchent les **mêmes portails** (DCA inoshop, CAL ASP.NET) :
classer un feed complet avant activation, observer la dispo en continu, spot-checker un prix.
Sans cadrage, le risque #1 d'agent est de **réinventer une surface parallèle** (re-câbler le
pipeline, dupliquer le connecteur, recréer un breaker, confondre l'observatoire avec une
source de prix). Vérifié à fond 2026-06-13 (audit 3-agents read-only) : **3 surfaces
distinctes existent, métiers orthogonaux, couches partagées — aucun doublon.**

## 🤔 Decision
**Trois surfaces fournisseur distinctes, jamais de système parallèle**, partageant les
**mêmes couches** :

| Surface | Fichier | Métier | Sortie | Plateformes |
|---|---|---|---|---|
| **classify** | `workers/supplier-availability-classify.ts` | full-feed pré-activation : quels refs peuvent devenir vendables | **buckets d'activation** (CONFIRMED/BLOCK/REVIEW), read-only | inoshop only (bulk `/search`) |
| **supplier-sync** | `modules/supplier-truth/supplier-sync.runner.ts` | **observatoire** continu prix+dispo | `supplier_offer_snapshot` (observations brutes + `parse_confidence`) | DCA+CAL, **DORMANT** (flag `SUPPLIER_TRUTH_SYNC_ENABLED`) |
| **supplier-price-verify** | `workers/supplier-price-verify.ts` | spot-check N-échantillon avant import | verdict CONFIRMED/FIX_FEED/REVIEW/BLOCK | inoshop+CAL |

**Couches PARTAGÉES (réutilisées par les 3, jamais dupliquées) :**
- **Connecteurs** (couche portail unique) : `connectors/supplier-registry.ts` (générique
  `spl_id`/platform/creds) + `inoshop.connector.ts` + `cal.connector.ts` (login, token,
  jitter anti-ban, `fetchSearchRaw` bulk / `fetchAvailability` per-ref).
- **Classification** : `connectors/inoshop-search-parse.ts` (`verdictForRef`/`ActivationBucket`) — pure.
- **Résilience** : `connectors/portal-classify-resilience.ts` (#960) — module **pur testé**
  (bisection + budget par-ref + circuit-breaker + dead-letter `REVIEW_PORTAL_TIMEOUT`).

**classify ≠ DCA-only** : générique via registry ; la limite `platform === 'inoshop'` est une
**contrainte portail** (seul inoshop expose le bulk `/search`), **pas un hardcode** — la dispo
CAL passe par supplier-sync / price-verify.

## 🔍 Considered Options
### Option 1 — 3 surfaces distinctes + couches partagées — **RETENUE**
**Pros:** un seul connecteur/parse/résilience réutilisés ; métiers clairs ; pas de double-conso.
**Cons:** 3 entrées à connaître (mitigé par la carte `suppliers.md`). **Cost:** faible (déjà bâti).
### Option 2 — Fusionner classify dans supplier-sync — **REJETÉE**
**Cons:** conflate full-feed pré-activation (buckets) et observatoire continu (snapshot) ;
cadences/sorties incompatibles. **Cost:** couplage + perte de lisibilité.
### Option 3 — Wrapper « session » partagé login/token — **REJETÉE**
**Cons:** devrait ponter Nest-DI (supplier-sync) ↔ CLI tsx standalone (classify) = **abstraction
forcée = bricolage**. Le **connecteur** est déjà la couche de session partagée. **Cost:** complexité nette.
### Option 4 — Module de résilience générique (BullMQ / breaker ai-content réutilisé) — **REJETÉE**
**Cons:** BullMQ = mauvais outil (portail mono-session) ; `CircuitBreakerService` ai-content =
gate par-provider, couplage inter-module. Aucun n'est un ordonnanceur de batch avec dead-letter
par-item → module pur dédié = meilleure solution.

## 🎯 Decision Rationale
**Prefer extension over creation / no parallel system** (CLAUDE.md). **Réutiliser si meilleur,
sinon meilleure solution, zéro bricolage** : connecteurs+parse réutilisés ; résilience = nouveau
module (rien d'existant n'était meilleur) ; pas de wrapper forcé.

## 📈 Consequences
**Positive :** ajout d'un fournisseur = 1 entrée registry ; 1 seul endroit pour la
résilience/parse ; pas de confusion observatoire↔prix. **Negative :** une plateforme sans
route bulk ne peut pas full-feed classify (→ per-ref). **Neutral :** supplier-sync reste dormant.

## 🔧 Implementation (DÉJÀ LIVRÉ)
- [x] Connecteurs + registry (DCA+CAL) · classifieur `inoshop-search-parse` · 3 workers.
- [x] Consolidation classify (#908) + résilience pure testée (#960).
- [x] Carte d'architecture : `.claude/knowledge/modules/suppliers.md`.

## ⚠️ Risks
- **Confusion observatoire ↔ source de prix** — *Med/Med* — carte `suppliers.md` + gotchas ;
  supplier-sync dormant + observations brutes (≠ buckets). Le prix = ADR-084 (`pieces_price`).
- **Recréer un breaker parallèle** — *Low/Med* — `portal-classify-resilience.ts` est le seul ;
  les breakers ai-content/rag-proxy sont d'un autre domaine (gate par-provider).

## 🔗 Related Decisions
- Relates to: **ADR-084** (écriture `pieces_price`). · Source : pipeline supplier-sync
  (#831/#837, `supplier_offer_snapshot`).

## 📚 References
- Archi : `.claude/knowledge/modules/suppliers.md` (carte 3 surfaces) · Runbook :
  `.claude/knowledge/ops/supplier-brand-price-load-procedure.md` · Skill : `supplier-price-load`.
- PRs : #831 #837 #908 #960. · MEMORY : `project_supplier_verify_consolidation_20260608`,
  `feedback_reuse_if_better_else_best_no_bricolage`, `feedback_one_frozen_method_no_improvised_variants`.

## 🔄 Review
**Review Date:** 2026-12-13 · **Criteria:** ajout d'une plateforme portail, activation de
supplier-sync, ou besoin d'une 4ᵉ surface.

## 🔄 Change Log
### v1.0.0 (2026-06-13) — ADR initial (record d'architecture déjà shippée #908/#960).
