---
id: ADR-044
title: "R3GuideController/Service backend rename → R3Conseils* (deprecate-30d-then-rename)"
status: accepted
date: 2026-05-06
decision_date: 2026-05-06
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G3"]
related_incidents: []
related_adr: ["ADR-040"]
---

# ADR-044: Rename `R3GuideController/Service` → `R3Conseils*` (PR-1 deprecate, PR-2 rename, PR-3 drop)

## Contexte

Depuis `@repo/seo-roles@0.1.0` (PR #304, ADR-040), le canon SEO classifie le
contenu pédagogique conseil/how-to comme **`R3_CONSEILS`** (et non
`R3_GUIDE`, qui est marqué `DEPRECATED_OUTPUT_ROLES` côté canon TS).

Côté backend NestJS, trois symboles backend portent encore le nom legacy :

- `backend/src/modules/blog/controllers/r3-guide.controller.ts` —
  `@Controller('api/r3-guide')` exposant `GET /api/r3-guide/:pg_alias`
- `backend/src/modules/blog/services/r3-guide.service.ts` — orchestrateur
- `backend/src/modules/blog/interfaces/r3-guide.interfaces.ts` —
  `R3GuidePage`, `R3GuidePayload`

Ces symboles servent en réalité du contenu **R3_CONSEILS** canon : la route
Remix consommatrice est déjà nommée `blog-pieces-auto.conseils.$pg_alias.tsx`
et le validator backend `validateR3Conseils()` (`page-role-validator.service.ts`)
utilise déjà la nomenclature canon. La dette est uniquement dans le triplet
controller/service/interface du module `blog`.

L'objectif n'est pas critique (pas d'incident en cours, pas de risque de
sécurité), mais le mot `R3GuideController` brouille la lecture des nouveaux
contributeurs et entretient la confusion entre `R3_CONSEILS` (conseil/how-to,
canon) et `R3_GUIDE` (legacy déprécié, redirigé vers `R6_GUIDE_ACHAT` par
`LEGACY_ROLE_ALIASES`).

## Décision

Renommer le triplet backend en suivant le pattern canon de cet repo
(per `feedback_deprecate_before_rename_before_drop.md`) :

### Phase 1 — `deprecate IN-PLACE` (T0 = 2026-05-06)

PR-1 monorepo (livrée avec cette ADR) : annotations `@deprecated` JSDoc sur
`R3GuideController`, `R3GuideService`, `R3GuidePage`, et commentaires
explicatifs dans `blog.module.ts`. **Aucun rename de fichier, aucun
changement de comportement, aucun changement de route.** L'IDE/TypeScript
LSP affiche l'annotation à tout consommateur, signalant la migration à venir.

Fenêtre d'observation : **30 jours** (T0 → 2026-06-05) pour laisser le temps
aux contributeurs de remarquer l'annotation et soulever d'éventuels usages
externes non recensés (scripts de monitoring, dashboards externes,
intégrations, agents Paperclip).

### Phase 2 — `rename` (T0 + 30j = 2026-06-05)

PR-2 monorepo :

1. Créer `backend/src/modules/blog/controllers/r3-conseils.controller.ts` →
   `@Controller('api/r3-conseils')` qui **délègue** au `R3GuideService`
   existant (zero logic duplication).
2. Créer `backend/src/modules/blog/services/r3-conseils.service.ts` qui
   ré-exporte / délègue à `R3GuideService`.
3. Créer `backend/src/modules/blog/interfaces/r3-conseils.interfaces.ts`
   qui ré-exporte `R3GuidePage as R3ConseilsPage`, etc.
4. Enregistrer les 2 nouveaux controllers/services dans `blog.module.ts`
   à côté des anciens (cohabitation temporaire).
5. Migrer le frontend consommateur
   (`frontend/app/routes/blog-pieces-auto.conseils.$pg_alias.tsx:156`) vers
   `/api/r3-conseils/:pg_alias`.
6. Garder `/api/r3-guide/:pg_alias` actif comme alias backward-compat pour
   les consommateurs externes éventuels.

Fenêtre d'observation supplémentaire : **30 jours** (T0+30j → T0+60j) avec
métriques HTTP sur les 2 routes ; quand `/api/r3-guide/*` reçoit `0` requêtes
sur 7 jours consécutifs, on passe à Phase 3.

### Phase 3 — `drop` (T0 + 60j = 2026-07-05 si conditions réunies)

PR-3 monorepo : suppression complète des fichiers `r3-guide.*.ts` et de
leur enregistrement dans `blog.module.ts`. Supprime la route alias
`/api/r3-guide/:pg_alias`.

## Pourquoi 3 phases et pas un rename direct

- `feedback_deprecate_before_rename_before_drop.md` : pattern canon
  (deprecate IN-PLACE → rename → drop). Reprend le rythme de PR-stack
  #304-#319 (canon SEO) et PR #330 (admin label normalization).
- Aucune urgence opérationnelle ne justifie de casser brutalement la route
  consommée par le frontend SSR.
- L'annotation `@deprecated` JSDoc surface la migration à venir aux
  contributeurs **sans** introduire d'overhead runtime ni casser de tests.
- Phase 2 cohabitation = filet de sécurité pour consommateurs externes
  inconnus (scripts CI tiers, dashboards, agents).

## Conséquences

- **Aucun changement runtime** en Phase 1. La route `/api/r3-guide/:pg_alias`
  continue de servir `R3GuidePayload` à l'identique.
- Les nouveaux contributeurs voient l'annotation `@deprecated` sur les
  symboles legacy via leur IDE/LSP TypeScript et savent qu'il faut utiliser
  `R3Conseils*` quand il sera disponible (Phase 2).
- Phase 2 et 3 ne démarrent **que si l'observation Phase 1 ne révèle pas
  d'usage externe imprévu**. Si un consommateur tiers est découvert, on
  élargit le scope de Phase 2 (ajout de header `Sunset:` HTTP RFC 8594,
  notification consommateurs) avant de passer à Phase 3.
- Pas de migration DB. Pas de nouvelle table. Pas de breaking change pour
  les consommateurs frontend connus (le seul, `blog-pieces-auto.conseils.
  $pg_alias.tsx`, sera migré en Phase 2 dans la même PR que la création
  des nouveaux symboles).

## Hors scope

- Le rename ne touche **pas** le contenu DB (pas de `__seo_page` row, pas
  de `__rag_content_refresh_log.page_type`). Le canon `PAGE_TYPE_TO_ROLE`
  expose déjà `R3_guide_howto → R3_CONSEILS` (alias bridge), donc la
  classification reste cohérente.
- Pas d'ENUM PostgreSQL impacté (canon TS-only per ADR-040).
- Pas de migration des admin routes (PR #330 a déjà aligné l'affichage des
  labels via `@repo/seo-roles`).

## Vérification

Phase 1 (livré dans la PR monorepo associée à cette ADR) :

```bash
grep -rn "@deprecated" backend/src/modules/blog/controllers/r3-guide.controller.ts \
  backend/src/modules/blog/services/r3-guide.service.ts \
  backend/src/modules/blog/interfaces/r3-guide.interfaces.ts \
  backend/src/modules/blog/blog.module.ts
```

Doit retourner ≥ 7 occurrences (1 file-level JSDoc + 1 class/interface
JSDoc par fichier + 2 inline comments dans blog.module.ts).

Phase 2 / Phase 3 : critères de promotion énoncés ci-dessus.

## Références

- `@repo/seo-roles@0.4.0` (PR-stack #304-#319, `seo-roles-canon-shipped-20260505`)
- `feedback_deprecate_before_rename_before_drop.md` (mémoire AI-COS)
- ADR-040 — Canon SEO Roles côté TS uniquement
- PR monorepo #330 (R3 label normalization admin) — Phase 0 du nettoyage
  R3 (UI surface). Cette ADR couvre Phase 1+ (backend symboles).
