---
type: moc
status: canon
updated: 2026-10-01
---

# MOC: Compliance

Index des plans d'exécution, checklists, audits et rapports de conformité.

---

## Plans d'Exécution Actifs

| Plan | Décision source | Status |
|------|-----------------|--------|
| [[2026-02-hardening-migration-plan]] | [[ADR-001-environment-separation]] | Executed |
| [[2026-02-hardening-execution-checklist]] | [[ADR-001-environment-separation]] | P0-P1 done, P2 pending |
| Stack canon `@repo/seo-roles` (9 PRs monorepo #304-312) | [[ADR-040-seo-roles-canon-ts-side-only]] | Executed (2026-05-05) |
| Cascade read-only hardening préprod (9 classes) | [[ADR-028-preprod-supabase-isolation]] | In progress (8/9 merged, 9e classe deploy regression — voir audit-trail 2026-05-07) |
| Plan F DevSecOps Phase 1 (NIST SSDF + OWASP SAMM v2 + SLSA L2) | [[ADR-043-plan-F-devsecops-phase-1-cadre]] | Proposed (cadre 3 sprints, threat-model-first) |
| Canon Enforcement Coverage Audit — registry [[REG-002-canon-files]] livrable C1 | [[ADR-048-canon-enforcement-coverage]] | Sprint 1 axe 1 LIVE (registry 35 fichiers categorises) |

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

Les evidence-packs sont constitués manuellement dans
`ledger/compliance/evidence-pack/YYYY/YYYY-MM/EP-YYYYMMDD-<slug>/`, conformément à
[[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]]. Leur index unique
`INDEX-EP-YYYYMMDD-<slug>.md` décrit les pièces du pack ; leur contenu dépend du
périmètre des preuves, pas d'un nombre fixe de documents.

### Packs 2026-02

- [[INDEX-EP-20260205-airlock-implementation]] - Implementation Airlock (observe -> enforce)
- [[INDEX-EP-20260205-incident]] - Incident response formalise
- [[INDEX-EP-20260205-monthly]] - Snapshot mensuel fevrier 2026
- [[INDEX-EP-20260205-test-v2]] - Refonte V2 test harness

### Packs 2026-04

- [[INDEX-EP-20260418-governance-hardening]] - Meta-vault hardening (Phase 5+6+residuels) — premier EP scope governance-vault

### Packs 2026-05

- [[INDEX-EP-20260506-adr-041-baseline]] - Baseline empirique ADR-041 (R1 router posture reaffirm)

### Rubriques historiques

Plusieurs packs existants utilisent les neuf rubriques ci-dessous. Cette liste décrit
leur organisation historique ; elle ne constitue pas un format uniforme pour tous les packs.

- `01-context.md` - Scope et objectifs
- `02-invariants.md` - Invariants examinés et preuves associées (T/G/AI/V)
- `03-decisions.md` - ADR et decisions associees
- `04-changes.md` - Changements appliques
- `05-ci-proof.md` - Preuves CI
- `06-audit-trail.md` - Journal chronologique
- `07-incidents.md` - Incidents lies
- `08-security-controls.md` - Controles de securite
- `09-attestations.md` - Revue et attestations de validation

Le pack [[INDEX-EP-20260506-adr-041-baseline]] utilise une autre organisation :
contexte, sources, script SQL, trajectoire, échantillons, recommandations et snapshot JSON.
Son index décrit ses pièces propres ; il n'est pas à convertir vers les neuf rubriques.

### Preuves, intégrité et validation

- Les preuves documentent les contrôles réellement exécutés, leurs résultats et leurs limites.
  La présence d'une rubrique ne prouve pas que le contrôle correspondant a eu lieu.
- Lorsqu'un `manifest.sha256` est présent, la vérification de ses empreintes porte uniquement
  sur les fichiers qu'il liste. Elle ne certifie ni leur véracité ni une validation humaine.
- La revue et les attestations humaines sont distinctes de la collecte et du contrôle d'intégrité.
  Elles ne se déduisent ni de la présence du pack ni d'un résultat CI.

Cette clarification ne modifie aucun pack historique et ne le déclare pas conforme rétroactivement.

> **Note historique** : certains packs référencent `DEC-002..013`, numérotation du canal de bundles Airlock
> distincte des quatre DEC legacy du vault reclassés en Phase 4. Voir [[airlock-decisions-reference]]
> pour le mapping DEC ↔ ADR, et ADR-102 D2 pour la lecture actuelle des références au canal retiré.

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
│   └── YYYY/YYYY-MM/EP-YYYYMMDD-<slug>/
└── reports/
    └── (à venir)
```

---

## Processus

1. **Décision** créée dans `ledger/decisions/adr/` (ADR signé)
2. **Plan d'exécution** créé dans `ledger/compliance/plans/`
3. **Checklist** créée si actions répétables (`ledger/compliance/checklists/`)
4. **Exécution** avec preuves (commits signés G3, logs, tests curl/Playwright)
5. **Evidence-pack** constitué manuellement si audit externe requis, selon ADR-102 et le workflow de [[AGENTS]]
6. **Rétrospective** dans `ledger/audit-trail/` si post-mortem utile

---

## Voir aussi

- [[MOC-Decisions]] - ADR canoniques
- [[MOC-Incidents]] - Post-mortems (source de nouvelles ADR)
- [[MOC-Rules]] - Règles canoniques T/G/AI/V
- [[rules-governance-process]] - G6 (Proof Requirements), G8 (Obsolete Handling)

---
