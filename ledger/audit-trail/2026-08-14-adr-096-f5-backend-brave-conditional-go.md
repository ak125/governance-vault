---
type: follow-up-decision
decision_id: ADR-096-F5-backend
title: "Backend de découverte web — Brave Search API, CONDITIONAL_GO"
date: 2026-08-14
owner: Fafa
status: conditional
blocking_precondition: explicit_storage_rights
parent_adr: ADR-096
follow_up: "F5 — choix gouverné du backend de recherche web"
related_prs:
  governance-vault:
    - 346  # source-score-weights@v1 (proposed)
  automecanik-raw:
    - 48   # F4a ceiling harness + plaquette-de-frein-reference-v1
related_adr:
  - ADR-096
  - ADR-062
---

# B1 — Backend de découverte : Brave Search API, sous condition

> ADR-096 §Follow-ups déclare le « choix gouverné du backend de recherche web » comme
> **GO owner séparé**. Cette entrée l'exerce. Elle ne modifie aucune clause d'ADR-096.

## Décision

```
selected_backend: brave-search-api
decision: CONDITIONAL_GO

allowed_use:
  - discovery report-only
  - URL candidates
  - title / rank / query provenance
  - snippet = DISCOVERY_HINT_ONLY

forbidden_use:
  - snippet comme preuve
  - Brave Answers
  - contenu Brave comme RAW
  - ranking Brave comme source_score
  - fetch automatique d'un domaine non approuvé

contractual_precondition:
  explicit_storage_rights = REQUIRED
```

## La condition est bloquante, et elle n'est pas théorique

Les conditions standard interdisent de stocker ou mettre en cache les résultats, même
partiellement, hors stockage transitoire. Un plan accordant des *storage rights* peut lever
cette restriction.

Or §D4 exige de persister une partie de la réponse de découverte — au minimum la requête,
l'URL candidate, son rang et la provenance. **Le plan standard est donc NO-GO pour notre
usage.** B1 ne devient GO qu'avec un contrat autorisant explicitement cette conservation.

Tant que cette preuve n'est pas établie : **aucune clé, aucun code réseau, aucune
intégration.**

## Pourquoi ce backend, et pourquoi ce n'est pas une question de ranking

Le critère n'est pas « le meilleur classement » — ce n'est justement pas son rôle. Le backend
occupe une fonction étroite : trouver des URLs candidates, puis laisser `source_score` et RAW
décider.

Brave dispose de son propre index indépendant et ne revend pas les SERP d'un tiers, ce qui
donne une chaîne de dépendance plus courte.

**Exa** est techniquement excellent — URL directe, filtres de domaine, recherche sémantique.
Mais aucune autorisation aussi nette n'a été trouvée sur notre droit persistant d'archiver la
réponse. *Le silence n'est pas une permission* : pour §D4, il est traité comme une réserve.

**Tavily** pose le même problème, avec une complexité supplémentaire : sa Search API retourne
systématiquement du contenu extrait en plus de l'URL. Ses conditions définissent l'Output sans
donner un droit d'archivage suffisamment explicite, et reportent sur le client la
responsabilité des conditions applicables aux services tiers.

**SerpAPI** reste techniquement viable — sa classification `DIRECT_SOURCE_URL` a été corrigée
en révision 2 de la matrice — mais ajoute une double dépendance : le prestataire *et* le moteur
dont il revend les SERP. Pour une fonction aussi étroite, cette couche supplémentaire n'est pas
justifiée.

## Contrainte architecturale : le ranking du fournisseur n'est pas le nôtre

```
Brave rank
    ↓
candidate pool
    ↓
normalisation + déduplication
    ↓
hard gates applicables à la découverte
    ↓
source-score-weights@v1
    ↓
NOTRE ranking
```

Le classement propriétaire sert **uniquement à constituer un pool**. Changer plus tard de
backend ne doit modifier ni §D3, ni les poids, ni la sémantique du classement.

F3 devra donc poser une interface neutre dès sa première ligne :

```
DiscoveryBackend.search(query) -> Candidate[]

Candidate:
  url · title · provider_rank · provider · query
  request_id (optionnel) · snippet_hint (optionnel)
```

**Aucun objet propre au fournisseur ne doit contaminer le contrat RAW.**

## Ce que cette décision ne débloque pas

```
A     source-score-weights@v1        proposed — vault#346
F4a   plafond de recall               mesuré — raw#48, 2,8 % provisoire
B0    découverte ouverte / capture fermée   décidé
B1    Brave Search API                CONDITIONAL_GO
      └─ storage rights explicites     précondition NON LEVÉE
D2    fetch / capture                  incomplet — Porte 1 2/7, Porte 2 2,5/8
F3    moteur                           bloqué par A + précondition B1
capture automatique                    NO-GO
```

Ordre à respecter :

```
A accepté + hash de projection
        +
preuve des storage rights
        ↓
F3 découverte report-only
        ↓
calibration sur plaquette-de-frein-reference-v1
        ↓
revue de domaines, dans l'ordre imposé par la référence humaine
```

## Contexte de mesure ayant conduit à B0-r2

Le plafond de recall de l'allowlist actuelle, mesuré sur `plaquette-de-frein-reference-v1`
(instantané `PROVISIONAL_DRAFT`) : **2,8 % au global, 0 % sur les 15 sources `primary`**.

C'est ce chiffre qui justifie d'ouvrir l'espace de **découverte** en report-only — et non
d'ouvrir l'allowlist de **capture**. Les deux périmètres restent distincts : un candidat hors
allowlist est signalé `DISCOVERED_UNAPPROVED_DOMAIN`, jamais récupéré, et passe par
`DOMAIN_REVIEW_REQUIRED` avant tout fetch. Les 3 domaines explicitement `deny` restent `deny` :
leur présence dans le corpus de référence ne vaut pas demande de réouverture.
