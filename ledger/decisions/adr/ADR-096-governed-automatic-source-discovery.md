---
id: ADR-096
title: "Governed Automatic Source Discovery, Scoring & Capture (RAW intelligent scraper — 4 entity types)"
status: accepted
date: 2026-07-15
decision_date: "2026-07-16"
version: "1.0.0"
deciders: [Fafa]
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-031"]
related_adr: ["ADR-031", "ADR-058", "ADR-060", "ADR-062", "ADR-083", "ADR-088", "ADR-089", "ADR-091", "ADR-093"]
related_rules: ["G1", "G2", "G3", "AP-10", "AP-11"]
related_incidents: []
reviewed_by: "@fafa"
tags: [raw, scraping, source-discovery, source-score, capture, governed-autonomy, adr-031-amendment]
---

# ADR-096 — Governed Automatic Source Discovery, Scoring & Capture (RAW intelligent scraper)

## Statut

**Accepted** — 2026-07-16, revue owner `@fafa` (architecture APPROVE + 4 corrections intégrées :
robots.txt en zone isolée §D2, seuils opérationnels versionnés ADR-062, frontière humain/Tier A §D6
alignée sur §D5, ligne MOC). Débloque la construction du **scraper intelligent gouverné** sur 4 types
d'entité (gamme, vehicle, diagnostic, constructeur). **L'engin reste NON construit** : cet ADR autorise
et CADRE le chantier ; l'implémentation (étape B) et les 4 pilotes font l'objet de **GO owner séparés**.

## Contexte

Jusqu'au 2026-07-15, la capture RAW était **humaine ou batch gouverné, « no agent scraping »** :
politique opérationnelle `automecanik-raw/docs/agent-capture-policy.md` + `manifests/ingestion-allowlist.yaml`
(fetch d'URLs **fournies** depuis un allowlist statique) + description du schéma
`_schemas/ingestion-worklist.schema.json`. Cette politique **dérive d'ADR-031** (séparation
4-couches raw/wiki/exports/consumers).

Conséquence mesurée (audit `smart-scraper-raw-to-wiki-real-state-2026-07-15.md`, monorepo) : aucun
moteur de découverte web autonome ; 0 dépendance SERP/headless ; worklist `vehicle_gamme_fit`
100 % `TODO` ; diagnostic/constructeur hors contrat d'ingestion. L'absence était **réelle et
gouvernée**, pas un chantier inachevé.

**L'owner décide de lever cette contrainte opérationnelle** : la découverte automatique gouvernée
de sources devient **exigée**, pour alimenter honnêtement le contenu (R1–R8) et le catalogue sur les
4 types. Le moteur part d'une **entité canonique existante** (sans URL fournie), trouve/évalue/
classe/capture les meilleures sources admissibles dans RAW — **l'humain gardant la validation avant
promotion, et la promotion downstream restant régie par les ADR existants (§D5)**.

## Décision

**On AUTORISE un moteur de découverte + scoring + capture automatique GOUVERNÉ**, qui **étend la
boucle RAW→WIKI existante** (briques `auto-capture-runner`, `author_from_raw`, `gen_coverage_map`,
`coverage-report`) — **sans créer de plateforme parallèle**. Cet ADR **amende ADR-031** : il
**préserve** la séparation 4-couches (la capture atterrit en RAW = **brut**, jamais en sortie
publique directe) et **supersède uniquement** la clause opérationnelle « no agent scraping / URLs
fournies seulement » d'`agent-capture-policy.md` + du schéma worklist.

### D1 — Périmètre : 4 types d'entité canonique

Le moteur opère sur `gamme`, `vehicle`, `diagnostic`, `constructeur`. Le contrat RAW
(`_schemas/ingestion-worklist.schema.json` `subject_type`, profils de complétude
`_schemas/completeness/`) est **étendu explicitement** à ces 4 types (+ `vehicle_gamme_fit`
conservé). Diagnostic référence les identifiants **existants** `__diag_system`/`__diag_symptom` ;
vehicle référence un **véhicule canonique existant** (jamais un `vehicle.slug` libre inventé).

### D2 — Chaîne gouvernée : DEUX portes distinctes (pré-fetch ≠ pré-persistance)

Le contrôle de sécurité **ne peut pas** être unique : certains critères (hash, doublon, pertinence,
MIME, prompt-injection) exigent d'avoir déjà les octets. On définit **deux portes** :

**Porte 1 — AVANT le fetch de la ressource CIBLE** (aucun octet de la cible lu) :
schéma **HTTPS** obligatoire · résolution **DNS + validation IP/SSRF** sur la cible (rejet IP privées /
link-local / loopback / metadata cloud) · **redirections re-validées à chaque saut** (pas de bypass
SSRF via redirect) · **authentification/paywall** = skip · **domaine** (allow/deny) · **rate-limit** ·
**budget par run** (requêtes/temps/octets).

**robots.txt** : avant tout fetch de la ressource cible, **récupération éventuelle de `robots.txt` en
zone isolée**, soumise aux **mêmes contrôles SSRF / redirections** que la cible — `robots.txt` est
lui-même une requête réseau, donc **jamais « avant toute requête réseau »**. La directive est ensuite
**respectée** (chemin interdit → skip de la cible).

**Fetch en zone ÉPHÉMÈRE ISOLÉE** : les octets récupérés **n'écrivent RIEN en RAW** à ce stade.

**Porte 2 — APRÈS fetch isolé, AVANT écriture RAW durable** :
**MIME / magic-bytes** (pas de confiance au Content-Type) · **taille max** · **hash** ·
**déduplication** (URL canonique + hash de contenu) · **pertinence** (facette recherchée) ·
**licence** · **détection de contenu hostile** · **`source_score` final** (§D3).

Les octets ne deviennent une **capture RAW durable** (`CAPTURED_NEEDS_REVIEW`) qu'**après la Porte 2**.

**Contenu web = donnée NON FIABLE** : il ne peut **JAMAIS** modifier les instructions, les poids
(`source_score`), les outils, les chemins, les URLs suivantes à explorer, ni les décisions du
moteur. Isolation prompt-injection stricte (le contenu est traité comme données, jamais comme
instructions).

### D3 — Trois scores DISTINCTS + durcissement `source_score`

| Score | Moment | Rôle |
|---|---|---|
| `source_score` | **AVANT capture** (Porte 2) | Classer les meilleures sources web candidates |
| `claim_confidence` | **APRÈS extraction** | Fiabilité de chaque fait (ADR-088/091, publisher≠page) |
| `shadow_score` WIKI | **AVANT promotion** | Évaluer la fiche éditoriale complète (ADR-088) |

`source_score` n'est **pas** un simple total pondéré. Il impose :

- des **hard gates** qu'**aucun score ne peut compenser** (licence restreinte, robots KO, SSRF,
  contenu hostile, hors-sujet total → **REJET**, jamais « rattrapé » par les autres dimensions) ;
- des **planchers et caps PAR dimension** (une dimension forte ne masque pas une dimension au sol) ;
- des **profils PAR type d'entité ET facette** (gamme ≠ vehicle ≠ diagnostic ≠ constructeur) ;
- un **plafond d'autorité pour une source INCONNUE** (elle ne peut atteindre le rang d'une source
  déjà validée) ;
- **aucune contribution d'une source inconnue à `claim_confidence`** avant validation humaine ;
- dans **chaque capture** : la **version du scorer** + le **hash du jeu de poids** + le **détail par
  dimension** ;
- règle explicite : **un bon `source_score` ne prouve JAMAIS qu'un claim est vrai** (il classe la
  source, il ne certifie pas le fait — ADR-088/091).

**Dimensions `source_score`** : autorité · correspondance exacte entité · précision
véhicule/moteur/gamme · couverture de la facette · primaire vs secondaire · fraîcheur/applicabilité ·
licence/réutilisabilité · gain de corroboration · pénalités duplication/contradiction.

**Gouvernance des poids (contrat ADR-062)** : le jeu de poids `source_score` est un **contrat
versionné au Vault** (Layer 2, explicable, révisable), **projeté déterministiquement vers RAW**
(comme le Repository Control Plane ADR-058). **Le runtime lit la projection, jamais le Vault
directement.** Toute modification des poids passe par une PR vault (traçable, signée).

### D4 — Provenance de capture (obligatoire)

Chaque source capturée conserve : **URL externe réelle** · contenu original · **hash** · date de
capture · domaine · type de source · **licence constatée** · **`source_score` détaillé (dimensions +
version scorer + hash des poids)** · **requête + facette** ayant conduit à la découverte.

### D5 — Frontière de promotion (le scraper N'A AUCUNE capacité de promotion)

Le scraper **s'arrête OBLIGATOIREMENT à RAW `CAPTURED_NEEDS_REVIEW`** et ne possède **aucune
capacité de promotion**. La promotion downstream reste **exclusivement gouvernée par
ADR-083/088/091/093** :

- **toute source inconnue, donnée de sécurité, ou valeur numérique critique** demeure
  **human-required** (ADR-091 sécurité humaine ; ADR-093 lock valeur-numérique) ;
- les **candidats NON-sécurité** peuvent suivre la **porte Tier A EXISTANTE** (ADR-083) **si ses
  conditions ET son flag sont satisfaits** — cet ADR ne crée ni ne supprime cette auto-promotion ;
- le **flip `exportable.seo` reste humain** (ADR-093).

> Cet ADR **ne supprime PAS** l'auto-promotion Tier A non-sécurité existante et **n'en crée pas de
> nouvelle**. Supprimer toute auto-promotion existante nécessiterait d'**amender explicitement
> ADR-083/091/093** — **hors périmètre** de cet ADR.

### D6 — Invariants préservés (limites fermes)

- **RAG = chatbot uniquement.** Le moteur n'utilise pas le RAG comme source ni comme producteur.
- Les **URLs externes de preuve** sont **découvertes automatiquement** ; **aucune URL, page, slug ou
  mot-clé SEO AutoMecanik n'est inventé**. Les requêtes de recherche sont **temporaires**, dérivées
  des **entités/facettes canoniques**.
- Pas de `vehicle.slug` libre → **référence à un véhicule canonique existant**.
- Diagnostic basé sur `__diag_system` / `__diag_symptom` **existants**.
- Déduplication par **URL canonique + hash de contenu**.
- Humain pour **autorité des sources inconnues**, **contradictions majeures**, **sécurité/numérique**
  et **flip `exportable.seo`** ; la **promotion WIKI Tier A reste inchangée selon §D5** (ADR-083, non
  supprimée par cet ADR).

### D7 — Rollout progressif + arrêt d'urgence (obligatoire)

L'activation est **gouvernée et progressive**, jamais big-bang :

1. **Découverte report-only** (aucune écriture RAW ; on observe classement + rejets) ;
2. **Capture en QUARANTAINE RAW** (`CAPTURED_NEEDS_REVIEW`, jamais au-delà) ;
3. **4 pilotes réels** (§Définition) ;
4. **Activation gouvernée** (par type, flaggée).

Avec : **kill switch global** (arrêt immédiat de toute découverte/capture), **budgets par run**
(requêtes/temps/octets), et **rollback SANS suppression des preuves déjà capturées** (on désactive/
quarantaine, on n'efface pas l'audit trail).

## Options Considérées

### Option A : Moteur de découverte+scoring+capture GOUVERNÉ (RETENUE)

Autonomie réelle **jusqu'à `CAPTURED_NEEDS_REVIEW`** ; deux portes de sécurité ; `source_score`
durci (hard gates + caps + poids versionnés ADR-062) ; promotion inchangée (ADR-083/091/093) ;
rollout progressif + kill switch. Étend la boucle existante.

**Avantages** : lève le goulot « URLs fournies » ; couvre les 4 types ; provenance + scoring
explicables/auditables ; sécurité web (SSRF/robots/injection) et séparation ADR-031 préservées ;
pas de nouvelle plateforme. **Inconvénients** : surface web nouvelle (mitigée par les 2 portes +
kill switch) ; nécessite un backend de recherche (absent aujourd'hui, choix gouverné à venir) ;
coût de gouvernance des poids.

### Option B : Statu quo (capture humaine / URLs fournies seulement)

Conserver « no agent scraping ». Goulot humain permanent ; worklist reste TODO ;
diagnostic/constructeur jamais couverts. **Rejetée par l'owner.**

### Option C : Autonomie totale incluant l'auto-promotion

Le moteur promeut aussi en WIKI/SEO. Violerait la séparation ADR-031, l'anti-inflation ADR-088/091,
la sécurité valeur-numérique ADR-093. **Rejetée (dangereuse).**

## Justification

Option A satisfait l'exigence owner (autonomie réelle de découverte) **sans** sacrifier les
garde-fous prouvés : séparation raw/wiki (ADR-031), anti-inflation d'autorité (ADR-088/091),
sécurité valeur-numérique (ADR-093), sécurité web (2 portes SSRF/robots/injection). La frontière est
nette : le scraper **produit des candidats en quarantaine RAW** ; **il ne promeut rien** — la
promotion reste régie, inchangée, par les ADR existants.

## Définition de « OPÉRATIONNEL » (critère de clôture)

Le scraper n'est déclaré opérationnel qu'après **4 pilotes réels (1 par type), SANS URL fournie
manuellement**, prouvant **la découverte ET la qualité du classement** :

- découverte réelle + **capture RAW** + **provenance complète** (§D4) ;
- **mesure de découverte des sources de référence** (recall : le moteur retrouve-t-il les sources de
  référence attendues pour la facette ?) ;
- **mesure de qualité du classement** vs référence humaine (le bon ordre, pas seulement « un » score) ;
- **seuils de réussite VERSIONNÉS par type ET facette dans le contrat ADR-062** (un seuil de découverte
  + un seuil de classement) ;
- **chaque pilote franchit SON PROPRE plancher** — aucune moyenne inter-types ne peut masquer un type
  en échec (un pilote sous son plancher ⇒ NON opérationnel pour ce type) ;
- **ventilation acceptés/rejetés avec reason codes** ; **≥ 1 rejet de sécurité correctement
  bloqué** ;
- **tests** : SSRF, redirection privée, robots, taille, MIME, doublon, injection ;
- **gain de couverture mesuré** ; **absence de domination injustifiée d'un seul domaine** ;
- **coût, durée, requêtes réseau, version du backend** rapportés ;
- **idempotence correcte** (voir ci-dessous) ; tests CI + rapport reproductible.

**Idempotence (formulation correcte — une recherche web live ne peut PAS être byte-identique)** :

- **même snapshot de découverte + mêmes versions/config** ⇒ **rapport byte-identique** ;
- **nouveau run live** ⇒ **aucune capture dupliquée** pour la même URL canonique + le même hash ;
- **contenu modifié** ⇒ **nouvelle version liée à la capture précédente** ;
- **toute différence de résultats reste visible et expliquée**.

Sans calibration du ranking, on prouverait seulement que le moteur produit **un** score, pas qu'il
trouve **les meilleures** sources.

## Conséquences

**Change (après acceptation)** :
- `automecanik-raw/docs/agent-capture-policy.md` : amendé (découverte auto gouvernée + 2 portes).
- `automecanik-raw/_schemas/ingestion-worklist.schema.json` : `subject_type` + provenance (§D4)
  étendus aux 4 types.
- `automecanik-raw/_schemas/completeness/` : profils `constructeur` (+ complétion diagnostic).
- **Contrat de poids `source_score` versionné au Vault (ADR-062) + projection déterministe vers RAW**
  (runtime lit la projection, ADR-058).
- Nouveau module de découverte/scoring **branché sur les briques RAW existantes** (pas de plateforme).

**Ne change PAS** : séparation 4-couches ADR-031 · RAG=chatbot · **frontière de promotion ADR-083/
088/091/093 (inchangée)** · sécurité valeur-numérique ADR-093 · pas d'URL/slug/kw AutoMecanik inventé.

**Follow-ups (GO owner séparés)** : contrats RAW 4 types ; contrat de poids `source_score` (ADR-062) ;
implémentation du moteur ; 4 pilotes réels ; choix gouverné du backend de recherche web (licences/
robots respectés).

## Non-goals

- Pas de capacité de promotion/publication dans le scraper (il s'arrête à `CAPTURED_NEEDS_REVIEW`).
- Pas de suppression ni de création d'auto-promotion downstream (régie par ADR-083/091/093).
- Pas de production de contenu par le RAG.
- Pas de nouvelle plateforme / control-plane / SEO-platform parallèle.
- Pas de `vehicle.slug` libre ni d'entité/URL/slug AutoMecanik inventés.
- Le runtime ne lit pas le Vault directement (lit la projection déterministe).
