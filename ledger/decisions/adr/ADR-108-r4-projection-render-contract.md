---
id: ADR-108
title: "Contrat de rendu de la projection R4 : section WIKI `definition` sourcée, correspondance vers les sections référence servies — amende ADR-086 §2bis, étend ADR-059 et ADR-106"
status: accepted
date: "2026-10-05"
decision_date: "2026-10-05"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-086"]
extends: ["ADR-059", "ADR-106"]
related_adr: ["ADR-031", "ADR-046", "ADR-062", "ADR-083", "ADR-086", "ADR-088", "ADR-095", "ADR-099", "ADR-106", "ADR-107"]
related_rules: ["G1", "AI1", "T1"]
related_incidents: []
version: "1.0.0"
---

# ADR-108 : Contrat de rendu de la projection R4

- **Statut** : Accepted (2026-10-05). La fusion par l'owner vaut ratification.
- **Numéro** : dérivé le 2026-10-05 (`main` du vault ∪ PR ouvertes) : `main` porte ADR-105, ADR-112
  et ADR-113 ; aucune PR ouverte ne porte un numéro de 106 à 111. Signé après les ADR-106 à 107, que
  le script owner exige sur `main`. Le script owner re-vérifie le numéro avant le commit.
- **Amende** [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2bis sur un seul point :
  ajout de la section `R4_REFERENCE/definition`, **optionnelle hors scoring**. Les tiers, les barres
  BRONZE / ARGENT / OR et le décompte des 9 éditoriales restent inchangés.
- **Étend** [[ADR-059-seo-runtime-projection|ADR-059]] (rendu d'une page référence depuis la
  projection) et ADR-106 (même modèle de contrat, appliqué au rôle R4).
- **Ordre de signature** : après ADR-106 et ADR-107, dont il reprend D1, D3, D6 à D8 et les formats
  structurés.

## Périmètre

Rôle **`R4_REFERENCE`**, entités `gamme`, page `/reference-auto/:slug`. Les sections R3 et R6 de la
gamme restent hors périmètre.

## Contexte

Constats vérifiés le 2026-10-04 : monorepo `main` `f1c601170`, WIKI `origin/main` `042e566`, base
en lecture seule.
Re-vérifiés le 2026-10-05 : monorepo `main` `658c0a3ce` (aucun fichier cité modifié depuis
`f1c601170`), WIKI épinglé inchangé, base en lecture seule.

1. **Le servi R4 ne lit pas la projection.**
   - La page lit `__seo_reference` : 239 lignes, dont 238 rattachées à une gamme par `pg_id`, en
     relation 1:1.
   - Le texte vient de `/content-gen --r4` et de `R4ContentEnricherService`. Celui-ci lit
     `RAG_KNOWLEDGE_PATH/gammes/<alias>.md` (`r4-content-enricher.service.ts:211`) : c'est une
     source RAG de contenu, contraire à ADR-031/046. Cette lecture figure déjà dans la dette
     suivie par `seo-no-rag-as-content-source.yml` et `audit/baselines/rag-authority-read-baseline.json`.
   - Aucune colonne de provenance.
2. **Le WIKI émet trois sections R4 éditoriales ou dérivées.**
   - `variants` (tier M) et `standards_norms` (tier R), éditoriales sourcées.
   - `definition` : **hors de l'enum §2bis**. Le builder (`build_exports_seo.py`, vers la ligne 408)
     la dérive de `decision_brief.function_oneliner`, lui-même dérivé de `dimensions.function`,
     avec `truth_level: inferred` et `source_ids: ["db:pieces_gamme"]`.
3. **Défaut de provenance.** Ce bloc `definition` déclare une source DB alors que son texte vient
   de la recherche web, et il répète `R3_CONSEILS/function`. Il ne peut fonder aucun rendu.
4. **Sections DB.** `compatibility` (M) et `related_parts` (R) sont déterministes (DB) selon
   ADR-086 §2bis. Le builder émet la seconde sous le nom `related`.
5. **Le rôle se définit par la définition.** La matrice des rôles (v5) assigne à R4 « définition,
   composition, rôle, confusions, glossaire, FAQ encyclopédique ». Le WIKI ne porte aujourd'hui
   aucune définition sourcée.
6. **Volume.** 4 gammes exportées sur 232.

## Décision

### D1 — `R4_REFERENCE/definition` entre dans le canon gamme, optionnelle hors scoring

- La section s'ajoute à l'enum §2bis : éditoriale sourcée, ni M ni R, hors de toute barre. C'est
  le même statut que les 4 sections de procédure.
- Contenu : ce qu'**est** la pièce (nature, place dans le système), distinct de `function`, qui dit
  ce qu'elle **fait**. Cette distinction est un critère de la porte de promotion (ADR-083/088), pas
  un contrôle de la projection.
- Côté WIKI (contrat ADR-062 §8, MINOR) : `editorial.definition` s'ajoute à
  `entity-data/gamme.schema.json`, avec la forme `editorialBlock` existante.
- Le builder émet ce bloc sourcé, et **cesse** d'émettre le bloc `definition` dérivé (constat 3).
  Cette correction du builder est un suivi WIKI, sans réécriture en place des fiches validées
  (ADR-107 D5).

### D2 — Table R4 v1

| Section WIKI (`R4_REFERENCE/…`) | Section servie (`page-contract-r4`) | Titre fixe |
|---|---|---|
| `definition` (`truth_level: sourced` uniquement) | `definition` | Définition |
| `variants` | `variants` | Variantes |
| `standards_norms` | `key_specs` | Normes et standards |

- La table vit dans le module de projection existant, sur le modèle du mapper R3 (ADR-106 D1).
  Elle est versionnée et testée.
- `standards_norms` est rendu en prose ou en liste (ADR-107 D1). Le tableau Critère / Valeur / Note
  du chemin historique n'est **jamais** reconstitué depuis une prose (ADR-107 D3).
- Un bloc `definition` qui n'est pas `sourced` est classé `unmapped / not_sourced` : compté, jamais
  rendu.

### D3 — Ce qui n'est pas projeté sur R4

- `compatibility` et `related_parts` restent des sections DB, composées par leurs consommateurs
  (R1, R2) ; la page R4 ne les rend pas depuis le WIKI.
- `R3_CONSEILS/faq` n'est pas rendue sur R4. La même FAQ sur deux pages indexées serait du
  contenu dupliqué, et la FAQ est routée vers R3 par ADR-086.
- Les autres sections du chemin historique (`takeaways`, `role_mecanique`, `composition`,
  `does_not`, `rules`, `scope`, `faq`, synonymes, confusions) n'ont pas de section WIKI. Sur le
  chemin projeté, elles ne sont pas rendues. **Aucun repli** vers `__seo_reference` : une page est
  servie soit entièrement depuis la projection, soit entièrement depuis le chemin actuel.
- Ajouter `composition` ou `confusions` au canon passe par un amendement d'ADR-086, quand des
  sources existeront.

### D4 — Complétude : `variants` (tier M) et `definition` sourcée

- Une entité R4 est prête à servir si `variants` et `definition` (sourcée) sont présentes et
  valides.
- `variants` est la seule section éditoriale M du rôle. `definition` est exigée parce qu'une page
  référence sans définition n'est pas une page R4 (constat 5).
- Cette exigence ne s'applique qu'au rendu R4 : la barre du canon gamme reste inchangée. Une
  gamme sans définition reste servie par le chemin actuel, sans noindex ni suppression.
- `standards_norms` est rendu s'il existe, jamais exigé.

### D5 — Présentation et activation : celles d'ADR-106

- Rendu en prose sûre par section (ADR-106 D6).
- Titres fixes de D2, aucun repris du chemin historique ni d'une génération (ADR-106 D8).
- En-tête de page inchangé : title, meta, H1.
- Provenance non affichée.
- Activation entité par entité, par `SEO_PROJECTION_READ_V1` et le canary
  `R4_REFERENCE@gamme:<pg_alias>`, après une comparaison écrite projeté vs servi. Acte owner
  (ADR-106 D7).
- L'entité est résolue par `__seo_reference.pg_id`, jamais par égalité de slug. Aujourd'hui, les
  238 lignes rattachées ont un slug égal au `pg_alias`, mais cette égalité n'est garantie par
  aucune contrainte. La 239e ligne n'a pas de `pg_id` : sans rattachement, pas de projection.
- L'identité de paire d'ADR-099 D5 s'applique : activer R3 n'active jamais R4, et inversement.

## Options considérées

- **Rendre le bloc `definition` dérivé actuel** : rejeté. Sa provenance déclarée est fausse
  (constat 3), et son texte double `function`.
- **Mettre `definition` en tier M ou R** : rejeté. Cela changerait les barres BRONZE / ARGENT / OR
  des 232 gammes, ce qui dépasse le besoin d'une page de rôle.
- **Compléter les sections manquantes depuis `__seo_reference`** : rejeté. Cela laisse servi un
  texte d'origine RAG à côté du canon, sur la même page (D3).
- **Rendre la FAQ R3 sur R4** : rejeté (D3).

## Ce que cet ADR ne fait pas

- Il ne modifie ni le WIKI, ni le builder, ni les fiches validées : il fixe le contrat que leurs
  évolutions suivront.
- Il n'active aucune lecture servie et ne change aucune URL, meta, H1 ou robots.
- Il ne décide pas du retrait de la lecture RAG de `R4ContentEnricherService`. Ce retrait relève
  déjà de la doctrine ADR-031/046 et de la procédure par tranche de `seo-no-rag-as-content-source`,
  qui décrémente la baseline dans la même PR.

## Conséquences

### Positives

- Une page référence peut être servie depuis le canon, avec une définition sourcée et distincte de
  la fonction.
- Le défaut de provenance du builder est nommé et corrigé à la source.

### Négatives

- Une page R4 projetée compte d'abord moins de sections que la page actuelle (D3). D'où
  l'activation entité par entité.
- Aucune entité n'est prête tant que le WIKI ne porte pas de définition sourcée.

## Rollback

- Avant activation : revert de la PR d'implémentation, sans effet servi.
- Après activation : retrait de l'entité du canary, ou coupure de `SEO_PROJECTION_READ_V1`. Le
  chemin actuel est servi aussitôt.

## Anti-patterns interdits

- Rendre une définition `inferred`, ou dont la provenance déclarée ne correspond pas au texte.
- Combler une section absente par `__seo_reference`, `rag://` ou une génération.
- Reconstituer un tableau de spécifications depuis une prose.
- Résoudre l'entité par similarité de slug.

## Références

- [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2, §2bis — bloc valide, taxonomie,
  tiers.
- [[ADR-059-seo-runtime-projection|ADR-059]] — projection SEO.
- ADR-106 — contrat de rendu R3 (modèle). ADR-107 — listes et FAQ structurées.
- [[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport|ADR-099]] D5 — lecture
  servie et canary par paire.
- [[ADR-083-tiered-wiki-promotion|ADR-083]] / [[ADR-088-promotion-gate-substance-scoring|ADR-088]]
  — porte de promotion.
- [[ADR-031-four-layer-content-architecture|ADR-031]] /
  [[ADR-046-r-stack-single-generator-and-layers|ADR-046]] — le RAG n'est pas une source de contenu.
- [[ADR-062-repository-contract-system-meta-model|ADR-062]] §8 — évolution SemVer du contrat WIKI.
