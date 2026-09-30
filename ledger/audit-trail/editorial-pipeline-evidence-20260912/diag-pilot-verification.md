# Diagnostic du filtre à huile — 14 septembre 2026

## Scan

PARTIAL_COVERAGE. Guide candidat filtre-a-huile : section diagnostic, failure_symptoms, FAQ visible et structurée, diagnostic_relations, notes de revue/provenance, carte de couverture et sources. Manifest détaillé : diag-pilot-coverage.json. Corrections candidates autorisées par les demandes utilisateur ; aucune intervention DB ou publique.

## Analysis

La capture FILTRON explique les fonctions des clapets et le maintien du passage d'huile. Elle n'établit pas la chaîne by-pass ouvert en permanence → lubrification insuffisante → perte de puissance, ni un bruit de démarrage attribuable automatiquement au filtre. Un principe technique avait été transformé en diagnostic.

Les deux pages FRAM historiques ont été consultées : [pression basse](https://www.fram.com/vehicle-maintenance-center/post/low-oil-pressure-causes-and-symptoms), sections Common Causes et Symptoms ; [by-pass](https://www.fram.com/vehicle-maintenance-center/post/the-role-of-the-oil-filter-bypass-valve-in-engine-protection), sections fonctionnement et défaillances. Elles évoquent des mécanismes possibles, mais ne justifient pas le classement groupé niveau/pompe/capteur « plus fréquent » du candidat. Le passage Sensor Issues répète celui sur l'huile contaminée : source composite à ne pas valider globalement. Pas d'archive FRAM nouvelle ni de pression chiffrée reprise.

Une recherche ciblée a identifié la [notice Renault Clio 5 phase 1 — témoins lumineux](https://www.user-manual.renault.com/fr/chapitre1-faites-connaissance-avec-votre-v%C3%A9hicule/temoins-lumineux). La capture native contient les passages pression huile et arrêt impératif ainsi que l'identité du modèle. L'alerte en roulant, ses accompagnements et les consignes sont conservés ensemble. La conduite à tenir ne constitue pas une preuve de causalité du filtre.

## Correction proposée

- Corps, FAQ et deux blocs structurés : retrait des fréquences non établies et de l'attribution automatique perte de puissance/bruit au filtre. Consigne Renault explicitement limitée au contexte de la notice ; orientation vers la notice propre au véhicule et la recherche de cause.
- Deux relations historiques conservées : mêmes symptom_slug, system_slug, relation_to_part et sources. part_role explicite le statut hypothétique ; confidence devient low, reviewed=false et diagnostic_safe=false restent inchangés. Ces liens ne sont pas validés. Aucun symptôme ou identifiant DB créé.
- Ancien claim filtre-huile-bypass-huile-non-filtree retiré avec sa généralisation ; retrait non comptabilisé comme preuve acquise. Deux nouvelles affirmations distinctes portent sur la consigne et le niveau normal dans la notice Renault.
- Une capture RAW ajoutée par le runner existant, avec domaine et besoin candidats, sans modification du collecteur. Inventaire, checksums et lineage régénérés nativement. Licence inconnue/niveau2/CAPTURED_NEEDS_REVIEW : usage interne seulement.

Archive : sources/auto-captures/filtre-a-huile/user-manual-renault-com-wl-filtre-a-huile-alerte-pression-re-a64b110a.md. SHA256 fichier complet : fc3dc89072596e51a15b1520f44c9b74f8180379a0eeb957ebb5de0fa2349235. Source catalogue : renault_clio5p1_alerte_pression_huile, active signifie archive disponible, pas relation diagnostique validée.

## Validation

Frontmatter, catalogue source, calcul natif 0.46 et carte structurelle : PASS sur le candidat final. Une ancre nouvelle trop longue a été rejetée puis raccourcie à un extrait de la même phrase ; les conditions restent intégralement dans le corps. Le schéma n'a pas été assoupli.

Carte : 14 → 15 déclarations, 8 → 10 captured, 6 → 5 pending_capture, 0 verified. Un retrait et deux ajouts distincts expliquent ces variations. Zéro erreur d'ancre déclarée restante ne signifie pas exhaustivité des affirmations de la page.

Promotion native dry-run : BLOCKED, cinq proof_unavailable (trois ISO, deux UE) sous COVERAGE_STRICT_FAIL, et SUBSTANCE_SCORE 0.46 < 0.85. Shadow 89 → 90/tier S avec reality manifest stale : aucune qualité réelle ou performance SEO démontrée par cette note.

RAW I/J PASS ; trois archives présentes dans le snapshot de promotion et vérifiées par leurs octets. Toutes les anciennes entrées de checksum de fichiers sont inchangées, une ajoutée ; l'horodatage de génération est mis à jour par le générateur. Identifiants et barrières diagnostiques conservés ; exports/review_status inchangés. Diff whitespace WIKI/RAW PASS.

232 tests ciblés du lot proof-gate non rejoués : aucun code, test ou dépendance changé, quatre empreintes du lot antérieur identiques. Ce sont des résultats antérieurs réutilisables ; les validations des données modifiées ont été exécutées ce lot. Ni CI complète ni navigateur ni DB ni contenu actuellement servi contrôlés.

## Verdict

PARTIAL_COVERAGE ; VALIDATED_FOR_SCOPE_ONLY pour la correction candidate, la capture et les contrôles décrits. Les relations causales restent non validées, les droits de réutilisation inconnus et la promotion bloquée. Restent le montage, la réutilisation, les preuves ISO/UE, l'exhaustivité et l'adéquation au rôle de page. Aucun commit/push/export/DB/déploiement/activation. Autres pages R et corpus non rescannés.
