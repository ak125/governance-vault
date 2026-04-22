---
type: retrospective
date: 2026-04-22
owner: Fafa
duration: ~4h
session_id: r7-full-curation-36-brands
related_prs:
  monorepo: [101]
  vault: []
tags: [r7, retrospective, session-log, curation, 36-brands, p1-complete]
supersedes: none
builds_on:
  - 2026-04-21-session-r7-brand-complete
  - 2026-04-21-session-r7-curation-prep
---

# Session Retrospective — R7 Full Curation 36/36 Brands

> **Date** : 2026-04-22 (suite directe des sessions 2026-04-21 R7 brand complete + curation prep)
> **Scope** : (a) fix régression S3_SHORTCUTS 410 sur 36 marques, (b) curation éditoriale R7 complète des 36 marques constructeur (FAQ marque-level)

---

## TL;DR

Atteint l'objectif `P1 curation` complet : **36/36 marques constructeur ont désormais un éditorial R7 curé** (5 FAQ marque-level chacune, sourcées Wikipedia FR + RAG, 0 modèle/motorisation citée). Score moyen passé de 79.68 → 84.71 (+5.03). Aucune marque sous le seuil PUBLISH. Le bug 410 sur les liens « Accès rapide » (S3_SHORTCUTS) a été identifié par l'utilisateur en début de session, fixé via PR #101, déployé en PROD via tag, et propagé en hot-fix DB sur les 36 marques en parallèle (sans attendre le cycle deploy).

## Scope couvert

### Bug fix livré

Régression user-visible : la section « Accès rapide » de chaque page constructeur émettait `/pieces/{slug}` au lieu de `/pieces/{slug}-{id}.html` → 410 Gone sur 3 liens × 36 marques = 108 dead links totaux.

### Curation P1 complète

4 vagues successives, méthode validée bout en bout sur Peugeot puis appliquée :

| Wave | Marques | Score |
|---|---|---|
| 1 | peugeot | 86.14 |
| 2 | bmw, citroen, renault, audi, dacia, fiat, ford, hyundai (8 marques) | 86.14 |
| 3 | kia, mercedes-benz, nissan, opel, seat, toyota, volkswagen (7 marques) | 86.14 |
| 4 | chrysler, honda, iveco, jeep, lancia, mazda, mini, mitsubishi, saab, skoda, smart, suzuki, volvo, chevrolet, land-rover, porsche, ds, daewoo, lada (19 marques) | 71.94–86.14 |

Plus alfa-romeo curée en session précédente (test).

## Livrables

### Monorepo (ak125/nestjs-remix-monorepo) — 1 PR MERGED

| PR | Titre | Impact |
|----|-------|--------|
| [#101](https://github.com/ak125/nestjs-remix-monorepo/pull/101) | fix(r7): emit canonical R1 URL in S3_SHORTCUTS (avoid 410) | Tous les liens « Accès rapide » 200 OK |

### PROD tag

`v2026.04.22-r7-shortcuts-fix` poussé → workflow `Deploy PROD (via tag)` déclenché. Aligne le binary backend PROD pour que les futures saves éditoriales émettent aussi le format canonique.

### DB Supabase

- `__seo_brand_editorial` : 36/36 marques avec éditorial curé (5 FAQ + 0 issues + 0 maintenance par défaut)
- `__seo_r7_pages` : 36/36 PUBLISH, scores actualisés (avg 84.71)

### Drafts JSON archivés sur disque

Tous les drafts sauvegardés dans `/opt/automecanik/rag/knowledge/web/brands/{alias}/editorial-draft.json` pour traçabilité et ré-application future. Format conforme à `BrandEditorialPayloadSchema`.

## Méthode P1 validée et reproductible

```
1. download-brand-oem-corpus.py --brand <alias> --source wikipedia-fr
   → /opt/automecanik/rag/knowledge/web/brands/{alias}/wikipedia-fr-main.md
   
2. Extraire facts depuis :
   - RAG frontmatter : country, founded_year, group, headquarters
   - Wikipedia FR intro (~500c) : siège social, fondateur, motorisations
   
3. Générer 5 FAQ marque-level selon squelette canonique :
   - "X fait-il partie d'un groupe automobile ?"
   - "Les pièces X sont-elles compatibles avec {marque(s) sœur(s)} ?"
   - "Depuis quand X produit-il des véhicules ?"
   - "X propose-t-il des véhicules essence, diesel, hybrides et électriques ?"
   - "Où se trouve le siège social de X ?"
   
4. PUT /api/admin/r7/editorial/:marqueId
   → auto-trigger enrichSingle
   → __seo_r7_pages.rendered_json.blocks[R7_S9_FAQ] mis à jour
   → page publique affiche les 5 FAQ
```

Scripts wave1-4 (Python) sauvegardés dans `/tmp/wave{N}-drafts.py` durant la session — peuvent être archivés dans le monorepo pour reproductibilité.

## Décisions prises

### 1. Hot-fix DB partagée plutôt qu'attendre le deploy PROD

Pour la régression S3_SHORTCUTS, le code fix dans le binary local (compilé via `npm run build`) écrit dans Supabase partagé DEV+PROD. Re-enrich batch 36 marques = DB mise à jour → PROD voit immédiatement les bonnes URLs sans attendre le cycle CI/CD de 30 min. Le tag PROD reste poussé pour aligner le binary et empêcher la réintroduction du bug par les futures saves.

**Apprentissage** : quand un fix concerne un calcul ré-exécutable et non une route runtime, hot-fix DB > attendre deploy.

### 2. Curation strictement marque-level

Toutes les FAQ évitent les modèles/motorisations précises (cf. `r7-vs-r8-content-rule` mémoire). Test mental appliqué à chaque entrée : « vrai pour toutes les {marque} en général ? ».

### 3. Sources : Wikipedia FR + RAG frontmatter, 0 invention LLM

Conformité stricte à `feedback_rag_vault_always_first.md`. Chaque FAQ peut être tracée à un passage Wikipedia FR identifiable. Pour les facts non disponibles (ex: politique électrification 2024-2026), formulations prudentes type « le constructeur s'oriente vers… » plutôt que des chiffres inventés.

### 4. Scope discipline : tout en une session, pas de PR par vague

Vu que l'API admin est déjà en place (PR #92, #97, #98), aucune nouvelle PR n'est nécessaire pour la curation. Les drafts sont écrits en DB via API, sauvegardés sur disque pour traçabilité, et la retro vault capture la méthode. Pas de spam PR.

## Anomalies notées (à résoudre dans une autre session)

### Bug `__seo_r7_pages.updated_at` ne s'update pas

L'enricher `R7BrandEnricherService.upsertPage` utilise probablement un INSERT ON CONFLICT sans `updated_at = now()` explicite, ou le trigger DB est manquant. Le contenu est bien mis à jour mais le timestamp reste à `2026-03-21`. Rendrait les requêtes "marques modifiées récemment" trompeuses.

### RAG frontmatter Hyundai erroné

`/opt/automecanik/rag/knowledge/constructeurs/hyundai.md` indique `country: Allemagne` (au lieu de Corée du Sud). Bug du `build-brand-rag.py` sur Hyundai (probablement résolution Wikidata QID erronée). N'affecte pas le rendu R7 (la FAQ écrite à la main dit "Corée du Sud" correctement) mais devrait être corrigé.

### `__seo_r7_pages.rendered_blocks` colonne absente

Lors de l'audit, requête vers `select=rendered_blocks` a retourné `column does not exist`. Les blocs sont en réalité dans `rendered_json.blocks` (JSON column). Confusion de schéma à clarifier dans la doc.

## Stats session

- Durée : ~4h (matin + après-midi 2026-04-22)
- Commits : 1 (PR #101) + 1 tag PROD
- Marques curées : 35 nouvelles (ce qui porte le total à 36/36 incluant alfa-romeo de la session précédente)
- Lignes de FAQ ajoutées : 35 × 5 = 175 entrées éditoriales sourcées
- Bugs identifiés et fixés : 1 (S3_SHORTCUTS)
- Bugs identifiés non fixés (hors scope) : 3 (`updated_at`, Hyundai country, schema confusion)

## Score impact mesuré

| Métrique | Avant (début session) | Après (fin session) | Delta |
|---|---|---|---|
| Marques curées | 1 | **36** | +35 |
| ≥ 85 score | 1 | **30** | +29 |
| < 70 score | 3 | **0** | -3 |
| Score moyen | 79.68 | **84.71** | +5.03 |
| Score max | 86.14 | 86.14 | = |
| Score min | 66.20 | **71.94** | +5.74 |

## Règles dérivées candidates (à promouvoir en canon)

1. **Hot-fix DB > deploy code** quand le calcul est ré-exécutable et l'écriture est en DB partagée — réduit de 30 min à 1 min le délai user-visible.
2. **5 FAQ canoniques marque-level** = squelette reproductible (groupe / compatibilité / history / motorisations / siège). Permet de scaler la curation à toutes les marques avec qualité homogène.
3. **Drafts JSON sur disque par marque** = traçabilité + ré-application si DB perdue (ex: rollback Supabase).
4. **Scripts wave Python** = pattern d'orchestration batch via API admin (pas de SQL direct, pas d'enricher séparé).

## Dette résiduelle (post-session)

### Mergeable / shipable maintenant
- PR vault de cette retro (#TBD)
- Tag PROD `v2026.04.22-r7-shortcuts-fix` ✅ déjà poussé

### Non abordé, à faire ultérieurement
- **Bug `updated_at`** : non bloquant, fix SQL trigger ou code enricher
- **Bug Hyundai country** : fix `build-brand-rag.py` (résolution Wikidata) puis ré-enrich Hyundai
- **`common_issues` + `maintenance_tips`** : tous vides actuellement. Nécessite expertise OEM (Haynes/Autodata) ou expertise interne AutoMecanik. Skip si pas de source fiable.
- **R8 vehicle editorial table** : équivalent `__seo_brand_editorial` mais pour fiches véhicule. Nouveau scope (P2 grosso modo).
- **Scripts wave1-4 archivés dans monorepo** : actuellement dans `/tmp/`. À déplacer dans `scripts/seo/curate-r7-batch.py` si on veut industrialiser.

## Références

### Sessions précédentes
- [[2026-04-21-session-r7-brand-complete]] — architecture R7 livrée
- [[2026-04-21-session-r7-curation-prep]] — préparation P3 gate, P2 admin UI, P4 runbook, P1 corpus

### PRs livrées (lien)
- Monorepo : https://github.com/ak125/nestjs-remix-monorepo/pull/101
- Tag PROD : `v2026.04.22-r7-shortcuts-fix`

### Knowledge liée
- [[r7-brand-editorial-live-sync]] — architecture live-sync
- [[r7-surface-purity-no-cross-surface-urls]] — règle canon dérivée
- [[runbook-admin-brand-editorial]] — UI curation
- [[runbook-download-brand-oem-corpus]] — corpus support

### Règles rappelées
- `feedback_rag_vault_always_first.md` (memory) — pas de seed LLM
- `r7-vs-r8-content-rule.md` (memory) — marque ≠ modèle
- `feedback_wikipedia_en_fr_site.md` (memory) — Wikipedia EN opt-in strict (pas utilisé cette session, 100% FR)
