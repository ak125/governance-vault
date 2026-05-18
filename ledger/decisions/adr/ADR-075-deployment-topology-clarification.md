---
id: ADR-075
title: Deployment Topology Clarification (DEV / PREPROD / PROD vocabulary canon)
status: proposed
date: 2026-05-18
decision_makers: [Architecture Team, Fafa]
version: 1.0.0
supersedes: []
amends: [ADR-001]
related_rules: []
related_incidents: []
reviewed_by: ""
---

# ADR-075: Deployment Topology Clarification

## Contexte

L'audit empirique du 2026-05-18 a identifié **419 occurrences confuses** du terme "preprod" / "pré-prod" / "PREPROD" / "pre-prod" à travers le monorepo (118 occurrences), le vault (242 occurrences), et les mémoires Claude (59 occurrences). Le vocabulaire est utilisé pour désigner **trois choses différentes** sans canon unifié :

1. Le **tag Docker** `:preprod` (artefact CI)
2. Le **container CI éphémère** qui consomme ce tag
3. Un **environnement intermédiaire imaginaire** entre DEV et PROD (interprétation littérale du préfixe "pré-")

[ADR-001](ADR-001-environment-separation.md) énonce une séparation logique en 3 environnements (DEV / PREPROD / PROD), mais **ne précise pas la topologie physique** (machines, ports, image tags, qui consomme quoi). Cette imprécision a généré des erreurs documentaires factuelles répétées :

- **Hostname inventé** : `preprod.automecanik.com` apparaît dans `closure-sequence-sitemap-auth-pr9a-20260517.md:69` — n'existe pas (jamais provisionné).
- **Formule "preprod miroir"** dans `incident-traffic-drop-2026-04-22-sitemap-stale.md:32` — faux : PREPROD est READ_ONLY (ADR-028 Option D), pas une réplique.
- **Conflation "DEV preprod"** dans 7+ documents `audit/dependencies/*.md` et `.spec/runbooks/*.md` — confond 2 machines distinctes.
- **Mémoires Claude auto-contradictoires** : une mémoire (`feedback_preprod_tag_is_dev_environment.md`, factuellement incorrecte) affirmait que `:preprod` est déployé sur le VPS DEV — alors qu'en réalité le runtime preprod tourne sur le runner self-hosted co-localisé avec PROD.

Le user a corrigé la même confusion sur **au moins 3 sessions distinctes** (2026-05-16, 2026-05-17, 2026-05-18). Symptôme classique d'un canon manquant.

### Topologie physique réelle (vérifiée par sources canoniques 2026-05-18)

Sources : `.sops.yaml:24-40`, `docker-compose.preprod.yml`, `.github/workflows/ci.yml:588-712`, `.github/workflows/deploy-prod.yml`.

```
Machine 1 — VPS DEV (hostname dev-automecanik)
  Rôle : poste opérateur SSH (code, dev local)
  Container preprod : NON DÉPLOYÉ ICI (.sops.yaml:27 explicit)
  Container production : NON DÉPLOYÉ ICI
  Backend NestJS local éventuel via `npm run dev` (port 3000)

Machine 2 — Hetzner ubuntu-16gb-nbg1-1
  Rôle 1 : GitHub Actions self-hosted runner hetzner-prod
  Rôle 2 : Container PREPROD éphémère (port 3200, localhost only)
           - image :preprod, READ_ONLY=true, APP_URL=http://localhost:3200
           - cible : E2E Smoke + Lighthouse CI uniquement
           - aucun humain n'y interagit, aucun domaine public
  Rôle 3 : Container PRODUCTION live derrière Caddy (ports 80/443)
           - image :production, trafic réel utilisateurs
           - www.automecanik.com
```

**Conséquence critique** : "DEV pré-prod" est une **formule fausse**. DEV et PREPROD vivent sur **deux machines physiques distinctes**, avec des rôles complètement différents (poste opérateur vs container CI éphémère).

## Décision

Adopter le glossary canon `.claude/rules/deployment.md` du monorepo (livré par PR #590) comme **single source of truth terminologique** pour les environnements de déploiement AutoMecanik. **Amend ADR-001** pour préciser que :

1. **DEV** désigne le **poste opérateur** (machine physique 1, `dev-automecanik`). C'est un environnement de travail SSH, sans container deploy déployé.
2. **PREPROD** désigne le **container CI éphémère** sur la machine physique 2 (co-localisé avec le runner self-hosted), en `READ_ONLY=true`, dont la seule finalité est l'exécution automatique des E2E Smoke + Lighthouse CI après chaque push `main`. **Aucun humain n'interagit avec PREPROD**.
3. **PROD** désigne le **container live** sur la même machine physique 2, derrière Caddy, exposant le trafic utilisateurs réel via `www.automecanik.com`.

### Règles induites

- Le terme "DEV pré-prod" / "DEV preprod" est **interdit** — il conflate 2 machines distinctes.
- Le hostname `preprod.automecanik.com` **n'existe pas** ; PREPROD n'a pas d'URL publique.
- "preprod miroir" est **interdit** — PREPROD est READ_ONLY, pas une réplique.
- Le terme générique "staging" (compounds deployment : `staging soak/env/server/VPS/deploy/deployment/gate`) est **banni** dans ce repo — utiliser PREPROD ou PROD.
- Le tag Docker `:preprod` reste utilisé techniquement (alias flottant réécrit à chaque merge main), mais documenté explicitement comme **artefact**, pas comme environnement.

### Lint guard (defense-in-depth)

Le canon est appliqué mécaniquement par :
- `scripts/lint/check-preprod-vocabulary.sh` (script bash, 4 patterns interdits + allowlist canon/errata/CHANGELOG/log)
- `.husky/pre-commit` (hook local block staged `.md`)
- `.github/workflows/preprod-vocabulary-guard.yml` (job BLOCKING sur PR + push main)

Sans guard, la documentation drifte ; avec guard, la régression est impossible mécaniquement. Pattern canon `feedback_no_bricolage_escalate_to_industry_standard` (remonter au niveau structural face à confusion récurrente).

## Options Considérées

### Option A: Glossary canon + lint CI (RETENUE)

**Description** : ship un fichier rule canon + cleanup mémoires + lint automatisé. ADR amend ADR-001. Aucune migration physique (image tag, compose file, workflow job name) — ces renames sont deferred à un Lot 5 séparé, conditionnel à 7 jours de validation lint sans violation.

**Avantages** :
- Force la cohérence terminologique mécaniquement
- Zero breaking change runtime/CI
- Rollback trivial (revert PR)
- Documentaire + lint pour les humains et Claude AI
- Coût ~3h30 d'implémentation

**Inconvénients** :
- Le mot "preprod" reste utilisé physiquement (image tag, compose file, workflow job display name) — confusion résiduelle possible sur ces artefacts (mitigée par documentation explicite dans le glossary)
- Lint allowlist nécessite maintenance

### Option B: Patch surface — corriger les pires occurrences uniquement

**Description** : Errata sur les ~10 fichiers les plus visibles, sans canon central ni lint.

**Avantages** :
- Coût minimal (~30 min)
- Pas de nouveau guard à maintenir

**Inconvénients** :
- **Rejeté** : confusion récurrente sur 3+ sessions = problème structurel, pas patch surface (`feedback_no_bricolage_escalate_to_industry_standard`)
- Drift inévitable sans guard automatisé
- Pas de canon → futures contributions ne sauront pas où poser le vocabulaire

### Option C: Renames physiques complets

**Description** : Renommer `:preprod` → `:ci-smoke`, `docker-compose.preprod.yml` → `docker-compose.ci-smoke.yml`, job "Deploy PREPROD" → "CI Smoke". Migration en un cycle.

**Avantages** :
- Élimine la source physique du mot confus
- Aligne nommage avec sémantique réelle

**Inconvénients** :
- **Rejeté pour V1** : risque > bénéfice immédiat. Branch protection rules pinned par nom de job, badges README, alertes Grafana, scripts de runbook — chaque consumer doit être audité.
- Deferred au Lot 5 conditionnel post-validation lint 7j (plan migration phasé : aliases → shift → deprecation → remove sur 2+ sprints).

## Conséquences

### Positives

- Canon terminologique unifié, chargé à chaque session Claude (rule + CLAUDE.md anchor)
- 0 violation mécaniquement (510 fichiers `.md` scannés post-cleanup)
- Réduction du coût cognitif pour nouveaux contributeurs
- Audit-trail explicite (errata in-place sur les 2 mémoires fictives)
- Permet rollback trivial chaque lot

### Négatives

- Le mot "preprod" reste utilisé techniquement (image tag, compose file) — légère dissonance maintenue jusqu'au Lot 5 deferred
- Allowlist du lint à maintenir si nouveaux paths errata ou docs canon doivent contourner

### Neutres

- ADR-001 reste actif (séparation logique 3-env intacte) ; ADR-075 ajoute la précision physique
- Le Lot 5 (renames) reste optionnel, conditionné à evidence empirique post-déploiement

## Critères de succès

- [ ] PR monorepo #590 mergée
- [ ] Lint workflow `Preprod vocabulary guard` vert sur main
- [ ] Repo-wide scan `bash scripts/lint/check-preprod-vocabulary.sh` → `✅ 0 violations`
- [ ] Test cognitif Claude : nouvelle session répond "PREPROD = container CI sur runner 49.12.233.2, pas un VPS séparé" au prompt "Sur quelle machine tourne PREPROD ?"
- [ ] 7 jours sans violation détectée → Lot 5 (renames physiques) peut être considéré

## Self-review verdict

**Self-review verdict: APPROVE**

**Checklist 8 items** :

1. ✅ ADR référence ADR-001 explicitement (relation amend documentée)
2. ✅ Status `proposed` initial — passe à `accepted` après merge PR monorepo #590 + 24-48h observation
3. ✅ Topologie physique vérifiée par 4 sources canoniques distinctes (`.sops.yaml`, `docker-compose.preprod.yml`, `ci.yml`, `deploy-prod.yml`)
4. ✅ Décision énonce le canon AVANT les règles induites (structure logique)
5. ✅ Options considérées incluent une rejected alternative explicite (Option B patch surface) + une deferred (Option C renames)
6. ✅ Conséquences distingue positives / négatives / neutres avec honnêteté (ne sur-promet pas l'élimination complète du mot "preprod")
7. ✅ Critères de succès empiriquement mesurables (lint repo-wide + test cognitif)
8. ✅ Lien explicite vers PR monorepo qui implémente le canon (#590) — l'ADR ne flotte pas isolée

## Liens

- ADR-001 (amend) : [ADR-001-environment-separation.md](ADR-001-environment-separation.md)
- ADR-028 (Option D read-only PREPROD) : [ADR-028-preprod-supabase-isolation.md](ADR-028-preprod-supabase-isolation.md)
- Monorepo PR : https://github.com/ak125/nestjs-remix-monorepo/pull/590
- Canon SoT (monorepo) : `.claude/rules/deployment.md` (vit dans le monorepo, chargé à chaque session Claude)
- Lint guard : `scripts/lint/check-preprod-vocabulary.sh` + `.github/workflows/preprod-vocabulary-guard.yml`

---
_Dernière mise à jour : 2026-05-18_
