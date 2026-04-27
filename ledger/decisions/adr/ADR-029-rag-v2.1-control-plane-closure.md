---
id: ADR-029
title: "RAG v2.1 Control Plane Closure — State Machine 7-Stage + Emitter/Detector"
status: proposed
date: 2026-04-25
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
related_rules: ["G1", "G2", "G3"]
related_incidents: []
related_adr: ["ADR-015", "ADR-022"]
reviewed_by: null
---

# ADR-029: RAG v2.1 Control Plane Closure — State Machine 7-Stage + Emitter/Detector

## Contexte

Le 2026-04-07, le commit [`c675c9a6`](https://github.com/ak125/nestjs-remix-monorepo/commit/c675c9a6)
a mergé sur `main` la spec RAG v2.1 :

- `.spec/00-canon/enrichment-report.schema.json` — state machine 7 stages
  (`v5_ssot`, `v5_audited`, `v5_enriched`, `v5_qa_passed`, `v5_indexed`, `v5_blocked`,
  `v5_pending_review`), 6 modes d'exécution (`audit_only`, `enrich_dry_run`,
  `enrich_write`, `qa_only`, `qa_write`, `index_ready_check`), validators R0-R8,
  decision matrix (`PROMOTE_L1`, `KEEP_L2`, `BLOCKED`, `PENDING_REVIEW`)
- `.spec/00-canon/conflict.schema.yaml` — `_conflicts[]` par gamme avec source tier A/B/C
- `.spec/00-canon/gamme-md-schema.md` — extension `lifecycle.stage` v5

**Data plane (frontmatters .md)** : largement appliqué entre le 2026-04-04 et le 2026-04-11.
État au 2026-04-25 sur les 241 fichiers `/opt/automecanik/rag/knowledge/gammes/*.md` :

| Indicateur | Couverture |
|---|---|
| `lifecycle.stage: v5_ssot` | 238/241 (98.7 %) |
| `oem_verified` | 237/241 (98.3 %) |
| `GammeContentContract.v4` | 232/241 (96.3 %) |

Les écarts résiduels (9 fichiers hors v4, 3 régressions stage, 4 niches sans OEM verify)
sont **intentionnels** (gammes secondaires ou choix éditoriaux confirmés). Le data plane
est considéré comme opérationnel pour le périmètre business.

**Control plane (scripts d'enrichissement et cron)** : déconnecté de la spec.

| Élément spec v2.1 | État réel | Évidence |
|---|---|---|
| Émission de `enrichment-report.json` à fin de run | **Aucun emitter** | `grep enrichment-report` dans `scripts/` et `rag/scripts/` → 0 hit |
| Détection `_conflicts[]` à `enrich_write` | **Aucun detector** | 0 fichier `.md` ne porte `_conflicts:` sur 241 |
| State machine 7 stages | **1 seul stage actif** (`v5_ssot`) | Pipeline limité à scrape + ingest, pas d'audit / qa / promote |
| Phase 4 du wrapper `auto-enrich-r4-rag.py` | **Cassée silencieusement** | Path bug `os.path.dirname(__file__)/enrich-rag-bulk.py` → script réel à `/opt/automecanik/app/scripts/rag/enrich-rag-bulk.py` |
| Détection régressions silencieuses (ex: drift `auto_generated`) | **Absente** | Régression `plaquette-de-frein` au stage `auto_generated` non détectée par le cron hebdo |

Le cron `run-phase-f.sh` (`0 2 * * 0`) tourne mais n'émet aucun artefact d'observabilité
prévu par la spec v2.1. Tout audit ou orchestration en aval (ex: skill `seo-content-architect`,
`/content-audit`, `/seo-gamme-audit`) opère sans signal de fraîcheur ni preuve de conflit.

## Décision

Implémenter la **state machine RAG v2.1 complète** telle que spécifiée par
`enrichment-report.schema.json`, en quatre phases livrées en PRs séquentielles vers `main`,
avec un seul ADR cadre (cet ADR) et exécution du périmètre intégral (pas d'hybride
"observabilité minimale en attendant", cf. `feedback_no_hybrid_workarounds.md`).

Le pattern **propose-before-write** d'ADR-022 (R8 control plane) est réutilisé comme primitive :
chaque transition d'état (`v5_ssot` → `v5_audited` → `v5_enriched` → `v5_qa_passed` →
`v5_indexed`) émet une proposition vérifiée avant écriture du frontmatter `.md`. Aucun
chantier de "Company Orchestrator" / multi-agent / 13 départements / control plane AI-COS
n'est introduit — le pipeline reste **déterministe et scripté** côté NestJS + scripts Python.

### Éléments structurants

1. **State machine 7 stages** — alignée à `$defs.lifecycle_stage`
   (`v5_ssot` → `v5_audited` → `v5_enriched` → `v5_qa_passed` → `v5_indexed` /
   `v5_blocked` / `v5_pending_review`). Implémentée comme `enum` partagé
   `shared/types/rag-lifecycle.ts` + persistée dans la table
   `__rag_enrichment_runs` (Supabase, RLS) à créer en P1.

2. **6 modes d'exécution** — exposés via flag `--mode {audit_only,enrich_dry_run,
   enrich_write,qa_only,qa_write,index_ready_check}` sur les scripts Python concernés
   et via paramètre `mode` du endpoint `POST /api/rag/admin/pipeline/launch` (existant).

3. **Emitter `enrichment-report.json`** — `RagEnrichmentReportEmitterService` (NestJS)
   produit un report JSON par `run_id` (UUID v4), validé schema, persisté à la fois :
   - en table `__rag_enrichment_runs` (queryable par `seo-gamme-audit`)
   - en fichier `/opt/automecanik/rag/logs/runs/{run_id}.json` (audit trail filesystem)

4. **Detector `_conflicts[]`** — `RagConflictDetectorService` (NestJS) appelé à `enrich_write` :
   quand deux sources fournissent des valeurs divergentes pour le même `field.path`,
   classifie `minor_variation` / `technical_conflict` / `safety_conflict` selon source tier
   (A=constructeur/norme, B=revendeur/guide, C=généraliste), append au frontmatter `.md`.

5. **Decision matrix** — `RagDecisionService` calcule `PROMOTE_L1` (no `technical_conflict`
   actif + tous validators R-cible PASS + 8 SEO regression checks PASS) /
   `KEEP_L2` / `BLOCKED` / `PENDING_REVIEW`. Aucune promotion auto sans review humain pour
   `safety_conflict`.

6. **Validators R0-R8 réutilisés** — les 10 agents existants `.claude/agents/r*-validator.md`
   sont attachés via mode `qa_only` / `qa_write` sans réécriture. Mapping rôle cible → validator :
   R3_GUIDE → `r3-conseils-validator` + `r6-guide-achat-validator`, R4 → `r4-reference-validator`,
   etc. Le service `QualityValidatorService` orchestre l'invocation.

7. **Plan de livraison en 4 phases (PRs séquentielles)** —
   Chaque phase merge sur `main` avant ouverture de la suivante. Aucune phase n'est
   "à moitié livrée".

   | Phase | Périmètre | Livrables | Stage cible |
   |---|---|---|---|
   | **P1** — Observabilité + path fix | Emitter + detector + path fix Phase 4 + table `__rag_enrichment_runs` | `RagEnrichmentReportEmitterService`, `RagConflictDetectorService`, migration Supabase, fix `auto-enrich-r4-rag.py:279`, smoke test cron manuel | `v5_ssot` (inchangé, observabilité seule) |
   | **P2** — Audit | `RagAuditService` + mode `audit_only` | Score qualité par bloc + transition `v5_ssot` → `v5_audited` | `v5_audited` |
   | **P3** — QA | `QualityValidatorService` + mode `qa_only` / `qa_write` | Invocation R*-validators selon rôle, transition `v5_audited` → `v5_qa_passed` ou `v5_blocked` / `v5_pending_review` | `v5_qa_passed` |
   | **P4** — Promote | `RagDecisionService` + mode `index_ready_check` + endpoint `POST /api/rag/admin/:alias/promote` | Promotion `v5_qa_passed` → `v5_indexed` (truth_level L2 → L1) | `v5_indexed` |

8. **Pré-requis livrés dans P1** (pas de PR séparée) — path fix Phase 4 (`auto-enrich-r4-rag.py:279`),
   création de la table `__rag_enrichment_runs`, types partagés `shared/types/rag-lifecycle.ts`,
   wiring fin de `run-phase-f.sh` pour appeler l'emitter.

### Données et migrations

P1 introduit la table Supabase :

```sql
CREATE TABLE __rag_enrichment_runs (
  run_id UUID PRIMARY KEY,
  alias TEXT NOT NULL,
  run_date DATE NOT NULL,
  execution_mode TEXT NOT NULL CHECK (execution_mode IN
    ('audit_only','enrich_dry_run','enrich_write','qa_only','qa_write','index_ready_check')),
  state_before TEXT NOT NULL,
  state_after TEXT NOT NULL,
  truth_level_before TEXT NOT NULL,
  truth_level_after TEXT NOT NULL,
  decision TEXT NOT NULL CHECK (decision IN
    ('PROMOTE_L1','KEEP_L2','BLOCKED','PENDING_REVIEW')),
  reason TEXT NOT NULL,
  report_json JSONB NOT NULL,           -- payload validé enrichment-report.schema.json
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_rag_runs_alias_date ON __rag_enrichment_runs(alias, run_date DESC);
```

RLS : lecture admin uniquement, écriture `service_role` uniquement (cohérent ADR-021).

Aucune migration des frontmatters existants n'est requise. Les 238 gammes `v5_ssot`
restent l'état initial. Les transitions sont opt-in et manuelles tant que P2-P4 ne sont
pas livrées.

### Risques et mitigations

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Emitter en P1 ralentit `run-phase-f.sh` au-delà du timeout cron (90 min) | Faible | Moyen | Emitter post-run, exécution en arrière-plan + écriture asynchrone DB |
| Detector génère `_conflicts[]` faux-positifs sur `minor_variation` | Moyen | Faible | Normalisation tier C / casse / espaces avant comparaison |
| P3 (QA) bloque trop de gammes en `v5_blocked` | Inconnue | Moyen | Mode `qa_only` (read-only) avant `qa_write`, calibration sur 10 gammes pilote |
| ADR-022 (R8) et ADR-029 (gammes) divergent sur `__rag_proposals` vs `__rag_enrichment_runs` | Faible | Faible | Table dédiée `__rag_enrichment_runs` (gammes), séparée de `__rag_proposals` (R8 véhicules). Pas de fusion. |

### Plan rollout

- **P1 PR** : ouverture immédiate après acceptation ADR-029. Smoke test sur déclenchement
  manuel de `run-phase-f.sh` avec `INTERNAL_API_KEY` valide. Validation : un fichier
  `enrichment-report.json` valide schema apparaît dans `/opt/automecanik/rag/logs/runs/`,
  une ligne dans `__rag_enrichment_runs`.
- **P1 mergé** → ADR-029 passe à `status: accepted`, `decision_date` renseigné.
- **P2-P4** : ouverture séquentielle, chaque PR référence cet ADR. Calibration sur
  10 gammes pilote (couvrir 1 par profil business : `freinage`, `filtration`, `direction`,
  `électrique`, `motorisation`, etc.) avant exécution sur l'ensemble des 241.

### Suivi (post-merge P1)

| Métrique | Cible J+7 | Source |
|---|---|---|
| Nombre de runs avec emitter actif | ≥ 1 (cron hebdo) | `__rag_enrichment_runs` count |
| `_conflicts[]` détectés sur 241 gammes | ≥ 1 (probablement plus) | `grep -c _conflicts: gammes/*.md` |
| Gammes en régression silencieuse remontées | régression `plaquette-de-frein` détectée | report `decision: PENDING_REVIEW` ou `BLOCKED` |

## Conséquences

**Positives :**
- Spec v2.1 (mergée 2026-04-07) cesse d'être déconnectée du code et devient
  observable + actionnable.
- Régressions silencieuses (drift `auto_generated`) détectées par cron hebdo, pas
  découvertes manuellement plusieurs semaines plus tard.
- Skills SEO en aval (`seo-content-architect`, `content-audit`, `seo-gamme-audit`)
  consomment un signal de fraîcheur et de conflit fiable, plutôt que de re-inférer
  l'état.
- Pattern `propose-before-write` d'ADR-022 étendu au domaine `gammes` sans dupliquer
  l'orchestration.

**Négatives :**
- Charge de livraison ~2-3 semaines réparties sur 4 PRs (P1 ~1 semaine, P2-P4
  ~1 semaine cumulé).
- Une nouvelle table Supabase à maintenir (`__rag_enrichment_runs`).

**Neutres :**
- Aucun chantier multi-agent introduit. Aucun lien avec ADR-006 (AI Orchestrator)
  ou ADR-025 (SEO Department). Le pipeline reste déterministe.

## Références

- Commit `c675c9a6` (2026-04-07) — spec v2.1 mergée
- ADR-022 — R8 RAG Control Plane (pattern propose-before-write réutilisé)
- ADR-015 — Vault as Single Source of Truth
- `feedback_no_hybrid_workarounds.md` (mémoire) — pas de "pragmatique en attendant"
- `feedback_branch_scope_discipline.md` (mémoire) — branches dédiées depuis main
- Mémoire `rag-enrichment-pipeline.md` — historique pipeline scripts/seo/rag-*.py
