---
title: 'Session handoff — MVP G6 + ADR-033 wiki alignment (2026-04-29 → 2026-04-30)'
type: handoff
status: open
date: 2026-04-30
related_adr: ['ADR-031', 'ADR-032', 'ADR-033']
related_prs:
  - https://github.com/ak125/automecanik-wiki/pull/8
  - https://github.com/ak125/automecanik-raw/pull/6
related_routines:
  - trig_01Tq3Z8ohU29suDmnezZhWnG    # DB freeze J+2 (2026-05-02)
  - trig_01LKqhkSKddud3ywGM9Yjb6z    # Revue ADR-033 J+30 (2026-05-29)
tags: [mvp, adr-033, adr-032, wiki, raw, handoff, follow-ups]
---

# Session handoff — MVP G6 + ADR-033 wiki alignment

> Document de transition. Session 2026-04-29 → 2026-04-30 (Plan rev 6 *verifier-dans-existant-si-starry-feigenbaum* + plan d'exécution *flickering-napping-kite*). Continuera dans une autre session.

## 1. Ce qui a été livré

### PRs ouvertes (à reviewer + merger)

| PR | Repo | Branche | Commits | État |
|---|---|---|---|---|
| **#8** | `ak125/automecanik-wiki` | `feat/mvp-g2-g10-bootstrap` | `baa5793`, `768abd9` | Open, mergeable, CI partiellement green |
| **#6** | `ak125/automecanik-raw` | `feat/mvp-g4-manifests` | `af7f6ff` | Open, mergeable |

### MVP §6 plan rev 6 (9/9 livrés)

- G1 (clone) ✅
- G2 (3 docs `_meta/`) ✅
- G3 (5 templates, dont diagnostic archivé per ADR-033 §D3) ✅
- G4 (manifests raw : `source-classification.md` + `tombstones.json` + workflow `raw-checksum-verify.yml`) ✅
- G5 (`entity-registry.json` peuplé 10 entrées) ✅
- G8 (workflows CI : `wiki-quality-gates.yml` + `wiki-protected-paths.yml` + `raw-checksum-verify.yml`) ✅
- G9-A (4 scripts Python : `validate-frontmatter.py`, `quality-gates.py` avec 9 nouveaux gates ADR-033/032, `compute-confidence-score.py`, `compute-symptom-confidence.py`) ✅
- G10 (skill `wiki-proposal-writer` scaffold à `app/.claude/skills/`) ✅
- G6 (5 pilotes : `plaquette-de-frein` enrichi v2.0.0 + `lada-granta` + `dacia` + `livraison` + `filtre-a-air` ; substitution `bruit-freinage` → `filtre-a-air` forcée par ADR-033 §D3) ✅

### Bonus livrés au-delà du plan

- Schema bump v1.0.0 → **v2.0.0** (cohabitation pendant migration Phase 4 ADR-033)
- `_meta/source-catalog.yaml` (registre canonique slugs sources stables, requis par ADR-033 §D1)
- pytest suite + 7 fixtures (positives + 5 négatives ciblées) — **8/8 PASS**
- Bloc `entity_data.maintenance` ADR-032 §D1 cohabité avec `diagnostic_relations[]` ADR-033 §D1
- 9 nouveaux gates `blocked_reasons` documentés et testés

### Validations finales

- 18/18 fichiers PASS `validate-frontmatter.py --all`
- 18/18 PASS `quality-gates.py --all` (1 WARN Brembo non bloquant)
- 8/8 PASS pytest fixtures
- 0 régression vs main
- 0 anti-pattern ADR-033 §D3 introduit

## 2. Vérification IsAdminGuard (audit utilisateur — 2026-04-30)

**Contexte** : audit utilisateur signalait que `IsAdminGuard` n'apparaîtrait pas dans l'inventaire `AdminModule`. Vérification empirique côté monorepo `nestjs-remix-monorepo` :

| Constat | Évidence |
|---|---|
| `IsAdminGuard` **est défini** | `backend/src/auth/is-admin.guard.ts:10` (`export class IsAdminGuard implements CanActivate`) |
| `IsAdminGuard` **est registered comme provider** | `backend/src/auth/auth.module.ts:43` (provider AuthModule) |
| `IsAdminGuard` **est largement utilisé** | ≥ 25 usages identifiés via `grep -rn IsAdminGuard backend/src/` |

**Inventaire usage `AdminModule` (`backend/src/modules/admin/controllers/`)** : confirmé importé + utilisé via `@UseGuards(AuthenticatedGuard, IsAdminGuard)` dans :

- `admin-gammes-seo-update.controller.ts:33`
- `admin-rag-ingest.controller.ts:26`
- `admin-root.controller.ts:13`
- `admin-health.controller.ts:9`
- `admin-gammes-seo-aggregates.controller.ts:20`
- `admin-gammes-seo-vlevel.controller.ts:23`
- `seo-cockpit.controller.ts:31`
- `admin-r8-vehicle.controller.ts:15`
- `admin-gammes-seo-thresholds.controller.ts:29`
- `admin-buying-guide.controller.ts:15`

**Pattern canonique observé** : `import { IsAdminGuard } from '@auth/is-admin.guard'` puis `@UseGuards(AuthenticatedGuard, IsAdminGuard)` au niveau controller.

**Verdict** : l'audit utilisateur signalant l'absence d'`IsAdminGuard` dans `AdminModule` est **incorrect** — le guard existe, est provided par `AuthModule`, et est utilisé sur 10+ controllers admin en plus de seo, gamme-rest, etc. **Aucune correction du pattern `@UseGuards(IsAdminGuard)` n'est nécessaire**.

**Note** : si la PR mentionnée par l'audit utilisateur cible un nouveau controller admin, l'import canonique à utiliser est `import { IsAdminGuard } from '@auth/is-admin.guard'` et le décorateur canonique est `@UseGuards(AuthenticatedGuard, IsAdminGuard)`.

## 3. Routines `/schedule` programmées (auto-fire)

| Routine | Fire | URL | Mission |
|---|---|---|---|
| `trig_01Tq3Z8ohU29suDmnezZhWnG` | 2026-05-02 09:00 UTC | https://claude.ai/code/routines/trig_01Tq3Z8ohU29suDmnezZhWnG | Ouvrir INC-2026-XXX + draft ADR-034 sur DB freeze probas non sourcées (`is_trusted: false` sur `__diag_symptom_cause_link`) |
| `trig_01LKqhkSKddud3ywGM9Yjb6z` | 2026-05-29 09:00 UTC | https://claude.ai/code/routines/trig_01LKqhkSKddud3ywGM9Yjb6z | Audit ADR-033 §"Revue planifiée" J+30 (4 critères) + propose bump status `proposed → accepted` |

## 4. Dette technique connue (à corriger avant phase Maturité)

### P0 — bloquants

1. **Sources stub dans `_meta/source-catalog.yaml`** : 3 entrées (`oem_renault_clio_iii_workshop`, `tecdoc_15_02_01_brake_noise`, `oem_filter_maintenance_general`) ont `archived_at` pointant sur fichiers inexistants. Soit capturer les vraies sources web-clip, soit downgrader le `type` (et donc `confidence` max).
2. **Slugs convention DB à vérifier** : mes 5 entrées `diagnostic_relations[].symptom_slug` dans `plaquette-de-frein.md` utilisent underscore (`bruit_grincement_freinage`). Vérifier `__diag_symptom.slug` réel en DB (lookup Supabase) — ces slugs doivent matcher l'inventaire DB pour que la migration Phase 4 ADR-033 fonctionne.

### P1 — important

3. **Skill `wiki-proposal-writer`** scaffolded ce matin référence l'ancienne convention `entity_data.symptoms[]`. À mettre à jour pour produire `diagnostic_relations[]` (canon ADR-033) — c'est la Phase 5 ADR-033, 1 PR monorepo.
4. **`pre-commit install`** non exécuté localement → mes 3 commits ne sont pas passés par les hooks Node.js existants (gitleaks, mdformat, validate-frontmatter.mjs). À activer avant la prochaine session.
5. **`lineage_id` UUIDv7** manquant sur les 5 pilotes G6. Schema le supporte mais ne le rend pas obligatoire ; à compléter pour traçabilité.

### P2 — confort

6. **Brembo WARN** dans `proposals/renault-megane-3.md` — gate `pollution_detected` flag la mention de marque. Whitelist contextuelle ou rephrase.
7. **`migrate-template.py` (G9-B)** absent → fiches v1.0.0 restent v1.0.0 par inertie. À écrire en Maturité.

## 5. Dépendances et séquencement Maturité

```
[P0 : merge PR #8 + #6]
       │
       ▼
[Routine 1 J+2 fire]   [Sources stub fix]   [Phase 5 skill update]
       │                       │                      │
       └───────────┬───────────┴──────────────────────┘
                   ▼
       [Phase 1 ADR-033 monorepo : GAMME_PAGE_CONTRACT v2]
                   │
                   ▼
       [Phase 2 ADR-033 : validateur TS CI]
                   │
                   ▼
       [Phase 3 ADR-033 : cron export diag-canon-slugs.json]
                   │
                   ▼
       [Phase 4 ADR-033 : migration 500+ fiches gamme]
                   │
                   ▼
       [G9-B Maturité : wiki-readiness-check.py + migrate-template.py]
                   │
                   ▼
       [G7 byte-identity raw migration]
                   │
                   ▼
       [Cron audit hebdo + Rollback drill C4]
                   │
                   ▼
       [Routine 2 J+30 fire — audit ADR-033 §Revue planifiée]
                   │
                   ▼
       [C1-C6 §9 → wiki-readiness-check.py = READY ?]
                   │
                   ▼
       [ADR transition Partie 3 — consommateurs unlocked]
```

## 6. Plans et fichiers de référence

- Plan source : `/home/deploy/.claude/plans/verifier-dans-existant-si-starry-feigenbaum.md` (Plan rev 6 MVP)
- Plan d'exécution session : `/home/deploy/.claude/plans/flickering-napping-kite.md` (Phase 1 partielle ADR-033)
- ADR-031 (vault, accepted 2026-04-28) : `ledger/decisions/adr/ADR-031-four-layer-content-architecture.md`
- ADR-032 (vault, accepted 2026-04-29, PR #107) : `ledger/decisions/adr/ADR-032-diagnostic-maintenance-unification.md`
- ADR-033 (vault, proposed 2026-04-29, PR #108 commit `77085ef`) : `ledger/decisions/adr/ADR-033-wiki-gamme-diagnostic-relations-contract.md`

## 7. Reprise — étapes de la prochaine session

**Action immédiate (J+0 à J+2)** :
1. Reviewer + merger PR wiki #8 puis raw #6 (sinon canon pas en place)
2. Corriger les 3 sources stub dans `_meta/source-catalog.yaml`
3. Lookup Supabase MCP : `SELECT slug FROM __diag_symptom` → réaligner `plaquette-de-frein.md` `diagnostic_relations[].symptom_slug`
4. Activer `pre-commit install --install-hooks` localement

**Action sous 1 semaine (J+3 à J+9)** :
5. Phase 1 ADR-033 monorepo : `automecanik-rag/docs/GAMME_PAGE_CONTRACT.md` v1→v2 + `template/new-gamme.md` + schema JSON monorepo
6. Phase 5 ADR-033 : update `app/.claude/skills/wiki-proposal-writer/SKILL.md` pour `diagnostic_relations[]`
7. Phase 2 ADR-033 : validateur TS `scripts/wiki/validate-gamme-diagnostic-relations.ts` + CI bloquante

**Action sous 2 semaines (J+10 à J+16)** :
8. Phase 3 ADR-033 : cron nightly `scripts/wiki/export-diag-canon-slugs.ts` + commit `exports/diag-canon-slugs.json` vers wiki
9. Phase 4 ADR-033 : migration progressive `scripts/wiki/migrate-symptoms-to-relations.ts` (`--dry-run` + `--per-system freinage` en pilote)
10. Routine 1 fire 2026-05-02 → reviewer ADR-034 vault PR

**Action sous 1 mois (J+17 à J+30)** :
11. G9-B Maturité : `wiki-readiness-check.py` + `migrate-template.py`
12. CI scheduled `wiki-quality-audit.yml` cron lundi 02:00 UTC
13. Rollback drill C4 sur fiche test
14. Routine 2 fire 2026-05-29 → audit ADR-033 J+30, possible bump status `proposed → accepted`

**Critère go Partie 3** : `wiki-readiness-check.py = READY` (les 6 C1-C6 §9 verts simultanément).

## 8. Garde-fous utilisateur (à ne pas oublier dans la prochaine session)

> 1. *« Ce qui vient du RAG dans raw n'est pas la vérité. »* → toute source RAG = `trust_level: to_verify` jusqu'à corroboration externe.
> 2. *« Aligner sur l'existant n'est pas une justification de design. »* → trancher sur les mérites techniques, pas sur le statu quo.
> 3. *« Une valeur d'enum schema (`entity_type: diagnostic`) n'implique pas un répertoire physique de fiches wiki. »*
> 4. *« Symptômes vivent dans `__diag_symptom` (rattachés à `__diag_system`). Fiches gamme R3 ne portent que les symptômes auxquels la pièce peut contribuer. »* (ADR-033)
> 5. *« Validation par symptôme, pas globale. `source_policy` enum explicite. »*
> 6. *« Brochure (Bosch FAD, Valeo formation) ≠ source high. »*
> 7. *« Données DB non sourcées en système live = exposition produit immédiate. »* (urgence DB freeze)
> 8. *« Toujours inclure un pilote non-safety (cas edge) pour vérifier que les gates ne sur-bloquent pas. »*
> 9. *« Le symptôme appartient au SYSTÈME, pas à la PIÈCE. La pièce **peut contribuer** via `relation_to_part: possible_cause | symptom_amplifier | secondary_effect`. »* (ADR-033 verrou conceptuel)
> 10. **Décisive ADR-033** : *« Bloc canon = `diagnostic_relations[]` top-level. `evidence.diagnostic_safe` (défaut `false`) sépare preuve SEO vs preuve diagnostic-live. »*
> 11. **Décisive process** : *« Avant de canoniser un design contenu, vérifier le canon vault (ADR-* récents). »*
> 12. **Décisive process** : *« Pas de bricolage. Pas de hybride transitoire. Big-bang quand la chaîne est prête. »*
