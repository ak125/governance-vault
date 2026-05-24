---
type: moc
status: canon
updated: 2026-04-17
---

# MOC: Policies

Index des **policies operationnelles** du vault : specifications de bundles, schemas JSON, prompts systeme, processus de design.

> Les **regles canoniques** (T/G/AI/V) sont dans [[MOC-Rules]].
> Les **decisions d'architecture** sont dans [[MOC-Decisions]].

Les policies decrivent **comment** appliquer les regles (format, template, schema, prompt).

---

## Specifications de Bundles

| Document | Role |
|----------|------|
| [[BUNDLE-SPEC]] | Specification complete d'un bundle (metadata, structure, contrats) |
| `bundle.schema.v1.json` | Schema JSON v1 pour validation programmatique |

## Processus

| Document | Role |
|----------|------|
| [[PROCESS-G1-design]] | Processus de design des bundles (phase G1) |
| [[exploration-budget]] | Exec contract G10 — scope strict + anti-creep + workflow probe (ADR-081) |

## Prompts Systeme

| Document | Role |
|----------|------|
| [[PROMPT-bundle-producer.v1]] | Prompt pour agent producteur de bundle |

## Exemples

- `policies/examples/bundle.example.v1/manifest.json` - Exemple manifest
- `policies/examples/bundle.example.v1/changes.patch` - Exemple patch
- `policies/examples/bundle.example.v1/constraints.json` - Exemple contraintes
- `policies/examples/bundle.example.v1/evidence.json` - Exemple evidence
- [[report]] - Exemple rapport

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

---

_Derniere mise a jour: 2026-04-17_
