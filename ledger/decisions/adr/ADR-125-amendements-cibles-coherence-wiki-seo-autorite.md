---
id: ADR-125
title: "Amendements ciblés de cohérence : validation sur preuve, seuil 0.85, chemins WIKI au singulier, pilote R2 et compatibilité absente, statut de GOVERNANCE-HUMAN : amende ADR-031, ADR-066, ADR-068, ADR-083, ADR-086, ADR-091, ADR-092, ADR-094, ADR-107 et G1"
status: proposed
date: "2026-11-10"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-031", "ADR-066", "ADR-068", "ADR-083", "ADR-086", "ADR-091", "ADR-092", "ADR-094", "ADR-107", "rules-vault"]
extends: []
related_adr: ["ADR-027", "ADR-031", "ADR-066", "ADR-067", "ADR-068", "ADR-076", "ADR-083", "ADR-086", "ADR-090", "ADR-091", "ADR-092", "ADR-094", "ADR-095", "ADR-099", "ADR-101", "ADR-102", "ADR-107", "ADR-112", "ADR-114", "ADR-117", "ADR-119", "ADR-121", "ADR-123"]
related_rules: ["G1", "Q4", "RULE-H0"]
related_incidents: []
version: "1.0.0"
---

# ADR-125 : amendements ciblés de cohérence (WIKI, SEO R2, autorité de GOVERNANCE-HUMAN)

- **Statut** : Proposed (2026-11-10). Rédigé par un agent (Claude CLI) sur délégation de l'owner. Il
  reste `proposed` jusqu'au commit de ratification
  ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D7). D'ici là, aucun de ses
  textes n'est en vigueur.
- **Amende** :
  - [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] : §3, §5 et §7 (D1) ;
  - [[ADR-092-rank1-content-gate|ADR-092]] : « Ce qui reste HUMAIN », Garde-fous, Angles morts (D1) ;
  - [[ADR-094-page-quality-composite-gate|ADR-094]] : Risque résiduel, point 2 (D1) ;
  - [[ADR-107-wiki-export-structured-lists-and-faq|ADR-107]] : D5 (D1) ;
  - [[ADR-083-tiered-wiki-promotion|ADR-083]] : TIER A, Invariant, Conséquences (D2) ;
  - [[ADR-091-wiki-score-recalibration|ADR-091]] : Contexte et Décision §4 (D2) ;
  - [[ADR-031-four-layer-content-architecture|ADR-031]] : amendement D23 (D3) ;
  - [[ADR-066-r2-content-composition-v2|ADR-066]] : porte « Gate V1 → PR 2 » (D4) ;
  - [[ADR-068-r2-doctrine-strict-no-auto-deindex|ADR-068]] : §C ligne `REJECT` et §D raison 4 (D4) ;
  - G1 de [[rules-vault]] (D5).

  Le reste de ces textes reste en vigueur.
- **Pourquoi un seul ADR** : les cinq décisions ont la même nature. Chacune aligne un texte sur une
  décision déjà prise ou sur un état déjà servi. Aucune ne change un comportement.
- **Méthode** : constats vérifiés le 2026-11-10, en lecture seule :
  - `main` du vault au commit `9250ca7` ;
  - `main` du dépôt WIKI au commit `d5c9453` : `_scripts/promotion_decision.py`,
    `_scripts/promote.py`, `_meta/quality-gates.md`, arborescence `wiki/` ;
  - `main` du monorepo au commit `068a917` : `frontend/app/utils/pieces-vehicle.loader.server.ts`,
    `frontend/app/utils/pieces-vehicle.meta.ts`, `scripts/wiki/wiki-readiness-check.py`.

  Non vérifié : ce que PREPROD et PROD servent réellement.

## Contexte

L'analyse du vault du 2026-11-10 a relevé cinq endroits où deux textes en vigueur se contredisent, ou
contredisent ce qui est servi.

| # | Textes | Écart |
|---|---|---|
| 1 | ADR-086, ADR-092, ADR-094, ADR-107 contre [[ADR-119-wiki-semantic-auto-review-replaces-human-review\|ADR-119]] D1 | ADR-119 D1 : aucune relecture, approbation ni vérification par sondage faite par un humain n'est une condition de promotion. Il amende huit ADR, pas ces quatre. Ils disent encore « couche humain-validée », « TIER B humain », « spot-check humain borné » lu comme plancher, « validation owner ». |
| 2 | ADR-083, ADR-091 contre le dépôt WIKI et [[ADR-117-wiki-promoter-canon-revision\|ADR-117]] | ADR-083 : seuil « proposé 0.80, owner-tunable ». ADR-091 : « 0.84 (ADR-083) » puis « 1.01 → 0.80 ». Servi depuis la PR WIKI #83 (2026-09-12) : `AUTO_PROMOTE_THRESHOLD = 0.85` (`promotion_decision.py:623`), `quality-gates.md` §7. ADR-117 cite 0.85. |
| 3 | ADR-031, amendement D23, contre le corps d'ADR-031 et le dépôt WIKI | Le corps fige `wiki/<entity_type_singular>/` et interdit le pluriel. D23 (2026-04-28) adopte le pluriel et se dit « l'autorité actuelle ». Le dépôt WIKI est au singulier depuis sa PR #24 (2026-05-13) : `wiki/constructeur`, `wiki/diagnostic`, `wiki/gamme`, `wiki/support`, `wiki/vehicle`. |
| 4a | ADR-066 contre [[ADR-067-r2-no-auto-suppression\|ADR-067]] | ADR-067 interdit `SUPPRESSED` automatique. La porte du pilote d'ADR-066 exige encore « 2-4 SUPPRESSED ». |
| 4b | ADR-068 contre [[ADR-076-soft-404-r2-strategy\|ADR-076]] | ADR-068 §D range « compatibilité absente » parmi les raisons de `REJECT`, dont la publication est « 404/410 ». ADR-076, postérieur, décide pour ce cas « HTTP 200 + `robots: noindex, follow` […] Pas 404/410 », sans amender ADR-068. Le code servi suit ADR-076 (`pieces-vehicle.loader.server.ts`, branche `noProducts`). |
| 5 | G1 de `rules-vault` contre `ops/GOVERNANCE-HUMAN.md` | G1 classe `governance-vault/ops/*` en « OPS - MOC, templates, scripts », sans autorité. Le fichier se dit « above ADRs » et « overrides any other document ». Or [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4\|ADR-102]], ADR-121 et [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte\|ADR-123]] ont amendé ses règles RULE-H3 à H6 comme un texte normatif. |

Deux points de la même analyse ne demandent aucune décision :

- ADR-090 contre ADR-027 (repli S2_DIAG) : déjà tranché par
  [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]], §Amendements ;
- les bannières « PROPOSÉ » et « DRAFT vault » d'ADR-083 et d'ADR-090, et la ligne « Proposed »
  d'ADR-095 : leur frontmatter dit `accepted` et fait foi
  ([[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport|ADR-099]], Erratum). La PR
  qui porte cet ADR corrige ces en-têtes ; ce sont des errata, pas des décisions.

## Principe directeur

Un texte en vigueur ne contredit ni un autre texte en vigueur, ni ce qui est servi sans le dire. Quand
la décision est déjà prise ailleurs, l'amendement la recopie et ne décide rien de plus.

## Décisions

### D1 — La validation d'une fiche WIKI se fait sur preuve, partout

ADR-119 D1 s'applique à ADR-086, ADR-092, ADR-094 et ADR-107. Une fiche WIKI est validée par son
décideur unique sur preuve, auto-review de sens comprise. Un humain peut contribuer, restreindre ou
retirer ; il n'approuve pas.

`rank_spotcheck` (ADR-092) n'existe dans aucun script du dépôt WIKI. Il reste une contribution humaine
facultative. Son absence ne bloque ni ne plafonne une promotion. Un verdict `fail` est un signalement
humain : il se traite par le retrait de la fiche ou par une nouvelle capture (ADR-119 D1).

### D2 — Le plancher de la promotion automatique est 0.85

La valeur en vigueur d'`AUTO_PROMOTE_THRESHOLD` est 0.85. ADR-083 laissait ce seuil au réglage de
l'owner ; il vaut 0.85 depuis la PR WIKI #83 (2026-09-12, `quality-gates.md` §7). La ratification de
cet ADR consigne cette valeur. La changer est une décision de l'owner, portée par une PR WIKI et
consignée dans un ADR.

### D3 — L'amendement D23 d'ADR-031 est abrogé

La convention de chemin figée dans le corps d'ADR-031 est la seule : `wiki/<entity_type_singular>/`.
Une mention de `wiki/gammes/`, `wiki/vehicles/` ou `wiki/constructeurs/` dans un texte du vault se lit
au singulier.

### D4 — R2 : pas de `SUPPRESSED` dans le pilote, HTTP 200 pour la compatibilité absente

- La borne « 2-4 SUPPRESSED » de la porte du pilote d'ADR-066 est caduque depuis ADR-067. Cet ADR ne
  la remplace par aucun chiffre.
- Pour la raison 4 de `REJECT` d'ADR-068 (compatibilité absente), la réponse HTTP est celle
  d'ADR-076. Les codes 404 et 410 restent ceux des raisons 1 à 3.

### D5 — `GOVERNANCE-HUMAN` porte des règles normatives, modifiées comme les règles

- Les règles RULE-H0 à RULE-H6 de [[GOVERNANCE-HUMAN]] sont normatives au sens de G1, au même rang que
  `ledger/rules/rules-*.md` : elles se modifient par PR signée, et un changement de décision passe par
  un ADR. C'est la pratique depuis ADR-102.
- Ce fichier prime sur tout prompt, comportement d'agent, automatisation et document non normatif.
- Entre ce fichier et un ADR accepté ou une règle, une contradiction est un constat (G1). L'owner la
  tranche par un ADR. Aucun des deux textes ne l'emporte d'office.
- RULE-H0 est inchangée : l'owner reste la seule autorité. Un ADR accepté est une décision de l'owner.

## Amendements

### ADR-086 (contrat éditorial de l'encyclopédie)

- **§3** : « couche **humain-validée** » se lit « couche validée par son décideur unique sur preuve,
  auto-review de sens comprise (ADR-119) ».
- **§5** : « TIER A auto / TIER B humain » se lit « TIER A promu / TIER B bloqué par ses motifs ».
- **§7** : « canon humain-validé » se lit « canon validé sur preuve ».

### ADR-092 (porte de contenu rang 1)

- **Ce qui reste HUMAIN (non délégable)**, point 1 : le « spot-check humain borné » est une
  contribution facultative (D1). Il n'est pas une condition de promotion.
- **Même section**, point 2 : l'invariant « une fiche sécurité ne s'auto-promeut pas » se lit selon
  [[ADR-114-wiki-safety-auto-gate|ADR-114]] et ADR-119 D3 : une fiche sécurité n'est promue que par
  la porte de sécurité, auto-review de sens PASS. « tout doute = TIER B humain » se lit « tout
  doute = TIER B, bloqué par ses motifs ».
- **Garde-fous** : « → TIER B humain » se lit « → TIER B, bloqué par ses motifs ».
- **Angles morts** : « lu comme plancher (cap B + `RANK_SPOTCHECK_MISSING` si absent) » est retiré.
  L'axe profondeur-vs-SERP reste non mesuré par le scorer.
- **Plan**, point 4 (`rank_spotcheck`, « posé par humain, non requis ») : maintenu.

### ADR-094 (porte composite de qualité de page)

- **Risque résiduel**, point 2 : « spot-check humain borné (`rank_spotcheck`) » se lit « contribution
  humaine facultative (`rank_spotcheck`, ADR-125 D1) ; l'axe reste non mesuré ».

### ADR-107 (listes structurées et FAQ des exports)

- **D5** : « validation owner » se lit « fusion de la PR WIKI par l'owner (ADR-121 D4) ». Cette fusion
  n'est pas une relecture de la fiche (ADR-119 D1).

### ADR-083 (promotion tiered)

- **TIER A** : « (**proposé 0.80**, owner-tunable) » se lit « (0.85 depuis la PR WIKI #83 du
  2026-09-12 ; ADR-125 D2) ».
- **Invariant AVANT / APRÈS**, ligne « Bar auto » : « score≥0.80 » se lit « score≥0.85 ».
- **Conséquences**, Risques + mitigation : « seuil **0.80** » se lit « seuil **0.85** ».

### ADR-091 (recalibrage du score)

- **Contexte** : « seuil de promotion TIER A **0.84** (ADR-083) » se lit « seuil de promotion TIER A
  **0.80**, valeur proposée par ADR-083 ».
- **Décision §4**, première phrase : « **1.01 → 0.80** » se lit « **1.01 → 0.85** ». La seconde phrase
  reste celle d'ADR-119.

### ADR-031 (architecture en quatre couches)

- **Amendement 2026-04-28 (D23)** : abrogé en entier, phrase « Cette §D23 est l'autorité actuelle »
  comprise. Il reste dans le fichier comme historique.
- **Couche 1**, « Convention de chemin figée » : maintenue, seule en vigueur.

### ADR-066 (composition de contenu R2 v2)

- **Rollout — Sequence**, « Gate V1 → PR 2 (HARD) » : « mix sain (4-7 INDEX + 2-4 SUPPRESSED + 0-2
  REJECT) » se lit « mix sain : pas 10 × INDEX, aucun `SUPPRESSED` automatique (ADR-067) ». Les pages
  qu'ADR-066 destinait à `SUPPRESSED` sortent en `review_required` (ADR-067, ADR-068 §C).

### ADR-068 (doctrine R2 stricte)

- **§C**, ligne `REJECT`, colonne Publication : « page invalide → 404/410 » vaut pour les raisons 1
  à 3 de §D. Pour la raison 4, la page répond selon ADR-076 : HTTP 200, `robots: noindex, follow`,
  sans canonical.
- **§D**, raison 4 : maintenue comme raison de `REJECT` du pipeline. Seule la réponse HTTP change de
  référence.

### G1 de `rules-vault` et `GOVERNANCE-HUMAN`

- **G1**, tableau : une ligne `ops/GOVERNANCE-HUMAN.md` (RULE-H0 à RULE-H6) est ajoutée, rôle
  « DECIDE - normatif », aux mêmes conditions que les règles. La ligne `governance-vault/ops/*` exclut
  ce fichier. `rules-vault` passe de 3.3.0 à 3.4.0.
- **`GOVERNANCE-HUMAN`, §0** : « above ADRs, agents, tools, and CI » devient « above agents, tools,
  prompts, and CI ». La phrase « This file overrides any other document, prompt, agent behavior, or
  automation » est remplacée par le texte de D5.
- RULE-H0 à RULE-H6 : aucun mot changé.

## Ce que cet ADR ne fait pas

- Il ne change aucun code, aucun seuil servi, aucune URL, aucune balise, aucun statut d'indexation.
- Il ne rétablit ni ne supprime aucune porte de promotion.
- Il ne tranche pas les seuils par `risk_level` de `quality-gates.md` §4 (0.70, 0.85, 0.95) :
  `promotion_decision.py` et `promote.py` n'en lisent qu'un, 0.85. C'est un constat pour le dépôt WIKI.
- Il ne déplace pas `GOVERNANCE-HUMAN` hors de `ops/`.
- Il ne modifie ni ADR-067, ni ADR-076, ni ADR-112, ni ADR-117, ni ADR-119.

## Mise en œuvre

| Où | Changement | Quand |
|---|---|---|
| Vault | Cet ADR ; G1 de `rules-vault` (3.4.0) ; §0 de `GOVERNANCE-HUMAN` ; errata d'en-tête d'ADR-083, ADR-090 et ADR-095 ; index de MOC-Decisions | PR qui porte cet ADR, en brouillon jusqu'à la ratification |
| Vault | `status: accepted`, `decision_date`, `amended_by: ["ADR-125"]` sur les neuf ADR amendés | Commit de ratification (ADR-121 D7) |
| Dépôt WIKI | `CLAUDE.md` l.54 et `_meta/ingestion-contract.md` l.86 : chemins au singulier | PR WIKI, après ratification |
| Monorepo | `scripts/wiki/wiki-readiness-check.py` : le contrôle C4 lit `wiki/gammes/`, absent, et passe à vide ; C5 cite le même chemin | PR monorepo, après ratification |

Aucune étape ne touche PREPROD ni PROD.

## Options considérées

### Option A — Laisser les textes en l'état — rejetée

Chaque lecteur, humain ou agent, doit alors savoir quel ADR postérieur l'emporte. C'est l'origine des
écarts relevés : ADR-091 cite un seuil qu'ADR-083 n'a jamais fixé.

### Option B — Un ADR par écart — rejetée

Cinq ADR, cinq PR, cinq ratifications pour des décisions déjà prises. La charge dépasse l'enjeu.

### Option C — Corriger le corps des ADR amendés — rejetée

Un ADR accepté ne se réécrit pas. La forme « se lit » d'ADR-119 garde l'historique et rend l'amendement
vérifiable.

### Option D — Pour D5, déplacer RULE-H0 à H6 dans `ledger/rules/` — rejetée

Le fichier est cité sous son nom par les ADR-102, 121 et 123. Le déplacer change des liens sans rien
décider de plus que la ligne ajoutée à G1.

### Option E — Pour D2, revenir à 0.80 — rejetée

Ce serait changer un seuil servi. Cet ADR aligne les textes ; il ne règle pas la promotion.

### Option F — Un ADR d'amendements ciblés, forme « se lit » — retenue

## Conséquences

### Positives

- Les neuf ADR et G1 disent la même chose que les décisions qui les ont suivis.
- `GOVERNANCE-HUMAN` a un rang défini, celui que trois ADR lui donnaient déjà en pratique.
- Le contrôle du monorepo qui passe à vide devient corrigeable : la convention est une.

### Négatives

- Neuf ADR de plus portent un `amended_by`. Leur lecture demande d'ouvrir ADR-125.
- La phrase de primauté de `GOVERNANCE-HUMAN` est restreinte. Un lecteur qui s'appuyait sur « overrides
  any other document » face à un ADR doit désormais demander une décision à l'owner.

## Métriques

- `python3 _scripts/check-adr-supersedes.py` : 0 erreur après le commit de ratification.
- Dépôt WIKI et monorepo : 0 occurrence de `wiki/gammes/`, `wiki/vehicles/`, `wiki/constructeurs/`
  dans un fichier lu par un contrôle, une fois les deux PR de suite fusionnées.

## Retour arrière

Revert de la PR. Aucun code ni aucune donnée ne dépend de cet ADR. Chaque décision peut aussi être
retirée seule avant la ratification : D1 à D5 sont indépendantes.

## Revue planifiée

**Date** : 2027-02-10

**Critères de revue** : les deux PR de suite (WIKI, monorepo) sont fusionnées ; aucun nouvel ADR ne
cite un seuil, un chemin ou une validation humaine contraires à D1, D2 et D3.

## Références

- [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] D1 ; [[ADR-114-wiki-safety-auto-gate|ADR-114]] ;
  [[ADR-117-wiki-promoter-canon-revision|ADR-117]] ; [[ADR-067-r2-no-auto-suppression|ADR-067]] ;
  [[ADR-076-soft-404-r2-strategy|ADR-076]] ; [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] ;
  [[ADR-101-vault-decides-canon-authority|ADR-101]].
- [[rules-vault]] G1 ; [[GOVERNANCE-HUMAN]] ; [[rules-engineering-quality]] Q4.
- Dépôt WIKI, `main` au commit `d5c9453` : `_scripts/promotion_decision.py` l.623,
  `_meta/quality-gates.md` §4 et §7.
- Monorepo, `main` au commit `068a917` : `frontend/app/utils/pieces-vehicle.loader.server.ts`
  (branche `noProducts`), `scripts/wiki/wiki-readiness-check.py` (C4, C5).
- (Relations structurées : voir `amends` / `related_adr` dans le frontmatter.)

---

*Proposé le : 2026-11-10*
*Accepté le : au commit de ratification de l'owner (ADR-121 D7)*
