---
type: runbook
scope: seo/r7/rag
surface: R7_BRAND
date: 2026-04-21
owner: Fafa
script: scripts/rag/build-brand-rag.py
tags: [runbook, r7, rag, wikidata, wikipedia, ops]
---

# Runbook — `build-brand-rag.py`

> **Script** : [`scripts/rag/build-brand-rag.py`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/scripts/rag/build-brand-rag.py) (monorepo)
> **Rôle** : génère/rafraîchit les 36 `.md` constructeur canoniques dans `/opt/automecanik/rag/knowledge/constructeurs/`
> **Sources** : Wikidata SPARQL + Supabase RPC + Wikipedia REST

---

## À quoi ça sert

Alimente le frontmatter YAML des fichiers RAG constructeur avec les données factuelles stables (country, founded_year, group, headquarters, logo_uri, top_models, top_engines, history). Zero LLM, zero scraping HTML.

Lu ensuite par `R7BrandEnricherService.loadBrandRag()` (backend) lors de l'enrichissement DB des pages R7.

**Complémentaire** : le contenu éditorial curé (FAQ, common_issues, maintenance_tips) vient de la table DB `__seo_brand_editorial`, **pas de ce script**.

## Quand lancer

| Trigger | Fréquence typique | Commande |
|---------|--------------------|----------|
| Nouvelle marque ajoutée en DB (`auto_marque`) | Rare (quelques/an) | `python3 scripts/rag/build-brand-rag.py --brand {alias}` |
| Rafraîchissement périodique des faits Wikidata | 1×/an suffit | `python3 scripts/rag/build-brand-rag.py` (tous) |
| Correction ciblée après changement catalogue | À la demande | `python3 scripts/rag/build-brand-rag.py --brand {alias}` |
| Test en dry-run avant run réel | Toujours d'abord | Ajouter `--dry-run` |

**NE PAS lancer en boucle/cron** : les données Wikidata bougent très peu pour des constructeurs établis. Cron quotidien = bruit, rate limits Wikidata, git churn pour rien.

## Préparation

```bash
cd /opt/automecanik/app
set -a && source backend/.env && set +a  # charge SUPABASE_SERVICE_ROLE_KEY
pip install requests pyyaml  # (déjà installé sur DEV)
```

Variables d'env requises : `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (les deux dans `backend/.env`).

## Commandes

### Dry-run une marque (observation)

```bash
python3 scripts/rag/build-brand-rag.py --brand alfa-romeo --dry-run
```

Sortie attendue :
```
🏭 alfa-romeo (id=13)
  QID résolu : Q26921
  Wikidata Q26921 → country=Italie founded=1910 group=Stellantis
  DB: 23 vehicles → 7 models, 6 engines
  Wikipedia : OK (336c)
  [DRY-RUN] frontmatter valide, 18 champs
```

### Run réel une marque (écrit le `.md`)

```bash
python3 scripts/rag/build-brand-rag.py --brand alfa-romeo
```

### Run 3 marques test (qualité avant mass)

```bash
python3 scripts/rag/build-brand-rag.py --limit 3 --dry-run
python3 scripts/rag/build-brand-rag.py --limit 3
```

### Run toutes les 36 marques

```bash
python3 scripts/rag/build-brand-rag.py  # prend ~2-3 min (rate limit Wikidata + Wikipedia)
```

### Re-enrichir DB R7 après rebuild `.md`

```bash
# Récupérer les marque_id via Supabase
curl -s -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "$SUPABASE_URL/rest/v1/auto_marque?select=marque_id&marque_display=eq.1&order=marque_alias" | jq -c '[.[].marque_id]'

# Login admin + enrich-batch
COOKIE=/tmp/r7-admin.cookie
curl -s -c $COOKIE -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@autoparts.com","password":"{password}"}'

curl -s -b $COOKIE -X POST http://localhost:3000/api/admin/r7/enrich-batch \
  -H "Content-Type: application/json" \
  -d '{"marqueIds":[13,22,33,...]}'  # coller le résultat du jq ci-dessus
```

## Sources détaillées

### Wikidata SPARQL (`country`, `founded_year`, `group`, `headquarters`, `logo_uri`)

Query stricte avec filtre P31 pour éviter les dérives :

```sparql
SELECT ?country ?countryLabel ?founded ?parent ?parentLabel
       ?hq ?hqLabel ?hqCountry ?hqCountryLabel ?logo WHERE {
  BIND(wd:{QID} AS ?entity)
  OPTIONAL { ?entity wdt:P17  ?country . }          # country of origin
  OPTIONAL { ?entity wdt:P571 ?founded . }          # inception
  OPTIONAL { ?entity wdt:P749 ?parent .             # parent organization (strict)
             FILTER(?parent != ?entity) }
  OPTIONAL { ?entity wdt:P159 ?hq .                 # headquarters location
             OPTIONAL { ?hq wdt:P17 ?hqCountry . } }
  OPTIONAL { ?entity wdt:P154 ?logo . }             # logo image
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en" }
}
LIMIT 1
```

**Pourquoi P749 seul, pas P127** : P127 (owned by) remonte des **actionnaires institutionnels** (BlackRock, fonds de pension) pour les sociétés cotées. Seul P749 (parent organization) garantit un vrai lien de filiation industrielle. Dérive observée sur BMW (P127 → "Stefan Quandt" puis "BlackRock") avant correction.

### Résolution QID via `wbsearchentities`

```python
# 1. Lookup dans les overrides manuels (volkswagen, toyota)
if alias in BRAND_QID_OVERRIDES: return BRAND_QID_OVERRIDES[alias]
# 2. Sinon : recherche Wikidata
params = {"action": "wbsearchentities", "search": brand_name,
          "language": "fr", "type": "item", "limit": 5}
# 3. Prioriser un hit dont la description contient "constructeur|automobile|car brand"
```

**Pourquoi des overrides** : la recherche peut remonter l'entité "groupe" (Volkswagen Group Q156578) au lieu de la marque (Volkswagen Q246). 2 overrides actuels : `volkswagen` et `toyota`.

### Supabase RPC `get_brand_bestsellers_optimized`

```python
POST $SUPABASE_URL/rest/v1/rpc/get_brand_bestsellers_optimized
Body: {"p_marque_id": 13, "p_limit_vehicles": 40, "p_limit_parts": 0}
```

Retourne `{vehicles: [...], parts: [...]}`. Le script agrège côté client :
- `top_models` : group by `modele_id`, tri par fréquence, limit 8
- `top_engines` : group by `(fuel, power_ps)`, tri par fréquence, limit 6

### Wikipedia REST summary

```python
# 1. Résoudre titre Wikipedia depuis QID via Wikidata sitelinks (frwiki)
GET https://www.wikidata.org/w/api.php
  ?action=wbgetentities&ids=Q26921&props=sitelinks&sitefilter=frwiki
# 2. Fetch extract prose
GET https://fr.wikipedia.org/api/rest_v1/page/summary/{title_path}
```

Retourne un `extract` prose prêt (~200-500 caractères). **Pas de HTML scraping**, API officielle.

## Cas d'erreur connus

| Symptôme | Cause probable | Remediation |
|----------|----------------|-------------|
| `QID Wikidata introuvable` | `wbsearchentities` remonte une entité non-automobile | Ajouter dans `BRAND_QID_OVERRIDES` du script avec le QID correct |
| `country=None` | Wikidata n'a pas de P17 sur cette entité (ex: Smart Q156490) | Laisser null, ou curer manuellement côté DB admin UI |
| `group=None` pour marque filiale | Wikidata P749 non renseigné ou entité parente supprimée | Accepter ou corriger sur Wikidata (souvent long) |
| `0 top_models` / `0 top_engines` | Table `__cross_gamme_car_new` (CGC_LEVEL=2) vide pour cette marque | Marque dormante (daewoo, lada, ds) — normal, accepter |
| `history=None` | Pas d'extract Wikipedia (article trop court, redirect…) | Lookup manuel + éditer le `.md` |
| Rate limit Wikidata (HTTP 429) | Trop de requêtes d'affilée | Le script a déjà 0.8s delay ; attendre 5 min et relancer avec `--brand` ciblé |

## Invariants (NE PAS casser)

1. **Préserve le body markdown** existant du `.md`. Seul le frontmatter est régénéré.
2. **Ne touche PAS** aux champs éditoriaux (`faq`, `common_issues`, `maintenance_tips`) — ceux-ci vivent en DB (`__seo_brand_editorial`).
3. **`wikidata_qid` traçable** : toujours inscrit dans le frontmatter, permet de retrouver la source de vérité.
4. **`lifecycle.content_hash`** : hash déterministe du payload hors lifecycle, détecte les changements réels.
5. **Schema Zod au chargement** : `brand-rag-frontmatter.schema.ts` valide côté enricher. Si le `.md` devient non conforme, l'enricher log warn + fallback empty (fail-safe). JAMAIS modifier ce schéma sans passer par `safeParse`.

## Checklist opérationnelle

Avant de run sur toutes les marques :

- [ ] Backup des 36 `.md` (git snapshot suffit, tout est versionné)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` chargé dans l'env
- [ ] Dry-run sur 3 marques représentatives (dont 1 défunte type daewoo)
- [ ] Si résultats OK, run complet 36 marques
- [ ] Diff git des `.md` pour inspection rapide (`git diff knowledge/constructeurs/`)
- [ ] Re-enrich DB R7 via `enrich-batch` endpoint
- [ ] Vérifier 36/36 PUBLISH en DB (`SELECT COUNT(*) FROM __seo_r7_pages WHERE seo_decision='PUBLISH'`)
- [ ] Commit + PR des `.md` modifiés

## Références

- Script : [`scripts/rag/build-brand-rag.py`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/scripts/rag/build-brand-rag.py)
- Schema Zod : [`backend/src/config/brand-rag-frontmatter.schema.ts`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/backend/src/config/brand-rag-frontmatter.schema.ts)
- Enricher consumer : [`backend/src/modules/admin/services/r7-brand-enricher.service.ts`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/backend/src/modules/admin/services/r7-brand-enricher.service.ts)
- Architecture complète : [[r7-brand-editorial-live-sync]]
- Pureté surface R7 : [[r7-surface-purity-no-cross-surface-urls]]
