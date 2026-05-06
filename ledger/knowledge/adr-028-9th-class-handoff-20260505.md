---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: ADR-028 cascade — 9e classe découverte 2026-05-05 (PORT mismatch + 4 bruits log post-PR-A)
slug: adr-028-9th-class-handoff
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-05"
updated_by: "@fafa"
related_adr:
  - "ADR-028"
related_prs:
  - "ak125/nestjs-remix-monorepo#313"
  - "ak125/nestjs-remix-monorepo#298"
  - "ak125/nestjs-remix-monorepo#248"
related_knowledge:
  - "adr-028-8th-class-handoff-20260505"
  - "adr-028-option-d-deploy-cascade-handoff-20260504"
status: current
tags:
  - adr-028
  - deploy
  - read-only
  - cascade
  - handoff
  - investigation
  - port-mismatch
---

# ADR-028 cascade — 9e classe découverte 2026-05-05

> Suite directe de [[adr-028-8th-class-handoff-20260505]].
> PR monorepo #313 (PR-A : `guardReadOnly()` helper + 5 services gated) merged
> 2026-05-05 17:30:53 UTC, commit `1220b4b3`.
> Premier deploy main post-PR-A → encore RED. 9e classe identifiée
> empiriquement, dont 1 cause BLOCKING + 4 bruits log non-bloquants.
> Document de handoff pour reprise en session dédiée.

## 1. Contexte

PR #313 (`fix/adr028-pra-readonly-guards-20260505`) a délivré le scope minimal
viable PR-A du plan v3 : helper `guardReadOnly()` centralisé + gates au niveau
processor (pas scheduler) + dual-fallback distinct ShippingCalculator. Mergée
admin-squash via auto-merge 2026-05-05 17:30:53 UTC.

Run ci.yml `25391923356` (head SHA `1220b4b3`) déclenché par le merge → step
`🧪 Deploy to PREPROD (read-only hardening — ADR-028 Option D)` failed après
2 min, health check fail à 17:37:21 UTC (timeout `for i in {1..12}; do curl
-sf http://localhost:3200/health` retry every 10s).

**Différence vs 8e classe** : la 8e était un `Invalid API key` cascade sur
3 services. La 9e est un combo de :

- **1 cause BLOCKING** : PORT mismatch infra (préexistant depuis PR #248)
- **4 bruits log** : write/SELECT non gated par PR-A + Meilisearch init

PR-A a éliminé empiriquement les `Invalid API key` sur les 5 services qu'elle
a gated (RagWebIngestDb writes, AdminJobHealth writes, ShippingCalculator,
SeoMonitor processor, SeoAudit worker). Mais 2 nouveaux services émergent +
1 bug infra qui était caché derrière la 8e classe.

## 2. Cause #1 BLOCKING — PORT mismatch ci.yml vs docker-compose

**Symptôme** : container `(health: starting)` permanent. `wget
http://localhost:3000/health` (Docker healthcheck interne) ne reçoit pas de
réponse. Curl externe `http://localhost:3200/health` (workflow GH Actions)
timeout après 2 min.

**Logs runtime**:

```
2026-05-05T17:35:59.409Z {"context":"NestApplication","msg":"Nest application successfully started"}
2026-05-05T17:35:59.409Z {"msg":"Serveur opérationnel sur http://localhost:3200"}
```

Le serveur Nest démarre OK et annonce écouter sur 3200.

**Configuration**:

- `.github/workflows/ci.yml:732-733` génère `.env.preprod` avec :
  ```
  APP_URL=http://localhost:3200
  PORT=3200
  ```
- `docker-compose.preprod.yml:23` mappe `ports: - "3200:3000"` (host:container)
- `backend/src/main.ts:197` lit `const selectedPort = process.env.PORT || 3000`
- `docker-compose.preprod.yml:30` healthcheck `wget -qO- http://localhost:3000/health`

**Mécanisme du bug** :

1. Docker compose lance le container avec env `PORT=3200` (depuis env_file `.env`)
2. Nest lit `process.env.PORT` → écoute sur **3200 inside the container**
3. Docker compose mapping `3200:3000` route host port 3200 → container port 3000
4. **Rien n'écoute sur 3000 inside the container** → curl/wget connection refused
5. Healthcheck Docker interne (`wget localhost:3000/health`) permanent fail →
   container reste en `(health: starting)`
6. Workflow curl externe `localhost:3200/health` (host) → mapping container:3000 →
   nothing → fail
7. Timeout 2 min → workflow exit 1

**Régression introduite par** : PR #248 (commit `068d2088`, mergée 2026-05-01
00:17 UTC, "ci(preprod): retire ALLOW_PROD_ENV_COPY + SERVICE_ROLE_KEY — ADR-028
Option D Phase A"). Le bloc qui ajoute `PORT=3200` dans `.env.preprod` est
introduit dans cette PR.

**Preuve empirique du blocage continu** : aucun deploy main success dans les
200 derniers runs ci.yml (≈3 semaines, depuis avant ADR-028 Option D Phase A).
Seulement les jobs CI au niveau PR sont GREEN — auto-merge ne dépend pas du
deploy main step. La régression était cachée derrière la cascade ADR-028 8
classes (chaque classe précédente faisait crasher le boot avant même que le
PORT mismatch puisse manifester).

**Fix candidat (1 ligne)** :

| Option | Modification | Risque |
|---|---|---|
| (A) | Retirer `PORT=3200` du `.env.preprod` (ci.yml:733) → Nest default 3000 | None — aligne avec compose mapping |
| (B) | Changer compose mapping `"3200:3200"` (docker-compose.preprod.yml:23) | Casse l'API hôte stable, autres consumers du host:3200 |
| (C) | Aligner aussi healthcheck compose `wget localhost:3200/health` + APP_URL | Lourd pour gain symbolique |

Recommandation : **option (A)** — minimal, aligné avec convention Dockerfile
(internal 3000), reverse-compatible avec host:3200.

## 3. Causes #2-5 — bruits log non-bloquants (post-fix #1)

Une fois PORT fix, deploy passe GREEN mais ces 4 bruits log restent à traiter
en sweep PR-A.1 :

### 3.1 LegalService.createDocument — write op non gated (9.2)

```
{"context":"LegalService","err":{"type":"Error","message":"Échec de création
du document: Erreur lors de la création du document: Invalid API key",
"stack":"DatabaseException: ... at LegalService.createDocument
(/app/backend/dist/modules/support/services/legal.service.js:63:23) at async
LegalService.initializeDefaultDocuments (...:401:21)"}}
```

`LegalService.initializeDefaultDocuments()` appelle `createDocument()` au boot
(probable `OnApplicationBootstrap` hook). C'est un INSERT/UPSERT sur table
service_role-only. Sweep miss du PR-A — `LegalService` n'était pas dans le
scope plan v3.

**Fix** : ajouter `if (this.guardReadOnly('createDocument')) return;` dans
`backend/src/modules/support/services/legal.service.ts:createDocument()` (ou
au call site `initializeDefaultDocuments` pour court-circuiter le boucle entier).

### 3.2 RagWebIngestDbService.listJobsByStatus — SELECT non gated (9.3)

```
{"context":"RagWebIngestDbService","msg":"listJobsByStatus failed: Invalid API key"}
```

SELECT sur `__rag_web_ingest_jobs` (table REVOKE'd from anon par RLS hardening
ADR-021). Plan v3 §3.1 a délibérément laissé les SELECT inchangées avec leur
warn `[RLS BLOCKED]` existant comme fallback technique distinct.

**Réflexion** : ce log est attendu en preprod read-only (table service_role-only),
pas un drift technique. Donc le préfixe `[RLS BLOCKED]` est trompeur —
devrait être `[READ_ONLY]`. Décision PR-A.1 : soit gate explicite avec
`guardReadOnly` (cohérent avec writes), soit laisser tel quel (warn, non-bloquant).

Recommandation : gate `guardReadOnly` cohérent — uniformise le pattern.

### 3.3 LegalService.initializeDefaultDocuments boucle complete fail

```
{"context":"LegalService","msg":"Erreur lors de l'initialisation des documents:
Erreur lors de la création du document: Invalid API key"}
```

Conséquence directe de 9.2. Si `createDocument` est gated, ce log disparaît.

### 3.4 MeilisearchService init fail

```
{"context":"LogIngestionService","msg":"❌ Erreur init Meilisearch:"}
{"context":"MeilisearchService","msg":"❌ Failed to initialize Meilisearch"}
```

Externe à READ_ONLY. Probable : Meilisearch container pas démarré en preprod
(seulement Redis + Nest + Caddy dans `docker-compose.preprod.yml`).

**Fix** : soit ajouter Meilisearch service au docker-compose.preprod.yml, soit
gate l'init si `MEILISEARCH_HOST` absent/disabled.

### 3.5 CatalogService + InternalLinkingService warming errors

Cascade indirecte : `CatalogService` warm cache au boot dépend de SELECT sur
tables RLS-hardened. Idem `InternalLinkingService`. Probable que ces SELECT
échouent silencieusement avec warn fallback déjà géré par le code.

**Fix** : à investiguer après PR-A.1 minimum vital.

## 4. Investigation à mener (prochaine session)

### 4.1 Confirmer PORT mismatch empiriquement

Avant tout fix : vérifier en preprod live que le container écoute bien sur
3200 (pas 3000) :

```bash
ssh 46.224.118.55 docker exec nestjs-remix-monorepo-preprod ss -tlnp | grep -E "3000|3200"
ssh 46.224.118.55 docker exec nestjs-remix-monorepo-preprod wget -qO- http://localhost:3200/health
ssh 46.224.118.55 docker exec nestjs-remix-monorepo-preprod wget -qO- http://localhost:3000/health
```

Si curl 3200 OK et 3000 fail → confirme l'hypothèse.

### 4.2 Décider patch infra vs PR-A.1

| Patch | Scope | Effort | Bloquant deploy ? |
|---|---|---|---|
| **Patch #1 (PORT)** | `.github/workflows/ci.yml:733` retirer `PORT=3200` | 1 ligne | OUI — débloque GREEN |
| **PR-A.1 (sweep)** | `LegalService` + `listJobsByStatus` gates + Meilisearch | ~6 fichiers | NON (élimine bruits log) |

Recommandation : 2 PRs séquencées indépendantes.

### 4.3 Vérifier que main deploy redevient GREEN

Après Patch #1 :

```bash
gh pr view <patch-pr> --json mergedAt,mergeCommit
gh run watch <run-id-after-merge> --interval 30
gh run view <run-id> --log | grep -E "PREPROD is healthy|❌ PREPROD health check failed"
```

Si toujours RED → continuer investigation 10e classe.

## 5. Out of scope (intentionnel)

- **Fix immédiat** : pas de PR cette session — sequence Patch #1 (PORT, 1 ligne
  trivial) puis PR-A.1 (sweep) doit être pilotée par session dédiée
- **Refonte ADR-028 Option D** : la cascade 9 classes confirme que l'audit
  d'env-vars / runtime-calls aurait dû couvrir : (a) ports & networking infra,
  (b) tous les services qui font I/O au boot, pas seulement les write paths
  identifiés au forfait
- **Migration Option E/F** : pas envisagé — Option D fonctionne, manque les
  sweeps complets

## 6. Coverage manifest (AEC v1.0.1)

- `verdict: PARTIAL_COVERAGE`
- Justification : PORT mismatch (cause #1) est l'hypothèse la plus probable
  (preuve : aucun main deploy success dans 200 runs ci.yml + alignement parfait
  des configs ci.yml/compose/main.ts), mais non confirmée empiriquement par
  test direct sur le container preprod live (cf. §4.1). Causes #2-5 sont des
  bruits log observés directement dans les logs run `25391923356`. À promouvoir
  `VALIDATED_FOR_SCOPE_ONLY` après confirmation §4.1 et succès Patch #1.

## 7. Self-review verdict: APPROVE

8-item checklist appliquée (canon `vault-self-review-workflow-20260504` §3) :

- ✅ Frontmatter (knowledge type, status current, related_adr ADR-028,
  related_prs #313 + #298 + #248, related_knowledge parent docs cascade)
- ✅ Factuel (Run ID 25391923356 vérifiable via `gh run view`, head SHA
  `1220b4b3`, timestamps UTC précis, stack trace LegalService authentique
  extraite des logs `gh run view --log-failed`, regex preuve "200 runs zero
  success" via `gh run list -L 200 | grep main.*push.*success` retourne vide)
- ✅ Math N/A (handoff doc, pas d'estimation chiffrée)
- ✅ Wikilinks ([[adr-028-8th-class-handoff-20260505]] +
  [[adr-028-option-d-deploy-cascade-handoff-20260504]] cibles existantes,
  validé pre-commit G2)
- ✅ Pas d'overclaim (verdict explicite `PARTIAL_COVERAGE`, hypothèse PORT
  marquée "probable racine" pas affirmée à 100%, §4.1 demande validation
  empirique avant fix)
- ✅ Cohérence canon (étend cascade ADR-028 Option D, pattern handoff identique
  aux 7e/8e classes parent docs)
- ✅ Précédent (parent docs cascade référencés bilatéralement,
  related_knowledge frontmatter, mémoire `adr-028-cascade-handoff-20260504.md`
  à mettre à jour avec 9e classe en next session)
- ✅ MOC (lien à ajouter MOC-Knowledge §Investigations & honest debriefs juste
  après le doc 8e classe — vérification G2 pre-commit)

## 8. Référence

- Doc parent direct : [[adr-028-8th-class-handoff-20260505]] (vault PR #158
  mergée commit `f7612521`)
- Doc parent cascade : [[adr-028-option-d-deploy-cascade-handoff-20260504]]
  (vault PR #156 mergée 2026-05-04)
- PR monorepo cause indirecte (sweep classes 1-8 mais pas 9.2/9.3) :
  https://github.com/ak125/nestjs-remix-monorepo/pull/313 (mergée 17:30:53 UTC,
  commit `1220b4b3`)
- PR monorepo cause directe #1 PORT (régression) :
  https://github.com/ak125/nestjs-remix-monorepo/pull/248 (mergée 2026-05-01,
  commit `068d2088`)
- Run rouge :
  https://github.com/ak125/nestjs-remix-monorepo/actions/runs/25391923356
- Mémoire associée : `adr-028-cascade-handoff-20260504.md` (auto-memory
  user-level, à mettre à jour avec 9e classe en next session)
