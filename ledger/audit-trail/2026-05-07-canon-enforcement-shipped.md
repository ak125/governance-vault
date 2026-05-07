---
type: audit-trail
date: 2026-05-07
session_id: canon-enforcement-shipped-2026-05-07
domain: canon-enforcement
related_adr: ["ADR-048", "ADR-049"]
status: shipped
---

# Canon enforcement coverage — sprints 1+2+3 + DB-2 sub-axe 2 SHIPPED

> Session day-long 2026-05-07. Refondation MOC vault + ouverture chantier
> canon enforcement ([[ADR-048-canon-enforcement-coverage]]) + chantier DB
> ([[ADR-049-db-governance-canon-enforcement]]) + livraison incrémentale
> sprints 1, 2, 3 ADR-048 + sprint DB-1 et DB-2 sub-axe 2 ADR-049.

## 1. Synthèse couverture canon (post-session)

| Domaine | Total | Enforced | % |
|---|---|---|---|
| `.spec/00-canon/` racine | 19 | 6 | **32%** |
| `.spec/00-canon/db-governance/` | 16 | 1 | **6%** |
| **Total** | **35** | **7** | **20.0%** |

**Commande re-runnable** :

```bash
python3 /opt/automecanik/governance-vault/_scripts/check-canon-freshness.py --json \
  | jq '.summary, .stats'
```

## 2. ADRs ouverts + acceptés aujourd'hui

### [[ADR-048-canon-enforcement-coverage]] — Option D hybrid 3 sprints
- **Status** : accepted 2026-05-07
- **Sprint 1 LIVE** : REG-002 baseline + check-canon-freshness.py
- **Sprint 2 LIVE** : 4 P0/P1 detectors (architecture, repo-map, prompt-registry, phase2-canon)
- **Sprint 3 LIVE** : check-canon-cross-repo.py (vault → monorepo dead-refs)
- **C5 amendement** : intégration db_classification (REG-002 v1.1.0+)

### [[ADR-049-db-governance-canon-enforcement]] — Option DB-D hybrid 4 sub-axes
- **Status** : accepted 2026-05-07
- **Sprint DB-1 LIVE** : extension REG-002 db_classification column
- **Sprint DB-2 sub-axe 2 LIVE (DB-P0)** : SQL rule R2 index justification check
- **Reste** : sub-axe 1 (domain-map auto-gen), sub-axe 3 (role-migration-registry Zod), sub-axe 4 (Supabase MCP — différé)

## 3. PRs livrées

### Vault (`ak125/governance-vault`) — 21 PRs MERGED

| PR | Sujet |
|---|---|
| #185 | refactor MOC-Governance pure-nav + drift fix |
| #186 | docs(moc) clarify SoT semantics + canon glossary |
| #188 | feat(scripts) check-moc-integrity (6 checks) |
| #189 | refactor MOC-Decisions ADR-031 insertion |
| #190 | chore(claude-md) footer date refresh |
| #191 | feat(adr-048) canon enforcement coverage |
| #194 | feat(reg-002) canon files registry baseline |
| #195 | feat(scripts) check-canon-freshness |
| #196 | feat(adr-049) DB governance canon enforcement |
| #197-201 | sprint 2 ADR-048 P0/P1 detectors propagation REG-002 |
| #202 | feat(scripts) check-canon-cross-repo |
| #203-206 | REG-002 v1.1.0→v1.4.0 (db_classification + sprint 2 rows) |
| #207 | REG-002 v1.5.0 sql-governance-rules.md prose-only→enforced |

### Monorepo (`ak125/nestjs-remix-monorepo`) — 7 PRs MERGED

| PR | Sujet |
|---|---|
| #358 | feat(spec-canon) check-architecture-drift (P0) |
| #361 | feat(spec-canon) check-repo-map-drift (P0) |
| #362 | feat(ast-grep) no-anthropic-direct-import-in-scripts |
| #363 | feat(seo-batch) AGENTS.md ownership canon |
| #365 | feat(spec-canon) check-prompt-registry-drift |
| #367 | feat(spec-canon) check-phase2-canon-enum-drift |
| #374 | feat(spec-canon) sql rule R2 check (ADR-049 sub-axe 2 DB-P0) |

## 4. Patterns canon adoptés (pour reproductibilité)

### Detector script Python — shape standardisé

- Sortie JSON canonique : `{check, findings[], summary{error,warning,info}, stats{}}`
- Flags : `--json`, `--strict`, `--since=<git-ref>` (où applicable)
- Mode warn-only initial avec escalade J+30 documentée
- Severity: `error` mappé sur `::error::` annotations CI, `warning` sur `::warning::`
- Pas de `|| true` swallow, pas de mock fallback

### Workflow CI standardisé

- `set -euo pipefail`
- JSON shape validation step distincte
- `timeout-minutes` job
- `try/catch` sur `actions/github-script` (pas de fail PR si comment-step casse)
- Permissions explicites `contents: read`, `pull-requests: write`
- Triggers `paths:` ciblés sur source + script + workflow

### REG-002 versioning (incremental SemVer)

- v1.0.0 : 35 fichiers baseline
- v1.1.0 : column `db_classification` ajoutée
- v1.2.0-v1.4.0 : rows `enforced_by` mises à jour par sprint
- v1.5.0 : sql-governance-rules.md → enforced

## 5. Liens externes / commits

- Vault main HEAD : voir `git log --oneline -25` sur `ak125/governance-vault`
- Monorepo main HEAD : voir `git log --oneline -10` sur `ak125/nestjs-remix-monorepo`
- Workflows actifs : 4 nouveaux `.github/workflows/spec-canon-*.yml`
- Scripts actifs vault : `check-canon-freshness.py`, `check-canon-cross-repo.py`,
  `check-moc-integrity.py` (intégrés à `weekly-lint.sh`, 11 checks total)

## 6. Triggers next-step (à surveiller)

- **2026-05-12** : éligibilité PR-3b (lint warn→error si `seo_role_normalization_failed_total=0/7d`)
- **2026-05-21** : deadline ADR-048 sprint suivant (cf. ADR-049 sub-axes 1+3)
- **Weekly Mon 02:00 UTC** : `vault-weekly-lint.yml` exécute les 11 checks et ouvre une issue si findings nouveaux

## 7. Mémoires Claude créées (pertinentes)

- `feedback_gh_pr_edit_body_graphql_deprecation.md` — `gh pr edit --body` silent-fail
- `feedback_design_pack_improves_existing_not_replaces.md` — design pack ne crée pas namespace parallèle
- (Confirmation patterns existants utilisés sans doublon : `vault-hooks-canonical-pattern.md`,
  `feedback_vault_self_review_before_admin_merge.md`, `feedback_check_merged_prs_before_planning.md`)

---

_Session classée. Prochains sprints (ADR-049 sub-axes 1/3) en attente de
trigger ou décision user._
