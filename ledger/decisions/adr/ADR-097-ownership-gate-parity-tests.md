---
id: ADR-097
title: "Parité de périmètre des gardes d'ownership — le gate block-new n'exempte plus les fichiers de test"
status: proposed
date: 2026-08-14
decision_date: ""
version: "1.0.0"
deciders: [Fafa]
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-058"]
related_adr: ["ADR-058", "ADR-062"]
related_rules: ["G1", "G2", "G3"]
related_incidents: []
reviewed_by: ""
tags: [ownership, registry, block-new, repository-control-plane, drift-dashboard, gate-parity, tests]
---

# ADR-097 — Parité de périmètre des gardes d'ownership

## Contexte

Deux gardes du monorepo portent la même responsabilité — *tout fichier indexé doit avoir un
propriétaire* — avec des périmètres opposés.

| garde | rôle | fichier | exemption des tests |
|---|---|---|---|
| **admission** | refuse un fichier créé sans `owner` + `domain` | `scripts/registry/check-new-files.js` | **oui** — `**/*.test.ts`, `**/*.spec.ts`, `**/__tests__/**` dans `EXCEPTION_GLOBS` (l. 70-76), court-circuit avant tout contrôle (l. 130-133) |
| **mesure** | émet un `ownership_gap` par chemin non couvert | `scripts/audit/build-drift-dashboard.ts` (`signal3_ownership`, l. 282-314) | **non** — aucune exemption |

Le gate d'admission tourne sur **chaque PR** (`registry-new-file-gate.yml`, sans filtre `paths`)
et en local (`.husky/pre-push:98,100`). La garde de mesure ne tourne que sur les PR touchant le
registre (`contract-drift-ratchet.yml`, filtre `paths`). Un test créé dans un sous-arbre non
possédé passe donc l'admission, et n'apparaît qu'à la **régénération suivante de la Layer 1** —
c'est-à-dire potentiellement des mois plus tard, dans une PR étrangère à son auteur.

### L'incident qui l'a rendu visible

Cinq fichiers de test ajoutés entre le 2026-06-26 et le 2026-07-16 dans quatre sous-arbres non
possédés (`backend/src/modules/{errors,staff,substitution}`, `backend/src/remix`) ont passé
l'admission. Ils sont apparus d'un coup comme cinq `ownership_gap` bloquants quand la Layer 1 a
été dégelée (`files.json` 2728 → 2833), dans une PR qui ne les avait pas créés. Fermé par
[PR #1350](https://github.com/ak125/nestjs-remix-monorepo/pull/1350), qui a déclaré les quatre
sous-arbres — sans élargir la baseline ni invoquer `--refresh`.

### La divergence est vis-à-vis du canon, pas seulement entre deux scripts

ADR-062 (`status: accepted`, donc normative) énonce l'invariant grepable :

> *Toute PR touchant un contract requiert review approuvée par son owner ; **toute PR créant un
> nouveau fichier sans ownership résolu est bloquée** (ADR-058 Phase 2 block-new gate).*

Sans réserve sur les tests. ADR-062 n'autorise un ownership non résolu que **temporairement, avec
ADR de dérogation et date de résolution cible**. `EXCEPTION_GLOBS` n'a ni l'une ni l'autre :
l'exemption des tests est une dérogation implicite et sans échéance à une décision acceptée.

### Ce qui n'est pas établi

Aucune source écrite ne **motive** l'exemption. Le docblock (`check-new-files.js:21-26`), le
commit de création du gate, les corps de PR d'origine et ADR-058 l'**énumèrent** tous et n'en
raisonnent aucun. Cette ADR ne reconstitue pas une intention : elle constate qu'aucune trace ne
la raisonne.

## Décision

**Retirer `**/*.test.ts`, `**/*.spec.ts` et `**/__tests__/**` de `EXCEPTION_GLOBS`**, de sorte
qu'un fichier de test obtienne son ownership **par héritage du glob de son sous-arbre**, comme
tout autre fichier — et soit refusé à l'admission si ce sous-arbre n'a pas de propriétaire.

**Conserver `audit/registry/**` et `.changeset/**`.** Mesure : aucun glob d'ownership ne les
couvre et ils comptent **0 chemin indexé** dans `files.json`. Leur exemption est réellement
porteuse et cohérente avec la garde de mesure ; celle des tests ne l'est pas.

**La décision est séquencée en deux PR monorepo, dans cet ordre :**

1. **PR-1 — déclarer l'ownership au grain module.** Ne dépend pas de cette ADR : c'est
   l'extension exacte du geste déjà posé par PR #1350.
2. **PR-2 — retirer les trois globs de test.** Attend le merge de PR-1 **et** l'acceptation de
   cette ADR.

**Interdiction nommée.** PR-1 ne doit **jamais** fermer les sous-arbres non possédés par les
globs fourre-tout `backend/src/**`, `frontend/app/**` ou `backend/scripts/**`. Mesure : ils
éteindraient **231 des 249** `ownership_gap` (92,8 % du signal) pour supprimer 1,2 % de bruit.
C'est le *silent fallback* interdit par l'invariant 3 du `CLAUDE.md` et l'anti-pattern « tout le
monde owne tout » nommé par ADR-062.

## Options Considérées

### Option A — héritage du sous-arbre (retenue)

**Description** : retirer les trois globs de test du gate d'admission. Un test hérite de
l'ownership de son sous-arbre ; sans sous-arbre possédé, il est refusé.

**Avantages** :
- Aligne l'admission sur ce que le système fait **déjà** : sur 434 fichiers matchant les globs
  de test, **431 (99,3 %) sont couverts par héritage** et passeraient au mérite. L'exemption
  n'est porteuse que pour **3** fichiers — exactement ceux qui produisent un `ownership_gap`.
- Rétablit la conformité à ADR-062 sans créer aucune exemption nouvelle.
- Supprime une exception au lieu d'en ajouter une : le seul sens de correction compatible avec
  la doctrine anti-dérogation du vault.
- Le feedback arrive **avant le push** (`.husky/pre-push`), pas seulement en CI.

**Inconvénients** :
- 68 des 465 répertoires sous racines de test plausibles (14,6 %) rejetteraient aujourd'hui un
  nouveau `*.test.ts`, concentrés là où vit toute la dette : `backend/src` (147 gaps) et
  `frontend/app` (70 gaps). D'où le séquencement.
- Coût historique mesuré : 16 des 315 tests ajoutés depuis la naissance du gate auraient été
  bloqués (5,1 %), sur 12 PR / 682 (1,8 %, ~4 PR/mois). **14 des 16 ont vu leur ownership
  déclarée quand même** — l'option n'ajoute pas de travail, elle l'avance.

### Option B — exempter aussi la garde de mesure

**Description** : ajouter la même exemption à `signal3_ownership`, pour harmoniser les deux
gardes par le bas.

**Avantages** :
- Seule option à coût CI nul immédiat : le ratchet est asymétrique (`added` doit être vide,
  `removed` informatif), donc la réduction passe.

**Inconvénients** — rédhibitoires :
- Sort **434 fichiers (15,3 % de `files.json`)** du périmètre mesuré pour éteindre **3
  `ownership_gap` sur 249 (1,2 %)**.
- Laisse 54 entrées de baseline à jamais non résolvables.
- **N'aurait rien empêché de l'incident du 2026-08-14 — elle l'aurait rendu invisible.**
- Exige d'encoder une notion d'exemption dans `build-drift-dashboard.test.ts`, dont le contrat
  actuel (`gapCount` == nombre exact d'orphelins) n'en connaît aucune. C'est un test
  anti-overclaim : le modifier pour faire passer le cas serait retourner la garde.

### Option C — statu quo

**Inconvénients** :
- La fenêtre est mécaniquement reproductible : le prochain rebuild de la Layer 1 reproduit
  l'incident, proportionnellement au nombre de tests créés entre deux régénérations.
- Divergence non déclarée vis-à-vis d'ADR-062 (`accepted`). S'y tenir exigerait de convertir les
  trois entrées en dérogation datée — **plus de travail que de les retirer**.

## Justification

**L'argument de catégorie est décisif.** Dix-huit des trente-huit règles `ast-grep` et le ratchet
`served-content-write` exemptent les tests — parce qu'ils jugent un **comportement**, et qu'un
test doit légitimement exercer le geste interdit. **Aucune garde d'attribution n'exempte quoi que
ce soit** : `signal3_ownership` n'exempte rien, `ownership.yaml` déclare déjà cinq arbres de
test, et `test` est un `FileKind` de première classe du registre.

Le meilleur modèle du repo tranche déjà dans ce sens en un seul artefact :
`commerce-no-rpc-without-authority.yml` exempte les tests **de la règle** tout en exigeant qu'ils
soient **nommés** dans `authority-graph.yaml`, avec un validateur qui vérifie leur existence.
Exempter du comportement, jamais de l'attribution.

`check-new-files.js` est un gate d'attribution qui a hérité de l'idiome des gates
comportementaux. L'option A ne crée donc aucune doctrine : elle nomme celle déjà appliquée
partout ailleurs — invariant 2 du `CLAUDE.md`, *étendre avant créer*.

**Deux précédents indépendants ont déjà tranché dans ce sens quand le cas s'est présenté.** Dans
le commit de création du gate lui-même, une fixture de test non possédée a été corrigée par
**deux entrées d'ownership**, pas par un élargissement de la liste d'exception. PR #1350 a rejoué
le même geste trois mois plus tard sur quatre sous-arbres. **L'exemption est la contre-exception,
pas la convention.**

## Conséquences

### Positives

- La fenêtre entre création et détection disparaît : un ownership manquant est signalé à
  l'auteur du fichier, au moment de sa création, et non des mois plus tard à un tiers.
- Le signal `ownership_gap` retrouve un sens : il mesure la dette réelle, sans zone aveugle.
- Conformité rétablie à l'invariant grepable d'ADR-062.
- PR-1 réduit la dette d'ownership **en l'attribuant**, pas en la masquant.

### Négatives

- Nouveau cas d'échec pour le développeur : créer un test dans un sous-arbre non possédé fait
  échouer le job `Block-new` **et** le hook `pre-push`. Correctif nommé et actionnable sur les
  deux surfaces : une entrée dans `ownership.yaml` avec `domain` D1..D15 **et** `owner`.
- Le gate ne devinera jamais le domaine à la place de l'auteur — invariant assumé d'ADR-058
  (*classification jamais forcée*). L'amélioration disponible est d'afficher les globs les plus
  proches du chemin refusé, pas de suggérer un domaine.
- PR-1 fait mécaniquement baisser `sourceConfidence: high` de 75,0 % (165/220) à ~65 % si les
  ~34 entrées sont `medium` — **sous le seuil d'acceptance V1 d'ADR-058 (≥ 70 %)**. Aucun script
  ne calcule cette métrique, donc aucune CI ne rougira : c'est un arbitrage owner à poser
  explicitement, pas un effet à découvrir.

### Neutres

- Aucun impact sur les 431 tests déjà couverts par héritage.
- Le job `Block-new (owner + domain required)` **n'est pas** dans les 13 required status checks
  de `main`. Cette ADR restaure donc un **signal rouge visible**, pas un verrou mécanique de
  merge. Écrire « la fenêtre est fermée » sans décision owner sur les required checks serait un
  overclaim.

## Critères de Succès

- [ ] PR-1 mergée : les 68 répertoires bloquants tombent à ~0, mesuré par rejeu de `classify()`
      sur `<dir>/hypothetical.test.ts`.
- [ ] PR-1 n'introduit **aucun** des trois globs fourre-tout, et déclare dans son corps le
      `ownership_high_confidence_pct` avant/après.
- [ ] PR-2 mergée : rejeu des 315 tests ajoutés depuis la naissance du gate contre l'overlay
      post-PR-1 → **0 bloqué** (16 avant PR-1), sortie de commande collée dans le corps de la PR.
- [ ] `signal3_ownership` et son test restent **inchangés** — aucune exemption ajoutée côté mesure.
- [ ] Aucun `--refresh` de `contract-drift-baseline.json` sur toute la séquence.

## Implémentation

**PR-1 — `ownership.yaml`, grain module.** Déclarer les sous-arbres mesurés comme bloquants (tête
de liste : `frontend/app/types`, `frontend/app/services`, `backend/scripts`,
`backend/src/common/exceptions`, `backend/src/modules/search/services`,
`backend/src/database/services`, `backend/src/modules/system/services`,
`backend/src/security/rpc-gate`). `sourceConfidence` selon l'origine du signal : `medium` pour
une attribution par similarité de concern (précédent PR #1350), `high` seulement si la source du
test est nommée et déclarée dans le même geste. Régénérer les projections L3 dans la même PR.

**PR-1bis — résidu racine.** `backend/src/instrument.test.ts` et
`backend/src/instrument-init-count.test.ts` n'ont pas de sous-arbre : deux globs de **chemin
exact**, déclarés conjointement avec leur source. Ne **pas** ajouter `backend/src/**` de
rattrapage — et acter que le prochain test créé à la racine rebloquera, ce qui est voulu.
`frontend/frontend/tests/e2e/` n'est pas déclaré : ce répertoire relève d'une suppression, pas
d'une attribution.

**PR-2 — le retrait.** Trois lignes de `EXCEPTION_GLOBS`, jamais le tableau entier. Mettre à jour
dans le même geste : le docblock (l. 21-26), le message d'aide qui propose encore « *mark the
path as an exception* » (l. 239-241), et l'en-tête de `registry-new-file-gate.yml` qui énumère
encore les tests comme exceptions. Créer `scripts/registry/check-new-files.test.ts` épinglant
quatre cas : test non possédé → `missing_both` ; test possédé → `ok` **au mérite** ;
`audit/registry/**` → exception conservée ; `.changeset/**` → exception conservée. Vérifier avant
de commiter que `scripts/registry/**` est lui-même couvert, sinon le nouveau fichier de test se
bloque lui-même.

### Non-goals explicites

- Aucune exemption ajoutée à `signal3_ownership` ni à son test.
- Aucun élargissement du filtre `paths` de `contract-drift-ratchet.yml` : `files.json` est une
  projection régénérée sur les PR registre ; l'élargir ne ferait rien voir de plus. Le seul point
  d'observation au moment de la création d'un fichier est le gate d'admission — c'est
  précisément pourquoi le correctif est de ce côté.
- Aucun `--refresh` de baseline.
- Aucune modification des 18 règles `ast-grep` qui exemptent les tests : elles jugent un
  comportement, pas une attribution.

### Décision owner distincte

Le job `Block-new` n'étant pas un required status check, son entrée dans la branch protection est
une décision séparée, hors PR-1 et PR-2.

## Revue Planifiée

**Date** : 2026-11-14

**Critères de revue** : reconsidérer si (a) le taux de PR bloquées dépasse durablement 3 %, (b)
la contrainte d'attribution produit des owners de complaisance plutôt que des propriétaires
réels, ou (c) un besoin légitime de test hors de tout sous-arbre gouverné apparaît de façon
répétée.

---

*Proposé le: 2026-08-14*
*Accepté le: *
