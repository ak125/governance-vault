---
title: "Plan F Phase 0 — verdict + plan Phase 1 (DevSecOps scoping close)"
date: 2026-05-06
type: session-trail
related_chantier: F
related_adr: ["ADR-021", "ADR-028", "ADR-030", "ADR-040"]
related_moc: ["MOC-Roadmap-2026"]
related_prs:
  - "ak125/governance-vault#163"
status: closed
session_closed_at: 2026-05-06
---

# Plan F Phase 0 — verdict & plan Phase 1

## Synthèse

Phase 0 du chantier F (DevSecOps) clôturée le 2026-05-06. 4 livrables analyse
produits côté DEV (`~/.claude/plans/`) :

- **F0.2** — STRIDE threat-model 4 surfaces e-commerce (paiement, admin, sessions, runner)
- **F0.3** — OWASP SAMM v2 maturity assessment (5 fonctions × 3 practices)
- **F0.4** — SLSA Level baseline (build/source/distribution)
- **F0.5** — Ce verdict

**F0.1** (provisioning Sentry/GSC creds DEV) reste **bloqué humain** — créer
les DSN Sentry et activer le SA Google. Identifié comme bloqueur arbitrage
sprint suivant ; à exécuter avant Phase 1.

## Métriques cumulées

| Indicateur | Valeur |
|-----------|--------|
| Surfaces threat-modélisées | 4 (paiement, admin, sessions, runner) |
| Findings totaux | 12 (5 critiques ❌ + 7 importants ⚠️) |
| Patterns transverses identifiés | 4 (T1 audit log, T2 rate limit, T3 secrets, T4 defense in depth) |
| Score SAMM actuel | **1.26 / 3** (entre ad-hoc et systematic) |
| Score SAMM cible 6 mois | **2.07 / 3** (systematic) |
| Niveau SLSA actuel | L0.5 (entre L0 et L1) |
| Niveau SLSA cible 6 mois | L2 |

## Verdict empirique

### Ordre F1-F7 ré-ordonné par criticité

Le plan-directeur listait F1-F7 sans hiérarchie. Le STRIDE + SAMM
ré-ordonnent l'urgence :

1. **F3** (MCP permissions dangereuses) — critique #1 STRIDE
2. **F4** (runner blast radius) — critique #4 + #5 STRIDE
3. **F1 + F7** (gitleaks/trufflehog en CI) — gap SAMM #1 + STRIDE T3
4. **F6** (permissions per-job workflows) — important #11 STRIDE
5. **F2 + nouveau F8** (SLSA Level 2 + SBOM + provenance + signature) — gap SAMM #5 + F0.4
6. **F5** (`service_role_key` côté serveur) — partiel via ADR-028, étendre

### Findings non couverts par F1-F7 actuels

À ajouter au plan F (extension F8-F10 ou intégrer F1-F7) :

- Rate limit callbacks paiement (critique #2 STRIDE)
- Session secret fail-fast si env missing (critique #3 STRIDE)
- SystemPay default SHA1 → SHA-256 (important #6)
- JWT admin 24h → 1h + refresh rotation (important #7)
- Table `__app_audit_log` unifiée (pattern T1)
- Redis auth + ACL (important #9)
- Logout `session.destroy()` (important #10)
- Login lockout (important #12)

### Plan Phase 1 (2 sprints × 2 semaines)

**Sprint 1 (~7-8 jours effort net, ~2 sem calendaires)** — quick wins + critiques :

| Item | Effort | Source |
|------|--------|--------|
| F0.1 — provisioning Sentry/GSC creds | 0.5j | Phase 0 carry-over |
| Critique #3 — session secret fail-fast | 0.5j | STRIDE 03-sessions |
| Important #10 — logout `session.destroy()` | 0.25j | STRIDE 03-sessions |
| F1 + F7 — gitleaks/trufflehog CI bloquant + audit historique | 2j | STRIDE T3 + SAMM #1 |
| Critique #2 — rate limit callbacks paiement | 1.5j | STRIDE 01-paiement |
| Important #11 — permissions per-job workflows | 1j | STRIDE 04-runner |
| Important #12 — login lockout | 1j | STRIDE 02-admin + 03-sessions |
| Important #6 — SystemPay SHA1 → SHA-256 | 0.5j | STRIDE 01-paiement |

**Total Sprint 1** : ~7.25j.

**Sprint 2 (~10-11 jours)** — patterns transverses + supply-chain :

| Item | Effort | Source |
|------|--------|--------|
| Critique #1 — MCP gate humain `apply_migration`/`execute_sql` | 1j | STRIDE 02-admin |
| Critique #4 + #5 — runner ephemeral + blast radius audit | 2-3j | STRIDE 04-runner |
| Pattern T1 — table `__app_audit_log` + middleware NestJS | 3j | Synthèse cross-surface |
| Important #7 — JWT admin 1h + refresh rotation | 2j | STRIDE 02-admin |
| Important #9 — Redis auth + ACL | 2j | STRIDE 03-sessions |

**Total Sprint 2** : ~10-11j.

**Sprint 3 (Phase 1 stretch)** — SLSA Level 2 :

| Item | Effort |
|------|--------|
| Provenance + signature image (cosign keyless via OIDC) | 2-3j |
| SBOM (Syft/CycloneDX) attaché aux images | 1j |
| Pinner Docker base + GH Actions par digest/SHA | 1j |
| Verify image avant docker-compose pull prod | 1j |

**Total Sprint 3** : ~5-6j.

## Décision finale

**Phase 0 = CLOSE** ✅ (4 livrables analyse + verdict).

**Phase 1 démarre** dès que :
1. F0.1 provisioning Sentry/GSC réalisé (humain pilote).
2. Mesure A/D activée pour arbitrage signal-prouvé du sprint suivant.
3. ADR-F1 cadre rédigée (Phase 1 ouverture, après Sprint 1 verdict).

**ADR-F1 cadre attendue** : status `proposed`, périmètre Sprints 1-2-3 ci-dessus,
approche threat-model first (F0.2) + SAMM-driven (F0.3) + SLSA-driven (F0.4).
Pattern enforcement = 4 couches ADR-040 réplicable.

## Caveats

1. **A et D non mesurés cette session** : creds Sentry/GSC absents env DEV.
   Premier ticket Phase 1 = F0.1. Sinon prochain arbitrage retombe sur défaut F
   sans signal.
2. **Self-assessment SAMM** : non-certifié OWASP. Pour conformité externe
   (RGPD DPO, PCI-DSS QSA), engager 3rd party Phase 3+.
3. **SLSA Level 3 hors atteinte** sans migrer GitHub-hosted runners (coût
   capacité Supabase MCP local). Trade-off accepté V1.
4. **SAMM score 1.26 → 2.07 = +0.81 sur 6 mois** : ambitieux mais réaliste
   si Sprints 1-2-3 livrés. À mesurer J+90 (mi-parcours).

## Procédure si signal flippe pendant Phase 1

Per plan DEV `verifier-tat-synth-tique-des-rosy-pebble.md` étape 6 :
- Si nouveau signal rouge `X` ≠ F (incident Paybox/SystemPay live, sandbox
  Google, désindexation brutale) → audit-trail intermédiaire signé G3.
- Décision : `pause Phase 1 / pivot X` (incident grave) ou `continue Phase 1 / queue X next sprint`.

## Références

- Plan DEV `~/.claude/plans/plan-F-devsecops-phase-0-scoping-20260506.md`
- F0.2 STRIDE `~/.claude/plans/F0.2-threat-model-stride/00-index-synthesis.md` (+ 4 pages)
- F0.3 SAMM `~/.claude/plans/F0.3-samm-assessment.md`
- F0.4 SLSA `~/.claude/plans/F0.4-slsa-baseline.md`
- Audit-trail vault précédent : `2026-05-06-sprint-arbitrage-F.md` (PR #163 mergée)
- [[MOC-Roadmap-2026]] — chantier F P0
- ADR-021/028/030 + PR monorepo #266 — préacquis F
- ADR-040 — pattern 4 couches enforcement à répliquer
- NIST SSDF v1.1 + OWASP SAMM v2 + SLSA v1.0 — référentiels canon Phase 1
