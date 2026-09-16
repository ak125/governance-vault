# Verrou de preuve à la promotion — 14 septembre 2026

## Scan

PARTIAL_COVERAGE. Décideur WIKI, validateur de couverture et gate de provenance natifs dans le candidat `/opt/automecanik/wiki-editorial-qualification-20260912`. Périmètre autorisé : corriger et améliorer le système dans les candidats isolés. Pas d’activation ou de publication. Manifest détaillé : proof-gate-coverage.json.

## Analysis

Deux défauts reproduits dans des fichiers temporaires de test :

1. Avec le score injecté à0.99 et les gates métier sans rapport simulés propres, les vrais évaluateurs de couverture/provenance laissaient passer sept cas : pending, faux captured/verified, hash manquant, ancre absente, carte vide ou absente. Sept tests rouges avant correction, un témoin positif vert. Ce sont des contre-exemples du décideur, pas une mesure de la qualité du guide.
2. Une archive supprimée/modifiée ou un hash absent de l’inventaire pouvaient être acceptés. Une modification des octets après la décision n’invalidait pas l’autorisation d’appliquer : seules les métadonnées étaient figées. Quatre tests rouges séparés.

Les contrôles de préparation autorisent légitimement un travail en attente ; ce comportement ne doit pas autoriser sa promotion. Le score expérimental réduit les points d’une source pending, mais cette pénalité ne constitue pas un veto.

## Correction proposée

- `check-coverage-map.py` conserve son mode de préparation. La promotion utilise son option de preuve stricte : carte non vide, ancre explicite, statut capturé, page active/référence RAW et hash requis. Le prédicat de page existant est réutilisé. Catalogue lu dans le checkout sélectionné, identifiants dupliqués refusés. Schéma indisponible : arrêt prudent.
- `quality-gates.py` vérifie les octets des seules archives référencées par la carte. Identifiant et hash doivent résoudre un fichier unique ; fichier absent, modifié ou chemin hors RAW refusés. La vérification historique de l’inventaire reste en place.
- `promotion_decision.py` utilise ces contrôles et ajoute les fichiers RAW au manifeste avant/après évaluation et avant application. Même résolution des racines explicites, environnementales ou par défaut. Aucun nouveau décideur, collecteur, seuil, dépendance ou changement de mode runtime.
- Tests ajoutés au fichier existant ; aucun changement au guide, au catalogue des sources, aux archives RAW ou à l’application ce lot.

## Validation

232 tests ciblés PASS, dont23cas nouveaux. Chaîne : validateur couverture, décideur, promoteur, GAP1, citation readiness et provenance RAW. Les nouveaux cas éprouvent notamment les deux moteurs legacy/6dim à score/tier maximal injecté, le témoin éligible, les fichiers absents/modifiés, les chemins externes et le changement avant application. Les contrôles de score/métier injectés sont explicitement isolés ; les évaluateurs de preuve restent réels. Aucun appel réseau/DB ou application de promotion hors répertoires temporaires des tests.

Compilation Python et diff ciblé PASS. Le dry-run natif du vrai guide reste BLOCKED : six motifs `proof_unavailable` et trois erreurs d’ancrage sous COVERAGE_STRICT_FAIL, plus SUBSTANCE_SCORE. Ces motifs se recouvrent sur certains claims : ce ne sont pas neuf affirmations distinctes. Les scores0.46/89 sont inchangés. Deux archives FILTRON/MAHLE sont désormais dans le manifeste avec leurs SHA réels. Le lint de préparation conserve ses trois erreurs d’ancrage ; aucune disparition artificielle des lacunes.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour les contre-exemples et garde-fous testés ; PARTIAL_COVERAGE pour le système éditorial. Le verrou vérifie la disponibilité, l’intégrité et le rattachement déclaré. Il ne démontre pas à lui seul que le passage source justifie sémantiquement chaque affirmation, ni les droits de publication, l’exhaustivité de la carte ou la performance SEO.

Restent : qualification OE/OES et diagnostic, capture ISO indisponible, montage/réutilisation, contenu servi, calibration générale des scores et CI distante. Les autres fiches et le corpus n’ont pas été rescannés. Aucun commit/push/merge/DB/export/déploiement/cron/activation.
