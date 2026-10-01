# Politique CI/CD - Governance Vault

**Statut**: Actif
**Dernière mise à jour**: 2026-10-01

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
| `git push` depuis CI | Contourne signature | `check-ci-read-only.py` : aucun `git push` dans une étape `run:`, bloc `permissions:` racine sans scope `write` hors `issues` |
| `git commit` depuis CI | Commits non signés | `check-ci-read-only.py` : aucun `git commit` dans une étape `run:` |
| GitHub Actions écrivant | Contourne validation | `check-ci-read-only.py` : aucun jeton autre que le `GITHUB_TOKEN` du workflow, sauf l'exception nommée (voir « Tokens et Permissions ») |
| Sync automatique | Pas de validation humaine | Script dry-run |
| IA commit directement | Pas de traçabilité humaine | Revue obligatoire, et un agent ne fusionne jamais (G4, ADR-102). Mécaniquement : PR requise (push direct refusé, `enforce_admins`), mais la protection n'exige aucune revue, voir [[branch-protection]] |

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

État au 2026-09-30 : aucun workflow ni script du monorepo ne lit `.spec/00-canon/rules.md` ;
les lectures réelles du vault par la CI du monorepo sont listées ci-dessous.

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

Retirée. `_scripts/sync-canon.sh` (monorepo → vault) est supprimé par
[[ADR-101-vault-decides-canon-authority|ADR-101]] : la seule synchronisation va du vault vers le
monorepo (`sync_canon_mirrors.py`, ADR-061 §3). Journal historique : [[sync-log]] (figé au 2026-02-02).

---

## Tokens et Permissions

| Token | Scope | Usage |
|-------|-------|-------|
| `GITHUB_TOKEN` (CI) | `contents: read` | Lecture monorepo |
| `GITHUB_TOKEN` (CI vault) | `contents: read` ; `issues: write` pour `vault-weekly-lint` et `vault-supabase-cost-check` | Checks, ouverture d'issues |
| Jeton d'App GitHub (`canon-publish.yml`, job `dispatch`) | Limité au dépôt cible de chaque itération (`repositories:`), jamais le vault | `repository_dispatch canon-updated` vers les dépôts consommateurs (ADR-061 §3) |
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
- À chaque PR : `_scripts/check-ci-read-only.py` sur les workflows réels (`test_ci_read_only.py`, check requis `Vault Scripts Tests`, [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]]). Toute nouvelle exception (scope `write`, jeton) s'ajoute dans ce script, par PR
- Revue trimestrielle des tokens GitHub
- Audit mensuel des signatures (`_scripts/audit-signatures.sh`) — cron non installé au 2026-09-30, voir [[cron-setup]]
- Monitoring des push sur le repo

*Voir aussi: [[signing-policy]], [[cron-setup]]*
