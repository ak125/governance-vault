---
type: evidence-pack
date: 2026-04-22
owner: Fafa
duration: ~1h
session_id: r6-antimistakes-cross-contamination-fix
scope: R6 BuyingGuide anti_mistakes generation — 4 sources contamination
related_files:
  - backend/src/modules/admin/services/buying-guide/buying-guide-rag-fetcher.service.ts
  - backend/src/modules/admin/services/buying-guide/buying-guide-section-extractor.service.ts
tags: [r6, anti-mistakes, contamination, fix, pipeline-quality]
continues_from: 2026-04-22-alias-expansions-batch-preventif.md
---

# R6 anti_mistakes cross-contamination fix

## TL;DR

Bug systémique observé sur 5 gammes freinage non-disques (machoires, cylindre-de-roue, etrier, flexible, tambour) + 2 gammes électriques (interrupteur-feux, temoin-d-usure) : `sgpg_anti_mistakes` peuplé avec du contenu de diagnostic partagé ("Symptôme** : Vibration volant...", "Pièces** : Kit roulement de roue...") au lieu d'anti-mistakes spécifiques à la gamme.

4 sources de contamination identifiées et fixées. Post-fix : `count=0` pour toutes les gammes non-spécifiques — préférable à contamination silencieuse.

## 4 sources de contamination

### Source 1 — `findGuideDocId` fuzzy match trop permissif

Le fuzzy matching chargeait le guide `choisir-disques-frein.md` pour toutes les gammes freinage dès qu'un mot en commun existait :

```
machoires-de-frein           → choisir-disques-frein  (match "frein")
cylindre-de-roue             → None (no match)  
interrupteur-des-feux-de-freins → choisir-disques-frein  (match "frein")
etrier-de-frein              → choisir-disques-frein  (match "frein")
flexible-de-frein            → choisir-disques-frein  (match "frein")
```

Le contenu du guide disques contaminait anti_mistakes de toutes ces gammes.

**Fix** : blacklist de mots génériques (`frein`, `freinage`, `moteur`, `auto`, `voiture`, `vitesse`) exclus du calcul de score + seuil adaptatif :
- Si slug a 1 mot distinctif → 1 match suffit (plaquette → choisir-plaquettes)
- Si slug a ≥2 mots distinctifs → 2 matches requis (filtre-a-carburant évite choisir-filtre-air)

### Source 2 — Extraction regex "Erreurs à éviter" sur allContent

Le fetcher extrayait la section "Erreurs à éviter" du `gammeContent + guideContent` concaténé. Quand le RAG gamme avait cette section polluée par un bloc diagnostic partagé, les items remontaient en anti_mistakes.

**Fix** : extraction regex retirée. Source unique = `v4Data.antiMistakes` (YAML structuré `selection.anti_mistakes`).

### Source 3 — Bloc "Solutions" markdown aspiré dans anti_mistakes

Même symptôme que source 2, mais sur la section "Solutions" du RAG. Des items comme `Pièces** : Kit roulement de roue`, `Pièces** : Disques de frein` (venant d'un bloc diagnostic partagé) étaient ajoutés aux anti_mistakes.

**Fix** : extraction de la section "Solutions" retirée.

### Source 4 — `sanitizeStringArray` trop tolérante

La sanitization filtrait seulement quelques patterns parasites (FAQ_TOO_SMALL, `^❌ "..."$`). Les items `**Symptôme** : ...`, `**Vérification** : ...`, `**Solution** : ...`, `**Coût** : ...`, `**Urgence** : ...` passaient comme anti-mistakes valides alors qu'ils proviennent de blocs diagnostic.

**Fix** : ajout de 2 regex dans `PARASITIC_PATTERNS` pour rejeter ces items structurés de diagnostic.

## Code modifié

- [`buying-guide-rag-fetcher.service.ts`](../../../../backend/src/modules/admin/services/buying-guide/buying-guide-rag-fetcher.service.ts)
  - `findGuideDocId` : GENERIC_WORDS + seuil adaptatif
  - Extraction anti_mistakes : seul `v4Data.antiMistakes` reste, fallbacks regex retirés
- [`buying-guide-section-extractor.service.ts`](../../../../backend/src/modules/admin/services/buying-guide/buying-guide-section-extractor.service.ts)
  - `PARASITIC_PATTERNS` étendu pour rejeter items de diagnostic

## Validation post-fix (5 gammes tests)

| Gamme | Avant fix | Après fix |
|---|---|---|
| machoires-de-frein | 4 items "Pièces**" contaminés | **0** (propre) |
| cylindre-de-roue | 4 items "Pièces**" contaminés | **0** (propre) |
| etrier-de-frein | 4 items "Pièces**" contaminés | **0** (propre) |
| interrupteur-des-feux-de-freins | 4 items "Pièces**" contaminés | **0** (propre) |
| temoin-d-usure | 4 items "Pièces**" contaminés | **0** (propre) |

## Conséquence sur le workflow

Pour les gammes dont `selection.anti_mistakes` du RAG contient uniquement des mots interdits commerciaux (ex: `❌ "homologué CT"`), la sanitize les retire → `sgpg_anti_mistakes = []`.

Dans ce cas, Phase 9 QA détecte le gap (q5=1) et la fix Q5 manuelle (UPDATE avec 5 anti-mistakes spécifiques) reste nécessaire — comme déjà fait sur filtre-a-air, filtre-a-carburant, etc.

**À terme (P3)** : nettoyer `selection.anti_mistakes` dans les RAG concernés pour contenir de vraies erreurs à éviter (pas des mots interdits de publicité).

## Pipeline global validé

9 gammes PASS 9/9 phases depuis l'installation de Phase 9 QA :

1. filtre-a-huile / filtre-a-air / filtre-a-carburant / filtre-d-habitacle / filtre-de-boite-auto
2. etrier-de-frein
3. temoin-d-usure
4. machoires-de-frein
5. cylindre-de-roue
6. interrupteur-des-feux-de-freins

Prêt pour CSV #10 avec pipeline durci.

---

_Generated 2026-04-22. Continues session pipeline-quality-hardening._
