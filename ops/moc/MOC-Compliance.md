---
type: moc
status: canon
updated: 2026-04-17
---

# MOC: Compliance

Index des plans d'exécution, checklists, audits et rapports de conformité.

---

## Plans d'Exécution Actifs

| Plan | Décision source | Status |
|------|-----------------|--------|
| [[2026-02-hardening-migration-plan]] | [[ADR-001-environment-separation]] | Executed |
| [[2026-02-hardening-execution-checklist]] | [[ADR-001-environment-separation]] | P0-P1 done, P2 pending |

---

## Checklists

### Pre-Deploy

| Checklist | Usage | Décision de référence |
|-----------|-------|----------------------|
| [[pre-deploy-hardening]] | Avant deploy PREPROD/PROD | [[ADR-001-environment-separation]] |

### Post-Incident

- *(à créer)*

### Quarterly Review

- *(à créer)*

---

## Audits & Rétrospectives

| Document | Type | Date |
|----------|------|------|
| [[2026-02-phase4-post-hardening-summary]] | Retrospective | 2026-02-03 |
| [[2026-02-paybox-compatibility-audit]] | Audit Paybox | 2026-02-03 |

---

## Evidence Packs

Les bundles de preuves sont dans `ledger/compliance/evidence-pack/YYYY/YYYY-MM/EP-*/`. Chaque pack a un `INDEX.md` listant ses 9 documents canoniques.

### Packs 2026-02

- [[INDEX-EP-20260205-airlock-implementation]] - Implementation Airlock (observe -> enforce)
- [[INDEX-EP-20260205-incident]] - Incident response formalise
- [[INDEX-EP-20260205-monthly]] - Snapshot mensuel fevrier 2026
- [[INDEX-EP-20260205-test-v2]] - Refonte V2 test harness

### Packs 2026-04

- [[INDEX-EP-20260418-governance-hardening]] - Meta-vault hardening (Phase 5+6+residuels) — premier EP scope governance-vault

### Structure canonique (9 documents par pack)

- `01-context.md` - Scope et objectifs
- `02-invariants.md` - Invariants respectes (T/G/AI/V)
- `03-decisions.md` - ADR et decisions associees
- `04-changes.md` - Changements appliques
- `05-ci-proof.md` - Preuves CI
- `06-audit-trail.md` - Journal chronologique
- `07-incidents.md` - Incidents lies
- `08-security-controls.md` - Controles de securite
- `09-attestations.md` - Signatures de validation
- `manifest.sha256` - Hashes SHA-256 (integrity)

> **Note** : les evidence-packs referencent `DEC-002..013` qui est le systeme de numerotation **Airlock canonique** (different des 4 vault DEC legacy reclasses en Phase 4). Voir [[airlock-decisions-reference]] pour le mapping complet DEC ↔ ADR.

---

## Structure `ledger/compliance/`

```
ledger/compliance/
├── plans/
│   ├── 2026-02-hardening-migration-plan.md           (ancien DEC-001)
│   └── 2026-02-hardening-execution-checklist.md      (ancien DEC-001-execution-plan)
├── checklists/
│   └── pre-deploy-hardening.md
├── evidence-pack/
│   └── 2026/2026-02/EP-*/
└── reports/
    └── (à venir)
```

---

## Processus

1. **Décision** créée dans `ledger/decisions/adr/` (ADR signé)
2. **Plan d'exécution** créé dans `ledger/compliance/plans/`
3. **Checklist** créée si actions répétables (`ledger/compliance/checklists/`)
4. **Exécution** avec preuves (commits signés G3, logs, tests curl/Playwright)
5. **Evidence-pack** généré si audit externe requis
6. **Rétrospective** dans `ledger/audit-trail/` si post-mortem utile

---

## Voir aussi

- [[MOC-Decisions]] - ADR canoniques
- [[MOC-Incidents]] - Post-mortems (source de nouvelles ADR)
- [[MOC-Rules]] - Règles canoniques T/G/AI/V
- [[rules-governance-process]] - G6 (Proof Requirements), G8 (Obsolete Handling)

---

*Dernière mise à jour: 2026-04-17*
