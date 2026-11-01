---
type: follow-up-decision
decision_id: ADR-096-F5-backend-sitemap
title: "Backend de découverte — sitemaps + robots des domaines approuvés, GO report-only sans score"
date: 2026-09-30
owner: Fafa
status: accepted
parent_adr: ADR-096
follow_up: "F5 — choix gouverné du backend de recherche web"
selected_backend: sitemap-robots
decision: GO
discovery_scope: approved_domains_only
capture_scope: approved_domains_only
unapproved_domain_action: NEVER_CONTACTED
scoring: BLOCKED_UNTIL_PROJECTION_PUBLISHED
network_switch: "automecanik-raw manifests/ingestion-allowlist.yaml → discovery.network"
related_prs:
  automecanik-raw:
    - 58   # backend sitemaps + robots, construit et testé hors ligne
    - 59   # allowlist 1.1.0 + interrupteur discovery.network: DISABLED
  governance-vault:
    - 347  # B1 Brave Search API, CONDITIONAL_GO — inchangé
    - 349  # source-score-weights@v1 accepté, calibration report-only
related_adr:
  - ADR-096
  - ADR-062
---

# B2 — Backend de découverte : sitemaps + robots des domaines approuvés

> ADR-096 §Follow-ups fait du « choix gouverné du backend de recherche web » un **GO owner
> séparé**. [[2026-08-14-adr-096-f5-backend-brave-conditional-go]] (B1) l'a exercé une première
> fois pour Brave, sous une condition qui n'est toujours pas levée. Cette entrée l'exerce pour un
> second backend. Elle ne modifie aucune clause d'ADR-096 et ne change rien à B1.

## Décision

```
selected_backend: sitemap-robots
decision: GO — découverte report-only, SANS score

allowed_use:
  - lire robots.txt des domaines `allow` de l'allowlist RAW
  - lire les sitemaps et index de sitemaps que ces domaines déclarent
  - rapporter des URL candidates : url · provider · provider_rank · query · facet · lastmod
  - garder l'empreinte de chaque sitemap lu : url · sha256 · octets · lastmod

forbidden_use:
  - télécharger une page (fetched_pages = 0)
  - capturer, ou écrire sous sources/, normalized/ ou manifests/ de RAW
  - contacter un domaine `deny` ou absent de l'allowlist
  - suivre une directive Sitemap qui pointe vers un autre domaine
  - scorer les candidats (source_score)
  - traiter l'ordre d'un sitemap comme un classement de qualité
  - générer des mots-clés, des synonymes ou des traductions pour la requête
```

## Pourquoi ce backend

La fonction du backend reste celle que B1 a bornée : **constituer un pool d'URL candidates**,
puis laisser `source_score` et RAW décider. Les sitemaps y répondent sans intermédiaire : chaque
domaine publie lui-même, pour les robots, la liste de ses pages. Aucun index tiers, aucune clé,
aucun fournisseur dont les conditions encadreraient la conservation des résultats.

La précondition bloquante de B1 (`explicit_storage_rights`) porte sur les résultats d'un
fournisseur de recherche. **Elle n'a pas d'objet ici.** Ce qui est conservé se limite à ce que le
domaine publie pour les robots (URL, date de modification), dans un rapport d'audit, jamais dans
RAW. `robots.txt` est lu avant tout sitemap, et un sitemap interdit n'est pas demandé.

La limite est connue et assumée : un sitemap ne dit rien du contenu d'une page. Le filtrage se fait
sur les mots du chemin (slug et titre de l'entité, tels quels). Le rappel sera partiel. C'est une
mesure à produire, pas un défaut à masquer.

## Ce que cette entrée précise dans l'ordre de B1

B1 fixait : « A accepté + hash de projection + preuve des storage rights → F3 découverte
report-only ».

- **A est accepté** depuis la fusion de vault #349 (`ledger/policies/source-score-weights.v1.json`, `status: accepted`). Mais la projection
  n'est **pas** publiée : `distribution_sha256` vaut `null` et `projection_requirements` reste
  bloquant.
- **Les storage rights** sont une condition propre à Brave (voir ci-dessus).

Le hash de projection garantit que **le classement est le nôtre**. Or une découverte sans score ne
classe rien : `provider_rank` est l'ordre du fichier, et aucun poids n'est lu. La règle
`report_only_until_calibrated` du contrat interdit déjà qu'un score serve à choisir une capture.

D'où la précision, **limitée à ce backend et à la découverte sans score** : elle n'attend pas la
projection. **Le scoring des candidats, lui, reste dans l'ordre de B1** : après publication de la
projection et de son hash.

## Comment le réseau s'ouvre et se referme

| Élément | État | Référence |
|---|---|---|
| Code de découverte (sitemaps + robots, budgets, décompression bornée) | fusionné, testé sans réseau | RAW #58 (`eb72cc3`) |
| Interrupteur `discovery.network` | `DISABLED` | RAW #59 (`1827f9c`) |
| Passage à `REPORT_ONLY` | **commit owner** dans l'allowlist, après fusion de cette entrée | à venir |

- L'interrupteur est relu **avant chaque requête**. Repasser à `DISABLED` arrête un run en cours.
- Budgets par domaine (défauts du code) : 40 requêtes, 300 s, 2 000 URL retenues, 10 Mio reçus par
  sitemap, 50 Mio une fois décompressé, 50 000 entrées par sitemap, profondeur d'index ≤ 2,
  5 s entre deux requêtes.
- Le rapport part sur la sortie standard ou dans un fichier choisi. Tout chemin sous `sources/`,
  `normalized/` ou `manifests/` est refusé.
- Chaque rapport porte le mode réseau, la version du backend et l'empreinte de l'allowlist.
  `--previous` affiche ce qui a été ajouté, retiré ou modifié depuis le run précédent (ADR-096 :
  toute différence live reste visible et expliquée).

Revenir en arrière ne demande qu'un commit : `discovery.network: DISABLED`. Aucun état n'est laissé
dans RAW.

## Ce que cette décision ne débloque pas

```
scoring des candidats               bloqué — projection + hash non publiés
capture automatique (D7-2 « auto »)  NO-GO
capture en quarantaine d'une URL     hors de cette entrée — GO owner par run
domaine hors allowlist               jamais contacté ; l'ajouter = PR RAW justifiée
B1 Brave Search API                  inchangé — CONDITIONAL_GO, storage rights non levés
éligibilité des facettes             non vérifiée par RAW (projection_only) :
                                     le rapport porte NOT_VERIFIED_NO_PROJECTION
```

Cinq facettes du profil `gamme` ne sont pas encore classées par le contrat de poids :
`decision_brief`, `installation`, `location_on_vehicle`, `variants`, `web_research_family`. Un
rapport de découverte sur l'une d'elles ne la rend pas éligible. Leur classement relève d'une
version du contrat, pas de cette entrée.
