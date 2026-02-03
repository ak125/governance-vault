---
date: 2026-02-03
mode: ENFORCE
level: P2
blocks: 0
allowlist_size: 154
denylist_p0: 7
denylist_p1: 17
denylist_p2: 40
related_commits:
  - ba00599d  # Migration 12 read-only vers allowlist
  - 17eeeca1  # Fix Dockerfile builder stage
  - 1656d363  # Fix Dockerfile backend/ path
deployment: 21637757353
---

# Baseline RPC Safety Gate — P2 ENFORCE

This document freezes the first stable production state
with maximum enforcement and zero blocked calls.

## État vérifié

| Metric | Value |
|--------|-------|
| Mode | ENFORCE |
| Level | P2 (maximum) |
| Allowlist | 154 fonctions |
| Denylist P0 | 7 fonctions |
| Denylist P1 | 17 fonctions |
| Denylist P2 | 40 fonctions |
| Total Blocks | 0 |

## Règle d'évolution

Toute nouvelle fonction RPC :
1. Ajout en **DENY P2** par défaut
2. Observation en preprod
3. Promotion explicite vers allowlist si nécessaire

**Jamais l'inverse** = deny by default.

## Commits de référence

| Commit | Description |
|--------|-------------|
| `ba00599d` | Migration 12 fonctions read-only de P2 vers allowlist |
| `17eeeca1` | Fix Dockerfile (builder stage) |
| `1656d363` | Fix Dockerfile (backend/ path) |
| `f07b3856` | Merge fix/paybox-callback-orderid-format |

## Vérification

```bash
curl -s https://www.automecanik.com/health/rpc-gate | jq '{
  mode,
  enforceLevel,
  allowlistSize,
  denylistP0Size,
  denylistP1Size,
  denylistP2Size,
  totalBlocks
}'
```

## Résultat attendu

```json
{
  "mode": "enforce",
  "enforceLevel": "P2",
  "allowlistSize": 154,
  "denylistP0Size": 7,
  "denylistP1Size": 17,
  "denylistP2Size": 40,
  "totalBlocks": 0
}
```

## Audit mensuel

Commande de vérification périodique :

```bash
# Comparer avec baseline
curl -s https://www.automecanik.com/health/rpc-gate | jq '{
  allowlistSize,
  denylistP2Size,
  totalBlocks,
  diff_allowlist: (.allowlistSize - 154),
  diff_denylist: (.denylistP2Size - 40)
}'
```

---

*Baseline figé le 2026-02-03 après activation P2 ENFORCE avec zéro block.*
