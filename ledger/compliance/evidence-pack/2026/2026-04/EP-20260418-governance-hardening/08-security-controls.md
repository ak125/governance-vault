---
type: security-controls
---

# Security Controls

## Controles en couches (defense in depth)

Le vault applique une **defense a 3 couches** redondantes par conception. Chaque couche est capable de detecter les violations, les couches ulterieures attrapent ce qui passerait a travers.

### Couche 1 — Local (machine dev)

| Controle | Fichier | Action |
|----------|---------|--------|
| Pre-commit hook G2 | `.githooks/pre-commit` | Refuse le commit si orphelin detecte |
| Pre-commit hook broken-links | `.githooks/pre-commit` | Refuse le commit si wikilink casse |
| Signature auto | `git config commit.gpgsign true` | Git signe automatiquement tout commit |
| Cle SSH dediee | `~/.ssh/id_ed25519` | Ed25519, verifiable via allowed_signers |

Activation requise par machine: `git config core.hooksPath .githooks`

### Couche 2 — CI (GitHub Actions)

| Job | Workflow | Verification |
|-----|----------|--------------|
| `g2-orphans` | vault-governance.yml | `check-orphans.sh` exit 1 si orphelin |
| `broken-links` | vault-governance.yml | `check-broken-links.sh` exit 1 si casse |
| `g3-signed-commits` | vault-governance.yml | `%G?` verifie avec allowed_signers |
| `g4-canon-write-block` | vault-governance.yml | Verif structurelle du workflow |

Tous les jobs tournent sur **chaque push et chaque PR**. Durees moyennes 4-6 secondes par job.

### Couche 3 — Branch Protection (cote GitHub)

Voir [[branch-protection]] pour la policy complete.

| Controle | Valeur |
|----------|--------|
| `enforce_admins` | true — personne ne contourne |
| `required_linear_history` | true — rebase obligatoire |
| `required_status_checks` | 4 display names exacts |
| `allow_force_pushes` | false |
| `allow_deletions` | false |
| `required_conversation_resolution` | true |

## Gestion des cles

Voir [[key-registry]] pour la liste complete.

| Cle | Role | Statut |
|-----|------|--------|
| K001 | deploy VPS | Active |
| K002 | Fafa Windows | Active (ajoutee 2026-04-17) |

Rotation: procedure dans [[signing-policy]] section "Rotation de Cle".

## Verifications periodiques

| Verification | Frequence | Script/Commande | Artefact |
|--------------|-----------|------------------|----------|
| Audit signatures retro | Mensuel | `_scripts/audit-signatures.sh --report` | `99-meta/reports/YYYY-MM-signature-audit.md` |
| Integrite branch protection | Ad-hoc + a chaque setup | `gh api .../protection \| jq` | Output comparaison avec [[branch-protection]] |
| Orphelins | Chaque commit + chaque PR | `check-orphans.sh` | CI job g2-orphans |
| Wikilinks casses | Chaque commit + chaque PR | `check-broken-links.sh` | CI job broken-links |

## Exclusions de perimetre

Ce pack **NE couvre PAS** :

- Les secrets applicatifs (aucun secret dans ce vault — vault documentaire)
- Les controles Airlock runtime (couverts par les EP-20260205-* et EP-mensuels futurs)
- Les controles infra hebergement GitHub (delegues a GitHub)
- Les sauvegardes (GitHub preserve l'historique; ce vault est auto-replique via git clone)

## Voir aussi

- [[rules-vault]] — G1-G4 canoniques
- [[signing-policy]] — G3 SSH signing
- [[branch-protection]] — Protection serveur main
- [[key-registry]] — Registre des cles autorisees
- [[ci-policy]] — G4 CI read-only
