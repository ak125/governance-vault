---
id: ADR-121
title: "Mandat explicite, revue technique, décision de gouvernance et fusion : des actes distincts — amende l'AEC, RULE-H5/H6, DoD2, G1, G4, G5 et ADR-101 D1"
status: proposed
date: "2026-11-01"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-101", "ADR-120", "rules-agent-exit-contract", "rules-engineering-definition-of-done", "rules-vault", "rules-governance-process"]
extends: []
related_adr: ["ADR-013", "ADR-058", "ADR-081", "ADR-099", "ADR-102", "ADR-114", "ADR-119"]
related_rules: ["AEC", "DoD2", "G1", "G4", "G5"]
related_incidents: []
version: "1.0.0"
---

# ADR-121 : mandat explicite, revue technique, décision de gouvernance et fusion — des actes distincts

- **Statut** : Proposed (2026-11-01). Rédigé par un agent sur le mandat de l'owner du 2026-11-01
  (mission SPACE-001). Rien n'est normatif avant la décision de l'owner et la fusion (§D7) ; cet ADR
  ne se déclare pas accepté et ne s'attribue aucune ratification.
- **Modifie**, sur les seuls passages listés en §Amendement : le contrat [[rules-agent-exit-contract]]
  (1.0.1 → 1.1.0), RULE-H5 et RULE-H6 de [[GOVERNANCE-HUMAN]], DoD2 point 6 de
  [[rules-engineering-definition-of-done]] (1.1.0 → 1.2.0), G1 et G4 de [[rules-vault]]
  (3.1.0 → 3.2.0), G5 de [[rules-governance-process]] (3.1.0 → 3.2.0), D1 de
  [[ADR-101-vault-decides-canon-authority|ADR-101]] et le point AP-self-merge de
  [[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]]. Les corps d'ADR-101 et d'ADR-120 restent
  inchangés ; leurs liens `amended_by` s'ajoutent à la ratification.
- **Reprend** le texte du candidat AEC 1.1.0 préparé le 2026-10-20 par une session Codex, resté non
  commité et numéroté ADR-117, identifiant pris depuis sur `main`.
- **Méthode** : constats vérifiés le 2026-11-01, en lecture seule, sur `main` du vault au commit
  `c2f5dd8` et sur `main` du monorepo au commit `6ab7854c2`.

## Contexte

### C1 — Le contrat de sortie interdit ce qu'un mandat autorise

La règle 1 de l'AEC dit : « Jamais de correction automatique. Un agent […] ne modifie RIEN sans
validation humaine explicite. » Le manifeste ajoute « `corrections_proposed` (JAMAIS appliquées
auto) ». L'invariant 7 du `CLAUDE.md` du monorepo dit au contraire : « Le mandat humain explicite
autorise les corrections de son périmètre ; ne pas redemander ce même accord pour chaque étape. »
L'AEC ne dit pas si un mandat explicite vaut validation pour chaque correction de son périmètre, ni
ce qu'il ne couvre pas.

### C2 — L'AEC accorde une auto-fusion qu'aucun workflow n'emploie

Le point 5 de la section « Distribution canonique » de l'AEC dit : « `canon-publish.yml` […] ouvre
une PR auto dans chaque repo applicatif pour resync. Auto-merge avec label `canon-sync` autorisé. »
L'état des dépôts est autre :

- `canon-publish.yml` du vault vérifie les hashes et émet l'événement `canon-updated` vers les dépôts
  consommateurs ; il ne copie aucun fichier et n'ouvre aucune PR ;
- `canon-sync.yml` du monorepo ouvre ou met à jour la PR `canon-sync/auto`, étiquetée `canon-sync` et
  `automated`, sans activer d'auto-fusion ; son corps demande de relire le diff et de fusionner.

Parmi les règles et les ADR actifs du vault, cette phrase est la seule à accorder une auto-fusion
(ADR-099 l'exclut pour les PR de sous-module). Elle contredit RULE-H6 (« An agent never merges »)
et G4.2. L'en-tête de l'AEC annonce la version 1.0.0, son tableau et son générateur la 1.0.1, et
deux étapes y restent « à créer » alors qu'elles existent.

### C3 — DoD2 renvoie à une exception que rien ne définit

Le point 6 de DoD2 admet le self-merge « documenté comme exception (cf. AP-self-merge en cas
d'urgence avec audit trail) ». [[rules-ai-antipatterns]] définit AP-01 à AP-12 et aucun AP-self-merge.
ADR-120 « garde l'exception AP-self-merge ». Une exception sans définition n'a ni déclencheur, ni
acteur, ni trace : chacun peut l'invoquer.

### C4 — « Revue humaine » désigne deux actes dans RULE-H5 et RULE-H6

RULE-H5 exige que tout changement du canon ou de la gouvernance soit « reviewed by a human » et
« committed manually ». RULE-H6 exige « Review and merge by a human ». Depuis
[[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]], la revue technique d'un diff est un
enregistrement gradué A, B ou C, dont les niveaux A et B ne demandent aucun humain ; depuis
[[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]], l'admission d'une fiche WIKI ne
demande plus de relecture humaine. Les deux règles ne disent pas si leur revue humaine est la revue
du diff ou la décision d'adopter le changement.

### C5 — Le compte qui fusionne ne prouve pas la décision humaine

Les sessions CLI agissent sous l'application `automecanik-agents[bot]` ; la session Desktop et
d'autres agents agissent sous le compte GitHub de l'owner. Une fusion enregistrée sous ce compte
(`merged_by`) prouve le compte, pas la décision d'un humain. ADR-114 à ADR-120 posent que « la
fusion par l'owner vaut ratification » ; les PR #386 à #389 (ADR-117 à ADR-120) portent toutes
`merged_by` = `automecanik-agents[bot]`, et leur trace ne dit pas qui a décidé. L'étape 10 de
l'`AGENTS.md` du vault
demande à l'agent qui la lit de « fusionner en squash » ; sa section « Anti-patterns » et G4.2 le
lui interdisent.

### C6 — Le statut `accepted-revised` est actif pour les scripts et absent de la doctrine

ADR-101 D1, G1 de [[rules-vault]] et G5 de [[rules-governance-process]] ne déclarent normatif que
le statut `accepted`. Le schéma `_scripts/schemas/adr.schema.json` admet sept statuts, dont
`accepted-revised`, et `ADR_STATUSES_ACTIVE` de `_scripts/governance_constants.py` le compte comme
actif ; `check-adr-supersedes.py` en dépend. Deux ADR portent ce statut sur `main` : ADR-002 et
ADR-009. Lue à la lettre, la doctrine les rend non normatifs, alors que les contrôles les traitent
comme actifs. Le tableau « Status Semantics » de [[MOC-Decisions]] annonce six statuts et omet
`rejected`.

### C7 — Un ADR proposé dont l'amendement est déjà en vigueur

[[ADR-081-doctrine-agility-amendments|ADR-081]] est `proposed` et amende
[[rules-governance-process]], dont G9 et G10 portent déjà sa mention. Une règle canon applique donc
un amendement que personne n'a ratifié. Ce constat est signalé ; cet ADR ne le tranche pas.

### C8 — Quatre notions confondues dans les passations

Les passations entre outils (issue #1947 du monorepo, « Passation ChatGPT Space → Claude Code CLI
(code) + Codex (revue) ») attribuent des responsabilités à des outils et à des sessions. Le dépôt
distingue pourtant quatre notions, chacune avec sa source :

- un **département** est l'une des 24 responsabilités du Command Center
  (`audit/automecanik-departments-map.md` du monorepo) ; ce n'est ni un processus ni un agent ;
- un **domaine d'ownership** est l'un des domaines de l'overlay L2 `ownership.yaml`
  ([[ADR-058-repository-control-plane|ADR-058]]), avec un owner humain : c'est lui que lit DoD2 ;
- un **agent du catalogue** est une fiche régie par [[ADR-013-agent-lifecycle-governance|ADR-013]]
  (niveaux G1 conception, G2 activation, G3 production) ;
- une **session** est une exécution temporaire de Claude CLI, Desktop ou Codex, sous un compte GitHub,
  pour un mandat : elle n'a ni ownership ni place au catalogue.

### C9 — Des fusions automatiques du monorepo qu'aucun ADR ne décide

Le monorepo exécute deux workflows qui arment l'auto-fusion de PR Dependabot :

- `dependabot-auto-merge.yml` l'arme selon une règle fixe : mises à jour patch ; mineures des
  dépendances directes de développement ; mineures des groupes `tiptap-ecosystem`,
  `storybook-ecosystem` et `vite-ecosystem` ; toute mise à jour de l'écosystème `github_actions`,
  majeures comprises ;
- `dependabot-claude-review.yml` fait juger la PR par un modèle, qui arme l'auto-fusion sur un verdict
  favorable. Son job ne s'exécute que si la variable `CLAUDE_REVIEW_ENABLED` vaut `true` : présent,
  il n'est pas actif. Ses 510 runs déclenchés par Dependabot (du 2026-05-04 au 2026-10-30), dont 505
  hors sous-module, ont tous la conclusion `skipped`.

Aucun ADR accepté ne les décide. La note de connaissance `auto-merge-dependabot-claude-review-architecture-20260504`
les décrit sans être normative et se réfère à ADR-028, qui traite d'un autre sujet.
[[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport|ADR-099]] D2 en exclut les
mises à jour de sous-module, revues par un humain. Le second workflow, s'il était activé,
contredirait RULE-H6 (« An agent never merges ») : c'est un modèle qui déclencherait la fusion.

## Principe directeur

Un mandat, une revue, une décision et une fusion sont des actes distincts. Chacun a son auteur et sa
preuve. Aucun n'en emporte un autre : un mandat n'autorise pas une fusion, une revue n'est pas une
décision, un compte n'est pas un humain.

## Décisions

### D1 — Le mandat explicite couvre son exécution, dans ses limites

Une demande explicite de correction autorise son exécution et sa vérification dans le périmètre
demandé ; cet accord ne se redemande pas à chaque étape. Une demande de scan, d'analyse ou de
proposition seule n'autorise aucune modification.

Le mandat ne lève aucune permission technique, aucune validation spécifique (D2) et aucune
restriction de fusion, de publication ou de déploiement. Un chemin réservé à l'owner reste réservé :
l'agent prépare le correctif dans le support existant (corps de PR, extrait à appliquer) et ne le
modifie par aucun autre accès. Une action qui dépasse le mandat exige un accord distinct.

### D2 — Cinq actes, cinq preuves

| Acte | Qui | Preuve |
|---|---|---|
| Revue technique d'un diff | auteur, revue indépendante, owner selon le niveau | enregistrement DoD2 sur la tête, niveaux A, B, C (ADR-120) |
| Décision de gouvernance : adopter un ADR, une règle, une policy | l'owner, `decision_makers` | changement porté par un ADR : ratification (D7) ; autre changement : fusion par l'owner de la tête épinglée, tracée selon D4 |
| Validation spécifique | l'humain que désigne l'ADR concerné | celle que fixe cet ADR |
| Fusion | l'owner | commande épinglée sur le SHA (D4) |
| Mise en production | l'owner | tag `v*` ou déclenchement manuel du déploiement PROD ([[rules-deployment-workflow]]) |

Les validations spécifiques restent celles de leurs ADR, notamment : l'accord nominatif de l'owner
sur le SHA pour les zones STOP (niveau C d'ADR-120) ; la revue humaine des niveaux G1 et G2
d'[[ADR-013-agent-lifecycle-governance|ADR-013]] pour le catalogue des agents ; les actes humains
qu'ADR-119 D7 maintient (validation d'une plage chiffrée, ADR-114 D4 ; autorité d'une source
inconnue ; décisions sécurité du diagnostic). ADR-119 retire la relecture humaine des fiches WIKI et
ne retire aucun de ces actes.

### D3 — Rien de ce qui précède la fusion ne l'autorise

Une auto-review, une revue indépendante, une case cochée, une CI verte, la ligne
`Self-review verdict: APPROVE`, un label, une DoD satisfaite ou un « go » général sont des conditions
de fusion. Aucun n'est une autorisation de fusionner.

### D4 — La fusion appartient à l'owner, et sa trace distingue trois éléments

Un agent ne lance jamais une commande de fusion, ni n'active une auto-fusion, quel que soit le compte
sous lequel il agit, celui de l'owner compris. Il remet à l'owner le numéro de PR, le SHA de tête
(40 caractères) et la commande épinglée sur ce SHA.

La trace d'une fusion distingue :

1. le **décideur humain** : l'owner, qui exécute lui-même la commande ;
2. le **SHA fusionné** : la tête épinglée (`--match-head-commit` ou équivalent), celle que nomme
   l'enregistrement DoD2 ;
3. le **compte technique** qui exécute (`merged_by`).

Le compte seul ne prouve pas la décision humaine. Cet ADR ne crée aucune identité, aucun bot et aucun
label pour la prouver (ADR-120 D5).

### D5 — Aucune exception implicite à la fusion humaine

- **PR `canon-sync`** : la phrase « Auto-merge avec label `canon-sync` autorisé » est retirée de l'AEC.
  Une PR de resynchronisation des miroirs se fusionne par l'owner, comme toute PR ; sa revue est de
  niveau A (projection régénérée par son script, vérifiée par les workflows `*-hash.yml`).
- **AP-self-merge** : aucune exception de ce nom n'existe. Une fusion d'urgence sans la revue exigée
  demanderait un ADR qui en définit le déclencheur, l'acteur, la trace et la revue a posteriori.
- **Auto-fusion Dependabot du monorepo (C9)** : cet ADR ne l'autorise pas et ne la désactive pas.
  C'est une divergence signalée (ADR-101 D3). Elle se résout par un ADR qui décide ces workflows et
  leurs bornes, ou par une PR du monorepo qui les retire ; ce choix appartient à l'owner. Une règle
  fixe exécutée par un workflow n'est pas un agent, mais elle fusionne sans décision humaine : seul un
  ADR peut l'admettre. Un modèle qui arme une fusion tombe sous D4.

### D6 — Les statuts normatifs sont `accepted` et `accepted-revised`

Est normatif un ADR en `status: accepted` ou `status: accepted-revised`, sans `superseded_by` actif.
Les autres statuts du schéma (`proposed`, `deferred`, `rejected`, `deprecated`, `superseded`) sont du
contexte. Le schéma `_scripts/schemas/adr.schema.json` fait foi pour la liste des statuts. Aucun
statut existant ne change.

### D7 — Un amendement entre en vigueur à sa ratification

Un ADR rédigé par un agent reste `proposed` jusqu'à la décision de l'owner. La ratification est
cette décision, suivie d'un commit sur la branche de la PR qui passe le statut à `accepted` (frontmatter
et ligne Statut), date la ligne « Accepté le » du pied de page, renseigne `decision_date`, ajoute les
liens `amended_by` réciproques, régénère l'index de [[MOC-Decisions]]
(`_scripts/sync_moc_decisions.py --write`) et retire des textes de la PR les mentions qui suspendent leur
entrée en vigueur à la ratification ; l'owner fusionne la tête qui le contient.
Une PR qui applique le texte d'un amendement à une règle reste en brouillon jusque-là : fusionner une
règle amendée par un ADR `proposed` reproduit le constat C7.

Un changement de règle ou de policy qu'aucun ADR ne porte, parce qu'il ne change pas de décision (G1),
n'a pas de commit de ratification : la décision de l'owner se prouve par sa fusion de la tête
épinglée, tracée selon D4.

### D8 — Une passation nomme chaque notion séparément

Une passation, un mandat ou un rapport qui attribue une responsabilité nomme séparément le
département, le domaine d'ownership et son owner, l'agent du catalogue s'il y en a un, et la session
qui exécute (outil, compte, checkout, HEAD, date). Une session ne reçoit ni ownership ni place au
catalogue. Le tableau « fonction → ancien exécutant → nouvel exécutant → preuve → statut » et les
états « préparé / reçu / exécuté / intégré / observé » de l'issue #1947 en sont l'exemple de
référence ; cet ADR ne crée ni registre ni format nouveau.

## Amendement

À la ratification (D7), les textes suivants entrent en vigueur. Ils figurent dans la même PR.

- **[[rules-agent-exit-contract]] 1.1.0** : règle 1 réécrite selon D1 ; règle 3, manifeste et
  reformulation distinguent les corrections proposées des corrections appliquées sous mandat ; un
  `PASS` de dossier ne remplace pas le `final_status` ; la section « Distribution canonique »
  décrit les mécanismes réels (C2) et retire l'auto-fusion (D5) ; en-tête aligné sur la version.
  Le manifeste `99-meta/canon-hashes.json` est régénéré.
- **[[GOVERNANCE-HUMAN]] RULE-H5 et RULE-H6** : la revue humaine exigée devient la décision de
  l'owner (D2) ; la revue du diff est l'enregistrement DoD2 ; rien ne vaut autorisation de fusion (D3) ;
  trace de fusion (D4).
- **[[rules-engineering-definition-of-done]] 1.2.0**, DoD2 point 6 : D4 et D5.
- **[[rules-vault]] 3.2.0** : G1 (tableau et vérification) selon D6 ; G4 point 2 selon D3 et D4.
- **[[rules-governance-process]] 3.2.0** : G5 (tableau) selon D6.
- **ADR-101 D1** : la liste des ADR normatifs se lit selon D6.
- **ADR-120**, « Ce que cet ADR ne fait pas » : la mention « Il garde l'exception AP-self-merge » se
  lit selon D5.

Documents opérationnels alignés dans la même PR : tableau « Status Semantics » de [[MOC-Decisions]]
(sept statuts, renvoi au schéma) ; `CLAUDE.md` et `README.md` du vault (statuts normatifs) ;
`AGENTS.md` du vault, étape 10 (l'agent remet la commande de fusion au lieu de la lancer) ;
`_scripts/compute-canon-hashes.py` et `99-meta/canon-hashes.json` (version 1.1.0 de l'AEC).

## Ce que cet ADR ne fait pas

- Il ne change aucun statut d'ADR existant, ne renumérote rien et ne touche pas ADR-081 (C7).
- Il ne revient sur aucune ratification passée, y compris celles dont la fusion porte le compte
  `automecanik-agents[bot]` (C5).
- Il ne modifie, n'active ni ne désactive aucun workflow de fusion du monorepo (C9).
- Il ne modifie aucune note de connaissance ni aucun audit-trail : ceux qui décrivent des
  auto-fusions passées restent des documents historiques, sans autorité (ADR-101 D1).
- Il ne crée aucune identité, aucun bot, aucun label, aucun check requis, aucun registre, et n'en
  retire aucun.
- Il ne modifie ni la protection de branche, ni `.github/`, ni un workflow.
- Il ne change ni les niveaux A, B, C d'ADR-120, ni l'admission WIKI d'ADR-119, ni les niveaux d'ADR-013.
- Il n'autorise aucune fusion, publication, mise en production ni mutation de ressource partagée.

## Mise en œuvre

Après la ratification et la fusion :

1. La resynchronisation de l'AEC ouvre la PR `canon-sync/auto` du monorepo ; l'owner la fusionne
   (D5). Les copies des dépôts wiki et raw se mettent à jour par une PR ordinaire ; d'ici là, leur
   workflow `agent-exit-contract-hash.yml` signale l'écart. Les miroirs ne s'éditent pas à la main.
2. Monorepo et, pour la copie wiki, vault, par PR ordinaire : le skill `governance-vault-ops` décrit
   les statuts normatifs selon D6 ; le manifeste du skill `v5-guardian` (`workspaces/seo-batch`) et
   la mention « AEC v1.0.0 » de `workspaces/marketing/CLAUDE.md` suivent l'AEC 1.1.0. La copie
   `workspaces/wiki/.claude/canon-mirrors/agent-exit-contract.md` n'est déclarée ni dans le
   manifeste des consommateurs ni dans `agent-exit-contract-hash.yml` : son écart reste invisible
   tant qu'elle n'y est pas déclarée. Pour la déclarer, une PR du vault l'ajoute aux consommateurs de
   `_scripts/compute-canon-hashes.py`, qui génère le manifeste `99-meta/canon-hashes.json`, et une PR
   du monorepo l'ajoute à `agent-exit-contract-hash.yml`. Sinon, une PR du monorepo la retire.
3. Les PR ouvertes qui citent l'auto-fusion `canon-sync` ou AP-self-merge s'alignent sur D5.
4. T6 de [[rules-technical]] montre encore `gh pr merge` à lancer « après approbation explicite » ;
   D3 et D4 réservent cette commande à l'owner. Une PR du vault aligne T6 sur D4.

## Options considérées

### Option A — Statu quo — rejetée

L'AEC continue d'interdire ce que les mandats autorisent, et d'accorder une auto-fusion qu'aucune
règle de fusion n'admet ; deux ADR restent normatifs pour les scripts et non pour la doctrine.

### Option B — Corriger chaque document sans ADR — rejetée

Les points C1, C3, C4 et C6 changent ce qui fait foi ; G1 exige un ADR pour une décision.

### Option C — Déclarer `accepted-revised` non normatif — rejetée

Elle retirerait sans décision deux ADR (ADR-002 et ADR-009) que les contrôles traitent comme
actifs, et obligerait à modifier ces contrôles.

### Option D — Un amendement unique qui sépare les actes — retenue

Il aligne l'AEC, RULE-H5/H6, DoD2, G1, G4 et G5 sur une même distinction, sans nouvelle identité ni
nouveau mécanisme, et garde chaque validation spécifique dans l'ADR qui la porte. Il remplace, pour
les ADR à venir, la convention « la fusion par l'owner vaut ratification » d'ADR-114 à ADR-120 par
un commit de ratification distinct de la fusion (D7).

## Conséquences

### Positives

- Un agent sait ce que son mandat couvre et ce qu'il ne couvre pas.
- Aucune règle ni aucun ADR actif du vault n'accorde plus de fusion sans humain.
- La normativité d'un ADR se lit de la même façon dans la doctrine et dans les scripts.

### Négatives

- La ratification demande un commit de plus avant la fusion (D7).
- La trace de fusion reste déclarative : le compte ne prouve pas l'humain (D4), et cet ADR ne crée pas
  de mécanisme qui le prouverait. Un changement sans ADR n'a pas d'autre preuve de décision que cette
  trace (D7). Le commit de ratification a la même limite : son auteur est un compte et une clé de
  signature.

## Métriques

- Fusions exécutées par un agent : cible zéro.
- Règles canon qui citent un ADR non ratifié comme source d'un amendement en vigueur.

## Retour arrière

Un ADR qui amende celui-ci. Les documents modifiés se restaurent par un revert de la PR, suivi de la
régénération du manifeste des hashes canon.

## Revue planifiée

**Date** : 2027-02-01.

**Critères** : les métriques ci-dessus ; un cas où D1 a été invoqué pour une action hors mandat ; le
sort des constats C7 et C9.

## Références

- [[rules-agent-exit-contract]] · [[GOVERNANCE-HUMAN]] · [[rules-engineering-definition-of-done]] ·
  [[rules-vault]] · [[rules-governance-process]] · [[rules-deployment-workflow]] ·
  [[rules-ai-antipatterns]] · [[MOC-Decisions]]
- [[ADR-101-vault-decides-canon-authority|ADR-101]] ·
  [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] ·
  [[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]] ·
  [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] ·
  [[ADR-013-agent-lifecycle-governance|ADR-013]] · [[ADR-058-repository-control-plane|ADR-058]] ·
  [[ADR-081-doctrine-agility-amendments|ADR-081]]
- Vault : `.github/workflows/canon-publish.yml`, `_scripts/compute-canon-hashes.py`,
  `_scripts/governance_constants.py`, `_scripts/schemas/adr.schema.json`.
- Monorepo : `.github/workflows/canon-sync.yml`, `.github/workflows/agent-exit-contract-hash.yml`,
  `.github/workflows/dependabot-auto-merge.yml`, `.github/workflows/dependabot-claude-review.yml`,
  `CLAUDE.md` (invariant 7), `audit/automecanik-departments-map.md`,
  `.spec/00-canon/repository-registry/ownership.yaml` ; issue #1947.

---

*Proposé le : 2026-11-01*
*Accepté le : à la décision de l'owner (D7)*
*Dernière revue : 2026-11-01*
