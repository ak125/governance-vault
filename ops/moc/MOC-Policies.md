---
type: moc
status: canon
updated: 2026-10-01
---

# MOC: Policies

Index des **policies operationnelles** du vault : specifications, schemas JSON, processus de design.

> Les **regles canoniques** (T/G/AI/V) sont dans [[MOC-Rules]].
> Les **decisions d'architecture** sont dans [[MOC-Decisions]].

Les policies decrivent **comment** appliquer les regles (format, template, schema, prompt).

---

## Specifications

| Document | Role |
|----------|------|
| [[SOURCE-SCORE-WEIGHTS-SPEC]] | Contrat de poids source_score (ADR-096 D3) — dimensions, hard gates, profils, calibration |
| `source-score-weights.v1.json` | Contrat Layer 2 machine-readable, projete vers RAW via canon-hashes |

Les specifications, le prompt et l'exemple du canal de bundles sont archives ([[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]]), voir [[INDEX-archive]].

## Processus

| Document | Role |
|----------|------|
| [[PROCESS-G1-design]] | Processus de design des fiches agents (niveau G1, ADR-013) |
| [[exploration-budget]] | Exec contract G10 — scope strict + anti-creep + workflow probe (ADR-081) |

## Templates (\_templates)

Templates reutilisables pour creer de nouveaux documents conformes.

- [[adr-template]] - Template ADR (Architecture Decision Record)
- [[rule-template]] - Template pour nouvelles regles (T/G/AI/V)
- [[incident-template]] - Template post-mortem incident
- [[deployment-template]] - Template deploy checklist

---

## Processus

1. Une **regle** (dans `ledger/rules/`) dit QUOI faire
2. Une **policy** (dans `ledger/policies/`) dit COMMENT le faire (format, outillage)
3. Un **agent** applique la policy
4. Un **evidence-pack** prouve la conformite

---

## Voir aussi

- [[MOC-Rules]] - Regles canoniques T/G/AI/V
- [[MOC-Decisions]] - ADR associees
- [[MOC-Compliance]] - Plans d'execution, evidence-packs
- [[validator-engine-spec]] - SPEC-002 Validator (consomme les bundles)
