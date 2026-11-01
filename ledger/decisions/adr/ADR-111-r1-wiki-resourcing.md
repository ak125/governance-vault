---
id: ADR-111
title: "Réalimentation de la page gamme (R1) depuis le WIKI : une autorité par champ, FAQ de sélection sourcée, slots R1 jamais réécrits — amende ADR-090 §C2/§C3 et ADR-086 §2bis, étend ADR-107"
status: accepted
date: "2026-10-05"
decision_date: "2026-10-05"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-090", "ADR-086"]
extends: ["ADR-107", "ADR-059"]
related_adr: ["ADR-031", "ADR-046", "ADR-059", "ADR-062", "ADR-083", "ADR-086", "ADR-088", "ADR-090", "ADR-099", "ADR-103", "ADR-106", "ADR-107", "ADR-108"]
related_rules: ["G1", "AI1", "T1"]
related_incidents: []
version: "1.0.0"
---

# ADR-111 : Réalimentation de la page gamme (R1) depuis le WIKI

- **Statut** : Accepted (2026-10-05). La fusion par l'owner vaut ratification.
- **Numéro** : dérivé le 2026-10-05 (`main` du vault ∪ PR ouvertes) : `main` porte ADR-105, ADR-112
  et ADR-113 ; aucune PR ouverte ne porte un numéro de 106 à 111. Signé après les ADR-106 à 110, que
  le script owner exige sur `main`. Le script owner re-vérifie le numéro avant le commit.
- **Amende** [[ADR-090-seo-projection-forward-writer-canon|ADR-090]] :
  - §C3 : aucun writer n'écrit plus les slots R1 (D5) ;
  - §C2 : entrées et `source_hash` du cache des blocs R1 sans RAG (D6).
- **Amende** [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2bis sur un seul point :
  `R1_ROUTER` gagne une section éditoriale `faq`, optionnelle hors scoring (D3).
- **Étend** ADR-107 D2 : `qa` s'ouvre à la FAQ de sélection.
- **Ordre de signature** : après ADR-106, ADR-107 et ADR-108, qui amende aussi ADR-086 §2bis.

## Périmètre

Rôle **`R1_ROUTER`**, entités `gamme`, pages gamme `/pieces/<slug>` : corps éditorial de la page,
et cache des blocs de maillage R1. Hors périmètre : sélecteur, motorisations, listes de produits,
et tout l'en-tête de page (title, meta, H1).

## Contexte

Constats vérifiés le 2026-10-04 : monorepo `main` `f1c601170`, WIKI `origin/main` `042e566`, base
en lecture seule.
Re-vérifiés le 2026-10-05 : monorepo `main` `658c0a3ce` (aucun fichier cité modifié depuis
`f1c601170`), WIKI épinglé inchangé, base en lecture seule.

1. **Ce que sert la page gamme.**
   - La RPC `get_buying_guide_with_r1_slots` lit la ligne non brouillon de
     `__seo_gamme_purchase_guide`. Elle y joint `__seo_r1_gamme_slots` et, pour 24 champs R1, sert
     la valeur du slot si elle existe, sinon celle du guide (`COALESCE`).
   - Le backend applique ensuite une porte de qualité. Si la porte échoue, il sert un guide gabarit
     (`buildAutoBuyingGuideV1`).
   - Guides d'achat : 241 lignes, 221 publiées, dernière mise à jour le 2026-04-21.
     - 226 lignes déclarent `sgpg_source_type = rag`, avec une URI `rag://…`. Elles sont toutes
       marquées vérifiées par le pipeline lui-même (`pipeline:rag-enrich`), sans relecture humaine.
     - Les 15 autres ne déclarent aucune source.
   - Slots R1 : 169 lignes, dernière mise à jour le 2026-05-07. Elles ont été écrites par
     `R1EnricherService`, qui lisait le RAG et a été retiré depuis.
   - La garde `scripts/audit/rag-r1-write-closure.test.ts` (décision owner du 2026-07-25) interdit
     tout writer TypeScript sur cette table tant qu'aucun writer canonique sourcé WIKI n'est
     approuvé.
   - Le corps R1 servi est donc d'origine RAG, contrairement à ADR-031/046.
2. **Ce que contiennent les champs R1** (mesure sur les 169 slots et les 221 guides publiés).
   - **Arguments 1 à 3** : chaque argument a 13 titres distincts, répartis en deux gabarits (le
     second écrit avec et sans accents) et dix titres propres à une gamme.
     - Gabarit A, sur 95 à 96 slots selon l'argument : « Compatibilité garantie », « Qualité
       équivalente à l'origine », « Prix plus juste ». C'est une promesse marchande (« 100 %
       compatible, sans erreur possible », « Jusqu'à 40 % moins cher »). Elle enfreint les
       interdits du contrat R1 (`hard_rules` : `ban_absolute_claims`, `ban_price_push`).
     - Gabarit B, sur 57 à 59 slots selon l'argument : « Compatibilité vérifiée », « Priorité
       sécurité », « Décision rapide ». Le texte est identique, aux accents près, sur 56 à 57
       d'entre eux (« Le guide structure les contrôles avant commande »).
     - Dix arguments propres à une gamme : de la sélection (« Halogène vs Xénon vs LED », « Bloc
       complet ou cabochon ») ou du diagnostic (« Test au multimètre »). Cinq slots sont vides.
     - Le code appelle ce bloc « Pourquoi acheter chez nous ».
   - **Argument 4** : 55 titres distincts.
   - Les 221 gammes publiées servent des arguments.
   - **Sous-titre de hero** : 167 slots sur 169 suivent le gabarit « Trouvez votre … au meilleur
     prix ». 52 gammes publiées n'ont aucun sous-titre.
   - **FAQ** : 169 FAQ distinctes, 721 questions, 4,3 par gamme. Un décompte par mots-clés
     (catégories non exclusives) donne :
     - 146 questions d'échéance, 140 de montage ou de « soi-même », 34 de symptômes : c'est du
       contenu R3 ;
     - 82 de prix et 78 de sélection.
     - 163 gammes sur 169 ont au moins une question de type R3.
   - **Autres champs** : microcopy du sélecteur absente pour 213 gammes, table de vérification
     absente pour 52, `h1_override` présent pour 26.
3. **Le rôle R1** (`.spec/00-canon/role-matrix.md`, v5).
   - R1 « n'est pas » une page guide d'achat, how-to, définition ou diagnostic.
   - Sorties autorisées : hero, sélecteur, rappels de compatibilité, variantes, **FAQ de
     sélection**, table légère, renvois R3/R4/R5/R6.
   - Sorties interdites : procédure, symptômes, prix détaillés, glossaire profond.
   - Bascule : « besoin comment choisir → R6 ». Depuis ADR-103, R6 est consolidé dans R3.
   - Le corps servi aujourd'hui porte des symptômes, des échéances, des erreurs de montage et le
     récit d'achat R6 : il sort du rôle.
4. **Le WIKI.**
   - ADR-086 §2bis ne donne à `R1_ROUTER` que `vehicle_selector`, une section DB.
   - Les sections d'achat `R6_GUIDE_ACHAT/selection_criteria` et `quality_tiers` existent. ADR-103
     D4 laisse leur projection sur R3 à une décision distincte, et ADR-106 la laisse hors du rendu
     R3.
   - La FAQ gamme est routée vers R3 par le builder. Aucune section ne porte une FAQ de sélection.
   - Le contrat de génération R1 (`page-contract-r1.schema.ts`) nomme déjà les sous-intentions de la
     page : vérifications de compatibilité, variantes de montage, identification de la référence,
     échange standard, consigne, livraison et retours.
5. **ADR-090 suppose l'ancienne recette.**
   - §C3 : un writer écrit les slots « depuis `intro_role` / `buy_args` », qui sont des champs du
     guide d'origine RAG, et persiste `r1s_gatekeeper_score`.
   - §C2 : `source_hash = md5(rag_data + db_state)`. L'entrée `confusion_with` n'est émise par aucun
     export WIKI. `related_parts` est émis sous `R4_REFERENCE/related`, dérivé de la DB.
   - Le cache des blocs R1 compte 238 lignes, construites le 2026-06-11, sans producteur (ADR-103,
     constat 7).

## Décision

### D1 — Une seule autorité par champ R1

| Champs servis aujourd'hui | Nature | Autorité | Sur une gamme basculée |
|---|---|---|---|
| FAQ de sélection | savoir pièce, rôle R1 | WIKI | rendue depuis la projection (D2) |
| critères de choix, niveaux de qualité, « comment choisir » | savoir pièce, rôle R6 consolidé dans R3 | WIKI ; page d'accueil R3 (décision distincte, ADR-103 D4) | non rendus sur R1 ; renvoi par les blocs de maillage (D6) |
| rôle de la pièce, risque, échéances, symptômes, erreurs, arbre de décision, cas d'usage, FAQ R3 | savoir pièce, rôles R3 et R4 | WIKI, servi sur R3 et R4 | non rendus sur R1 ; renvoi par les blocs de maillage |
| table de vérification (`safe_table_rows`) | sortie R1 autorisée, sans section WIKI | — | non rendue en v1 ; amendement ADR-086 quand une source existe |
| arguments 1 à 4, sous-titre de hero | promesse marchande ou gabarit (constat 2) | marchand (owner), hors WIKI | non rendus tant que leur source n'existe pas (D4) |
| microcopy du sélecteur, intro compatibilités, ligne équipementiers, cross-sell famille, pépites, plan visuel, bloc micro-SEO, `intent_lock` | texte d'interface ou de génération | hors WIKI | non lus (D4) |
| `h1_override` | en-tête de page | inchangée | source actuelle conservée |

- Un champ n'a jamais deux sources sur une même page : pas de `COALESCE` entre projection, slots
  et guide sur une gamme basculée.
- Les dix arguments propres à une gamme (constat 2) ne sont pas repris tels quels.
  - Le savoir de sélection qu'ils portent appartient au WIKI : FAQ de sélection (D3) ou variantes
    (`R4_REFERENCE/variants`).
  - Le diagnostic appartient à R3 ou R5.
  - Le bloc « arguments » ne porte que des promesses marchandes.

### D2 — Table R1 v1

| Section WIKI | Rendu sur R1 | Titre fixe |
|---|---|---|
| `R1_ROUTER/faq` (D3) | paires `qa`, au plus 6, dans l'ordre du WIKI | Questions fréquentes |

- Au-delà de 6 paires (borne d'ADR-090 §C3, conservée), les suivantes sont comptées, pas rendues.
  Aucun texte n'est tronqué.
- `FAQPage` ne s'émet que depuis `qa`, et son activation est un acte owner (ADR-107 D4).
- Un bloc `R1_ROUTER/faq` sans `qa` n'est pas rendu sur R1 : la FAQ de sélection n'existe que
  sous forme de paires.
- La table vit dans le module de projection existant, sur le modèle du mapper R3.

### D3 — `R1_ROUTER/faq` entre dans le canon gamme

- `R1_ROUTER` gagne une section éditoriale sourcée, optionnelle, hors scoring. C'est le même statut
  que `R4_REFERENCE/definition` (ADR-108 D1). `vehicle_selector` reste une section DB.
- Contenu : questions qui aident à trouver la bonne pièce pour son véhicule, dans les
  sous-intentions du contrat R1 (compatibilité, variantes de montage, identification de la
  référence, échange standard, consigne). Ni procédure, ni symptôme, ni définition, ni prix.
- Ce périmètre, et les interdits du contrat R1 (`hard_rules` : marqueurs de procédure,
  affirmations absolues, incitation par le prix), sont des critères de la porte de promotion
  (ADR-083/088), pas des contrôles de la projection.
- Côté WIKI (contrat ADR-062 §8, MINOR) : `editorial.selection_faq` s'ajoute à
  `entity-data/gamme.schema.json`, avec la forme `editorialBlock` et le champ `qa`. Le builder
  l'émet sous `R1_ROUTER/faq` ; `R1_ROUTER` rejoint les rôles autorisés de l'entité `gamme`.
- ADR-107 D2 s'applique en entier : une seule vérité, `content_md` dérivé de `qa`.
- Aucune réécriture en place des fiches validées (ADR-107 D5).

### D4 — Promesses commerciales et texte d'interface : hors WIKI

- Le WIKI porte le savoir sourcé sur les pièces (ADR-031). Une promesse de compatibilité ou de prix
  engage le marchand : elle ne se source pas dans le WIKI et ne se rédige pas gamme par gamme.
- Sa source future est un jeu unique de promesses, déclaré et validé par l'owner. Ce jeu respecte
  les interdits du contrat R1, ce que le gabarit A actuel ne fait pas (constat 2). Il n'existe pas ;
  le créer est une **décision distincte**.
- Jusque-là, une gamme basculée ne rend ni les arguments ni le sous-titre de hero. Les arguments
  étant servis sur les 221 gammes, leur absence est visible : la comparaison de D7 la montre.
  L'owner peut créer la source marchande avant la première activation.
- Le texte d'interface et de génération n'est pas lu sur une gamme basculée. La page traite déjà
  l'absence de ces champs (constat 2).

### D5 — §C3 amendé : aucun writer n'écrit les slots R1

- La page R1 lit sa section dans la projection active, écrite par le writer de projection comme
  les autres blocs de la gamme.
- Aucune copie n'est écrite dans `__seo_r1_gamme_slots` : ce serait une seconde source du même
  contenu. La garde `rag-r1-write-closure` reste telle quelle ; aucun writer de slots n'est prévu.
- `r1s_gatekeeper_score` ne s'applique plus : les portes de §C4 (CanonGate, QualityGate) jugent
  chaque bloc à son écriture.
- `__seo_r1_gamme_slots` et `__seo_gamme_purchase_guide` restent intacts : ni mise à jour, ni
  suppression. Leur sort, quand plus aucune gamme ne les lira, est une décision owner distincte.

### D6 — §C2 amendé : le cache des blocs R1 sans RAG

| Kind | Entrée |
|---|---|
| `compatible-parts` | pièces liées depuis la DB (`db_owned`) |
| `avoid-confusion` | non produit tant qu'aucune section de confusions sourcée n'existe (amendement ADR-086, cf. ADR-108 D3) |
| `buying-guide` | règle de lien d'ADR-103 D5 |

- `source_hash = md5(db_state + empreintes des blocs projetés utilisés)`. `rag_data` disparaît.
- Le writer d'ADR-059 tourne en PROD depuis le 2026-10-05 (feeder planifié), mais il n'écrit que
  les faits, les blocs de contenu, leurs versions et les runs : le rôle de producteur du cache prévu
  par ADR-090 §C2 n'est pas implémenté. Quand il le sera, il n'écrira le cache que pour les gammes
  du canary R1. Les 238 lignes actuelles restent servies, sans
  suppression.
- Le reste de §C2 est inchangé : bornes, cible `pg_level='1'`, existence-gating, frontend qui
  n'arbitre rien.

### D7 — Complétude et activation

- Une gamme est prête si `R1_ROUTER/faq` porte au moins une paire `qa` valide.
- Activation gamme par gamme, par `SEO_PROJECTION_READ_V1` et le canary
  `R1_ROUTER@gamme:<pg_alias>`. L'entité est résolue par `pg_id`, jamais par similarité de slug.
- Sur une gamme basculée : aucun repli vers le guide, les slots ou le gabarit
  `buildAutoBuyingGuideV1`.
- Inchangés : l'en-tête de page (title, meta, H1, dont `h1_override` lu à sa source actuelle), les
  parties composées depuis la DB, et les blocs de maillage.
- L'identité de paire d'ADR-099 D5 s'applique : basculer R1 ne bascule ni R3 ni R4.
- Avant l'ajout au canary : comparaison écrite projeté vs servi, qui liste chaque section retirée
  selon D1. Acte owner.
- Après une activation : suivi de la gamme dans la collecte Search Console existante avant
  d'étendre le canary. Le corps R1 basculé est bien plus court que le corps actuel.
- `rag://` reste dans `TRUSTED_SOURCE_PREFIXES` tant qu'une gamme sert le guide d'origine RAG. Son
  retrait est une décision owner, quand plus aucune gamme ne le sert.

## Options considérées

- **Écrire les slots R1 depuis le WIKI** (lettre d'ADR-090 §C3) : rejeté. Ce serait une seconde
  copie du contenu projeté, et les slots portent surtout des promesses et du gabarit (constat 2).
- **Servir les critères de choix R6 sur R1** : rejeté. R1 n'est pas une page guide d'achat, et la
  matrice envoie « comment choisir » vers R6, consolidé dans R3. Le jour où R3 rendra ces sections,
  le même contenu serait servi sur deux pages.
- **Composer les arguments depuis les critères de choix** : rejeté. Ce bloc dit pourquoi acheter
  ici, pas comment choisir : le remplir de critères changerait son sens.
- **Rendre la FAQ R3 sur R1** : rejeté. Contenu dupliqué entre deux pages indexées, et contenu
  hors rôle R1 (symptômes, procédure).
- **Garder les champs du guide en complément de la projection** : rejeté. Cela laisse servi un
  texte d'origine RAG à côté du canon, sur la même page.

## Ce que cet ADR ne fait pas

- Il ne crée aucune fiche, ne modifie ni le WIKI, ni le builder, ni la RPC, et n'active aucune
  lecture servie.
- Il ne décide pas où les sections R6 sont servies sur R3 (ADR-103 D4 reste ouvert).
- Il ne crée pas la source des promesses commerciales (D4).
- Il ne touche ni aux deux tables actuelles, ni au cache des blocs, ni aux URL, meta, H1 ou robots.

## Conséquences

### Positives

- Le corps éditorial R1 peut sortir du RAG gamme par gamme, avec une seule source par champ.
- La page R1 revient à son rôle de routeur : plus de contenu R3 ou R6 servi en double.

### Négatives

- Une page R1 basculée est bien plus courte qu'aujourd'hui : DB, FAQ de sélection et renvois. Le
  risque de classement est réel ; d'où l'activation gamme par gamme et le suivi de D7.
- Une gamme basculée perd les arguments et le sous-titre tant que la source marchande n'existe pas.
- Aucune gamme n'est prête avant la production de FAQ de sélection dans le WIKI.

## Rollback

- Avant activation : revert, sans effet servi.
- Après activation : retrait de la gamme du canary, ou coupure de `SEO_PROJECTION_READ_V1`. La RPC
  actuelle est servie aussitôt.

## Anti-patterns interdits

- Écrire un writer vers `__seo_r1_gamme_slots`.
- Servir sur une même page un champ issu de deux sources, par `COALESCE` ou par repli.
- Rédiger une promesse commerciale dans le WIKI, ou la générer gamme par gamme.
- Servir sur R1 une section d'un autre rôle (R3, R4, R6).
- Reconstituer des cartes, des étapes ou des paires depuis une prose.
- Résoudre une gamme par similarité de slug.

## Références

- [[ADR-090-seo-projection-forward-writer-canon|ADR-090]] §C2, §C3, §C4.
- [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2bis.
- [[ADR-103-r6-guide-achat-consolidation-into-r3|ADR-103]] D1, D4, D5.
- ADR-106 — contrat de rendu R3 (modèle). ADR-107 — FAQ structurée. ADR-108 — section `definition`.
- [[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport|ADR-099]] D5 — canary par
  paire.
- [[ADR-031-four-layer-content-architecture|ADR-031]] /
  [[ADR-046-r-stack-single-generator-and-layers|ADR-046]] — le RAG n'est pas une source de contenu.
- [[ADR-062-repository-contract-system-meta-model|ADR-062]] §8 — évolution SemVer du contrat WIKI.
