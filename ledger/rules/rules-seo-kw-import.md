# Rules - SEO Keyword Import & Alias Enrichment

> **Source de verite** - Regles de gouvernance import Google Ads KP au 2026-04-22
> **Version**: 1.0.0 | **Status**: CANON
> **Taxonomie**: R-SEO-KW = pipeline import keywords Google Ads KP vers `__seo_keywords`
> **Pipeline cible**: `scripts/seo/import-gads-kp.py` (skills-first, zero-LLM)

---

## Contexte

Le pipeline `import-gads-kp.py` lit les exports CSV Google Ads KP et filtre les keywords
pertinents pour une gamme via trois signaux :

1. **Core words** extraits de `pg_name` (stop-words retires, len >= 3)
2. **Aliases RAG** du fichier `gammes/{pg_alias}.md` (title + variants)
3. **Aliases centraux** de `config/rag-alias-expansions.yaml`

Un keyword est accepte si il contient un alias OU tous les core words (et pas de
terme `must_not_contain`). Sinon il est rejete avec reason = `no_core_match`,
`exclude:{term}`, ou `confusion:{term}`.

**Probleme observe** : le filtre core-words echoue silencieusement sur les variations
morphologiques (singulier/pluriel, synonymes electriques, suffixes francais). Sur la
gamme pg_id=806 (Interrupteur des feux de freins), 18/188 keywords ont ete rejetes au
premier import pour `no_core_match`, dont 16 etaient des vrais positifs, representant
4 500 vol/mois (27% du volume total). Sans la regle ci-dessous, le rejet serait passe
silencieusement.

---

## R-SEO-KW-01: Review obligatoire des rejets > 5% volume

**Regle**: Si la somme des volumes des keywords rejetes par le filtre RAG >= 5% du volume
total du CSV, l'import DOIT etre reviewe par un humain AVANT le commit en `__seo_keywords`.

**Pourquoi ?** Les rejets silencieux cumulent une dette SEO invisible : chaque 500 vol/mois
perdu est un couloir transactionnel absent du corpus R1/R3/R4/R6 pour toute la vie du site.

**Comment appliquer ?**

1. Run dry-run : `python3 import-gads-kp.py <csv> --pg-id <id> --dry-run --verbose`
2. Verifier la ligne `Rejets: {...}` dans la sortie
3. Si `no_core_match > seuil_5_pct` :
   - Sortir la liste des rejets avec volume via `--suggest-aliases` (a venir, voir R-SEO-KW-05)
   - Classer chaque rejet dans l'arbre de decision R-SEO-KW-02 ci-dessous
4. Iterer `dry-run -> fix -> dry-run` jusqu'a rejets acceptables (< 5% vol)
5. Puis `import live` sans flag `--dry-run`

**Evidence**: cas pg_id=806 (2026-04-22) : 170 KW / 12 100 vol -> 186 KW / 16 500 vol apres
3 iterations YAML (+9.4% KW, +36% vol).

---

## R-SEO-KW-02: Arbre de decision sur les rejets

Pour chaque rejet, un des 3 verdicts suivants :

| Type de rejet | Exemple | Action |
|---|---|---|
| **Variation morphologique** | `feu` vs `feux`, `frein` vs `freins`, `capteur` vs `contacteur` vs `commutateur` vs `interrupteur` pour les pieces electriques | Patch `normalize_kw` ou `check_relevance` dans `import-gads-kp.py` (affecte TOUTES les gammes) |
| **Alias SEO commercial scope gamme** | `cartouche filtrante` pour `filtre-a-huile`, `contacteur feux stop` pour `interrupteur-des-feux-de-freins` | Ajout dans `config/rag-alias-expansions.yaml` sous le bloc de la gamme concernee |
| **Hors-scope reel** | Prefixe modele spurieu (`contacteur clio 3 feux stop`), formulation ambigue tres bas volume | Ne rien faire, documenter dans le summary JSON |

**Pourquoi cet arbre ?** Les aliases YAML sont du travail manuel qui s'accumule au fil des
imports. Les patches du script sont un cout fixe qui sert toutes les gammes. Un rejet qui
se retrouve sur 10+ gammes est un signal qu'il faut patcher le script, pas le YAML.

---

## R-SEO-KW-03: Batch YAML par session

**Regle**: Les modifications de `config/rag-alias-expansions.yaml` suite a des reviews de
rejets doivent etre regroupees en UNE PR par session de batch (par dossier
`.claude/prompts/R*_{ROLE}/`). Pas une PR par gamme.

**Pourquoi ?** 20 gammes importees = 20 micro-PRs = bruit dans la review queue. Une PR
batch par session = 1 changelog lisible par gamme, review efficiente, lineage clair.

**Convention de nommage branche**: `fix/seo-kw-aliases-{role}-{YYYYMMDD}`
Exemple: `fix/seo-kw-aliases-r1-router-20260422`.

**Convention de commit**: enumerer les gammes touchees dans le body, pas le title.
```
fix(seo): alias expansions for R1 router batch (13 gammes)

- interrupteur-des-feux-de-freins: +13 aliases (rejets 4500 vol/mois)
- filtre-a-huile: +5 aliases (rejets 800 vol/mois)
- ...
```

---

## R-SEO-KW-04: Patches script dans leur propre PR

**Regle**: Toute modification de `normalize_kw`, `check_relevance`, ou de la logique de
filtrage dans `import-gads-kp.py` doit etre livree dans une PR dediee, SEPAREE des
modifications YAML, avec :

1. Corpus de test (au moins 5 gammes deja importees avec leur CSV original)
2. Dry-run before/after pour chaque gamme : `170 -> 186 KW`, regressions mises en evidence
3. Validation manuelle que les rejets nouveaux ne contiennent pas de faux positifs

**Pourquoi ?** Un patch morphologique mal cadre peut faire passer des KW d'une gamme dans
une autre (ex: si on retire le `s` final, `filtres` -> `filtre` risquerait de matcher
des gammes `filtre` strictes). Risque de contamination cross-gamme.

---

## R-SEO-KW-05: `--suggest-aliases` en pre-requis

**Regle**: Toute review de rejets selon R-SEO-KW-01 doit utiliser le flag
`--suggest-aliases` qui affiche un bloc YAML pret-a-coller trie par
volume decroissant. Pas de copie manuelle rejet par rejet.

**Statut**: flag a implementer dans le pipeline (PR monorepo dediee, voir R-SEO-KW-04).

**Specification** :
```bash
python3 import-gads-kp.py <csv> --pg-id <id> --dry-run --suggest-aliases [--threshold-vol 50]
```
Sortie attendue (stdout, YAML valide, copiable tel quel) :
```yaml
interrupteur-des-feux-de-freins:
  # suggested from 2026-04-22T17:09:45Z import (18 rejets, vol 4500)
  - contacteur de pedale de frein  # vol=500
  - interrupteur feux stop         # vol=500
  - ...
```

---

## Cross-references

- Pipeline: `scripts/seo/import-gads-kp.py` (monorepo `ak125/nestjs-remix-monorepo`)
- Aliases centraux: `config/rag-alias-expansions.yaml` (monorepo)
- RAG gammes: `/opt/automecanik/rag/knowledge/gammes/{pg_alias}.md` (DEV VPS runtime)
- V-Level classification: [[rules-seo-vlevel]] (aval : les KW importes seront classifies)
- PageRole validation: [[rules-seo-pagerole]] (aval : le contenu genere par /content-gen)
- Deployment : [[rules-deployment-workflow]] (D1-D6)

---

_Derniere mise a jour : 2026-04-22_
_Creee suite au batch R1_ROUTER 2026-04-22 (voir ledger/audit-trail)._
