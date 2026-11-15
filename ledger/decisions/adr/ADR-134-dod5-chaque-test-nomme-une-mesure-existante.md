---
id: ADR-134
title: "DoD5 : chaque test nomme une mesure qui existe (registry-fresh, registre des migrations) et clause transitoire tant que la comparaison au schéma live n'est pas mesurée — amende rules-engineering-definition-of-done (v1.4.0)"
status: proposed
date: "2026-11-15"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["rules-engineering-definition-of-done"]
extends: []
related_adr: ["ADR-058", "ADR-101", "ADR-120", "ADR-121", "ADR-123"]
related_rules: ["DoD5", "G1", "G6"]
related_incidents: []
reviewed_by: ""
version: "1.0.0"
---

# ADR-134 : DoD5, chaque test nomme une mesure qui existe

- **Statut** : Proposed. Rédigé par un agent (Claude Code CLI, machine DEV) le 2026-11-15 sur le
  mandat 02-A de l'owner, porté par le département 02 et transmis sous la lettre Y. Rien n'est
  normatif avant la ratification par l'owner (décideur humain : Marwane) puis la fusion de la tête
  qui la porte ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4 et D7). La PR
  qui porte cet ADR reste en brouillon jusqu'à la ratification.
- **Modifie**, sur les seuls passages listés en §Amendement, la section DoD5 de
  [[rules-engineering-definition-of-done]] (1.3.0 → 1.4.0) : tests 1 et 4, dernière ligne de la
  preuve requise, clause transitoire. L'énoncé OBLIGATOIRE de DoD5, ses tests 2 et 3, ses
  anti-patterns, sa raison, la ligne DoD5 du gabarit d'auto-évaluation et les sections DoD1 à DoD4
  et DoD6 à DoD9 restent inchangés.
- **Ne modifie aucun ADR**, ni aucun fichier du monorepo (§Ce que cet ADR ne fait pas).
- **Méthode** : constats vérifiés le 2026-11-15, en lecture seule, sur `main` du vault au commit
  `156b143150e7f63dd1df8a54a4bd255569ceb4b8` et sur `main` du monorepo au commit
  `c70c4025fa08e40193a9912182c9e0f2896db2d8`, par lecture des fichiers, des journaux de runs GitHub
  Actions et de requêtes SQL `SELECT` sur la base Supabase. Le détail des commandes et de leurs
  sorties est dans le rapport du mandat, non publié parce qu'il cite des chemins du serveur.

## Contexte

DoD5 exige « aucune migration en attente, aucun drift entre schema canon (`audit/registry/db.json`)
et état Supabase live, aucun contrat de type cassé ». Deux de ses quatre tests citent une mesure qui
ne mesure pas ce qu'ils disent. Le département 02 a relevé cinq constats ; chacun a été revérifié.

| # | Constat du département 02 | Vérification | Verdict |
|---|---|---|---|
| C1 | `mcp__supabase__list_migrations` (test 4) lit `supabase_migrations.schema_migrations`, pas le registre du moteur de migrations | `list_migrations` et `SELECT count(*), max(version) FROM supabase_migrations.schema_migrations` : 474 lignes, dernière version `20261004131024`. Le skill `db-migration` du monorepo le dit aussi : « Lit `supabase_migrations.schema_migrations`, pas le ledger du moteur ». | Confirmé |
| C2 | Le registre du moteur est `infra.schema_migrations`, alimenté par `scripts/ci/apply-supabase-migration.py` | `SELECT` sur `infra.schema_migrations` : 353 lignes, toutes `applied`, dont 270 inscrites par une base de référence (`baseline-2026-05-16` : 221 ; `baseline-33810961050` : 49) ; dernière : `20261105_gamme_page_cached_volatile`. Dans git : 440 fichiers `.sql` sous `backend/supabase/migrations/`, dont 87 `.down.sql` que le moteur ignore, soit 353 migrations montantes | Confirmé |
| C3 | `apply-supabase-migration.py --status` mesure l'écart entre git et ce registre | Workflow `migration-ledger-freshness.yml` (cron quotidien 04:30 UTC, lecture seule) : run 43557419275 du 2026-11-14 sur `main` `245f7cb8027084973c72ffc2ff64fcfdf8e45915` et run 43677471198 du 2026-11-15 sur `main` `960370c627a38c7d845fc8f021666b78bda87a05` impriment tous deux « Summary : 353 applied, 0 pending, 0 drift, 0 orphan, 0 applying, 0 failed » | Confirmé, deux nuances (ci-dessous) |
| C4 | `registry-fresh.yml` ne lit pas la base live | Le workflow ne reçoit aucun secret de base ; `scripts/registry/build-db-registry.js` se décrit comme un scan hors ligne des fichiers SQL. Il compare les projections committées du registre (dont `audit/registry/db.json`) à leur reconstruction depuis le dépôt | Confirmé, une nuance (ci-dessous) |
| C5 | La comparaison `db.json` ↔ base live n'existe pas ; le contrôle le plus proche est `check-ledger-catalog-ratchet.py --verify` | `--verify` (même workflow, run 43557419275) : « 353 migrations applied · 99 absences · baseline 99 » puis « ledger et catalogue concordent (au baseline près) ». Il vérifie, par nom et dans n'importe quel schéma, que les objets déclarés par les migrations appliquées existent ; il tolère les 99 absences de sa base de référence et ne lit ni `db.json`, ni les colonnes, ni les objets créés hors migration | Corrigé : le contrôle existe, mais il ne mesure qu'un sens et ne compare pas `db.json` |

Nuances relevées en vérifiant :

- **N1, sur C3.** Le code de sortie de `--status` ne vaut 1 que sur `drift`, `applying` ou `failed`.
  Une migration `pending` n'échoue que si elle a plus de 30 jours (`--max-pending-age-days 30`), et un
  `orphan` n'est qu'un avertissement. Un run vert ne prouve donc pas « 0 pending, 0 orphan » : les
  compteurs se lisent sur la ligne `Summary`.
- **N2, sur C3.** Le run mesure `main` une fois par jour, pas l'arbre de la PR. La migration qu'une PR
  ajoute n'y figure pas avant la fusion ; elle relève du test 2 (migrations atomiques).
- **N3, sur C4.** Le job « Registry freshness (warn-only, Phase 1) » porte `continue-on-error: true`.
  Le run du workflow conclut alors `success` même quand le job échoue. Sur les 40 runs du 2026-11-14
  10:44 UTC au 2026-11-15 13:09 UTC, les 40 runs concluent `success` et 9 jobs concluent `failure` ;
  exemple : run 43717493054 (PR #2078 du monorepo), check run 132822068707 en `failure`, étapes
  « Deep-inventory freshness » et « Freshness diff » en échec. « Vert » doit donc désigner la
  conclusion du job, pas celle du run.

## Principe directeur

Un test de la DoD nomme une mesure qui existe et dit ce qu'elle compare. Ce qui n'est pas mesuré est
écrit comme tel dans la preuve, sans être retiré de l'exigence.

## Décisions

### D1 — Test 1 : registry-fresh nommé par ce qu'il compare

Le test 1 garde « `registry-fresh.yml` vert sur la PR ». Sa parenthèse, qui annonçait une cohérence
avec la base live, est remplacée par ce que le workflow compare réellement : projections committées du
registre reconstruites depuis le dépôt, overlay L2 validé, invariants I1 à I6 ; il ne lit pas la base
live. « Vert » désigne la conclusion du job « Registry freshness (warn-only, Phase 1) » (N3). Quand
son filtre `paths` ne déclenche pas le workflow, le test est non applicable et la preuve le dit.

### D2 — Test 4 : le registre du moteur de migrations remplace list_migrations

Le test 4 devient : « Registre des migrations conforme à git :
`scripts/ci/apply-supabase-migration.py --status` donne 0 pending, 0 drift, 0 orphan, 0 applying,
0 failed ; citer le run. » Les compteurs se lisent sur la ligne `Summary` (N1). Le run cité est celui
de `migration-ledger-freshness.yml`, programmé ou lancé à la main, qui mesure `main` (N2).

### D3 — Dernière ligne de la preuve requise

La ligne `mcp__supabase__list_migrations matches git: yes` est remplacée par
`Migration ledger --status : <run>, 0 pending, 0 drift, 0 orphan`.

### D4 — Clause transitoire

Tant que la mesure du schéma contre la base live n'existe pas, la preuve cite le résultat de
`check-ledger-catalog-ratchet.py --verify` et porte la mention « comparaison db.json / base live :
non mesurée » ; la case DoD5 se coche sur les tests 1 à 4. La clause dit ce que `--verify` mesure
(C5), pour qu'il ne soit pas lu comme la comparaison manquante.

### D5 — L'énoncé reste

L'énoncé « aucun drift entre schema canon (`audit/registry/db.json`) et état Supabase live » reste
dans la règle. La clause transitoire constate qu'il n'est pas mesuré ; elle ne le retire pas. Décider
de construire cette mesure revient à l'owner.

### Écarts par rapport au texte proposé par le département 02

Le texte du département est repris mot pour mot pour le test 4, la ligne de preuve, la clause
transitoire et l'énoncé. Quatre ajouts, chacun pour que le test nomme une mesure qui existe :

1. Test 1 : « vert » rattaché à la conclusion du job (N3), et cas du workflow non déclenché.
2. Test 4 : lecture des compteurs sur la ligne `Summary` (N1) et run qui mesure `main` (N2).
3. Clause transitoire : une phrase dit ce que `--verify` vérifie et ne vérifie pas (C5).
4. Note d'amendement sous le titre de DoD5, version 1.4.0 et pied de page, comme pour ADR-120,
   ADR-121 et ADR-123.

## Amendement

Les textes suivants figurent dans la même PR. Ils deviennent canon applicable lorsque l'owner
fusionne la tête qui porte la ratification (ADR-121 D7) ; avant cette fusion, ils ne modifient pas le
canon de `main`.

- **[[rules-engineering-definition-of-done]] 1.4.0** : section DoD5, tests 1 et 4 (D1, D2), dernière
  ligne de la preuve requise (D3), clause transitoire (D4), note d'amendement sous le titre ; ligne
  Version de l'en-tête, `updated` et `related_adrs` du frontmatter, pied de page « Dernière revue ».

## Ce que cet ADR ne fait pas

- Il ne construit pas la mesure du schéma contre la base live et ne décide pas de la construire.
- Il ne modifie ni `.github/PULL_REQUEST_TEMPLATE.md`, ni `scripts/ci/pr-dod-gate.mjs`, ni aucun
  workflow du monorepo. La gate ne lit que la présence et l'état des lignes DoD1 à DoD9 ; la ligne
  DoD5 du gabarit (« registry-fresh green, migrations atomic ») reste exacte après l'amendement.
- Il ne change pas `continue-on-error` sur `registry-fresh.yml` (N3) : le test 1 lit la conclusion du
  job, quel que soit ce réglage.
- Il ne touche à aucun autre item de la DoD.

## Options considérées

- **Retenue : nommer les mesures existantes et garder l'énoncé**, avec une clause transitoire qui dit
  ce qui n'est pas mesuré.
- **Retirer de l'énoncé la comparaison avec la base live** : écartée, l'exigence garde sa raison
  (ADR-058 V4, `live = canonical = git`) ; seule sa mesure manque.
- **Garder `list_migrations`** : écartée, il lit une table que le moteur n'alimente pas (C1, C2).

## Conséquences

- Positives : chaque preuve DoD5 cite un run et des compteurs vérifiables ; un job registry-fresh en
  échec ne passe plus pour vert.
- Négatives : la preuve DoD5 s'allonge de deux lignes tant que la clause transitoire s'applique ; le
  test 4 dépend d'un run quotidien sur `main`, pas d'une mesure sur la PR.
- Neutre : la gate `pr-dod-gate` n'a rien à changer.

## Retour arrière

Revenir à la version 1.3.0 de la section DoD5 par un ADR d'amendement. Aucun code ni aucune donnée
n'est à défaire.

## Revue planifiée

À la décision de l'owner sur la mesure du schéma contre la base live : si elle est construite, un ADR
d'amendement retire la clause transitoire et nomme la mesure dans les tests.

## Références

- [[rules-engineering-definition-of-done]] (DoD5)
- [[ADR-058-repository-control-plane]] (V4 : `live = canonical = git`)
- [[ADR-101-vault-decides-canon-authority|ADR-101]], [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] (D7)
- [[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]], [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte|ADR-123]] (précédents d'amendement de la DoD)
- [[rules-governance-process]] (G6, preuves)
- Monorepo, `main` `c70c4025f` : `.github/workflows/registry-fresh.yml`,
  `.github/workflows/migration-ledger-freshness.yml`, `scripts/ci/apply-supabase-migration.py`,
  `scripts/audit/check-ledger-catalog-ratchet.py`, `scripts/registry/build-db-registry.js`,
  `.claude/skills/db-migration/SKILL.md`
- [[MOC-Decisions]]

---

*Proposé le : 2026-11-15*
*Accepté le : —*
*Dernière revue : 2026-11-15*
