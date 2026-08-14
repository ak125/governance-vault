# SOURCE-SCORE-WEIGHTS — spécification du contrat de poids

> Contrat Layer 2 exigé par [[ADR-096-governed-automatic-source-discovery]] §D3, gouverné
> selon ADR-062. Fichier : `ledger/policies/source-score-weights.v1.json`.
> **Statut : `proposed` — revue owner requise, aucun merge automatique.**

## Pourquoi ce contrat existe

ADR-096 §D3 impose que les poids de `source_score` soient un **contrat versionné au Vault,
projeté déterministiquement vers RAW**, et que **le runtime lise la projection, jamais le Vault**.
Sans ce contrat, la chaîne est bloquée mécaniquement : le schéma de capture RAW
(`auto-capture-frontmatter.schema.json`) rend `weights_contract_ref`, `weights_hash` et
`profile_ref` **obligatoires**. Toute capture `discovery.mode: auto` est donc schéma-invalide
tant que ce contrat n'existe pas.

Les tests RAW nomment déjà la cible attendue : `source-score-weights@v1`
(`_scripts/tests/test_adr096_contracts.py:267`).

## Ce que le contrat n'est pas

Ce n'est **pas** un scorer. Il ne contient aucune formule de calcul de dimension : il déclare
les dimensions, leurs poids, leurs planchers, leurs plafonds et les profils applicables. Comment
une dimension est *mesurée* relève de l'implémentation du scorer, versionnée séparément par
`scorer_version`.

Ce n'est **pas** une source de vérité runtime. Le runtime lit la projection publiée dans
`99-meta/canon-hashes.json`, jamais ce fichier.

## Les cinq sections

### `hard_gates` — cinq assertions positives

Nommées positivement parce que le schéma RAW impose `hard_gates[].passed: const true` : une
capture persistée ne peut porter qu'un gate **franchi**. Un objet `ssrf: passed=true` serait
absurde ; `network_target_safe: passed=true` se lit.

| assertion | porte | reason code de rejet |
|---|---|---|
| `license_permitted` | 2 | `LICENSE_RESTRICTED` |
| `robots_permitted` | 1 | `ROBOTS_DENIED` |
| `network_target_safe` | 1 | `SSRF_BLOCKED` |
| `content_safe` | 2 | `HOSTILE_CONTENT` |
| `subject_relevant` | 2 | `OUT_OF_SCOPE` |

Un hard gate non franchi **rejette**. Aucune dimension ne le compense.

### `dimensions` — les neuf de §D3

Somme des poids = 100. `floor` est un minimum **non compensable** sur la valeur brute ;
`cap` est le maximum atteignable, égal au poids sauf restriction d'autorité.

`penalites_duplication_contradiction` a une **polarité inversée** : la valeur mesure l'absence
de duplication et de contradiction.

### `facets` — ce qu'une source externe peut documenter

Les identifiants proviennent exclusivement des profils de complétude RAW
(`_schemas/completeness/<type>.yaml`). Aucun n'est inventé.

La distinction est de nature, pas de commodité : `discovery_eligible` désigne ce qu'une source
**externe** peut documenter ; `non_discovery` regroupe les contraintes d'identité canonique, de
structure, de couverture, de provenance DB interne et de maillage.

Le cas qui fixe la règle est `sections_h2_canon` : le moteur peut chercher le **contenu**
nécessaire aux sections, mais il ne doit pas scorer une source sur sa capacité à prouver que
*les H2 canoniques existent*. Confondre les deux remélangerait la qualité d'une source avec la
complétude de la projection WIKI.

**Seul le profil `gamme` est validé par l'owner.** Les trois autres portent
`derived_by_rule: true` : la même règle y a été appliquée mécaniquement, et leur classification
doit être confirmée en revue. Une question reste ouverte sur `probable_causes_with_gammes`, qui
mêle un fait documentable et un maillage interne.

### `profiles` — `entity_type` × `discovery_facet`

Mécanique reprise de `automecanik-wiki/_scripts/shadow_score.py`, dont le framework est éprouvé
et testé :

- une dimension hors profil est **neutralisée** — exclue du total *et* des planchers, jamais
  comptée comme un zéro ;
- le total est **renormalisé** sur les dimensions applicables, pour qu'un type à peu de
  dimensions ne soit pas désavantagé ;
- un plancher non atteint **plafonne le rang** et émet `floor_not_met:<dimension>`.

Ce qui n'est **pas** repris de `shadow_score` : ses poids sont codés en dur dans le script
(lignes 32-41). Acceptable pour un scorer report-only sous ADR-088 ; interdit ici par §D3.

### `authority_policy`

`source_type_authority` associe une autorité brute à chacune des 9 valeurs de l'enum fermé
partagé par `ingestion-allowlist.schema.json` et `auto-capture-frontmatter.schema.json`.

`unknown_source_cap` plafonne un domaine hors allowlist à **9 points**, soit **sous le plancher
de la dimension autorité (11)**. Conséquence mécanique : une source inconnue échoue toujours son
plancher d'autorité et ne peut jamais atteindre le rang d'une source déjà validée — sans qu'un
seuil supplémentaire soit nécessaire.

## Calibration — séparée de la stabilité du framework

Le framework est stable. **Les nombres sont v0.** Chaque profil porte son propre statut :

```
gamme         shadow_calibration    reference_set: plaquette-de-frein-reference-v1
vehicle       shadow_unvalidated    reference_set: null
diagnostic    shadow_unvalidated    reference_set: null
constructeur  shadow_unvalidated    reference_set: null
```

`plaquette-de-frein` dispose de 72 sources déjà annotées par tier — une référence humaine
préexistante. Elle calibre **les profils gamme uniquement**. Elle ne valide ni `vehicle`, ni
`diagnostic`, ni `constructeur`, et aucune moyenne inter-types ne peut le laisser croire :
§OPÉRATIONNEL exige que *chaque* pilote franchisse *son* plancher.

Un profil `shadow_unvalidated` peut produire un score en **report-only**. Il ne doit pas servir
de critère de sélection pour une capture durable.

## Projection — mécanisme existant, à étendre

Aucun système de projection n'est à construire. Le vault publie déjà des hashes canoniques
consommés par les dépôts aval :

```
99-meta/canon-hashes.json          clé actuelle : aec
   ↓  repository_dispatch: canon-updated
automecanik-raw
   .github/workflows/agent-exit-contract-hash.yml
   _scripts/check-aec-hash.sh      push · PR · cron · dispatch · manuel
```

Après acceptation de ce contrat : ajouter une clé `source-score-weights` via
`_scripts/compute-canon-hashes.py` — le fichier de hashes est **généré, jamais édité à la
main** — et poser côté RAW un vérificateur calqué sur `check-aec-hash.sh`.

`metadata.distribution_sha256` reste `null` dans ce document : il est rempli par la projection,
pas par l'auteur.

## Canonicalisation et hash

RFC 8785 (JCS), UTF-8. Le hash porte sur le document canonicalisé **privé du champ qui le
porte** (`metadata.distribution_sha256`). Toute autre clé entre dans le hash — y compris les
notes : modifier une note change le hash, donc impose une version.

## Ce qui reste à trancher en revue

1. La classification des facettes pour `vehicle`, `diagnostic` et `constructeur`
   (`derived_by_rule: true`).
2. Le sort de `probable_causes_with_gammes`, à confirmer ou à scinder.
3. Les poids v0 eux-mêmes, qui n'ont pas encore rencontré une seule source réelle.
4. Les 5 `source_type` éditoriaux n'ont **aucun domaine allowlisté**
   (`ingestion-allowlist.yaml:33-36`, décision owner license-sensible en attente) : le recall
   atteignable sur ces familles est plafonné à zéro tant que cette décision n'est pas prise.
