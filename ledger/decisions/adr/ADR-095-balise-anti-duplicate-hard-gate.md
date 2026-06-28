---
id: ADR-095
title: Gate dure anti-duplicate balises R0→R8
status: Accepted
date: 2026-06-27
deciders: [Fafa]
supersedes: []
amends: [ADR-066]      # gate structurel catalog_signature — la balise est la couche sœur
tags: [seo, balise, anti-duplicate, R8, R2, hard-gate]
---

# ADR-095 — Gate dure anti-duplicate des balises émises (R0→R8)

## Statut
Proposed — débloque **D-3** (hard-gate `indexable_effective`) du plan balises. D-0/D-1/D-2
(crawl baseline, `SeoFingerprintCore` pur, mesure `r8-diversity-check`) sont déjà livrés en
**shadow/report-only** et n'exigent pas cet ADR ; **seul le verdict bloquant le requiert**.

## Contexte
Les balises sœurs (motorisations d'un même modèle) collisionnent (title/H1/meta-desc). Le socle
anti-duplicate existant (`__seo_r8_fingerprints`, `r8-diversity-check`, `catalog_signature` ADR-066)
couvre le **contenu**, pas les **balises émises**, et ne voit que ~0.54 % des pages affichables.
Poser un **verdict dur** (bloquant) sur une collision de balise = **décision canon** : elle modifie
le comportement de publication/flip et doit être gouvernée avant toute implémentation D-3
(cf. `feedback_no_canon_claim_without_vault_adr`).

## Décision
1. **Périmètre du hard-gate = `indexable_effective`** (200 ∧ index ∧ canonical cohérent ∧ ¬soft-404
   ∧ ¬noindex), **PAS** `type_display='1'`. Autorité = `computeIndexabilityVerdict()` /
   `R2IndexabilityGate` **live, déterministe** — **jamais** le snapshot async (rétrogradé en
   drift-detector).
2. **Hard uniquement sur la collision EXACTE** de `title` / `H1` / identité, sur pages
   `indexable_effective`. `near-dup` (pg_trgm) = **report-only `CALIBRATION_PENDING`** jusqu'à P-7.
   Catalogue/FAQ factuellement partagés = **report-only** (exemption gouvernée, label override
   patron R-SEO-09).
3. **« Bloque le changement, pas la page »** : la gate refuse l'**application d'un changement** qui
   introduit/maintient une collision exacte (publication / flip / activation / remplacement balise /
   passage INDEX d'un lot). Elle **ne mute jamais** URL / canonical / robots / noindex / suppression —
   toute désindexation reste une décision séparée owner-gated.
4. **Gouvernance flag** : activée via la clé réservée `SEO_CHAIN_DUPLICATE_GATE_MODE`
   (`SeoChainFlagKeySchema`), rollout **shadow → enforce** par surface, observabilité via
   `__seo_event_log` (`observation_kind=BALISE`), rollback par flag (ADR-055).

## Conséquences
- **+** D-3 peut implémenter un verdict bloquant gouverné, observable, réversible, per-surface.
- **+** Aucun système parallèle : étend `r8-diversity-check` / Observatory / `computeIndexabilityVerdict`.
- **−** Un changement introduisant une collision exacte sur page indexable sera refusé (comportement
  voulu) → nécessite un discriminant (puissance/carburant) avant publication.
- Calibration des seuils near-dup (P-7) reste hors de cet ADR (report-only d'ici là).

## Références
- Plan balises R0→R8 rév.9 (P-PRECOND.1 / D-3).
- ADR-066 (catalog_signature, gate structurel) — amendé/complété.
- ADR-055 (flips), ADR-064 (control plane 4-layer), ADR-075 (vocab deploy).
