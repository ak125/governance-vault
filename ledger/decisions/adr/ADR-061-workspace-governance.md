---
id: ADR-061
title: "Workspace Governance — frontière, lifecycle, ownership, anti-mini-monorepo"
status: accepted
date: 2026-05-13
decision_date: 2026-05-13
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "G5"]
related_incidents: []
related_adr: ["ADR-015", "ADR-031", "ADR-033", "ADR-036", "ADR-058", "ADR-060"]
---

# ADR-061 : Workspace Governance — frontière, lifecycle, ownership, anti-mini-monorepo

## Context

[[ADR-060-repository-roles-doctrine]] (accepted 2026-05-13) invariant 5 mentionne « les runtimes opérationnels vont aux workspaces (`workspaces/marketing/`, `workspaces/wiki/`, `workspaces/seo-batch/`) » mais **ne précise pas leur gouvernance interne**. Au 2026-05-13, 4 workspaces Claude Code coexistent dans le monorepo `ak125/nestjs-remix-monorepo` :

| Workspace | Path | Rôle | ADR de référence |
|---|---|---|---|
| **DEV root** | `app/` | dev daily backend/frontend, refactor, CI, ADR, governance | (racine, pas d'ADR dédié) |
| **Marketing** | `app/workspaces/marketing/` | 3 agents G1 (LEAD/LOCAL/RETENTION) Phase 1-2 | [[ADR-036-marketing-operating-layer]] |
| **Wiki** | `app/workspaces/wiki/` | sas wiki documentaire (Phase 2) | [[ADR-033-wiki-gamme-diagnostic-relations-contract]] |
| **SEO batch** | `app/workspaces/seo-batch/` | 39 agents R0-R8 + 16 skills SEO | (référencé par [[ADR-031-four-layer-content-architecture]]) |

Risques observés en l'absence de canon explicite :

1. **Dérive « mini-monorepo »** : chaque workspace pourrait acquérir son propre `package.json`, `tsconfig.json`, build pipeline indépendant, devenant un sous-système autonome avec conventions divergentes, duplication, drift, agents incompatibles.
2. **Pollution canon** : un workspace pourrait écrire dans `governance-vault/`, `automecanik-wiki/wiki/<entity_type>/` directement, ou `automecanik-raw/`, en violation d'ADR-060 invariants 1-3 et 5.
3. **Canon mirrors non-canonisés** : chaque workspace contient `.claude/canon-mirrors/` mais aucune règle ne dit *qui le maintient*, *comment il se synchronise*, *si modification manuelle est autorisée*.
4. **Lifecycle implicite** : aucun cadre ne définit la création, la deprecation, ou le sunset d'un workspace.
5. **Agents non documentés** : risque de charger des agents non listés dans `AGENTS.md` du workspace, ou d'utiliser un workspace pour des agents hors périmètre.

Memory rule `feedback_canon_rule_live_iff_adr_accepted` : tant qu'aucune ADR ne canonise la gouvernance workspace, ces risques restent fragiles.

## Decision

Adopter une **gouvernance canon des workspaces** structurée en 6 invariants opposables à tout futur PR/agent.

### 1. Typologie canon (catégories autorisées)

**Deux et seulement deux catégories** de workspace Claude Code sont canon :

| Catégorie | Path canon | Rôle |
|---|---|---|
| **DEV root** | `app/` | Workspace racine, dev daily, accès complet aux skills DEV, **aucun agent Paperclip R*/G* chargé** |
| **Domain workspace** | `app/workspaces/<domain>/` | Périmètre métier dédié (marketing, seo-batch, wiki, futurs domaines), charge **uniquement** les agents/skills/rules du domaine |

**Toute autre catégorie est interdite** : pas de `workspaces/foo-utility/` sans ADR de création, pas de `tools/<workspace>/`, pas de `scripts/<workspace>/`.

### 2. Structure obligatoire par domain workspace

Chaque `app/workspaces/<domain>/` **doit** contenir :

| Fichier / Dossier | Obligatoire ? | Rôle |
|---|---|---|
| `README.md` | ✅ Oui | Documenter rôle, périmètre, agents, outputs autorisés/interdits |
| `CLAUDE.md` | ✅ Oui | Configuration Claude Code spécifique au workspace |
| `AGENTS.md` | ✅ Oui (si agents Paperclip présents) | Lister agents activés, leur rôle, leur scope |
| `.claude/settings.json` | ✅ Oui | Configuration Claude Code (permissions, hooks) |
| `.claude/canon-mirrors/` | ✅ Oui | Mirrors **read-only** des canons vault/wiki nécessaires |
| `.claude/rules/` | ✅ Oui | Règles locales au workspace (mirrors canon vault + complément local éventuel) |
| `.claude/agents/` | Optionnel | Agents Paperclip si workspace en utilise |
| `.claude/skills/` | Optionnel | Skills locales au workspace |

**Aucun autre fichier n'est canon** au niveau workspace root : pas de `package.json`, pas de `tsconfig.json`, pas de `build.sh`, pas de `Dockerfile` (cf. invariant 6 anti-mini-monorepo).

### 3. Canon mirrors — règles de synchronisation

`app/workspaces/<domain>/.claude/canon-mirrors/` est **read-only par construction** :

- **Source** : copies des canons depuis `governance-vault/` ou `automecanik-wiki/` (chemins exacts dans le `README.md` du workspace).
- **Synchronisation** : par cron VPS DEV (`scripts/cron/sync-canon-mirrors.py` ou équivalent), **jamais** par PR humaine au workspace.
- **Modification manuelle interdite** : pre-commit hook bloque les diffs dans `.claude/canon-mirrors/*` non-issus du script de sync (signature détectable).
- **Sortie** : tout PR modifiant `.claude/canon-mirrors/*` doit pointer vers un commit upstream vault/wiki et inclure le manifeste sync. Sinon = régression.

**Justification** : les canon mirrors sont des copies projectives, jamais SoT — cf. [[ADR-060-repository-roles-doctrine]] invariants 1-2.

### 4. Outputs autorisés / interdits par workspace

Pour chaque domain workspace, le `README.md` doit lister explicitement les **outputs autorisés** et **outputs interdits**. Règles canon transversales :

| Workspace | Output autorisé | Output interdit |
|---|---|---|
| `workspaces/marketing/` | Tables DB `__marketing_*` via backend NestJS `marketing/`, briefs structurés (jamais `.md` flottants wiki) — cf. [[ADR-036-marketing-operating-layer]] | Wiki direct, vault, raw, automecanik-rag |
| `workspaces/wiki/` | `automecanik-wiki/proposals/*.md` (FLAT, schema v1.0) — cf. [[ADR-033-wiki-gamme-diagnostic-relations-contract]] et D19 d'[[ADR-031-four-layer-content-architecture]] | `automecanik-wiki/wiki/<entity_type>/` direct, vault, raw |
| `workspaces/seo-batch/` | RPC monorepo (`backend/supabase/migrations/`), scripts SEO (`scripts/seo/`), tables `__seo_*` | Vault, wiki direct, raw |

**Interdits transversaux** (s'appliquent à tous les workspaces) :

- **Écriture vault** : aucun workspace n'écrit dans `governance-vault/`. La gouvernance est centrale, pas distribuée.
- **Écriture raw** : aucun workspace n'écrit dans `automecanik-raw/`. La collecte raw est pipeline dédié, pas workspace agentique.
- **Écriture rag knowledge directe** : `automecanik-rag/knowledge/` est répertoire généré (D22 d'ADR-031), jamais modifié par workspace.

### 5. Agents autorisés par workspace

L'`AGENTS.md` de chaque workspace **liste exhaustivement** les agents Paperclip et skills locaux activés. **Aucun agent hors-AGENTS.md ne peut être invoqué** sous le scope du workspace.

État au 2026-05-13 :

| Workspace | Agents | Skills locaux |
|---|---|---|
| `app/` (DEV root) | **0 agent R*/G*** | 8 skills DEV (code-review, db-migration, frontend-design, governance-vault-ops, responsive-audit, session-log, ui-ux-pro-max, vehicle-ops) |
| `workspaces/marketing/` | 3 agents G1 (LEAD/LOCAL/RETENTION) — Phase 1-2 ADR-036 | Skills marketing (cf. AGENTS.md) |
| `workspaces/wiki/` | (Phase 2 future : agents wiki orchestrateurs) | `wiki-proposal-writer` |
| `workspaces/seo-batch/` | 39 agents R0-R8 | 16 skills SEO (content-gen, kw-classify, pollution-scanner, seo-gamme-audit, r8-diversity-check, rag-check, v5-guardian, …) |

**Invariant** : ajouter ou retirer un agent d'un workspace **exige** une PR modifiant `AGENTS.md` du workspace, signée G3.

### 6. Anti-mini-monorepo (5 interdictions structurelles)

Pour éviter qu'un workspace dérive en sous-monorepo autonome (point A du review user 2026-05-13) :

1. **Pas de `package.json` au niveau workspace root** — le monorepo a un seul `package.json` racine (`app/package.json`). Les workspaces n'ont pas de dépendances npm propres.
2. **Pas de `tsconfig.json` workspace root** — config TS centralisée dans `app/tsconfig.json` + `packages/tsconfig/`.
3. **Pas de build pipeline indépendant** — pas de `Dockerfile`, pas de `build.sh`, pas de `Makefile` workspace. Le CI/build est central via `app/.github/workflows/`.
4. **Pas de gestion de versions indépendante** — aucun workspace n'a son `CHANGELOG.md` propre. L'historique est dans le repo monorepo unique.
5. **Pas de duplication de code monorepo** — les workspaces n'embarquent jamais une copie de `backend/`, `frontend/`, `packages/`. Ils consomment ces modules via références canon (cf. `.claude/canon-mirrors/` + `AGENTS.md`).

**Test mécanique** : `find app/workspaces -maxdepth 3 -name "package.json" -o -name "tsconfig.json" -o -name "Dockerfile" -o -name "Makefile"` doit retourner ø au 2026-05-13. Tout hit futur = régression bloquante.

### 7. Lifecycle workspace

| Phase | Procédure |
|---|---|
| **Création** | PR vault avec ADR dédié (motivation, périmètre, agents, outputs autorisés/interdits, sunset criteria) + PR monorepo créant `app/workspaces/<domain>/` avec structure obligatoire (§2). |
| **Modification mineure** | PR monorepo signée (modifier `README.md`, `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, `.claude/skills/`). |
| **Ajout/retrait agent** | PR monorepo signée modifiant `AGENTS.md` du workspace. |
| **Deprecation** | Marquer dans `README.md` du workspace (banner `> ⚠️ DEPRECATED — sunset le YYYY-MM-DD`) + amendement de l'ADR de création (`superseded_by` ou `status: deprecated`). |
| **Sunset** | Après 30 jours minimum de deprecation visible, archiver dans `app/_archive/workspaces/<domain>-<date>/` (préserver le code, retirer du Claude Code routing). Audit-trail vault obligatoire. |

## Options considérées

### Option A — Pas d'ADR, laisser canon de fait (rejetée)

Continuer sans canon explicite.

**Inconvénients** : violation de `feedback_canon_rule_live_iff_adr_accepted` ; les 5 risques observés (mini-monorepo drift, pollution canon, canon mirrors non gouvernés, lifecycle implicite, agents non documentés) restent ouverts.

### Option B — Bundle dans ADR-060 (rejetée)

Insérer les 7 sections workspace governance dans ADR-060 comme nouvelles décisions.

**Inconvénients** : viole le pattern « 1 ADR = 1 décision » établi par ADR-058/059/060. ADR-060 a déjà 5 invariants ; ajouter 6+ invariants workspace dilue le concern doctrine repository roles avec les détails opérationnels workspace.

### Option C — Nouvel ADR-061 dédié workspace governance (chosen)

Une ADR séparée, concern unique : gouvernance interne des workspaces. Pattern aligné avec ADR-058/059/060.

**Avantages** :
- Concern pur, évolution indépendante possible (ajout futurs workspaces sans modifier ADR-060)
- Cross-références faciles depuis ADRs futurs (« voir ADR-061 §6 anti-mini-monorepo »)
- Lecture rapide : 1 page = workspace governance complète
- Aligne avec invariant 5 d'ADR-060 sans le diluer

## Conséquences

### Positives

- Workspace governance ratifiée → `feedback_canon_rule_live_iff_adr_accepted` satisfaite, canon LIVE
- 5 risques observés verrouillés mécaniquement (typologie, structure, canon mirrors, outputs, agents, anti-mini-monorepo, lifecycle)
- Futurs workspaces (e.g. workspace customer-support, workspace ops) suivent un cadre canon plutôt qu'improvisation
- Pattern de PR pour modifier un workspace bien défini

### Négatives / Coûts

- Documentation workspace existants à mettre à jour (audit `README.md` / `CLAUDE.md` / `AGENTS.md` des 4 workspaces actuels — out-of-scope ici, sous-projet PR monorepo distinct si gaps détectés).
- Test mécanique anti-mini-monorepo (§6) à scripter en CI — sous-projet distinct (CI invariants hardening déjà identifié dans plan downstream).

### Neutres

- ADR-031, ADR-033, ADR-036, ADR-058, ADR-060 inchangés dans le body
- Aucune modification immédiate des workspaces existants
- `automecanik-wiki/`, `automecanik-raw/`, `automecanik-rag/` inchangés

## Conformité règles vault

- **G1 (Canon fait foi)** : ADR-061 ratifiée AVANT toute création de nouveau workspace ou modification structurelle d'un workspace existant
- **G2 (Zéro orphelin)** : MOC-Decisions ligne ADR-061 ajoutée + MOC-AuditTrail entrée
- **G3 (Signed commits)** : commit signé via clé `vault-signing@automecanik.com`
- **G5 (Canon authoritative)** : ADR-061 référencée par MOC-Decisions post-merge

## Mise en œuvre

ADR-061 créée directement en `status: accepted` (pattern atomique [[ADR-059-seo-runtime-projection]] et [[ADR-060-repository-roles-doctrine]] du 2026-05-13). Aucune cascade d'implémentation immédiate — la doctrine est déclarative, applicable à tout futur PR/agent touchant un workspace.

Audit-trail vault créée dans la même PR (`ledger/audit-trail/2026-05-13-adr-061-workspace-governance.md`) conformément à `feedback_auto_vault_audit_trail_on_adr`.

Sous-projets downstream rendus cohérents (chacun aura sa propre planification) :

1. **Audit conformité des 4 workspaces existants** — vérifier que `README.md`, `CLAUDE.md`, `AGENTS.md` couvrent les invariants §1-§5 d'ADR-061. PR monorepo si gaps.
2. **Script CI anti-mini-monorepo** — implémenter le test mécanique §6 dans un workflow CI bloquant.
3. **Script cron `sync-canon-mirrors`** — formaliser la synchronisation `.claude/canon-mirrors/` par cron VPS DEV.

## Références

- [[ADR-015-vault-single-source-of-truth]]
- [[ADR-031-four-layer-content-architecture]]
- [[ADR-033-wiki-gamme-diagnostic-relations-contract]]
- [[ADR-036-marketing-operating-layer]]
- [[ADR-058-repository-control-plane]]
- [[ADR-060-repository-roles-doctrine]]
- [[MOC-Decisions]]
- Memory : `feedback_canon_rule_live_iff_adr_accepted`, `feedback_no_bricolage_align_existing_contract`, `dual-workspace-claude-context`
- Brainstorm continuation : `/home/deploy/.claude/plans/verifier-la-meilleure-delightful-kurzweil.md` (session 2026-05-13)
