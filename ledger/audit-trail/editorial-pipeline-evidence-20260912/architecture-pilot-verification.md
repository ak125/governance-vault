# Architectures et clapets du filtre à huile — 14 septembre 2026

PARTIAL_COVERAGE. Candidat WIKI autorisé ; aucun commit/push/export/DB/déploiement. [Coverage exact](architecture-pilot-coverage.json).

## Scan

Six fichiers lus, certains par passages : contrat WIKI, proposition, carte de couverture, catalogue et archives MAHLE/FILTRON. HEAD/origin WIKI 01cea8deda48d84b6a2993cd4bdefe8280082c0b, fetch sans dérive. Le code de validation est inchangé ; aucun nouveau système ni nouveau scrape.

## Analysis

Le critère d'architecture affirmait des caractéristiques trop générales : cartouche nécessairement en papier et clapets généralement portés par le boîtier moteur. Les passages retenus de MAHLE expliquent le remplacement du filtre vissé comme ensemble et celui de l'élément en cartouche ; ils ne prouvent pas l'emplacement général des clapets.

FILTRON explique le lien entre orientation et anti-retour, ainsi que le by-pass en conditions de colmatage ou d'huile froide. La formulation sur la position « tête en bas » a été remplacée par le principe d'orientation afin de ne pas traduire une géométrie ambiguë en règle universelle. Le réglage du by-pass selon moteur est rattaché au passage MAHLE approprié, et non à FILTRON.

Sources archivées : [MAHLE oil filters](https://www.mahle-aftermarket.com/na/en/products-and-services/filters/oil-filters/), [FILTRON valves](https://filtron.eu/en/insights/filter-guide/spin-on-oil-filter-valves.html). Les limites de section et empreintes de passages sont dans [la preuve de rattachement](architecture-pilot-source-validation.json).

## Correction proposée et préparée

- Architecture : boîtier et élément remplacés ensemble sur le filtre vissé ; élément remplacé dans le boîtier réutilisé pour la cartouche. Critère, résumé et bloc variants alignés. Respecter l'architecture du véhicule est le conseil éditorial associé, pas une preuve de compatibilité précise.
- Anti-retour : rôle de retenue à l'arrêt et nécessité liée à l'orientation, sans généraliser une position de montage.
- By-pass : principe de maintien du passage d'huile en cas de colmatage/froid ; différence de réglage selon moteur. Aucune pression chiffrée ajoutée ni vérifiée.
- Retrait du claim clapets-cartouche dans boîtier avec sa formulation. Ce retrait est tracé dans le patch ; il ne constitue pas une preuve supplémentaire. Le nouveau claim colmatage/froid porte sur le fonctionnement, pas sur une perte de puissance.

La confiance déclarée du claim de réglage est fondée sur la nouvelle formulation qualitative et le passage primaire MAHLE ; elle ne valide pas les anciennes données numériques. Toutes les entrées concernées restent captured, aucune verified. Les phrases ISO et les relations diagnostiques conservées restent hors validation de ce lot.

## Validation

Frontmatter, calcul du score0.46, quatre ancres ciblées, hashes des deux archives et contrôle natif raw_ref passent. Les archives sont inchangées ; zéro nouvelle capture. Les flags proposed/exportsfalse et les relations diagnostiques non validées sont préservés.

Carte actuelle : 14 déclarations, 8 captured, 0 verified. Les erreurs d'ancrage passent de10 à6 : trois rattachements corrigés et un ancien claim retiré ; une nouvelle déclaration de fonctionnement est ajoutée. [Résultat natif](architecture-pilot-coverage-validation.json).

Promotion native : BLOCKED avec COVERAGE_STRICT_FAIL et SUBSTANCE_SCORE. Le score shadow89/tierA n'est pas une approbation :6page_unproven et reality-manifest stale restent signalés. [Décision complète](architecture-pilot-promotion.json).

Les197tests du lot précédent sont réutilisables sur le code inchangé. Empreintes du validateur, de son fichier de tests et de sa dépendance identiques ; les validations des données modifiées ont été rejouées. Aucun test applicatif ou scan des autres propositions répété sans changement.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour ces corrections de formulation et rattachements. Le guide entier demeure PARTIAL_COVERAGE et bloqué pour promotion. Les six entrées restantes concernent ISO (3), droit/qualité OE-OES (2), diagnostic by-pass permanent (1). Montage, réutilisation et faits hors carte restent également à qualifier.

La prochaine étape doit vérifier ces affirmations auprès des sources officielles, décider de l'utilité de chaque information pour le guide et retirer les déclarations périmées avec traçabilité. Le nombre de sources, le nombre de claims et le score ne remplacent pas cette vérification.

[Patch](architecture-pilot-wiki.patch) · [Guide candidat](architecture-pilot-proposal-candidate.txt).
