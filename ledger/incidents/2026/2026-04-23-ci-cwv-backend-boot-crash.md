---
id: INC-2026-009
type: incident
title: "CI CWV Performance Gate bloqué : crash silencieux du backend Nest au fresh boot"
date: 2026-04-23
date_detected: 2026-04-22
date_resolved: 2026-04-23
severity: medium
status: resolved
impact_duration: ""
affected_systems:
  - ci
  - backend
  - performance-gates-workflow
root_cause: "APP_URL manquant dans env vars du step \"Start server\" de .github/workflows/perf-gates.yml. Le backend crashait avec ConfigurationException (payment.config.ts:48-62) au boot en CI. bufferLogs:true masquait partiellement la stack. Fix mergé via monorepo PR #123."
related_rules: []
related_adrs: []
owner: "@automecanik.seo"
reviewed_by: ""
tags:
  - incident/medium
  - post-mortem
  - ci-cwv
  - backend-boot
  - resolved
---

# INC-2026-009: CI CWV Performance Gate bloqué — crash silencieux du backend Nest au fresh boot

> [!warning] Résumé
> Le job `🔍 CWV Performance Check` (workflow Performance Gates) échoue systématiquement sur les PR qui le déclenchent. `npm start` du backend retourne exit 1 juste après `DiagnosticEngineModule` init, sans stack trace ni log d'erreur. Timeout 60s de l'attente `/health` → exit 124. **Aucun impact prod/DEV** : le backend déployé tourne (HTTP 200), c'est un problème de fresh boot CI-only. Bloque la mergeabilité des PR frontend qui déclenchent Performance Gates.

## Timeline

| Heure UTC | Événement |
|-----------|-----------|
| 2026-04-22 16:52 | Premier run CWV échoué PR #116. Interprété flake infra. |
| 2026-04-23 10:35 | Second run CWV échoué après rebase sur origin/main (post vague RLS 4a). Pattern identique. |
| 2026-04-23 10:45 | Prod + DEV confirmés HTTP 200. Crash CI-only. |
| 2026-04-23 11:05 | Log CI : dernière ligne Nest = `[DiagnosticEngineModule]`, puis `npm error code 1` en 10 ms. |
| TBD | Root cause |
| TBD | Fix |

## Impact

- **Utilisateurs affectés** : 0 (prod/DEV opérationnels)
- **Durée d'indisponibilité** : 0 (prod)
- **Impact business** : Performance Gates bloquant pour toute PR frontend. PR #116 (fix F5 brand-colors, innocent) en attente. Lighthouse n'a jamais tourné depuis 2+ jours → régression perf potentielle masquée.

## Observations

### Fonctionne
- Prod `https://www.automecanik.com/health` : HTTP/2 200 ✅
- Prod `https://www.automecanik.com/` : HTTP/2 200 ✅
- DEV VPS `http://46.224.118.55:3000/health` : HTTP/1.1 200 ✅
- 15/16 checks CI de PR #116 passent (typecheck, eslint, tests backend+frontend, codeql, security, migration safety, etc.)

### Échoue
- `npm start` CI → crash silencieux exit 1 après `DiagnosticEngineModule`
- Zéro stack, zéro log d'erreur Nest
- Timeout 60s `until curl http://localhost:3000/health` → exit 124

### Différences CI vs prod/DEV
- CI utilise **valeurs mock** :
  - `SESSION_SECRET=ci-perf-test-session-secret-not-for-production-use`
  - `SYSTEMPAY_CERTIFICATE_PROD=ci-mock-systempay-certificate-prod-not-for-production-use`
  - `PAYBOX_HMAC_KEY=0000000000000000000000000000000000000000000000000000000000000000`
- CI `NODE_ENV=production` peut activer validations strictes absentes en DEV

### Preuve d'innocence PR #116
```
frontend/app/routes/constructeurs.$brand.$model.$type.tsx        +3/-3
frontend/app/routes/constructeurs.$brand.$model.$type[.].tsx     +7/-3
frontend/app/routes/constructeurs.$brand.$model.$type[.]html.tsx +18/-4
```
Zéro fichier backend. Zéro config. Zéro dépendance.

## Hypothèses (non validées)

### H1 — Régression RLS récente
Vagues RLS 4a (#119) et 4b (#120) ont drop des policies dans les dernières 24h. Un service boot-time pourrait échouer sur une table désormais refusée. Contre-argument : commentaire migration 4b dit "Backend uses SUPABASE_SERVICE_ROLE_KEY only" + service_role policies préservées. **Action** : grep callsites boot sur `___config*`, `ic_postback`, `kg_*`.

### H2 — Paybox RSA STRICT mode refuse mocks
Commits récents `c91d804e paybox callback gate secure-by-default strict mode`. Avec `NODE_ENV=production`, validation stricte pourrait refuser `PAYBOX_HMAC_KEY=0000...`. **Action** : tracer constructeur `PaymentsModule`.

### H3 — Import dynamique helmet/compression
`main.ts` fait `await import('helmet')` dans try/catch. Contre-argument : catch global `console.error('Erreur lors du démarrage du serveur')` absent du log CI → erreur ne passe pas par ce try.

### H4 — bufferLogs: true avale la stack
`NestFactory.create(AppModule, { bufferLogs: true })` : si un module crash pendant init, stack trace pourrait être perdue. **Action** : désactiver bufferLogs temporairement ou `process.on('uncaughtException')` early.

## Root Cause

**APP_URL env var manquant dans le step "Start server" du workflow `.github/workflows/perf-gates.yml`**.

Le fichier `backend/src/config/payment.config.ts:48-62` valide 4 env vars obligatoires pour l'initialisation du PaymentsModule, dont `APP_URL`. Quand Nest monte AppModule, `payment.config.ts` throw `ConfigurationException('Missing required environment variable: APP_URL')` qui remonte dans le bootstrap. Le process exit avec code 1.

`NestFactory.create(AppModule, { bufferLogs: true })` dans `main.ts` bufferise les logs jusqu'à `app.useLogger(logger)`. L'exception tombe avant ce flush, d'où la perte partielle de la stack trace visible. Seule la ligne `[ExceptionHandler] Missing required environment variable: APP_URL` apparaît dans le log CI complet (le message metier de la DomainException).

Reproduction locale confirmée (Node 20, NODE_ENV=production, mocks CI exacts) :
- Avec `APP_URL` set → Nest démarre, HTTP 200 sur /health en <1s
- Sans `APP_URL` → `npm start` exit 1 en 50ms, 60s timeout `/health`, exit 124

## Résolution

**Monorepo PR #123** (commit `619919f3`, mergé 2026-04-23 ~15:00 UTC) : ajout d'une seule ligne dans le step "Start server" :

```yaml
APP_URL: http://localhost:3000
```

+ commentaire explicatif multi-lignes référençant cet incident.

**Hypothèses initiales toutes réfutées** :
- H1 (régression RLS vague 4a/4b) : ❌ backend ne touche pas ces tables au boot
- H2 (Paybox RSA strict refuse mocks) : ❌ crash pré-runtime Paybox
- H3 (helmet dynamic import) : ❌ `catch` global aurait loggé
- H4 (bufferLogs avale la stack) : ✅ partiellement vrai, a contribué à la difficulté du diagnostic mais pas la cause

## Résolution

À définir.

## Preuves

- Run CWV #1 pre-rebase : https://github.com/ak125/nestjs-remix-monorepo/actions/runs/24791159333/job/72548690575
- Run CWV #2 post-rebase : https://github.com/ak125/nestjs-remix-monorepo/actions/runs/24830539178/job/72677611190
- PR #116 (frontend R8, innocent) : https://github.com/ak125/nestjs-remix-monorepo/pull/116
- PR #119 vague 4a : https://github.com/ak125/nestjs-remix-monorepo/pull/119
- PR #120 vague 4b : https://github.com/ak125/nestjs-remix-monorepo/pull/120
- Migration 4a : `backend/supabase/migrations/20260422_drop_always_true_policies_kg_internal.sql`
- Migration 4b : `backend/supabase/migrations/20260423_drop_critical_anon_leak_policies.sql`
- Workflow : `.github/workflows/perf-gates.yml` step "Start server" timeout 60s

## Lessons Learned

1. **Performance Gates ne tourne pas sur toutes les PR**. PR RLS (SQL-only) ne le déclenchent pas → régression backend induite par RLS peut passer invisible.
2. **bufferLogs: true + crash silencieux = debug impossible**. Perte des stack traces si erreur arrive avant `useLogger`.
3. **Les mocks secrets CI doivent être testés**. Validation stricte `NODE_ENV=production` qui refuse les mocks = crash silencieux sans message utile.

## Actions Correctives

- [ ] A1 — Reproduire crash local avec env vars CI (mock creds + `NODE_ENV=production`). Owner: @backend-team — 2026-04-24
- [ ] A2 — Désactiver `bufferLogs` temporairement ou ajouter `process.on('uncaughtException')` early dans `main.ts`. Owner: @backend-team — 2026-04-24
- [ ] A3 — Identifier root cause (H1/H2/H3/H4) avec stack. Owner: @backend-team — 2026-04-25
- [ ] A4 — Ajouter Performance Gates sur PR touchant `backend/supabase/migrations/*.sql`. Owner: @devops — 2026-04-28
- [ ] A5 — Runbook `ops/runbooks/ci-debug.md` "crash CI-only backend". Owner: @automecanik.seo — 2026-04-30
- [ ] A6 — Décision PR #116 : admin merge justifié OU attendre résolution. Owner: @automecanik.seo — 2026-04-24

## Communication

- [ ] Équipe backend notifiée
- [ ] Commentaire PR #116 avec lien vers cet incident
- [ ] Post-mortem partagé après résolution

## Références

- [[2026-04-22-redis-public-exposure-bsi]] — Incident précédent même jour, parallèle des vagues RLS
- [[2026-04-20-gsc-5xx-vehicle-page-cold-rpc]] — Incident précédent sur vehicle page (R8)
- [[MOC-Incidents]]

---

*Créé le: 2026-04-23*
*Owner: @automecanik.seo*
*Status: investigating*
