# Governance Vault

**AutoMecanik Governance Ledger** — vault Obsidian dedie a l'audit, incidents, ADR, regles, et connaissance operationnelle du monorepo AutoMecanik.

> **Point d'entree**: ouvre `ops/moc/MOC-Governance.md` dans Obsidian.

---

## Taxonomie Canonique

Les regles sont nommees par prefix pour eviter les collisions:

| Prefix | Domaine | Fichier |
|--------|---------|---------|
| `T1-T7` | Technical Rules (Supabase, Sessions, Zod, HMAC, etc.) | `ledger/rules/rules-technical.md` |
| `G1-G4` | Vault Governance (Canon, Zero Orphelin, Signed Commits, CI read-only) | `ledger/rules/rules-vault.md` |
| `G5-G8` | Governance Process (Proof Requirements, Obsolete Handling) | `ledger/rules/rules-governance-process.md` |
| `AI1-AI10` | AI-COS Rules (agents IA) | `ledger/rules/rules-ai-cos.md` |
| `V1-V6` | V-Level SEO | `ledger/rules/rules-seo-vlevel.md` |
| `PageRole` | SEO PageRole Taxonomy | `ledger/rules/rules-seo-pagerole.md` |

Voir `ops/moc/MOC-Rules.md` pour l'index complet.

---

## Regles Vault (G1-G4)

### G1: Canon Fait Foi

Le canon architectural reste **exclusivement** dans le monorepo (`.spec/00-canon/`). Ce vault est un **miroir enrichi operationnel**, non normatif. En cas de conflit, `.spec/00-canon/` fait foi.

### G2: Zero Orphelin

Aucun document ne peut etre orphelin. Tout document doit etre:

- lie depuis au moins 1 MOC dans `ops/moc/`, OU
- reference via un wikilink Obsidian depuis un autre document

Enforcement: `_scripts/check-orphans.sh` + CI job `g2-orphans`.

### G3: Commits Signes

Tous les commits DOIVENT etre signes cryptographiquement (SSH ed25519 prefere, GPG accepte). Voir `99-meta/signing-policy.md`.

Enforcement: CI job `g3-signed-commits`.

### G4: CI Read-Only sur Canon

Aucun workflow CI ne doit modifier les zones canoniques. Le kill-switch `AI_VAULT_WRITE=false` est respecte en production.

Voir `99-meta/ci-policy.md`.

---

## Structure

```
governance-vault/
├── .github/workflows/    # CI gouvernance (G2, G3, G4)
├── .githooks/            # Pre-commit hooks (G2 + broken links)
├── _scripts/             # Scripts enforcement (check-orphans, broken-links, sync-canon, ...)
├── _templates/           # Templates (ADR, incident, rule, deployment)
├── 99-meta/              # Gouvernance du vault (signing-policy, key-registry, ci-policy, sync-log)
├── ledger/               # Contenu canonique
│   ├── _archive/         # Documents archives (superseded)
│   ├── agents/           # 119 agents en 11 categories, chaque categorie a son INDEX
│   ├── audit-trail/      # Retrospectives, bundles rejetes, audits RPC
│   ├── compliance/       # Plans d'execution, checklists, evidence-packs
│   ├── decisions/adr/    # Architecture Decision Records (ADR-001 a ADR-014)
│   ├── incidents/        # Post-mortems
│   ├── knowledge/        # Specs, patterns, architecture technique
│   ├── policies/         # Bundle specs, prompts systeme, processus
│   └── rules/            # Regles canoniques T/G/AI/V
└── ops/moc/              # Maps of Content (MOC-Governance, MOC-Decisions, MOC-Rules, ...)
```

---

## Navigation Principale (MOCs)

Point d'entree: `ops/moc/MOC-Governance.md`. Autres MOCs:

- `MOC-Decisions` — 14 ADR canoniques
- `MOC-Rules` — taxonomie T/G/AI/V complete
- `MOC-Compliance` — plans d'execution, evidence-packs
- `MOC-Agents` — 119 agents par categorie
- `MOC-Incidents` — post-mortems
- `MOC-Knowledge` — base de connaissances
- `MOC-AuditTrail` — bundles rejetes, audits RPC, retrospectives
- `MOC-Policies` — bundle specs, templates

---

## Commandes Utiles

```bash
# Verifier G2 (aucun orphelin)
_scripts/check-orphans.sh .

# Verifier les wikilinks casses
_scripts/check-broken-links.sh .

# Verifier les signatures (G3) localement
git log --show-signature -5

# Synchroniser depuis le canon monorepo
_scripts/sync-canon.sh --dry-run
_scripts/sync-canon.sh --commit

# Activer le pre-commit hook localement (une fois)
git config core.hooksPath .githooks

# (Re)appliquer la protection serveur de main
_scripts/setup-branch-protection.sh
```

Details complets sur la protection serveur : [[branch-protection]]

---

## Setup d'une Nouvelle Machine

```bash
git clone git@github.com:ak125/governance-vault.git
cd governance-vault

# 1. Installer le pre-commit hook
git config core.hooksPath .githooks

# 2. Configurer la signature SSH (voir 99-meta/signing-policy.md)
git config --local gpg.format ssh
git config --local user.signingkey ~/.ssh/id_ed25519.pub
git config --local commit.gpgsign true

# 3. Tester
_scripts/check-orphans.sh .      # Doit afficher: PASS: 0 orphan
_scripts/check-broken-links.sh . # Doit afficher: PASS: 0 broken wikilink
```

---

## Statistiques (2026-04-17)

| Metrique | Valeur |
|----------|--------|
| ADR actifs | 14 |
| Documents .md total | 238 |
| MOCs racines | 9 |
| INDEX de sous-archives | 18 |
| Agents | 119 (11 categories) |
| Evidence-packs | 4 (fevrier 2026) |
| Orphelins (G2) | **0** |
| Wikilinks casses | **0** |

---

## Liens

- **Monorepo**: https://github.com/ak125/nestjs-remix-monorepo
- **Canon source**: `.spec/00-canon/` dans le monorepo
- **Repo ce vault**: https://github.com/ak125/governance-vault
- **Plan original**: `.spec/governance/governance-vault-plan.md` dans le monorepo

---

_Derniere mise a jour: 2026-04-17_
