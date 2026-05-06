---
title: "État des 9 chantiers (A→I) au 2026-05-06 — handoff session"
date: 2026-05-06
type: session-trail
related_chantier: ALL
related_moc: ["MOC-Roadmap-2026"]
related_adr: ["ADR-021", "ADR-028", "ADR-030", "ADR-040", "ADR-043"]
status: closed
session_closed_at: 2026-05-06
---

# État des 9 chantiers (A→I) au 2026-05-06

> Snapshot canon de l'état Plan F + 8 autres chantiers à la clôture de
> session 2026-05-06 (~19:00 UTC). Sert de base de référence pour la
> prochaine session.

## Règle canon appliquée

Un chantier est `LIVE` **seulement** si l'ADR de référence a `status: accepted`
dans MOC-Decisions (memory DEV `feedback_canon_rule_live_iff_adr_accepted.md`).
Code shippé partial sans ADR Accepted = `partial` ou `proposed`, pas LIVE.

## État synthétique

| Chantier | Priorité | État | ADRs / Signal | Reste |
|----------|----------|------|---------------|-------|
| **F** — DevSecOps | **P0** | 🟡 **proposed (Sprint 1 en cours)** | ADR-043 `proposed` ; signaux A+F+D NOT RED empirique | Sprint 1 (8 items) → Sprint 2 → Sprint 3 SLSA L2 |
| **A** — Runtime e-commerce | P1 | 🔴 **TBD** | aucun plan dédié ; ADR-016 vehicle cache `accepted` | Plan global TBD ; signal A NOT RED (0 issue PROD 14d) |
| **D** — SEO indexation | P2 | 🟡 **partial** | ADR-040 `accepted` (R0..R8 canon) ; signal D NOT RED (30/30 indexed) | D1-D7 plan global TBD ; priorité = qualité position (avg 14.9) |
| **B** — Catalogue | P3 | 🟡 **partial** | ADR-032 `proposed` (phases 0-4 shippées) | Phase 5 ADR-032 (PR-8/9/10/11) |
| **E** — Performance | P4 | 🟡 **partial** | ADR-016 `accepted`, ADR-017 `accepted` (Phase 1 LIVE -96% RPC #1) | Plan global TBD ; 8 RPC restantes ADR-017 |
| **C** — Raw/Wiki/Diag | P5 | 🟢 **infra close** | ADR-031, ADR-033, ADR-039 `accepted` ; verdict READY 2026-05-01 | Migration legacy fiches gamme (Phase 2 ADR-033) |
| **H** — Marketing | P6 | 🟡 **Phase 1 mergée** | ADR-036 `proposed` (5 PRs Phase 0-1.3) ; ADR-038 `accepted` | Phase 2 (LEAD/LOCAL/RETENTION) gated `local_canon.validated: true` |
| **G** — RAG support | P7 | 🟡 **partial** | ADR-022 `accepted` (R8 control plane) ; ADR-029 `proposed` | Pipeline enrichissement LIVE ; RAG v2.1 control plane closure pending |
| **I** — Agents/Paperclip | P8 | 🟡 **partial** | ADR-034 `proposed` ; ADR-037/038/039 `accepted` ; R12 exit contract | ADR-034 promotion J+30 (~2026-05-30 audit) |

## Détail par chantier

### F — DevSecOps / sécurité prod (P0, focus Sprint 1)

**Phase 0 close 2026-05-06** (audit-trail [[2026-05-06-plan-F-phase-0-verdict]]).
4 livrables analyse côté DEV (`~/.claude/plans/`) :

- F0.2 STRIDE — 4 surfaces × 6 catégories → 12 findings + 4 patterns transverses
- F0.3 SAMM v2 — score 1.26/3 actuel, cible 2.07/3 sur 6 mois
- F0.4 SLSA — niveau L0.5 actuel, cible L2 sur 6 mois
- F0.5 verdict — Plan Phase 1 = 3 sprints × 2 sem (~22-25j cumulés)

**Préacquis** (cités, pas réécrits) : ADR-021 RLS (`accepted`), ADR-028 prod isolation (`accepted`), ADR-030 npm ci ignore-scripts (`accepted`), husky pre-push hook PR monorepo #266 mergée 2026-05-02.

**Signaux empiriques 3/3 NOT RED** :
- A (Sentry) : 0 issues PROD 14d, 0 events PROD 24h ([[2026-05-06-signal-A-empirical-correction]])
- F (npm audit + secret-grep) : 0 CVE CVSS≥7.0 + exploit path runtime ([[2026-05-06-sprint-arbitrage-F]])
- D (GSC) : 30/30 top URLs indexed ([[2026-05-06-signal-d-empirical-update]])

**Sprint 1 en cours** :

| # | Ticket | PR monorepo | État |
|---|--------|-------------|------|
| 1 | Aligner `GSC_SITE_URL` env var (Domain) | (local backend/.env) | ✅ done |
| 2 | Smoke-test Sentry event end-to-end | (manuel curl) | ✅ done |
| 3 | Logout `session.destroy()` error propagation | [#338](https://github.com/ak125/nestjs-remix-monorepo/pull/338) | 🟡 OPEN, auto-merge enabled |
| 4 | Session secret fail-fast PROD + random DEV | [#339](https://github.com/ak125/nestjs-remix-monorepo/pull/339) | 🟡 OPEN, auto-merge enabled |
| 5 | gitleaks/trufflehog CI bloquant | — | ⏳ next ticket |
| 6 | Rate limit callbacks paiement | — | ⏳ Sprint 1 reste |
| 7 | Permissions per-job workflows | — | ⏳ Sprint 1 reste |
| 8 | Login lockout après N tentatives | — | ⏳ Sprint 1 reste |
| 9 | SystemPay SHA1 → SHA-256 default | — | ⏳ humain pilote (Lyra portal config) |

**Promotion ADR-043 `proposed → accepted`** : conditionnée à Sprint 1 close avec ≥80% items livrés + audit-trail `2026-MM-DD-plan-F-sprint-1-close.md` + amélioration empirique ≥1 signal SAMM.

### A — Runtime e-commerce / business core (P1)

**État** : zéro plan dédié, juste préacquis [[ADR-016-vehicle-page-matview-persistence]] (`accepted`).

**Signal A** : NOT RED (0 issues PROD 14d). Pas d'urgence.

**Reste** : plan global A1-A6 (commandes / panier / paiement / emails / observability checkout / logs business) à écrire quand prochain arbitrage de sprint le sélectionne.

### D — SEO indexation / crawl budget (P2)

**État** : pipelines R0-R8 LIVE via [[ADR-040-seo-roles-canon-ts-side-only]] (`accepted` 2026-05-05). R7 36/36 brands curées. KW pipeline canon LIVE.

**Signal D** : NOT RED (30/30 top URLs indexed). Aggregate 28j : 2093 clicks / 126K impressions / CTR 1.66% / avg position 14.9 (page 2 Google).

**Implication** : priorité Phase 1+ devient « qualité position » (D1+D5) plutôt que « coverage » (déjà OK).

**Reste** : D1-D7 plan global TBD ; aligner `GSC_SITE_URL` ✅ done cette session.

### B — Catalogue / compatibilité véhicule (P3)

**État** : [[ADR-032-diagnostic-maintenance-unification]] `proposed` avec `implementation_status: phases-0-4-shipped, phase-5-pending` (vault PR #161). V-Level v5.0 LIVE. Alias romain/arabe wired (PR monorepo #122).

**Reste** : Phase 5 ADR-032 (PR-8/9/10/11) pour promotion `proposed → accepted`.

### E — Performance backend / frontend (P4)

**État** : [[ADR-016-vehicle-page-matview-persistence]] `accepted` (2026-04-27 evidence-based promotion). [[ADR-017-rpc-pieces-cast-cleanup]] `accepted` (Phase 1 LIVE, RPC #1 -96%, 8 RPC restantes).

**Reste** : Plan global E1-E7 TBD ; finir ADR-017 8 RPC restantes.

### C — Knowledge / Raw / Wiki / Diagnostic Canon (P5)

**État** : [[ADR-031-four-layer-content-architecture]], [[ADR-033-wiki-gamme-diagnostic-relations-contract]], [[ADR-039-wiki-frontmatter-zod-canon]] `accepted`. Verdict READY 2026-05-01 (audit-trail [[2026-05-01-roadmap-canonization-and-chantier-c-ready]]). Sprint 3 P3 closed via PRs monorepo #259/#262/#265/#268.

**Reste** : migration legacy fiches gamme (Phase 2 ADR-033) ; routine audit J+30 ADR-033 fire 2026-05-29.

### H — Marketing / acquisition (P6)

**État** : [[ADR-036-marketing-operating-layer]] `proposed` ; Phase 0 + Phase 1.1/1.2/1.3 mergées 2026-04-30 (5 PRs monorepo #225/#238/#240/#241 + ADR-038 naming canon #247). [[ADR-038-marketing-agent-naming-canon]] `accepted` 2026-05-01.

**Reste** : Phase 2 (LEAD / LOCAL / RETENTION agents) gated par `local_canon.validated: true`.

### G — RAG / support client / assistant (P7)

**État** : [[ADR-022-r8-rag-control-plane]] `accepted` (propose-before-write, 5-layer gates). Pipeline enrichissement 232 gammes .md LIVE. [[ADR-029-rag-v2.1-control-plane-closure]] reste `proposed` avec `implementation_status: no-implementation-wave` (vault PR #161).

**Reste** : RAG v2.1 control plane closure (state machine 7-stage + emitter/detector) ; dépendant de C (wiki validé) + D (pages indexées) + B (compat fiable).

### I — Agents / gouvernance / Paperclip (P8)

**État** : [[ADR-034-aicos-operating-contract]] `proposed` avec `implementation_status: contract-active-since-2026-04-30, accepting-promotion-after-30d-evidence`. [[ADR-037-agent-naming-canon]], [[ADR-038-marketing-agent-naming-canon]], [[ADR-039-wiki-frontmatter-zod-canon]] `accepted` 2026-05-01. R12 exit contract LIVE.

**Reste** : audit J+30 ADR-034 (~2026-05-30 via routine `trig_01Tq3Z8ohU29suDmnezZhWnG`) avant promotion `proposed → accepted`.

## Routines auto-fire en cours

- 2026-05-29 09:00 UTC — audit ADR-033 J+30 (`trig_01LKqhkSKddud3ywGM9Yjb6z`)
- ~2026-05-30 — audit ADR-034 J+30 (`trig_01Tq3Z8ohU29suDmnezZhWnG`)
- Quotidien 02:00/03:00 UTC — `diag-canon-slugs-export` + `wiki-canon-shape-check` (drift detection chantier C)
- Hebdomadaire — `vault-supabase-cost-check` (chantier I)

## Bloqueurs & dépendances cross-chantier

| De | Dépend de | Pourquoi |
|----|-----------|----------|
| F Phase 1 promotion | F Sprint 1 close | ADR-043 `proposed → accepted` requires evidence |
| G RAG v2.1 closure | C wiki validé + D indexation OK + B compat fiable | RAG = consommateur, pas SoT |
| H Phase 2 marketing | `local_canon.validated: true` | Gate édito |
| I ADR-034 promotion | J+30 audit (~2026-05-30) | 30j evidence respect AP-12 |

## Prochaine session — handoff

**État au moment du handoff (2026-05-06 ~19:00 UTC)** :

- 8 PRs vault mergées cette session (#128, #161, #162, #163, #164, #166, #172, #174)
- 2 PRs monorepo OPEN avec auto-merge `--squash --delete-branch` activé :
  - [#338](https://github.com/ak125/nestjs-remix-monorepo/pull/338) logout session.destroy
  - [#339](https://github.com/ak125/nestjs-remix-monorepo/pull/339) session secret fail-fast
- 3/3 signaux empiriques NOT RED → sprint suivant = F par défaut P0→P8 confirmé
- Phase 0 Plan F close, Phase 1 cadrée par ADR-043 `proposed`

**Action utilisateur prochaine session** :

1. **Vérifier que #338 et #339 ont mergé** (CI complet) :
   ```bash
   gh pr view 338 --repo ak125/nestjs-remix-monorepo --json state,mergedAt
   gh pr view 339 --repo ak125/nestjs-remix-monorepo --json state,mergedAt
   ```
   Si mergé : Sprint 1 ticket #1 + #2 ✅ done.

2. **Décider Sprint 1 ticket #5** (gitleaks/trufflehog CI bloquant ~2j) ou
   **basculer sur autre chantier** si signal A/D rouge entre-temps.

3. **Lire la nouvelle session** :
   - `governance-vault/ledger/audit-trail/2026-05-06-9-chantiers-state-handoff.md` (cet audit-trail)
   - `governance-vault/ledger/decisions/adr/ADR-043-plan-F-devsecops-phase-1-cadre.md` (cadre Phase 1)
   - `~/.claude/plans/F0.2-threat-model-stride/00-index-synthesis.md` (12 findings)
   - `~/.claude/projects/-opt-automecanik-app/memory/MEMORY.md` (mémoires DEV à jour)

**Si signal A ou D devient rouge avant Sprint 1 close** : pivot via audit-trail
intermédiaire signé G3 (cf. ADR-043 §"Procédure si signal flippe pendant Phase 1").

## Mémoires DEV créées cette session

- `roadmap-canon-shipped-20260506.md` — MOC-Roadmap-2026 SHIPPED
- `gsc-sa-resolved-20260506.md` — GSC SA Owner OK
- `feedback_canon_rule_live_iff_adr_accepted.md` — règle canon LIVE iff accepted
- `feedback_decision_must_be_signal_proven_not_intuited.md` — décision sprint = signal empirique
- `feedback_check_sops_encrypted_secrets_too.md` — chercher fichiers chiffrés avant claim "missing"
- `feedback_progress_dashboard_required.md` — tenir dashboard récap auto-mode

## Références

- [[MOC-Roadmap-2026]] — canon racine 9 chantiers + P0→P8
- [[2026-05-06-sprint-arbitrage-F]] — verdict F par défaut
- [[2026-05-06-plan-F-phase-0-verdict]] — Phase 0 close + plan Phase 1
- [[2026-05-06-signal-d-empirical-update]] — signal D NOT RED
- [[2026-05-06-signal-A-empirical-correction]] — signal A NOT RED
- [[ADR-043-plan-F-devsecops-phase-1-cadre]] — Plan F Phase 1 cadre `proposed`
- Plan DEV `~/.claude/plans/plan-F-devsecops-phase-0-scoping-20260506.md`
- Plan DEV `~/.claude/plans/F0.2-threat-model-stride/` (4 STRIDE pages + index)
- Plan DEV `~/.claude/plans/F0.3-samm-assessment.md`
- Plan DEV `~/.claude/plans/F0.4-slsa-baseline.md`
