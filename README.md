# Governance Vault

**AutoMecanik Governance Ledger** — vault Obsidian dedie a l'audit, incidents, ADR, regles, et connaissance operationnelle du monorepo AutoMecanik.

> **Point d'entree**: ouvre `ops/moc/MOC-Governance.md` dans Obsidian.

---

## Taxonomie Canonique

Les regles sont nommees par prefixe pour eviter les collisions (T, G, AI, V, R-SEO, R-SEO-KW, AP, D, Q, DoD, AEC).
Au 2026-09-30, `ledger/rules/` compte 13 fichiers de regles. L'index complet (prefixe, fichier, domaine) est `ops/moc/MOC-Rules.md` : il n'est pas recopie ici.

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

Voir `99-meta/ci-policy.md`. Le check requis `G4: CI read-only sur canon` n'execute que des `echo` : la lecture seule vient des `permissions: contents: read` declarees par chaque workflow (voir [[branch-protection]]).

---

## Structure

```
governance-vault/
├── .github/workflows/    # 6 workflows ; checks requis sur main : voir branch-protection
├── .githooks/            # pre-commit (G2 + liens casses), pre-push (+ signatures G3)
├── .spec/00-canon/planning/  # Enums du planning (ADR-053)
├── _scripts/             # Scripts (check-orphans, check-broken-links, preflight-write, sync_moc_decisions.py, ...)
├── _templates/           # Templates (ADR, incident, rule, deployment, verification, ...)
├── 99-meta/              # Gouvernance du vault (signing-policy, key-registry, ci-policy, branch-protection, ...)
├── dist/policies/        # Politiques OPA compilees (wasm + bundles)
├── policies/             # Sources OPA par domaine (seo-content/)
├── runbooks/             # Runbooks hors ops/ (soft-404-telemetry)
├── ledger/               # Contenu canonique
│   ├── _archive/         # Documents archives (superseded)
│   ├── agents/           # 119 agents en 11 categories, chaque categorie a son INDEX
│   ├── audit-trail/      # Retrospectives, bundles rejetes, audits RPC
│   ├── canon-coverage/   # Couverture des canons (REG-002)
│   ├── compliance/       # Plans d'execution, checklists, evidence-pack/
│   ├── decisions/adr/    # Architecture Decision Records (statuts : MOC-Decisions)
│   ├── incidents/        # Post-mortems
│   ├── knowledge/        # Specs, patterns, architecture technique
│   ├── policies/         # Bundle specs, prompts systeme, processus
│   ├── rules/            # Regles canoniques (13 fichiers)
│   ├── snapshots/        # Snapshots du planning (ADR-053)
│   └── verdicts/         # Verdicts empiriques
└── ops/
    ├── GOVERNANCE-HUMAN.md
    ├── moc/              # Maps of Content (MOC-Governance, MOC-Decisions, MOC-Rules, ...)
    └── runbooks/         # Runbooks d'exploitation
```

---

## Navigation Principale (MOCs)

Point d'entree: `ops/moc/MOC-Governance.md`. Autres MOCs:

- `MOC-Decisions` — index des ADR et de leurs statuts (projection auto-generee)
- `MOC-Rules` — taxonomie T/G/AI/V complete
- `MOC-Compliance` — plans d'execution, evidence-packs
- `MOC-Agents` — 119 agents par categorie
- `MOC-Incidents` — post-mortems
- `MOC-Knowledge` — base de connaissances
- `MOC-AuditTrail` — bundles rejetes, audits RPC, retrospectives
- `MOC-Policies` — bundle specs, templates
- `MOC-Planning-Live` — planning (ADR-053)
- `MOC-Repository-Control-Plane` — Repository Control Plane
- `MOC-Roadmap-2026` — roadmap 2026

---

## Commandes Utiles

```bash
# Verifier G2 (aucun orphelin)
_scripts/check-orphans.sh .

# Verifier les wikilinks casses
_scripts/check-broken-links.sh .

# Verifier les signatures (G3) localement
git log --show-signature -5

# _scripts/sync-canon.sh : obsolete, ecrit des chemins v1 rejetes par le check requis
# « No V1 Paths (ADR-015) » ; ne pas l'utiliser (voir 99-meta/cron-setup.md)

# Activer les hooks locaux pre-commit et pre-push (une fois)
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

# 1. Installer les hooks locaux (pre-commit, pre-push)
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

## Statistiques (instantane du 2026-09-30)

Chiffres releves a la main a cette date, non mis a jour automatiquement. Pour les ADR et leurs statuts, la reference est `ops/moc/MOC-Decisions.md`.

| Metrique | Valeur |
|----------|--------|
| Fichiers ADR | 90 (numeros jusqu'a ADR-099) |
| Fichiers de regles | 13 |
| Documents .md suivis | 540 |
| MOCs racines | 12 |
| INDEX de sous-archives | 20 |
| Agents | 119 (11 categories) |
| Evidence-packs | 6 (fevrier, avril et mai 2026) |
| Incidents | 18 |
| Orphelins (G2) | **0** |
| Wikilinks casses | **0** |

---

## Liens

- **Monorepo**: https://github.com/ak125/nestjs-remix-monorepo
- **Canon source**: `.spec/00-canon/` dans le monorepo
- **Repo ce vault**: https://github.com/ak125/governance-vault
- **Plan original**: `.spec/governance/governance-vault-plan.md`, absent de `main` du monorepo (verifie le 2026-09-30)

---

_Derniere mise a jour: 2026-09-30_
