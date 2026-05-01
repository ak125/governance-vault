---
id: ADR-038
title: "Marketing Agent Naming Canon — frontmatter `role:` + `business_unit:` Zod-validated, fail-fast (étend ADR-037 au scope marketing)"
status: accepted
date: 2026-04-30
decision_date: 2026-05-01
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-036"]
related_rules: ["G1", "G2", "G3", "Q1", "Q2", "AP-10", "AP-11"]
related_incidents: []
related_adr: ["ADR-013", "ADR-025", "ADR-031", "ADR-036", "ADR-037"]
---

# ADR-038: Marketing Agent Naming Canon (extension ADR-037 au marketing)

## Contexte

ADR-036 ratifie `MarketingMatrixService` (`backend/src/config/marketing-matrix.service.ts`,
PR #240) — service parallèle au `OperatingMatrixService` (ADR-025) pour préserver
le snapshot SEO inchangé. À l'arrivée des 3 agents Phase 1-2 (`local-business-agent`,
`marketing-lead-agent`, `customer-retention-agent`), le contrat de mapping
agent→identité doit être figé.

ADR-037 a établi pour le SEO le canon `frontmatter role: Zod-validated, fail-fast`.
ADR-037 §"Évolutions futures" mentionnait explicitement :

> Canon `role:` étendu à `workspaces/marketing/.claude/agents/*.md` (ADR-036) :
> à l'arrivée des 3 agents marketing, `role:` obligatoire dès création.
> Pas de retro-fit.

Cet ADR-038 applique ce canon au scope marketing, en l'étendant avec les
spécificités du domaine (rôles canon distincts, scope multi-business_unit).

### État pré-ADR-038 (constat empirique)

`MarketingMatrixService.scanAgents()` (PR #240, déjà sur main) utilise un
**scan filename-based** :

```ts
// backend/src/config/marketing-matrix.service.ts
for (const entry of fs.readdirSync(abs, { withFileTypes: true })) {
  if (!entry.isFile() || !entry.name.endsWith('.md')) continue;
  const name = entry.name.replace(/\.md$/, '');
  if (found.has(name)) found.set(name, true);
}
// + scope hardcodé via AGENT_SCOPES Record
```

C'est **exactement le pattern** qu'ADR-037 vient de déprécier pour le SEO.
Source de vérité éclatée (filename + AGENT_SCOPES const + agent file body
sans contrat). Pas de fail-fast. Aucune validation Zod.

### Audit empirique (règle CLAUDE.md « vérifier l'existant AVANT d'inventer »)

| Élément | État |
|---|---|
| `gray-matter@^4.0.3` + `js-yaml@^4.1.1` | **Déjà en deps backend** (utilisés par ADR-037) |
| `agent-frontmatter.schema.ts` (SEO) | **Existe** depuis ADR-037 — pattern Zod établi |
| `parseMarketingAgentFrontmatter` | À créer (mirror du SEO) |
| 3 agents marketing à créer | Phase 1.5 PR-1.5 d'ADR-036 |
| Cross-validation frontmatter ↔ canon | À créer (`EXPECTED_AGENT_ROLES` Map) |

**Conclusion** : appliquer ADR-037 au marketing n'invente rien — c'est le même
pattern Zod déjà éprouvé sur le SEO, étendu avec les spécificités marketing.

## Décision

### 1. Schéma Zod canon `marketing-agent-frontmatter.schema.ts`

Mirror de `agent-frontmatter.schema.ts` (ADR-037), différences :

```ts
export const MarketingAgentFrontmatterSchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  role: z.enum([
    MarketingRoleId.MARKETING_LEAD,
    MarketingRoleId.LOCAL_BUSINESS,
    MarketingRoleId.CUSTOMER_RETENTION,
  ]),
  business_unit: z
    .array(z.enum([ECOMMERCE, LOCAL, HYBRID]))
    .min(1),
  model: z.string().optional(),
  tools: z.array(z.string()).optional(),
}).passthrough();
```

### 2. Enum `MarketingRoleId` dans `marketing-matrix.types.ts`

3 rôles canon Phase 1-2 d'ADR-036 :

| RoleId | Agent attendu | Scope canon |
|---|---|---|
| `MARKETING_LEAD` | marketing-lead-agent | ECOMMERCE + LOCAL (lecture coordination) |
| `LOCAL_BUSINESS` | local-business-agent | LOCAL only |
| `CUSTOMER_RETENTION` | customer-retention-agent | ECOMMERCE primary + HYBRID exceptionnel |

### 3. Cross-validation `EXPECTED_AGENT_ROLES`

Map version-controlled dans `marketing-matrix.service.ts` qui associe chaque
filename canonique à son `role:` attendu :

```ts
const EXPECTED_AGENT_ROLES = new Map([
  ['customer-retention-agent', MarketingRoleId.CUSTOMER_RETENTION],
  ['local-business-agent', MarketingRoleId.LOCAL_BUSINESS],
  ['marketing-lead-agent', MarketingRoleId.MARKETING_LEAD],
]);
```

Si un fichier existe mais déclare un `role:` différent → `parseError` →
fail-fast au boot via `formatBootLog()`.

### 4. Refactor `scanAgents()`

- Lecture frontmatter via `gray-matter`
- Validation Zod via `safeParseMarketingAgentFrontmatter`
- Cross-check role contre `EXPECTED_AGENT_ROLES`
- Surface `parseErrors[]` dans le snapshot
- `formatBootLog()` ajouté (mirror SEO) — émet `level: 'error'` par parseError

### 5. Suppression `AGENT_SCOPES` Record

Le scope d'un agent vient désormais **uniquement** du frontmatter `business_unit:`
qu'il déclare. Plus de map externe — élimination du pattern « source de vérité
fragmentée » (anti-pattern AP-10).

`MarketingAgentEntry` :
```ts
{
  name: string;
  present: boolean;
  role: MarketingRoleId | null;       // null si fichier absent
  scope: ReadonlyArray<MarketingBusinessUnit>;  // depuis frontmatter
}
```

### 6. Création des 3 agents stubs

`workspaces/marketing/.claude/agents/{local-business,marketing-lead,customer-retention}-agent.md` —
chacun avec frontmatter complet (`role:` + `business_unit:` + `name:` +
`description:` + `model:` + `tools:`).

## Options Considérées

### Option A — Étendre ADR-037 au marketing (CHOISIE)

Pattern unifié : 1 contrat Zod par scope (SEO et marketing), même mécanisme,
même fail-fast, même cross-validation. Les enums sont distincts (`RoleId` vs
`MarketingRoleId`) mais le pattern est identique.

| Pour | Contre |
|---|---|
| Cohérence cross-services (SEO + marketing même pattern) | 2 schemas Zod (un par scope) |
| Fail-fast au boot pour les 2 services | — |
| Source de vérité unique par agent (son frontmatter) | — |
| Réutilise gray-matter + Zod déjà en deps | — |
| Élimination du `AGENT_SCOPES` const (source de vérité fragmentée) | — |
| Cross-validation filename ↔ role attendu (canon code) | — |

### Option B — Schema unifié (REJETÉE)

`agent-frontmatter.schema.ts` accepterait `role: RoleId | MarketingRoleId`
dans un seul Zod enum.

| Pour | Contre |
|---|---|
| Un seul schema | **Couple SEO et marketing** dans le même schema (anti AP-10) |
| | `OperatingMatrixService` accepterait des roles marketing (incohérent) |
| | Évolutions futures (autres modules) recoupent le god-schema |

ADR-036 a déjà décidé services séparés pour éviter le god-object — étendre cette
logique aux schemas est cohérent.

### Option C — Hardcoded `AGENT_SCOPES` conservé + ADR-037 partiel (REJETÉE)

Ajouter `role:` au frontmatter mais garder `AGENT_SCOPES` Record pour le scope.

| Pour | Contre |
|---|---|
| Migration plus douce (pas de suppression de code) | **Source de vérité fragmentée** : frontmatter `business_unit:` + `AGENT_SCOPES` const externe |
| | Risque de drift entre les 2 (un ajout de scope dans frontmatter sans toucher la const = bug silent) |
| | C'est exactement le pattern bricolage que ADR-037 a refusé |

## Conséquences

### Positives

- **Cohérence cross-services** : SEO (`OperatingMatrixService`) et marketing
  (`MarketingMatrixService`) suivent le même pattern frontmatter Zod fail-fast.
- **Source de vérité unique par agent** : son fichier `.md`. Pas de map externe.
- **Cross-validation** filename ↔ role canon (en code) ↔ frontmatter
  (déclaratif) — drift détecté au boot.
- **Élimination `AGENT_SCOPES`** : un Record TS hardcodé en moins, donc une
  source de drift en moins.
- **Fail-fast au boot** : si l'auteur d'un agent oublie `role:` ou se trompe,
  `MarketingModule.onModuleInit()` lève une erreur explicite.

### Négatives / coûts

- **Création des 3 agents stubs** : devait arriver de toute façon (Phase 1.5
  PR-1.5 d'ADR-036) — l'ADR-038 figure le contrat dès le départ, pas de
  retro-fit.
- **`MarketingMatrixService.scanAgents()` réécrit** : 100 lignes refactorées,
  20 lignes supprimées (AGENT_SCOPES const). Tests existants à étendre (déjà fait :
  30 tests, dont 13 nouveaux pour la Zod + cross-validation).
- **Migration audit JSON** marketing : si déjà committé, la forme du payload
  change (nouveau champ `role` dans agents, plus de scope hardcodé). Au moment
  d'ADR-038, le marketing audit JSON n'existe pas encore (Phase 1.5 PR-1.5
  l'introduit) — donc pas de migration.

### Anti-patterns écartés

1. Pas de schema unifié SEO+marketing (préserve séparation des concerns ADR-036).
2. Pas de `AGENT_SCOPES` Record en plus du frontmatter (source de vérité
   fragmentée).
3. Pas de fallback silent (un fichier mal frontmatté est une erreur boot,
   pas un warning).
4. Pas de tolérance sur `business_unit: []` (Zod `.min(1)` — un agent qui ne
   peut servir aucune business_unit n'a pas sa place dans la matrice).
5. Pas d'invention d'`AGENTIC_ENGINE` / `FOUNDATION` côté marketing (ces rôles
   sont SEO-spécifiques, ADR-037 §3 §5).

## Plan de migration

### Phase 0 — Gouvernance (J+0 → J+1)

1. PR vault : ADR-038 (cette ADR) → mergée et `accepted`.
2. Pas de canon-publish (ADR purement architecture monorepo, comme ADR-037).

### Phase 1 — Implémentation backend (J+1 → J+3)

PR monorepo dédiée :

1. **Étendre types** : `MarketingRoleId` enum + `MarketingAgentParseError`
   interface dans `backend/src/config/marketing-matrix.types.ts`.
2. **Schema Zod** : créer `backend/src/config/marketing-agent-frontmatter.schema.ts`.
3. **Refactor service** : `MarketingMatrixService.scanAgents()` lit frontmatter
   via gray-matter, valide via Zod safeParse, cross-check via `EXPECTED_AGENT_ROLES`.
4. **Suppression `AGENT_SCOPES` const** : scope vient du frontmatter.
5. **`formatBootLog()` méthode** : mirror du pattern OperatingMatrixService —
   émet `level: 'error'` par parseError.
6. **Création 3 agents stubs** dans `workspaces/marketing/.claude/agents/` avec
   frontmatter complet conforme au schéma.
7. **Tests** : extension `marketing-matrix.service.test.ts` avec 13 nouveaux
   cas (parseValid, missing role, invalid role, mismatch role, empty
   business_unit, etc.). Tests existants conservés.

### Phase 2 — Wiring boot fail-fast (différé Phase 1.6 PR-1.6 d'ADR-036)

`MarketingModule.onModuleInit()` consomme `formatBootLog()` et propage les
erreurs via le logger NestJS — pattern miroir de `WriteGuardModule.onModuleInit()`
côté SEO. Hors scope ADR-038, c'est de la plomberie standard.

## Validation

### Phase 0

- [ ] PR vault ADR-038 mergée et `accepted`

### Phase 1

- [ ] PR monorepo mergée sur `main` avec CI verte
- [ ] 30 tests `marketing-matrix.service.test.ts` passent (dont 13 ADR-038)
- [ ] 3 agents `workspaces/marketing/.claude/agents/*.md` présents
- [ ] `MarketingMatrixService` snapshot `agents[]` retourne 3 entrées avec
  `role` et `scope` issus du frontmatter
- [ ] `formatBootLog().filter(e => e.level === 'error').length === 0` sur les
  3 agents migrés
- [ ] Test négatif : un fichier sans `role:` → 1 erreur boot
- [ ] Test négatif : `role:` non-valide → 1 erreur boot
- [ ] Test négatif : filename ↔ role mismatch → 1 erreur boot
- [ ] Test négatif : `business_unit: []` → 1 erreur boot

### Phase 2 (post-merge ADR-038)

- [ ] `MarketingModule.onModuleInit()` propage les bootlog erreurs
- [ ] Smoke test : un agent fichier malformé → boot fail explicite (pas
  silent unknown)

## Décisions ouvertes

1. **Future Phase 3+ d'ADR-036 (providers externes)** : si nouveaux agents
   arrivent (`gbp-bot-agent`, `mailjet-bot-agent`), étendre `MarketingRoleId`
   enum et `EXPECTED_AGENT_ROLES` map, plus une mise à jour ADR-038 (ou ADR
   dédié si besoin).
2. **Lint CI** : ajouter un workflow `marketing-agent-frontmatter-lint` qui
   parse les `.md` agents en `safeParse` et fait échouer la PR si invalide.
   Différé Phase 1 — la fail-fast au boot couvre déjà la régression structurelle.

## Évolutions futures

- **Skills marketing** : `workspaces/marketing/.claude/skills/*.md` peuvent
  adopter le même pattern (`role:` + Zod). Hors scope ADR-038.
- **Routine Paperclip** : si un wrapper `mkt-agent-runner` est créé, il lira
  le frontmatter pour décider quel scope (`business_unit`) est autorisé.

## Références

- [[ADR-013-agent-lifecycle-governance]] — G1/G2/G3 governance des agents
- [[ADR-025-seo-department-architecture]] — pattern OperatingMatrix
- [[ADR-031-four-layer-content-architecture]] — pattern frontmatter Zod
- [[ADR-036-marketing-operating-layer]] — Phase 1-2 marketing, 3 agents
  attendus, services séparés
- [[ADR-037-agent-naming-canon]] — canon SEO frontmatter `role:` Zod-validated
  (cet ADR-038 étend ADR-037 au scope marketing)
- [[rules-engineering-quality]] — Q1 (no bricolage), Q2 (grep-first)
- [[rules-ai-antipatterns]] — AP-10 (architecture explicite),
  AP-11 (vérifier l'existant)
- PR monorepo séquence : #240 (marketing matrix service initial), PR ADR-038
  (cet ADR) — branche `feat/adr-038-marketing-agent-naming-canon`

---

_Décision prise sur preuves empiriques — `MarketingMatrixService` (PR #240, déjà
sur main) utilisait le pattern filename-based exact qu'ADR-037 a déprécié pour
le SEO. ADR-038 applique le canon ADR-037 au marketing avec ses spécificités
domain (3 rôles distincts, scope multi-business_unit). Options B (schema unifié)
et C (AGENT_SCOPES conservé) documentées et explicitement rejetées._
