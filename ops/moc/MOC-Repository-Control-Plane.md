---
type: moc
status: canon
updated: 2026-05-13
adr_link: ADR-058
---

# MOC: Repository Control Plane

Index opérationnel du Repository Control Plane (ADR-058) — registry canonique
3 couches (data auto + overlay manuel + projection générée) avec gates CI
progressifs V1 (warning → block-new).

> **Source de vérité** : `ADR-058-repository-control-plane.md` (frontmatter +
> body). Cette MOC est l'**index dérivé**, pas la SoT. Plan d'exécution détaillé
> : `/home/deploy/.claude/plans/verifier-la-vraie-logical-whistle.md` (monorepo-side).

---

## État

| Champ | Valeur |
|-------|--------|
| ADR | [[ADR-058-repository-control-plane]] (status `proposed` au 2026-05-13) |
| Phase courante | V1 PR-A en cours (cette PR) |
| Tier scoping | V1 livré ici ; V1.5 et V2 = plans séparés signal-proven |
| Acceptance | `proposed` → `accepted` après PR-G mergée + 7-14 j signal vert |

---

## Séquence V1 (8 PRs, A → H)

Toutes les PRs sont indépendamment mergeables. La fenêtre 7-14 jours entre
PR-G et PR-H est intentionnelle (signal empirique avant promotion canon).

| PR | Cible | Scope clé | Statut |
|----|-------|-----------|--------|
| **A** | vault | ADR-058 `proposed` + cette MOC + ligne MOC-Decisions | 🟡 en cours |
| **B** | monorepo | Package `@repo/registry` (Zod schemas minimal V1) | ⚪ pending |
| **C** | monorepo | 5 producteurs Layer 1 (`scripts/registry/build-*-registry.js`) | ⚪ pending |
| **D** | monorepo | Overlay Layer 2 (`.spec/00-canon/repository-registry/*.yaml`) | ⚪ pending |
| **E** | monorepo | Merge canonical (Layer 3) + freshness CI Phase 1 warn | ⚪ pending |
| **F** | monorepo | LLM entrypoint (`.claude/knowledge/REPO_MAP.md`) | ⚪ pending |
| **G** | monorepo | CI gates Phase 2 (block-new owner+domain) | ⚪ pending |
| **H** | vault | ADR-058 `proposed` → `accepted` | ⚪ pending |

---

## Architecture 3 couches (rappel ADR-058)

```
Layer 1 (auto)        Layer 2 (overlay manuel)
audit/registry/  +  .spec/00-canon/repository-registry/
{files,db,rpc,...    {ownership,domains,status-overrides,
 deps,runtime}.json   delete-policy}.yaml
        │                          │
        └────────────┬─────────────┘
                     ▼
            Layer 3 (projection générée)
            audit/registry/canonical.json
                     │
                     ▼
                Consommateurs
   • CI Gates V1 (Phase 1 warn → Phase 2 block-new)
   • .claude/knowledge/REPO_MAP.md (LLM entrypoint)
   • Future V1.5 : provenance, diff PR comments
   • Future V2 : MCP server, block-all
```

**SoT** = couple Layer 1 auto + Layer 2 overlay. **Layer 3 = projection**, jamais
SoT primaire (cf. memory `feedback_generated_artifact_is_projection_not_sot.md`).

---

## Invariants V1 (5)

| ID | Invariant | Outillage |
|----|-----------|-----------|
| V1-1 | Versioning de schéma SemVer | `schemaVersion: '1.0.0'` dans chaque entry |
| V1-2 | Déterminisme strict | JSON triés + hash SHA-256 stable 2 runs |
| V1-3 | Classification jamais forcée | `status: UNKNOWN`, `sourceConfidence: low\|medium\|high` |
| V1-4 | Schema invariants minimaux | `validate-invariants.ts` : 4 invariants critiques |
| V1-5 | Tests round-trip Zod | 1 test valide + 1 test invalide par schema |

---

## Critères d'acceptance (V1 → `accepted`)

Status passe à `accepted` quand PR-G mergée + 7-14 jours de signal empirique
vert observés. Métriques requises sur la fenêtre :

| Métrique | Seuil V1 (PR-H) | Seuil V2 (block-all) |
|----------|------------------|-----------------------|
| files inventory coverage | 100 % | 100 % |
| ownership coverage | ≥ 90 % | ≥ 95 % |
| ownership high-confidence | ≥ 70 % | ≥ 80 % |
| status known (non-UNKNOWN) | ≥ 85 % | ≥ 95 % |
| block-new false positives | 0 | 0 |
| registry_orphan_count | stable ou ↓ | stable ou ↓ |

**Aucune dépendance MCP / V1.5 / V2.** Cf. memory
`feedback_coverage_per_dimension_thresholds.md` pour la discipline
seuils-par-dimension.

---

## Out of scope explicite (ADR-058)

### Hors V1, V1.5 ou V2 (jamais dans cette lignée)
- Cleanup des dead-code candidates (plan séparé post-PR-H)
- Suppression tables orphan-candidates (plan séparé DB cleanup)
- Rename dossiers / restructure NestJS modules
- Upgrade dépendances
- ADR-049 REG-002 (canon-files registry) — reste indépendant, ADR-058 le
  complète via `relates-to`, ne supersedes pas

### Différé V1.5 (plan séparé post-PR-H + 30j stabilité)
- Provenance per artifact (in-toto v0.1)
- Diff PR comments (`peter-evans/create-or-update-comment`)
- JSON Schema export (`zod-to-json-schema`)
- Property-based testing étendu (fast-check ≥ 500 props)
- RefId URN format (`kind:domain:id`)
- Generated `.d.ts` complets
- Hermetic builders (NETWORK_BLOCK=1)
- Budget runtime + CI fail
- `classificationTrail[]` per entry

### Différé V2 (plan futur signal-proven)
- MCP server `@repo/registry-mcp` (5 tools)
- SLSA L2 complet (signed provenance, builder isolation)
- Versioned canonical artifacts (`canonical-v2.json`)
- CI Phase 3 block-all

---

## Anti-patterns à éviter

- Considérer `canonical.json` comme SoT primaire (c'est une **projection**)
- Éditer manuellement `audit/registry/*.json` (hook pre-commit refuse sauf si
  reproductible depuis sources Layer 1+2 — `npm_lifecycle_event` + hash check,
  pas marker env forgeable)
- Créer `.spec/00-canon/LLM_REPO_MAP.md` (anti-duplication `.claude/knowledge/`)
- Activer Phase 3 block-all « par discipline » (attendre signal métrique 30j vert
  sur toutes couvertures)
- Forcer une classification ambiguë en LEGACY/LIVE (préférer UNKNOWN + low conf)
- Réécrire `scripts/audit/build-deep-inventory.js` (l'étendre via flags)
- Modifier schémas Zod après PR-E sans bump major + ADR (contrat stable)
- Cleaner / refactor / upgrade AVANT PR-H

Cf. memories `feedback_v1_v1_5_v2_tiered_scoping.md`,
`feedback_generated_artifact_is_projection_not_sot.md`,
`feedback_hook_reproducibility_proof_over_env_marker.md`.

---

## Liens

### Vault
- ADR : [[ADR-058-repository-control-plane]]
- ADRs voisins : [[ADR-015-vault-single-source-of-truth]],
  [[ADR-048-canon-enforcement-coverage]], [[ADR-049-db-governance-canon-enforcement]],
  [[ADR-053-planning-live-system]]
- MOC racine : [[MOC-Decisions]] (ADR-058 indexé dans table « ADR Actifs »)
- MOC roadmap : [[MOC-Roadmap-2026]]

### Monorepo
- Plan directeur : `/home/deploy/.claude/plans/verifier-la-vraie-logical-whistle.md`
- Producteurs existants à étendre : `scripts/audit/build-deep-inventory.js`,
  `scripts/audit/build-db-usage-map.js`
- Package canonique pattern de référence : `packages/seo-roles/`
- Knowledge prose existante (consommateur F) : `.claude/knowledge/` (42 modules MD)
