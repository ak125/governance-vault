---
id: ADR-105
title: "`__seo_event_log` : index GIN (payload) retiré ; tout lecteur jsonb apporte son index ciblé — amende ADR-025"
status: accepted
date: "2026-10-03"
decision_date: "2026-10-03"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-025"]
extends: []
related_adr: ["ADR-045", "ADR-055"]
related_rules: ["G1"]
related_incidents: []
version: "1.0.0"
---

# ADR-105 : `__seo_event_log` — index GIN (payload) retiré, index ciblé à la demande

- **Statut** : Accepted (2026-10-03). La fusion par l'owner vaut ratification.
- **Amende** [[ADR-025-seo-department-architecture|ADR-025]] sur un seul point : la ligne
  `CREATE INDEX ON __seo_event_log USING GIN (payload);` du § « Event log unifié ». Le reste
  d'ADR-025 reste en vigueur : la table, ses colonnes, son ENUM et l'index
  `(event_type, created_at)`.
- **Méthode** : constats mesurés le 2026-10-03 en lecture seule (rôle en
  `transaction_read_only`) sur l'instance PostgreSQL 17.6 démarrée le 2026-09-17 01:14Z
  (`stats_reset` nul), et relevé du code du monorepo à la même date.

## Contexte

ADR-025 prescrit deux index sur `__seo_event_log` : `(event_type, created_at)` et un GIN sur
`payload`. La migration monorepo `20260425_seo_event_log.sql` les a créés, avec un troisième,
`btree (entity_url) WHERE entity_url IS NOT NULL`, qu'ADR-025 ne mentionne pas.

Constats du 2026-10-03 :

1. **Taille.** La table compte 746 814 lignes pour 312 Mo de heap. Ses 6 index pèsent 247 Mo,
   dont 75 112 448 octets pour le GIN et 67 215 360 octets pour l'index `entity_url`.
2. **Lectures.** Depuis le 2026-09-17, chacun de ces deux index a été parcouru 2 fois, la
   dernière le 2026-09-26 12:24Z pour le GIN et le 2026-09-23 15:03Z pour `entity_url`.
   Aucun lecteur du monorepo n'explique ces parcours. Sur la même période,
   `idx_seo_event_log_type_created` compte 114 828 parcours.
3. **Opérateurs.** Un GIN `jsonb_ops` ne sert que `@>`, `?`, `?|`, `?&`, `@?` et `@@`. Les
   lectures du code passent par `->>`, que ce GIN ne sert pas. C'est le cas des requêtes
   d'[[ADR-045-seo-monitoring-cron-v0|ADR-045]] (`payload->>source`) et de la purge
   d'[[ADR-055-seo-shadow-mode-architecture|ADR-055]] (`payload->>'subtype' LIKE …`).
4. **Le seul `@>` n'emploie pas le GIN.** Parmi les fonctions SQL, seul le trigger
   `trg_auto_type_rebuild_cache` emploie `@>`, dans deux requêtes : l'UPDATE d'auto-résolution
   et le `NOT EXISTS` de dédoublonnage. Il s'exécute chaque fois qu'un type devient affichable.
   Le planificateur sert ces deux requêtes par `idx_seo_event_log_type_created` (condition
   d'index `event_type = 'anomaly_detected'`, 2 lignes estimées sur 746 814). Le `@>` n'y est
   qu'un filtre sur ces 2 lignes. Les EXPLAIN, sans ANALYZE, n'ont fait bouger aucun compteur.
5. **`entity_url`.** Aucun code et aucune fonction ne filtre sur
   `__seo_event_log.entity_url`. Son prédicat partiel couvre 743 228 lignes sur 746 814.
6. **Coût.** Les deux index sont maintenus à chaque insertion, environ 3 600 par jour, et le GIN
   l'est en plus par sa liste d'attente (`fastupdate`).

Le GIN prescrit coûte donc 75 Mo et une maintenance continue, sans aucun lecteur. Le retirer sans
amender ADR-025 contredirait un ADR accepté (G1).

## Décision

### D1 — Le GIN générique sur `payload` n'est plus prescrit

ADR-025 ne prescrit plus que l'index `(event_type, created_at)`. Après le retrait (D3), la table
garde 4 index :

| Index | Définition |
|---|---|
| `__seo_event_log_pkey` | unique, btree (`id`) |
| `idx_seo_event_log_type_created` | btree (`event_type`, `created_at` DESC) |
| `idx_seo_event_log_severity_unresolved` | btree (`severity`, `created_at` DESC) WHERE `resolved_at IS NULL` |
| `uq_seo_event_log_r2_order_placed_order_id` | unique, btree (`payload ->> 'order_id'`), partiel sur `event_type = 'r2_order_placed'` |

### D2 — Un lecteur jsonb ou `entity_url` apporte son propre index

Un futur lecteur qui filtre `payload` (par `@>`, `?` ou `->>`) ou `entity_url` doit d'abord
mesurer son plan. S'il a besoin d'un index, il l'ajoute dans sa propre PR. Cet index doit être
**ciblé** : partiel (par exemple sur `event_type`), ou d'expression (`(payload ->> 'clé')`).
L'EXPLAIN qui le choisit sert de justification. `uq_seo_event_log_r2_order_placed_order_id`
est un exemple de cette forme.

Un GIN générique sur tout `payload` ne revient que si un plan mesuré le choisit pour un lecteur
réel.

### D3 — Exécution

Le retrait se fait par la migration monorepo `20261003_drop_seo_event_log_unread_indexes`
(`DROP INDEX CONCURRENTLY`, hors transaction). Elle est gardée par ses propres pré-conditions,
qui la font s'arrêter avant tout DROP :

- **fenêtre** : les compteurs doivent couvrir au moins 30 jours, soit au plus tôt le 2026-10-17
  à 01:14Z ;
- **définition** : chaque index doit avoir exactement la définition relevée ;
- **compteurs** : `idx_scan` et `last_idx_scan` doivent être identiques aux valeurs relevées.
  Un seul parcours depuis le relevé arrête la migration, et la preuve est alors à refaire.

La migration est fusionnée après cet ADR.

Elle retire aussi `idx_seo_event_log_entity_url`. Cet index n'a jamais figuré dans ADR-025 ; cet
ADR le mentionne pour que la liste des index de la table soit décrite à un seul endroit (D1).

## Options considérées

| Option | Verdict | Raison |
|---|---|---|
| Retirer les deux index, index ciblé à la demande | **Retenue** | Libère 135,7 Mo et deux maintenances à chaque insertion, sans retirer aucune lecture mesurée. |
| Garder les deux index | Rejetée | 135,7 Mo et une maintenance continue pour 2 parcours chacun, inexpliqués, en 16 jours. |
| Retirer le GIN sans ADR | Rejetée | Contredit ADR-025, accepté (G1). |
| Remplacer le GIN par `jsonb_path_ops` | Rejetée | Plus petit, mais aucun lecteur ne le choisirait non plus : `type_created` sert déjà le seul `@>`. |
| Créer dès maintenant un index ciblé pour le trigger | Rejetée | Le plan actuel lit 2 lignes par `type_created`. Un index sans lecteur qui le choisit serait spéculatif. |

## Ce que cet ADR NE fait PAS

- Il ne modifie ni la table, ni ses colonnes, ni l'ENUM `seo_event_type`, ni les 4 index conservés.
- Il ne modifie pas la migration appliquée `20260924_vehicle_cache_trigger_rebuild_failure_observable.sql`.
  Son commentaire « COÛT », qui attribue au GIN les requêtes du trigger, est inexact ; la nouvelle
  migration le corrige.
- Il ne change ni la rétention ni la purge de la table, comme celle d'ADR-055.
- Il n'amende pas ADR-045, qui mentionnait le GIN pour décrire la table à sa date et ne le
  prescrivait pas.
- Il n'applique rien en base. L'application se fait par le workflow manuel du monorepo, lancé par
  l'owner.

## Conséquences

**Positives**

- La table perd 135,7 Mo (142 327 808 octets) d'index : 247 Mo → 111 Mo, et 6 → 4 index.
- Chaque insertion maintient deux index de moins, dont le GIN.
- ADR-025 décrit de nouveau les index réellement utiles.

**Négatives**

- Un futur filtre `@>` peu sélectif sur `event_type` pourrait passer en parcours de table.
  D2 couvre ce cas : le lecteur mesure son plan et apporte son index ciblé dans sa PR.
- Pour revenir en arrière, le `.down.sql` de la migration recrée les deux index à l'identique,
  avec `CONCURRENTLY`.

## Mise en œuvre

Dans cette PR :

- cet ADR ;
- `amended_by: ["ADR-037", "ADR-105"]` dans ADR-025 ;
- la régénération de `MOC-Decisions`.

Dans le monorepo :

- une PR porte la migration, son `.down.sql`, et la mise à jour de la fixture
  `scripts/db/test-vehicle-cache-trigger-observable.sh`, qui ne recrée plus le GIN.
- Cette PR n'est fusionnée qu'après cet ADR, et au plus tôt le 2026-10-17.
- L'owner l'applique ensuite avec `only_ids = 20261003_drop_seo_event_log_unread_indexes`.

## Références

- [[ADR-025-seo-department-architecture|ADR-025]] : architecture amendée (§ « Event log unifié »)
- [[ADR-045-seo-monitoring-cron-v0|ADR-045]] : lecteurs `payload->>source`
- [[ADR-055-seo-shadow-mode-architecture|ADR-055]] : persistance shadow et purge `payload->>'subtype'`
