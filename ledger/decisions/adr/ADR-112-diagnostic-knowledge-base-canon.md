---
id: ADR-112
title: "Base de connaissances diagnostic — affirmations sourcées WIKI, une seule voie d'écriture, moteur déterministe plafonné par la preuve : remplace ADR-032, amende ADR-027, ADR-033, ADR-035, ADR-080 et ADR-090"
status: accepted
date: "2026-10-04"
decision_date: "2026-10-04"
decision_makers: ["@fafa"]
supersedes: ["ADR-032"]
superseded_by: []
amends: ["ADR-027", "ADR-033", "ADR-035", "ADR-080", "ADR-090"]
extends: ["ADR-031", "ADR-086"]
related_adr: ["ADR-027", "ADR-031", "ADR-032", "ADR-033", "ADR-035", "ADR-046", "ADR-059", "ADR-072", "ADR-077", "ADR-080", "ADR-083", "ADR-086", "ADR-090", "ADR-091", "ADR-093", "ADR-096"]
related_rules: ["G1", "G2", "G3", "Q1", "Q2", "AP-10"]
related_incidents: ["INC-2026-013"]
version: "1.0.0"
---

# ADR-112 : Base de connaissances diagnostic — affirmations sourcées, une seule voie d'écriture, moteur plafonné par la preuve

- **Statut** : Accepted (2026-10-04). La fusion par l'owner vaut ratification.
- **Objectif fixé par l'owner** (2026-10-04) : « une vraie base solide avec des diagnostics auto
  experts ». Cet ADR fixe comment cette base se construit, ce qu'elle a le droit d'affirmer, et comment
  le moteur s'en sert.
- **Remplace** [[ADR-032-diagnostic-maintenance-unification|ADR-032]] (resté `proposed` depuis le
  2026-04-29). Ce qui tourne déjà en est repris (§D9).
- **Amende** :
  - [[ADR-027-r5-consolidation-into-r3-s2-diag|ADR-027]] ;
  - [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] ;
  - [[ADR-035-diagnostic-tool-source-trust-flag|ADR-035]] ;
  - [[ADR-080-intent-resolution-v1-doctrine|ADR-080]] ;
  - [[ADR-090-seo-projection-forward-writer-canon|ADR-090]].

  Chaque amendement est décrit en §Amendements. Le reste de ces ADR reste en vigueur.
- **Étend** [[ADR-031-four-layer-content-architecture|ADR-031]] (RAW → WIKI → exports → DB) et
  [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] (le graphe `kg_*` est une projection,
  pas une source de vérité parallèle).
- **Méthode** : les chiffres ci-dessous ont été mesurés le 2026-10-04, en lecture seule :
  - base de données partagée DEV/PREPROD/PROD ;
  - `main` du monorepo au commit `1dfb06a93` ;
  - `main` du WIKI au commit `042e566`.

## Contexte

### État mesuré le 2026-10-04

| Élément | Constat |
|---|---|
| Vocabulaire `__diag_*` | 13 systèmes, 62 symptômes (plus une table doublon `__diag_symptoms` de 31 lignes), 58 causes |
| Liens symptôme → cause | 162 liens. `relative_score` copié d'un fichier éditorial sans source ([[2026-05-02-diagnostic-tool-unsourced-probas\|INC-2026-013]], toujours ouvert). `evidence_for` en texte libre, sans référence |
| Affichage client | L'assistant affiche `relative_score` sous la forme « NN/100 » pour chaque hypothèse (`ResultHypotheses.tsx`) |
| Autres affirmations | 21 règles de sécurité, 30 opérations d'entretien, 75 liens entretien → symptôme. Cause → pièce : constante TypeScript `CAUSE_GAMME_MAP`, aucune table. Cause → vérification : un texte libre par cause (`verification_method`) |
| Origine de toutes ces lignes | Amorce posée par migrations, aucune source citée |
| Graphe `kg_*` | 89 nœuds, 72 arêtes ; tables d'apprentissage vides. Les 19 intervalles `MaintenanceInterval` sont tous `validation_status = pending`, sans aucune source. Leur `source_type = 'oem'` vient d'une réconciliation de schéma (ADR-032, amendement du 2026-06-21), pas d'un document constructeur |
| Deux canons d'entretien servis | Le calendrier lit `kg_*` ; le moteur lit `__diag_maintenance_operation`. Les valeurs divergent : kit de distribution 120 000 km / 72 mois d'un côté, 80 000–160 000 km / 48–72 mois de l'autre ; bougies 60 000 km contre 30 000–60 000 km |
| WIKI | 4 fiches gamme (les 4 filtres) portent `diagnostic_relations`, toutes `reviewed: false` et `diagnostic_safe: false`. Aucune source capturée dans RAW |
| Chaîne WIKI → DB | Conçue et codée, rien n'est fusionné : spec #1658, tables #1659, drapeaux PROD #1661, schéma entretien #1663, writer #1669 (drapeau éteint), export WIKI #102 |
| Canon | ADR-032 et ADR-035 sont restés `proposed` depuis 5 mois. ADR-080 place l'alimentation scraping → RAW → WIKI → DB (« Block B ») en V1.1, derrière trois paliers de chiffres commerciaux |

### Ce qui manque pour une base experte

Une base experte doit pouvoir dire, pour chaque affirmation, **d'où elle vient**, **qui l'a relue** et
**à quel point elle est sûre**. Aujourd'hui, aucune ligne ne peut le dire. Le moteur classe des
hypothèses avec des chiffres sans source et les affiche comme des mesures. Personne ne peut corriger
une affirmation sans migration manuelle. Deux tables d'entretien se contredisent sur des pièces de
sécurité.

## Principe directeur

> Une affirmation de diagnostic n'entre dans la base servie que par une seule voie : sources → RAW →
> WIKI relu par un humain → projection gouvernée → `__diag_*`. Le moteur n'affirme jamais plus que ce
> que la preuve permet, il le dit en mots, et il sait dire « pas assez d'éléments ».

## Décisions

### D1 — Cinq types d'affirmations, chacun avec sa place dans le WIKI

| Affirmation | Place dans le WIKI | Cible en base |
|---|---|---|
| symptôme → cause (avec portée véhicule) | fiche gamme, `diagnostic_relations[]` (ADR-033) | `__diag_symptom_cause_link` + `__diag_link_provenance` (ADR-035) |
| cause → pièce | fiche gamme de la pièce, `diagnostic_relations[].cause_slug` (§Amendements, ADR-033) | créée par migration en phase 3 ; remplace `CAUSE_GAMME_MAP` |
| cause → vérification | fiche gamme, `diagnostic.quick_checks[]` (ADR-033 D2), rattachée à un `cause_slug` | créée par migration en phase 3 ; remplace le texte libre `verification_method` |
| règle de sécurité | entity_type `diagnostic` (ADR-031) : une entrée par règle, avec un identifiant stable | `__diag_safety_rule` |
| intervalle d'entretien | fiche gamme, `entity_data.maintenance` (bloc existant) | `__diag_maintenance_operation` |

- Le **vocabulaire** (systèmes, symptômes, causes, avec leurs slugs) reste canon en base
  (ADR-033 D2 et D5). Il est exporté vers le WIKI (`diag-canon-slugs.json`). Un terme nouveau naît par
  migration relue, jamais par le writer.
- Les règles de sécurité ne forment **jamais** un fichier par symptôme (ADR-033 D3 maintenu). Leur
  chemin exact est fixé par la PR de schéma du WIKI (phase 0).
- Les causes qui ne sont pas une pièce (réglage, condition d'usage) sont **différées**. Elles
  attendent une place dans le WIKI décidée par un ADR, qui n'est pas ouvert.

### D2 — Une seule voie d'écriture

- Le seul writer des affirmations est le module de projection d'ADR-035
  (`DiagnosticProjectionModule`, RPC `__diag_projection_apply`). Il lit l'export dérivé du WIKI ; il
  ne lit jamais RAW, ni RAG.
- Il a deux modes :
  - **rattacher** une provenance à une ligne existante (ADR-035, dès la phase 1) ;
  - **créer ou remplacer** une affirmation (à partir de la phase 3). Ce mode exige que l'entrée WIKI
    ait `reviewed: true`, un `cause_slug` explicite, des citations ancrées, et que toutes ses
    sources soient `raw_proven`.
- Il ne supprime rien. Une affirmation qui disparaît du WIKI est **retirée** (`retired_at`), son
  historique est gardé.
- Chaque exécution est observable : une ligne de run, des conflits typés, aucun saut silencieux.
- Les lignes posées par migration (l'**amorce** : 162 liens, 21 règles, 30 opérations) restent
  servies. Elles sont marquées « non sourcées » et remplacées une à une quand une affirmation sourcée
  arrive. Aucune suppression en bloc.

### D3 — Des niveaux de preuve en mots, plafonnés par la preuve

Le client voit trois niveaux, jamais un nombre :

| Niveau affiché | Plafond imposé par la preuve |
|---|---|
| **probable** | exige deux sources indépendantes et concordantes, ou une source constructeur, toutes `raw_proven`, avec `reviewed: true` et `diagnostic_safe: true` |
| **possible** | exige au moins une source `raw_proven` et `reviewed: true` ; c'est aussi le plafond de toute ligne de l'amorce |
| **à vérifier** | tout le reste |

- Le niveau affiché est le **plus bas** des deux : celui que donnent les réponses du client, et le
  plafond fixé par la preuve.
- Aucun pourcentage, aucun score sur 100 (ADR-035 D3 maintenu).

### D4 — Un moteur déterministe et explicable

- Pour chaque cause, le moteur combine les symptômes observés par un **OU bruité avec fuite** :
  - chaque lien porte une force en mots : souvent, parfois, rarement, non précisée ;
  - une **table de correspondance versionnée** traduit chaque mot en nombre, et fixe la fuite (la
    part des causes non listées) ;
  - « non précisée » prend la valeur prudente ;
  - la table vit dans le monorepo, avec ses tests, et sa version fait partie de `kb_version` (D10).
- Une réponse **négative** compte : un symptôme absent fait baisser les causes qui l'expliquent
  souvent.
- Le moteur **s'abstient** : si aucune hypothèse n'atteint « possible », ou s'il manque trop de
  réponses, il dit « pas assez d'éléments ». Il propose alors la question ou la vérification la plus
  utile.
- Mêmes entrées, même `kb_version` : même sortie, au bit près (ADR-080 §Determinism, maintenu).
- Pas d'apprentissage automatique des poids (D12).

### D5 — La sécurité est une couche séparée

- Les règles de sécurité sont évaluées **avant** le classement et **indépendamment** de lui. Une
  règle de sécurité ne dépend jamais du rang d'une hypothèse.
- Trois niveaux : **critique** (ne pas rouler), **majeure** (consulter rapidement), **mineure**.
- Une alerte critique s'affiche toujours en premier.
- Une règle de sécurité exige une source et une relecture humaine (ADR-096 : valeurs de sécurité =
  humain obligatoire).
- Sur le jeu de référence, aucune alerte critique attendue ne doit manquer (D11).

### D6 — D'abord les vérifications, les pièces en dernier

- Les vérifications sont proposées dans cet ordre :
  1. sécurité d'abord ;
  2. puis celles qui départagent le mieux les hypothèses restantes ;
  3. à utilité égale, les moins coûteuses (temps, outillage).
- Les pièces viennent en dernier, avec la mention « vérifiez avant d'acheter ».
- Une pièce n'est jamais proposée pour une hypothèse « à vérifier ».

### D7 — Codes défaut OBD

- Les codes génériques EOBD (P0xxx…) sont des **indices** qui renforcent ou affaiblissent des
  symptômes. Un code seul n'est jamais un diagnostic.
- Les codes propres à un constructeur restent hors périmètre tant qu'aucune source n'est capturée.

### D8 — Entretien : un seul canon

- **Cible** : `__diag_maintenance_operation`, alimenté par la projection à partir de
  `entity_data.maintenance` des fiches gamme, avec des intervalles en fourchette (min/max).
- `kg_*` ne reçoit **aucun nouveau writer** et **aucune nouvelle ligne**.
- Le calendrier (`/api/diagnostic-engine/calendar`) reste branché sur les RPC `kg_*` jusqu'à sa
  migration en phase 5. Cette migration se fait dans une PR distincte ; l'URL ne change pas.
- Aucune interface n'affiche « constructeur » comme origine d'un intervalle sans document constructeur
  capturé dans RAW.
- Le retrait des lignes `kg_*` est une décision owner distincte. Elle n'est pas prise ici.
- Personnalisation : par carburant (ADR-032 D2, repris). Elle se fait par famille moteur seulement si
  une famille moteur sourcée existe.

### D9 — Ce qu'on garde d'ADR-032

Restent en vigueur, comme décisions d'implémentation :

- **D2** (personnalisation par carburant) ;
- **D3** (un seul point d'entrée RPC, tant que le calendrier lit `kg_*`) ;
- l'amendement du 2026-06-21 (adaptateur `maintenance_priority`) ;
- **D9** (point d'entrée agrégé du calendrier) ;
- **D5 et D6**, tels que livrés.

Ne sont pas repris :

- **D1**, en ce qu'il fait de `kg_*` le canon de l'entretien : remplacé par D8 ;
- **D7**, en tant que source de valeurs : ses 19 intervalles restent servis sans être un canon.

Les autres objets `kg_*` (déclencheurs de sécurité, vue `v_dtc_lookup`, cas) gardent leur état. Ils ne
reçoivent aucune nouvelle écriture ; leur avenir est une décision distincte.

### D10 — Version de la base et rejeu

- `kb_version` identifie exactement l'état de la base. C'est une empreinte de :
  - la version de l'export WIKI projetée ;
  - la version de la table de correspondance (D4) ;
  - la version du moteur.
- Elle est **enregistrée dans chaque session**. Toute session peut être rejouée.
- `kb_version` entre dans l'empreinte de déterminisme d'ADR-080.

### D11 — Jeu de référence

- Le jeu de référence est un ensemble de cas experts : symptômes et véhicule, niveaux attendus,
  alertes de sécurité obligatoires.
- Chaque cas est tiré d'un document source capturé dans RAW et relu par un humain. Il n'est tiré ni
  des sessions, ni d'une invention d'agent.
- Il tourne en CI sur chaque PR qui touche le moteur, la table de correspondance ou la projection.
- **Porte bloquante** : 100 % des alertes critiques attendues sont émises.
- Les autres seuils (cause attendue dans les 3 premières, abstentions justifiées) sont fixés dans le
  fichier du jeu au moment de sa première validation. Ensuite, ils ne peuvent que monter.

### D12 — Ce qui apprend et ce qui n'apprend pas

- Les sessions et les retours clients servent à **mesurer**. Ils ne modifient jamais une force, un
  niveau ou une règle.
- Un agent ou un LLM peut **proposer** une affirmation candidate dans `proposals/` du WIKI, avec des
  citations ancrées. Il ne valide rien et n'écrit pas en base. Il ne bascule jamais `reviewed` ni
  `diagnostic_safe`.
- RAG n'a aucune autorité d'écriture (ADR-046, ADR-031).
- La relecture automatique ne s'applique qu'aux cas déjà couverts par
  [[ADR-093-auto-review-earn-gate|ADR-093]]. Elle ne s'étend jamais aux règles de sécurité.

### D13 — Phases et portes

| Phase | Contenu | Porte de sortie |
|---|---|---|
| 0 — Canon | cet ADR et ADR-035 acceptés ; retrait de l'assistant de tout nombre par lien (score « NN/100 », barre, sous-scores), comme l'exige ADR-035 D3 ; PR de schéma WIKI (§Amendements, ADR-033), migration `label_aliases` et validateur | plus aucun nombre par lien dans l'assistant en PROD ; schéma fusionné, validateur vert |
| 1 — Provenance | chaîne #1658, #1659, #1661, #1663, #1669 et WIKI #102 fusionnée, drapeaux éteints ; premier run activé par l'owner | résultat honnête attendu par ADR-035 D6 |
| 2 — Sources | capture RAW pour un système pilote, par le pilote diagnostic d'ADR-096 ; propositions WIKI relues | au moins une affirmation projetée avec une provenance vivante |
| 3 — Créer et remplacer | mode « créer ou remplacer » du writer (D2) ; tables cause → pièce et cause → vérification | jeu de référence du système pilote validé ; 100 % des alertes critiques |
| 4 — Moteur | D3 à D7 derrière un drapeau ; `kb_version` par session ; comparaison avec le moteur actuel sur le jeu de référence et sur les sessions enregistrées | seuils du jeu atteints ; bascule par l'owner |
| 5 — Entretien | calendrier migré vers `__diag_maintenance_operation` aux intervalles sourcés | valeurs sourcées pour chaque intervalle affiché |

- Chaque phase passe par ses propres PR.
- Restent des décisions de l'owner :
  - l'application d'une migration ;
  - l'activation d'un drapeau en PROD ;
  - le tag de production.
- Tout changement de contenu indexé passe par une PR distincte, en zone STOP owner (SEO).
- Les fiabilités fixes affichées sur les pages indexées `/diagnostic-auto` et `/diagnostic-auto/*`
  (« Fiabilité 60 % / 85 % / 95 % », « 95 % de fiabilité ») sont des nombres sans source, de même
  nature. Leur retrait est une de ces PR distinctes, ouverte dès la phase 0. Les meta et les H1 n'en
  font pas partie.

### D14 — Clôture d'INC-2026-013

L'incident se clôt quand les trois conditions sont vérifiées en PROD :

1. aucun score, pourcentage ou sous-score sans source n'est affiché, ni dans l'assistant, ni sur
   `/diagnostic-auto` et `/diagnostic-auto/*` ;
2. chaque hypothèse affichée porte son niveau de preuve (D3) ;
3. chacun des 162 liens a soit une provenance vivante, soit le marquage « non sourcé », plafonné à
   « possible ».

La clôture est actée par une PR vault sur l'incident.

### D15 — Rapport avec ADR-080 et ADR-077

- L'alimentation de la base (le « Block B » d'ADR-080) n'attend plus les paliers V1A, V1B et V1.1.
  Elle avance selon les phases de D13. La couche d'intention et de commerce d'ADR-080 garde ses
  paliers.
- Aucune porte d'[[ADR-077-diagnostic-cp-v1-evidence-gates|ADR-077]] n'est déclenchée :
  - pas d'extraction du moteur (G1) ;
  - pas de journal de divergence `kg_*` (G6) ;
  - pas de pré-remplissage de l'assistant (G9) ;
  - pas de changement du cookie VehicleContext (G10).

  La phase 4 modifie le calcul à l'intérieur des services existants.

## Amendements

### ADR-033 (contrat WIKI des relations)

Champs ajoutés au bloc `diagnostic_relations[]`, tous optionnels sauf mention contraire :

- `cause_slug` : clé vers `__diag_cause.slug`.
  - **obligatoire** pour le mode « créer ou remplacer » (D2) ;
  - le mode « rattacher » garde la résolution actuelle par `CAUSE_GAMME_MAP`. Cette constante devient
    vérifiée contre le WIKI, puis remplacée en phase 3.
- `evidence.strength` : souvent, parfois, rarement, non précisée (D4).
- `vehicle_scope` : carburant, ou famille moteur sourcée. Références canon uniquement.
- `citations[]` : ancrées dans RAW (identifiant de source, emplacement, empreinte de l'extrait).
  **Obligatoires** pour le niveau « probable » et pour le mode « créer ou remplacer ».

Autres changements :

- `label_aliases` sur `__diag_symptom` (prévu par ADR-033 D4, absent de la base) est introduit en
  phase 0, par migration relue.
- D3, troisième ligne : le moteur diagnostic est désormais régi par cet ADR.

### ADR-035 (provenance)

- **D2** : à partir de la phase 3, le writer gagne le mode « créer ou remplacer », aux conditions de
  D2 ci-dessus. Avant la phase 3, ADR-035 D2 s'applique tel quel.
- **D4** : à partir de la phase 4, la pondération 100/0 est remplacée par les niveaux plafonnés de D3.
  La condition `diagnostic_safe: true` reste exigée pour « probable ».
- **D3** s'applique dès l'acceptation : le retrait de l'affichage des nombres par lien fait partie de
  la phase 0 (D13).
- Tout le reste d'ADR-035 est maintenu.

### ADR-027 (S2_DIAG)

- « INPUT A autoritaire » (`__diag_*`) désigne l'**autorité de structure** : quel symptôme, quelle
  cause, quel système. Ce n'est pas un certificat de preuve.
- Tout lien affiché porte son niveau de preuve (D3).
- Changer le contenu S2_DIAG indexé est une PR distincte, en zone STOP owner.

### ADR-090 (writer de projection SEO)

- La puce « Fallback S2_DIAG observable » de §E se lit selon la correction du 2026-07-07 d'ADR-027 :
  le contenu S2_DIAG existant peut rester servi tel quel, mais `get_observable_symptoms_for_gamme`
  n'est jamais une source de nouvelle S2_DIAG canonique.
- Retirer ce repli du code est une PR distincte, en zone STOP owner (SEO).

### ADR-080 (intention V1)

- Le Block B (scraping → RAW → WIKI → DB) est détaché des paliers V1A, V1B et V1.1 (D15).
- `kb_version` entre dans l'empreinte de déterminisme (D10).
- Les résultats (`outcomes`) servent à mesurer, jamais à modifier un poids ; c'est déjà ce que posent
  les interdits V1A.x.
- La description de R5 en §1 (pages d'acquisition indexables), périmée depuis les redirections
  d'ADR-027, n'est pas traitée ici.

## Ce que cet ADR ne fait pas

- Il ne crée aucune table, aucune migration et aucun code. Chaque phase passe par ses PR.
- Il ne supprime ni ne vide aucune table, ni `kg_*`, ni l'amorce `__diag_*`.
- Il ne change aucune URL, aucun meta, aucun H1, et aucune page indexée.
- Il ne bascule aucune entrée WIKI en `reviewed` ou `diagnostic_safe`.
- Il ne donne aucun rôle à RAG.
- Il ne décide pas du sort des objets `kg_*` hors entretien.

## Options considérées

### Option A — Garder `kg_*` comme canon de l'entretien (ADR-032) — rejetée

Ses 19 intervalles sont en attente de validation, sans source, et contredits par une seconde table
servie. Le garder fige deux canons au lieu d'un.

### Option B — Réseau bayésien ou poids appris — rejetée

Aucune donnée de résultat (tables d'apprentissage vides). Le comportement serait inexplicable pour le
client et contraire au déterminisme d'ADR-080. L'OU bruité de D4 en est la forme explicable, sans
apprentissage.

### Option C — Base rédigée par un LLM — rejetée

Invention de contenu, contraire à ADR-031 et ADR-046. Un LLM ne peut que proposer (D12).

### Option D — Garder `relative_score` et l'ajuster à la main — rejetée

C'est la cause d'INC-2026-013 : des chiffres sans source affichés comme des mesures.

### Option E — Affirmations sourcées WIKI et moteur déterministe plafonné par la preuve — retenue

D1 à D15. Elle étend la chaîne déjà codée (ADR-035), garde ce qui tourne, et rend chaque affirmation
vérifiable.

## Conséquences

### Positives

- Chaque affirmation dit d'où elle vient, qui l'a relue, et à quel point elle est sûre.
- Le client ne voit plus de faux chiffres. Il voit des niveaux honnêtes, des alertes de sécurité en
  premier, et des vérifications avant les achats.
- Une correction passe par le WIKI, sans migration manuelle.
- Un seul canon d'entretien, à terme.

### Négatives

- Au démarrage, presque tout est « à vérifier » ou « possible » : la base dit honnêtement qu'elle n'est
  pas encore sourcée.
- La capture des sources (phase 2) est le travail le plus long, et rien ne la remplace.
- Le calendrier reste sur des valeurs non sourcées jusqu'à la phase 5.

### Priorité

Fusionner cet ADR décide aussi que la base avance sans attendre les paliers commerciaux d'ADR-080 (D15).

## Métriques

- Nombre d'affirmations par niveau (probable / possible / à vérifier), par système.
- Conflits `source_not_raw_proven` et leur baisse au fil de la capture RAW.
- Part de l'amorce encore « non sourcée ».
- Résultats du jeu de référence à chaque PR concernée.
- Taux d'abstention.
- Nombres par lien affichés : la cible est zéro.

## Retour arrière

- Chaque phase se coupe par son drapeau (ADR-035 D5, et le drapeau moteur de la phase 4).
- Le moteur actuel reste en place jusqu'à la bascule de la phase 4.
- Aucune donnée n'est supprimée : un retour arrière ne perd rien.

## Revue planifiée

**Date** : J+90 après acceptation.

**Critères** :

- phase atteinte ;
- affirmations sourcées par système ;
- état de chacune des trois conditions de D14.

## Références

- [[ADR-031-four-layer-content-architecture|ADR-031]] · [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] ·
  [[ADR-035-diagnostic-tool-source-trust-flag|ADR-035]] · [[ADR-046-r-stack-single-generator-and-layers|ADR-046]] ·
  [[ADR-059-seo-runtime-projection|ADR-059]] · [[ADR-077-diagnostic-cp-v1-evidence-gates|ADR-077]] ·
  [[ADR-080-intent-resolution-v1-doctrine|ADR-080]] · [[ADR-083-tiered-wiki-promotion|ADR-083]] ·
  [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] · [[ADR-093-auto-review-earn-gate|ADR-093]] ·
  [[ADR-096-governed-automatic-source-discovery|ADR-096]]
- Incident : [[2026-05-02-diagnostic-tool-unsourced-probas|INC-2026-013]]
- Monorepo : spec #1658, tables #1659, drapeaux #1661, schéma entretien #1663, writer #1669 ; WIKI : export #102

---

*Accepté le : 2026-10-04 (fusion owner = ratification)*
