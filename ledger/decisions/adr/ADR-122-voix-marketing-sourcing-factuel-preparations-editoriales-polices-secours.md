---
id: ADR-122
title: "Voix marketing : sourcing factuel, préparations éditoriales hors brief et polices de secours — trois textes approuvés par l'owner le 2026-11-04, amende rules-marketing-voice (1.1.0)"
status: proposed
date: "2026-11-04"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["rules-marketing-voice"]
extends: []
related_adr: ["ADR-031", "ADR-036", "ADR-038", "ADR-061", "ADR-101", "ADR-119", "ADR-121"]
related_rules: ["G1", "G4"]
related_incidents: []
version: "1.0.0"
---

# ADR-122 : voix marketing — sourcing factuel, préparations éditoriales hors brief et polices de secours

- **Statut** : Proposed (2026-11-04). Les trois textes de D1 à D3 sont ceux que Marwane a approuvés
  le 2026-11-04 (remise du département 02 Gouvernance, relayée par le département 23 IA, Agents &
  Automatisation). Cet ADR les consigne mot pour mot et ne les réarbitre pas. Il reste `proposed`
  jusqu'à la décision de l'owner sur ce candidat, consignée par le commit de ratification
  (ADR-121 D7) ; aucun agent ne ratifie. Avant la fusion par l'owner de la tête ratifiée, ni cet ADR
  ni les textes qu'il porte ne modifient le canon de `main`. Rédigé par un agent (session Claude
  Code CLI, serveur DEV) sur le mandat de l'owner du 2026-11-04.
- **Modifie**, sur le seul passage listé en §Amendement : [[rules-marketing-voice]] (1.0.1 → 1.1.0).
- **Relie** à la même décision deux textes du monorepo, qui exécute (G1) : D2 et D3.

## Contexte

### C1 — La clause « Sourcing factuel » admet le RAG comme preuve

[[rules-marketing-voice]] 1.0.1, §Obligatoires absolus, dit : « tout chiffre, durée, kilométrage,
garantie cité doit être vérifiable en RAG `gammes/` ou `wiki/vehicle/` ou DB `__orders` ».
L'obligation ne couvre que quatre types de faits et accepte un résultat RAG comme vérification.
[[ADR-031-four-layer-content-architecture|ADR-031]] range le RAG parmi les consommateurs des
exports WIKI ; l'admission d'un fait relève de la WIKI selon
[[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]]. La clause diverge de ces ADR
(G1 : constat).

### C2 — La règle du workspace marketing ne laisse aucune place aux préparations d'un lot

`workspaces/marketing/.claude/rules/marketing-batch.md` (monorepo), §« Sortie en table DB, pas en
`.md` flottants », interdisait tout fichier `.md` créé par un agent hors
`workspaces/marketing/.claude/agents/`. [[ADR-036-marketing-operating-layer|ADR-036]] écarte le
stockage **des briefs** en `.md` flottants dans `automecanik-wiki/` (§Anti-patterns à éviter) ; les
textes, recherches et preuves préparatoires d'un lot n'avaient aucune destination admise.

### C3 — La constitution UX interdit des polices que les tokens emploient en secours

`design-system/UX-CONSTITUTION.md` (monorepo) interdit `system-ui` et `-apple-system` sans
distinguer famille principale et police de secours. `packages/design-tokens/src/tokens.json` les
place toutes deux en secours après les familles principales approuvées (Outfit, DM Sans) ;
`frontend/tailwind.config.cjs` y place `system-ui`. Divergence document ↔ code.

### C4 — Une décision, trois textes

Le 2026-11-04, l'owner a approuvé un texte exact pour chacun de ces constats. Le texte de D1 modifie
une règle `canon` du vault : selon G1, ce changement de décision passe par un ADR. Les textes de D2 et
D3 sont des documents du monorepo ; ils relèvent de la même décision, que cet ADR consigne.

## Décisions

Chaque texte est cité tel qu'approuvé. L'empreinte est le SHA-256 du texte seul, en UTF-8, sans
saut de ligne final.

### D1 — Sourcing factuel ([[rules-marketing-voice]] 1.1.0, §Obligatoires absolus)

> Toute affirmation factuelle conserve une référence vérifiable, datée ou versionnée, adaptée à sa nature. Les faits techniques renvoient aux sources applicables et à leur état d’admission WIKI selon les ADR en vigueur ; les compatibilités au catalogue ; prix, stock, délais et garanties à leur source métier applicable et datée. Un résultat RAG ne vaut pas, à lui seul, preuve d’admission ou de validité métier.

Empreinte : `1805ec07d00e64e2aa2329284af1d67cde869f387c462c004e1a1c9a3cff3978`. Ce texte remplace la
clause citée en C1.

### D2 — Préparations éditoriales (monorepo, `workspaces/marketing/.claude/rules/marketing-batch.md`)

> Les briefs opérationnels restent enregistrés dans `__marketing_brief` ; aucun fichier Markdown ne les remplace. Les textes, scripts éditoriaux, recherches et preuves préparatoires peuvent être conservés dans le dossier existant du lot, dans les limites du mandat et des destinations autorisées. Ils ne constituent pas un brief opérationnel approuvé. La remise relie la version éditoriale retenue au brief concerné, sans second suivi ni remplacement des enregistrements et validations exigés.

Empreinte : `03fd9c8472969f714f95f0481998e91955449b8867dcaa29e6e66cc3d7c23d0d`. Ce texte remplace le
paragraphe de la section citée en C2, dont le titre reste. Les briefs restent dans
`__marketing_brief` : ADR-036 n'est pas amendé.

### D3 — Polices de secours (monorepo, `design-system/UX-CONSTITUTION.md`)

> Pour les interfaces AutoMecanik utilisant les tokens natifs, `system-ui` et `-apple-system` restent interdits comme familles principales de marque. Leur présence comme polices de secours après la famille principale approuvée est autorisée dans les piles heading/body/sans existantes. Cette précision ne change ni les familles principales, ni les valeurs des tokens, ni les autres interdictions.

Empreinte : `3a7cf8bc92d653110797bf0b0703e83fc5401299c7d62129b23c223ffbcaadba`. Ce texte s'ajoute
après le bloc « FORBIDDEN Fonts », dont la liste ne change pas.

## Amendement

Les textes suivants figurent dans la même PR. Ils deviennent canon applicable lorsque l'owner
fusionne la tête qui porte la ratification (ADR-121 D7) ; avant cette fusion, ils ne modifient pas le
canon de `main`.

- **[[rules-marketing-voice]] 1.1.0** : §Obligatoires absolus, la puce « Sourcing factuel » porte le
  texte de D1 ; `version` et `updated` du frontmatter, en-tête et table « Versionnage » alignés.
  Inchangés : §Interdits absolus (stock confirmé par requête live au moteur de stock, prix issu
  d'une requête SQL en temps réel), les autres obligations, le verrou `local_canon` des voix LOCAL et
  HYBRID, les validations distinctes (ADR-121 D2) et l'admission WIKI d'ADR-119.
- **`_scripts/compute-canon-hashes.py`** : version de `marketing_voice` 1.0.1 → 1.1.0.
  **`99-meta/canon-hashes.json`** régénéré par `--write` : seule l'entrée `marketing_voice` change
  (version, `canon_sha256`, `distribution_sha256`), avec la date `updated` du manifeste.
- **Index de [[MOC-Decisions]]** régénéré par `_scripts/sync_moc_decisions.py --write`.

Les textes de D2 et D3 se publient dans une PR du monorepo ; les deux miroirs de la voix, par la PR
de `canon-sync` (§Mise en œuvre).

## Ce que cet ADR ne fait pas

- Il ne modifie ni ADR-036, ni ADR-119, ni ADR-121, ni aucune autre règle du vault.
- Il ne crée aucune gate, aucun check, aucun registre, aucun suivi, ni aucun droit d'écriture
  (WIKI, RAW, vault ou RAG), et n'en retire aucun.
- Il ne change ni les familles principales, ni les valeurs des tokens, ni les autres interdictions
  de la constitution UX.
- Il ne modifie aucun code applicatif du monorepo : ni les DTO du module `marketing/`, ni
  `marketing-preparation.ts`, ni `brand-compliance-gate.service.ts`. Dans le vault, seule la
  constante de version de `marketing_voice` change dans `_scripts/compute-canon-hashes.py`
  (§Amendement).
- Il n'autorise aucune fusion, publication, synchronisation ni mise en production.

## Mise en œuvre

1. La PR du vault porte cet ADR, la règle, le script, le manifeste et l'index. Elle reste en
   brouillon jusqu'à la ratification (ADR-121 D7).
2. La décision de l'owner sur la tête de cette PR est consignée par le commit de ratification :
   statut `accepted` (frontmatter et ligne Statut), `decision_date`, ligne « Accepté le », index de
   [[MOC-Decisions]] régénéré, mentions suspensives retirées, liens `amended_by` réciproques
   applicables ajoutés (ADR-121 D7). La portée de ces liens pour la règle amendée,
   [[rules-marketing-voice]], est à qualifier par le département 02 sur le candidat, lors de la
   ratification. Si la règle reçoit des métadonnées, son `canon_sha256` change (le frontmatter y est
   inclus) : le manifeste se régénère par `--write` puis se vérifie par `--check`, et l'effet sur la
   distribution et les miroirs se constate alors. Les empreintes du manifeste à la proposition
   décrivent le candidat proposé, pas l'état après ratification.
3. L'owner fusionne la tête épinglée (ADR-121 D4).
4. Les miroirs du monorepo suivent les mécanismes existants
   ([[ADR-061-workspace-governance|ADR-061]] §3) : `canon-publish` envoie `canon-updated` au
   monorepo, dont `canon-sync` ouvre ou met à jour sa PR ; `marketing-voice-hash.yml` vérifie les
   copies contre `main` du vault. Les miroirs ne s'éditent pas à la main. La fusion des miroirs ne
   vaut pas chargement : un service ou un agent n'emploie la version 1.1.0 qu'une fois la version
   déployée sur sa cible et sa lecture effective constatée.
5. La PR du monorepo qui porte D2 et D3 se fusionne après la fusion du vault.

## Options considérées

### Option A — Modifier la règle sans ADR — rejetée

Le texte de D1 change ce que la règle exige et ce qu'elle admet comme preuve. G1 et le `CLAUDE.md`
du vault réservent ce changement à un ADR.

### Option B — Un ADR par texte — rejetée

L'owner a pris une seule décision sur trois textes ; seul D1 touche le vault. Trois ADR
disperseraient cette décision.

### Option C — Un ADR qui consigne la décision et cite les trois textes — retenue

La décision et ses textes exacts restent liés par leurs empreintes, et le vault reste la seule source
de la règle amendée.

## Conséquences

### Positives

- La clause de sourcing ne contredit plus ADR-031 ni ADR-119.
- Les préparations d'un lot marketing ont une place admise, sans devenir des briefs.
- La constitution UX décrit les piles de polices réellement employées par les tokens.

### Négatives

- Jusqu'à la fusion de leur PR, les miroirs du monorepo gardent la version 1.0.1 de la voix ; après
  la fusion du vault, `marketing-voice-hash.yml` signale cet écart.

## Retour arrière

Avant fusion : fermer la PR. Après fusion : un ADR qui amende celui-ci ; la règle, le script et le
manifeste se restaurent par un revert de la PR, suivi de la régénération du manifeste ; les miroirs
suivent par `canon-sync`.

## Revue planifiée

**Date** : 2027-02-04.

**Critères** : une affirmation marketing publiée sans référence datée ou versionnée ; un résultat RAG
présenté comme preuve d'admission ; une préparation éditoriale traitée comme brief.

## Références

- [[rules-marketing-voice]] · [[rules-vault]] · [[MOC-Decisions]]
- [[ADR-031-four-layer-content-architecture|ADR-031]] ·
  [[ADR-036-marketing-operating-layer|ADR-036]] · [[ADR-038-marketing-agent-naming-canon|ADR-038]] ·
  [[ADR-061-workspace-governance|ADR-061]] · [[ADR-101-vault-decides-canon-authority|ADR-101]] ·
  [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] ·
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]]
- Vault : `_scripts/compute-canon-hashes.py`, `_scripts/sync_canon_mirrors.py`,
  `.github/workflows/canon-publish.yml`.
- Monorepo : `workspaces/marketing/.claude/rules/marketing-batch.md`, `design-system/UX-CONSTITUTION.md`,
  `.claude/canon-mirrors/marketing-voice.md`, `workspaces/marketing/.claude/canon-mirrors/marketing-voice.md`,
  `.github/workflows/canon-sync.yml`, `.github/workflows/marketing-voice-hash.yml`.

---

*Proposé le : 2026-11-04*
*Accepté le : — (décision de l'owner à consigner par le commit de ratification, ADR-121 D7)*
