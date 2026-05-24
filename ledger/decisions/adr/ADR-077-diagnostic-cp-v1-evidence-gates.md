---
id: ADR-077
title: "Diagnostic Control Plane V1 — Evidence-Gated V1.5 Registry (10 deferral gates G1..G10)"
status: accepted
date: 2026-05-19
decision_date: 2026-05-19
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: []
related_adr: [ADR-013, ADR-015, ADR-058, ADR-070, ADR-076]
related_rules: [G1, G2, T1]
related_incidents: []
reviewed_by: "@fafa"
---

# ADR-077 : Diagnostic Control Plane V1 — Evidence-Gated V1.5 Registry (10 deferral gates G1..G10)

## Contexte

Le **2026-05-18→19**, Diagnostic Control Plane V1 a shippé (PR #606, #622, #625, #628, #630 hotfix deploy). Le plan V1 a **explicitement déferré 10 items vers V1.5+ evidence-gated**, chacun avec un trigger d'escalation nommé.

Ces deferrals ne vivent durablement nulle part — uniquement dans la mémoire AI-COS volatile (`MEMORY-active-work.md`, `project_diagnostic_control_plane_v1_plan.md`). Sans artefact canon, ils érodent en ~30j par rotation d'agents et par requêtes "fais juste ce petit truc" :

- `feedback-no-autoescalation-after-single-go` : un "fais le" = scope nommé uniquement
- `feedback-v1-first-dont-build-ultimate-engine-too-early` : V1 = seul livrable, V1.5+ NON-planifiée tant que 4 gates non-passées
- `guard-hierarchy-stop-at-v1-funnel-truth` : STOP-at-V1 + funnel-as-truth + Admin UI lockdown

**Risque réel** : drift incrémental où chaque "petite extension" légitime individuellement érode le STOP-at-V1 jusqu'au retour god-engine 60-90 jours plus tard, exactement comme la dérive corrigée par PR-A→E (4 domaines mélangés dans `DiagnosticEngineOrchestrator`).

## Décision

Locker les **10 deferrals V1→V1.5** comme **canon L4 ADR-013** dans cet ADR vault, et projeter le canon vers le monorepo via le pattern Repository Control Plane (ADR-058) : overlay TS+Zod typé + YAML projection + CODEOWNERS auto-sync + status query stateless on-demand.

**Les 10 gates G1..G10** :

| Gate | Item différé | Trigger | Type |
|---|---|---|---|
| G1 | Engine extraction réelle vers D6/D11/D16 | ≥30j PR-D enforcement sans override | auto |
| G2 | Dual-path 30j divergence check | depends_on G1 + engine extraction PR mergée | derived |
| G3 | OTel spans `domain=…` (diagnostic/commerce/maintenance/editorial) | ≥1 demande tracing concrète documentée | reactive |
| G4 | Grafana dashboard JSON commit | ≥1 alert config née de l'observation preprod/prod | reactive |
| G5 | GA4 events mirror des counters vehicle_ctx | Consent conduit V2 + transport layer prêts | reactive |
| G6 | Table `__diag_kg_divergence_log` + replay CLI | `diagnostic_kg_shadow_diverged_total_rate > 5%` sustained 7d OU replay CLI explicitement demandé | hybrid |
| G7 | Cohorte golden 200 sessions divergence | depends_on G6 + variance divergence rate stable | derived |
| G8 | Admin UI lecture-seule metrics | ≥3 plaintes distinctes équipe ops sur lecture metrics | reactive |
| G9 | Wizard pre-fill profond depuis VehicleContext + historique | `diagnostic_to_commerce_funnel_ratio ≥ baseline × 1.30` sustained 7d ET 6 critères V1→V1.5 tous passés | auto + dependency |
| G10 | Bump VehicleContext cookie schema v:1 → v:2 | Nouveau champ business-justifié AND ADR L4 vault validant l'extension | reactive |

**Promotion path** (canon, identique pour les 10) :
```
gate_trigger_fires → ADR L4 nouvelle dans vault → plan exécution → PR dédié → merge
```
**Aucun raccourci** — y compris pour les gates "réactifs simples" (G3/G4/G5/G8/G10).

## Options Considérées

### Option A: Memory-only (status quo)

**Description** : laisser les deferrals dans `MEMORY-active-work.md` et `project_diagnostic_control_plane_v1_plan.md` uniquement.

**Avantages** :
- Zéro coût d'implémentation immédiat
- Aucune dette de maintenance d'un nouvel artefact

**Inconvénients** :
- Memory volatile, pas canon (cf. `vault-sot-adr013`)
- Ne survit pas rotation agents AI-COS
- Aucun blocage mécanique des `blocked_paths`
- Drift garanti en ~30j

### Option B: ADR-only sans overlay machine-readable

**Description** : seulement l'ADR L4 vault, pas de projection monorepo.

**Avantages** :
- Canon-aligné ADR-013
- Coût minimal (1 fichier vault)

**Inconvénients** :
- Pas d'outillage runtime (impossible status reporting)
- Pas de blocage CODEOWNERS automatique
- Détection des triggers reste manuelle

### Option C: ADR + Overlay TS+Zod + YAML projection + CODEOWNERS auto-sync + Status CLI (RETENUE)

**Description** : ADR vault (canon L4) + overlay TS+Zod typé dans `packages/registry/src/overlay/` (pattern canon ADR-058) + YAML projection automatique dans `canonical.json` + CODEOWNERS section auto-générée + script status CLI on-demand stateless.

**Avantages** :
- 100% alignement pattern canon existant (cf. `domains.ts`+`domains.yaml`)
- Blocage GitHub-native (CODEOWNERS approval required)
- Status query stateless (zéro état persistant — pas de violation G6)
- Event-driven via `__seo_event_log` existant (pas polling)
- Réversibilité totale (suppression section CODEOWNERS + delete files)
- Tests Zod parse + metrics parse inclus
- Drift protection : pre-commit hook + CI meta-discipline auto-check

**Inconvénients** :
- ~300 LOC à écrire et maintenir
- Coordination 2 PRs (vault + monorepo)

### Option D: Policy-as-code Rego dédié

**Description** : `policies/governance/evidence-gates.rego` policy OPA bloquant via CI.

**Avantages** :
- Industrie standard policy-as-code

**Inconvénients** :
- Rego pas encore mergé sur `main` du monorepo (cf. `find . -name "*.rego"` = uniquement worktree preprod-env-contract)
- Ajouter Rego = nouvelle infra → anti-pattern STOP-at-V1
- CODEOWNERS GitHub-native suffit pour blocking déterministe

## Justification

**Option C retenue** car :

1. **Canon-aligned** : suit le pattern Repository Control Plane (ADR-058) déjà mature (`domains.ts`+`domains.yaml`+`ownership.ts`+...).
2. **Zéro nouvelle infra** : réutilise `packages/registry`, `__seo_event_log`, CODEOWNERS, Paperclip routines, prom-client PR-C. Aucun Rego, aucune nouvelle table, aucun nouveau workflow GH Actions.
3. **Méta-discipline auto-vérifiée** : un step CI vérifie que le registre lui-même ne viole AUCUN des 10 gates qu'il documente.
4. **Detection event-driven** : `__seo_event_log` étend l'enum `event_type` avec `evidence_gate_fired` (≤30 LOC migration SQL), Paperclip routine subscribe au flux. Pas de polling weekly.
5. **Stateless** : status query lit overlay + interroge metrics endpoint live + émet stdout JSON. Pas de fichier persistant.

## Conséquences

### Positives

- Canon L4 lock des 10 deferrals (signed commit ADR-015)
- Blocage mécanique GitHub-native sur `blocked_paths` (CODEOWNERS approval `@ak125`)
- Status query déterministe et reproductible
- Drift protection via pre-commit hook + CI meta-discipline check
- 100% réversible (suppression overlay + section CODEOWNERS = retour à zéro)
- Promotion path codifié et non-falsifiable (aucun raccourci possible)

### Coûts opérationnels

- ~300 LOC TS/YAML à maintenir
- 1 migration SQL `__seo_event_log.event_type` enum extension (≤30 lignes, conditionnelle sur feasibility)
- 1 Paperclip routine daily à scheduler

### Hors-scope V1 (gate-on-evidence)

- ast-grep blocking rule pour `blocked_paths` (différé jusqu'à preuve d'un override tenté — `feedback-evidence-before-perimeter-expansion`)
- Notification riche Slack/email (Paperclip task creation suffit)
- Dashboard live des gates (= violation G4 par méta-discipline)
- Persistent state file `evidence-gates-status.json` (= violation G6 conceptuelle)
- Backfill historique des observations PR-A→E
- Auto-bump gates si trigger fire (humain seul valide promotion path)

## Méta-discipline (CRITIQUE)

Le registre lui-même **NE VIOLE AUCUN** des 10 gates qu'il documente :

| Tentation | Gate violé | Action correcte |
|---|---|---|
| Dashboard temps réel | G4 | Stdout JSON only |
| Nouvelle table `__evidence_gates_*` | G6 | Réutilise `__seo_event_log` (enum extension) |
| Admin UI lecture status | G8 | CLI + Paperclip task creation |
| OTel spans `gate_status=fired` | G3 | Aucune instrumentation OTel |
| Extraction engine "préparatoire" | G1 | Status-only, zéro changement engine |
| GA4 mirror du status | G5 | Aucun analytics frontend |
| Bump cookie pour metadata gate | G10 | Aucune modif cookie schema |
| Wizard pre-fill avec gate context | G9 | Aucune modif wizard |

Auto-check CI step : `audit-evidence-gates-meta-discipline` refuse merge si un fichier du PR Evidence Gates Registry match les `blocked_paths`/`blocked_globs` du YAML.

## Critères de Succès

- [x] ADR-077 mergée vault `main` (signed commit ADR-015)
- [ ] Overlay TS+Zod `evidence-gates.ts` ajouté `packages/registry/src/overlay/`
- [ ] YAML projection `.spec/00-canon/repository-registry/evidence-gates.yaml` projetée dans `audit/registry/canonical.json`
- [ ] CODEOWNERS auto-sync idempotent, section auto-managed en place
- [ ] Status CLI `npm run audit:evidence-gates` retourne 10 gates `GATED` initialement
- [ ] Pre-commit hook drift check actif
- [ ] CI step meta-discipline auto-check actif
- [ ] Paperclip routine `evidence-gate-listener` schedulée

## Implémentation

**PR vault** : `feat/adr-077-evidence-gates`
- 1 fichier : cet ADR
- Worktree : `vault-adr-077`

**PR monorepo** : `feat/evidence-gates-registry`
- `packages/registry/src/overlay/evidence-gates.ts` — Zod schema overlay (pattern `domains.ts`)
- `.spec/00-canon/repository-registry/evidence-gates.yaml` — projection (pattern `domains.yaml`)
- `packages/registry/src/overlay/__tests__/evidence-gates.spec.ts` — tests Zod parse
- `scripts/audit/sync-codeowners-from-gates.ts` — auto-sync ≤80 LOC
- `scripts/audit/evidence-gates-status.ts` — status CLI ≤100 LOC stateless
- `scripts/audit/__tests__/evidence-gates-status.spec.ts` — tests metrics parse
- `.github/CODEOWNERS` — append section auto-managed
- `.husky/pre-commit` — append drift check line
- `.github/workflows/audit.yml` — append meta-discipline step
- `package.json` — npm script `audit:evidence-gates`
- `backend/supabase/migrations/*_extend_seo_event_log_evidence_gate_fired.sql` — enum extension (conditionnel)
- Worktree : `app-worktrees/pr-evidence-gates-registry`

**Total scope** : ~300 LOC, 0 logique métier, 0 nouvelle infra, 0 nouveau state persistant.

## Revue Planifiée

**Date** : 2026-08-19 (T+90j post-merge PR-E Diagnostic CP V1)
**Critères de revue** :
- Évaluer 6 critères evidence V1→V1.5 (funnel +30%, handoff ≥100/j, 0 incident safety_gate, divergence <5%, vehicle_ctx_invalid <0.1%, 30j sans sev2+)
- Si tous passés : ouvrir ADRs L4 successeurs pour chaque gate FIRED → planifier exécution
- Si 1+ échoue : moratoire V1.5, debug exécution V1 avant nouvelle planification

---

*Proposé le : 2026-05-19*
*Accepté le : 2026-05-19*
*Dernière revue : 2026-05-19*
