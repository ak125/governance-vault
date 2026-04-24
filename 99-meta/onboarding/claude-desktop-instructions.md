---
type: knowledge
status: canon
updated: 2026-04-24
audience: [claude-desktop-operator, onboarding]
related_adr: [ADR-012, ADR-015]
related_rules: [G1, G2, G3, G4]
---

# Governance Vault — Instructions Claude Desktop

> **Contexte** : ce document est un condensé pour Claude Desktop (MCP filesystem) — à distinguer de [[CLAUDE]] et [[AGENTS]] racine du vault, qui s'adressent aux agents Claude Code / Cowork / Codex. Le chemin canonique illustré (`C:\Users\...`) est un exemple poste Windows ; adapter à ton système. Les règles G1-G4, placements et workflow sont identiques partout.

Tu travailles sur le Governance Vault AutoMecanik (clone de `ak125/governance-vault`).

## Règle Absolue

Ce vault n'est PAS le canon architectural. Le canon vit dans `.spec/00-canon/` du monorepo `ak125/nestjs-remix-monorepo`. Ce vault est un miroir enrichi opérationnel (règle G1).

Chemin canonique (exemple poste Windows) : `C:\Users\Marwane\nestjs-remix-monorepo\governance-vault\` (exposé via MCP `governance-vault`).

JAMAIS écrire dans :

- `app/.local/governance-vault/` — DEPRECATED (voir [[ADR-015-vault-single-source-of-truth]])
- `.spec/00-canon/` — canon, modifier via monorepo uniquement

## Règles G1-G4 à respecter

- **G1 Canon-Fait-Foi** : ne jamais modifier un document `status: canon` sans ADR (Architectural Decision Record)
- **G2 Zéro-Orphelin** : tout nouveau document doit être lié depuis un MOC (`ops/moc/MOC-*.md`) ou un INDEX-*
- **G3 Commits-Signés** : proposer uniquement des commits signés ed25519 ; ne jamais contourner la signature
- **G4 CI-Read-Only** : ne jamais proposer d'écriture depuis un workflow GitHub Actions

## Structure v2 du vault

```
ledger/            # Historique immuable
  incidents/YYYY/
  decisions/adr/
  audits/
  audit-trail/
  policies/
  agents/
  compliance/
  knowledge/
  deployments/
  _archive/
ops/               # Opérationnel
  moc/             # Maps of Content (points d'entrée)
  rules/           # Taxonomie T / G / AI / V
  policies/
_templates/        # Modèles réutilisables
_scripts/          # check-orphans, check-broken-links, new-incident, evidence-pack
99-meta/           # Gouvernance du vault
AGENTS.md          # Guardrails agents (lire en priorité)
CLAUDE.md          # Instructions agents (ce fichier est un extrait)
```

## Placement par type de document

| Type | Destination | Template |
|------|-------------|----------|
| Incident | `ledger/incidents/YYYY/YYYY-MM-DD-<slug>.md` | `_templates/incident-template.md` |
| ADR | `ledger/decisions/adr/ADR-NNN-<slug>.md` | `_templates/adr-template.md` |
| Règle T/G/AI/V | `ops/rules/rules-<taxonomie>.md` | `_templates/rule-template.md` |
| Audit report | `ledger/audit-trail/YYYY-MM-DD-<slug>.md` | — |
| Evidence-pack | `ledger/audits/evidence-packs/EP-YYYYMMDD-<slug>/` | `_scripts/evidence-pack.sh` |
| Knowledge | `ledger/knowledge/` | libre |
| MOC | `ops/moc/MOC-<scope>.md` | — |

## Workflow nouveau-document

1. `git pull --rebase origin main` (le cron DEV VPS absorbe les pushes, mais vérifier quand même)
2. Vérifier que la branche de travail est bien basée sur `origin/main` à jour : `git merge-base --is-ancestor origin/main HEAD`
3. Créer une branche : `git checkout -b <type>/<slug>` (ex : `docs/inc-2026-003-xxx`, `adr/ADR-NNN-yyy`)
4. Utiliser un helper si disponible : `_scripts/new-incident.sh <severity> <slug>` ou `_scripts/evidence-pack.sh`
5. Rédiger avec frontmatter YAML conforme au template
6. Lier depuis un MOC (`ops/moc/MOC-*.md`) — G2
7. Valider : `_scripts/check-orphans.sh .` et `_scripts/check-broken-links.sh .`
8. Proposer le commit signé : `git commit -S -m "docs(<type>): ..."`
9. Push + PR via `gh pr create --base main`
10. Attendre CI G1-G4 verte, review, merge rebase

## Anti-patterns (BLOQUÉS)

- Écrire dans `.local/governance-vault/` (pre-commit hook bloque)
- Créer un document sans frontmatter YAML
- Créer un document orphelin (pas lié depuis MOC/INDEX)
- Proposer un commit non signé
- Force-push sur `main`
- Modifier `status: canon` sans ADR
- Renuméroter un ADR `status: accepted` (immutable)
- Écrire depuis CI (`AI_VAULT_WRITE=false` doit rester respecté)

## Conventions nommage

- Wikilinks courts stem-only : `[[ADR-015-vault-single-source-of-truth]]`, `[[rules-vault|G1]]`
- Dans les tableaux markdown : éviter `[[path|alias]]` (le `|` casse le parsing), préférer liste ou stem unique
- Frontmatter YAML : `type`, `status`, `updated: YYYY-MM-DD` minimum (champs additionnels selon template)

## Référence croisée — où trouver quoi

| Je cherche... | Je regarde... |
|---|---|
| Un incident | `ops/moc/MOC-Incidents.md` |
| Une décision | `ops/moc/MOC-Decisions.md` |
| Une règle | `ops/moc/MOC-Rules.md` |
| Un agent | `ops/moc/MOC-Agents.md` |
| Une policy | `ops/moc/MOC-Policies.md` |
| Un audit | `ops/moc/MOC-AuditTrail.md` |
| Un evidence-pack | `ops/moc/MOC-Compliance.md` |
| Savoirs opérationnels | `ops/moc/MOC-Knowledge.md` |
| Le canon (hors vault) | `.spec/00-canon/` du monorepo |

## 3-VPS Architecture (voir [[ADR-012-aicos-vps-architecture]])

| VPS | Rôle | Write vault ? |
|---|---|---|
| DEV (46.224.118.55) | Dev, CI, vault runtime canonique | Oui (via PR signée) |
| PROD (49.12.233.2) | Production | Non (read-only mirror) |
| AI-COS (178.104.1.118) | Agents IA, Airlock | Non (git clone read-only) |

## Limites Claude Desktop dans ce contexte

- Tu peux lire/chercher/suivre wikilinks dans tout le vault via MCP filesystem
- Tu peux **proposer** des modifications, mais pas **signer** les commits (G3)
- Le workflow reste : Claude Desktop rédige → l'utilisateur review dans Obsidian → l'utilisateur commit signé en terminal
- Pour toute tâche nécessitant `gh` / `git push` : donner à l'utilisateur la commande exacte à copier

## Contact

- Owner : Fafa (automecanik.seo@gmail.com)
- Repo : https://github.com/ak125/governance-vault
- Canon : https://github.com/ak125/nestjs-remix-monorepo (`.spec/00-canon/`)

---

*Ces instructions sont un condensé de `CLAUDE.md` + `AGENTS.md` à la racine du vault. En cas de doute, te référer à ces deux fichiers (accessibles via MCP).*
