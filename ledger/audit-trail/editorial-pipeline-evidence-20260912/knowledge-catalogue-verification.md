# Corpus classe, changements et lecture editoriale — 13 septembre 2026

## Scan

Deux manifests de collecte figes (12 septembre 11:05 UTC et 13 septembre 06:00 UTC), toutes leurs metadonnees et trois objets de provenance filtre-a-huile. Projection de 16998 occurrences vers 7343 empreintes distinctes. Aucun audit semantique global des corps. Perimetre exact dans knowledge-catalogue-coverage.json et calculs dans knowledge-catalogue-summary.json.

## Analysis

7226 contenus AutoMecanik, 91 Alliance, 26 Auto Pieces. Les familles se recouvrent : 1946 contenus sont a la fois recycled et consumer_copy. Le nouveau tableau utilise 19 combinaisons exclusives pour ne pas gonfler le total ; le detail par famille est explicitement non additif. La famille wiki n'est ni une acceptation native ni une preuve de disponibilite des exports.

Comparaison par identite (source, chemin) : dix ajouts, treize modifications de corps, zero retrait, zero reclassification, 16975 occurrences inchangees. Cela n'est pas contradictoire avec 18 empreintes nouvelles et sept disparues de l'inventaire precedent : une modification peut remplacer une empreinte sans supprimer un fichier. Horodatage seul ignore ; source manquante/incomplete, configuration changee ou absence de baseline restent non comparables.

Pilote filtre-a-huile : deux versions de proposition distinctes (GitHub/VPS). Note GitHub declare 29 sources primaires, index VPS declare 22 sur 59 URL. La divergence doit etre rapprochee aux revisions ; aucun choix de vainqueur automatique. Aucune entree de cet index ne porte une empreinte de capture ; absence de captures ailleurs non etablie. Le niveau de confiance declare ne prouve pas la qualite factuelle.

## Correction proposee et preparee avec autorisation utilisateur

Extension du collecteur existant dans une copie isolee /home/deploy/knowledge-navigation-candidate-20260913. catalogue() produit une fiche par empreinte avec tous projets/familles/provenances et qualification not_evaluated. render_catalogue() genere les fiches Markdown, tableaux natifs Obsidian Bases, accueil et changements. Aucun corps documentaire recopie. Les fichiers identiques de navigation ne sont pas reecrits ; les anciennes fiches sont conservees comme unobserved et exclues de la vue actuelle, sans suppression de source.

Le bilan candidat expose les changements en plus des totaux historiques, et le render existant pointe vers le catalogue. Aucun nouveau crawler, moteur de score, taxonomie d'autorite, orchestrateur ni notification. Le runtime quotidien reste inchange.

Un document de lecture editoriale accompagne le pilote : partir d'une page/section active et de sa question, distinguer manque/rendu/contradiction, retrouver ou capturer le passage utile, qualifier via le WIKI natif, composer la section puis verifier le rendu et la revision. Ce document d'analyse ne remplace pas le canon. Obsidian sert a consulter/filtrer/relier ; aucune qualification ni synchronisation bidirectionnelle configuree.

## Validation

Huit tests de fonctionnalite echouent avant implementation. Apres correction : 24 tests unittest PASS (13 existants et 11 nouveaux), dont identites multiples, separation projets, absence de certification, erreurs source sans fausses suppressions, modifications vs metadonnees, non-reecriture et conservation des fiches non observees. Rejeu metadonnees sans reseau ni executant principal : 7343 fiches, 16998 provenances, zero lien Markdown local casse, cinq vues Bases controlees structurellement. Notebook de reproduction fourni ; pas d'execution kernel revendiquee. Le premier validateur de frontmatter utilisait un separateur trop large (--- dans un titre) ; validation corrigee pour le separateur de ligne, puis toutes fiches verifiees.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour projection et differences ; PARTIAL_COVERAGE pour objectif editorial. Aucun deploy/commit/push/merge/DB/corpus source, nouveau timer, envoi externe ni modification de coffre Obsidian existant. Rendu dans Obsidian non verifie. La verite des affirmations et les besoins de chaque page restent a traiter via la chaine native. Les 24 tests ne sont pas une preuve d'activation.

Documentation primaire consultee : [Bases](https://help.obsidian.md/bases), [Proprietes](https://help.obsidian.md/properties), [Syntaxe Bases](https://help.obsidian.md/bases/syntax), [Backlinks](https://help.obsidian.md/plugins/backlinks), [Contenus fiables Google](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).

[[ledger/audit-trail/2026-09-12-editorial-pipeline-codex|Rapport cumulatif]].
