# Filtre à huile — conception et média, 14 septembre 2026

Statut : PARTIAL_COVERAGE. VALIDATED_FOR_SCOPE_ONLY pour les contrôles décrits ci-dessous. Candidats RAW/WIKI autorisés ; aucun commit Git, push, export, changement DB ni déploiement.

## Scan

Périmètre : deux critères de choix du guide `proposals/filtre-a-huile.md`, leur représentation structurée et leur preuve documentaire. Douze fichiers explicitement lus, dont certains scripts par extraits ; exclusions dans [coverage](mahle-pilot-coverage.json). RAW HEAD/origin 7565934186fced370f78ea64d7616b912a0c9a6c, WIKI HEAD/origin 01cea8deda48d84b6a2993cd4bdefe8280082c0b, fetch sans dérive au début du lot.

## Analysis

Le critère média associait cellulose, synthétique et microfibres de verre à une efficacité croissante, en citant notamment une page de filtres de transmission. Cet appui ne justifie pas une hiérarchie générale pour l'huile moteur.

Le passage technique « Spin-on oil filter mix up? » de [MAHLE](https://www.mahle-aftermarket.com/na/en/products-and-services/filters/oil-filters/) décrit des différences internes selon le moteur malgré une apparence semblable, y compris le média et la finesse de filtration. La recommandation de confirmer la référence dans le catalogue est une conséquence éditoriale de ce constat, pas une preuve de compatibilité d'une pièce.

La page est composite : sections hydrauliques, performances promotionnelles, intervalles génériques et exemple OX 345 D exclus du raisonnement. Aucune date de publication établie. La capture entière conserve le contexte mais seuls les passages utiles soutiennent les nouvelles déclarations.

## Correction proposée et préparée

Dans le candidat autorisé : nouvelle capture native RAW, immuable, au statut CAPTURED_NEEDS_REVIEW (licence inconnue). Entrée d'intention par lacune pour pg_id 7 et consommateur WIKI uniquement. Catalogue natif relié au fichier par manifest_id et SHA ; deux ancres de claims dans la section critères. Remplacement de l'ancien claim de hiérarchie plutôt que conservation d'une fausse preuve. Texte, résumé et selection_criteria structurés alignés. Historique de provenance reformulé pour ne plus présenter des URLs ou anciens compteurs comme preuve actuelle.

Les exports restent désactivés et la fiche proposée. Aucun changement du moteur, des seuils ou des flags d'approbation.

## Validation

- Capture native réussie ; rejeu ignoré pour duplicate_content_hash, sans nouvelle copie.
- Gates RAW I et J PASS ; frontmatter WIKI PASS ; coverage strict PASS : 15 déclarations / 9 H2. Ce dernier vérifie schéma, sources et titres, pas l'appui sémantique de chaque phrase.
- Contrôle natif du raw_ref MAHLE : zéro échec/avertissement ; SHA du corps et du fichier recalculés ; les deux ancres existent dans la section déclarée.
- Score legacy vérifié à 0.46 ; promotion avant/après BLOCKED. Les passes déclaratifs dans la sortie legacy ne constituent pas une preuve d'exécution exhaustive des contrôles aval.
- Shadow : 82, dimension A 19.8 sous le plancher 22 ; 12 déclarations page_unproven et reality-manifest stale. Aucune inflation manuelle de confiance pour franchir le seuil.

Preuves : [capture](mahle-pilot-capture.json), [rejeu](mahle-pilot-repeat.json), [rattachement et ancres](mahle-pilot-source-validation.json), [coverage](mahle-pilot-coverage-validation.json), [promotion](mahle-pilot-promotion-after.json), [patch WIKI](mahle-pilot-wiki.patch), [patch RAW](mahle-pilot-raw.patch), [proposition candidate](mahle-pilot-proposal-candidate.txt).

## Verdict

Deux affirmations disposent maintenant d'une archive et d'un appui borné au bon contexte. La source n'est pas promue et le guide n'est pas validé pour publication. Les affirmations normes, diagnostic, entretien et OE/OES restent à qualifier. Les scores disponibles restent des indicateurs partiels ; ils ne mesurent pas la probabilité d'être premier sur Google.

Prochaine action : reprendre les 12 déclarations non prouvées depuis leurs lacunes réelles, vérifier leur présence dans le texte et la pertinence de chaque passage avant toute collecte supplémentaire ; distinguer suppression d'une assertion infondée, besoin de nouvelle preuve et information hors rôle R6. Le contenu servi et le reality manifest devront ensuite être vérifiés dans leur environnement effectif.
