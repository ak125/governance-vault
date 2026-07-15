---
id: ADR-096
title: "Governed Automatic Source Discovery, Scoring & Capture (RAW intelligent scraper — 4 entity types)"
status: Proposed
date: 2026-07-15
deciders: [Fafa]
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-031"]
related_adr: ["ADR-031", "ADR-083", "ADR-088", "ADR-091", "ADR-093"]
related_rules: ["G1", "G2", "G3", "AP-10", "AP-11"]
related_incidents: []
reviewed_by: ""
tags: [raw, scraping, source-discovery, source-score, capture, governed-autonomy, adr-031-amendment]
---

# ADR-096 — Governed Automatic Source Discovery, Scoring & Capture (RAW intelligent scraper)

## Statut

**Proposed** — GO owner nominatif 2026-07-15. Débloque la construction du **scraper intelligent
gouverné** sur 4 types d'entité (gamme, vehicle, diagnostic, constructeur). **Rien n'est
implémenté ni canonique tant que cet ADR n'est pas `Accepted` (signé G3 par l'owner).** L'engin
reste NON construit jusqu'à acceptation ; cet ADR autorise et CADRE le chantier.

## Contexte

Jusqu'au 2026-07-15, la capture RAW était **humaine ou batch gouverné, « no agent scraping »** :
politique opérationnelle `automecanik-raw/docs/agent-capture-policy.md` + `manifests/ingestion-allowlist.yaml`
(fetch d'URLs **fournies** depuis un allowlist statique) + description du schéma
`_schemas/ingestion-worklist.schema.json` (« la worklist n'ingère RIEN par elle-même »). Cette
politique **dérive d'ADR-031** (séparation 4-couches raw/wiki/exports/consumers).

Conséquence mesurée (audit `smart-scraper-raw-to-wiki-real-state-2026-07-15.md`, monorepo) :
il n'existe **aucun** moteur de découverte web autonome ; 0 dépendance SERP/headless ; la worklist
`vehicle_gamme_fit` est 100 % `TODO` ; diagnostic/constructeur ne sont **pas** dans le contrat
d'ingestion. L'absence était **réelle et gouvernée** — pas un chantier inachevé.

**L'owner décide de lever cette contrainte opérationnelle** : la découverte automatique gouvernée
de sources devient **exigée**, pour alimenter honnêtement le contenu SEO (R1–R8) et le catalogue
sur les 4 types. Le besoin : partir d'une **entité canonique existante** (sans URL fournie),
trouver/évaluer/classer/capturer seul les meilleures sources admissibles dans RAW — **l'humain
gardant la validation avant toute promotion WIKI/SEO**.

## Décision

**On AUTORISE un moteur de découverte + scoring + capture automatique GOUVERNÉ**, qui **étend la
boucle RAW→WIKI existante** (briques `auto-capture-runner`, `author_from_raw`, `gen_coverage_map`,
`coverage-report`) — **sans créer de plateforme parallèle**. Cet ADR **amende ADR-031** : il
**préserve** la séparation 4-couches (la capture atterrit en RAW = **brut**, jamais en sortie
publique directe), le principe **« aucun consommateur ne lit RAW directement »**, et l'interdiction
de **promotion/publication automatique** ; il **supersède uniquement** la clause opérationnelle
« no agent scraping / URLs fournies seulement » de `agent-capture-policy.md` + du schéma worklist.

### D1 — Périmètre : 4 types d'entité canonique

Le moteur opère sur `gamme`, `vehicle`, `diagnostic`, `constructeur`. Le contrat RAW
(`_schemas/ingestion-worklist.schema.json` `subject_type`, profils de complétude
`_schemas/completeness/`) est **étendu explicitement** à ces 4 types (+ `vehicle_gamme_fit`
conservé). Diagnostic référence les identifiants **existants** `__diag_system`/`__diag_symptom` ;
vehicle référence un **véhicule canonique existant** (jamais un `vehicle.slug` libre inventé).

### D2 — Autonomie RÉELLE mais gouvernée (chaîne obligatoire)

1. Entrée = **entité canonique existante uniquement** (pas d'URL obligatoire).
2. Charge le **profil de complétude** de l'entité → identifie les **facettes manquantes**.
3. **Chercheurs spécialisés** explorent automatiquement : doc constructeur · doc équipementier ·
   documents techniques/réglementaires · guides professionnels · sources secondaires (corroboration).
   Les requêtes sont **temporaires**, **dérivées des entités/facettes canoniques** — jamais des
   mots-clés SEO inventés.
4. **Filtre de sécurité AVANT capture** (fail-closed) élimine : accès interdit/authentifié ·
   `robots.txt` non respecté · domaine dangereux ou **IP privée (SSRF)** · contenu hors-sujet ·
   doublon · licence restreinte · fichier trop volumineux / type dangereux. **Protections
   obligatoires** : SSRF, validation des redirections, **prompt-injection** du contenu scrapé,
   rate-limiting, limites de taille/type.
5. **`source_score`** (voir D3) calculé pour chaque candidat ; **déduplication** par URL canonique
   + hash de contenu ; classement.
6. **Capture automatique** des meilleures sources **admissibles** dans RAW sous
   **`CAPTURED_NEEDS_REVIEW`**, avec provenance complète (D4).
7. **Extraction atomique** des faits, liés à leurs **preuves**, puis **comparaison inter-sources**
   (détection de contradictions).
8. **Re-recherche des facettes faibles** uniquement (contradictoires / insuffisamment corroborées).
9. **Arrêt** quand le **contrat de couverture** est atteint, le **budget épuisé**, ou un **blocage
   explicite** est établi.
10. RAW transmet à WIKI **après les gates + validation humaine**. **Aucune promotion/publication
    automatique.**

### D3 — Trois scores DISTINCTS (ne jamais mélanger)

| Score | Moment | Rôle |
|---|---|---|
| `source_score` | **AVANT capture** | Classer les meilleures sources web candidates |
| `claim_confidence` | **APRÈS extraction** | Fiabilité de chaque fait (ADR-088/091, publisher≠page) |
| `shadow_score` WIKI | **AVANT promotion** | Évaluer la fiche éditoriale complète (ADR-088) |

**`source_score` = dimensions explicables** : autorité de la source · correspondance exacte avec
l'entité · précision véhicule/moteur/gamme · couverture de la facette recherchée · caractère
primaire vs secondaire · fraîcheur / période d'applicabilité · licence / réutilisabilité · gain de
corroboration · pénalités de duplication ou contradiction.

**Les pondérations `source_score` sont VERSIONNÉES au Vault** (fichier de poids gouverné,
explicable, révisable) — **jamais cachées dans un prompt** ni un magic-constant code.

### D4 — Provenance de capture (obligatoire)

Chaque source capturée conserve : **URL externe réelle** · contenu original · **hash** · date de
capture · domaine · type de source · **licence constatée** · **`source_score` détaillé** · **requête
+ facette** ayant conduit à la découverte.

### D5 — Frontière humaine (décision finale d'autorité)

L'humain ne fournit plus toutes les URL, mais conserve **exclusivement** : (a) la **validation de
l'autorité définitive** d'une source **inconnue** (avant qu'elle ne compte comme autoritaire) ;
(b) l'arbitrage des **contradictions importantes** ; (c) le contrôle des **données de sécurité et
valeurs numériques critiques** (ADR-093 + lock `numeric_exactitude`) ; (d) l'**autorisation de
promotion WIKI/SEO**. Une source inconnue **peut être capturée pour examen** mais **jamais promue
automatiquement comme autoritaire** (amende le point de validation d'autorité : de *avant-capture*
vers *avant-promotion* ; le reste d'ADR-088/091 inchangé).

### D6 — Invariants préservés (limites fermes)

- **RAG = chatbot uniquement.** Le moteur n'utilise pas le RAG comme source ni comme producteur.
- Les **URLs externes de preuve** peuvent être **découvertes automatiquement** ; **aucune URL,
  page, slug ou mot-clé SEO AutoMecanik n'est inventé**.
- Pas de `vehicle.slug` libre → **référence à un véhicule canonique existant**.
- Diagnostic basé sur `__diag_system` / `__diag_symptom` **existants**.
- Déduplication par **URL canonique + hash de contenu**.
- **0 écriture WIKI/DB/SEO** sans validation humaine ; **0 promotion automatique**.

## Options Considérées

### Option A : Moteur de découverte+scoring+capture GOUVERNÉ (RETENUE)

**Description** : autonomie réelle jusqu'à `CAPTURED_NEEDS_REVIEW` ; humain garde autorité +
promotion. Étend la boucle existante. Poids `source_score` versionnés au Vault.

**Avantages** : lève le goulot « URLs fournies » ; couverture réelle des 4 types ; provenance +
scoring explicables et auditables ; sécurité (SSRF/robots/injection) et séparation ADR-031
préservées ; pas de nouvelle plateforme.

**Inconvénients** : surface de sécurité web nouvelle (mitigée par le filtre pré-capture + protections
obligatoires) ; nécessite un backend de recherche (absent aujourd'hui) ; coût de gouvernance des
poids `source_score`.

### Option B : Statu quo (capture humaine / URLs fournies seulement)

**Description** : conserver `agent-capture-policy.md` « no agent scraping ».

**Inconvénients** : goulot humain permanent ; worklist reste 100 % TODO ; diagnostic/constructeur
jamais couverts. **Rejetée par l'owner (2026-07-15).**

### Option C : Autonomie totale incluant l'auto-promotion

**Description** : le moteur promeut aussi en WIKI/SEO sans humain.

**Inconvénients** : viole la séparation ADR-031, l'anti-inflation ADR-088/091, la sécurité
valeur-numérique ADR-093 ; risque de duplicate/pollution SEO ; source inconnue auto-autoritaire.
**Rejetée (dangereuse).**

## Justification

Option A satisfait l'exigence owner (autonomie réelle de découverte) **sans** sacrifier les
garde-fous qui ont une raison d'être prouvée : la séparation raw/wiki (ADR-031), l'anti-inflation
d'autorité (ADR-088/091), la sécurité valeur-numérique (ADR-093), et la sécurité web (SSRF/robots/
injection). Le déplacement du point de validation d'autorité (*avant-capture* → *avant-promotion*)
est le **minimum** nécessaire pour permettre la capture automatique tout en gardant l'humain maître
de ce qui devient « autoritaire » et de ce qui est publié.

## Définition de « OPÉRATIONNEL » (critère de clôture)

Le scraper n'est déclaré opérationnel qu'après **4 pilotes réels (1 par type), SANS URL fournie
manuellement**, prouvant chacun : découverte réelle · classement explicable · capture RAW ·
provenance complète · corroboration + contradictions visibles · **amélioration mesurée de la
couverture** · **2ᵉ exécution idempotente** · **0 écriture WIKI/DB/SEO sans validation** · tests CI
+ rapport reproductible. Tant que ces 4 pilotes n'ont pas réussi, on ne présente **rien** comme
« scraper opérationnel ».

## Conséquences

**Change (après acceptation)** :
- `automecanik-raw/docs/agent-capture-policy.md` : amendé (découverte auto gouvernée autorisée,
  filtre sécurité pré-capture obligatoire).
- `automecanik-raw/_schemas/ingestion-worklist.schema.json` : `subject_type` + capture étendus aux
  4 types ; provenance de capture (D4) formalisée.
- `automecanik-raw/_schemas/completeness/` : profils `constructeur` (+ complétion diagnostic).
- Nouveau fichier de **poids `source_score` versionné au Vault** (gouverné, explicable).
- Nouveau module de découverte/scoring **branché sur les briques RAW existantes** (pas de plateforme).

**Ne change PAS** : séparation 4-couches ADR-031 · RAG=chatbot · 0 auto-promotion · validation
humaine d'autorité (déplacée avant-promotion) · sécurité valeur-numérique ADR-093 · pas d'URL/slug/kw
AutoMecanik inventé.

**Dépendances / follow-ups** (GO owner séparés) : contrats RAW 4 types (PR raw) ; implémentation du
moteur (PR) ; 4 pilotes réels ; choix du backend de recherche web (gouverné, respect licences/robots).

## Non-goals

- Pas de promotion/publication automatique.
- Pas de production de contenu par le RAG.
- Pas de nouvelle plateforme / control-plane / SEO-platform parallèle.
- Pas de `vehicle.slug` libre ni d'entité/URL/slug AutoMecanik inventés.
