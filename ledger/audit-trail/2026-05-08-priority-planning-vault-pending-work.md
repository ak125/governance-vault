---
title: "Priority planning vault pending work — 27 vault PRs + 11 ADRs proposed + ADR-051 collision résolue"
date: 2026-05-08
type: session-trail
related_chantier: D
related_adr: ["ADR-051", "ADR-052"]
related_moc: ["MOC-Decisions", "MOC-AuditTrail"]
related_prs:
  - "ak125/governance-vault#211"
  - "ak125/governance-vault#212"
  - "ak125/governance-vault#213"
  - "ak125/governance-vault#214"
---

# Planning prioritaire vault — work pending discovery 2026-05-08

## Contexte

Session déclenchée par demande utilisateur "il y a beaucoup de travail en attente dans le vault, vérifier". Discovery parallèle vault + monorepo + ADR statuses → **27 PRs vault open**, **30 PRs monorepo open**, **11 ADRs en `proposed`**.

Découverte critique : **collision ADR-051** entre PR #211 (perf-sprint frontend bundle budget enforcement, créée 22:00:14Z) et PR #212 (mon SQL role canon deprecation, créée plus tard dans la même session). Antériorité tranchée pour PR #211 → mon ADR renumber en ADR-052.

## P0 — Collision ADR-051 résolue (✅ exécuté)

- PR #212 fermée avec commentaire de redirect vers PR #214.
- ADR-051 → ADR-052 rename : `git mv ledger/decisions/adr/ADR-051-sql-role-canon-deprecation.md ledger/decisions/adr/ADR-052-sql-role-canon-deprecation.md` + `sed` frontmatter `id: ADR-051` → `id: ADR-052` + title H1 + MOC-Decisions entry.
- PR #214 ouverte (`feat/adr-052-sql-role-canon-deprecation`), auto-merge SQUASH armé.
- PR #213 (audit-trail R6 cascade) force-pushée avec références ADR-051 → ADR-052.

**Workaround technique** : worktree isolé `/tmp/vault-adr052-rename` car parallel session interférait avec mes branches (collision déjà documentée dans `feedback_git_worktree_for_concurrent_governance.md`). Push depuis main vault dir nécessaire pour contourner bug script `_scripts/check-signatures.sh:23` qui rejette les worktrees (`! -d "$VAULT_PATH/.git"` → fail car `.git` est un fichier dans worktree). Fix existant en attente de merge : PR vault #149.

## P1 — ADRs `proposed` shipped à statuer (11 ADRs)

| ADR | Date | Verdict recommandé |
|---|---|---|
| ADR-024 R1 cache | 2026-04-27 | Vérifier shipped → promote |
| ADR-029 RAG v2.1 | 2026-04-25 | P1 LIVE → promote |
| ADR-031 four-layer | 2026-04-28 | Wiki/raw shipped → promote |
| ADR-032 diag/maintenance | 2026-04-29 | Vérifier puis promote |
| ADR-033 wiki gamme diagnostic | 2026-04-29 | Wave 2 closed → promote |
| ADR-034 AI-COS contract | 2026-04-30 | LIVE → promote |
| ADR-035 diag source trust | 2026-05-02 | Vérifier shipped |
| ADR-036 marketing operating | 2026-04-30 | Vérifier shipped |
| ADR-043 Plan F DevSecOps | 2026-05-06 | Sprint 1 partial → garder proposed |
| ADR-044 SEO Strategy 2026 | 2026-05-07 | En cours → garder proposed |
| ADR-045 SEO Monitoring V0 | 2026-05-07 | V0.A shipped → promote |

Application `feedback_canon_rule_live_iff_adr_accepted.md` : tout chantier LIVE doit avoir son ADR.status=accepted.

## P2 — Vault PRs anciennes à triager (24 PRs >7 jours)

- **Knowledge / audit-trail dormants** : ~14 PRs (#9, #13, #22, #29, #40, #59, #64, #65, #70, #72, #75, #88, #92, #93, #110, #114, #116, #122) — triage relevance puis merge ou close.
- **Bug fixes scripts critiques** : #149 (worktree script fix — débloque les sessions futures de bug `_scripts/check-signatures.sh:23`), #136 (audit baseline pattern) — priorité haute.
- **Knowledge cross-links** : #151 — review + merge.
- **Session audits** : #131, #173 — triage age.

## P3 — Cascade R6 canon en cours (5 PRs auto-merge armed)

| PR | Status | Note |
|---|---|---|
| monorepo #385 | OPEN auto-merge | PR-A + PR-C squashed, BEHIND main |
| monorepo #386 | OPEN auto-merge | PR-B skill split |
| monorepo #392 | MERGED dans branche PR-A | Cascade naturelle |
| vault #214 | OPEN auto-merge | ADR-052 (renamed from #212) |
| vault #213 | OPEN auto-merge | Audit-trail R6 cascade (force-pushed avec ADR-052 refs) |

## P4 — Concurrent perf-sprint cascade (monorepo, ~6 PRs)

PRs #387, #391, #393, #394, #395, #396 — session parallèle propriétaire (perf-sprint). Ne pas interférer. Frontend bundle budget signalé dans ADR-051 vault (PR #211).

## P5 — R6 follow-ups déférés (post empirical signal)

- **PR-E** frontend `PageRole.R6_SUPPORT="R6"` → `"R6_SUPPORT"` : migration DB requise (audit Supabase MCP colonnes role TEXT historiques)
- **PR-F** purge `LEGACY_ROLE_ALIASES` : précondition `seo_role_legacy_resolution_total = 0/7j` sur tous consommateurs majeurs instrumentés
- **ADR-052 promotion** `proposed → accepted` : review humaine post-merge PR #214

## P6 — Monorepo PRs anciennes (~15 PRs >5 jours)

- ADR-027/044 follow-ups R3 deprecation : #341, #336, #335
- seo-roles refactors antérieurs au cascade R6 : #315, #314
- CI fixes : #290, #293
- Dependabot : #280, #300, #301 (auto-mergent normalement)

## Séquençage immédiat recommandé

**Jour 1 (2026-05-08)** :
1. ✅ Collision ADR-051 résolue
2. Surveiller auto-merge des 5 PRs cascade R6
3. Merge PR vault #149 (worktree script fix — débloque sessions futures)

**Jour 2-3** :
4. Triage des 14 PRs vault knowledge anciennes
5. Promote ADR-031, ADR-033, ADR-034, ADR-045 (LIVE shipped) → accepted

**Jour 4-7** :
6. Audit DB Supabase MCP pour PR-E (compter colonnes stockant `"R6"`/`"R6_GUIDE"` historiques)
7. Bootstrap PR-A consumer instrumentation (backend NestJS + frontend Remix metrics endpoint)

**Semaine 2 (J+7)** :
8. PR-F precondition check : `seo_role_legacy_resolution_total = 0/7j` mesurable

## Mémoires utilisées

- `feedback_git_worktree_for_concurrent_governance.md` — worktree isolé
- `feedback_canon_rule_live_iff_adr_accepted.md` — ADR shipped → accepted
- `feedback_progress_dashboard_required.md` — auto-mode dashboard
- `feedback_check_merged_prs_before_planning.md` — gh pr list avant scope
- `feedback_decision_must_be_signal_proven_not_intuited.md` — PR-F empirical signal
- `r6-canon-cascade-shipped-20260508.md` — contexte session précédente
