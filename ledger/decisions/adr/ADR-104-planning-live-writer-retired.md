---
id: ADR-104
title: "Planning Live : writer automatique, projection GitHub Project et alertes P0 retirés ; MOC figé, taxonomies conservées — amende ADR-053"
status: accepted
date: "2026-10-01"
decision_date: "2026-10-01"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-053"]
extends: []
related_adr: ["ADR-020", "ADR-102"]
related_rules: ["G4", "G8"]
related_incidents: []
version: "1.0.0"
---

# ADR-104 : Planning Live — writer automatique retiré, MOC figé

- **Statut** : Accepted (2026-10-01). La fusion par l'owner vaut ratification.
- **Amende** [[ADR-053-planning-live-system|ADR-053]] sur les passages listés en D3. Le reste
  d'ADR-053 reste en vigueur, en particulier l'invariant I4 (taxonomies versionnées).
- **Méthode** : chaque constat ci-dessous a été vérifié le 2026-10-01 sur `main` du vault, sur
  GitHub et sur la machine DEV (fichier cron, journal du writer, jeton `gh`).

## Contexte

ADR-053 a mis en place un système « Planning Live » :

- un cron quotidien sur la machine DEV (`/etc/cron.d/planning-live`) ;
- ce cron lance `_scripts/planning/run-cron.sh`, qui exécute `sync_planning.py` ;
- le résultat écrit `ops/moc/MOC-Planning-Live.md` et un snapshot `ledger/snapshots/planning/`, puis
  les pousse directement sur `main` ;
- le système alimente aussi un GitHub Project et des issues d'alerte `planning-p0-stagnant`.

Constats :

1. **Rien publié sur `main` depuis le 2026-08-14.** Le dernier commit du writer est `4c94c7d`. De
   2026-05-08 à 2026-08-14, le writer a poussé 63 commits directement sur `main`. Son journal compte
   61 lignes `Bypassed rule violations`, ce qui veut dire que la protection de branche a été
   contournée.
2. **Exécutions fausses du 2026-08-15 au 2026-09-14.** Les 31 exécutions ont commité sur la branche
   extraite dans le checkout partagé, pas sur `main`. Le push répondait `Everything up-to-date` et le
   journal écrivait `OK`. Chaque exécution commençait par un `git reset --hard origin/main` sur cette
   branche.
3. **Aucune exécution depuis le 2026-09-14.** Le répertoire du verrou `/var/lock/automecanik` est sur
   tmpfs et n'existe plus depuis le redémarrage du 2026-09-17. Le script sort donc avant d'écrire son
   journal. Le cron n'a pas de `MAILTO` et la machine n'a pas de MTA actif : le silence n'a été
   signalé à personne. Cet arrêt est **accidentel** : si le répertoire est recréé, le cron reprend
   ses `git reset --hard` sur le checkout partagé.
4. **La projection GitHub Project n'a jamais fonctionné.** Le journal compte 4 722 lignes
   `GH Project upsert failed` et aucun succès. Le jeton `gh` de la machine DEV n'a pas le scope
   `project`.
5. **Les alertes P0 sont périmées.** Les 4 issues `planning-p0-stagnant` encore ouvertes (#278, #314,
   #321, #341) portent sur des PR du monorepo toutes fermées ou fusionnées (#494, #924, #992, #1305).
6. **Le MOC n'est plus à jour.** `MOC-Planning-Live` est daté du 2026-08-14. Sur les 52 PR qu'il liste,
   9 ne sont plus ouvertes (7 fermées, 2 fusionnées).
7. **Le mécanisme est incompatible avec la gouvernance actuelle.**
   - `main` exige une PR et `enforce_admins` est actif : le push direct est refusé.
   - Depuis la règle G4 v3.1.0 ([[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]]),
     un agent prépare une PR et un humain la fusionne. Un writer quotidien par PR imposerait donc
     une fusion owner chaque jour.
8. **Personne n'a remarqué l'arrêt pendant 7 semaines** (du 2026-08-14 au 2026-10-01). Le MOC
   n'était pas lu comme source de priorités.

## Décision

### D1 — Writer automatique retiré

- Le writer est neutralisé sur la machine DEV, sans dépendre de l'arrêt accidentel du constat 3 :
  son environnement Python (`/opt/automecanik/.venvs/planning-live`) et son fichier
  d'environnement sont archivés hors du vault. `run-cron.sh` vérifie la présence de ce venv avant
  de prendre le verrou et avant toute commande git ; sans lui, il sort en erreur.
- Le fichier `/etc/cron.d/planning-live` appartient à root. Sa suppression est une action owner
  qui reste à faire. Tant qu'il est installé, il lance chaque jour `run-cron.sh`, qui s'arrête
  sur le venv absent.
- Supprimer `_scripts/planning/` de `main` ne suffit pas à arrêter le cron : il exécute le
  checkout partagé du vault, dont la branche extraite n'est pas forcément `main`.
- Le dossier `_scripts/planning/` est supprimé : `run-cron.sh`, `sync_planning.py`, les writers, les
  alertes, la projection GitHub Project, `setup-github-project.sh` et leurs tests. Ce code n'a plus
  de chemin d'exécution légitime (constat 7). L'historique git le conserve.
- Plus aucun processus n'écrit automatiquement dans le vault.

### D2 — Projections retirées

- Le GitHub Project n'est plus alimenté.
- Les alertes `planning-p0-stagnant` ne sont plus émises. Les 4 issues ouvertes sont fermées après
  la fusion, avec un renvoi à cet ADR.

### D3 — Ce qui change dans ADR-053

- **I1** (« MOC + git + snapshots = SoT canonique ») : le MOC et les snapshots deviennent un
  **instantané historique figé au 2026-08-14**. Ce ne sont plus une source de vérité du planning
  courant.
- **I2** (« `sync_planning.py` = unique writer auto ») : il n'y a plus de writer. Le MOC n'est plus
  modifié, sauf par un ADR (ici : le bandeau d'état figé).
- **I3** et **I5**, ainsi que le §6 (mécanisme d'alerte) : sans objet.
- Le champ `planning_live_state` d'ADR-053 passe de `live` à `retired`.

### D4 — Ce qui est conservé

- **I4** et les taxonomies `.spec/00-canon/planning/*.yml`. Elles sont consommées par la règle
  [[rules-engineering-definition-of-done]], par le check 7 de `check-moc-integrity.py` et par
  `build-planning-registry.js` du monorepo (libellés de PR).
- Les snapshots de `ledger/snapshots/planning/` (63 `run-*.json` sur 61 jours, plus 61 pointeurs
  `latest.json`) et le contenu du MOC (G8 : pas de réécriture de l'histoire). Le `semantic_hash` du MOC reste celui du dernier snapshot, donc le check 7 reste
  cohérent.

### D5 — Condition d'un éventuel retour

Un nouveau writer de planning exige un nouvel ADR, avec trois conditions :

1. il passe par PR (G4) ;
2. il tourne dans un clone dédié, jamais dans un checkout partagé ;
3. son silence est détecté : un état avec un âge maximal, vérifié par un autre processus que
   lui-même.

## Options considérées

| Option | Verdict | Raison |
|---|---|---|
| Retirer le writer et figer le MOC | **Retenue** | Supprime un mécanisme en panne qui n'avait plus de chemin d'exécution légitime. Conserve les taxonomies utilisées. |
| Clone dédié et PR automatique quotidienne | Rejetée | Impose une fusion owner chaque jour (G4.2). Le constat 8 montre que le MOC n'était pas lu. |
| Recréer le répertoire du verrou | Rejetée | Relancerait les `reset --hard` sur le checkout partagé. Le push direct sur `main` est refusé de toute façon. |
| Laisser en l'état | Rejetée | ADR-053 resterait marqué `live` alors que le système est arrêté. Du code qui pousse sur `main` resterait réactivable. |

## Ce que cet ADR NE fait PAS

- Il ne modifie pas les taxonomies `.spec/00-canon/planning/*.yml`, ni la règle de Definition of
  Done.
- Il ne supprime ni les snapshots ni le journal `/var/log/governance-vault/planning-sync.log`, qui
  reste une preuve.
- Il ne désigne pas de nouvelle source de vérité pour les priorités. L'état d'une PR se lit sur
  GitHub.
- Il ne modifie pas le monorepo. Le libellé « chantier/EPIC SoT » de `build-planning-registry.js`
  et la fixture associée relèvent d'un suivi monorepo.
- Il ne ferme pas le GitHub Project. L'owner peut le fermer depuis l'interface GitHub : le jeton de
  la machine DEV n'a pas le scope nécessaire.
- Il ne touche à aucun workflow `.github/` : aucun workflow ne lançait le writer.

## Conséquences

**Positives**

- Le vault n'a plus aucun writer automatique, ce qui est cohérent avec G4.
- Le checkout runtime du vault n'est plus soumis à des `reset --hard` quotidiens.
- ADR-053 ne prétend plus qu'un système arrêté est « live ».

**Négatives**

- Il n'y a plus de vue agrégée des PR des deux dépôts. Celle qui existait était périmée depuis le
  2026-08-14 et n'avait pas été remarquée.

## Mise en œuvre

Dans cette PR :

- cet ADR, et `amended_by: ["ADR-104"]` plus `planning_live_state: retired` dans ADR-053 ;
- le bandeau « figé » de `MOC-Planning-Live` ;
- la suppression de `_scripts/planning/` ;
- la mise à jour de `.spec/00-canon/planning/README.md`, `ledger/snapshots/planning/README.md`,
  [[governance-runtime-map]], [[cron-setup]] et [[deploy-bot]] ;
- la régénération de `MOC-Decisions`.

Actions owner :

- avant la fusion : archiver le venv et le fichier d'environnement du writer (script fourni, sans
  root). Le script de fusion refuse de fusionner tant que le venv est présent ;
- supprimer `/etc/cron.d/planning-live` (script fourni, demande sudo). Cette étape peut venir
  après la fusion : le writer est déjà neutralisé ;
- en option, fermer le GitHub Project depuis l'interface.

Après la fusion : fermer les issues #278, #314, #321 et #341 avec un renvoi à cet ADR.

## Références

- [[ADR-053-planning-live-system|ADR-053]] — système amendé
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] — G4 v3.1.0 (écriture par PR, fusion humaine)
- [[ADR-020-weekly-vault-lint|ADR-020]] — revue planifiée
- [[governance-runtime-map]] — diagnostic du writer (Couche D)
- [[MOC-Planning-Live]] — instantané figé
