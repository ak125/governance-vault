---
id: ADR-005
title: Airlock Observe Mode Activation
status: accepted-revised
version: 1.1.0
date: 2026-02-03
date_revision: 2026-03-07
decision_makers: [Architecture Team]
supersedes: null
related_to: [ADR-002, ADR-003, ADR-009, ADR-011]
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

## Moteur d'execution (revision v1.1 — ADR-011)

> Depuis ADR-011 (2026-03-07), Claude API remplace OpenClaw comme moteur d'execution des agents.
> L'Airlock observe mode s'applique desormais aux bundles generes par Claude API / Cowork.

## Criteres de Sortie (Observe → Enforce)

La transition vers le mode enforce necessite:

1. **Minimum 14 jours d'operation stable** avec Claude API comme moteur (cf. ADR-009 v2.0)
2. **Revue des candidats bloques** (fonctions P0/P1)
3. **Zero faux positifs critiques** sur periode d'observation
4. **Zero violation Airlock** en mode enforce
5. **ADR separee** documentant la decision de transition

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

## References

- ADR-002 v2.0 (Airlock & Zero-Trust — Claude API)
- ADR-003 (RPC Governance)
- ADR-009 v2.0 (Phase 1 Agent Activation)
- ADR-011 (Remplacement OpenClaw par Claude API)
- Audit Trail 2026-02-03

---
_Derniere mise a jour: 2026-03-07_
