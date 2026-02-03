---
id: ADR-005
title: Airlock Observe Mode Activation
status: accepted
date: 2026-02-03
decision_makers: [Architecture Team]
supersedes: null
related_to: [ADR-002, ADR-003]
---

# ADR-005: Airlock Observe Mode Activation

## Contexte

Suite à l'audit Airlock du 2026-02-03, le système a été déclaré
**formellement gouvernable** avec:

- 4 ADR documentées (ADR-001 à ADR-004)
- 1 incident archivé (INC-2026-01-11)
- MOC alignés avec le contenu réel
- RpcGateService opérationnel

## Décision

Airlock est activé en **mode observe uniquement**.

### Configuration

| Paramètre | Valeur |
|-----------|--------|
| `RPC_GATE_MODE` | `observe` |
| `RPC_GATE_ENFORCE_LEVEL` | `P0` |
| Blocking | Non |
| Logging | Oui (sampling 1/100 ALLOW) |

### Scope

- Aucun blocage (BLOCK → OBSERVE)
- Métriques et logs actifs
- Création automatique de PR autorisée
- Agents sans droits d'écriture directe

## Critères de Sortie (Observe → Enforce)

La transition vers le mode enforce nécessite:

1. **Minimum 7 jours d'observation** avec métriques
2. **Revue des candidats bloqués** (fonctions P0/P1)
3. **Zero faux positifs critiques** sur période d'observation
4. **ADR séparée** documentant la décision de transition

## Conséquences

### Positives
- Collecte de données avant enforcement
- Identification des patterns d'appels RPC
- Risque réduit de blocages inattendus

### Négatives
- Pas de protection active (observe seulement)
- Nécessite monitoring actif

### Neutres
- Configuration réversible à tout moment

## Vérification

```bash
# Vérifier le mode actuel
curl -s http://localhost:3000/health | jq '.rpcGate.mode'
# Attendu: "observe"

# Vérifier les métriques
curl -s http://localhost:3000/health | jq '.rpcGate.totalCalls'
```

## Rollback

En cas de problème, désactiver complètement:

```bash
# .env
RPC_GATE_MODE=disabled
```

## Références

- ADR-002 (Airlock & Zero-Trust)
- ADR-003 (RPC Governance)
- Audit Trail 2026-02-03

---
_Dernière mise à jour: 2026-02-03_
