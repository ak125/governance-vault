# Politique CI/CD - Governance Vault

**Statut**: Actif
**Dernière mise à jour**: 2026-02-02

---

## Principe Fondamental

> **La CI est en LECTURE SEULE sur le governance vault.**
> Aucun workflow, action, ou script automatisé ne peut modifier le vault.

---

## Ce qui est AUTORISÉ

| Action | Outil | Usage |
|--------|-------|-------|
| Lire les règles | CI monorepo | Valider conformité code |
| Lire les templates | CI monorepo | Générer rapports |
| Lire l'audit trail | Dashboards | Monitoring |
| Exporter des logs | CI monorepo | Vers stockage externe |

---

## Ce qui est INTERDIT

| Action | Raison | Enforcement |
|--------|--------|-------------|
| `git push` depuis CI | Contourne signature | Hook pre-push |
| `git commit` depuis CI | Commits non signés | Config locale |
| GitHub Actions écrivant | Contourne validation | Pas de token write |
| Sync automatique | Pas de validation humaine | Script dry-run |
| IA commit directement | Pas de traçabilité humaine | Revue obligatoire |

---

## Architecture CI Recommandée

```
┌─────────────────────────────────────────────────────────┐
│                    MONOREPO CI                          │
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                  │
│  │   Build     │      │    Tests    │                  │
│  └──────┬──────┘      └──────┬──────┘                  │
│         │                    │                          │
│         ▼                    ▼                          │
│  ┌─────────────────────────────────────┐               │
│  │         Validation Rules            │ ◄─── READ     │
│  │    (lit .spec/00-canon/rules.md)    │     ONLY      │
│  └──────────────────┬──────────────────┘               │
│                     │                                   │
│                     ▼                                   │
│  ┌─────────────────────────────────────┐               │
│  │         Export Logs (externe)       │               │
│  │    (vers S3, GCS, pas le vault)     │               │
│  └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 GOVERNANCE VAULT                        │
│                                                         │
│  ┌─────────────────────────────────────┐               │
│  │   POINT D'ÉCRITURE UNIQUE           │               │
│  │   (VPS: /opt/automecanik/           │               │
│  │         governance-vault)           │               │
│  │                                     │               │
│  │   - Commits signés SSH              │               │
│  │   - Hook pre-push actif             │               │
│  │   - Validation humaine obligatoire  │               │
│  └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

---

## Intégration avec le Monorepo

### Lecture des Règles (Autorisé)

```yaml
# .github/workflows/validate-rules.yml
name: Validate Against Canon Rules

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Lire les règles depuis le canon local (pas le vault)
      - name: Validate imports
        run: |
          # Utilise .spec/00-canon/rules.md (monorepo)
          # PAS governance-vault
          ./scripts/validate-rules.sh
```

### Export de Logs (Autorisé - vers externe)

```yaml
# Export vers S3, pas vers le vault
- name: Export deployment log
  run: |
    aws s3 cp deploy-log.json s3://automecanik-logs/deploys/
```

---

## Workflow de Synchronisation Manuelle

Quand le canon change, la synchronisation est **manuelle**:

```bash
# 1. Sur le VPS (seul endroit autorisé)
ssh deploy@vps

# 2. Vérifier les changements (dry-run)
cd /opt/automecanik/governance-vault
./scripts/sync-canon.sh --dry-run

# 3. Valider humainement les changements
# Lire l'output, vérifier que c'est attendu

# 4. Appliquer avec commit signé
./scripts/sync-canon.sh --commit

# 5. Pousser (hook vérifie la signature)
git push origin main
```

---

## Tokens et Permissions

| Token | Scope | Usage |
|-------|-------|-------|
| `GITHUB_TOKEN` (CI) | `contents: read` | Lecture monorepo |
| Personal Access Token | Aucun sur vault | INTERDIT |
| Deploy key | Read-only | Optionnel pour clone |

**JAMAIS de token write sur governance-vault.**

---

## Exceptions

Aucune exception n'est autorisée.

Si un cas d'usage légitime nécessite une écriture automatisée:
1. Proposer une ADR
2. Validation CTO/CEO
3. Documenter dans [[signing-policy]]
4. Implémenter avec signature déléguée (HSM)

---

## Audit

Cette politique est vérifiée par:
- Revue trimestrielle des tokens GitHub
- Audit mensuel des signatures ([[../scripts/audit-signatures.sh]])
- Monitoring des push sur le repo

*Voir aussi: [[signing-policy]], [[cron-setup]]*
