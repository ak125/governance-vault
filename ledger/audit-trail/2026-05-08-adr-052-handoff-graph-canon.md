---
title: "ADR-052 handoff graph canon hoist + R6→R1 amendement — session shipped 2026-05-08"
date: 2026-05-08
type: session-trail
related_chantier: SEO
related_adr: ["ADR-052"]
related_moc: ["MOC-Decisions"]
related_prs:
  - "ak125/governance-vault#241"
  - "ak125/nestjs-remix-monorepo#405"
status: shipped
session_closed_at: 2026-05-08
---

# ADR-052 — handoff graph canon hoist + R6→R1 amendement

> **Statut** : shipped 2026-05-08 — vault PR #241 + monorepo PR #405 ouvertes.
> ADR-052 status `proposed` à promouvoir `accepted` post-merge code.

## Synthèse

Migration de la matrice de maillage inter-rôles depuis le registre backend
ad-hoc (`ALLOWED_LINKS` dans `backend/src/modules/seo/types/page-role.types.ts`)
vers un **mirror typé** du canon markdown (`@repo/seo-roles/handoff-graph.ts`).
Backend devient consommateur via `isHandoffAllowed()` ; rendu effectif via
`isRenderableLinkAllowed()` qui combine handoff conceptuel + surface routable.

En effet de bord transverse, **9 rôles sur 10** voient leur matrice alignée
au canon. Côté R6 spécifiquement : gain R1 + R3 au rendu public ; gain R5
uniquement en handoff conceptuel (filtré au rendu, ADR-027 sunset autonome).

## Drivers empiriques (audit codebase 2026-05-08)

1. **Drift backend `ALLOWED_LINKS` vs canon `handoff_targets`** sur 9/10
   rôles. R6_GUIDE_ACHAT n'autorisait que `[R4, R2]` côté backend alors que
   le canon spécifie `[R2, R3, R5, R4]`.
2. **Trou empirique du canon lui-même** : R1 absent de
   `R6_GUIDE_ACHAT.handoff_targets` malgré la mission planner.md
   « identifier la bonne pièce » + asymétrie R0/R2/R7/R8 (tous listent R1).
3. **Bug latent backend** : `pageRoleToRoleId(PageRole.R3_BLOG)` default
   retournait `RoleId.R3_GUIDE` déprécié (handoffs vides) au lieu de
   `R3_CONSEILS` canon vivant. Sans ce fix, `isLinkAllowed(R6, R3_BLOG)`
   restait `false` même après amendement canon.

## Itérations plan (7 cycles utilisateur critique)

| Version | Critique utilisateur | Correction |
|---|---|---|
| v1 | Invariant Zod `handoff ∩ forbidden = ∅` faux conceptuellement | Suppression — axes orthogonaux |
| v1 | Hoist dans `seo-role-contracts` (mauvais package) | Migration vers `seo-roles` (identité) |
| v1 | Inventer `allowed_target_roles` parallèle au canon | Réutiliser `handoff_targets` markdown existant |
| v1 | Fallback runtime r5 = bricolage | Scope retiré entièrement |
| v2 | Question R1 ∈ R6 mal cadrée | Auto-tranché sur preuve empirique |
| v3 | Severity hard/soft + Counter.inc<1µs trop précis | Formulation prudente |
| v4 | "0 ms latence" overclaim + log grep décisionnel | "incrément mémoire sync" + métrique Prometheus/OTel |
| v5 | severity 3-niveaux contredit hard/soft | Retrait label `severity`, dérivation Grafana |
| v5.2 | 3 angles morts (R3_BLOG default, 2 services, prom-client absent) | Errata explicite : fix R3_BLOG, chain v9 conditionnel, log Loki + in-memory |

## Livrables

### Canon `@repo/seo-roles@0.5.0` (mirror typé)
- `packages/seo-roles/src/handoff-graph.ts` — `ROLE_HANDOFF_GRAPH` (12 RoleId entries),
  `ROLE_HANDOFF_GRAPH_VERSION="1.0.0"`, `getHandoffTargets`, `isHandoffAllowed`.
- `packages/seo-roles/src/__tests__/handoff-graph.test.ts` — **12/12 tests verts** :
  exhaustivité, pas de self-loop, R6 amendement, R6_SUPPORT vide, golden parser
  set-equality vs `role-matrix.md`.
- `packages/seo-roles/src/index.ts` — re-export PR-0E surface.

### Canon markdown amendé
- `.spec/00-canon/role-matrix.md:170` — ajout `{target: R1, condition: "besoin = verifier compatibilite avant commande"}` aux R6_GUIDE_ACHAT.handoff_targets.

### Backend dérivation
- `backend/src/modules/seo/types/page-role.types.ts` — `ALLOWED_LINKS` supprimé,
  `isLinkAllowed` réécrit (consulte canon), `isRenderableLinkAllowed` ajouté,
  `pageRoleToRoleId(R3_BLOG)` default fix R3_GUIDE → R3_CONSEILS.
- `backend/src/modules/seo/routable-surface-registry.ts` — créé. `ROUTABLE_SURFACES`
  exclut R5 (ADR-027), R3_GUIDE (déprécié), R6_SUPPORT (info pure), rôles non-page.
- `backend/src/modules/seo/services/seo-handoff-metrics.service.ts` — créé. Compteur
  in-memory `Map<string, number>` aligné `MetricsService` legacy (pas de prom-client).
- `backend/src/modules/seo/internal-linking.service.ts` — `validateLinkByRole()` consomme
  `isRenderableLinkAllowed`, log structuré + métrique `seo_handoff_filtered`.
- `backend/src/modules/seo/seo.module.ts` — `ALLOWED_LINKS` retiré exports,
  `isRenderableLinkAllowed`+`hasRoutableSurface` exportés, `SeoHandoffMetricsService`
  provider ajouté.

### Tests régression
- `backend/tests/unit/page-role-mapping.test.ts` — créé, couverture exhaustive mapping.
- `backend/tests/unit/page-role-links.test.ts` — réécrit, matrice complète vs canon.

## Verdict empirique CI local

- Canon `npm run build && npm test` → 12/12 handoff-graph + 232 total tests verts.
- Backend `tsc --noEmit` → exit 0 (NODE_OPTIONS=--max-old-space-size=6144).
- Backend Jest : non lancé localement, validation CI.

## Hors scope (volontaire — documenté ADR-052)

- **Chain v9 service** `seo-internal-linking.service.ts` : absent de `main`
  (introduit dans branche seo-v9-pr2c ultérieure). Modification reportée
  à intégration cascade v9 ou PR follow-up.
- **r5 contract** : orthogonal au link graph, follow-up owner R5.
- **Frontend identité drift** `'R6'`/`'R6_GUIDE'` : bloqué migration DB
  historique (précondition R6 cascade ADR-051 PR-E).
- **Migration Prometheus** : prom-client absent du backend, follow-up
  infra séparée (lockfile update + `/metrics` endpoint).
- **Drift sémantique r6.ts contract** `semantic_intents`. Bug réel détecté
  pendant audit, follow-up séparé.

## Forward-compatibility

Aligné avec **PR-A.bis future** (`packages/seo-roles/src/intents.ts:18-19`
mentionne « future canon.json build pipeline derives this matrix from prompts »).
Quand PR-A.bis livrera, `handoff-graph.ts` deviendra à son tour dérivé du
`canon.json`. Cette PR pose les rails (TS canon backend-consumable + mirror
typé du markdown SoT) sans précéder la décision SoT globale.

## Disciplines observabilité retenues (extensions futures)

1. Logger structuré chemin réponse SEO → `setImmediate(() => void emit(...))`.
2. Sampling déterministe `hash(source:target:entityId) % 100 < rate`, jamais
   `Math.random()`.
3. Classification divergence shadow/diff ≥ 3 niveaux (`none|soft|hard`) — n'applique
   pas au counter événementiel actuel (2 niveaux suffisent).
4. Décisions SEO empiriques basées sur métrique Prometheus/OTel agrégeable, jamais
   sur grep Loki.
5. Helper canonical/URL **ne jamais** utiliser `decodeURI()` sur path (risque sémantique
   sur `%2F`).

## Branche & worktree

- Worktree : `/tmp/wt-seo-roles-handoff` (créé depuis `main` via `git worktree add`).
- Branche monorepo : `feat/seo-roles-handoff-graph` (depuis `main`, non depuis
  cascade seo-v9 — `feedback_branch_scope_discipline`).
- Branche vault : `feat/adr-052-handoff-graph-canon` (depuis `main`).
- Stash original `feat/seo-v9-pr5-gamme-shadow` : `wip CLAUDE.md before seo-roles-handoff-graph branch`
  (récupérable via `git stash pop` sur la branche d'origine).

## Suite (post-merge)

1. Promote ADR-052 status `proposed` → `accepted` post-merge monorepo.
2. Mémoire à sauvegarder `seo-handoff-graph-canon-shipped-20260508.md` + entrée MEMORY.md.
3. Smoke DEV preprod : `curl -X POST .../api/seo/validate-links` avec R6 → R1/R3/R5.
4. Monitoring 7j métrique `seo_handoff_filtered` + log Loki.
5. Follow-up séparés : chain v9 service, Prometheus migration, r5 contract, frontend drift.
