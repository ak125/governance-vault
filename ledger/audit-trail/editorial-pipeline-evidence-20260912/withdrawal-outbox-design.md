# Propagation des retraits — proposition technique non normative

Statut : REVIEW_REQUIRED pour le contrat ; PARTIAL_COVERAGE pour la chaîne.
Préparation isolée du 12 septembre 2026. Aucun schéma, événement réel, flag,
queue de production ou contenu publié modifié. Ce document ne crée pas de canon.

## 1. Scan : mécanismes et limites vérifiés

L'outbox existante `__rag_change_events` reste le journal de changements et
`__seo_projection_runs` le registre de runs. Les deux queues projection-write et
projection-refresh restent les transports ; aucun second scheduler proposé.

L'inventaire SQL en lecture seule conservé dans `outbox-schema-inventory.json`
montre `rce_new_hash NOT NULL`, `rce_old_hash` nullable, aliases de gammes, rôles,
sections, statut, compteur jobs et erreur ; pas de colonne entity_id. Il recensait
554 événements historiques, aucun pending. Cela ne prouve pas l'absence de clients.

Les appelants applicatifs relus sont `SeoProjectionWriteProcessor.handle` puis
`SeoProjectionRefreshProcessor.handle` : après écriture, enqueue direct d'un
singleton avec triggeredBy/runId ; le consumer appelle la RPC globale de refresh.
Le commentaire BullMQ du fichier diffère des imports réellement utilisés
`@nestjs/bull` et `bull` : conserver cette pile, aucune migration de queue induite.
La matrice `method-consolidation.md` détaille les autres lecteurs et producteurs.

ADR-090 §A impose le registre de runs et le snapshot rejouable uniques ; §B/C1
impose outbox unique, ciblage, double whitelist, re-filtrage dans le processor,
dédup 60 min et breaker. Le frontmatter est accepted mais le corps conserve des
mentions draft/proposed : anomalie documentaire à résoudre au vault, pas licence
pour choisir une nouvelle règle. Référence :
[[ledger/decisions/adr/ADR-090-seo-projection-forward-writer-canon]].

## 2. Analyse : identité, contenu et ordre sont distincts

La cible proposée est une identité stable émise par le dépôt autoritaire ; le
mapping actuel doit encore être vérifié avant de pouvoir garantir cette stabilité. Son chemin est
un localisateur, son hash une empreinte de contenu, son commit une provenance.
Ni une URL ni un hash de texte ne remplace cette identité. Le raccord initial doit
utiliser les identifiants déjà présents dans les manifests WIKI et expliciter les
correspondances vers exports et DB. Aucun rapprochement approximatif par titre,
slug ressemblant ou filtre textuel ne doit autoriser un retrait.

Une version approuvée doit pouvoir être reliée aux éléments suivants :

| Élément | Représentation proposée et preuve exigée |
|---|---|
| Source | dépôt autoritaire + identifiant natif ; chemin/alias conservés comme localisateurs |
| Version source | commit propre à la fiche + hash du contenu ; acceptation vérifiée dans un snapshot identifié |
| Entité cible | type + identifiant DB/canon existant ; gamme_alias est un alias complémentaire |
| Dépendance | source/version → facts partagés ou bloc précis → entité/rôle |
| Résultat | version de projection + run + hash/URI du snapshot ayant servi à l'écriture |
| Ordre | prédécesseur attendu et état accepté courant ; jamais ordre lexical des SHA Git |

Si un ancien enregistrement ne permet pas cette jonction, il reste à réconcilier.
Un déplacement de chemin exige une correspondance explicite d'identité ; il ne
constitue pas à lui seul un retrait puis une nouvelle source indépendante.

## 3. Correction proposée : faire évoluer l'outbox existante

Choix recommandé à soumettre à l'owner : distinguer explicitement l'opération
`replace` de `withdraw`, rendre `rce_new_hash` nullable uniquement pour `withdraw`
et valider la cohérence par contrainte. Retrait = old_hash connu, new_hash NULL ;
remplacement = new_hash connu. La création initiale exige une opération définie
séparément, car old_hash NULL ne signifie pas retrait. Conserver l'historique des
événements existants sans le réinterpréter comme des retraits.

Ajouter au contrat de cette même outbox l'identité source/version, l'identité
entité cible, l'opération, le snapshot approuvé et le prédécesseur attendu. Les
noms/types SQL définitifs, migration et mapping des 554 anciens événements sont
à préparer après validation du contrat. Ne pas cacher ces données dans
`merge_mode`, une liste de gammes ou un champ d'erreur. Ne pas fournir un faux hash
zéro ou un hash de tombstone pour satisfaire artificiellement NOT NULL : il ne
serait plus l'empreinte du nouveau contenu attendue des anciens lecteurs.

Exemple sémantique, non payload SQL exécutable :

```json
{
  "operation": "withdraw",
  "source": {"repository": "wiki", "id": "<identifiant-natif>"},
  "expected_previous": {"commit": "<commit-approuve-A>", "content_hash": "<H1>"},
  "accepted_transition": {"commit": "<commit-approuve-B>", "snapshot_hash": "<S2>"},
  "new_content_hash": null,
  "targets": [{"entity_id": "<id-canon-existant>", "roles": ["R3_CONSEILS"]}],
  "reason": "<decision-de-retrait-referencee>"
}
```

L'événement n'accorde aucune autorité par sa seule présence : vérifier promotion,
source, snapshot et mapping avant acceptation puis scope avant exécution. Une
source retirée de RAW ne supprime pas arbitrairement toute fiche WIKI qui la cite :
elle invalide les faits dépendants à requalifier. Une source WIKI retirée peut
invalider plusieurs cibles ; conserver cette liste de dépendances dans la preuve
versionnée du run. Le stockage durable exact de ce mapping doit être arrêté en
réutilisant les manifests/snapshots et structures de versions existants ; aucune
nouvelle base de dépendances autonome n'est proposée ici.

## 4. Publication fiable et reprise

1. Le point d'acceptation WIKI produit une transition explicite et un snapshot
   vérifiable. Un scan de répertoire absent, tronqué ou rejeté n'est pas un ordre.
2. Dans la DB de projections, le changement de version/validité et son événement
   outbox sont enregistrés dans la même transaction. Un appel Supabase suivi d'un
   autre appel indépendant n'assure pas cette propriété. Préparer une RPC
   transactionnelle après décision de contrat ; pas de transaction distribuée
   prétendue entre Git, PostgreSQL, Redis et l'index.
3. Le relais existant à identifier/reconnecter lit l'outbox et utilise les queues
   existantes. L'absence de code retrouvé ne justifie pas un nouveau cron.
4. Chaque consumer relit l'état autoritaire accepté et le scope, puis applique
   l'opération de façon idempotente. Clé logique : événement + cible + consumer ;
   la mémoire Redis seule n'est pas une preuve durable d'achèvement.
5. Les acquittements par cible/consumer doivent être durables dans le suivi
   existant à faire évoluer. `jobs_enqueued` prouve une mise en file, jamais le
   retrait effectif du contenu. Aucun statut done global avant toutes les cibles
   obligatoires achevées ou exclusions explicitement justifiées.
6. Un crash après effet mais avant acquittement provoque un rejeu sans doublon.
   Une panne index laisse l'événement à reprendre ; elle ne transforme pas une
   réponse incomplète en succès. Les incidents/breaker existants restent utilisés.

L'outbox transactionnelle couvre le risque de double écriture DB/message ; la
livraison peut se répéter et impose donc des consumers idempotents. Référence de
principe : [AWS, Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html).

Dédup 60 min : coalescer les réveils par entité/rôle, sans perdre les transitions.
Si un second événement arrive pendant qu'un job existe ou tourne, il reste pending ;
le consumer recharge l'état courant et le relais confirme qu'aucun événement requis
n'est resté sans traitement avant de considérer le groupe terminé. Le singleton
actuel à payload runId unique ne fournit pas cette preuve. Le détail doit être
validé contre le §B/C1 existant avant modification du processor.

## 5. Parcours et contre-épreuves attendues

| Scénario | Résultat exigé |
|---|---|
| Retrait explicite H1 | Autorité vérifiée ; seule la dépendance source/version ciblée devient invalide ; historique conservé |
| Remplacement H1→H2 | H2 accepté et vérifié avant bascule ; H1 cesse d'alimenter les cibles après convergence |
| Message répété | Même état final, aucun nouveau doublon de version ou retrait élargi |
| H1→H2 reçu après H2→H3 | Comparaison avec état accepté courant ; jamais de retour à H2 ; événement obsolète tracé |
| Événement futur avec prédécesseur absent | Mise en attente/réconciliation ; pas d'acceptation fondée sur timestamp |
| Rejeu historique après retrait | Reconstruction d'audit permise ; aucune réactivation courante sans nouvelle promotion explicite |
| Snapshot partiel, illisible, hash erroné | Aucun retrait inféré de l'absence ; échec observable avant effets actifs |
| Rename de source | Mapping d'identité vérifié ; ancien chemin seul insuffisant pour supprimer |
| Deux sources partagent un fait | Requalification du fait avec preuves restantes ; retrait d'une preuve ≠ suppression automatique du fait |
| Source partagée R3/R6/R8 | Recalcul des dépendances réelles ; isolation par rôle sans oublier les facts partagés |
| Nouveau retrait pendant un job coalescé | Second événement conservé puis traité ; aucun done fondé seulement sur enqueue |
| Crash après index et avant ack | Rejeu exact sans duplication ; toutes les cibles requises finissent acquittées |
| Whitelist retirée entre enqueue et traitement | Re-filtrage worker ; exclusion observable ; aucune écriture hors scope |

Le débranchement logique du contenu dépendant doit précéder sa collecte physique.
Les pages conservent leurs contrats : retirer un bloc invalide n'autorise pas à
supprimer automatiquement une URL, changer une meta/H1 indexée ou réactiver un
fallback legacy/RAG. R1 doit revalider ses liens vers une ressource retirée ; R3 son
contenu réellement servi ; R7 ses blocs curés. R2/R6/R8 gardent leurs contrats
métier distincts mais doivent cesser la production directe via le RAG. R9 reste
déprécié vers G*, exclu de toute activation.

## 6. Correctif isolé préparé et validation exécutée

Le writer SEO relisait les exports pour les métadonnées, le snapshot puis la
projection. Le candidat capture chaque fichier une fois et réutilise ces octets
aux trois étapes, sans changer la signature publique ni le format d'archive.
Les noms d'entrées identiques sont refusés avant écriture active. Cela ferme une
course réelle ; cela ne prouve pas qu'un lot capturé séquentiellement appartient
à un état source approuvé. Le builder conserve le dernier commit touchant chaque
fiche (`_wiki_file_commit_meta`) : plusieurs commits dans un même lot sont légitimes.
Il ne faut donc PAS ajouter une garde d'égalité des source_wiki_commit. L'autorité
de replay reste le hash du snapshot ; la preuve d'acceptation est distincte.

Contre-épreuves archivées : trois échecs avant correction ; tests de mutation
après ouverture du run et après publication du snapshot, archive réelle décompressée,
refus des noms dupliqués, entrée tardive absente et absence de version active en
cas d'échec. Voir les journaux snapshot-consistency*.log et le patch cumulatif.
Les 54 tests du candidat RAG et 74 tests de rôles précédents restent réutilisables
sur leurs fichiers inchangés ; ils ne valident pas cette proposition d'outbox.

## 7. Décisions owner précises et dépendances de livraison

- Valider la représentation retrait/remplacement, new_hash nullable conditionnel,
  identités hors gamme, relation au snapshot promu et mapping des anciens événements.
  Source : ADR-090 §A et §B/C1, évolution de contrat et signature sous revue @fafa.
- Valider le stockage des dépendances et acquittements dans les mécanismes existants,
  ainsi que le traitement des changements arrivant dans la fenêtre de dédup.
  Source : ADR-090 §B/C1 et garantie de replay §A.
- Toute modification réelle de DB/migration, activation ou intervention sur pages
  SEO indexées relève du périmètre owner de CLAUDE invariant9. Aucune de ces actions
  n'est incluse dans les correctifs isolés ni déduite de cette proposition.

Ordre de livraison proposé : contrat au vault → mapping complet et fixtures →
RPC/version+outbox atomique → relais/queues existants → consumers et re-filtrage →
preuves de reprise/hors-ordre → rendu ciblé/CI → activation séparément autorisée.
Le correctif de cohérence du snapshot est préparé indépendamment de ces décisions.

## 8. Verdict et conditions de sortie

PARTIAL_COVERAGE. Proposition concrète, non normative, raccordement non implémenté.
Avant activation : schéma approuvé et migration testée, autorité/identités prouvées,
contre-épreuves du tableau exécutées sur DB+queue+index de test, replay versionné,
UI publique et dépendances partagées vérifiées. Coverage : `coverage.json`.


## 9. Précisions vérifiées sur la filiation existante

Cette lecture affine la proposition ; elle n'ajoute ni registre ni schéma parallèle.
Sources : WIKI `_meta/schema/exports-seo.schema.json`, `_scripts/build_exports_seo.py`
(fonctions `_wiki_file_commit_meta`, `_extract_facts_sources_blocks`, construction
payload) ; app `seo-projection.types.ts` et `seo-projection-writer.service.ts`.

| Jonction réelle | Ce que le code permet de prouver | Limite à conserver |
|---|---|---|
| fiche → entity_id | `entity_type:slug`, avec `wiki_path` dans l'export | Un renommage de slug change cette identité ; aucun mapping de renommage implicite |
| fiche → source_wiki_commit | Dernier commit modifiant cette fiche, métadonnée informative | Ne décrit pas le HEAD de promotion ; ne donne pas l'ordre des messages |
| source_refs → sources | id, sinon source_id, sinon `src-<index>` ; type normalisé et URL | Les identifiants positionnels ne garantissent pas une identité stable après réordonnancement |
| fact → source | `facts[].source_id` optionnel | Une source absente ne peut pas être devinée à partir du texte |
| bloc → preuves | `blocks[].source_ids` préfixés db/web/raw/oem/specialist, copiés dans content JSON DB | Pas de bijection démontrée avec `sources[].id` ; db:table est une dépendance DB légitime |
| export → bloc DB | block_id explicite ou entité#rôle#section normalisée ; index si section absente | Renommer/réordonner des sections peut changer l'identité ; ne prouve pas le retrait des anciens blocs |
| version DB → export exact | run_id puis exports_snapshot_hash/URI ; les références sources restent dans l'archive | Aucune preuve de graphe inverse complet ou d'acquittement multi-consumer à ce stade |

Correctif isolé supplémentaire : le writer résout les identifiants une seule fois,
refuse les doublons qui touchent le rôle demandé AVANT upsert/facts/blocs, et réutilise
ces mêmes lignes pour écrire. Les doublons entre deux rôles indépendants ne sont pas
créés par la simple égalité du nom de section ; les overrides d'identifiant partagés
entre rôles sont détectés lorsqu'ils sont présents dans le même export. Un doublon
limité à un autre rôle ne bloque pas le rôle demandé. Le mode tous-rôles vérifie tous
les blocs. Aucun suffixe automatique ni nouvel algorithme d'identité inventé.

Le pipeline candidat passe à 1.0.1 pour tracer la capture unique et le préflight
d'identités ; la signature publique et le contrat d'archive restent inchangés.
Cette garde ne réconcilie pas d'anciens conflits déjà en DB et ne rend pas les
identifiants positionnels stables. Ces deux limites restent dans le prochain mapping.


## 10. Affinement R8 fondé sur le corpus réel

La proposition Scénic II contient deux axes pour chacune des sections known_issues
et maintenance. Le mapper ignorait usefulness_target dans l'identité : quatre blocs
distincts entraient en collision deux à deux. Le candidat pipeline1.1.0 conserve
cet axe WIKI dans l'identité R8 dérivée ; section et contenu restent inchangés.
Cela affine §9 : la clé d'un bloc R8 inclut sa cible moteur lorsque fournie, et ne
peut pas être réduite à un libellé de section. La convention est à revoir sous ADR090
§A avant livraison. Les retraits doivent cibler le même axe ; jamais tout R8 par
simple nom de section. Voir [[ledger/audit-trail/editorial-pipeline-evidence-20260912/editorial-duplicate-findings|preuves du corpus, compatibilité et limites]].


## 11. Consumer existant : correction des faux acquittements

### Scan

Lecture ciblée du writer, des processors write/refresh, du module et de la
configuration Bull de WorkerModule ; RPC de migration PR-6c et moteur Bull installé.
Le relais `seo/r2/services/outbox-relay.service.ts` concerne **__seo_outbox_event**
(ADR-072), pas **__rag_change_events** (ADR-090). Son existence ne prouve pas le
raccordement du journal éditorial ; il n'est ni recopié ni redirigé dans ce lot.

### Analysis

Deux défauts reproduits : une réponse RPC ne confirmant qu'une seule vue était
acceptée comme refresh global réussi ; une réponse refreshed=false était rendue
normalement par le processor, donc classée completed par Bull. Une suppression
logique pourrait alors ne pas être répercutée sans qu'un retry soit déclenché.
Il s'agit d'une contre-épreuve logicielle, pas d'un retrait réel constaté en échec.

### Correction autorisée, réalisée dans le candidat

Le writer vérifie exactement les deux noms de vues définis par la RPC et des
confirmations booléennes true. Réponse vide, partielle, dupliquée, inconnue, malformée
ou partiellement fausse : erreur explicite. Le processor transforme les échecs
opérationnels en rejet vers Bull ; READ_ONLY demeure un skip observable sans appel DB.
Aucune queue, aucun cron et aucun mécanisme de retry supplémentaire. La configuration
existante WorkerModule prévoit 3 tentatives et backoff exponentiel à partir de 5 s.
Pipeline candidat 1.1.1 et runner 1.0.1 ; signatures publiques inchangées.

### Validation

10 tests en échec / 4 passants avant correctif. Après : **72 tests PASS / 4 suites**,
lint des quatre fichiers, tsc backend et diff-check PASS. Le moteur Bull installé est
exercé sans Redis : horloges et transitions mockées ; confirmation partielle →
moveToFailed, jamais moveToCompleted. Panne puis invocation de rejeu réussie testées.
Les tests R8/capture du lot précédent passent dans la même exécution.
Preuves : refresh-ack-baseline.log, refresh-ack-tests.log, refresh-ack-lint.log,
refresh-ack-typecheck.log, refresh-ack-verification.json. Patch cumulatif actuel :
application-refresh-ack.patch ; tous les patches antérieurs sont conservés.

### Verdict

VALIDATED_FOR_SCOPE_ONLY pour ce correctif ; PARTIAL_COVERAGE pour la propagation.
**Aucun raccordement outbox ni acquittement durable par consumer réalisé.** La
persistance Redis et les délais réels de retry ne sont pas éprouvés. removeOnFail
reste true ; après épuisement des tentatives, cette file ne conserve pas le job.
Le singleton peut encore coalescer une notification arrivant pendant un refresh ;
la garantie durable dépend du raccordement transactionnel décrit aux §3–5.
Pas de RPC live exécutée, DB modifiée, migration, CI nouvelle ou déploiement.


## 12. Transaction existante-bloc + outbox — candidat éprouvé sur PostgreSQL

**Scan** : schéma natif ADR059, writer (hash/no-op, confidence, run/snapshot), outbox
13 colonnes déjà inventoriée en lecture seule, runner de migrations et lint SQL.
**Analysis** : des appels DB indépendants ne garantissent pas la bascule avec son
événement. L'identité de bloc, la version attendue et le prédécesseur outbox permettent
une comparaison atomique, sans rapprochement approximatif de titres.

**Correction proposée/préparée sous l'autorisation « continue »** : migration
`20260912212340_seo_projection_block_outbox.sql`, créée avec Supabase CLI 2.117.0.
RPC SECURITY INVOKER réservée au service_role. Verrou de ligne sur le bloc exact,
contrôle entité/rôle, version active attendue et événement précédent. Remplacement :
nouvelle version, dépréciation précédente et bascule. Retrait : pointeur NULL,
historique conservé. Dans les deux cas, événement pending inséré dans la même
transaction. L'empreinte de requête rend le rejeu exact sans effet ; un rejeu modifié
échoue. Elle ne remplace pas le hash de contenu. Les clés étrangères préservent
les runs, blocs et versions référencés. Aucun nouveau journal ou scheduler.

Le nouveau hash devient nullable seulement pour withdraw ; une contrainte validée
préserve le comportement legacy. Les deux index sont créés CONCURRENTLY via le
marqueur natif @non_transactional ; reprise capable de reconstruire un index invalide.
Lint initial : trois diagnostics. Deux dérogations locales expliquées dans le SQL :
le mode autocommit réellement exécuté et le changement de nullabilité intentionnel.
Ce dernier reste une évolution de contrat sous revue avant toute base partagée.

**Validation** : 18 tests PASS sur PostgreSQL17.11 réel, conteneur jetable sans réseau,
sans port ni volume persistant, supprimé à la fin. Schéma projection natif exécuté ;
outbox de test reconstruite depuis l'inventaire sauvegardé, pas certification du
catalogue partagé courant. Panne injectée dans l'INSERT outbox → rollback complet des
lignes ; deux sessions réellement concurrentes, attente Lock observée → un seul événement.
Rejeu après retrait, ancienne version, prédécesseur périmé, scope incorrect, run sans
snapshot/failed, régression, nullabilité legacy et privilèges éprouvés. Réapplication
avec données conservées et index valides. SQL lint, marqueur migration et diff-check PASS.
Un premier démarrage de fixture a rencontré le serveur temporaire d'initialisation Docker ;
le harness attend maintenant le processus PostgreSQL définitif avant d'appliquer le schéma.

**Verdict : PARTIAL_COVERAGE**, transaction VALIDATED_FOR_SCOPE_ONLY. Pas de raccord
runtime de cette RPC, migration partagée, promotion, index/corpus, CI ou déploiement.
L'existence de hash/URI du snapshot ne prouve PAS l'acceptation WIKI. La RPC traite
uniquement un bloc déjà actif ; pas de création, de réactivation après retrait ou de
retrait déduit d'une absence. Une régression est rejetée ; le chemin draft/conflict du
writer natif doit rester responsable de sa conservation. Les événements restent pending :
aucune preuve d'acquittement durable consumer, refresh MV, queue réelle ou rendu public.

Point concret de raccord suivant : le writer enregistre aujourd'hui les références du
snapshot à closeRun. Persister le snapshot vérifié avant le premier appel transactionnel,
puis relier les transitions explicitement acceptées et leur mapping source/bloc. Raccorder
ensuite les consumers existants et leurs ACK durables avant toute activation. Vérifier les
anciens clients d'outbox : ne pas leur servir un retrait avec un faux hash nouveau.
Preuves : `block-outbox-postgres-tests.log`, `block-outbox-verification.json`,
`block-outbox-sql-lint-initial.log`, `block-outbox-sql-lint.log`,
`block-outbox-migration-marker.log`, `application-block-outbox.patch`.


## 13. Raccordement du writer aux remplacements transactionnels

**Scan** : writer, types, gate d'export natif, wrapper callRpc, tests de rôles/snapshot,
contrat SQL du lot12. **Analysis** : snapshot publié sur disque avant l'écriture, mais
hash/URI enregistrés seulement à closeRun ; incompatible avec la précondition SQL.
L'upsert de bloc pouvait aussi réaffecter une identité ou réutiliser un bloc retiré.
Le source_type du mapper est le truth_level (ex. sourced), pas la constante wiki.

**Correction proposée/préparée sous autorisation « continue »** : snapshot attaché au
run running, résultat exact relu avant toute écriture d'entité. Remplacement d'un bloc
actif par callRpc natif uniquement, avec identité, scope, version attendue, événement
précédent, wiki_path et contenu/provenance du mapper. Vérification stricte du résultat.
Aucun repli direct si RPC/lecture/garde échoue. Anciennes versions restent traitées par
la transaction du lot12 ; source_type devient un paramètre exact inclus dans l'empreinte
de rejeu. Migration candidate encore non appliquée, aucune surcharge antérieure déployée.
Bloc inactif ou identité réaffectée : réconciliation requise. Création via INSERT avec
refus de collision, sans upsert d'une ligne existante. No-op et draft/conflict natifs
conservés. Pipeline1.2.0, runner1.0.1.

**Validation** :89 tests PASS/4 suites writer, mapper, snapshot, refresh. Appel public
projectExports avec gate natif et archive réelle ; transport DB simulé, wrapper callRpc
réel, y compris refus de garde. Snapshot non confirmé → zéro écriture d'entité ; RPC
périmée → résultat blocked, conflit, run failed. Absence RPC, résultat vide/incohérent,
erreurs de lecture, bloc retiré et collision de création testés sans repli direct.
18 tests PostgreSQL17.11 réexécutés avec la signature et provenance mises à jour : PASS.
Ce sont deux couches de preuve distinctes, pas une intégration PostgREST complète.
ESLint3 fichiers, tsc backend, SQL lint, marqueur migration et diff-check PASS.
Le premier passage Jest a révélé une assertion ancienne assimilant première mise à
jour du run et clôture ; elle cible maintenant explicitement la clôture. Aucun échec
baseline avant changement du writer n'est revendiqué.

**Verdict** :PARTIAL_COVERAGE. Remplacement raccordé dans le code candidat, non activé.
Retrait explicite WIKI non raccordé, absence de bloc jamais interprétée comme un retrait.
Création initiale, facts partagés et drafts restent hors transaction de remplacement :
ne pas annoncer l'atomicité d'une entité entière. Les écritures partielles multi-blocs
et leur comptabilisation restent à auditer avant activation. Autorité WIKI amont inchangée ;
snapshot/commit seuls ne constituent pas une nouvelle preuve de promotion.
Aucun ACK consumer durable, relais de reprise, Redis réel, migration partagée, CI ou
rendu public validé. Preuves : writer-outbox-*.log, writer-outbox-verification.json,
application-writer-outbox.patch cumulatif. Les anciens patches/preuves restent historiques.


## 14. Écritures partielles et état réel du job — 13 septembre 2026

**Scan** : projectOne/writeEntity/writeBlocks, agrégats du run, processor write et
contrat des résultats. **Analysis** : une exception tardive remplaçait l'issue de
l'entité par facts noop/role blocked sans conserver les écritures précédentes.
Le processor conditionnait le refresh aux compteurs de succès complet, puis rendait
normalement un run bloqué : Bull le classait completed. Deux défauts liés, observés
sur des contre-épreuves exécutées avant modification du code :5 échecs/59 passants.

**Correction préparée sous autorisation « continue »** : progression locale à l'entité
et au run, propagée aux méthodes natives. Facts et blocs signalés écrits avant l'erreur
restent dans le résultat ; le conflit write_error enregistre aussi cette progression.
La partition des roleOutcome reste exacte : le rôle partiel est blocked, pas written.
Refresh demandé si une écriture active est comptabilisée, même pour un rôle blocked ;
puis exception explicite vers Bull. Run bloqué, snapshot non préparé ou openRun échoué
ne sont plus des completed. READ_ONLY, entrée vide et noop valide conservent leur
comportement. Pipeline1.2.1/runner1.0.2. Aucun nouvel état SQL, journal ou scheduler.

**Validation** :97 tests PASS/4 suites, ESLint4 fichiers, tsc backend, diff-check PASS.
Parcours public writer avec archive réelle, DB simulée ; facts réussis puis bloc en
échec ; premier bloc transactionnel réussi puis second en échec ; compteur du run et
conflit persisté simulé inspectés. Moteur Bull natif processJob avec transitions et
horloges simulées : refresh demandé puis failed, jamais completed. Les18 tests SQL
antérieurs sont réutilisés, pas relancés : hashes de la migration et du harness Python
identiques à writer-outbox-verification.json ; aucun changement de dépendance/fixture.

**Verdict** :PARTIAL_COVERAGE. Le lot corrige la conservation des succès rapportés par
les méthodes existantes et leur traitement par la file. Il ne transforme pas les
écritures legacy facts/création en transaction ; leurs erreurs intermédiaires et
acquittements incertains ne sont pas certifiés. Une panne à closeRun/recordConflict,
un crash avant enqueue ou une notification coalescée nécessitent encore une reprise
durable. Retrait WIKI explicite, relais outbox et ACK consumers non raccordés. Aucun
Redis réel, chaîne PostgREST intégrée, CI, rendu public, écriture partagée ou déploiement.
Preuves : partial-write-baseline.log, partial-write-tests.log,
partial-write-verification.json et application-partial-write.patch cumulatif.


## 15. Acquittement transactionnel de la projection et reprise native — 13 septembre 2026

**Scan** : RPC native de refresh, MVs, outbox éditoriale, writer/processor write,
module et feeder existants ; harness PostgreSQL et tests du contrat refresh.
**Analysis** : un succès du refresh ne conservait aucune preuve durable des événements
éditoriaux pris en compte. Une écriture déjà validée dont l'enqueue était perdu pouvait
rester sans nouvelle demande lors d'un passage writer sans modification.

**Correction préparée sous autorisation « continue »** : nouvelle colonne nullable
rce_projection_refreshed_at dans __rag_change_events, sans modifier le statut global.
La RPC existante capture les identifiants réellement visibles, rafraîchit les deux MVs,
puis acquitte exclusivement ces identifiants dans la même transaction. Aucun seuil
MAX(id) : les séquences peuvent être allouées avant un commit tardif, comme documenté
par [PostgreSQL 17](https://www.postgresql.org/docs/17/transaction-iso.html).
Le contrat exact à deux lignes et l'accès service_role sont conservés ; search_path
est fixé vide et les objets qualifiés. Index partiel pending créé concurremment via
le marqueur natif autocommit, réparable par réapplication. Migration générée par la CLI
Supabase native 2.117.0. Une seule exemption Squawk locale, après diagnostic initial,
pour le mode transactionnel supposé par le lint alors que le runner respecte le marqueur.
Le writer détecte les événements replace/withdraw non acquittés et le processor peut
demander le singleton existant même sur un passage sans écriture. READ_ONLY court-circuite
la lecture et l'enqueue. Erreurs DB/queue propagées ; les effets actifs déjà confirmés
ne dépendent pas du succès de cette lecture supplémentaire. Pipeline1.2.1/runner1.0.3.

**Validation** :24 tests PostgreSQL17.11 PASS, dont6 nouvelles contre-épreuves :
ACK/rejeu/statut global, retrait conservant l'historique, rollback des deux vues si ACK
échoue, événement validé pendant refresh, identifiant inférieur validé tardivement,
privilèges/réapplication. Sessions concurrentes réelles observées via pg_stat_activity.
Fixture éphémère isolée réseau, tmpfs, aucun port/volume ; conteneur propre supprimé.
106 tests applicatifs/5 suites PASS, transports DB/queue simulés, archive et wrapper
natifs ;9 nouveaux tests de reprise. ESLint5 fichiers, tsc backend, lint SQL, marqueur
migration et diff-check PASS. Aucun échec baseline avant correction revendiqué.

**Verdict** :PARTIAL_COVERAGE. ACK durable limité à la projection SEO et aux transitions
explicites replace/withdraw ; il ne termine pas les autres consommateurs. Reprise au
prochain passage du writer, sans relais autonome ni nouveau scheduler. Le singleton peut
encore absorber une demande pendant un refresh actif ; les événements tardifs restent
pending pour un passage suivant. Aucun délai de reprise garanti sans nouvelle exécution.
Feeder R1 inchangé, désactivé par défaut. Retraits acceptés WIKI toujours à raccorder ;
aucune absence interprétée comme retrait. Facts/créations legacy, panne closeRun/conflit,
Redis réel, transport PostgREST intégré, charge/verrous, CI et rendu public restent hors
preuve. Les clients historiques de l'outbox exigent une vérification avant application
partagée. Aucun commit/push/merge, déploiement, activation ou écriture DB partagée.
Preuves : refresh-ack-*.log, refresh-ack-verification.json et application-refresh-ack.patch
cumulatif. Les anciennes sections et patches décrivent des jalons historiques.


## 16. Reprise du singleton à la fin du job et au redémarrage — 13 septembre 2026

**Scan** : processor refresh/write, module Nest, feeder, options WorkerModule et
consommateurs outbox existants ; API et implémentation installée Bull4.16.5,
liaison des décorateurs @nestjs/bull ; fixture Redis Testcontainers du repo.
**Analysis** : add() avec l'identifiant du job actif ne crée pas de successeur.
Un contrôle dans handle() conserverait une fenêtre entre sa dernière lecture et
la suppression du job. Dans [Bull4.16.5](https://github.com/OptimalBits/bull/blob/v4.16.5/REFERENCE.md),
le hook completed intervient après moveToCompleted ; le code installé confirme
cet ordre. Aucun relais éditorial actif identifié dans les chemins examinés ; le
relais R2 est distinct et ne doit pas être réutilisé pour changer d'outbox.

**Correction préparée sous autorisation « continue »** : le processor existant
réconcilie les pending après completed, lorsque le singleton a été supprimé, et
au démarrage via un onModuleInit non bloquant. Il réutilise la même queue, le même
job, le même identifiant désormais constant partagé, le délai5s et les tentatives
bornées existantes. READ_ONLY reste dans le writer, avant DB/enqueue. Un échec de
lecture/enqueue dans un hook est loggé explicitement ; pas de rejection orpheline
EventEmitter ni de bouclage artificiel des jobs échoués. Aucune planification
périodique, aucun feeder activé, aucun nouveau journal. Runner1.0.4, pipeline1.2.1.

**Validation** :119 tests PASS/6 suites, dont7 sur Redis éphémère réel avec wiring
Nest/Bull natif. Témoin sans hook : événement tardif conservé mais aucun successeur.
Avec correction : successeur créé après suppression ; producteur après lecture
finale ; reprise au redémarrage sans nouveau write ; job Redis déjà présent consommé
une seule fois ; panne RPC temporaire rejouée ; panne persistante arrêtée après3
tentatives sans acquitter le pending. La DB est simulée dans ces tests Redis.
Délai5s vérifié avant promotion manuelle du job dans la fixture ; backoff d'échec
raccourci pour le test seulement. Six nouveaux tests unitaires complètent les
contrôles de hooks, READ_ONLY et erreurs observables. Premier passage :2 défauts
de fixture corrigés (objet Job ancien après réutilisation de l'identifiant, arrêt
avant disponibilité du worker). Diagnostic open-handles puis chaîne finale terminés
normalement ; aucun forceExit. ESLint6 fichiers, tsc backend et diff-check PASS.
Les24 tests PostgreSQL précédents sont réutilisés après vérification exacte des
hashes des2 migrations et du harness inchangés ; aucun rerun SQL inutile.

**Verdict** :PARTIAL_COVERAGE. Reprise après fin réussie et redémarrage sain prouvée
dans le périmètre isolé. Un échec du hook de réconciliation laisse le pending et
requiert une nouvelle occasion de reprise ; après épuisement des tentatives, aucune
relance sans limite. Pas de relais périodique autonome. Test de reconnexion et de
cycle Nest, pas de SIGKILL système ni perte du serveur Redis. Chaîne PostgreSQL,
PostgREST et Redis intégrée non prouvée. ACK projection ne vaut pas ACK des autres
consommateurs. Mapping des retraits acceptés WIKI, lineage complet, facts/créations
legacy et erreurs tardives de journalisation restent à traiter. Aucune migration
partagée, activation, CI, page publique ou livraison. Preuves : queue-recovery-*.log,
queue-recovery-verification.json et application-queue-recovery.patch cumulatif.


## 17. Observations de retrait dans le builder WIKI existant — 13 septembre 2026

**Scan** : CLAUDE WIKI, promote.py, promotion_decision.py, schéma frontmatter et
builder SEO natif. **Analysis** : la validation/promotion WIKI est automatique.
Le statut deprecated existe, mais les chemins examinés ne produisent pas de
transition de retrait acceptée et vérifiable par les consommateurs. Une absence,
un statut ou un gate SEO perdu ne suffisent pas pour fabriquer cette autorité.

**Correction préparée sous autorisation « ensuite »** : ajout de --format json
au builder existant, sans moteur parallèle. Le cas UNRECONCILED fournit identité
attendue depuis le chemin, empreintes des octets source/export lus, déclarations
observées, coordonnées natives des blocs et motif du blocage. Le mode ciblé couvre
la source absente si son ancien export subsiste. Tout le lot reste sans écriture
avant réconciliation ; withdrawal_authorized est toujours false. Le chemin source
ne vient jamais du JSON historique. Les liens hors scope sont refusés. Hash source
et frontmatter utilisent les mêmes octets capturés ; hash fichier et hash du corps
ne sont pas confondus. Métadonnées YAML non JSON et constantes numériques non finies
sont signalées sans fabriquer de valeurs. Le texte reste le défaut et les erreurs
préalables conservent leur comportement natif, éventuellement sans JSON.

**Validation** :102 tests PASS (88 builder,14 score/schema), dont20 nouveaux tests
builder. Trois contre-épreuves métadonnées invalides échouaient avant correction.
Fixtures temporaires : dépréciation/perte d'approbation, source absente, scope ciblé,
identité falsifiée, JSON invalide, liens sortants, mutation source pendant lecture,
dates/sets/NaN et comptage dry-run/écriture. Compilation Python, hooks natifs des3
fichiers et diff-check staged PASS ; mdformat a normalisé le README au premier
passage, puis contrôle vert. Aucun test applicatif/Redis/SQL relancé : code concerné
inchangé dans ce lot, preuves précédentes restent distinctes et historiques.

**Verdict** :PARTIAL_COVERAGE. Ce diagnostic ne retire aucun contenu WIKI ou aval.
Il ne prouve ni l'autorité de retrait, ni l'identité DB des consommateurs ; les
champs observed_* restent non vérifiés. Le raccordement opérationnel exige un
contrat de transition de retrait issu du parcours WIKI, liant la lignée et les
versions avant/après aux dépendances réellement consommées. Prochaine action :
préparer cette extension du moteur existant et ses contre-épreuves de fraîcheur,
rejeu et remplacement partiel, dans la gouvernance canon, avant raccordement.
Ne pas réintroduire une validation humaine systématique des fiches.
Aucune mutation de corpus, DB partagée, activation, CI, commit/push/merge ou livraison.
Preuves : withdrawal-observations-*.log, withdrawal-observations-verification.json,
wiki-withdrawal-observations.patch cumulatif. Patch applicatif précédent inchangé.


## 18. Contrat proposé de transition WIKI et fraîcheur du prédécesseur — 13 septembre 2026

**Statut du contrat : proposition non normative, REVIEW_REQUIRED.** Ce document
prépare l'extension du moteur existant ; il ne lui accorde aucune nouvelle autorité.
Le changement de code de ce lot renforce uniquement la capture des entrées de
promotion et leur fraîcheur. Il ne rend pas un retrait exécutable.

### Scan et analyse

Le runner natif `_run_real_evaluators` choisit automatiquement la fiche canon
approved comme baseline de comparaison lorsque l'appelant n'en fournit aucune.
Le manifeste antérieur n'incluait que la baseline explicitement fournie. La cible
pouvait donc changer sans invalider la décision. Autre lacune : les empreintes des
moteurs étaient revérifiées avant apply mais pas comparées pendant l'évaluation ;
le dry-run pouvait déclarer éligible un résultat calculé entre deux révisions.

### Correction préparée et vérifiée dans le moteur existant

`capture_input_manifest` ajoute `canon_target`, résolue par le même résolveur que
l'exécuteur, y compris lorsqu'elle est absente (hash nul). La baseline explicite
reste capturée séparément. Le manifeste observe donc la destination réelle même
si le comparateur reçoit un autre prédécesseur historique. Édition, disparition
ou apparition de la cible pendant l'évaluation bloquent la décision ; après
l'évaluation, elles font refuser l'autorisation d'application. Une autre fiche
sans rapport ne l'invalide pas. Les deux empreintes de code sont comparées avant
et après l'évaluation. Une recapture devenue impossible produit un refus typé ;
elle n'est pas transformée en état éligible ou en absence interprétée comme retrait.
Les fixtures anciennes ont reçu leur entity_type, indispensable au résolveur natif.

### Proposition : entrées et autorité de la transition

La demande de transition exprime l'intention ; ses déclarations ne font jamais
preuve. Elle reste dans le parcours de propositions. Le moteur automatique existant
collecte les preuves et décide ; l'exécuteur applique seulement cette décision.
Aucune validation humaine systématique des fiches n'est réintroduite.

| Entrée nécessaire | Vérification proposée |
|---|---|
| Opération explicite : remplacement ou retrait complet | Absence de demande = aucune transition ; aucun retrait déduit d'un diff de répertoire |
| Entité et lignée natives | Même entity_type/slug attendu et lineage_id stable vérifié dans les versions ; ambiguïté ou ancienne lignée manquante = bloqué |
| Prédécesseur attendu | Version WIKI acceptée et empreinte du fichier exact ; comparer avec canon_target courant, jamais trier des SHA comme des dates |
| Proposition et preuves | Octets de proposition, passages source effectivement utilisés, versions de policy/schema/évaluateurs et résultats des gates ; indisponibilité ou contradiction = bloqué |
| Périmètre consommé | Exports historiques identifiés et vérifiés dans le snapshot natif ; coordonnées natives vers versions actives DB/consommateurs ; aucune jonction par titre ressemblant |
| État après transition | Remplacement : proposition éligible et même lignée ; retrait complet : preuve positive couvrant l'intégralité du contenu ciblé, sans nouveau contenu |

Un motif textuel, le seul statut deprecated, un fichier absent, une panne RAW ou
un gate inconnu ne sont pas une preuve positive de retrait complet. Le vérificateur
de cette preuve de retrait n'existe pas encore dans le moteur : tant qu'il manque,
la décision correspondante doit rester bloquée. La correction de fraîcheur de ce
lot ne résout pas cette lacune sémantique et n'en fabrique pas un substitut.

### Proposition : trois effets à distinguer

1. **Remplacement de fiche** : la nouvelle proposition passe les gates existants,
   y compris régression/provenance, avec prédécesseur et lignée vérifiés. L'ancien
   contenu reste dans l'historique. Le garde actuel contre l'écrasement d'une fiche
   approved reste actif dans ce candidat ; une future transition contrôlée devra
   l'étendre avec ses préconditions, sans le contourner.
2. **Retrait d'un bloc lors d'un remplacement** : un bloc absent du nouvel export
   ne devient retirable qu'après vérification d'une transition explicite et d'un
   périmètre d'export complet. La jonction porte sur son identité native complète
   (entité/rôle/section/axe), sa dépendance source et sa version active attendue.
   Les blocs conservés et les facts partagés avec d'autres preuves subsistent.
3. **Retrait complet de connaissance** : exige la preuve positive précédente et
   l'inventaire des dépendances de la version ciblée. Ce retrait n'autorise jamais
   à supprimer une page indexée, changer son URL ou ses métadonnées. Les contrats
   de publication et d'indexabilité continuent à s'appliquer indépendamment.

### Proposition : ordre, rejeu et exécution

Juste avant l'effet WIKI, revérifier les entrées capturées et les versions de code.
La preuve de fraîcheur doit être liée aux octets effectivement écrits ; une simple
séquence de checks sans protection de l'écriture concurrente ne suffit pas. Le
moteur et l'exécuteur actuels ne fournissent pas encore un compare-and-swap atomique
sur le corpus Git. Ne pas prétendre que le hash-before/hash-after ferme cette course.
L'état avant/après et la décision devront rester dans la preuve du snapshot/run
existant ; le stockage durable de cette acceptation reste à raccorder.

Côté consommateurs, utiliser les versions natives et l'outbox existante :

- Prédécesseur actif exact + transition acceptée courante : appliquer l'effet ciblé.
- Même transition et même effet déjà enregistrés : rejeu sans nouveau changement.
- Prédécesseur différent ou transition dépassée : conflit observable, aucune réactivation.
- Cible/dependance inconnue ou preuve manquante : bloqué, aucune opération élargie.
- Effet réalisé mais acquittement absent : reprendre l'acquittement avec la même identité.

L'ACK projection ne vaut pas achèvement RAG/cache/index. Aucun statut global terminé
avant confirmation de chaque consommateur requis. Les mécanismes SQL/queue déjà
préparés restent utilisés ; aucun journal de dépendances ou scheduler parallèle.

### Validation et limites du lot courant

199 tests PASS :50 moteur de décision,47 promoteur,88 builder et14 score/schema.
Quinze nouveaux tests, dont9 contre-épreuves rouges avant correction. Le runner
natif et son choix automatique de baseline sont exercés avec évaluateurs injectés ;
les écritures sont limitées aux fixtures temporaires. Compilation Python, hooks
natifs des2 fichiers et diff-check staged PASS. Aucun changement de corpus partagé.

Contrat proposé encore non exécuté : preuve de retrait complet, acceptation durable,
jonction de lignée avec consommateurs, effet Git atomique, remplacement partiel et
rejeu bout en bout. Les captures n'ont pas été certifiées exhaustives pour tous les
inputs des gates (contenus RAW référencés, configuration effective, imports et schémas).
Le CLI charge aussi fm/body avant la décision : leur lien exact avec les octets écrits
mérite une contre-épreuve dédiée avant tout élargissement des transitions.

**Verdict : PARTIAL_COVERAGE.** Aucun retrait autorisé ou propagé par ce lot, aucune
suppression WIKI, migration partagée, activation, CI, commit/push/merge ou livraison.
Prochaine action : éprouver puis corriger le lien décision → octets appliqués dans
l'exécuteur existant, avant d'ajouter un effet de transition. Preuves :
transition-inputs-counterproof.log, transition-inputs-tests.log,
transition-inputs-hooks.log, transition-inputs-verification.json,
wiki-transition-inputs.patch cumulatif. Les sections précédentes sont historiques.


## 19. Décision liée au contenu appliqué par le promoteur — 13 septembre 2026

**Scan/analysis** : le CLI chargeait fm/body avant la capture des entrées de décision,
puis transmettait ces valeurs anciennes avec un simple résumé de score à l'exécuteur.
Une proposition modifiée avant capture pouvait donc être évaluée dans sa nouvelle
version mais écrite avec son ancien contenu ou son ancien slug. Une modification
pendant l'exécution pouvait aussi être supprimée par le déplacement de proposition.
Trois contre-épreuves CLI ont reproduit ces défauts avant correction.

**Correction préparée sous autorisation « continue »** : l'exécuteur existant reçoit
la décision canonique complète et les racines nécessaires à sa revérification.
Il refuse une évaluation/score isolé. Il lit la proposition, compare le hash de ces
octets au candidat capturé, puis parse ces mêmes octets pour obtenir contenu et
identité. Il ne reçoit plus fm/body chargés auparavant par le CLI. Les métadonnées
de promotion restent issues de la même évaluation et sont stampées par le parcours
natif ; YAML et fins de lignes suivent la sérialisation native. Pas de promesse de
byte-identité du fichier final avec la proposition brute.

Le statut promouvable est défini une fois dans le moteur et utilisé par CLI et
exécuteur : proposed/in_review. Une bascule vers draft/approved/deprecated entre
prélecture et capture ne contourne plus le préflight. Juste avant écriture, l'ensemble
des entrées capturées et les révisions moteur sont revérifiés. Le garde anti-écrasement
d'une cible approved reste en place. Après écriture, avant suppression de la proposition,
le contenu source est comparé aux octets capturés ; s'il diffère, la proposition est
conservée et apply_error indique explicitement l'effet canon déjà réalisé.

**Compatibilité** : signature interne désormais
`apply_promotion(target, wiki_root, decision, *, raw_root=None, baseline_path=None)`.
Les appels retrouvés dans les scripts WIKI étaient le CLI et ses tests ; l'appelant
natif est adapté. La recherche ciblée des scripts Python applicatifs n'a pas trouvé
d'autre appel. Aucun fallback permissif vers ancienne signature ou score isolé.
La décision reste un résultat de confiance dans le même processus ; ce lot ne crée
pas de jeton d'autorisation portable ni d'endpoint pour des décisions fournies.

**Validation** :209 tests PASS (57 promoteur,50 décision,88 builder,14 score/schema).
Dix nouveaux tests ;3 contre-épreuves CLI rouges avant correction. Contenu/slug
changés avant capture, mutation après autorisation, pendant parsing et avant écriture,
mutation source pendant l'écriture canon, statuts devenus non promouvables, refus
d'une évaluation nue. CLI/exécuteur/manifeste natifs, évaluateurs injectés et fichiers
temporaires. Deux fixtures de sérialisation partaient draft : soumises explicitement
in_review dans le test, sans modifier le corpus de fixtures partagé. Compilation,
hooks natifs3 fichiers et diff-check staged PASS.

**Verdict : PARTIAL_COVERAGE.** Le lien entre octets capturés et contenu/identité
appliqués est éprouvé pour ces cas. Les fenêtres entre contrôle et écriture, puis
entre comparaison source et unlink, restent non atomiques face à un autre processus.
Une panne d'écriture partielle n'est pas couverte par un remplacement de fichier
atomique. Une mutation source détectée après écriture peut laisser le canon écrit
et la proposition conservée : erreur explicite, pas de rollback prétendu.
Prochaine action : cartographier les mécanismes natifs d'exclusion/écriture atomique
et éprouver les courses et pannes à la frontière d'application, avant d'étendre les
transitions ou de connecter un retrait. Le contrat §18 demeure proposé ; aucun
retrait complet, acceptation durable ou mapping consommateur nouveau. Aucune mutation
corpus partagé/DB, activation, CI, commit/push/merge ou déploiement.
Preuves : applied-snapshot-*.log, applied-snapshot-verification.json,
wiki-applied-snapshot.patch cumulatif. Les jalons antérieurs restent historiques.


## 20. Publication atomique native et consolidation du candidat — 13 septembre 2026

**Scan/analysis** : patterns flock des scripts de synchronisation applicatifs et
os.replace des outils natifs ; aucun verrou de promotion WIKI trouvé. write_text
pouvait tronquer un canon avant une panne. Le CLI renvoyait 0 même après apply_error,
et le format texte ne montrait pas l'erreur. Trois contre-épreuves ont échoué :
fsync fichier, publication replace et statut de sortie sur échec d'application.

**Correction préparée sous autorisation « continuer jusqu'au bout »** : flock
exclusif non bloquant sur l'inode du répertoire checkout pendant l'exécution native.
Deux promoteurs utilisant ce checkout ne publient plus simultanément ; contention
= PROMOTION_BUSY explicite. Aucun fichier de verrou, registry ou scheduler ajouté.
Runtime POSIX obligatoire, aucun fallback sans verrou. Source, cible et décision
sont revérifiées sous ce verrou. Le canon est sérialisé dans un temporaire du même
répertoire, permissions reprises du fichier existant ou de la proposition, flush et
fsync, puis revérification et os.replace. Le répertoire cible est synchronisé avant
suppression éventuelle de la proposition. Un échec de synchronisation après publication
signale explicitement l'effet partiel et conserve la proposition. Le CLI expose
apply_failures et renvoie 1 pour une application bloquée/échouée ; les messages sont
visibles en texte et JSON. Diagnostic dry-run inchangé.

**Validation** :216 tests PASS (64 promoteur,50 décision,88 builder,14 score/schema).
Sept nouveaux tests ; trois rouges avant corrections. Deux processus réels prouvent
l'exclusion ; SIGKILL réel avant replace prouve ancien canon intact, source conservée,
libération du verrou et reprise native réussie. Pannes fsync/replace injectées :
ancien fichier intact et temporaire nettoyé sur exception ordinaire. Panne fsync
répertoire après publication : nouveau canon complet et source conservée, erreur.
Compilation, hooks3 fichiers et diff-check staged PASS.

**Limites connues** : verrou advisory d'un checkout, ni verrou distribué ni contrôle
des auteurs de propositions qui l'ignorent. La course compare/unlink de source reste
possible avec un auteur non coopératif ; aucune transaction atomique entre deux
fichiers n'est annoncée. Un SIGKILL peut laisser un .tmp ; il n'est pas une fiche
Markdown, n'est pas publié comme contenu et n'est pas purgé automatiquement. Pas de
preuve de coupure électrique ou de crash à chaque instruction. Crash après publication
ou erreur fsync peuvent conserver source et canon ; pas de rollback distribué.

### Consolidation des quatre candidats

| Candidat | État vérifié maintenant | Validation disponible |
|---|---|---|
| WIKI | Patch cumulatif wiki-atomic-promotion.patch, aucun diff non staged |216 tests actuels et hooks |
| Application | Hash du patch staged identique au précédent checkpoint | Preuves antérieures conservées, pas de nouveau test runtime |
| RAW | Hash du patch staged identique au précédent checkpoint | Preuves antérieures conservées, pas de nouvelle acquisition |
| RAG | Hash du patch staged identique au précédent checkpoint | Preuves antérieures conservées, pas de nouvel accès index |

candidate-consolidation.json conserve HEAD, hash et état non staged de chaque
candidat. Les anciens tests ne sont pas réannoncés comme exécutés aujourd'hui.

**Point métier requis pour achever le raccordement de retrait** : le moteur natif
ne définit pas l'événement qui autorise un retrait complet. Question transmise à
l'utilisateur : demande explicite ciblant fiche/version, vérifiée automatiquement,
ou retrait limité aux anciens blocs d'un remplacement validé. Tant que ce choix
manque, le contrat §18 reste proposé ; aucune absence, dépréciation déclarée ou panne
de gate n'est convertie en autorisation. Cette question porte sur le déclencheur
métier, pas sur une validation humaine systématique des fiches.

**Verdict : PARTIAL_COVERAGE.** Correctifs du candidat appliqués/staged et validés
sur les périmètres indiqués ; raccordement de retrait complet non achevé. Aucun
contenu partagé supprimé, migration partagée, activation, CI, commit/push/merge ou
déploiement. Preuves : atomic-promotion-*.log, atomic-promotion-verification.json,
candidate-consolidation.json et wiki-atomic-promotion.patch.
