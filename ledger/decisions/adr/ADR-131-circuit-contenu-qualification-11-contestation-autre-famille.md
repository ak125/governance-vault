---
id: ADR-131
title: "Circuit du contenu : qualification technique de la fiche WIKI par le 11 avant la promotion, contestation par une autre famille de modèles, profondeur selon le risque : amende ADR-114 et ADR-119"
status: proposed
date: "2026-11-15"
decision_date: ""
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-114", "ADR-119"]
extends: []
related_adr: ["ADR-031", "ADR-046", "ADR-093", "ADR-102", "ADR-107", "ADR-111", "ADR-114", "ADR-119", "ADR-121", "ADR-125"]
related_rules: ["G1", "G4"]
related_incidents: []
reviewed_by: ""
version: "0.1.0"
---

# ADR-131 : qualification du 11 et contestation par une autre famille, avant la promotion WIKI

- **Statut** : Proposed (2026-11-15). Rédigé par un agent (Claude Code CLI, machine DEV) sur mandat
  de l'owner (« Circuit du contenu : qualification du 11 et contre-relecture Codex »). La ratification
  (`accepted`) et la fusion sont des actes réservés à l'owner
  ([[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]],
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]]).
- **Amende** [[ADR-114-wiki-safety-auto-gate|ADR-114]] (D2, D3) et
  [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] (D2, D3, D4) sans réécrire leur
  texte. Le commit de ratification pose `amended_by: ["ADR-131"]` sur les deux.
- **N'active rien.** Aucune condition n'est câblée dans `promotion_decision.py`, aucun verrou n'est
  levé, aucune donnée n'est écrite en base, rien n'est activé en PROD. Les candidats (skill, schéma,
  exécuteur) sont dans une PR WIKI en brouillon, non câblés (Mise en œuvre).

## Contexte

### Les décisions de l'owner

Décisions de Marwane du 14 nov. 2026, citées mot pour mot :

- à 23:46 : « circuit va duscrapind au RAW au WIKI, puis aux pages, et il dois contenir étape où le 11
  qualifie les réponses et passe par les skill et une relecture codex » ;
- à 23:57 : « utiliser les meilleures approche les meilleures strategie les plus robuste les plus safe
  les plus moderne les meilleure solutions pas de bricolage ».

### Ce qui existe

- **Circuit** : RAW (captures brutes) → WIKI (fiche sourcée, validée par son décideur sur preuve) →
  projections → pages ([[ADR-031-four-layer-content-architecture|ADR-031]],
  [[ADR-125-amendements-cibles-coherence-wiki-seo-autorite|ADR-125]] D1). Le RAG n'a aucune autorité
  de contenu ([[ADR-046-r-stack-single-generator-and-layers|ADR-046]]).
- **Décideur unique** : `promotion_decision.py` (WIKI), ADR-114 D2.
- **Auto-review de sens** (ADR-119 D2) : au moins deux passes et trois réfutateurs par écart candidat ;
  un écart n'est écarté qu'à l'unanimité, passage cité à l'appui ; clé {empreinte du texte publié,
  captures citées, révision du protocole} ; un FAIL n'est jamais remplacé par un PASS sur la même
  clé. La condition `semantic_auto_review_pass` est bloquante pour les fiches sécurité, report-only
  ailleurs (ADR-119 D3). L'exécuteur `_scripts/semantic_review_executor.py` n'appelle qu'une seule
  commande, donc une seule famille de modèles.
- **Relecture de forme** : `.claude/prompts/_shared/editorial-review.md` (monorepo) relit un brouillon
  français. Elle n'a pas d'autorité sur le fond.
- **Le 11 (Expertise Technique Automobile)** a qualifié le 2026-11-07 cinq paires question-réponse
  de la FAQ du filtre à huile, avec une méthode écrite (fiche du département 11, doc « Départements
  AutoMecanik ») :

  > Vérifier les affirmations et conditions des réponses techniques, séparément du signal de demande.
  > Ne pas généraliser les intervalles, couples, emplacements ou gestes d'un véhicule à tous les
  > autres. Décrire les limites et les cas nécessitant une aide professionnelle. Rechercher de
  > nouvelles preuves seulement pour les faits manquants ; les sources de questions ne valent pas
  > validation des réponses qu'elles contiennent.

  Ses preuves étaient des sources web lues pendant la qualification ; aucune n'est une capture RAW
  citée par la fiche. Cette qualification ne peut donc pas être une condition de promotion telle
  quelle.
- **Producteur** : `_meta/source-policy.md` du WIKI, ligne 74, déclare le skill
  `wiki-proposal-writer` « Anthropic seul pour le texte rédactionnel ». C'est une prose ; aucun champ
  machine de la fiche ne porte la famille du producteur, et le schéma `semantic-review/v1` ne porte la
  famille d'aucun modèle.

### Ce qui manque

1. Aucune étape ne qualifie la **justesse technique** de chaque affirmation (source, portée, limite)
   avant la promotion : l'auto-review de sens vérifie la fidélité aux captures, pas les limites de
   portée ni les cas qui demandent un professionnel.
2. Toute l'auto-review peut tourner sur une seule famille de modèles, celle du producteur.
3. ADR-119 D4(e) étalonne la seule `plaquette-de-frein` ; aucune consigne retirée d'une autre fiche
   n'entre dans le jeu de référence.

## Principe directeur

> Une fiche n'atteint une page qu'une fois qualifiée affirmation par affirmation sur ses captures, et
> contestée par une famille de modèles qui ne l'a ni écrite ni qualifiée. Les artefacts sont des
> preuves que le décideur lit ; aucun d'eux n'est un décideur.

## Décisions

### D1 — Place : une qualification par fiche WIKI, avant la promotion (point a)

- Le 11 qualifie la **fiche WIKI**, une fois, avant sa promotion. Le texte qualifié est le texte publié
  défini par ADR-119 D2 (corps et toutes les chaînes du frontmatter), avec les captures RAW qu'il cite.
- Les pages R1, R3 et R4 héritent de cette qualification. Aucune page n'est requalifiée : une
  projection ne porte que ce que la fiche promue porte.
- La clé de l'artefact réunit l'empreinte du texte publié, les captures citées et l'empreinte du
  skill de qualification. Un nouveau texte, de nouvelles captures ou une nouvelle révision du skill
  font une nouvelle clé, donc une nouvelle qualification. Une page modifiée sans changer la fiche
  n'en déclenche aucune.

### D2 — Trois rôles distincts (point b)

| Rôle | Qui | Ce qu'il juge | Statut |
|---|---|---|---|
| Qualification | le 11, par le skill `qualification-technique` du WIKI | la justesse technique de chaque affirmation : **affirmation, source, portée, limite, verdict** (`conserver`, `preciser`, `reformuler`, `retirer`) | artefact `technical-qualification/v1`, rôle `qualification` |
| Contestation | Codex, ou tout modèle d'une famille différente de celle du producteur et de celle du 11 | indépendamment : la fiche (auto-review de sens d'ADR-119 D2, passes et réfutateurs répartis entre familles) et la qualification du 11 (position `agree`, `contest` ou `undecidable` par affirmation, et affirmations oubliées) | artefact `semantic-review/v1` ; artefact `technical-qualification/v1`, rôle `contestation` |
| Relecture de forme | `editorial-review.md` | la langue et la forme | inchangée, sans autorité sur le fond, n'est pas une condition |

- Le nom « 11 » désigne une méthode exécutée et versionnée (le skill), pas une personne ni un nouveau
  rôle humain. Aucune relecture humaine ne devient une condition (ADR-119 D1, maintenu).
- La transposition de la méthode du 7 nov. dans le circuit : la seule source admise est un passage
  recopié à l'identique d'une capture citée ; la connaissance propre du modèle n'est pas une source ;
  un fait manquant ne se cherche pas pendant la qualification, il donne `retirer` ou `preciser`, et la
  recherche passe par une nouvelle capture RAW puis une nouvelle fiche.

### D3 — Le décideur unique lit les artefacts comme conditions (point c)

- Une condition `technical_qualification_pass` s'ajoute au tableau d'ADR-114 D3, sur le modèle de
  `semantic_auto_review_pass` (ADR-119 D3) : nécessaire, jamais suffisante, fail-closed, recalculée par
  `promotion_decision.py` depuis les artefacts versionnés sous
  `_audit/technical-qualification/<slug>/<clé>/<sha256 du fichier>.json`.
- Elle est vraie seulement si, pour la clé de la fiche décidée :
  - un artefact de qualification et un artefact de contestation qui le désigne par son empreinte
    existent, conformes au schéma ;
  - chaque segment du texte publié (découpage déterministe d'ADR-119 D2) figure dans la qualification,
    avec ses affirmations ou la mention qu'il n'en porte aucune ;
  - aucune affirmation n'est bloquante (D4) ;
  - la condition d'indépendance (D5) et la condition de fraîcheur (D7) sont vraies.
- Une affirmation est acquise seulement si la qualification la rend non bloquante **et** si le
  contestataire est `agree`. Une position `contest` ou `undecidable`, ou une affirmation oubliée
  (`missed`) que le contestataire ne rend pas `conserver`, suit la règle de blocage de D4 avec le
  verdict le plus strict des deux.
- **Un FAIL n'est remplacé par aucun PASS sur la même clé**, quel que soit le modèle ou l'ordre des
  exécutions. Un artefact en erreur (`error`) n'est ni PASS ni FAIL : la qualification se relance
  sur la même clé.
- Les artefacts ne portent aucun verdict de fiche ni aucune approbation : le décideur les recalcule.
  Cela précise ADR-114 D2 comme ADR-119 D3 l'a fait : un artefact produit par un modèle et lu comme
  une condition bloquante n'est pas un décideur.

### D4 — Profondeur selon le risque (point d)

- L'étape s'applique à **toutes les gammes**.
- Chaque segment reçoit un **plancher déterministe**, calculé hors du modèle par des fonctions WIKI
  existantes. La profondeur est `complete` si l'une de ces règles s'applique :
  - `safety_family` : la fiche relève de la sécurité (`safety_families.py::is_safety_proposal`,
    ADR-114 D1, fail-closed) ; tous ses segments sont alors `complete` ;
  - `numeric_value` : le segment porte une valeur au sens d'ADR-114 D4 (extracteur de valeurs du
    WIKI) ;
  - `procedure` : le segment relève d'une procédure (sections « Montage », « Entretien », champs
    `replacement_guidance`, `maintenance_interval`, `maintenance`) ;
  - `diagnostic_relation` : le segment porte une relation de diagnostic (`diagnostic_relations`,
    section « Symptômes », `failure_symptoms`).
- Sinon il est `allegee` (descriptif). Le relecteur peut monter un segment (`escalated` ; un doute,
  `doubt`, vaut `complete`), jamais le descendre sous le plancher.
- **Blocage** : en profondeur `complete`, tout verdict autre que `conserver` et toute affirmation sans
  passage cité bloquent ; en profondeur `allegee`, seul `retirer` bloque, les autres verdicts sont
  consignés.
- Ajouter un motif de plancher ou rendre un verdict bloquant durcit le contrôle : PR WIKI. Retirer un
  motif ou rendre un verdict non bloquant l'assouplit : ADR (même règle qu'ADR-114 D1 et ADR-119 D2).

### D5 — Indépendance des familles (point e)

- Le contestataire vient d'une **famille de modèles différente** de celle du producteur et de celle
  du 11. Pour l'auto-review de sens d'ADR-119 D2, chaque écart candidat reçoit au moins une passe et
  au moins un réfutateur de cette autre famille ; cette exigence durcit ADR-119 D2.
- Les modèles et leurs familles sont consignés : `reviewer.model` et `reviewer.provider` dans chaque
  artefact `technical-qualification/v1`, `producer.provider` avec la base de cette déclaration
  (`producer.basis`). Pour `semantic-review/v1`, qui consigne les modèles sans leur famille, la PR qui
  versionne l'exécution déclare la famille de chaque modèle, jusqu'à une révision du schéma.
- Une famille de producteur inconnue (`unknown`) rend la condition fausse : elle ne se suppose pas.
  Au 2026-11-15, la famille `anthropic` des fiches écrites par `wiki-proposal-writer` est déclarée
  par `_meta/source-policy.md` (ligne 74).
- Le 11 peut être de la famille du producteur ; c'est le contestataire qui porte l'indépendance.

### D6 — Étalonnage avant tout blocage (point f)

- Aucune des conditions de D3 ne devient bloquante avant un étalonnage versionné dans le WIKI sur ce
  jeu :
  - les cinq paires de la FAQ du filtre à huile qualifiées par le 11 le 2026-11-07 ;
  - les consignes de `filtre-a-huile` retirées le 2026-09-30 : serrage (« visser à la main jusqu'au
    contact puis serrer d'une fraction de tour », « couple du couvercle ») et « à chaque vidange » ;
  - la question 5 de la FAQ de `plaquette-de-frein` au commit `88f9f88` (écart de sécurité confirmé
    le 2026-10-21, ADR-119 D4(e)), avec les autres écarts de ce jeu de référence.
- La part retrouvée est consignée par cas, avec les modèles, **sans seuil**. Un écart de sécurité
  connu que l'étape ne retrouve pas est consigné comme tel et s'examine avant le câblage.
- Ce jeu complète ADR-119 D4(e) ; il ne le remplace pas.

### D7 — Fraîcheur de chaque relecteur (point g)

- Chaque relecteur (qualification, contestation, auto-review de sens) lit la fiche et les captures
  **depuis `origin`** (référence et commit consignés), ou après une garde de fraîcheur
  (`check-repo-freshness.sh`, code de sortie consigné). L'artefact porte `freshness.read_from`,
  `freshness.ref`, `freshness.commit`, `freshness.raw_commit` et `freshness.checked_at`.
- La clé adressée par contenu (D1) garantit que l'artefact porte sur le texte décidé ; la consignation
  de la fraîcheur garantit que ce texte était celui d'`origin` au moment de la lecture. Un artefact
  sans preuve de fraîcheur rend la condition fausse.

### D8 — FAQ R1 : rien hors de la fiche promue (point h)

- Une réponse de FAQ R1 n'atteint une page que si elle figure dans `entity_data.editorial.selection_faq.qa`
  de la fiche WIKI promue ([[ADR-107-wiki-export-structured-lists-and-faq|ADR-107]] D2,
  [[ADR-111-r1-wiki-resourcing|ADR-111]] D3). Elle y est qualifiée et contestée comme toute
  affirmation du texte publié.
- Une formulation proposée par le 11 (`proposed_wording`) est une proposition au rédacteur, jamais une
  source ni un texte de page. Elle n'atteint une page qu'en entrant dans une fiche, qualifiée, contestée
  et promue sous une nouvelle clé.

## Amendements

### ADR-114 (Safety Auto-Gate)

- D2 précisé : les artefacts de qualification et de contestation sont des conditions lues par le
  décideur unique, pas des décideurs.
- D3 : la condition `technical_qualification_pass` (D3 du présent ADR) s'ajoute au tableau, pour
  toute fiche, sécurité comprise, une fois l'étalonnage de D6 consigné et la condition câblée par une
  PR WIKI.

### ADR-119 (auto-review de sens)

- D2 durci : au moins une passe et au moins un réfutateur de chaque candidat viennent d'une famille de
  modèles différente de celle du producteur (D5) ; les familles des modèles sont déclarées.
- D3 : `semantic_auto_review_pass` reste ; la contestation de la fiche par une autre famille en fait
  partie.
- D4(e) complété par le jeu de D6. La levée du verrou par `SAFETY_AUTO_APPROVAL_ADR = "ADR-119"` reste
  régie par ADR-119 D4 ; cet ADR n'en lève aucun.

## Ce que cet ADR ne fait pas

- Il ne câble rien dans `promotion_decision.py`, ne lève aucun verrou et n'active aucune condition.
- Il n'écrit rien en base, n'active rien en PROD et ne modifie aucune page ni aucune fiche.
- Il ne rend aucune relecture humaine nécessaire (ADR-119 D1, maintenu) et ne donne aucune autorité
  de fond à `editorial-review.md`.
- Il ne fixe aucun seuil de part retrouvée.
- Il ne traite ni le lot FH-004 ni l'auteur éditorial.

## Mise en œuvre

Candidats préparés dans la PR WIKI en brouillon de ce mandat, non câblés :

- `_meta/skills/qualification-technique/SKILL.md` (`status: candidate`, `wired: false`) : méthode,
  plancher, invites de qualification et de contestation ;
- `_meta/schema/technical-qualification-run.schema.json` (`technical-qualification/v1`) et ses tests ;
- `_scripts/semantic_review_executor.py` : plusieurs fournisseurs (`--reviewer MODÈLE COMMANDE`), même
  isolement (entrée standard seule, aucun outil, aucun MCP, aucune session), passes et réfutateurs
  répartis à tour de rôle ; tests dans `_scripts/test_semantic_review.py` ;
- les artefacts d'étalonnage, sous `_audit/technical-qualification/calibration-20261115/`.

Après ratification : une PR WIKI câble D3 dans le décideur (tests : artefact absent, périmé,
incomplet, en erreur, sans contestation, contestation de même famille, producteur inconnu, FAIL non
remplaçable), d'abord en report-only, puis bloquante une fois l'étalonnage consigné.

## Options considérées

### Point a — place de la qualification

- **A1 — Qualifier chaque page (R1, R3, R4) avant publication — rejetée.** Trois qualifications du
  même fait, divergences possibles entre pages, et une page qualifiée sur un texte que le WIKI n'a pas.
- **A2 — Qualifier la fiche WIKI une fois, avant la promotion — retenue.** Une seule vérité qualifiée,
  héritée par les projections (ADR-031).
- **A3 — Qualifier après la promotion, en contrôle a posteriori — rejetée.** Un défaut atteint une page
  avant d'être vu ; ADR-119 D5 a déjà remplacé le contrôle a posteriori par un contrôle préalable.

### Point b — rôles

- **B1 — Un seul relecteur pour le fond et la forme — rejetée.** Mêle la justesse technique et la
  langue ; une relecture de forme n'a pas de preuve à citer.
- **B2 — Codex seul, sans qualification du 11 — rejetée.** Codex conteste ; personne ne qualifie la
  portée et les limites affirmation par affirmation.
- **B3 — Trois rôles séparés : qualification, contestation, forme — retenue.**

### Point c — lecture par le décideur

- **C1 — Le skill du 11 rend un verdict de fiche que le décideur recopie — rejetée.** Un second
  décideur, contraire à ADR-114 D2.
- **C2 — Une seule condition fusionnée avec `semantic_auto_review_pass` — rejetée.** Mélange deux
  protocoles de révisions différentes dans une même clé ; un durcissement de l'un change la clé de
  l'autre.
- **C3 — Une condition distincte, recalculée depuis des artefacts versionnés, sur le modèle de
  `semantic_auto_review_pass` — retenue.**

### Point d — critère de classement de la profondeur

- **D1 — Classement par fiche (sécurité ou non) — rejetée.** Une valeur ou une procédure d'une fiche
  non sécurité serait relue en allégé, alors que le mandat la veut complète.
- **D2 — Classement par le modèle seul — rejetée.** Le modèle relu fixerait sa propre barre ; aucune
  garantie de stabilité entre exécutions.
- **D3 — Plancher déterministe par segment, montée possible par le relecteur, jamais de descente —
  retenue.** Les quatre motifs reposent sur des fonctions WIKI existantes ; le relecteur ne peut que
  durcir.
- **Allégée non bloquante (report-only) — rejetée** au profit de « seul `retirer` bloque » : une
  affirmation qu'aucune capture ne porte est déjà un écart au sens d'ADR-119 D2.

### Point e — indépendance

- **E1 — Indépendance de contexte seulement (passes séparées, même famille) — rejetée.** C'est l'état
  actuel ; les biais d'une même famille ne s'écartent pas.
- **E2 — Une autre famille pour la contestation, familles consignées, producteur inconnu
  bloquant — retenue.**
- **Famille du producteur : champ machine dans la fiche — différé.** Il demande une évolution du
  schéma de fiche ; d'ici là, la déclaration de `_meta/source-policy.md` sert de base, citée dans
  chaque artefact.

### Point f — étalonnage

- **F1 — Seuil de part retrouvée — rejetée.** Aucune base pour fixer une valeur (pas de constante
  métier inventée) ; ADR-119 D4(e) a fait le même choix.
- **F2 — Part retrouvée consignée par cas, avec les modèles, sans seuil — retenue.**
- **F3 — Jeu limité à `plaquette-de-frein` — rejetée.** Ne couvre ni les consignes de montage ni la
  FAQ R1.

### Point g — fraîcheur

- **G1 — Clé adressée par contenu seulement — rejetée.** Prouve la correspondance au texte, pas que ce
  texte était celui d'`origin`.
- **G2 — Garde de fraîcheur seulement — rejetée.** Ne lie pas l'artefact au texte décidé.
- **G3 — Clé adressée par contenu et fraîcheur consignée — retenue.**

### Point h — FAQ R1

- **H1 — La FAQ R1 vient d'une source séparée, qualifiée à part — rejetée.** Seconde source de vérité,
  contraire à ADR-107 D2 et ADR-111 D3.
- **H2 — La FAQ R1 n'entre que par `selection_faq.qa` de la fiche promue — retenue.**

## Conséquences

### Positives

- Chaque affirmation qui atteint une page porte une source, une portée et une limite consignées.
- Les biais d'une famille de modèles sont contestés par une autre.
- La profondeur suit le risque par une règle déterministe, durcissable sans ADR.

### Négatives

- Coût : deux exécutions de plus par fiche, et une seconde famille de modèles à maintenir.
- Une fiche peut rester bloquée tant qu'une capture ne tranche pas une affirmation `undecidable`.
- Une nouvelle révision du skill change la clé et demande une nouvelle qualification de chaque fiche.

### Neutres

- `editorial-review.md`, ADR-119 D1, D5 à D7 et ADR-114 D1, D4 à D8 restent inchangés.

## Étalonnage candidat du 2026-11-15

Ces résultats sont consignés dans le WIKI, sous `_audit/technical-qualification/calibration-20261115/`
(rapport et artefacts). Ils ne valident rien et ne fixent aucun seuil (D6). La qualification a tourné
sur `claude-opus-5-5`, de la famille anthropic.

- Consignes du filtre à huile retirées le 2026-09-30 : les six sont retrouvées par le skill 0.1.0
  comme par le 0.2.0. Aucune n'est conservée, et le serrage comme le couple sont retirés.
- Cinq paires du 2026-11-07 : les verdicts sont plus stricts que ceux du 11. Les sources du 11 ne
  sont pas des captures du RAW.
- `plaquette-de-frein@88f9f88`, question 5 :
  - le skill 0.1.0 la **manque** : il conclut `conserver` alors que sa limite décrit l'omission ;
  - le 0.2.0 la retrouve : il conclut `preciser`, pour le même motif que la référence.

  Écarts de sens : 7 sur 8 lignes retrouvées en 0.1.0, 8 sur 8 en 0.2.0. Écarts de formulation : 4
  sur 12 en 0.1.0 ; en 0.2.0, 2 entièrement et 2 en partie.
- Défaut resté ouvert : un `conserver` dont la limite décrit une contradiction. La contestation est
  consignée dans le même rapport.

## Inconnues

- La part retrouvée sur le jeu de D6 au-delà de l'étalonnage candidat du 2026-11-15, et la variance
  d'une exécution à l'autre (un seul modèle de qualification, une exécution par révision).
- Le coût réel par fiche en profondeur `complete` sur une fiche longue.
- La fiche du département 11 du doc de pilotage indique que « cette organisation n’ajoute pas un
  passage obligatoire du 11 à chaque modification ni un second pilotage ». D1 ajoute une
  qualification par fiche WIKI, à chaque nouveau texte de fiche. L'écart est signalé ; la décision du
  14 nov. 2026 à 23:46 est postérieure, et l'owner tranche à la ratification.

## Retour arrière

Avant fusion : fermer la PR. Après : un ADR qui remplace celui-ci ; tant que la condition n'est pas
câblée, aucun code ne dépend de cet ADR.

## Revue planifiée

À la PR WIKI qui câble D3, et au plus tard le 2027-02-15.

## Références

- [[ADR-114-wiki-safety-auto-gate|ADR-114]],
  [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]],
  [[ADR-031-four-layer-content-architecture|ADR-031]],
  [[ADR-046-r-stack-single-generator-and-layers|ADR-046]]
- [[ADR-107-wiki-export-structured-lists-and-faq|ADR-107]], [[ADR-111-r1-wiki-resourcing|ADR-111]],
  [[ADR-125-amendements-cibles-coherence-wiki-seo-autorite|ADR-125]]
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]],
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]]
- [[MOC-Decisions]]

---

*Proposé le : 2026-11-15*
*Dernière revue : 2026-11-15*
