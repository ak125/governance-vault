# Audit R3 — diagnostic integre et controles de role, 13 septembre 2026

## Scan

Lot cible sur le validateur PageRoleValidatorService, son raccordement dans ConseilQualityScorerService.auditGamme, le contrat PriorityFix et les tests de service/parcours HTTP. Les cinq fichiers du lot sont enumeres dans r3-section-role-coverage.json. AdminModule importe deja SeoModule, qui exporte le validateur : pas de nouvelle infrastructure ni de service parallele.

## Analysis

Le validateur R3/conseils demandait encore NO_LINK_TO_R5 et appliquait un vocabulaire exclusif a la page entiere. Cela contredisait l'integration des details R5 dans R3/S2_DIAG prevue par ADR-027. En outre, exposer une erreur dans le rapport sans la raccorder aux sections a ameliorer aurait laisse la boucle sans action correspondante. L'ancre et les redirections constituent un lot distinct, documente dans le rapport de cycle de vie.

## Correction (proposee et preparee dans le candidat autorise)

La demande obsolete de lien R5 est retiree ; le controle R4 demeure. validateR3Sections exige une URL R3/conseils et valide les sections ordinaires avec le controle R3 existant. Seul S2_DIAG reutilise les controles diagnostiques existants, y compris les interdits commerciaux et proceduraux. La page conserve le role R3. Une faute de type S2_DIAGNOSTIC ne recoit aucune exemption. Les autres consommateurs du validateur global ne recoivent pas d'exemption lexicale generale.

L'audit calcule cette validation sur les sections enregistrees et restitue roleValidation.scope=stored_sections. Les erreurs rendent canSkip faux et ajoutent role_violation aux priority_fixes ainsi que les sections concernees a sections_to_improve. Une erreur globale non attribuable conserve toutes les sections ordinaires pour revue ; elle ne designe pas arbitrairement une section. Le resume porte role_review. Aucun score stocke ni poids numerique n'est modifie. Aucune page R5 n'est creee et aucun contenu n'est supprime.

## Validation

135 tests PASS dans sept suites : validateur historique, dix cas de validation par section, parcours HTTP R3, doublons, sources, scorer et backfill. Les cas couvrent diagnostic autorise dans S2_DIAG, diagnostic refuse ailleurs, faute de type, pollution commerciale/procedurale, maintien du controle R4, retrait de NO_LINK_TO_R5, URL de guide achat refusee, restitution des erreurs et maintien de S2_DIAG dans les travaux. Le parcours HTTP instancie le vrai validateur avec le client Supabase installe et un transport memoire GET ; aucune base partagee n'est appelee.

ESLint des cinq fichiers : exit 0 et journal vide. Diff check de travail puis staged : PASS. HEAD candidat 0c31807c8453c251d70c7575eafcc973f04eed14 ; origin/main releve apres fetch 466cc15ce9b385a61503cc0224f40bec700ec41a. Aucun changement upstream dans les fichiers existants de ce lot depuis ce HEAD ; cela ne certifie pas une integration globale. Les preuves sont r3-section-role-tests.log, r3-section-role-lint.log et les deux patches. Le patch incremental compare les snapshots pris avant ce lot ; le patch candidat comprend aussi les modifications anterieures des memes fichiers. Aucun test rouge avant correction n'est revendique pour ce lot.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour le chemin d'audit des sections R3 enregistrees ; PARTIAL_COVERAGE pour la demande globale. Ces controles lexicaux ne valident pas la verite des faits, les sources, la structure du tableau, l'ancre ni le HTML publie. validatePageWithHtml et les consommateurs globaux de forbidden-overlap restent sans distinction par section. Typecheck global, CI, base partagee et deploiement non executes. La collecte de sources utiles, les structures des autres roles et l'inventaire exhaustif des destinations restent ouverts.
