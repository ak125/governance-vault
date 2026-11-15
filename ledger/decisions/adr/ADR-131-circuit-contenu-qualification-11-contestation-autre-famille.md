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
version: "0.2.0"
---

# ADR-131 : qualification du 11 et contestation par une autre famille, avant la promotion WIKI

- **Statut** : Proposed (2026-11-15). Rédigé par un agent (Claude Code CLI, machine DEV) sur mandat
  de l'owner (« Circuit du contenu : qualification du 11 et contre-relecture Codex »), complété le
  même jour (« corroboration par un second domaine d'autorité », D9 et D10). La ratification
  (`accepted`) et la fusion sont des actes réservés à l'owner
  ([[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]],
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]]).
- **Amende** [[ADR-114-wiki-safety-auto-gate|ADR-114]] (D2, D3) et
  [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] (D2, D3, D4) sans réécrire leur
  texte. Le commit de ratification ajoute `"ADR-131"` à leur `amended_by` (ADR-114 porte déjà
  `"ADR-119"`).
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

Décisions de Marwane du 15 nov. 2026 (heure de Paris), citées mot pour mot, qui fondent D9 et D10 :

- à 14:55 : « Pas de relecture humaine car impossible trop long mais autoreview avec comparaison sur
  autre domaine d'autorité pour confirmer » ;
- à 15:02 : « Justement c'est pour cela que le scraping doit être fait plusieurs fois jusqu'à
  atteindre le score ou autre qui satisfait ».

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
4. Une affirmation de profondeur `complete` peut être conservée sur une seule capture : rien n'exige
   qu'un second domaine d'autorité la confirme, ni ne relance la recherche quand il manque.

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
| Qualification | le 11, par le skill `qualification-technique` du WIKI | la justesse technique de chaque affirmation : **affirmation, source, portée, limite, verdict** (`conserver`, `preciser`, `reformuler`, `retirer`) | artefact `technical-qualification` (v1, v2 dès le skill 0.3.0), rôle `qualification` |
| Contestation | Codex, ou tout modèle d'une famille différente de celle du producteur et de celle du 11 | indépendamment : la fiche (auto-review de sens d'ADR-119 D2, passes et réfutateurs répartis entre familles) et la qualification du 11 (position `agree`, `contest` ou `undecidable` par affirmation, et affirmations oubliées) | artefact `semantic-review/v1` ; artefact `technical-qualification` (v1 ou v2), rôle `contestation` |
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
  artefact `technical-qualification` (v1 ou v2), `producer.provider` avec la base de cette déclaration
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

### D9 — Corroboration par un second domaine d'autorité (point i)

- **Règle, en profondeur `complete`** :
  - `conserver` exige une capture de rôle `proof` (`source_type_editorial_role` du catalogue) et au
    moins une capture d'un **autre domaine d'autorité**, concordantes sur la valeur et sur la portée ;
  - une seule source, ou un seul domaine : `preciser`, la portée bornée à cette source ;
  - une discordance entre domaines : `retirer` si elle touche une valeur, une procédure ou la
    sécurité, `preciser` sinon.

  En profondeur `allegee`, rien ne change : la corroboration est consignée, rien n'est déclassé.
- **Le domaine est une classe d'éditeur**, calculée hors du modèle depuis les métadonnées du
  catalogue (`_meta/source-catalog.yaml`), comme le plancher de D4 :
  - constructeur (`oem_manual`, `oem_workshop` publiés par le constructeur du véhicule) ;
  - fabricant ou équipementier de la pièce ;
  - référentiel technique (`tecdoc_official`, `parts_feed_certified`) : il corrobore, il ne fournit
    jamais la capture `proof` ;
  - formation et documentation pédagogique (`brochure`, `formation`).

  Deux captures du même éditeur, ou dont l'une reprend l'autre, comptent pour un seul domaine. Une
  capture sans classe déclarée ne compte pour aucun domaine (fail-closed). Le choix entre trois
  définitions est au point i des Options.
- **Partage des tâches** :
  - le modèle lit les passages et déclare la concordance, l'objet d'une discordance et un éventuel
    déclassement de son fait ;
  - un contrôle déterministe recalcule les domaines, les captures et la preuve, et remplace ce que le
    modèle a écrit. Il déclasse un `conserver` non confirmé, consigné `declassed_by: control` avec
    le verdict d'origine, et refuse un artefact `technical-qualification/v2` incohérent. Le schéma v2
    refuse aussi un `conserver` `complete` sans preuve, sans deux domaines ou sans concordance ;
  - la reprise d'une capture par une autre ne se lit pas dans les métadonnées. La qualification la
    signale ; le contestataire la vérifie (`checks.independence`). Un `fails` impose `contest` sur un
    `conserver` `complete`, donc le blocage de D3.
- **Prérequis au câblage** : le catalogue ne porte pas la classe d'éditeur. Son champ `type`
  confond constructeur et équipementier : Filtron, MAHLE, ZF, Brembo et Delphi sont `oem_manual`,
  comme Renault. Une PR WIKI ajoute un champ `publisher_class` aux entrées du catalogue, qui reste la
  source unique ; aucune table parallèle. D'ici là, aucune capture n'a de domaine, et la règle
  déclasse tout `conserver` `complete`.
- **Aucune relecture humaine** n'est une condition (ADR-119 D1, maintenu). La confirmation par un
  second domaine est l'autoreview que l'owner a décidée le 15 nov. 2026 à 14:55. Elle durcit la
  qualification du 11 ; elle ne remplace ni la contestation (D2, D5) ni l'auto-review de sens.

### D10 — Reprise jusqu'à la corroboration, bornée (point j)

- **Score** : la part des affirmations `complete` confirmées par deux domaines (`conserver`, preuve,
  au moins deux domaines, concordance). Il se calcule hors du modèle, depuis l'artefact.
- **Questions de reprise** : chaque affirmation `complete` non confirmée reçoit une question ciblée
  dans l'artefact (`retake_questions`). La question porte son motif (`single_domain`, `no_capture`,
  `discordant`) et les domaines déjà présents. Elle est rédigée par le modèle ; à défaut, un gabarit
  la remplace, consigné comme tel.
- **Reprise** : un run `RUN_TARGETED_RAW_TO_WIKI` sur ces questions seulement, plus profond et non
  plus large (seo-content-loop, étapes 1 et 5). Il produit de nouvelles captures RAW, puis une
  nouvelle fiche, une nouvelle clé (D1), une nouvelle qualification et une nouvelle contestation.
  Aucun artefact antérieur n'est remplacé ; un FAIL reste un FAIL (D3).
- **Arrêt**, selon l'itération bornée de seo-content-loop §5. La boucle s'arrête :
  - quand la cible est atteinte ;
  - quand une reprise ne fait pas progresser le score ;
  - ou quand le maximum de reprises est atteint.

  Le lot est alors livré `à revoir`, avec ses questions restantes. La cible et le maximum sont au
  point j des Options.
- **Rien de non confirmé n'est publié tel quel.** À l'arrêt, une affirmation non confirmée est soit
  bornée à sa source (`preciser`), soit retirée. D4 reste inchangé : en profondeur `complete`, un
  `preciser` bloque. Une affirmation bornée reste donc bloquante tant qu'un second domaine ne la
  confirme pas. La fiche est alors promue sans elle, ou elle ne l'est pas. Rendre publiable une
  affirmation bornée à une seule source assouplirait D4 ; ce choix revient à l'owner (Inconnues).

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
- D1 maintenu : la corroboration par un second domaine (D9) et la reprise (D10) sont des
  auto-reviews ; aucune relecture humaine n'est une condition.
- D4(e) complété par le jeu de D6. La levée du verrou par `SAFETY_AUTO_APPROVAL_ADR = "ADR-119"` reste
  régie par ADR-119 D4 ; cet ADR n'en lève aucun.

## Ce que cet ADR ne fait pas

- Il ne câble rien dans `promotion_decision.py`, ne lève aucun verrou et n'active aucune condition.
- Il n'écrit rien en base, n'active rien en PROD et ne modifie aucune page ni aucune fiche.
- Il ne rend aucune relecture humaine nécessaire (ADR-119 D1, maintenu) et ne donne aucune autorité
  de fond à `editorial-review.md`.
- Il ne fixe aucun seuil de part retrouvée.
- Il ne pose pas `publisher_class` dans le catalogue, n'ajoute aucune capture et ne lance aucune
  reprise (D9, D10).
- Il ne traite ni le lot FH-004 ni l'auteur éditorial.

## Mise en œuvre

Candidats préparés dans la PR WIKI en brouillon de ce mandat, non câblés :

- `_meta/skills/qualification-technique/SKILL.md` (`status: candidate`, `wired: false`) : méthode,
  plancher, invites de qualification et de contestation ;
- `_meta/schema/technical-qualification-run.schema.json` (`technical-qualification/v1`, puis `v2` en
  0.3.0 : corroboration par affirmation, domaines des captures, questions de reprise) et ses tests ;
- `_scripts/technical_qualification.py` : domaine de chaque capture sous les trois définitions du
  point i, application et contrôle de la règle de D9, questions de reprise, score et arrêt de D10 ;
  tests dans `_scripts/test_technical_qualification.py` ;
- `_scripts/semantic_review_executor.py` : plusieurs fournisseurs (`--reviewer MODÈLE COMMANDE`), même
  isolement (entrée standard seule, aucun outil, aucun MCP, aucune session), passes et réfutateurs
  répartis à tour de rôle ; tests dans `_scripts/test_semantic_review.py` ;
- les artefacts d'étalonnage, sous `_audit/technical-qualification/calibration-20261115/`.

Après ratification : une PR WIKI câble D3 dans le décideur (tests : artefact absent, périmé,
incomplet, en erreur, sans contestation, contestation de même famille, producteur inconnu, FAIL non
remplaçable, `conserver` `complete` sans second domaine), d'abord en report-only, puis bloquante une
fois l'étalonnage consigné. Avant elle, la PR WIKI qui pose `publisher_class` dans le catalogue (D9).

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

### Point i — définition du domaine d'autorité

Les trois définitions sont calculées par le même module, sur les captures des trois cas d'étalonnage
(Étalonnage candidat) :

| Définition | Filtre à huile (Renault, Filtron, MAHLE) | Plaquette (ZF, Brembo ×3, Delphi, Wikipedia) | Défaut |
|---|---|---|---|
| I1 — classe d'éditeur | 2 domaines : constructeur, équipementier | 1 domaine : équipementier ; Wikipedia sans classe | demande `publisher_class` au catalogue |
| I2 — `source_type` de `_meta/source-policy.md` | 1 domaine : tout est `oem_manual` | 2 domaines, dont `wiki_externe` (Wikipedia) | confond constructeur et équipementier ; une encyclopédie devient un second domaine |
| I3 — hôte web | 3 domaines | 4 domaines : zf, bremboparts, delphiautoparts, wikipedia | un éditeur sur deux hôtes compte deux fois ; une reprise sur un autre hôte aussi |

- **I1 — classe d'éditeur — retenue.** Elle sépare ce que le métier sépare (le constructeur du
  véhicule, le fabricant de la pièce, le référentiel, la pédagogie) et compte un éditeur une seule
  fois, quel que soit son hôte. Elle demande un champ que le catalogue n'a pas (prérequis de D9).
- **I2 — `source_type` — rejetée.** Le type mesure un plafond de confiance et un rôle éditorial, pas
  une indépendance. Sur le filtre, il ne voit qu'un domaine là où il y a un constructeur et deux
  équipementiers. Sur la plaquette, il fait de Wikipedia, de rôle `corroboration`, le second domaine
  de cinq captures d'équipementiers.
- **I3 — hôte web — rejetée.** Elle compte l'adresse, pas l'éditeur. Un éditeur publié sur deux
  hôtes compte deux fois, et un texte repris sur un autre hôte aussi : elle ne voit aucune reprise.
  Les captures des trois cas ne contiennent pas d'éditeur sur deux hôtes (les trois captures Brembo
  sont sur `bremboparts.com`) ; ce défaut n'est montré que par le test du module. Sur ces cas, I3
  revient à compter chaque éditeur : sur la plaquette, 9 des 10 affirmations qu'elle confirmerait
  reposent sur deux équipementiers concurrents, et la dixième sur Brembo et Wikipedia.

### Point j — cible et maximum de la reprise

Le dernier tour d'une boucle ne change pas ce qui est publié : à l'arrêt, une affirmation non
confirmée est bornée ou retirée (D10). La cible et le maximum ne décident que du moment où la
recherche s'arrête.

- **J1 — Cible 100 %, maximum fixé par le brief du run et consigné — retenue.** La cible est la règle
  elle-même : toute affirmation `complete` confirmée. Le maximum suit seo-content-loop §5, qui le
  laisse au brief ; l'arrêt sur non-progression s'applique toujours. Aucune constante n'est
  inventée.
- **J2 — Cible 80 %, maximum 3 reprises — rejetée.** Ni 80 % ni 3 n'ont de base : l'étalonnage du
  2026-11-15 ne mesure que le tour 0, et son score est nul pour les trois cas. Une cible sous 100 %
  arrête la recherche plus tôt sans rien publier de plus.
- **J3 — Cible 100 %, maximum de 2 reprises fixé par cet ADR — rejetée pour l'instant.** Le nombre
  est simple à contrôler, mais il est sans base tant qu'aucune reprise n'est mesurée. Un maximum se
  fixera par ADR une fois des reprises étalonnées.
- **J4 — Sans cible ni maximum, arrêt sur non-progression seule — rejetée.** La boucle n'est pas
  bornée, contrairement à seo-content-loop §5.

## Conséquences

### Positives

- Une fois D3 câblé, chaque affirmation qui atteint une page porte une source, une portée et une limite
  consignées.
- Les biais d'une famille de modèles sont contestés par une autre.
- La profondeur suit le risque par une règle déterministe, durcissable sans ADR.
- Une fois D9 câblé, une affirmation `complete` conservée est confirmée par deux classes d'éditeurs,
  dont l'une prouve ;
  ce qui manque devient une question de reprise ciblée, pas une recherche au hasard.

### Négatives

- Coût : deux exécutions de plus par fiche, et une seconde famille de modèles à maintenir.
- Une fiche peut rester bloquée tant qu'une capture ne tranche pas une affirmation `undecidable`.
- Une nouvelle révision du skill change la clé et demande une nouvelle qualification de chaque fiche.
- Tant que `publisher_class` manque au catalogue, aucune affirmation `complete` n'est conservée.
- Une fiche dont toutes les captures viennent d'une même classe (la plaquette : cinq captures
  d'équipementiers) reste bloquée tant qu'aucune capture d'un autre domaine n'est ajoutée. Chaque
  reprise coûte un run de recherche, une fiche, une qualification et une contestation.

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

Le skill 0.3.0 (corroboration, D9) a été relancé sur les trois cas, avec de nouvelles clés ; aucun
résultat de 0.1.0 ou 0.2.0 n'est remplacé. Le domaine suit I1, sous une hypothèse : le catalogue n'a
pas `publisher_class`, et l'étalonnage lui applique une classe posée hors du dépôt (Renault
constructeur ; Filtron, MAHLE, ZF, Brembo, Delphi équipementiers ; Wikipedia sans classe). Seul le
tour 0 de la boucle est mesuré : aucune capture n'est ajoutée (D10).

| Cas | Affirmations `complete` | Part retrouvée | Déclassées faute de second domaine | Score |
|---|---|---|---|---|
| Filtre, consignes retirées | 12 : 4 `preciser`, 8 `retirer` | 6 sur 6 | 0 | 0 sur 12 |
| Cinq paires | 8 : 7 `preciser`, 1 `retirer` | verdicts plus stricts que le 11, comme en 0.2.0 | 2, par le modèle | 0 sur 8 |
| `plaquette-de-frein@88f9f88` | 93 : 90 `preciser`, 2 `retirer`, 1 `reformuler` | Q5 en partie ; sens 8 sur 8 ; formulation 6 sur 12 | 40, par le modèle | 0 sur 93 |

- Le contrôle déterministe n'a déclassé aucune affirmation : le modèle a appliqué la règle lui-même,
  et aucun artefact ne contient de violation.
- Q5 (body:52) : `preciser`, mais la limite nomme les essais à vitesse réduite et le rodage, pas le
  mauvais montage ni la pression instable à la pédale. La 0.2.0 la retrouvait en entier.
- Sous I2, une affirmation de la plaquette serait confirmée, avec Wikipedia pour second domaine. Sous
  I3, une des cinq paires (Filtron et MAHLE) et dix de la plaquette le seraient, dont neuf par deux
  équipementiers concurrents.
- Le défaut resté ouvert en 0.2.0 est masqué, pas corrigé. Plusieurs affirmations déclassées depuis
  `conserver` ont une limite qui décrit un écart de fond (`entity_data` « signal sonore » et « en
  principe », une paire de L155). Sous 0.3.0, elles finissent en `preciser` faute de second domaine ;
  sur ces cas, le verdict ne distingue plus l'affirmation exacte et bornée de l'affirmation à
  corriger : la différence ne se lit que dans la limite.
- Chaque affirmation non confirmée a sa question de reprise, rédigée par le modèle : 12, 8 et 93.

La qualification 0.3.0 a ensuite été contestée par `gpt-5.6-sol`, de la famille openai, avec la
commande et l'isolement de la contestation de la 0.2.0. Chaque artefact désigne la qualification par
son empreinte et partage sa clé.

| Cas | `agree` | `contest` | `undecidable` | Oubliées | Contestation de la 0.2.0 |
|---|---|---|---|---|---|
| Filtre, consignes retirées | 12 | 0 | 0 | 0 | 4 / 0 / 7 / 0 sur 11 |
| Cinq paires | 4 | 3 : 2 plus strictes, 1 sur la limite | 1 (`retirer`) | 1 | 7 / 1 / 0 / 0 sur 8 |
| `plaquette-de-frein@88f9f88` | 78 | 15 : 12 plus souples, 2 plus strictes, 1 sur la limite | 0 | 6 | 95 / 11 / 1 / 6 sur 107 |

- Défauts masqués : sur les cinq affirmations relevées plus haut, la contestation en sépare une par
  son verdict (L155, `retirer`). Elle en nomme deux dans son motif tout en restant `agree` sur
  `preciser` (« en principe », ECE R90), en voit une en partie (« signal sonore ») et en conteste
  une vers `conserver`. D'autres `agree` sur `preciser` décrivent une contradiction dans leur motif
  (le « Oui » sur le témoin d'usure). Le défaut reste masqué dans les verdicts des deux familles.
- Q5 (body:52) : `agree` sur `preciser`. Le mauvais montage et la pression instable ne sont pas
  retrouvés.
- Les 12 contestations plus souples demandent `conserver` pour des affirmations déclassées faute de
  second domaine : l'invite de contestation 0.3.0 ne rappelle pas la règle de D9. D3 retient le
  verdict le plus strict ; elles ne lèvent aucun blocage.
- Aucune affirmation n'est déclarée sur deux domaines : les vérifications de concordance et
  d'indépendance (`checks`) ne sont pas exercées.

Le skill 0.3.1 (complément n° 4 au mandat S) cite à l'identique la règle de D9 dans l'invite de
contestation ; l'invite de qualification ne change pas. D1 en fait une nouvelle clé : ces
contestations ne forment pas une paire de décision avec la qualification 0.3.0 (D3). Ce sont des
mesures d'étalonnage, et aucun artefact n'est remplacé. Les 12 affirmations contestées vers
`conserver` ont été recontestées par `gpt-5.6-sol`, sur les deux segments qui les portent, avec une
invite figée avant l'envoi (`3dd039f2…`, 133 605 octets). Il y a eu deux tirages 0.3.1 et un témoin
sous l'invite 0.3.0, avec le même paquet.

| Exécution | Les 12 affirmations |
|---|---|
| Contestation 0.3.0, fiche entière | 12 `contest` vers `conserver` |
| Témoin : invite 0.3.0, deux segments | 12 `agree` sur `preciser` |
| 0.3.1, tirage 1 | 12 `agree` sur `preciser` |
| 0.3.1, tirage 2 | 12 `agree` sur `preciser` |

- Le témoin rend le même résultat sans la citation. L'écart avec la contestation 0.3.0 vient donc du
  paquet (fiche entière en lots, contre deux segments) ou de la variance. La citation de D9 n'en est
  pas la cause démontrée.
- Au tirage 2, 10 motifs sur 12 invoquent la règle ; au témoin, 5 sur 12. Au tirage 1, `statement`
  recopie le texte de l'affirmation au lieu d'en donner le motif.
- Les défauts masqués le restent dans les verdicts. Pour « marques de qualité », la contestation
  passe de `contest` vers `conserver` à `agree` sur `preciser`.
- Aucune affirmation n'est toujours déclarée sur deux domaines : la concordance et l'indépendance ne
  sont toujours pas exercées. Elles le seront sur les cas du mandat AC.

## Inconnues

- Une affirmation bornée à une seule source (`preciser`) bloque en profondeur `complete` (D4, D10).
  L'owner tranche à la ratification : laisser D4 tel quel (la fiche est promue sans l'affirmation),
  ou rendre publiable une affirmation explicitement attribuée à sa source, ce qui assouplit D4.
- Deux équipementiers concurrents (Filtron et MAHLE) forment un seul domaine sous I1. Rien ne dit
  encore s'ils doivent compter pour deux quand ils publient chacun leur propre essai.
- La reprise d'une capture par une autre n'est vue que par des modèles (qualification et
  contestation), pas par un contrôle déterministe.
- Le nombre de reprises nécessaire à une fiche réelle : aucune reprise n'est encore mesurée.
- Quand toutes les affirmations finissent en `preciser`, le verdict ne sépare plus une affirmation
  exacte mais seule d'une affirmation à corriger (Étalonnage candidat, 0.3.0). La contestation par
  une autre famille ne le sépare pas davantage : elle voit l'écart dans ses motifs, mais une fois
  seulement dans son verdict. Rien ne dit encore si la reprise doit commencer par ces affirmations, ni
  si le skill doit garder les deux motifs distincts.
- L'effet de la citation de D9 dans l'invite de contestation (skill 0.3.1, complément n° 4 au mandat
  S) : sur les deux segments recontestés, le témoin sans citation rend le même résultat. L'effet sur
  une fiche entière, et ce que porte `statement` dans une position, restent à mesurer.
- Les vérifications de concordance et d'indépendance par le contestataire : aucun cas de
  l'étalonnage ne déclare deux domaines, elles n'ont toujours pas tourné, 0.3.1 comprise. Elles le
  seront sur les cas du mandat AC.
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
