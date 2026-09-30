# ISO pilote — 14 septembre 2026

## Scan

PARTIAL_COVERAGE. Trois mentions ISO du candidat `gamme:filtre-a-huile`, leurs déclarations de couverture, le bloc structuré `standards_norms` et la voie de capture native. Périmètre candidat uniquement, autorisé par les demandes de correction et de continuation de l’utilisateur. Manifest détaillé : iso-pilot-coverage.json.

## Analysis

Les notices officielles permettent de borner les objets d’essai. Elles ne contiennent pas de résultats propres à une référence de filtre. L’ancienne phrase « caractéristique normalisée » et le raccourci bêta du bloc structuré excédaient les preuves consultées.

Sources consultées le 14 septembre 2026, sans lecture du texte intégral payant :

- [ISO 4548-2:1997](https://www.iso.org/standard/21712.html) : titre et métadonnées de la méthode relative au clapet de dérivation ; notice indiquant une confirmation en 2024.
- [ISO 4548-9:2008](https://www.iso.org/standard/44520.html) : résumé et métadonnées, essais d’anti-retour lorsque présents sur les filtres visés. Le résumé indique 2007, alors que le titre et les métadonnées indiquent 2008 : incohérence de notice conservée dans les notes, sans inventer une édition. Révision annoncée ; projet non traité comme norme publiée.
- [ISO 4548-12:2017](https://www.iso.org/standard/62763.html) : résumé de l’essai multipasse en régime stable, qui exclut les variations de débit. Révision annoncée. Aucun chiffre de performance ou intervalle d’entretien déduit.

La recommandation de demander des résultats et conditions comparables est une conséquence éditoriale, pas un résultat d’essai ni une citation normative.

## Correction proposée

Dans WIKI : section lisible consacrée aux normes, suppression des mentions dispersées ambiguës, bloc structuré aligné, trois notices distinctes au catalogue et ancres correspondantes. L’entrée historique de série reste pour les relations diagnostiques non qualifiées. Aucun symptôme, classement OE/OES, montage ou URL publique modifié ce lot.

Dans le candidat RAW : trois besoins ciblés de capture, un domaine ajouté à l’allowlist native, niveau 2/licence inconnue/WIKI seulement. Type existant `technical_datasheet` utilisé pour les notices publiques de métadonnées, sans créer une taxonomie ou un collecteur concurrent. Aucun changement du runtime.

La première tentative native reçoit HTTP403. Aucune archive créée, aucune méthode de contournement essayée ; les deux autres notices ne sont pas tentées après ce refus. La consultation web de l’agent ne remplace pas la capture RAW : sources `to_capture`, trois déclarations ISO `pending_capture`. Le journal natif du refus reste joint.

## Validation

- Schéma de proposition et calcul natif 0.46 : PASS.
- Trois ancres ISO : présentes dans leur section ; erreurs globales de rattachement 6 → 3. Ce résultat mesure la cohérence du texte, pas sa validation factuelle.
- Carte inchangée en disponibilité des preuves : 14 déclarations, 8 captured, 6 pending, 0 verified. Les trois erreurs restantes concernent le diagnostic et OE/OES.
- Schéma des trois notices PASS ; raw_ref natif sans erreur, car `to_capture` est explicitement ignoré par ce contrôle. Ce PASS n’est pas une archive validée.
- Gates RAW I et J PASS. Deux archives équipementier antérieures inchangées par SHA ; aucune nouvelle capture.
- 197 tests du précédent lot non rejoués : aucun code/test/dépendance changé ; empreintes du validateur, de ses tests et de requirements identiques. Contrôles des données modifiées rejoués.
- Protections de proposition, exports false et relations diagnostiques non approuvées conservées à l’identique.

## Verdict

PARTIAL_COVERAGE ; VALIDATED_FOR_SCOPE_ONLY pour la structure et les états vérifiés. Promotion native BLOCKED : COVERAGE_STRICT_FAIL et SUBSTANCE_SCORE. Score expérimental 89/tier A inchangé, six page_unproven et reality manifest stale. Ne pas attribuer le blocage à un contrôle de preuve absent des motifs retournés : la solidité de cette barrière indépendamment du score doit encore être éprouvée.

Aucun commit, push, export, DB, déploiement ou activation. Restent : capture licite des notices, assertions OE/OES et diagnostic, montage/réutilisation, contenu servi et fiabilité générale des scores. Les autres propositions et le corpus de 7 000 contenus n’ont pas été rescannés.
