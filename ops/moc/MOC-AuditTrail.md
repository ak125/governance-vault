---
type: moc
status: canon
updated: 2026-04-17
---

# MOC: Audit Trail

Journal chronologique des **evenements de gouvernance** : audits ponctuels, retrospectives de phase, bundles rejetes par l'Airlock, audits RPC, post-mortems formalises.

> Les **ADR** sont dans [[MOC-Decisions]].
> Les **evidence-packs** (preuves structurees) sont dans [[MOC-Compliance]].

---

## Retrospectives & Audits (2026-02)

| Date | Document | Type |
|------|----------|------|
| 2026-02-02 | [[2026-02-02-rpc-safety-gate-audit]] | Audit (RPC Safety Gate) |
| 2026-02-03 | [[2026-02-03_governance-formalization-complete]] | Completion (v1 governance) |
| 2026-02-03 | [[2026-02-phase4-post-hardening-summary]] | Retrospective (Phase 4) |
| 2026-02-03 | [[2026-02-paybox-compatibility-audit]] | Audit (Paybox) |
| 2026-02-04 | [[2026-02-04_phase13-14-vault-sync-complete]] | Completion (vault sync) |
| 2026-04-17 | [[2026-04-17-governance-vault-v2-refactor]] | Retrospective (v2 refactor, 6 phases) |

---

## Sous-Sections

### Bundles Rejetes (par Airlock)

Les rejets Airlock sont journalises pour prouver le fonctionnement du garde-fou.

- [[INDEX-bundles-2026-02]] - 8 bundles rejetes en fevrier 2026

### Audits RPC

- [[INDEX-audit-trail-rpc]] - Baselines P2 enforce, audits RpcGateService

---

## Processus

1. **Evenement** detecte (rejet Airlock, incident, completion de phase, audit planifie)
2. Document cree dans `ledger/audit-trail/` ou son sous-dossier thematique
3. Frontmatter : `type: audit-report | retrospective | completion | bundle-rejection`
4. Lien retour vers ADR(s) et plan(s) concernes
5. Si post-mortem -> peut produire une nouvelle ADR (voir [[MOC-Incidents]])

---

## Voir aussi

- [[MOC-Decisions]] - ADR canoniques
- [[MOC-Compliance]] - Plans d'execution et evidence-packs
- [[MOC-Incidents]] - Post-mortems formalises
- [[MOC-Rules]] - Regles T/G/AI/V
- [[validator-engine-spec]] - Les 10 gates qui produisent les bundles REJECTED

---

_Derniere mise a jour: 2026-04-17_
