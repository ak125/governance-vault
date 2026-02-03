# MOC: Decisions

Index des ADR (Architecture Decision Records) et décisions opérationnelles.

---

## ADR Actifs

| ID | Titre | Status | Date | Fichier |
|----|-------|--------|------|---------|
| ADR-001 | Environment Separation (DEV/PREPROD/PROD) | Accepted | 2026-02-03 | [[ADR-001-environment-separation]] |
| ADR-002 | Airlock & Zero-Trust Agents | Accepted | 2026-02-03 | [[ADR-002-airlock-zero-trust]] |
| ADR-003 | RPC Governance via RpcGateService | Accepted | 2026-02-03 | [[ADR-003-rpc-governance]] |
| ADR-004 | rm/ Module Scope (DEV-only) | Accepted | 2026-02-03 | [[ADR-004-rm-module-scope]] |
| ADR-005 | Airlock Observe Mode Activation | Accepted | 2026-02-03 | [[ADR-005-airlock-observe-activation]] |

---

## Décisions Opérationnelles Récentes

| Date | Décision | Impact |
|------|----------|--------|
| 2026-02-03 | Activation gouvernance formelle | Vault aligné avec réalité système |

---

## Par Catégorie

### Architecture
- [[ADR-001-environment-separation]] - Séparation des environnements DEV/PREPROD/PROD
- [[ADR-004-rm-module-scope]] - Classification module rm/ comme DEV-only

### Sécurité
- [[ADR-002-airlock-zero-trust]] - Principe Zero-Trust pour agents IA
- [[ADR-003-rpc-governance]] - Contrôle centralisé des appels RPC
- [[ADR-005-airlock-observe-activation]] - Activation Airlock mode observe

### Performance
- (aucune ADR active)

### SEO
- (aucune ADR active)

---

## ADR Legacy (Implicites)

Ces décisions existent dans le code mais n'ont pas d'ADR formelle:

| Décision | Source | Status |
|----------|--------|--------|
| Supabase Direct SDK (no Prisma) | CLAUDE.md R2 | Implicite - Rule R2 |
| Redis Sessions | CLAUDE.md R3 | Implicite - Rule R3 |
| Monorepo Structure | repo-map.md | Implicite - Canon |

> Note: Ces décisions sont documentées dans les règles (R1-R7) plutôt que comme ADR formelles.

---

## Template

Voir `02-decisions/_templates/`
- `adr-template.md` - Pour décisions architecturales
- `operational-decision-template.md` - Pour décisions opérationnelles

---

## Processus ADR

1. Contexte identifié
2. Options analysées
3. Décision prise (avec justification)
4. Conséquences documentées
5. Revue planifiée
6. Validation par decision_makers

---

_Dernière mise à jour: 2026-02-03_
