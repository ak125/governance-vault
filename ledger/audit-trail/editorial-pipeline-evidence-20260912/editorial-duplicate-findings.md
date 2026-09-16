# Doublons et collisions éditoriales — vérification du corpus

12 septembre 2026. PARTIAL_COVERAGE. Preuve ponctuelle utilisant les producteurs
et le mapper natifs ; aucun scanner runtime, registre ou scheduler ajouté.

## Scan

Deux checkouts vérifiés au même HEAD WIKI `01cea8deda48d84b6a2993cd4bdefe8280082c0b` :
`/opt/automecanik/wiki-auto-validation` et le candidat
`/opt/automecanik/wiki-editorial-qualification-20260912`. Ce HEAD correspond à main
vérifié par git ls-remote. Ces deux copies ne constituent pas deux corpus indépendants.

Par checkout : **3 exports SEO existants, 9 fiches WIKI, 15 propositions métier**.
Deux autres documents sous proposals sont exclus explicitement : index de navigation
et brief qualité des sources. Au total,58 fichiers lus et hashés sur les deux copies,
54 enregistrements métier/export examinés. Comparaison des identifiants uniquement ;
ni audit sémantique complet de la prose, ni vérification factuelle des affirmations.

Les exports JSON sont lus sans modification. Pour les fiches/propositions, seul le
transformateur natif `_extract_facts_sources_blocks` est utilisé en mémoire ; l'éligibilité
est relevée séparément. Aucun export écrit, aucune approbation ou promotion effectuée.
Le script de preuve JS charge directement `mapExportBlockToDbBlock` depuis le candidat
TypeScript via ts-node ; il n'instancie pas de writer ou de connexion DB.

Preuves : `editorial-identity-inputs.json` (inventaire/hashes/entrées),
`editorial-identity-corpus.json` (avant), `editorial-identity-corpus-after.json`,
`editorial-identity-comparison.json`. Deux index sans frontmatter apparaissaient comme
erreurs de parsing dans le premier relevé ; leur statut documentaire a été contrôlé,
puis ils ont été exclus nominativement avec le brief qualité. Aucun échec métier masqué.

## Analysis : résultat réellement observé

**Aucune collision d'identifiant dans les 3 exports existants ou les 9 fiches WIKI
contrôlés.** Ils ne portent toutefois que2 blocs structurés chacun par checkout : ce
constat n'est pas une certification du site ou de tous les anciens contenus.

**Deux collisions logiques dans la proposition `proposals/renault-scenic-ii.md`**, présentes
à l'identique dans les deux checkouts. Statut source `proposed`, non éligible à l'export.

| Section | Deux périmètres présents | Diagnostic |
|---|---|---|
| known_issues | engine_family:f4r et engine_family:k9k | Textes différents, même ancien block_id |
| maintenance | fuel:diesel et fuel:essence | Textes différents, même ancien block_id |

Ces quatre blocs sont des contenus distincts à conserver. Les supprimer ou fusionner
leurs textes au titre de doublons aurait perdu la séparation métier entre moteurs.
Le couple « Symptômes/symptomes » était une fixture de test, pas le doublon réel identifié.
Aucun doublon exact de texte dans un même rôle porté par des identifiants distincts
n'a été relevé dans cette projection structurée du corpus. Cela ne mesure pas la
similarité sémantique, les formulations voisines ou le texte non projeté.

Cause : `_map_vehicle_to_blocks` transmet déjà la clé moteur dans `usefulness_target`,
avec une section partagée. Le mapper applicatif conservait cette clé dans content,
mais l'ignorait dans l'identité du bloc. Le contrôle préparé précédemment refusait
alors les collisions ; il ne permettait pas encore de conserver les quatre blocs R8.

## Correction proposée et préparée dans le candidat

Le mapper existant inclut désormais la clé `usefulness_target` dans l'identité dérivée
**pour R8 seulement**. C'est l'axe déjà fourni par WIKI, prévu par ADR-086 §4, et non un
compteur ajouté pour faire disparaître le conflit. La clé est encodée sans perte avec
encodeURIComponent pour préserver les séparateurs de l'identité. block_kind, contenu,
sources et truth_level ne changent pas. Les autres rôles, R8 sans axe et block_id
explicitement fourni conservent leur identité. La garde de collision reste active.

Exemple dérivé du cas réel :
`vehicle:renault-scenic-ii#R8_VEHICLE#known-issues#engine_family%3Ak9k`.
Changer le texte ne change pas l'identité ; déplacer un bloc natif R8 muni de sa
section et de son axe ne la change pas non plus. Deux contenus sur la même section
et le même axe restent ambigus et ne doivent pas être acceptés comme deux versions
actives simultanées dans un même export.

Quatre fichiers app modifiés ce lot ; pipeline candidat **1.1.0**, signature publique
inchangée. La convention d'identité R8 évolue : elle doit être revue avant livraison
selon ADR-090 §A. Ni schema SQL ni contrat d'export WIKI ni corpus modifiés.
Patch cumulatif : `application-r8-scope.patch` ; anciens patches conservés.

## Validation

- Baseline :3 tests échouaient,41 passaient avant correction (`r8-scope-baseline.log`).
- Candidat : **53 tests PASS/3 suites**, lint4 fichiers et tsc backend PASS.
  Voir `r8-scope-final-tests.log`, `r8-scope-lint.log`, `r8-scope-typecheck.log`.
- Le test d'écriture simulée conserve4 versions/4 identifiants, puis le rejeu en ordre
  inverse produit0 nouvelle version. Aucune DB sollicitée par ces tests.
- Même corpus, mapper corrigé :0 collision retrouvée, même nombre de blocs ;58 hashes
  de fichiers sources recontrôlés sans changement. Les quatre contenus Scénic restent
  présents, leurs identités sont détaillées dans la comparaison JSON.
- Contrôle Supabase séparé, SELECT de compteurs uniquement : **0 ligne dans
  __seo_content_blocks et0 dans __seo_content_block_versions** au moment du relevé.
  Aucun bloc R8 enregistré dans ces deux tables. Preuve : `r8-projection-db-counts.json`.

## Verdict et limites

PARTIAL_COVERAGE. Défaut confirmé dans le mapping d'une proposition réelle et correctif
isolé vérifié ; aucun écrasement constaté dans les deux tables de projection contrôlées.
Ce constat ne couvre pas les anciens producteurs RAG, caches, autres bases ou pages
publiques. Pas de navigateur, de CI nouvelle, de migration ou de déploiement.

Les migrations/RPC relues traitent block_id comme clé opaque et ne limitent pas à un
bloc par entity/role/block_kind. Aucun parsing par split de block_id repéré dans le
périmètre applicatif ciblé. Cela ne certifie pas tous les consommateurs externes.
La RPC trie actuellement par rôle/kind ; un ordre entre plusieurs axes de même kind
n'est pas garanti et reste à définir lors du raccordement R8 au rendu. Aucun SQL live
modifié. Les anciens identifiants éventuels, leurs versions de replay et les chemins
legacy doivent être réconciliés avant activation ; les deux tables contrôlées sont
actuellement vides. Les retraits WIKI→outbox→consumers restent un lot distinct ouvert.


## Complément autorisé « corriger » — compatibilité historique

Scan ciblé du writer, de son test, du reader/RPC et du chemin véhicule public.
Le rendu public examiné ne consomme pas cette projection ; aucun ordre d'affichage
public n'est modifié dans ce lot. L'ordre SQL entre axes reste un point du futur
raccordement R8, pas une raison d'ajouter un tri à un chemin sans consommateur.

Analysis : le nouvel identifiant pourrait coexister avec un ancien identifiant actif
sans axe lors d'un rejeu sur une base déjà alimentée. Les tables vides relevées au lot
précédent ne constituent pas une garantie pour chaque environnement ou futur rejeu.

Correction autorisée, réalisée dans le candidat : un SELECT groupé des anciens
identifiants R8 dérivés précède toute écriture de facts/blocs de l'entité. Un ancien
bloc actif impose une réconciliation explicite ; une erreur de lecture bloque aussi
l'écriture. Les ID explicites et les rôles non sélectionnés restent hors de ce contrôle.
Aucun retrait automatique ou renommage historique n'est effectué. Le mécanisme de
signalement des erreurs du writer existant reste utilisé.

Validation : **58 tests PASS / 3 suites**, dont deux nouveaux contre-exemples en échec
avant la protection. Le client Supabase réel est aussi exercé avec transport HTTP
simulé : réponse contenant l'ancien bloc actif et réponse 503, uniquement des GET,
aucune mutation transmise. Lint des deux fichiers modifiés, tsc backend et diff-check
PASS. Le mapper natif est rejoué sur les entrées sauvegardées : même sortie, zéro
collision ; les 58 hashes sources sont revérifiés inchangés.

Preuves : `r8-legacy-baseline.log`, `r8-legacy-tests.log`, `r8-legacy-lint.log`,
`r8-legacy-typecheck.log`, `r8-legacy-verification.json`,
`editorial-identity-corpus-final.json`. Patch cumulatif courant :
`application-r8-legacy.patch` ; `application-r8-scope.patch` conservé comme état antérieur.

Verdict : VALIDATED_FOR_SCOPE_ONLY pour les tests du correctif ; PARTIAL_COVERAGE pour
le chantier global. Le SELECT préalable n'est ni une migration transactionnelle ni
une protection contre un ancien writer concurrent. Avant activation, déployer une seule
version du writer et réconcilier explicitement toute identité historique signalée.
Pas de DB réelle écrite, de migration exécutée, de commit, push, merge ou déploiement.
