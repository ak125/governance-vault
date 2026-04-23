---
type: evidence-pack
date: 2026-04-23
owner: Fafa
duration: ~45m
session_id: alias-dict-roman-arabic-normalization
scope: SEO KW import — wiring + roman/arabic modele matching
related_files:
  - config/rag-alias-expansions.yaml
  - scripts/seo/import-gads-kp.py
  - backend/supabase/migrations/20260423_extract_vehicle_keywords_roman_arabic.sql
prototype_gamme: tambour-de-frein
tags: [pipeline, seo, aliases, v-level, rpc, roman-arabic]
continues_from: 2026-04-22-alias-expansions-batch-preventif.md
---

# Alias dict effectif + normalisation romain ↔ arabe pour V-Level

## TL;DR

Trois decouvertes critiques en continuant le rollout de `tambour-de-frein` :

1. **Le loader `load_alias_expansions()` et le fix apostrophe `normalize_kw`
   annonces le 2026-04-22 n'avaient jamais ete committes** : `scripts/seo/import-gads-kp.py`
   sur `main` ne chargeait pas `config/rag-alias-expansions.yaml`. Le dict existait
   mais n'etait pas consomme. Wiring effectif dans cette session.
2. **Les chiffres romains dans `auto_modele` (clio iii / megane ii / scenic iii…)
   ne matchaient pas les KW en chiffres arabes (clio 3, megane 2)** — angle mort
   V-Level massif couvrant 1482 modeles actifs.
3. Apres fix dict + RPC : **tambour-de-frein passe de 134 -> 246 pertinents (+83%)**
   et de **55 -> 96 vehicle KW tagges (+74%)**, dont 10 nouveaux `clio i..iv`.

## Trois fixes structurels

### 1. Wiring effectif du dict alias-expansions

Le dict `config/rag-alias-expansions.yaml` (73 gammes, ~228 aliases) existait
sur `main` mais `import-gads-kp.py` ne le chargeait pas. Ajoute :

```python
# Cache module-level, charge au premier appel
_ALIAS_EXPANSIONS_CACHE: Optional[dict[str, list[str]]] = None

def load_alias_expansions() -> dict[str, list[str]]:
    ...  # lit YAML, cache en memoire

# Merge dans load_gamme_rag()
expansions = load_alias_expansions().get(pg_alias, [])
for alias in expansions:
    result['aliases'].add(normalize_kw(alias))
```

### 2. Fix apostrophe `normalize_kw`

Egalement absent de `main`. `extract_core_words("Filtre d'habitacle")` rendait
`['filtre', "d'habitacle"]` au lieu de `['filtre', 'habitacle']`. Le fix supprime
apostrophes/tirets/underscores avant split :

```python
text = re.sub(r"[‘’‛'\-_]", ' ', text)
```

### 3. Normalisation romain ↔ arabe dans `extract_vehicle_keywords`

La CTE `active_modeles` de la RPC genere maintenant deux formes par modele :
- `canonical` (toujours retourne comme `matched_model`) = forme DB originale
- `match_form` = soit l'original, soit la variante arabe

Mapping romain -> arabe (ordre : du plus long au plus court pour eviter la
transformation parasite `iii -> 1ii`) :

```
\yx\y   -> 10
\yix\y  -> 9
\yviii\y -> 8
\yvii\y  -> 7
\yvi\y   -> 6
\yiv\y   -> 4
\yv\y    -> 5
\yiii\y  -> 3
\yii\y   -> 2
\yi\y    -> 1
```

La forme arabe est emise UNION dans `active_modeles` uniquement si le remplacement
produit un resultat distinct de l'original. Les modeles sans romains sont intacts.

`matched_model` reste toujours la forme canonique DB (ex. "clio iii", jamais "clio 3"),
pour preserver le contrat avec `match_keywords_batch` et les filtres frontend.

## Validation tambour-de-frein (pg_id=123)

| Metrique | Avant | Apres dict | Apres RPC roman/arabe |
|---|---|---|---|
| Pertinents (apres filtre) | 134 | **246** (+83%) | 246 |
| Aliases charges | 7 | **17** | 17 |
| `no_core_match` rejects | 125 | 13 | 13 |
| Vehicle KW tagges | 1 (bug) | 55 | **96** (+74%) |
| Dont clio i/ii/iii/iv | 0 | 0 | **10** |
| V2 champions | 1 | 2 | **3** |
| V4 catalogue fallback | 86 | 158 | **299** |

Exemples de KW nouvellement captures/tagges :
- `tambour clio 3` (vol 500) -> matched_model `clio iii`
- `tambour clio 2` (vol 500) -> matched_model `clio ii`
- `tambour clio 4` (vol 500) -> matched_model `clio iv`
- `tambour arriere clio 3` (vol 500) -> matched_model `clio iii`
- `tambour 206` (vol 500) -> matched_model `206`

## Limite connue (hors scope) : V3 variants restent a 0

`match_keywords_batch` exige `kw.energy IS NOT NULL` pour produire une correspondance
vers `type_id`. La majorite des KW "tambour clio 3" n'ont pas d'energie (pas de suffixe
`diesel`/`essence`/`hdi`/`tdi`/…) donc sont exclus de ce matching.

Ces KW contribuent donc au V-Level **indirectement** via le tagging `model+type=vehicle`
mais ne produisent pas directement de V3 variant. C'est une limite architecturale de
`match_keywords_batch` (necessite variant/puissance pour mapper vers un `type_id`),
pas un bug du patch actuel.

Follow-up possible : relaxer `match_keywords_batch` pour tolerer `energy IS NULL`
avec un fallback V3 au niveau modele (sans type_id precis). Hors scope de cette PR.

## Impact predit sur les autres gammes

1482 modeles actifs avec romain -> toutes les gammes avec KW type "piece modele X"
beneficient automatiquement (retour plus riche du `extract_vehicle_keywords` apres
re-import). Exemples impactes potentiellement :
- plaquette/disque/etrier + clio/megane/scenic/golf en chiffres
- amortisseur + clio/megane/laguna/scenic
- filtre-a-huile + clio i..v, megane i..iv, scenic i..iii
- tout ce qui concerne classique Renault/Peugeot/VW avec multiples generations

Gammes deja traitees non impactees : **uniquement** celles dont le CSV ne contenait
pas de KW `{gamme} {marque} {num}`. A verifier a la re-importation si necessaire.

## Files touches

- `config/rag-alias-expansions.yaml` (+1 alias : `tambour` pour tambour-de-frein)
- `scripts/seo/import-gads-kp.py` (+54 lignes : loader + apostrophe fix + merge dans load_gamme_rag)
- `backend/supabase/migrations/20260423_extract_vehicle_keywords_roman_arabic.sql` (nouveau)
- Migration DB appliquee via MCP Supabase (CREATE OR REPLACE FUNCTION)

## Rollback

```bash
# Revert script + yaml
git revert <commit-sha>

# Revert RPC : re-deployer l'ancienne version (sans la CTE arabe)
# Source ancienne dans git history du fichier .sql avant ce PR (ou
# restaurer la version `active_modeles` single-source du commit precedent)
```

## Git

- Branche : `seo/alias-dict-normalize-roman-arabic-20260423`
- Base : `main` (a25de23e apres fast-forward)
- Fork de `main` pour respecter la discipline de branche dediee
  (cf. `feedback_branch_scope_discipline.md`)

---

_Generated 2026-04-23. Continues session alias-expansions-batch-preventif (2026-04-22)._
