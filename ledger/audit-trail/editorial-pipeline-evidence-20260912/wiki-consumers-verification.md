# WIKI : connaissances et besoins des consommateurs — 14 septembre 2026

## Scan

PARTIAL_COVERAGE. Exigence utilisateur : un WIKI riche en connaissances mécaniques, commerciales, marketing et SEO, précises et exactes, pour alimenter les pages R et le RAG au service des clients. Lecture ciblée du schéma gamme, des trois contrats de manifeste export, du modèle gamme et du candidat filtre-a-huile. Pas de vérification de chaque route applicative.

## Analysis

Le schéma gamme prévoit neuf blocs éditoriaux, commerce_intent, intents, decision_brief et des liens métier. Le candidat remplit neuf blocs, mais aucun ne renseigne usefulness_target. Cette absence n'est pas une erreur de schéma et ne prouve pas à elle seule une absence d'utilité ; elle montre que l'objectif consommateur n'est pas explicité dans ce champ.

Le contrôle direct du candidat contre entity-data/gamme.schema.json retourne 17 erreurs : cinq sur decision_brief et douze sur les identifiants sources de sept blocs. Le validateur frontmatter précédemment vert n'est donc pas une validation de ce contrat métier. Certaines incompatibilités ont été introduites ou conservées dans les derniers lots. Ce constat corrige la portée des validations antérieures ; il ne remet pas en cause les archives réellement contrôlées.

Le modèle gamme contient également des statuts historiques et des exemples numériques mécaniques dont la preuve n'est pas fournie dans ce modèle. Il ne peut pas servir tel quel de standard d'excellence éditoriale. Pas de modification du canon ou de ses copies ce tour.

## Correction proposée

Objectifs à vérifier par besoin réel, sans imposer mécaniquement tous les blocs à toutes les pièces :

| Besoin client | Connaissance utile au WIKI | Preuve ou limite |
| --- | --- | --- |
| Comprendre | Rôle, fonctionnement, variantes, termes et schémas | Passage constructeur/équipementier, portée explicitée |
| Choisir | Critères déterminants, erreurs de sélection, différences justifiables | Justificatifs propres aux produits ; correspondances exactes obtenues du catalogue |
| Entretenir | Échéances applicables, contrôles, précautions, limites des procédures | Notice applicable ; aucune instruction universelle déduite d'un seul exemple |
| Réagir à un symptôme | Conduite à tenir, hypothèses, vérifications et limites | Distinguer mécanisme et causalité ; référencer la source diagnostique canonique |
| Acheter avec confiance | Bénéfices établis, objections, contenu des kits, éléments de comparaison | Faits vérifiés ; prix, stock et offres courantes depuis leurs systèmes responsables |
| Obtenir de l'aide | Questions client, conditions de réponse, cas nécessitant escalade | Documents de service approuvés, dates et périmètre |
| Trouver la bonne réponse | Terminologie, questions et intentions issues des données de recherche | Mesures datées ; pas de mot-clé ou intention inventé pour gonfler un score |

Chaque bloc doit porter un besoin, une preuve localisable, un périmètre d'application et ses limites. À la consommation : page destinataire existante, rôle, conditions de réutilisation, compléments catalogue requis. La même connaissance peut servir plusieurs usages ; répéter le même article intégral partout n'établit pas leur adéquation. Le mapping exact des rôles R reste à vérifier dans le registre canon avant toute mutation de routes.

Les règles SEO et la gouvernance des rôles gardent leur source canonique. Le WIKI contient les connaissances et signaux validés utiles à leur application ; il ne devient pas une copie concurrente des règles ou des données transactionnelles. Le RAG consomme la connaissance validée et conserve ses sources/conditions ; il ne sert pas de preuve à cette même connaissance.

Priorité immédiate : résoudre la divergence du contrat métier et vérifier les consommateurs natifs avant de poursuivre l'enrichissement. Ne pas changer un enum de provenance ou préfixer arbitrairement les sources pour faire passer le schéma. Puis établir les besoins manquants par rôle/entité, rechercher uniquement les preuves utiles et vérifier leur appui réel. Le montage/réutilisation du pilote reste un lot ouvert après ce contrôle.

## Validation

Vérification directe JSON Schema : FAIL17, preuve wiki-consumers-schema-check.json. Lecture des interfaces : pas de preuve de routage, publication, pertinence ou exhaustivité globale. Aucune modification de code, schéma, proposition, source RAW ou statut de publication ce tour. Pas de suite de tests rejouée pour ce cadrage documentaire.

## Verdict

PARTIAL_COVERAGE. L'objectif métier est explicité, mais la richesse et l'exactitude de toutes les connaissances ne sont pas démontrées. Le pilote reste bloqué, le corpus et toutes les pages R ne sont pas qualifiés. La compatibilité contractuelle doit être corrigée avant de présenter le WIKI comme prêt pour tous ses consommateurs.
