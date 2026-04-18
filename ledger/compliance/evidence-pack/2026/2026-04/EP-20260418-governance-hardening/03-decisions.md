---
type: decisions
---

# Decisions

## Positionnement

La phase de hardening couverte par ce pack est **operationnelle** (structure documentaire + enforcement), **pas architecturale**. Aucune nouvelle ADR n'a ete creee. Les 14 ADRs canoniques restent intactes.

Pour l'index complet et actuel des ADRs, voir [[MOC-Decisions]].

## ADRs indirectement touchees (contexte, non-modifiees)

Ces ADRs sont referencees parce que leur **piste d'audit** beneficie du hardening operationnel (zero orphelin, commits signes, branch protection). Aucune modification n'a ete apportee a leur contenu.

- [[ADR-001-environment-separation]] — A produit Phase 4 (hardening PROD read-only) dont ce pack prolonge la trace de gouvernance documentaire
- [[ADR-002-airlock-zero-trust]] — Renforce par l'enforcement G3 (toute modif vault est signee et auditable)
- [[ADR-010-airlock-enforce-activation]] — Meme logique : l'audit-trail Airlock depend de la solidite du vault documentaire

## Nouveaux documents operationnels crees dans la periode

Ces documents vivent dans `99-meta/` ou `ledger/knowledge/` et ne sont pas des decisions architecturales — ils ne necessitent pas d'ADR.

| Document | Scope | Rule reference |
|----------|-------|----------------|
| [[airlock-decisions-reference]] | Mapping Airlock DEC-002..013 vs ADR monorepo | G6 (Proof Requirements) |
| [[branch-protection]] | Policy serveur main (4 checks + enforce_admins) | G1, G2, G3, G4 |
| [[signing-policy]] (mise a jour) | Lien vers branch-protection ajoute | G3 |
| [[key-registry]] (mise a jour) | Ajout cle K002 Fafa-Windows | G3 |

## Reclassement DEC legacy (contexte historique, pas cette periode)

Pour memoire, la reclassification des 4 vault DEC legacy a eu lieu en Phase 4 (anterieure a ce pack) :

| Ancien ID | Nouvelle localisation | Raison |
|-----------|----------------------|--------|
| DEC-001 | [[2026-02-hardening-migration-plan]] | Plan d'execution d'ADR-001, pas une decision |
| DEC-002 | [[2026-02-phase4-post-hardening-summary]] | Retrospective, pas une decision |
| DEC-003 | [[2026-02-paybox-compatibility-audit]] | Audit technique, pas une decision |
| DEC-004 | [[ADR-014-remove-paybox-callback-test]] | Seule vraie decision — promu ADR |

Ce reclassement est documente de facon canonique dans [[MOC-Decisions]] section "Décisions non-ADR (historique)". Aucune ADR dediee n'a ete creee pour le reclassement lui-meme — c'est une operation de curation.

## Decisions infrastructurelles prises durant la periode (hors ADR)

| Decision | Justification | Artefact |
|----------|---------------|----------|
| Hardcoder les cles publiques dans `.github/workflows/vault-governance.yml` | Cles publiques = non-sensibles; evite un secret Actions pour un usage verifiable | Workflow commit |
| Utiliser display names dans `required_status_checks.contexts` | GitHub matche par `name:` field, pas par job key (diagnostique apres PR #4 bloquee) | `_scripts/setup-branch-protection.sh` |
| `required_signatures: false` cote GitHub | Plan Free ne supporte pas ce parametre; le job CI `%G?` couvre equivalent | [[branch-protection]] |
| `find_python()` dans scripts `.sh` | Windows Store alias empoisonne `python`, il faut sonder `sys.version_info` | `_scripts/check-orphans.sh`, `_scripts/check-broken-links.sh` |

## Voir aussi

- [[MOC-Decisions]] — Index canonique des ADRs (source de verite)
- [[MOC-Rules]] — Regles T/G/AI/V
- [[airlock-decisions-reference]] — Mapping complet Airlock DEC ↔ ADR
