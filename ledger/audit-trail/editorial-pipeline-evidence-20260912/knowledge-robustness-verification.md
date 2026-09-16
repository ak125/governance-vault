# Robustesse du catalogue — 13 septembre 2026

## Scan

Candidat `/home/deploy/knowledge-navigation-candidate-20260913`. Comparaison des inventaires figes des 12 et 13 septembre; generateur et tests existants. Perimetre detaille dans `knowledge-robustness-coverage.json`. Ce lot ne relit pas les corps des 7343 documents.

## Analysis

Contre-preuves reproduites: une modification de politique/collecteur pouvait presenter une absence comme une suppression de source; des empreintes de methode absentes pouvaient donner « unchanged ». Le rendu validait les anciens noms de fiches, mais pas les nouveaux; une erreur de metadata tardive pouvait laisser des fiches deja modifiees. Les empreintes des inventaires compares etaient absentes de la projection.

## Correction proposee et preparee

Autorisation owner: corriger, ameliorer et continuer le candidat. Comparaison suspendue pour methode inconnue/invalide/modifiee. Empreintes SHA-256 des inventaires en JSON canonique conservees, avec celles de politique et collecteur (ces dernieres designent la collecte historique, pas le code actuel du rendu). Tous les noms hash sont verifies et tous les fichiers serialises avant le premier remplacement; catalogue.json reste ecrit en dernier. Reutilisation du remplacement atomique existant par fichier. Aucun changement de dependance, de qualification ou du timer.

## Validation

`knowledge-robustness-before.log`: cinq nouvelles methodes de test echouent avant correction (5 failures, dont deux sous-cas dans une methode, et 1 error pour la provenance absente). `knowledge-robustness-tests.log`: 31 tests PASS apres correction, dont noms invalides, metadata tardive, politique modifiee, methode inconnue et reprise apres interruption d'ecriture simulee. Replay reel: 7343 contenus, 16998 occurrences, 10 ajouts, 13 modifications, 16975 inchanges; aucune source incomparable sur ces deux snapshots. 7343 fiches et cinq vues verifiees structurellement, zero lien Markdown local casse. Les quatre fichiers du collecteur actif conservent leurs empreintes precedentes.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour ces controles; PARTIAL_COVERAGE global. Aucun deploiement ni activation. Une erreur disque peut encore produire un dossier temporairement mixte: les ecritures sont atomiques par fichier, pas une transaction de dossier. Une reprise converge dans le scenario teste. Pas de preuve UI Obsidian, de qualification factuelle ni de fermeture d'une lacune de page.

Suite editoriale: relier une question manquante d'une page active a un passage capture precis, confronter les revisions GitHub/VPS du pilote filtre-a-huile, puis utiliser la qualification WIKI native et verifier la section servie. Aucun score ou nombre de sources ne remplace cette preuve.

Retour: [[ledger/audit-trail/2026-09-12-editorial-pipeline-codex|Rapport principal]].
