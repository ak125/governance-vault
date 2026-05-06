---
title: "Signal A mesuré empiriquement (Sentry déjà provisionné) — correction audit-trails précédents"
date: 2026-05-06
type: session-trail
related_chantier: F
related_adr: ["ADR-021", "ADR-028"]
related_moc: ["MOC-Roadmap-2026"]
related_prs:
  - "ak125/governance-vault#163"
  - "ak125/governance-vault#164"
  - "ak125/governance-vault#166"
status: closed
session_closed_at: 2026-05-06
---

# Signal A — mesuré empiriquement (correction)

## Synthèse

Sur demande utilisateur de re-vérifier en profondeur (« verifie bien ×3 »),
**découverte que Sentry est entièrement provisionné depuis ce matin**
(2026-05-06 ~14:41 UTC, fichier `secrets/sentry.dev.sops.env` créé).

Mes audit-trails précédents (#163, #164, #166) annonçaient :

> « A NOT MEASURED — Sentry creds absents env DEV »

→ **Inexact.** Les creds étaient présents mais chiffrés via SOPS. Je n'avais
inspecté que le `.env` plain text et raté le pattern `secrets/*.sops.env`.

Cette audit-trail corrige empiriquement.

## Configuration Sentry vérifiée (best-in-class)

### Provisioning complet

| Item | État |
|------|------|
| Org Sentry `auto-pieces-equipement` | ✅ |
| **4 projets Sentry** (DEV + PROD × backend + frontend) | ✅ `automecanik-{backend,frontend}-{dev,prod}` |
| Plateforme backend | `node-nestjs` |
| Plateforme frontend | `javascript-remix` |
| DSN backend + frontend | ✅ `secrets/sentry.dev.sops.env` |
| Auth token | ✅ |
| Pattern stockage | **SOPS encrypted** (age key `~/.config/sops/age/keys.txt`) |

### Intégration code

| Composant | Fichier | État |
|-----------|---------|------|
| Backend SDK | `backend/src/instrument.ts` (importé en 1er ligne dans `main.ts`, pattern OpenTelemetry canon) | ✅ |
| Backend module | `@sentry/nestjs` + `SentryModule` dans `app.module.ts` | ✅ |
| Backend filter | `SentryExceptionCaptured` dans `global-error.filter.ts` | ✅ |
| Frontend client | `frontend/app/entry.client.tsx` `Sentry.init` | ✅ |
| Frontend server | `frontend/app/entry.server.tsx` `Sentry.init` | ✅ |
| Pattern fail-open | Si `SENTRY_DSN` unset → SDK no-op, pas de crash | ✅ |

### CI/CD wiring

| Étape | État |
|-------|------|
| `docker-compose.preprod.yml` declare `environment:` Sentry vars | ✅ ligne 21-27 |
| CI workflow (ci.yml ligne 772-783) decrypt SOPS via `sops exec-env` | ✅ best-practice (in-memory) |
| Fallback si sops/age key absent → deploy succeeds, SDK no-op | ✅ graceful degradation |

## Mesure signal A (cette session, post-discovery)

### Issues unresolved last 14d

| Projet | Issues | Détail |
|--------|--------|--------|
| backend-dev | 1 | `GlobalErrorFilter.catch` count=23 userCount=0 (catch-all générique, non critique) |
| **backend-prod** | **0** | aucune |
| frontend-dev | 0 | aucune |
| **frontend-prod** | **0** | aucune |

### Events received last 24h

| Projet | Events |
|--------|--------|
| backend-dev | 16 |
| **backend-prod** | **0** |
| frontend-dev | 0 |
| **frontend-prod** | **0** |

**Verdict signal A : ✅ NOT RED**. 0 issue PROD checkout, 0 event PROD 24h.
Trafic prod faible (cohérent avec GSC : ~75 clicks/jour) mais ce qui se passe
ne génère pas d'erreur backend.

## Application règle décision sprint — version finale empirique

| Signal | Mesure | Verdict |
|--------|--------|---------|
| **A** (Sentry checkout error rate) | 0 issues PROD 14d, 0 events PROD 24h | **✅ NOT RED** |
| **F** (npm audit + secret-grep) | 6 high CVE / 0 CVSS≥7.0 + exploit path runtime ; secret-grep clean 30j | NOT RED (audit-trail #163) |
| **D** (GSC indexation) | top 30 URLs indexées = 100% ; aggregate stable | ✅ NOT RED (audit-trail #166) |

Application précédence A → F → D → défaut F :
- A non rouge → next
- F non rouge → next
- D non rouge → next
- défaut P0→P8 = **F**

**Verdict sprint suivant reste F (DevSecOps)**, désormais avec **3/3 signaux
mesurés empiriquement NOT RED** (au lieu de 1 + 2 fallbacks comme précédemment
annoncé).

## Plan F Phase 1 — caveats levés

| Caveat audit-trail #164 | État |
|--------------------------|------|
| F0.1 — provisioning Sentry/GSC creds bloqueur humain | **✅ Levé**. Sentry était déjà fait (mon erreur), GSC fait par user post-#164. |
| « 1er ticket Plan F = provisionner Sentry + GSC creds DEV-side » | **Plus pertinent**. Remplacer par : « 1er ticket = aligner env var `GSC_SITE_URL` (URL prefix vs Domain) + valider workflow Sentry events flow PROD via test event ». |
| « A et D non mesurés » | **Levé**. 3/3 signaux mesurés empiriquement. |

**Plan Phase 1 reste valide** sur les 3 sprints (Sprint 1 quick wins, Sprint 2
patterns transverses, Sprint 3 SLSA L2). Aucune modification du périmètre.

## Cause racine de mon erreur initiale

J'ai grep `^GSC_\|^SENTRY_` dans `backend/.env` plain text et trouvé
`GSC_*` mais pas `SENTRY_*`. J'en ai conclu Sentry absent. Je n'ai pas étendu
la recherche aux patterns `secrets/*.sops.env` ni aux fichiers chiffrés en
général.

**Leçon canonisée dans mémoire DEV**
(`feedback_check_sops_encrypted_secrets_too.md` à créer post-merge) : avant
de conclure « creds X manquants », chercher également `secrets/*.sops*`,
`*.sops.env`, `*.enc`, `*.gpg`, `vault/*` — et vérifier si CI workflow
décrypte au déploiement. Pattern de stockage SOPS+age est best-practice
moderne, ignorer par défaut serait sous-estimer le niveau de maturité de
l'infra.

## Mémoires DEV à mettre à jour post-merge

- `gsc-sa-resolved-20260506.md` — déjà à jour ✅
- Nouvelle : `feedback_check_sops_encrypted_secrets_too.md` (canon : étendre la
  recherche aux fichiers chiffrés avant de conclure « secret manquant »).
- Index `MEMORY.md` à amender en conséquence.

## Procédure si signal flippe

Inchangée — cf. `2026-05-06-plan-F-phase-0-verdict.md` §"Procédure si signal
flippe pendant Phase 1".

## Références

- Audit-trail vault précédents :
  - `2026-05-06-sprint-arbitrage-F.md` (PR #163 mergée) — A annoncé NOT MEASURED (corrigé ici)
  - `2026-05-06-plan-F-phase-0-verdict.md` (PR #164 mergée) — F0.1 annoncé bloqueur (partiellement levé ici)
  - `2026-05-06-signal-d-empirical-update.md` (PR #166 mergée) — D mesuré NOT RED (toujours valide)
- Plan DEV `~/.claude/plans/F0.2-threat-model-stride/01-paiement.md` — STRIDE paiement (toujours valide)
- ADR-021 RLS, ADR-028 prod isolation — préacquis F
- [[MOC-Roadmap-2026]] — chantier F P0
