---
id: ADR-116
title: "Relations de diagnostic hors sécurité relues par une règle de preuve vérifiée par le décideur WIKI : amende ADR-033 (D1, D4) et ADR-112 (principe directeur, D12), étend ADR-093"
status: accepted
date: "2026-10-15"
decision_date: "2026-10-15"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-033", "ADR-112"]
amended_by: ["ADR-117"]
extends: ["ADR-093"]
related_adr: ["ADR-031", "ADR-033", "ADR-035", "ADR-046", "ADR-083", "ADR-093", "ADR-096", "ADR-112", "ADR-113", "ADR-114", "ADR-115"]
related_rules: ["G1", "G6", "Q1", "Q2", "AP-11"]
related_incidents: ["INC-2026-013"]
version: "1.0.0"
---

# ADR-116 : Relations de diagnostic hors sécurité — relecture par une règle de preuve

- **Statut** : Accepted (2026-10-15). La fusion par l'owner vaut ratification.
- **Amende** :
  - [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] : D1 (sens de `evidence.reviewed`,
    deux champs ajoutés) et D4 (dernière phrase) ;
  - [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] : principe directeur et D12 (dernier point).

  Chaque amendement est décrit en §Amendements. Le reste de ces ADR reste en vigueur.
- **Étend** [[ADR-093-auto-review-earn-gate|ADR-093]] : sa barre L3 (au moins 3 sources primaires
  distinctes hors sécurité) s'applique aussi à chaque relation, durcie comme
  [[ADR-114-wiki-safety-auto-gate|ADR-114]] D3. Le texte d'ADR-093 ne change pas (§Rapport avec ADR-093).
- **Ne modifie ni ADR-115 ni ADR-035.** ADR-115 projette une relation qui porte `evidence.reviewed: true`
  « posé selon ADR-033 D4 », et ne ferme aucune des voies qu'ADR-033 D4 et ADR-112 D12 admettent. Une
  relation relue selon cet ADR est donc projetable sans changer leur texte.
- **Pourquoi un ADR séparé** : ADR-033 D4 réserve le passage à `reviewed: true` à un humain ou à une
  « règle ADR explicite ». Cette règle n'existe pas ; cet ADR l'écrit. ADR-033 et ADR-112 sont acceptés,
  leur texte n'est pas rouvert, comme pour ADR-115.
- **Méthode** : constats vérifiés le 2026-10-15, en lecture seule :
  - `main` du WIKI au commit `9545e8d` (#114 fusionnée) ; PR WIKI #113 relue à sa tête `be372f4`,
    puis resynchronisée sur ce `main` en `e922869` sans changement de son contenu ;
  - `main` du vault au commit `f68336e` ;
  - relations comptées avec les fonctions du décideur WIKI (`_publisher_key`,
    `source_type_editorial_role` du catalogue), restreintes aux sources de chaque relation.

## Contexte

### La porte de la phase 2 d'ADR-112 n'a pas de chemin

ADR-112 D13 ferme la phase 2 sur « au moins une affirmation projetée avec une provenance vivante ».
Depuis ADR-115, une relation n'est projetée que si elle porte `evidence.reviewed: true`. Aucune voie ne
pose cette valeur aujourd'hui :

| Voie admise | État au 2026-10-15 |
|---|---|
| Relecture « manuelle » (ADR-033 D4) | le WIKI n'a plus de voie humaine depuis le 2026-09-12 (WIKI #83). Une proposition qui déclare elle-même sa relecture n'est pas une relecture humaine : WIKI #113, en revue, la bloque (`REVIEW_AUTHORITY_CLAIMED`) |
| « Règle ADR explicite » (ADR-033 D4) | aucune n'existe |
| Relecture automatique (ADR-112 D12) | limitée « aux cas déjà couverts par ADR-093 ». ADR-093 et ADR-114 promeuvent des fiches entières. Le promoteur (`_promoted_frontmatter`) pose les champs de revue de la fiche et recopie ses relations telles que proposées : il ne touche jamais une relation |

La porte de la phase 2 est donc inatteignable par construction. Les 162 liens de l'amorce resteraient
tous « non sourcés » (ADR-112 D14, condition 3), et la base ne pourrait pas devenir experte, ce qui est
l'objectif d'ADR-112. C'est le blocage qu'ADR-114 a levé pour les fiches sécurité : une exigence
humaine, sans voie humaine.

### Les relations d'aujourd'hui

Les cinq relations du WIKI (`main`, `9545e8d`). Toutes sont hors sécurité, `reviewed: false`,
`diagnostic_safe: false`, sans `cause_slug` :

| Fiche | Symptôme | `source_policy` | Sources | Éditeurs de rôle `proof` | Citations |
|---|---|---|---|---|---|
| filtre-a-air | `perte_puissance_filtration` | `2_medium_concordant` | 2, `to_capture` | 0 | 0 |
| filtre-a-carburant | `perte_puissance_filtration` | `2_medium_concordant` | 2, `to_capture` | 0 | 0 |
| filtre-a-huile | `voyant_huile` | `manual_review` | 1, `active` (`oem_manual`) | 1 (Renault) | 0 |
| filtre-a-huile | `perte_puissance_filtration` | `manual_review` | 2, `active` (`oem_manual`) | 2 (Filtron (MANN+HUMMEL), MAHLE Aftermarket) | 0 |
| filtre-d-habitacle | `odeur_habitacle` | `manual_review` | 1, `active` (`blog_pro`, rôle `corroboration`) | 0 | 0 |

Avec la règle de D2, **aucune des cinq** ne serait relue aujourd'hui. C'est voulu : la règle ne relit
que ce que la preuve porte. Elle donne en revanche à chaque relation une cible mesurable : sources
capturées, trois éditeurs de preuve, extraits ancrés.

### Ce que les contrôles existants prouvent déjà

| Contrôle (WIKI) | Ce qu'il prouve |
|---|---|
| `_citation_issues` (`quality-gates.py`) | une citation nomme une source de **sa propre** relation, `active` et prouvée dans RAW |
| `gate_citation_anchors` (`quality-gates.py`) | l'extrait cité (début, fin, empreinte) correspond aux octets de l'archive RAW épinglée par `raw_ref.expected_sha256` ; exécuté par la promotion |
| `gate_diagnostic_relations` (`quality-gates.py`) | `source_policy` respectée par relation (`source_policy_violated`, `_meta/quality-gates.md` §5.bis) |
| `_safety_proof_publishers` (`promotion_decision.py`, ADR-114 D3) | éditeurs distincts de rôle `proof`, à l'échelle de la fiche |
| vérification de valeur (ADR-114 D4) | une valeur chiffrée publiée est vérifiée contre une plage validée |

Deux limites concernent la durée de vie d'une ancre :

- les ancres ne sont vérifiées qu'à la promotion. Le gate cross-repo (`quality-gates.py --cross-repo`)
  tourne hors CI, dans le flux gouverné d'activation, et ne vérifie que le `raw_ref` des sources ;
- le garde d'activation (`check-activation-guard.py`) ne bloque que le passage d'une source à
  `active`. Changer le `raw_ref` d'une source déjà `active` se fait par simple édition.

Aucun contrôle ne prouve que l'extrait cité **soutient le sens** de la relation. C'est le risque 4
d'ADR-093 (« jamais le CONTENU sémantique »). Cet ADR le déclare (§Conséquences négatives) ; il ne le
masque pas.

## Principe directeur

> Une relation de diagnostic hors sécurité est relue par la preuve qu'elle porte, vérifiée par le
> décideur unique du WIKI. Ce que la machine ne sait pas vérifier la laisse non relue. La règle ne pose
> jamais `diagnostic_safe`, ne touche jamais à la sécurité, et ne remplace aucune preuve manquante.

## Décisions

### D1 — Périmètre

- **Entrent** : les entrées `diagnostic_relations[]` d'une fiche gamme que
  `_scripts/safety_families.py::is_safety_proposal` classe hors sécurité. Un doute ou une erreur de
  classification vaut sécurité (ADR-114 D1).
- **N'entrent pas** :
  - les relations d'une fiche sécurité ;
  - `safety_rules[]` : une règle de sécurité exige une relecture humaine (ADR-112 D5) ;
  - `diagnostic.quick_checks[]` et `diagnostic_not_applicable` ;
  - `evidence.diagnostic_safe`, sur toute entrée.

### D2 — Conditions, toutes prouvées, pour chaque relation

| Condition | Preuve exigée |
|---|---|
| `fiche_eligible` | la fiche porteuse est `ELIGIBLE` au décideur, avec tout ce qu'il contrôle pour une fiche |
| `not_safety` | D1 |
| `sources_raw_proven` | toutes les sources de la relation sont `active` avec un `raw_ref` (la définition de `raw_proven` des exports) |
| `citations_anchored` | au moins une citation, et toutes ses citations passent `_citation_issues` et `gate_citation_anchors` |
| `proof_publishers_min` | au moins 3 éditeurs distincts de rôle `proof` parmi les sources nommées par les citations ancrées de la relation ; même calcul qu'ADR-114 D3 (`_publisher_key`, rôle lu dans `source_type_editorial_role` du catalogue, raison rapportée pour chaque source non comptée) |
| `source_policy_resolved` | `evidence.source_policy` différent de `manual_review`, et aucun `source_policy_violated` sur la relation |
| `numeric_verified` | toute valeur chiffrée du texte de la relation passe la vérification de valeur d'ADR-114 D4 |
| `no_review_claimed` | la proposition ne déclare aucune relecture (`REVIEW_AUTHORITY_CLAIMED`, WIKI #113) |

Pourquoi 3 éditeurs :

- ADR-093 L3 exige au moins 3 sources primaires distinctes pour promouvoir une fiche hors sécurité sans
  humain. Une relation relue sans humain ne peut pas exiger moins qu'une fiche.
- ADR-114 D3 durcit cette barre de deux façons, reprises ici : les sources sont distinguées par
  éditeur, et seul le rôle `proof` du catalogue compte.
- Seules comptent les sources dont un extrait est ancré : chaque éditeur compté a un passage vérifiable
  dans RAW.

Règles communes :

- une condition dont le calcul échoue est fausse, et son erreur est rapportée ;
- un résultat absent n'est jamais un succès ;
- durcir une condition se fait par PR WIKI ; l'assouplir exige un ADR.

### D3 — Écriture : un seul writer, une relecture jamais héritée

- Seul `apply_promotion` écrit, au moment où il promeut la fiche, par `_promoted_frontmatter`. Aucun
  autre script et aucune option ne pose la valeur.
- Pour chaque relation de D1 :
  - toutes conditions prouvées : `evidence.reviewed: true`,
    `evidence.reviewed_by: "rule:ADR-116@<révision du décideur>"`, `evidence.reviewed_at: <date UTC>` ;
  - sinon : `evidence.reviewed: false`, sans `reviewed_by` ni `reviewed_at`.
- Une relation non relue ne bloque jamais la promotion de sa fiche.
- La relecture n'est jamais héritée. La proposition porte toujours `reviewed: false` (WIKI #113) : la
  relecture est recalculée à chaque promotion de la fiche.
- Les entrées hors D1 sont écrites telles que proposées, comme aujourd'hui.
- **Révocation**, sans mécanisme nouveau :
  - une source qui n'est plus `active` fait perdre `raw_proven` à la relation dans l'export ; ADR-115
    retire alors sa provenance au run suivant (`retired_at`) ;
  - une archive RAW ré-épinglée qui casse un extrait ancré fait échouer le gate cross-repo (D4,
    précondition d) : la ré-épingle est bloquée tant que la fiche n'est pas corrigée.

### D4 — Verrou : une constante de code, rien d'autre

- Constante `RELATION_REVIEW_ADR: str | None = None` dans `promotion_decision.py`, sur le modèle de
  `SAFETY_AUTO_APPROVAL_ADR` (ADR-114 D5).
- **Vide** : mode report-only. Le décideur calcule les conditions de D2 et les inscrit dans sa trace
  (`would_review`). Il n'écrit rien dans la fiche.
- Une PR WIKI dédiée inscrit `RELATION_REVIEW_ADR = "ADR-116"`. Elle n'est recevable que si ces
  préconditions sont déjà fusionnées, chacune prouvée par un test :
  - (a) les conditions de D2 sont calculées par le décideur ;
  - (b) la garde `REVIEW_AUTHORITY_CLAIMED` de WIKI #113 est fusionnée, et refuse aussi `reviewed_by`
    et `reviewed_at` dans une proposition ;
  - (c) le schéma de frontmatter admet `evidence.reviewed_by` et `evidence.reviewed_at` ;
  - (d) une ancre ne peut plus casser en silence. Deux composants existants sont étendus, aucun n'est
    créé :
    - `quality-gates.py --cross-repo`, seul chemin qui enforce le gate cross-repo, vérifie aussi les
      ancres des citations des fiches du canon, et plus seulement celles d'une fiche promue ;
    - `check-activation-guard.py` traite un changement du `raw_ref` d'une source déjà `active` comme
      une activation. Ce changement passe donc par le flux gouverné d'activation, qui exécute
      `--cross-repo`. Aujourd'hui, le garde ne bloque que le passage d'une source à `active` ;
  - (e) la PR porte la mesure report-only du corpus : relations évaluées, `would_review`, motifs.
- Aucune variable d'environnement ni aucune option CLI ne lève le verrou.
- Le fichier entre dans l'empreinte du moteur de décision : changer la constante invalide toute
  décision déjà rendue (`STALE_DECISION`).
- Pour refermer la règle, une PR WIKI remet la constante à vide (§Retour arrière).

### D5 — Ce qui reste inchangé

- `diagnostic_safe: true` reste un flip humain ciblé (ADR-033 critère 9, `_meta/quality-gates.md`
  §5.bis). Une relation relue par la règle est donc plafonnée à « possible » : « probable » exige
  `diagnostic_safe: true` (ADR-112 D3).
- Une règle de sécurité exige une relecture humaine (ADR-112 D5).
- Un agent ou un LLM ne fait que proposer (ADR-112 D12, deuxième point). Le décideur n'est pas un agent
  qui propose : c'est du code déterministe, versionné dans l'empreinte du moteur, qui vérifie.
- Le RAG n'a aucune autorité d'écriture de contenu (ADR-031, ADR-046).
- La condition de projection d'ADR-115 et l'ordre de ses conflits.
- Le jeu de référence d'ADR-112 D11 reste relu par un humain.
- Le mode « créer ou remplacer » d'ADR-112 D2 garde ses conditions. Une relation relue par la règle et
  qui porte un `cause_slug` y est admise : D2 de cet ADR exige déjà ses citations ancrées et ses
  sources `raw_proven`.

### D6 — Observabilité

- Chaque décision rendue porte, pour chaque relation de D1 :
  - ses conditions et ses conditions bloquantes ;
  - les éditeurs comptés, et les sources non comptées avec leur raison ;
  - l'état de la politique : `ratified` avec l'ADR inscrite, ou `not_ratified`.
- La trace existante du décideur suffit : cet ADR ne crée aucun canal.
- Côté monorepo, les conflits `not_reviewed` d'ADR-115 comptent les relations capturées et pas encore
  relues.

## Amendements

### ADR-033 (contrat WIKI des relations)

- **D1, `reviewed`** : « statut de validation humaine » devient « statut de relecture : par un humain,
  ou, pour une relation hors sécurité, par la règle de preuve d'ADR-116 ».
- **Champs ajoutés** au bloc `evidence`, optionnels, écrits par le seul décideur WIKI (ADR-116 D3) :
  - `reviewed_by` : `rule:ADR-116@<révision>` pour une relecture par la règle ;
  - `reviewed_at` : date UTC de la relecture.
- **D4, dernière phrase** : « Le flip à `reviewed = true` ou `diagnostic_safe = true` est strictement
  manuel ou couvert par règle ADR explicite, jamais en automatique » devient :
  - le flip à `reviewed = true` ou `diagnostic_safe = true` est strictement manuel ou couvert par une
    règle ADR explicite ;
  - ADR-116 est cette règle pour `reviewed`, sur les relations hors sécurité ;
  - aucune règle ne couvre `diagnostic_safe` ;
  - hors d'une telle règle, jamais en automatique.
- Le reste d'ADR-033 est maintenu, dont son critère 9.

### ADR-112 (base de connaissances diagnostic)

- **Principe directeur** : « WIKI relu par un humain » se lit « WIKI relu par un humain, ou, pour une
  relation hors sécurité, par la règle de preuve d'ADR-116 ».
- **D12, dernier point** : « La relecture automatique ne s'applique qu'aux cas déjà couverts par
  ADR-093 » devient « … qu'aux cas couverts par ADR-093 et, pour les relations hors sécurité, par
  ADR-116 ». « Elle ne s'étend jamais aux règles de sécurité » est maintenu.
- **D12, deuxième point** : maintenu.
- **D13, phase 2** : la porte est inchangée. Elle devient atteignable : une relation relue par la règle,
  dont toutes les sources sont `raw_proven` et qui se résout vers un lien existant, donne une
  provenance vivante (ADR-115).
- Le reste d'ADR-112 est maintenu, dont D3, D5 et D11.

## Rapport avec ADR-093 (extension)

- ADR-093 fixe la barre de promotion d'une fiche. Cet ADR applique sa barre L3 à chaque relation, avec
  les deux durcissements d'ADR-114 D3 (D2, `proof_publishers_min`).
- Le reste du gate s'applique par la fiche porteuse (`fiche_eligible`). Le périmètre sécurité est celui
  de L0, porté par le classifieur unique (D1).
- Le risque 4 d'ADR-093 s'applique ici tel quel (§Conséquences négatives).
- Le texte d'ADR-093 ne change pas.

## Ce que cet ADR ne fait pas

- Il ne relit aucune relation : aucune des cinq ne remplit D2, et le verrou est fermé.
- Il ne pose pas `diagnostic_safe` et n'ouvre aucune voie pour le poser.
- Il ne touche ni aux règles de sécurité, ni aux relations des fiches sécurité, ni à `quick_checks`.
- Il ne change ni la barre de promotion des fiches, ni ADR-115, ni le writer monorepo.
- Il ne rouvre aucune voie humaine dans le WIKI et n'en ferme aucune.
- Il ne change aucune URL, aucun meta, aucun H1, ni aucune règle d'indexation.

## Mise en œuvre

Une PR WIKI, après la fusion de cet ADR, en report-only :

- conditions de D2 dans le décideur, constante vide, trace de D6 ;
- schéma : `evidence.reviewed_by` et `evidence.reviewed_at` ; description de `reviewed` alignée sur
  ADR-033 D1 amendé ;
- garde `REVIEW_AUTHORITY_CLAIMED` de WIKI #113, fusionnée d'abord, étendue à ces deux champs ;
- ancres des fiches du canon vérifiées par `quality-gates.py --cross-repo`, et changement du
  `raw_ref` d'une source `active` soumis au garde d'activation (D4, précondition d) ;
- tests : chaque condition en échec puis en succès, relecture jamais héritée, constante vide sans
  aucune écriture.

Puis la PR de levée de D4, une fois la mesure report-only faite.

Aucune PR monorepo : la projection (ADR-115) lit déjà `reviewed`.

## Options considérées

### Option A — Statu quo — rejetée

La porte de la phase 2 reste inatteignable, et tous les liens restent « non sourcés ».

### Option B — Une relecture humaine par relation — rejetée

Elle rétablirait, pour les seules relations, la validation humaine systématique supprimée le
2026-09-12 (WIKI #83). Elle ne rend pas non plus la preuve plus vérifiable : D2 l'exige pour chaque
relation.

### Option C — Une barre plus basse (2 sources, ou 1 source constructeur) — rejetée

C'est la barre de « probable » d'ADR-112 D3, qui suppose une relecture humaine en plus. Sans humain,
elle serait plus basse que la barre L3 d'une fiche.

### Option D — Un contrôle lexical (symptôme et pièce cités dans l'extrait) — rejetée

Un tel contrôle serait une heuristique liée à la langue, alors que les sources sont en plusieurs langues.
Il ne prouverait pas le sens et donnerait une fausse assurance. Le risque est déclaré à la place.

### Option E — Une relecture par un LLM — rejetée

Un LLM ne fait que proposer (ADR-112 D12 et son option C).

### Option F — Un verrou par variable d'environnement ou option CLI — rejetée

Même raison qu'ADR-114 option D : le verrou doit être inscrit, revu et versionné avec le décideur.

### Option G — Une règle de preuve dans le décideur unique, verrouillée, report-only d'abord — retenue

D1 à D6.

## Conséquences

### Positives

- La porte de la phase 2 d'ADR-112 a un chemin, qui reste fermé tant que la preuve manque.
- Chaque relation a une cible mesurable : sources capturées, trois éditeurs de preuve, extraits ancrés.
- Toute relecture par la règle est traçable (`reviewed_by`), révoquée quand sa preuve tombe, et
  réversible en bloc.
- Une seule autorité, le décideur existant : aucun second décideur.

### Négatives

- Aucun contrôle ne prouve que l'extrait soutient la relation (ADR-093, risque 4). Une relation fausse,
  citée chez trois éditeurs avec des extraits ancrés, serait relue. Atténuations :
  - la barre de trois éditeurs de preuve ;
  - des extraits vérifiables dans RAW ;
  - le plafond « possible », faute de `diagnostic_safe` ;
  - la relecture a posteriori (§Métriques) et la révocation.
- Aucune relation sur cinq aujourd'hui : le gain dépend de la capture (ADR-096) et de la rédaction des
  citations.
- Deux PR WIKI avant la première relecture.

## Métriques

- Par run du décideur : relations évaluées, `would_review` (report-only) ou relues, motifs bloquants par
  condition.
- Monorepo : conflits `not_reviewed` (ADR-115). Ils baissent quand des relations capturées sont relues.
- Relecture a posteriori, dans les 30 jours après la levée : les extraits cités des relations relues par
  la règle sont relus. Un désaccord donne une proposition corrective de la fiche ; un seul désaccord
  avance la revue de cet ADR.

## Retour arrière

- Une PR WIKI remet `RELATION_REVIEW_ADR` à vide.
- Les fiches dont une relation porte `reviewed_by: rule:ADR-116@…` sont promues à nouveau. Leur
  proposition porte `reviewed: false` (WIKI #113) : leurs relations repassent à `false`, et ADR-115
  retire leur provenance au run suivant. Aucune édition à la main du canon.
- Un nouvel ADR retire la règle.

## Revue planifiée

**Date** : J+90 après la levée du verrou, ou le 2027-01-13 si le verrou n'est pas levé d'ici là.

**Critères** :

- relations relues par la règle, et motifs bloquants les plus fréquents ;
- résultat de la relecture a posteriori ;
- aucune relation de fiche sécurité relue par la règle, aucun `diagnostic_safe` posé par elle ;
- évolution des conflits `not_reviewed`.

## Références

- [[ADR-033-wiki-gamme-diagnostic-relations-contract|ADR-033]] ·
  [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] ·
  [[ADR-093-auto-review-earn-gate|ADR-093]] ·
  [[ADR-114-wiki-safety-auto-gate|ADR-114]] ·
  [[ADR-115-diagnostic-projection-requires-review|ADR-115]] ·
  [[ADR-035-diagnostic-tool-source-trust-flag|ADR-035]] ·
  [[ADR-113-diagnostic-coverage-target|ADR-113]]
- WIKI : PR #83 (validation automatique, 2026-09-12), PR #113 (relecture auto-déclarée refusée ; en revue le 2026-10-15),
  PR #114 (Safety Auto-Gate, éditeurs de preuve distincts), `_meta/quality-gates.md` §5.bis et §7,
  `_scripts/promotion_decision.py`, `_scripts/quality-gates.py`, `_scripts/build_exports_diagnostic.py`.
- (Relations structurées : voir `amends` / `extends` / `related_adr` dans le frontmatter.)

---

*Proposé le : 2026-10-15*
*Accepté le : à la fusion owner (fusion = ratification)*
