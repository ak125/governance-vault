---
id: ADR-003
title: RPC Governance via RpcGateService
status: accepted
date: 2026-02-03
decision_makers: [Architecture Team]
supersedes: null
---

# ADR-003: RPC Governance via RpcGateService

## Contexte

Le projet utilise Supabase avec de nombreuses fonctions RPC (Remote Procedure Calls).
Certaines fonctions RPC sont critiques (DELETE massif, DDL, elevation de privileges).

**Probleme identifie**:
- 64+ fonctions RPC dangereuses identifiees dans le schema
- Risque d'appel accidentel ou malveillant
- Pas de controle centralise des acces RPC

## Decision

Implementation d'un service central **RpcGateService** pour controler tous les appels RPC.

### Architecture

```
Application → RpcGateService → evaluate() → ALLOW/BLOCK/OBSERVE → Supabase RPC
```

### Classification des fonctions

| Niveau | Acces | Exemples |
|--------|-------|----------|
| **P0 CRITICAL** | BLOCK_ALL | `delete_duplicates_batch`, `exec_sql`, `rollback_switch` |
| **P1 HIGH** | SERVICE_ROLE_ONLY | `execute_diff_apply_workflow`, `create_index_async` |
| **P2 MEDIUM** | SERVICE_ROLE_ALLOWLIST | `acquire_import_lock`, `create_batch_contract` |
| **ALLOWLIST** | READ_SAFE | 154 fonctions de lecture/validation |

### Fichiers de gouvernance

```
governance/rpc/
├── rpc_allowlist.json   # 154 fonctions autorisees
└── rpc_denylist.json    # 64 fonctions a risque (P0/P1/P2)
```

### Comportement

1. **Mode observe**: Log toutes les violations sans bloquer
2. **Mode enforce**: Bloque les appels selon le niveau configure
3. **Admin override**: Token special pour bypass (audit obligatoire)
4. **Fail-safe**: Bascule en observe si fichiers governance manquants

## Consequences

### Positives
- Controle centralise de tous les appels RPC
- Tracabilite complete (metriques, logs)
- Protection contre les appels accidentels

### Negatives
- Overhead sur chaque appel RPC
- Maintenance des listes allowlist/denylist

### Neutres
- Hot-reload possible sans restart

## Implementation

- Service: `backend/src/security/rpc-gate/rpc-gate.service.ts`
- Types: `backend/src/security/rpc-gate/rpc-gate.types.ts`
- Module: `backend/src/security/rpc-gate/rpc-gate.module.ts`

36 services utilisent actuellement RpcGateService.

## Verification

```bash
# Verifier les metriques du gate
curl http://localhost:3000/health | jq '.rpcGate'

# Verifier les fichiers de gouvernance
ls -la governance/rpc/
```

## References

- ADR-002 (Airlock & Zero-Trust)
- CLAUDE.md section "Rules R1-R7"

---
_Derniere mise a jour: 2026-02-03_
