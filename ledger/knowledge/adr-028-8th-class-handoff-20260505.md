---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: ADR-028 cascade — 8e classe découverte 2026-05-05 (Invalid API key + RPC gate + script manquant)
slug: adr-028-8th-class-handoff
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-05"
updated_by: "@fafa"
related_adr:
  - "ADR-028"
related_prs:
  - "ak125/nestjs-remix-monorepo#298"
related_knowledge:
  - "adr-028-option-d-deploy-cascade-handoff-20260504"
status: current
tags:
  - adr-028
  - deploy
  - read-only
  - cascade
  - handoff
  - investigation
---

# ADR-028 cascade — 8e classe découverte 2026-05-05

> Suite directe de [[adr-028-option-d-deploy-cascade-handoff-20260504]].
> PR monorepo #298 (7e classe SESSION_SECRET) mergée 2026-05-05 12:48 UTC.
> Premier deploy main post-#298 → encore RED. 8e classe identifiée empiriquement.
> Document de handoff pour reprise en session dédiée.

## 1. Contexte

PR #298 (`fix/main-session-secret-readonly`) a réglé la 7e classe — SESSION_SECRET
strict-validation au bootstrap `backend/src/main.ts:64`. Mergée admin-squash
2026-05-05 12:48:21 UTC.

Run ci.yml `25377292210` (head SHA `82c1b62`) déclenché par le merge → step
`🧪 Deploy to PREPROD (read-only hardening — ADR-028 Option D)` failed après
4m42s, health check fail à 12:55:55 UTC (timeout 2 min).

**Différence vs classes 1-7** : les 7 premières étaient des **strict-throws au
boot** (`getOrThrow`, `throw new Error si !env`). La 8e classe = combo de
**runtime errors post-boot** qui empêchent le health check de répondre dans
les 2 minutes du smoke test.

## 2. Symptômes empiriques (logs run 25377292210)

### 2.1 Invalid API key Supabase (2 services non couverts par sweep classe 4)

```
{"context":"RagWebIngestDbService","msg":"failOrphanedRunningJobs failed: Invalid API key"}
{"context":"RagWebIngestDbService","msg":"listJobsByStatus failed: Invalid API key"}
{"context":"AdminJobHealthService","msg":"recordSuccess(seo-monitor) error: Invalid API key"}
```

Ces 2 services ne sont pas dans la liste des 15 (PR #284) ni des 4 (PR #287)
fixés en classes 4 et 5. Soit :

- (A) Sweep classes 4/5 incomplet — manque `getEffectiveSupabaseKey()` wiring
  pour ces 2 services
- (B) Les services utilisent une autre clé que Service Role (Anon ?
  Publishable ?) qui n'est pas valide en preprod
- (C) La clé est correcte mais le constructeur Supabase échoue silencieusement
  → premier appel runtime renvoie "Invalid API key" générique

**Note** : ce ne sont pas des throws au boot — le service démarre mais échoue
au premier RPC, ce qui n'apparaît pas dans le smoke test direct mais bloque
les jobs cron BullMQ qui tournent immédiatement après start.

### 2.2 RPC blocked par safety gate P1 enforce

```
{"context":"RpcGateService","env":"production","mode":"enforce","enforceLevel":"P1",
 "rpc":"get_random_vehicle_gamme_combinations","decision":"BLOCK",
 "reason":"UNKNOWN_BLOCKED_PROD",
 "error":"RPC blocked by safety gate: get_random_vehicle_gamme_combinations (UNKNOWN_BLOCKED_PROD)"}
```

Stack trace :
```
SeoMonitorProcessor.callRpc (supabase-base.service.js:308)
  → SeoMonitorProcessor.getRandomUrlSample (seo-monitor.processor.js:182)
    → SeoMonitorProcessor.handleMonitoring (seo-monitor.processor.js:89)
```

La RPC `get_random_vehicle_gamme_combinations` n'est pas dans la whitelist
P1 enforce — bloquée par `RpcSafetyGateService` (ADR-017). Soit :

- (A) RPC introduite récemment sans ajout au whitelist canon
- (B) Whitelist canon vit dans un fichier que la dernière mod a déplacé
  (suspect : la relocation canon-mirrors PR #303 a touché beaucoup de paths,
  vérifier qu'aucune liste RPC n'a glissé)
- (C) RPC volontairement bloquée mais le cron `seo-monitor` ne devrait pas
  s'exécuter en preprod read-only

### 2.3 Script Bash absent dans Docker image (secondaire)

```
{"context":"SeoAuditSchedulerService","msg":"💥 Job #repeat:... failed after 2 attempts:
 Command failed: /app/scripts/seo-audit-weekly.sh
 /bin/sh: /app/scripts/seo-audit-weekly.sh: not found"}
```

Job BullMQ `seo-audit-weekly` invoque un script absent du Dockerfile COPY.
Symptôme secondaire (n'aide pas le boot fail mais pollue les logs).

## 3. Investigation à mener (prochaine session)

### 3.1 Audit Supabase key effective au constructeur

```bash
# Trouver les 2 services qui échouent
grep -nE "createClient|new SupabaseClient" \
  backend/src/modules/rag/services/rag-web-ingest-db.service.ts \
  backend/src/admin/services/admin-job-health.service.ts

# Vérifier qu'ils utilisent getEffectiveSupabaseKey() (pattern PR #284)
grep -nE "getEffectiveSupabaseKey|SUPABASE_SERVICE_ROLE_KEY" \
  backend/src/modules/rag/services/rag-web-ingest-db.service.ts \
  backend/src/admin/services/admin-job-health.service.ts

# Tester la key directement en preprod
ssh 46.224.118.55 'docker compose exec backend env | grep SUPABASE_'
curl -sI -H "apikey: $KEY" -H "Authorization: Bearer $KEY" \
  "$SUPABASE_URL/rest/v1/" | head -3
```

Hypothèse de tête : ces 2 services manquent le helper `getEffectiveSupabaseKey()`
ajouté en PR #284 — c'est un sweep manqué de la classe 4. Fix : ajouter le
wiring dans les 2 fichiers, similaire aux 15 services déjà fixés.

### 3.2 RPC whitelist canon

```bash
# Trouver le canon de whitelist RPC
grep -rn "get_random_vehicle_gamme_combinations\|RPC_WHITELIST\|rpcWhitelist" \
  backend/src/database/ backend/src/config/ \
  governance-vault/ledger/rules/ governance-vault/ledger/decisions/

# ADR-017 RPC Cleanup phase 1 — voir mémoire `adr-017-rpc-cleanup.md`
```

Décider entre :
- Ajouter la RPC au whitelist canon (si légitime)
- Désactiver le cron `seo-monitor` en mode read-only
- Marquer la RPC `UNKNOWN_OK_PROD` (statut intentionnel non-bloquant)

### 3.3 Script Bash COPY dans Docker

```bash
grep -n "scripts/seo-audit" Dockerfile docker-compose*.yml
ls scripts/seo-audit-weekly.sh 2>/dev/null
```

Soit ajouter un `COPY scripts/ /app/scripts/` au Dockerfile, soit retirer le job
BullMQ si script obsolète.

## 4. Out of scope (intentionnel)

- **Fix immédiat** : pas de PR cette session — le fix demande audit grep + tests
  preprod, mérite session dédiée
- **Refonte ADR-028 Option D** : la cascade (8 classes empiriques, pas 7) suggère
  que l'audit aurait dû être plus large dès le départ. Pas un défaut d'Option D
  mais d'audit env-var/runtime-call. À documenter en post-mortem une fois la 8e
  fixée
- **Migration vers OptionE/F** : pas envisagé — Option D fonctionne, manque juste
  les sweeps complets

## 5. Coverage manifest (AEC v1.0.1)

- `verdict: PARTIAL_COVERAGE`
- Justification : la cause exacte des `Invalid API key` n'est pas confirmée
  empiriquement (3 hypothèses listées, aucune testée en preprod). Le diagnostic
  est basé sur lecture logs + cohérence avec le pattern classes 4/5. La RPC
  whitelist gap est plus certain. Le script Bash gap est trivialement vérifiable.
- À promouvoir `VALIDATED_FOR_SCOPE_ONLY` après que le fix preprod confirme la
  cause #2.1.

## 6. Self-review verdict: APPROVE

8-item checklist appliquée (canon `vault-self-review-workflow-20260504` §3) :

- ✅ Frontmatter (knowledge type, status current, related parent + ADR-028 + PR #298)
- ✅ Factuel (Run ID 25377292210 vérifiable via gh, head SHA 82c1b62, timestamps UTC précis, stack trace authentique extraite des logs)
- ✅ Math N/A (handoff doc, pas d'estimation chiffrée)
- ✅ Wikilinks ([[adr-028-option-d-deploy-cascade-handoff-20260504]] cible existante validée pre-commit)
- ✅ Pas d'overclaim (verdict explicite `PARTIAL_COVERAGE`, 3 hypothèses listées au lieu d'affirmer une cause unique, "Hypothèse de tête" vs assertion)
- ✅ Cohérence canon (étend handoff session 2 ADR-028 Option D, anti-patterns retex section 4 cohérent)
- ✅ Précédent (parent doc `adr-028-option-d-deploy-cascade-handoff-20260504` référencé bilateralement)
- ✅ MOC (lien à ajouter MOC-Knowledge §Investigations & honest debriefs juste après le doc parent — vérification G2 pre-commit)

## 7. Référence

- Doc parent : [[adr-028-option-d-deploy-cascade-handoff-20260504]] (vault PR #156 mergée 2026-05-04)
- PR monorepo cause : https://github.com/ak125/nestjs-remix-monorepo/pull/298 (mergée)
- Run rouge : https://github.com/ak125/nestjs-remix-monorepo/actions/runs/25377292210
- Mémoire associée : `adr-028-cascade-handoff-20260504.md` (auto-memory user-level, mise à jour 2026-05-05 avec 8e classe)
- ADR-017 RPC Cleanup phase 1 : voir mémoire `adr-017-rpc-cleanup.md`
- Pattern `getEffectiveSupabaseKey()` : voir PR #284 + `adr-028-cascade-handoff-20260504.md` §Pattern canon
