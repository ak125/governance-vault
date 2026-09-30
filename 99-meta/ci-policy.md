# Politique CI/CD - Governance Vault

**Statut**: Actif
**Dernière mise à jour**: 2026-09-30

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
| `git push` depuis CI | Contourne signature | `permissions: contents: read` dans chaque workflow du vault |
| `git commit` depuis CI | Commits non signés | `permissions: contents: read` (aucun push possible) |
| GitHub Actions écrivant | Contourne validation | Pas de token write |
| Sync automatique | Pas de validation humaine | Script dry-run |
| IA commit directement sur `main` | Pas de traçabilité humaine | PR requise (push direct refusé, `enforce_admins`). La protection n'exige aucune revue : voir [[branch-protection]] |

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
│  │        (sans acces au vault)        │     ONLY      │
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

La CI du monorepo lit le vault, dépôt public, sans jeton sur le vault :

- `99-meta/canon-hashes.json`, pour vérifier les copies des canons (`agent-exit-contract-hash.yml`,
  `marketing-voice-hash.yml`) et les resynchroniser par auto-PR **dans le monorepo** (`canon-sync.yml`,
  déclenché aussi par l'événement `canon-updated` de `canon-publish.yml`, voir [[canon-dispatch-setup]]) ;
- `ledger/decisions/adr/` en checkout partiel, pour refuser une référence à un ADR absent de `main`
  (`vault-canon-exists.yml`).

Aucune de ces lectures n'écrit dans le vault.

### Export de Logs (Autorisé - vers externe)

```yaml
# Export vers S3, pas vers le vault
- name: Export deployment log
  run: |
    aws s3 cp deploy-log.json s3://automecanik-logs/deploys/
```

---

## Workflow de Synchronisation Manuelle

Obsolète. `_scripts/sync-canon.sh` écrit des chemins v1 que le check requis `No V1 Paths (ADR-015)`
rejette, et un push direct sur `main` est refusé par la protection. Voir [[cron-setup]] et [[sync-log]]
(journal figé au 2026-02-02).

---

## Tokens et Permissions

| Token | Scope | Usage |
|-------|-------|-------|
| `GITHUB_TOKEN` (CI) | `contents: read` | Lecture monorepo |
| `GITHUB_TOKEN` (CI vault) | `contents: read` ; `issues: write` pour `vault-weekly-lint` et `vault-supabase-cost-check` | Checks, ouverture d'issues |
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
- Audit mensuel des signatures (`_scripts/audit-signatures.sh`) — cron non installé au 2026-09-30, voir [[cron-setup]]
- Monitoring des push sur le repo

*Voir aussi: [[signing-policy]], [[cron-setup]]*
