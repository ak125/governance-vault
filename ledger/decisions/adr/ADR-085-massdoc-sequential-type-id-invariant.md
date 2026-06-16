---
id: ADR-085
title: "Numérotation interne véhicule : séquence globale Massdoc + allocateur gouverné (auto_type.type_id)"
status: proposed
date: "2026-06-15"
decision_date: "2026-06-15"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: []
related_adr: []
related_rules: []
related_incidents: []
---

# ADR-085 : Numérotation interne véhicule — séquence globale Massdoc + allocateur gouverné

## § Contexte (faits vérifiés 2026-06-15)

`auto_type.type_id` **est** une séquence globale Massdoc, autorité de numérotation interne du référentiel véhicule
(TecDoc-dérivé, 53 959 types). État vérifié en DB :

- Legacy `0–59999` (30 502 types) : `type_id == KTYPNR` historiquement (KTYPNR adopté pour les véhicules anciens).
- Ajoutés `60000–83456` (23 457 types) : alloués par Massdoc, contigus, 0 trou (bijectif).
- Pont source ↔ interne : `tecdoc_map.type_id_remap` (`old_id` = KTYPNR source `100001–801701` → `new_id` = id interne).
  23 457 lignes, bijectif, `new_id ⊆ auto_type`, 0 orphelin.
- **KTYPNR = clé SOURCE uniquement** ; conservée pour 301 / traçabilité (RPC `resolve_type_id_remap`).
- High-water Massdoc = **83456** → prochain = **83457**. Aucune séquence Postgres n'existait : l'allocation se faisait
  **ad hoc** dans `scripts/fix-vehicles-massdoc.py` — un bricolage à éroger en règle gouvernée.
- Les URLs véhicule sont keyées `type_id` → toute renumérotation casserait les URLs (interdit).

État de la consolidation (evidence) : le travail de **données** est abouti — véhicules récents des constructeurs
au catalogue déjà ajoutés (orphelins ≥2021 ≈ 0, dump à jour jusqu'à 2025-12) ; codes moteur seedés à 100 %
(`auto_type_motor_code` = 63 091 = total des paires disponibles ; 50 741/53 959 véhicules couverts) ; 3 218
véhicules sans code = sans code dans la source TecDoc (non seedables, ~6 % attendus). Cet ADR **ne porte pas un
backlog de données** : il fige la **gouvernance** de numérotation pour les futures vraies vagues (export TecDoc
plus frais, nouveau modèle d'une marque à demande).

## § Décision (invariants non négociables)

### 1. Séquence Massdoc monotone
`auto_type.type_id` = séquence globale Massdoc. Tout nouvel id = `nextval` ≥ `max(type_id)+1` (83457 à la création),
**jamais réutilisé**. Micro-trous possibles sur rollback de transaction = acceptables (monotone, pas strictement contigu).

### 2. KTYPNR = clé source, jamais un id
Jamais adopter le KTYPNR (ni aucun id source) comme `type_id`. Le KTYPNR est enregistré dans `tecdoc_map.type_id_remap.old_id`.

### 3. Aucune réutilisation des trous legacy
Jamais réutiliser un trou legacy `0–59999` (ambiguïté / bricolage interdit).

### 4. Aucune renumérotation
Jamais renuméroter l'existant (no URL changes ever ; URLs véhicule keyées `type_id`).

### 5. Traçabilité source obligatoire
Chaque allocation enregistre la source (`old_id` → `new_id`) → garantit 301 + traçabilité.

## § Mécanisme (appliqué + vérifié LIVE 2026-06-15)

Migration `backend/supabase/migrations/20260615_massdoc_type_id_allocator.sql` (monorepo PR #998, mergée
`2c566c31f`) : séquence `tecdoc_map.type_id_seq` (MINVALUE 83457, alignée au high-water live à l'apply) +
fonction idempotente `tecdoc_map.allocate_massdoc_type_id(integer)` (1 source → 1 id Massdoc, réutilise si déjà
mappé). `SECURITY DEFINER` + `REVOKE EXECUTE FROM PUBLIC` (mint d'ids = rôle gouverné uniquement).

Propriétés : **ADDITIVE · IDEMPOTENT · RÉVERSIBLE** ; touche seulement le schéma `tecdoc_map` (0 ligne `auto_type`) ;
objets **inertes** tant que le flux d'ajout unifié ne les appelle pas. Étend le pont `tecdoc_map` existant
(zéro système parallèle). Remplace le script ad hoc `fix-vehicles-massdoc.py`.

**Vérification LIVE** (`apply_migration`, squawk clean) :

- `type_id_seq` : `last_value` 83457, `is_called=false` → prochain `nextval` = **83457**.
- `EXECUTE` révoqué de PUBLIC.
- `allocate_massdoc_type_id(135713)` → **61280** (id existant, idempotent, **sans insert**).
- `type_id_remap` inchangé (23 457), séquence non consommée par le test.

**Correctif de revue (bug attrapé à l'apply)** : la 1re version faisait `setval(GREATEST(83456, max), is_called=true)`
→ ERROR 22003 (83456 < MINVALUE 83457 quand `max=83456`). Corrigé en
`setval(GREATEST(83457, max+1), is_called=false)` : le prochain `nextval` renvoie exactement la valeur, ≥ MINVALUE.

Flux unifié recommandé (vagues futures) : `allocate → INSERT auto_type → INSERT auto_type_motor_code` dans **une
seule transaction par véhicule** (échec véhicule ⇒ rollback de la ligne remap). Protection SEO des nouveaux ids :
`noindex` + 301 des URLs source (déjà géré). **Par vagues owner-gated**, jamais d'injection globale.

## § Conséquences

### Positives
- Remplace un script ad hoc par une fonction DB gouvernée (no-bricolage) ; idempotent + réversible ; préserve les URLs ;
  traçabilité source garantie ; extension du pont existant (zéro système parallèle).

### Négatives / coût
- Micro-trous de séquence sur rollback (acceptés). Chaque vague reste une action owner-gated (latence voulue).
  Méthode id véhicule et méthode tarif restent **séparées** (pas de fusion de clés).

### Risques + mitigations
- Sans cet ADR : allocation à la main → collision / KTYPNR adopté par erreur / renumérotation accidentelle (casse URLs).
  Mitigation = cet ADR + l'allocateur gouverné (déjà live, réversible).

## § Séquence (post-signature)
1. Renfort roadmap `tecdoc-integration-roadmap-v3.md` invariant #9 (pointer vers ADR-085 + l'allocateur) — diff owner-only.
2. (Quand une vraie vague arrive — export TecDoc plus frais) implémenter le flux unifié `add_vehicle_with_motor_codes`
   appelant l'allocateur, owner-gated, par vagues.

## § Références
- Migration appliquée (monorepo) : `backend/supabase/migrations/20260615_massdoc_type_id_allocator.sql` (PR #998, `2c566c31f`).
- Design consolidé (monorepo) : `audit/id-internal-massdoc-sequential-consolidation-2026-06-15.md`.
- Evidence d'état + demande FR (monorepo) : `audit/p2-pilot-french-demand-verification-2026-06-15.md`.
- Renfort (monorepo, owner-only) : `.spec/00-canon/tecdoc-integration-roadmap-v3.md` invariant #9.
- Mémoire agent liée (monorepo, hors wikilink vault) : `project_massdoc_consolidation_state_20260615`.
