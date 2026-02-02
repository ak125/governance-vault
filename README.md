# Governance Vault

**AutoMecanik Governance Ledger**

Vault Obsidian dédié à l'audit, incidents, ADR, et règles IA.

---

## Règles Fondamentales

### R-Vault-01: Canon Fait Foi

> Le canon architectural reste **exclusivement** dans le monorepo (`.spec/00-canon/`).
> Ce vault est un **miroir enrichi opérationnel**, non normatif.
> En cas de conflit, `.spec/00-canon/` fait foi.

### R-Vault-02: Zéro Orphelin

> Aucun document ne peut être orphelin.
> Tout document doit être lié depuis **au moins 1 MOC**.

### R-Vault-03: Commits Signés

> Tous les commits DOIVENT être signés cryptographiquement.
> Un commit non signé invalide la piste d'audit.

---

## Structure

```
governance-vault/
├── 00-index/           # MOC (Maps of Content)
├── 01-incidents/       # Post-mortems
├── 02-decisions/       # ADR + décisions opérationnelles
├── 03-rules/           # Règles (R1-R11, AI-COS)
├── 04-audit-trail/     # Logs déploiements, sécurité
├── 05-compliance/      # Checklists, rapports
├── 06-knowledge/       # Architecture, glossaire
├── 99-meta/            # Gouvernance du vault
└── _assets/            # Diagrams, screenshots
```

---

## Synchronisation

Ce vault est synchronisé depuis `.spec/00-canon/` du monorepo via:

```bash
VAULT_PATH="/path/to/governance-vault" ./sync-canon.sh
```

---

## Vérification

```bash
# Vérifier les orphelins
./check-orphans.sh /path/to/governance-vault

# Vérifier les signatures
git log --show-signature -5
```

---

## Liens

- **Monorepo**: [nestjs-remix-monorepo](https://github.com/ak125/nestjs-remix-monorepo)
- **Canon**: `.spec/00-canon/`
- **Plan original**: `.spec/governance/governance-vault-plan.md`
