---
id: ADR-047
title: "Contract-as-code — `@repo/seo-role-contracts` SoT comportemental, séparé de l'identité"
status: proposed
date: 2026-05-07
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-040"]
related_rules: ["G1", "G2", "Q1", "AP-04", "AP-08", "AP-10", "AP-11"]
related_incidents: []
related_adr: ["ADR-040", "ADR-046"]
implementation_status: phase-0-baseline-2026-05-07
---

# ADR-047 — `@repo/seo-role-contracts` : SoT comportemental R-stack séparé de l'identité

## Contexte

[[ADR-040-seo-roles-canon-ts-side-only]] foundé `@repo/seo-roles` comme
single-source-of-truth canonique pour l'identité des rôles R0-R8 (RoleId
enum, normalize, alias, intents, keyword-cluster schema). Version actuelle
`@repo/seo-roles@0.5.0` (vu dans `packages/seo-roles/package.json`).

**Mais le package mélange deux préoccupations distinctes** :

1. **Identité** (légitime — c'est sa raison d'être) :
   - `RoleId` enum, alias, normalize functions
   - `ROLE_BADGE_COLORS`, display labels
   - `keyword-intent.ts`, `keyword-cluster.schema.ts`

2. **Comportement** (mauvais endroit) :
   - `forbidden-overlap.ts` exporte la **logique** + **data** de quels
     termes sont interdits par paire de rôles
   - Les enrichers backend importent `getForbiddenOverlap()` mais doivent
     aussi consulter d'autres règles métier (longueurs, sections,
     schemas Schema.org) qui ne sont **pas** dans `seo-roles` — donc ces
     règles sont **dupliquées en dur** dans les enrichers eux-mêmes :

```bash
$ grep -rEn "min_chars|max_chars|MIN_CHARS|MAX_CHARS" \
    backend/src/modules/admin/services/*-enricher.service.ts
backend/src/modules/admin/services/r1-enricher.service.ts:30:const R1_MICRO_SEO_MIN_CHARS = 1500;
backend/src/modules/admin/services/r1-enricher.service.ts:31:const R1_MICRO_SEO_MAX_CHARS = 3000;
```

Rajouter `min_chars` à `seo-roles` polluerait son scope identitaire. Et
laisser ces règles dupliquées dans 8 enrichers (R1/R2/R3/R4/R6/R7/R8 +
gamme-detail) garantit drift à 6 mois. AGENTS.md des agents R\*
(`workspaces/seo-batch/agents/*/AGENTS.md`) déclare encore une 3ème
vérité non synchronisée.

**Triple SoT implicite = anti-pattern AP-11 (duplication)**.

## Décision

Créer un nouveau package `@repo/seo-role-contracts` qui détient le **SoT
comportemental** R-stack. `@repo/seo-roles` ne garde que l'**identité**.
Bump major `seo-roles` 0.5.0 → 1.0.0 (breaking : `getForbiddenOverlap`
move).

### Structure `@repo/seo-role-contracts`

```
packages/seo-role-contracts/
├── package.json
├── src/
│   ├── schema.ts           # Zod RoleContract type
│   ├── contracts/
│   │   ├── r0.ts           # 1 fichier export contract par rôle
│   │   ├── r1.ts
│   │   ├── r2.ts
│   │   ├── r3.ts
│   │   ├── r4.ts
│   │   ├── r6.ts
│   │   ├── r7.ts
│   │   └── r8.ts
│   ├── index.ts            # export const CONTRACTS: Record<RoleId, RoleContract>
│   └── __tests__/
│       └── conformance.test.ts  # chaque RoleId a un contract
└── tsconfig.json
```

### Schema Zod RoleContract

```ts
import { z } from 'zod';
import { RoleId } from '@repo/seo-roles';

export const SectionSpec = z.object({
  id: z.string(),                                  // ex: "R1_S0", "R1_S4_MICRO_SEO"
  min_chars: z.number().int().nonnegative(),
  max_chars: z.number().int().nonnegative(),
  required: z.boolean().default(true),
});

export const RoleContract = z.object({
  id: z.nativeEnum(RoleId),
  allowed_sections: z.array(SectionSpec),
  forbidden_overlap: z.array(z.union([z.string(), z.nativeEnum(RoleId)])),
  allowed_schemas: z.array(z.enum([
    'Article', 'FAQPage', 'HowTo', 'Product', 'Offer',
    'AggregateRating', 'Review', 'Brand', 'Vehicle', 'BreadcrumbList',
  ])),
  content_contracts: z.object({
    definition: z.string().optional(),
    procedure: z.string().optional(),
    comparison: z.string().optional(),
    diagnostic: z.string().optional(),
  }).partial(),
  semantic_intents: z.array(z.enum([
    'transactional', 'informational', 'navigational', 'investigational',
  ])),
  uniqueness_thresholds: z.object({
    min_specific_ratio: z.number().min(0).max(1).default(0.6),
    max_boilerplate: z.number().min(0).max(1).default(0.4),
    min_entropy_shannon: z.number().nonnegative().optional(),
    max_jaccard_inter_gamme: z.number().min(0).max(1).optional(),
    max_template_phrase_ratio: z.number().min(0).max(1).optional(),
  }).partial(),
  promotion_gate: z.object({
    requires_validations: z.array(z.enum([
      'semantic', 'role', 'diagnostic', 'license',
    ])),
  }),
});

export type RoleContract = z.infer<typeof RoleContract>;
```

### Lecteurs canoniques (DI seul moyen d'accéder aux règles)

| Layer | Lecteur | Usage |
|---|---|---|
| L4 enrichers | `R1EnricherService`, `ConseilEnricherService`, ... | `CONTRACTS.R1_ROUTER.allowed_sections`, `.min_chars`, `.forbidden_overlap` |
| Validators | `r1-router-validator`, `gatekeeper`, `content-quality-gate` | Conformance check post-generation |
| KP planners | `r1-keyword-plan-batch.service.ts` | Phases pipeline lit `seo_priority` (constants) **et** intents (contract) |
| AGENTS.md | `workspaces/seo-batch/agents/*/AGENTS.md` | Référence textuelle vers `packages/seo-role-contracts/src/contracts/r{N}.ts` (pas duplication) |
| Frontend | Badges qualité admin, content-audit dashboard | `import { CONTRACTS } from '@repo/seo-role-contracts'` |
| `seo-roles` | `forbidden-overlap.ts` | **Move** vers contracts en PR-G Phase 2 |

### Migration `@repo/seo-roles` 0.5.0 → 1.0.0 (breaking)

- **Retire** : `forbidden-overlap.ts` (déplacé en `seo-role-contracts/r{N}.ts`)
- **Garde** : `canonical.ts` (RoleId), `normalize.ts`, `display.ts`,
  `colors.ts`, `intents.ts`, `keyword-cluster.schema.ts`,
  `text-normalize.ts`, `branded.ts`, `legacy.ts`
- **Bump** : v1.0.0 (major — ABI break sur `getForbiddenOverlap`)
- **Migration consumers** : grep `getForbiddenOverlap|forbidden_overlap` →
  remplacer par `CONTRACTS[role].forbidden_overlap`. PR-G livré atomique
  avec PR-F (création contracts) pour ne pas casser CI.

## Statut

- **Statut** : `proposed` (cet ADR + [[ADR-046-r-stack-single-generator-and-layers]] vault PR Phase 0)
- **Implémentation** : Phase 2 du plan refondation R-stack (2 sem, 4 PRs)
  - PR-F : créer `packages/seo-role-contracts/`
  - PR-G : migrer `forbidden-overlap` de seo-roles vers contracts
    + bump seo-roles 1.0.0 + migration consumers
  - PR-H : refactor enrichers wave 1 (R1/R3/R4/R6) lisent contracts
  - PR-I : refactor enrichers wave 2 (R7/R8) + validators + AGENTS.md

### Critère de sortie Phase 2

```bash
grep -rEn 'min_chars\|max_chars\|FORBIDDEN_TERMS\|allowed_sections' \
  backend/src/modules/admin/services/*-enricher.service.ts \
  | grep -v 'from .*seo-role-contracts'
# doit retourner 0 résultats
```

## Conséquences

### Positives

- **Triple SoT éliminé** : 1 source identité (`seo-roles`), 1 source
  comportement (`seo-role-contracts`), 1 lecture AGENTS.md (référence,
  pas duplication).
- **Drift mécaniquement empêché** : ast-grep
  `no-hardcoded-rules-in-enrichers` (Phase 1 PR-B étendu Phase 2)
  bloque tout `min_chars: 1500` hors d'un import depuis contracts.
- **Tests conformance** : chaque `RoleId` enum doit avoir un contract
  (test unitaire). Si nouveau rôle ajouté à `seo-roles`, CI fail si
  contract manque.
- **Frontend cohérent** : badges qualité admin lisent les mêmes seuils
  que les enrichers backend. Plus de désync admin UI vs production.

### Négatives / risques

- **Bump major `seo-roles` 1.0.0** : breaking pour tout consumer externe
  (s'il y en a — à vérifier). Mitigation : PR-G livre la migration de
  tous les consumers internes en atomique avec le bump.
- **Refactor enrichers Wave 1 (4 services) + Wave 2 (2 services)** :
  risque moyen. Mitigation : tests snapshot par service, séparation
  vagues, dry-run grep avant merge.
- **Surface contract** : 8 contracts × ~50 lignes Zod = 400 lignes neuves.
  Mais centralisées au lieu de dupliquées dans 8 enrichers + 8 AGENTS.md
  + 5 frontend usages. Net négatif sur lignes totales.

## Anti-patterns à rejeter (futurs)

- ❌ Ajouter une règle métier dans un enricher service en dur — bloqué
  par ast-grep `no-hardcoded-rules-in-enrichers`.
- ❌ Mettre une règle comportementale dans `@repo/seo-roles` — review
  rejette (scope identité only depuis ADR-040 + cet ADR).
- ❌ Dupliquer une valeur de seuil dans AGENTS.md → utiliser référence
  textuelle vers `packages/seo-role-contracts/src/contracts/r{N}.ts`.
- ❌ Faire évoluer un seuil sans bumper le contract version — chaque
  modification de `RoleContract` schema = bump semver `seo-role-contracts`
  + ADR vault si change majeur.

## Références

- Plan détaillé : `/home/deploy/.claude/plans/je-remarque-une-faiblesse-eventual-flamingo.md` § Phase 2
- ADR amendé : [[ADR-040-seo-roles-canon-ts-side-only]] (scope clarifié à
  identité only — comportement déplacé en `seo-role-contracts`)
- ADR pair : [[ADR-046-r-stack-single-generator-and-layers]] (cadre
  L0-L5)
- Mémoires session : `feedback_link_rules_in_db_not_hardcode` (esprit
  similaire — gouvernance déclarative vs hardcode), `feedback_canon_rule_live_iff_adr_accepted`
