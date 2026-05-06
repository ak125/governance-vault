---
title: "Session 2026-05-06 — R3 cleanup grid livrée (P0/P1 + P3 Phase 1)"
date: 2026-05-06
type: session-trail
related_chantier: D
related_adr: ["ADR-040", "ADR-044"]
related_prs:
  - "ak125/nestjs-remix-monorepo#330"
  - "ak125/nestjs-remix-monorepo#335"
  - "ak125/nestjs-remix-monorepo#336"
  - "ak125/governance-vault#173"
status: closed
session_closed_at: 2026-05-06
---

# 2026-05-06 — R3 cleanup grid livrée (P0/P1 + P3 Phase 1)

> **Chantier de rattachement** : `D` (SEO indexation / crawl budget).
> Étend l'application opérationnelle d'ADR-040 (canon SEO R0..R8 socle
> TS-side, voir `2026-05-05-seo-canon-r0-r8-stack-shipped.md`) à 3
> surfaces où subsistait du shadow legacy `R3_BLOG` / `R3_guide` :
> dashboards admin, docs SEO batch, triplet backend `R3GuideController`.
> Aucune nouvelle décision architecturale — application du canon déjà acté.

## Contexte

Le canon `@repo/seo-roles@0.4.0` classifie le contenu pédagogique
conseil/how-to comme `R3_CONSEILS` (et le contenu pré-achat comme
`R6_GUIDE_ACHAT`). L'audit utilisateur début de session a recensé une
grille en 5 priorités du shadow legacy `R3_BLOG` / `R3_guide` :

| Priorité | Description |
|----------|-------------|
| P0 | Labels DB legacy affichés dans l'UI admin (`admin.rag.cockpit.tsx` etc.) |
| P1 | Docs / skills SEO batch utilisant "R3 Blog" / `R3_BLOG_HUB` comme racine |
| P2 | Helper `normalizeRoleLabel` frontend |
| P3 | Rename backend `R3GuideController/Service/interfaces` → `R3Conseils*` |
| P4 | Drop alias HTTP `/api/r3-guide/:pg_alias` |

P2 a été refusé d'emblée : `@repo/seo-roles@0.4.0` exporte déjà
`getRoleDisplayLabel`, `getRoleShortLabel`, `normalizeRoleId`,
`LEGACY_ROLE_ALIASES`, `PAGE_TYPE_TO_ROLE` — inventer un helper local
violerait `feedback_verify_existing_first.md`.

P3 ne pouvant pas être livré en une seule PR (route `/api/r3-guide/:pg_alias`
consommée par le frontend SSR Remix), formalisé en plan 3 phases per
`feedback_deprecate_before_rename_before_drop.md`.

## Livrables (3 PRs monorepo + 1 PR vault)

### PR #330 — P0 admin labels (mergée 15:36 UTC)

`fix(admin): unify role labels via @repo/seo-roles in 3 admin routes`

3 routes admin RAG (`admin.rag.cockpit.tsx`, `admin.content-refresh.tsx`,
`admin.rag.pipeline.tsx`) maintenaient des maps locales `PAGE_TYPE_LABELS`
/ `PAGE_TYPE_SHORT` qui shadowaient le canon (alors que les 3 importaient
déjà `getRoleDisplayLabel`). Labels divergents entre routes ("Conseils DIY"
vs "R3 Conseils" vs "R3 Conseils" pour `R3_conseils` ; "Guide How-To" vs
"R3 Guide How-To" vs "R3 Guide" pour `R3_guide_howto`).

Changements :
- Drop des 3 maps locales (legacy `R3_guide` est résolu par
  `LEGACY_ROLE_ALIASES` du canon, pas par hardcode local).
- Routage display via `getRoleDisplayLabel` / `getRoleShortLabel`.
- `PAGE_TYPE_OPTIONS` (dropdown filter) re-dérivé via canon
  (`Object.keys(PAGE_TYPE_TO_ROLE)`).
- Comparaisons `i.page_type === "R1_pieces"` remplacées par
  `pageTypeToRoleId(i.page_type) === RoleId.R1_ROUTER`.
- 10 cas de régression ajoutés à `packages/seo-roles/src/__tests__/display.test.ts`
  pour asservir le contrat `LEGACY_ROLE_ALIASES` / `PAGE_TYPE_TO_ROLE` /
  `CANONICAL_DISPLAY_LABELS`.

Behavior change signalé : `R6` bare (rare, ambigu) rend désormais
`"R6 · Legacy à qualifier"` au lieu d'une chaîne brute — surface la
dette plutôt que la masquer.

Régression CWV documentée : bundle +7KB (~0.6% sur threshold 1.28MB),
introduite par les imports `RoleId` enum + `pageTypeToRoleId` runtime.
Acceptée à l'admin-merge — candidat de cleanup follow-up : revert des
2 comparaisons sur input-context avec eslint-disable inline documenté
(la règle eslint elle-même autorise les literals legacy en INPUT).

### PR #335 — P3 Phase 1 backend `@deprecated` (open)

`chore(blog): mark R3GuideController/Service/interfaces @deprecated (PR-1, ADR-044)`

4 fichiers `backend/src/modules/blog` annotés `@deprecated` JSDoc :
- `controllers/r3-guide.controller.ts`
- `services/r3-guide.service.ts`
- `interfaces/r3-guide.interfaces.ts`
- `blog.module.ts` (commentaires inline)

**Aucun changement de comportement, aucun rename de fichier, aucune
modification de route.** Effet : IDE/LSP affiche le hint `@deprecated`
à tout consommateur de ces symboles, signalant la migration à venir.

### PR #336 — P1 docs SEO batch (open)

`docs(seo-batch): drop legacy R3_BLOG / "R3 Blog" labels in canon-output contexts`

5 fichiers `workspaces/seo-batch/.claude/` :
- `skills/seo-content-architect/SKILL.md`
- `skills/seo-content-architect/references/rag-verification.md`
- `agents/blog-hub-planner.md` (`R3_BLOG_HUB` inventé → `R3_CONSEILS` canon)
- `skills/rag-ops/references/intent-patterns.md`
- `skills/content-audit/SKILL.md` (detection `PageRole.R3_CONSEILS` primary,
  legacy `PageRole.R3_BLOG` mention déclaré normalisé via
  `LEGACY_ROLE_ALIASES`)

### Vault PR #173 — ADR-044 + audit trail (open)

`proposal(adr-044): R3GuideController/Service backend rename → R3Conseils*`

ADR-044 documente le plan 3-phases de P3 :

| Phase | Date | Scope |
|-------|------|-------|
| 1 ✅ | 2026-05-06 | `@deprecated` JSDoc IN-PLACE (PR #335) |
| 2 | 2026-06-05 (T0+30j) | Créer `R3ConseilsController @Controller('api/r3-conseils')` délégant à `R3GuideService`, migrer frontend (`blog-pieces-auto.conseils.$pg_alias.tsx`), garder `/api/r3-guide` alias backward-compat |
| 3 | 2026-07-05 (T0+60j) | Drop l'alias quand `/api/r3-guide` reçoit 0 requêtes / 7j consécutifs |

Drive-by fix `_scripts/check-signatures.sh` worktree-compat (`-d` →
`-e` pour reconnaître les worktrees où `.git` est un fichier gitlink).

## Décisions tracées

- **P2 helper local refusé** par discipline canon. `@repo/seo-roles`
  expose déjà tous les helpers nécessaires.
- **P3 split en 3 phases** plutôt que rename direct. Justification :
  route consommée par frontend SSR + canon `feedback_deprecate_before_rename_before_drop`.
- **Renumber forcé ADR-043 → ADR-044** : pendant la session, vault PR
  #174 (Plan F DevSecOps) a aussi pris ADR-043 et a été mergée sur
  main avant le rebase de cette PR. Mon ADR a été décalé en ADR-044.
  Renumber propagé dans le file rename, frontmatter, header, MOC row,
  PR title/body, et JSDoc refs des 4 fichiers backend de PR #335.
- **Régression CWV PR #330 acceptée** à l'admin-merge (0.6% bundle).
  Cleanup follow-up identifié mais hors scope today (revert comparisons
  `pageTypeToRoleId` + eslint-disable INPUT-context inline).

## Restant

| Item | Trigger | Bloqué par |
|------|---------|-----------|
| P3 Phase 2 (rename + cohabitation) | 2026-06-05 | Calendrier (30j observation `@deprecated`) |
| P3 Phase 3 (drop alias) | 2026-07-05 + condition `0 req /7d` | P3 Phase 2 + métriques HTTP |
| P4 (drop `/api/r3-guide`) | Bloqué par P3 Phase 3 | — |
| Cleanup CWV +7KB de PR #330 | optionnel | aucun |

## Refs

- ADR-040 — Canon SEO Roles côté TS, single source of truth
- ADR-044 (cette PR) — Plan 3 phases R3GuideController rename
- `feedback_deprecate_before_rename_before_drop` (AI-COS memory)
- `feedback_verify_existing_first` (AI-COS memory)
- `feedback_git_worktree_for_concurrent_governance` (AI-COS memory) —
  appliqué à partir de PR #335 après collision concurrent agent dans
  PR #330 (worktree obligatoire)
- `2026-05-05-seo-canon-r0-r8-stack-shipped.md` (audit-trail) — socle
  canon dont cette session étend l'application
- `2026-05-06-r1-drift-canon-shipped.md` (audit-trail) — autre extension
  parallèle du même canon
