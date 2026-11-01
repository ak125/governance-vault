---
type: knowledge
status: canon
updated: 2026-10-01
related_adrs: [ADR-001, ADR-002, ADR-003, ADR-010, ADR-014, ADR-102]
---

# Airlock Decisions Reference (DEC-002 → DEC-013)

> **But de ce document** : lever l'ambiguite entre les anciens `DEC-001..004` du **vault** (reclasses en Phase 4 du refactor v2) et les `DEC-002..013` **canoniques de l'Airlock**, qui sont un systeme de numerotation distinct utilise dans les evidence-packs fevrier 2026.

---

## TL;DR — Deux systemes DEC

| Systeme | Scope | Statut |
|---------|-------|--------|
| **Vault DEC-001..004** (legacy) | 4 fichiers mal classes dans le vault (plans/audits presentes comme decisions) | **Reclasses** en Phase 4 (2026-04-17) → voir [[MOC-Decisions]] |
| **Airlock DEC-002..013** (canonique) | 12 decisions de securite internes a l'Airlock, referencees dans les evidence-packs | **Actifs**, formellement actes par les ADR listees ci-dessous, sauf DEC-004 (retire par ADR-102) |

Si tu lis `DEC-00X` dans le vault, refere-toi a [[MOC-Decisions]] pour determiner lequel.

---

## Mapping canonique Airlock DEC ↔ ADR

| Airlock DEC | Titre | ADR canonique | Remarques |
|-------------|-------|---------------|-----------|
| DEC-002 | Airlock Zero-Trust | [[ADR-002-airlock-zero-trust]] | Principe zero-trust et RPC gate. Le pipeline de bundles est retire par [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] (D1, D2) |
| DEC-003 | PREPROD GitHub Gate | [[ADR-001-environment-separation]] | Section "PREPROD" : seul PREPROD peut pusher vers github-actions |
| DEC-004 | Kill-Switch Global | [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] | **Retire** (D4). ADR-002 n'a pas de section "Kill-switch" et aucun code ne lisait `AI_VAULT_WRITE`. Reponse a incident : fermer les PR de l'agent, revoquer sa cle de signature et le jeton GitHub de sa machine |
| DEC-005 | Rotation des Secrets | *(policy operationnelle)* | Pas d'ADR dedie ; documente dans [[signing-policy]] pour les cles SSH, et dans les procedures interne monorepo |
| DEC-006 | CI Obligatoire | [[ADR-003-rpc-governance]] + [[rules-vault]] G4 | CI comme garde-fou systematique pour canon + RPC. G4 v3.1.0 (ADR-102 D3) : la CI du vault n'ecrit rien, verifie par `_scripts/check-ci-read-only.py` |
| DEC-007 | Incident Response | [[MOC-Incidents]] | Processus operationnel, pas une decision architecturale |
| DEC-008 | Read-Only PROD | [[ADR-001-environment-separation]] | Section "PROD" : strict read-only, pas de push direct |
| DEC-009 | Disaster Recovery | *(policy operationnelle)* | Pas d'ADR dedie ; backups Supabase + snapshots documentes dans le monorepo |
| DEC-010 | Access Control | [[ADR-010-airlock-enforce-activation]] | Phase enforce du RPC gate (ADR-010 §1 a §3), RBAC effectif |
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

**Pourquoi elles restent telles quelles** : les evidence-packs sont des **artefacts historiques immuables** (regle G8 Obsolete Handling). Les modifier reviendrait a reecrire l'histoire. Ce document de reference suffit a lever l'ambiguite au moment de la lecture.

---

## Si tu veux ajouter une nouvelle Airlock DEC

Non — on n'ajoute plus de DEC. Le systeme Airlock a ete fige a DEC-013. Toute nouvelle decision architecturale passe par le systeme ADR canonique du vault (voir [[_templates/adr-template]] et [[MOC-Decisions]]).

---

## Voir aussi

- [[MOC-Decisions]] — index des ADR du vault
- [[MOC-Compliance]] — Plans d'execution et evidence-packs
- [[ADR-002-airlock-zero-trust]] — Architecture Airlock principale
- [[ADR-001-environment-separation]] — DEV/PREPROD/PROD separation
- [[ADR-010-airlock-enforce-activation]] — Phase enforce de l'Airlock
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] — Airlock = RPC gate ; canal de bundles et kill-switch retires

---

_Derniere mise a jour: 2026-10-01 (ADR-102)_
