# AGENTS.md — Governance Vault Single Source of Truth

> Instructions obligatoires pour tout agent (Claude Code, Cowork, AI-COS, Codex, scripts, humains utilisant un agent) qui produit un document de gouvernance.

---

## Règle absolue

**Tous les documents de gouvernance vivent dans ce repo uniquement.**

Canonical path (runtime sur DEV VPS) : `/opt/automecanik/governance-vault/` (cloné depuis `git@github.com:ak125/governance-vault.git`)

**Jamais** dans :

- `/opt/automecanik/app/.local/governance-vault/` — DEPRECATED depuis 2026-04-18 (voir [[ADR-015-vault-single-source-of-truth|ADR-015]])
- `/opt/automecanik/app/.local/*` — gitignoré, ton travail sera perdu
- `/opt/automecanik/app/.spec/` — canon architectural uniquement (règle [[rules-vault|G1]])

Voir aussi [[ADR-015-vault-single-source-of-truth|ADR-015]] pour la décision formelle et [[ADR-012-aicos-vps-architecture|ADR-012]] pour l'architecture 3-VPS.

---

## Placement par type de document (structure v2)

| Type | Destination | Template |
|------|-------------|----------|
| Incident / post-mortem | `ledger/incidents/YYYY/YYYY-MM-DD-<slug>.md` | `_templates/incident-template.md` |
| ADR (décision architecturale) | `ledger/decisions/adr/ADR-NNN-<slug>.md` | `_templates/adr-template.md` |
| Règle T/G/AI/V | `ops/rules/rules-<taxonomie>.md` | `_templates/rule-template.md` |
| Policy | `ledger/policies/` ou `ops/policies/` | — |
| Audit report | `ledger/audit-trail/YYYY-MM-DD-<slug>.md` | — |
| Evidence-pack | `ledger/audits/evidence-packs/EP-YYYYMMDD-<slug>/` | `_scripts/evidence-pack.sh` |
| Agent registry / specs | `ledger/agents/` | — |
| Compliance | `ledger/compliance/` | — |
| Savoir opérationnel | `ledger/knowledge/` | libre markdown |
| MOC (Map of Content) | `ops/moc/MOC-<scope>.md` | voir MOCs existantes |
| Déploiement | `ledger/deployments/` | `_templates/deployment-template.md` |

---

## Workflow nouveau-document

1. **Toujours** : `cd /opt/automecanik/governance-vault/` (ou ton clone Windows/PC)
2. **Preflight OBLIGATOIRE** — refuse si clone périmé ou v1 paths détectés :
   ```bash
   _scripts/preflight-write.sh
   ```
   Exit 0 = GO. Exit 10-13 = fix requis (voir message). Ne jamais écrire sans GO.
3. Créer une branche : `git checkout -b <type>/<slug>`
   - Exemples : `docs/inc-2026-003-xyz`, `adr/ADR-NNN-yyy`, `chore/archive-zzz`
4. **Utiliser les helpers** si dispo :
   - `_scripts/new-incident.sh <severity> <slug>` → scaffold incident
   - `_scripts/evidence-pack.sh` → scaffold evidence-pack
5. Écrire le fichier avec **frontmatter YAML conforme** au template de son type
6. **Lier depuis une MOC** (`ops/moc/MOC-*.md`) ou un INDEX — règle [[rules-vault|G2]] "Zéro orphelin"
7. Valider localement :
   ```bash
   _scripts/check-orphans.sh .
   _scripts/check-broken-links.sh .
   ```
8. Commit **signé** (règle [[rules-vault|G3]]) :
   ```bash
   git commit -S -m "docs(<type>): ..."
   ```
9. Push + PR :
   ```bash
   git push -u origin <branch>
   gh pr create --base main
   ```
10. Attendre CI G1-G4 vert, review, merge rebase (linear history)

---

## Preflight automatique (ADR-015 §Guardrails)

**Pourquoi** : le cron `vault-sync.sh` sync `main` toutes les 5 min, mais ça ne couvre pas la fenêtre entre 2 ticks. Si un agent démarre dans cette fenêtre avec un clone périmé, il risque de recréer le bug PR #7 (2026-04-18 : clone 16 commits en retard → PR sur structure v1 vs main v2).

**Que vérifie `_scripts/preflight-write.sh`** :
1. Canonical path (pas dans `.local/governance-vault/`)
2. `git fetch origin` réussit (réseau OK)
3. Working tree propre (pas de changements en cours perdus)
4. Si sur `main` : local = `origin/main` (pas behind / pas diverged)
5. Si sur branche : informatif si `origin/main` a avancé
6. Aucun fichier sous path v1 (réutilise `check-v1-paths.sh`)

**Codes de sortie** : 0 = GO, 10 = clone périmé, 11 = tree sale, 12 = dans .local/, 13 = v1 paths, 20 = repo KO, 21 = fetch KO.

---

## Anti-patterns (BLOQUÉS par G1-G4)

- Écrire dans `/opt/automecanik/app/.local/governance-vault/*` (PR #81 ajoute hook pre-commit)
- Créer un document sans frontmatter YAML
- Créer un document sans lien depuis une MOC ou INDEX (violation [[rules-vault|G2]])
- Commit non-signé sur branche mergeable (violation [[rules-vault|G3]])
- `git push --force` sur `main` du vault (branch protection active)
- Modifier un document `status: canon` sans ADR nouvelle ou superseding (violation [[rules-vault|G1]])
- Renuméroter un ADR existant `status: accepted` (immutable)
- Écrire depuis un workflow GitHub Actions (violation [[rules-vault|G4]] : CI Read-Only, `AI_VAULT_WRITE=false`)

---

## Référence croisée — où trouver quoi

| Je cherche... | Je regarde... |
|---------------|---------------|
| Un incident | [[MOC-Incidents]] |
| Une décision architecturale | [[MOC-Decisions]] |
| Une règle T/G/AI/V | [[MOC-Rules]] |
| Un agent | [[MOC-Agents]] |
| Une policy | [[MOC-Policies]] |
| Un audit / retro | [[MOC-AuditTrail]] |
| Un evidence-pack compliance | [[MOC-Compliance]] |
| Savoirs opérationnels | [[MOC-Knowledge]] |
| Le canon architectural | `/opt/automecanik/app/.spec/00-canon/` ([[rules-vault|G1]] : canon fait foi) |

---

## 3-VPS Architecture (rappel [[ADR-012-aicos-vps-architecture|ADR-012]])

| VPS | Rôle | Write access vault ? |
|-----|------|---------------------|
| **DEV** (46.224.118.55) | Dev, CI artefacts, vault runtime canonique | Oui (via PR signée) |
| **PROD** (49.12.233.2) | Production | Non (read-only mirror via sync-canon) |
| **AI-COS** (178.104.1.118) | Agents IA, Airlock | Non (git clone read-only via HTTPS) |

Aucune VPS ne doit écrire de gouvernance hors du workflow GitHub PR.

---

## Contact

- **Owner** : Fafa — `automecanik.seo@gmail.com`
- **Repo GitHub** : https://github.com/ak125/governance-vault
- **Documentation** : voir `README.md` à la racine du vault
- **CLAUDE.md** : `/CLAUDE.md` à la racine du vault (instructions détaillées)

---

_Dernière mise à jour : 2026-04-18 — ADR-015 accepted_
