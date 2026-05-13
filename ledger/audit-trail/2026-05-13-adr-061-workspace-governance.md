---
date: 2026-05-13
type: audit-trail
related: [ADR-061, ADR-015, ADR-031, ADR-033, ADR-036, ADR-058, ADR-060, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-13 — ADR-061 Workspace Governance (création accepted atomique)

## What

Création de **ADR-061 « Workspace Governance — frontière, lifecycle, ownership, anti-mini-monorepo »** directement en `status: accepted` (decision_date 2026-05-13, signée @fafa, pattern atomique inauguré par ADR-059 et ADR-060 le même jour).

L'ADR codifie **7 invariants** opposables à tout futur PR/agent touchant les workspaces :

1. **Typologie canon** : DEV root (`app/`) + domain workspaces (`app/workspaces/<domain>/`) uniquement
2. **Structure obligatoire** : `README.md` + `CLAUDE.md` + `AGENTS.md` + `.claude/{settings.json,canon-mirrors/,rules/}`
3. **Canon mirrors read-only** : sync par cron VPS DEV, jamais PR humaine
4. **Outputs autorisés/interdits** par workspace : jamais vault, raw, rag knowledge direct
5. **`AGENTS.md` exhaustif** : tout agent invoqué doit y être listé
6. **Anti-mini-monorepo** : pas de `package.json`, `tsconfig.json`, `Dockerfile`, `Makefile`, CHANGELOG ou duplication code monorepo au niveau workspace root
7. **Lifecycle** : création = ADR vault dédié, deprecation 30j minimum, sunset `_archive/workspaces/`

## Why

[[ADR-060-repository-roles-doctrine]] invariant 5 (accepted 2026-05-13) mentionne les workspaces sans préciser leur gouvernance interne. Au 2026-05-13, 4 workspaces coexistent dans `nestjs-remix-monorepo` (`app/`, `workspaces/marketing/`, `workspaces/wiki/`, `workspaces/seo-batch/`) avec des structures empiriquement similaires mais **non canonisées**.

Risques non-gouvernés identifiés :

1. **Dérive « mini-monorepo »** : un workspace pourrait acquérir un `package.json`, build pipeline indépendant, devenir sous-système autonome avec conventions divergentes (point A du review user 2026-05-13).
2. **Pollution canon** : écriture potentielle dans `governance-vault/`, `automecanik-wiki/wiki/<entity_type>/` direct, ou `automecanik-raw/` en violation d'ADR-060.
3. **Canon mirrors non-canonisés** : `.claude/canon-mirrors/` existe dans chaque workspace mais aucune règle ne définit synchronisation et règles de modification.
4. **Lifecycle implicite** : aucun cadre formel pour création, deprecation, sunset.
5. **Agents non documentés** : risque d'invoquer agents hors-`AGENTS.md`.

L'utilisateur a explicitement listé ces concerns dans le brainstorm continuation 2026-05-13 :
> qui peut écrire quoi / quel workspace sert à quoi / quels fichiers sont canon mirrors / quels agents sont autorisés / quels outputs sont interdits / comment éviter les mini-monorepos parallèles

## How

Création via PR vault `feat/adr-061-workspace-governance` :

1. `ledger/decisions/adr/ADR-061-workspace-governance.md` : créé directement en `status: accepted`, `decision_date: 2026-05-13`. Frontmatter `related_adr: [ADR-015, ADR-031, ADR-033, ADR-036, ADR-058, ADR-060]`.
2. `ops/moc/MOC-Decisions.md` : ligne ADR-061 ajoutée en `Accepted` (section « ADR Actifs » + section auto-générée).
3. Ce fichier audit-trail créé.
4. `ops/moc/MOC-AuditTrail.md` : entrée ajoutée pour audit-trail file linkage.

**Aucune modification** des autres ADRs, ni des 4 workspaces existants — la doctrine est déclarative. Audit des workspaces existants vs ADR-061 §1-§5 sera un sous-projet PR monorepo distinct si gaps détectés.

## What changes downstream

Avec `ADR-061.status == "accepted"` :

- **Canon LIVE** : la gouvernance workspace devient canon courant. Toute violation future (création workspace sans ADR, `package.json` workspace root, modification manuelle `.claude/canon-mirrors/*`, agent hors `AGENTS.md`, etc.) est régression.
- **Sous-projets cohérents** :
  - **Audit conformité 4 workspaces existants** : vérifier que `README.md`/`CLAUDE.md`/`AGENTS.md` couvrent §1-§5 ADR-061. PR monorepo si gaps.
  - **Script CI anti-mini-monorepo** : implémenter test mécanique §6 ADR-061 (find ø au niveau workspace pour `package.json`/`tsconfig.json`/`Dockerfile`/`Makefile`). Workflow CI bloquant.
  - **Script cron `sync-canon-mirrors`** : formaliser synchronisation `.claude/canon-mirrors/` par cron VPS DEV (§3 ADR-061).
- **Création future workspace** : exige un ADR dédié (motivation, périmètre, agents, outputs, sunset criteria) AVANT toute PR monorepo créant le répertoire.

Aucune modification de runtime, hooks, ou code requise par cette ratification — la doctrine est déclarative.

## Refs

- [ADR-061](../decisions/adr/ADR-061-workspace-governance.md) (accepted 2026-05-13)
- [ADR-060](../decisions/adr/ADR-060-repository-roles-doctrine.md) (doctrine repository roles, ratifiée même session PR vault #264)
- [ADR-031](../decisions/adr/ADR-031-four-layer-content-architecture.md) (4-layer content, ratifiée même session PR vault #262)
- [ADR-036](../decisions/adr/ADR-036-marketing-operating-layer.md) (workspace marketing canon, ratifiée même session PR vault #263)
- [ADR-033](../decisions/adr/ADR-033-wiki-gamme-diagnostic-relations-contract.md) (workspace wiki Phase 2)
- [ADR-058](../decisions/adr/ADR-058-repository-control-plane.md) (Repository Control Plane monorepo)
- Brainstorm continuation 2026-05-13 : `/home/deploy/.claude/plans/verifier-la-meilleure-delightful-kurzweil.md`
- Memory : `feedback_canon_rule_live_iff_adr_accepted`, `feedback_no_bricolage_align_existing_contract`, `dual-workspace-claude-context`
