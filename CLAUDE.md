# CLAUDE.md — Instructions pour les agents IA travaillant sur ce vault

Ce fichier guide les agents Claude (Code, Desktop, Cowork, Agent SDK) quand ils editent le governance vault.

---

## Regle Maitresse

> **Ce vault n'est PAS le canon.** Le canon architectural reside dans `.spec/00-canon/` du monorepo. Ce vault est un **miroir enrichi operationnel** (G1).

Avant toute modification:

1. Identifier si le changement est operationnel (autorise ici) ou canonique (interdit ici — modifier le monorepo)
2. Lire les MOCs concernees (`ops/moc/MOC-*.md`) pour comprendre le contexte
3. Respecter la taxonomie T/G/AI/V (voir README)

---

## Regles Vault (a respecter imperativement)

### G1: Canon Fait Foi

NE JAMAIS modifier un document qui declare `status: canon` sans:

- Ouvrir une ADR si c'est une vraie decision (voir `_templates/adr-template.md`)
- Ou pointer vers le canon monorepo si c'est une regle technique

### G2: Zero Orphelin

Chaque nouveau document CREE DOIT etre lie:

- Soit depuis un MOC existant (`ops/moc/MOC-*.md`)
- Soit depuis un INDEX-* local (`ledger/agents/*/INDEX-agents-*.md`, `ledger/compliance/.../INDEX-EP-*.md`, ...)

Avant de committer, executer:

```bash
_scripts/check-orphans.sh .
```

Si FAIL, lier ou archiver dans `ledger/_archive/` (G8).

### G3: Commits Signes

Ne jamais proposer un commit non signe a l'utilisateur. Si la config signing manque, guider l'utilisateur vers `99-meta/signing-policy.md`.

### G4: CI Read-Only

NE JAMAIS modifier depuis un workflow GitHub Actions. Le kill-switch `AI_VAULT_WRITE=false` doit rester respecte. Toute tentative de write depuis CI est une violation critique.

---

## Conventions de Nommage

### Wikilinks

- Prefere les wikilinks courts: `[[ADR-001-environment-separation]]`, `[[rules-technical]]`
- Pour les fichiers a nom identique (ex: `01-context.md` dans 4 evidence-packs): utilise un **stem unique** (`INDEX-EP-xxx.md`) plutot qu'un wikilink path-based
- Dans les **tableaux markdown**, evite `[[path|alias]]` — le `|` doit etre escape en `\|` ce qui casse le parsing Obsidian. Utilise une liste a la place, ou renomme le fichier cible pour avoir un stem unique

### Frontmatter YAML

Tout document canonique doit avoir:

```yaml
---
type: adr | rule | plan | checklist | retrospective | audit-report | evidence-pack | moc | index | policy | spec | knowledge | template
status: canon | draft | superseded | deprecated
updated: YYYY-MM-DD
---
```

Pour les ADR specifiquement:

```yaml
---
id: ADR-XXX
title: "..."
status: Proposed | Accepted | Superseded
date: YYYY-MM-DD
decision_makers: [...]
supersedes: []
superseded_by: []
related_rules: [...]
---
```

### Nouvelles ADR

Utiliser `_templates/adr-template.md`. Numero = dernier ADR + 1 (voir `MOC-Decisions`).

### Nouveaux Incidents

Utiliser `_templates/incident-template.md`. Lier depuis `MOC-Incidents`.

### Nouvelles Regles

Utiliser `_templates/rule-template.md`. L'ajouter au fichier de regles approprie (T/G/AI/V) et l'indexer dans `MOC-Rules`.

---

## Workflow Typique

Quand l'utilisateur demande une modification:

1. **Lire les MOCs pertinents** pour comprendre le contexte (pas juste le fichier cible)
2. **Verifier** si le changement touche du canon (auquel cas refuser et rediriger vers le monorepo)
3. **Appliquer** le changement + lier depuis un MOC/INDEX si creation
4. **Executer** `_scripts/check-orphans.sh .` et `_scripts/check-broken-links.sh .`
5. **Proposer** un commit message clair + rappeler qu'il doit etre signe (G3)

---

## Ce qu'il ne faut PAS faire

- Creer un fichier sans le lier (G2 violation)
- Modifier une regle `status: canon` sans ADR
- Utiliser le format legacy `DEC-00X` (reclasse en Phase 4 vers ADR-014 + plan/audit-trail)
- Utiliser les anciens chemins `../05-agents/...`, `../02-decisions/...` (structure v1, remplacee par `ledger/`)
- Committer sans signature
- Creer des fichiers `INDEX.md` supplementaires (utiliser `INDEX-<scope>.md` pour stems uniques)

---

## Scripts Utiles

| Script | Role |
|--------|------|
| `_scripts/check-orphans.sh` | G2 enforcement (exit 1 si orphelins) |
| `_scripts/check-broken-links.sh` | Detection wikilinks casses (exit 1 si casses) |
| `_scripts/sync-canon.sh --dry-run` | Preview sync depuis `.spec/00-canon/` |
| `_scripts/audit-signatures.sh` | Audit retro des signatures git |
| `_scripts/evidence-pack.sh` | Generer un nouveau evidence-pack |

---

## Contact

- Owner: Fafa (automecanik.seo@gmail.com)
- Canon source: https://github.com/ak125/nestjs-remix-monorepo
- Ce vault: https://github.com/ak125/governance-vault

---

_Dernière mise a jour: 2026-04-17_
