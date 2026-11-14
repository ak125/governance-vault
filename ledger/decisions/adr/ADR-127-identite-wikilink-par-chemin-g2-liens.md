---
id: ADR-127
title: "Identité d'un document par son chemin pour G2 et les liens cassés : homonymes tous contrôlés, lien court résolu si le nom est unique, ambiguïté signalée, lien vers soi non compté"
status: proposed
date: "2026-11-14"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: []
related_adr: ["ADR-020", "ADR-121", "ADR-126"]
related_rules: ["G1", "G2"]
related_incidents: []
reviewed_by: ""
version: "1.0.0"
---

# ADR-127 : identité d'un document par son chemin pour G2 et les liens cassés

- **Statut** : Proposed (2026-11-14). Rédigé par un agent (Claude Code CLI, machine DEV) sur mandat de
  l'owner (« Mandat J », lot 2). Aucune acceptation n'est déclarée : la décision appartient à l'owner et
  se consigne par un commit de ratification sur la branche
  ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D7). La PR qui porte cet ADR reste
  en brouillon jusque-là.
- **N'amende pas l'énoncé de G2** ([[rules-vault]]) : un document reste non orphelin s'il est référencé
  par un wikilink depuis un autre document. Cet ADR fixe comment ce « référencé » se calcule, ce qui
  change l'ensemble des documents que G2 contrôle effectivement (G1).

## Contexte

Constats vérifiés le 2026-11-14 sur `main` (`adfba90a2e5232a66a5162765363d605010c1e73`), 565 fichiers
`.md` :

1. `_scripts/check-orphans.sh` indexait les documents dans un dictionnaire `nom → chemin`. Pour un nom
   porté par plusieurs fichiers, seul le dernier lu était contrôlé. 10 noms sont portés par plusieurs
   fichiers (51 fichiers : `README` ×5, `01-context` à `09-attestations` dans les evidence-packs) ;
   41 de ces fichiers n'étaient jamais contrôlés par G2 (un seul par nom l'était).
2. Les liens entrants étaient comptés par nom, depuis le dernier segment du lien : un `[[README]]` ou un
   `[[dossier/README]]` rendait « lié » n'importe quel `README.md`.
3. `_scripts/check-broken-links.sh` acceptait un lien dès que son dernier segment était le nom d'un
   fichier existant : `[[mauvais/chemin/note]]` passait si une `note.md` existait ailleurs.
4. Un lien d'un document vers lui-même comptait comme lien entrant.

Avec une identité par chemin, l'arbre réel révèle 5 orphelins (4 `README.md` et un `01-context.md`
d'evidence-pack) et 2 liens ambigus (`[[README]]` dans [[MOC-Governance]], `[[01-context]]` dans un
INDEX d'evidence-pack). Aucun lien de chemin existant n'est cassé.

## Décision

**D1 — Un document est identifié par son chemin** relatif à la racine du vault, sans `.md`. G2 contrôle
chaque document, homonymes compris.

**D2 — Résolution d'un lien** (alias `|…` et ancre `#…` retirés) :
- la cible contient `/` : chemin depuis la racine du vault, `/` initial accepté ; résolution exacte,
  sinon le lien est cassé ;
- la cible ne contient pas `/` : nom ; résolu si un seul document le porte, **ambigu** si plusieurs,
  cassé si aucun.

**D3 — Un lien ambigu ne compte pour aucune cible** et fait échouer `check-broken-links.sh`, qui le
liste avec ses candidats. La correction est d'écrire le lien par son chemin
(`[[dossier/nom|alias]]`, `[[/README|README]]` pour la racine).

**D4 — Un lien d'un document vers lui-même est valide mais ne compte pas comme lien entrant.**

**D5 — Un seul résolveur**, `_scripts/wikilinks.py`, utilisé par `check-orphans.sh` et
`check-broken-links.sh`. L'interface des deux scripts (arguments, codes de sortie, emplacement des
rapports) est inchangée ; les workflows, hooks et `weekly-lint.sh` qui les appellent ne changent pas.

Inchangés : liste blanche des racines G2 (`ops/moc`, `99-meta`, `_assets`, `_templates`, `_scripts`,
`README.md`, `CLAUDE.md`, `AGENTS.md`), dossiers exclus (`.git`, `.obsidian`), liens ignorés dans le
code, sensibilité à la casse.

## Options Considérées

### Option A : garder la résolution par nom, avertir sur les homonymes

**Inconvénients** : un homonyme non lié reste invisible pour G2 ; un lien de chemin erroné reste accepté.

### Option B : chemin seul, aucun lien court

**Inconvénients** : oblige à réécrire environ 2 500 occurrences de liens courts (511 noms distincts)
qui désignent sans ambiguïté un document unique.

### Option C : chemin comme identité, lien court accepté si le nom est unique (retenue)

**Avantages** : aucun document n'échappe à G2 ; les liens courts existants restent valides ; seuls les
liens réellement ambigus sont à réécrire (2 sur l'arbre actuel).

## Justification

G2 promet qu'aucun document n'est inaccessible. Avec un index par nom, cette promesse ne couvrait pas
les fichiers homonymes, et un lien pouvait être compté pour un autre document que celui qu'il désigne.
L'identité par chemin aligne le contrôle sur ce que le lien désigne réellement.

## Conséquences

### Positives

- les 51 fichiers homonymes sont tous contrôlés ;
- un lien de chemin erroné est signalé comme cassé ;
- un nouvel homonyme qui rend ambigu un lien court existant est signalé à son introduction.

### Négatives

- ajouter un fichier qui porte le nom d'un document déjà lié par un lien court fait échouer
  `check-broken-links.sh` jusqu'à la réécriture de ces liens par leur chemin.

### Neutres

- `_scripts/check-canon-backlinks.py` présente le même défaut (un lien du vault crédite un fichier canon
  du monorepo par son seul nom) ; il n'est pas modifié ici.
- `_scripts/check-moc-integrity.py` ne résout aucun lien par nom et n'est pas concerné.

## Critères de Succès

- [ ] Sur deux homonymes dont un seul est lié, `check-orphans.sh` signale l'autre
  (`_scripts/test_wikilinks.py`)
- [ ] `check-orphans.sh .` et `check-broken-links.sh .` passent sur l'arbre du vault
- [ ] Checks requis verts sur la PR

## Implémentation

Même PR que cet ADR : `_scripts/wikilinks.py`, `_scripts/check-orphans.sh`,
`_scripts/check-broken-links.sh`, `_scripts/test_wikilinks.py` ; liens réécrits par chemin dans
[[MOC-Governance]] et l'INDEX de `EP-20260506-adr-041-baseline` ; orphelins révélés liés depuis
[[MOC-Planning-Live]], [[MOC-Policies]] et [[MOC-Knowledge]]. Aucun document archivé ni supprimé.

## Revue Planifiée

**Date** : à la ratification par l'owner.
**Critères de revue** : nombre de liens ambigus introduits par de nouveaux homonymes.

---

*Proposé le : 2026-11-14*
*Accepté le : —*
*Dernière revue : 2026-11-14*
