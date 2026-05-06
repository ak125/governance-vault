---
id: ADR-037
title: "Agent Naming Canon — frontmatter `role:` Zod-validated, fail-fast, source de vérité unique"
status: accepted
date: 2026-04-30
decision_date: 2026-05-01
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-025"]
related_rules: ["G1", "G2", "G3", "Q1", "Q2", "AP-10", "AP-11"]
related_incidents: []
related_adr: ["ADR-013", "ADR-025", "ADR-031", "ADR-036"]
---

# ADR-037: Agent Naming Canon — frontmatter `role:` Zod-validated

## Contexte

`OperatingMatrixService` (introduit PR #222, ADR-025) cartographie les agents
opérationnels (`.claude/agents/*.md`) sur les rôles canoniques `R0_HOME` à
`R8_VEHICLE`. Le contrat de mapping actuel est **filename-based** :

```ts
// backend/src/config/operating-matrix.service.ts
const ROLE_PREFIX_RE = /^(r\d)(_|-)/i;
// + scoring suffix matching depuis ROLE_ID_LIST
```

### État post-PR #234 / #235 / #237

Après les 3 PR follow-up de la session 2026-04-30, `unmappableAgents.length`
passe de 15 à 12 (les 3 `r3-*` auto-résolus par `DEPRECATED_ROLES` filtering
introduit dans #237). Restent **12 agents non-mappables** par filename :

| Catégorie | Nombre | Agents |
|---|---|---|
| Sans préfixe `R*` | 9 | `agentic-critic`, `agentic-planner`, `agentic-solver`, `blog-hub-planner`, `brief-enricher`, `conseil-batch`, `keyword-planner`, `phase1-auditor`, `research-agent` |
| `R6_*` ambigus (suffixe ne discrimine pas R6_GUIDE_ACHAT vs R6_SUPPORT) | 3 | `r6-content-batch`, `r6-image-prompt`, `r6-keyword-planner` |

Le suffix-matching (PR #235) ne peut pas trancher sans information additionnelle :
`r6-keyword-planner` ne contient ni `guide-achat` ni `support`, et les 9
non-prefixed sont par définition orchestrateurs ou utilitaires partagés
hors hiérarchie R0-R8.

### Audit empirique (règle CLAUDE.md « vérifier l'existant AVANT d'inventer »)

| Élément | État | Évidence |
|---|---|---|
| `gray-matter@^4.0.3` dans `backend/package.json` | **Installé** | dependencies |
| `js-yaml@^4.1.1` dans `backend/package.json` | **Installé** | dependencies |
| Frontmatter Markdown sur les 39 agents existants | **Ubiquitous** | Tous ont `name` + `description`, certains `model` + `tools` (format Claude Code natif) |
| Pattern `gray-matter` + Zod schema dans backend | **Établi (4 services)** | `brand-rag-frontmatter.schema.ts`, `diagnostic-content.service.ts`, `seo-generator.service.ts`, `reference.service.ts` |
| Pattern `parseFrontmatter` strict + `safeParseFrontmatter` (Zod) | **Établi** | `brand-rag-frontmatter.schema.ts` |
| Cache LRU sur frontmatter parsing | **Établi** | `diagnostic-content.service.ts` (5 min TTL) |

**Conclusion** : la classification d'agent par frontmatter Zod-validated
n'est pas une nouvelle convention — c'est l'extension du pattern majoritaire
du backend pour le contenu Markdown structuré.

### Tension architecturale

L'enum `RoleId` (`backend/src/config/role-ids.ts`) est **volontairement fermé**
sur la hiérarchie SEO R0-R8 (issue ADR-025). Les 9 agents sans préfixe ne sont
pas des rôles SEO — ce sont des orchestrateurs (`agentic-*`) ou des
utilitaires partagés transversaux (`brief-enricher`, `keyword-planner`,
`phase1-auditor`, `research-agent`, `blog-hub-planner`, `conseil-batch`).

Forcer ces agents dans R0-R8 serait incorrect ; les ignorer comme
`unmappableAgents` permanent est une dette tolérée. Un canon doit trancher.

## Décision

**Option A pure** : la **source de vérité du rôle d'un agent est son
frontmatter `role:`**, validé par schéma Zod, échoue à la première erreur
(fail-fast) au boot.

### Mécanisme

#### 1. Élargir l'enum `RoleId` avec 2 rôles canon hors-SEO

```ts
// backend/src/config/role-ids.ts
export enum RoleId {
  // ... R0-R8 inchangés ...
  AGENTIC_ENGINE = 'AGENTIC_ENGINE',  // orchestrateurs moteur agentique
  FOUNDATION = 'FOUNDATION',           // utilitaires partagés transversaux
}
```

`AGENTIC_ENGINE` et `FOUNDATION` sont ajoutés à `NON_WRITING_ROLES` du
`OperatingMatrixService` (ils ne sont pas dans `EXECUTION_REGISTRY` — comme
R0_HOME et R6_SUPPORT).

#### 2. Schéma Zod canon

Nouveau fichier `backend/src/config/agent-frontmatter.schema.ts` (clone du
pattern de `brand-rag-frontmatter.schema.ts`) :

```ts
import { z } from 'zod';
import { ROLE_ID_LIST } from './role-ids';

export const AgentFrontmatterSchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  role: z.enum(ROLE_ID_LIST as [string, ...string[]]),
  model: z.string().optional(),
  tools: z.array(z.string()).optional(),
});

export type AgentFrontmatter = z.infer<typeof AgentFrontmatterSchema>;

export function parseAgentFrontmatter(raw: unknown): AgentFrontmatter {
  return AgentFrontmatterSchema.parse(raw); // throws on first error
}

export function safeParseAgentFrontmatter(raw: unknown) {
  return AgentFrontmatterSchema.safeParse(raw);
}
```

#### 3. Refactor `OperatingMatrixService.scanAllAgents()`

```ts
import matter from 'gray-matter';
import { parseAgentFrontmatter } from './agent-frontmatter.schema';

private scanAllAgents(): AgentEntry[] {
  const agents: AgentEntry[] = [];
  for (const file of files) {
    const raw = fs.readFileSync(file, 'utf-8');
    const { data } = matter(raw);
    const parsed = parseAgentFrontmatter(data); // fail-fast
    agents.push({ source: rel, file, role: parsed.role });
  }
  return agents;
}
```

La regex filename `ROLE_PREFIX_RE` reste comme **convention humaine
informative** (lisibilité du dossier) mais cesse d'être autoritaire.
`extractRoleId(filename)` est supprimé et `agentsIndex` est construit
exclusivement depuis le frontmatter.

#### 4. Fail-fast au boot

`formatBootLog()` émet `level: 'error'` (au lieu de silent UNKNOWN) si :
- un agent a un frontmatter sans clé `role:` ;
- un agent a un `role:` non listé dans `ROLE_ID_LIST` ;
- un fichier `.md` n'a pas de frontmatter du tout.

Le `WriteGuardModule.onModuleInit()` propage l'erreur via le logger NestJS.
`unmappableAgents[]` est supprimé du payload `OperatingMatrix` —
**plus aucun agent ne peut être silencieusement non-mappable**.

#### 5. Mapping figé pour les 12 unmappables actuels

| Agent (file) | `role:` |
|---|---|
| agentic-critic.md | `AGENTIC_ENGINE` |
| agentic-planner.md | `AGENTIC_ENGINE` |
| agentic-solver.md | `AGENTIC_ENGINE` |
| blog-hub-planner.md | `FOUNDATION` |
| brief-enricher.md | `FOUNDATION` |
| keyword-planner.md | `FOUNDATION` |
| phase1-auditor.md | `FOUNDATION` |
| research-agent.md | `FOUNDATION` |
| conseil-batch.md | `R3_CONSEILS` |
| r6-content-batch.md | `R6_GUIDE_ACHAT` |
| r6-image-prompt.md | `R6_GUIDE_ACHAT` |
| r6-keyword-planner.md | `R6_GUIDE_ACHAT` |

Les 24 agents déjà mappables conservent leur rôle actuel (R0-R8),
explicitement déclaré dans leur frontmatter par script de migration
(cf. Plan de migration, Phase 1).

## Options Considérées

### Option A — Frontmatter `role:` (CHOISIE)

| Pour | Contre |
|---|---|
| Self-describing : l'agent porte sa propre identité | Migration one-shot des 39 frontmatters (mécanique, scriptable) |
| Source de vérité unique (le fichier agent) | — |
| Pattern industriel (Hugo, Jekyll, Astro Content Collections, MDX, Obsidian) | — |
| Réutilise pattern backend établi (4 services + 1 schema Zod) | — |
| Test trivial (mock un fichier MD avec frontmatter) | — |
| Fail-fast élimine la classe d'erreur « silent UNKNOWN » | — |
| Aligné avec ADR-013 « la fiche décide » | — |

### Option B — Renames avec suffixes (REJETÉE)

```
r6-content-batch.md           → r6-guide-achat-content-batch.md
agentic-critic.md             → r-orchestration-agentic-critic.md
keyword-planner.md            → r-foundation-keyword-planner.md
... (12 git mv)
```

| Pour | Contre |
|---|---|
| Étend convention filename existante (zéro code) | **Tatoue les décisions d'architecture dans les filenames** — c'est exactement ce qu'on a refusé en PR #235 pour la déprécation R3_GUIDE |
| | Casse `git blame` et historique des 12 fichiers |
| | Invente des préfixes non-canoniques (`r-orchestration-`, `r-foundation-`) hors enum `RoleId` |
| | Si rôle change demain (ex: réorg) → nouveau `git mv` cascadé |
| | Couplage fort filename ↔ identité, irréversible sans dommage à l'historique |

### Option C — Overrides Map (REJETÉE)

```ts
// backend/src/config/operating-matrix.service.ts
const AGENT_ROLE_OVERRIDES: Record<string, RoleId> = {
  'agentic-critic': RoleId.AGENTIC_ENGINE,
  'r6-content-batch': RoleId.R6_GUIDE_ACHAT,
  // ... 10 autres
};
```

| Pour | Contre |
|---|---|
| Léger en surface code (1 constante TS) | **Source de vérité fragmentée** : filename + map externe + frontmatter potentiel |
| Préserve identité fichiers | Ajout d'agent = 2 endroits à modifier (créer fichier + ajouter override) |
| | Risque de dérive : map peut désynchroniser des fichiers réels (un agent supprimé reste dans la map) |
| | Maintenance manuelle à perpétuité |
| | Anti-pattern AP-10 (couplage architectural implicite) |

## Conséquences

### Positives

- **Self-describing agents** : l'agent porte sa propre identité, indépendant
  de la convention filename (qui reste pure aide humaine).
- **Source de vérité unique** : le fichier agent. Pas de map externe, pas
  de regex à entretenir, pas de renames.
- **Fail-fast** : tout agent mal frontmatté échoue au boot du
  `WriteGuardModule`. Plus de silent UNKNOWN. Plus jamais de
  `unmappableAgents[]` qui s'accumule sans surveillance.
- **Pattern industriel standard** : reproduit le format Astro Content
  Collections, Hugo, Jekyll, MDX. Onboarding minimal pour les nouveaux
  contributeurs.
- **Réutilise le pattern majoritaire backend** (4 services existants),
  zéro nouvelle dépendance.
- **Aligné ADR-013** : la « fiche agent » devient l'autorité, conforme
  au cycle G1 → G2 → G3.

### Négatives / coûts

- **Migration one-shot** : ajouter `role:` à 39 frontmatters via script
  idempotent. Mécanique, scriptable, validable par diff git.
- **Refactor de `extractRoleId()`** privé : suppression de la regex et
  du suffix scoring. Tests existants à régénérer (cas `r3-image-prompt` →
  R3_CONSEILS reste vrai mais via frontmatter, pas via regex).
- **Coût boot léger** : lecture + parse de 39 fichiers `.md` au démarrage
  de `WriteGuardModule`. Mitigé par cache LRU si nécessaire (pattern
  `diagnostic-content.service.ts`). Boot délégué reste sub-100ms.

### Anti-patterns explicitement écartés

1. Pas de renames de filenames (ne pas tatouer les décisions dans les noms).
2. Pas de map d'overrides parallèle (pas de source de vérité fragmentée).
3. Pas de regex étendue sur filename pour absorber les ambiguïtés
   (l'extraction filename est définitivement supprimée comme autorité).
4. Pas d'ajout silencieux de rôles transversaux aux R0-R8 SEO (préserver
   l'enum SEO fermé d'ADR-025).
5. Pas de double mécanisme « frontmatter + fallback regex » qui invite la
   dérive — un seul chemin canonique.
6. Pas de boot silencieux sur frontmatter manquant (fail-fast obligatoire).
7. Pas de génération automatique de `role:` par LLM dans le script de
   migration (mapping table figée par cet ADR, déterministe).
8. Pas de canon vault lu par runtime backend (le frontmatter vit dans le
   monorepo, pas dans le vault — cf. ADR-031 séparation 4 layers).

## Plan de migration

### Phase 0 — Gouvernance (J+0 → J+2)

1. PR vault : ADR-037 (cette ADR) → mergée et `accepted`.
2. Pas de canon-publish workflow nécessaire (ADR purement architecture
   monorepo backend, pas de règle propagée).

### Phase 1 — Implémentation backend (J+2 → J+5)

PR monorepo dédiée (`chore/matrix-pr-d3-zero-unmappable`) :

1. **Étendre enum** : ajouter `AGENTIC_ENGINE` et `FOUNDATION` dans
   `backend/src/config/role-ids.ts` (`RoleId` + `ROLE_ID_LIST`).
2. **Schema Zod** : créer `backend/src/config/agent-frontmatter.schema.ts`.
3. **Refactor service** : remplacer `extractRoleId(filename)` par
   `parseAgentFrontmatter(data)` dans `scanAllAgents()`.
4. **NON_WRITING_ROLES** : ajouter `AGENTIC_ENGINE` + `FOUNDATION`.
5. **Boot fail-fast** : `formatBootLog()` émet `error` si parsing échoue.
6. **Tests** : `backend/src/config/operating-matrix.service.test.ts`
   régénérés pour couvrir les cas frontmatter (valid / missing role /
   invalid role / no frontmatter / R3_CONSEILS via role: au lieu de regex).
7. **Script migration** : `scripts/seo/inject-agent-role.ts` idempotent
   qui injecte `role:` dans les 39 agents selon mapping table figée.
8. **Régénération artefacts** : `npx tsx scripts/seo/dump-agent-matrix.ts`
   → `audit-reports/seo-agent-matrix.{json,md}` avec `unmappableAgents`
   field supprimé.
9. **Documentation** : `.claude/agents/README.md` (monorepo) explique
   le contrat frontmatter.

### Phase 2 — ADR-036 alignment (différé, hors scope D3)

ADR-036 introduit 3 agents marketing (LEAD/LOCAL/RETENTION). Au moment
de leur arrivée en monorepo, ils déclarent leur `role:` directement
(pas de migration ad-hoc). Si nécessaire, `RoleId` peut être étendu avec
`MARKETING_*` rôles canon (séparé d'ADR-037, traité par ADR-036 Phase 1).

## Validation

### Phase 0

- [ ] PR vault ADR-037 mergée et `accepted`
- [ ] Pas de drift hash sur `99-meta/canon-hashes.json` (ADR sans canon
  fichier propagé)

### Phase 1

- [ ] PR-D3 mergée sur `main` avec CI verte
- [ ] `audit-reports/seo-agent-matrix.json` ne contient plus la clé
  `unmappableAgents` (supprimée du payload `OperatingMatrix`)
- [ ] Test : un agent fichier sans `role:` → erreur boot
- [ ] Test : un agent avec `role:` invalide → erreur Zod
- [ ] Test : `expect(snap.agentsIndex).toMatchObject({...39 agents...})`
- [ ] Job CI `🛡️ Matrix JSON determinism` reste vert (canonicalize
  fonctionne sans `unmappableAgents`)
- [ ] `formatBootLog().filter(e => e.level === 'error').length === 0`
  sur les 39 agents migrés
- [ ] Smoke test endpoint admin :
  `GET /api/admin/governance/seo-operating-matrix?format=md` →
  pas de section « Agents non-mappables »

## Décisions ouvertes

1. **`AGENTIC_ENGINE` doit-il être étendu en sous-rôles** (`PLANNER`,
   `CRITIC`, `SOLVER`) au moment de l'introduction d'un moteur d'exécution
   agentique formel ? → différé, peut être traité par un ADR ultérieur
   sans rompre ce canon (ajout enum, mapping fichiers).
2. **Cache LRU sur le scan agents** : si le boot devient mesurablement
   lent (>200ms cumul I/O), introduire un cache `Map<path, {mtime,
   role}>`. Pour 39 fichiers, négligeable au moment de cet ADR ; sera
   réévalué si l'inventaire dépasse 100 agents.
3. **CI lint sur agents** : ajouter un workflow `agent-frontmatter-lint`
   qui parse tous les `.md` agents en `safeParse` et fait échouer la PR
   si un fichier est invalide. Différé Phase 1 — la fail-fast au boot
   couvre déjà la régression structurelle, le lint CI est un bonus DX.

## Évolutions futures (hors scope MVP)

- **Canon `role:` étendu à `.claude/skills/*.md`** : appliquer le même
  pattern Zod aux skills (ils ont déjà un frontmatter `name`,
  `description`). Cohérence cross-artefacts.
- **Canon `role:` étendu à `workspaces/marketing/.claude/agents/*.md`**
  (ADR-036) : à l'arrivée des 3 agents marketing, `role:` obligatoire
  dès création. Pas de retro-fit.
- **Self-describing pour autres types** : si `.claude/commands/*.md`
  arrivent (slash commands customs), même contrat.

## Références

- [[ADR-013-agent-lifecycle-governance]] — G1/G2/G3 governance des agents
- [[ADR-025-seo-department-architecture]] — pattern OperatingMatrix
  (cet ADR amende le contrat de mapping introduit ici)
- [[ADR-031-four-layer-content-architecture]] — pattern frontmatter Zod
  validé sur wiki/raw, étendu ici aux agents
- [[ADR-036-marketing-operating-layer]] — 3 agents marketing devront
  adopter ce canon dès leur arrivée
- [[rules-engineering-quality]] — Q1 (no bricolage), Q2 (grep-first)
- [[rules-ai-antipatterns]] — AP-10 (architecture explicite),
  AP-11 (vérifier l'existant avant inventer)
- PR monorepo séquence : #234 (R3_GUIDE remove), #237 (gaps + dep-aware),
  PR-D3 (cet ADR) — branche `chore/matrix-pr-d3-zero-unmappable`
- Knowledge support : `seo-operating-matrix-and-nonblocking-bootstrap-20260430.md`,
  `seo-operating-matrix-followup-handoff-20260430.md`
- Plan exécution : `/home/deploy/.claude/plans/expressive-munching-mochi.md`

---

_Décision prise sur preuves empiriques (gray-matter + js-yaml déjà installés,
4 services backend utilisent déjà ce pattern, 39 agents ont déjà un
frontmatter Claude Code natif). Options B et C documentées et explicitement
rejetées pour mémoire architecturale._
