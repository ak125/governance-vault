---
type: knowledge
status: canon
updated: 2026-10-01
audience: [claude-desktop-operator, onboarding]
related_adr: [ADR-012, ADR-015, ADR-101]
related_rules: [G1, G2, G3, G4]
---

# Governance Vault — Instructions Claude Desktop

> **Contexte** : ce document est un condensé pour Claude Desktop (MCP filesystem) — à distinguer de [[CLAUDE]] et [[AGENTS]] racine du vault, qui s'adressent aux agents Claude Code / Cowork / Codex. Le chemin canonique illustré (`C:\Users\...`) est un exemple poste Windows ; adapter à ton système. Les règles G1-G4, placements et workflow sont identiques partout.

Tu travailles sur le Governance Vault AutoMecanik (clone de `ak125/governance-vault`).

## Règle Absolue

Le vault décide, le monorepo `ak125/nestjs-remix-monorepo` exécute (règle G1, [[ADR-101-vault-decides-canon-authority|ADR-101]]). Les ADR `accepted` et les règles de `ledger/rules/` sont normatifs. Dans `.spec/00-canon/` du monorepo, seuls les contrats consommés par du code, un générateur ou un check CI font foi, dans leur domaine.

Chemin canonique (exemple poste Windows) : `<home>\nestjs-remix-monorepo\governance-vault\` (exposé via MCP `governance-vault`).

JAMAIS écrire dans :

- `app/.local/governance-vault/` — DEPRECATED (voir [[ADR-015-vault-single-source-of-truth]])
- `.spec/00-canon/` — fichiers du monorepo, modifiés par PR monorepo uniquement

## Règles G1-G4 à respecter

- **G1 Le Vault Décide** : aucune décision prise ou modifiée sans ADR (Architectural Decision Record) ; une divergence entre une règle et le code se signale
- **G2 Zéro-Orphelin** : tout nouveau document doit être lié depuis un MOC (`ops/moc/MOC-*.md`) ou un INDEX-*
- **G3 Commits-Signés** : proposer uniquement des commits signés ed25519 ; ne jamais contourner la signature
- **G4 Écriture par PR, CI en lecture seule** : toute modification passe par une PR signée ; un agent ne fusionne jamais ; ne jamais proposer d'écriture depuis un workflow GitHub Actions

## Structure v2 du vault (dossiers principaux)

```
ledger/            # Historique immuable
  incidents/YYYY/
  decisions/adr/
  audit-trail/
  rules/           # Taxonomie T / G / AI / V (rules-<domaine>.md)
  policies/
  agents/
  compliance/      # evidence-pack/YYYY/YYYY-MM/EP-…/, checklists/, plans/
  knowledge/
  _archive/
ops/               # Opérationnel
  moc/             # Maps of Content (points d'entrée)
  runbooks/
policies/          # Policies de contenu (ex. seo-content/)
_templates/        # Modèles réutilisables
_scripts/          # preflight-write, check-orphans, check-broken-links, check-v1-paths, new-incident
99-meta/           # Gouvernance du vault
AGENTS.md          # Guardrails agents (lire en priorité)
CLAUDE.md          # Instructions agents (ce fichier est un extrait)
```

## Placement par type de document

| Type | Destination | Template |
|------|-------------|----------|
| Incident | `ledger/incidents/YYYY/YYYY-MM-DD-<slug>.md` | `_templates/incident-template.md` |
| ADR | `ledger/decisions/adr/ADR-NNN-<slug>.md` | `_templates/adr-template.md` |
| Règle T/G/AI/V | `ledger/rules/rules-<domaine>.md` | `_templates/rule-template.md` |
| Audit report | `ledger/audit-trail/YYYY-MM-DD-<slug>.md` | — |
| Evidence-pack | `ledger/compliance/evidence-pack/YYYY/YYYY-MM/EP-YYYYMMDD-<slug>/` | manuel |
| Knowledge | `ledger/knowledge/` | libre |
| MOC | `ops/moc/MOC-<scope>.md` | — |

## Workflow nouveau-document

1. `git pull --rebase origin main` (le cron `vault-sync.sh` ne met à jour que le checkout de la machine DEV, pas ce clone)
2. Preflight obligatoire : `_scripts/preflight-write.sh` — exit 0 = GO ; tout autre code = corriger avant d'écrire (voir [[AGENTS]])
3. Créer une branche : `git checkout -b <type>/<slug>` (ex : `docs/inc-2026-003-xxx`, `adr/ADR-NNN-yyy`)
4. Utiliser un helper si disponible : `_scripts/new-incident.sh <severity> <slug>`
5. Rédiger avec frontmatter YAML conforme au template
6. Lier depuis un MOC (`ops/moc/MOC-*.md`) — G2
7. Valider : `_scripts/check-orphans.sh .` et `_scripts/check-broken-links.sh .`
8. Proposer le commit signé : `git commit -S -m "docs(<type>): ..."`
9. Push + PR via `gh pr create --base main`
10. Attendre que tous les checks requis soient verts (liste dans [[branch-protection]]), puis merge squash : `gh pr merge <N> --squash --match-head-commit <sha>` ; la protection n'exige aucune review

## Anti-patterns (interdits)

Bloqués mécaniquement : orphelins, wikilinks cassés, commits non signés, chemins v1 (checks requis) et push direct ou forcé sur `main` (protection de branche). L'écriture CI est empêchée par les permissions `contents: read` des workflows, pas par le check G4 (simple marqueur). Le reste repose sur les hooks locaux ou la revue.

- Écrire dans `.local/governance-vault/` (pre-commit hook bloque)
- Créer un document sans frontmatter YAML
- Créer un document orphelin (pas lié depuis MOC/INDEX)
- Proposer un commit non signé
- Force-push sur `main`
- Modifier `status: canon` sans ADR
- Renuméroter un ADR `status: accepted` (immutable)
- Écrire depuis CI (G4 : la CI n'écrit rien, vérifié par `_scripts/check-ci-read-only.py`)
- Fusionner une PR (G4 : la fusion revient à un humain)

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
| Les contrats du monorepo (hors vault) | `.spec/00-canon/` du monorepo (rang : ADR-101 D2) |

## 3-VPS Architecture (voir [[ADR-012-aicos-vps-architecture]])

| VPS | Rôle | Write vault ? |
|---|---|---|
| DEV | Dev, CI, vault runtime canonique | Oui (via PR signée) |
| PROD | Production | Non (miroir en lecture seule) |
| AI-COS | Agents IA | Non (git clone read-only) |

## Limites Claude Desktop dans ce contexte

- Tu peux lire/chercher/suivre wikilinks dans tout le vault via MCP filesystem
- Tu peux **proposer** des modifications, mais pas **signer** les commits (G3)
- Le workflow reste : Claude Desktop rédige → l'utilisateur review dans Obsidian → l'utilisateur commit signé en terminal
- Pour toute tâche nécessitant `gh` / `git push` : donner à l'utilisateur la commande exacte à copier

## Contact

- Owner : Fafa (automecanik.seo@gmail.com)
- Repo : https://github.com/ak125/governance-vault
- Monorepo (exécute) : https://github.com/ak125/nestjs-remix-monorepo

---

*Ces instructions sont un condensé de `CLAUDE.md` + `AGENTS.md` à la racine du vault. En cas de doute, te référer à ces deux fichiers (accessibles via MCP).*
