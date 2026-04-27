---
title: "Session 2026-04-25 — ADR-029 P1 fondation (état + follow-ups)"
date: 2026-04-25
type: session-trail
related_adr: ["ADR-029"]
related_prs:
  - "ak125/governance-vault#77"
  - "ak125/nestjs-remix-monorepo#187"
status: in-progress
session_closed_at: 2026-04-25
---

# Session 2026-04-25 — ADR-029 P1 fondation

## Résumé

Première session de la **clôture du control plane RAG v2.1** (ADR-029).
Décision prise : implémenter la state machine 7 stages complète en
4 phases séquentielles (P1 Observabilité + path fix, P2 Audit, P3 QA,
P4 Promote). Aucun chantier multi-agent / orchestrateur introduit.

Origine : la spec v2.1 mergée le 2026-04-07 (commit `c675c9a6`,
`.spec/00-canon/enrichment-report.schema.json` + `conflict.schema.yaml`)
n'est pas branchée au pipeline d'enrichissement existant. Aucun emitter
d'`enrichment-report.json`, aucun detector de `_conflicts[]`. Régressions
silencieuses (drift `lifecycle.stage: auto_generated` sur `plaquette-de-frein`)
non détectées par le cron hebdo.

## Livré dans cette session

### Vault

- **ADR-029** (status: `proposed`) — PR [ak125/governance-vault#77](https://github.com/ak125/governance-vault/pull/77)
  - Commit `3231cf4` sur branche `feat/adr-029-rag-v2.1-control-plane`
  - Fichier : `ledger/decisions/adr/ADR-029-rag-v2.1-control-plane-closure.md`
  - 205 lignes, cadre les 4 phases + decision matrix + pré-requis P1

### Monorepo (PR draft)

- **PR draft** [ak125/nestjs-remix-monorepo#187](https://github.com/ak125/nestjs-remix-monorepo/pull/187)
  - Commit `93dd47a5` sur branche `feat/rag-v2.1-control-plane-p1`
  - 6 fichiers, 832 insertions, typecheck clean
  - Migration `__rag_enrichment_runs` (RLS service_role, 3 index, alignée ADR-021)
  - Types TS miroirs des schemas canon (`rag-lifecycle.types.ts` + `rag-lifecycle.schema.ts` Zod)
  - `RagEnrichmentReportEmitterService` (validation + DB + dump filesystem)
  - `RagConflictDetectorService` (5 fields safety + 6 patterns technical, normalisation NFKC)
  - Wiring `rag-proxy.module.ts` (providers + exports)

## Follow-ups — Restant pour P1

> La PR monorepo #187 reste **draft** tant que ces items ne sont pas couverts.
> Cohérent avec ADR-029 §"Pas d'hybride en attendant".

### À ajouter dans la PR monorepo #187 (mêmes branche/repo)

1. **Endpoint admin smoke test**
   - Route : `POST /api/rag/admin/pipeline/emit-report`
   - Garde : `IsAdminGuard` + `INTERNAL_API_KEY`
   - DTO Zod minimal pour test manuel (alias + execution_mode + state_before/after + decision/reason au minimum)
   - Localisation suggérée : `backend/src/modules/rag-proxy/rag-proxy.controller.ts` ou nouveau `controllers/rag-admin-pipeline.controller.ts`

2. **Tests unitaires**
   - `isDecisionCoherent()` : couvrir 4 décisions × {avec/sans conflits} × {validators PASS/FAIL}
   - `RagConflictDetectorService.detect()` : couvrir 5 fields safety + 6 patterns technical + minor_variation par défaut + cas equivalence après normalisation NFKC
   - `RagEnrichmentReportEmitterService.emit()` : mock Supabase, vérifier rejet schema invalid + decision incoherent

3. **Endpoint admin de listing**
   - `GET /api/rag/admin/pipeline/runs?alias=X&since=YYYY-MM-DD` (filtrage par gamme + date)
   - Utile pour `seo-gamme-audit` skill et dashboard SEO findings

### PR séparée — repo `ak125/automecanik-rag`

> Repo distinct du monorepo. À ouvrir dans une nouvelle session sur worktree
> isolé (cf. §"Pattern multi-session" ci-dessous).

4. **Path fix** [auto-enrich-r4-rag.py:279](https://github.com/ak125/automecanik-rag/blob/main/scripts/pipeline/auto-enrich-r4-rag.py#L279)
   - Bug : cherche `enrich-rag-bulk.py` dans `os.path.dirname(__file__)` (= `/opt/automecanik/rag/scripts/pipeline/`)
   - Réel emplacement : `/opt/automecanik/app/scripts/rag/enrich-rag-bulk.py` (monorepo)
   - Fix proposé : path absolu vers le monorepo OU symlink, OU déplacer le bulk script dans le repo rag (à arbitrer)

5. **Wiring `run-phase-f.sh`**
   - Fin de script : `curl -X POST http://localhost:3000/api/rag/admin/pipeline/emit-report` avec payload synthétisé depuis l'output `rag-enrich-from-web-corpus.py` + `ingest-oem-enriched-gammes.py`
   - Auth : `X-Internal-Key: $INTERNAL_API_KEY` (déjà chargé par le script)
   - Garde : si l'endpoint retourne != 201, log + non-bloquant (l'observabilité ne doit pas casser le pipeline)

6. **Wiring `rag-enrich-from-web-corpus.py`**
   - Quand 2 sources `phase5_enrichment` produisent des valeurs divergentes pour le même `field.path` du frontmatter, append au `_conflicts[]` du `.md` (selon `conflict.schema.yaml`)
   - Script Python doit POST vers `RagConflictDetectorService` ou implémenter directement la classification (à arbitrer — éviter la duplication de logique)

## Phases suivantes — P2/P3/P4

> Hors scope P1. À ouvrir comme PRs séparées **après** merge de P1.
> Cohérent avec ADR-029 §"4 phases livrées en PRs séquentielles".

- **P2 — Audit** : `RagAuditService` + mode `audit_only`, transition `v5_ssot` → `v5_audited`. Score qualité par bloc.
- **P3 — QA** : `QualityValidatorService` orchestre les 10 R*-validators existants (`.claude/agents/r*-validator.md`). Modes `qa_only` (read) puis `qa_write`. Transition `v5_audited` → `v5_qa_passed` / `v5_blocked` / `v5_pending_review`.
- **P4 — Promote** : `RagDecisionService` + mode `index_ready_check`. Endpoint `POST /api/rag/admin/:alias/promote`. Transition `v5_qa_passed` → `v5_indexed` (truth_level L2 → L1).

Calibration P3/P4 sur 10 gammes pilote (1 par profil business : `freinage`,
`filtration`, `direction`, `électrique`, `motorisation`, etc.) avant
exécution sur les 241.

## Pattern multi-session — leçon tirée

**Cause racine** identifiée pendant la session : deux sessions Claude Code
partageaient le working tree `/opt/automecanik/governance-vault/`. Un seul
`.git/HEAD`, un seul index, un seul tree de fichiers untracked. Race
condition sur les checkout/branch operations → mon `git add` a embarqué le
mauvais fichier (commit `84ceaf7` annonçait ADR-029 mais contenait l'ADR R5
d'une autre session, reset effectué).

**Solution canon adoptée** : `git worktree add` pour isoler la session.
- Vault : `/tmp/vault-adr-029` (worktree dédié sur branche
  `feat/adr-029-rag-v2.1-control-plane`)
- Monorepo : `.worktrees/rag-v2.1-p1` (worktree dédié sur branche
  `feat/rag-v2.1-control-plane-p1`)

Chaque session a son propre `HEAD`, propre index, propre tree de fichiers
— mais elles partagent le pool d'objets `.git/objects` (push/fetch unifiés,
pas de duplication).

**À codifier** : prochaine session doit créer son worktree isolé d'emblée
si elle modifie le vault ou le monorepo. Le pattern `.worktrees/X` côté
monorepo est déjà adopté ; le pattern `/tmp/vault-X` côté vault est
nouveau et à formaliser éventuellement dans une rule dédiée si la
fréquence multi-session augmente.

## Worktrees actifs au moment de la fermeture

| Repo | Worktree | Branche |
|---|---|---|
| `governance-vault` | `/tmp/vault-adr-029` | `feat/adr-029-rag-v2.1-control-plane` |
| `nestjs-remix-monorepo` | `/opt/automecanik/app/.worktrees/rag-v2.1-p1` | `feat/rag-v2.1-control-plane-p1` |

Les deux peuvent être conservés tels quels pour la prochaine session, ou
nettoyés via `git worktree remove` une fois les PRs mergées.

## Refs

- ADR-029 (vault) — `ledger/decisions/adr/ADR-029-rag-v2.1-control-plane-closure.md`
- Spec v2.1 mergée 2026-04-07 — commit `c675c9a6` (monorepo `.spec/00-canon/`)
- ADR-022 (R8 control plane, pattern propose-before-write réutilisé)
- ADR-021 (RLS hardening, aligné pour `__rag_enrichment_runs`)
- Mémoire `feedback_no_hybrid_workarounds.md` — pas de "pragmatique en attendant"
- Mémoire `feedback_branch_scope_discipline.md` — branches dédiées depuis main
