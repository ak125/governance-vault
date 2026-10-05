---
id: ADR-109
title: "Profil éditorial constructeur et contrat de rendu de la projection R7 — étend ADR-086 §2/§6, ADR-056 et ADR-107"
status: accepted
date: "2026-10-05"
decision_date: "2026-10-05"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: ["ADR-086", "ADR-056", "ADR-107"]
related_adr: ["ADR-031", "ADR-046", "ADR-056", "ADR-059", "ADR-062", "ADR-083", "ADR-086", "ADR-088", "ADR-099", "ADR-106", "ADR-107"]
related_rules: ["G1", "AI1", "T1"]
related_incidents: []
version: "1.0.0"
---

# ADR-109 : Profil éditorial constructeur et contrat de rendu R7

- **Statut** : Accepted (2026-10-05). La fusion par l'owner vaut ratification.
- **Numéro** : dérivé le 2026-10-05 (`main` du vault ∪ PR ouvertes) : `main` porte ADR-105, ADR-112
  et ADR-113 ; aucune PR ouverte ne porte un numéro de 106 à 111. Signé après les ADR-106 à 108, que
  le script owner exige sur `main`. Le script owner re-vérifie le numéro avant le commit.
- **Étend** :
  - [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2, qui exige des `blocks[]` pour
    le canon constructeur, et §2bis, qui annonce des « profils différents » pour véhicule,
    diagnostic et constructeur sans définir celui du constructeur ;
  - [[ADR-056-r7-brand-runtime-completion|ADR-056]], pour le rendu d'une page marque depuis la
    projection ;
  - ADR-107 D2 : le champ `qa` s'ouvre à la FAQ constructeur.
- **Ordre de signature** : après ADR-106 et ADR-107.

## Périmètre

Rôle **`R7_BRAND`**, entités `constructeur`, pages `/constructeurs/{alias}-{id}.html`.

## Contexte

Constats vérifiés le 2026-10-04 : monorepo `main` `f1c601170`, WIKI `origin/main` `042e566`, base
en lecture seule.
Re-vérifiés le 2026-10-05 : monorepo `main` `658c0a3ce` (aucun fichier cité modifié depuis
`f1c601170`), WIKI épinglé inchangé, base en lecture seule.

1. **Le schéma WIKI contredit ADR-086 §2.**
   - `entity-data/constructeur.schema.json` déclare `additionalProperties: false`, avec les seuls
     champs `name`, `country`, `founded`, `brand_aliases`, `models`, `tier` et `vlevel`.
   - Aucun champ éditorial n'y figure, aucun ancrage DB non plus. Une fiche conforme à ADR-086 §2
     serait rejetée par le schéma.
2. **Aucune fiche, aucun mapper.**
   - `wiki/constructeur/` est vide ; il existe une proposition (`dacia`).
   - `build_exports_seo.py` route `constructeur` vers `R7_BRAND`, mais aucune fonction ne produit
     de bloc pour cette entité.
3. **Le servi R7 ne lit pas la projection.**
   - Listes déterministes depuis la DB (RPC `get_brand_page_data_optimized`) : identité, pièces
     populaires, véhicules populaires, gammes, marques liées.
   - Surcouche éditoriale lue depuis `__seo_r7_pages` (36 pages publiées, dernière le 2026-04-22),
     produite par `R7BrandEnricherService` à partir de gabarits (S2, S3, S7, S8) et de
     `__seo_brand_editorial`.
   - `__seo_brand_editorial` : 36 lignes hors pipeline WIKI, 34 curées par un agent le 2026-04-22
     et 2 par un compte d'administration. La section « À propos » (S11) s'appuie sur Wikipédia
     pour 32 marques (`history: wikipedia` dans les fiches RAG constructeur).
4. **Le gamme a son ancrage DB explicite** (`pg_id` dans `gamme.schema.json`). Le constructeur
   n'en a pas.

## Décision

### D1 — Profil éditorial constructeur

| Section (`R7_BRAND/…`) | Tier | Source |
|---|---|---|
| `brand_overview` | **M** | éditorial sourcé : origine, groupe, positionnement, repères historiques utiles à l'orientation |
| `faq` | R | éditorial sourcé : questions d'orientation marque |

- Ce sont les « contenus d'orientation marque » et la « FAQ marque » de la matrice des rôles (v5).
- Interdits, comme pour R7 : procédure, symptômes, fiche véhicule détaillée.
- Les listes de navigation (modèles, gammes, pièces, véhicules) restent des faits DB. Elles ne sont
  jamais rédigées dans le WIKI.

### D2 — Évolution du contrat WIKI (ADR-062 §8, MINOR)

- `entity-data/constructeur.schema.json` gagne deux champs optionnels :
  - `marque_id` : ancrage DB explicite, sur le modèle de `pg_id` pour la gamme, validé contre un
    manifeste commité comme `related_gammes` ;
  - `editorial` : objet fermé `{brand_overview, faq}`, chaque section ayant la forme `editorialBlock`
    du schéma gamme.
- Le builder produit les blocs `R7_BRAND/brand_overview` et `R7_BRAND/faq` depuis `editorial`.
  Pas d'`editorial`, pas de bloc ; aucun texte par défaut.
- La FAQ constructeur peut porter `qa`, avec toutes les règles d'ADR-107 D2 et D3 : une seule
  vérité, `content_md` dérivé, `FAQPage` seulement depuis `qa`.

### D3 — Table R7 v1

| Section WIKI | Section servie | Titre fixe |
|---|---|---|
| `brand_overview` | `R7_S11_ABOUT` | À propos de la marque |
| `faq` | `R7_S9_FAQ` | Questions fréquentes |

- Composées depuis la DB, inchangées : `R7_S1_HERO`, `R7_S3_SHORTCUTS`, `R7_S4_GAMMES`, `R7_S5_PARTS`,
  `R7_S6_VEHICLES`, `R7_S10_RELATED`.
- **Non rendues sur le chemin projeté** : les sections de gabarit `R7_S2_MICRO_SEO`, `R7_S7_COMPATIBILITY`
  et `R7_S8_SAFE_TABLE`. Un texte de gabarit n'est pas du contenu sourcé (ADR-086 §2, « non
  générique »).
- `__seo_r7_pages` et `__seo_brand_editorial` ne sont pas lus sur le chemin projeté. **Aucun
  repli** vers ces tables ni vers un texte par défaut.
- La table vit dans le module de projection existant, sur le modèle du mapper R3 (ADR-106 D1).

### D4 — Complétude

- Une entité R7 est prête à servir si `brand_overview` est présente et valide.
- `faq` est rendue si elle existe, jamais exigée.

### D5 — Présentation et activation : celles d'ADR-106

- Prose sûre par section, titres fixes, provenance non affichée.
- En-tête inchangé : title, meta, H1.
- Activation marque par marque, par `SEO_PROJECTION_READ_V1` et le canary
  `R7_BRAND@constructeur:<slug>`, après une comparaison écrite projeté vs servi. Acte owner.
- La page est rattachée à l'entité par `marque_id`, jamais par similarité de nom ou d'alias.

### D6 — Séquence

- ADR-086 (séquence, point 5) ne fait passer le constructeur qu'**après** la preuve sur la gamme.
- Cet ADR fixe le contrat pour que l'évolution du schéma soit prête ; la production de fiches
  constructeur suit cette séquence.

## Options considérées

- **Projeter les sections de gabarit** : rejeté. Ce serait du remplissage générique.
- **Importer `__seo_brand_editorial` dans le WIKI** : rejeté. Ce contenu a été curé hors pipeline
  et n'a pas passé la porte de promotion. Il peut servir de piste de sources, pas de fiche.
- **Rattacher par `marque_alias`** : rejeté. Une égalité de nom n'est pas un ancrage ; on
  retient la même règle que `pg_id`.

## Ce que cet ADR ne fait pas

- Il ne crée aucune fiche, ne modifie ni le WIKI ni le builder, et n'active aucune lecture servie.
- Il ne change ni URL, ni meta, ni H1, ni robots, ni les listes DB de la page.

## Conséquences

### Positives

- Le canon constructeur devient conforme à ADR-086 §2, et la page marque peut être servie depuis
  une source validée.
- Le schéma et ADR-086 cessent de se contredire.

### Négatives

- Une page R7 projetée perd les sections de gabarit (D3). D'où la comparaison et l'activation
  marque par marque.
- Aucune marque n'est prête avant la production de fiches, elle-même soumise à la séquence ADR-086.

## Rollback

- Avant activation : revert, sans effet servi.
- Après activation : retrait de la marque du canary, ou coupure de `SEO_PROJECTION_READ_V1`.

## Anti-patterns interdits

- Rédiger dans le WIKI une liste que la DB possède.
- Combler une section par un gabarit, `__seo_brand_editorial` ou `rag://`.
- Rattacher une page à une fiche par similarité de nom.

## Références

- [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2, §2bis, §6, séquence.
- [[ADR-056-r7-brand-runtime-completion|ADR-056]] — runtime R7.
- ADR-106 — contrat de rendu R3 (modèle). ADR-107 — FAQ structurée.
- [[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport|ADR-099]] D5 — canary par
  paire.
- [[ADR-062-repository-contract-system-meta-model|ADR-062]] §8 — évolution SemVer du contrat WIKI.
- [[ADR-031-four-layer-content-architecture|ADR-031]] /
  [[ADR-046-r-stack-single-generator-and-layers|ADR-046]] — le RAG n'est pas une source de contenu.
