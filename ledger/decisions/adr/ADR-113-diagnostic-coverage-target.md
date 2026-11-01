---
id: ADR-113
title: "Couverture de la base de diagnostic — gammes publiées, symptômes du vocabulaire, séries moteur du constructeur : amende ADR-033 et ADR-112"
status: accepted
date: "2026-10-04"
decision_date: "2026-10-04"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-033", "ADR-112"]
extends: []
related_adr: ["ADR-031", "ADR-033", "ADR-035", "ADR-086", "ADR-089", "ADR-093", "ADR-096", "ADR-112"]
related_rules: ["G1", "G6", "Q1", "AP-11"]
related_incidents: []
version: "1.0.0"
---

# ADR-113 : Couverture de la base de diagnostic — gammes publiées, symptômes, séries moteur

- **Statut** : Accepted (2026-10-04). La fusion par l'owner vaut ratification.
- **Objectif fixé par l'owner** (2026-10-04) : le diagnostic doit porter sur toutes les gammes, tous
  les symptômes et tous les véhicules. Il a limité la première étape aux gammes publiées.
- **Amende** :
  - [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] : D8 et §Amendements (sens de « famille
    moteur sourcée »), D13, Métriques, Revue planifiée ;
  - [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] : champ « sans objet diagnostic »,
    sens de la famille moteur dans `vehicle_scope`.

  Chaque amendement est décrit en §Amendements. Le reste de ces ADR reste en vigueur.
- **Pourquoi un ADR séparé** : ADR-112 a été fusionnée (vault #373, 2026-10-04) avant que cette cible
  soit écrite. Son texte n'est pas rouvert.
- **Méthode** : les chiffres ci-dessous ont été mesurés le 2026-10-04, en lecture seule :
  - base de données partagée DEV/PREPROD/PROD ;
  - `main` du monorepo au commit `659afc791` ;
  - `main` du WIKI au commit `042e566`.

## Contexte

### Ce qu'ADR-112 ne fixe pas

ADR-112 fixe comment une affirmation entre dans la base et ce qu'elle a le droit d'affirmer. Elle ne
fixe ni jusqu'où la base doit aller, ni comment on mesure qu'elle y va. Sans cible mesurée, « base
experte » ne se vérifie pas.

Le mot « couverture » a déjà un sens dans le WIKI : la coverage map
d'[[ADR-089-content-coverage-map-canon|ADR-089]] relie chaque affirmation d'une fiche à sa source. Cet
ADR compte autre chose : à l'échelle du catalogue, les gammes, les symptômes et les séries moteur qui
portent des affirmations relues. Il ne remplace pas la coverage map et ne la duplique pas.

### État mesuré le 2026-10-04

| Axe | Constat |
|---|---|
| Gammes publiées | 232 : la vue `__pg_gammes` (`pieces_gamme` avec `pg_display = '1'`, `pg_level` différent de 0, `pg_g_level` G1 ou G2). La table `gamme_aggregates` en compte 241 : c'est une table d'indicateurs SEO qui inclut 9 gammes non affichées. Elle ne définit pas la publication |
| Relations dans le WIKI | 4 fiches gamme en portent (filtre à huile, à air, à carburant, d'habitacle), toutes publiées. Aucune de leurs relations n'est relue (`reviewed: false`) |
| Vocabulaire de symptômes | 62 symptômes actifs dans `__diag_symptom`. Leurs liens vers une cause viennent de l'amorce, sans source (ADR-112, Contexte) |
| Types de véhicule | 53 959 dans `auto_type`. 50 741 portent au moins un code moteur du catalogue (`auto_type_motor_code` : 63 091 lignes, 12 061 codes distincts ; ADR-086 §4 le décrivait encore vide), dont 8 427 en portent plusieurs ; 3 218 n'en portent aucun |
| Familles moteur | `kg_engine_families` : 10 lignes. 3 sont des codes de série (D4F, F4R, K9K). Les 7 autres sont des appellations commerciales (BlueHDi, EcoBoost, HDi, PureTech, TDI, THP, TSI) |
| Rattachement famille → véhicules | Le WIKI ne porte aucune correspondance code moteur → série, et `wiki/vehicle` ne contient aucune fiche. Son modèle de fiche (`_templates/new-vehicle.md`) liste déjà, par motorisation, les codes moteur tirés de `auto_type_motor_code`, jamais inférés. Le générateur `scripts/wiki-generators/kg-engine-evidence-seed.py` (`resolve_vehicles`) rattache une famille aux fiches véhicule RAW par marque du groupe, carburant et cylindrée à une tolérance près |

## Principe directeur

> La couverture se mesure, elle ne se remplit pas. Une gamme, un symptôme ou une série n'est compté
> que par des affirmations relues, au niveau que leur preuve permet (ADR-112 D3), ou, pour une gamme,
> par un constat « sans objet » relu. Chaque mesure publie son dénominateur.

## Décisions

### D1 — Première étape : les gammes publiées

- Le périmètre est défini par un **critère** : les gammes de la vue `__pg_gammes` (232 au 2026-10-04).
  Ce n'est ni une liste figée, ni `gamme_aggregates`.
- Chaque mesure publie son dénominateur du jour. Si le nombre de gammes publiées change, la variation
  apparaît dans la mesure.
- Les gammes non publiées sont hors de la première étape. Les y faire entrer demande un amendement
  ultérieur, sans date.

### D2 — Gammes : deux issues, toutes deux relues

Chaque gamme publiée doit aboutir à l'une de deux issues :

- **couverte** : sa fiche WIKI porte au moins une affirmation d'ADR-112 D1 relue (`reviewed: true`) ;
- **sans objet diagnostic** : sa fiche porte le constat relu (`reviewed: true`, bascule selon ADR-033
  D4), avec son motif, que la gamme n'a aucune relation diagnostic (cause, amplificateur, effet
  secondaire) avec un symptôme du vocabulaire. Le champ est ajouté à ADR-033 (§Amendements).

Règles :

- Aucune relation n'est écrite pour atteindre la cible. Une gamme qui ne porte ni affirmation relue,
  ni constat « sans objet » relu, reste « non couverte » dans la mesure.
- « Sans objet » est compté à part, avec la liste des gammes et leurs motifs. Il ne se confond pas avec
  « couverte ».
- Une gamme qui porte une affirmation relue compte « couverte », même si sa fiche porte aussi un
  constat « sans objet ».
- Une gamme couverte est rangée au niveau de sa meilleure affirmation (probable, possible, à vérifier).
  Une affirmation relue dont aucune source n'est `raw_proven` compte au niveau « à vérifier ».

### D3 — Symptômes : chaque symptôme du vocabulaire relié à une cause

- Cible : chaque symptôme actif du vocabulaire canon (`__diag_symptom`, 62 au 2026-10-04) est relié à
  au moins une cause par une affirmation symptôme → cause relue, portée par la fiche d'une gamme
  publiée.
- Le symptôme est rangé au niveau de sa meilleure affirmation, comme une gamme.
- Deux comptes à part, publiés avec la liste de leurs symptômes :
  - **hors périmètre** : les affirmations relues qui relient le symptôme à une cause sont toutes portées
    par des fiches de gammes non publiées ;
  - **en attente** : le symptôme porte au moins un lien de l'amorce (`__diag_symptom_cause_link`, non
    sourcé, ADR-112 D2), et aucune des causes que ces liens lui associent n'est rattachée à une pièce
    par la correspondance cause → pièce en vigueur (`CAUSE_GAMME_MAP`, puis la table de la phase 3
    d'ADR-112). Ce compte signale des causes sans pièce rattachée : réglage ou condition d'usage,
    différés par ADR-112 D1, ou pièce pas encore rattachée.
- Chaque symptôme est rangé dans le premier compte dont il remplit la condition, dans cet ordre :
  relié (au niveau de sa meilleure affirmation), hors périmètre, en attente. Tout autre symptôme est
  « non relié ».

### D4 — Véhicules : la série moteur du constructeur, avec le carburant

- L'unité véhicule est la famille moteur avec le carburant, portée par `vehicle_scope` (ADR-112,
  amendement d'ADR-033).
- La **famille** est la **série moteur du constructeur**, désignée par son code de série (par exemple
  N47, EA189, K9K).
- Une appellation commerciale (TDI, HDi, PureTech, TSI, EcoBoost…) n'est pas une famille : elle recouvre
  plusieurs séries, dont les pannes diffèrent.
- Ce sens précise, pour le diagnostic seulement, la clé `engine_family:` de
  [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §4 (mêmes exemples : N47, K9K).
  - Le type est relié à son code moteur par la base (`auto_type_motor_code`, le « backfill DB »
    d'ADR-086 §4).
  - Le code est relié à la série par la correspondance sourcée ci-dessous. Le code seul ne vaut pas
    série.
  - La clé SEO d'ADR-086 §4 n'est pas modifiée.
- Une affirmation s'applique sans portée, à un carburant, ou à une série. Elle n'est jamais recopiée
  type par type.
- Un type est rattaché à une série par son code moteur du catalogue et par une **correspondance code →
  série sourcée et relue**.
  - Elle vit dans le WIKI et y est relue ([[ADR-031-four-layer-content-architecture|ADR-031]]). Ce
    n'est jamais une table écrite à la main.
  - Elle n'est jamais déduite d'un préfixe de code, ni de la marque, du carburant et de la cylindrée.
  - Si elle est projetée en base, ce ne peut être que par la voie unique d'ADR-112 D2, le module de
    projection d'[[ADR-035-diagnostic-tool-source-trust-flag|ADR-035]].
  - Son ajout aux types d'affirmation d'ADR-112 D1, sa place dans le WIKI parmi les entités d'ADR-031
    et sa cible en base sont fixés par une décision séparée ; cet ADR ne les fixe pas. Cette décision
    part de l'existant : le modèle de fiche `vehicle` porte déjà les codes moteur de chaque
    motorisation.
- `kg_engine_families` reste une projection, régie par ADR-086 §6 et ADR-112 D9 ; cet ADR ne la modifie
  pas. Une appellation qui y figure ne vaut pas série pour la mesure.
- Un type dont le code n'est rattaché à aucune série n'est couvert que par les affirmations sans portée
  ou par carburant.

### D5 — Mesure

À chaque exécution de la projection (ADR-112 D2), trois taux sont publiés. Chacun porte son
dénominateur du jour et la version de l'export WIKI projeté, qui est une composante de `kb_version`
(ADR-112 D10).

| Taux | Numérateur | Dénominateur | Comptes publiés |
|---|---|---|---|
| Gammes | couvertes + sans objet | gammes publiées (`__pg_gammes`) | probable, possible, à vérifier, sans objet, non couverte |
| Symptômes | reliés | symptômes actifs du vocabulaire (`__diag_symptom`) | probable, possible, à vérifier, hors périmètre, en attente, non relié |
| Véhicules | séries portant au moins une affirmation relue de portée série | séries rattachées par la correspondance sourcée | séries : probable, possible, à vérifier, non couverte |

Les types d'`auto_type` sont publiés en quatre comptes, avec le nombre total de types. Un type est
rangé dans le premier compte dont il remplit la condition, dans cet ordre :

1. couvert au titre d'au moins une de ses séries ;
2. série rattachée, sans affirmation relue ;
3. code moteur non rattaché à une série ;
4. sans code moteur.

- Chaque gamme, chaque symptôme, chaque série rattachée et chaque type tombe dans un seul compte. La
  somme des comptes égale le dénominateur.
- La liste des éléments de chaque compte est publiée avec les taux. Pour les types, ce sont les
  comptes seuls.
- La mesure lit l'export WIKI que lit la projection pour les numérateurs, et la base pour les
  dénominateurs. Le compte « en attente » lit aussi l'amorce et la correspondance cause → pièce en
  vigueur. Elle ne lit ni RAW ni RAG.
- Le support de publication est fixé par la PR qui livre la mesure.

### D6 — État initial (2026-10-04)

| Taux | Valeur | Comptes |
|---|---|---|
| Gammes | 0 / 232 | non couverte 232, sans objet 0. 4 gammes portent des relations, aucune n'est relue |
| Symptômes | 0 / 62 | non relié 62, hors périmètre 0, en attente 0 |
| Véhicules | non défini : 0 série rattachée (dénominateur 0) | types : couvert 0, série sans affirmation relue 0, code non rattaché 50 741, sans code 3 218 (total 53 959) |

« En attente » vaut 0 : chacun des 62 symptômes a, dans l'amorce, au moins une cause rattachée à une
pièce par `CAUSE_GAMME_MAP`. Les 58 causes de `__diag_cause` y figurent toutes ; 4 n'y ont aucune
pièce.

### D7 — Ordre et plafonds

- Après le système pilote d'ADR-112, les phases 2 et 3 se répètent système par système, jusqu'aux
  cibles de D2 et D3.
- Chaque système passe la porte de la phase 3 avec ses propres cas, ajoutés au jeu de référence
  d'ADR-112 D11, dont les seuils ne peuvent que monter.
- La cible ne lève aucun plafond de preuve (ADR-112 D3).
- Elle n'étend pas la relecture automatique au-delà
  d'[[ADR-093-auto-review-earn-gate|ADR-093]] (ADR-112 D12).
- Aucune date n'est fixée : le rythme vient de la capture des sources
  ([[ADR-096-governed-automatic-source-discovery|ADR-096]]).

## Amendements

### ADR-112 (base de connaissances diagnostic)

- **D8 et §Amendements (`vehicle_scope`)** : « famille moteur sourcée » s'entend au sens d'ADR-113
  D4 : une série moteur du constructeur, rattachée aux types par la correspondance sourcée.
- **D13** : sous le tableau des phases s'ajoute la règle suivante. Après le système pilote, les phases
  2 et 3 se répètent système par système jusqu'aux cibles d'ADR-113. Chaque système passe la porte de
  la phase 3 avec ses propres cas, ajoutés au jeu de référence de D11, dont les seuils ne peuvent que
  monter.
- **D13, phase 0** : la PR de schéma WIKI livre aussi le champ `diagnostic_not_applicable` (ADR-033,
  ci-dessous).
- **Métriques** : s'ajoutent les trois taux d'ADR-113 D5, avec leurs dénominateurs et leurs comptes.
- **Revue planifiée** : s'ajoutent aux critères les trois taux, comparés à l'état initial d'ADR-113 D6.
- Tout le reste d'ADR-112 est maintenu.

### ADR-033 (contrat WIKI des relations)

Nouveau champ optionnel de fiche gamme, en frontmatter, à côté de `diagnostic_relations[]` :

```yaml
diagnostic_not_applicable:
  reason: "…"        # motif, une phrase, obligatoire
  reviewed: false    # relecture humaine ; même règle de bascule qu'ADR-033 D4
```

- Une fiche ne porte pas à la fois ce champ et des `diagnostic_relations[]`. Le validateur CI
  d'ADR-033 D5 le refuse.
- La bascule de `reviewed` suit ADR-033 D4 : manuelle, ou couverte par une règle d'ADR explicite.
- Le champ est livré par la PR de schéma WIKI de la phase 0 d'ADR-112.

Dans `vehicle_scope`, le champ ajouté par ADR-112 :

- la famille moteur est la série moteur du constructeur, désignée par son code de série (ADR-113 D4) ;
- une appellation commerciale n'est pas une valeur valide ;
- une série n'est valide que si la correspondance sourcée d'ADR-113 D4 la contient.

## Ce que cet ADR ne fait pas

- Il ne crée aucune table, aucune migration et aucun code.
- Il ne fixe aucune date ni échéance.
- Il ne fixe ni le type d'affirmation de la correspondance code → série, ni sa place dans le WIKI, ni
  sa cible en base.
- Il ne modifie pas la clé SEO `engine_family:` d'ADR-086 §4.
- Il ne modifie ni `kg_engine_families` ni aucun autre objet `kg_*` (ADR-086 §6, ADR-112 D9).
- Il n'étend pas la cible aux gammes non publiées.
- Il ne bascule aucune entrée WIKI en `reviewed` ou `diagnostic_safe`, et ne lève aucun plafond
  d'ADR-112.
- Il ne change aucune URL, aucun meta, aucun H1, et aucune page indexée.

## Options considérées

### Option A — Cible sur `gamme_aggregates` (241) — rejetée

Cette table d'indicateurs inclut 9 gammes non affichées. Son contenu vient d'un remplissage, pas de la
publication.

### Option B — Liste figée de gammes — rejetée

Elle diverge dès qu'une gamme est publiée ou retirée, sans que la mesure le montre.

### Option C — L'appellation commerciale comme famille — rejetée

Une appellation (TDI, PureTech…) recouvre plusieurs séries aux pannes différentes. Une affirmation
portée par l'appellation serait fausse pour une partie des moteurs.

### Option D — Rattachement par marque, carburant et cylindrée, ou par préfixe de code — rejetée

C'est une déduction, pas une preuve. C'est ce que fait aujourd'hui le générateur
`kg-engine-evidence-seed.py` (`resolve_vehicles`) : marque du groupe, carburant, cylindrée à 0,15 L
près.

### Option E — Affirmations recopiées type par type — rejetée

53 959 types : ce serait une duplication de plus, sans source.

### Option F — Cible chiffrée avec une date — rejetée

Elle pousse à remplir pour tenir la date. Le rythme vient de la capture des sources.

### Option G — Critère, comptes séparés, série moteur sourcée — retenue

D1 à D7.

## Conséquences

### Positives

- « Base experte » devient mesurable : trois taux, un état initial, des dénominateurs publiés.
- Le manque reste visible : « non couverte », « en attente » et « hors périmètre » sont des comptes
  publiés, avec leur liste.
- La portée véhicule s'appuie sur le code moteur du catalogue, présent pour 50 741 types sur 53 959.

### Négatives

- Il faut capturer des sources pour 232 gammes et pour chaque série. C'est le travail le plus long.
- La correspondance code → série doit être sourcée avant toute affirmation par série. D'ici là, seules
  les portées « sans portée » et « carburant » s'appliquent.
- Les 3 218 types sans code moteur ne sont couverts que par ces deux portées.
- Chaque constat « sans objet » demande une relecture.

## Métriques

Les trois taux de D5, à chaque exécution de la projection, comparés à l'état initial de D6.

## Retour arrière

- Cet ADR ne crée ni donnée ni code.
- Le retirer rend à ADR-112 et ADR-033 leur texte antérieur.
- Le champ « sans objet diagnostic », s'il a été livré, reste optionnel.

## Revue planifiée

**Date** : avec la revue d'ADR-112, J+90 après son acceptation, soit le 2027-01-02.

**Critères** :

- les trois taux et leur évolution depuis D6 ; si aucune mesure n'a été publiée, la revue le
  constate ;
- les comptes « en attente » et « hors périmètre » : justifient-ils un ADR pour les causes qui ne sont
  pas des pièces, ou l'extension aux gammes non publiées ?
- l'état de la correspondance code → série.

## Références

- [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] ·
  [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] ·
  [[ADR-031-four-layer-content-architecture|ADR-031]] ·
  [[ADR-035-diagnostic-tool-source-trust-flag|ADR-035]] ·
  [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] ·
  [[ADR-089-content-coverage-map-canon|ADR-089]] · [[ADR-093-auto-review-earn-gate|ADR-093]] ·
  [[ADR-096-governed-automatic-source-discovery|ADR-096]]
- Vault : #373 (ADR-112)

---

*Accepté le : 2026-10-04 (fusion owner = ratification)*
