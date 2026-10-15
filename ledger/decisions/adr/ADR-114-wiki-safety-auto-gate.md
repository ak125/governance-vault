---
id: ADR-114
title: "Promotion WIKI des fiches sécurité-critiques sur preuve vérifiable (Safety Auto-Gate) : amende ADR-083, ADR-091, ADR-093 et ADR-096"
status: accepted
date: "2026-10-15"
decision_date: "2026-10-15"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-083", "ADR-091", "ADR-093", "ADR-096"]
extends: []
related_adr: ["ADR-031", "ADR-032", "ADR-033", "ADR-035", "ADR-046", "ADR-059", "ADR-083", "ADR-086", "ADR-088", "ADR-089", "ADR-091", "ADR-093", "ADR-096", "ADR-102", "ADR-112"]
related_rules: ["G1", "G6", "Q1", "Q2", "AP-11"]
related_incidents: []
version: "1.0.0"
---

# ADR-114 : Promotion WIKI des fiches sécurité-critiques sur preuve vérifiable (Safety Auto-Gate)

- **Statut** : Accepted (2026-10-15). La fusion par l'owner vaut ratification.
- **Amende** :
  - [[ADR-083-tiered-wiki-promotion|ADR-083]] : TIER B, renvoi de « tout flag safety » ;
  - [[ADR-091-wiki-score-recalibration|ADR-091]] : Décision §4, plancher `HUMAN_SPOT_CHECK` ;
  - [[ADR-093-auto-review-earn-gate|ADR-093]] : barre « Sécurité », §Sécurité points 1, 3 et 4,
    §Humain = exception points 1 et 9, §Ce qui reste, séquence de sortie point iv, couches L1 et L5,
    lecture de §Plan de mise en œuvre et §Angles morts ;
  - [[ADR-096-governed-automatic-source-discovery|ADR-096]] : §D5 (frontière de promotion) et
    dernier point de §D6.

  Chaque amendement est décrit en §Amendements. Le reste de ces ADR reste en vigueur.
- **Pourquoi un ADR séparé** : ADR-093 l'exige. Sa séquence de sortie (point iv) dit que toute
  exception au plancher humain sécurité « serait un ADR séparé exigeant une vérif de VALEUR réelle ».
  Cette vérification existe désormais (D4).
- **Méthode** : constats vérifiés le 2026-10-11, en lecture seule, sur `main` du WIKI au commit
  `cc04f08` et sur la PR WIKI #107 (Safety Auto-Gate), relue à sa tête `6293fb4`. Le classifieur
  sécurité a été exécuté sur les fiches gamme de `main` et sur les familles prescrites par ADR-093 L0 ;
  les types de source sont lus dans `_meta/source-catalog.yaml`. Le périmètre de D4 a été revérifié le
  2026-10-13 sur `main` du WIKI au commit `6bc00e7` (#107 fusionnée en `6d1548a`) et sur `main` du
  monorepo au commit `a84fd56` (`DiagnosticContentService`), puis le 2026-10-15 sur `main` du WIKI
  au commit `2953c1e` (scripts inchangés depuis `6bc00e7`) et sur `main` du monorepo au commit
  `4b55b97` (lecteurs de D4 inchangés depuis `a84fd56`).

## Contexte

### Quatre ADR renvoient la sécurité à un humain

| ADR | Texte |
|---|---|
| ADR-083 | TIER B reçoit « tout flag safety » : « c'est là que vit le jugement E-E-A-T + sécurité » |
| ADR-091 §4 | les pièces sécurité (freinage, direction, airbag, suspension) restent `HUMAN_SPOT_CHECK` |
| ADR-093 | « Sécurité : JAMAIS auto-publiée », plancher humain incompressible ; une valeur chiffrée critique est exclue de l'auto-approbation tant qu'aucune vérification de valeur n'existe |
| ADR-096 §D5 | « toute source inconnue, donnée de sécurité, ou valeur numérique critique demeure human-required » |

### Le WIKI n'a plus de voie humaine

Le 2026-09-12, l'owner a supprimé la validation humaine systématique (WIKI #83). Depuis, un décideur
unique, `_scripts/promotion_decision.py`, rend l'un de trois résultats : `ELIGIBLE`, `BLOCKED` ou
`UNKNOWN_FAIL_CLOSED`. Une fiche bloquée l'est par des motifs structurés. Elle est réévaluée
automatiquement une fois les preuves corrigées. Une revue humaine peut apporter des informations, mais
elle n'est ni un passage obligatoire ni un moyen de contourner une preuve manquante
(`_meta/quality-gates.md` §6 et §7).

Combinés, ces deux états produisent un blocage permanent. Les ADR interdisent la promotion automatique
d'une fiche sécurité, et le WIKI n'offre plus de voie humaine. Aucune fiche sécurité ne peut donc
être promue. Sur `main` du WIKI, 3 des 10 fiches gamme (4 validées, 6 propositions) relèvent d'une
famille sécurité : `courroie-d-accessoire`, `disque-de-frein` et `plaquette-de-frein`, toutes trois
des propositions.

### Le périmètre et la barre d'ADR-093 ne sont pas entièrement implémentés

- **Périmètre (L0)** : ADR-093 prescrit d'étendre la classification sécurité à la transmission, aux
  roulements et moyeux de roue, à la visserie de roue, au circuit de frein et à la direction assistée.
  `_scripts/safety_families.py` couvre six familles : freinage, direction, distribution,
  électricité-sécurité, airbag et suspension. Il classe non sécurité `roulement-de-roue`,
  `moyeu-de-roue`, `cardan`, `soufflet-de-cardan`, `vis-de-roue`, `ecrou-de-roue` et `goujon-de-roue`.
- **Sources primaires (L3)** : ADR-093 exige au moins 3 sources primaires distinctes pour une fiche
  non sécurité. Le décideur WIKI ne compte que les types de référence distincts (`kind`, au moins 2).
- **Réfutation (L5)** : le contrôle `refutation_gate` prescrit par ADR-093 n'existe pas. Ses points (c)
  et (d) comparent le décideur WIKI au script monorepo `auto_review_wiki_proposal.py`, dont le verdict
  n'a aucun consommateur.

Le catalogue des sources porte déjà la notion de source de preuve : `source_type_editorial_role`
attribue le rôle `proof` ou `corroboration` à chaque type, et chaque source déclare son `publisher`.

### La vérification de valeur exigée par ADR-093 existe

- `_scripts/numeric_exactitude.py` classe chaque valeur chiffrée d'un texte.
- `_meta/numeric-plausibility.yaml` porte les plages plausibles par famille et par grandeur. Il suit
  l'option A décidée par l'owner (2026-07-02/03) : la machine propose une plage, un humain la valide une
  fois, après capture d'une source constructeur ou normative précise.
- Une valeur n'est `numeric_verified` que dans une plage `validated`, corroborée par au moins deux
  sources captées distinctes et concordantes. Une plage `proposed` ne confère jamais ce statut.
- Au 2026-10-11, le fichier compte 6 plages, toutes `proposed` : aucune valeur dimensionnée n'est
  vérifiable.

### La Safety Auto-Gate est câblée, verrouillée

La PR WIKI #107 place la Safety Auto-Gate dans le décideur unique. Elle est fail-closed et verrouillée
par une constante de code vide, `SAFETY_AUTO_APPROVAL_ADR`. Le motif `SAFETY_HUMAN_REVIEW` y porte
`policy.status: not_ratified`.

### Ce que la gate ne contrôle pas encore

Une fiche promue est publiée entière, pas seulement son corps :

- le dépôt WIKI est public : chaque champ du frontmatter d'une fiche est lisible par tous ;
- le monorepo lit lui-même des fiches du canon. `DiagnosticContentService` lit `wiki/diagnostic/` et
  `wiki/support/` par le sous-module d'ADR-032 D5, que maintient ADR-112 D9, et sert le titre,
  `entity_data` et le corps de chaque fiche ;
- deux exports du WIKI publient du texte tiré du frontmatter d'une fiche.

Ces deux exports sont les suivants :

- l'export SEO (`build_exports_seo.py`, ADR-086) ne lit jamais la prose (ADR-059). Il projette les
  champs structurés du frontmatter :
  - `entity_data.editorial.<section>.content_md` ;
  - `maintenance.educational_advice` ;
  - `decision_brief.selection_criteria_top` et `function_oneliner` ;
  - les blocs et faits déjà structurés ;
- l'export diagnostic (`build_exports_diagnostic.py`, ADR-035 D2) projette les relations
  `diagnostic_relations` (contrat ADR-033), dont le texte libre `part_role`, que le monorepo inscrit en
  base de provenance (ADR-035 D1). Il y joint des données du catalogue des sources.

Les autres répertoires d'`exports/` ne lisent pas les fiches : `diag-canon*` vient de la base de
production, `rag/` de générateurs du monorepo, et `support/` est vide.

La condition `numeric_exactitude_verified` de #107 ne contrôle que le corps de la fiche. Elle ne voit
ni le frontmatter, publié avec la fiche, ni le texte que ces deux exports publient. #107 range ce point
parmi ses résidus (« valeurs chiffrées du frontmatter »). D4 le ferme avant que la gate puisse s'ouvrir.

## Principe directeur

> Une fiche sécurité est promue par la preuve, jamais par la confiance. Ce que la machine ne sait pas
> prouver bloque la fiche. Aucune approbation, humaine ou automatique, ne remplace une preuve
> manquante.

## Décisions

### D1 — Périmètre sécurité : un classifieur unique, fail-closed

- Une fiche relève de la sécurité si `_scripts/safety_families.py::is_safety_proposal` le dit. Ce
  classifieur est déjà partagé par le décideur et par `gate_safety_unsourced`.
- Le périmètre à couvrir est la couche L0 d'ADR-093, maintenue. Les familles qu'il ne reconnaît pas
  encore (Contexte) y entrent par PR WIKI, testées sur les fiches citées. Cette couverture est une
  précondition de la levée du verrou (D5).
- Un doute ou une erreur de classification vaut sécurité.
- Ajouter une famille ou un motif se fait par PR WIKI, parce que cela rend le contrôle plus strict.
  Retirer une famille ou un motif exige un ADR.

### D2 — Un seul décideur

- `promotion_decision.py` (WIKI) est le seul décideur de promotion. Il n'existe ni second décideur
  LLM, ni décideur monorepo.
- Le verdict `auto_promotion_eligible` de `scripts/wiki-generators/auto_review_wiki_proposal.py`
  (monorepo) n'a aucun consommateur et ne confère aucune autorité de promotion. Ce script n'est pas
  modifié.

### D3 — Conditions de la Safety Auto-Gate

Une fiche sécurité est `ELIGIBLE` seulement si **toutes** les conditions suivantes sont prouvées.

| Condition | Preuve exigée |
|---|---|
| `dim_A_floor`, `dim_C_floor` | dimensions du score six dimensions (ADR-088) : A (preuve) ≥ 22 et C (couverture) ≥ 15 ; une dimension absente ou non numérique est un échec |
| `no_quality_gate_fail` | les cinq contrôles atomiques source, claim, contradiction, risk et confidence exécutés, dans cet ordre, et PASS ; les contrôles de `quality-gates.py`, dont `gate_safety_unsourced`, restent bloquants |
| `proof_sources_min` | au moins 3 éditeurs distincts (`publisher`) parmi les sources `active` de rôle `proof`, lu dans `source_type_editorial_role` du catalogue sans liste recopiée ; chaque source captée dans RAW et citée par la fiche ; un éditeur qui n'est pas un texte, sans caractère alphanumérique visible, ou qui porte un caractère que la base Unicode ne définit pas, ne compte pas (`publisher_absent`) |
| `numeric_exactitude_verified` | D4 |
| `no_disputed_claims` | déclaration explicite `no_disputed_claims: true` dans le frontmatter |
| `diagnostic_live_authority_not_claimed` | aucune entrée ne porte `diagnostic_safe: true` (ADR-033, flip humain ciblé) |
| `no_manual_review_policy` | aucune source à `source_policy: manual_review`, ni dans les preuves ni dans la coverage map |
| `coverage_strict_pass` | couverture stricte PASS (ADR-089) ; un avertissement bloque |
| `regression_gate_pass` | comparaison de versions NEW, NEUTRAL ou IMPROVED |
| `provenance_pass` | provenance RAW vérifiée PASS |

`proof_sources_min` place la barre sécurité au moins au niveau de la couche L3 d'ADR-093 (au moins
3 sources primaires distinctes pour une fiche non sécurité) : la barre sécurité ne peut pas être plus
basse que la barre non sécurité. Elle la durcit sur deux points :

- les sources sont distinguées par éditeur, pour que trois pages d'un même fabricant ne comptent pas
  comme trois preuves ;
- seul le rôle `proof` du catalogue compte. La liste de L3 compte aussi `tecdoc_official` et
  `parts_feed_certified` comme primaires ; le catalogue, plus récent et seule source de vérité des
  types, les range en corroboration. Les types de rôle `proof` sont tous primaires pour L3.

Règles communes :

- une condition dont le calcul échoue est fausse, et son erreur est rapportée ;
- un résultat absent n'est jamais un succès ;
- le contrôle `NUMERIC_HIGH_HARM` (couple, pression) reste bloquant pour toute fiche, sécurité ou
  non ;
- les conditions de toute fiche (score, niveau de vérité, types de sources, empreintes identiques entre
  décision et écriture) s'appliquent aussi.

### D4 — Vérification de valeur sur tout le texte publié

- `numeric_exactitude_verified` porte sur **tout le texte publié** :
  - la fiche promue elle-même, telle que la promotion l'écrit : son corps et son frontmatter entier,
    valeurs et clés, sans aucun champ exempté ;
  - les documents que les exporteurs en tirent, texte du catalogue des sources compris.
- Le corps est lu sous trois formes :
  - rendue : prose, titres, code, texte HTML, texte alternatif d'image ;
  - écrite : balises, attributs et commentaires HTML, titres et destinations des liens et des images,
    définitions de référence, info des blocs de code ;
  - sans balisage : le source de chaque bloc lu en ignorant le balisage, liens réduits à leur libellé,
    balises HTML et caractères de balisage Markdown retirés.

  Chaque forme est aussi lue à la compatibilité Unicode près (exposants et indices gardés),
  caractères invisibles retirés. Les glyphes vides (blanc braille, blancs hiéroglyphiques, remplisseur
  khitan, tête de note nulle), qu'un rendu dessine sans encre, y sont lus comme un espace. Les
  échappements d'URL y sont affichés comme une IRI, plus strictement que RFC 3987 §3.2 : seuls les
  caractères non ASCII valides sont décodés, tout échappement ASCII est gardé tel qu'écrit. Puis, dans
  une lecture à part, ils sont tous décodés.
- Aucune liste de champs ne borne ce contrôle, ni recopiée ni tirée d'un lecteur : la fiche est
  publique et un lecteur peut en servir n'importe quel champ. Les documents exportés sont ceux que
  produisent les exporteurs eux-mêmes. Un champ ajouté à la fiche ou à un export entre dans le contrôle
  sans autre modification.
- Chaque chaîne du frontmatter et des exports est lue :
  - telle qu'écrite ;
  - telle qu'un rendu Markdown ou HTML l'affiche ;
  - telle que l'affiche le rendu des blocs projetés des pages R3 du monorepo
    (`renderProjectionMarkdown`) : HTML affiché tel qu'écrit, sa grammaire inline appliquée jusque dans
    ce HTML ; ses blocs séparés, puis joints sans séparateur comme les joint `stripHtml` (`25` /
    `1. Nm` y devient `25Nm`) ;
  - sans structure de blocs : ses lignes jointes, HTML retiré, comme les affiche un rendu qui ne
    connaît ni code indenté ni bloc HTML.

  Les échappements d'URL y sont lus comme dans le corps.
- Chaque lecture, du corps comme d'une chaîne, est lue aussi en squelette : entités et tout
  caractère hors lettres, chiffres, espaces, ponctuation de nombre et de clause, symboles d'unité et
  signe `×` entre deux nombres retirés, sans séparateur. C'est ainsi que l'affichent les surfaces R3
  qui passent le rendu des blocs projetés par `stripHtml` du monorepo (extrait, HowTo JSON-LD, liste
  de contrôle) : `25"Nm` y devient `25Nm`, `25"°C` y devient `25°C`. Sa violation est suffixée
  `squelette` et n'est rapportée que si aucune autre lecture ne porte la même valeur. Chaque extrait
  ancré y est lu aussi, sous le statut et l'identité de sa source : une marque, une touche ou un
  guillemet entre un nombre et son unité, ou entre deux de ses chiffres, n'y cache pas la valeur
  affichée.
- Monde fermé : le contrôle ne modélise pas chaque moteur de rendu, il refuse ce qu'aucune de ses
  lectures ne rend. Les rendus pris en compte sont GitHub, Obsidian, que déclare le README du dépôt,
  avec ses modules de base, activés ou non, sans module tiers (`.obsidian/community-plugins.json`
  vide), et les surfaces R3. Tel qu'écrit, en entité HTML ou échappé, dans le corps ou dans une chaîne
  publiée, est une violation (`unmodelled_<genre>`), quoi qu'il affiche :
  - tout `$`, monétaire compris (`formula`) : GitHub rend `$25^\circ C$` en `25°C` ;
  - un bloc de code que GitHub ou Obsidian rend autrement que son texte, par le premier mot de son
    info : `math`, `mermaid`, `geojson`, `topojson`, `stl`, `query` (recherche intégrée d'Obsidian),
    `base` (vue « Bases » d'Obsidian) (`rendered_fence`) ;
  - du HTML brut, balise ou commentaire (`raw_html`) : direction, style, texte masqué ;
  - une note de bas de page (`footnote`), note en ligne d'Obsidian `^[…]` comprise, fermée ou non : son
    renvoi affiche un numéro, sa définition s'affiche en fin de page ;
  - une syntaxe d'Obsidian qui masque ou remplace son texte (`obsidian`) : insertion `![[…]]`, qui
    affiche à sa place une autre note ou un fichier ; lien à libellé, à titre ou à bloc
    (`[[note|25]]` n'affiche que `25`, `[[note#titre]]` affiche `note > titre`), ou écrit avec
    l'extension de sa note (`[[25.md]]`, blancs de fin compris), qu'Obsidian peut afficher sans elle ;
    commentaire `%%…%%`, masqué (`2%%x%%5 Nm` s'affiche `25 Nm`) ; identifiant de bloc `^id` en fin
    de ligne, suivi au plus de blancs, masqué, relevé dans tout dernier mot de ligne dont un `^`
    précède un caractère, hors note. Un lien simple, `[[note]]`, affiche son texte sans ses crochets,
    que lit la lecture sans balisage ; un surlignage `==…==` est lu par la lecture squelette, qui
    retire ses signes ;
  - une citation dont la première ligne que lit l'analyseur (lignes blanches sautées, blancs
    retirés) commence par `[!`, quel que soit le bloc qu'elle ouvre (`callout`) : l'encadré
    d'Obsidian et l'alerte de GitHub affichent le marqueur en icône et en titre, le type à défaut de
    titre ;
  - un contrôle bidirectionnel (propriété Unicode `Bidi_Control`) ou un caractère de classe
    bidirectionnelle R, AL ou AN (`display_order`) : sans eux ni HTML, l'algorithme bidirectionnel
    Unicode (UAX #9) affiche un paragraphe de gauche à droite dans l'ordre où il est écrit ;
  - un caractère de contrôle hors tabulation et fins de ligne (`control_character`), dont l'affichage
    n'est pas défini ;
  - un code emoji (`emoji_shortcode`), que GitHub affiche en image : `:two:` affiche le chiffre 2 en
    touche. Tout nom de cette forme l'est, sauf celle, qu'aucun code ne porte, des minutes d'une heure
    et de son décalage horaire (`10:00:00`, `2026-10-14T10:00:00+02:00`) ;
  - un chiffre que la lecture ne lit pas tel qu'il s'affiche (`numeral`) : caractère de valeur
    numérique Unicode que les chiffres décimaux de sa décomposition de compatibilité n'écrivent pas
    (`❷`, `〇`, `Ⅻ` ; `½`, décomposé `1⁄2`, lu `2`), ou barre de fraction (`⁄`).
    `numeric_exactitude.py` ne lit que les chiffres décimaux ;
  - un caractère que la base Unicode de l'interpréteur ne définit pas (`unknown_character`) : non
    attribué, d'usage privé ou demi-codet isolé. Sa classe bidirectionnelle, sa valeur numérique et son
    affichage sont inconnus du contrôle : pour une base plus récente, il peut être un chiffre ou une
    lettre de droite à gauche. Chaque propriété de caractère est celle de la base Unicode de
    l'interpréteur qui exécute le contrôle ;
  - une image, du dépôt ou distante (`image`) : ce qu'elle affiche n'est pas du texte ;
  - une imbrication au-delà de la profondeur de l'analyseur (`nesting`) : le contenu d'une citation ou
    d'un item de liste ouvert au dernier niveau (20 citations ou 10 niveaux de liste), que
    l'analyseur ne lit pas et que GitHub affiche ;
  - le numéro d'un item de liste ordonnée suivi d'une unité ou d'un chiffre (`ordered_list_number`) :
    le numéro qu'affiche le navigateur (`start` de la liste, puis de 1 en 1), ou le rang de l'item dans
    le rendu projeté, n'est pas du texte pour la lecture et se lit avec ce qui le suit (`25.` puis
    `Nm`, `2.` puis `5 Nm`), case à cocher en tête de paragraphe comprise (`25. [x] Nm`), que GitHub
    et Obsidian affichent en case et le rendu projeté non. Un premier bloc qui n'affiche rien (code,
    titre ou cellule vides, ou faits de caractères invisibles ou de glyphes blancs, lien sans
    libellé) n'a pas de ligne : le numéro se lit alors avec le bloc suivant, et l'item est une
    violation quel que soit ce bloc.

  Une chaîne publiée dont une lecture, ou son squelette, commence par une unité, symbole ou en lettres
  (`mm`, `millimètres`), est une violation aussi (`unmodelled_leading_unit`) : les surfaces R3
  joignent sans séparateur les champs d'une même section, et un nombre qui finit le champ précédent
  s'y lirait avec elle, y compris par un début d'entité que la chaîne achève (`25&nbsp` puis `;mm`).

  Le code du corps tel qu'écrit, affiché tel quel, est inerte ; dès qu'un décodage change le corps, son
  code est relu. Dans une chaîne publiée, qu'un lecteur peut servir sous toute forme, le code n'est
  jamais inerte.
- Chaque valeur chiffrée doit être `numeric_verified`. Une valeur hors ancre de la coverage map est non
  sourcée. Un extrait ancré porte sa source dans chaque forme où il se lit ; un extrait dont la borne
  coupe une valeur (nombre, unité, exposant, marque d'approximation), telle qu'écrite, à la
  compatibilité près ou en squelette, ne la porte pas et est rapporté.
  Seul le corps porte des ancres : une valeur dimensionnée du frontmatter ou d'un export n'est
  jamais vérifiable, même sur une plage `validated`, et bloque la fiche. Une telle valeur se publie
  dans la prose ancrée du corps, que l'export SEO ne reprend pas.
- Une entrée gouvernée absente de l'arbre évalué rend la condition qui la lit fausse et `UNAVAILABLE` :
  un défaut d'infrastructure, jamais un verdict sur le contenu. C'est le cas de
  `_meta/numeric-plausibility.yaml` et, quand l'arbre évalué est distinct de celui des scripts (revue
  `gap1`), de `_meta/source-catalog.yaml`. Dans l'exécution habituelle, un catalogue absent, illisible
  ou malformé arrête l'exécution au chargement des contrôles qualité, sans décision écrite.
- La lecture est prudente. Une chaîne interne (note de revue, slug, URL, suite d'échappements `%XX`)
  compte comme une valeur affichée si elle porte un nombre suivi d'une unité ou de `%`, ou un nombre
  nu dans une clause qui nomme une grandeur dimensionnée d'une famille de
  `_meta/numeric-plausibility.yaml`. Ainsi `Manuel_2019_%28FR%29.pdf`, lu sans balisage, compte
  `2019%`. Le monde fermé a le même coût : bloquent aussi une note de bas de page, note en ligne
  d'Obsidian comprise, fermée ou non, toute insertion `![[…]]` et tout lien `[[…|…]]`, `[[…#…]]`,
  `[[…^…]]` ou `[[….md]]` d'Obsidian, tout `%%`, toute citation qui s'ouvre sur `[!` (`> [!note]`),
  tout dernier mot de ligne qui porte un `^` suivi d'un caractère (`10^3`), hors note, tout bloc
  `query` ou `base`, tout HTML brut (dans une chaîne publiée, un lien automatique
  `<https://…>` et une balise écrite en code compris), tout `$`, prix compris, tout caractère d'une
  écriture de droite à gauche (hébreu, arabe), tout nom entre deux deux-points hors heure (`:100:`
  d'un rapport `1:100:5`), tout chiffre non décimal (chiffre romain `Ⅻ`, idéogramme `三`), toute
  fraction (`½`, `1⁄2`), toute image, tout caractère d'une version d'Unicode plus récente que celle
  de l'interpréteur, toute chaîne publiée qui commence par une unité ou par un mot qui en commence
  une (`barre de torsion`, lu `bar` ; `Inchangé`, lu `Inch`), tout item de liste ordonnée qui
  commence, après une case à cocher éventuelle (`[x]`), par un chiffre, une unité, un mot qui en
  commence une (`1. Inchangé`, lu `1. Inch`) ou un bloc vide, invisible ou blanc et, dans un corps
  dont un décodage diffère du texte écrit (échappement `%XX`, entité), une balise ou un `$` écrit en
  code.
  La lecture squelette sur-approxime de même : elle joint ce que sépare un signe qu'elle retire
  (`20-30%` y compte `2030%`), extrait ancré compris (`10-20 Nm` y est classé `1020 Nm`, hors
  plage). Un tel faux positif garde la fiche bloquée et ne publie rien.
- Résidus, non détectés :
  - un nombre sans unité adjacente : écrit seul dans un champ (nombre YAML ou JSON, ou chaîne) dont
    l'unité est écrite dans sa clé ou dans un champ voisin qui ne commence pas par elle, ou, en fin de
    champ, suivi d'une partie de son unité dont le champ voisin porte le reste (`25 N` puis `m`, que
    les surfaces R3 joignent en `25 Nm`) ; dans le corps, séparé de son unité par du texte ou de la
    structure (unité avant le nombre, en en-tête de colonne, en amorce de liste, après deux-points) ;
    nu, dans une clause dont la grandeur n'a pas de plage pour la famille de la fiche dans
    `_meta/numeric-plausibility.yaml`. Au 2026-10-13, les nombres écrits seuls dans un champ du
    frontmatter des 24 fiches et propositions du WIKI sont des identifiants, des années, des noms de
    modèle ou de motorisation, des puissances, des cylindrées, des rangs, des scores et des comptes.
    Seules les cylindrées (`displacement_cc`, 61 valeurs dans 6 propositions véhicule) seraient lues
    comme valeur dimensionnée si leur unité était écrite à côté ; aucune de ces propositions n'est une
    fiche sécurité ;
  - une unité ou un chiffre écrit en lettres qui leur ressemblent (`Νm`, nu grec ; `2Ƽ Nm`, lettre
    latine ton cinq ; `2З`, zé cyrillique ; `O` pour `0`) ; un chiffre décimal d'une autre écriture
    (bengali, dévanagari) est lu à sa valeur, quel que soit le chiffre latin auquel son glyphe
    ressemble ; un caractère visible que la lecture squelette retire (marque combinante, guillemet,
    symbole d'espace `␣` ou `〿`), entre un nombre et son unité ou entre deux de ses chiffres, est,
    lui, lu, extrait ancré compris ;
  - un caractère que la lecture squelette garde entre un nombre et son unité : ponctuation de nombre
    ou de clause (`20.Nm`, `20,Nm`, `20; Nm`, `20: Nm`, ou un chiffre de compatibilité qui l'écrit,
    `⒛` pour `20.`), point médian ou signe degré qui n'écrit pas une unité (`N·m`, `°C`) : `20·Nm`,
    `20 · Nm`, `20°Nm`. La lecture squelette le garde et `numeric_exactitude.py` n'y lit aucune
    valeur ; seul un nombre nu dans une clause qui nomme une
    grandeur dimensionnée de la famille y est compté ;
  - une valeur écrite en pictogramme (`🔟`, `💯`), sans valeur numérique Unicode, ou en mots
    (`vingt-cinq Nm`, `XXV Nm` en lettres latines) : `numeric_exactitude.py` ne lit que les chiffres
    décimaux ;
  - une unité prolongée par un caractère (`25 mm2`) : `numeric_exactitude.py` lit l'unité sans borne à
    droite ; la valeur reste comptée, sous l'unité qu'elle prolonge (`25 mm`) ;
  - un nombre dont les groupes de chiffres sont séparés par un séparateur de milliers (espace,
    insécable ou fine : `1 200 Nm`), par une barre oblique (fraction : `1/2 Nm`) ou par tout
    caractère visible que la lecture squelette garde ou change en espace (lettre, lettre
    modificative comprise : `1ʼ200 Nm`, `1ʹ200 Nm` ; point médian, ou ce que la compatibilité y
    ramène : `1·200 Nm`, `1·5 Nm` écrit pour `1,5 Nm` ; signe `×` entre deux nombres : `2×25 Nm` ;
    point en chef, changé en espace : `1˙200 Nm`) : `numeric_exactitude.py` n'en lit que le dernier
    groupe (`200 Nm`, `2 Nm`, `5 Nm`, `25 Nm`) ; un extrait ancré qui le porte est classé sur ce
    groupe, plage et concordance des sources comprises (`1 200 Nm` d'une source y corrobore `200 Nm`
    d'une autre), et, pour une barre oblique, aussi sur les chiffres joints de sa lecture squelette
    (`12 Nm`) ;
  - une valeur dont les chiffres sont ceux d'une suite d'échappements d'un caractère non ASCII
    (`%E2%80%89 bar`) : la lecture la décode, mais hors d'un lien la page l'affiche telle qu'écrite,
    ses derniers chiffres devant l'unité (`89 bar`). C'est le prix d'une lecture sans faux positif des
    URL de source accentuées (`Frein_%C3%A0_disque`, jamais lu `3%`), présentes dans le corpus ;
  - le contexte d'un extrait ancré : il est classé sur son propre texte, sa phrase hors de l'ancre
    n'entre pas dans sa clause ;
  - les valeurs que seule l'application connaît (SHA du commit, horodatages), lues sur des valeurs
    neutres de la forme que la promotion écrit ;
  - le texte du catalogue des sources que l'export diagnostic reprend, lu tel qu'il est à la décision
    et non tel que le régénère une modification ultérieure du catalogue ;
  - deux graphies d'un même éditeur : `publisher` est un texte libre ; casse, espaces, forme Unicode et
    caractères invisibles sont normalisés, une autre orthographe compte pour un autre éditeur.
- Une valeur dimensionnée n'est vérifiable que dans une plage `validated` de
  `_meta/numeric-plausibility.yaml`, corroborée par deux sources captées distinctes et concordantes. Une
  valeur liée à une référence ou à un véhicule (`always_ref_specific`) n'est jamais généralisée à la
  gamme.
- La validation d'une plage est un acte humain unique par famille et par grandeur, jamais par fiche.
  Elle passe par une PR WIKI fusionnée par l'owner (ADR-102). Cette PR porte `validated_by` et le
  `source_slug` capté qui fonde la plage.
- Tant qu'une grandeur n'a pas de plage `validated`, toute fiche sécurité qui l'affiche reste bloquée.

### D5 — Levée du verrou : une constante de code, rien d'autre

- La Safety Auto-Gate s'ouvre quand une PR WIKI dédiée inscrit `SAFETY_AUTO_APPROVAL_ADR = "ADR-114"`
  dans `promotion_decision.py`.
- Cette PR n'est recevable que si trois préconditions sont déjà fusionnées dans le WIKI, chacune
  prouvée par un test :
  - (a) le contrôle de D4 lit tout le texte publié, hors des seuls résidus qu'il énumère : la fiche
    promue entière, corps sous ses trois formes, et les documents exportés ;
  - (b) le classifieur couvre l'union L0 d'ADR-093 (D1) ;
  - (c) la condition `proof_sources_min` est calculée par le décideur (D3).
- Aucune variable d'environnement ni aucune option CLI ne lève le verrou.
- Le fichier entre dans l'empreinte du moteur de décision : changer la constante invalide toute
  décision déjà rendue (`STALE_DECISION`).
- Pour refermer la gate, une PR WIKI remet la constante à vide.

### D6 — Issue d'une fiche sécurité

- **Toutes conditions prouvées** : la fiche suit la porte TIER A d'ADR-083, comme toute fiche :
  - `review_status: approved` ;
  - `reviewed_by: skill:promoter@<sha>` ;
  - `auto_promoted: true` ;
  - `exportable.seo: true`.

  Pour une fiche sécurité, cette porte est la seule voie automatique vers `exportable.seo: true`.
  Hors de cette porte, `exportable.seo` ne change que par une PR revue.
- **Une condition non prouvée** : la fiche reste `BLOCKED`, avec la liste de ses conditions
  bloquantes. Une fois la preuve corrigée, la réévaluation est automatique.
  - Un humain contribue en capturant une source, en cataloguant son type ou en validant une plage
    (D4).
  - Il n'approuve jamais une fiche par-dessus une preuve manquante.

### D7 — Ce qui reste inchangé

- `diagnostic_safe: true`, l'autorité sur le moteur diagnostic LIVE, reste un flip humain ciblé
  (ADR-033). La promotion ne le pose jamais.
- L'autorité d'une source inconnue reste humaine (ADR-096 §D5). Une source ne compte qu'une fois
  cataloguée avec son type, et une source en `manual_review` bloque.
- Le RAG n'a aucune autorité d'écriture de contenu (ADR-031, ADR-046).
- Une règle de sécurité du diagnostic exige toujours une source et une relecture humaine (ADR-112 D5).
  La promotion d'une fiche ne vaut pas relecture de ses règles.
- Les fiches non sécurité gardent leur barre actuelle.

### D8 — Observabilité

- Chaque décision rendue sur une fiche sécurité porte :
  - ses conditions ;
  - ses conditions bloquantes ;
  - l'état de la politique (`ratified` ou `not_ratified`, avec l'ADR inscrite) ;
  - le manifeste de ses entrées et les révisions des moteurs.
- La trace existante du décideur suffit : cet ADR ne crée aucun canal.

## Amendements

### ADR-083 (promotion tiered)

- **TIER B** : « tout flag safety » s'entend des contrôles sécurité, `gate_safety_unsourced`
  notamment. Ils restent bloquants.
- L'appartenance d'une fiche à une famille sécurité ne la place plus en TIER B quand la Safety
  Auto-Gate d'ADR-114 est prouvée et ratifiée (D3, D5).
- Une fiche sécurité bloquée l'est par ses motifs (ADR-114 D6). Elle n'attend pas d'approbation
  humaine.
- Le reste d'ADR-083 est maintenu.

### ADR-091 (recalibrage du score)

- **Décision §4**, seconde phrase : les pièces sécurité sont promues selon ADR-114. Sans la
  ratification inscrite dans le code (D5), elles restent bloquées.
- Le seuil applicable aux pièces non sécurité n'est pas modifié par cet ADR.
- Le reste d'ADR-091 est maintenu.

### ADR-093 (auto-review à barre de preuve)

- **Barre par catégorie, « Sécurité »** : « jamais auto-publiée » est remplacé par ADR-114 D3 à D6.
  Une fiche sécurité est promue si toutes les conditions de D3 sont prouvées et la ratification
  inscrite (D5). Sinon elle reste bloquée.
- **§Sécurité, point 1** : l'invariant `is_safety ⇒ eligible=False ⇒ HUMAN_SPOT_CHECK` du script
  monorepo est maintenu tel quel. Ce script n'a pas d'autorité de promotion (ADR-114 D2). L'extension au
  périmètre L0 unifié est portée par le classifieur WIKI (D1).
- **§Sécurité, point 3** (verrou exactitude) : la vérification de valeur est celle d'ADR-114 D4. Une
  valeur chiffrée non vérifiée bloque toujours la fiche.
- **§Sécurité, point 4** : la barrière sécurité est la Safety Auto-Gate d'ADR-114, fail-closed, dans le
  décideur unique.
- **§Humain = exception** :
  - point 1 : une fiche sécurité n'est plus envoyée à un humain, mais bloquée par ses motifs (D6) ;
  - point 9 : pour une fiche sécurité, le passage à `exportable.seo: true` par la porte TIER A suit
    ADR-114 D6.
- **§Ce qui reste** :
  - « Toute la sécurité reste humaine » est remplacé par ADR-114 D4 (validation humaine unique de
    chaque plage chiffrée) et D7 ;
  - « Le flip `exportable.seo` reste 100 % humain » : pour une fiche sécurité, il suit ADR-114 D6.
- **Séquence de sortie, point iv** : réalisé par cet ADR.
- **Couches L1 et L5, points (c) et (d)** : elles reposent sur le verdict du script monorepo et sur
  `cross_check_status`, déclaré par le producteur. Ce script ne décide pas (D2). Pour les fiches
  sécurité, leur objet (diversité réelle des sources primaires) est porté par `proof_sources_min`
  (D3).
- **Couche L5, points (a) et (b)** : portés par les contrôles existants de `quality-gates.py`
  (`confidence_overclaimed`, `source_slug_unknown`) et par la provenance RAW.
- **§Plan de mise en œuvre et §Angles morts** : leurs mentions d'une sécurité humaine se lisent selon
  ADR-114.
- Le reste d'ADR-093 est maintenu : couche L0, couches L2 à L4, barre non sécurité, garde-fous, flag
  `PROMOTE_GATE_ENGINE`.

### ADR-096 (découverte automatique de sources)

- **§D5, premier point** : une donnée de sécurité suit ADR-114. Une source inconnue reste soumise à la
  validation humaine de son autorité. Une valeur numérique critique n'est vérifiée que par ADR-114 D4.
- **§D5, troisième point** : pour une fiche sécurité, le passage à `exportable.seo: true` par la
  porte TIER A suit ADR-114 D6.
- **§D6, dernier point** : la sécurité et les valeurs numériques suivent ADR-114 ; pour une fiche
  sécurité, le passage à `exportable.seo: true` suit ADR-114 D6. L'autorité des sources inconnues et
  les contradictions majeures restent humaines.
- Le scraper n'a toujours aucune capacité de promotion. Le reste d'ADR-096 est maintenu.

## Ce que cet ADR ne fait pas

- Il ne valide aucune plage chiffrée et ne promeut aucune fiche.
- Il ne modifie pas le seuil, le moteur de score ni le flag `PROMOTE_GATE_ENGINE` des fiches non
  sécurité.
- Il ne statue pas sur la voie humaine des fiches non sécurité, supprimée le 2026-09-12 (WIKI #83).
  Pour ces fiches, l'écart entre ce choix et le texte des ADR (TIER B « humain » d'ADR-083,
  `exportable.seo` « 100 % humain » d'ADR-093 et 096, alors que la porte TIER A le pose déjà) reste à
  régulariser par un ADR distinct.
- Il ne met pas en œuvre la barre non sécurité L3 d'ADR-093 (au moins 3 sources primaires), absente du
  décideur WIKI (Contexte). Elle relève d'ADR-093, sans nouvel ADR.
- Il ne bascule aucune entrée en `diagnostic_safe` et ne touche pas le moteur diagnostic LIVE.
- Il ne change aucune URL, aucun meta, aucun H1, ni aucune règle d'indexation.

## Options considérées

### Option A — Statu quo — rejetée

Les ADR interdisent la promotion automatique et le WIKI n'a plus de voie humaine. Aucune fiche sécurité
n'est jamais promue, quelle que soit sa preuve.

### Option B — Rétablir une approbation humaine par fiche sécurité — rejetée

- Elle contredit la décision de l'owner du 2026-09-12.
- Un humain qui approuve une fiche ne vérifie pas mieux un chiffre qu'une plage validée et corroborée
  par deux sources.
- Elle rouvre la possibilité d'approuver par-dessus une preuve manquante.

### Option C — Promotion sécurité sur le score seul — rejetée

Le score prouve la provenance et la structure, jamais l'exactitude d'une valeur. ADR-093 l'a déjà
écarté.

### Option D — Verrou par variable d'environnement ou option CLI — rejetée

Un tel verrou n'est ni revu ni versionné. Il n'invalide pas les décisions déjà rendues.

### Option E — Contrôle des chiffres limité au corps — rejetée

La fiche est publiée entière, et les exports SEO et diagnostic publient son frontmatter, pas sa prose.
Ce contrôle laisserait passer tout le frontmatter.

### Option F — Contrôle limité au texte que projettent les exporteurs — rejetée

Il laisserait passer les champs qu'aucun exporteur ne projette, alors que le dépôt est public et que le
monorepo lit lui-même `wiki/diagnostic/` et `wiki/support/` (ADR-112 D9). Une liste de champs tirée
des lecteurs connus ne couvrirait pas un lecteur ajouté plus tard. Le contrôle de D4 est plus strict ;
son coût est un faux positif possible sur une chaîne interne, qui garde la fiche bloquée.

### Option G — Gate sans sources de preuve ni couverture L0 — rejetée

C'est la gate de #107 telle quelle. Une fiche sécurité y passerait avec moins de sources primaires
qu'ADR-093 n'en exige d'une fiche non sécurité, et les familles absentes du classifieur (roulements,
cardans, visserie de roue) seraient promues comme des pièces ordinaires.

### Option H — Safety Auto-Gate, sources de preuve, vérification de valeur sur le texte publié, constante de code — retenue

D1 à D8.

## Conséquences

### Positives

- Une fiche sécurité peut être promue dès que sa preuve est complète, sans attente humaine par fiche.
- Les fiches sécurité suivent la même boucle SCRAPING → RAW → WIKI → consommateurs que les autres.
- L'acte humain restant est unique par grandeur chiffrée, pas par fiche.
- Chaque décision est traçable et rejouable.

### Négatives

- Tant qu'aucune plage n'est validée, toute fiche sécurité qui affiche une valeur dimensionnée reste
  bloquée. C'est voulu.
- Une chaîne interne qui porte un nombre et une unité bloque la fiche comme une valeur affichée (D4).
  Il faut alors la réécrire : hors du corps, aucune ancre n'existe et la valeur ne peut pas être
  vérifiée.
- Une valeur dimensionnée ne peut vivre que dans la prose ancrée du corps. Dans le frontmatter ou un
  export, elle bloque la fiche même sur une plage `validated` (D4).
- Un lecteur qui assemble un nombre et l'unité écrite dans sa clé ou dans un champ voisin, ou coupée
  entre deux champs voisins, peut afficher une valeur que la gate n'a pas lue comme telle (résidus de
  D4).
- La détection de contradiction dans la prose reste déclarative (`no_disputed_claims`). Une
  contradiction non déclarée n'est rattrapée que par les contrôles existants.
- La gate vérifie l'existence, le type et la cohérence des sources, et la valeur des chiffres. Elle ne
  vérifie pas le sens d'une affirmation sans chiffre. La première fiche promue doit être relue après
  coup (Métriques).

## Métriques

- Nombre de fiches sécurité `ELIGIBLE` et `BLOCKED`, avec la répartition des conditions bloquantes.
- Nombre de plages `validated` sur le total des plages.
- Relecture a posteriori de chaque fiche sécurité promue pendant les 30 jours qui suivent la levée du
  verrou, consignée dans la PR qui l'a promue.

## Retour arrière

- Une PR WIKI remet `SAFETY_AUTO_APPROVAL_ADR` à vide. Toute décision rendue devient `STALE_DECISION` et
  les fiches sécurité redeviennent bloquées.
- Une fiche déjà promue se retire par une PR WIKI revue, comme toute fiche approuvée.
- Retirer cet ADR rend à ADR-083, 091, 093 et 096 leur texte antérieur.

## Revue planifiée

**Date** : J+90 après la levée du verrou dans le code, ou le 2027-01-11 si le verrou n'a pas été levé.

**Critères** :

- les métriques ci-dessus et les relectures a posteriori ;
- un éventuel défaut de valeur ou de sens dans une fiche promue : si c'est le cas, refermer la gate
  (Retour arrière) avant toute analyse ;
- l'état de la détection de contradiction dans la prose.

## Références

- [[ADR-083-tiered-wiki-promotion|ADR-083]] ·
  [[ADR-091-wiki-score-recalibration|ADR-091]] ·
  [[ADR-093-auto-review-earn-gate|ADR-093]] ·
  [[ADR-096-governed-automatic-source-discovery|ADR-096]] ·
  [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] ·
  [[ADR-035-diagnostic-tool-source-trust-flag|ADR-035]] ·
  [[ADR-059-seo-runtime-projection|ADR-059]] ·
  [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] ·
  [[ADR-088-promotion-gate-substance-scoring|ADR-088]] ·
  [[ADR-089-content-coverage-map-canon|ADR-089]] ·
  [[ADR-032-diagnostic-maintenance-unification|ADR-032]] ·
  [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]]
- WIKI : PR #83 (validation automatique, 2026-09-12), PR #107 (Safety Auto-Gate),
  `_meta/quality-gates.md` §6 et §7, `_scripts/promotion_decision.py`, `_scripts/numeric_exactitude.py`,
  `_meta/numeric-plausibility.yaml`, `_scripts/build_exports_seo.py`,
  `_scripts/build_exports_diagnostic.py`.
- (Relations structurées : voir `amends` / `related_adr` dans le frontmatter.)
