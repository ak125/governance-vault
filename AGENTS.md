# AGENTS.md — Governance Vault Single Source of Truth

> Instructions obligatoires pour tout agent (Claude Code, AI-COS, scripts, humains utilisant un agent)
> qui produit un document de gouvernance depuis le **DEV VPS** (`46.224.118.55`).

---

## Règle absolue

**Tous les documents de gouvernance vivent dans ce repo uniquement.**

Canonical path : `/opt/automecanik/governance-vault/` (cloné depuis `git@github.com:ak125/governance-vault.git`)

**Jamais** dans :
- `/opt/automecanik/app/.local/governance-vault/` — DEPRECATED depuis 2026-04-18 (voir [ADR-013](02-decisions/adr/ADR-013-vault-single-source-of-truth.md))
- `/opt/automecanik/app/.local/*` — gitignoré, ton travail sera perdu
- `/opt/automecanik/app/.spec/` — canon architectural uniquement (R-Vault-01)

Voir aussi [ADR-013](02-decisions/adr/ADR-013-vault-single-source-of-truth.md) pour la décision formelle.

---

## Placement par type de document

| Type | Destination | Template |
|------|-------------|----------|
| Incident / post-mortem | `01-incidents/YYYY/YYYY-MM-DD-<slug>.md` | `01-incidents/_templates/incident-template.md` |
| ADR (décision architecturale) | `02-decisions/adr/ADR-NNN-<slug>.md` | voir ADR-012 comme modèle |
| DEC (décision opérationnelle) | `02-decisions/DEC-NNN-<slug>.md` | voir DEC-003 comme modèle |
| Règle R-* | `03-rules/` ou `03-policies/` | — |
| Audit | `04-audit-trail/` | — |
| Agent registry / specs | `05-agents/` | — |
| Compliance | `05-compliance/` ou `06-compliance/` | — |
| Savoir opérationnel | `06-knowledge/` | libre markdown |

---

## Workflow nouveau-document

1. **Toujours** : `cd /opt/automecanik/governance-vault/`
2. Vérifier qu'on est à jour : `git pull --rebase origin main`
3. Créer une branche : `git checkout -b <type>/<slug>`
   - Exemples : `docs/inc-2026-003-xyz`, `adr/ADR-014-yyy`, `chore/archive-zzz`
4. **Utiliser les helpers** si dispo :
   - `scripts/new-incident.sh <severity> <slug>` → scaffold incident
5. Écrire le fichier avec **frontmatter YAML conforme** au template
6. **Lier depuis une MOC** (`00-index/MOC-*.md`) — règle R-Vault-02 "Zéro orphelin"
7. Valider : `scripts/check-orphans.sh`
8. Commit **signé** : `git commit -S -m "docs(<type>): ..."`
9. Push + PR : `gh pr create --base main`

---

## Anti-patterns (BLOQUÉS)

- Écrire dans `/opt/automecanik/app/.local/governance-vault/*`
- Créer un document sans frontmatter
- Créer un document sans lien depuis une MOC
- Commit non-signé
- `git push --force` sur `main` du vault
- Renuméroter un ADR existant (immutable une fois `status: accepted`)

---

## Référence croisée — où trouver quoi

| Je cherche... | Je regarde... |
|---------------|---------------|
| Un incident | `00-index/MOC-Incidents.md` |
| Une décision | `00-index/MOC-Decisions.md` |
| Une règle IA | `00-index/MOC-Rules.md` |
| Un agent | `00-index/MOC-Agents.md` |
| Le canon architectural | `/opt/automecanik/app/.spec/00-canon/` (R-Vault-01 : canon fait foi) |

---

## Contact

- **Owner** : `@automecanik.seo@gmail.com`
- **Repo GitHub** : https://github.com/ak125/governance-vault
- **Documentation** : voir `README.md`
