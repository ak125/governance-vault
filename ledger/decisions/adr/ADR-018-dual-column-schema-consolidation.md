---
id: ADR-018
title: "Consolider le schéma dual TEXT/INTEGER sur tables `auto_*` et `pieces_*`"
status: deferred
date: 2026-04-21
decision_makers:
  - "@automecanik.seo"
supersedes: []
superseded_by: []
related_rules:
  - db-governance-policy
related_incidents:
  - INC-2026-005-gsc-5xx-vehicle-page-cold-rpc
related_adrs:
  - ADR-016-vehicle-page-matview-persistence
  - ADR-017-rpc-pieces-cast-cleanup
reviewed_by: "Claude Opus 4.7"
tags:
  - adr/deferred
  - domain/db-governance
  - domain/catalog
  - tech/postgres
  - tech/supabase
  - technical-debt
---

# ADR-018 : Consolider le schéma dual TEXT/INTEGER sur tables `auto_*` et `pieces_*`

> [!note] Statut : DEFERRED
> Cet ADR décrit la cause racine des incidents INC-2026-005 et des 9 RPC coûteuses corrigées par ADR-017. Il ne sera activé (`status: proposed` → `accepted`) qu'**après validation 48 h** de l'ADR-017, qui prouve qu'aucune RPC ne dépend plus des colonnes TEXT. Le travail est estimé à **2-4 semaines** et doit être planifié en sprint dédié.

## Contexte

Les tables `auto_type`, `auto_modele`, `auto_marque`, `pieces`, `pieces_gamme`, `pieces_relation_type` stockent **chaque identifiant en deux copies** :

| Colonne TEXT | Colonne INTEGER | Origine |
|---|---|---|
| `auto_type.type_id` | `auto_type.type_id_i` | Ingestion TecDoc initiale (ID en string dans la source), colonne `_i` ajoutée ultérieurement pour indexation |
| `auto_type.type_modele_id` | `auto_type.type_modele_id_i` | idem |
| `auto_type.type_marque_id` | `auto_type.type_marque_id_i` | idem |
| `pieces_gamme.pg_id` | `pieces_gamme.pg_id_i` | idem |
| `pieces.piece_pg_id` | `pieces.piece_pg_id_i` | idem |
| `pieces_relation_type.rtp_type_id` | — (déjà INTEGER natif) | Table régénérée plus récemment |

### Conséquences observées

1. **Casts dans chaque JOIN** : `auto_type.type_id TEXT` ↔ `pieces_relation_type.rtp_type_id INTEGER` force `rtp_type_id::text` ou `type_id::integer`, **bloquant les index** (root cause des RPC coûteuses d'ADR-017).
2. **Pattern `NULLIF(col, '')::INTEGER`** dans 8+ RPC : nécessaire parce que la colonne TEXT tolère des chaînes vides `''` issues de l'ingestion TecDoc.
3. **Divergence possible** : `type_id_i` peut devenir NULL ou différer de `type_id` si un backfill échoue. Aucun contrainte DB ne garantit `type_id_i = type_id::integer`.
4. **Confusion développeurs** : quelle colonne utiliser ? La memory `feedback_internal_ids.md` documente déjà un incident causé par l'usage accidentel de colonnes TecDoc brutes.
5. **Coût disque** : duplication pour ~368 M lignes sur `pieces_relation_type` et 54 k lignes sur `auto_type` + équivalents autres tables. Ordre de grandeur : ~5-10 GB de doublons.

## Décision (proposée, à ratifier après ADR-017)

**Éliminer les colonnes TEXT redondantes et conserver uniquement la forme INTEGER native, en renommant `*_i` → `*` à terme.**

Migration en 4 phases étalée sur 3-4 semaines, avec fenêtres de maintenance minimales grâce à `CREATE OR REPLACE` et renames atomiques.

## Options Considérées

### Option A : Garder TEXT, supprimer `_i` (rejetée)

Inverse du sens de consolidation.

**Rejetée** car :
- Le JSON Supabase (PostgREST) sérialise mieux les INTEGER que les TEXT numériques.
- Indexation INTEGER plus efficace que TEXT pour jointures.
- Le TecDoc source a évolué : les nouvelles tables (`pieces_relation_type`, `pieces_media_img`, etc.) sont déjà INTEGER natif.

### Option B : Garder INTEGER `_i`, supprimer TEXT (RETENUE)

Standardiser sur INTEGER partout, renommer `_i` → forme courte.

**Avantages**
- Aligne toutes les tables sur le format INTEGER natif.
- Supprime les casts → supprime les RPC bricolages.
- Supprime la dette PK composite sur TEXT (`auto_type_pkey` actuel sur `type_id TEXT`).
- Économise ~5-10 GB disque.

**Inconvénients**
- Migration longue (~2-4 semaines de sprint dédié).
- Touche toutes les RPC + backend NestJS (centaines de queries).
- Nécessite un freeze d'ingestion TecDoc pendant la fenêtre critique.

### Option C : Vues de compatibilité

Garder les colonnes TEXT et INTEGER, créer des vues qui exposent uniquement la forme INTEGER.

**Avantages**
- Sans changement physique.

**Inconvénients**
- Ne résout ni les casts dans les RPC SQL ni l'occupation disque.
- Ajoute une couche de vues à maintenir.
- Bricolage déguisé.

### Option D : Statut quo

**Rejetée** — ADR-017 documente que ce pattern cause 82% du CPU DB. Laisser pourrir = INC-2026-005 bis dans 6-12 mois.

## Justification (provisoire)

Option B est la seule **non-bricolage**. Les options A et C font de la cosmétique, D refuse de traiter.

Le coût (2-4 semaines) est amorti sur :
- Fin définitive des RPC coûteuses (pas juste les 9 d'ADR-017).
- Fin de la classe de bug "cast bloquant index".
- Simplification documentaire (une seule colonne par ID).
- Prérequis pour partitionnement `pieces_relation_type` par tranche de `rtp_pg_id` (si jamais nécessaire plus tard).

## Conséquences

### Positives

- **Schéma physique simple** : une colonne par identifiant, type natif.
- **RPC SQL simple** : aucun cast, aucun `NULLIF(...)::INTEGER`.
- **CI gate** : on peut ajouter une règle lint SQL refusant `text::integer` et `::text` sur ces tables.
- **Aligne la memory** : `feedback_internal_ids.md` et `db-pieces-indexes.md` ne décrivent plus une exception mais la règle.

### Négatives

- **Migration risquée** : touche la PK de tables larges (`auto_type`, `auto_marque`, etc.).
- **Backend NestJS** : régénération types + audit des `.from('auto_type').select('type_id')` pour re-sélectionner `type_id` INTEGER (ex-`type_id_i`).
- **RAG ingestion** : les markdown stockent parfois `type_id` comme string ; revoir les frontmatters.
- **Fenêtre de maintenance** : renames `ALTER TABLE ... RENAME COLUMN` sont rapides mais verrouillent la table.

### Neutres

- API publique (HTTP) inchangée si les noms de champs sont préservés (via alias SQL au besoin).

## Critères de Succès

- [ ] 0 colonne `*_i` résiduelle dans `information_schema.columns` pour tables `auto_*` et `pieces_*`
- [ ] 0 cast `::text` / `::integer` / `NULLIF(...)::INTEGER` dans `pg_proc WHERE nspname='public'`
- [ ] CI gate actif qui refuse ces patterns dans les migrations futures
- [ ] `backend/src/database/types/database.types.ts` régénéré, types NestJS tous INTEGER
- [ ] RAG frontmatters audités et migrés (script à écrire)
- [ ] 0 incident de régression sur 14 jours post-bascule

## Implémentation (high-level, à détailler quand activé)

### Phase 1 — Audit & inventaire (~3 jours)

1. Script Python qui liste toutes les queries SQL (migrations + RPC) référençant la colonne TEXT.
2. Grep backend NestJS pour `type_id`, `modele_id`, `marque_id`, `pg_id`, `piece_pg_id` dans les services.
3. Grep frontend Remix pour les endpoints qui consomment ces champs.
4. Checklist validée : chaque usage sait comment il migre.

### Phase 2 — Harmonisation des RPC (~1 semaine)

1. Réécrire toutes les RPC avec colonnes INTEGER (partiellement déjà fait via ADR-017 pour les 9 auditées).
2. Ajouter trigger de garantie `type_id_i = type_id::integer` le temps de la transition.
3. Déployer, observer 48 h.

### Phase 3 — Renommages (~3-5 jours, fenêtre maintenance)

1. `ALTER TABLE auto_type DROP CONSTRAINT auto_type_pkey`
2. `ALTER TABLE auto_type DROP COLUMN type_id`
3. `ALTER TABLE auto_type RENAME COLUMN type_id_i TO type_id`
4. `ALTER TABLE auto_type ADD PRIMARY KEY (type_id)`
5. Répéter pour `type_modele_id`, `type_marque_id`, `auto_modele.*`, `auto_marque.*`, `pieces_gamme.pg_id`, `pieces.piece_pg_id`.
6. Régénérer `database.types.ts`.

### Phase 4 — CI gate & nettoyage (~2-3 jours)

1. Ajouter gate `tools/validator-gates/gate-no-text-cast-on-pieces.sh`.
2. Script RAG qui re-normalise les frontmatters avec des ID INTEGER.
3. Doc de gouvernance DB mise à jour.
4. Fermer ADR-018 (`status: accepted` → `implemented`).

## Revue Planifiée

**Date** : 2026-06-21 (après stabilisation ADR-017 J+30 + avant tout autre travail DB structurant)
**Critères de revue** :
- Si ADR-017 n'a pas réduit CPU >= 60% → ADR-018 urgent (racine toujours présente).
- Si un autre incident SEV2+ liée aux casts apparaît entre-temps → escalader à SEV1, démarrer ADR-018 immédiatement.
- Si l'ingestion TecDoc change de format (JSON API au lieu de CSV texte) → re-évaluer si le schéma dual peut disparaître "gratuitement" via le nouveau pipeline.

## Liens

- Related : [[ADR-017-rpc-pieces-cast-cleanup]] (prérequis)
- Related : [[2026-04-20-gsc-5xx-vehicle-page-cold-rpc]]
- Related memory : `db-pieces-indexes.md`, `feedback_internal_ids.md`
- Related rules : [[rules-technical]]

---

*Proposé le : 2026-04-21*
*Activation prévue : après validation J+30 d'ADR-017*
*Statut actuel : deferred*
