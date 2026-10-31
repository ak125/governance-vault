---
id: ADR-120
title: "DoD2 : une preuve de revue liée au SHA de tête remplace l'approbation humaine GitHub — amende rules-engineering-definition-of-done (v1.1.0)"
status: accepted
date: "2026-10-31"
decision_date: "2026-10-31"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: []
related_adr: ["ADR-053", "ADR-058", "ADR-101", "ADR-102", "ADR-104", "ADR-119"]
related_rules: ["DoD2", "G5", "G6"]
related_incidents: []
version: "1.0.0"
---

# ADR-120 : DoD2 — une preuve de revue liée au SHA de tête remplace l'approbation humaine GitHub

- **Statut** : Accepted (2026-10-31). La fusion par l'owner vaut ratification. Rédigé par un agent sur
  le mandat de l'owner du 2026-10-31 ; rien n'est normatif avant la fusion
  ([[ADR-101-vault-decides-canon-authority|ADR-101]], G4.2 de
  [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]]).
- **Modifie** la règle [[rules-engineering-definition-of-done]] (v1.0.0 → v1.1.0) sur les seuls
  passages listés en §Amendement : section DoD2, point 2 de « Application aux agents IA », ligne DoD2
  du gabarit d'auto-évaluation, « Contrôle au niveau revue » et « Enforcement automatique ». DoD1 et
  DoD3 à DoD9, ainsi que l'escape hatch, restent inchangés.
- **Ne modifie aucun ADR**, ni la gate `pr-dod-gate` du monorepo (§Ce que cet ADR ne fait pas).
- **Méthode** : constats vérifiés le 2026-10-31, en lecture seule, sur `main` du vault au commit
  `1388726` et sur `main` du monorepo au commit `2a49166e2` : `scripts/ci/pr-dod-gate.mjs`,
  `.github/workflows/pr-dod-gate.yml`, `.github/PULL_REQUEST_TEMPLATE.md`, `audit/registry/` ; auteur,
  assignees, reviews et checks requis des PR brouillons #1935 et #1936 du monorepo et de la PR #388 du
  vault ; identité du jeton `gh` des sessions CLI.

## Contexte

### DoD2 exige une approbation que le mandat a remplacée

DoD2 v1.0.0 exige « au moins un reviewer humain confirmé » et, en test de discrimination,
« ≥1 review approval humain ». Les identités GitHub observées le 2026-10-31 ne laissent qu'une
manière de la satisfaire :

- les sessions CLI agissent sous l'application GitHub `automecanik-agents[bot]`, autrice de #1936 du
  monorepo et de la PR #388 du vault ; une approbation de sa part serait celle d'un agent, et la
  v1.0.0 ne compte pas les bots, sauf bot documenté comme reviewer canonique dans `canonical.json`,
  qui n'en documente aucun ;
- la session Desktop agit sous le compte de l'owner, auteur de #1935 ; GitHub refuse qu'un compte
  approuve sa propre PR ;
- l'owner peut approuver une PR de l'application, mais c'est alors une revue technique humaine PR par
  PR. Le mandat de l'owner du 2026-10-31 la remplace par une auto-review avec preuves et corrections,
  et exclut de lui renvoyer une revue technique de PR.

Le workflow du monorepo exécute la gate dans le job « DoD self-evaluation present », qui figure parmi
les checks requis des PR #1935 et #1936. DoD2 y reste consultative (`DOD_ADVISORY_ITEMS: DoD2`) ; le
commentaire du workflow motive ce choix « until agents get an identity distinct from the owner » et
qualifie encore la gate de « Not yet a required check ». Ces deux mentions sont dépassées : les
sessions CLI ont une identité distincte, et le job est requis.

Conséquence observée : les PR portent une case « DoD2 — revue humaine attendue » qu'aucun acteur ne
ferme. Cette attente n'apporte aucun contrôle : aucune revue n'est faite à sa place, et la fusion
humaine reste la seule décision réelle. Une approbation donnée sur un SHA ancien ne dirait d'ailleurs
rien du code fusionné : la règle ne lie l'approbation à aucune tête.

### Deux revues distinctes

[[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] a remplacé la relecture humaine des
**fiches WIKI** par une auto-review de sens. La revue du **code d'une PR** relève de DoD2. Ce sont deux
périmètres : le premier admet un contenu dans le WIKI, le second admet un diff dans une branche. Cet
ADR ne traite que le second.

### Une référence d'ownership absente

DoD2 renvoie à `audit/registry/planning.json` (champ `owners`) pour l'owner du domaine. Ce fichier est
absent de `main` du monorepo. L'ownership des chemins est porté par l'overlay L2 `ownership.yaml`
([[ADR-058-repository-control-plane|ADR-058]]), que le test de discrimination 3 lit déjà.

## Principe directeur

La revue d'une PR est une preuve, pas un état GitHub : elle nomme le SHA qu'elle a lu, ce qu'elle a
trouvé et ce qui en a été fait. Un owner humain reste responsable, la fusion reste humaine, les zones
STOP gardent leur accord nominatif.

## Décisions

### D1 — Un owner responsable, la fusion humaine

La PR a un `assignee` humain, l'owner responsable. Le domaine de chaque chemin modifié a un owner non
`__unassigned__` dans `ownership.yaml`. Un agent ne fusionne pas ; la fusion reste un acte humain
(G4.2 d'ADR-102 pour le vault). DoD2 satisfaite ne vaut ni fusion, ni publication, ni autorisation de
mutation PROD.

### D2 — Une preuve de revue à la place de l'approbation

L'approbation GitHub n'est plus exigée. DoD2 exige un **enregistrement de revue** dans le corps de la
PR, ou dans un commentaire que le corps cite. Il contient :

- le SHA de tête revu (40 caractères) et le SHA de base (merge-base) ;
- la procédure suivie et qui l'a exécutée (session, agent ou compte) ;
- le périmètre lu : le diff attribuable, fichier par fichier, et ce qui est exclu ;
- chaque constat avec son sort : **corrigé** (commit et test de non-régression, ou raison pour laquelle
  le défaut n'est pas testable), **réfuté** (preuve citée : code, test ou sortie), **reporté** (motif et
  suivi) ;
- les preuves exécutées et leurs résultats ; les preuves reprises sans relance, avec la raison
  (entrées, dépendances, configuration et données inchangées) ;
- les limites : ce que la revue ne couvre pas.

Un constat confirmé dans le diff de la PR qui touche la correction, la sécurité ou un contrat bloque
DoD2 tant qu'il n'est ni corrigé ni réfuté. Un PASS déclaré, un score de confiance ou une case cochée ne
remplacent pas cet enregistrement.

Une revue humaine reste possible ; elle produit le même enregistrement.

### D3 — Niveau de revue selon le risque

| Niveau | Périmètre du diff | Revue exigée |
|---|---|---|
| A | documentation, prose, données d'audit, projections générées par leur script ; aucun code exécuté | auto-review par l'auteur, sur la tête |
| B | code, tests, scripts, configuration, CI ou gardes, hors zones STOP | niveau A, plus une revue indépendante automatisée sur un SHA figé |
| C | zones STOP (liste ci-dessous) | niveau B, plus l'accord nominatif de l'owner du domaine, consigné sur la PR et nommant le SHA revu, avant la fusion |

Le niveau est celui du fichier le plus risqué du diff.

**Revue indépendante** : faite par une session ou un agent distinct de l'auteur, sans le contexte de sa
conversation, qui n'écrit pas sur la branche pendant la revue. Elle porte sur un SHA figé et rend ses
constats ; l'auteur les traite (D2). Elle ne devient pas une seconde mission d'intégration. Une revue
relancée dans la session de l'auteur n'est pas indépendante.

**Zones STOP** : paiement (passerelles et leurs clés, [[rules-technical]] T5) ; prix et stock servis ;
panier et commande ; RLS ([[ADR-021-database-rls-hardening-zero-trust|ADR-021]]) ; opération destructive
en base et migration irréversible ([[rules-engineering-quality]]) ; SEO indexé (URL, title, meta, H1,
suppression de page) ; déploiement PROD ([[rules-deployment-workflow]]).

### D4 — La preuve vaut pour un SHA

L'enregistrement vaut pour le SHA de tête qu'il nomme. Un push qui change la tête le rend périmé. Il
n'est reporté sur la nouvelle tête que par un nouvel enregistrement qui nomme ce SHA et montre que le
diff attribuable est identique : diff de la PR contre la merge-base, hors projections régénérées par
leur script officiel (fusion de `main` sans conflit sur les fichiers de la PR, `resync`). Sinon, la
partie modifiée est revue au niveau qu'elle exige.

### D5 — Aucun contournement

DoD2 ne se satisfait pas par une nouvelle identité GitHub, un bot, une fausse approbation, un label ou
une case cochée sans enregistrement. L'escape hatch `dod-skip-justified` reste régi par ses propres
exigences ; un skip n'est pas une revue.

## Amendement

Dans [[rules-engineering-definition-of-done]], version 1.1.0 :

- **DoD2** : titre, paragraphe OBLIGATOIRE (owner du domaine lu dans `ownership.yaml`), test de
  discrimination, anti-patterns bloquants, evidence requise et raison réécrits selon D1 à D5 ;
- **Application aux agents IA**, point 2 : DoD2 se lit « assignee, owner du domaine et enregistrement
  de revue sur la tête » ;
- **Gabarit d'auto-évaluation** : la ligne DoD2 garde son identifiant en tête (lu par la gate) et
  décrit l'enregistrement ;
- **Contrôle au niveau revue** : un DoD2 coché sans enregistrement, ou dont l'enregistrement nomme un
  autre SHA que la tête, est refusé ;
- **Enforcement automatique**, point 2 : la gate, exécutée dans un check requis, évalue encore DoD2
  sur l'état GitHub, en consultatif ; ce point le constate.

## Ce que cet ADR ne fait pas

- Il ne modifie pas `pr-dod-gate.mjs` ni son workflow. La gate continue de compter les approbations
  pour DoD2, en consultatif, et le job qui l'exécute reste requis pour les autres items. Cet écart
  entre décision et code est un constat, à résoudre par une PR du monorepo (ADR-101 D3), par exemple
  une gate qui vérifie que l'enregistrement nomme la tête.
- Il ne crée aucune identité, aucun bot, aucun check requis, et n'en retire aucun.
- Il ne change ni la fusion humaine, ni la publication, ni le déploiement PROD, ni l'accord nominatif
  des zones STOP.
- Il ne touche pas l'escape hatch ni DoD1 et DoD3 à DoD9.
- Il ne change pas l'admission des fiches WIKI (ADR-119).

## Mise en œuvre

Après la fusion, dans le monorepo, par PR de code ordinaire :

1. `.github/PULL_REQUEST_TEMPLATE.md` : ligne DoD2 et commentaire qui citent « ≥ 1 approbation
   humaine ».
2. `scripts/ci/pr-dod-gate.mjs` et `pr-dod-gate.yml` : décider si la gate vérifie l'enregistrement
   (SHA de tête présent) ; tant que rien ne change, DoD2 reste consultative.
3. Les PR ouvertes qui portent « DoD2 — revue humaine attendue » remplacent cette attente par
   l'enregistrement de D2.

## Options considérées

### Option A — Statu quo — rejetée

DoD2 continue d'exiger, PR par PR, une revue technique humaine que l'owner a remplacée ; la case reste
une attente que personne ne ferme et aucune revue n'est exigée à sa place.

### Option B — Une nouvelle identité GitHub, ou l'application des agents comme approbatrice — rejetée

Créer un compte pour approuver, ou faire approuver par `automecanik-agents[bot]` les PR de l'owner,
contourne le contrôle au lieu de l'exercer : l'approbation dirait qu'une revue a eu lieu sans en
porter la preuve, et elle ne lierait pas la revue au SHA lu.

### Option C — `dod-skip-justified` sur chaque PR — rejetée

Le skip exige deux approbateurs humains et un événement de gouvernance par PR : il remplace la revue
par une exception et rend celle-ci permanente.

### Option D — Auto-review seule, quel que soit le risque — rejetée

Elle suffit pour une PR de documentation ; pour du code exécuté, l'auteur ne peut pas être son seul
contrôle.

### Option E — Preuve de revue liée au SHA, graduée selon le risque — retenue

Elle remplace une attente que personne ne ferme par une preuve vérifiable, garde l'owner, la fusion humaine et les
zones STOP, et rend périmée toute preuve qui ne porte pas sur le code fusionné.

## Conséquences

### Positives

- DoD2 devient satisfiable et vérifiable sur pièce.
- Une revue ne couvre plus un code qu'elle n'a pas lu (D4).
- Les PR ne portent plus d'attente de revue humaine fictive.

### Négatives

- Le niveau B demande une revue indépendante par PR de code.
- Tant que la gate n'est pas adaptée, la conformité à D2 et D4 se contrôle à la lecture.
- Un enregistrement peut être faux ; seule la relecture de ses preuves le détecte.

## Métriques

- Part des PR fusionnées dont l'enregistrement DoD2 nomme la tête fusionnée.
- Défauts trouvés après fusion dans un diff revu, par niveau.

## Retour arrière

Revenir à DoD2 v1.0.0 par un ADR qui amende celui-ci. Aucune donnée ni aucun code n'est à défaire.

## Revue planifiée

**Date** : 2027-01-31.

**Critères** :

- les métriques ci-dessus ;
- l'adaptation de la gate (§Mise en œuvre, point 2) ;
- un défaut en PROD issu d'un diff revu de niveau B ou C.

## Références

- [[rules-engineering-definition-of-done]] ·
  [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] ·
  [[ADR-101-vault-decides-canon-authority|ADR-101]] ·
  [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] ·
  [[ADR-058-repository-control-plane|ADR-058]] ·
  [[ADR-053-planning-live-system|ADR-053]] ·
  [[ADR-104-planning-live-writer-retired|ADR-104]]
- Monorepo : `scripts/ci/pr-dod-gate.mjs`, `.github/workflows/pr-dod-gate.yml`,
  `.github/PULL_REQUEST_TEMPLATE.md`.

---

*Proposé le : 2026-10-31*
*Accepté le : à la fusion par l'owner*
*Dernière revue : 2026-10-31*
