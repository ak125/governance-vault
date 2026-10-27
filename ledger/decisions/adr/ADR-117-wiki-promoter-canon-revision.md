---
id: ADR-117
title: "Révision en place d'une fiche du canon WIKI écrite par le promoteur, jugée par le décideur unique : amende ADR-093 (L4, Humain = exception point 6) et ADR-116 (D4, Métriques, Retour arrière)"
status: accepted
date: "2026-10-22"
decision_date: "2026-10-22"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-093", "ADR-116"]
extends: []
related_adr: ["ADR-031", "ADR-033", "ADR-046", "ADR-083", "ADR-093", "ADR-112", "ADR-114", "ADR-115", "ADR-116"]
related_rules: ["G1", "G6", "Q1", "Q2", "AP-11"]
related_incidents: ["INC-2026-013"]
version: "1.0.0"
---

# ADR-117 : Révision en place d'une fiche du canon écrite par le promoteur

- **Statut** : Accepted (2026-10-22). La fusion par l'owner vaut ratification.
- **Amende** :
  - [[ADR-093-auto-review-earn-gate|ADR-093]] : couche L4 (anti-écrasement) et §Humain = exception,
    point 6 ;
  - [[ADR-116-diagnostic-relation-review-rule|ADR-116]] : D4 (une précondition ajoutée), §Métriques
    et §Retour arrière.

  Chaque amendement est décrit en §Amendements. Le reste de ces ADR reste en vigueur.
- **Ne modifie ni ADR-083, ni ADR-114, ni ADR-115.** ADR-083 ne contient aucune règle
  d'anti-écrasement : seule une docstring du code la lui attribue. ADR-114 D6 et ADR-093 point 9
  (`exportable.seo`) s'appliquent tels quels : une révision ne change jamais `exportable` (D3).
- **Pourquoi un ADR séparé** : ADR-093 L4 refuse toute écriture sur une fiche du canon déjà approuvée
  et, au point 6, envoie ce cas à un humain. Cette voie humaine n'existe plus. ADR-116 suppose
  pourtant qu'une fiche du canon peut être « promue à nouveau ». Aucun ADR ne dit comment une fiche
  du canon change. Cet ADR l'écrit, sans rouvrir le texte d'ADR-093 ni celui d'ADR-116.
- **Méthode** : constats vérifiés le 2026-10-22, en lecture seule :
  - `main` du WIKI au commit `aafd5f4` : code du décideur et du promoteur, contrôles d'unicité du
    slug, schéma de frontmatter, frontmatter des 11 fiches du canon, score legacy des 5 fiches écrites
    par le promoteur (`compute-confidence-score.py`) ;
  - `main` du vault au commit `684e734`.

## Contexte

### Une fiche du canon ne peut pas changer

| Point | Constat sur `main` `aafd5f4` |
|---|---|
| Écriture | `apply_promotion` refuse d'écrire si `_canon_already_approved` est vrai (« refus écrasement canon déjà approved »). Un canon illisible compte comme approuvé |
| Sélection | `promote.py` saute la proposition avant toute décision : « canon déjà approved — pas d'écrasement (idempotent) » |
| Versement | `_scripts/check-slug-uniqueness.mjs` (CI `lint.yml` et hook pre-commit) refuse deux fichiers de même `entity_type:slug` sous `wiki/` et `proposals/`. Une proposition de même slug que le canon ne peut même pas être versée |
| Voie humaine | aucune depuis le 2026-09-12 (WIKI #83) ; ADR-093 point 6 y renvoie pourtant |
| Garde de chemin | `wiki-protected-paths.yml` refuse toute écriture sous `wiki/` sans l'un de quatre marqueurs : `promotion-from-proposals:`, `rollback:` (§10), `template-migration:` et `metadata-backfill:`. Les deux derniers ne couvrent que des écritures mécaniques : migration de gabarit, ou métadonnée calculée par un outil de contrôle, sans changement du corps |

Une fiche du canon est donc figée. Hors rétrogradation (§10), rien ne peut la corriger ni
l'améliorer, et l'édition à la main reste exclue.

### Ce que cela bloque aujourd'hui

- **ADR-116 n'atteint aucune de ses relations.** Les 5 relations hors sécurité qu'il a mesurées sont
  portées par 4 fiches du canon : `filtre-a-air` (1), `filtre-a-carburant` (1), `filtre-a-huile` (2)
  et `filtre-d-habitacle` (1). ADR-116 D3 n'écrit le cachet de relecture qu'au moment d'une
  promotion : aucune de ces relations ne peut être relue, même une fois sa preuve capturée. Son
  §Retour arrière (« promues à nouveau ») et la « proposition corrective » de ses §Métriques ne sont
  pas exécutables non plus.
- **Une erreur du canon reste en place.** `filtre-a-air` porte `entity_data.pg_id: 510`. Le monorepo
  (`gamme-map.constants.ts`) et le contrat d'URL (`filtre-a-air-8`) donnent 8, et la liste « Points à
  vérifier » de la fiche demande de contrôler cette valeur. Sa relation `perte_puissance_filtration`
  cite deux sources `to_capture` qui ne la fondent pas (WIKI #126).

### Qui a écrit les 11 fiches du canon

| Fiches | Écrites par | Marques lues dans le frontmatter |
|---|---|---|
| `gamme/filtre-a-air`, `filtre-a-carburant`, `filtre-a-huile`, `filtre-d-habitacle` | le promoteur | `reviewed_by: skill:promoter@<révision>`, égal à `promotion_evidence.promoter` ; `auto_promoted: true` ; `promotion_tier: A` |
| `gamme/plaquette-de-frein` (famille sécurité) | le promoteur | mêmes marques |
| `diagnostic/faq`, `safety-config`, `signs`, `vocab-clusters`, `wizard-steps` ; `support/controles-mensuels` | WIKI #7 et #8 (2026-04-29 et 30), fusionnées par l'owner | `reviewed_by: skill:adr-032-rg-1@claude` ; aucune marque du promoteur |

Aujourd'hui, aucune de ces fiches ne porte `evidence.reviewed: true`, `evidence.diagnostic_safe: true`
ni `diagnostic_not_applicable.reviewed: true`.

### Pourquoi seul ce que le promoteur a écrit peut être remplacé

- Une proposition ne peut porter aucune autorité de relecture : `REVIEW_AUTHORITY_CLAIMED` la bloque
  (§7 de `_meta/quality-gates.md`). Si l'on remplaçait une fiche du canon qui en porte une, la
  décision humaine serait effacée sans être vue.
- Une fiche entrée par une PR humaine, sans les marques du promoteur, porte une décision que le
  décideur n'a pas rendue. Il n'a pas à la remplacer.

### Pourquoi la rétrogradation §10 ne suffit pas

§10 de `_meta/quality-gates.md` rétrograde une fiche promue « ensuite identifiée problématique » : son
statut repasse à `in_review` sans `git revert`, elle est déplacée vers `proposals/` et l'action est
journalisée. Pour une amélioration, cette voie a quatre défauts :

- la fiche disparaît du canon jusqu'à la promotion suivante. Les builders d'exports rapportent alors
  l'export existant `UNRECONCILED` et sortent en erreur (`build_exports_diagnostic.py`,
  `build_exports_content.py`) ;
- sans fiche du canon, la régression n'a plus de base : le verdict est `NEW`, qui passe. La version
  corrigée n'est plus comparée à celle qu'elle remplace ;
- rien ne lie la rétrogradation à une version corrigée. Aucun script de `_scripts/` ne lit
  `blocked_reasons` ni `rollback_from_commit`, et `in_review` est un statut promouvable
  (`PROMOTABLE_INPUT_STATUSES`). L'appelant périodique peut donc re-promouvoir la fiche telle quelle,
  si le décideur la juge toujours `ELIGIBLE` ;
- `_meta/audit-log.jsonl`, que §10 alimente, n'existe pas sur `main`.

§10 reste la voie d'une fiche défectueuse (D6), pas celle d'une amélioration.

## Principe directeur

> Une fiche du canon écrite par le promoteur peut être remplacée par le promoteur. Elle passe la même
> barre qu'une promotion, sans régression par rapport à la version qu'elle remplace. Le promoteur ne
> remplace jamais ce qu'il n'a pas écrit. Une révision ne change jamais ce qu'une promotion ne décide
> pas seule : l'exposition (`exportable`), la sécurité et l'autorité humaine.

## Décisions

### D1 — Périmètre : le canon écrit par le promoteur, hors sécurité

Une fiche du canon est révisable si toutes les conditions suivantes sont vraies, lues sur le canon :

| Condition | Refus |
|---|---|
| `reviewed_by` a la forme `<PROMOTER_ID>@<révision>`, est égal à `promotion_evidence.promoter`, et le canon porte `auto_promoted: true` et `promotion_tier: A`. `PROMOTER_ID` est la constante du décideur, sans copie | `REVISION_NOT_PROMOTER_CANON` |
| ni le canon ni la proposition ne sont une fiche sécurité (`is_safety_proposal`). Un doute ou une erreur de classification vaut sécurité (ADR-114 D1) | `REVISION_SAFETY` |
| le canon ne porte aucune autorité de relecture que le décideur n'a pas écrite. `_claimed_review_authority`, appliqué au canon, ne trouve que des relations `reviewed: true` dont `reviewed_by` est un cachet `rule:ADR-116@…` (ADR-116 D3). Un calcul en erreur vaut autorité présente | `REVISION_HUMAN_AUTHORITY_PRESENT` |

Au 2026-10-22, les 4 fiches filtre entrent. `plaquette-de-frein` n'entre pas : c'est une fiche
sécurité, corrigée par §10 et ADR-114. Les 6 fiches de WIKI #7 et #8 n'entrent pas : L4 continue de
les protéger.

Entrer dans le périmètre ne suffit pas à être révisé (D3). Le score legacy de `filtre-a-air`,
`filtre-a-carburant` et `filtre-d-habitacle` vaut aujourd'hui 0.84, sous le seuil de 0.85 ; celui de
`filtre-a-huile` vaut 0.92. Une révision de l'une des trois premières doit donc élever son score, par
exemple en citant des sources capturées dans la limite de confiance de leur type au catalogue.

### D2 — Déclaration : une révision est explicite et épinglée

- La proposition déclare `revision_of: {path, sha256}` :
  - `path` est le chemin du canon. Il doit être égal à `_promotion_target_path` de la proposition :
    même `entity_type`, même `slug` ;
  - `sha256` est l'empreinte du fichier du canon sur lequel la révision a été écrite.
- Le décideur compare `sha256` à l'empreinte `canon_target` que son manifeste d'entrées inscrit déjà.
  `apply_promotion` la revérifie sous son verrou, avant et après la mise en place. Une empreinte
  différente donne `REVISION_BASE_STALE` : une révision écrite sur une version périmée n'est jamais
  appliquée.
- Une `revision_of` sans fiche approuvée à son chemin est refusée (`REVISION_TARGET_MISSING`). Elle
  n'est jamais lue comme une première promotion.
- Sans `revision_of`, rien ne change : `promote.py` saute la proposition et `apply_promotion` refuse
  l'écrasement (L4).

### D3 — Barre : celle d'une promotion, plus la non-régression

- Toutes les portes d'une promotion s'appliquent à la proposition :
  - décision `ELIGIBLE`, avec les couches d'ADR-093 ;
  - seuil de §7 (0.85) ;
  - refus d'une autorité auto-déclarée (`REVIEW_AUTHORITY_CLAIMED`).
- Régression : la porte existante, avec le canon remplacé pour base. Seuls `NEUTRAL` et `IMPROVED`
  passent. `NEW` (base absente ou illisible), `REGRESSED` et `UNAVAILABLE` refusent
  (`REVISION_REGRESSION`).
- Invariants, comparés au canon :
  - `exportable` identique (`REVISION_EXPORTABLE_CHANGED`) : une révision ne change pas l'exposition
    (ADR-093 point 9, ADR-114 D6) ;
  - `safety_rules[]` identique (`REVISION_SAFETY_RULES_CHANGED`) : une règle de sécurité exige une
    relecture humaine (ADR-112 D5).
- Les relations sont relues de nouveau par la règle d'ADR-116 à la révision, puisque sa relecture
  n'est jamais héritée (ADR-116 D3). Une relation relue dans le canon qui ne remplit plus ADR-116 D2
  perd son cachet : c'est une révocation.
- Durcir une condition se fait par PR WIKI. L'assouplir exige un ADR.

### D4 — Écriture : le même writer, le même marqueur

- Seul `apply_promotion` écrit, sous son verrou et ses contrôles d'empreinte existants. Le commit
  porte le marqueur `promotion-from-proposals:`, déjà admis par `wiki-protected-paths.yml`. Aucun
  garde ni aucun workflow `.github` n'est modifié.
- Il écrit les champs de §8, comme pour toute promotion, avec trois différences :
  - `exportable` reste celui du canon, égal à celui de la proposition (D3). Le passage forcé de
    `exportable.seo` à true ne s'applique pas ;
  - `promotion_evidence.revision_of` porte `path`, `sha256` et `reviewed_by` du canon remplacé ;
  - `revision_of` n'est pas recopié au premier niveau du canon.
- `provenance.promoted_from` et `promoted_at` sont écrits comme pour toute promotion. La proposition
  est retirée : la sémantique de déplacement ne change pas.
- La version remplacée reste dans l'historique Git ; `revision_of.sha256` la désigne.
- Les exports se régénèrent par la projection existante, comme après toute promotion.

### D5 — Verrou : une constante de code, report-only d'abord

- Constante `CANON_REVISION_ADR: str | None = None` dans `promotion_decision.py`, sur le modèle de
  `SAFETY_AUTO_APPROVAL_ADR` (ADR-114 D5) et de `RELATION_REVIEW_ADR` (ADR-116 D4).
- **Vide** : mode report-only.
  - Pour toute proposition qui déclare `revision_of`, le décideur calcule D1 à D3 et inscrit
    `would_revise` dans sa trace.
  - La décision reste `BLOCKED` (`CANON_REVISION_NOT_RATIFIED`, `policy.status: not_ratified`).
  - `apply_promotion` refuse l'écrasement, comme aujourd'hui.
- Une PR WIKI dédiée inscrit `CANON_REVISION_ADR = "ADR-117"`. Elle n'est recevable que si ces
  préconditions sont déjà fusionnées, chacune prouvée par un test :
  - (a) D1 à D4 sont calculés par le décideur, avec un test par code de refus ;
  - (b) `check-slug-uniqueness.mjs` et `gate_slug_collision` (`quality-gates.py`) admettent la seule
    paire déclarée : le canon, et la proposition dont `revision_of.path` le désigne. Ils refusent
    toute autre collision ;
  - (c) le schéma de frontmatter admet `revision_of` dans une proposition et
    `promotion_evidence.revision_of` dans le canon ;
  - (d) dans `promote.py`, pour une révision déclarée, le saut « canon déjà approved » est remplacé
    par la décision du décideur : un seul chemin de décision ;
  - (e) la PR porte la mesure report-only du corpus : une révision identité de chaque fiche du canon
    de `main` (son contenu, sans les champs écrits par le promoteur), avec `would_revise` et ses
    motifs.
- Aucune variable d'environnement ni aucune option CLI ne lève le verrou.
- Le fichier entre dans l'empreinte du moteur de décision : changer la constante invalide toute
  décision déjà rendue (`STALE_DECISION`).
- Pour refermer la voie, une PR WIKI remet la constante à vide (§Retour arrière).

### D6 — Ce qui reste inchangé

- L4 et le point 6 d'ADR-093 s'appliquent à toute fiche du canon hors D1, et à toute proposition
  sans `revision_of`.
- Toute fiche défectueuse peut toujours être rétrogradée par §10. Une fiche sécurité du canon se
  corrige par §10 et la Safety Auto-Gate d'ADR-114.
- `exportable` ne change que par une PR revue, ou, pour une fiche sécurité, par la porte d'ADR-114 D6.
- `diagnostic_safe` reste un flip humain ciblé. Une révision n'en pose aucun, et un canon qui en
  porte un n'est pas révisable (D1).
- Le décideur reste unique et le promoteur reste le seul writer de `wiki/`. Aucune voie humaine n'est
  rouverte ni fermée.
- Le RAG n'a aucune autorité d'écriture de contenu (ADR-031, ADR-046).
- Une révision n'atteint le monorepo que par l'avancée de son pointeur vers le WIKI, comme toute
  promotion.

### D7 — Observabilité

- Chaque décision rendue pour une proposition qui déclare `revision_of` porte :
  - `revision_of`, ses conditions D1 à D3 et ses codes de refus ;
  - le verdict et le delta de régression ;
  - `would_revise` ou la révision écrite, et l'état de la politique : `ratified` avec l'ADR inscrite,
    ou `not_ratified`.
- La fiche écrite porte `promotion_evidence.revision_of`.
- La trace existante du décideur suffit : cet ADR ne crée aucun canal.

## Amendements

### ADR-093 (auto-review à barre de preuve)

- **Couche L4 — Anti-écrasement** : maintenue, sauf pour une révision admise par ADR-117 (D1 à D3,
  avec le verrou de D5 levé). La lecture fail-closed est maintenue : un canon illisible bloque,
  révision comprise.
- **§Humain = exception, point 6** : une proposition dont le canon est déjà approuvé ou illisible
  n'est plus envoyée à un humain. Elle est bloquée par ses motifs, sauf si c'est une révision admise
  par ADR-117.
- **Point 9** : non modifié. Une révision ne change jamais `exportable` (ADR-117 D3).
- Le reste d'ADR-093 est maintenu.

### ADR-116 (relecture des relations par une règle de preuve)

- **D4** : une précondition (f) s'ajoute à la levée de `RELATION_REVIEW_ADR` : `CANON_REVISION_ADR`
  est déjà inscrit (ADR-117 D5). Toutes les relations mesurées sont sur des fiches du canon. Sans
  révision, la règle ne relirait que des fiches à leur première promotion, et son retour arrière ne
  serait pas exécutable.
- **§Retour arrière, point 2** : « sont promues à nouveau » se lit « sont révisées selon ADR-117 ;
  une fiche dont la révision est refusée est rétrogradée par §10 ».
  - La révision reprend le contenu de la fiche et sa proposition porte `reviewed: false` (WIKI #113).
  - Avec `RELATION_REVIEW_ADR` vide, les relations sont écrites telles que proposées, donc
    `reviewed: false`.
  - Le score de régression ne lit pas `reviewed` : retirer un cachet ne fait pas régresser la fiche.
    La révision peut pourtant être refusée par une autre porte, par exemple si un contrôle a changé
    depuis la promotion. La rétrogradation §10 retire alors la fiche du canon. Le retour arrière ne
    dépend donc pas d'une porte de qualité.
  - « Aucune édition à la main du canon » est maintenu.
- **§Métriques** : « une proposition corrective de la fiche » se lit « une révision selon ADR-117 ».
- Le reste d'ADR-116 est maintenu.

## Ce que cet ADR ne fait pas

- Il ne révise aucune fiche : le verrou est fermé.
- Il n'ouvre la révision ni des fiches que le promoteur n'a pas écrites, ni des fiches sécurité.
- Il ne change ni la barre de promotion, ni ADR-115, ni le writer monorepo.
- Il ne change ni `exportable`, ni `diagnostic_safe`, ni `safety_rules[]`.
- Il ne rouvre aucune voie humaine dans le WIKI et n'en ferme aucune.
- Il ne modifie aucun garde ni aucun workflow.
- Il ne change aucune URL : le chemin et le slug du canon sont conservés (D2). Il ne décide d'aucun
  meta ni d'aucun H1 : une révision suit le même chemin qu'une promotion vers ses consommateurs.

## Mise en œuvre

1. Une PR WIKI, après la fusion de cet ADR, en report-only :
   - D1 à D4 dans le décideur, avec la constante vide et la trace de D7 ;
   - le schéma, l'unicité du slug et `promote.py` (préconditions b à d) ;
   - `_meta/quality-gates.md` §7, §8 et §10 alignés ;
   - tests : chaque code de refus, l'empreinte périmée, `exportable` conservé, constante vide sans
     aucune écriture.
2. Une proposition de révision de `filtre-a-air`, à soumettre une fois actives les entrées du
   catalogue de WIKI #126 :
   - `pg_id` corrigé en 8 ;
   - sources de `perte_puissance_filtration` remplacées, avec des citations ancrées ;
   - score legacy porté au-dessus du seuil par ces sources capturées (D1).
3. La PR de levée de D5, avec la mesure du corpus (précondition e).
4. Ensuite seulement, la levée d'ADR-116 (préconditions a à f).

Aucune PR monorepo.

## Options considérées

### Option A — Statu quo — rejetée

Le canon reste figé. ADR-116 ne peut relire aucune des relations qu'il a mesurées, et
`pg_id: 510` reste en place.

### Option B — Une voie humaine de révision — rejetée

Elle rétablirait, pour le canon, la validation humaine systématique supprimée le 2026-09-12
(WIKI #83). Elle ne rend pas la preuve plus vérifiable que D3.

### Option C — Rétrogradation §10, puis promotion — rejetée pour une amélioration

La fiche est absente du canon entre les deux, les exports deviennent `UNRECONCILED`, la régression
perd sa base, et rien ne lie la rétrogradation à la version corrigée (§Contexte). §10 reste la voie
d'un défaut.

### Option D — Une nouvelle fiche à un autre slug — rejetée

Deux fiches pour une même gamme dupliqueraient le contenu. Le slug porte le contrat d'URL, et
l'unicité du slug l'interdit.

### Option E — Un écrasement autorisé par variable d'environnement ou option CLI — rejetée

Même raison qu'ADR-114 option D : le verrou doit être inscrit, revu et versionné avec le décideur.

### Option F — La révision de tout canon approuvé, quel qu'en soit l'auteur — rejetée

Elle effacerait des décisions humaines (fiches fusionnées par l'owner, flips ciblés) qu'aucune
proposition ne peut porter.

### Option G — La révision en place du canon écrit par le promoteur, par le décideur unique, verrouillée, report-only d'abord — retenue

D1 à D7.

## Conséquences

### Positives

- ADR-116 peut relire les relations qu'il a mesurées. Son retour arrière et sa relecture a posteriori
  deviennent exécutables.
- Une erreur du canon (`pg_id: 510`) se corrige par la voie de preuve, sans édition à la main.
- Chaque révision est comparée à la version qu'elle remplace, épinglée par empreinte, et tracée.
- Pas de second writer, pas de second décideur, aucun garde modifié.

### Négatives

- Le risque 4 d'ADR-093 s'applique à chaque révision comme à chaque promotion : la barre ne vérifie
  pas le sens.
- La non-régression est celle du score existant (formule legacy : confiance moyenne des sources,
  sections, liens, diversité des types), pas celle de la vérité. Une révision qui ajoute une source
  de confiance moyenne, ou qui retire une affirmation fausse, peut faire baisser le score et être
  refusée. La correction d'un défaut passe alors par §10, avec ses limites.
- Trois des quatre fiches du périmètre sont aujourd'hui sous le seuil (0.84). Seule une révision qui
  élève leur score passe : une correction isolée, comme celle de `pg_id`, ne suffit pas.
- Les 6 fiches de WIKI #7 et #8 et la fiche sécurité restent figées hors §10.
- Deux PR WIKI avant la première révision. La levée d'ADR-116 attend aussi celle-ci
  (précondition f).

## Métriques

- Par run du décideur :
  - propositions qui déclarent `revision_of` ;
  - `would_revise` (report-only), ou révisions écrites ;
  - motifs de refus par code, et verdicts de régression.
- Après la levée :
  - révisions appliquées ;
  - refus `REVISION_BASE_STALE`, qui mesurent les courses ;
  - fiches révisées puis rétrogradées par §10.

## Retour arrière

- Une PR WIKI remet `CANON_REVISION_ADR` à vide : L4 s'applique de nouveau à tout le canon. Si une
  fiche du canon porte un cachet `rule:ADR-116@…`, le retour arrière d'ADR-116 passe d'abord : il
  procède par révision, ou à défaut par §10.
- Une révision déjà écrite n'est pas annulée en bloc : c'est une fiche promue par le décideur, sous
  toutes ses portes. Une révision défectueuse se corrige par une nouvelle révision ou, à défaut, se
  rétrograde par §10. L'historique Git et `revision_of.sha256` désignent la version remplacée.
- Un nouvel ADR retire la règle.

## Revue planifiée

**Date** : J+90 après la levée du verrou, ou le 2027-01-20 si le verrou n'est pas levé d'ici là.

**Critères** :

- révisions appliquées, et refus par code ;
- aucune révision d'une fiche sécurité ou d'une fiche hors D1, et aucun changement d'`exportable` par
  une révision ;
- fiches révisées puis rétrogradées par §10 ;
- état de la levée d'ADR-116.

## Références

- [[ADR-093-auto-review-earn-gate|ADR-093]] ·
  [[ADR-116-diagnostic-relation-review-rule|ADR-116]] ·
  [[ADR-114-wiki-safety-auto-gate|ADR-114]] ·
  [[ADR-083-tiered-wiki-promotion|ADR-083]] ·
  [[ADR-115-diagnostic-projection-requires-review|ADR-115]] ·
  [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] ·
  [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]]
- WIKI :
  - PR #7 et #8 (fiches RG-1, 2026-04-29 et 30), #83 (validation automatique, 2026-09-12),
    #113 (relecture auto-déclarée refusée), #126 (catalogue des preuves de `filtre-a-air`,
    brouillon) ;
  - `_meta/quality-gates.md` §7, §8 et §10 ;
  - `_scripts/promotion_decision.py` (`apply_promotion`, `_canon_already_approved`,
    `_promoted_frontmatter`, `_claimed_review_authority`), `_scripts/promote.py`,
    `_scripts/compare-proposal-versions.py`, `_scripts/check-slug-uniqueness.mjs`,
    `_scripts/quality-gates.py` (`gate_slug_collision`) ;
  - `.github/workflows/wiki-protected-paths.yml`.
- (Relations structurées : voir `amends` / `extends` / `related_adr` dans le frontmatter.)

---

*Proposé le : 2026-10-22*
*Accepté le : à la fusion owner (fusion = ratification)*
