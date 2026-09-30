# Audit R3 — titres et paragraphes dupliques, 13 septembre 2026

## Scan

La demande est de poursuivre l'amelioration des controles existants en respectant le cycle de vie des pages. Le lot suit le chemin deja cable GET /api/internal/seo/audit/r3/:pgId -> ConseilQualityScorerService.auditGamme -> KeywordPlanGatesService.auditFromSections -> GA3_CROSS_SECTION_DEDUP -> sections_to_improve / shouldSkipGamme. Lectures ciblees consignees dans r3-heading-dedup-coverage.json ; aucune exploration exhaustive de toutes les pages n'est revendiquee.

## Analysis

L'audit lisait le corps et le type de section, mais pas sgc_title. GA3 cherchait des paragraphes identiques en minuscules, sans la normalisation canonique des accents. Ainsi Symptômes et symptomes dans deux titres ne pouvaient pas etre compares. Cinq tests de regression nouveaux echouent avant correction ; vingt tests de ces deux suites passent deja. Ce sont des contre-exemples controles, pas une mesure de prevalence dans le corpus public.

Autre constat, distinct et non corrige dans ce lot : PageRoleValidatorService demande encore NO_LINK_TO_R5 et reserve des termes de diagnostic a R5. Le contrat R3 declare pourtant S2_DIAG integre selon ADR-027, tandis que forbidden-overlap conserve certains interdits R5 sur R3. Cette contradiction exige une validation tenant compte des sections ; aucune exemption globale de vocabulaire n'a ete introduite. Les anciennes pages R5 ne doivent pas etre recreees pour satisfaire une alerte obsolete.

## Correction (proposee et preparee dans le candidat autorise)

Quatre fichiers applicatifs : le scorer selectionne et valide sgc_title, le transmet au gate et restitue le titre avec l'identifiant de ligne ; GA3 compare les titres declares et les paragraphes avec normalizeSeoText existant de @repo/seo-roles. Aucun nouveau moteur de score ni seuil de similarite. Le gate conserve warn, les deux sections deviennent a examiner et shouldSkipGamme reste faux meme avec des scores de 100. Le contenu et les scores stockes ne sont pas modifies.

Les titres ne sont pas extraits du sommaire ni des libelles de navigation. Une egalite de titres est un signal de revue, pas une preuve que tout le texte est identique. Les titres absents ou differents ne sont pas assimiles a des doublons. Une colonne titre absente de la reponse complete provoque un echec observable plutot qu'un audit incomplet silencieux. S2 et S2_DIAG de meme titre sont signales comme deux sections existantes a examiner ; le cas teste n'appelle aucune creation.

## Validation

73 tests passent dans cinq suites : deduplication, parcours HTTP d'audit R3, sources, couverture des packs et backfill. Les requetes du parcours HTTP passent par le client Supabase installe avec transport memoire : GET uniquement, selection sgc_title verifiee, aucune base partagee appelee. Les tests couvrent accents composes/decomposes, casse, espaces, paragraphes normalises, titres distincts, donnees manquantes et decision de travail S2/S2_DIAG. ESLint : zero erreur, zero warning ; diff checks passent sur les fichiers du lot.

Preuves : r3-heading-dedup-before-tests.log, r3-heading-dedup-after-tests.log, r3-heading-dedup-lint.log. Le patch incremental isole ce tour ; le patch candidat inclut les changements precedemment autorises dans ces memes fichiers. Les 24 tests service R3 et 3 tests de rendu du lot ancre precedent restent des preuves distinctes, non reexecutees ici.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour ce controle du candidat ; PARTIAL_COVERAGE pour l'ensemble de la boucle. Ni deploiement, ni ecriture dans les contenus partages. La detection de paraphrases, la qualite factuelle, l'inventaire exhaustif des redirections, les revisions de pages servies et l'alignement des regles de vocabulaire par section restent ouverts. La modification ne garantit aucun classement Google et ne constitue pas une validation de publication.
