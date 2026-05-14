---
id: ADR-065
title: "Migration Safety Gate — grep → squawk (SQL AST linter)"
status: proposed
date: 2026-05-14
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G1, T1]
related_incidents: []
reviewed_by: ""
---

# ADR-065 : Migration Safety Gate — grep → squawk (SQL AST linter)

## Contexte

Le CI du monorepo `nestjs-remix-monorepo` exécute un job `migration-safety` ([`.github/workflows/ci.yml:487-577`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/.github/workflows/ci.yml#L487-L577)) qui inspecte chaque migration SQL ajoutée par un PR pour détecter 7 opérations dangereuses :

| Sévérité | Pattern grep | Action |
|---|---|---|
| P0 BLOCK | `DROP TABLE` | exit 1 sauf si `-- APPROVED:` sur la même ligne |
| P0 BLOCK | `ALTER TABLE … DROP COLUMN` | idem |
| P0 BLOCK | `ALTER TABLE … DISABLE ROW LEVEL` | idem |
| P0 BLOCK | `DROP POLICY` | idem |
| P1 WARN | `TRUNCATE` | warning seul |
| P1 WARN | `DELETE FROM` sans `WHERE` | warning seul |
| P1 WARN | `GRANT … TO public` | warning seul |

La logique est 90 lignes de bash inline avec `grep -iE` sur le contenu brut du fichier `.sql`.

### Incident déclencheur — false positive sur prose `--` comment (2026-05-14)

PR [#514 `feat(seo-crux)`](https://github.com/ak125/nestjs-remix-monorepo/pull/514) ajoute une rollback migration `backend/supabase/migrations/20260514_seo_crux_field_history.down.sql`. Ligne 13 contient une note descriptive expliquant pourquoi une valeur d'ENUM ne peut pas être supprimée :

```sql
-- référence (toutes supprimées par le DROP TABLE event_log si jamais
```

Cette ligne est **un commentaire SQL `--`** — c'est de la prose française décrivant un comportement hypothétique. Le grep `grep -iE 'DROP\s+TABLE'` la matche, et le filtre `grep -v '\-\- APPROVED:'` ne la retire pas (la prose ne porte pas le marker). Le gate échoue avec :

```
❌ DROP TABLE detected without '-- APPROVED:' comment
```

Le PR a été débloqué en **reformulant la prose pour éviter le mot "DROP TABLE"** (commit hâtif visible sur main : "toutes supprimées par la **suppression du log event si jamais si jamais** effectué" — duplication "si jamais si jamais" témoin d'un edit pressé). C'est le pattern **bricolage** qu'on doit éviter — la prochaine fois qu'un dev écrit "DROP TABLE" dans un commentaire descriptif, le gate refire.

### Cause racine — structurelle, pas du tweak

`grep` opère sur du **texte brut**. Il ne peut pas distinguer :

- du SQL exécutable (`DROP TABLE foo;`)
- une chaîne littérale (`SELECT 'DROP TABLE foo' FROM ...`)
- un commentaire (`-- DROP TABLE event_log`)
- un identifiant (`CREATE TABLE drop_table_audit (...)`)

Le whitelist `-- APPROVED:` traite le symptôme : il force tout DROP légitime à porter un marker, ce qui produit du bruit (129 annotations dans 16 migrations existantes) mais ne résout pas la classe de false positives sur la prose. Le grep ne comprend pas le SQL, donc on ne peut pas le réparer plus finement — il faut **remonter d'un niveau** (canon `feedback_no_bricolage_escalate_to_industry_standard.md`) et utiliser un parser SQL réel.

## Décision

Remplacer le gate `migration-safety` du CI par [**squawk**](https://github.com/sbdchd/squawk), un linter Postgres construit sur `libpg_query` (le vrai parser Postgres extrait du moteur C). Squawk évalue l'AST SQL, donc les commentaires et chaînes littérales ne déclenchent jamais les règles.

### Pourquoi squawk plutôt qu'Atlas migrate lint / sqlfluff

- **Squawk** = linter standalone sur fichiers SQL bruts. Drop-in pour le pattern existant `backend/supabase/migrations/*.sql`. Maintenu activement (v2.52.1 sortie 2026-05-13, releases hebdomadaires). Utilisé en prod par Stripe / Sentry / Discord. **GitHub Action officielle** [`sbdchd/squawk-action@v2`](https://github.com/sbdchd/squawk-action) qui poste les violations en commentaires PR.
- **Atlas migrate lint** = framework de migration complet (versioning + auto-generation + rollback). Imposerait de refactor toute la couche migration Supabase. Trop lourd pour un problème de gate CI.
- **sqlfluff** = multi-dialect mais centré sur le formatting, pas la safety. Pas le bon outil.

### Configuration retenue (`.squawk.toml` à la racine du monorepo)

```toml
assume_in_transaction = true
pg_version            = "17.0"           # Supabase managed PG (MCP get_project verified)

excluded_paths = [
  "**/*.down.sql",                       # Rollbacks invert intent : DROP/TRUNCATE legitimate by design.
]

[upload_to_github]
fail_on_violations = true                # CI hard-fail sur toute violation default-rule.
```

- **Pas de `included_rules`** : la lecture de [`crates/squawk_linter/src/lib.rs`](https://github.com/sbdchd/squawk/blob/main/crates/squawk_linter/src/lib.rs) `Rule::is_opt_in()` confirme que seule `require-table-schema` est désactivée par défaut. **Toutes les autres règles sont actives par défaut**, y compris les 5 équivalents des P0 BLOCK legacy (`ban-drop-table`, `ban-drop-column`, `ban-drop-database`, `ban-truncate-cascade`, `disallowed-unique-constraint`) **plus** un large set de règles modernes (`prefer-bigint-over-int`, `prefer-identity`, `prefer-timestamptz`, `prefer-robust-stmts`, `require-concurrent-index-creation`, `require-timeout-settings`, etc.).
- **Pas de `excluded_rules`** : on fait confiance au set par défaut upstream. Si une règle produit du bruit sur un pattern légitime, préférer un `-- squawk-ignore-file <rule>` documenté dans la migration plutôt qu'une exclusion globale dans le config (canon `feedback_no_bricolage_clean_layer.md`).

### Périmètre laissé hors squawk

Les 3 règles WARN legacy qui n'existent pas dans squawk stock :

| Règle legacy | Couvert par | Justification |
|---|---|---|
| `DISABLE ROW LEVEL` | Supabase advisors + `scripts/audit/rpc-safety-gate.js` | Pas un sujet de migration-shape ; déjà multi-couches |
| `GRANT … TO public` | idem | idem |
| `DELETE FROM` sans `WHERE` | (sortie de scope) | Pas un anti-pattern de migration ; runtime-relevant |
| `DROP POLICY` | (autorisé) | Pattern idempotent re-create dans la même migration — design-allowed |

## Conséquences

### Positives

- Aucun false positive sur prose `--` commentée : l'AST parser ignore le contenu des commentaires nativement.
- Plus de noise `-- APPROVED:` à ajouter dans les nouvelles migrations (les 129 existants restent en prose).
- Set de règles élargi : modern best-practice (concurrent index, bigint over serial, timestamptz, etc.) qui pousse la qualité des nouvelles migrations sans effort supplémentaire.
- Comments PR auto via `sbdchd/squawk-action@v2` (input `upload-to-github` par défaut `true`) — feedback contextualisé sur la ligne fautive.
- Diff net : **+32 / -79 lignes en `ci.yml`** — gate plus léger et plus lisible.

### Risques / mitigations

- **Squawk OSS upstream est tier-1 mais externe** → on pin la version (`version: "2.52.1"` dans l'action input + dans `.squawk.toml` references). Bump explicite, jamais `latest`.
- **Squawk hard-error si tous les fichiers explicites sont exclus par `excluded_paths`** ("Failed to find files for provided patterns"). Mitigation : **defense-in-depth** dans le workflow shell — pré-filtre `.down.sql` avant `files:` input. Si la liste résultante est vide, on skip le step squawk via `if:`.
- **Adoption par autres PRs en cours** : 7 PRs ouverts touchent `backend/supabase/migrations/*`. Après merge de cette ADR + PR monorepo, ils doivent rebase. Coût de coordination faible.

### Follow-ups (post-merge)

- **Symétrie pre-commit local** (`.husky/pre-commit`) : optionnel. Pourrait fail-fast au commit local. Pas dans le scope de cette ADR — squawk-cli a un install platform-binary délicat à invoquer depuis npx. À traiter si signal de friction.
- **Wrapper SARIF** : squawk n'émet pas SARIF nativement (reporters : tty/gcc/json/gitlab). Les violations apparaissent uniquement en commentaire PR, pas dans GitHub Security tab. Pas critique ; à reconsidérer si on adopte un workflow de revue centralisée.
- **Activation `require-table-schema`** (seule règle opt-in) : si on standardise sur des schemas explicites (`public.foo` vs `foo`) — à débattre séparément.

## Plan d'exécution (PR monorepo associé)

PR monorepo : [`feat/ci-squawk-migration-safety`](https://github.com/ak125/nestjs-remix-monorepo/pull/517) — un seul commit, scope minimal :

1. `+38 .squawk.toml` (nouveau).
2. `+32 / -79 .github/workflows/ci.yml` (réécriture du job `migration-safety`).
3. **Aucun changement aux 219 migrations existantes** ni aux 129 `-- APPROVED:` annotations (kept as prose).
4. **Aucun script `npm run sql:lint`** ajouté — squawk-cli a un binaire platform-specific compliqué à invoquer reliably depuis npx ; CI est la source canonique.

## Références

- [PR monorepo #517](https://github.com/ak125/nestjs-remix-monorepo/pull/517) — implementation
- [Squawk docs — `.squawk.toml` reference](https://github.com/sbdchd/squawk/blob/main/docs/docs/cli.md)
- [Squawk rules overview](https://squawkhq.com/docs/rules)
- [`sbdchd/squawk-action@v2`](https://github.com/sbdchd/squawk-action)
- Précédent : [[ADR-049-db-governance-canon-enforcement]] — template DB governance
- Incident : PR #514 false positive (commit pre-fix `2079d1e5`, fix-bricolage commit on main `8bf0c037`)
- Canon référencés : `feedback_no_bricolage_escalate_to_industry_standard`, `feedback_no_bricolage_clean_layer`, `feedback_pr_scope_recovery_vs_platform`
