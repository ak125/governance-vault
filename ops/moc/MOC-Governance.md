---
type: moc
status: canon
role: master-index
updated: 2026-05-07
---

# MOC: Governance

**Master Index** du vault de gouvernance AutoMecanik. Point d'entree unique de navigation.

> Ce MOC ne contient pas de statistiques numeriques. Chaque metrique vit dans sa source canonique unique (voir la section "Single Source of Truth" ci-dessous). Cette discipline garantit qu'aucun chiffre ne peut deriver entre l'index et la realite.

---

## Navigation Principale

| MOC | Role |
|-----|------|
| [[MOC-Decisions]] | Index des ADR (statuts a jour, source canonique = frontmatter de chaque ADR) |
| [[MOC-Rules]] | Taxonomie T / G / AI / V / R-SEO / R-SEO-KW / AP / D / Q / AEC — regles canoniques |
| [[MOC-Compliance]] | Plans d'execution, checklists, evidence-packs |
| [[MOC-Agents]] | Catalogue agents par categorie (registry SoT : [[REG-001-agents]]) |
| [[MOC-Incidents]] | Post-mortems et incidents |
| [[MOC-Knowledge]] | Base de connaissances (specs, guides) |
| [[MOC-AuditTrail]] | Audit-trail, bundles rejetes, audits RPC |
| [[MOC-Policies]] | Bundle specs, prompts systeme, processus |

---

## Regles Vault (G1-G4)

Les 4 regles de gouvernance du vault lui-meme. Voir [[rules-vault]].

| Regle | Description | Enforcement |
|-------|-------------|-------------|
| G1 | Canon fait foi | Sync one-way depuis `.spec/00-canon/` |
| G2 | Zero orphelin | `_scripts/check-orphans.sh` |
| G3 | Commits signes | SSH signing (ed25519) via git config |
| G4 | CI read-only sur canon | `AI_VAULT_WRITE=false` en prod |

---

## Taxonomie Canonique

Voir [[MOC-Rules]] pour la taxonomie complete (T / G / AI / V / R-SEO / R-SEO-KW / AP / D / Q / AEC). Aucune duplication ici — la taxonomie a une source unique.

---

## Single Source of Truth

> Le `governance-vault` est la **source de verite unique des documents de gouvernance operationnelle** (ADR, rules, MOCs, audit-trail, evidence-packs, runbooks, registry agents — formalise par [[ADR-015-vault-single-source-of-truth]]). Le **canon architectural** (contrats de schemas, code patterns figes) reste dans `.spec/00-canon/` du monorepo. Les deux sont distincts et ne se recouvrent pas.

Pour les definitions operationnelles des differents sens du mot `canon` (canon architectural / document canonique / canonical path / registry / source), un glossaire sera ajoute dans la section dediee de ce MOC en PR-2.

---

## Meta

- [[README]] - Documentation generale du vault
- [[signing-policy]] - Politique de signature (SSH ed25519)
- [[key-registry]] - Registre des cles SSH
- [[sync-log]] - Log de synchronisation canon
- [[ci-policy]] - Politique CI/CD (read-only sur canon)
- [[cron-setup]] - Configuration des tasks cron
- [[deploy-bot]] - Role du bot CI/CD (non-SPOF)
- [[claude-desktop-instructions]] - Onboarding Claude Desktop (MCP filesystem, condense CLAUDE.md + AGENTS.md)
- [[obsidian-setup]] - Topologie canonique coffre Obsidian (1 clone = 1 vault, plugins Dataview/Templater/Git, SSH signing G3)

## Archive

- [[INDEX-archive]] - Documents archives (superseded, OpenClaw, etc.)

---

## Cycle de Vie

```
Probleme/Incident -> [[MOC-Incidents]]
        |
        v
Decision prise  -> [[MOC-Decisions]] (nouveau ADR)
        |
        v
Plan execute    -> [[MOC-Compliance]] (plan + checklist)
        |
        v
Preuves         -> [[MOC-Compliance]] (evidence-pack)
        |
        v
Audit-trail     -> [[MOC-AuditTrail]] (retrospective, rejects)
```
