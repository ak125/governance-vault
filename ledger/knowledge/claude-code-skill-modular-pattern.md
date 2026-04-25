---
type: knowledge
scope: devex/claude-code
date: 2026-04-25
owner: Fafa
pr: https://github.com/ak125/nestjs-remix-monorepo/pull/183
tags: [claude-code, skills, modular-architecture, refactoring, no-bricolage]
---

# Claude Code SKILL.md — Modular Pattern (Concern-Based References)

> **Statut** : pattern candidat (n=1, à promouvoir en ADR si n ≥ 3)
> **Origine** : refactor `seo-content-architect` skill, monorepo PR #183 (2026-04-25)
> **Scope** : skills Claude Code (`.claude/skills/<name>/SKILL.md`), pas les skills programmatiques AI-COS (cf. `01-skill-model.md`).

---

## Problème

Un `SKILL.md` Claude Code est chargé **intégralement** dans le contexte LLM à chaque invocation. Les skills volumineux (>800 lignes) gaspillent des tokens à chaque appel parce que :

- Ils chargent le détail de **toutes** les phases workflow, même celles qui ne s'appliquent pas au scénario courant
- Ils embarquent des templates curl, des tableaux d'extraction, des formats de rapport qui ne sont utiles que dans des branches conditionnelles spécifiques
- Le contenu rarement nécessaire (ex. enrichissement schema v4, mode batch multi-gammes, correction linguistique BDD/RAG) cohabite avec le workflow always-on

Cas concret : `seo-content-architect/SKILL.md` faisait **1021 lignes (~50 KB)**. À chaque invocation, ~9 000 tokens chargés alors que ~5 000 suffisaient pour le scénario nominal mono-gamme sans contenu externe.

## Pattern

**Concern-based split** : extraire les sections longues + conditionnelles dans `references/<concern>.md`, **chargées à la demande** par le LLM uniquement quand leur scénario matche.

### Architecture

```
.claude/skills/<skill-name>/
├── SKILL.md                       # logique + workflow + règles always-on
└── references/
    ├── <role>-role.md             # vocabulaire / template par rôle (existant)
    ├── <concern-1>.md             # détail conditionnel #1
    ├── <concern-2>.md             # détail conditionnel #2
    └── ...
```

### Règle d'extraction (3 critères cumulatifs)

Une section est candidate à l'extraction si **les 3 conditions** sont remplies :

1. **Longue** : ≥ 50 lignes, OU contient ≥ 1 tableau de mapping/extraction, OU embarque ≥ 1 commande shell/curl complète
2. **Conditionnelle** : déclenchée par un scénario (ex: "si le sujet est une pièce", "si docs supplémentaires", "si batch multi-gammes"), pas always-on
3. **Self-contained** : pas de cross-refs intra-skill nécessitant 2 sections distinctes pour être comprises

Une section qui ne remplit que 1 ou 2 critères reste inline dans SKILL.md.

### Pattern de pointer dans SKILL.md

Quand une section est extraite, SKILL.md garde **un stub structuré** :

```markdown
### Phase Xx — <Titre> (déclencheur condition)

**Déclencheur** : <quand cette phase s'active>
**Objectif** : <quoi obtenir, en 1-2 phrases>

**Détail canonique** : voir [`references/<concern>.md`](references/<concern>.md) — <courte énumération du contenu>.

**Règles invariantes (résumé) :**
- <règle 1 inviolable>
- <règle 2 inviolable>
- <règle 3 inviolable>
```

L'ordre est intentionnel : **déclencheur** d'abord (le LLM décide s'il doit charger la ref), **règles invariantes** restent inline (jamais bypass-ables), **détail** délégué.

### Anti-bricolage

- Le contenu extrait est **verbatim** — aucune réécriture sémantique pendant l'extraction (sépare le refactor du contenu de la modification du contenu)
- Les references ne sont pas utilisées pour cacher du contenu obsolète ou contradictoire — si une section est extraite, c'est qu'elle est **toujours valide**, juste rare
- L'extraction n'est **pas** un fork : SKILL.md garde l'autorité sur le workflow et les règles invariantes

## Première application — `seo-content-architect`

| Section extraite | Lignes (avant) | → Reference | Loaded when |
|---|---|---|---|
| Phase 0 — Triage contenu brut | ~58 | `references/triage-phase0.md` | Contenu externe fourni |
| Phase 1b — Vérification RAG | ~92 | `references/rag-verification.md` | Sujet = pièce/gamme |
| Phase 1d — Enrichissement gamme.md v4 | ~199 | `references/gamme-enrichment.md` | Docs supplémentaires + lacunes |
| Correction Linguistique (détail BDD/RAG) | ~53 | `references/lang-correction.md` | Erreur détectée à corriger |
| Mode Batch (multi-gammes) | ~59 | `references/batch-mode.md` | Traitement batch |

**Résultat** : SKILL.md 1021 → 645 lignes (-37 %), ~44 % de tokens en moins chargés à chaque invocation par défaut. Aucun contenu perdu, contenu préservé verbatim dans les references. PR : https://github.com/ak125/nestjs-remix-monorepo/pull/183.

## Critères de promotion en ADR

Ce pattern est **candidat**. Promouvoir en ADR canonique quand **les 2 conditions** sont remplies :

1. **n ≥ 3 skills** Claude Code distincts ont appliqué le pattern (échantillon suffisant pour calibrer un seuil)
2. **Le seuil de déclenchement** (lignes / tokens / nombre de sections) converge sur les 3 cas — sinon attendre

L'ADR codifierait alors :
- Seuil obligatoire (ex. "SKILL.md > N lignes ⇒ split obligatoire")
- Format de pointer normalisé (frontmatter, structure du stub)
- Hook CI éventuel (linter qui flag les SKILL.md > seuil sans references/)

Tant que n < 3, le pattern reste **descriptif** (cette knowledge note) et **non normatif**.

## Anti-patterns observés (à ne pas reproduire)

- **Split par lignes** plutôt que par concern : couper « toutes les 200 lignes » crée des references arbitraires sans cohérence sémantique. Toujours splitter par scénario / concern.
- **Sur-extraction** : extraire des règles always-on (interdictions, axiomes) dans une ref. Ces règles **doivent** rester inline pour ne jamais être manquées.
- **Pointer-only** : remplacer une section par un simple `voir references/X.md` sans déclencheur ni règles invariantes. Le LLM perd alors le critère pour décider si la ref est nécessaire.
- **Réécriture pendant l'extraction** : changer la sémantique du contenu pendant le refactor. Sépare en 2 PRs : (1) extraction verbatim, (2) modifications sémantiques si nécessaires.

## Références

- Première application : monorepo PR #183 (2026-04-25)
- Skill modèle : `.claude/skills/seo-content-architect/` (monorepo `ak125/nestjs-remix-monorepo`)
- Distinction avec skill AI-COS programmatique : voir [[01-skill-model]]
- Pattern documentaire similaire (mais sur scope différent) : [[r7-brand-route-refactoring]]
