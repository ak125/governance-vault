# Choix et définitions OE/OES — 14 septembre 2026

## Scan

PARTIAL_COVERAGE. Candidat filtre-a-huile : section Marques & qualité, bloc structuré quality_tiers, deux déclarations de couverture, catalogue de sources et une demande de capture RAW. Corrections autorisées par les demandes de l'utilisateur, sans publication. Manifest : oe-quality-coverage.json ; patchs incrémentaux joints, travail staged antérieur préservé.

## Analysis

Le guide attribuait au règlement trois niveaux universels de qualité et classait globalement sept marques OE/OES. Ces formulations excédaient la preuve disponible.

- [Lignes directrices européennes, consolidation du 17 avril 2023](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX%3A02010XC0528%2801%29-20230417), consultation du 14 septembre : paragraphes 18-20, origine et qualité équivalente. Le paragraphe 19 renvoie désormais au règlement 2018/858. La consolidation est documentaire ; les actes du Journal officiel font foi.
- [Règlement 461/2010, texte initial, article 5](https://eur-lex.europa.eu/legal-content/FR/ALL/?uri=celex%3A32010R0461) : restrictions de concurrence et conditions de l'exemption. Son objet ne permet pas de certifier toutes les références commercialisées par une marque. Aucune conclusion sur sa période actuelle d'application n'est tirée du texte initial.

L'absence de justification par référence est une conclusion de cette revue limitée, pas la preuve que les pièces d'une marque seraient de mauvaise qualité. La recommandation de demander des justificatifs est une conséquence éditoriale. Le passage MAHLE sur les différences internes selon moteur reste la preuve technique antérieure ; son archive est inchangée.

## Correction proposée

Corps et bloc structuré remplacent le classement par deux définitions bornées et des critères de vérification propres à la référence. Le nom interne quality_tiers est conservé pour respecter le contrat existant. Retrait de la liste globale des marques sans créer de nouveau classement.

| Ancienne déclaration | Disposition | Nouvelle déclaration |
| --- | --- | --- |
| filtre-huile-trois-niveaux-qualite-oe-oes-equivalent | Classement excessif retiré, non compté comme prouvé | filtre-huile-definition-piece-origine, §19 |
| filtre-huile-oes-droit-rechange | Ancien texte absent du corps, identité généralisée non démontrée ; retiré | filtre-huile-definition-qualite-equivalente, §20, affirmation distincte |

Catalogue historique rectifié et référence EUR-Lex 2023 ajoutée sans confondre index de liens et archive primaire. Dans RAW candidat : un besoin et un domaine ciblés, type technique existant, niveau 2/licence inconnue, consommateur WIKI seulement. La capture native retourne fetch_failed:CaptureHTTPError:unsupported_mime. Aucune archive créée, aucune tentative alternative de contournement. Les deux nouvelles déclarations restent pending_capture, source to_capture et hash null. Aucun droit de réutilisation publique qualifié.

## Validation

- Frontmatter et calcul natif 0.46 : PASS. Deux entrées catalogue conformes au schéma ; statuts et hash absent cohérents.
- Deux ancres de cette section présentes. Le contrôle structurel global reste FAIL avec une ancre diagnostique, contre trois auparavant. Ce gain de cohérence ne signifie pas acquisition de preuve.
- Carte : 14 déclarations, 8 captured, 6 pending_capture, 0 verified. Deux déclarations retirées et deux distinctes ajoutées, aucune nouvelle capture.
- Promoteur natif, dry-run : BLOCKED. Six proof_unavailable et une ancre absente sous COVERAGE_STRICT_FAIL ; SUBSTANCE_SCORE 0.46 < 0.85. Score expérimental 89/tier A, reality manifest stale. Le score ne lève pas ces refus.
- RAW gates I/J PASS ; deux archives existantes vérifiées par SHA. Demande EUR-Lex reste TODO.
- Les 232 tests du lot proof-gate sont une preuve antérieure réutilisée, non rejouée : ce lot ne change aucun code, test ou dépendance ; quatre empreintes enregistrées dans la preuve précédente sont identiques. Les contrôles natifs ont été rejoués sur les données modifiées. Aucun test de classement Google ou de contenu servi.
- review_status, confidence_score, exportable et diagnostic_relations inchangés ; aucune approbation attribuée. Diff whitespace WIKI/RAW PASS.

## Verdict

PARTIAL_COVERAGE ; VALIDATED_FOR_SCOPE_ONLY pour les corrections candidates, leur structure et les contrôles exécutés. Le guide reste bloqué. Restent : preuve RAW européenne/ISO, qualification diagnostique, montage/réutilisation et exhaustivité du guide. Autres pages R et corpus non rescannés ce lot. Aucun commit, push, export, DB, déploiement ou activation.
