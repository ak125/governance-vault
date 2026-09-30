# Ancrage des affirmations et entretien — 14 septembre 2026

PARTIAL_COVERAGE. Correction préparée dans le candidat WIKI autorisé ; aucun commit, push, export, changement DB ou déploiement.

## Scan

18 fichiers lus, certains par extraits, dans le WIKI et les deux captures RAW. Les 12 anciennes déclarations pending_capture du filtre à huile ont été rapprochées du texte et des preuves disponibles. Contrôle structurel automatisé des 15 propositions, distinct de leur analyse factuelle. [Périmètre exact](claims-pilot-coverage.json).

## Analysis

Le validateur contrôlait les titres de sections, sans rechercher text_anchor dans leur contenu. Douze contre-exemples étaient acceptés : extrait disparu, autre section, commentaire, exemple de code, URL ou titre répété. Une carte pouvait donc passer après la modification de son texte.

Les douze anciennes entrées du filtre ne sont pas douze faits démontrés faux : il y a des paraphrases non ancrées, des détails absents, des sources trop larges et des extrapolations. Chaque cas et la prochaine action figurent dans [les dispositions](claims-pilot-dispositions.json). Modifier seulement les ancres pour les faire passer masquerait les questions de preuve.

## Correction proposée et préparée

Le validateur existant analyse désormais le Markdown avec CommonMark. Un extrait déclaré doit être présent dans un bloc de prose de la section H2/H3 déclarée et unique ; un parent peut contenir ses sous-sections. Code, commentaires, destinations de liens et titres ne prouvent pas une affirmation de prose. Unicode NFC, casse et espaces sont normalisés ; pas de rapprochement sémantique qui effacerait une négation ou modifierait une valeur. Le champ reste optionnel conformément au schéma existant.

Dépendance markdown-it-py 3.0.0 déclarée dans le fichier déjà installé par la CI, version utilisée pour les tests. Ce parsing réutilise une bibliothèque, pas une nouvelle grammaire Markdown artisanale. Documentation primaire : [markdown-it-py](https://markdown-it-py.readthedocs.io/en/latest/using.html).

L'entretien du guide renvoie maintenant aux échéances du constructeur, sur la base d'une phrase de [MAHLE](https://www.mahle-aftermarket.com/na/en/products-and-services/filters/oil-filters/) déjà archivée. Les formulations chaque-vidange et intervalle long/huile synthétique ont été remplacées dans le corps, la FAQ et les champs structurés. Une ancienne entrée est remplacée par le claim échéance-constructeur ; l'entrée capacité/intervalle est retirée avec sa généralisation non étayée, et reste tracée dans le patch. Ce retrait ne vaut pas preuve nouvelle. Aucune nouvelle capture du même document.

## Validation

- Avant : 12 échecs attendus sur les contre-exemples, 12 succès. Après : 197 tests ciblés passent, dont 24 tests du validateur et les suites promotion, génération de carte et citabilité. Compilation Python réussie.
- Fiche : frontmatter PASS, score legacy vérifié à 0.46 ; rattachement natif RAW et SHA de la capture MAHLE inchangés ; nouvelle ancre entretien présente.
- Carte actuelle : 14 déclarations, 4 captured, aucune verified ; 10 extraits historiques encore absents de la section déclarée. [Résultat ciblé](claims-pilot-coverage-after.json).
- Promotion native : BLOCKED, avec COVERAGE_STRICT_FAIL et SUBSTANCE_SCORE. Les raisons sont produites par le décideur existant, sans nouveau contournement. [Décision](claims-pilot-promotion.json).
- Impact sur les 15 propositions : 1 PASS, 6 WARN (cartes absentes), 8 FAIL, soit 34 erreurs d'ancrage. Ces résultats portent uniquement sur la structure et les rattachements. [Résultats par fiche](claims-pilot-coverage-all.json).

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour le comportement du validateur et le rattachement de la correction entretien. PARTIAL_COVERAGE pour la qualité globale. Le candidat révèle un retard de correction des cartes ; il ne passera pas la vérification globale de couverture tant que ces écarts restent ouverts. Aucune dégradation silencieuse ni validation forcée.

Les droits de publication restent inconnus. Montage, réutilisation, diagnostic, normes et équivalences OE/OES ne sont pas validés par ce lot. Le score n'est ni une note d'exactitude ni une prévision de classement Google.

Prochaine action : reprendre les dix entrées restantes du filtre, en commençant par les architectures et clapets pour lesquels FILTRON/MAHLE existent déjà ; corriger les formulations avec leurs passages puis leurs ancres. Les normes et affirmations réglementaires nécessitent une qualification officielle distincte. Les autres propositions restent dans le relevé d'écarts.

[Patch candidat](claims-pilot-wiki.patch) · [Guide candidat](claims-pilot-proposal-candidate.txt) · [Preuve entretien](claims-pilot-source-validation.json) · [Tests](claims-pilot-tests-regression.log).
