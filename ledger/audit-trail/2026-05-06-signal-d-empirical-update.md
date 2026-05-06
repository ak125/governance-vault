---
title: "Signal D mesuré empiriquement post-GSC SA add — 30/30 indexed (NOT RED)"
date: 2026-05-06
type: session-trail
related_chantier: D
related_adr: ["ADR-040"]
related_moc: ["MOC-Roadmap-2026"]
related_prs:
  - "ak125/governance-vault#163"
  - "ak125/governance-vault#164"
status: closed
session_closed_at: 2026-05-06
---

# Signal D — mesure empirique post-déblocage GSC

## Synthèse

Suite à l'ajout du service account `ga4-mcp-server@automecanik-email.iam.gserviceaccount.com`
en **Owner** sur la propriété GSC `sc-domain:automecanik.com` (action humaine 2026-05-06,
~15 min après audit-trail Phase 0 verdict #164), signal D désormais mesurable
empiriquement.

**Verdict signal D : ✅ NOT RED** sur top 30 URLs traffic-driving.

## Mesures

### Aggregate searchAnalytics (28 derniers jours)

| Métrique | Valeur |
|----------|--------|
| Clicks | 2 093 |
| Impressions | 126 014 |
| CTR | 1.66% |
| Position moyenne | 14.9 |

**Lecture** : ~75 clicks/jour, page 2 Google en moyenne. Pas catastrophique
mais marge d'amélioration importante (CTR < 2% à position 15 = normal).

### URL Inspection — top 30 URLs par impressions

**30/30 indexed = 100%** verdict PASS, coverage "Submitted and indexed".

Profil des top 30 :
- ~22 URLs `/blog-pieces-auto/conseils/{piece}` (pages éditoriales R3-like)
- ~7 URLs `/constructeurs/{brand}/{model}/{type}.html` (pages véhicules R8-like)
- 1 URL homepage `/`

**Pas d'erreur 404, pas d'unknown URL, pas de coverage issue** sur les pages
qui font effectivement du trafic.

### Sample initial 5 URLs (à valeur indicative seulement)

Le sample initial avant cette mesure étendue a flagé 2 anomalies :

| URL | Verdict | Status | Note |
|-----|---------|--------|------|
| `/pieces/disque-de-frein.html` | NEUTRAL | 404 | URL inventée par test, n'existe pas en prod |
| `/blog-pieces-auto/calendrier-entretien` | NEUTRAL | URL unknown | URL inventée, n'existe pas en prod |

→ **Sample biaisé**, anomalies = artéfacts du test, pas findings réels.

## Application règle décision sprint (mise à jour)

| Signal | Mesure | Verdict |
|--------|--------|---------|
| **A** (Sentry checkout) | NOT MEASURED (Sentry creds toujours absents env DEV) | indéterminé → fallback NOT RED |
| **F** (npm audit + secret-grep) | 6 high CVE / 0 CVSS≥7.0 + exploit path runtime ; secret-grep clean 30j | NOT RED (audit-trail #163) |
| **D** (GSC indexation) | top 30 URLs indexées = 100% ; aggregate stable | **✅ NOT RED** (cette session) |

Application précédence A → F → D → défaut F :
- A non rouge → next
- F non rouge → next
- D non rouge → next
- défaut P0→P8 = **F**

**Verdict sprint suivant reste F (DevSecOps)**, désormais avec **evidence empirique
sur les 3 signaux** (A par défaut, F mesuré, D mesuré).

## Implications pour Phase 1 Plan F

Aucun changement sur Phase 1 (déjà cadrée audit-trail #164). Mais on récupère
deux observations utiles :

1. **D non urgent** : 100% top URLs indexées → la priorité pour D quand son tour
   viendra (post-F) sera **qualité de position** (avg 14.9 → cible page 1) plutôt
   que **coverage** (déjà bonne). Cela bascule le scope D1-D7 du plan-directeur :
   D6 (logs Googlebot) et D2 (sitemap par confiance) deviennent moins prioritaires
   que D1 (audit indexabilité par type page → mais avec angle "boost position"
   plutôt que "lever 404") et D5 (enrichissement R7/R3 stratégique).

2. **Findings F0.1 partiels** :
   - GSC creds : ✅ provisionné + autorisé (cette session)
   - Sentry creds : ❌ toujours non provisionné — reste bloqueur pour signal A

## Configuration corrigée

`backend/.env` actuel : `GSC_SITE_URL=https://www.automecanik.com` (URL prefix property).

**Réalité** : la propriété GSC est `sc-domain:automecanik.com` (Domain property).
Les deux formats existent dans GSC, ce sont des propriétés distinctes. La
service account a été ajoutée au format Domain.

**Action correctrice recommandée** (Sprint 1 Plan F, item rapide) : aligner
l'env var `GSC_SITE_URL=sc-domain:automecanik.com` ou garder URL prefix mais
ajouter un second var `GSC_DOMAIN_PROPERTY=sc-domain:automecanik.com` pour
les appels Domain-property-only (`urlInspection`).

## Mémoire DEV mise à jour

`~/.claude/projects/-opt-automecanik-app/memory/gsc-sa-permission-gap-20260506.md`
réécrite en `gsc-sa-resolved-20260506.md` (état RESOLVED + caveat env var format).

## Procédure si signal flippe

Inchangée — cf. `2026-05-06-plan-F-phase-0-verdict.md` §"Procédure si signal
flippe pendant Phase 1".

## Références

- Audit-trail vault précédent : `2026-05-06-sprint-arbitrage-F.md` (PR #163 mergée)
- Audit-trail vault Phase 0 verdict : `2026-05-06-plan-F-phase-0-verdict.md` (PR #164 mergée)
- Plan DEV `~/.claude/plans/F0.2-threat-model-stride/00-index-synthesis.md`
- Plan F Phase 0 scoping `~/.claude/plans/plan-F-devsecops-phase-0-scoping-20260506.md`
- [[MOC-Roadmap-2026]] — chantier D P2
- Memory DEV `gsc-sa-resolved-20260506.md` (post-action humaine GSC UI)
