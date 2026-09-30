# R6 — contrats de comparaison et provenance

## Scan

Lecture ciblée de 17 fichiers applicatifs/configuration/tests, listés dans [le manifeste](r6-contract-coverage.json). Registry consultée via jq, consignes du dépôt conservées. Candidat isolé sur HEAD 0c31807c ; les chemins applicatifs ciblés ne divergeaient pas de origin/main au début du lot. Le helper partagé conserve aussi les changements indexés des lots précédents.

## Analysis

- `sgpg_selection_criteria` a deux usages : critères de compatibilité V1 et comparaison de niveaux V2. Le cast backend puis le mode AltTier frontend transformaient les premiers en faux niveaux de qualité.
- Une simulation de bonne qualité ne corrigeait pas ce mélange de versions à l'écriture.
- Le producteur legacy attribuait `source_verified=true` avec la confiance et le score, puis le lecteur transmettait ce drapeau, y compris pour RAG. Le repli manuel le forçait aussi à true. Le libellé par défaut du helper affirmait « Source vérifiée » sans disposer d'une preuve.

## Correction préparée avec autorisation utilisateur

1. Contrat R6QualityTier existant exprimé en schéma Zod, type dérivé. Deux conteneurs V2 conservés, vérification des champs requis et des doublons normalisés. Aucun critère V1 converti en niveau, aucune donnée DB supprimée ou fusionnée.
2. Données absentes/invalides : `qualityTiersReviewRequired=true`, tableau vide et avertissement journalisé avec le champ et la gamme. Le frontend affiche une indisponibilité explicite dans la même section/ancre. Le mode AltTier est retiré. La route exige explicitement un verdict false pour afficher des cartes, ce qui protège aussi contre un ancien payload encore en cache. V1 reste inchangé.
3. L'écriture legacy porte le filtre de version V1/null dans l'UPDATE lui-même, puis exige une ligne affectée. V2 et versions inconnues ne sont pas ciblées ; zéro ligne n'est plus un succès. Les diagnostics sans contenu conservent leur chemin. Aucun appel au producteur réel ni modification DB pendant ce lot.
4. Le producteur legacy écrit `source_verified=false`, reviewer/date de vérification null. Les lecteurs V1/V2 refusent les anciennes déclarations de vérification RAG et exigent un booléen true pour les autres sources. Le fallback manuel ne fabrique plus de badge. Le helper partagé utilise un libellé neutre lorsqu'il n'a pas d'information suffisante.

La déclaration non-legacy déjà stockée reste une déclaration, pas une nouvelle validation factuelle. Ce lot n'approuve aucun contenu WIKI ni aucune affirmation automobile.

## Validation

- Avant : **18 échecs / 2 succès** sur les 20 premiers tests backend et **2 échecs / 1 succès** frontend, enregistrés avant modification du code.
- Après : **73 tests backend réussis** (49 sur R6/données/orchestration et 24 sur R3 pour le helper partagé), **5 tests frontend réussis** (composant et loader).
- Les tests du writer passent par le SDK Supabase installé avec un fetch simulé : URL de requête, méthode PATCH, filtre pg_id, filtre V1/null, select des lignes affectées, refus à zéro ligne et diagnostic sans restriction de version. Ils ne valident pas PostgreSQL, les permissions ni RLS en environnement réel.
- Typage backend complet : succès. Typage frontend global : **limité**, 15 erreurs TS2307 dans les fichiers non modifiés, dépendances `@tiptap/react`/`@playwright/test` absentes. Aucun diagnostic dans les fichiers de ce lot. Pas de suppression de tests ni d'assouplissement de configuration.
- ESLint ciblé : aucune erreur ; avertissements legacy existants (3 backend, 1 frontend). Les essais ont également révélé puis permis de corriger une erreur JSX transitoire et la fixture du loader adaptée au contrat React Router installé (`context`, `url`, `pattern`).
- Documentation Supabase consultée : [filtres](https://supabase.com/docs/reference/javascript/using-filters), [UPDATE et retour des lignes](https://supabase.com/docs/reference/javascript/update), changelog et SDK local. Pas de changement de version ni de dépendances.

## Verdict

**VALIDATED_FOR_SCOPE_ONLY** pour les contrats et comportements testés ; **PARTIAL_COVERAGE** pour le système. Code préparé et indexé, non committé et non déployé. Aucun contenu existant ni statut dans la base n'a été changé. Les métadonnées et caches servis ne sont donc pas déclarés corrigés.

Restant : qualification documentaire et reprise des critères déjà stockés, capture MAHLE ciblée, remplacement de la production legacy V1 par la projection WIKI gouvernée, puis validation DB/CI/frontend complète avant déploiement coordonné. Les scores ne prouvent ni la qualité factuelle ni un classement Google.
