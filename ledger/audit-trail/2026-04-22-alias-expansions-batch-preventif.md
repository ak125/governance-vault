---
type: evidence-pack
date: 2026-04-22
owner: Fafa
duration: ~1h
session_id: alias-expansions-batch-preventif
scope: SEO alias dictionary + apostrophe normalization fix
related_files:
  - config/rag-alias-expansions.yaml
  - scripts/seo/import-gads-kp.py
prototype_gammes: [filtre-a-huile, filtre-a-air, filtre-a-carburant, filtre-de-boite-auto, filtre-d-habitacle]
tags: [pipeline, seo, aliases, ssot, preventif, apostrophe-bug]
continues_from: 2026-04-22-pipeline-quality-hardening-p2.md
---

# Traitement préventif de la dette d'aliases RAG

## TL;DR

Après 4 gammes importées (filtre-a-huile → filtre-d-habitacle), pattern systémique détecté : **3 gammes sur 4 ont nécessité l'ajout d'aliases sémantiques** pour faire matcher les synonymes SEO commerciaux (gasoil/diesel, boite auto/automatique, pollen/clim). Traitement à la racine + découverte d'un bug **apostrophe dans `normalize_kw`** qui divisait le matching par 5 pour toutes les gammes en `*-d-*` ou `*-a-*`.

## Deux fixes structurels

### 1. Dictionnaire d'alias-expansions centralisé

Nouveau fichier [`config/rag-alias-expansions.yaml`](../../../../config/rag-alias-expansions.yaml) :
- **60 gammes couvertes**, **196 aliases SEO** curés par famille
- Chargé par `import-gads-kp.py` au démarrage (cache singleton)
- Fusionné avec les `variants[].aliases` du RAG (additif, idempotent)
- Zéro modification des RAG `.md` existants (SSOT séparé, plus maintenable)

Familles couvertes :
```
Filtration (5)    Freinage (9)      Distribution (6)
Allumage (3)      Suspension (5)    Direction (4)
Embrayage (3)     Démarrage (3)     Climatisation (4)
Échappement (4)   Refroidissement (4)  Injection/Admission (4)
Transmission (1)  Essuyage (1)      Éclairage (4)
```

### 2. Bug apostrophe `normalize_kw` corrigé

**Diagnostic** : `extract_core_words("Filtre d'habitacle")` retournait `['filtre', "d'habitacle"]` au lieu de `['filtre', 'habitacle']`. Donc un KW "filtre habitacle voiture" ne matchait PAS `d'habitacle` → rejet `no_core_match`.

**Impact observé** sur filtre-d-habitacle :
- Avant fix : **296 KW pertinents** sur 1663
- Après fix : **1616 KW pertinents** sur 1663 (+546%)

**Patch** : `normalize_kw` remplace désormais `[' ' ' - _ ]` par espaces avant split.

**Impact prédit** sur toutes les gammes avec apostrophe dans `pg_name` :
- `filtre-a-huile` (pg_name "Filtre à huile" → core OK déjà)
- `filtre-d-habitacle` (pg_name "Filtre d'habitacle" → ÉTAIT cassé, **fixé**)
- `rotule-d-attelage`, `soupape-d-echappement`, etc. → potentiellement impactés

## Architecture additive vs intrusive

Choix délibéré : dictionnaire externe plutôt que modification de chaque RAG `.md`.

| Approche | Pour | Contre |
|---|---|---|
| Modifier chaque RAG | SSOT unique par gamme | 232 fichiers à maintenir, régénération destructive |
| **Dictionnaire central** | 1 fichier à maintenir, additif, zéro régression | 2 SSOT (RAG + dict) |

Retenu : **dict central**. Les aliases SEO commerciaux évoluent différemment des aliases techniques RAG (fréquence des KW Google, trends saisonnières). Les séparer permet des cycles d'évolution indépendants.

## Nettoyage post-migration

Variants ajoutés manuellement lors des rollouts #2/#3/#4 retirés des RAG (redondants avec le dict central) :
- `filtre-a-carburant.md` : variant "Filtre a gasoil diesel" retiré
- `filtre-d-habitacle.md` : variant "Filtre a pollen habitacle" retiré
- `filtre-de-boite-auto.md` : variant "Filtre boite automatique" retiré

Commentaires de suppression laissés en place pour auditabilité.

## Validation end-to-end

| Gamme | Raw CSV | Pertinents avant | Pertinents après | Delta | Stage |
|---|---|---|---|---|---|
| filtre-a-huile | 1978 | 1522 | 1522 | = | FULLY_ENRICHED |
| filtre-a-air | 1225 | 849 | 849 | = | FULLY_ENRICHED |
| filtre-a-carburant | 1304 | 940 | 940 | = | FULLY_ENRICHED |
| filtre-de-boite-auto | 15 | 10 | 10 | = | FULLY_ENRICHED |
| **filtre-d-habitacle** | 1683 | **1482** | **1616** | **+134** | FULLY_ENRICHED |

Gains :
- `filtre-d-habitacle` : +134 KW grâce au fix apostrophe (variant retiré, dict central seul)
- Autres gammes : idempotentes (dict produit les mêmes aliases que les variants retirés)

## Maintenance future

Quand un nouveau CSV montre un taux de rejet `no_core_match > 50%` :
1. Inspecter les KW rejetés
2. Identifier les synonymes commerciaux récurrents
3. Ajouter la section `<pg_alias>:` dans `rag-alias-expansions.yaml`
4. Re-importer (idempotent)

Aucune modification de RAG `.md` nécessaire.

## Files touchés

- `config/rag-alias-expansions.yaml` (**nouveau**, 60 gammes / 196 aliases)
- `scripts/seo/import-gads-kp.py` (patch : `load_alias_expansions()` + fix `normalize_kw` apostrophes)
- `rag/knowledge/gammes/filtre-a-carburant.md` (variant retiré)
- `rag/knowledge/gammes/filtre-d-habitacle.md` (variant retiré)
- `rag/knowledge/gammes/filtre-de-boite-auto.md` (variant retiré)

## Rollback

```bash
git revert <commit-sha>
# Ou restaurer les variants des 3 RAG .md + retirer le dict + unpatching script
```

---

_Generated 2026-04-22. Continues session pipeline-quality-hardening-P2._
