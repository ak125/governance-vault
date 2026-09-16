# Pages retirees et sections de destination — verification du 13 septembre 2026

## Scan

Priorite owner : verifier les pages deja arretees ou regroupees avant de revoir les roles et la qualite. Lecture ciblee du registre des contrats, decisions acceptees, routes et services ; 12 GET sans mutation, six sur DEV3000 et six sur le site public. Preuve horodatee : role-lifecycle-http-20260913.json. Le controle ne constitue pas un inventaire exhaustif des anciennes URL.

## Analysis

| Surface | Etat etabli | Destination ou fonction | Niveau de preuve |
| --- | --- | --- | --- |
| R5 detail diagnostic | Consolidee dans R3 selon ADR-027 | R3, section S2_DIAG, fragment diagnostic-rapide | Decision acceptee + un ancien slug verifie en HTTP 301 dans les deux environnements |
| R5 hub diagnostic-auto | Maintenu comme hub/outillage dans ADR-027 | Entree diagnostic, pas recreation des anciennes pages detail | Decision et inclusion sitemap dans le code ; pas de controle HTTP du hub dans ce lot |
| R6 guide achat | Une page autonome toujours active | guide-achat/filtre-a-huile repond 200 | HTTP public et DEV ; ne permet pas de conclure pour toutes les gammes |
| R6 consolidation vers R3 | Mecanisme conditionnel present | Service sous SEO_R6_CONSOLIDATION_ENABLED | Lecture code ; valeur effective globale du flag non mesuree, aucune activation |
| Anciennes routes article | Redirections conditionnelles presentes | advice + pg_alias vers conseils ; legacy_table __blog_guide vers guide-achat | Code loader ; pas de catalogue historique ni de test HTTP de ces alias dans ce lot |
| R6_SUPPORT | Surface utilitaire distincte du guide achat | Hors registre de contenu indexable | Registre @repo/seo-role-contracts ; ne pas confondre les deux R6 |
| R0/R1/R2/R3/R4/R6_GUIDE_ACHAT/R7/R8 | Roles de contenu declares actifs dans le registre | Contrats propres a chaque intention | Registre, pas validation de toutes les pages rendues |

Exemple public : /diagnostic-auto/voyant-disque-de-frein renvoie 301 vers /blog-pieces-auto/conseils/disque-de-frein#diagnostic-rapide. La destination renvoie 200 et contient le H2 Diagnostic rapide du disque de frein, mais aucun identifiant diagnostic-rapide. Le probleme est le raccordement du fragment, pas une absence de cette section. Le titre servait a fabriquer son identifiant ; changer le titre pouvait casser les liens.

Les recommandations de consolidation R3 du document historique du 3 juin restent des recommandations et ne prouvent pas une redirection executee. La matrice de roles de mars ne doit pas faire revivre les details R5 retires par ADR-027 ulterieure.

## Correction (proposee et preparee dans le candidat autorise)

Ancre S2_DIAG fixe dans le payload R3, utilisee par sommaire et contenu. Ancien fragment derive du titre conserve autour de la vraie section, sans recopier son contenu ni creer un bloc vide. Cache R3 versionne v4 pour ne pas resservir les anciens fragments. Les changements META deja presents sur origin/main sont preserves comme prerequis dans les deux fichiers du service/test R3 ; le patch du prerequis est conserve separement. Aucun changement des decisions de consolidation, du flag R6, des redirections publiques ou des donnees partagees.

## Validation

24 tests du service R3 passent, incluant les cas de filtrage META amont et deux titres differents pour S2_DIAG. Trois tests de rendu React passent : les deux fragments atteignent le meme tableau reel ; un fragment deja canonique ne cree pas de doublon d'identifiant ; absence d'alias compatible. ESLint backend/frontend : 0 erreur, deux warnings any des tests META amont ; git diff --check passe. Les preuves de lint sont separees ; les controles HTTP precedents representent l'etat en service avant ce candidat, pas une preuve de deploiement. Aucun typecheck global, CI ou navigateur apres deploiement dans ce lot.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour le correctif d'ancre et ses tests ; PARTIAL_COVERAGE pour le cycle de vie global des pages R. Etape suivante : rapprocher l'inventaire reel des URL avec les decisions de cycle de vie, puis faire controler a la boucle la destination, l'existence de la section et sa revision avant de compter ses preuves. Une page retiree ne doit pas etre proposee a la recreation pour combler un score ; la preuve utile doit etre rattachee a la section qui la remplace. Cette recommandation de mise en oeuvre ne cree aucune regle canonique.

Restent inconnus : couverture de tous les anciens slugs R5, conditions d'echec du service de redirection, etat global de la consolidation R6, completude factuelle et duplication semantique de toutes les sections, donnees Search Console et resultats visiteurs. Le score admin v2.3 prepare dans ce meme candidat reste un proxy structurel et ne valide ni publication ni position Google.
