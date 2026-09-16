# Consolidation des méthodes — 12 septembre 2026

Reprise : [[ledger/audit-trail/2026-09-12-editorial-pipeline-codex|rapport du chantier]].
Verdict : **PARTIAL_COVERAGE**. Périmètre code/contrats ciblé ; présence et enregistrement
ne prouvent pas des appels en production. Aucun chemin déclaré mort sur une simple absence
de grep. Propriétaire d'exécution = composant ci-dessous ; arbitrage canon = owner du dépôt.

## Décisions et ordre

| Méthode / propriétaire | Déclencheur réel et sortie | Statut étayé | Décision | Dépendance / effet concret |
|---|---|---|---|---|
| Ancien téléchargement dans `RagVideoManagementService` | Ancienne route vidéo désormais reliée au client RAW dans candidat | Retrait déjà préparé, types/tests acquisition verts | retirer, préparé | Listing/stream/delete/enrich conservés ; pas de retrait des autres fonctions vidéo |
| RAW `auto-capture-runner.py`, `capture_http.py` | CLI acquisition → reçus/blob/Gate J | Candidat testé, runtime non activé | conserver | Entrée commune texte/vidéo ; pas de producteur concurrent à ajouter |
| App `cleanup/apply`, `video/single` | Routes admin → RAW dans candidat ; main → RAG | Routes enregistrées ; tests Nest existants | migrer, préparé | Reçu RAW non retrievable ; anciens tests25 réutilisables |
| App PDF `AdminRagIngestController.apply` | UI `admin.rag.ingest.tsx` → extraction/LLM → `RagMdMergerService.merge` → sync SQL → event | Appel frontend + DI prouvés, fréquence runtime inconnue | migrer | Contourne RAW/WIKI et peut annoncer applied après erreur SQL ; contrat UI à adapter avant raccord RAW |
| `RagCleanupService.runCleanupBatch` | `cleanup/batch` dry/commit → dédoublonnage SQL | Route administrateur enregistrée | conserver sous examen | Maintenance ≠ acquisition ; ne pas détourner vers RAW ni supprimer sur son seul nom |
| `cleanup/sync-files` / `syncFilesToDb` | Route admin + PDF apply → fichiers miroir → SQL | Deux appelants démontrés | migrer | Autre entrée d'écriture ; retraits/fraîcheur du miroir ne prouvent pas l'état SQL |
| Sync WIKI→miroir | Cron shell → sync Python → fichiers + `.last-sync.json` | Cron présent, candidat14 tests | conserver | Détecte absents/sous-scope sans purge ; n'applique pas de tombstone |
| `build_exports_seo.py` | CLI approved-only → exports/seo | Candidat68 tests | conserver | Refus de snapshot incohérent avant écritures ; retrait aval reste nécessaire |
| RAG `wiki_ingester.py` | CLI manifest content/source_path → chunks/embeddings → ancienne classe ; `--cleanup` préfixe | Script callable, invocation opérationnelle non démontrée | à confirmer puis migrer | Contrat différent du manifest WIKI ; cleanup avant lecture peut détruire sur manifest absent ; ne pas exécuter |
| WIKI `rag.schema.json` | Manifest id/path/hash/classes/tombstone → lecteur déclaré wiki_ingester | Contrat publié, lecteur incompatible par inspection | unifier après décision canon | Chemin wiki singulier et classes v1 ne s'assimilent pas à exports/rag/v2 |
| RAG F5 `import_wiki_exports.py` | CLI Markdown frontmatter → v2, clé source/path/hash/chunk | Callable ; v2 absent dans inventaire précédent | conserver/corriger, préparé | Hash du corps vérifié ; UUID stable ; retrait des anciennes versions, reprise ; force-reembedding refusé |
| RAG `KnowledgeService.delete_document` | API/build plane + garde L5 → tombstone/fichier/index | Route et service présents ; mode d'appel effectif non mesuré | corriger, préparé | parent_id CRUD ≠ hash parent du pipeline ; utiliser source_path exact ; aucun succès si index non confirmé |
| RAG `index_retirement.retire_exact_objects` | Appelé par les deux consommateurs précédents | Utilitaire partagé candidat ; aucun endpoint/cron | unifier, préparé | Comparaison des propriétés exactes puis UUID ; borne200 avant suppression ; contrôle résidu ; pas de purge par texte |
| RAG `orchestrator.pipeline` | Documents → chunks, parent_id hash(path+content), source_uri chemin#section | Producteur défini ; fréquence d'exécution non établie | conserver identité / migrer entrée | Ne pas confondre source_uri avec URL d'origine ni parent_id avec id CRUD |
| R2 `R2EnricherService` | Execution registry → ExecutionRouter/ModuleRef → fichiers RAG → writer protégé | DI dynamique démontrée | migrer | R2 n'est pas mort ; conserver signature catalogue, remplacer l'origine par WIKI approuvé |
| R6 `BuyingGuideEnricherService` | Admin/internal + router dynamique → BuyingGuideRagFetcher → SQL guide | Appelants et DI démontrés | migrer | supplementaryFiles + confidence1.0 n'établissent pas une source validée |
| R8 `VehicleRagGeneratorService` | Route admin + R8 enrich si source absente → fichier miroir ou proposition selon mode | Appelants/DI démontrés | migrer | Génération de RAG persistante ; conserver alternative DB owned et ses30 tests, ne pas supprimer à l'aveugle |
| R7 BrandEditorial/enricher | DB curée → compose/gates/version/queue → contenu optionnel du hub | Chemins publics repérés, gate6 tests | conserver/corriger, déjà préparé | FAQ inventées retirées ; hard gate ne peut plus passer sur un score élevé |
| R1 slots et ressources | RPC slots → GammeResponseBuilder / cache maillage → route pièces | Reader actif dans code ; WIKI producer manquant | conserver reader, raccorder writer | Ne pas recréer ancien RAG→R1 supprimé |
| R3 projection/legacy | Reader projeté + canary ; corps de page encore legacy | Preuve service44 tests précédente | migrer rendu après invalidation | READY_FOR_RENDER ne prouve pas rendu projeté ; renderer à raccorder |
| SEO feeder | `triggerEntity` ciblé + discovery/cron gamme, queues existantes | Providers/jobs enregistrés ; flags runtime non vérifiés | conserver puis unifier scope | Le nom R1 ne signifie pas que la découverte ne parcourt que R1 ; rôles autorisés propres à l'entité |
| SEO write/refresh processors | write result → singleton refresh → RPC MV globale | Appels explicites dans code | migrer vers outbox canon | Aucun hash/diff/rôle transmis au refresh courant ; ne pas ajouter un deuxième scheduler |
| `__rag_change_events` | Outbox canonique de refresh ciblé | DB : 554 événements historiques, aucun pending, derniers11 avril ; aucun émetteur/lecteur repéré dans src actuel | conserver et reconnecter | Colonnes source/oldhash/newhash/roles, pas entity_id ; new_hash NOT NULL ; représentation du retrait à définir |
| R9/G* | Enum legacy, affichage déprécié, operating matrix et assertions de rejet | Appels résiduels de compatibilité ; 74 tests verts de deux suites | conserver compatibilité, pas réactiver | La gouvernance est G* ; pas de route publique R9 ni de générateur à ajouter |
| knowledge-jobs | Timer utilisateur existant vers service commun | Lecture list-timers seulement | conserver, hors mutations | Aucun changement de service, planification ou droits Hermes |

Ordre : (1) consolidations locales index/retraits présentes dans ce lot ; (2) représentation
canonique retrait/outbox et identité inverse WIKI/export/entité/rôle, avec revue de signature
writer selon ADR-090 ; (3) raccorder aux queues existantes et re-filtrage des rôles ; (4) fermer
les écritures concurrentes PDF/sync/R2/R6/R8 en migrant leurs appelants ; (5) terminer WIKI→R1,
WIKI→R7 et rendu R3, puis vérifier les parcours visibles des six rôles publics. Les différences
R1 navigation, R2 transaction, R3 intervention, R6 choix, R7 marque, R8 véhicule sont conservées.

## Preuves et limites du lot retraits

- Baselines : f5-replacement-baseline.log (4 échecs), native-withdrawal-baseline.log
  (3 échecs), native-identity-baseline.log (3 échecs révélant l'identité réelle),
  f5-hash-baseline.log (1 échec). Ce sont des étapes successives, pas11 défauts distincts.
- `retirement-sdk-guards-tests.log` : **54 PASS**, exit0 ; deux avertissements de
  dépréciation Pydantic/Authlib. Fixtures index en mémoire, fichiers temporaires,
  construction de filtre SDK réelle, gardes L5 natives. Pas de serveur Weaviate ni de HTTP/UI.
- `r9-deprecation-tests.log` : **74 PASS**, exit0, deux suites ; tous les cas ne sont pas R9.
- `retirement-diff-check.log` : exit0. Patch cumulatif : `rag-retirement.patch`.
  `rag-consumption.patch` est conservé comme ancien jalon, pas remplacé.
- API SDK consultée : [suppression Weaviate](https://docs.weaviate.io/weaviate/manage-objects/delete).
  Le candidat évite les suppressions par filtre textuel : égalité tokenisée ≠ identité exacte.
- `outbox-schema-inventory.json` : SQL SELECT de métadonnées et agrégats uniquement,
  projet massdoc vérifié précédemment. 547 done/append_only,5 done/enrich_write,2 skipped.
  L'absence récente d'événements est un constat, pas une preuve générale de code mort.

Les retraits WIKI ne sont **pas** encore propagés à tous les consommateurs. Le F5 remplace
les versions admises dans son index ; le retrait admin natif traite sa collection/son chemin.
Le miroir, SQL __rag_knowledge, anciens préfixes/classes, SEO versions/caches/MV et rendu R*
restent non couverts par cette invalidation. L'approbation et la monotonie du snapshot WIKI
restent une condition d'activation. Aucun export incomplet ou rejeté ne vaut retrait.

L'outbox demande une décision concrète de représentation : identité d'entité hors gamme,
absence de new_hash lors d'un retrait, portée des rôles et source_commit/snapshot approuvé,
rejeu d'une annulation/remplacement. Les types SQL et le texte canon ne suffisent pas à
inventer ces valeurs. Ce rapport prépare ces écarts ; il ne modifie ni canon ni schéma.


## Identités de blocs et provenance par fiche — lot complémentaire

**Conserver** le mapper existant et ses identifiants pour les exports non ambigus.
**Corriger** son appel dans writeEntity : les doublons d'identifiant sont détectés
avant toute écriture de l'entité concernée ; mêmes lignes réutilisées dans writeBlocks.
**À confirmer** : jonction source_refs/sources/source_ids, stabilité des IDs positionnels,
renommages, collisions avec d'anciennes lignes DB et propagation de retrait inter-runs.
Aucun changement de format ou génération automatique de suffixes. Le commit de chaque
fiche est informatif ; plusieurs commits sont légitimes dans le même lot WIKI.
Détails : [[ledger/audit-trail/editorial-pipeline-evidence-20260912/withdrawal-outbox-design|proposition de filiation, section9]].


## Cause amont de collision R8 identifiée

**Conserver** les quatre contenus Scénic II par moteur/carburant. **Corriger** le
mapper applicatif existant pour utiliser usefulness_target dans l'identité R8.
**Ne pas retirer** ces contenus comme doublons de section. **À confirmer avant
livraison** : compatibilité des identités, rejeu historique et ordre du rendu R8.
Voir [[ledger/audit-trail/editorial-pipeline-evidence-20260912/editorial-duplicate-findings|audit des doublons réels]].
