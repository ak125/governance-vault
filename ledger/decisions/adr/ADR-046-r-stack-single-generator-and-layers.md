---
id: ADR-046
title: "R-stack canonique — 1 générateur par rôle + chaîne L0-L5 mécaniquement gouvernée"
status: proposed
date: 2026-05-07
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "Q1", "AP-04", "AP-08", "AP-10", "AP-11"]
related_incidents: []
related_adr: ["ADR-027", "ADR-031", "ADR-033", "ADR-037", "ADR-038", "ADR-039", "ADR-040", "ADR-044"]
implementation_status: phase-0-baseline-2026-05-07
---

# ADR-046 — R-stack canonique : 1 générateur par rôle + chaîne L0-L5 gouvernée

## Contexte

Audit R-stack [[2026-05-07-r-stack-audit]] (cf. evidence-pack) révèle 4
problèmes structurels :

1. **Wiki n'est PAS la SoT canon** — `automecanik-wiki/wiki/{gammes,vehicles}/`
   sont vides. R7 brands fonctionne (36/36 sync `exports/rag/constructeurs/`)
   mais c'est une exception. Les 1655 fichiers RAG legacy gammes (17.6 MB
   total, ~10.6 KB / fichier en moyenne) sont consommés en runtime sans
   passer par wiki/curation/promotion.
2. **Dispersion R1 : 4+ implémentations** — `r1-enricher.service.ts`,
   `r1-content-from-rag.service.ts`, `r1-keyword-plan-batch.service.ts`,
   `r1-image-prompt.service.ts`, `r1-keyword-plan-gates.service.ts`,
   `r1-related-resources.service.ts`, plus configs `r1-keyword-plan.constants.ts`
   et `r1-media-rules.constants.ts`. Responsabilités enchevêtrées.
3. **Triple SoT implicite** — `@repo/seo-roles@0.5.0` détient à la fois
   l'identité (RoleId, normalize) **et** le comportement (forbidden-overlap
   data + logique exportée). Les enrichers contiennent règles métier en
   dur (`R1_MICRO_SEO_MIN_CHARS = 1500` dans `r1-enricher.service.ts:30`).
   AGENTS.md déclare encore une 3ème vérité. Drift programmé à 6 mois.
4. **Aucune barrière mécanique L3 read-only** — la mirror RAG
   `/opt/automecanik/rag/knowledge/` peut être écrite par n'importe quel
   process. Une `ast-grep` rule `no-direct-rag-knowledge-write.yml` existe
   au monorepo mais ne contraint que le code TS — n'empêche pas un script
   Python ad-hoc d'écraser des fiches.

[[ADR-031-four-layer-content-architecture]] avait posé la chaîne 4-layer raw/wiki/exports/consumers, mais
l'enforcement reste culturel. [[ADR-040-seo-roles-canon-ts-side-only]] a foundé `@repo/seo-roles` mais
en TS-side only sans séparation identité/comportement. [[ADR-039-wiki-frontmatter-zod-canon]] cadre
le frontmatter wiki Zod mais sans `validated_by` multi-domaine ni lineage
complet.

## Décision

Pose le **cadre canonique R-stack** en 6 layers + couche transversale
contracts, avec enforcement mécanique fail-closed à chaque frontière.

### Layers canon

| Layer | Localisation | Rôle | Enforcement |
|---|---|---|---|
| **L0 RAW** | `governance-vault/ledger/knowledge/_raw/` (3767 fichiers) | Brut, immutable, schema mirror | Read-only, append-only |
| **L1 WIKI** | `automecanik-wiki/wiki/{gammes,constructeurs,vehicles,diagnostic}/` | Curation + frontmatter Zod v3.0.0 | Multi-validation `validated_by.{semantic, role, diagnostic, license}` |
| **L1.5 CONTRACTS** | `packages/seo-role-contracts/` ([[ADR-047-seo-role-contracts-as-code]]) | SoT comportemental — sections, longueurs, intents, schemas, thresholds, promotion gates | Zod, pré-commit ast-grep enforcement |
| **L2 EXPORTS** | `automecanik-wiki/exports/rag/{topic}/` | Machine-ready, lineage propagé, checksum | Promotion gate fail-closed (toutes validations true) |
| **L3 RAG MIRROR** | `/opt/automecanik/rag/knowledge/{topic}/` | Read-only runtime | `chmod 555` + owner `rag-sync` + CI guard + boot fail-fast si manifest > 24h + git pre-push hook |
| **L4 GENERATORS** | `backend/src/modules/admin/services/*-enricher.service.ts` | 1 service canon par rôle, lit contracts L1.5 | Refactor obligatoire, pas de règle métier hors L1.5 |
| **L5 DB CACHE** | `__seo_*_slots`, `__seo_gamme_*`, `__blog_*` | Read-only runtime, write only par L4 | RLS Supabase + WriteGuard ([[ADR-021-database-rls-hardening-zero-trust]]) |

### Principe non-négociable

- **Zéro écriture directe dans L3** (chmod + ast-grep + CI + git hook).
- **Zéro règle métier hors L1.5** (refactor enrichers wave 1/2 — wave 1 :
  R1, R3, R4, R6 ; wave 2 : R7, R8 + validators + AGENTS.md).
- **Promotion L1→L2 uniquement si toutes les validations passent**
  (`validated_by.semantic`, `.role`, `.diagnostic`, `.license` ∧
  `review_status === 'accepted'`). Jamais d'auto-accept sur `truth_level`
  seul.
- **1 LIVE générateur par rôle** — les 5+ implémentations déviantes R1
  (services orchestration / image-prompt / KP-gates / related-resources)
  conservent leurs scopes orthogonaux (orchestration, media, KP) mais ne
  produisent **aucune règle métier R1** (cells configs orthogonales,
  pas business rules dupliquées).

### Frontmatter wiki v3.0.0 (extension [[ADR-039-wiki-frontmatter-zod-canon]])

Schema Zod ajouté, backward-compat avec v2.0.0 via auto-migration CI :

```ts
{
  truth_level: z.enum(['L0', 'L1', 'L2', 'L3']),
  review_status: z.enum(['pending', 'reviewed', 'accepted', 'rejected']),
  validated_by: z.object({
    semantic: z.boolean().default(false),
    role: z.boolean().default(false),
    diagnostic: z.boolean().default(false),
    license: z.boolean().default(false),
  }),
  source_origin: z.enum([
    'legacy_rag', 'db_skeleton', 'proposal_human', 'auto/r7-classifier',
  ]),
  lineage: z.object({
    source_hash: z.string(),
    source_commit: z.string(),
    schema_version: z.string(),
    exporter_version: z.string(),
    exported_at: z.string().datetime().optional(),
  }),
  diagnostic_relations: z.array(...).optional(), // ADR-033
}
```

## Statut

- **Statut** : `proposed` (cet ADR + [[ADR-047-seo-role-contracts-as-code]] vault PR Phase 0)
- **Implémentation** : roadmap 7 phases, 23 PRs, 6-8 semaines
  - Phase 0 (cet ADR) : baseline audit + 2 ADRs
  - Phase 1 (1 sem, 5 PRs) : garde-fous mécaniques + L3 RO
  - Phase 2 (2 sem, 4 PRs) : `seo-role-contracts` package + refactor enrichers (PIVOT)
  - Phase 3A (1 sem, 3 PRs) : wiki ingestion only (legacy importer + skeleton generator)
  - Phase 3B (2 sem, 4 PRs) : validation pipeline + promotion gate
  - Phase 4 (1 sem, 4 PRs) : R8 canonical identity + R1 bump conditionné par diversity audit
  - Phase 6 (1 sem, 2 PRs) : lock canonical + ADRs accepted

Plan détaillé : `/home/deploy/.claude/plans/je-remarque-une-faiblesse-eventual-flamingo.md`

## Conséquences

### Positives

- **Drift programmé éliminé** : SoT identité (`seo-roles`) séparée de SoT
  comportement (`seo-role-contracts`). 1 seul endroit qui mute pour les
  règles métier R*.
- **Promotion fail-closed** : aucune fiche RAG mirror sans 4 validations
  vertes. Élimine la zone grise auto-accept truth_level seul.
- **L3 mécaniquement RO** : chmod + manifest TTL + boot fail-fast NestJS.
  Plus de "j'ai oublié l'enforcement culturel".
- **Génération canonique consolidée** : enrichers refactorés lisent
  contracts. Plus de `R1_MICRO_SEO_MIN_CHARS = 1500` hardcodé en 6
  endroits différents.

### Négatives / risques

- **Ampleur** : 23 PRs sur 6-8 semaines. Risque de fatigue avant Phase 4.
  Mitigation : Phase 1 livre valeur immédiate (garde-fous), Phase 2 est le
  pivot et délivre l'essentiel — Phase 3+ peut ralentir sans casser.
- **Refactor enrichers (Phase 2 PR-H/I)** : risque moyen — wave 1 + wave
  2 séparées, tests snapshot sur chaque. Pas de big-bang.
- **Backward compat frontmatter v2.0.0** : auto-migration CI peut tomber
  sur edge cases (caractères Unicode dans payload). Mitigation : test
  end-to-end sur fiche pilote `plaquette-de-frein.md`.
- **R1 bump 1500/3000 déjà shipped** (PR monorepo #346, commit
  `9f72a0bd`) : Phase 4 PR-S devra reconnaître ce fait et migrer le
  constant existant `R1_MICRO_SEO_MIN_CHARS = 1500` (l. 30 de
  `r1-enricher.service.ts`) vers le contract `seo-role-contracts/r1.ts`,
  pas re-bumper.

## Anti-patterns à rejeter (futurs)

- ❌ Ajouter une règle métier R\* dans un enricher (`min_chars`, `FORBIDDEN`,
  `allowed_sections`) hors d'un import depuis `@repo/seo-role-contracts`
  — bloqué par ast-grep `no-hardcoded-rules-in-enrichers` (PR-B Phase 1
  étendu Phase 2).
- ❌ Promouvoir une fiche L1→L2 sans `validated_by.*` tous true — bloqué
  par `wiki-to-rag-exporter.py` (Phase 3B PR-O).
- ❌ Écrire directement dans `rag/knowledge/` — bloqué par chmod 555 + CI
  guard + git pre-push (Phase 1 PR-E).
- ❌ Créer un nouveau service R\* en parallèle d'un enricher canonique —
  AGENTS.md ownership (Phase 1 PR-C) impose 1 LIVE par rôle.
- ❌ Auto-accept un fichier RAG legacy en l'important sans pipeline de
  validation — `legacy-rag-importer.py` (Phase 3A PR-K) marque
  `validated_by={all: false}` par défaut.

## Références

- Plan détaillé : `/home/deploy/.claude/plans/je-remarque-une-faiblesse-eventual-flamingo.md`
- Audit baseline : [[2026-05-07-r-stack-audit]]
- ADRs liés : [[ADR-027-r5-consolidation-into-r3-s2-diag]] (R5 sunset),
  [[ADR-031-four-layer-content-architecture]] (4-layer architecture),
  [[ADR-033-wiki-gamme-diagnostic-relations-contract]] (diagnostic_relations[]),
  [[ADR-037-agent-naming-canon]] + [[ADR-038-marketing-agent-naming-canon]] (frontmatter Zod),
  [[ADR-039-wiki-frontmatter-zod-canon]] (frontmatter v2.0.0),
  [[ADR-040-seo-roles-canon-ts-side-only]] (foundation seo-roles),
  [[ADR-044-seo-strategy-2026-roles-priority]] (priorités R6/R8/R7)
- Mémoires session : `feedback_no_bricolage_*`, `feedback_branch_scope_discipline`,
  `feedback_canon_rule_live_iff_adr_accepted`
