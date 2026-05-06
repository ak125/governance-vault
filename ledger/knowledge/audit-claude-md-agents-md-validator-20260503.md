---
type: knowledge
status: canon
created: 2026-05-03
updated: 2026-05-03
tags: [audit, claude-md, agents-md, validator, ci-gate, codeowners, handoff, scope-scanned]
related-adr: [ADR-012, ADR-015, ADR-022, ADR-031, ADR-032, ADR-033, ADR-036, ADR-037, ADR-038, ADR-039]
related-prs: [nestjs-remix-monorepo#271, nestjs-remix-monorepo#272, nestjs-remix-monorepo#273, automecanik-wiki#18]
related-memory: [feedback_no_hardcoded_infra_in_agentsmd, feedback_no_hybrid_workarounds, feedback_verify_existing_first, feedback_branch_scope_discipline]
verdict: SCOPE_SCANNED (Phase A + B livrées, suite future P3)
---

# Audit `CLAUDE.md` / `AGENTS.md` — validateur structurel & garde-fou CI (2026-05-03)

> Session consignant le passage d'une **discipline mémorielle** (« je dois me
> rappeler de pas hardcoder d'IP dans les fichiers d'agents ») à une
> **discipline structurelle** (« la CI me l'interdit, le pre-commit le
> bloque ») via un validateur bash réutilisé sur les patterns existants du
> monorepo. Pas de bricolage — réutilisation pure de
> [scripts/check-no-localhost.sh](https://github.com/ak125/nestjs-remix-monorepo/blob/main/scripts/check-no-localhost.sh) +
> [.github/workflows/wiki-validate.yml](https://github.com/ak125/nestjs-remix-monorepo/blob/main/.github/workflows/wiki-validate.yml).

---

## 1. Périmètre & verdict d'audit (initial B+ ~80/100)

| Fichier | Grade | Dérive identifiée |
|---|---|---|
| `CLAUDE.md` (root monorepo) | B+ | Workspace `wiki/` absent table, pas de pointer vers `agents/` |
| `workspaces/marketing/CLAUDE.md` | A- | OK |
| `workspaces/seo-batch/CLAUDE.md` | B | Section « Phase actuelle » manquante |
| `workspaces/wiki/CLAUDE.md` | A | OK |
| `backend/content/automecanik-wiki/CLAUDE.md` (submodule) | C+ | ADR-031 noté « à créer » alors qu'`accepted` 2026-04-28 |
| `agents/ceo/AGENTS.md` | B+ | OK |
| `agents/cmo/AGENTS.md` | B+ | OK |
| `agents/cpo/AGENTS.md` | **D+** | **Stub 28 lignes** — protocole/format/règles absents |
| `agents/cto/AGENTS.md` | B+ | OK |
| `agents/rag-lead/AGENTS.md` | A | AEC absent + `ADMIN_API_KEY ABSENTE` (assertion d'état figée) |
| `agents/seo-content/AGENTS.md` | A- | OK |
| `agents/seo-qa/AGENTS.md` | B+ | OK |

5 dérives ciblées + absence de garde-fou structurel.

---

## 2. Ce qui a été livré (Phase A + Phase B)

### 2.1 PRs mergées sur main

| # | Repo | Titre | Merge commit |
|---|---|---|---|
| #18 | `automecanik-wiki` | docs(claude): refresh ADR refs (031 accepted, 022 conditional, 033 added) | `800a9d22` |
| #271 | `nestjs-remix-monorepo` | feat(agents): audit + structural gate AGENTS.md/CLAUDE.md | `c2626e5e` |
| #272 | `nestjs-remix-monorepo` | fix(agents): harden validator (H1 + S1 + regression tests) | `e6cb93ef` |
| #273 | `nestjs-remix-monorepo` | chore: bump wiki submodule pointer 02cb4326 → 800a9d22 | `6e4d431d` |

### 2.2 Phase A — Curative (corrections ciblées)

- **A1** `agents/cpo/AGENTS.md` : stub 28 lignes → **101 lignes** (rôle, hiérarchie, protocole 6 étapes, format rapport, AEC, priorités P0-P3, règles)
- **A2** `automecanik-wiki/CLAUDE.md` (submodule, PR #18) : ADR-031 status à jour (`accepted` 2026-04-28), ADR-022 reformulée en contrat conditionnel `RAG_PROPOSAL_MODE`, ADR-033 ajoutée avec 3 règles `diagnostic_relations[]` §D2
- **A3** `CLAUDE.md` root : 4 workspaces (ajout `wiki/`) + section **Agents Paperclip AI-COS** (table sans UUID — SoT mapping = Paperclip) + note validation + bump date 2026-05-03
- **A4** `workspaces/seo-batch/CLAUDE.md` : section « Phase actuelle » (parité marketing/wiki, pointe les mémoires `r4-batch-progress.md` / `kw-pipeline-status.md` / `seo-kw-pipeline-canon-20260423.md`)
- **A5** `agents/rag-lead/AGENTS.md` : ajout en-tête AEC `CONTRAT DE SORTIE` (manquant — vrai gap canon AEC v1.0.0) + reformulation `ADMIN_API_KEY ABSENTE` en contrat conditionnel basé env runtime

### 2.3 Phase B — Préventive structurelle (garde-fou CI)

- **B1** `scripts/agents/validate-agents-md.sh` (nouveau, ~350 lignes bash, `set -uo pipefail`)
  - 5 modes : `--all` / `--staged` / `--diff <ref>` / `--file <path> [--type agents-md]` / `--self-test`
  - **9 self-tests embarqués** (tmpfile heredoc, pas de `/tmp` externe) :
    1. BLOCK IP brute (3 VPS hardcoded `46.224.118.55`, `49.12.233.2`, `178.104.1.118`)
    2. BLOCK UUID complet (regex format complet `[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}`)
    3. BLOCK token/clé inline (case-insensitive : `(token|api[_-]?key|secret)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9_.-]+`)
    4. BLOCK ADR « à créer »
    5. BLOCK structure AGENTS.md incomplète (absence AEC / rôle / < 60 lignes)
    6. WARN URL github (review manuelle, non bloquante)
    7. PASS fichier propre
    8. PASS « présente » lowercase (FR normal — non-régression)
    9. PASS « down » lowercase (FR normal — non-régression)
  - Anti-patterns sur **lignes ajoutées uniquement** (diff staged / PR), pas de cleanup rétroactif
  - Exclusions : `backend/content/automecanik-wiki/**` (submodule a son propre `_scripts/quality-gates.py`), `.worktrees/`, `node_modules/`, `dist/`
  - Hint mémoire dans la sortie d'erreur : `→ voir mémoire feedback_no_hardcoded_infra_in_agentsmd.md`
- **B2** `.husky/pre-commit` : bloc `if … then … fi` ancré path `(^|/)`, placé **avant** `lint-staged` et `refresh-knowledge` (pattern correct = checks bloquants en premier)
- **B3** `.github/workflows/agents-md-validation.yml` : 4 gates en série
  1. `shellcheck` du script bash (action `ludeeus/action-shellcheck@master`)
  2. `--self-test` (la logique du validateur elle-même)
  3. `--diff ${{ github.event.pull_request.base.sha }}` (anti-patterns sur lignes ajoutées — `base.sha` au lieu de `origin/<base_ref>` pour gérer l'edge case PR forkée externe)
  4. `--all` (structure complète sur AGENTS.md modifiés)
  - `fetch-depth: 0` obligatoire (sans ça `git diff` retourne vide silencieusement)
- **B4** Note de validation dans `CLAUDE.md` root sous la section Agents Paperclip
- **B5** `.github/CODEOWNERS` (nouveau) : protection `@ak125` sur `/agents/`, `/CLAUDE.md`, `/.claude/rules/`, `/scripts/agents/`, `/.github/workflows/agents-md-validation.yml`, `/.github/CODEOWNERS`

### 2.4 Hardening post-review (PR #272)

Identifié par self-review (skill `code-review` AutoMecanik + agent indépendant `superpowers:code-reviewer`) :

- **H1** *(HAUTE → fixé)* : `${{ github.event.pull_request.base.sha }}` au lieu de `origin/${{ github.base_ref }}`. Sur PR forkée externe, `actions/checkout@v4` peut configurer `origin` vers le fork → `git diff origin/main` retournerait vide silencieusement → gate passerait à tort.
- **H2** *(HAUTE → vérifié comme faux positif)* : l'agent supposait que la regex `RE_STATE_FIGE` case-insensitive matcherait « présente » lowercase. Tests empiriques ont prouvé que le filtre per-ligne case-sensitive (sans `-i`) rejette correctement → **pas de fix appliqué**, mais ajout de **2 self-tests de non-régression** (tests 8 + 9) pour figer le comportement correct.
- **S1** *(SUGGESTION → fixé)* : reorder husky pre-commit (validateur AVANT `lint-staged`).

### 2.5 Cohérence submodule (PR #273)

Pointer `backend/content/automecanik-wiki` bumped `02cb4326` → `800a9d22`. Inclut PR wiki #18 + 5 PRs métier wiki (#17 audit fiches RAG, #15 cohérence proposals, #14 cross-repo gate, #13 raw_ref content-addressing, #12 wiki-symptom-confidence drift) + 3 nightly diag-canon exports. Aucun impact fonctionnel monorepo (contenu lu par agents Claude Code workspace `wiki/`, pas par le code applicatif).

### 2.6 Mémoire canon enrichie

Sauvegardée dans `~/.claude/projects/-opt-automecanik-app/memory/feedback_no_hardcoded_infra_in_agentsmd.md` + indexée dans `MEMORY.md` :

> Pas d'IP/URL/UUID/clé en dur dans `AGENTS.md` ou `CLAUDE.md`. Référencer
> env vars (`PAPERCLIP_API_URL`, `RAG_API_BASE`, `INTERNAL_API_KEY`, etc.)
> + contrat d'usage. UUID Paperclip restent dans le registre Paperclip
> (SoT mapping), pas dans `CLAUDE.md` root.

---

## 3. Pattern technique réutilisable

```
┌──────────────────────────────────────────────────────────────────┐
│ Pattern « validateur structurel + 4-gate CI » réutilisable       │
│                                                                  │
│  scripts/<domain>/validate-<domain>.sh                           │
│  ├─ --all          (structure check, fichiers entiers)           │
│  ├─ --staged       (anti-pattern, diff cached, pre-commit)       │
│  ├─ --diff <ref>   (anti-pattern, diff vs ref, CI)               │
│  ├─ --file <path>  (debug)                                       │
│  └─ --self-test    (tests négatifs embarqués, méta-validation)   │
│                                                                  │
│  .husky/pre-commit                                               │
│  └─ if path matches → bash validate-<domain>.sh --staged         │
│                                                                  │
│  .github/workflows/<domain>-validation.yml                       │
│  ├─ shellcheck                                                   │
│  ├─ --self-test                                                  │
│  ├─ --diff ${{ github.event.pull_request.base.sha }}             │
│  └─ --all                                                        │
│                                                                  │
│  .github/CODEOWNERS                                              │
│  └─ /<domain-paths>/  @<owner>                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Niveaux de sortie** : `PASS` (exit 0), `WARN` (exit 0, advisory), `BLOCK` (exit 1).

**Anti-patterns sur lignes ajoutées uniquement** : pas de cleanup rétroactif, pas de blocage sur l'historique. Évite les PRs « grosses » et les conflits de scope.

**Hint mémoire dans la sortie d'erreur** : `→ voir mémoire <name>` permet à un futur dev/agent de comprendre la règle sans re-grep.

Réutilisable pour :
- `runbooks/*.md` (validation structure + anti-patterns)
- `governance-vault/ledger/policies/*.md` (validation frontmatter + canon)
- Templates d'agents `_templates/*.md`
- Toute famille de fichiers `.md` à structure stable

---

## 4. Améliorations futures (P1 → P3)

> Non engagées dans cette session — listées pour reprise propre future.

### P1 — `agents-md-validation` workflow trigger trop strict

**Problème observé pendant la session** : PR #273 (submodule pointer bump uniquement) a été bloquée au merge avec « 14 of 14 required status checks are expected ». Le workflow `agents-md-validation.yml` a un `paths` filter qui ne s'est pas déclenché → le check requis « Validate AGENTS.md / CLAUDE.md » n'est pas apparu → branch protection a refusé.

**Workaround temporaire** : merger main dans la branche pour amener des fichiers matchant le paths filter.

**Fix structurel proposé** : retirer le `paths` filter du `pull_request` trigger, mais ajouter un short-circuit dans le job qui exit 0 immédiatement si aucun fichier pertinent n'est modifié. Pattern :

```yaml
on:
  pull_request:  # plus de paths filter
jobs:
  validate:
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - id: changed
        run: |
          if git diff --name-only ${{ github.event.pull_request.base.sha }} HEAD \
            | grep -qE '(^|/)(AGENTS|CLAUDE)\.md$|^scripts/agents/|^\.claude/rules/'; then
            echo "relevant=true" >> $GITHUB_OUTPUT
          fi
      - if: steps.changed.outputs.relevant != 'true'
        run: echo "Aucun fichier pertinent — skip" && exit 0
      - if: steps.changed.outputs.relevant == 'true'
        # ... shellcheck + self-test + diff + all ...
```

Ainsi le check apparaît toujours en `success` (court-circuit ou validation réelle), évitant le « expected mais absent ».

### P2 — Validateur miroir côté `automecanik-wiki`

Le wiki a son propre `_scripts/quality-gates.py` (9 gates frontmatter + ADR-033 anti-patterns) mais **rien** sur le `CLAUDE.md` du repo. Si la même classe de drift réapparaît côté wiki (ex : ADR-XX « à créer » dans le futur), rien ne la bloquera.

**Action** : porter `validate-agents-md.sh` côté `ak125/automecanik-wiki` (adapté au contexte mono-fichier `CLAUDE.md` du repo). PR séparée dans le wiki repo.

### P2 — Aligner sections canoniques 3 agents (3 WARN actuels)

Le `--all` retourne 3 WARN advisory (non bloquants) :
- `agents/rag-lead/AGENTS.md` : section « ## Hiérarchie » manquante (utilise du contenu équivalent dispersé)
- `agents/seo-content/AGENTS.md` : section « ## Format ... » manquante (utilise « ## Types de tickets »)
- `agents/seo-qa/AGENTS.md` : section « ## Hiérarchie » manquante (a juste « **Reporte à** : ... »)

**Action** : restructurer ces 3 fichiers pour aligner sur la convention CMO/CTO/CPO (Rôle / Hiérarchie / Infrastructure / Protocole / Format / Règles / Priorités). PR séparée.

### P3 — Cleanup rétroactif des IP hardcodées existantes

CMO / CTO / SEO-content / SEO-qa AGENTS.md contiennent toujours `46.224.118.55:3000` et `178.104.1.118:3100` en dur. Volontairement non touchés dans cette PR (scope discipline). **Le validateur ne les flag pas** car les anti-patterns ne s'appliquent qu'aux lignes ajoutées, pas à l'existant.

**Action** : remplacer par références env vars (`NESTJS_DEV_URL`, `PAPERCLIP_API_URL`, `RAG_API_BASE`) + contrats conditionnels. PR séparée, 1 fichier à la fois pour faciliter review.

### P3 — `shellcheck` en pre-commit local

Actuellement `shellcheck` ne tourne qu'en CI (B3 step 1). Un dev pourrait commit un script bash buggé localement et découvrir l'erreur uniquement en CI.

**Action** : ajouter `shellcheck scripts/agents/*.sh 2>/dev/null || true` (soft-fail) dans `.husky/pre-commit`, juste avant l'invocation du validateur. Soft-fail acceptable car `shellcheck` n'est pas garanti localement.

### P3 — Markdown link checker

Aucun gate ne vérifie les liens cassés dans les `CLAUDE.md` / `AGENTS.md`. Si un lien vers un ADR vault devient mort (renommage, suppression), aucune détection automatique.

**Action** : ajouter `lychee` ou `markdown-link-check` en CI sur les fichiers gouvernance. WARN uniquement (false positives possibles sur intranet).

### P3 — Auto-bump submodule pointer

Le drift wiki submodule (cf. PR #273) va se reproduire à chaque PR mergée côté wiki repo. Sans monitoring, le pointer reste stale jusqu'à ce que quelqu'un remarque.

**Action** : workflow CI `submodule-drift-check.yml` qui ouvre une PR auto si le pointer est en retard de N commits sur l'origin/main du submodule. Read-only depuis la perspective du vault (le push en monorepo est OK).

### P3 — Frontmatter Zod / JSON Schema pour `AGENTS.md`

Anthropic + l'industrie poussent un format universel `AGENTS.md` (spec sur agents.md). Si un jour une convention frontmatter émerge (`schema_version`, `role_id`, etc.), notre validateur bash devra évoluer vers un validateur Zod TS (pattern ADR-039 wiki). **Pas urgent** — laisser l'écosystème stabiliser avant d'investir.

### P3 — CODEOWNERS — étendre aux `.claude/skills/`

Actuellement `/agents/`, `/CLAUDE.md`, `/.claude/rules/` sont protégés. Mais `.claude/skills/*.md` (16 skills DEV/SEO côté workspaces) ne le sont pas. Une PR pourrait modifier un skill canon sans review owner.

**Action** : ajouter `/.claude/skills/    @ak125` au CODEOWNERS si le scope skills devient critique.

---

## 5. Anti-patterns évités explicitement (canon)

1. ❌ **Inventer un format frontmatter Zod pour AGENTS.md** — over-engineering pour 7 fichiers prose. On a aligné sur le pattern existant `_scripts/quality-gates.py` du wiki en plus simple (bash + grep).
2. ❌ **Auto-générer les sections par script** — les humains éditent les AGENTS.md, on valide pas on génère.
3. ❌ **Dupliquer les UUID Paperclip dans le repo** — SoT mapping = Paperclip, pas le monorepo.
4. ❌ **Cleanup rétroactif des IP existantes** — hors scope, risque dérive ; le validateur bloque seulement les **nouvelles** additions.
5. ❌ **Hook qui patche les internals Claude Code** — cf. `feedback_no_bricolage_clean_layer.md`.
6. ❌ **Solution hybride transitoire** — cf. `feedback_no_hybrid_workarounds.md`. Le validateur va direct en CI BLOCK, pas en mode warning préalable.
7. ❌ **Hardcoder l'IP Paperclip dans les nouvelles AGENTS.md** — env var `PAPERCLIP_API_URL` uniquement. Mémoire `feedback_no_hardcoded_infra_in_agentsmd.md`.

---

## 6. Coverage manifest AEC v1.0.0

```yaml
scope_requested: Audit + correction CLAUDE.md / AGENTS.md monorepo + garde-fou anti-régression
scope_actually_scanned:
  - 12 fichiers canon (5 CLAUDE.md + 7 AGENTS.md)
  - 4 PRs ouvertes/mergées (monorepo #271/#272/#273, wiki #18)
files_read_count: 11 (dont plan rev 6, MEMORY.md ciblé, validateur, husky, workflow, CODEOWNERS)
excluded_paths:
  - .worktrees/* (worktrees temporaires non canoniques)
  - .claude/knowledge/modules/*.md (auto-refresh hook pre-commit, 42 fichiers)
  - log.md (auto-append session-log Stop hook)
unscanned_zones:
  - PR forkée externe — comportement réel non testé empiriquement (analyse statique uniquement)
  - 4 AGENTS.md historiques (CMO/CTO/seo-content/seo-qa) — IP hardcodées non corrigées (volontaire, hors scope)
corrections_proposed: 5 (Phase A) + 5 garde-fous (Phase B) + 3 hardening (PR #272) + 1 submodule bump (PR #273) = 14
corrections_applied: 14 (toutes mergées sur main + wiki main)
validation_executed:
  - 16 + 17 + 15 checks CI PASS sur PR #271 / #272 / #273 (monorepo)
  - 3 checks PASS sur PR #18 (wiki)
  - --self-test 9/9 PASS (validateur méta-validé)
  - Review skill code-review : APPROVE
  - Review agent superpowers:code-reviewer : APPROVE
remaining_unknowns:
  - Comportement empirique sur PR forkée externe (mitigation appliquée via base.sha)
  - Drift futur sur submodule pointer si PRs wiki s'enchaînent
  - Évolution Anthropic AGENTS.md spec universelle
final_status: SCOPE_SCANNED
```

---

## 7. Références

- **PRs livrées** : `nestjs-remix-monorepo` #271 (`c2626e5e`), #272 (`e6cb93ef`), #273 (`6e4d431d`) ; `automecanik-wiki` #18 (`800a9d22`)
- **Plan détaillé** : `/home/deploy/.claude/plans/je-veux-savoir-si-tranquil-riddle.md` (rev 6)
- **Mémoire canon** : `feedback_no_hardcoded_infra_in_agentsmd.md`
- **ADRs liées** : ADR-012 (3-VPS), ADR-015 (vault SoT), ADR-022 (R8 RAG control plane), ADR-031 (raw/wiki/exports/consumers), ADR-032 (diagnostic & maintenance), ADR-033 (gamme `diagnostic_relations[]`), ADR-036 (marketing operating layer), ADR-037/038 (agent naming canon), ADR-039 (wiki frontmatter Zod)
- **Patterns réutilisés** :
  - `scripts/check-no-localhost.sh` (anti-pattern script local)
  - `.github/workflows/wiki-validate.yml` (pattern shape-check CI)
  - `.husky/pre-commit` ast-grep wire (déclenchement conditionnel)
  - `.github/workflows/agent-exit-contract-hash.yml` (pattern hash-canon-publish)

---

## 8. Reprise future (ordre recommandé)

1. **P1** — Fix `agents-md-validation` workflow trigger (paths filter → short-circuit interne) pour éviter le blocage de merge sur PRs micro qui ne touchent pas `agents/` ni `CLAUDE.md`
2. **P2** — Aligner les 3 AGENTS.md historiques (rag-lead / seo-content / seo-qa) sur la convention sections canoniques (3 WARN actuels → 0 WARN)
3. **P2** — Porter le validateur côté `automecanik-wiki` repo (CLAUDE.md du wiki)
4. **P3** — Cleanup rétroactif des IP hardcodées (CMO / CTO / seo-content / seo-qa), 1 fichier par PR
5. **P3** — Étendre CODEOWNERS aux skills, ajouter `shellcheck` local, link-checker, auto-bump submodule

Pas d'urgence sur les P3 — la qualité actuelle est verrouillée structurellement.
