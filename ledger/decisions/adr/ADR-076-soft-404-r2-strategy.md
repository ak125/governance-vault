---
id: ADR-076
title: "Soft-404 R2-PRODUIT — Multi-tier alternatives + JSON-LD ItemList + append-only telemetry"
status: accepted
date: 2026-05-18
decision_date: 2026-05-18
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: []
related_adr: [ADR-016, ADR-022, ADR-026, ADR-031, ADR-070]
related_rules: [G1, T1]
related_incidents: []
reviewed_by: "@fafa"
---

# ADR-076 : Soft-404 R2-PRODUIT — Multi-tier alternatives + JSON-LD ItemList + append-only telemetry

## Contexte

La route Remix `/pieces/:gamme/:marque/:modele/:type.html` (R2-PRODUIT) sert un triplet véhicule + gamme valides mais peut tomber sur un couple `(type_id, pg_id)` sans relation dans `pieces_relation_type` (trou de catalogue ciblé, ex. vérifié sur BMW 525d F10 × `kit-de-freins-arriere`).

Avant cette ADR, la page servait un placeholder "Non disponible" avec `noindex, follow` et un composant `NoProductsAlternatives` câblé sur un endpoint `/api/rm/alternatives` retournant des alternatives non compat-aware (ordre alphabétique pour les gammes, marques mélangées pour les véhicules — ex. Alfa Romeo en N°1 sur une BMW). Aucune télémétrie, aucun JSON-LD structuré, aucune capture de demande commerciale.

## Décision

Adopter un pattern soft-404 R2 unifié, composé de cinq invariants :

1. **HTTP 200 + `robots: noindex, follow`** sur la branche `noProducts`. Pas 404/410 — le triplet véhicule existe en catalogue, seul le couple (gamme × type) est creux.
2. **Pas de canonical sur la page soft-404.** Canonicaliser vers une autre page serait un signal contradictoire avec `noindex` (cf. Google Search Central "Soft 404 errors").
3. **JSON-LD `ItemList`** émis dans le `<head>`. Google crawle en `follow` ; l'`ItemList` permet la propagation de link-equity vers les alternatives sans indexer la soft-404 elle-même.
4. **Ranking multi-tier compat-aware** des alternatives :
   - Tier 1 : même `modele_id` (autres motorisations du même véhicule)
   - Tier 2 : même `modele_parent` (autres générations de la famille)
   - Tier 3 : même `marque_id` (autres modèles de la marque)
   - Filtre dur `EXISTS pieces_relation_type` pour les trois tiers (véhicules, gammes, modèles).
   - Cache Redis 5min keyed `alt:{type_id}:{pg_id}:v1` + etag `sha256` sur canonical JSON (replay-safe).
5. **Télémétrie append-only `__soft_404_events`** + vue 30j `v_soft_404_demand_30d`. Ownership `D3 / @ak125/seo-team`. Rétention 90j. UA classifié sans fingerprinting (`bot` / `browser` / `unknown`). Throttle Redis 60s par session.

## Conséquences

### Positives

- La page soft-404 devient un hub de rebond mesurable (3 blocs hiérarchisés + lead capture link `/contact?ref=soft-404&gamme=&type=`).
- Demand-list catalogue alimentée par `v_soft_404_demand_30d` (≥ 3 hits browsers / 30 jours).
- Link-equity préservée via `ItemList` Schema.org.
- Single-write-path : un seul service backend (`RmAlternativesService`), un seul endpoint, un seul payload v2.
- URL strictement préservée, `noindex, follow` invariant — pas de risque de désindexation involontaire.

### Coûts opérationnels

- Une surface op nouvelle (table + vue) provisionnée avec runbook + ownership + retention (cf. mémoire `feedback_new_token_type_equals_operational_debt`).
- Cache Redis 5min sur le payload — invalidation passive, pas de bus.

### Hors-scope V1 (gate-on-evidence)

- Tier 4 cross-brand (Audi A6, Mercedes Classe E mêmes specs).
- Drawer form Conform pour devis personnalisé.
- Dashboard Grafana de soft-404 (V2 si volume > 1k hits/j).
- Worker cron demand-list automatisé.
- A/B copy testing via GrowthBook.
- Embeddings sémantiques pour clustering inter-gammes.
- Colonne `pg_cluster TEXT` dans `pieces_gamme` (V1 = liste statique TS).

## Alternatives considérées

- **HTTP 404 / 410 strict** : refusée — perte de link-equity et UX dégradée (le triplet véhicule reste valide en catalogue).
- **Canonical pointant vers `/pieces/:gamme.html`** : refusée — signal contradictoire avec `noindex`, anti-pattern Google.
- **ML scoring sémantique des alternatives** : déferrée en V2 (gate-on-evidence : la liste statique des clusters et le ranking déterministe couvrent 95% du besoin V1).
- **Pages "soft-404 gamme seule"** (`/pieces/:gamme.html` vide) : hors-scope cette ADR ; pattern à dériver séparément si besoin.

## Implémentation de référence

- PR monorepo : [ak125/nestjs-remix-monorepo#595](https://github.com/ak125/nestjs-remix-monorepo/pull/595)
- Branche : `feat/soft-404-r2-strategy`
- Spec : `docs/superpowers/specs/2026-05-18-soft-404-r2-strategy-design.md`
- Plan : `docs/superpowers/plans/2026-05-18-soft-404-r2-strategy.md`
- Runbook télémétrie : `governance-vault/runbooks/soft-404-telemetry.md`

## Self-review verdict

APPROVE
