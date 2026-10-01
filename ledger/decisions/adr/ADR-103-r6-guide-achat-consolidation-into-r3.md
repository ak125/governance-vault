---
id: ADR-103
title: "Guides d'achat (R6_GUIDE_ACHAT) consolidés dans les conseils (R3) — retrait de l'index sous drapeau, maillage interne aligné avant activation : amende ADR-090 §C2"
status: accepted
date: "2026-10-01"
decision_date: "2026-06-10"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-090"]
extends: ["ADR-027"]
related_adr: ["ADR-027", "ADR-031", "ADR-040", "ADR-044", "ADR-086", "ADR-090", "ADR-101"]
related_rules: ["G1", "G2", "AP-10"]
related_incidents: []
version: "1.0.0"
---

# ADR-103 : Guides d'achat (R6_GUIDE_ACHAT) consolidés dans les conseils (R3)

- **Statut** : Accepted (2026-10-01). La fusion par l'owner vaut ratification.
- **Ratifie** la décision owner du 2026-06-10 (consolidation R6 → R3), déjà implémentée en code
  derrière un drapeau éteint (monorepo #925 et #1613).
- **Étend** [[ADR-027-r5-consolidation-into-r3-s2-diag|ADR-027]] : même modèle que la consolidation
  R5 → R3, appliqué aux guides d'achat.
- **Amende** [[ADR-090-seo-projection-forward-writer-canon|ADR-090]] sur le seul point §C2
  « existence-gating du lien `buying-guide` » (voir D5). Le reste d'ADR-090 reste en vigueur.
- **Méthode** : chaque chiffre ci-dessous a été mesuré le 2026-10-01 (base de données en lecture
  seule, `main` du monorepo au commit `4dcd4cf9b`, GSC sur 90 jours).

## Périmètre

Cet ADR porte sur le rôle **`R6_GUIDE_ACHAT`** (nom canonique,
[[ADR-040-seo-roles-canon-ts-side-only|ADR-040]]) :

- les pages détail `/blog-pieces-auto/guide-achat/{pg_alias}` servies par `r6-guide.service.ts` ;
- le hub `/blog-pieces-auto/guide-achat`.

Il ne porte **pas** sur `R6_SUPPORT` (`/support/*`, `/cgv`), visé par la règle R-SEO-08 de
[[rules-seo-pagerole]]. Il ne porte pas non plus sur la page autonome
`/blog-pieces-auto/guide-achat/comment-utiliser-selecteur-vehicule-pieces-auto`, qui a sa propre route.

## Contexte

1. **Deux pages pour une même intention.** Le guide d'achat (« comment choisir ») et l'article
   conseils (R3) d'une même gamme se disputent les mêmes requêtes. R3 porte déjà l'intention
   « choisir » : la section S3 « Choisir le bon … » existe pour **259 gammes**.
2. **Mesure GSC, 90 jours** : guides d'achat **83 clics / 9,5k impressions** ; conseils
   **764 clics**. Le guide capte peu et dilue le conseil.
3. **Décision owner du 2026-06-10**, implémentée inerte par le monorepo #925 (`72af6c316`) :
   redirection 301 du guide vers les conseils, seulement si la gamme a un article conseils publié.
4. **Monorepo #1613** (`4dcd4cf9b`, 2026-10-01), toujours derrière le drapeau éteint
   `SEO_R6_CONSOLIDATION_ENABLED` : pages sans conseils servies en `noindex, follow`, hub en
   `noindex, follow`, guides retirés du sitemap blog et du hub de crawl éditorial.
5. **État des données (2026-10-01)** : 221 guides publiés.
   - 73 ont un article conseils, donc 301 vers les conseils à l'activation.
   - 148 n'en ont pas : servis en `noindex, follow`, URL et canonical inchangées.
   - 0 guide sans gamme.
6. **Maillage interne non aligné.** Mesuré le 2026-10-01, le site lie massivement vers les guides :
   - **221 lignes sur 238** de `__seo_r1_related_blocks_cache` contiennent un lien `buying-guide`
     vers `/guide-achat/{alias}` (pages gamme R1) ;
   - liens codés en dur dans le frontend :
     - page conseils (`blog-pieces-auto.conseils.$pg_alias.tsx`, encart « Consultez le guide
       d'achat ») ;
     - `ConseilSections.tsx` (section S3) ;
     - `pieces.$slug.tsx` (« Liens utiles ») ;
     - `r1-reusable-content.ts` (carte « Guide d'achat ») ;
     - `ContentGuidePills.tsx` ;
   - liens de navigation vers le hub (8 composants, dont `QuickAccessGrid`, `GuidesStrip`,
     `BlogNavigation`, `plan-du-site`) ;
   - redirections héritées vers `/guide-achat/*` (`$.tsx`, `blog-pieces-auto.article.$slug.tsx`).

   Activé tel quel, le drapeau ferait pointer ces liens vers des 301 ou des pages hors index. Sur
   une page conseils, l'encart renverrait même par 301 vers la page elle-même.

## Décision

### D1 — Le guide d'achat n'est plus une page indexable autonome

L'intention « choisir sans erreur » est portée par R3 (article conseils, section S3).
`R6_GUIDE_ACHAT` reste un rôle du code (ADR-040), mais aucune page de ce rôle n'est destinée à
l'index.

### D2 — Posture par page, sans suppression ni changement d'URL

Drapeau allumé :

| Cas | Réponse |
|---|---|
| Guide dont la gamme a un article conseils publié | 301 vers `/blog-pieces-auto/conseils/{pg_alias}` |
| Guide sans article conseils | page servie, `noindex, follow`, URL et canonical inchangées |
| Hub `/blog-pieces-auto/guide-achat` | page servie, `noindex, follow` |
| Sitemap blog et hub de crawl éditorial | plus aucune URL de guide, à leur prochaine génération normale |

Aucune page n'est supprimée et aucune URL ne change. La génération du sitemap n'est jamais
déclenchée pour l'occasion. La redirection est *self-gatée* : jamais de 301 vers une page conseils
inexistante.

### D3 — Les 148 guides sans conseils ne sont pas « comblés »

Aucun contenu n'est généré pour donner un article conseils aux 148 gammes concernées. Un article
conseils naît par le pipeline normal (RAW → WIKI → consommateur). Dès qu'il est publié, la
redirection s'applique d'elle-même.

### D4 — Les sections WIKI `R6_GUIDE_ACHAT/*` sont inchangées

Les sections `R6_GUIDE_ACHAT/selection_criteria` et `quality_tiers` du contrat éditorial
([[ADR-086-encyclopedia-editorial-content-contract|ADR-086]]) restent dans la fiche gamme. Les
projeter dans R3 est hors périmètre et relèvera d'une décision distincte.

### D5 — Maillage interne aligné, condition préalable à l'activation (amende ADR-090 §C2)

Drapeau allumé, **aucun lien interne n'est émis vers une URL de guide retirée**.

- **Liens R1 (ADR-090 §C2).** Le *writer* émet un lien `buying-guide` vers un guide seulement si
  le guide est publié non-draft **et** la consolidation est éteinte. Consolidation allumée, le bloc
  `buying-guide` ne garde que le lien conseils (déjà prévu par §C2, score 0,9). La décision reste
  côté writer : le chemin de lecture et le frontend n'arbitrent rien, comme le pose §C2.
- **Liens codés en dur.** Chaque lien vers un guide est soit retiré, soit remplacé par le lien
  conseils. La cible est décidée par le backend à partir du même drapeau, puis transmise au
  frontend, qui ne devine rien.
- **Redirections héritées.** Pas de chaîne : une redirection qui visait un guide redirigé vise
  directement la page conseils.
- **Navigation vers le hub.** Les liens de navigation ne pointent plus vers le hub retiré.

Ce travail se fait dans une PR monorepo derrière le même drapeau, éteint par défaut, donc sans
effet avant l'activation.

### D6 — Ordre d'activation

1. Fusion de cet ADR par l'owner.
2. PR monorepo « maillage » (D5) fusionnée, et la mise à jour de la section R6 de
   `.spec/00-canon/role-matrix.md` (voir Conséquences).
3. Sonde PROD redéfinie (owner, `.github/workflows/prod-smoke-tests.yml`). La sonde « R6 guide »
   suit aujourd'hui les redirections : après l'activation, elle mesurerait la page conseils et
   passerait pour une mauvaise raison. Elle doit vérifier la posture de D2 :
   - 301 vers les conseils pour un guide qui en a ;
   - 200 et `noindex` pour un guide qui n'en a pas.
4. Câblage du drapeau en PROD (owner) : ajouter `SEO_R6_CONSOLIDATION_ENABLED_OVERRIDE` depuis la
   variable `PROD_SEO_R6_CONSOLIDATION_ENABLED` dans `deploy-prod.yml`, sur le modèle des
   variables `PROD_SEO_PROJECTION_*`. Puis passer la variable à `true` et créer le tag PROD.
5. Reconstruction du cache des blocs R1 par le writer, jamais par SQL manuel. Contrôle attendu :
   0 ligne de `__seo_r1_related_blocks_cache` contenant `/guide-achat/`.
6. Observation (voir Métriques).

## Options considérées

- **Laisser les deux pages indexées** : rejeté. La cannibalisation est mesurée (83 contre
  764 clics) et la cible R3 existe déjà.
- **Supprimer les guides ou leur renvoyer 404/410** : rejeté. Aucune suppression de page, aucune
  URL perdue ; le `noindex, follow` garde la page utile au visiteur.
- **301 de tous les guides, même sans conseils** : rejeté. Ce serait une redirection vers 404,
  ou vers une page hors sujet.
- **Activer sans aligner le maillage** : rejeté. Cela créerait 221 liens R1 vers des 301 ou des
  pages hors index, et des boucles sur les pages conseils.

## Ce que cet ADR NE fait PAS

- Il n'active pas le drapeau : l'activation reste un acte owner (D6).
- Il ne génère aucun contenu et n'écrit rien dans `sg_content` ni dans le WIKI.
- Il ne change ni ne supprime aucune URL et ne déclenche aucun sitemap.
- Il ne touche pas `R6_SUPPORT` ni la règle R-SEO-08.
- Il ne modifie pas le contrat ADR-086.

## Conséquences

### Positives

- Une seule page indexable par intention de gamme. Les signaux se concentrent sur R3.
- Le modèle de consolidation éprouvé par ADR-027 est réutilisé, sans nouveau mécanisme.

### Négatives

- Les 83 clics par trimestre des guides passent par une 301 ou disparaissent de l'index, le temps
  que R3 les reprenne.
- Le retour arrière demande un déploiement PROD (voir Rollback).

### Constats (ADR-101 D3)

- **`.spec/00-canon/role-matrix.md`** (contrat lu par `validate-role-coherence.js`) décrit encore
  R6 comme une page « Guide d'achat » autonome. C'est une divergence avec cet ADR, à résoudre par
  une PR monorepo qui met à jour la section `### R6 —`, en gardant ce titre, que le contrôle C3
  exige.
- [[ADR-044-seo-strategy-2026-roles-priority|ADR-044]] (`proposed`, non normatif) donne une
  priorité à R6. Cet ADR la rend caduque pour `R6_GUIDE_ACHAT`.

## Métriques de succès (J+30 après le tag PROD)

- GSC : les URL de guides sont « redirigées » ou « exclues par noindex » ; aucune n'est en 404.
- Clics des pages conseils au moins égaux à la base de 764 sur 90 jours, à saisonnalité
  comparable.
- `sitemap-blog.xml` : 0 URL `/guide-achat/` après sa prochaine génération normale.
- Cache des blocs R1 : 0 lien vers `/guide-achat/`.
- Liens internes du frontend : 0 lien rendu vers un guide retiré.

## Rollback

Passer `PROD_SEO_R6_CONSOLIDATION_ENABLED` à `false`, puis redéployer PROD (nouveau tag).

- Les pages reprennent leur posture d'avant, sans perte, puisque rien n'a été supprimé.
- Les guides reviennent dans le sitemap à sa prochaine génération.
- Le cache API (`Cache-Control` 300 s) s'efface seul.
- Les 301 déjà vues peuvent rester en cache chez les robots quelque temps.

## Anti-patterns interdits

- Générer du contenu pour « combler » les 148 guides sans conseils (D3).
- Supprimer une page de guide ou lui renvoyer 404 ou 410.
- Activer le drapeau avant la fusion de la PR « maillage » (D5, D6).
- Filtrer les liens de guide dans le chemin de lecture ou le frontend au lieu du writer (ADR-090 §C2).
- Déclencher la génération du sitemap pour accélérer le retrait.

## Références

- [[ADR-027-r5-consolidation-into-r3-s2-diag|ADR-027]] — modèle de consolidation R5 → R3.
- [[ADR-040-seo-roles-canon-ts-side-only|ADR-040]] — noms de rôles `R6_GUIDE_ACHAT` et `R6_SUPPORT`.
- [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] — sections WIKI `R6_GUIDE_ACHAT/*`.
- [[ADR-090-seo-projection-forward-writer-canon|ADR-090]] — writer des blocs R1, §C2 amendé ici.
- [[ADR-101-vault-decides-canon-authority|ADR-101]] — rang des fichiers `.spec/00-canon/**`, constats.
- [[ADR-031-four-layer-content-architecture|ADR-031]] — un guide d'achat est une section de la fiche gamme.
- Monorepo : #925 (`72af6c316`), #1613 (`4dcd4cf9b`).
