# R6 — refus editorial effectivement respecte

## Scan

Périmètre ciblé : 19 fichiers applicatifs lus, souvent par extraits, listés dans [le manifeste](r6-quality-coverage.json). Code du candidat isolé, contrôles amont et lecture du rendu V2. Aucun audit DB ni interrogation du pipeline réel. Le candidat est sur HEAD 0c31807c ; origin/main 4b9d2ffd ; les trois fichiers source modifiés ne différaient pas entre ces révisions avant ce lot.

## Analysis

1. `wouldUpdate` refusait certains guides en simulation, mais le chemin hors simulation construisait et écrivait quand même leur contenu. Les tests avant correction reproduisent ce défaut pour un score de 100 avec des critères copiés, et pour un score insuffisant.
2. Le contrôle D1 ne refusait les explications copiées qu'au-delà de la moitié des critères et comparait très peu de variantes. Il ne vérifiait pas la structure avant accès aux propriétés. Des variantes accentuées, des explications vides et des données de mauvais type échappaient au contrôle ou provoquaient une erreur.
3. Le producteur extrait une checklist de compatibilité et peut fabriquer `label=guidance`, notamment avec son complément V4. Le lecteur V2 traite encore ce tableau comme des niveaux de qualité et le composant accepte `AltTier`. Ce chemin de code explique une possibilité de confusion ; son origine historique dans les lignes DEV n'est pas prouvée.
4. [L'examen des sources](r6-quality-sources.md) écarte les caractéristiques de transmission et de carburant diesel pour une affirmation générale sur le filtre d'huile moteur.

## Correction préparée avec autorisation utilisateur

Quatre fichiers du candidat : gate existante durcie, décision unique pour simulation/exécution, diagnostics retournés aussi en exécution, tests. Réutilisation du schéma SelectionCriterionSchema et de normalizeSeoText. Un seul doublon normalisé, une explication identique au libellé ou un critère mal formé bloque le lot éditorial. Les numéros de lignes sont exposés dans les raisons, sans suppression ni fusion automatique des critères.

L'exception existante où toutes les sections sont rejetées conserve uniquement ses métadonnées de diagnostic. Les tests vérifient l'ensemble exact des champs écrits et `source_verified=false`. Cette exception n'écrit pas de contenu. Un guide partiellement acceptable mais refusé par la gate n'appelle pas l'écriture.

## Validation

- Avant correction : **8 échecs, 2 succès** sur les 10 premiers cas, dont les deux divergences simulation/exécution.
- Après correction : **24/24 tests**, trois suites : 12 nouveaux tests de validation/orchestration, 8 du lecteur buying-guide-data, 4 de redirection R6.
- Typage backend complet `tsc --noEmit` : succès. Tests finaux compilés par ts-jest ; aucun changement fonctionnel après ceux-ci.
- ESLint ciblé : zéro erreur, un avertissement legacy préexistant dans le chargement du brief.
- `git diff --check` ciblé : succès. Logs, patch et empreintes conservés ici.
- Aucun test connecté à une DB, aucun déploiement, aucune validation navigateur ou CI. Les succès structurels ne valident pas l'exactitude des affirmations.

## Verdict

**VALIDATED_FOR_SCOPE_ONLY** pour cette protection du chemin d'écriture ; **PARTIAL_COVERAGE** pour le système éditorial. Le site servi et ses données existantes ne sont pas corrigés par ce candidat non déployé.

Suite prioritaire : corriger explicitement le contrat V1/V2 des niveaux de qualité et l'attribution `source_verified`, puis qualifier le passage MAHLE et reprendre les critères déjà stockés. Aucun score n'est présenté comme une probabilité de classement Google.
