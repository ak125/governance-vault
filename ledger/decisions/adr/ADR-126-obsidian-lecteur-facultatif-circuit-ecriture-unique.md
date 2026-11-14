---
id: ADR-126
title: "Obsidian, lecteur facultatif du vault : un seul circuit d'écriture, obsidian-setup sans statut canon, .obsidian/ et _backups/ ignorés"
status: proposed
date: "2026-11-14"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: []
related_adr: ["ADR-015", "ADR-101", "ADR-102", "ADR-121"]
related_rules: ["G1", "G2", "G3", "G4"]
related_incidents: []
reviewed_by: ""
version: "1.0.0"
---

# ADR-126 : Obsidian, lecteur facultatif du vault

- **Statut** : Proposed (2026-11-14). Rédigé par un agent (Claude Code CLI, machine DEV) sur mandat de
  l'owner (« Mandat J — Vault : Obsidian hors du processus »). Aucune acceptation n'est déclarée : la
  décision appartient à l'owner et se consigne par un commit de ratification sur la branche
  ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D7). La PR qui porte cet ADR reste
  en brouillon jusque-là.
- **N'amende aucun ADR ni aucune règle.** Le sens de G1 à G4 ne change pas ; seuls l'Objectif de
  [[rules-vault]] et l'énoncé de G2 perdent le nom d'un outil.

## Contexte

Constats vérifiés le 2026-11-14 sur `main` du vault (`adfba90a2e5232a66a5162765363d605010c1e73`) :

1. `99-meta/obsidian-setup.md` porte `status: canon`. Il déclare canoniques trois plugins Obsidian
   (Dataview, Templater, Git). Le vault ne contient aucune requête Dataview ni aucune syntaxe Templater
   (recherche sur tous les fichiers suivis : 0 occurrence).
2. Le même document prescrit des commits depuis l'interface d'Obsidian (plugin Git : « Commit / push /
   pull depuis l'UI Obsidian », « Commit manuel via UI »). [[rules-vault|G4]] et [[AGENTS]] imposent un
   worktree dédié créé depuis `origin/main`, des commits signés, une PR et la fusion par l'owner.
3. `99-meta/onboarding/claude-desktop-instructions.md` décrit un troisième circuit : rédaction dans
   Claude Desktop, relecture dans Obsidian, commit signé en terminal. Son étape 10 dit « merge squash »
   sans désigner l'owner.
4. `.gitignore` n'exclut ni `.obsidian/` ni `_backups/` (snapshots du plugin Git). Le dépôt est public.
5. README, l'Objectif de [[rules-vault]], l'énoncé de G2 et l'index des règles décrivent le dépôt comme
   un « vault Obsidian » et ses liens comme des « wikilinks Obsidian ». Les contrôles
   (`_scripts/check-orphans.sh`, `_scripts/check-broken-links.sh`) lisent les fichiers Markdown et la
   syntaxe `[[...]]` sans aucune dépendance à Obsidian.

Trois circuits d'écriture décrits pour un même dépôt, dont deux contournent le worktree dédié, et un
document `canon` qui prescrit des outils inutilisés : c'est un écart entre un texte et la règle G4, à
signaler et résoudre (G1).

## Décision

**D1 — Le vault est un dépôt Git de documents Markdown reliés par des wikilinks `[[...]]`.** Aucune
règle ni procédure du vault ne demande un outil de lecture ou d'édition particulier. Obsidian, comme tout
lecteur Markdown, est facultatif et sert à lire.

**D2 — Un seul circuit d'écriture : celui d'[[AGENTS]]** (worktree dédié depuis `origin/main`, preflight,
commits signés, PR, fusion par l'owner). Aucun document du vault ne décrit d'écriture, de commit, de push
ou de relecture obligatoire depuis Obsidian ou Claude Desktop. `claude-desktop-instructions.md` est aligné
sur ce circuit : Claude Desktop lit et propose du texte ; l'application suit [[AGENTS]].

**D3 — `99-meta/obsidian-setup.md` perd son statut `canon`** et devient une note d'usage facultatif
(`status: current`) : lecture seule, clone autonome hors de tout autre dépôt, plugin Git en pull seul sans
commit ni push depuis l'interface, aucun plugin requis, Dataview et Templater retirés, notes quotidiennes
et Canvas désactivés. L'écriture renvoie à [[AGENTS]].

**D4 — `.obsidian/` et `_backups/` sont ignorés par Git.** Le vault ne versionne aucune configuration
d'outil. Versionner un jour une configuration `.obsidian/` demanderait un ADR qui lève cette exclusion.

**D5 — Formulation indépendante de l'outil**, sans changement de sens : README, Objectif de
[[rules-vault]] et énoncé de G2 (« wikilink (`[[...]]`) » au lieu de « wikilink Obsidian »),
[[MOC-Governance]] et [[MOC-Rules]].

## Options Considérées

### Option A : statu quo documenté

**Description** : garder `obsidian-setup.md` canon et ajouter une mention « ne pas commiter depuis
Obsidian ».

**Inconvénients** :
- garde canoniques deux plugins que rien n'utilise ;
- laisse coexister plusieurs circuits d'écriture dans des documents de statut `canon`.

### Option B : retirer `obsidian-setup.md` et `claude-desktop-instructions.md`

**Description** : archiver les deux documents.

**Inconvénients** :
- perd des consignes utiles à la lecture (clone autonome, pas de ZIP, pas de coffre imbriqué) ;
- un retrait de document est plus lourd qu'un alignement et n'apporte rien de plus à D2.

### Option C : lecteur facultatif, circuit unique (retenue)

**Description** : D1 à D5.

**Avantages** :
- un seul circuit d'écriture décrit, celui que G4 et la protection de `main` imposent déjà ;
- aucune dépendance à un outil dans les règles ;
- aucune configuration locale publiée par erreur sur un dépôt public.

## Justification

G4 et la protection de `main` fixent déjà le seul chemin par lequel une modification atteint `main`. Les
documents qui en décrivent un autre ne créent aucun droit ; ils induisent en erreur. Le changement de
statut de `obsidian-setup.md` est une décision au sens de G1 : il est porté ici. Les autres
modifications alignent des textes sur G4 sans changer de décision.

## Conséquences

### Positives

- un lecteur du vault trouve un seul circuit d'écriture ;
- `.obsidian/` et `_backups/` ne peuvent plus être commités par un `git add -A`.

### Négatives

- un poste qui utilisait le plugin Git pour commiter doit passer par un worktree et un terminal.

### Neutres

- les contrôles G2 et liens cassés ne changent pas ici ; l'identité des liens par chemin relève d'une PR
  et d'une décision distinctes.
- `_scripts/check-public-ip.py` continue de scanner `.obsidian/` présent sur disque.

## Critères de Succès

- [ ] Aucune procédure d'écriture passant par Obsidian ou Claude Desktop dans le vault
- [ ] `git check-ignore .obsidian/x _backups/x` renvoie les deux chemins
- [ ] Aucun sens de règle modifié (relecture du diff de [[rules-vault]] : Objectif et G2, mots seuls)

## Implémentation

Même PR que cet ADR : `.gitignore`, `99-meta/obsidian-setup.md`,
`99-meta/onboarding/claude-desktop-instructions.md`, `README.md`, [[rules-vault]] (v3.4.1),
[[MOC-Governance]], [[MOC-Rules]], commentaire de `_scripts/test_check_public_ip.py`.

Hors périmètre : versionnement d'une configuration `.obsidian/` ; [[ADR-114-wiki-safety-auto-gate|ADR-114]]
et ses mentions du rendu Obsidian ; les mentions historiques d'Obsidian dans les ADR, audit-trails et
savoirs datés, qui décrivent un état passé.

## Revue Planifiée

**Date** : à la ratification par l'owner.
**Critères de revue** : réapparition d'un circuit d'écriture hors [[AGENTS]] dans un document du vault.

---

*Proposé le : 2026-11-14*
*Accepté le : —*
*Dernière revue : 2026-11-14*
