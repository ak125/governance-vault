---
id: ADR-115
title: "Provenance diagnostic : seule une relation relue est projetée — amende ADR-035 (principe directeur, D2, D6, D7)"
status: accepted
date: "2026-10-11"
decision_date: "2026-10-11"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-035"]
extends: []
related_adr: ["ADR-033", "ADR-035", "ADR-112", "ADR-113"]
related_rules: ["G1", "G6", "Q1"]
related_incidents: ["INC-2026-013"]
version: "1.0.0"
---

# ADR-115 : Provenance diagnostic — seule une relation relue est projetée

- **Statut** : Accepted (2026-10-11). La fusion par l'owner vaut ratification.
- **Amende** [[ADR-035-diagnostic-tool-source-trust-flag|ADR-035]] : principe directeur, D2 (condition
  de projection), D6 (critères 1 et 2), D7 (une interdiction ajoutée). Chaque amendement est décrit
  en §Décisions.
  - Ces amendements s'appliquent dès la fusion de cet ADR, sans attendre les phases
    d'[[ADR-112-diagnostic-knowledge-base-canon|ADR-112]]. La phrase d'ADR-035 « Jusque-là, D1 à D7
    s'appliquent tels quels » se lit donc avec eux.
  - Le reste d'ADR-035, avec ses amendements par ADR-112, reste en vigueur.
- **Ne modifie pas ADR-112.** Sa porte de phase 1 (D13) renvoie au « résultat honnête attendu par
  ADR-035 D6 » : elle se lit avec D6 tel qu'amendé ici. Le texte d'ADR-112 ne change pas.
- **Pourquoi un ADR séparé** : ADR-035 est accepté depuis le 2026-10-04. Son texte n'est pas rouvert,
  comme pour ADR-112 avec [[ADR-113-diagnostic-coverage-target|ADR-113]].
- **Méthode** : les chiffres ci-dessous ont été mesurés le 2026-10-11, en lecture seule :
  - base de données partagée DEV/PREPROD/PROD ;
  - resolver de projection de `main` du monorepo au commit `9384ef9a7`, exécuté hors ligne sur les
    tables actives lues en base ;
  - exports `exports/diagnostic` du WIKI au commit `88017732` (schéma 2.0.0). Le sous-module WIKI du
    monorepo épingle ce commit depuis #1758, et l'image l'embarque depuis #1762 (`9384ef9a7`).

## Contexte

### Ce que D6.1 attendait

ADR-035 D6.1, rédigé le 2026-09-30 : « Le premier run activé donne `exported = 3`, `projected = 0`,
`conflicts = 3` (`source_not_raw_proven`) : le résultat honnête tant qu'aucune source n'est
capturée. » ADR-112 D13 fait de ce résultat la porte de sortie de sa phase 1.

### Ce que le premier run donnerait aujourd'hui

Le resolver de `main`, rejoué sur les exports du WIKI et sur les tables actives de la base :

| Gamme | Symptôme | Sources | `reviewed` | Résultat |
|---|---|---|---|---|
| filtre-a-air | `perte_puissance_filtration` | 2 `to_capture` | false | conflit `source_not_raw_proven` |
| filtre-a-carburant | `perte_puissance_filtration` | 2 `to_capture` | false | conflit `source_not_raw_proven` |
| filtre-d-habitacle | `odeur_habitacle` | 1 `to_capture` | false | conflit `source_not_raw_proven` |
| filtre-a-huile | `voyant_huile` | 1 `active`, `raw_proven` | false | **projetée** (lien 112) |
| filtre-a-huile | `perte_puissance_filtration` | 2 `active`, `raw_proven` | false | **projetée** (lien 152) |

Résultat : `exported = 5`, `projected = 2`, `conflicts = 3`. D6.1 est faux sur deux comptes.

Les deux relations projetées décrivent leur rôle comme une « hypothèse non établie ». Elles portent
`confidence: low`, `source_policy: manual_review`, `reviewed: false` et `diagnostic_safe: false`.
Leurs sources sont bien capturées dans RAW, mais personne n'a relu l'affirmation. Le run leur
donnerait pourtant une ligne de provenance vivante : les liens 112 et 152 deviendraient
« documentés » au sens d'ADR-035 D1, et seraient affichés comme tels dès le drapeau
`DIAGNOSTIC_PROVENANCE_EXPOSE_ENABLED` (ADR-035 D4).

### La cause

`raw_proven` dit qu'un document existe dans RAW. Il ne dit pas que ce document soutient la relation.
Seule la relecture, dans le WIKI, l'établit : c'est le sens de `evidence.reviewed`
([[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] : « statut de validation humaine »).
Son passage à `true` est « strictement manuel ou couvert par règle ADR explicite, jamais en
automatique » (ADR-033 D4).

ADR-112 en fait déjà son principe directeur : « sources → RAW → WIKI relu par un humain → projection
gouvernée ». Son mode « créer ou remplacer » exige `reviewed: true`, et son niveau « possible » aussi
(D3). Le mode « rattacher » d'ADR-035 D2, seul actif avant la phase 3 d'ADR-112, ne l'exige pas.
C'est cet écart que cet ADR ferme.

## Principe directeur (remplace celui d'ADR-035)

> Une relation symptôme → cause n'est « documentée » en base que par une provenance WIKI **relue**
> (`evidence.reviewed: true`, posé selon ADR-033 D4), dont toutes les sources sont prouvées dans RAW.
> Aucun nombre n'est affiché pour un lien tant qu'aucune fréquence sourcée n'existe.

## Décisions

### D1 — Projeter exige `reviewed: true` (amende ADR-035 D2)

- Le troisième point d'ADR-035 D2 devient : une relation n'est projetée que si toutes ses sources sont
  `raw_proven` **et** si son entrée WIKI porte `evidence.reviewed: true`. Les deux valeurs viennent
  du builder du WIKI et sont recopiées telles quelles.
- « Relue » veut dire `evidence.reviewed: true`, posé selon ADR-033 D4. Cet ADR n'ouvre aucune voie
  nouvelle pour le poser, et ne ferme aucune de celles qu'ADR-033 D4 et ADR-112 D12 admettent.
- Une relation dont toutes les sources sont `raw_proven`, mais qui n'est pas relue, donne le conflit
  **`not_reviewed`**.
- Ce conflit est évalué **en dernier**, après tous les conflits existants, dont
  `source_not_raw_proven`, qui l'est déjà aujourd'hui.
  - L'ordre d'évaluation suit la chaîne d'ADR-112 : sources → RAW → WIKI relu. Une relation ni
    capturée ni relue compte donc en `source_not_raw_proven`.
  - Cet ordre ne présume pas de l'ordre des événements (D6.2) : une relation peut être relue avant la
    capture de ses sources. Elle compte alors en `source_not_raw_proven`, et au niveau « à vérifier »
    d'ADR-113 D2.
  - Le compte `source_not_raw_proven` continue de mesurer la capture RAW (ADR-035 §Conséquences,
    ADR-112 §Métriques). Le compte `not_reviewed` ne porte que sur les relations déjà capturées et
    sans autre conflit.
- Le reste d'ADR-035 D2 est maintenu. Le writer ne modifie jamais `reviewed` ni `diagnostic_safe`, et
  ne crée ni symptôme, ni cause, ni lien.
- Une relation déjà projetée qui repasse à `reviewed: false` dans le WIKI n'est pas reprise par le run
  suivant. Sa ligne de provenance est alors retirée (`retired_at`), comme toute relation qui n'est
  plus projetée (ADR-035 D1). Aucun mécanisme nouveau.

### D2 — Critères de succès (amende ADR-035 D6.1 et D6.2)

- **D6.1** devient : le premier run activé projette exactement les relations relues dont toutes les
  sources sont `raw_proven` et qui se résolvent vers un lien existant. Chaque autre relation exportée
  donne un conflit typé, et `exported = projected + conflicts`.
  - Avec les exports du WIKI au commit `88017732` : `exported = 5`, `projected = 0`, `conflicts = 5`
    (3 `source_not_raw_proven`, 2 `not_reviewed`).
  - Ces comptes sont un constat daté, pas une cible : ils suivent les exports que l'image embarque au
    moment du run. La règle, elle, ne change pas.
- **D6.2** devient : une relation qui se résout vers un lien existant, sans autre conflit, produit une
  ligne vivante au run suivant, sans intervention en base, dès qu'elle remplit les deux conditions :
  - sa dernière source non prouvée passe `active` par le flux gouverné ;
  - son entrée WIKI porte `evidence.reviewed: true`.

  L'ordre de ces deux événements est indifférent.
- D6.3 et D6.4 sont inchangés.

### D3 — Interdiction ajoutée (amende ADR-035 D7)

- Projeter une relation dont l'entrée WIKI ne porte pas `evidence.reviewed: true`.
- Comme l'interdiction sur `raw_proven`, elle est portée par la base (contrainte sur
  `__diag_link_provenance`), pas par le seul code du writer.

## Ce que cet ADR ne fait pas

- Il ne passe aucune relation à `reviewed: true`. Ce passage reste « strictement manuel ou couvert
  par règle ADR explicite, jamais en automatique » (ADR-033 D4), dans le WIKI (ADR-035 D2), dans la
  limite d'ADR-112 D12.
- Il ne change ni la pondération par `diagnostic_safe` (ADR-035 D4), ni les drapeaux (D5), ni le mode
  « créer ou remplacer » d'ADR-112.
- Il ne modifie pas le texte d'ADR-112.
- Il n'active rien : aucun drapeau, aucune migration appliquée.

## Mise en œuvre

Une PR monorepo, après la fusion de cet ADR :

- resolver : conflit `not_reviewed`, évalué en dernier, avec ses tests ;
- migration :
  - `not_reviewed` ajouté aux raisons admises par `__diag_projection_conflicts` ;
  - contrainte `reviewed` sur `__diag_link_provenance`.

  Les trois tables sont vides au 2026-10-11 : aucun run n'a eu lieu.
- L'application de la migration reste un acte de l'owner.

Le premier run activé doit respecter ADR-035 D7 tel qu'amendé : il attend cette PR et sa migration.

## Options considérées

### Option A — Réécrire D6.1 à 5 / 2 / 3 — rejetée

Le texte redeviendrait exact, mais deux hypothèses non établies deviendraient « documentées ». Le
critère validerait le défaut au lieu de le signaler.

### Option B — Filtrer sur `confidence` ou sur `part_role` — rejetée

`confidence` est une note de l'auteur, et `part_role` un texte libre : aucun des deux n'est une
validation. Les lire reviendrait à deviner.

### Option C — Projeter, puis masquer à l'affichage les provenances non relues — rejetée

Une ligne vivante dirait « documenté » en base. Chaque lecteur (moteur, assistant, mesures) devrait
refaire le même filtre. Une seule règle, appliquée à l'écriture, évite cette duplication.

### Option D — Exiger `diagnostic_safe: true` — rejetée

`diagnostic_safe` autorise une relation à peser sur le rang (ADR-035 D4) : c'est une marche au-dessus
de la relecture. L'exiger effacerait la distinction entre « documenté » et « pondère le rang », que
D4 pose.

### Option E — Exiger `reviewed: true` à la projection — retenue

D1 à D3.

## Conséquences

### Positives

- « Documenté » exige la même relecture que le mode « créer ou remplacer » d'ADR-112 (D2).
- Les conflits nomment le premier maillon manquant, dans l'ordre de la chaîne : la capture
  (`source_not_raw_proven`), puis la relecture (`not_reviewed`). La relecture des relations déjà
  capturées devient mesurable.
- Toute provenance vivante remplit les conditions du niveau « possible » d'ADR-112 D3.

### Négatives

- Le premier run ne documente aucun lien tant qu'aucune relation capturée n'est relue (0 sur 5 au
  2026-10-11).
- Une PR monorepo et une migration de plus avant le premier run activé.

## Métriques

- Conflits `not_reviewed` par run : relations capturées, pas encore relues. À lire avec les conflits
  `source_not_raw_proven` (ADR-035 §Revue planifiée), qui comptent aussi les relations ni capturées
  ni relues.
- Lignes de provenance vivantes avec `reviewed: false` : zéro, garanti par la contrainte.

## Retour arrière

Un nouvel ADR qui retire la condition. Côté code : revert de la PR monorepo et migration inverse.

## Revue planifiée

**Date** : avec la revue d'ADR-035, J+90 après son acceptation, soit le 2027-01-02.

**Critères** :

- évolution des conflits `not_reviewed` : la relecture WIKI suit-elle la capture RAW ?
- aucune ligne vivante avec `reviewed: false`.

## Références

- [[ADR-035-diagnostic-tool-source-trust-flag|ADR-035]] ·
  [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] ·
  [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] ·
  [[ADR-113-diagnostic-coverage-target|ADR-113]]
- Monorepo : #1758 (projection WIKI → DB sous drapeau OFF, sous-module WIKI à l'export 2.0.0), #1762
  (projection câblée pour PROD, exports dans l'image)

---

*Proposé le : 2026-10-11*
*Accepté le : 2026-10-11 (fusion owner = ratification)*
