---
type: audit-report
status: draft
updated: 2026-09-12
---

# Parcours éditorial AutoMecanik — jalon de reprise Codex

## Objectif et verdict

Réviser scraping → RAW → WIKI → projections → édition, avec séparation catalogue,
explication, procédure et diagnostic ; qualifier R2/R8 et la notation sans fabriquer
du contenu pour augmenter une note. **PARTIAL_COVERAGE** : cartographie initiale et
lots isolés qualifiés sur leurs périmètres (synchronisation, notation, transport RAW, réception admin texte, vidéo RAW, reprise des inventaires RAW, corps importé dans RAG). Aucune promotion ni export sur le corpus partagé, aucune
publication, aucun déploiement ni changement de droits Hermes pendant cette reprise.
Ce document est un constat technique, pas une nouvelle règle canonique.
Reprise : [[ledger/audit-trail/editorial-pipeline-evidence-20260912/CHECKPOINT|checkpoint du chantier]].

## Scan : références vérifiées

- Application : `/opt/automecanik/app`, compte `deploy`, `main`,
  `0c31807c8453c251d70c7575eafcc973f04eed14`, frais après fetch. Nombreux non-suivis préservés.
- WIKI validation : `/opt/automecanik/wiki-auto-validation`,
  `01cea8deda48d84b6a2993cd4bdefe8280082c0b`, frais après fetch.
- RAW historique : `4cd819a5feedb4b3d0d4ed1ef9b3f081f68d50c0`, 30 commits derrière
  `origin/main`, 2 devant. Mécanisme de capture lu via `git show origin/main:...`.
- WIKI historique utilisé par le cron : branche
  `feat/wiki-freinage-clio3-proposals-2026-06-02`, HEAD
  `277c2ded0bd512c886b4605ce9f1eaa89c06924d` ; aucune remise à zéro.
- PR WIKI #86 relue via GitHub : OPEN, draft, tête
  `9d6d06a556621e4cf7313f69569c629fba21ebf6`, six checks SUCCESS.
- Vault : preflight natif GO sur le checkout existant ; rapport isolé depuis origin/main
  dans `/opt/automecanik/governance-editorial-pipeline-20260912`, branche
  `codex/editorial-pipeline-audit-20260912`. Ancienne branche du vault préservée.

## Analysis : carte des étapes et responsabilités

| Étape | Source / propriétaire | Mécanisme vérifié et limite |
|---|---|---|
| Besoin et rôle | role-matrix v5 ; D3 SEO, D5 contenu | R2 achat de références compatibles ; R8 contexte véhicule ; R3 intervention ; R4 explication ; R5 triage ; R6 choix avant achat. Une entité WIKI peut alimenter plusieurs usages, pas fusionner leurs promesses. |
| Recherche / capture | RAW ; gouvernance ADR-096 | `_scripts/auto-capture-runner.py:202` consomme des URLs fournies, allowlist, robots, extraction, hash. ADR-096 accepté autorise une découverte gouvernée ; l'audit du 15 juillet lui est antérieur. Activation réelle du backend de découverte non établie ici. |
| Réutilisation RAW | RAW immuable, manifests | Le runner déduplique le contenu extrait par SHA-256 (`:179`, `:237`). Cela évite un stockage doublon après fetch ; ce n'est pas une économie prouvée de requête HTTP ni de tokens. Ne pas rescraper la fiche candidate pendant cette reprise. |
| Extraction / proposition | WIKI proposals ; D3 outils | Le flux existant sélectionne des affirmations utiles, sources et blocs. `author_from_raw.py` est un point d'entrée historique identifié, son activation actuelle reste à vérifier. Références moteur/OE conservées dans RAW/catalogue si inutiles à l'explication. |
| Qualification | WIKI source policy / coverage / gates | `source_gate.py:1` contrôle same-repo ; provenance cross-repo composée ailleurs. PASS structurel ne certifie pas chaque phrase. Captures fabricant de #86 toujours à acquérir selon le dossier ; aucune nouvelle capture effectuée. |
| Décision / promotion | WIKI `promotion_decision.py:159` et `promote.py` | Décision pure compose substance, couverture, régression, provenance. `authorize_apply` revérifie les entrées. #86 reste bloquée au dernier dry-run/apply transmis ; score recalculé ici inchangé à 0,58. Ancienne preuve apply réutilisée, pas rejouée. |
| Exports SEO | WIKI `build_exports_seo.py:181` | Filtre approved + exportable.seo ; support exclu et diagnostic conditionnel R3. Métadonnées de commit par fichier pour idempotence (`:98`). Aucun export du candidat autorisé. |
| Miroir RAG | Monorepo `scripts/rag-sync/`, D6 consommation | Cron horaire installé ; source effective historique. Manifest observé 2026-09-12 08:00 UTC, 36 exports, 36 SKIP, 0 écriture. Cela prouve une recopie inchangée, pas la fraîcheur de connaissance. |
| Index RAG | Repo RAG, `scripts/importers/import_wiki_exports.py` | Filtre audience/review/truth/source/hash ; clé naturelle source/path/hash/chunk (`:412`) avant insertion. Indexation réellement activée, retrait des anciennes versions et embeddings non vérifiés. Pas de coût token chiffré sans télémétrie. |
| Projection SEO | D3 `seo-projection` | Writer : snapshot avant écriture (`:221`), restriction roles_allowed (`:335`), no-op par hash (`:440`). Extraits lus ; ni DB ni queues ni flags actuels validés. |
| Rendu | D5 R3, D3 R2/R8, D8 frontend | `r3-projection-decision.service.ts:186-188` expose READY_FOR_RENDER mais sert encore legacy ; même résultat source en fallback `:222-223`. Ce maillon ne prouve donc pas que la fiche WIKI est rendue. Aucun parcours navigateur ni publication qualifié. |

Le registry attribue rag-proxy à `@ak125/rag-team`, scripts WIKI à
`@ak125/seo-team`, blog à `@ak125/content-team`. Les désignations indiquent
l'ownership du code, pas l'autorisation de publier.

## R2/R8 : réutilisation légitime et doublons

- R8 apporte identité, version, motorisation et contexte du véhicule. R2 répond à la
  disponibilité de références compatibles et à l'achat. Réutiliser l'identité ou le
  même fait catalogue est légitime ; recopier une explication générale dans chaque
  variante ne crée pas une différence utile.
- `r2-composition.service.ts:4` construit un plan pur à partir R1/R8/MotorDelta/Cluster ;
  `r2-v2.module.ts` branche les services de signatures et snapshots. Ce constat ne
  démontre pas que toutes les pages publiques utilisent ce plan.
- `r8-diversity-check.py:156` mesure les collisions entre sœurs. Ses tests distinguent
  séquence de blocs stable attendue, FAQ absente, et FAQ présente mais identique.
  Les seuils textuels seuls ne prouvent ni différence catalogue ni cannibalisation.
- Stratégie : préserver `catalog_signature`, faire d'abord varier les données utiles
  propres au véhicule et à la compatibilité, réutiliser les preuves WIKI par rôle,
  comparer ensuite les blocs effectivement rendus. Aucun changement H1/meta/URL/indexation.

## Défauts prouvés, corrections et limites

### P1 — provenance du miroir insuffisante

Avant : `assert_source_is_exports_rag` acceptait `exports/unreviewed/rag`,
`another-wiki/exports/rag` et un lien symbolique vers un fichier RAW extérieur.
Sept tests de régression échouent contre le code de main.

Correction préparée dans le worktree applicatif : rattacher les chemins résolus au
WIKI déclaré, vérifier tous les fichiers avant copie, refuser source absente/vide,
ne pas avancer le manifest après échec de copie, rendre l'échec du manifest observable.
Le cron refuse une branche WIKI hors main et reconnaît les worktrees Git.

Limites : pas de reconstruction d'exports ni de manifeste source signé ; pas de
suppression automatique des fichiers retirés ; pas de transaction multi-fichiers.
Une copie partielle en cas d'erreur d'I/O reste possible, mais n'est plus déclarée fraîche.
Le défaut de provenance est reproduit ; aucune exfiltration ou ingestion effective
par ce défaut n'est affirmée.

### P1 — succès de sync sur une source historique

Logs réels : le 12 septembre à 10:00 heure Paris, `WARN: wiki not on main ... skipping pull`,
puis réécriture du manifest ; les deux ticks suivants indiquent un verrou occupé.
Le cron legacy auto-enrich est encore installé et échoue avec `INTERNAL_API_KEY not set`.
Ne pas lui fournir une clé pour le réactiver : il décrit une chaîne PDF → RAG → enrichissement.
Installation ne signifie pas écriture de contenu réussie. Crons inchangés dans cette mission.

Remédiation à qualifier séparément : préparer une source d'exports conforme et fraîche,
prouver le dry-run, puis proposer la bascule opérationnelle. Le correctif code seul
fera échouer explicitement la configuration actuelle ; il ne répare pas le runtime.

### P1 — titres vides comptés comme substance

Avant : le regex ne consommait que les huit premiers caractères du titre ; son reste
était compté parmi les vingt caractères requis pour une rubrique remplie.
Cinq titres longs sans explication pouvaient produire 1,00 avec sources high déclarées
et un lien existant. Correction : mesurer uniquement après la fin du titre complet,
jusqu'au titre suivant ; chaque rubrique requise ne compte qu'une fois.

Worktree WIKI `/opt/automecanik/wiki-editorial-qualification-20260912`, branche
`codex/editorial-substance-sections-20260912`. Aucun poids, seuil, source, contenu ou
statut de #86 modifié. Trois nouveaux contre-exemples échouaient avant ; ils passent après.

### P2 — score structurel utilisé comme mesure de substance

| Cas synthétique | Score avant | Interprétation |
|---|---:|---|
| Toutes rubriques renseignées, aucune liaison interne | 0,80 | Plafond inférieur au seuil 0,85 ; ne pas ajouter de lien inutile. |
| Même provenance présentée en RAW et URL, avec lien | 1,00 | Diversité de formats, aucune preuve d'indépendance. |
| Même phrase répétée sous les cinq rubriques | 1,00 | Le score ne mesure pas la valeur ni la déduplication sémantique. |
| Titres longs sans corps, avec lien | 1,00 | Bug de comptage corrigé ; pas une qualification générale de l'utilité. |
| Aucune source, rubriques et lien présents | 0,50 | Un score insuffisant ; la source doit aussi être bloquée par les gates dédiés. |
| Candidat réel filtre à huile #86 | 0,58 avant et après correctif | Reste non promu. |

Ces chiffres portent sur `compute_score`, pas sur l'éligibilité de promotion complète.
Une fixture à 1,00 n'est pas déclarée ELIGIBLE. Le score secondaire stale reste inactif.

## Correction proposée : stratégie de suite

1. Achever la qualification des deux diffs, puis PRs distinctes application et WIKI.
   Rejouer les tests uniquement si leurs entrées changent ; CI complète sur les candidats
   publiés. Aucun push/PR effectué par cette reprise.
2. Qualifier l'applicabilité de la substance avec un corpus étendu R3/R4/R6/R8 : article
   court utile, contradiction, valeur de sécurité sans contexte, doublon R2/R8 et projection
   périmée. Garder le décideur unique ; aucune baisse de seuil ni activation opportuniste
   du shadow scorer. Définir les critères avec les contrats existants avant ajustement.
3. Établir l'invalidation source retirée → proposition → export → miroir/index → projection.
   Les hashes d'idempotence ne prouvent pas cette propagation ; pas de purge aveugle.
4. Vérifier un parcours contrôlé jusqu'au rendu réel, en tenant compte du service R3 qui
   maintient legacy. La publication SEO et les changements runtime restent un lot distinct.
5. Mesurer le travail évité : captures inchangées, copies SKIP, embeddings évités, jobs et
   appels LLM réellement supprimés. Stockage en octets ≠ tokens injectés. Aucun gain financier
   ni nombre de tokens économisés n'est revendiqué à ce jalon.

## Validation

- Synchronisation : 10 tests temporaires, avant 7 échecs / après 10 PASS ; simulation,
  relecture identique sans copie ni modification du mtime, frontières de provenance,
  absence de source et erreurs d'I/O. `bash -n` cron et `git diff --check` PASS.
- WIKI : 96 tests PASS (contrat schéma/scorer, promote, promotion_decision). Sous-suite
  avant correctif : 3 échecs / 11 succès. Seuil et gardes inchangés.
- R8 : 30 tests existants PASS ; aucun appel DB.
- Comparaison arithmétique avant/après sur les 24 fiches parseables de proposals/wiki
  du runtime WIKI : 0 score modifié, 0 erreur, 0 franchissement du seuil. Ce contrôle
  ne certifie pas leurs affirmations et ne réécrit aucun frontmatter. Résultat JSON adjacent.
- #86 : six CI SUCCESS relues, distinctes des tests des nouveaux correctifs.
- Logs reproductibles : dossier `editorial-pipeline-evidence-20260912/` adjacent.

## Coverage manifest

Voir `editorial-pipeline-evidence-20260912/coverage.json`. Lecture ciblée et partielle ;
les extraits ne valent pas lecture intégrale. Non couverts : vérité de tout le corpus,
DB partagée, Weaviate live, activation découverte, files BullMQ, télémétrie LLM,
parcours navigateur, PREPROD et PROD. Corrections préparées dans des branches isolées
sur autorisation de reprise ; aucune livraison runtime. **PARTIAL_COVERAGE**.

## Transfert complémentaire reçu : acquisitions admin vers RAW

La demande transmise depuis Hermes est intégrée à ce chantier, sans nouvelle tâche.
PR RAW #50 revérifiée OPEN/draft, commit `90e901ca20d82323d5faa9f1025d80dc064a7c06`,
worktree `/home/deploy/worktrees/raw-acquisition-routing-20260912` propre ; les deux
jobs Python 3.11/3.12 sont SUCCESS. Les 219 tests locaux et quatre contre-épreuves
sont des preuves transférées, non rejouées ici. Le correctif Gate J / persistance
atomique n'est pas dupliqué dans les branches de ce jalon.

Les routes `admin/cleanup/apply` et `admin/ingest/video/single` ont été relues dans
le contrôleur. Elles appellent encore les services RAG. La CLI RAW reste une capture
HTML, pas une API média. La suite doit cartographier producteurs RAW, protections
réseau et contrats binaires, puis raccorder les routes avec leurs clients conservés.
L'affectation image à une page reste publication après validation. Aucun branchement
admin vers RAW ni support binaire n'est déclaré réalisé par ce jalon.

Validation documentaire : G2 0 orphelin, 0 wikilink cassé. Diffs applicatifs et WIKI
sélectionnés dans leur index Git et copiés en patch dans les preuves ; non committés,
non poussés. Les nouveaux correctifs ne disposent pas encore de CI distante.


## Suite du jalon : transport réseau du producteur RAW

### Scan et analyse

Relecture de la CLI RAW, de ses tests, de `raw-contract.md`,
`agent-capture-policy.md`, des hooks CI et des clauses réseau ADR-096. Recherches
ciblées RAW/app/RAG : aucun transport sortant protégé réutilisable trouvé dans les
zones explorées. Ce constat ne certifie pas l'absence dans tous les dépôts.

La CLI utilisait `urlopen` avec redirections automatiques et lecture sans plafond ;
`RobotFileParser.read()` constituait une deuxième entrée réseau sans ces contrôles.
La route admin vidéo appelle encore `yt-dlp` et écrit dans `_raw/videos` côté RAG.
Le producteur HTML ne remplace pas ce chemin média.

### Correction isolée

Worktree `/home/deploy/worktrees/raw-capture-network-20260912`, branche
`codex/raw-capture-network-20260912`, base exacte de PR RAW #50 :
`90e901ca20d82323d5faa9f1025d80dc064a7c06`. Trois fichiers indexés, non committés :
runner étendu, `_scripts/capture_http.py`, `_scripts/tests/test_capture_http.py`.
Aucune modification de la branche originale de #50.

Le transport commun vérifie HTTPS, port 443, absence d'identifiants, allowlist/deny,
adresses publiques sur toutes les réponses DNS ; la connexion utilise l'adresse
numérique validée et conserve la vérification TLS du nom. Chaque requête, y compris
robots et redirections, repasse ces contrôles. Une redirection doit rester dans la
même entrée de politique d'allowlist ; robots est recontrôlé sur la destination HTML.
Pas de proxy ambiant, cookies ou redirection implicite.

Plafonds : HTML 2 MiB, robots 256 KiB, quatre redirections par ressource, douze
requêtes par capture. Lecture bornée même sans Content-Length ; réponses compressées,
MIME inattendus, contrôles binaires et signatures incompatibles refusés. La licence
restreinte configurée est refusée avant le réseau. Gate J et la persistance atomique
de #50 restent l'unique voie d'écriture.

La limite de 90 secondes est vérifiée entre opérations et lectures de corps. Elle
n'interrompt pas le résolveur DNS système ni toute lecture d'en-têtes : ce n'est pas
une garantie dure de durée totale. Les limites restent par capture, pas un budget
partagé de campagne. Un HTTP 200 ne prouve pas l'absence de paywall ni la licence ;
la pertinence, les injections textuelles et le source_score restent à qualifier.
Les binaires sont refusés, pas ingérés ; aucune preuve PDF/image/vidéo acquise ici.

### Validation et verdict

- Commande native du hook : `python3 -m pytest _scripts/ -q` : **271 PASS**.
- Contre-épreuves sur `fetch` : la base accepte quatre cas dangereux simulés
  (HTTP, DNS privé, flux trop gros, PDF déclaré HTML) ; le candidat les refuse tous.
- Tests de parcours interne : réponses HTTP simulées → extraction → vrai Gate J →
  écriture dans un dossier temporaire → rejeu sans deuxième source. Un refus réseau
  ne crée aucune source. Aucune requête réelle ni source durable ajoutée au corpus.
- `git diff --cached --check` PASS. Suite automatiquement couverte par le hook
  `raw-scripts-tests` existant ; aucune configuration CI changée. **CI distante non
  exécutée sur ce nouveau candidat**, distincte de celle de PR #50.
- Patch et logs `raw-network-*` dans le dossier de preuves adjacent.

**PARTIAL_COVERAGE**. Le producteur HTML est durci dans une branche isolée ;
`admin/cleanup/apply` et `admin/ingest/video/single` ne sont pas raccordés à RAW.
Prochaine action : établir le contrat serveur d'acquisition et les enveloppes médias
existantes, puis raccorder les appels admin sans assimiler acquisition et affectation
à une page. Les clients d'affectation d'images restent préservés.


## Jalon suivant : réception du texte admin dans RAW

### Scan et analyse

Le schéma RAW `recycled-frontmatter.schema.json` et le contrat existant autorisent
la matière recyclée `secondary` / `to_verify`, sans autorité de publication. Le
corps reçu d'un client admin ne prouve pas qu'une URL a été téléchargée : sa
provenance doit rester déclarée. Aucun appel littéral frontend à `cleanup/apply`
n'a été trouvé dans les recherches ciblées ; les clients externes restent inconnus.

### Correction préparée et raccordée dans le candidat

`admin/cleanup/apply` garde son chemin et ses deux gardes (session + admin), mais
appelle maintenant `RawAcquisitionClientService`. Il ne transmet plus de décision
client à `RagCleanupService.applyIngest`. Le champ `decision` reste accepté pour
compatibilité mais est ignoré. Les chemins internes `syncFiles` et les affectations
d'images aux pages ne sont pas modifiés.

Le client filtre les champs de matière source puis appelle la CLI possédée par le
dépôt RAW, via `python3` et stdin JSON, sans shell. Le processus ne reçoit ni secrets
applicatifs ni identifiants DB. Sa réponse est validée : destination RAW, chemin
lié au reçu, état `to_verify`, `retrievable=false`, jamais PLAN ou active.

Le runner RAW existant est étendu par `--submission-stdin` ; aucun téléchargement
n'a lieu dans ce mode. Il construit le frontmatter avec le schéma natif recyclé,
force L4/to_verify et `source_url_verified=false`, conserve le corps soumis, refuse
la PII évidente et réutilise Gitleaks avant stockage durable. Le contrôle Gate J de
la voie URL est conservé. Les deux voies partagent la publication atomique existante
sans écrasement, factorisée dans le même runner.

Identité du reçu : URL déclarée normalisée (ou clé source) + SHA-256 du corps exact.
Rejeu identique → même reçu, fichier et mtime préservés ; corps modifié → nouvelle
source immuable, reliée par `source_identity_hash`. Une modification des seuls
métadonnées ne remplace pas le premier témoin. Les inventaires/checksums/lineage
sont générés par `regen-manifests.py`, sans format parallèle. Le producteur verrouille
sa séquence locale ; une erreur d'inventaire conserve la source et renvoie un échec.
Le rejeu répare les inventaires avant de rendre un succès. Ce verrou ne coordonne
pas encore les autres producteurs historiques du dépôt.

Le reçu est un ID SHA-256 RAW, pas l'ancien ID DB RAG. Exemple :
`{action: RECEIVED, destination: raw, status: to_verify, retrievable: false, duplicate: false}`,
avec `id`, `raw_path` et `content_hash`. Une matière refusée donne 422 ; producteur
absent, panne ou reçu invalide donnent 503, sans repli vers une écriture RAG.

### Conditions d'activation, encore non appliquées

Le serveur doit disposer de `RAW_ACQUISITION_SCRIPT` (chemin absolu du runner RAW
corrigé) et de `RAW_GITLEAKS_BIN` (binaire Gitleaks qualifié), plus Python avec les
dépendances RAW natives et Git. Ce sont les coordonnées des outils producteurs,
pas un flag de publication. La configuration consommateur `AUTOMECANIK_RAW_PATH`
n'est pas utilisée comme destination d'écriture. Le producteur doit viser un
checkout de réception isolé et writable ; ni le RAW historique ni WIKI runtime.
Aucune configuration, unité systemd, permission ou montage n'a été livré ici.
Le Gitleaks du cache pre-commit a été utilisé uniquement pour les preuves temporaires,
pas retenu comme chemin d'installation d'exploitation.

Information de coordination reçue : le traitement quotidien WIKI utilise désormais
`knowledge-jobs.timer` et le verrou `wiki-validation-reports/validation.lock`.
Guide de transfert lu ; état du service non requalifié en direct pendant ce lot.
Aucune modification de ce service ni de son checkout WIKI.

### Validation

- RAW : **286 PASS**, commande native `python3 -m pytest _scripts/ -q` ; la preuve
  réseau précédente est incluse dans cette nouvelle suite après factorisation.
- NestJS : **15 PASS**, client et délégation du contrôleur, gardes conservées,
  décision forgée ignorée, absence de repli, reçu incohérent et délai dépassé refusés.
- **Typage backend complet PASS**, `tsc --noEmit` avec cache temporaire séparé.
- **ESLint ciblé PASS**, cinq fichiers applicatifs ; `git diff --cached --check` PASS.
- **CLI réelle + Gitleaks réel + Gate A + inventaires natifs PASS** dans un dépôt
  temporaire : réception, doublon, nouvelle version et faux secret refusé sans ajout.
- **Client Nest réel → CLI RAW réelle PASS** dans un dépôt temporaire : décision
  client supprimée, frontmatter L4/to_verify, reçu stable et inventaires présents.
- Aucune requête réseau, DB, capture de source externe ou modification du corpus
  runtime dans ces preuves. Pas de parcours HTTP complet ni de navigateur certifié.
- Les avertissements ts-jest sur les fichiers JS déjà compilés de `seo-roles/dist`
  concernent la configuration inchangée de transformation JS ; les deux suites ont passé.

### Verdict et suite

**VALIDATED_FOR_SCOPE_ONLY** pour la réception de texte dans les essais isolés ;
**PARTIAL_COVERAGE** pour tout le pipeline. Les cinq fichiers applicatifs et le
runner/test RAW supplémentaires sont indexés mais non committés/poussés. Les patches
séparent le premier lot réseau, son extension admin, et leur combinaison.
La voie `admin/ingest/video/single` appelle toujours le service RAG historique :
le support binaire, le raccordement vidéo et son activation restent à réaliser.
La calibration par rôle, les sources de #86 et le rendu éditorial restent également
ouverts ; aucune validation WIKI ou publication n'est déduite d'une réception RAW.


## Jalon vidéo — validation et raccordement isolés

Scan : ancien `RagVideoManagementService.ingestVideoUrl` téléchargeait avec yt-dlp
vers RAG et créait des sidecars destinés à l'édition. yt-dlp absent sur l'hôte ;
répertoire vidéo par défaut contrôlé vide (une éventuelle surcharge runtime n'est
pas exclue). Aucun appel frontend littéral de cette acquisition trouvé. Les opérations
de liste/stream/affectation et l'affectation des images aux pages sont conservées.

Analyse : la réception d'un média n'autorise ni sa publication ni son indexation.
Le producteur doit conserver les octets, la provenance et les versions avant qualification.
Les plateformes vidéo ne figurent pas dans l'allowlist native ; aucune extension faite.

Correction préparée sous autorisation dans les worktrees : route admin vidéo existante
→ client RAW → mode natif `--video-stdin`. Suppression de l'ancien téléchargeur RAG.
Réception de vidéos directes MP4/MOV/WebM/Matroska après le transport HTTPS/robots/DNS
public et limites de taille. ffprobe local s'exécute dans un namespace réseau isolé,
avec limites temps/mémoire/protocoles. Scanner textuel et Gate J avant stockage.
Blob identifié par SHA256, témoin par URL canonique+hash ; sources distinctes peuvent
partager un blob, une version différente conserve le témoin précédent. Manifestes
natifs, sidecar et LFS vidéo ; un échec conserve les sources et le rejeu répare.
Un verrou Git non bloquant commun couvre captures URL, soumissions texte et vidéo.
Les délais durs DNS/en-têtes terminent le worker réseau ; le client utilise GNU timeout
pour borner le groupe des sous-processus. Le détail d'activation est préparé dans
`raw-media-activation.md` (aucune configuration runtime effectuée).

Validation : **293 tests RAW** sur `_scripts/tests/` PASS, dont 9 nouvelles preuves
média sur Gate J/manifests réels et réseau/probe simulés. **25 tests Nest** sur deux
suites PASS ; ESLint six fichiers et typage backend complet PASS après correction
de deux erreurs de forme/import. `raw-media-bridge-proof.cjs` exécute le vrai client
Nest, timeout, CLI RAW, allowlist, ffprobe isolé, Gitleaks et manifestes sur MP4/WebM
synthétiques ; réseau externe simulé explicitement. Reçu stable au rejeu, octets
préservés, 0 appel DB. La preuve texte client→CLI a aussi été rejouée après le changement
de lanceur et passe. Les anciens tests sync/scorer/R8 inchangés sont réutilisés.

Preuves : `raw-media.patch` et `admin-media-routing.patch` sont les deltas du jalon
précédent ; `raw-all-acquisitions.patch` et `application-all-acquisitions.patch` sont
les candidats cumulés. Voir `raw-media-tests.log`, `raw-media-bridge-proof.log`,
`raw-admin-bridge-after-media.log`, `raw-media-lint.log`, `raw-media-typecheck.log`
et `raw-media-proof-dependencies.json`. Logs lint/typage vides = sortie0 vérifiée,
le résultat Nest est consigné depuis la sortie de session (pas présenté comme log brut).

Verdict : **VALIDATED_FOR_SCOPE_ONLY** pour ces corrections isolées ; le parcours
complet reste **PARTIAL_COVERAGE**. Téléchargement fabricant réel, conteneur déployé,
retour HTTP/navigateur et droits de réception restent à valider séparément. Le scanner
textuel ne certifie pas l'absence de PII dans les images/sons. Aucun export, merge,
push, promotion, changement du timer knowledge-jobs ou du verrou WIKI.

Prochaine action poursuivie : preuve de retrait/version périmée et calibration sur
contre-exemples, puis rendu représentatif selon les contrats des rôles existants.


## Consommation et clôture du diagnostic borné

[[ledger/audit-trail/editorial-pipeline-evidence-20260912/editorial-consumption-findings|Détail consommation, retrait, calibration et rendu]].
[[ledger/audit-trail/editorial-pipeline-evidence-20260912/raw-media-activation|Préparation du raccordement média]].

Nouveau correctif RAG : corps Markdown conservé et corps vide refusé ;25 tests PASS,
2 régressions avant. Nouveau correctif RAW : manifest_id natif et reprise inventaire/
worklist, scanner avant capture HTML ;296 tests PASS. Les anciennes sources sont préservées.
Les preuves des lots médias/texte déjà qualifiés restent réutilisables : leurs chemins
ne sont pas modifiés par la dernière correction de capture HTML.

Retrait : une source absente laisse sa copie miroir, synced_at avance ; l'index simulé
conserve aussi les versions remplacées/retirées. La correction du corps importé ne
prétend pas réparer cet historique. Le dossier propose rapprochement explicite des
snapshots et invalidation ciblée des dépendances, sans suppression automatique.
Calibration :8 contre-exemples arithmétiques et6 fixtures qualité natives ; seuils
inchangés. Les tests du décideur déjà verts gardent leur valeur sur le périmètre inchangé.
Rendu :44 tests R3 PASS confirment la source legacy même lorsque la projection est prête.
Le rendu d'une fiche WIKI qualifiée jusqu'au navigateur reste non démontré.

Les candidats applicatif, RAW, WIKI et RAG sont indexés dans leurs worktrees respectifs,
non committés, non poussés, non déployés. Le checkpoint et le coverage manifest désignent
les corrections, preuves réutilisables et limites. Le périmètre global reste
**PARTIAL_COVERAGE**, sans changement du passage quotidien knowledge-jobs.


### Inventaire réel final — lecture seule

Le complément d'inventaire distingue maintenant les couches : collection Weaviate
KB_Knowledge_v2 absente ; tables de projection SEO examinées vides ;619 lignes SQL
__rag_knowledge sans corps vide, dont8 lignes non actives encore retrievable=true.
Les chemins SQL lus filtrent status=active : exposition non démontrée. Le Weaviate
legacy contient9945 objets Knowledge (voir les autres comptes dans l'inventaire).
Ces constats ne sont ni une migration ni une validation de bout en bout. Le parcours
qualifié demeure bloqué avant sa cible d'index et avant son rendu ; aucun fallback
vers un producteur RAG de contenu n'a été ajouté. Les preuves DB ci-dessus sont des
SELECT de métadonnées/comptes, pas des validations de migrations ou de publication.

## Extension explicite — tous les rôles éditoriaux

[[ledger/audit-trail/editorial-pipeline-evidence-20260912/all-role-coverage|Matrice complète par rôle, parcours représentatifs et limites]].

**Scan / analysis** : contrats v5 + code courant, R1/R2/R3/R6/R7/R8 et ligne R9
explicite. R9_GOVERNANCE est déprécié vers G* ; clarification utilisateur demandée,
sans nouvelle définition inventée. Les identifiants R0/R4/R5 rencontrés sont également
situés dans la matrice. Sources admissibles, édition, projection, rendu, retraits,
duplication, interactions et niveaux de preuve sont distingués par rôle.

**Correction autorisée, candidate à livraison** : sync refuse les miroirs non
réconciliés avant copie ; builder SEO WIKI refuse les anciens exports sans source
éligible avant écriture du lot ; aucune suppression. R7 utilise uniquement les FAQ
curées et un score élevé ne peut plus transformer un hard gate échoué en PUBLISH.
Aucun seuil, URL, metadata optimisée ni contenu DB existant modifié.

**Validation** : 14 tests sync (4 nouveaux échecs avant), 68 tests exports WIKI
(4 échecs de retrait avant), 6 tests R7 (4 échecs avant), 20 tests writer dont 12
nouveaux cas couvrant les six rôles, 73 tests contrats/indexabilité, 14 tests structure
R2. Les passages 69 tests ciblés et 21 tests R7/admission se recouvrent : ne pas
additionner les comptes. Lint TS, typage backend complet et hooks WIKI ciblés PASS.
Les preuves RAW 296, acquisitions Nest 25, RAG 25, scorer 96 et R3 44 inchangées ne
sont pas rejouées sans motif.

**Verdict** : PARTIAL_COVERAGE ; sync/exports/R7 VALIDATED_FOR_SCOPE_ONLY. Les
patches cumulatifs actuels sont `application-all-roles.patch` et `wiki-all-roles.patch` ;
les anciens patches restent les preuves de leurs jalons. `candidate-state.json`
porte l'état indexé courant. Rien committé, poussé, activé, promu ou déployé.

Les gardes de retrait rendent les incohérences observables ; elles ne réalisent pas
encore la propagation source→outbox→versions→caches→index→page. R2/R6/R8 conservent
des producteurs legacy à re-sourcer ; WIKI→R1, WIKI→R7 et les consumers/renderers
restants sont détaillés dans la matrice. Le chemin R3 ne vaut pas preuve des autres
rôles. Toute suite maintient les frontières d'activation/publication existantes.

## Reprise : consolidation, retraits et versions remplacées

Voir [[ledger/audit-trail/editorial-pipeline-evidence-20260912/method-consolidation|matrice conserver/unifier/migrer/retirer/à confirmer]].
Le candidat RAG possède maintenant un utilitaire de suppression confirmée partagé par ses
consommateurs existants : remplacement F5 et retrait admin natif. Source_path exact et UUID
remplacent l'ancien raccordement erroné parent_id ; retrait interrompu reprenable, hash vérifié,
pas de purge des exports absents/rejetés, pas de faux succès CLI, verrou unique et refus de
force-reembedding sans embeddings.54 tests ciblés PASS, contre-épreuves et logs bruts conservés.
R9 : transition vers G* confirmée, compatibilité conservée ; deux suites74 PASS.

Contrôle SQL en lecture seule : l'outbox possède554 événements historiques, aucun pending,
new_hash NOT NULL et aucune colonne entity_id. Les processors courants enqueuent encore un
refresh singleton générique sans passer par cette outbox. Le raccordement de retrait WIKI→
outbox→projections/rendu reste à préparer après représentation canonique des identités/états.
Aucun rôle activé, aucun changement knowledge-jobs, aucun push/merge/deploy ni suppression réelle.
Verdict maintenu **PARTIAL_COVERAGE**.


## Lot suivant — cohérence du snapshot et proposition outbox

**Scan** : chemins d'écriture/refresh relus, archive et captures d'exports inspectées,
ADR-090 §A/B relu. Coverage : manifeste actualisé avec chemins et hashes.

**Analysis** : une triple lecture permettait d'archiver des octets différents de
ceux effectivement projetés. Les noms d'exports identiques rendaient une archive
ambiguë. Le contrat outbox conserve new_hash NOT NULL sans entity_id physique ;
le refresh actuel reste singleton direct. Frontmatter ADR090 accepted et mentions
proposed/draft dans le corps divergent ; anomalie signalée sans modifier le canon.

**Correction (proposée/préparée sous autorisation utilisateur)** : quatre fichiers
app corrigés dans le worktree isolé, capture unique et refus des noms dupliqués,
signature publique/format conservés. Patch cumulatif :
`editorial-pipeline-evidence-20260912/application-snapshot-consistency.patch`.
Voir [[ledger/audit-trail/editorial-pipeline-evidence-20260912/withdrawal-outbox-design|proposition concrète non normative de propagation des retraits]].
Elle réutilise outbox/runs/queues et détaille les décisions owner ; raccordement
non implémenté et aucune migration préparée comme si le contrat était acquis.

**Validation** : 3 régressions échouaient avant correction ; **39 tests PASS,
3 suites**, lint quatre fichiers puis dernier test modifié, typecheck backend PASS.
Le journal final est `snapshot-consistency-verified-tests.log` ; un intermédiaire
`final-tests.log` conserve une erreur de helper de test ensuite corrigée, pas une
régression runtime. Baselines/logs historiques conservés. RAG54 et rôle74 inchangés
réutilisables ; aucun résultat cumulé assimilé à un test de bout en bout.

**Verdict** : PARTIAL_COVERAGE. Prochain raccord soumis à l'évolution owner du
contrat ADR090. Pas d'activation, de suppression réelle, de publication ou de CI
nouvelle. Les octets sont cohérents mais leur appartenance à un snapshot source
unique approuvé reste à prouver en amont.


## Lot identités de blocs et filiation WIKI

**Scan** : schéma export WIKI, builder et mapper/writer/garde natifs relus ;
jonctions concrètes détaillées dans la proposition outbox, section9.
**Analysis** : normalisation de sections, index positionnels et overrides pouvaient
produire le même block_id ; l'écriture séquentielle acceptait les collisions.
Le source_wiki_commit est propre à chaque fiche et informatif ; une exigence de
commit identique pour tout le lot aurait contredit le builder existant.

**Correction (proposée/préparée sous autorisation)** : trois fichiers app modifiés ;
identités résolues une fois et vérifiées avant toute écriture de l'entité, lignes
réutilisées, périmètre rôle conservé. Pipeline1.0.1 ; signature publique inchangée.
Patch cumulatif `editorial-pipeline-evidence-20260912/application-block-identity.patch`.
Proposition de retrait amendée, sans nouvelle convention canon ni garde mono-commit.

**Validation** : baseline5 échecs ; **47 PASS/3 suites**, lint3 fichiers et tsc
backend PASS, journaux `block-identity-verified-*.log`. Test avec garde réelle,
archive temporaire et DB simulée : preuve conservée, conflit visible, run failed,
aucune version active pour l'entité ambiguë. L'erreur intermédiaire de type du
helper est corrigée en réutilisant le type de méthode réel, sans copie divergente.

**Verdict** : PARTIAL_COVERAGE. Pas de réconciliation des collisions historiques,
renommages ou identifiants positionnels. Pas de preuve runtime/CI nouvelle. Les
47 tests remplacent les39 du lot précédent dans ce périmètre, sans les additionner.


## Lot corpus réel — collision R8 par motorisation

**Scan** :3 exports,9 fiches WIKI,15 propositions métier dans deux checkouts du même
HEAD main vérifié ;58 fichiers hashés,4 documents navigation/qualité exclus.
Détails : [[ledger/audit-trail/editorial-pipeline-evidence-20260912/editorial-duplicate-findings|constats de doublons et collisions réels]].
**Analysis** : deux collisions logiques dans la proposition ScénicII non éligible ;
quatre contenus différents, aucun à supprimer comme doublon. Le mapper omettait
l'axe moteur déjà fourni par WIKI dans l'identité R8. Le cas Symptômes/symptomes
reste une fixture, pas une observation de données publiées.

**Correction (proposée/préparée sous autorisation)** : mapper existant étendu à l'axe
R8 ; mêmes contenu/kind, IDs autres rôles/sans axe/explicites préservés. Pipeline1.1.0,
revue de convention d'identité ADR090 §A avant livraison. Patch cumulatif
`editorial-pipeline-evidence-20260912/application-r8-scope.patch`.

**Validation** :3 baseline failures ;53 tests PASS/3 suites, lint et tsc PASS.
Même corpus :0 collision après correction sans perte de blocs ou modification de
sources. SELECT de compteurs en lecture seule :0 ligne dans __seo_content_blocks
et __seo_content_block_versions. Aucun écrit DB ni projection réelle effectuée.

**Verdict** : PARTIAL_COVERAGE. Pas de preuve globale d'absence de doublons ou d'impact
sur le site ; legacy RAG, prose non projetée et rendu public hors de ce contrôle.
Rejeu historique, ordre des axes au rendu et raccord outbox restent à qualifier.


## Suite autorisée « corriger » : rejeu historique R8

Protection réalisée dans le candidat contre coexistence ancien ID actif / nouveaux
ID par motorisation, avant facts/blocs ; erreur DB également bloquante. 58 tests
PASS, lint/tsc/diff-check PASS, mapper natif et 58 hashes sources inchangés.
Voir [analyse et limites](editorial-pipeline-evidence-20260912/editorial-duplicate-findings.md).
Patch courant : application-r8-legacy.patch. Aucun déploiement ni écriture DB.
PARTIAL_COVERAGE.


## Suite : faux acquittements du consumer refresh

Le candidat exige la confirmation des deux vues et transmet les échecs opérationnels
à Bull. READ_ONLY préservé.10 contre-épreuves échouaient avant ;72 tests PASS/4 suites
après, lint et tsc PASS. Pipeline1.1.1/runner1.0.1.
Voir [correction, preuves et limites](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#11-consumer-existant--correction-des-faux-acquittements).
Patch courant application-refresh-ack.patch. Outbox non raccordée, aucune DB réelle
modifiée ou activation. PARTIAL_COVERAGE.


## Suite : transaction bloc et outbox éditoriale

**Scan/analysis** : schéma natif et outbox existante ; risque de double écriture et
rejeu périmé. **Correction préparée sous autorisation** : RPC transactionnelle pour
remplacement/retrait d'un bloc existant, événement dans __rag_change_events, historique
conservé, verrou et prédécesseur attendu, rejeu exact sans effet.
**Validation** :18 tests PASS sur PostgreSQL17.11 éphémère ; rollback par panne outbox,
concurrence réelle, retrait/rejeu, intégrité historique et privilèges. SQL lint,
marqueur migration et diff-check PASS. Deux exceptions SQL locales documentées.
**Verdict** :PARTIAL_COVERAGE. RPC non raccordée au writer, aucun ACK consumer durable,
aucune migration partagée ni activation. Le raccord exige l'acceptation WIKI et le snapshot
persisté avant écriture. Détail et limites :
[transaction éprouvée](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#12-transaction-existante-bloc--outbox--candidat-éprouvé-sur-postgresql).
Patch courant : application-block-outbox.patch ; block-outbox-verification.json.


## Suite : writer raccordé aux remplacements transactionnels

**Scan/analysis** : référence snapshot tardive, upsert d'identité et provenance SQL.
**Correction préparée** : snapshot confirmé en DB avant les écritures ; remplacement
par callRpc avec préconditions ; refus d'un bloc retiré, d'une réaffectation ou d'un
résultat non confirmé. source_type exact conservé. Pipeline1.2.0.
**Validation** :89 tests/4 suites PASS avec transport simulé et wrapper natif ;18 tests
PostgreSQL17.11 PASS séparément ; lint, tsc et contrôles migration PASS.
**Verdict** :PARTIAL_COVERAGE. Remplacement raccordé dans le candidat ; retrait WIKI
explicite, relais et ACK durables restent à raccorder. Pas d'atomicité globale facts/blocs,
ni de preuve PostgREST/queue/public. Aucun déploiement ou migration partagée.
Détails : [raccord writer](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#13-raccordement-du-writer-aux-remplacements-transactionnels).
Patch courant application-writer-outbox.patch ; writer-outbox-verification.json.


## Suite du 13 septembre : progression partielle et échec du job

**Scan/analysis** : perte des compteurs après exception, refresh omis et job completed
malgré run failed. **Correction préparée** : progression conservée par entité, conflit
avec effets déjà rapportés, refresh sur blocs partiels puis échec transmis à Bull.
**Validation** :5 contre-épreuves rouges avant ;97 tests PASS/4 suites après ; lint4
fichiers, tsc backend et diff-check PASS. Bull natif, transports/transitions simulés.
SQL18 antérieurs réutilisés après contrôle des hashes inchangés.
**Verdict** :PARTIAL_COVERAGE. Pas d'atomicité globale ou reprise durable démontrée,
aucune DB partagée/activation. Voir [progression partielle](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#14-écritures-partielles-et-état-réel-du-job--13-septembre-2026).
Patch courant application-partial-write.patch ; partial-write-verification.json.


## Suite du 13 septembre : acquittement de la projection et reprise native

**Scan/analysis** : refresh sans ACK durable, enqueue perdu non repris par un writer noop.
**Correction préparée** : capture exacte des événements visibles, refresh des deux vues
et ACK projection atomiques ; reprise des pending par le writer et le singleton existants.
**Validation** :24 tests PostgreSQL17.11 PASS avec concurrence et rollback réels ;
106 tests/5 suites applicatives PASS avec transports simulés ; ESLint, tsc, SQL lint,
marqueur natif et diff-check PASS. Aucun baseline rouge revendiqué pour ce lot.
**Verdict** :PARTIAL_COVERAGE. Reprise dépendante d'un prochain passage writer ; aucune
activation ou migration partagée. Retraits WIKI acceptés et autres consommateurs restent
à raccorder. Voir [acquittement et limites](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#15-acquittement-transactionnel-de-la-projection-et-reprise-native--13-septembre-2026).
Patch courant application-refresh-ack.patch ; refresh-ack-verification.json.


## Suite du 13 septembre : reprise après completed et redémarrage

**Scan/analysis** : singleton actif absorbe add(), et contrôle avant completed trop tôt.
**Correction préparée** : réconciliation outbox dans les hooks natifs completed et
onModuleInit non bloquant, même file/job/debounce, READ_ONLY et retries bornés conservés.
**Validation** :119 tests/6 suites PASS dont7 Redis réel avec wiring Nest/Bull ;
ESLint6 fichiers, tsc et diff-check PASS. SQL24 réutilisés après hashes inchangés.
**Verdict** :PARTIAL_COVERAGE. Reprise sur fin réussie/redémarrage sain, sans relais
périodique autonome ; une panne du hook ou des retries épuisés reste observable et
pending. Pas de SIGKILL ou chaîne PostgREST intégrée prouvés, aucune activation.
Voir [reprise native](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#16-reprise-du-singleton-à-la-fin-du-job-et-au-redémarrage--13-septembre-2026).
Patch courant application-queue-recovery.patch ; queue-recovery-verification.json.


## Suite du 13 septembre : diagnostic de réconciliation WIKI

**Scan/analysis** : validation WIKI automatique confirmée ; statut deprecated sans
contrat de retrait accepté dans le moteur natif. **Correction préparée** : rapport
JSON dans le builder existant, identité/empreintes/motif et conservation du lot ;
aucune absence transformée en suppression. **Validation** :102 tests PASS dont88
builder et14 score/schema ;3 contre-épreuves rouges avant correction ; compilation,
hooks natifs et diff-check PASS. **Verdict** :PARTIAL_COVERAGE. Observations non
vérifiées, aucune décision de retrait ou connexion consommateur produite, aucune
mutation corpus/DB ou activation. Voir [diagnostic WIKI](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#17-observations-de-retrait-dans-le-builder-wiki-existant--13-septembre-2026).
Patch WIKI courant wiki-withdrawal-observations.patch ; withdrawal-observations-verification.json.


## Suite du 13 septembre : prédécesseur WIKI et contrat de transition

**Scan/analysis** : baseline native implicite absente du manifeste ; révision moteur
non comparée pendant l'évaluation. **Correction préparée** : capture canon_target
présent/absent indépendamment de l'override baseline, refus des changements de cible
ou moteurs, erreurs de recapture typées. Contrat de transition proposé dans le
[document existant, §18](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#18-contrat-proposé-de-transition-wiki-et-fraîcheur-du-prédécesseur--13-septembre-2026),
sans autorité nouvelle. **Validation** :199 tests PASS/4 fichiers ;15 nouveaux tests,
dont9 rouges avant correction ; compilation, hooks2 fichiers et diff-check PASS.
**Verdict** :PARTIAL_COVERAGE. Aucun retrait branché, garde anti-écrasement conservé.
Application des octets évalués, acceptation durable et mapping consommateurs encore
à éprouver ; aucune mutation de corpus/DB, activation ou livraison.
Patch WIKI courant wiki-transition-inputs.patch ; transition-inputs-verification.json.


## Suite du 13 septembre : contenu appliqué lié à la décision WIKI

**Scan/analysis** : fm/body chargés avant décision pouvaient diverger du contenu évalué.
**Correction préparée** : exécuteur reçoit décision complète, parse les octets dont
le hash est vérifié, contrôle le statut et revérifie avant écriture ; proposition
changée pendant écriture conservée avec effet partiel explicite. **Validation** :
209 tests PASS,10 nouveaux dont3 rouges avant correction ; compilation, hooks3
fichiers et diff-check PASS. **Verdict** :PARTIAL_COVERAGE. Courses filesystem et
écriture partielle non atomiques restent ouvertes, aucune propagation de retrait.
Voir [contenu appliqué, §19](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#19-décision-liée-au-contenu-appliqué-par-le-promoteur--13-septembre-2026).
Patch WIKI courant wiki-applied-snapshot.patch ; applied-snapshot-verification.json.


## Suite du 13 septembre : publication atomique et consolidation

**Scan/analysis** : absence de verrou promoteur et publication directe ; code de
sortie 0 même après échec. **Correction préparée** : flock natif par checkout,
publication atomique du canon avec fsync et statut d'échec explicite texte/JSON.
**Validation** :216 tests PASS, deux processus réels et SIGKILL avant publication ;
hooks3 fichiers, compilation et diff-check PASS. Hashes des candidats app/RAW/RAG
inchangés ; preuves antérieures conservées comme historiques. **Verdict** :
PARTIAL_COVERAGE. Auteurs source non coopératifs et transaction multi-fichiers hors
garantie. Le déclencheur métier du retrait complet attend la réponse utilisateur ;
aucun retrait implicite n'a été inventé. Voir [consolidation, §20](editorial-pipeline-evidence-20260912/withdrawal-outbox-design.md#20-publication-atomique-native-et-consolidation-du-candidat--13-septembre-2026).
Patch WIKI courant wiki-atomic-promotion.patch ; candidate-consolidation.json.


## 2026-09-13 — boucle de contenu et validité des scores

### Scan

Reprise après le doute utilisateur sur les scores et les sources utiles. Lecture seule
sur les runtimes ; contre-exemples synthétiques hors corpus. Application candidate
10 commits derrière origin/main d1457bf0 ; les deux services de score et leurs
configurations lus sont identiques à main. WIKI 01cea8de frais. Inventaire exact des
lectures VPS, hashes, exclusions et observations dans
[content-loop-score-diagnosis.json](editorial-pipeline-evidence-20260912/content-loop-score-diagnosis.json).

### Analysis

1. **Score de section trompeur comme mesure d'excellence.** Appel du vrai
`ConseilQualityScorerService.scoreSection`, seuls décorateurs et constructeur DB
substitués : S1 contenant « banane » répété 60 fois et `sources=not-a-source` obtient
100/100 sans pénalité ; sans source, 85/100. Ce calcul vérifie surtout forme et
présence, pas pertinence ni support des affirmations.
2. **Score scalaire WIKI également insuffisant.** Le vrai `compute_score` renvoie
1,00 pour cinq sections remplies de « banane », deux confiances high déclarées et un
lien résolu. Le score n'est pas une probabilité de vérité. Ces expériences ne
prouvent PAS le passage des autres gates ni une publication de ces textes.
3. **La tâche quotidienne fonctionne, mais son périmètre est documentaire.**
`knowledge-jobs.timer` actif ; exécution du 13 septembre 08:00:59 Europe/Paris,
terminée 08:01:34, exit0. 16 998 occurrences documentaires / 7 343 contenus uniques,
issus de snapshots GitHub/VPS ; aucune recherche web métier dans ce collecteur.
Validation WIKI : 0 éligible, 0 promu, 15 bloqués. Causes comptées (chevauchantes) :
SUBSTANCE_SCORE15, SOURCE_DIVERSITY14, TRUTH_LEVEL7, SAFETY_HUMAN_REVIEW3,
GATE_RISK3, NUMERIC_HIGH_HARM1. Réévaluer les mêmes propositions ne les enrichit pas.
Le service oneshot inactif après succès ne signifie pas timer arrêté.
4. **La capture native consomme des URLs fournies.** Dans le runner inspecté,
`provided` est la voie exécutable ; la découverte automatique n'est pas réalisée
par ce script. ADR-096 et le skill prévoient une recherche plus riche, mais un
contrat ou une méthode ne prouvent pas un exécutant actif. Aucun moteur alternatif
sur d'autres hôtes n'a été exhaustivement recherché.
5. **Un ancien pipeline RAG est encore planifié.** Cron toutes les 30 minutes et
watcher PDF. Derniers passages observés jusque 10:00 : INTERNAL_API_KEY not set,
avant traitement. Ce code vise PDF→RAG→enrichissement ; le réactiver en ajoutant une
clé ne construit pas la boucle canonique RAW→WIKI. Aucune configuration changée.
6. **La documentation mélange objectif et preuve.** `seo-content-loop` dit « itérer
jusqu'au score », contient des seuils illustratifs rank-#1 et des mentions humaines
antérieures à la décision WIKI automatique du 12 septembre. Le score de substance
shadow documente lui-même des heuristiques v0. Il faut distinguer conformité,
substance évaluée et résultat observé ; aucun chiffre interne ne certifie une
première place Google.

### Correction proposée

Ordre de réparation : calibrer les scorers existants sur des contenus évalués
indépendamment (bons et mauvais, courts et longs, doublons et sources non probantes) ;
produire des manques éditoriaux explicites par intention et entité ; raccorder ces
manques à la découverte gouvernée ADR-096 et au runner RAW existant ; extraire des
faits nouveaux et utiles avec passages source ; mesurer le gain avant/après puis
les résultats de pages réellement servies. Une itération sans information nouvelle
ou avec source inaccessible doit rester visible et bornée. Ne pas simplement monter
les seuils, multiplier les textes ou créer un nouveau score concurrent.

Conserver les blocs utiles et les faits catalogue à leur place. L'excellence
requiert réponse utile, preuves, absence de contradictions, différenciation réelle,
bon rôle de page ; une longueur ou un lien ne compense pas une affirmation fausse.
Les mesures SEO se font par page/requête/date, distinctes de l'autorisation WIKI.

### Validation

Deux contre-exemples reproductibles sauvegardés :
[score-counterexample.cjs](editorial-pipeline-evidence-20260912/score-counterexample.cjs)
et [score-counterexample.py](editorial-pipeline-evidence-20260912/score-counterexample.py).
Exécution native des calculs ; aucun accès DB, modèle, scrape, publication, ni
modification de score métier. Les 216 tests du lot WIKI précédent restent une
preuve de comportement technique sur ce lot, PAS une calibration éditoriale.

Google distingue utilité/fiabilité et signaux de classement :
[contenu utile](https://developers.google.com/search/docs/fundamentals/creating-helpful-content),
[guide SEO](https://developers.google.com/search/docs/fundamentals/seo-starter-guide).

### Verdict

**PARTIAL_COVERAGE.** Défaut de validité des deux scores comme métrique d'excellence
reproduit ; portée limitée de la tâche quotidienne et panne du pipeline legacy
observées. Qualité factuelle du corpus, performances Google et boucle complète
non certifiées. Aucun service partagé ni candidat applicatif modifié.


## 2026-09-13 — ajout utilisateur : règles SEO et anti-duplication

### Scan

Lecture ciblée du registry courant (origin/main), des contrôles de diversité R8,
distinction commerciale R2, qualité et rôles, et du composeur R8. Lecture du code,
pas de mesure sur la DB ou les pages publiques. Sources Google vérifiées :
[canonicalisation](https://developers.google.com/search/docs/crawling-indexing/canonicalization),
[contenu généré](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content).

### Analysis

Les briques existent : `scripts/qa/r8-diversity-check.py` compare les empreintes de
variantes sœurs et observe les collisions title/H1/description (ces dernières sont
report-only, sans effet sur le verdict). `R2CommercialDistinctivenessService`
compare familles, références, équipementiers et compatibilités ; les règles
catalogue doivent rester prioritaires sur les différences de formulation.
`PageRoleValidatorService` porte les contrôles de rôle, maillage et canonical.
Le composeur R8 documente une limite : un même corps éditorial de gamme peut être
réutilisé entre variantes, avec un contexte factuel différent.

Présence du code ne prouve ni activation dans la boucle ni conformité des pages.
Une empreinte différente ne prouve pas une information différente. La similarité
n'est pas non plus automatiquement une faute : caractéristiques communes exactes,
structure de page et avertissements nécessaires peuvent être identiques. Google
indique que la duplication normale n'est pas en soi une violation de ses règles.
La génération de nombreuses pages sans valeur ajoutée peut, elle, enfreindre ses
règles sur la production abusive à grande échelle.

### Correction proposée — exigences à raccorder aux contrôles existants

| Niveau | Vérification attendue | Cas de calibration |
|---|---|---|
| Sections d'une même fiche | Identité canonique des sections, répétitions exactes et recouvrement d'information | Symptômes/symptomes, accents/casse/espaces ; même identité sans perte des faits distincts |
| Corps éditorial | Utilité, sources probantes, absence de remplissage ou simple paraphrase répétée | Texte long répétitif, synonymes sans nouvelle information |
| Pages d'une même famille | Comparaison entre variantes et conservation des faits identiques légitimes | Deux motorisations, seul nom changé ; différence catalogue réelle reconnue |
| Pages de rôles différents | Respect du rôle et de l'intention, contrôle du risque de concurrence interne | Guide d'achat, fiche véhicule et diagnostic ne portent pas la même promesse |
| Page composée et rendue | Doublons introduits par assemblage, titres/FAQ/blocs, liens et données structurées cohérents avec le visible | WIKI correct mais bloc ajouté deux fois dans le rendu |
| Ensemble du site | Comparaisons entre familles pertinentes, canonical/maillage/indexabilité selon contrats existants ; observations page/requête | Deux URLs répondant à la même intention ; absence de données signalée, pas de fusion automatique |

Les défauts certains (même section ajoutée deux fois, liens invalides, contradiction)
doivent être traités explicitement ; une bonne moyenne ne compense pas un contrôle
obligatoire échoué. Les ressemblances éditoriales sont des signaux à qualifier par
contexte et utilité, pas un seuil universel inventé ni un déclencheur de retrait.
Préserver les contrats SEO indexés : aucun changement automatique d'URL, canonical,
H1/meta, noindex ou suppression de page dans cette passe. Ne pas reformuler
artificiellement des faits pour gagner de la diversité.

Raccorder ces observations au flux existant : manque identifié → recherche RAW
pertinente → proposition WIKI vérifiée → composition → contrôle du rendu et des
pages voisines → mesure des résultats. Aucun nouveau moteur concurrent proposé.

### Validation

Cartographie statique et confrontation aux recommandations Google. Manifest de
lecture complété dans `content-loop-score-diagnosis.json`. Aucun code métier,
seuil, DB ou service modifié ; pas de tests de runtime supplémentaires pour cet
ajout documentaire.

### Verdict

PARTIAL_COVERAGE : exigences SEO/anti-duplication intégrées à la correction proposée,
contrôles existants repérés ; câblage effectif et pages réelles restent à vérifier.


## 2026-09-13 — revérification des règles avant validation

### Scan

Statuts de 20 ADRs relevés ; lectures ciblées des règles de promotion, preuve,
découverte, composition et anti-duplication. Instructions du workspace et du skill
relues. Le détail des fichiers, empreintes et profondeurs de lecture se trouve dans
`content-loop-score-diagnosis.json`, entrée `rules_review_20260913` : 33 fichiers
VPS dans ce sous-périmètre, avec lectures partielles identifiées. Ce nombre n'est
pas un décompte de règles intégralement validées. Les artefacts antérieurs conservent
leurs observations datées ; ils ne sont pas remplacés par une preuve plus large.

### Analysis

| Constat vérifié | Conséquence |
|---|---|
| Workspace CLAUDE et seo-batch.md désignent encore RAG comme source de production | Contradiction avec le contrat racine RAW → WIKI → exports/projection ; correction des instructions dérivées |
| Skill impose une revue humaine systématique et des TIER B humains | Incompatible avec la décision WIKI automatique du 12 septembre, quality-gates §7 ; preuve manquante demeure bloquante |
| Skill présente la boucle comme une course au score et au rang 1 | Les contre-exemples déjà reproduits interdisent de certifier l'excellence depuis ce score ; retirer seuils illustratifs et promesses absolues |
| ADR-094 porte status: proposed | Verdict composite reste une proposition, pas une règle active à déclarer satisfaite |
| ADR-095 porte Accepted dans l'en-tête mais Proposed dans le corps | Conflit de statut signalé ; aucune bascule shadow/enforce ni modification canonique dans ce lot |
| ADR-067 interdit la suppression automatique fondée sur similarité | Contrôler les candidats et qualifier les ressemblances ; préserver les pages existantes et les faits communs exacts |
| source-policy §9.3 sépare article général, compatibilité catalogue et procédure précise | Rechercher les informations utiles au contenu retenu, sans imposer des identifiants techniques inutiles |
| shadow_score annonce report-only, promotion_decision possède une sélection conditionnelle | Vérifier le moteur effectivement sélectionné ; présence et commentaires seuls ne prouvent pas activation |

Les règles anciennes, proposées et opérationnelles ne doivent pas être fusionnées
par une simple lecture de leurs titres. Les gates sécurité restent applicables ;
l'automatisation WIKI n'autorise ni le diagnostic LIVE ni une mutation SEO indexée.

### Correction autorisée dans le candidat

Trois documents modifiés dans le worktree applicatif isolé :
`workspaces/seo-batch/.claude/skills/seo-content-loop/SKILL.md`,
`workspaces/seo-batch/CLAUDE.md`, `workspaces/seo-batch/.claude/rules/seo-batch.md`.
Le guide exige une vérification des références et de leur exécution, dirige la
collecte vers les manques utiles, distingue les niveaux de score et les contrôles
anti-doublons, et cesse d'imposer une recherche parallèle ou un score inventé.
Métadonnées et politique d'invocation conservées, version du skill 1.1.
Lien du contrat de sortie corrigé ; adresses infra remplacées par le pointeur
au contrat existant. Patch isolé : `seo-content-loop-rules.patch`.

Aucune formule, seuil, règle canonique, activation, DB ou page publiée modifiée.
Les autres skills/agents legacy restent hors de ce correctif et doivent être
cartographiés avant d'être invoqués pour une production. Le retrait WIKI versionné
reste un raccordement distinct à réaliser, selon la stratégie acceptée.

### Validation

- Contrôle des instructions : PASS, 1 fichier, zéro blocage et avertissement.
- YAML et préservation des champs natifs du skill : PASS ; lien AEC existant.
- Diff sans erreur d'espacement : PASS.
- Contrôles vault des orphelins et liens cassés : PASS (exit0).
- Validateur générique skill-creator : exit1 sur le candidat **et sur la version
  antérieure**, car il ne prend pas en charge trois champs Claude préexistants.
  Incompatibilité de format explicitée ; aucun champ d'invocation supprimé pour
  obtenir artificiellement un PASS. Ce résultat ne valide pas le chargement runtime.

Les 216 tests WIKI antérieurs ne sont pas réexécutés pour ces seuls documents et
ne prouvent pas la qualité éditoriale. Ni CI, ni parcours de bout en bout, ni test
de classement ou corpus représentatif dans cette passe.

### Verdict

**PARTIAL_COVERAGE** : contradictions opérationnelles corrigées dans trois documents
et patch vérifiable conservé. Aucune validation globale de la boucle. Restent la
résolution canonique du statut ADR-095, l'examen des contrats non relus en entier,
le raccordement des contrôles au rendu et la calibration des scores sur un corpus
évalué indépendamment. Les mécanismes existants doivent être améliorés sur ces
preuves, sans relever arbitrairement un seuil ou inventer un nouveau décideur.


## 2026-09-13 — qualification des packs Conseil et moyenne trompeuse

### Scan

Service Conseil, configuration des packs, appelant admin et contrôles existants
sources/doublons examinés. Manifest `pack_quality_correction_20260913` dans
`content-loop-score-diagnosis.json` : 19 fichiers avec lectures ciblées déclarées.
Le candidat est 11 commits derrière origin/main ; service et constantes concernés
comparés à main sans différence avant modification. Travaux précédents préservés.

### Analysis

`computeGammeCoverage` calculait une moyenne uniquement sur les lignes notées et
pondérait implicitement les identités de section répétées. Avec sept sections dont
une sans note, il annonçait encore une moyenne de 80. Les seuils existants
`minSectionScore` et `minPackScore` n'étaient pas appliqués dans ce résultat.
`packComplete` signifiait présence des sections uniquement ; cette sémantique est
conservée et explicitée, pas transformée silencieusement en certificat qualité.
Le contrôleur admin retourne directement le résultat : le nouveau détail est donc
branché sur cette méthode dans le candidat, sans preuve d'activation runtime.

Les autres briques inspectées ont des portées distinctes : GA3 signale des
paragraphes répétés entre sections ; GA5 vérifie une liste JSON de sources ; les
empreintes de BriefGates comparent du texte normalisé. Elles ne résolvent pas la
qualification arithmétique de ce pack. Aucun second détecteur de similarité créé.

### Correction autorisée

Service existant étendu et tests adjacents ajoutés. La moyenne exige exactement une
note valide par section requise. Section absente, non notée, note invalide ou identité
répétée = moyenne null et qualification `not_evaluable`, avec détails explicites.
Les sections facultatives/hors contrat ne gonflent pas la moyenne du pack requis.

Le nouveau `qualityStatus` distingue `not_evaluable`, `below_threshold` et
`meets_thresholds`. Le dernier exige le plancher de chaque section ET le seuil du
pack, définis dans la configuration existante. La comparaison utilise la moyenne
non arrondie ; une moyenne affichée arrondie à 70 ne fait pas passer 69,86.
`packComplete` demeure une mesure de présence. Aucun seuil ni formule de score de
section n'est modifié. `meets_thresholds` ne certifie ni vérité factuelle ni classement.

Patch isolé : `conseil-pack-quality.patch`. Deux fichiers indexés dans le candidat,
sans commit, push, mutation de DB, publication ni déploiement.

### Validation

13 tests de régression échouent avant correction ; 29 tests passent après correction
(13 cas nouveaux et 16 contrôles sémantiques existants). Cas : score absent, plancher
individuel, seuil global, frontière d'arrondi, doublon d'identité, valeurs hors domaine,
pack incomplet, sections facultatives et seuils différents selon le pack.
ESLint ciblé et diff-check : PASS. Adaptateur de lecture en mémoire : aucune DB,
aucun réseau, aucun backfill exécuté. Logs avant/après conservés dans les preuves.
Pas de CI, chargement HTTP réel ou validation de page publiée dans ce lot.

### Verdict

**VALIDATED_FOR_SCOPE_ONLY** pour le calcul et le contrat du résultat de pack testé ;
**PARTIAL_COVERAGE** pour la boucle éditoriale. Le score individuel peut encore
surévaluer les répétitions et les sources non probantes : la calibration et le
raccordement aux preuves restent nécessaires. Les doublons traités ici sont des
identités de section DB répétées ; ce lot ne prétend pas résoudre tous les titres
équivalents comme Symptômes/symptomes ni les similarités entre pages.


## 2026-09-13 — sources déclarées, remplissage et routage des corrections

### Scan

11 fichiers ciblés ; détails et empreintes dans `section_sources_correction_20260913`.
Les implémentations du score, de GA5 et de lecture des références publiques ont été
comparées. Les utilitaires existants de normalisation et de provenance ont été lus.
Les fichiers utilitaires/GA5 étaient identiques à origin/main avant correction.
Recherche des appelants dans backend/src : pas d'appelant applicatif trouvé pour
runAuditGates/auditFromSections, hors implémentation et tests. Cela n'exclut pas les
appels par opérateur ou outillage externe, mais interdit d'annoncer la boucle active.

### Analysis

Le score accordait le crédit de source à toute chaîne autre que quelques valeurs
vides. GA5 acceptait une liste non vide, même `[null]` ou `[{}]`. Le contrat de lecture
existant attend des références chaînes ou des objets portant une référence chaîne.
GA5 produisait une correction no_sources mais ses corrections étaient absentes de
sectionsToImprove : shouldSkipGamme pouvait donc ignorer une gamme sans sources.
Enfin, la longueur HTML et les occurrences consécutives du même mot gonflaient les
mesures de contenu. La responsabilité de preuve factuelle reste aux contrôles WIKI.

### Correction autorisée

Un prédicat de déclaration est ajouté à l'utilitaire de provenance existant et
réutilisé par le score et GA5 : liste JSON non vide, chaque entrée portant une
référence chaîne non blanche (chaîne directe ou objet avec ref). Aucun résolveur,
registre parallèle, appel réseau ou affirmation de source vérifiée ajouté.
Les libellés publics et le parseur de rendu restent inchangés.

Le score mesure la longueur du texte extrait et réutilise le dédoublonnage de mots
consécutifs existant jusqu'à stabilisation, uniquement pour la mesure. Le contenu
stocké n'est pas réécrit. Même seuils et pénalités qu'avant. Ce normaliseur ne
constitue pas un détecteur de répétitions sémantiques ou de toutes les formes Unicode.

Les corrections GA5 rejoignent sectionsToImprove ; le chemin auditFromSections →
shouldSkipGamme conserve maintenant ce besoin de correction même avec score100.
GA5 reste un avertissement de déclaration, sans activation d'un nouveau hard gate.

### Validation

Avant : 17 échecs /22 succès sur39 cas ; après ajout du correctif et de deux cas de
chaîne audit/skip : 57 tests réussis, 3 suites. Les13 tests pack et16 tests sémantiques
précédents sont inclus. ESLint sur5 fichiers et diff-check : PASS.
Rejeu du vrai scoreSection : banane×60 avec source arbitraire, ancien100 → nouveau50 ;
sans source, ancien85 → nouveau50. Pénalités existantes CONTENT_TOO_SHORT20,
WORD_COUNT_LOW15, NO_SOURCES15. Script de preuve mis à jour pour charger les vrais
utilitaires importés ; sortie conservée dans score-counterexample-after.json.

Les tests couvrent les formats de référence positifs/négatifs, balisage volumineux,
répétition consécutive et prose ordinaire. Le cas positif de prose vérifie la stabilité
du calcul, pas une expertise factuelle du texte. Aucun réseau, DB, backfill ou service.
Patch `conseil-source-measurement.patch` cumulatif sur5 fichiers, incluant le lot pack.

### Verdict

VALIDATED_FOR_SCOPE_ONLY sur ces défauts et chemins testés ; PARTIAL_COVERAGE global.
Une référence arbitraire au bon format peut encore être déclarée : elle n'est pas
une preuve. La qualité factuelle, les répétitions sémantiques, le raccordement de
l'audit à un appelant effectif et la découverte de sources utiles restent à traiter.
Aucun commit, push, publication, modification SEO indexée ou déploiement exécuté.


## 2026-09-13 — parcours fiable des notes manquantes

### Scan

Six fichiers techniques/contrat sont enumeres avec leur perimetre de lecture et
empreinte dans `backfill_correction_20260913`. Recherche des appelants dans backend/src,
scripts et workspaces (TS, Python, shell, Markdown), conservee dans backfill-callers.txt.
Les regles deja lues sont reutilisees. Skill Supabase applique et documentation
courante du filtre gt et du tri order consultee. Comparaison ciblee avec origin/main
avant modification ; aucune difference amont sur les fichiers cibles.

### Analysis

Le backfill avance par offset parmi les notes NULL, alors que ses propres ecritures
retirent des lignes de cette selection. Reproduction : seulement 150 lignes sur 250
traitees. L'ancienne mise a jour pouvait aussi ecraser une note renseignee entre la
lecture et l'ecriture ; une reponse sans ligne modifiee etait comptee comme succes.
Une erreur de lecture fabriquait un compte de 100 echecs sans connaitre le nombre lu.

Le controleur admin appelle bien ce backfill. En revanche, la recherche ne trouve
pas d'appelant applicatif de auditFromSections/runAuditGates hors definitions/tests.
Le fallback de priorite retient les sections absentes ; il ne raccorde pas ces audits
qualitatifs. La RPC de priorite n'a pas ete auditee ici. Aucun raccordement nouveau
n'est invente avant identification du chemin effectivement execute.

### Correction autorisee

Parcours par sgc_id croissant avec curseur strictement superieur, limite 100, sans
offset. Le curseur avance aussi apres un echec d'ecriture, evitant une boucle sur les
memes echecs. Mise a jour conditionnee au score encore NULL, retour de l'identifiant
modifie : compte updated uniquement pour une ligne renvoyee, skipped sinon.
Les erreurs de lecture interrompent explicitement le traitement ; pas de faux compte.
Le compteur skipped est ajoute au resultat deja transmis par le controleur.

### Validation

Cinq contre-tests echouent avant correction ; 62 tests passent ensuite dans quatre
suites, incluant les 57 cas precedents. ESLint sur les deux fichiers modifies,
formatage et diff-check : PASS. Reproduction avec le vrai client Supabase installe et
son constructeur de requetes ; transport HTTP en memoire, sans appel DB ni reseau.
Le parcours couvre 250 lignes, 100 echecs initiaux suivis de 150 succes, note renseignee
concurremment, erreur de lecture, conservation des notes existantes et idempotence.
Logs avant/apres et patch cumulatif sont conserves dans le dossier de preuves.

### Verdict

VALIDATED_FOR_SCOPE_ONLY pour le comportement teste ; PARTIAL_COVERAGE global.
Aucun backfill reel execute. Le schema vivant, les contraintes/RLS et le plan SQL
restent a verifier avant execution. Une insertion concurrente derriere le curseur
necessite un passage suivant ; ce parcours ne constitue pas un instantane. Une
modification concurrente du contenu alors que sa note reste NULL n'est pas couverte.
Les notes non NULL existantes ne sont pas recalculees par cet endpoint.
La boucle active, les preuves factuelles WIKI, la decouverte de sources utiles et
les doublons semantiques restent des travaux distincts. Aucun commit/push/deploiement.

## 2026-09-13 — GA3 : les doublons détectés restent à corriger

### Scan

Périmètre : GA3, ses agrégations et auditFromSections vers shouldSkipGamme.
Appelants recherchés dans backend/src, scripts, migrations et chemins cachés
seo-batch. Aucun appelant applicatif identifié hors implémentation/tests dans
ces chemins. Fraîcheur : 12 commits derrière origin/main ; fichiers ciblés
comparés sans différence amont avant correction.

### Analysis

GA3 détectait des passages répétés mais renvoyait zéro correction. Ses résultats
étaient aussi absents des agrégations. Un pack noté 100 pouvait donc être ignoré.
Les instructions opérateur R3 examinées utilisent encore RAG et des comptes ou
moyennes ; le batch sélectionne les plans absents. Ce constat ne prouve pas leur
exécution. Le raccordement périodique reste ouvert.

### Correction autorisée

Une correction duplicate_content par section impliquée rejoint priority_fixes et
sections_to_improve. Les deux côtés sont désignés ; aucune propriété déduite de
l'ordre. Aucun nouveau seuil, poids, détecteur ou changement de sévérité warn.
Les textes et notes stockés ne sont pas modifiés. Priorité seule peut rester 0,
mais les corrections sont conservées et skip est false.

### Validation

Avant : 3 échecs/2 succès sur5 cas. Après ajout du cas banane répété dans sept
sections avec anciennes notes100 : 75 tests PASS /6 suites, dont6 nouveaux cas.
ESLint3 fichiers, formatage et diff-check PASS. Fonctions pures, aucune DB/réseau.
Preuves : dedup-before.log, dedup-after.log, dedup-lint.log, dedup-callers.txt,
conseil-dedup-routing.patch dans le dossier de preuves. Patch cumulatif HEAD sur
3 fichiers, incluant le lot sources précédent dans le service.

### Verdict

VALIDATED_FOR_SCOPE_ONLY pour ce routage ; PARTIAL_COVERAGE global. GA3 compare des
segments exacts de plus de40 caractères. Ni titres équivalents accentués, ni tous
les doublons sémantiques/inter-pages ne sont couverts. Preuves factuelles, collecte
utile, réévaluation des notes et appelants effectifs restent à traiter.
Aucun commit, push, contenu indexé ou déploiement modifié.

## 2026-09-13 — instructions R3 alignées sur les chemins présents

### Scan

Lecture des instructions R3 et de leur orchestrateur, du routeur, du registre,
des entrées pipeline/projection et de la décision de lecture R3. Détails dans
r3-operator-coverage-manifest.json. Fraîcheur : 12 commits amont, aucun changement
amont sur les fichiers ciblés. Règles racine réutilisées ; politiques WIKI de
promotion automatique et périmètre éditorial relues par extraits.

### Analysis

L'entrée exécutable R3 est retirée du registre et du routeur. Les anciennes
instructions demandent pourtant conseil-enricher, lecture RAG, UPSERT manuel et
validation par score. Le batch exclut les plans existants. Le planificateur simple
refuse une nouvelle note inférieure à l'ancienne, même si celle-ci était surestimée.
Les listes de sections et formules recopiées divergent des constantes courantes.

Le forward-writer contrôle l'intégrité des exports WIKI, sans refaire leur scoring.
La décision R3 distingue READY_FOR_RENDER et servedBodySource='legacy'. Dans le code
examiné, une projection prête ne remplace donc pas encore le corps de page servi.
Aucune activation runtime déduite de cette lecture.

### Correction autorisée

Quatre instructions modifiées : r3-keyword-planner, r3-keyword-plan-batch,
keyword-planner et conseil-batch. Le planificateur réutilise les contrats et
contrôles existants, demande des preuves WIKI et expose le raccordement manquant.
Le batch examine aussi les contenus existants défectueux et conserve chaque motif.
Formules de score parallèles, validation sur note seule et UPSERT recopiés retirés.
Une baisse de note peut être le résultat légitime d'une réévaluation.

L'orchestrateur ne désigne plus le producteur R3 supprimé comme cible disponible ;
sa sortie R3 distingue plan et exécution. La méthode seo-content-loop n'est pas une
API. La neutralisation de conseil-batch est préservée ; sa mention de validation
humaine systématique est alignée sur la décision automatique WIKI existante.
Aucune nouvelle règle canon créée, aucun producteur ni rendu public réactivé.

### Validation

45 tests existants PASS /2 suites : execution-router et r3-projection-decision.
Ils confirment le refus explicite du dispatch R3 et la distinction prêt/servi.
Frontmatter YAML des4 fichiers PASS ; validateur d'instructions : aucun blocage,
2 avertissements préexistants sur lignes inchangées de conseil-batch (états OFF,
expression SQL historique ON CONFLICT). Diff-check PASS. Aucun test miroir ajouté
pour ces documents. Les75 tests du lot précédent ne sont pas réexécutés ici.

Patch r3-operator-routing.patch et journal r3-operator-routing-tests.log conservés.
Les tests reposent sur les doubles existants ; pas de requête DB ni preuve runtime.

### Verdict

VALIDATED_FOR_SCOPE_ONLY pour l'alignement documentaire et les comportements testés ;
PARTIAL_COVERAGE global. Restent : collecte/découverte utile, appelant effectif de
l'audit, qualification des preuves et liaison du rendu R3 à la projection selon
son contrat gouverné. Les autres rôles de l'orchestrateur ne sont pas audités ici.
Aucun commit, push, corpus, flag, publication ou déploiement modifié.

## 2026-09-13 — audit R3 accessible par le chemin interne existant

### Scan

Contrat de décision R3, service de page et amont, puis API interne, scorer et gates.
Manifeste : r3-audit-api-coverage-manifest.json, 39 fichiers lus par extraits ou
intégralement selon la liste. App 12 commits derrière l'amont ; les propriétaires
modifiés de l'audit ne divergent pas. Le service de rendu diffère en amont pour un
filtrage des META hors contrat : laissé intact, à intégrer avant un chantier rendu.

### Analysis

L'API de couverture existante compte surtout des présences ; elle ne relie pas les
contrôles qualitatifs corrigés au contenu stocké. Le renderer R3 reste un maillon
à réaliser : READY_FOR_RENDER ne prouve pas un contenu projeté servi.
Un raccordement d'audit utile doit recalculer les notes, garder l'ancienne mesure
visible, restituer les corrections et refuser une lecture incomplète.

### Correction autorisée

GET /api/internal/seo/audit/r3/:pgId?pack=standard ajouté au contrôleur interne,
sous InternalApiKeyGuard existant. Paramètres validés avant lecture. Le service
ConseilQualityScorerService.auditGamme vérifie la gamme, lit les sections avec
comptage exact, recalcule via scoreSection puis utilise auditFromSections et
shouldSkipGamme. Aucune écriture ni dispatch. Les erreurs DB, données hors contrat
et résultats tronqués produisent un échec explicite ; gamme absente distincte de
pack vide. Les identités inconnues et répétées empêchent canSkip et restent visibles.
Les instructions du planner pointent désormais vers cet appel candidat ; sa
présence dans le code ne vaut pas disponibilité dans un environnement.

### Validation

Avant : endpoint absent, assertions HTTP échouent avec 404. Après : 13 tests HTTP
PASS avec vraie injection NestJS, vraie garde, vrai scorer, vrais gates et client
Supabase installé dont le transport est en mémoire. Cas : anciennes notes100,
doublons, identités inconnues, sections manquantes, gamme absente, lecture échouée
ou tronquée, corps mal typé, pack demandé, paramètres invalides et absence de clé.
59 tests voisins PASS : 72 tests distincts /6 suites au total, deux commandes.
ESLint3 fichiers PASS puis lint du test final PASS ; formatage, YAML, validateur
d'instructions (0 blocage/0 avertissement) et diff-check ciblé PASS.

Les requêtes de test ne touchent aucune base réelle. Le score du cas banane avec
un tableau de références déclarées passe ici de100 stocké à65 pour S1 ; le cas
historique à50 utilisait une déclaration de source différente. Les références
restent non vérifiées : ni65 ni50 ne certifie la qualité factuelle.

### Verdict

VALIDATED_FOR_SCOPE_ONLY pour l'API candidate testée ; PARTIAL_COVERAGE global.
Aucun commit/push/activation/DB/corpus/publication modifié. Restent le consommateur
actif de boucle, la collecte utile, la qualification et le rendu projeté servi.
La décision canSkip est heuristique, jamais une permission de publier. Patch du
lot, journaux et manifeste conservés dans le dossier de preuves ; dépendance aux
corrections précédentes conservée explicitement.

## 2026-09-13 — contrat du consommateur IA-SEO et inventaire fiable

### Scan

Instructions IA-SEO Master, contrat coverage, pagination Supabase et colonnes
existantes. Périmètre de lecture applicatif listé dans
seo-heartbeat-contract-coverage-manifest.json : 13 fichiers, extraits inclus.
Le consommateur documentaire est identifié ; les instructions effectivement
chargées par Paperclip et son activité en service ne sont pas établies.

### Analysis

Les instructions demandaient entities_total, wiki_missing et content_missing,
absents de la réponse API. Elles pouvaient donc transformer un manque de plan
en manque WIKI, et manquer les défauts des contenus déjà présents. L'inventaire
plafonnait ses lectures, ignorait quatre erreurs sur cinq et utilisait un marqueur
d'enrichissement comme présence de contenu. Cinq gammes étaient exclues pour un
motif RAG devenu étranger au contrat de preuve éditoriale.

### Correction autorisée

Instructions alignées sur les vrais champs et sur l'audit R3 candidat. Les gammes
actives sont toutes proposées avec pg_id, même déjà planifiées ou renseignées.
wiki_evidence_status vaut not_evaluated : aucune absence ou acceptation WIKI ne se
déduit de cet inventaire. Les besoins de collecte doivent partir d'un défaut et
d'une information précise manquante. Le parcours et son point de reprise vont
dans le suivi existant ; les plafonds de tickets et la frontière du rôle restent.

Les cinq lectures sont paginées avec ordre stable et comptage exact. Une erreur,
un compte absent, un total changeant ou une page incomplète empêchent un bilan
faussement exploitable. Le contenu présent est une chaîne stockée non vide,
indépendamment de sgc_enriched_by. Les compteurs historiques p1/p2 sont conservés
pour compatibilité et documentés comme compteurs de plans/contenus.

### Validation

Avant : les 9 nouveaux tests échouent. Après : 22 tests PASS /2 suites, dont 9 de
couverture et les 13 HTTP R3 du lot précédent. Client Supabase installé avec
transport en mémoire ; plafond serveur inférieur à la page demandé, présence
réelle vs marqueur, erreur de chacune des cinq tables et comptes invalides testés.
ESLint 2 fichiers PASS. Validateur AGENTS : 0 blocage, 0 avertissement après
restauration du contrat de sortie et des rubriques obligatoires. Diff-check ciblé
PASS. Patch du delta et journaux conservés sous seo-heartbeat-contract-*.

### Verdict

VALIDATED_FOR_SCOPE_ONLY sur ces comportements candidats ; PARTIAL_COVERAGE global.
La pagination ne fournit pas un snapshot transactionnel : un changement à total
constant peut échapper au contrôle. Coût de lecture global et droits réels non
mesurés. Présence stockée, qualité heuristique, preuve WIKI et page servie restent
distinctes. Aucune DB, aucun corpus, ticket, runtime, commit, push ou déploiement
modifié. Suite : vérifier le consommateur effectif et les endpoints disponibles,
puis la collecte utile, la qualification et le rendu projeté réellement servi.

## 2026-09-13 — vérification du consommateur effectif : DEV indisponible, AI-COS non accessible

### Scan

Lecture seule du checkout DEV principal, de son artefact compilé, des listeners,
processus et health. Vérification du cron existant et extraits récents de son log.
12 fichiers applicatifs/documentaires lus par extraits ou intégralement, plus
entrées opérationnelles listées dans seo-runtime-inspection-coverage-manifest.json.
Tentative SSH AI-COS refusée avant exécution de la commande distante.

### Analysis

DEV main est à ef84ec4586d73c497d480d805f483b2c0e11ea65. Aucun listener3000 ;
GET /health retourne code curl000 (pas de réponse HTTP), aucun superviseur applicatif
observé. Le log du cron existant signale sain à09:20:13UTC puis DOWN à10:10:11,
10:20:11 et10:30:11UTC. La date exacte de début et la cause restent inconnues.
Le cron de sync est présent ; le relancer ne constituerait pas un diagnostic et
pourrait muter le checkout. Aucun nouveau système de surveillance nécessaire.

Le document IA-SEO du checkout principal conserve wiki_missing et ne contient pas
r3_audit_candidates. L'artefact compilé du contrôleur ne contient pas l'endpoint R3
candidat. Cette présence disque ne prouve pas quelles instructions AI-COS charge.
La connexion à l'alias aicos est bloquée par HOST_KEY_VERIFICATION_FAILED : nouvelle
empreinte ED25519 présentée, non authentifiée, conservée dans le manifeste. Aucune
commande distante AI-COS exécutée, aucun contournement ou changement known_hosts.

### Correction proposée

Authentifier l'empreinte AI-COS depuis la console fournisseur ou un canal de confiance,
puis vérifier service et configuration chargée. Déterminer si l'arrêt DEV est voulu
avant remise en route, car démarrer l'application peut déclencher crons et queues.
Conserver le candidat isolé ; sa publication/raccordement ne se déduit pas de ce
contrôle. Aucun démarrage, déploiement, ticket, écriture DB ou corpus effectué.

### Validation

Les constats DEV sont des lectures actuelles, les événements de santé sont des logs
historiques explicitement horodatés. Les 22 tests du lot précédent restent valables
pour le candidat inchangé ; aucun test supplémentaire requis pour ce lot sans code.
Aucune réponse de l'audit en service obtenue. Journal noyau filtré sans résultat :
ne permet pas de conclure à l'absence d'incident. Diagnostic consigné et copié.

### Verdict

PARTIAL_COVERAGE. INSUFFICIENT_EVIDENCE pour les instructions réellement chargées et
les runs AI-COS. Deux obstacles précis sont établis : voie DEV indisponible et identité
SSH AI-COS non vérifiée. La cause de l'arrêt, la collecte effective, la qualification
WIKI et le contenu servi restent ouverts. Ne pas annoncer une boucle opérationnelle.

## 2026-09-13 — rectification owner : AI-COS supprimé, DEV disponible

### Scan

Owner indique AI-COS supprimé et DEV3000 up. Vérification directe à10:45:42UTC :
GET /health HTTP200, listener3000 présent. main reste ef84ec4586d73c497d480d805f483b2c0e11ea65.
Périmètre de recherche borné et quatre fichiers lus/extraits listés dans
seo-runtime-owner-correction.json.

### Analysis

L'indisponibilité précédemment observée est historique et ne doit plus être présentée
comme un obstacle actuel. Le changement de clé de l'ancien alias AI-COS est sans objet
pour la suite : aucune authentification, restauration ou réactivation à demander.
L'attribution de la boucle active à Paperclip était une hypothèse documentaire
insuffisante. Les corrections agents/seo-content sont conservées comme travail legacy,
à exclure du raccordement actif tant qu'aucun consommateur actuel ne les utilise.

La méthode seo-content-loop existe dans seo-batch, sans preuve de déclenchement auto.
Le scheduler SEO applicatif existe ; ces extraits ne prouvent pas qu'il pilote la
boucle éditoriale. Le cron utilisateur comporte sync-rag-from-wiki.sh ; cela ne prouve
pas davantage cette boucle, RAG restant réservé au chatbot.

### Correction autorisée

Rapport et checkpoint rectifiés. Aucune suppression de travaux précédents, aucun
changement de code, known_hosts, runtime, cron ou contenu. Ne pas réintroduire AI-COS.

### Validation

HTTP200 et listener confirmés. Aucun nouveau test applicatif, code inchangé.

### Verdict

PARTIAL_COVERAGE : DEV disponible confirmé, suppression AI-COS confirmée par owner.
Le pilote actuel et son dernier run éditorial restent à identifier ; cela devient
la prochaine action, sans dépendance à l'ancien accès SSH AI-COS.

## 2026-09-13 — pilote WIKI : relayer la décision de promotion complète

### Scan

Recherche du pilote actuel après suppression AI-COS. Owner ne connaît pas son point
d'entrée. Audit SEO hebdomadaire = sitemap/URLs ; ancien content-refresh indiqué
supprimé dans AdminModule. Pilote raw_to_wiki_content_loop_pilot.py trouvé au WIKI :
rapport diagnostique de sources/proposals existantes, sans collecte ni planification.
18 fichiers/extraits listés dans content-loop-pilot-coverage-manifest.json. Fetch amont,
pas de diff des propriétaires contrôlés ; deux fichiers pilotes propres avant lot.

### Analysis

Le pilote transformait un tier A/S en promotion PASS sans lire la décision canonique.
Il ignorait le code retour du processus, transmettait0.80 refusé par le CLI courant
(minimum0.85) et omettait raw-root nécessaire à la provenance. Son message de blocage
référençait encore un seuil1.01. Quatre tests existants utilisaient des APIs retirées.
Aucun dernier run effectif établi : aucun rapport loop trouvé dans _audit profondeur2
ne prouve pas une absence sur d'autres machines ou dossiers.

### Correction autorisée

Deux fichiers WIKI candidats modifiés. stage_promotion relaie promotion_status,
eligible et blocking_reasons. Tier seul ne décide plus. Erreur processus ou résultat
absent/ambigu/incohérent restent UNKNOWN ; refus canonique reste FAIL. run transmet
raw-root. Défaut du seuil délégué au CLI canonique, surcharge explicite conservée.
Motifs actuels dans le rapport, description diagnostique précisée. Aucun nouveau
scorer/décideur, aucune activation. Tests anciens adaptés au contrat state/static_proofs
avec mêmes intentions, plus14 régressions et intégrations ciblées.

### Validation

Baseline4 échecs /10 ; avant correction16 échecs /22. Final138 tests PASS /3 fichiers,
dont24 pilote et tests du promoteur/décideur existant. Un test appelle vraiment le CLI
promoteur sur fichiers temporaires avec --dry-run et vérifie absence de mutation.
py_compile2 fichiers et diff-check ciblés PASS. Pas de DB/corpus partagé, aucune
collecte, promotion réelle, écriture runtime, publication ou commit/push.

### Verdict

VALIDATED_FOR_SCOPE_ONLY pour cet adaptateur candidat ; PARTIAL_COVERAGE global.
Déclencheur et dernier run actuels restent inconnus. Le pilote diagnostique ne remplace
pas une boucle de collecte opérationnelle. Les verdicts composites historiques et
le matching entity-id du promoteur ne sont pas modifiés dans ce lot. Patch et journaux
content-loop-pilot-* conservés ; dépendance au promoteur candidat explicitée.

## 2026-09-13 — identité exacte de la fiche et portée explicite des verdicts

### Scan

Sélection du promoteur, tests et portée des verdicts du pilote. Neuf fichiers/extraits
listés dans content-loop-identity-coverage-manifest.json. Fetch WIKI amont : propriétaires
contrôlés sans diff amont ; changements antérieurs indexés conservés. ADR094 reste proposed.

### Analysis

Le filtre entity-id utilisait slug in filename : une fiche voisine pouvait être
sélectionnée, même si la fiche exacte n'existait pas. Le type et le slug déclarés dans
son frontmatter n'étaient pas confrontés à la demande avant évaluation.
Les verdicts historiques du pilote portent la projection et les résultats fournis ;
ils peuvent être positifs alors qu'un contrôle éditorial reste bloqué. Le contrat
existant les sépare de page_quality_ready ; ce lot ne redéfinit pas ces booleens.

### Correction autorisée

Sélection exacte du nom, slug seul conservé pour compatibilité. Le CLI compare le
slug et, s'il est fourni, le type avant évaluation ou skip. Une incompatibilité donne
BLOCKED/ENTITY_ID_MISMATCH ; --target ne contourne pas --entity-id. Cette validation
d'entrée n'ajoute pas de scorer. Rapport du pilote enrichi de verdict_scope pour
expliciter les limites et renvoyer aux blocages éditoriaux, inconnues et page_quality_ready.

### Validation

Cinq nouveaux tests échouaient avant correction. Après :143 tests PASS /3 fichiers
(pilote, promoteur, décideur). Cas exact/voisins, cible absente, mauvais type/slug et
cible explicite incompatible. Évaluation interdite dans les tests d'identité fausse,
fichiers temporaires conservés sans promotion. py_compile3 et diff-check ciblés PASS.
Patch content-loop-identity.patch = delta sur index précédent, pas un patch autonome.

### Verdict

VALIDATED_FOR_SCOPE_ONLY sur la sélection et les contrôles testés ; PARTIAL_COVERAGE global.
Aucun seuil, verdict historique, corpus, DB, runtime, cron, publication ou commit/push
modifié. Déclencheur et dernier run restent à identifier. Le rapport ne doit pas être
interprété comme une garantie d'excellence ou de classement depuis un booléen technique.

## 2026-09-13 — tâche quotidienne identifiée, collecte et validation sans enrichissement établi

### Scan

Timers et cron DEV, workflows WIKI/RAW, programme et sources knowledge-jobs, trois
rapports récents.14 fichiers/extraits et entrées opérationnelles listés dans
content-loop-scheduled-runtime-coverage-manifest.json. Preuves allowlistées conservées.

### Analysis

knowledge-jobs.timer est enabled, quotidien08:00 Paris. Dernier run13sept06:00:59UTC,
fin08:01:34Paris, exit0. Il collecte des dépôts/dossiers documentaires puis exécute
le promoteur natif sur wiki-auto-validation avec --all --apply et RAW explicite.
Ce constat précise/remplace les mentions précédentes de déclencheur global inconnu
ou de tâche purement documentaire : sa collecte est documentaire, sa seconde étape
évalue aussi les propositions WIKI. Inspection seule, aucun run lancé par cet agent.

Dernier résultat :0 éligible,0 promue,15 bloquées ; mêmes comptes aux deux rapports
précédents conservés. Aucun error technique. Le libellé validated du résumé signifie
que le passage de validation s'est exécuté ; il ne signifie pas que les fiches sont
validées. La configuration collecte7 dépôts GitHub et6 dossiers VPS, pas des sources
automobiles nouvelles déterminées par les manques des fiches. Le programme ne relie
pas les défauts détectés à création/amélioration de propositions à partir de ces manques.

Exemple filtre-à-huile : moteur promotion legacy0.46 pour seuil0.85, BLOCKED/SUBSTANCE_SCORE.
Mesure secondaire tierS/91 mais manifest_status stale. Les cinq gates de l'évaluation
sont pass ; le score restant bloque. Ne pas choisir le maximum ni basculer le moteur
pour faire passer la fiche. Les16998 documents/9655 occurrences dupliquées du collecteur
comptent ses copies documentaires : ce ne sont pas des mesures de duplicate SEO.

### Correction autorisée

Suivi mis à jour sur ce déclencheur réel. Une ligne de CI WIKI candidate inclut les
tests du pilote avec ceux du promoteur/décideur, afin que les régressions récentes
soient couvertes après publication. Aucun changement de timer, source configurée,
seuil, moteur ou runtime. Aucun apply/commit/push/PR/notification exécuté ici.

### Validation

Preuve systemd et rapports réels. YAML et chemins de tests CI valides ; diff-check PASS.
La commande CI couvre le même ensemble143 tests déjà verts ; pas de répétition sur
code et dépendances inchangés. CI distante du candidat non exécutée/non publiée.

### Verdict

PARTIAL_COVERAGE. Déclenchement quotidien collection+validation prouvé. Boucle complète
de recherche automobile→propositions améliorées→pages servies non établie. Suite :
partir d'un manque concret, rechercher/capturer les preuves utiles puis qualifier,
en distinguant moteur appliqué, score secondaire et fraîcheur des preuves.


## 2026-09-13 — intégrité des scores et preuves de calcul

### Scan

Lectures ciblées du promoteur, pilote, scorer scalaire, shadow, générateur coverage et
contrats de sources. Manifeste content-loop-score-integrity-coverage-manifest.json :
périmètre des lectures distingué de la vérification automatique des 15 propositions.
WIKI HEAD et origin/main : 01cea8deda48d84b6a2993cd4bdefe8280082c0b, 0/0 après fetch.

### Analysis

Filtre à huile : score legacy 0.46 = sources 0.24 (8 confiances absentes, défaut medium)
+ sections 0.12 (2/5 titres reconnus) + liens 0 + diversité 0.10. Titres non reconnus
ne signifient PAS faits absents. Le shadow 91/S utilisait 13 claims pending_capture,
dont 10 high, alors que gen_coverage_map impose déjà high→medium sans capture.
Autres défauts reproduits : liens de proposals donnant +0.20 comme du canon ; manifeste
shadow lu depuis le checkout du code ; perte des notes et des détails dans les adapters ;
inputs score absents du snapshot ; _index.md traité comme proposition en batch.

### Correction autorisée

Calcul détaillé unique, API scalaire conservée, preuves et moteur propagés jusqu'au
pilote. Promoteur aligné sur le répertoire wiki/ pour les liens. Manifest shadow du
repo évalué, notes conservées. Shadow réutilise _cap_medium du générateur : captures
absentes/pending/inconnues plafonnées, notes explicites. Aucune confiance réécrite.
Snapshot étendu à coverage, reality manifest et cibles wikilinks utilisées seulement ;
une fiche étrangère reste hors périmètre. Hash moteur inclut gen_coverage_map.
Batch exclut la navigation underscore ; cible explicite conserve son diagnostic.
CI existante étendue aux tests shadow. Patch delta sur index précédent, pas autonome.

### Validation

224 tests PASS /6 fichiers ;14 nouveaux cas dont12 échecs observés avant correction.
Contrats générateur, schéma, promoteur, décision, pilote, shadow couverts. YAML/CI,
py_compile5 et diff-check PASS. Rejeu natif --all --dry-run :15 propositions,0 éligible,
0 erreur d'évaluation ; hashes du corpus inchangés. Parité scalaire avant/après sur
15 propositions avec le même scope canon de liens :0 différence.
Filtre à huile : shadow 91/S→79/B, A26.5→17.3,13 preuves non capturées signalées ;
legacy0.46 et décision BLOCKED inchangés. Manifeste périmé toujours signalé.

### Verdict

VALIDATED_FOR_SCOPE_ONLY ; PARTIAL_COVERAGE global. Aucun apply réel, nouvelle capture,
modification corpus partagé/DB/timer/runtime, commit/push/PR ou publication. Ces scores
restent des proxys, pas des preuves de vérité ni de classement SEO. Suite : matérialiser
les pages sources utiles aux claims et vérifier leur ancrage via les outils existants,
puis relier ce traitement à knowledge-jobs sans restaurer AI-COS. Découverte/enrichissement
et projection vers les pages servies restent non établis. Preuves dans les trois fichiers
content-loop-score-integrity* de ce répertoire d'audit.

## 13 septembre — intégrité du diagnostic admin v2.3 (lot isolé)

Scan : moteur QualityScoringEngineService, profils, RPC source, agrégateur et endpoint interne.
Analysis : guide_source_verified et métadonnées R1 attribués à d'autres rôles ; historique
__rag_content_refresh_log sélectionné par gamme sans version de page ; tableau de gates vide
crédité ; date de pipeline substituée à la fraîcheur d'une page. Ces champs ne prouvent pas
la qualité éditoriale. Les profils R2/R5/R7/R8 ont des dimensions vides ; R0 est absent.

Correction autorisée par l'owner : v2.3 dans le candidat application, séparation des signaux
par rôle, ancien pipeline ignoré sans redistribution de ses points, date absente/invalide/future
sans bonus, refus des profils/gates/pénalités inconnus. Les notes restent des diagnostics de
structure ; elles ne peuvent plus attribuer HEALTHY et portent publication_assessment=NOT_EVALUATED.
L'identité pg_id/alias/RoleId et les preuves manquantes figurent dans le snapshot. Les actions
ne prescrivent plus de quotas de texte/FAQ ; elles demandent des réponses utiles et sourcées.

Validation : 29 tests ciblés PASS (2 fichiers ; inclut invariance inter-rôles et ancien RAG,
absence de certification malgré note élevée, profils vides refusés). ESLint : 0 erreur,
29 avertissements sur littéraux de rôles historiques. git diff --check PASS. Aucun appel
au calcul qui écrit en DB, aucun déploiement ; valeurs déjà enregistrées et UI actives inchangées.
Patch et journaux : `editorial-pipeline-evidence-20260912/admin-score-evidence-v23*`.
Verdict : VALIDATED_FOR_SCOPE_ONLY pour ce lot ; projet PARTIAL_COVERAGE.

Poursuite autorisée : vérifier rôles ET structures, contrats/constantes/validateurs/rendu.
Découverte : 7 des 8 contrats de page ont allowed_sections vide ; R1 n'en décrit qu'une.
Conflit documentaire à résoudre avant toute modification des rôles : paquet contrats décrit
R5 comme sunset ADR-027, alors que des surfaces diagnostiques et d'autres projections le
conservent. R6_SUPPORT est explicitement une surface utilitaire hors série éditoriale ;
R6_GUIDE_ACHAT est le guide. Ne pas fusionner leurs identités sous un simple libellé R6.

## Jalon : pages retirees et ancre R3, 13 septembre 2026

Verification ciblee : details R5 consolides dans R3 selon ADR-027, un 301 public confirme mais fragment destination absent. Candidat : ancre S2_DIAG stable, ancien fragment preserve, cache v4 ; 24 tests service et 3 tests rendu passent. Le guide achat filtre-a-huile reste HTTP200 : aucune conclusion de suppression globale R6. Rapport : [[ledger/audit-trail/editorial-pipeline-evidence-20260912/role-lifecycle-verification-20260913|verification du cycle de vie des pages]]. Preuves HTTP, patch et manifeste role-lifecycle-score-coverage-manifest.json dans le meme dossier. PARTIAL_COVERAGE ; aucun deploiement.

## Jalon : controle des titres R3 dupliques, 13 septembre 2026

Le gate GA3 existant recoit maintenant sgc_title via l'audit et reutilise normalizeSeoText pour titres/paragraphes. Les deux sections restent a examiner, meme avec scores 100 ; aucune suppression automatique ni recreation R5. Cinq tests rouges avant correction ; 73 tests verts dans cinq suites apres correction ; lint sans erreur/warning. [[ledger/audit-trail/editorial-pipeline-evidence-20260912/r3-heading-dedup-verification|Rapport, limites et suite]] ; manifeste r3-heading-dedup-coverage.json au meme dossier. PARTIAL_COVERAGE, candidat uniquement.

## Jalon : validation R3 par section, 13 septembre 2026

Correction du chemin audit R3 : retrait de NO_LINK_TO_R5, controles diagnostiques existants reserves a S2_DIAG, autres sections soumises aux controles R3. Erreurs exposees avec scope stored_sections, canSkip faux, role_violation raccorde aux sections a ameliorer. 135 tests verts dans sept suites, lint sans erreur/warning, diff checks PASS. [[ledger/audit-trail/editorial-pipeline-evidence-20260912/r3-section-role-verification|Rapport de validation R3 par section]] ; manifeste r3-section-role-coverage.json. VALIDATED_FOR_SCOPE_ONLY pour ce lot ; PARTIAL_COVERAGE global. HTML publie et consommateurs globaux restent a verifier ; aucun deploiement.

## Jalon : HTML R3 compose et destination, 13 septembre 2026

Sept fichiers prepares : marqueur S2_DIAG dans le vrai rendu, analyse DOM de l'article dans validatePageWithHtml, borne/ancre unique et donnees de tableau trois colonnes. Reutilisation des controles par section. 15 echecs avant ; 154 tests backend et 4 frontend passent apres, dont rendu React SSR vers validateur reel ; lint zero. PUBLIC 301/200 avec ancre encore absente, DEV3000 ECONNREFUSED a 15:44 UTC. [[ledger/audit-trail/editorial-pipeline-evidence-20260912/r3-html-verification|Rapport et limites HTML R3]] ; manifeste r3-html-coverage.json. Aucun deploiement ; branchement effectif du monitor sur tous les SSR non prouve. PARTIAL_COVERAGE.

## Jalon : raccordement de l'audit R3 au HTML servi, 13 septembre 2026

Le SSR ecrit directement dans Express et echappe au retour chaine inspecte par l'intercepteur Nest. L'audit interne R3 existant lit maintenant la route conseils sur BASE_URL explicite, conserve les redirections et rend les erreurs de lecture visibles. canSkip exige controles stockes et rendu valide ; pageReviewRequired expose le travail de rendu sans inventer une reecriture. Une S2_DIAG stockee mais omise du HTML est detectee. URL/date/SHA256 attribuent la preuve ; correspondance de revision non evaluee. Six fichiers prepares, 113 tests backend et quatre frontend PASS ; lint zero erreur, un avertissement preexistant. [[ledger/audit-trail/editorial-pipeline-evidence-20260912/r3-served-audit-verification|Rapport du raccordement HTML servi]] ; manifeste r3-served-audit-coverage.json. VALIDATED_FOR_SCOPE_ONLY, PARTIAL_COVERAGE global ; ni deploiement ni activation de boucle, aucun nouveau constat public/DEV.

## Jalon : executants reels de la boucle, 13 septembre 2026

DEV HTTP200 mais audit R3 candidat absent du controleur compile. knowledge-jobs quotidien termine correctement : collecte documentaire multi-projets, 16998 occurrences/7343 contenus uniques, puis 15 propositions WIKI bloquees, aucune promotion. Aucun chemin lacune R3 vers recherche de source dans cet executant. Ancien cron RAG toutes les 30 minutes : derniers passages bloques par cle interne absente, aucune reactivation. Hermes prive non inspectable par le compte SSH ; notification seule prouvee dans le runner. Consigne historique SEO corrigee (AI-COS retire, nouveau contrat rendu, compteurs non assimilables a des faits). [[ledger/audit-trail/editorial-pipeline-evidence-20260912/seo-executor-verification|Rapport des executants et limites]] ; manifeste seo-executor-coverage.json. Validation documentaire zero blocage/warning, aucune mutation runtime. PARTIAL_COVERAGE.

## Jalon : corpus classe et navigation Obsidian

Projection candidate du collecteur existant : 7343 fiches de provenance sans copie des corps, projets et combinaisons de familles, cinq vues Bases, changements precis (10 ajouts/13 modifications). 24 tests PASS, zero lien local casse, aucun statut de qualification accorde. Pilote filtre-a-huile conserve divergence GitHub/VPS et ecart 29 sources primaires annoncees/22 declarees dans index, sans validation factuelle. [[ledger/audit-trail/editorial-pipeline-evidence-20260912/knowledge-catalogue-verification|Rapport corpus et methode editoriale]]. Runtime inchange ; PARTIAL_COVERAGE. Candidat /home/deploy/knowledge-navigation-candidate-20260913, archive Obsidian et notebook de reproduction disponibles.

## Jalon : robustesse des comparaisons et du rendu documentaire

Candidat: les changements de politique/collecteur ou empreintes inconnues ne sont plus qualifies en suppressions/absences documentaires. Empreintes des snapshots conservees. Noms verifies et generation preparee avant ecriture; reprise apres interruption testee. 31 tests PASS et 7343 fiches/16998 provenances revalidees. [[ledger/audit-trail/editorial-pipeline-evidence-20260912/knowledge-robustness-verification|Rapport de robustesse et limites]]. Runtime inchange; atomicite par fichier seulement, integration et qualification editoriale non prouvees. PARTIAL_COVERAGE.

## Jalon : capture utile et correction ciblee filtre a huile

Guide R6 DEV200, public403. Generalisation anti-retour obligatoire confrontee au passage FILTRON; capture native immuable dans nouveau candidat RAW courant, hashes et source-catalog relies. Proposition WIKI corrigee sur le role des clapets et deux formulations insuffisamment sourcees. Gate I/J, schema, coverage et provenance cibles PASS; collecte repetee dedupliquee. Promotion reste BLOCKED a0.46; aucune fermeture de lacune dans la page servie. [[ledger/audit-trail/editorial-pipeline-evidence-20260912/filtre-pilot-verification|Rapport du pilote et limites]]. PARTIAL_COVERAGE.


## 2026-09-14 — R6 : blocage qualité cohérent entre simulation et exécution

Scan et analysis : le contrôle refusait en simulation mais pouvait écrire en exécution. Correction préparée dans le candidat autorisé : gate D1 stricte, décision partagée et diagnostics explicites, sans mutation des données servies. Validation : 24 tests ciblés, typage backend et lint sans erreur. Verdict : VALIDATED_FOR_SCOPE_ONLY / PARTIAL_COVERAGE.

Détails des cinq états, exclusions, limites, sources et preuves : [rapport R6](editorial-pipeline-evidence-20260912/r6-quality-verification.md), [coverage](editorial-pipeline-evidence-20260912/r6-quality-coverage.json).

Navigation du vault : [[r6-quality-verification]] · [[r6-quality-sources]].


## 2026-09-14 — R6 : séparation V1/V2 et vérification des sources

Scan/analysis : critères véhicule transformés en niveaux de qualité et provenance vérifiée fabriquée par score. Correction candidate autorisée : schéma de tiers, lacune explicite, version filtrée dans UPDATE, vérification legacy retirée. Validation : 73 tests backend, 5 frontend, typage backend ; typage frontend limité par 15 erreurs de dépendances absentes hors fichiers touchés. Verdict : VALIDATED_FOR_SCOPE_ONLY / PARTIAL_COVERAGE.

Détails, exclusions et preuves : [[r6-contract-verification]] et [coverage](editorial-pipeline-evidence-20260912/r6-contract-coverage.json).


## 2026-09-14 — filtre à huile : preuve par passage MAHLE

Scan/analysis : hiérarchie de médias appuyée sur transmission, contexte insuffisant. Correction candidate : archive MAHLE native, deux claims conception/media et leurs ancres, texte/structure alignés. Validation : RAW I/J, WIKI schéma/coverage/raw_ref/SHA, déduplication PASS ; promotion BLOCKED à0.46. Shadow82 mais A19.8<22, 12 page_unproven et reality stale. Verdict PARTIAL_COVERAGE, aucun site/DB modifié.

Détails des cinq états et périmètre : [[mahle-pilot-verification]] et [coverage](editorial-pipeline-evidence-20260912/mahle-pilot-coverage.json).


## 2026-09-14 — ancrage réel et entretien constructeur

Scan/analysis : couverture validait le titre sans vérifier l'extrait. Correction candidate : contrôle natif CommonMark de l'ancre, section unique, exclusions code/commentaires/URL ; entretien filtre renvoyé au constructeur via MAHLE déjà archivé. Validation : 197 tests PASS ; décision native BLOCKED avec 10 ancres ciblées absentes. Effet structurel sur15propositions : 1PASS/6WARN/8FAIL (34écarts), sans correction artificielle. Verdict PARTIAL_COVERAGE, aucun site/DB modifié.

Détails et dispositions des12anciennes déclarations : [[claims-pilot-verification]] et [coverage](editorial-pipeline-evidence-20260912/claims-pilot-coverage.json).


## 2026-09-14 — architectures et clapets reliés à leurs passages

Scan/analysis : généralisations architecture/cartouche et rattachements de clapets insuffisants. Correction candidate : trois anciens claims bornés à MAHLE/FILTRON, principe colmatage/froid ajouté, assertion clapets-cartouche retirée et tracée. Validation : quatre ancres et raw_ref/SHA PASS ;6ancres restantes, promotion BLOCKED. Shadow89/tierA ne vaut pas approbation (6page_unproven, realitystale). Verdict PARTIAL_COVERAGE. Zéro nouvelle capture, aucun site/DB modifié.

Preuves et périmètre : [[architecture-pilot-verification]] et [coverage](editorial-pipeline-evidence-20260912/architecture-pilot-coverage.json).

## 14 septembre — notices ISO et preuve manquante explicite

[[iso-pilot-verification]] — Trois références ISO bornées aux notices officielles et éditions, texte/structure/ancres alignés. Correction candidate uniquement. Capture native initiale HTTP403, autres notices non tentées, aucune archive fabriquée ; trois demandes de capture natives restent TODO et trois sources to_capture.

Erreurs d’ancrage 6→3 ; carte14/8captured/6pending/0verified inchangée en disponibilité. Schéma/calcul0.46/gates RAW I/J PASS. Promotion BLOCKED COVERAGE_STRICT_FAIL et SUBSTANCE_SCORE ; shadow89/tierA avec6page_unproven et realitystale. 197tests précédents réutilisés sur code inchangé ; contrôles des données rejoués. Voir iso-pilot-* pour patchs, statut du collecteur et manifest PARTIAL_COVERAGE. La protection indépendante contre les preuves manquantes reste à éprouver ; aucun résultat global de qualité ou de SEO revendiqué.

## 14 septembre — preuve bloquante indépendante du score

[[proof-gate-verification]] — Défaut reproduit : sept cas de preuve absente pouvaient passer à0.99 ; quatre autres contre-preuves concernent les octets et la fraîcheur avant application. Contrôles natifs renforcés à la promotion, avec empreinte des archives effectivement référencées et racines cohérentes.

232tests ciblés PASS dont23nouveauxcas. Guide natif BLOCKED avec six preuves pending explicitement listées et trois ancres en défaut ;0.46/89inchangés, deux archives dans le snapshot. Aucun texte métier/RAW/app modifié ce lot. PARTIAL_COVERAGE : le contrôle d’intégrité n’établit pas l’appui sémantique des sources. Pas de publication/activation.

## 14 septembre — définitions OE/OES et preuve européenne

[[oe-quality-verification]] — Classement universel et liste globale de marques retirés du candidat. Deux définitions bornées aux lignes directrices 2023 remplacent deux anciennes déclarations, sans comptabiliser un retrait comme preuve acquise. Source historique rectifiée, demande EUR-Lex native préparée et tentée : unsupported_mime, aucune archive.

Deux ancres réparées, une ancre diagnostique restante ; carte 14/8captured/6pending/0verified. Promotion BLOCKED avec six preuves indisponibles et une ancre, substance0.46, shadow89 inchangé. Schémas, calcul, RAW I/J, SHA antérieurs et diff PASS ;232tests antérieurs non rejoués sur code inchangé. PARTIAL_COVERAGE, aucun contenu servi ou runtime modifié.

## 14 septembre — diagnostic prudent et consigne constructeur capturée

[[diag-pilot-verification]] — Corps, FAQ visible/structurée, failure_symptoms et relations alignés : fréquences et chaîne by-pass/perte de puissance non établies retirées. Deux liens historiques restent hypothèses low, reviewed=false/diagnostic_safe=false, identifiants et sources conservés. Une archive Renault Clio5phase1 apporte deux affirmations contextualisées de conduite à tenir, sans preuve de causalité du filtre.

Carte15/10captured/5pending/0verified, structure PASS. Un ancien claim retiré, deux nouveaux distincts ; le retrait n'est pas une preuve acquise. Promotion BLOCKED cinq preuves ISO/UE +substance0.46 ; shadow90/tierS et realitystale n'autorisent rien. Schémas/calcul, RAW I/J, SHA3archives et diff PASS.232tests antérieurs réutilisables, code inchangé. PARTIAL_COVERAGE ; montage/réutilisation/exhaustivité et causalités restent ouverts. Aucun contenu publié ou runtime modifié.

## 14 septembre — exigence de richesse métier et consommateurs

[[wiki-consumers-verification]] — L'utilisateur explicite le WIKI comme base riche mecanique/commerciale/marketing/SEO pour pages R et RAG. Matrice de besoins/preuves/limites proposée, respect des sources catalogue et gouvernance. Vérification directe du contrat gamme :17erreurs dans le pilote (decision_brief5, source_ids12), malgré frontmatter vert antérieur.9blocs éditoriaux, aucun usefulness_target renseigné ; pas de conclusion d'exhaustivité. Priorité : corriger cohérence des contrats/consommateurs, puis enrichir par besoin. Aucun code/contenu publié modifié. PARTIAL_COVERAGE.

## 14 septembre — collecte RAW orientée besoins

[[raw-acquisition-audit-verification]] — Lecture ciblée de trois fichiers : URL fournies uniquement, disponibilité de capture distincte de preuve utile, GET sans revalidation conditionnelle dans le transport inspecté, compteur RAW du diagnostic limité au répertoire historique. Stratégie de collecte proposée avec besoins, sources, passages contextualisés et qualification ; aucun code ni runtime modifié. Performances non mesurées, autres exécutants non inspectés. PARTIAL_COVERAGE ; défaut contrat WIKI17 reste ouvert.
