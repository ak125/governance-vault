# MOC: Governance

Master Index du vault de gouvernance AutoMecanik.

---

## Navigation Principale

- [[MOC-Incidents]] - Post-mortems et incidents
- [[MOC-Decisions]] - ADR et décisions opérationnelles
- [[MOC-Compliance]] - Plans d'exécution et checklists
- [[MOC-Rules]] - Règles techniques et gouvernance
- [[MOC-Knowledge]] - Base de connaissances

---

## Règles Vault

| Règle | Description | Enforcement |
|-------|-------------|-------------|
| R-Vault-01 | Canon fait foi | Sync one-way |
| R-Vault-02 | Zéro orphelin | check-orphans.sh |
| R-Vault-03 | Commits signés | Hook pre-push + config git |
| R-Vault-04 | CI read-only | Aucun write token |

---

## Meta

- [[README]] - Documentation du vault
- [[signing-policy]] - Politique de signature
- [[key-registry]] - Registre des clés
- [[sync-log]] - Log de synchronisation
- [[ci-policy]] - Politique CI/CD (read-only)
- [[cron-setup]] - Configuration des crons

---

## Statistiques

| Métrique | Valeur |
|----------|--------|
| Documents | ~30 |
| Incidents | 0 |
| ADR | 0 |
| Décisions | 1 |
| Règles | 19 |

*Dernière mise à jour: 2026-02-02*
