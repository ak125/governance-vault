# Consommation, retrait, calibration et rendu — preuves bornées

## Scan

Importeur natif RAG `scripts/importers/import_wiki_exports.py`, modèle strict
`app/models/wiki_frontmatter.py`, fixtures/tests F.5 ; miroir applicatif
`scripts/rag-sync/sync-wiki-exports-to-rag.py` et freshness service ; décision et
service R3 ; scorer natif WIKI et fixtures de qualité. Aucune connexion DB,
aucune purge, aucun export/promotion. RAG main distant vérifié au commit1dfea97.

## Analyse

1. **Corps perdu par l'importeur RAG — prouvé, correction isolée.** Le parser
   renvoyait seulement les métadonnées. La boucle insérait `meta.body` ou une chaîne
   vide alors que `body` est interdit par le schéma strict. Deux contre-épreuves
   échouaient : corps réel perdu et export vide accepté. Le commentaire promettant
   une chaîne d'embedding applicative ne correspondait pas à l'appel `data.insert`.
   Une vectorisation éventuelle dépend de la collection déployée, non inspectée ici.
2. **Retrait et remplacement ne se propagent pas — prouvé sur fixtures.** Après
   retrait d'un export parmi deux, le miroir garde son fichier et avance synced_at.
   Le freshness service ne déduit sa santé que de l'âge du timestamp. Dans la vraie
   boucle d'import avec index mémoire simulé, une nouvelle version crée un second
   objet ; après retrait du fichier, les deux restent présents sans erreur.
   Cette preuve ne donne ni le nombre ni l'état des objets en base réelle.
3. **La note mesure surtout une forme — corpus de caractérisation.** Explication
   courte sans rubriques ajoutées0,56 ; toutes rubriques sans lien0,80 ; tout rempli
   avec labels medium0,84 ; paragraphes répétés avec références high et lien résolu1,00.
   Une contradiction textuelle ou une procédure sans passage probant ne modifie pas
   cette arithmétique. Il ne s'agit PAS d'une preuve de promotion indue : le décideur
   compose ensuite d'autres gates. Les six fixtures natives examinées confirment
   deux cas positifs sans échec et quatre cas invalides rejetés (source inconnue,
   confiance surévaluée, relation à la pièce absente, entretien manquant).
4. **R3 n'a pas encore de renderer de projection — limite contractuelle confirmée.**
   READY_FOR_RENDER signifie DTO prêt, et servedBodySource reste legacy. Les44 tests
   des services R3 confirment le comportement, le repli entier, le ciblage rôle+entité,
   le bypass de cache pour la canary et le cache legacy. Aucun article du candidat
   WIKI n'est donc présenté ici comme rendu. Le généraliste #86 n'est pas à transformer
   en procédure R3 pour remplir les rubriques du scorer.

## Correction préparée et choix proposés

- Import RAG : parser en une lecture métadonnées ET corps ; valider les métadonnées
  inchangées ; refuser le corps vide avant la recherche d'idempotence ; transmettre
  le Markdown réel à l'insertion. Compatibilité du parser metadata-only conservée.
  Checkout isolé `/home/deploy/worktrees/rag-editorial-consumption-20260912`, base1dfea97.
- RAW : identité `manifest_id` explicite des nouvelles captures HTML, scanner avant
  écriture, refresh natif y compris au rejeu ; reçu existant du même item permet de
  reprendre sa worklist, et échec de cette mise à jour retourne un code non nul.
  Aucun ancien frontmatter RAW réécrit. La déduplication HTML inter-URL historique
  reste fondée sur le contenu ; elle n'est pas une déduplication sémantique des faits.
- Retrait : étendre le chemin canonique existant par un rapprochement d'inventaires
  WIKI et dérivés, avec version/source/entity/role/claim concernés. L'absence d'un
  fichier dans un export partiel ou raté ne peut pas autoriser un retrait. Il faut
  d'abord une preuve de snapshot source complet et une liste explicite des dérivés
  gérés ; les fichiers legacy du miroir ne possèdent pas tous cette attribution.
  Préparer le différentiel en lecture seule ; conserver les versions sources ;
  invalider seulement les dépendances des faits effectivement utilisés. Ne pas
  confondre source inutilisée et source d'un passage retenu.
- L'index doit cesser de servir une version retirée/supplantée sans supprimer RAW
  ni l'historique WIKI. Un remplacement doit qualifier le nouveau contenu et son
  index avant bascule, avec reprise après erreur. Éviter `force-reembedding` comme
  réparation des objets vides : il insère un nouvel objet sans réparer l'ancien.
  La mutation des objets existants attend leur inventaire réel et un lot nominatif.
- Calibration : conserver pour l'instant le seuil0,85 et le décideur natif. Faire
  évoluer le contrat canonique par usage éditorial, en réutilisant les profils de
  complétude existants et les gates de preuves, avant tout changement de poids.
  Exiger une matrice annotée article général/R2/R8/procédure/diagnostic/choix, avec
  positifs et négatifs, et mesurer séparément faux refus de substance et blocages
  source/risque/provenance. Aucun bonus artificiel de rubrique, lien ou source clonée.
- R2 et R8 : préserver identité catalogue et catalog_signature. Le partage d'un fait
  est légitime ; la répétition d'un texte général ne prouve aucune spécificité.
  La différence doit porter sur compatibilité/références disponibles pour R2 et
  identité/contexte véhicule pour R8. Les30 tests R8 déjà verts sont inchangés.
- Rendu : le prochain lot R3 doit suivre P2-R3-E (renderer Markdown→HTML, sanitization,
  remplacement atomique du BODY, repli observable, isolation du HEAD, même canary).
  Ni le service actuel ni ces tests ne permettent d'annoncer un rendu de projection.
  Choisir d'abord une fiche correspondant réellement au rôle et qualifiée/exportable.
  #86 reste bloquée ; une preview de son Markdown ne serait pas une preuve de parcours.

## Validation

`rag-body-baseline.log` : 2 échecs/1 succès avant ; `rag-body-tests.log` :25 tests PASS
après, parser/modèle natifs, index en mémoire. Python de test isolé, dépendances
consignées ; aucune dépendance applicative/runtime modifiée.
`consumer-withdrawal-probe.json` : retraits non propagés dans les fixtures.
`editorial-calibration-probe.json` :8 cas arithmétiques +6 fixtures qualité natives.
`r3-serving-proof.log` :44 tests PASS sur2 suites. Aucun navigateur/DB.
`raw-inventory-tests.log` :296 tests RAW PASS après l'extension inventaire/reprise.

## Coût et idempotence

Ce qui est prouvé : un rejeu identique de miroir évite une copie ; un rejeu identique
RAG évite une insertion après la recherche de clé naturelle ; le cache legacy R3
évite une seconde composition dans la fixture. Ce qui n'est pas économisé par la
réception RAW actuelle : le rejeu peut encore télécharger et inspecter la source
avant de constater le doublon. Aucun montant ni nombre de tokens économisés n'est
avancé : pas de télémétrie d'embeddings/LLM ou de contexte injecté sur le runtime.
Le timer knowledge-jobs et la modernisation restent hors de ces changements.

## Verdict et frontière de livraison

**VALIDATED_FOR_SCOPE_ONLY** pour les correctifs isolés ; **PARTIAL_COVERAGE** pour
le parcours. Les patches sont préparés et non livrés. Le retrait des versions déjà
servies, la modification d'un rendu SEO indexé, la promotion/export et l'activation
runtime restent des étapes distinctes. `CLAUDE.md` invariant9 demande un accord owner
nominatif pour SEO indexé ; invariant6 interdit la suppression automatique de pages.
Ces frontières ne remplacent pas le travail préparatoire : les critères de test,
contre-épreuves, risques et choix de reprise ci-dessus sont déjà disponibles.


## Complément : inventaire réel en lecture seule

La cible Supabase a été identifiée depuis le SUPABASE_URL du backend puis recoupée
avec le connecteur ; aucune clé n'a été affichée. Les tables entités/facts/versions/
blocs/runs de projection contrôlées contiennent **0 ligne**. Dans __rag_knowledge,
619 lignes, 0 corps vide, 502 avec retrievable=true. Parmi ces dernières :7superseded
et1merged ; les chemins SQL de lecture examinés filtrent aussi status=active.
Il s'agit d'une incohérence d'état documentée, pas d'une preuve de réponse chatbot
fondée sur ces8lignes. Les identités de ces8lignes ont été inventoriées sans lire leur corps.

Le schéma Weaviate de l'instance atteinte par rag-api-prod ne contient **pas**
KB_Knowledge_v2, cible obligatoire du nouvel importeur. Les collections observées
contiennent KB_Knowledge9945, Catalog7035, Diagnostic421 et Media176 objets.
Leurs vectorizers sont none ; ceci ne certifie ni présence ni validité des vecteurs
fournis par les autres producteurs. L'importeur F.5 doit donc être considéré comme
**non exécutable vers sa cible sur cet état**, et le correctif corps comme préventif
pour cette voie. Il ne faut pas attribuer ses défauts aux619 lignes SQL ni aux9945
objets legacy sans preuve de filiation.

La preuve WIKI→index→projection→rendu est bloquée par un état concret : ciblev2
absente, projectionDB vide, rendererR3 absent. La franchir nécessiterait des étapes
de migration/indexation/projection/activation distinctes et non effectuées ici.
Aucune mutation de l'instance n'a été faite. Voir runtime-consumer-inventory.json/sql.
