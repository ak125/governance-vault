---
id: REG-002
title: Canon Coverage Registry — .spec/00-canon/* enforcement audit
status: active
version: 1.0.0
last_audit: 2026-05-07
total_files: 35
related_adr: ADR-048
---

# REG-002 Canon Coverage Registry

Audit factuel fichier-par-fichier de `.spec/00-canon/*` du monorepo `nestjs-remix-monorepo`. Établit l'état d'enforcement de chaque fichier canon — quel artefact downstream le consomme, quelle date de dernière modification, quel ADR le référence.

Source de vérité pour le check `_scripts/check-canon-freshness.py` (PR sprint 1 PR-B). Audit livrable du critère **C1** d'[[ADR-048-canon-enforcement-coverage|ADR-048]].

## Méthode d'audit

- **Liste fichiers** : `find .spec/00-canon -type f \( -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \)` (35 fichiers, 15 racine + 20 dans `db-governance/`)
- **Date de dernière modification** : `stat -c '%y' <fichier>` (filesystem time, pas git log — historiquement plus fidèle au "last touched")
- **Consumers programmatiques** : `grep -rE "<filename>" --include="*.ts" --include="*.py" --include="*.json" --include="*.yaml" backend/ packages/ scripts/ workspaces/ 2>/dev/null | grep -v node_modules | grep -v ".spec/"` — zéro hit pour les 27 prose-only fichiers
- **ADR refs** : `grep -l "<basename>" ledger/decisions/adr/*.md` excluant ADR-048 (l'audit ADR référence circulairement tous les fichiers, pas significatif)
- **State** : classification sur la base des consumers réels et du pattern d'enforcement existant

## Quick Stats

| State | Count | % |
|-------|-------|---|
| **enforced** | 3 | 8.6% |
| **prose-with-derivation** | 5 | 14.3% |
| **prose-only** | 27 | 77.1% |
| **deprecated** | 0 | 0% |
| **TOTAL** | **35** | 100% |

## Schéma de la table

| Champ | Type | Description |
|---|---|---|
| `path` | string | path FS relatif depuis `.spec/00-canon/` |
| `state` | enum | `enforced` / `prose-with-derivation` / `prose-only` / `deprecated` |
| `enforcement_mechanism` | nullable string | mécanisme actuel (Zod, TS package, dep-cruiser, ...) |
| `consumers` | nullable string | artefacts downstream qui consomment ce fichier |
| `last_modified` | date ISO | filesystem mtime |
| `last_referenced_adr` | nullable string | ADR le plus récent qui le référence (excluant ADR-048) |
| `freshness_threshold_days` | int | défaut 180j, surcharge possible per-file pour fichiers très stables |

## Registry — fichiers racine `.spec/00-canon/*` (15 fichiers)

| path | state | enforcement_mechanism | consumers | last_modified | last_referenced_adr | freshness_threshold_days |
|---|---|---|---|---|---|---|
| `architecture.md` | prose-with-derivation | JSDoc `@see` cite | `backend/src/config/cache-ttl.config.ts` | 2026-02-19 | ADR-015 | 180 |
| `artefact-registry.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |
| `brand-md-schema.md` | enforced | TS schema cite comme SoT | `backend/src/config/brand-role-map.schema.ts` (Zod-derived) | 2026-03-11 | (none) | 180 |
| `conflict.schema.yaml` | prose-only | (none) | (none) | 2026-04-08 | ADR-029 | 365 |
| `enrichment-report.schema.json` | prose-only | (none) | (none) | 2026-04-08 | ADR-029 | 365 |
| `gamme-md-schema.md` | enforced | Zod via `wiki-proposal-frontmatter.schema.ts` (ADR-039) | `automecanik-wiki/_scripts/validate-frontmatter.{py,mjs}` LIVE | 2026-04-08 | ADR-026, ADR-029 | 180 |
| `governance-policy.md` | prose-only | (none) | (none) | 2026-01-07 | ADR-018 | 180 |
| `image-matrix-v1.md` | prose-only | (none) | (none) | 2026-02-24 | (none) | 365 |
| `image-matrix-v2.md` | prose-only | (none) | (none) | 2026-02-25 | (none) | 365 |
| `phase2-canon.md` | prose-with-derivation | JSDoc `@see` cite (5 fichiers TS) | `execution-registry.{types,constants}.ts`, `content-section-policy.ts`, `execution-plan-resolver.service.ts`, `evidence-grading.constants.ts` | 2026-03-14 | (none) | 180 |
| `phase-matrix.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |
| `pipeline-phases.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |
| `prompt-registry.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |
| `rag-document-classification-matrix.md` | prose-only | (none) | (none) | 2026-03-15 | (none) | 180 |
| `repo-map.md` | prose-only | (none) | (none) | 2026-03-09 | (none) | 90 |
| `role-matrix.md` | enforced | TS package `@repo/seo-roles` + 4 layers (ADR-040) | router-validator, gatekeeper, content-quality-gate, etc. | 2026-03-14 | (none) | 180 |
| `rules.md` | prose-only | (none) | (none) | 2026-01-07 | ADR-006, ADR-013, ADR-014 | 180 |
| `tecdoc-integration-roadmap-v3.md` | prose-only | (none) | (none) | 2026-03-28 | (none) | 365 |
| `video-governance-p0.md` | prose-only | (none) | (none) | 2026-02-24 | (none) | 365 |

## Registry — sous-répertoire `db-governance/*` (20 fichiers)

Sous-projet dense. Si la migration P3 sprint 3 dépasse le scope alloué, ce sous-arbre fera l'objet d'un ADR fils dédié (**ADR-049 candidate**, à évaluer fin sprint 1).

| path | state | enforcement_mechanism | consumers | last_modified | last_referenced_adr | freshness_threshold_days |
|---|---|---|---|---|---|---|
| `db-governance/change-control-plan.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |
| `db-governance/domain-map.md` | prose-only | (récemment modifié) | (none) | 2026-05-06 | (none) | 90 |
| `db-governance/execution-map.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |
| `db-governance/final-exec-summary.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 365 |
| `db-governance/full-structural-audit.md` | prose-only | (none) | (none) | 2026-03-15 | (none) | 365 |
| `db-governance/legacy-canon-map.md` | prose-only | (récemment modifié) | (none) | 2026-05-05 | ADR-040 | 90 |
| `db-governance/perf-findings.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 365 |
| `db-governance/phase-2a-rpc-audit-results.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 365 |
| `db-governance/phase-2b-first-monitoring-review.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 365 |
| `db-governance/phase-2b-rpc-audit-results.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 365 |
| `db-governance/pr4b-mcp-inventory-2026-05-05.md` | prose-only | (récemment modifié) | (none) | 2026-05-05 | ADR-040 | 90 |
| `db-governance/role-implementation-map.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |
| `db-governance/role-migration-registry.md` | prose-only | (récemment modifié) | (none) | 2026-05-05 | (none) | 90 |
| `db-governance/schema-governance-matrix.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |
| `db-governance/sql-governance-rules.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |
| `db-governance/sql-migration-checklist.md` | prose-only | (none) | (none) | 2026-03-14 | (none) | 180 |

## Notes d'audit

### Files marqués `enforced` (3 — l'objectif coverage à fin sprint 3 est ≥80%, soit 28+)

- **`gamme-md-schema.md`** : enforced via Zod schema `wiki-proposal-frontmatter.schema.ts` (backend) + `validate-frontmatter.{py,mjs}` (automecanik-wiki) — ADR-039 LIVE
- **`role-matrix.md`** : enforced via TS package `@repo/seo-roles` + 4 layers (router-validator, gatekeeper, content-quality-gate, frontend badges) — ADR-040 LIVE
- **`brand-md-schema.md`** : enforced via `backend/src/config/brand-role-map.schema.ts` qui cite explicitement ce fichier comme SoT et dérive un schema Zod — ad hoc, pas d'ADR formelle (à formaliser)

### Files marqués `prose-with-derivation` (5)

JSDoc `@see` ou commentaire pointe vers le canon, des constants/types sont **dérivés** par un humain. **Pas de drift detection automatique** — un changement dans le canon nécessite un humain pour propager dans les constants. Risque de désynchronisation silencieuse.

- `architecture.md` : 1 ref dans `cache-ttl.config.ts`
- `phase2-canon.md` : 5 refs dans `execution-registry`, `content-section-policy`, `execution-plan-resolver`, `evidence-grading`

### Files marqués `prose-only` (27 — vraie dette d'enforcement)

Aucun consumer programmatique détecté. Le canon vit en prose, le code peut diverger arbitrairement longtemps sans signal. Cible prioritaire de la migration sprint 2-3 d'ADR-048.

**Priorité P0 sprint 2** (par criticité applicative + récence ADR référent) :
- `architecture.md` (déjà prose-with-derivation, candidate dependency-cruiser)
- `phase2-canon.md` (déjà prose-with-derivation, candidate tests d'intégration)

**Priorité P1 sprint 2** (schématisable rapidement) :
- `prompt-registry.md` (Zod schema pour structure prompts)
- `repo-map.md` (auto-generator depuis filesystem)

**Priorité P2 sprint 3** :
- `pipeline-phases.md`, `image-matrix-v1/v2.md`, `rag-document-classification-matrix.md`

**Priorité P3 sprint 3 (potentiellement ADR-049 fils)** :
- `db-governance/*` 20 fichiers (densité élevée, plusieurs récemment modifiés mais pas mécaniquement enforced)

### Files marqués `deprecated` (0)

Aucun fichier identifié comme deprecated à ce stade. Audit à compléter : si certains fichiers (ex. `image-matrix-v1.md` superseded par `v2.md` ?) sont obsolètes, marquer explicitement.

## Voir aussi

- [[ADR-048-canon-enforcement-coverage]] — décision parente, scope, options, critères de succès
- [[REG-001-agents]] — pattern registry suivi par REG-002 (frontmatter `id/title/status/version/last_audit/total_*`)
- `_scripts/check-canon-freshness.py` (PR-B sprint 1) — consommateur de cette registry pour cron freshness weekly-lint

---

*Audit livré le 2026-05-07 (axe 1 ADR-048 sprint 1)*
*Owner : Fafa (decision_makers ADR-048)*
*Prochaine revue : à chaque ADR qui modifie l'état d'enforcement d'un fichier canon (ex. ADR migration P0/P1/P2)*
