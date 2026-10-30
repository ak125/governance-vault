---
id: ADR-119
title: "Auto-review de sens à la place de toute relecture humaine des fiches WIKI, familles de sécurité comprises : amende ADR-031, ADR-083, ADR-088, ADR-091, ADR-093, ADR-096 et ADR-114"
status: accepted
date: "2026-10-30"
decision_date: "2026-10-30"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-031", "ADR-083", "ADR-088", "ADR-091", "ADR-093", "ADR-096", "ADR-114"]
extends: []
related_adr: ["ADR-031", "ADR-033", "ADR-046", "ADR-083", "ADR-088", "ADR-089", "ADR-091", "ADR-093", "ADR-096", "ADR-102", "ADR-112", "ADR-114", "ADR-115", "ADR-116", "ADR-117"]
related_rules: ["G1", "G6", "Q1", "Q2", "AP-11"]
related_incidents: []
version: "1.0.0"
---

# ADR-119 : Auto-review de sens à la place de la relecture humaine des fiches WIKI, sécurité comprise

- **Statut** : Accepted (2026-10-30). La fusion par l'owner vaut ratification.
- **Amende** :
  - [[ADR-091-wiki-score-recalibration|ADR-091]] : Décision §4, troisième point des Conséquences,
    Rollout & rollback ;
  - [[ADR-114-wiki-safety-auto-gate|ADR-114]] : D2, D3, D5, D6, dernier point des Conséquences
    négatives, Métriques, Retour arrière et Revue planifiée ;
  - [[ADR-083-tiered-wiki-promotion|ADR-083]] : Tension à résoudre, TIER B, Invariant AVANT / APRÈS
    et Conséquences ;
  - [[ADR-093-auto-review-earn-gate|ADR-093]] : Décision, Le gate EARN, §Sécurité (point 1),
    §Humain = exception, §Ce qui reste, Risque résiduel (point 4), Alternatives rejetées,
    Garde-fous, Plan de mise en œuvre et Angles morts ;
  - [[ADR-096-governed-automatic-source-discovery|ADR-096]] : §D5 et dernier point de §D6 ;
  - [[ADR-031-four-layer-content-architecture|ADR-031]] : deuxième phrase du principe directeur,
    schéma de l'architecture cible et point « Propose-before-write » de l'Héritage ADR-022 ;
  - [[ADR-088-promotion-gate-substance-scoring|ADR-088]] : plafond de `no_disputed_claims: false`.

  Chaque amendement est décrit en §Amendements. Le reste de ces ADR reste en vigueur.
- **Ne modifie ni ADR-033, ni ADR-112, ni ADR-115, ni ADR-116, ni ADR-117.** Le flip
  `diagnostic_safe`, la relecture des relations et celle des règles de sécurité du diagnostic ne sont
  pas des relectures de fiche. Elles restent régies par leurs ADR (§Ce que cet ADR ne fait pas).
- **Pourquoi un ADR séparé** : ADR-114 a remplacé l'approbation humaine d'une fiche sécurité par une
  preuve. Il a gardé une relecture humaine a posteriori de chaque fiche promue (Métriques) et laissé
  intact le texte d'ADR-091 selon lequel aucune pièce de sécurité n'est publiée sans revue humaine. Il
  a aussi renvoyé à « un ADR distinct » l'écart entre les ADR et la voie humaine supprimée pour les
  fiches non sécurité. Le 2026-10-30, l'owner demande de supprimer la relecture humaine et de la
  remplacer par une auto-review, familles de sécurité comprises. Cet ADR le décide et régularise cet
  écart.
- **Méthode** : constats vérifiés le 2026-10-30, en lecture seule :
  - `main` du WIKI au commit `edae4a9` : `_scripts/promotion_decision.py`,
    `_scripts/build_exports_content.py`, `_scripts/gates/contradiction_gate.py`,
    `_meta/quality-gates.md` §1, §6, §7 et §10, historique de `wiki/gamme/plaquette-de-frein.md` ;
  - PR WIKI #120, son commentaire de relecture a posteriori du 2026-10-21, et PR WIKI #124 ;
  - pin du sous-module WIKI sur `main` du monorepo ;
  - `main` du vault au commit `9cd82dc`.

## Contexte

### Ce qui reste de la relecture humaine dans les ADR

| ADR | Texte en vigueur |
|---|---|
| ADR-091 | Conséquences : « Aucune pièce de sécurité n'est publiée sans revue humaine (principe « no auto-approval ») ». ADR-114 a amendé §4, pas ce point. |
| ADR-114 | Métriques : relecture a posteriori de chaque fiche sécurité promue pendant 30 jours. Conséquences négatives : « La première fiche promue doit être relue après coup ». Retour arrière : une fiche promue « se retire par une PR WIKI revue ». |
| ADR-083 | TIER B : « Reste `in_review` jusqu'à approbation humaine ». Invariant : humain sur « le résidu risqué ». Conséquences : « tout safety/contradiction → humain ». |
| ADR-093 | « Sinon → humain » ; §Humain = exception, points 2 à 9 ; « Le flip `exportable.seo` reste 100 % humain ». |
| ADR-096 | §D5 : « human-required » ; « le flip `exportable.seo` reste humain ». §D6 : « Humain pour […] contradictions majeures ». |
| ADR-031 | « validée humainement » ; la promotion « requiert validation humaine explicite ». |
| ADR-088 | « `no_disputed_claims:false` plafonne au TIER B (revue humaine) ». |

### Le WIKI n'a plus de voie humaine depuis le 2026-09-12

`_meta/quality-gates.md` le dit en toutes lettres :

- §1 : « Aucune étape de validation humaine n'est obligatoire pour une fiche WIKI. »
- §6 : une revue humaine « peut contribuer des informations, mais n'est ni un passage obligatoire ni
  un moyen de contourner une preuve manquante ».
- §7 : la validation humaine systématique est supprimée par décision de l'owner du 2026-09-12 (WIKI
  #83). Le motif historique `SAFETY_HUMAN_REVIEW` est « un blocage technique, pas une tâche
  humaine ».

Les textes du tableau décrivent donc une étape qui n'existe plus. Une fiche bloquée n'attend personne :
elle attend une preuve.

### Ce que la relecture du 2026-10-21 a montré

ADR-114 a été accepté le 2026-10-15, et la PR WIKI #115 a levé le verrou le même jour. La PR WIKI
#120 a finalisé la promotion automatique le 2026-10-21, et la promotion quotidienne a écrit
`wiki/gamme/plaquette-de-frein.md` (`35d057b`).

La relecture a posteriori exigée par ADR-114 (Métriques) a été consignée le même jour dans un
commentaire de #120. Un agent l'a faite, pas un humain. Elle procède ainsi :

- la fiche est lue au commit `88f9f88`, identique à `main` au 2026-10-30, et comparée à ses six
  captures RAW, dont les identifiants concordent ;
- 196 affirmations sont relevées, en 8 lots ;
- chaque écart signalé est soumis à trois réfutateurs indépendants.

Résultat : 29 écarts confirmés et 2 réfutés. Les confirmés comptent 1 écart de sécurité, 12 de sens
(dont 2 doublons), 16 de formulation et 0 de valeur, la fiche ne publiant aucun chiffre.

L'écart de sécurité est la réponse à la question 5 de la FAQ. Elle attribue un freinage moins
efficace après remplacement au seul rodage. Deux sources citées par la fiche
(`oem:bremboparts_remplacement_kit`, `oem:zf_installation_plaquettes`) placent les premiers freinages
après le pompage de la pédale jusqu'à une course stable, et citent un montage incorrect parmi les
causes d'une performance réduite. Un défaut réel pourrait ainsi passer pour un rodage normal.

La PR WIKI #124 a refermé la gate le même jour (constante vide), comme l'exige ADR-114 (Revue
planifiée) devant un défaut de sens.

Trois enseignements :

- la Safety Auto-Gate ne voit pas le sens d'une affirmation sans chiffre. ADR-114 le disait ;
- une relecture outillée, avec extraction exhaustive des affirmations et réfutation indépendante, a vu
  l'écart de sécurité et les écarts de sens ;
- cette relecture peut avoir lieu avant la promotion au lieu d'après.

### Où en est `plaquette-de-frein`

- La fiche est toujours dans `wiki/gamme/` sur `main` du WIKI, dépôt public. Son contenu est celui que
  la relecture a lu.
- Le commentaire de #120 annonce sa correction « par une PR WIKI revue par un humain ». Cette voie
  n'existe pas.
- Aucun consommateur ne la sert au 2026-10-30. Le sous-module WIKI du monorepo est épinglé à
  `8801773`, qui ne contient pas la fiche.

### Un constat : `no_disputed_claims` hors sécurité

- Pour une fiche sécurité, le décideur exige `no_disputed_claims: true` (ADR-114 D3).
- Pour une fiche non sécurité, il ne lit pas ce champ, et `contradiction_gate.py` ne contrôle que les
  relations diagnostic et les symptômes legacy.
- Seul l'export de contenu (`build_exports_content.py`) écarte une fiche dont `no_disputed_claims`
  n'est pas `true`.

ADR-088 voulait qu'une telle fiche soit plafonnée au TIER B. La divergence est antérieure à cet ADR.
Elle est signalée ici et se résout par une PR WIKI (Mise en œuvre, point 5).

## Principe directeur

> La preuve décide, et la relecture du sens fait partie de la preuve. Une machine relit chaque fiche
> avant sa promotion. Ce qu'elle ne peut pas écarter en citant une source bloque la fiche. Un humain
> peut apporter une preuve, restreindre une fiche ou la retirer. Il ne l'approuve jamais et
> n'assouplit jamais un contrôle.

## Décisions

### D1 — Aucune relecture humaine n'est une condition de promotion

- Aucune relecture, approbation ni vérification par sondage (`HUMAN_SPOT_CHECK`) faite par un humain
  n'est une condition de promotion d'une fiche WIKI, famille de sécurité comprise.
- Un humain peut contribuer : capturer une source, cataloguer son type, valider une plage chiffrée
  (ADR-114 D4) ou signaler un défaut.
- Un humain peut restreindre ou retirer : passer `exportable.seo` à `false` ou rétrograder une fiche
  par §10.
- Un humain n'approuve jamais une fiche, ne lève jamais un motif de blocage et ne passe jamais
  `exportable.seo` à `true`.
- La fusion d'une PR par l'owner porte sur du code, une règle ou une donnée de référence. Ce n'est pas
  une relecture du contenu d'une fiche.
- Un défaut signalé par un humain se traite par le retrait de la fiche (§10) ou par une nouvelle
  capture. La fiche n'attend jamais une réponse humaine.

### D2 — Protocole de l'auto-review de sens

L'auto-review vérifie que chaque affirmation de la fiche dit ce que disent ses captures citées, et
qu'elle n'omet rien de ce qu'elles rattachent au même sujet.

- **Périmètre** : le texte publié de la fiche, tel que la promotion l'écrirait. C'est le corps et
  toutes les chaînes du frontmatter, soit la fiche telle que la définit ADR-114 D4. Les documents
  exportés projettent ces champs. Le texte du catalogue des sources, que les exports reprennent aussi,
  n'est pas une affirmation de la fiche : il reste contrôlé par ADR-114 D4 pour les valeurs.
- **Entrées** : ce texte et les captures RAW que la fiche cite, rien d'autre.
  - Le relecteur ne voit ni la proposition de travail ni le raisonnement du producteur.
  - Il n'est pas le producteur.
  - Lire une capture pour contrôler une fiche n'est pas la lecture de RAW par un consommateur
    qu'interdit ADR-031 : c'est la lecture que fait déjà le contrôle de provenance.
- **Extraction** : toutes les affirmations du texte, segment par segment. Une omission compte comme une
  affirmation. Il y a omission quand la fiche laisse de côté une condition, une précaution ou une cause
  qu'une capture citée rattache au même sujet.
- **Détection** : au moins deux passes indépendantes, dans des contextes séparés et sans partage de
  sortie. Un écart candidat relevé par une seule passe suffit.
- **Réfutation** : chaque candidat est soumis à au moins trois réfutateurs indépendants.
  - Il est écarté seulement si tous le réfutent en citant un passage d'une capture.
  - Sinon il est confirmé.
- **Connaissance** :
  - Pas de RAG (ADR-031, ADR-046).
  - La connaissance propre d'un modèle peut lever un candidat, jamais l'écarter.
  - Un candidat qu'aucune capture ne permet de trancher reste confirmé. La fiche reste bloquée jusqu'à
    ce qu'une source captée le tranche.
- **Affirmation non portée** : une affirmation qu'aucune capture citée ne porte est un écart. Sa classe
  suit sa portée.
- **Classes** :
  - valeur : chiffre, unité, intervalle ou quantité. Cette classe complète ADR-114 D4 sans le
    remplacer ;
  - sécurité : écart qui peut conduire à une action ou à une omission dangereuse ;
  - sens : affirmation contredite, déformée ou sur-généralisée, ou divergence entre sources non
    déclarée ;
  - formulation : écart sans effet sur le sens. Il est consigné et ne bloque pas.
- **Verdict** :
  - PASS si la relecture est complète et ne confirme aucun écart de valeur, de sécurité ou de sens ;
  - FAIL dès qu'un tel écart est confirmé, même si la relecture est incomplète ;
  - INCOMPLETE ou ERROR sinon. Ce ne sont pas des verdicts : la relecture se relance.
- **Complétude** : le décideur la recalcule, le relecteur ne la déclare pas.
  - Une fonction WIKI déterministe découpe le texte publié en segments.
  - Chaque segment doit figurer dans l'artefact avec son empreinte et ses affirmations, ou avec la
    mention explicite qu'il n'en porte aucune.

**Artefact** :

- Il est versionné dans le WIKI.
- Sa clé réunit l'empreinte sha256 du texte publié, les identifiants des captures citées et la
  révision du protocole. Il consigne aussi les identifiants des modèles.
- Il n'écrit jamais la fiche et ne l'approuve pas.
- Un FAIL sur une clé n'est jamais remplacé par un PASS sur la même clé, quel que soit le modèle. Un
  nouveau texte, de nouvelles captures ou une nouvelle révision du protocole font une nouvelle clé.
- La PR WIKI qui met en œuvre la condition (D3) fixe le chemin, le schéma et l'exécuteur, sans
  constante métier inventée.

**Révision du protocole** :

- Durcir le protocole se fait par PR WIKI : passes ou réfutateurs plus nombreux, classe bloquante
  ajoutée.
- L'assouplir exige un ADR : passes ou réfutateurs moins nombreux, réfutation non unanime, classe
  bloquante retirée.

### D3 — Condition `semantic_auto_review_pass`

- La condition s'ajoute au tableau d'ADR-114 D3 pour toute fiche sécurité.
  - Preuve exigée : un artefact D2 de verdict PASS dont la clé correspond à la fiche décidée (texte
    publié, captures citées, révision courante du protocole).
  - Aucun FAIL ne doit exister sur la même clé.
- Elle est fail-closed : un artefact absent, périmé, incomplet, en erreur ou illisible rend la
  condition fausse.
- Elle est nécessaire, jamais suffisante, et ne peut que bloquer.
  - Cela précise ADR-114 D2 : un artefact produit par un modèle et lu comme une condition bloquante
    n'est pas un décideur.
  - `promotion_decision.py` reste le seul décideur.
- Pour une fiche non sécurité, la condition est calculée et tracée en report-only.
  - La rendre bloquante se fait par PR WIKI, parce que cela durcit le contrôle.
  - La retirer des fiches sécurité exige un ADR.
- `no_disputed_claims` reste une condition déclarative. L'auto-review la complète : une divergence non
  déclarée entre sources est un écart de sens.

### D4 — Levée du verrou

- La Safety Auto-Gate se rouvre quand une PR WIKI inscrit `SAFETY_AUTO_APPROVAL_ADR = "ADR-119"` dans
  `promotion_decision.py`. Toute décision déjà rendue devient `STALE_DECISION`.
- Cette PR n'est recevable que si les préconditions suivantes sont fusionnées dans le WIKI, chacune
  prouvée par un test ou par un artefact versionné :
  - (a) à (c) : les préconditions d'ADR-114 D5 restent vraies ;
  - (d) la condition de D3 est câblée dans le décideur pour toute fiche sécurité, quelle que soit la
    valeur de la constante. Des tests couvrent l'artefact absent, périmé, incomplet et en erreur, et
    le FAIL non remplaçable ;
  - (e) étalonnage : deux relectures complètes et indépendantes de `plaquette-de-frein` au commit
    `88f9f88` rendent chacune FAIL et confirment l'écart de sécurité de la question 5 de la FAQ. Les
    écarts confirmés le 2026-10-21 servent de jeu de référence. La part retrouvée est consignée, sans
    seuil ;
  - (f) chaque fiche sécurité déjà au canon a un artefact D2. Une fiche en FAIL est retirée par §10
    avant la levée. Au 2026-10-30, `plaquette-de-frein` est la seule.
- Aucune variable d'environnement ni aucune option CLI ne lève le verrou (ADR-114 D5, maintenu).

### D5 — Après une promotion

- L'auto-review préalable de D2 remplace la relecture humaine a posteriori d'ADR-114 (Métriques). La
  fenêtre de relecture ouverte par la levée du 2026-10-15, jusqu'au 2026-11-14, n'a plus d'objet.
- Pendant les 30 jours qui suivent la levée, l'auto-review est relancée sur chaque fiche sécurité
  promue. Un FAIL compte comme un défaut.
- Un défaut de valeur, de sécurité ou de sens constaté sur une fiche promue, par l'auto-review ou par
  un signalement, referme la gate avant toute analyse (ADR-114, Revue planifiée, maintenu). La fiche
  est retirée par §10.
- La correction d'une fiche sécurité promue passe par son retrait (§10), puis par une nouvelle
  promotion par le décideur, avec une nouvelle auto-review. La PR de retrait retire aussi les exports
  qui dérivent de la fiche, sans laisser d'export orphelin.

### D6 — `exportable.seo`

- `exportable.seo` passe à `true` seulement par une promotion à la porte TIER A d'ADR-083. Pour une
  fiche sécurité, c'est ADR-114 D6.
- Hors de cette porte, il ne change que vers `false` (restriction ou retrait), par une PR WIKI.
- Cette règle vaut pour toutes les fiches. Elle remplace « flip `exportable.seo` 100 % humain »
  (ADR-093, ADR-096). Une révision ne change toujours pas `exportable` (ADR-117 D3).

### D7 — Ce qui reste inchangé

- La validation d'une plage chiffrée reste un acte humain unique par famille et par grandeur (ADR-114
  D4). C'est une donnée de référence, pas la relecture d'une fiche.
- L'autorité d'une source inconnue reste humaine (ADR-096 §D5). C'est la validation d'une source, pas
  celle d'une fiche.
- Le flip `diagnostic_safe` et `reviewed` (ADR-033), la relecture des règles de sécurité du
  diagnostic (ADR-112 D5) et celle des relations (ADR-115, ADR-116) restent régis par leurs ADR.
- La révision en place d'ADR-117 reste fermée aux fiches sécurité.
- La barre non sécurité ne change pas, hors condition D3 en report-only.
- Le RAG n'a aucune autorité de contenu ni de scoring (ADR-031, ADR-046).
- Un seul décideur (ADR-114 D2). Les fusions restent réservées à l'owner (ADR-102).

### D8 — Observabilité

- La trace de chaque décision porte, pour la condition D3 :
  - la clé de l'artefact et son verdict ;
  - les écarts confirmés par classe et le nombre de candidats écartés ;
  - la part des écarts confirmés qu'aucune capture ne tranche.
- La trace existante du décideur suffit. Cet ADR ne crée aucun canal.

## Amendements

### ADR-091 (recalibrage du score)

- **Décision §4**, seconde phrase, telle qu'amendée par ADR-114 : les pièces sécurité sont promues
  selon ADR-114, avec la condition d'auto-review d'ADR-119 D3. Elles ne passent par aucune relecture
  humaine.
- **Conséquences, troisième point** : « Aucune pièce de sécurité n'est publiée sans revue humaine »
  est remplacé par : « Aucune pièce de sécurité n'est publiée sans preuve vérifiée et sans auto-review
  de sens PASS (ADR-114, ADR-119). »
- **Rollout & rollback** : remettre le seuil à 1.01 bloque toute promotion automatique. Aucune voie
  humaine ne prend le relais.
- Le reste d'ADR-091 est maintenu.

### ADR-114 (Safety Auto-Gate)

- **D2** : précisé par ADR-119 D3. Un artefact d'auto-review lu comme condition bloquante n'est pas
  un second décideur.
- **D3** : la condition `semantic_auto_review_pass` (ADR-119 D3) s'ajoute au tableau.
- **D5** : la levée inscrit `"ADR-119"`, avec les préconditions d'ADR-119 D4.
- **D6** : « Hors de cette porte, `exportable.seo` ne change que par une PR revue » se lit selon
  ADR-119 D6 : hors de cette porte, seulement vers `false`.
- **Conséquences négatives, dernier point** : « La première fiche promue doit être relue après coup »
  est remplacé par l'auto-review préalable (ADR-119 D2) et sa relance (ADR-119 D5).
- **Métriques, troisième point** : remplacé par les métriques d'ADR-119.
- **Retour arrière, deuxième point** : « une PR WIKI revue » se lit « une PR WIKI de retrait (§10),
  fusionnée par l'owner », sans relecture du contenu (ADR-119 D1, D5).
- **Revue planifiée** : « les relectures a posteriori » se lit « les relances d'auto-review » (ADR-119
  D5). La règle « refermer la gate avant toute analyse » est maintenue.
- Le reste d'ADR-114 est maintenu.

### ADR-083 (promotion tiered)

- **Tension à résoudre** : le contrôle du risque est maintenu. Il passe de la validation humaine à
  la preuve et à l'auto-review de sens (ADR-114, ADR-119). Rien n'est publié sans contrôle.
- **TIER B** : le résidu reste bloqué par ses motifs et se réévalue automatiquement une fois la preuve
  corrigée. Il n'attend aucune approbation humaine. `reviewed_by: "<email>"` n'est plus une voie de
  promotion.
- **Invariant AVANT / APRÈS** :
  - ligne « Autorité `approved` » : la porte TIER A seule ;
  - ligne « Humain » : contributions et retraits seulement (ADR-119 D1).
- **Conséquences** :
  - « tout safety/contradiction → humain » se lit « tout safety/contradiction → bloqué par ses motifs,
    ou porte de sécurité » ;
  - le rollback à 1.01 bloque toute promotion automatique, sans voie humaine de relais.
- Le reste d'ADR-083 est maintenu.

### ADR-093 (auto-review à barre de preuve)

- **Décision et Le gate EARN** : « TIER B → humain » et « Sinon → humain » se lisent « bloqué par
  ses motifs, réévalué automatiquement ».
- **§Sécurité, point 1**, tel qu'amendé par ADR-114 : l'étiquette `HUMAN_SPOT_CHECK` du script
  monorepo reste sans autorité (ADR-114 D2) et ne sollicite aucun humain (ADR-119 D1).
- **§Humain = exception** : les points 2 à 9 ne sollicitent plus un humain.
  - Les points 2 à 8 bloquent la fiche par leurs motifs.
  - Le point 9 suit ADR-119 D6.
  - Le point 1 l'était déjà par ADR-114.
- **§Ce qui reste** : « Le flip `exportable.seo` reste 100 % humain » est remplacé par ADR-119 D6.
  L'activation de flag et la ratification restent des actes de l'owner sur la règle, pas sur une
  fiche.
- **Risque résiduel, point 4** : la vérification sémantique est désormais l'auto-review d'ADR-119 D2,
  qui compare les affirmations aux captures citées.
- **Garde-fous** : « → humain » se lit « → bloqué ». « Rollback […] retour exact au comportement
  humain » se lit « retour au blocage de toute promotion automatique ».
- **§Alternatives rejetées, §Plan de mise en œuvre (séquence de sortie comprise) et §Angles morts** :
  leurs mentions d'une sécurité humaine, d'une vérification sémantique « hors scope » ou d'un renvoi
  « → humain » se lisent selon ADR-114 et ADR-119.
- Le reste d'ADR-093 est maintenu, dont la couche L0 et la barre non sécurité.

### ADR-096 (découverte automatique de sources)

- **§D5, premier point** : une donnée de sécurité et une valeur numérique critique suivent ADR-114 et
  ADR-119. Une source inconnue reste soumise à la validation humaine de son autorité.
- **§D5, troisième point** : le passage d'`exportable.seo` à `true` suit ADR-119 D6.
- **§D6, dernier point** : une contradiction majeure bloque la fiche (ADR-119 D2 et D3). Elle se
  résout par une contribution (capture, catalogue), pas par un arbitrage humain. L'autorité des
  sources inconnues reste humaine.
- Le scraper n'a toujours aucune capacité de promotion. Le reste d'ADR-096 est maintenu.

### ADR-031 (architecture en quatre couches)

- **Principe directeur, deuxième phrase** : « validée humainement » se lit « validée par le décideur
  unique sur preuve, auto-review de sens comprise (ADR-114, ADR-119) ». L'acte humain porte sur les
  règles qui fixent cette preuve, fusionnées par l'owner, et sur les contributions.
  - Ce principe est une formulation de l'owner, figée et non négociable. C'est l'owner qui en change
    la deuxième phrase (demande du 2026-10-30).
  - Les trois autres phrases restent inchangées et non négociables.
- **Architecture cible, schéma** : « validation humaine + sourcing + lint » se lit « décision sur
  preuve + sourcing + lint ».
- **Héritage ADR-022, point « Propose-before-write »** : la promotion vers `automecanik-wiki/`
  requiert la décision du décideur unique, pas une validation humaine explicite.
- La séparation RAW / WIKI / exports / consommateurs est maintenue. Aucun consommateur ne lit RAW. Le
  reste d'ADR-031 est maintenu.

### ADR-088 (score de substance)

- **`no_disputed_claims: false`** plafonne toujours au TIER B, mais le TIER B n'a plus de revue
  humaine.
  - La fiche reste en proposition, bloquée par ce motif, jusqu'à ce qu'une source captée tranche la
    divergence ou que la fiche ne porte plus l'affirmation disputée.
  - Elle n'est pas rejetée : l'honnêteté n'est toujours pas punie.
  - Le décideur doit lire ce champ pour toute fiche (Contexte, constat).
- Le reste d'ADR-088 est maintenu.

## Ce que cet ADR ne fait pas

- Il ne lève pas le verrou. Il ne promeut, ne corrige et ne retire aucune fiche, `plaquette-de-frein`
  comprise.
- Il ne crée ni exécuteur ni artefact : c'est le rôle des PR WIKI (Mise en œuvre).
- Il ne touche pas au diagnostic.
  - Le flip `diagnostic_safe` et la relecture des règles de sécurité du diagnostic restent humains
    (ADR-033, ADR-112 D5).
  - Les relations restent régies par ADR-115 et ADR-116.
  - Les remplacer par une auto-review exigerait un ADR distinct.
- Il ne valide aucune plage et ne change pas l'autorité des sources inconnues.
- Il ne modifie pas `scripts/wiki-generators/auto_review_wiki_proposal.py` (monorepo). Son étiquette
  `NEXT_HUMAN_SPOT_CHECK` n'a ni consommateur ni autorité (ADR-114 D2).
- Il ne change aucune URL, aucun meta, aucun H1, ni aucune règle d'indexation.
- Il ne modifie aucun garde, aucun workflow, ni la fusion par l'owner.

## Mise en œuvre

1. Une PR WIKI, en report-only :
   - l'exécuteur du protocole D2 ;
   - le schéma de l'artefact et la fonction de découpage ;
   - la condition D3, bloquante pour les fiches sécurité et tracée pour les autres ;
   - la trace D8 ;
   - `_meta/quality-gates.md` §6 et §7 alignés, dont le texte de la constante et de
     `SAFETY_HUMAN_REVIEW` ;
   - les tests de la précondition (d).
2. L'étalonnage sur `plaquette-de-frein` au commit `88f9f88`, artefacts versionnés (précondition e).
3. La PR WIKI de retrait de `plaquette-de-frein` par §10, si son auto-review rend FAIL, avec ses
   exports dérivés. Elle n'attend pas la levée.
4. La PR WIKI de levée (D4).
5. Une PR WIKI qui fait lire `no_disputed_claims` par le décideur pour toute fiche (ADR-088 amendé).
   Elle durcit le contrôle et ne requiert pas d'autre ADR.
6. Une PR monorepo distincte qui aligne la formulation « validée humainement » de l'invariant 4 du
   `CLAUDE.md` racine sur ADR-031 amendé. Elle ne change aucun code.

## Options considérées

### Option A — Statu quo — rejetée

Les ADR décrivent une relecture humaine que le WIKI n'offre plus depuis le 2026-09-12. La relecture
a posteriori exigée par ADR-114 a été faite par un agent. Le texte et la pratique divergent.

### Option B — Rétablir une relecture humaine par fiche sécurité — rejetée

- Elle contredit la décision de l'owner du 2026-09-12 et sa demande du 2026-10-30.
- La seule relecture faite sous ADR-114 est celle d'un agent outillé. Elle a trouvé l'écart de
  sécurité.
- Elle rouvrirait l'approbation par-dessus une preuve manquante.

### Option C — Auto-review a posteriori seulement — rejetée

La fiche serait publiée avant d'être relue. C'est le scénario du 2026-10-21 : une fiche sécurité au
canon avec un écart de sécurité, sur un dépôt public.

### Option D — Verdict unique d'un modèle, sans réfutation — rejetée

Un seul passage ne s'oppose à rien. La réfutation indépendante a écarté 2 des 31 écarts signalés le
2026-10-21. Sans elle, ces faux positifs auraient bloqué la fiche, et un faux négatif ne serait
contredit par personne.

### Option E — Auto-review comme décideur — rejetée

Un modèle qui rend une fiche éligible serait un second décideur (ADR-114 D2). Son verdict varie d'un
passage à l'autre. Il ne doit donc pouvoir que bloquer.

### Option F — Auto-review de sens préalable, bloquante pour la sécurité, sans voie humaine d'approbation — retenue

D1 à D8.

## Conséquences

### Positives

- Les ADR décrivent ce que fait le WIKI. Plus aucune fiche n'attend une étape qui n'existe pas.
- Le sens d'une fiche sécurité est vérifié avant sa publication, et plus seulement sa preuve et ses
  chiffres.
- L'écart du 2026-10-21 devient un cas d'étalonnage. La gate ne se rouvre pas sans le détecter.
- La règle d'`exportable.seo` est la même pour toutes les fiches.

### Négatives

- Un modèle n'est pas déterministe. Deux passages peuvent diverger. L'artefact par clé, le FAIL non
  remplaçable et la relance sur 30 jours limitent ce risque sans l'annuler.
- Chaque fiche coûte au moins deux passes de détection et trois réfutations par candidat.
- Un faux positif garde une fiche bloquée jusqu'à une capture qui le tranche. C'est voulu.
- Une omission que ni la fiche ni ses captures n'évoquent reste invisible. La couverture des sources
  relève d'ADR-089.
- `plaquette-de-frein` reste au canon avec ses écarts connus jusqu'à son retrait (Mise en œuvre,
  point 3).

## Métriques

- Par passage de l'auto-review :
  - fiches relues et verdicts (PASS, FAIL, INCOMPLETE, ERROR) ;
  - écarts confirmés par classe et candidats écartés ;
  - part des écarts confirmés qu'aucune capture ne tranche ;
  - coût et durée par fiche.
- Étalonnage : part des écarts de référence du 2026-10-21 retrouvée.
- Relance sur 30 jours : FAIL sur une fiche promue. Chaque FAIL referme la gate.
- Fiches non sécurité : nombre de fiches que la condition bloquerait en report-only.

## Retour arrière

- Une PR WIKI remet `SAFETY_AUTO_APPROVAL_ADR` à vide. Toute décision rendue devient `STALE_DECISION`
  et les fiches sécurité redeviennent bloquées.
- Une fiche déjà promue se retire par §10, avec ses exports dérivés, par une PR WIKI fusionnée par
  l'owner.
- Retirer cet ADR rend leur texte aux ADR amendés. La voie humaine supprimée dans le WIKI le
  2026-09-12 ne revient pas pour autant.

## Revue planifiée

**Date** : J+90 après la levée du verrou, ou le 2027-01-28 si le verrou n'est pas levé d'ici là.

**Critères** :

- les métriques ci-dessus ;
- un défaut de valeur, de sécurité ou de sens dans une fiche promue : refermer la gate (Retour
  arrière) avant toute analyse ;
- la stabilité des verdicts lors des relances ;
- l'opportunité de rendre la condition D3 bloquante pour les fiches non sécurité.

## Références

- [[ADR-114-wiki-safety-auto-gate|ADR-114]] ·
  [[ADR-091-wiki-score-recalibration|ADR-091]] ·
  [[ADR-083-tiered-wiki-promotion|ADR-083]] ·
  [[ADR-093-auto-review-earn-gate|ADR-093]] ·
  [[ADR-096-governed-automatic-source-discovery|ADR-096]] ·
  [[ADR-031-four-layer-content-architecture|ADR-031]] ·
  [[ADR-088-promotion-gate-substance-scoring|ADR-088]] ·
  [[ADR-117-wiki-promoter-canon-revision|ADR-117]] ·
  [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] ·
  [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] ·
  [[ADR-089-content-coverage-map-canon|ADR-089]] ·
  [[ADR-046-r-stack-single-generator-and-layers|ADR-046]] ·
  [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]]
- WIKI :
  - PR #83 (validation automatique, 2026-09-12), #120 (promotion automatique finalisée, et
    commentaire de relecture a posteriori du 2026-10-21), #124 (gate refermée) ;
  - `_meta/quality-gates.md` §1, §6, §7 et §10 ;
  - `_scripts/promotion_decision.py` (`SAFETY_AUTO_APPROVAL_ADR`, `_safety_local_conditions`),
    `_scripts/build_exports_content.py`, `_scripts/gates/contradiction_gate.py`.
- (Relations structurées : voir `amends` / `related_adr` dans le frontmatter.)

---

*Proposé le : 2026-10-30*
*Accepté le : à la fusion owner (fusion = ratification)*
