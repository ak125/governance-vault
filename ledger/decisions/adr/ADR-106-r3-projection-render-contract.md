---
id: ADR-106
title: "Contrat de rendu de la projection R3 : correspondance sections WIKI → sections servies, complétude dérivée des tiers ADR-086 — étend ADR-086 §2bis et ADR-059"
status: accepted
date: "2026-10-05"
decision_date: "2026-10-05"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: ["ADR-086", "ADR-059"]
related_adr: ["ADR-031", "ADR-046", "ADR-062", "ADR-086", "ADR-090", "ADR-099", "ADR-103"]
related_rules: ["G1", "AI1", "T1"]
related_incidents: []
version: "1.0.0"
---

# ADR-106 : Contrat de rendu de la projection R3

- **Statut** : Accepted (2026-10-05). La fusion par l'owner vaut ratification.
- **Numéro** : dérivé le 2026-10-05 (`main` du vault ∪ PR ouvertes) : `main` porte ADR-105, ADR-112
  et ADR-113 ; aucune PR ouverte ne porte un numéro de 106 à 111. Le script owner re-vérifie le
  numéro avant le commit.
- **Étend** [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2bis, qui confie la
  correspondance vers la taxonomie servie à « une responsabilité de projection existante » sans la
  définir. Étend [[ADR-059-seo-runtime-projection|ADR-059]] pour le rendu d'une page conseils
  depuis la projection.
- **N'amende pas** ADR-086 : la taxonomie WIKI, les tiers, les exclusions déterministes et le
  verrou `truth_level` restent tels quels.

## Périmètre

Rôle **`R3_CONSEILS`** uniquement, entités `gamme`. Les rôles R4, R7 et R8 auront chacun leur
contrat de rendu, sur le même modèle. Les sections `R6_GUIDE_ACHAT/*` restent hors périmètre,
comme le prévoit [[ADR-103-r6-guide-achat-consolidation-into-r3|ADR-103]] D4.

## Contexte

Constats vérifiés le 2026-10-03 : monorepo `main`, WIKI au commit épinglé par le sous-module
(`042e566`), vault `main`.
Re-vérifiés le 2026-10-05 : monorepo `main` `658c0a3ce` (aucun fichier cité modifié depuis
`f1c601170`), WIKI épinglé inchangé.

1. **Deux vocabulaires sans pont.**
   - Le WIKI exporte des sections **sémantiques** (`function`, `failure_symptoms`, `faq`…), comme le
     veut ADR-086 §2bis.
   - Le mapper de projection R3 n'accepte que la taxonomie **servie** `S1…S8`, c'est-à-dire l'enum
     `section_terms` de `page-contract-r3.json`. Toute autre section est classée
     `unmapped / unknown_section`.
   - Conséquence : aucune entité ne peut atteindre l'état prêt-à-servir, quel que soit le contenu
     du WIKI.
2. **La complétude est déléguée sans source.**
   - Le mapper reçoit `requiredSections` de l'appelant. Son commentaire renvoie à une décision du
     vault qui n'a pas été prise.
   - Le seul candidat existant est le pack conseil `standard` : `S1, S2, S3, S4_DEPOSE, S5, S6, S8`.
     Ce pack appartient au chemin d'écriture historique (`sg_content`).
3. **Le pack `standard` est insatisfaisable depuis le WIKI.**
   - `S3` est déterministe (DB) selon ADR-086 §2bis, « Exclusions déterministes ».
   - `S5` (format Erreur → Risque → Correctif) n'a aucune section ADR-086 correspondante.
   - `S4_DEPOSE` et `S6` correspondent à des sections **optionnelles hors scoring** : les exiger
     créerait la pression de remplissage qu'ADR-086 interdit.
4. **Les exports contiennent des sections hors enum.**
   - Au commit WIKI épinglé, `filtre-a-huile` porte, en plus des sections §2bis :
     - `R3_CONSEILS/maintenance` (`truth_level: editorial`) ;
     - `R4_REFERENCE/related` et `R4_REFERENCE/definition` ;
     - `R6_GUIDE_ACHAT/selection`.
   - Aucune n'est dans l'enum §2bis.
5. **Le contenu est de la prose courte.**
   - Les 14 blocs des 4 exports font 93 à 513 caractères (123 à 513 pour `filtre-a-huile`).
   - Les listes et la FAQ sont aplaties en un seul paragraphe.
   - Les formats servis historiques (tableau pour S2, étapes pour S4, questions-réponses pour S8)
     ne sont pas reconstructibles sans changer la représentation côté WIKI.
6. **Volume.** 4 gammes exportées sur 232 ; 0 export `constructeur` et 0 export `vehicle`.
7. **Les sections optionnelles ne sont pas encore exportables.** Le schéma WIKI
   `entity-data/gamme.schema.json` (objet `editorial`) ne déclare que les 9 sections tier M et
   tier R. `removal_procedure`, `installation_procedure`, `post_install_checks` et
   `safety_warnings`, déclarées par ADR-086 §2bis, n'y figurent pas. Le builder ne peut donc pas les
   émettre aujourd'hui. Les ajouter relève du contrat WIKI (ADR-062), pas de cet ADR.

## Décision

### D1 — La correspondance vit côté projection, dans une table unique et versionnée

- La correspondance `section WIKI → section servie` est une **table déclarée** dans le code de
  projection du monorepo. Elle étend le mapper R3 existant, sans nouveau module ni service
  parallèle.
- Elle est versionnée (`render_contract_version`) et couverte par des tests.
- Le WIKI garde ses noms sémantiques. `build_exports_seo` reste inchangé (ADR-086 §5).

### D2 — Table R3 v1

| Section WIKI (`R3_CONSEILS/…`) | Section servie | Fondement |
|---|---|---|
| `function` | `S1` | entrée historique de S1 : `domain.role` (rôle de la pièce) |
| `maintenance_interval` | `S2` (1er composant) | entrées historiques de S2 : `maintenance.interval` + `maintenance.wear_signs` |
| `failure_symptoms` | `S2` (2e composant) | idem : signes d'usure |
| `removal_procedure` | `S4_DEPOSE` | format servi « étapes » (dépose) |
| `installation_procedure` | `S4_REPOSE` | format servi « étapes » (repose) |
| `post_install_checks` | `S6` | format servi « checklist de vérification finale » |
| `faq` | `S8` | format servi « FAQ » |
| `safety_warnings` | encadré rattaché à la première procédure présente, dans l'ordre `S4_DEPOSE` puis `S4_REPOSE` ; **aucune section propre** | voir D4 |
| `replacement_guidance` | **non projetée en v1** | aucune section servie équivalente (voir Options) |

Les « entrées historiques » et « formats servis » sont ceux que le monorepo déclare aujourd'hui
pour chaque section R3 (`RAG_SECTION_REQUIREMENTS`, `SECTION_QUALITY_CRITERIA`). Ils servent de
preuve de l'intention de chaque section, pas de source de contenu.

Quand `S2` reçoit ses deux composants, l'ordre est fixe : intervalle, puis signes. Si un seul est
présent, il est rendu seul.

Une section WIKI revendiquée par plusieurs blocs d'une même enveloppe est **invalide** : la section
servie qui l'accueille n'est pas rendue du tout, et l'entité n'est pas prête. Aucun « dernier bloc
gagne ».

### D3 — Ce qui n'est jamais rendu depuis le WIKI

- `S2_DIAG`, `S3`, `S7` et `S_GARAGE` sont composés depuis la DB par le consommateur (ADR-086
  §2bis). Ils n'ont pas de section WIKI et ne sont jamais exigés du WIKI.
- Tant qu'aucun composeur DB n'existe pour l'une de ces sections, le chemin projeté ne la rend pas.
- Il n'y a **aucun repli** vers un contenu `sg_content` ou `rag://` pour combler l'absence.
- Toute section absente de la table D2 (constat 4) est classée `unmapped / unknown_section` : elle
  est comptée et journalisée, jamais rendue. Corriger l'export relève du WIKI (contrat ADR-062),
  pas de la projection.
- `replacement_guidance` est classée `unmapped / not_projected` : comptée, jamais rendue, jamais
  validée.

### D4 — `safety_warnings` n'a pas de section propre et ne compte jamais pour la complétude

- `S5` est au format encadré et figure dans le pack `standard`. Y placer `safety_warnings`
  donnerait une cible de couverture à une section dont ADR-086 dit « aucune cible, absence =
  valide ».
- `safety_warnings` est donc rendu comme encadré **à l'intérieur** de la première procédure
  présente, dans l'ordre `S4_DEPOSE` puis `S4_REPOSE`.
- Sans procédure hôte, l'encadré n'est pas rendu. Il est compté (`unmapped /
  callout_without_host`), sans rendre l'entité incomplète.
- Il n'entre dans aucun calcul de complétude.

### D5 — La complétude d'une page conseils projetée dérive des tiers ADR-086, pas du pack conseil

- Une entité `R3_CONSEILS` est **prête à servir** si les sections servies issues des sections
  **obligatoires** (tier M) d'ADR-086 sont présentes et valides :
  - `S1`, alimentée par `function` ;
  - `S2`, alimentée par `maintenance_interval` **et** `failure_symptoms`.
- Les autres sections de D2 sont rendues si elles existent, et ne sont jamais exigées.
- Les packs conseil (`standard`, `pro`, `eeat`) restent la règle du chemin d'écriture historique.
  Ils ne s'appliquent pas au chemin projeté. **Une seule source pour les requis** : les tiers
  d'ADR-086, traduits par la table D2.

### D6 — Le rendu v1 est de la prose sûre, par section

- Le rendu affiche `content_md` en prose, section par section, avec un sous-ensemble Markdown sûr :
  pas de HTML brut ni de script.
- Les formats structurés (tableau, étapes numérotées, questions-réponses) demandent une
  représentation structurée dans l'export. Cette évolution du contrat WIKI (ADR-062) fera l'objet
  d'une décision distincte.
- Le v1 n'invente aucune structure à partir de la prose.

### D7 — Activation : entité par entité, toujours décidée par l'owner

- Ce contrat ne sert rien par lui-même. Une page passe au chemin projeté uniquement par
  `SEO_PROJECTION_READ_V1` **et** le canary `R3_CONSEILS@gamme:<slug>`, deux décisions de l'owner.
- Avant d'ajouter une entité au canary, il faut une comparaison écrite **projeté vs servi actuel**
  pour cette entité : sections présentes, longueur, sections perdues, et changements visibles des
  moteurs (titres de section H2, ancres, données structurées FAQ, liens internes de la section
  META).
- Une page projetée peut compter moins de sections que la page actuelle (D3, D5). C'est un
  arbitrage SEO sur une page indexée, réservé à l'owner.

### D8 — Présentation du corps projeté

- **Titres fixes par section servie**, un seul texte par section, tenu dans le code à côté de la
  table D2 :

  | Section servie | Titre |
  |---|---|
  | `S1` | Rôle de la pièce |
  | `S2` | Entretien et signes d'usure |
  | `S4_DEPOSE` | Démontage |
  | `S4_REPOSE` | Remontage |
  | `S6` | Vérifications après montage |
  | `S8` | Questions fréquentes |

  L'ancre est dérivée du titre. Aucun titre n'est repris de `sg_content`, du plan de titres
  historique ni d'une génération. Un titre propre à une entité demande un champ dans l'export WIKI,
  donc une évolution du contrat (ADR-062).
- **Pas de section META sur le chemin projeté.** Les listes de liens historiques viennent de
  `sg_content`, que D3 exclut. Le maillage du contenu projeté passe par les liens Markdown écrits
  dans le WIKI, soumis à la règle de liens guides d'ADR-103 D5.
- **Provenance non affichée.** Les `source_ids` sont des références internes (RAW, DB), pas des
  citations publiques. Ils restent dans la projection pour l'audit.
- L'en-tête de page (title, meta description, H1, extrait, mots-clés) reste celui du chemin
  actuel. Seul le corps change.

## Options considérées

- **Renommer les sections du WIKI en `S1…S8`** : rejeté. Contredit ADR-086 §2bis (noms
  sémantiques) et couple le WIKI à une taxonomie de rendu.
- **Utiliser le pack `standard` comme requis** : rejeté. Il est insatisfaisable (constat 3) et
  forcerait le remplissage de sections optionnelles ou déterministes.
- **`safety_warnings` → `S5`** : rejeté (D4).
- **`replacement_guidance` → `S5` ou `S4_DEPOSE`** : non retenu en v1. S5 est au format
  Erreur → Risque → Correctif et S4 est une procédure en étapes : dans les deux cas, il faudrait
  réécrire le bloc. À reprendre si le WIKI ajoute une section « erreurs à éviter » (amendement
  ADR-086).
- **Projeter `R6_GUIDE_ACHAT/selection_criteria` dans `S3`** : non retenu. ADR-086 fait de S3 une
  section déterministe DB, et ADR-103 D4 renvoie cette question à une décision distincte.

## Ce que cet ADR ne fait pas

- Il ne modifie ni le WIKI, ni le builder d'exports, ni les tiers ADR-086.
- Il n'active aucune lecture servie et ne change aucune URL, meta, H1 ou robots.
- Il ne crée aucune section servie nouvelle : l'enum `page-contract-r3.json` est inchangé.
- Il ne décide pas des rôles R4, R7 et R8.

## Conséquences

### Positives

- Une entité R3 peut devenir prête à servir sans contenu inventé, et une seule table fait foi.
- Les sections absentes ou hors enum sont visibles (compteurs `unmapped` / `missing`), pas
  masquées.

### Négatives

- La page projetée sera d'abord moins riche que la page actuelle : pas de S3, S5 ni S7 tant que les
  composeurs DB et la structure WIKI n'existent pas. D'où l'activation entité par entité (D7).
- `replacement_guidance` est sourcé mais non affiché en v1.
- Les lignes `S4_DEPOSE`, `S4_REPOSE`, `S6` et l'encadré de sécurité restent sans contenu tant que le
  contrat WIKI n'expose pas les sections optionnelles (constat 7).

## Rollback

- Avant activation : revert de la PR d'implémentation, sans effet servi.
- Après activation d'une entité : la retirer du canary, ou couper `SEO_PROJECTION_READ_V1`. Le
  chemin actuel est servi immédiatement.

## Anti-patterns interdits

- Combler une section absente par du contenu `rag://`, `sg_content` ou généré.
- Exiger une section optionnelle ou déterministe du WIKI pour atteindre l'état prêt-à-servir.
- Deviner une correspondance hors de la table D2, à l'exécution ou par similarité de nom.
- Dupliquer la table dans un second endroit (front, script, autre service).
- Déduire une liste, des étapes ou des questions d'une prose (D6).
- Reprendre un titre de section du chemin historique ou d'une génération (D8).

## Références

- [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2bis, §5 — taxonomie, tiers,
  exclusions, verrou `truth_level`.
- [[ADR-059-seo-runtime-projection|ADR-059]] — projection SEO.
- [[ADR-090-seo-projection-forward-writer-canon|ADR-090]] — writer de projection.
- [[ADR-103-r6-guide-achat-consolidation-into-r3|ADR-103]] D4 — sections R6 hors projection R3 ; D5 — règle de liens guides, appliquée au contenu projeté (D8).
- [[ADR-031-four-layer-content-architecture|ADR-031]] / [[ADR-046-r-stack-single-generator-and-layers|ADR-046]] — le RAG
  n'est pas une source de contenu.
- [[ADR-062-repository-contract-system-meta-model|ADR-062]] §8 — évolution SemVer du contrat d’export WIKI.
