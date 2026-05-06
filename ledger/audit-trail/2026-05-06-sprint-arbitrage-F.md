---
title: "Sprint arbitrage 2026-05-06 — verdict F (DevSecOps) par défaut P0→P8"
date: 2026-05-06
type: session-trail
related_chantier: F
related_adr: ["ADR-021", "ADR-028", "ADR-030", "ADR-040"]
related_moc: ["MOC-Roadmap-2026"]
related_prs:
  - "ak125/governance-vault#128"
  - "ak125/governance-vault#161"
  - "ak125/governance-vault#162"
status: closed
session_closed_at: 2026-05-06
---

# Sprint arbitrage 2026-05-06 — verdict F par défaut

## Synthèse

Suite à la canonisation de [[MOC-Roadmap-2026]] (vault PR #128 mergée
2026-05-06, commit `b53713f`), arbitrage du prochain sprint entre les
3 candidats équivalents F/A/D selon la grille
Revenue/Risk/Blocking/Effort/Evidence et la règle de décision conditionnelle
issue du plan DEV
`~/.claude/plans/verifier-tat-synth-tique-des-rosy-pebble.md` :

```
SI A signal rouge critique → A
SINON SI F signal rouge → F
SINON SI D signal rouge critique → D
SINON → F (par défaut P0→P8)
```

**Verdict : F (DevSecOps) par défaut P0→P8.** Aucun signal rouge critique
sur A. Signal F mesuré non-rouge. D non mesurable cette session (creds GSC
absents). Défaut P0 = F appliqué.

## Signaux mesurés (cette session)

### F — Vulnérabilités / secrets

**Outils utilisés** : `npm audit --json --production` (production tree only) +
substitut secret-grep manuel (gitleaks/trufflehog non installés).

**Résultats `npm audit --production`** :

| Severity | Count |
|----------|-------|
| critical | 0 |
| high | 6 |
| moderate | 19 |
| low | 0 |
| info | 0 |
| **total** | **25** |

**Détail high (CVSS ≥ 7.0 + exploit path runtime ?)** :

| CVE | Package | CVSS | Exploit path runtime |
|-----|---------|------|---------------------|
| GHSA-5j98-mcp5-4vw2 | `glob` (10.2.0–10.5.0) | 7.5 | ❌ vulnérabilité dans CLI `-c/--cmd` ; usage codebase = library import, pas CLI |
| GHSA-xxjr-mmjv-4gpg | `lodash` (≤4.17.22) | 6.5 | moderate inflated as "high" by audit aggregator |
| GHSA-3v7f-55p6-f55p | `picomatch` (4.0–4.0.4) | 5.3 | moderate inflated as "high" |
| GHSA-xf7r-hgr6-v32p | `multer` (<2.1.0) | (no score) | DoS only |
| `@nestjs/config` (high via lodash) | — | — | transitive of lodash |
| `@nestjs/platform-express` (high via core) | — | — | transitive |

**Verdict signal F** : **NOT RED**. Aucun CVE n'atteint le seuil J0
*« CVSS ≥ 7.0 + exploit path runtime »* simultanément. `glob` 7.5 = vrai high
mais exploit limité au CLI, codebase l'utilise comme library.

**Secret scan** : grep manuel sur 30j de commits pour patterns courants
(`sk-`, `ghp_`, `AIza`, `aws_secret`, `service_role_key=…`) → **0 hit**.
Couverture **partielle** — gitleaks/trufflehog à installer pour scan robuste
en sprint F (ticket F4 « secrets management »).

### A — Sentry checkout

**Non mesuré cette session** : Sentry creds (`SENTRY_AUTH_TOKEN`,
`SENTRY_ORG`, `SENTRY_PROJECT`) absents de l'env DEV utilisé. Mesure
nécessite session avec creds Sentry (humain pilote ou ticket dédié).

**Conséquence pour la règle** : ne peut pas confirmer A *« rouge critique »*.
Application du fallback : *défaut F*.

### D — GSC indexation

**Non mesuré cette session** : creds GSC (`GSC_CLIENT_EMAIL`, `GSC_PRIVATE_KEY`)
définis dans `backend/.env.example` mais vides dans l'env actif local DEV.
Mesure nécessite session avec creds GSC.

**Conséquence pour la règle** : ne peut pas confirmer D *« rouge critique »*.
Application du fallback : *défaut F*.

## Application de la règle de décision

| Étape | Évaluation | Résultat |
|-------|------------|----------|
| 1. A rouge critique ? | Non mesurable (creds absents) → traiter comme NOT RED par défaut | NEXT |
| 2. F rouge ? | NPM audit : 0 CVE CVSS≥7.0 + exploit path ; secret-grep clean | NOT RED, NEXT |
| 3. D rouge critique ? | Non mesurable (creds absents) → traiter comme NOT RED par défaut | NEXT |
| 4. Défaut P0→P8 | F | **F** |

**Caveats à documenter dans le ticket sprint** :

- A et D non mesurés → premier ticket Plan F = **« provisionner Sentry +
  GSC creds DEV-side pour pouvoir mesurer A/D au sprint suivant »**.
  Sinon arbitrage suivant retombera sur le même default sans signal.
- gitleaks/trufflehog à installer pour mesure F robuste.

## Décision

**Sprint suivant = chantier F (DevSecOps / sécurité prod)**, par défaut P0→P8.

**Justification empirique** : pas de signal rouge ailleurs ; pas de signal
rouge sur F non plus, mais F est P0 et le manque de plan global F1-F7 est le
risque latent maximal en absence de signal autre.

**Pattern attendu Plan F** : threat-model first (STRIDE), map F1-F7 vers NIST
SSDF v1.1 + OWASP SAMM v2 + SLSA Level cible. 4 couches enforcement réplicant
ADR-040 (TS branded / Zod boundary / ast-grep statique / Prometheus counters).
ADR-021/028/030 + husky #266 cités comme préacquis, pas réécrits. Phase 0 =
2 semaines scoping (threat-model + maturity assessment SAMM).

## Suivi (procédure si signal flippe)

Si avant ouverture du sprint F un signal A ou D devient rouge critique
(incident Paybox, Sentry checkout > seuil, sandbox Google, désindexation
brutale > seuil), audit-trail intermédiaire requis
(`2026-MM-DD-sprint-F-signal-{A|D}-detected.md`) et décision documentée
*pause F / pivot* selon gravité (canon plan DEV §"Procédure si signal
flippe en cours de sprint").

## Références

- [[MOC-Roadmap-2026]] — grille hebdo Revenue/Risk/Blocking/Effort/Evidence (canon depuis 2026-05-06)
- [[ADR-021-database-rls-hardening-zero-trust]] — préacquis F (RLS hardening)
- [[ADR-028-preprod-supabase-isolation]] — préacquis F (isolation prod)
- [[ADR-030-npm-ignore-scripts-alpine-musl]] — préacquis F (supply-chain hardening)
- [[ADR-040-seo-roles-canon-ts-side-only]] — pattern 4-couches enforcement à répliquer
- Plan DEV `~/.claude/plans/verifier-tat-synth-tique-des-rosy-pebble.md` — règle décision conditionnelle, étapes 4/5/6
- Vault PR #128 (mergée 2026-05-06, commit `b53713f`) — MOC-Roadmap-2026 canon shipped
- Vault PR #161 (open) — reconciliation `implementation_status` drift ADR-029/032/034
- Vault PR #162 (open) — tag `related_chantier: D` audit-trail 2026-05-05
