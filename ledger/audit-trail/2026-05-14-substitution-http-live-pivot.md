---
date: 2026-05-14
type: audit-trail
related: [ADR-048, ADR-058, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-14 — Substitution module `http_live` retention pivot (canari PR #466 closed)

## What

Le module `backend/src/modules/substitution/` du monorepo `nestjs-remix-monorepo` change de verdict cleanup :

- **Avant** (triage automatique) : `dead_subtree` (candidat `git rm` Step B de [`audit/cleanup-plan-by-domain.md`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/audit/cleanup-plan-by-domain.md)).
- **Après** (post-incident 2026-05-13) : `http_live` — **retention permanente requise**.

## Why

Le 2026-05-13, la PR #466 (canari `substitution` drop) a été closed avant merge. La review auto a détecté que `@Controller('api/substitution') @Get('check')` est consommé en runtime par `frontend/app/routes/pieces.$slug.tsx:206` via un `fetch('${API_URL}/api/substitution/check?...')`. TypeScript ne voit pas cet edge HTTP (pas d'import statique cross-package).

Sans ce check, le drop aurait cassé `/pieces/:slug` en prod silencieusement : 404 sur chaque appel `/api/substitution/check`, fallback `.catch(() => null)` côté frontend aurait mangé le signal sans alarme.

Le triage initial `audit/runtime-entrypoints.json#nestjs_unreachable_modules` qui plaçait substitution en candidat `dead_subtree` était **techniquement correct** (NestJS DI ne le voit pas) **mais incomplet** : le scope `string_refs` était limité à `backend/src + .github + scripts + supabase/migrations`, **`frontend/app` exclu**.

## What was done

### Méthodologie corrigée (PR #469 mergée 2026-05-13)

- `scripts/cleanup/validate-before-delete.sh` section 4b **HTTP-route-callers** :
  - Pour chaque fichier sous un sous-arbre candidat, extraction des `@Controller('<path>')` du sous-arbre.
  - Grep `-F` (fixed) du `<path>` à travers `frontend/app`, `packages`, `scripts`, `e2e`, `tests`.
  - Hit → report `[HTTP-ROUTE-CALLER]` et blocage du `git rm`.
- Règle dérivée canonique : **tout sous-arbre contenant un `@Controller(...)` est `http_live` par défaut** jusqu'à preuve grep contraire sur l'intégralité des workspaces.

### Documentation canonique (PR #489 monorepo, 2026-05-14)

- `audit/unreachable-modules/substitution.md` (new) — triage retention aligné sur le pattern `upload.md` (PR #476) et `agentic-engine.md` (PR #477).
- `audit/cleanup-plan-by-domain.md` Step B — état post-arbitrage : 3 modules retention documentée (`substitution`, `upload`, `agentic-engine`), seul `mcp-validation` reste candidat `dead_subtree` plausible.
- `.claude/knowledge/modules/substitution.md` Gotchas + Références — gotcha `http_live` + règle dérivée.

### Branche locale obsolète (PR #466 invalidée)

La branche locale `chore/pr-3b-1-substitution-drop-clean` (commits `e32f6163` drop -1427L + `675e3e7e` doc triage) contient des changements invalidés par le pivot. Force-delete prévu post-merge PR #489.

### Mémoire stale

`/home/deploy/.claude/projects/-opt-automecanik-app/memory/cleanup-monorepo-roadmap-20260511.md` marquait PR-3b-1 comme « shipped » alors que réalité = drop invalidé, branche locale orpheline. Refresh prévu post-merge PR #489.

## Decision rationale

- **No-bricolage** : pas de cherry-pick partiel des commits invalidés, force-delete branche orpheline.
- **Robust** : check méthodologique `[HTTP-ROUTE-CALLER]` ajouté à `validate-before-delete.sh` (PR #469) protège mécaniquement contre toute récidive.
- **Modern** : alignement sur pattern `audit/unreachable-modules/<module>.md` par module retention (PR #476 / #477 / #489).
- **Best-in-class** : 3 surfaces canon mises à jour cohérentes (audit/, knowledge/, cleanup-plan/), audit-trail vault SoT par ADR-054.

## References

- **Incidents/PRs** :
  - [PR #466 closed](https://github.com/ak125/nestjs-remix-monorepo/pull/466) — canari échoué (origine du pivot).
  - [PR #469](https://github.com/ak125/nestjs-remix-monorepo/pull/469) — `validate-before-delete.sh` HTTP-route-caller aware (prereq-2).
  - [PR #476](https://github.com/ak125/nestjs-remix-monorepo/pull/476) — `upload` retention (option B, pattern triage doc).
  - [PR #477](https://github.com/ak125/nestjs-remix-monorepo/pull/477) — `agentic-engine` retention (option B).
  - [PR #489](https://github.com/ak125/nestjs-remix-monorepo/pull/489) — `substitution` pivot doc canonique (cet audit-trail couvre la décision).
- **Code** :
  - Caller frontend : `frontend/app/routes/pieces.$slug.tsx:206` (`fetch /api/substitution/check`).
  - Check méthodologique : `scripts/cleanup/validate-before-delete.sh` section 4b.
- **Canon** :
  - [ADR-048](../decisions/adr/ADR-048-canon-enforcement-coverage.md) — canon enforcement coverage (le pivot évite une régression dans la baseline cleanup et durcit le check `validate-before-delete.sh`).
  - [ADR-058](../decisions/adr/ADR-058-repository-control-plane.md) — repository control plane (les `audit/` artifacts mis à jour sont projetés par le registry).
