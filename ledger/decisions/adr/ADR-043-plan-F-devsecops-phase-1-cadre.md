---
id: ADR-043
title: "Plan F (DevSecOps) — cadre Phase 1 threat-model-first sur 3 sprints"
status: proposed
date: 2026-05-06
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G3", "Q1", "AP-12"]
related_incidents: []
related_adr: ["ADR-021", "ADR-028", "ADR-030", "ADR-040"]
implementation_status: phase-0-closed-2026-05-06, phase-1-not-started
---

# ADR-043 — Plan F (DevSecOps) Phase 1 cadre

## Contexte

[[MOC-Roadmap-2026]] (canon depuis 2026-05-06, vault PR #128) classe
**Chantier F (DevSecOps / sécurité prod) en P0**. Trois ADRs préacquises
adressent des pans isolés ([[ADR-021-database-rls-hardening-zero-trust]],
[[ADR-028-preprod-supabase-isolation]],
[[ADR-030-npm-ignore-scripts-alpine-musl]]) plus une PR husky `pre-push`
(monorepo #266 mergée 2026-05-02), mais **aucun fil conducteur transverse
n'existe** pour structurer une stratégie F1-F7 sur 6-12 mois.

**Phase 0 (close 2026-05-06)** a livré 4 artefacts analyse :

| Livrable | Localisation | Output |
|----------|--------------|--------|
| F0.2 STRIDE | `~/.claude/plans/F0.2-threat-model-stride/` | 4 surfaces × 6 catégories STRIDE → 12 findings + 4 patterns transverses |
| F0.3 SAMM v2 | `~/.claude/plans/F0.3-samm-assessment.md` | Score 1.26 / 3 actuel → cible 2.07 / 3 sur 6 mois |
| F0.4 SLSA | `~/.claude/plans/F0.4-slsa-baseline.md` | Niveau L0.5 actuel → cible L2 sur 6 mois |
| F0.5 verdict | Vault audit-trail [[2026-05-06-plan-F-phase-0-verdict]] (PR #164 mergée) | Plan Phase 1 = 3 sprints × 2 sem (~22-25j cumulés) |

**Sprint arbitrage 2026-05-06** ([[2026-05-06-sprint-arbitrage-F]] PR #163,
[[2026-05-06-signal-d-empirical-update]] PR #166,
[[2026-05-06-signal-A-empirical-correction]] PR #172) confirme par mesure
empirique :

- Signal A (Sentry) : 0 issues PROD 14d, 0 events PROD 24h → **NOT RED**
- Signal F (npm audit + secret-grep) : 0 CVE CVSS≥7.0 + exploit path runtime ; secret-grep clean → **NOT RED**
- Signal D (GSC) : top 30 URLs traffic-driving = 100% indexed → **NOT RED**

→ Sprint suivant = **F par défaut P0→P8**, désormais avec evidence sur 3/3 signaux.

Cet ADR formalise le contrat Phase 1 sous gouvernance G3 (signature ED25519)
pour que les 3 sprints suivants opèrent contre une cible canon, pas contre
un scratch local DEV.

## Décision

### Architecture canonique

**Approche Phase 1 = threat-model-first** (STRIDE + LINDDUN si données
utilisateur), **map vers 3 standards industriels canon** :

1. **NIST SSDF v1.1** — 19 pratiques en 4 groupes (PO/PS/PW/RV)
2. **OWASP SAMM v2** — 5 fonctions × 3 practices (Governance / Design /
   Implementation / Verification / Operations)
3. **SLSA v1.0** — Build / Source / Distribution tracks, niveau cible L2

**4 couches enforcement** réplicant le pattern ADR-040
([[ADR-040-seo-roles-canon-ts-side-only]]) :

| Couche | Implémentation Plan F |
|--------|----------------------|
| 1. Compile-time | Branded types pour secrets, tokens, IDs (`SecretToken`, `JwtToken`, `WebhookSignature`) |
| 2. Runtime Zod boundary | `parseSecretOrThrow<T>` + counter `parse_failed_total` |
| 3. Static lint (ast-grep) | Rules `no-process-env-in-controllers`, `no-service-role-in-frontend`, `no-hardcoded-credentials` |
| 4. Observability counters | `secret_scan_failed_total`, `rls_violation_total`, `unauthorized_admin_attempt_total`, `webhook_signature_mismatch_total` |

### 3 sprints × 2 semaines (~22-25j cumulés)

**Sprint 1 — quick wins + critiques (~7-8j)** :

| Item | Source finding | Effort |
|------|----------------|--------|
| Aligner `GSC_SITE_URL` env var (Domain vs URL prefix) | F0.4 caveat (déjà fait 2026-05-06 post-cadre) | 0j (done) |
| Smoke-test event Sentry → valide wiring end-to-end | Phase 0 followup (déjà fait 2026-05-06) | 0j (done) |
| Session secret fail-fast si env missing | STRIDE 03-sessions critique #3 | 0.5j |
| Logout `req.session.destroy()` côté server | STRIDE 03-sessions important #10 | 0.25j |
| gitleaks/trufflehog en CI bloquant + audit historique git | F1+F7 + SAMM gap #1 | 2j |
| Rate limit callbacks paiement (Caddy + `@Throttle`) | STRIDE 01-paiement critique #2 | 1.5j |
| GitHub Actions `permissions:` per-job systématique | STRIDE 04-runner important #11 | 1j |
| Login lockout après N tentatives | STRIDE 02-admin / 03-sessions important #12 | 1j |
| SystemPay default `SIGNATURE_METHOD=SHA1 → SHA-256` | STRIDE 01-paiement important #6 | 0.5j |

**Sprint 2 — patterns transverses (~10-11j)** :

| Item | Source finding | Effort |
|------|----------------|--------|
| MCP `apply_migration` / `execute_sql` gate humain | STRIDE 02-admin critique #1 | 1j |
| Self-hosted runner ephemeral + blast radius audit | STRIDE 04-runner critique #4 + #5 | 2-3j |
| Pattern T1 — table `__app_audit_log` + middleware NestJS | Synthèse cross-surface | 3j |
| JWT admin `expiresIn: 1h` + refresh token rotation | STRIDE 02-admin important #7 | 2j |
| Redis auth + ACL (defense in depth) | STRIDE 03-sessions important #9 | 2j |

**Sprint 3 — SLSA Level 2 supply-chain (~5-6j)** :

| Item | Source finding | Effort |
|------|----------------|--------|
| Provenance attestation + cosign keyless via OIDC | F0.4 SLSA L2 | 2-3j |
| SBOM (Syft / CycloneDX) attaché image Docker | F0.4 SLSA L2 | 1j |
| Pinner Docker base + GH Actions par digest/SHA | F0.4 SLSA L2 | 1j |
| `docker compose` verify image avant pull prod | F0.4 SLSA L2 | 1j |

### Évidence requise pour promotion `proposed → accepted`

Cette ADR-043 reste `proposed` jusqu'à :

1. **Sprint 1 close** avec evidence (PRs monorepo mergées + audit-trail vault sprint-1-close)
2. **Mesure empirique amélioration** sur ≥ 1 signal :
   - SAMM Verification gap #1 fermé (gitleaks/trufflehog CI bloquant LIVE)
   - SAMM Operations gap réduit (rate limit + lockout LIVE)
   - 0 vulnerability high/critical avec exploit path runtime sur npm audit (pas le cas aujourd'hui mais réaliste post-Sprint 1)
3. **Audit-trail Sprint 1 verdict signé G3** dans vault avec décompte fixes
   livrés vs items planifiés.

Promotion à `accepted` post-Sprint 1 si ≥ 80% items livrés. Si Sprint 2 ou 3
diffère significativement du plan, amender via ADR-043-revised (semver bump
`version: 2.0`).

### Anti-patterns figés (interdits)

Pour éviter les régressions Phase 1 :

- ❌ **Ré-écrire ADR-021/028/030 + husky #266 comme « phase 1 du plan F »**.
  Ce sont des **préacquis** cités, pas des items à livrer.
- ❌ **Mélanger Sprint 1 quick wins et Sprint 2 patterns transverses dans
  une PR unique**. Discipline branche-par-item per memory DEV
  `feedback_branch_scope_discipline.md`.
- ❌ **Auto-escalader le scope Sprint** : un signal A/D rouge mid-sprint
  déclenche audit-trail intermédiaire signé G3 (`pause F / pivot X` ou
  `continue F / queue X`), pas pivot silencieux.
- ❌ **Promouvoir ADR-043 à `accepted` sans evidence Sprint 1** ; viole
  Q1/G6 anti-BS et règle canon (memory DEV
  `feedback_canon_rule_live_iff_adr_accepted.md`).

## Options Considérées

### Option A — Implémenter F1-F7 sans cadre (vision plan-directeur stricte)

**Description** : exécuter les 7 sujets F1-F7 listés dans `MOC-Roadmap-2026`
directement, sans Phase 0 d'analyse.

**Avantages** :
- Délivrable immédiat
- Pas de phase « papier »

**Inconvénients** :
- Pas de threat-model → priorisation arbitraire
- Pas de SAMM baseline → on ne sait pas si on progresse
- Pas de SLSA cible → SBOM/cosign omis ou bricolés
- Risque de réinvention des préacquis (ADR-021/028/030)
- Plan-directeur F1-F7 reflète priorités passées, pas signaux STRIDE
  empiriques (ex: rate limit callbacks paiement = critique non listé)

**Rejetée**.

### Option B — Plan F sur threat-model + SAMM + SLSA, 3 sprints (retenue)

**Description** : Phase 0 livre threat-model (STRIDE) + SAMM v2 self-assessment
+ SLSA L2 baseline. Phase 1 exécute en 3 sprints alignés sur findings empiriques.

**Avantages** :
- Standards industriels canon (NIST SSDF, OWASP SAMM, SLSA)
- Findings empiriques par surface (4 STRIDE pages livrées)
- Score SAMM mesurable J0 + J90 (mid-Phase 1) + J180 (cible 2.07)
- Pattern enforcement réplicable [[ADR-040-seo-roles-canon-ts-side-only]]
- Préacquis cités, pas réécrits

**Inconvénients** :
- 2 semaines Phase 0 « papier » avant tout code (mitigation : Phase 0
  parallélisable avec quick wins triviaux comme env var GSC, déjà appliqués)
- Self-assessment SAMM non-certifié → conformité externe (PCI-DSS QSA, RGPD
  DPO) reste hors scope

**Retenue**.

### Option C — Hire 3rd-party security audit + apply recommandations

**Description** : engager auditeur externe (consultant pen-test + SAMM
qualifié), recevoir rapport, appliquer recommandations.

**Avantages** :
- Conformité externe possible
- Vision indépendante (pas biais self-assessment)

**Inconvénients** :
- Coût élevé (5-15k€ pour pen-test + SAMM v2 assessor)
- Délai 4-8 semaines de l'engagement
- Recommandations non-prioritisées par signal business (revenue / risk)
- Hors-scope V1 (solo maintainer, budget limité)

**Différée Phase 3+** (post-Sprint 3, si maturité atteinte justifie).

## Conséquences

### Positives

- Plan F devient canon signé G3, plus de scratch local DEV référencé
  cross-session sans backlinks
- 4 couches enforcement répliquées d'ADR-040 → cohérence pattern enforcement
  monorepo
- Standards industriels (NIST SSDF / OWASP SAMM / SLSA) → langage commun avec
  futurs auditeurs externes
- Score SAMM J0 = 1.26 → mesurable mid-Phase 1 et fin-Phase 1, refus
  d'amélioration cosmétique non-quantifiée

### Négatives

- 22-25j d'effort cumulé sur 3 sprints = bande passante DEV indisponible
  pour autres chantiers (B catalogue, H marketing) pendant ~6 semaines
- Phase 0 « papier » avant code peut donner impression de non-livrable
  (atténué par 4 audit-trails vault déjà canonisés cumulant 800+ lignes)
- Promotion ADR-043 à `accepted` dépend de l'évidence Sprint 1 ; si Sprint 1
  livre < 80% items, ADR reste `proposed` indéfiniment (acceptable, pas
  d'urgence à canoniser)

### Neutres

- ADR-021/028/030 statut inchangé (déjà `accepted`, restent préacquis)
- Husky pre-push (PR monorepo #266) reste actif, aucune modification

## Critères de succès (mesurables)

| Critère | Cible 6 mois | Mesure |
|---------|-------------|--------|
| Score SAMM v2 global | ≥ 2.0 / 3 | Self-assessment J+90 et J+180 (Toolbox SAMM) |
| Score SAMM Verification — Security Testing | ≥ 2 | gitleaks/trufflehog en CI bloquant LIVE |
| Score SAMM Operations — Incident Management | ≥ 2 | SLA réponse incident formel + tiers gravité 1/2/3 documentés |
| Niveau SLSA Build track | ≥ 2 | Provenance + signature image (cosign keyless via OIDC) LIVE |
| Findings critiques STRIDE résolus | 5 / 5 | Audit-trail vault Sprint 1+2 close avec evidence par item |
| 0 régression sur préacquis | maintenue | ADR-021 RLS, ADR-028 prod isolation, ADR-030 supply-chain inchangés |

## Revue planifiée

- **J+30** (~2026-06-06) — Sprint 1 close. Audit-trail vault `2026-MM-DD-plan-F-sprint-1-close.md`. Décision `proposed → accepted` ou continuer Sprint 2.
- **J+90** (~2026-08-06) — Sprint 3 close. Mesure SAMM mid-cycle.
- **J+180** (~2026-11-06) — Cible SAMM 2.07. Décision suite (Phase 2 — refinement vs lock).

## Références

- [[MOC-Roadmap-2026]] — chantier F P0
- [[2026-05-06-sprint-arbitrage-F]] — verdict F par défaut P0→P8
- [[2026-05-06-plan-F-phase-0-verdict]] — Phase 0 close + plan Phase 1
- [[2026-05-06-signal-d-empirical-update]] — signal D NOT RED
- [[2026-05-06-signal-A-empirical-correction]] — signal A NOT RED + correction
- [[ADR-021-database-rls-hardening-zero-trust]] — préacquis F
- [[ADR-028-preprod-supabase-isolation]] — préacquis F
- [[ADR-030-npm-ignore-scripts-alpine-musl]] — préacquis F
- [[ADR-040-seo-roles-canon-ts-side-only]] — pattern 4-couches enforcement réplicable
- Plan DEV `~/.claude/plans/plan-F-devsecops-phase-0-scoping-20260506.md`
- Plan DEV `~/.claude/plans/F0.2-threat-model-stride/00-index-synthesis.md`
- Plan DEV `~/.claude/plans/F0.3-samm-assessment.md`
- Plan DEV `~/.claude/plans/F0.4-slsa-baseline.md`
- NIST SSDF v1.1 — https://csrc.nist.gov/Projects/ssdf
- OWASP SAMM v2 — https://owaspsamm.org/
- SLSA v1.0 — https://slsa.dev/
