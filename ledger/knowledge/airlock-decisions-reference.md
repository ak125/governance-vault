---
type: knowledge
status: canon
updated: 2026-04-18
related_adrs: [ADR-001, ADR-002, ADR-003, ADR-010, ADR-014]
---

# Airlock Decisions Reference (DEC-002 → DEC-013)

> **But de ce document** : lever l'ambiguite entre les anciens `DEC-001..004` du **vault** (reclasses en Phase 4 du refactor v2) et les `DEC-002..013` **canoniques de l'Airlock**, qui sont un systeme de numerotation distinct utilise dans les evidence-packs fevrier 2026.

---

## TL;DR — Deux systemes DEC

| Systeme | Scope | Statut |
|---------|-------|--------|
| **Vault DEC-001..004** (legacy) | 4 fichiers mal classes dans le vault (plans/audits presentes comme decisions) | **Reclasses** en Phase 4 (2026-04-17) → voir [[MOC-Decisions]] |
| **Airlock DEC-002..013** (canonique) | 12 decisions de securite internes a l'Airlock, referencees dans les evidence-packs | **Actifs**, formellement actes par les ADR listees ci-dessous |

Si tu lis `DEC-00X` dans le vault, refere-toi a [[MOC-Decisions]] pour determiner lequel.

---

## Mapping canonique Airlock DEC ↔ ADR

| Airlock DEC | Titre | ADR canonique | Remarques |
|-------------|-------|---------------|-----------|
| DEC-002 | Airlock Zero-Trust | [[ADR-002-airlock-zero-trust]] | Architecture Airlock + pipeline zero-trust v2.0 |
| DEC-003 | PREPROD GitHub Gate | [[ADR-001-environment-separation]] | Section "PREPROD" : seul PREPROD peut pusher vers github-actions |
| DEC-004 | Kill-Switch Global | [[ADR-002-airlock-zero-trust]] | Section "Kill-switch" : `AI_VAULT_WRITE=false` + arret d'urgence |
| DEC-005 | Rotation des Secrets | *(policy operationnelle)* | Pas d'ADR dedie ; documente dans [[signing-policy]] pour les cles SSH, et dans les procedures interne monorepo |
| DEC-006 | CI Obligatoire | [[ADR-003-rpc-governance]] + [[rules-vault]] G4 | CI comme garde-fou systematique pour canon + RPC |
| DEC-007 | Incident Response | [[MOC-Incidents]] | Processus operationnel, pas une decision architecturale |
| DEC-008 | Read-Only PROD | [[ADR-001-environment-separation]] | Section "PROD" : strict read-only, pas de push direct |
| DEC-009 | Disaster Recovery | *(policy operationnelle)* | Pas d'ADR dedie ; backups Supabase + snapshots documentes dans le monorepo |
| DEC-010 | Access Control | [[ADR-010-airlock-enforce-activation]] | Phase enforce de l'Airlock, RBAC effectif |
| DEC-011 | Observability | *(policy operationnelle)* | Logs, traces, metriques — documente dans canon monorepo |
| DEC-012 | Third-Party Risk | [[ADR-014-remove-paybox-callback-test]] | Decision specifique : suppression du test Paybox legacy (exposition reduite) |
| DEC-013 | Compliance & Evidence | Structure `ledger/compliance/evidence-pack/` | Pas d'ADR — c'est la structure elle-meme qui implemente la decision |

---

## Ou trouver les Airlock DEC dans le vault

Les references `DEC-00X` (numerotation Airlock) apparaissent dans :

- `ledger/compliance/evidence-pack/2026/2026-02/*/02-invariants.md`
- `ledger/compliance/evidence-pack/2026/2026-02/*/03-decisions.md`
- `ledger/compliance/evidence-pack/2026/2026-02/*/08-security-controls.md`
- `ledger/compliance/evidence-pack/2026/2026-02/*/09-attestations.md`
- `_scripts/gov` (comments)
- `_scripts/evidence-pack.sh` (comments)

**Pourquoi elles restent telles quelles** : les evidence-packs sont des **artefacts historiques immuables** (regle G8 Obsolete Handling). Les modifier reviendrait a reecrire l'histoire. Ce document de reference suffit a lever l'ambiguite au moment de la lecture.

---

## Si tu veux ajouter une nouvelle Airlock DEC

Non — on n'ajoute plus de DEC. Le systeme Airlock a ete fige a DEC-013. Toute nouvelle decision architecturale passe par le systeme ADR canonique du vault (voir [[_templates/adr-template]] et [[MOC-Decisions]]).

---

## Voir aussi

- [[MOC-Decisions]] — 14 ADR canoniques du vault
- [[MOC-Compliance]] — Plans d'execution et evidence-packs
- [[ADR-002-airlock-zero-trust]] — Architecture Airlock principale
- [[ADR-001-environment-separation]] — DEV/PREPROD/PROD separation
- [[ADR-010-airlock-enforce-activation]] — Phase enforce de l'Airlock

---

_Derniere mise a jour: 2026-04-18_
