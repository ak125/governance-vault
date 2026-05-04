---
type: knowledge
status: canon
created: 2026-05-04
updated: 2026-05-04
tags: [adr-031, plan-v3, rag-to-wiki, defense-in-depth, pre-commit, ci-gate, posix-ere-fix, partial-coverage]
related-adr: [ADR-031]
related-prs: [nestjs-remix-monorepo#286, nestjs-remix-monorepo#288, nestjs-remix-monorepo#290, nestjs-remix-monorepo#292]
related-knowledge: [rag-to-wiki-sot-pipeline-20260503]
related-memory: [gstack-cherry-pick-candidates, vault-hooks-canonical-pattern, feedback_no_long_polling_until_loops]
verdict: PARTIAL_COVERAGE (Étape 9 deliverable 3 livré + bug POSIX ERE corrigé en cours de session, reste deliverables 1+2 côté repo automecanik-rag)
---

# Plan v3 §Étape 9 deliverable 3 — pre-commit + CI gate `no-direct-rag-knowledge-paths`

> Session 2026-05-04. Livre la garde permanente côté monorepo : pre-commit
> hook + workflow CI qui **bloquent** toute écriture directe vers
> `automecanik-rag/knowledge/` depuis les répertoires de pipeline refactorisés.
> Defense-in-depth complement à PR #286 (ast-grep `severity: warning`).
>
> Plan source : `/home/deploy/.claude/plans/je-comprend-rien-a-spicy-reddy.md`

## Contexte

PR #286 (Étape 9 deliverable 3 partiel — règle ast-grep) a livré une garde
AST-level **non-bloquante** (severity: warning) scopée sur les literals
Python dans `scripts/{wiki-generators,wiki-exports,raw-downloaders}/`. Cette
garde flag mais ne bloque pas. Plan v3 §Étape 9 demandait explicitement un
**pre-commit qui refuse** les writes directs.

Cette session livre la couche bloquante manquante avec un pattern canonique
**1 script + hook + CI même SoT** (cf. mémoire `vault-hooks-canonical-pattern.md`).

## Livré (PR monorepo #290)

| Fichier | Rôle |
|---|---|
| `scripts/ci/check-no-direct-rag-knowledge-paths.sh` | Bash gate : `--staged` (hook), `--all` (CI), exit 2 (bad usage). `set -euo pipefail`, basename-anchored allowlist, scope path-prefix. |
| `.husky/pre-commit` | Appel `--staged` avant `ast-grep scan` (gate strict avant scan permissif) |
| `.github/workflows/check-no-direct-rag-knowledge-paths.yml` | Appel `--all` sur PR + push main, shellcheck `severity: error` |

## Distinction vs PR #286 (defense-in-depth)

| Couche | Severity | Match | Scope fichiers |
|---|---|---|---|
| `.ast-grep/rules/no-direct-rag-knowledge-write.yml` (#286) | warning | AST `kind: string` | `.py` uniquement |
| `scripts/ci/check-no-direct-rag-knowledge-paths.sh` (#290) | error (exit 1) | Regex literal entre quotes | `.py/.ts/.tsx/.js/.mjs/.cjs/.sh/.yml/.yaml` |

Même **scope dirs** (`scripts/{wiki-generators,wiki-exports,raw-downloaders}/`)
— pas d'élargissement sauvage qui aurait flag 24 références legacy
out-of-scope dans `scripts/seo/`, `scripts/rag/`, `backend/`. Discipline
anti-bricolage : élargir le scope = chantier dédié futur.

## Bug POSIX ERE (détecté + corrigé en session)

**Symptôme** : pendant les tests E2E (12 cas), un fichier Python avec literal
single-quote `'automecanik-rag/knowledge/x'` n'était pas flagué, alors que
`grep -nE` direct le trouvait.

**Cause** : pattern bash initial `[\x27"`]` utilisait l'escape hex `\x27`
qui est **PCRE-only**. Sous `grep -E` (POSIX ERE) sur stock GNU/BSD grep,
l'escape est silencieusement ignoré → couverture trompeuse, single-quoted
literals bypassaient le gate.

**Fix** (commit `4e180cbd`) :

```bash
# POSIX ERE char class : single quote injecté via $'\047' (ANSI-C octal).
# Évite le \x27 hex qui est PCRE-only et silently misses single quotes
# sous grep -E.
quote_class=$'[\047"`]'
pattern="${quote_class}(automecanik-rag/knowledge/|/opt/automecanik/rag/knowledge/)"
```

Validation post-fix : 12 cas E2E, 17/17 CI verts (TypeScript, ESLint,
Backend Tests, Frontend Tests, CodeQL, Security Audit, Secrets Detection,
Migration Safety, ADR-010 Governance, Deterministic gates, Import Firewall,
RPC Safety Gate, DEV Safety x2, Core Build, plus le workflow custom à 6s).

## État plan v3 post-session (cross-référencé git log monorepo)

| # | Étape | Status | PR(s) |
|---|---|---|---|
| 1 | Geler générateurs (`ALLOW_LEGACY_RAG_WRITE`) | ❓ probablement obsolète post-Étape 5 PR-3 | — |
| 2 | Workflow CI sync-from-wiki | ⚠️ remplacé par cron DEV VPS (PR #288, "meilleure approche zero PAT") | monorepo#288 |
| 3 | Audit classification origine 329 fiches | ✅ | wiki#17 |
| 4 | Copier 329 fiches → raw/recycled | ✅ | raw#15 |
| 5 | Refactor scripts placement | ✅ | monorepo#270, #275 |
| 6 | Régénérer contenu wiki/exports/rag/ | ✅ (fix mkdir) | monorepo#292 |
| 7 | Activer workflow sync (cron variation) | ✅ | monorepo#288 |
| 8 | Cleanup legacy + ADR-031 §D22 amend | ❓ à auditer | — |
| 9 | Garde permanente | ⚠️ **partial** | monorepo#286 (AST warn), #290 (pre-commit + CI block) |

**Étape 9 sub-deliverables canoniques** :
- ✅ deliverable 3 : pre-commit + CI monorepo (**cette session, PR #290**)
- ❓ deliverable 1 : pre-commit côté repo `automecanik-rag` refusant commits sans marker `synced-from-wiki:`
- ❓ deliverable 2 : pre-commit grep monorepo (équivalent à deliverable 3, fusionné)

Donc **8/9 étapes livrées**, reste deliverable 1 d'Étape 9 côté repo rag.

## Pattern canon validé

- **1 script + hook + CI même SoT** (cf. `vault-hooks-canonical-pattern.md`)
- `chmod +x` systématique
- shellcheck `severity: error` en CI (pas warning)
- Scope **identique** à ast-grep règle (pas d'élargissement)
- Pattern **quote-aware** (literal entre `'`/`"`/backtick) pour ne pas flag les commentaires
- Allowlist **basename-anchored** (évite faux positifs `_test_violator.py` matchant `*_test_*.py`)
- AEC verdict : `PARTIAL_COVERAGE` (12 E2E + 17 CI, pas de preuve exhaustive)

## Coverage manifest (AEC v1.0.0)

```
scope_requested        : Étape 9 deliverable 3 plan v3 (pre-commit + CI block)
scope_actually_scanned : monorepo PR #290 (3 fichiers, 189 LOC)
files_read_count       : 3 livrables + .ast-grep règle #286 + .husky/pre-commit existant
excluded_paths         : scripts/{seo,rag}/, backend/, frontend/ (24 legacy refs out-of-scope, future phase)
unscanned_zones        : repo automecanik-rag (deliverable 1 Étape 9 — chantier distinct)
corrections_proposed   : N/A (livraison directe + auto-merge enabled)
corrections_applied    : N/A (le PR ne corrige aucun code existant, ajoute une garde)
validation_executed    : 12 cas E2E locaux (quote types, comments, scope, allowlist, multi-violations, shell+yaml, basename anti-greedy) + 17/17 CI workflows
remaining_unknowns     : robustesse face à futurs patterns dynamic-build (os.path.join + variables) — non couvert ni par ast-grep ni par grep texte
final_status           : PARTIAL_COVERAGE
```

## Référence

- ADR-031 §D20/D22 — pipeline canon raw → wiki → wiki/exports/rag → rag/knowledge
- Plan v3 : `/home/deploy/.claude/plans/je-comprend-rien-a-spicy-reddy.md` §Étape 9
- Knowledge précédent : `rag-to-wiki-sot-pipeline-20260503.md` (snapshot 2026-05-03, à updater)
- Self-review session : 15-axes checklist postée comme review comment sur PR #290
- Mémoire DEV : `feedback_no_long_polling_until_loops.md` (raison du pattern ScheduleWakeup au lieu de `until ... sleep`)
