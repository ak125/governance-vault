---
type: runbook
scope: seo/r7/rag
surface: R7_BRAND
date: 2026-04-21
owner: Fafa
script: scripts/rag/download-brand-oem-corpus.py
tags: [runbook, r7, rag, oem, corpus, wikipedia, wikidata, rappel-conso, ops]
---

# Runbook — `download-brand-oem-corpus.py`

> **Script** : [`scripts/rag/download-brand-oem-corpus.py`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/scripts/rag/download-brand-oem-corpus.py) (monorepo)
> **Rôle** : télécharge un corpus brut multi-source par marque pour **aider** la curation éditoriale R7 (FAQ / common_issues / maintenance_tips)
> **Sources** : Wikipedia FR + Wikidata SPARQL + Rappel Conso FR (défaut) — Wikipedia EN + NHTSA (opt-in)
> **Complémentaire à** : [[runbook-build-brand-rag]] (facts Wikidata+DB+Wikipedia, scope différent)
> **Consommateur aval** : runbook-admin-brand-editorial ([vault PR #26](https://github.com/ak125/governance-vault/pull/26)) (UI curation humaine)

---

## À quoi ça sert

Produit un dossier plat par marque dans `/opt/automecanik/rag/knowledge/web/brands/{alias}/` contenant :

- la page principale Wikipedia FR en plaintext
- la liste des modèles Wikipedia FR (si la page existe)
- la liste structurée des modèles + motorisations Wikidata SPARQL (JSON)
- les rappels consommateurs FR avec défauts/risques structurés (JSON)
- (opt-in) la page principale Wikipedia EN + les recalls NHTSA US

Chaque fichier inclut son frontmatter YAML / `_meta` JSON avec `source_uri`, `fetched_at`, `script`, `schema_version`. Provenance garantie.

Ce corpus **alimente** la curation humaine : l'admin ouvre `/admin/brands-seo?brand={alias}` en parallèle du corpus pour **rédiger** ses FAQ / issues / maintenance_tips marque-level (cf. runbook-admin-brand-editorial ([vault PR #26](https://github.com/ak125/governance-vault/pull/26))).

## Ce que ce script NE fait PAS

- **Aucune synthèse LLM** (règle : source canonique + humain seulement)
- **N'écrit rien dans `__seo_brand_editorial`** — c'est du corpus brut uniquement
- **Ne déclenche pas d'enrichissement R7** — zéro side-effect DB
- **N'enrichit pas le frontmatter RAG** des `.md` constructeur — c'est le job de [[runbook-build-brand-rag]]

## Sources détaillées

### Défaut (FR-only, fiable)

| Source | Fichier généré | API | Volume typique |
|---|---|---|---|
| Wikipedia FR main | `wikipedia-fr-main.md` | fr.wikipedia.org/w/api.php | 30-100 KB |
| Wikipedia FR list models | `wikipedia-fr-models.md` | idem (si page existe) | 10-40 KB |
| Wikidata SPARQL models | `wikidata-models.json` | query.wikidata.org | 100-200 modèles |
| Rappel Conso FR v2.1 | `rappel-conso-fr.json` | data.economie.gouv.fr/api/explore/v2.1/ | 0-100 fiches |

### Opt-in

| Source | Fichier | Pourquoi opt-in |
|---|---|---|
| Wikipedia EN main | `wikipedia-en-main.md` | Site + SEO sont FR — du contenu EN collé dans l'éditorial pollue le signal. Usage : cross-ref technique, à traduire avant de poser dans l'UI |
| NHTSA recalls US | `nhtsa-recalls.json` | L'API `recallsByVehicle` exige un triplet `(make, model, modelYear)`. Sans liste de modèles fournie, la requête retourne 0. Le script lit `wikidata-models.json` (s'il existe) pour énumérer → ~50-200 requêtes/marque |

## Pré-requis

```bash
cd /opt/automecanik/app
set -a && source backend/.env && set +a  # charge SUPABASE_SERVICE_ROLE_KEY
pip install requests  # déjà installé sur DEV
```

Variables d'env requises : `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.

## Commandes

### Dry-run une marque (planification)

```bash
python3 scripts/rag/download-brand-oem-corpus.py --brand alfa-romeo --dry-run
```

Sortie attendue :
```
=== download-brand-oem-corpus.py ===
Sources activées : ['rappel-conso', 'wikidata', 'wikipedia-fr']
Output root      : /opt/automecanik/rag/knowledge/web/brands
[MODE DRY-RUN]
Marques à traiter : 1

[1/1] alfa-romeo (id=13, name=ALFA ROMEO)
  [DRY-RUN] output → /opt/automecanik/rag/knowledge/web/brands/alfa-romeo
  [DRY-RUN] would fetch FR:Alfa Romeo
  [DRY-RUN] would fetch FR:Liste des modèles Alfa Romeo
  [DRY-RUN] would SPARQL Wikidata Q26921
  [DRY-RUN] would fetch Rappel Conso ALFA ROMEO
```

### Run réel une marque

```bash
python3 scripts/rag/download-brand-oem-corpus.py --brand alfa-romeo
```

Sortie attendue :
```
[1/1] alfa-romeo (id=13, name=ALFA ROMEO)
  ✅ wikipedia-fr-main (37888c)
  ✅ wikidata-models (117 entrées)
  ✅ rappel-conso-fr (7 fiches)
```

### Batch N marques

```bash
python3 scripts/rag/download-brand-oem-corpus.py --limit 5
# traite les 5 premières marques par alias (alfa-romeo, audi, …)
```

### Source spécifique

```bash
python3 scripts/rag/download-brand-oem-corpus.py --source wikidata,rappel-conso
# ne télécharge pas Wikipedia, utile pour un rafraîchissement ciblé
```

### Force re-download

```bash
python3 scripts/rag/download-brand-oem-corpus.py --brand bmw --force
# écrase les fichiers existants (sinon skip)
```

### Opt-in Wikipedia EN + NHTSA

```bash
# Wikipedia EN seul (cross-ref technique)
python3 scripts/rag/download-brand-oem-corpus.py --brand bmw --source wikipedia-en

# Tout avec NHTSA (nécessite wikidata-models.json déjà présent)
python3 scripts/rag/download-brand-oem-corpus.py --brand bmw --source all
```

## Quand lancer

| Trigger | Fréquence | Commande |
|---------|-----------|----------|
| Avant curation d'une marque pilote | 1×/marque | `--brand {alias}` |
| Rafraîchir le corpus toutes marques | trimestriel | (pas d'alias, pas de limit) |
| Après publication d'un rappel FR connu | à la demande | `--brand {alias} --source rappel-conso --force` |

**NE PAS lancer en cron quotidien** : les données bougent peu entre 2 sessions, rate limit Wikipedia + Wikidata.

## Tests réels (2026-04-21)

| Marque | Wiki FR | Wikidata modèles | Rappel Conso FR |
|---|---|---|---|
| alfa-romeo | 38 KB | 117 | 7 fiches |
| bmw | 38 KB | 150 | 100 fiches |
| peugeot | 59 KB | 150 | 100 fiches |
| renault | 97 KB | 150 | 79 fiches |
| citroen | 55 KB | 132 | 100 fiches |

Volume Rappel Conso corrélé à la part de marché FR (Alfa faible, marques FR/DE dominantes).

## Pièges connus

### Titre Wikipedia non trouvé

`auto_marque.marque_name` est stocké en MAJUSCULES (`PEUGEOT`, `CITROËN`). Wikipedia exige la casse normale (`Peugeot`, `Citroën`). Le script applique `name.title()` par défaut. Si un cas reste non trouvé (ex: `MG Motor` stocké comme `MG`), ajouter un override dans `WIKI_TITLE_OVERRIDES_FR` du script.

### Rappel Conso FR : 0 résultats

Vérifier :
1. Le dataset `rappelconso-v2-gtin-espaces` existe (API v2.1) ; l'ancien `rappelconso0` v1.0 est **déprécié**.
2. La `sous_categorie_produit` contient `automobiles` (pas `véhicules`) dans la taxonomie actuelle.
3. Certaines marques ont 0 rappel en France — c'est légitime, pas un bug.

### NHTSA retourne 0

L'API exige `make`, `model`, `modelYear` — les 3 obligatoires. Si `wikidata-models.json` n'existe pas pour la marque, le script loggue un warning `NHTSA: pas de modèles` et skip. Pré-requis : lancer d'abord `--source wikidata` pour obtenir la liste de modèles.

### Wikipedia EN vs FR

**Ne jamais coller directement** du contenu `wikipedia-en-main.md` dans l'éditorial R7 FR. Le site et le SEO sont FR. Utiliser EN seulement pour cross-vérifier un détail technique, puis rédiger en FR dans l'UI.

## Output layout

```
/opt/automecanik/rag/knowledge/web/brands/
├── alfa-romeo/
│   ├── wikipedia-fr-main.md        # FR prose
│   ├── wikidata-models.json        # 117 modèles structurés
│   └── rappel-conso-fr.json        # 7 rappels FR
├── bmw/
│   └── ...
└── peugeot/
    └── ...
```

Chaque fichier a un frontmatter ou `_meta` avec :
```yaml
source_type: corpus
source_label: wikipedia-fr | wikidata-sparql-models | rappel-conso-fr | nhtsa-recalls | wikipedia-en
source_uri: <URL exacte d'origine>
fetched_at: '2026-04-21T17:12:00+00:00'
script: download-brand-oem-corpus
schema_version: 1
```

## Règles dérivées

1. **0 LLM, 0 scraping HTML** — uniquement API publiques ou SPARQL. Les regex HTML fragiles (observées sur l'ancien script gammes) sont bannies.
2. **Provenance obligatoire** — chaque fichier cite sa `source_uri` d'origine. L'admin qui réutilise un fragment doit pouvoir citer la source.
3. **Corpus brut, pas synthèse** — le script ne condense rien. Le second étage (curation admin ou futur extracteur de candidats) reste à la charge de l'humain.
4. **FR-first** — tout ce qui est EN/US est opt-in et signalé comme "cross-ref, ne pas coller".
5. **Idempotent par défaut** — skip si le fichier existe, sauf `--force`.

## Références

- PR introduction : https://github.com/ak125/nestjs-remix-monorepo/pull/99
- Script monorepo : [`scripts/rag/download-brand-oem-corpus.py`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/scripts/rag/download-brand-oem-corpus.py)
- Pattern inspiré : [`scripts/rag/download-oem-corpus.py`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/scripts/rag/download-oem-corpus.py) (Phase F gammes)
- Runbook sibling (facts stables) : [[runbook-build-brand-rag]]
- Runbook aval (curation admin UI) : runbook-admin-brand-editorial ([vault PR #26](https://github.com/ak125/governance-vault/pull/26))
- Architecture R7 : [[r7-brand-editorial-live-sync]]
- Règle canon surface purity : [[r7-surface-purity-no-cross-surface-urls]]
