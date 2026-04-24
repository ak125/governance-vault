---
category: investigation
doc_family: knowledge
source_type: diagnostic
title: R8 Enricher "vehicle not found" — investigation post ADR-022 P2d merge
slug: r8-enricher-vehicle-not-found-investigation-20260424
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-24"
updated_by: "@claude"
related_adr: ["ADR-022"]
related_prs: ["nestjs-remix-monorepo#148"]
status: draft
---

# R8 Enricher "vehicle not found" — investigation 2026-04-24

## Symptôme

`POST /api/admin/r8/enrich/:typeId` retourne systématiquement :
```json
{"status":"failed","seoDecision":"REJECT","diversityScore":0,
 "warnings":["vehicle not found"],"reasons":["CONTENT_BROKEN"],
 "pageKey":"r8_vehicle_<id>"}
```

Testé sur **3 type_ids** (12180 SMART, 17106 SMART, 19053 autres) — tous KO
post-merge PR #148 (wire variation enricher).

## Ce qui fonctionne (éliminés comme cause)

| Vérification | Résultat |
|--------------|----------|
| RPC `get_vehicle_page_data_cached(12180)` via MCP Supabase | ✅ Retourne `{vehicle: {...}, catalog: ..., success: true}` |
| Cache `__vehicle_page_cache` WHERE type_id IN (12180, 17106, 19053) | ✅ 3/3 rows présents |
| Appel REST direct `/rest/v1/rpc/...` avec SERVICE_ROLE_KEY | ✅ Retourne payload complet avec `vehicle` key |
| RPC dans allowlist `governance/rpc/rpc_allowlist.json` | ✅ Présent |
| Route publique R8 `/constructeurs/smart-151/city-coupe-151001/0-8-cdi-12180.html` | ✅ HTTP 200 (utilise `VehicleRpcService` → même RPC) |
| Backend `/api/admin/vehicle-rag/status` + `generate/:modeleId` | ✅ Fonctionnent (preuve Supabase connection OK dans backend) |
| Backend PID 3007875 bound port 3000, démarré 16:32 (après rebuild dist post-#148) | ✅ |
| `grep selectVariation` dist `r8-vehicle-enricher.service.js` | ✅ Wire compilé |
| Process env `DEV_KILL_SWITCH` | ❌ Non-set (kill-switch inactif) |

## Key insight

**Deux services backend utilisent EXACTEMENT le même pattern** pour appeler
`get_vehicle_page_data_cached` :

1. `backend/src/modules/vehicles/services/vehicle-rpc.service.ts:64-68`
   ```typescript
   this.callRpc<any>('get_vehicle_page_data_cached',
     { p_type_id: typeId }, { source: 'api' });
   ```
   → Sert la route publique `/constructeurs/...` **FONCTIONNE** (HTTP 200)

2. `backend/src/modules/admin/services/r8-vehicle-enricher.service.ts:127-131`
   ```typescript
   this.callRpc<Record<string, any>>('get_vehicle_page_data_cached',
     { p_type_id: typeId }, { source: 'api' });
   ```
   → `fetchVehicleData()` retourne null → "vehicle not found" **ÉCHOUE**

Même SupabaseBaseService parent, même `callRpc` method, même RPC name,
même params, même context. Pourtant résultat opposé.

## Différences observées (à investiguer comme causes possibles)

### Diff 1 — Constructor super() call
- `VehicleRpcService` : `super()` sans configService → utilise `getAppConfig()` fallback
- `R8VehicleEnricherService` : `super(configService)` → utilise injected ConfigService

Impact théorique : clés Supabase identiques dans les 2 paths, devrait être équivalent.

### Diff 2 — RpcGate injection
- `VehicleRpcService` : injecte `rpcGate: RpcGateService` dans constructor + `this.rpcGate = rpcGate`
- `R8VehicleEnricherService` : **AUCUN** rpcGate injecté → fallback `{decision: 'ALLOW', reason: 'GATE_NOT_INJECTED'}`

Impact théorique : sans rpcGate, les deux décisions sont ALLOW → rien ne bloque.

### Diff 3 — Processus orphelins
Au moment de l'investigation, 3 processus `node dist/main.js` running :
- PID 2352136 (24h+ uptime)
- PID 2427877 (24h+ uptime)
- PID 3007875 (binds port 3000, démarré après rebuild dist)

Un des orphans pourrait avoir :
- Des connexions DB stale (mais ne devrait pas servir les requêtes port 3000)
- Des cache Redis stale (L1 via CacheService dans VehicleRpcService uniquement)

## Pistes non explorées (pour reprise)

### P1 — Kill orphan processes + retest
```bash
kill 2352136 2427877
# Wait 5s, re-auth, retest enrich endpoint
```
**Cost** : trivial. **Gain si succès** : confirme hypothèse orphan pollution.

### P2 — Ajouter console.log temporaire dans `fetchVehicleData`
```typescript
const { data, error } = await this.callRpc<Record<string, any>>(...);
this.logger.log(`fetchVehicleData: error=${JSON.stringify(error)} data_keys=${data ? Object.keys(data).join(',') : 'null'}`);
```
Commit debug branch, push, merge main, observe via stdout.
**Cost** : +5 lignes temporaires. **Gain** : voit le vrai payload côté backend.

### P3 — Compare invocation via VehicleRpcService direct depuis enricher
Injecter `VehicleRpcService` dans `R8VehicleEnricherService` et appeler
`vehicleRpc.getVehiclePageDataOptimized(typeId)` au lieu de `fetchVehicleData`.
Si ça marche → le problème est dans `fetchVehicleData` spécifiquement.

### P4 — Vérifier si `callRpc` a un timeout ou race condition
Le `fetchVehicleData` de l'enricher n'a pas de `Promise.race([timeout])` contrairement
à `VehicleRpcService` qui a `RPC_TIMEOUT_MS = 2000`. Si RPC prend > timeout du
callRpc interne, peut-être un wrap silent.

### P5 — Comparer version Supabase-js + JSON return type
`@supabase/supabase-js: ^2.95.0`. Known behaviors avec RPC retournant type
`json` (non `jsonb`) : peut être désérialisé différemment selon la version.

## État actuel à la pause (session 2026-04-24 ~16:45 UTC)

- Branche main à jour, wire enricher compilé dans dist
- Backend port 3000 restart réussi post-merge
- 2 orphan processes présents (non diagnostiqués)
- **Aucun console.log ajouté** (no bricolage per user preference)
- **Aucun orphan killé** (attente compréhension root cause)

## Reprise — ordre recommandé

1. **P1 kill orphans + retest** (15 min, low risk)
2. Si encore KO : **P2 console.log minimal diagnostique** sur une branche dédiée + commit signed
3. Analyser payload réel observé
4. Fix ciblé selon payload
5. Cleanup console.log
6. Merger fix
7. Reprendre rollout SMART

## Actions user possibles hors session

- Review cette investigation + décider P1 vs P2
- Killer manuellement les 2 orphan processes (2352136, 2427877)
- Vérifier via `pm2 logs` ou `systemd journalctl` si config logging existe

## Refs

- Issue reproductible : POST /api/admin/r8/enrich/12180
- PR #148 (merged 14:28 UTC) : wire selectVariation dans 5 blocs R8 enricher
- RPC Gate allowlist : `governance/rpc/rpc_allowlist.json` (contient bien l'RPC)
- Route publique fonctionnelle (preuve RPC + DB OK) : `/constructeurs/smart-151/city-coupe-151001/0-8-cdi-12180.html`
- ADR-022 design : `ledger/knowledge/r8-rag-control-plane-design-20260423.md`
- Plan rollout : monorepo `/home/deploy/.claude/plans/objectif-sont-les-page-validated-pizza.md`
