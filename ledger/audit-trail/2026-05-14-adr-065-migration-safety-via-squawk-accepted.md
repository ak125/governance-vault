---
date: 2026-05-14
type: audit-trail
related: [ADR-065, ADR-049, ADR-058, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-14 — ADR-065 Migration Safety Gate — grep → squawk (acceptance)

## What

Promotion de **[[ADR-065-migration-safety-via-squawk]]** :

- `status: proposed → accepted`
- `decision_date: null → 2026-05-14`
- `reviewed_by: "" → "@fafa"`
- decision_maker : @fafa

L'ADR-065 entre en canon LIVE (`feedback_canon_rule_live_iff_adr_accepted`). Le PR monorepo [`feat/ci-squawk-migration-safety`](https://github.com/ak125/nestjs-remix-monorepo/pull/517) est **débloqué pour merge** : il remplace le job `migration-safety` regex-based par `sbdchd/squawk-action@v2`, ajoute `.squawk.toml` au root (pg_version 17.0, `excluded_paths = ["**/*.down.sql"]`, `[upload_to_github] fail_on_violations = true`), pin `squawk-cli@2.52.1` en devDep racine, et expose `npm run sql:lint` pour parité locale.

## Why

Décision conduite en 4 rounds de revue contradictoire :

1. **Round 1** : proposition initiale avec config TOML inventée (`banned_rules`, `require_rules`). Reviewer humain a flagué la syntaxe — corrigée via `excluded_rules` / `included_rules` / `excluded_paths` (schema squawk authoritative).
2. **Round 2** : reviewer a proposé `included_rules = ["prefer-robust-stmts", "prefer-bigint"]` + `excluded_rules = ["ban-drop-not-null"]`. Verification source (`crates/squawk_linter/src/lib.rs Rule::is_opt_in()` ne retourne `true` que pour `RequireTableSchema`) a montré : `included_rules` no-op (règles déjà default-on), `prefer-bigint` n'existe pas (vrai nom `prefer-bigint-over-int`), `ban-drop-not-null` est une règle *safe* (bans DROP NOT NULL, pas adding NOT NULL — confusion avec `adding-not-nullable-field`). Config minimale finale retient seulement `pg_version` + `assume_in_transaction` + `excluded_paths`.
3. **Round 3** : action input `pattern:` → `files:` (action.yml note : "Cannot contain glob patterns" pour `files`). Version d'action `@v1` → `@v2` (confirmé via squawk-action README).
4. **Round 4** : "no bricolage" répété 3× a forcé escalade explicite — restoration de `npm run sql:lint` (pinned devDep `squawk-cli@2.52.1` + invocation directe `node node_modules/squawk-cli/js/bin/squawk` qui bypasse deux quirks de la distribution npm), fix worktree-detection bug dans `_scripts/check-signatures.sh` (companion vault PR #276).

Le déclencheur initial était un false-positive du gate regex legacy sur un commentaire prose français dans `20260514_seo_crux_field_history.down.sql:13` (PR monorepo #514). Le fix pragmatique sur main a reformulé la prose ("la suppression du log event si jamais si jamais effectué" — duplication témoin d'un edit pressé, commit `8bf0c037`). C'est exactement le pattern bricolage que squawk élimine structurellement (AST parser ignore le contenu des commentaires).

## Bénéfices runtime mesurés

- **Diff CI** : `+32 / -79` lignes en `.github/workflows/ci.yml` (gate plus léger, plus lisible).
- **Set de règles élargi** : 30+ rules default-on incluant modern best-practice (`require-concurrent-index-creation`, `require-timeout-settings`, `prefer-bigint-over-int`, `prefer-identity`, `prefer-timestamptz`, `prefer-robust-stmts`, `disallowed-unique-constraint`) — alors que le gate legacy couvrait 7 patterns regex.
- **Premier passage full-corpus local** (`npm run sql:lint`) : 1116 findings sur 181 / 216 migrations lintables (mostly modernization opportunities, **non-blocking** car le gate CI lint uniquement les fichiers changés).
- **129 `-- APPROVED:` annotations existantes** conservées en prose (aucun churn, squawk les ignore comme commentaires).

## Audit-trail companion : vault PR #276 (worktree fix)

Au cours de l'exécution du PR monorepo #517, le pre-push hook G3 du vault (`_scripts/check-signatures.sh`) a échoué sur un worktree avec `Error: not a git repo` — cause : `[[ -d "$VAULT_PATH/.git" ]]` est `false` dans un worktree (`.git` y est un fichier pointeur, pas un répertoire). Workaround initial : push depuis le main checkout. Workaround éliminé via [PR vault #276](https://github.com/ak125/governance-vault/pull/276) — remplace `[[ -d ]]` par `git rev-parse --is-inside-work-tree` aux 3 call sites (check-signatures.sh + evidence-pack.sh). Méta-test : la PR #276 elle-même est poussée depuis un worktree, prouvant le fix.

## Impacts cross-canon

- **ADR-049 (DB Governance)** : ADR-065 utilise le même template frontmatter, étend la couverture safety à la couche migration linting (vs RPC/RLS déjà couvert par `scripts/audit/rpc-safety-gate.js`).
- **ADR-058 (Repository Control Plane)** : `.squawk.toml` au root est tracé via ownership.yaml `glob: .squawk.toml` (domain D15, owner @ak125), conforme §PR-G.
- **MOC-Decisions** : ADR-065 indexé (ligne dédiée, formule canonique grepable « regex sur SQL ne distingue pas syntaxe et prose ; passer à libpg_query (squawk) pour parser l'AST »).
- **Canon mémoire** ajouté au monorepo : `feedback_grep_based_sql_gates_are_bricolage` + `feedback_two_pr_recovery_platform_for_ci_gate_replacement` (institutionalise les leçons).

## Follow-ups (out of scope post-acceptance)

Listés dans corps ADR-065 § "Follow-ups (post-merge)" :

- Symétrie pre-commit local optionnelle (`.husky/pre-commit` invoke `npm run sql:lint -- <staged.sql>`).
- Wrapper SARIF si workflow de revue centralisée adopté un jour.
- Activation `require-table-schema` (seule règle opt-in) si standardisation schemas explicites.
- Modernisation rétroactive des 181 migrations avec findings squawk (chantier V2 séparé).

## Décideur

@fafa (2026-05-14), après 4 rounds de revue contradictoire (round 4 = direction explicite "no bricolage" × 3 ayant forcé l'élimination des workarounds résiduels : sql:lint réintégré + G3 worktree bug corrigé).
