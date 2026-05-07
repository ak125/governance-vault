---
id: ADR-048
title: "Canon Enforcement Coverage Audit"
status: accepted
date: 2026-05-07
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G1]
related_incidents: []
reviewed_by: ""
---

# ADR-048: Canon Enforcement Coverage Audit

## Contexte

Suite à la refondation MOC vault (PR #185 / #186 / #187 / #188 mergées 2026-05-07) qui a éliminé les duplications structurelles dans le vault et instauré le drift detector mécanique `check-moc-integrity.py`, l'**audit honnête de la robustesse du canon architectural** a révélé un déséquilibre critique :

- Le **vault** (gouvernance opérationnelle, supposé miroir) dispose désormais d'enforcement mécanique solide : hooks signés G2/G3, weekly-lint 9 checks, drift detector MOC.
- Le **canon architectural** (`.spec/00-canon/` du monorepo, désigné par G1 + ADR-015 §5) dispose d'un enforcement **asymétrique et lacunaire**.

### Audit factuel `.spec/00-canon/*` au 2026-05-07

35 fichiers totaux (15 racine + 20 dans `db-governance/`). Catégorisation par état d'enforcement :

#### ✅ Enforced mécaniquement (3 fichiers — 8.6%)

| Fichier | Enforcement | Référence |
|---|---|---|
| `gamme-md-schema.md` | Zod schema `wiki-proposal-frontmatter.schema.ts` + `automecanik-wiki/_scripts/validate-frontmatter.{py,mjs}` LIVE | ADR-039 |
| `role-matrix.md` | TS package `@repo/seo-roles` + 4 layers enforcement (router-validator, gatekeeper, etc.) LIVE | ADR-040 |
| `brand-md-schema.md` | TS schema `backend/src/config/brand-role-map.schema.ts` cite comme SoT, dérive Zod | (ad hoc) |

#### 🟡 Cités via JSDoc dans le code (5 fichiers — prose link, drift detection 0)

| Fichier | Citations | Risque |
|---|---|---|
| `architecture.md` | `cache-ttl.config.ts` (1× `@see`) | drift cache TTL non détecté si canon évolue |
| `phase2-canon.md` | `execution-registry.types.ts`, `execution-registry.constants.ts`, `content-section-policy.ts`, `execution-plan-resolver.service.ts`, `evidence-grading.constants.ts` (5× `@see`) | les constants dérivés peuvent diverger silencieusement |
| `db-governance/legacy-canon-map.md` | (récemment modifié 2026-05-05) | partiel |
| `db-governance/role-migration-registry.md` | (récemment modifié 2026-05-05) | partiel |
| `db-governance/domain-map.md` | (récemment modifié 2026-05-06) | partiel |

#### ❌ Aucun enforcement détecté (27 fichiers — 77.1%)

`repo-map.md`, `prompt-registry.md`, `pipeline-phases.md`, `phase-matrix.md`, `image-matrix-v1.md`, `image-matrix-v2.md`, `governance-policy.md`, `rules.md`, `rag-document-classification-matrix.md`, `tecdoc-integration-roadmap-v3.md`, `video-governance-p0.md`, `artefact-registry.md`, `enrichment-report.schema.json`, `conflict.schema.yaml`, et 13 fichiers `db-governance/*` non récemment modifiés.

Vérifié par `grep -rE "<filename>" --include="*.ts" --include="*.py"` : zéro programmatic consumer.

### Audit factuel des dates de modification

- `governance-policy.md`, `rules.md` : 2026-01-07 (4 mois)
- `architecture.md` : 2026-02-19 (2.5 mois)
- `repo-map.md`, `brand-md-schema.md` : 2026-03-09 / 2026-03-11 (~2 mois)
- 13 fichiers : tous datés 2026-03-14 (modifs en batch, depuis intouchés)
- `gamme-md-schema.md`, `conflict.schema.yaml`, `enrichment-report.schema.json` : 2026-04-08 (1 mois)
- 4 fichiers `db-governance/*` : 2026-05-05/06 (récents, partiels)

À comparer à : ADR-047 créé 2026-05-07. **Le canon est plus vieux que ~80% des ADRs qui prétendent y conformer.**

### Risques identifiés

1. **Drift silencieux canon → code (élevé)** : 77% du canon est prose-only sans gate. Une modif schéma applicatif peut diverger arbitrairement longtemps sans signal.
2. **Single-signer SPOF (modéré)** : Fafa seul signe G1, ADR-015, modifs canon. Pas de peer review automatique, pas d'invariant cross-repo.
3. **Fraîcheur non vérifiée (élevé)** : `governance-policy.md` et `rules.md` datent de janvier ; aucun signal automatique si stale.
4. **Asymétrie enforcement (paradoxe)** : le miroir (vault) est mieux gardé que la source (canon). Inverse de ce qui devrait être.

### Trajectoire saine déjà observable

ADR-039 (Zod), ADR-040 (seo-roles + 4 layers), dep-cruiser planifié (memory `roadmap-p0-p3-canon-repos-20260501` "P3"). Le pattern existe — il faut le systématiser.

## Décision

**Option D — Hybride audit + migration progressive (cf. Options Considérées ci-dessous)**.

3 axes parallèles sur 3 sprints :

### Axe 1 — Audit one-shot fichier-par-fichier (sprint 1)

Pour chaque fichier de `.spec/00-canon/*`, ouvrir une row dans un nouveau registry vault `ledger/canon-coverage/REG-002-canon-files.md` :

| Champ | Type | Source |
|---|---|---|
| `path` | string | path FS relatif |
| `state` | enum {`enforced`, `prose-with-derivation`, `prose-only`, `deprecated`} | audit humain |
| `consumers` | array<string> | grep direct ou ADR référent |
| `enforcement_mechanism` | nullable string | "Zod ADR-039", "TS package ADR-040", null, ... |
| `last_modified` | date | `git log -1 --format=%ai` |
| `last_referenced_adr` | nullable string | dernier ADR qui le cite |
| `freshness_threshold_days` | int (default 180) | seuil au-delà duquel flag |

Owner audit : Fafa (single-signer assumé pour cette phase, peer review possible après).

### Axe 2 — Migration progressive prose → enforcement (sprints 2-3)

Priorité par risque (cf. tableau Risques) :

- **P0 (sprint 2)** : `architecture.md` → dependency-cruiser pour invariants module/import (déjà planifié roadmap P3, accélérer). `phase2-canon.md` → tests d'intégration sur transitions de phase (5 fichiers TS le citent, candidats naturels).
- **P1 (sprint 2)** : `prompt-registry.md` → schema YAML/JSON Zod (les prompts sont structurés, schématisables). `repo-map.md` → généré automatiquement depuis le filesystem (drift = diff visible).
- **P2 (sprint 3)** : `image-matrix-v1/v2.md`, `pipeline-phases.md`, `rag-document-classification-matrix.md` — schemas dérivés.
- **P3 (sprint 3)** : `db-governance/*` (20 fichiers) → audit sub-projet, possiblement délégué à un ADR fils dédié (le scope est conséquent).

Pas tout le canon en une fois — priorisation par risque mesuré (consommateurs réels, fraîcheur, criticité applicative).

### Axe 3 — Cron `canon-freshness-check` (sprint 1, low-cost)

Nouveau script vault `_scripts/check-canon-freshness.py` exécuté en weekly-lint :

- Pour chaque fichier listé dans `REG-002-canon-files.md`, vérifier `last_modified >= today - freshness_threshold_days`
- Pour chaque ADR récent (< 6 mois), vérifier qu'aucun fichier canon qu'il référence n'est plus vieux que lui de > 90 jours
- Sortie warn-only initialement (cohérent stratégie escalade J+30 du PR-3 check-moc-integrity)

Pattern réutilise `check-moc-integrity.py` (orchestrator `run_modern`, `--json` flag, contrat `{check, findings, summary}`).

### Axe transverse — Cross-repo invariant vault ↔ monorepo (sprint 3)

Un nouveau check `_scripts/check-canon-cross-repo.py` qui :
- Pour chaque mention `[[ADR-NNN]]` ou `.spec/00-canon/X` dans un ADR vault, vérifie l'existence physique dans le monorepo
- Pour chaque fichier `.spec/00-canon/*`, vérifie qu'au moins un ADR récent le référence (sinon flag "potentiellement orphan")
- Branché en weekly-lint vault, requiert accès filesystem au monorepo (déjà disponible via `--monorepo PATH` du weekly-lint actuel — pattern `check-canon-backlinks.py`)

## Options Considérées

### Option A — Audit one-shot + ADR-stack par gap

**Description** : Pattern "9 PRs canon SEO" (memory `seo-roles-canon-shipped-20260505`) appliqué au canon technique global. 1 audit massif, puis 1 ADR + PR par fichier pour ajouter enforcement.

**Avantages** : Coverage 100% rapide, traçabilité ADR par fichier, alignement total avec le pattern qui a marché pour seo-roles.

**Inconvénients** : Surcharge cognitive (15-25 ADRs supplémentaires en peu de temps), risque de bricolage par fatigue, ne respecte pas le principe "priorisation par risque" — traite tous les fichiers à égalité même les peu critiques.

### Option B — Cron `canon-freshness-check` léger + rappels manuels

**Description** : Pas de migration prose → enforcement. Juste un signal régulier "ce fichier canon est stale" via weekly-lint.

**Avantages** : Coût initial minimal (1 script + 1 ligne weekly-lint).

**Inconvénients** : Ne résout pas le problème de fond (drift silencieux entre canon et code). Détecte la fraîcheur temporelle, pas la cohérence sémantique. Insuffisant.

### Option C — Migration progressive prose → schémas exécutables uniquement

**Description** : Continuer la trajectoire ADR-039/ADR-040 sans audit préalable. Migrer fichier par fichier au gré de l'évolution applicative.

**Avantages** : Zero audit cost, migration "naturelle" par le code.

**Inconvénients** : Aucune vue d'ensemble du gap, priorisation aléatoire (qui pousse migre ce qui le concerne, pas forcément les fichiers les plus critiques). Le risque "Fafa hands-on" identifié reste.

### Option D — Hybride A+C (RETENUE)

**Description** : Audit one-shot léger (axe 1) qui dimensionne l'ampleur réelle, puis migration progressive priorisée par risque mesuré (axe 2), avec cron freshness léger en filet (axe 3) et invariant cross-repo (axe transverse).

**Avantages** :
- Vue d'ensemble immédiate (audit sprint 1 = 1 fichier registry)
- Priorisation par risque mesuré (cf. tableau Risques)
- Coût initial proportionné (pas 25 ADRs d'un coup)
- Filet temporal en parallèle (cron freshness)
- Réutilise les patterns réussis (check-moc-integrity, ADR-039 Zod, ADR-040 packages)
- Pas de bricolage : chaque axe a une SoT canonique unique

**Inconvénients** :
- Coordination 3 axes en parallèle
- Sprint 3 conséquent (db-governance/* possiblement à déléguer en ADR fils)

## Conséquences

### Positives attendues

- **Détection automatique** de drift canon ↔ code en production sur les fichiers migrés (objectif : 80% de coverage à fin sprint 3)
- **Fin du paradoxe** "miroir mieux gardé que source"
- **Onboarding contributeurs externes facilité** : canon vérifiable mécaniquement, plus juste prose à croire
- **Audit-trail mécanique** pour modifications canon (au-delà signature Fafa seul)
- **Single-signer SPOF mitigé** par cron + invariant cross-repo (pas remplacé, mais doublé d'une vérification machine)

### Négatives attendues

- **Coût initial axe 1 audit** : estimé 1-2 jours (15 fichiers racine + 20 db-governance, scan + classification)
- **Coût axe 2 migration P0+P1** : estimé 1 sprint (5 fichiers, dependency-cruiser + 2 schemas Zod + 1 generator filesystem)
- **Coût axe 2 migration P2** : estimé 1 sprint (3 fichiers, schemas Zod)
- **Coût axe 3 cron** : 1 demi-journée (~150 lignes Python, pattern check-moc-integrity)
- **Coût axe transverse cross-repo check** : 1 journée
- **Charge récurrente** : weekly-lint passe de 9 à 11 checks (+2)
- **Frottement modifs canon urgentes** : un gate supplémentaire (acceptable, on a déjà G2/G3 + signed commits)
- **Db-governance/* sub-projet** : potentiellement 1 ADR fils dédié (ADR-049 ?) si scope > 1 sprint

### Neutres

- Aucun impact sur `governance-vault/` (déjà enforced post-PR-3)
- Aucun impact sur les ADRs qui référencent G1 — leur autorité demeure inchangée
- Compatible avec la trajectoire existante (ADR-039, ADR-040, dep-cruiser P3 déjà planifié)

## Critères de Succès

Quantifiés et auditables :

- [ ] **C1 — Audit complet (fin sprint 1)** : `ledger/canon-coverage/REG-002-canon-files.md` créé, tous les 35 fichiers `.spec/00-canon/*` ont une row avec `state` explicite (enforced / prose-with-derivation / prose-only / deprecated). 100% coverage.
- [ ] **C2 — Migration P0+P1 (fin sprint 2)** : minimum 5 fichiers prose-only migrés vers enforcement mécanique (`architecture.md` via dep-cruiser, `phase2-canon.md` via tests d'intégration, `prompt-registry.md` via Zod, `repo-map.md` via generator, `pipeline-phases.md` via tests).
- [ ] **C3 — Cron freshness LIVE (fin sprint 1)** : `_scripts/check-canon-freshness.py` actif en weekly-lint mode `--warn`, reporting hebdomadaire opérationnel.
- [ ] **C4 — Cross-repo invariant LIVE (fin sprint 3)** : `_scripts/check-canon-cross-repo.py` actif en weekly-lint, validation bidirectionnelle vault ↔ monorepo, mode `--warn` initialement.
- [ ] **C5 — Coverage ≥ 80% à fin sprint 3** : sur les 35 fichiers, ≥ 28 ont un état `enforced` ou `deprecated` (les 20%) restants peuvent être `prose-with-derivation` justifié, 0 `prose-only` non-justifié.

## Implémentation

### Sprint 1 (S+1, 1 sem)

- [ ] PR vault : `feat(adr-048): canon-coverage registry REG-002 + axe 1 audit` — fichier `ledger/canon-coverage/REG-002-canon-files.md` peuplé, audit factuel des 35 fichiers
- [ ] PR vault : `feat(scripts): check-canon-freshness.py + weekly-lint integration` — axe 3
- [ ] PR vault : `chore(adr-049): draft db-governance audit (proposed)` SI scope db-governance > 1 sprint (à évaluer après axe 1)

### Sprint 2 (S+2, 1 sem)

- [ ] PR monorepo : `feat(spec-canon): dependency-cruiser invariants enforcing architecture.md` — P0
- [ ] PR monorepo : `feat(seo): integration tests enforcing phase2-canon.md transitions` — P0
- [ ] PR monorepo : `feat(prompt-registry): Zod schema + validator` — P1
- [ ] PR monorepo : `feat(spec-canon): repo-map auto-generator + drift CI` — P1

### Sprint 3 (S+3, 1 sem)

- [ ] PR monorepo : `feat(spec-canon): pipeline-phases tests + image-matrix Zod + rag-classification schema` — P2
- [ ] PR vault : `feat(scripts): check-canon-cross-repo.py + weekly-lint integration` — axe transverse
- [ ] Si db-governance hors scope : merge ADR-049 et fermeture ADR-048 avec C5 partiel documenté

### Trigger de cette ADR

Cette ADR est **proposed** à 2026-05-07. Pour passer `accepted` :

1. Review humaine par Fafa (decision_makers signataire)
2. Validation des Critères de Succès (sont-ils atteignables ? réalistes ?)
3. Validation du phasing (3 sprints = 3 sem, OK ?)
4. Merge PR avec status flip `proposed → accepted`

Issue GitHub liée : #189 (deadline 2026-05-21).

## Suivi

- **Owner principal** : Fafa
- **Reviewers potentiels** : à identifier (peer review G3, possiblement avec un agent externe en assist)
- **Deadline finalisation décision** : 2026-05-21 (T+14j depuis création draft)
- **Trigger d'escalation** : si non finalisé sous 14j, alerter via issue #189 et considérer comme régression d'engagement
- **Métrique de progression** : reporting weekly via `99-meta/canon-coverage-snapshot.json` (à produire par le check-canon-freshness)

---

*Proposé le: 2026-05-07*
*Finalisé (sections élaborées) le: 2026-05-07*
*Accepté le: 2026-05-07*
*Dernière revue: 2026-05-07*
