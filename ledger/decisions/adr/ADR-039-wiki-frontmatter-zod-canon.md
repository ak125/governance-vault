---
id: ADR-039
title: "Wiki Proposal Frontmatter Zod Canon — TS mirror du JSON Schema canon, validateur CLI mono-repo (PR-C ADR-033)"
status: accepted
date: 2026-04-30
decision_date: 2026-05-01
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "Q1", "Q2", "AP-10", "AP-11"]
related_incidents: []
related_adr: ["ADR-031", "ADR-032", "ADR-033", "ADR-037", "ADR-038"]
---

# ADR-039: Wiki Proposal Frontmatter Zod Canon

## Contexte

ADR-031 fixe l'architecture 4-layer (raw / wiki / exports / consumers).
ADR-033 (vault PR #108) introduit `diagnostic_relations[]` top-level
(frontmatter v2.0.0). Le canon JSON Schema vit dans le wiki repo :
`automecanik-wiki/_meta/schema/frontmatter.schema.json` (343 lignes,
Draft 2020-12, supporte v0.legacy / v1.0.0 / v2.0.0 cohabitants).

### Validateurs existants

| Validateur | Localisation | Rôle |
|---|---|---|
| `validate-frontmatter.py` | wiki repo `_scripts/` | Python, JSON Schema canon, CLI |
| `validate-frontmatter.mjs` | wiki repo `_scripts/` | JS, JSON Schema canon, CLI |
| `quality-gates.py` | wiki repo `_scripts/` | Python, 9 quality gates ADR-033/032 |

**Gap identifié** : aucune validation TS côté monorepo. Au moment où
Phase 3 ADR-033 ouvrira les consommateurs (DB ingest `WikiProposalSyncService`,
RAG sync, SEO export, blog hub), le backend NestJS aura besoin de valider
les proposals à l'ingest, en runtime. Sans canon TS, le risque est :
- Soit dupliquer la logique (réinventer une regex partielle, anti-pattern AP-11)
- Soit dépendre d'un sub-process Python (couplage fragile, anti-pattern AP-10)
- Soit accepter des proposals invalides en runtime (bricolage)

### Audit empirique (règle CLAUDE.md « vérifier l'existant AVANT d'inventer »)

| Élément | État |
|---|---|
| `gray-matter@^4.0.3` + `js-yaml@^4.1.1` | **Déjà installés** (utilisés par ADR-037, ADR-038) |
| Pattern `*.schema.ts` Zod dans `backend/src/config/` | **5 fichiers existants** : `agent-frontmatter.schema.ts`, `marketing-agent-frontmatter.schema.ts`, `brand-rag-frontmatter.schema.ts`, `brand-role-map.schema.ts`, `duplicate-gate.schema.ts` |
| `safeParseXxxFrontmatter` helper convention | **Établi** par ADR-037 et ADR-038 |
| CLI Zod-validator pattern (`scripts/<domain>/...`) | **Établi** par `scripts/seo/dump-agent-matrix.ts` (#222) et `scripts/seo/inject-agent-role.ts` (#239) |

**Conclusion** : créer `wiki-proposal-frontmatter.schema.ts` n'invente rien,
c'est l'extension du pattern majoritaire backend Zod aux wiki proposals.

## Décision

### 1. Schema Zod TS canon

Nouveau fichier `backend/src/config/wiki-proposal-frontmatter.schema.ts`,
**miroir TS** du JSON Schema canon `automecanik-wiki/_meta/schema/frontmatter.schema.json` v1.0.0/v2.0.0.

**Source de vérité** : le JSON Schema (wiki repo) reste autoritaire. La Zod
TS est une dérivation pour usage runtime monorepo. Si divergence détectée,
la JSON Schema tranche, la Zod doit être ré-alignée.

**Couverture** :
- 3 versions cohabitantes : `0.legacy`, `1.0.0`, `2.0.0`
- 5 entity_types canon : `gamme`, `vehicle`, `constructeur`, `support`, `diagnostic`
- Discriminated union sur `source_refs[].kind` (4 variantes : `raw`, `external_url`, `manual`, `recycled`)
- `diagnostic_relations[]` top-level (ADR-033 §D1) : 3 valeurs `relation_to_part` enum
- `entity_data.maintenance{}` (ADR-032) : passthrough optionnel
- 2 conditional rules (`allOf` JSON Schema → `superRefine` Zod) :
  1. `truth_level ∈ {L1,L2,L3}` → `source_refs.length >= 1`
  2. `exportable.{rag|seo|support} = true` → `review_status = "approved"` ET `no_disputed_claims = true` ET `reviewed_by` ET `reviewed_at`
- 1 cross-validation supplémentaire (TS uniquement, pour fail-fast plus précis) : `id === "<entity_type>:<slug>"`

### 2. CLI validator monorepo

`scripts/wiki/validate-proposal.ts` — CLI tsx callable :

```bash
npx tsx scripts/wiki/validate-proposal.ts <file>...
npx tsx scripts/wiki/validate-proposal.ts --all <wiki-repo-root>
```

Exit codes : `0` (all valid), `1` (au moins 1 invalide), `2` (script error).
Skip `_*.md` files (canon meta : `_index.md`, `_README.md`, etc.).

### 3. Tests Jest

`backend/src/config/wiki-proposal-frontmatter.schema.test.ts` — 30 cas couvrant :
- Inputs valides v0.legacy / v1.0.0 / v2.0.0 (gamme + 4 autres entity_types)
- Rejets : schema_version, id mismatch, entity_type, slug pattern (start/end hyphen)
- Conditional `truth_level` + `source_refs` rule (allOf §1)
- Conditional `exportable` + `review_status` rule (allOf §2)
- Discriminated union `source_refs[].kind` (4 variantes)
- `diagnostic_relations[]` (`part_role` minLength, `relation_to_part` enum, `sources` minItems, defaults)
- Strict mode (no additional properties)
- Helper functions `parseWikiProposalFrontmatter` + `safeParseWikiProposalFrontmatter`

### 4. Smoke test sur le wiki repo réel

Au moment de cet ADR (2026-04-30) :
- `proposals/` : 12/12 valides (excluant `_index.md`)
- `wiki/diagnostic/` : 3/3 valides
- `wiki/gammes/`, `wiki/vehicles/`, `wiki/constructeurs/`, `wiki/supports/` : à vérifier au moment de PR-C merge

## Options Considérées

### Option A — Zod TS dans le monorepo, JSON Schema reste autoritaire (CHOISIE)

| Pour | Contre |
|---|---|
| Pattern établi (5 fichiers `*.schema.ts` existants) | 2 sources : JSON Schema (wiki) + Zod TS (monorepo) — risque drift |
| Backend NestJS peut valider runtime sans subprocess | Drift mitigé par tests + smoke contre wiki réel |
| CLI réutilisable depuis CI monorepo (tsx) | — |
| Zéro nouvelle dépendance | — |

### Option B — Sous-process Python depuis NestJS (REJETÉE)

Le backend appellerait `python3 _scripts/validate-frontmatter.py` via `child_process.exec`.

| Pour | Contre |
|---|---|
| 1 source de vérité (Python uniquement) | Couplage fragile (Python runtime requis sur PROD) |
| | Latence par appel sub-process |
| | Anti-pattern AP-10 (couplage architectural fragile) |

### Option C — Génération automatique Zod depuis JSON Schema (REJETÉE pour MVP)

Outil type `json-schema-to-zod` qui génère le `.ts` au build.

| Pour | Contre |
|---|---|
| 1 source de vérité, génération auto | Dépendance build supplémentaire |
| | Les `superRefine` (allOf conditional) ne sont pas trivialement générables |
| | Couvre 80% mais nécessite override manuel pour les 20% restants |
| | Différé : peut être adopté plus tard si l'effort de maintenance manuelle justifie l'outil |

Option C reste **évolutive** post-ADR-039 — si la maintenance manuelle s'avère
trop lourde (>2 syncs annuels), passer à C via amendement.

## Conséquences

### Positives

- **Cohérence cross-services** : SEO (ADR-037), marketing (ADR-038) et wiki
  (ADR-039) utilisent le même pattern Zod backend.
- **Backend NestJS prêt pour Phase 3 ADR-033** : `WikiProposalSyncService`
  pourra valider runtime sans dépendance externe.
- **CI monorepo** peut désormais bloquer un PR qui inclut/référence un wiki
  proposal mal frontmatté (workflow futur, hors scope ADR-039).
- **Tests Jest** : 30 cas qui couvrent les invariants canon + edge cases.

### Négatives / coûts

- **Maintenance manuelle de 2 sources** : si le JSON Schema (wiki repo) bouge,
  la Zod TS doit être mise à jour. Mitigé par :
  - Tests Jest qui catch le drift au CI
  - Smoke test régulier (CLI sur wiki repo réel)
  - Convention : tout PR sur le JSON Schema canon doit accompagner une PR
    dans le monorepo (référence manuelle, pas de mécanisme auto)
- **Validation conditionnelle** (`superRefine`) un peu plus verbeuse que le
  JSON Schema `allOf` — accepté pour expressivité TS.

### Anti-patterns écartés

1. Pas de **scratch validator** maison qui réinvente une logique partielle.
2. Pas de **sub-process Python** depuis NestJS (couplage fragile).
3. Pas de **god-schema** unifiant SEO + marketing + wiki — chaque domaine
   a son fichier Zod (cohérent ADR-038).
4. Pas de **`unknown` partout** — tous les sub-types sont typés strictement
   sauf `entity_data` (passthrough volontaire — délégué au sub-schema par
   entity_type côté wiki repo).
5. Pas de **réécriture du Python `quality-gates.py`** — c'est un validateur
   séparé qui couvre 9 gates additionnels (ADR-033 §D2-D4) et reste
   autoritaire côté wiki repo.

## Plan de migration

### Phase 0 — Gouvernance (J+0 → J+1)

1. PR vault : ADR-039 (cette ADR) → mergée et `accepted`.
2. Pas de canon-publish (ADR purement architecture monorepo, comme ADR-037 et ADR-038).

### Phase 1 — Implémentation backend (J+1 → J+2)

PR monorepo dédiée (`feat/adr-033-pr-c-wiki-zod-validator`) :

1. **Schema Zod** : `backend/src/config/wiki-proposal-frontmatter.schema.ts`
2. **CLI validator** : `scripts/wiki/validate-proposal.ts`
3. **Tests** : `backend/src/config/wiki-proposal-frontmatter.schema.test.ts` (30 cas)
4. **Smoke test** : exécuter le CLI sur `automecanik-wiki/proposals/` réel
   pour vérifier 0 régression
5. Pas de wire dans NestJS module à ce stade (Partie 3 différée)

### Phase 2 — CI bloquant (différé Phase 3 ADR-033)

Workflow `wiki-proposal-validation.yml` qui :
- Trigger sur PR monorepo qui touche `automecanik-wiki/**` (si submoduled) OU
- Trigger sur PR wiki repo qui appelle ce monorepo via `gh api` cross-repo
- Exécute `npx tsx scripts/wiki/validate-proposal.ts --all` sur les fichiers modifiés
- Fail si exit code ≠ 0

À discuter Phase 3 selon le mode d'intégration retenu (submodule, sync,
canon-publish-style hash check, etc.).

## Validation

### Phase 0

- [ ] PR vault ADR-039 mergée et `accepted`

### Phase 1

- [ ] PR monorepo mergée sur `main` avec CI verte
- [ ] 30 tests `wiki-proposal-frontmatter.schema.test.ts` passent
- [ ] Smoke `npx tsx scripts/wiki/validate-proposal.ts --all /opt/automecanik/automecanik-wiki/proposals` → 12/12 valid
- [ ] Smoke `... --all /opt/automecanik/automecanik-wiki/wiki` → 100% valid (ou liste explicite des invalides documentée)
- [ ] Typecheck strict pass (`tsc --noEmit`)

### Phase 2 (post-merge ADR-039, différé)

- [ ] Workflow CI déployé
- [ ] Test négatif : un PR avec un proposal mal frontmatté → CI fail explicite

## Décisions ouvertes

1. **Mode d'intégration cross-repo** monorepo ↔ wiki repo : submodule vs
   sync explicite vs canon-publish-style hash check. À trancher Phase 3
   ADR-033.
2. **Maintenance JSON Schema → Zod** : actuellement manuel (PR jumelé
   recommandé). Si dérive empirique > 2 incidents/an, considérer Option C
   (génération auto `json-schema-to-zod`).
3. **Lint CI sur skill frontmatter** (`.claude/skills/**/SKILL.md`) :
   ADR-037/038 ont fait les agents. Skills restent à canoniser. Hors scope
   ADR-039 — ouvrir un ADR-040 si besoin.

## Évolutions futures

- **`WikiProposalSyncService` côté backend NestJS** : Phase 3 ADR-033 — service
  consommateur DB qui ingère les proposals validées, utilisera ce schema TS.
- **Plug Zod schema dans le skill** : `wiki-proposal-writer` (PR-B mergée)
  pourrait à terme appeler `safeParseWikiProposalFrontmatter` au lieu/en
  plus de `quality-gates.py` Python — mais cela nécessite tsx au runtime
  Claude Code, ce qui n'est pas trivial. Différé.

## Références

- [[ADR-031-four-layer-content-architecture]] — 4-layer raw/wiki/exports/consumers
- [[ADR-032-diagnostic-maintenance-unification]] — `entity_data.maintenance{}`
- [[ADR-033-wiki-gamme-diagnostic-relations-contract]] — `diagnostic_relations[]` v2.0.0
- [[ADR-037-agent-naming-canon]] — pattern Zod fail-fast SEO agents
- [[ADR-038-marketing-agent-naming-canon]] — pattern Zod fail-fast marketing agents
- [[rules-engineering-quality]] — Q1 (no bricolage), Q2 (grep-first)
- Canon JSON Schema : `automecanik-wiki/_meta/schema/frontmatter.schema.json`
- Validators wiki repo : `_scripts/{validate-frontmatter,quality-gates}.{py,mjs}`
- Plan rev 3 : `/home/deploy/.claude/plans/mvp-et-raw-et-wobbly-brooks.md`
- PR monorepo : `feat/adr-033-pr-c-wiki-zod-validator` (ouverte par cette ADR)

---

_Décision prise sur preuves empiriques — 5 fichiers `*.schema.ts` existants
dans `backend/src/config/`, 4 services backend utilisent déjà ce pattern.
Option B (sub-process Python) et Option C (génération auto) explicitement
rejetées pour mémoire architecturale. Option C reste évolutive si la
maintenance manuelle devient lourde (post-ADR-039)._
